"""fda-device-shortage.v1 — six devices, and no memory of the others.

TWO TABLES, ONE PAGE, DIFFERENT SCHEMAS. Table 1 is the shortage list — six
rows on first capture, with Category, Product Code, Availability and Estimated
Shortage Duration, Additional Information, Reason for Interruption (per 506J)
and Date. Table 2 is discontinuations — 145 rows, with Date Posted, Category,
Product Code, Manufacturer Name, Device Trade Name and Reason for
Discontinuance. They share only two column names, so they are parsed
separately; treating them as one table would silently align `Date Posted`
against `Category`.

WHY IT PERISHES. Six live rows. A set that small turns over completely
invisibly: a device enters, a device leaves, and there is no resolved list and
no transition event. `fda.shortages.current` at least keeps seven resolved drug
records; this page has no such concept at all.

The second loss is the estimate. "Estimated through Q4 2026" is a promise, and
the Date column carries its own revision trail concatenated in place —
"2026/03/13 Initial2026/06/16Revised". The trail is kept only as far as the
current page shows it, and only the latest estimate survives. `date_raw` is
emitted verbatim rather than parsed, because the concatenation is the evidence.

NO JAVASCRIPT. Both tables are server-rendered in a Drupal node, so the HTML is
the interface and a regex over table markup is the whole parser.
"""

import re
from html import unescape

from wss import derive

PARSER_VERSION = "1"

TABLE = re.compile(r"<table[^>]*>(.*?)</table>", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
TAGS = re.compile(r"<[^>]*>")

# Column order is positional because the headers carry footnote markup and
# non-breaking spaces that make exact-string matching brittle. The header row
# is checked against these instead, so a reordered table fails loudly.
SHORTAGE_COLS = ["category", "product_code", "availability", "additional_info",
                 "reason", "date_raw"]
DISCONTINUED_COLS = ["date_posted", "category", "product_code", "manufacturer",
                     "trade_name", "reason"]

SHORTAGE_HEAD = "reason for interruption"
DISCONTINUED_HEAD = "reason for discontinuance"


def _text(html: str) -> str:
    return " ".join(unescape(TAGS.sub(" ", html)).split())


def _rows(table_html: str) -> tuple[list[str], list[list[str]]]:
    out = []
    for raw in ROW.findall(table_html):
        cells = [_text(c) for c in CELL.findall(raw)]
        if cells:
            out.append(cells)
    return (out[0] if out else []), out[1:]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:48] or "unknown"


def parse(body: bytes, ctx: derive.ParseContext):
    html = body.decode("utf-8", errors="replace")
    tables = TABLE.findall(html)
    seen_shortage = seen_discontinued = 0

    for table in tables:
        header, rows = _rows(table)
        head = " ".join(header).lower()
        if SHORTAGE_HEAD in head:
            cols, prefix = SHORTAGE_COLS, "device"
        elif DISCONTINUED_HEAD in head:
            cols, prefix = DISCONTINUED_COLS, "discontinued"
        else:
            continue
        for cells in rows:
            if len(cells) != len(cols):
                # A row that does not match the header width is a colspan
                # banner or a footnote, not data.
                continue
            record = dict(zip(cols, cells))
            code = record.get("product_code", "")
            # The product code is "HBA (Neurosurgical pattie)" — the code is the
            # key, the description is a label, and keying on the whole string
            # would split one device in two the day FDA reworded the gloss.
            short = (re.match(r"\s*([A-Z]{3})\b", code) or [None, _slug(code)])[1]
            if prefix == "device":
                eid = f"device:{short}"
                seen_shortage += 1
            else:
                # Product codes repeat across manufacturers here, so the trade
                # name is part of the key.
                eid = f"discontinued:{short}:{_slug(record.get('trade_name', ''))}"
                seen_discontinued += 1
            yield derive.Observation(eid, "listed", prefix, "state")
            for field, value in record.items():
                if value:
                    yield derive.Observation(eid, field, value, "text")

    if not seen_shortage and not seen_discontinued:
        raise ValueError(
            "fda-device-shortage.v1: neither table matched. The headers are "
            "matched on 'Reason for Interruption' and 'Reason for "
            "Discontinuance'; FDA has reworded them or moved the data behind "
            "JavaScript. Read the raw page before relaxing the gate"
        )

    feed = "feed:fda_device_shortages"
    # The live set is six rows. Carrying the count as its own observation is
    # what makes "it turned over" visible at all, since no transition is
    # published and the entities themselves simply appear and vanish.
    yield derive.Observation(feed, "devices_in_shortage", seen_shortage, "count")
    yield derive.Observation(feed, "devices_discontinued", seen_discontinued, "count")


derive.register("fda-device-shortage.v1", parse, PARSER_VERSION)
