"""FDA iRES drug recalls -> observations.

Kept despite openFDA publishing a free recall endpoint, because the free one
carries **no FEI** -- only `recalling_firm` as a name string. iRES carries
FIRMFEINUM, which is the whole reason this source justifies an API key and a
local capture: it is the only recall feed that joins to the inspection series
on the establishment rather than on a firm name.

Field names are SHOUTED and dates are MM/DD/YYYY here, unlike the Data
Dashboard sources; that difference is the source's, not a normalisation we
chose to skip.

`observed_at` is **RECALLINITIATIONDT**. Recall class lives in
CENTERCLASSIFICATIONTYPETXT as a bare digit 1/2/3 where 1 is most severe --
note this runs OPPOSITE to the inspection severity scale, which ascends.
"""
import json

from wss import derive

PARSER_VERSION = "1"


def _us_yyyymmdd(value):
    """'08/31/2026' -> 20260831."""
    parts = (value or "").strip().split("/")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    mm, dd, yyyy = parts
    if len(yyyy) != 4:
        return None
    return int(f"{yyyy}{mm:0>2}{dd:0>2}")


def _iso(value):
    parts = (value or "").strip().split("/")
    if len(parts) != 3:
        return None
    mm, dd, yyyy = parts
    return f"{yyyy}-{mm:0>2}-{dd:0>2}"


def parse(body: bytes, ctx: derive.ParseContext):
    payload = json.loads(body)

    total = payload.get("RESULTCOUNT")
    if total is not None:
        yield derive.Observation(
            entity_id="feed:recalls", metric="feed_records_total",
            value=int(total), unit="count")

    for row in payload.get("RESULT") or []:
        fei = str(row.get("FIRMFEINUM") or "").strip()
        initiated = _us_yyyymmdd(row.get("RECALLINITIATIONDT"))
        at = _iso(row.get("RECALLINITIATIONDT"))
        if not fei or initiated is None:
            continue
        firm = f"firm:{fei}"

        yield derive.Observation(firm, "recall", 1, "count", observed_at=at)
        # The entity is a bare FEI, which no reader can act on. The name
        # travels with every row so a chart can title a bar without
        # reaching back into the raw archive, which charts must not do.
        name = (row.get("FIRMLEGALNAM") or "").strip()
        if name:
            yield derive.Observation(firm, "label", name[:120], "", observed_at=at)
        yield derive.Observation(firm, "recall_initiated", initiated, "yyyymmdd", observed_at=at)

        klass = (row.get("CENTERCLASSIFICATIONTYPETXT") or "").strip()
        if klass in ("1", "2", "3"):
            yield derive.Observation(firm, "recall_class", int(klass), "class", observed_at=at)
            yield derive.Observation(firm, "is_class_i", 1 if klass == "1" else 0, "bool", observed_at=at)

        # A recall that has terminated is finished; an ongoing one is still
        # removing product from the market. The distinction matters for any
        # question about how long a disruption lasted.
        yield derive.Observation(
            firm, "recall_terminated", 0 if not row.get("TERMINATIONDT") else 1,
            "bool", observed_at=at)


derive.register("fda-ires-recall.v1", parse, PARSER_VERSION)
