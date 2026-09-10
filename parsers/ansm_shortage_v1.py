"""ansm-shortage.v1 — France's medicine availability, and its one-year memory.

THE CORRECTION THIS SOURCE CARRIES. A screen of seven European regulators
concluded that Europe keeps its shortage history — Britain lists 75 expired
Serious Shortage Protocols back to 2019, Germany's BfArM shows resolved
notifications under a dedicated Archiv, EUDAMED versions all 3.4 million device
records. France does not, so the behaviour is regulator-specific rather than
continental, and the earlier claim was too broad.

WHAT PERISHES, measured on first capture. 291 rows: 139 "Tension
d'approvisionnement", 89 "Remise à disposition", 47 "Rupture de stock", 16
"Arrêt de commercialisation". Of the 89 RESOLVED rows, 85 are 2026 and 4 are
2025 — none older — while unresolved shortages carry `Mise à jour` dates back
to 2021. Live rows kept, closed rows purged after about a year. Identical
signature to tga.shortages.au.

THE SUBSTANCE IS IN THE PRODUCT STRING. "Prevymis 120 mg, granulés en sachet –
[létermovir]" carries brand, strength, form and the INN in brackets. The INN is
extracted so France can be joined to FDA and TGA on substance rather than on
brand, which does not travel between countries. The full string is kept too,
because the extraction is a guess and the string is the evidence.

DATES ARE FRENCH. DD/MM/YYYY throughout. Reading them as US MM/DD silently
mangles every day past the twelfth and, worse, leaves the first twelve looking
correct.
"""

import re
from html import unescape

from wss import derive

PARSER_VERSION = "1"

ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
TAGS = re.compile(r"<[^>]*>")
DATE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
# The INN sits in square brackets at the end of the product string.
INN = re.compile(r"\[([^\]]+)\]\s*$")

COLUMNS = ["statut", "updated_at", "product", "resolved_at", "domain"]

# Statut is a closed vocabulary on the page. Normalised to ASCII keys so a
# metric name never carries an accent, while the French text stays as the value.
STATUS = {
    "tension d'approvisionnement": "tension",
    "remise à disposition": "resolved",
    "rupture de stock": "rupture",
    "arrêt de commercialisation": "discontinued",
}


def _text(html: str) -> str:
    return " ".join(unescape(TAGS.sub(" ", html)).split())


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:64]


def _iso(value: str) -> str:
    m = DATE.search(value or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def parse(body: bytes, ctx: derive.ParseContext):
    html = body.decode("utf-8", errors="replace")
    counts: dict[str, int] = {}
    seen = 0

    for raw in ROW.findall(html):
        cells = [_text(c) for c in CELL.findall(raw)]
        if len(cells) != len(COLUMNS):
            continue
        record = dict(zip(COLUMNS, cells))
        product = record["product"]
        if not product:
            continue
        seen += 1
        eid = f"med:{_slug(product)}"
        # `Mise à jour` is ANSM's own "when this record last moved", which is
        # the event date. Without it every unchanged row would restate itself
        # as a fresh observation on every capture.
        observed = _iso(record["updated_at"]) or None

        status_fr = record["statut"]
        status = STATUS.get(status_fr.lower(), _slug(status_fr) or "unknown")
        counts[status] = counts.get(status, 0) + 1

        yield derive.Observation(eid, "status", status, "state", observed_at=observed)
        yield derive.Observation(eid, "status_fr", status_fr, "text", observed_at=observed)
        yield derive.Observation(eid, "product", product, "text", observed_at=observed)
        inn = INN.search(product)
        if inn:
            yield derive.Observation(eid, "substance", inn.group(1).strip().lower(),
                                     "text", observed_at=observed)
        if record["domain"]:
            yield derive.Observation(eid, "domain", record["domain"], "text", observed_at=observed)
        for field in ("updated_at", "resolved_at"):
            iso = _iso(record[field])
            if iso:
                yield derive.Observation(eid, field, iso, "date", observed_at=observed)

    if not seen:
        raise ValueError(
            "ansm-shortage.v1: no five-column rows found. ANSM has changed the "
            "table or moved it behind JavaScript — read the raw page before "
            "relaxing the gate"
        )

    feed = "feed:ansm_shortages"
    yield derive.Observation(feed, "records_total", seen, "count")
    for status, n in sorted(counts.items()):
        yield derive.Observation(feed, f"records_{status}", n, "count")


derive.register("ansm-shortage.v1", parse, PARSER_VERSION)
