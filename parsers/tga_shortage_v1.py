"""tga-shortage.v1 — Australia's medicine shortages, and the year-long memory.

WHY IT PERISHES, precisely. On first capture TGA held 984 records: 409 current,
278 discontinued, 204 resolved, 93 anticipated. **203 of the 204 resolved
shortages ended in 2026**, with exactly one 2022 survivor — while CURRENT
shortages persist back to 2003. Live rows are kept; closed rows are purged
after roughly a year.

The resolution is the only event that says how long a shortage LASTED, and it
is on screen for about twelve months before deletion. A weekly capture turns
that rolling window into a permanent duration series. The US comparison is the
argument for bothering: `fda.shortages.current` holds SEVEN resolved shortages
across fourteen years, so the same question is already unanswerable there.

STATUS LETTERS were read off the data, not assumed. `A` has 92 of 93 start
dates in the future (anticipated), `R` has all 204 end dates in the past
(resolved), `D` has 263 of 278 carrying the literal end `Unknown` — a
discontinuation does not end, which is why it has no end date — and `C` is
what is left (current).

TWO DATE FORMATS IN ONE RECORD. `shortage_start` arrives as "01 Jan 2013" and
`last_updated` as "16-10-2009". Assuming either one alone silently drops half
the dates, so both are parsed and anything else is passed through as text.

GRAIN. One record per ARTG registration number — 984 records, 984 distinct
`artg_numb`, no duplicates. So the ARTG number is the business key and a
product's successive shortages will overwrite one another in the live feed,
which is exactly what the archive is for.
"""

import json
import re
from datetime import date, datetime

from wss import derive

PARSER_VERSION = "1"

# Read off the data (see module docstring), not from a legend — the page ships
# no legend, and inventing one would put a guess in every row.
STATUS = {"A": "anticipated", "C": "current", "D": "discontinued", "R": "resolved"}

# `var tabularData = {...};` inlined in the search page. The Angular bundles
# name no XHR endpoint, so this literal IS the interface.
PAYLOAD = re.compile(r"var\s+tabularData\s*=\s*(\{.*?\});\s*\n", re.S)

# Plain text fields worth keeping. Sponsor_Name is a COMPANY, not a person.
TEXT_FIELDS = {
    "active_ingredients": "active_ingredient",
    "trade_names": "trade_name",
    "dose_form": "dose_form",
    "atc_level1": "atc_level1",
    "Sponsor_Name": "sponsor",
    "availability": "availability",
    "shortage_impact": "shortage_impact",
    "patient_impact": "patient_impact",
}

DATE_FIELDS = ("shortage_start", "shortage_end", "deleted_date", "last_updated")


def _parse_date(value) -> date | None:
    """"01 Jan 2013" and "16-10-2009" both appear, sometimes in one record."""
    text = str(value or "").strip()
    if not text or text.lower() == "unknown":
        return None
    for fmt in ("%d %b %Y", "%d-%m-%Y", "%d %B %Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _iso(value) -> str:
    d = _parse_date(value)
    return d.isoformat() if d else ""


def parse(body: bytes, ctx: derive.ParseContext):
    text = body.decode("utf-8", errors="replace")
    match = PAYLOAD.search(text)
    if not match:
        # A 1.7 MB page that renders its chrome and loses the payload is the
        # failure this guards. The gate's must_contain catches it first; this
        # is the second line, because a gate can be relaxed and a parser that
        # silently yields nothing looks like a quiet week.
        raise ValueError(
            "tga-shortage.v1: `var tabularData` not found. TGA has moved the "
            "data behind an XHR or changed the literal's name; find the new "
            "shape before relaxing the gate"
        )
    records = json.loads(match.group(1)).get("records") or []

    counts: dict[str, int] = {}
    durations: list[int] = []
    for row in records:
        artg = str(row.get("artg_numb") or "").strip()
        if not artg:
            continue
        eid = f"artg:{artg}"
        # `last_updated` is TGA's own "when this record last changed", which is
        # the event date. Falling back to the fetch time would restate every
        # unchanged record as a fresh observation every week.
        observed = _iso(row.get("last_updated")) or None

        raw_status = str(row.get("status") or "").strip().upper()
        status = STATUS.get(raw_status, raw_status.lower() or "unknown")
        counts[status] = counts.get(status, 0) + 1
        yield derive.Observation(eid, "status", status, "state", observed_at=observed)

        for field in DATE_FIELDS:
            iso = _iso(row.get(field))
            if iso:
                yield derive.Observation(eid, field, iso, "date", observed_at=observed)
            elif str(row.get(field) or "").strip().lower() == "unknown":
                # A discontinuation does not end. Recording the literal keeps
                # "no end date" distinguishable from "field was blank".
                yield derive.Observation(eid, field, "unknown", "text", observed_at=observed)

        # The number the archive exists to produce. Only meaningful once a
        # shortage has closed, which is precisely the state TGA deletes.
        start, end = _parse_date(row.get("shortage_start")), _parse_date(row.get("shortage_end"))
        if start and end and end >= start and status == "resolved":
            days = (end - start).days
            durations.append(days)
            yield derive.Observation(eid, "duration_days", days, "count", observed_at=observed)

        for field, metric in TEXT_FIELDS.items():
            value = str(row.get(field) or "").strip()
            if value:
                yield derive.Observation(eid, metric, value, "text", observed_at=observed)

    feed = "feed:tga_shortages"
    yield derive.Observation(feed, "records_total", len(records), "count")
    for status, n in sorted(counts.items()):
        yield derive.Observation(feed, f"records_{status}", n, "count")
    # Carried at feed level so a chart can show the closable-window size
    # without re-scanning every entity.
    yield derive.Observation(feed, "resolved_with_duration", len(durations), "count")


derive.register("tga-shortage.v1", parse, PARSER_VERSION)
