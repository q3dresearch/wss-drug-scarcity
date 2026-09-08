"""FDA import refusals -> observations.

CAUTION, and it is the reason this parser exists in the shape it does: this
endpoint is **not filtered to drugs**. A live sample of 5,000 refusals was 38%
Tobacco Products, 26% Drugs and Biologics and 24% Human Drugs. Joining it to a drug establishment
registry without filtering produces a large, confident, wrong answer -- it did
here, inflating an apparent enforcement effect roughly 2x before the
composition was checked.

So `is_human_drug` is emitted on every row. Any downstream question has to
either filter on it or explicitly decide not to; the trap is not hidden behind
a field a reader has to know to look for.

`observed_at` is **RefusalDate**.
"""
import json

from wss import derive

PARSER_VERSION = "1"


def _iso_yyyymmdd(value):
    text = (value or "").strip()[:10]
    parts = text.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts) or len(parts[0]) != 4:
        return None
    return int("".join(parts))


def parse(body: bytes, ctx: derive.ParseContext):
    payload = json.loads(body)

    total = payload.get("totalrecordcount")
    if total is not None:
        # This endpoint returns "recent" refusals against a 5000-row cap, so a
        # total at or above the cap means the window is truncating.
        yield derive.Observation(
            entity_id="feed:import_refusals", metric="feed_records_total",
            value=int(total), unit="count")

    for row in payload.get("result") or []:
        fei = str(row.get("FEINumber") or "").strip()
        refused = _iso_yyyymmdd(row.get("RefusalDate"))
        if not fei or refused is None:
            continue
        firm = f"firm:{fei}"
        at = row.get("RefusalDate")[:10]

        yield derive.Observation(firm, "import_refusal", 1, "count", observed_at=at)
        # The entity is a bare FEI, which no reader can act on. The name
        # travels with every row so a chart can title a bar without
        # reaching back into the raw archive, which charts must not do.
        name = (row.get("FirmName") or "").strip()
        if name:
            yield derive.Observation(firm, "label", name[:120], "", observed_at=at)
        yield derive.Observation(firm, "refused_at", refused, "yyyymmdd", observed_at=at)

        # Two vocabularies, deliberately both emitted. ProductCategory is the
        # coarse bucket and says "Drugs and Biologics" (26% of a 5,000 sample);
        # IndustryCodeDescription is finer and says "Human Drugs" (24%). An
        # earlier draft of this parser tested ProductCategory against "human
        # drugs" and matched nothing, which is worse than no flag at all --
        # a guard reading 0% looks like an answer.
        category = (row.get("ProductCategory") or "").strip().lower()
        industry = (row.get("IndustryCodeDescription") or "").strip().lower()
        yield derive.Observation(
            firm, "is_drug_or_biologic", 1 if category == "drugs and biologics" else 0,
            "bool", observed_at=at)
        yield derive.Observation(
            firm, "is_human_drug", 1 if industry == "human drugs" else 0,
            "bool", observed_at=at)

        yield derive.Observation(
            firm, "is_foreign",
            0 if (row.get("CountryCode") or "").strip().upper() == "US" else 1,
            "bool", observed_at=at)


derive.register("fda-importrefusal.v1", parse, PARSER_VERSION)
