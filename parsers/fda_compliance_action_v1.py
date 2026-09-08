"""FDA compliance actions -> observations.

The escalation step between an inspection and a recall: warning letters,
injunctions, seizures. Carries the FEI, so it joins the inspection series on
the establishment rather than on a firm name.

`observed_at` is **ActionTakenDate** — see fda_inspection_classification_v1
for why event date rather than capture time.

Action type is emitted as a 0/1 per type instead of a string, so a downstream
question ("how many warning letters at this plant before it stopped being
registered") is a SUM over a named metric rather than a string match a reader
has to get exactly right.
"""
import json
import re

from wss import derive

PARSER_VERSION = "1"


def _iso_yyyymmdd(value):
    text = (value or "").strip()[:10]
    parts = text.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts) or len(parts[0]) != 4:
        return None
    return int("".join(parts))


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "_", (text or "").lower()).strip("_")[:40]


def parse(body: bytes, ctx: derive.ParseContext):
    payload = json.loads(body)

    total = payload.get("totalrecordcount")
    if total is not None:
        yield derive.Observation(
            entity_id="feed:compliance_actions", metric="feed_records_total",
            value=int(total), unit="count")

    for row in payload.get("result") or []:
        fei = str(row.get("FEINumber") or "").strip()
        taken = _iso_yyyymmdd(row.get("ActionTakenDate"))
        if not fei or taken is None:
            continue
        firm = f"firm:{fei}"
        at = row.get("ActionTakenDate")[:10]

        yield derive.Observation(firm, "compliance_action", 1, "count", observed_at=at)
        yield derive.Observation(firm, "action_taken", taken, "yyyymmdd", observed_at=at)

        kind = _slug(row.get("ActionType"))
        if kind:
            yield derive.Observation(firm, f"action_{kind}", 1, "count", observed_at=at)

        yield derive.Observation(
            firm, "is_foreign",
            0 if (row.get("CountryCode") or "").strip().upper() == "US" else 1,
            "bool", observed_at=at)


derive.register("fda-compliance-action.v1", parse, PARSER_VERSION)
