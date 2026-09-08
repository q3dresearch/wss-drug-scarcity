"""FDA inspection citations -> observations.

The classification source records that a plant got an OAI. This records what the
investigator actually wrote: the CFR paragraph cited and the observation text.
That distinction is the point -- 21 CFR 211.113 (failure to validate a sterile
process) and an incomplete training record are both citations on the same
inspection, and only one of them is a reason a drug stops shipping.

Joins to fda.inspections.drugs on the SAME entity, firm:<fei>, and carries
InspectionID so a citation can be tied to its specific visit.

`cfr_part` is emitted alongside the full reference because the part is the
grouping that means something: 210/211 are drug GMP, 212 is PET drugs, 600s are
biologics, 1250 is interstate conveyance sanitation. A count of citations
without the part is a count of paperwork and contamination added together.

ProgramArea=Drugs is applied at the endpoint, not here. Unfiltered, this API
spans everything FDA inspects -- a live sample returned National Railroad
Passenger Corporation under 21 CFR 1250 -- so a parser-side filter would be a
second place for the mistake to hide.

`observed_at` is InspectionEndDate, the event date, not capture time.
"""
import json
import re

from wss import derive

PARSER_VERSION = "1"

# "21 CFR 211.113" -> 211. Tolerates missing spaces and a bare paragraph.
_PART = re.compile(r"(?:\b21\s*CFR\s*)?(\d{1,4})(?:\.\d+)?", re.I)


def _iso_yyyymmdd(value):
    text = (value or "").strip()[:10]
    parts = text.split("-")
    if len(parts) != 3 or not all(p.isdigit() for p in parts) or len(parts[0]) != 4:
        return None
    return int("".join(parts))


def _cfr_part(reference):
    m = _PART.search(reference or "")
    return int(m.group(1)) if m else None


def parse(body: bytes, ctx: derive.ParseContext):
    payload = json.loads(body)

    total = payload.get("totalrecordcount")
    if total is not None:
        # 5000-row cap per response, sliced one calendar year per endpoint.
        # A year passing the cap truncates silently, so the count is recorded.
        yield derive.Observation(
            entity_id="feed:citations", metric="feed_records_total",
            value=int(total), unit="count")

    for row in payload.get("result") or []:
        fei = str(row.get("FEINumber") or "").strip()
        ended = _iso_yyyymmdd(row.get("InspectionEndDate"))
        if not fei or ended is None:
            continue
        firm = f"firm:{fei}"
        at = row.get("InspectionEndDate")[:10]

        yield derive.Observation(firm, "citation", 1, "count", observed_at=at)

        name = (row.get("LegalName") or "").strip()
        if name:
            yield derive.Observation(firm, "label", name[:120], "", observed_at=at)

        reference = (row.get("ActCFRNumber") or "").strip()
        if reference:
            yield derive.Observation(firm, "cfr", reference[:60], "", observed_at=at)
            part = _cfr_part(reference)
            if part is not None:
                yield derive.Observation(firm, "cfr_part", part, "part", observed_at=at)
                # Drug GMP proper. Everything else this endpoint returns under a
                # Drugs filter is adjacent regulation, not manufacturing quality.
                yield derive.Observation(
                    firm, "is_gmp", 1 if part in (210, 211) else 0, "bool", observed_at=at)

        short = (row.get("ShortDescription") or "").strip()
        if short:
            yield derive.Observation(firm, "citation_topic", short[:120], "", observed_at=at)


derive.register("fda-inspection-citation.v1", parse, PARSER_VERSION)
