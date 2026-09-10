"""fda-outsourcing.v1 — who may compound sterile drugs today, and who stopped.

503B outsourcing facilities exist because of the 2012 NECC meningitis outbreak.
This register is the list operating under that regime NOW — 96 facilities on
first capture. Registration renews, so a facility that lapses, withdraws or is
closed simply stops appearing. FDA publishes no departure event and keeps no
former-registrant list, so the exit leaves no trace at all — and the exit is
usually the interesting one, because it tends to follow an inspection.

The second loss is enforcement status, edited in place. "Action Based on Last
Inspection" reads Open or Closed; "Form 483 Issued?" and "Recall Conducted?"
are Yes/No. A facility moving Open -> Closed has had something resolved, and
after the edit there is nothing to say it was ever Open.

PERSONAL DATA IS FINGERPRINTED HERE, NOT DROPPED AND NOT PUBLISHED. The Contact
column pairs an individual's name with a direct phone number. The raw page goes
to object storage with the column intact — deleting at capture would be
irreversible, and the bytes are the evidence — and this parser emits only a
salted hash.

WHY A HASH AND NOT NOTHING. The contact is a de facto OWNERSHIP KEY, and it is
the only one FDA publishes. The register lists facilities, not owners, and on
first capture eight contacts appear at more than one facility. Most are obvious
multi-site operators (BSO Golden/Lakewood, SCA Little Rock/Windsor). Three are
not visible from the names at all: Ajenat Pharmaceuticals with BPI Labs, both in
Largo FL; Olympia with Wesley, both in Orlando; and Fagron Compounding Services
with Fresenius Kabi Compounding, two corporate parents sharing a dba. Dropping
the column outright would have thrown that away, which is the mistake the
"censor at derive, never at capture" rule exists to prevent — censoring is not
the same as discarding.

The fingerprint answers "did this change?" and "do these two share a contact?"
and answers nothing else. Name and phone are hashed separately, because a
facility can change its named person while keeping the line, and that
distinction is the churn signal.

THE SALT IS THE ACCESS CONTROL. A ten-digit phone number has too little entropy
to survive an unsalted hash — anyone could enumerate all 10^10 and match. With
`WSS_PII_SALT` set as a repo secret and never committed, the fingerprints are
stable across captures (so change detection works) and useless to anyone
without it. **If the salt is unset the fields are simply not emitted**, so a
misconfigured run loses a signal rather than publishing a phone number.
"""

import hashlib
import os
import re
from html import unescape

from wss import derive

PARSER_VERSION = "1"

TABLE = re.compile(r"<table[^>]*>(.*?)</table>", re.S)
ROW = re.compile(r"<tr[^>]*>(.*?)</tr>", re.S)
CELL = re.compile(r"<t[dh][^>]*>(.*?)</t[dh]>", re.S)
TAGS = re.compile(r"<[^>]*>")

# Positional, because the headers carry footnote markers ("Last Inspection 2",
# "Action Based on Last Inspection 4,5") and non-breaking spaces that make
# exact matching brittle. The header row is verified before any row is read.
COLUMNS = [
    "facility",
    None,                      # Contact — NAME + PHONE, fingerprinted only
    "initial_registration",
    "most_recent_registration",
    "last_inspection",
    "form_483_issued",
    "recall_conducted",
    "action_status",
    "intends_sterile_from_bulk",
]

EXPECTED_HEAD = ("facility", "initial registration", "action based on last inspection")

SALT_ENV = "WSS_PII_SALT"

# A CLOSED vocabulary, because the cell is free text carrying dates and footnote
# markers. Slugging it directly produced 23 one-off metric names -- including
# `action_warning-letter-closeout-issued-7-27-2026-fmd-145-letter-issued-7` --
# and split one state three ways as `open`, `open-7` and `open7` where a
# footnote digit had run into the word. A metric name is a column; it cannot be
# minted per row. The verbatim text still travels as the entity's
# `action_status`, so nothing is lost.
ACTION_CLASSES = (
    ("warning letter", "warning_letter"),
    ("untitled letter", "untitled_letter"),
    ("fmd-145", "fmd_145"),
    ("regulatory meeting", "regulatory_meeting"),
    ("open", "open"),
    ("n/a", "none"),
)


def _action_class(cell: str) -> str:
    text = re.sub(r"\d", " ", (cell or "").lower())
    for needle, name in ACTION_CLASSES:
        if needle in text:
            return name
    return "none" if not text.strip() else "other"


def _fingerprint(value: str) -> str:
    """Stable, salted, one-way. Empty when the salt is unset — fail closed."""
    salt = os.environ.get(SALT_ENV, "").strip()
    if not salt or not value:
        return ""
    return hashlib.sha256(f"{salt}|{value}".encode()).hexdigest()[:12]


def _split_contact(cell: str) -> tuple[str, str]:
    """("kenneth metzler", "7542654280") from "Kenneth Metzler 1-754-265-428".

    The name is whatever precedes the first digit; the phone is the last ten
    digits, so a leading country code does not change the key.
    """
    name = re.split(r"\d", cell, 1)[0].strip().lower()
    digits = re.sub(r"\D", "", cell)
    return name, (digits[-10:] if len(digits) >= 10 else "")


def _text(html: str) -> str:
    return " ".join(unescape(TAGS.sub(" ", html)).split())


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")[:64]


def parse(body: bytes, ctx: derive.ParseContext):
    html = body.decode("utf-8", errors="replace")
    facilities = 0
    status_counts: dict[str, int] = {}

    for table in TABLE.findall(html):
        rows = [[_text(c) for c in CELL.findall(r)] for r in ROW.findall(table)]
        rows = [r for r in rows if r]
        if not rows:
            continue
        head = " ".join(rows[0]).lower()
        if not all(token in head for token in EXPECTED_HEAD):
            continue
        if len(rows[0]) != len(COLUMNS):
            # Column count is the guard on the positional mapping. If FDA adds
            # or removes one, every field after it would silently shift — the
            # contact column could land in `initial_registration` and be
            # published. Fail instead.
            raise ValueError(
                f"fda-outsourcing.v1: expected {len(COLUMNS)} columns, found "
                f"{len(rows[0])}: {rows[0]}. The mapping is POSITIONAL and the "
                f"Contact column carries names and phone numbers, so a shifted "
                f"table must not be parsed. Re-map before re-enabling."
            )

        for cells in rows[1:]:
            if len(cells) != len(COLUMNS):
                continue
            record = {c: v for c, v in zip(COLUMNS, cells) if c}
            contact_raw = cells[1]          # never emitted, only fingerprinted
            name = record.get("facility", "")
            if not name:
                continue
            facilities += 1
            eid = f"facility:{_slug(name)}"
            # Presence IS the observation. There is no departure event, so a
            # facility vanishing between captures is only visible because every
            # capture recorded that it was here.
            yield derive.Observation(eid, "registered", "yes", "state")
            yield derive.Observation(eid, "facility_name", name, "text")
            for field, value in record.items():
                if field == "facility" or not value:
                    continue
                yield derive.Observation(eid, field, value, "text")
            person, phone = _split_contact(contact_raw)
            for metric, value in (("contact_person_fp", person), ("contact_phone_fp", phone)):
                fp = _fingerprint(value)
                if fp:
                    yield derive.Observation(eid, metric, fp, "id")

            status = _action_class(record.get("action_status", ""))
            status_counts[status] = status_counts.get(status, 0) + 1

    if not facilities:
        raise ValueError(
            "fda-outsourcing.v1: no table matched. The header must contain "
            f"{EXPECTED_HEAD}. FDA has reworded the columns or moved the list "
            "behind JavaScript; read the raw page before relaxing the gate"
        )

    feed = "feed:fda_outsourcing"
    yield derive.Observation(feed, "facilities_registered", facilities, "count")
    for status, n in sorted(status_counts.items()):
        yield derive.Observation(feed, f"action_{status}", n, "count")


derive.register("fda-outsourcing.v1", parse, PARSER_VERSION)
