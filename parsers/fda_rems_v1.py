"""fda-rems.v1 — which drugs are restricted today, and silence about the rest.

A REMS is the machinery FDA imposes when a drug is approved only on condition
its use is controlled: prescriber certification, pharmacy enrolment, patient
registries. 71 programmes are approved on first capture.

WHAT PERISHES. FDA can RELEASE a REMS when the restriction is judged no longer
necessary, and a released programme leaves this page. The release is the
substantive event — the drug becomes materially easier to prescribe — and the
index offers no released, inactive or archived view; every link on it returns to
itself or leaves for fda.gov. "Which drugs stopped being restricted, and when"
therefore exists only for whoever kept the list.

`approved_at` is fixed and `last_updated` moves. Adasuve was approved
2012-12-21 and last updated 2026-05-11 — fourteen years of modifications, of
which one date survives.

THE FLAGS ARE THE SHAPE OF THE RESTRICTION, NOT ITS PRESENCE. MedGuide merely
informs the patient; ETASU (Elements To Assure Safe Use) and Implementation
System gate distribution. A programme dropping ETASU while staying listed is a
loosening that a bare count of REMS would miss entirely, so each flag travels
as its own observation rather than being summed.
"""

import re
from html import unescape

from wss import derive

PARSER_VERSION = "1"

ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
TAGS = re.compile(r"<[^>]*>")

# Positional. Column 2 has an EMPTY header on the page — it is the active
# ingredient list — so there is no name to match it by.
COLUMNS = [
    "rems_name",
    "active_ingredients",
    "approved_at",
    "last_updated",
    "flag_medication_guide",
    "flag_communication_plan",
    "flag_etasu",
    "flag_implementation_system",
]
FLAGS = [c for c in COLUMNS if c.startswith("flag_")]

EXPECTED_HEAD = ("rems approved", "last updated", "etasu")


def _text(html: str) -> str:
    return " ".join(unescape(TAGS.sub(" ", html)).split())


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:64]


def _iso(value: str) -> str:
    """FDA writes 12/21/2012 here. Anything else passes through unchanged."""
    m = re.match(r"\s*(\d{1,2})/(\d{1,2})/(\d{4})\s*$", value or "")
    return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}" if m else (value or "").strip()


def parse(body: bytes, ctx: derive.ParseContext):
    html = body.decode("utf-8", errors="replace")
    rows = [[_text(c) for c in CELL.findall(r)] for r in ROW.findall(html)]
    rows = [r for r in rows if r]

    header = next((r for r in rows if all(t in " ".join(r).lower() for t in EXPECTED_HEAD)), None)
    if header is None:
        raise ValueError(
            "fda-rems.v1: header row not found. Expected a row containing "
            f"{EXPECTED_HEAD}. Either FDA reworded the columns or a runner was "
            "served the 404 apology page accessdata gives them — check the raw "
            "bytes before touching the gate"
        )
    if len(header) != len(COLUMNS):
        # The mapping is positional and column 2 has no header text, so a
        # width change cannot be absorbed by matching names.
        raise ValueError(
            f"fda-rems.v1: expected {len(COLUMNS)} columns, found {len(header)}: "
            f"{header}. Re-map before re-enabling."
        )

    count = 0
    flag_totals = {f: 0 for f in FLAGS}
    for cells in rows:
        if len(cells) != len(COLUMNS) or cells is header:
            continue
        record = dict(zip(COLUMNS, cells))
        name = record["rems_name"]
        if not name or name.lower().startswith("name"):
            continue
        count += 1
        eid = f"rems:{_slug(name)}"
        # Presence IS the observation. A released REMS leaves no departure
        # record, so it is only visible as a row that stopped appearing.
        yield derive.Observation(eid, "approved", "yes", "state")
        yield derive.Observation(eid, "rems_name", name, "text")
        ing = record["active_ingredients"].strip().strip(",")
        if ing:
            # The page repeats an ingredient once per product in a shared
            # system ("alvimopan,alvimopan,alvimopan"), which counts products,
            # not substances. Deduplicated, order kept.
            uniq = list(dict.fromkeys(p.strip() for p in ing.split(",") if p.strip()))
            yield derive.Observation(eid, "active_ingredients", ", ".join(uniq), "text")
            yield derive.Observation(eid, "product_count", len(ing.split(",")), "count")
        for field in ("approved_at", "last_updated"):
            iso = _iso(record[field])
            if iso:
                yield derive.Observation(eid, field, iso, "date")
        for flag in FLAGS:
            on = bool(record[flag].strip())
            yield derive.Observation(eid, flag, "yes" if on else "no", "state")
            flag_totals[flag] += 1 if on else 0

    if not count:
        raise ValueError("fda-rems.v1: header matched but no data rows parsed")

    feed = "feed:fda_rems"
    yield derive.Observation(feed, "rems_approved_total", count, "count")
    for flag, n in flag_totals.items():
        yield derive.Observation(feed, f"total_{flag}", n, "count")


derive.register("fda-rems.v1", parse, PARSER_VERSION)
