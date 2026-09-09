"""fda.decrs.v1 — the drug establishment register, with the people removed.

FDA publishes the CURRENT register and no history. An establishment is removed
when its registration lapses or is inactivated by an enforcement action, and
that removal is published nowhere: the row simply stops being in the file.
The disappearance is the event, and it only exists in accumulated captures.

**This is the fleet's first `personal_data: present` source.** The raw file
carries named people at named firms with working email addresses. The bytes are
kept verbatim in object storage -- never in git -- and this parser is what
stands between them and anything published.

Two rules, and the second matters more than the first:

  1. The four contact columns are dropped by name.
  2. A column this parser has never seen is a HARD FAILURE, not a passthrough.

Rule 2 is the one that survives contact with reality. Dropping a denylist works
until FDA adds `ESTABLISHMENT_CONTACT_PHONE`, at which point a denylist quietly
publishes it. An allowlist plus a refusal means a schema change stops the derive
and asks a human, which is the correct outcome for a file full of personal data.

Censoring here rather than refusing the source is deliberate: throwing away a
record because it contains an email destroys it permanently, while redaction is
reversible in the direction that matters -- the raw bytes are still there, in a
private bucket, if a question ever genuinely needs them.
"""

import io
import re
import zipfile

from wss import derive

PARSER_VERSION = "1"

# Business facts about a registered establishment. Safe to publish.
KEEP = {
    "FEI_NUMBER": "fei",
    "DUNS_NUMBER": "duns",
    "FIRM_NAME": "firm_name",
    "ADDRESS": "address",
    "EXPIRATION_DATE": "registration_expires",
    "OPERATIONS": "operations",
    "REGISTRANT_NAME": "registrant_name",
    "REGISTRANT_DUNS": "registrant_duns",
    "EXCLUSION_FLAG": "exclusion_flag",
}

# Named individuals and their working addresses. Never published, never derived.
DROP = {
    "ESTABLISHMENT_CONTACT_NAME",
    "ESTABLISHMENT_CONTACT_EMAIL",
    "REGISTRANT_CONTACT_NAME",
    "REGISTRANT_CONTACT_EMAIL",
    # A free-text agent block. Sometimes a company, often a person with an
    # email in the middle of it. Unparseable safely, so it does not leave.
    "AGENT_DETAILS",
}


class UnknownColumn(Exception):
    """FDA added a column. Stop, rather than guess whether it is personal."""


def _rows(body: bytes):
    """The tab-separated member of the zip, as dict rows."""
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        name = next((n for n in z.namelist() if n.lower().endswith(".txt")), None)
        if name is None:
            return
        text = z.read(name).decode("utf-8", "replace")
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return
    header = [h.strip() for h in lines[0].split("\t")]

    unknown = [h for h in header if h and h not in KEEP and h not in DROP]
    if unknown:
        raise UnknownColumn(
            f"unrecognised column(s) {unknown} in the DECRS file. This source "
            f"is personal_data: present, so an unknown column is not passed "
            f"through -- decide whether it identifies a person, then add it to "
            f"KEEP or DROP in parsers/fda_decrs_v1.py and re-derive. The raw "
            f"bytes are already archived, so nothing is lost by stopping here.")

    for line in lines[1:]:
        cells = line.split("\t")
        yield {h: (cells[i].strip() if i < len(cells) else "")
               for i, h in enumerate(header) if h}


class NoIdentifier(Exception):
    """A row with neither an FEI nor a DUNS cannot be tracked between captures."""


def parse(body: bytes, ctx: derive.ParseContext):
    for row in _rows(body):
        # KEY. Not every establishment has an FEI: 14 of the 21 on the exclusion
        # list carry only a DUNS, and an earlier version of this parser skipped
        # them with a bare `continue` -- silently dropping two thirds of the
        # sharpest signal in the source, with no error and no count.
        #
        # An excluded firm with no FEI is arguably the more interesting case:
        # it never held an FDA establishment identifier, or no longer does.
        fei = (row.get("FEI_NUMBER", "") or "").strip()
        duns = (row.get("DUNS_NUMBER", "") or "").strip()
        if fei:
            key = f"fei:{fei}"
        elif duns and duns.strip("0"):
            key = f"duns:{duns}"
        else:
            # Neither identifier. "Lyssy and Eckel Inc." carries DUNS 000000000,
            # a placeholder rather than a number. Falling back to the firm name
            # keeps the row -- dropping an EXCLUDED establishment is the worst
            # possible thing to drop -- and the `name:` prefix is itself the
            # warning: a name is not a stable key, so a rename reads as a
            # disappearance plus an arrival. Anything counting removals must
            # treat name-keyed rows separately.
            slug = re.sub(r"[^a-z0-9]+", "-", (row.get("FIRM_NAME", "") or "").lower()).strip("-")
            if not slug:
                raise NoIdentifier(
                    "an establishment row has no FEI, no usable DUNS and no firm "
                    "name. There is nothing to key it by; the raw bytes are "
                    "archived, so decide what to do before deriving.")
            key = f"name:{slug}"
        for column, metric in KEEP.items():
            value = (row.get(column, "") or "").strip()
            if value:
                yield derive.Observation(entity_id=key, metric=metric,
                                         value=value, unit="text")


derive.register("fda.decrs.v1", parse, PARSER_VERSION)
