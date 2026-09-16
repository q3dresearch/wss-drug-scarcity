"""hpra-products.v1 — Ireland's authorised medicines, one row per product.

WHAT THIS ARCHIVE IS FOR. HPRA publishes what is authorised TODAY and overwrites
the file. `RegistrationStatus` reads `AU` on 12,326 of 12,326 products across
both lists, so the field that would record a withdrawal never records one --
a product that loses authorisation simply stops appearing. Presence is therefore
the only question this parser must serve well, and everything else is an
attribute of a row that happens to be there.

THE KEY IS `DrugIDPK` AND IT IS NOT QUITE UNIQUE. Publisher-minted, shaped like
`VPA10793/004/001`. The animal list has 1,991 distinct across 1,991 rows, but the
HUMAN LIST HAS 10,330 DISTINCT ACROSS 10,335 -- five collisions. Counted before
anything was diffed, because a non-unique key manufactures departures and
arrivals out of nothing. Duplicates are emitted once and counted, never silently
collapsed.

TWO SERIES, BECAUSE HUMAN AND VETERINARY ARE DIFFERENT POPULATIONS. They have
different regulators upstream, different authorisation routes and different
sizes, and a single series would let a veterinary withdrawal look like a human
one in any aggregate.

ATC AND ACTIVESUBSTANCE ARE WHY THIS SOURCE SITS IN THIS REPO. They are the
only cross-country join keys here. Measured against what the repo already holds:
Ireland's 2,545 substances overlap 234 of TGA Australia's 288 `active_ingredient`
values (81%), 29 of FDA's 70 (41%), and only 22 of ANSM France's 186 (12%) --
because ANSM names substances in French. ATC is the fix for France and Ireland is
the first source here to carry FULL codes: 2,297 distinct at levels 4 and 5
(`A01AA01`), against `atc_level1`'s 14 top-level categories elsewhere.

BOTH ARE MULTI-VALUED. A product has several ATC codes and several substances --
16,565 ATC elements across 10,335 products. They are emitted one observation per
value, never joined into a string, so a downstream filter can match any one.

MARKETINFO IS THE LIVE SIGNAL, NOT REGISTRATIONSTATUS. It actually varies --
Marketed 3,730 / Not marketed 2,032 / Unknown 4,573 on the human list -- and a
move to "Not marketed" may lead a departure. Worth capturing precisely because
it is the one field that moves.
"""

import re

from wss import derive

PARSER_VERSION = "2"

HUMAN = "ie.hpra.products.human"
ANIMAL = "ie.hpra.products.animal"
COUNTS = "ie.hpra.products.file"

PRODUCT = re.compile(r"<Product>(.*?)</Product>", re.S)
# One capture group per field, pulled by name so column order cannot matter.
FIELD = {
    "licence_number": "LicenceNumber",
    "product_name": "ProductName",
    "pa_holder": "PAHolder",
    "authorised_date": "AuthorisedDate",
    "product_type": "ProductType",
    "market_info": "MarketInfo",
    "registration_status": "RegistrationStatus",
    "dosage_form": "DosageForm",
}
DDMMYYYY = re.compile(r"^(\d{2})/(\d{2})/(\d{4})$")


def _all(block: str, tag: str) -> list[str]:
    """Every value of a repeating element, deduped, order preserved."""
    out, seen = [], set()
    for m in re.finditer(rf"<{tag}>(.*?)</{tag}>", block, re.S):
        v = re.sub(r"\s+", " ", m.group(1)).strip()
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return out


def _one(block: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", block, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def _iso(d: str) -> str:
    m = DDMMYYYY.match(d or "")
    return f"{m.group(3)}-{m.group(2)}-{m.group(1)}" if m else ""


def parse(body: bytes, ctx: derive.ParseContext):
    xml = body.decode("utf-8", errors="replace")
    animal = "Animallist" in (ctx.url if ctx else "") or "<Species>" in xml
    series = ANIMAL if animal else HUMAN
    file_id = "animal" if animal else "human"

    seen: set[str] = set()
    dupes = 0
    rows = 0
    for m in PRODUCT.finditer(xml):
        block = m.group(1)
        key = _one(block, "DrugIDPK")
        if not key:
            # No publisher key means no stable identity. Hashing the name would
            # turn every reformulation into a departure plus an arrival.
            continue
        rows += 1
        if key in seen:
            dupes += 1
            continue
        seen.add(key)

        yield derive.Observation(entity_id=key, metric="listed", value=1,
                                 unit="presence", series_id=series)
        for metric, tag in FIELD.items():
            v = _one(block, tag)
            if not v:
                continue
            if metric == "authorised_date":
                iso = _iso(v)
                if iso:
                    yield derive.Observation(entity_id=key, metric=metric,
                                             value=iso, unit="date",
                                             series_id=series)
                continue
            yield derive.Observation(entity_id=key, metric=metric, value=v,
                                     unit="text", series_id=series)

        # The join keys. Multi-valued, so one observation per value.
        for code in _all(block, "ATC"):
            yield derive.Observation(entity_id=key, metric="atc", value=code,
                                     unit="code", series_id=series)
        for sub in _all(block, "ActiveSubstance"):
            yield derive.Observation(entity_id=key, metric="active_substance",
                                     value=sub, unit="text", series_id=series)

    # File-level facts in their own series. These describe the fetch, not a
    # medicine, and must never share the product entity namespace.
    yield derive.Observation(entity_id=file_id, metric="products_in_file",
                             value=rows, unit="count", series_id=COUNTS)
    yield derive.Observation(entity_id=file_id, metric="distinct_keys",
                             value=len(seen), unit="count", series_id=COUNTS)
    # The alarm that matters: if this stops being 0 the key has decayed and any
    # diff built on it is reporting churn that did not happen.
    yield derive.Observation(entity_id=file_id, metric="duplicate_keys",
                             value=dupes, unit="count", series_id=COUNTS)


derive.register("hpra-products.v1", parse, PARSER_VERSION)
