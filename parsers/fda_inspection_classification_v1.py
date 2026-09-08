"""FDA inspection classifications -> observations.

One row per inspection of an establishment, carrying the FEI. This is the
first link in the enforcement chain the repo is built to follow:
inspection -> compliance action -> recall -> shortage.

`observed_at` is **InspectionEndDate**, not capture time. The whole point of
this source is when the inspection happened; dating it at fetch would collapse
five years of history onto the day we downloaded it and make any lead-time
question unanswerable.

Classification is ordinal so it fits a numeric `value`, ascending in severity:
NAI 0, VAI 1, OAI 2. Higher is worse, which is the opposite of the shortage
parser's availability scale — stated here because the two get joined.

Purity rule: nothing depends on today's date. Dates are absolute YYYYMMDD
integers so a re-derive years from now is byte-identical.
"""
import json

from wss import derive

PARSER_VERSION = "1"

# Ascending severity. `Classification` is a sentence, `ClassificationCode` the
# short form; the code is preferred and the sentence is the fallback because
# FDA has shipped rows with one populated and not the other.
_SEVERITY = {"NAI": 0, "VAI": 1, "OAI": 2}


def _iso_yyyymmdd(value):
    """'2026-08-19' -> 20260819. Returns None on anything else."""
    text = (value or "").strip()[:10]
    parts = text.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    y, m, d = parts
    if len(y) != 4:
        return None
    return int(f"{y}{m:0>2}{d:0>2}")


def _severity(row):
    code = (row.get("ClassificationCode") or "").strip().upper()
    if code in _SEVERITY:
        return _SEVERITY[code]
    text = (row.get("Classification") or "").upper()
    for code, rank in _SEVERITY.items():
        if f"({code})" in text:
            return rank
    return None


def parse(body: bytes, ctx: derive.ParseContext):
    payload = json.loads(body)

    total = payload.get("totalrecordcount")
    if total is not None:
        # The API caps a response at 5000 rows and these endpoints are sliced
        # one per fiscal year. If a year's true count passes the cap the slice
        # truncates silently, so the count is recorded and compared downstream.
        yield derive.Observation(
            entity_id="feed:inspections", metric="feed_records_total",
            value=int(total), unit="count")

    for row in payload.get("result") or []:
        fei = str(row.get("FEINumber") or "").strip()
        ended = _iso_yyyymmdd(row.get("InspectionEndDate"))
        if not fei or ended is None:
            continue
        firm = f"firm:{fei}"
        at = row.get("InspectionEndDate")[:10]

        yield derive.Observation(firm, "inspected", 1, "count", observed_at=at)
        # The entity is a bare FEI, which no reader can act on. The name
        # travels with every row so a chart can title a bar without
        # reaching back into the raw archive, which charts must not do.
        name = (row.get("LegalName") or "").strip()
        if name:
            yield derive.Observation(firm, "label", name[:120], "", observed_at=at)
        yield derive.Observation(firm, "inspection_end", ended, "yyyymmdd", observed_at=at)

        rank = _severity(row)
        if rank is not None:
            yield derive.Observation(firm, "classification", rank, "ordinal", observed_at=at)
            # Broken out as its own 0/1 so "how many OAIs" is a SUM rather than
            # a filter on an ordinal that a reader has to decode first.
            yield derive.Observation(firm, "is_oai", 1 if rank == 2 else 0, "bool", observed_at=at)

        yield derive.Observation(
            firm, "is_foreign",
            0 if (row.get("CountryCode") or "").strip().upper() == "US" else 1,
            "bool", observed_at=at)


derive.register("fda-inspection-classification.v1", parse, PARSER_VERSION)
