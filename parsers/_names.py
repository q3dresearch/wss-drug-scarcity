"""One firm-name normaliser, imported by both sides of the join.

The shortage feed names a manufacturer as a string. The enforcement feeds name
an establishment as a string plus an FEI. Nothing carries both, so the only
bridge is the name — and a bridge built from a string is only as good as the
normalisation being IDENTICAL on both sides.

That is why this is a module and not two copies. Two normalisers that disagree
about "Inc." do not raise; they return an empty join, which reads exactly like
"no shortage is made by a firm with an enforcement record" — a finding rather
than a bug.

Measured on the live data: 86% of shortage records carry a manufacturer whose
normalised name matches an enforcement firm. The remaining ambiguity is not in
the string — it is that a firm holds several plants, so a name resolves to a
median of 1 FEI but a mean of 3.0 and a maximum of 17. Only 30% of shortage
records land on a firm with exactly one establishment. Anything drawn from this
join has to say which of the two it is using.

Not a parser: registers no schema. `discover_parsers` imports it harmlessly.
"""
import re

# Corporate furniture that varies between FDA systems for the same company.
# Deliberately does NOT strip geographic words ("USA", "Deutschland"): those
# distinguish real, separately-inspected establishments of one parent.
_SUFFIX = re.compile(
    r"\b(INC|LLC|L\.?L\.?C|LTD|CORP|CORPORATION|CO|COMPANY|PLC|GMBH|SA|AG|BV|NV"
    r"|PVT|PRIVATE|LIMITED|PHARMACEUTICALS?|PHARMA|LABORATORIES|LABS?"
    r"|INTERNATIONAL|HOLDINGS?|GROUP|SRL|S\.?R\.?L|KG|AS|OY|AB)\b"
)


def firm_key(name: str) -> str:
    """A stable join key for a firm name, or "" when there is nothing to join on.

    >>> firm_key("Fresenius Kabi USA, LLC")
    'FRESENIUS KABI USA'
    >>> firm_key("FRESENIUS KABI USA LLC.")
    'FRESENIUS KABI USA'
    """
    upper = re.sub(r"[^A-Z0-9 ]", " ", (name or "").upper())
    return " ".join(_SUFFIX.sub(" ", upper).split())
