"""FDA Product Code Builder reference tables -> observations.

A lookup table, not a time series: the codes that make up an FDA product code
(industry, class, subclass, process indicator). It is captured because the
enforcement feeds cite these codes and nothing else publishes the expansion,
so without it a refusal's `ProductCode` is an opaque string forever.

The envelope is generic -- RESULT.COLUMNS names the fields and RESULT.DATA is
a list of positional rows -- and the column set DIFFERS per endpoint
(['INDID','INDDESC'] for industry, ['PICID','PICCODE','PICDESC'] for the
process indicator). So the parser reads COLUMNS rather than assuming names; a
fixed-field parser would silently emit nothing for three of the four
endpoints.

Reference rows have no event date, so `observed_at` correctly defaults to the
capture time: the fact recorded is "this code was listed when we looked".
"""
import json
import re

from wss import derive

PARSER_VERSION = "1"


def _slug(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:60]


def parse(body: bytes, ctx: derive.ParseContext):
    payload = json.loads(body)
    result = payload.get("RESULT") or {}
    columns = [str(c) for c in (result.get("COLUMNS") or [])]
    rows = result.get("DATA") or []
    if not columns or not rows:
        return

    # The table is named by its own column set, so the four endpoints land in
    # four entity namespaces without hard-coding which is which.
    table = _slug("-".join(columns))

    yield derive.Observation(
        entity_id=f"pcb:{table}", metric="rows_listed", value=len(rows), unit="count")

    # The id is the first column, the human-readable expansion the last.
    for row in rows:
        if not isinstance(row, list) or not row:
            continue
        record = dict(zip(columns, row))
        code = str(row[0]).strip()
        if not code:
            continue
        yield derive.Observation(
            entity_id=f"pcb:{table}/code:{code}", metric="listed", value=1, unit="count")
        label = str(row[-1]).strip()
        if label and len(row) > 1:
            yield derive.Observation(
                entity_id=f"pcb:{table}/code:{code}", metric="label",
                value=label[:120], unit="")


derive.register("fda-pcb-reference.v1", parse, PARSER_VERSION)
