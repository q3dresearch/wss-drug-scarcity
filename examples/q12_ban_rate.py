"""Q12 — import bans as a RATE, using DECRS as the denominator.

`enforcement-year.svg` has carried this caveat since it was written:

    RAW COUNTS WITH NO DENOMINATOR. FDA publishes no fetchable list of
    registered sites per country, so these cannot be turned into rates --
    "more Chinese firms banned" may only mean "more Chinese firms" (Q12).

DECRS is that list. 10,080 registered drug establishments, each with an
address whose country code parses on 100% of rows. So the count becomes a
rate, and Q12 stops being blocked.

The denominator is a SNAPSHOT and the numerator is CUMULATIVE. Firms banned
over many years are divided by sites registered today, which understates the
rate wherever the registered base has grown and overstates it where the base
has shrunk. That is stated on the chart rather than smoothed over: an honest
ratio with a named flaw beats a raw count with none, but not by so much that
the flaw can go unmentioned.
"""
from __future__ import annotations

import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from visualize import (  # noqa: E402  -- shared palette and primitives
    BASELINE, DEEMPH, GRID, INK, INK2, MUTED, OUT_DIR, SLOTS,
    bar, nice_axis, para, rows, txt, wrap,
)

# ISO-3 in a trailing parenthesis is how DECRS ends every address:
#   "Rugao, Jiangsu, China (CHN)"
COUNTRY = re.compile(r"\(([A-Z]{3})\)\s*$")
# Import Alert entity ids are "country:<name>/firm:<slug>", with the country
# spelled out in words rather than coded.
NAME_TO_ISO3 = {
    "china": "CHN", "india": "IND", "united states": "USA", "germany": "DEU",
    "canada": "CAN", "france": "FRA", "italy": "ITA", "korea": "KOR",
    "south korea": "KOR", "japan": "JPN", "spain": "ESP", "mexico": "MEX",
    "united kingdom": "GBR", "brazil": "BRA", "taiwan": "TWN",
    "switzerland": "CHE", "israel": "ISR", "turkey": "TUR", "ireland": "IRL",
    "austria": "AUT", "belgium": "BEL", "netherlands": "NLD",
}
LABEL = {v: k.title() for k, v in NAME_TO_ISO3.items()}


def registered_by_country(obs) -> Counter:
    """Sites on the current register, by country. The denominator."""
    address = {}
    for r in obs:
        if r["source_id"] == "fda.decrs.registrations" and r["metric"] == "address":
            address[r["entity_id"]] = r["value"]
    out = Counter()
    for value in address.values():
        m = COUNTRY.search(value.strip())
        if m:
            out[m.group(1)] += 1
    return out


def refusals_by_country(obs) -> tuple[Counter, Counter]:
    """Refusal firm-days per country, and how many hit a registered site.

    Country and denominator both come from DECRS, keyed on FEI, rather than
    from a name parsed out of an alert entity id.

    NOT a refusal count. `import_refusal` is emitted as (firm, 1, date), so a
    firm refused five times in a day collapses to one row -- 89,086 records
    reduce to 55,875 firm-days. Labelled as firm-days everywhere.
    """
    addr, refus = {}, Counter()
    for r in obs:
        s, e, m = r["source_id"], r["entity_id"], r["metric"]
        if s == "fda.decrs.registrations" and m == "address" and e.startswith("fei:"):
            addr[e[4:]] = r["value"]
        elif s.startswith("fda.refusals") and m == "import_refusal" and e.startswith("firm:"):
            refus[e[5:]] += 1
    den, num = Counter(), Counter()
    for fei, a in addr.items():
        m = COUNTRY.search(a.strip())
        if not m:
            continue
        den[m.group(1)] += 1
        num[m.group(1)] += refus.get(fei, 0)
    return num, den


def banned_by_country(obs) -> Counter:
    """Firms ever listed on Import Alert 66-40, by country. The numerator."""
    out = Counter()
    seen = set()
    for r in obs:
        if r["source_id"] != "fda.importalert.66-40" or r["metric"] != "first_listed":
            continue
        entity = r["entity_id"]
        if entity in seen:
            continue
        seen.add(entity)
        name = entity.split("/", 1)[0].split(":", 1)[-1].replace("-", " ").strip().lower()
        iso = NAME_TO_ISO3.get(name)
        if iso:
            out[iso] += 1
    return out


def chart_refusal_rate(obs) -> str:
    """Refusal firm-days per registered site — the denser of the two measures."""
    num, den = refusals_by_country(obs)
    FLOOR = 40
    pairs = [(c, num[c], den[c]) for c in den if den[c] >= FLOOR and num[c] > 0]
    pairs.sort(key=lambda p: -(p[1] / p[2]))
    pairs = pairs[:12]

    W, L = 880, 132
    plot_w, row_h = W - L - 216, 34
    peak, ticks = nice_axis(max(n / d for _, n, d in pairs))
    body = [txt(24, 38, "Being alerted and being refused are not the same thing",
                size=19, fill=INK, weight="600")]
    lead, dy = para(24, 62, (
        f"Import-refusal firm-days per site on the current drug establishment register, "
        f"2001-2026 — {sum(num.values()):,} firm-days against {sum(den.values()):,} sites. "
        f"Mexico tops this AND the import-alert rate. Germany and China are opposites: "
        f"Germany 3.4 refusals per site on 0.8 alerts per 100, China 0.5 refusals on 14.1 "
        f"alerts. An alert is standing detention without physical examination, so an alerted "
        f"firm stops shipping and its refusals collapse. The alert is the policy; the refusal "
        f"is the exercise."), size=12.5, fill=INK2, chars=118)
    body += lead
    T = 62 + dy + 44
    H = T + row_h * len(pairs) + 96

    for i in range(ticks + 1):
        x = L + plot_w * i / ticks
        body.append(f'<line x1="{x:.1f}" y1="{T-8}" x2="{x:.1f}" '
                    f'y2="{T + row_h*len(pairs):.1f}" stroke="{GRID}" stroke-width="1"/>')
        body.append(txt(x, T - 16, f"{peak*i/ticks:.0f}", size=10.5, fill=MUTED,
                        anchor="middle", tab=True))
    body.append(txt(L + plot_w / 2, T - 34, "refusal firm-days per registered site",
                    size=11, fill=INK2, anchor="middle"))
    for i, (iso, n, d) in enumerate(pairs):
        y = T + i * row_h
        body.append(txt(L - 12, y + 22, LABEL.get(iso, iso), size=12, fill=INK, anchor="end"))
        w = plot_w * (n / d) / peak
        body.append(bar(L, y + 6, max(w, 2), 22, SLOTS[1] if i < 3 else SLOTS[0]))
        body.append(txt(L + max(w, 2) + 10, y + 22,
                        f"{n/d:.1f}   ·   {n:,} of {d:,} sites", size=11, fill=INK2, tab=True))
    body.append(f'<line x1="{L}" y1="{T-8}" x2="{L}" y2="{T + row_h*len(pairs):.1f}" '
                f'stroke="{BASELINE}" stroke-width="1.5"/>')
    foot, _ = para(24, H - 76, (
        "Q22. FIRM-DAYS, not refusals: `import_refusal` is emitted as (firm, 1, date), so a firm "
        "refused five times in a day collapses to one row and 89,086 records reduce to 55,875. "
        "Note also Q23 — only 14% of all firm-days hit a registered site at all, so this measures "
        "enforcement against the REGISTERED base, not enforcement overall."),
        size=10.5, fill=MUTED, chars=142, leading=14)
    body += foot
    out = OUT_DIR / "refusal-rate-by-country.svg"
    out.write_text(wrap(W, H, "Refusal firm-days per registered site",
                        "FDA import-refusal firm-days 2001-2026 per site on the current "
                        "drug establishment register, by country.", "\n".join(body)))
    return f"wrote {out.name}"


def chart(obs) -> str:
    den, num = registered_by_country(obs), banned_by_country(obs)
    # Only countries with enough registered sites for a rate to mean anything.
    # Below this a single ban swings the number by whole percentage points.
    FLOOR = 40
    pairs = [(c, num.get(c, 0), den[c]) for c in den if den[c] >= FLOOR]
    pairs = [p for p in pairs if p[1] > 0]
    pairs.sort(key=lambda p: -(p[1] / p[2]))
    pairs = pairs[:12]

    W, L = 880, 132
    plot_w, row_h = W - L - 210, 34
    peak, ticks = nice_axis(max(100 * n / d for _, n, d in pairs))

    body = [txt(24, 38, "Import bans per 100 registered sites, not raw counts",
                size=19, fill=INK, weight="600")]
    lead, dy = para(24, 62, (
        f"Firms on FDA Import Alert 66-40 (GMP failure) divided by sites on the "
        f"current drug establishment register. {sum(den.values()):,} registered sites, "
        f"country parsed from the address on 100% of them. Ranked by rate — which is "
        f"not the order the raw counts give."), size=12.5, fill=INK2, chars=118)
    body += lead
    T = 62 + dy + 44
    H = T + row_h * len(pairs) + 92

    for i in range(ticks + 1):
        x = L + plot_w * i / ticks
        body.append(f'<line x1="{x:.1f}" y1="{T-8}" x2="{x:.1f}" '
                    f'y2="{T + row_h*len(pairs):.1f}" stroke="{GRID}" stroke-width="1"/>')
        body.append(txt(x, T - 16, f"{peak*i/ticks:.0f}", size=10.5, fill=MUTED,
                        anchor="middle", tab=True))
    body.append(txt(L + plot_w / 2, T - 34, "banned firms per 100 registered sites",
                    size=11, fill=INK2, anchor="middle"))

    for i, (iso, n, d) in enumerate(pairs):
        y = T + i * row_h
        rate = 100 * n / d
        body.append(txt(L - 12, y + 22, LABEL.get(iso, iso), size=12, fill=INK, anchor="end"))
        w = plot_w * rate / peak
        body.append(bar(L, y + 6, max(w, 2), 22, SLOTS[1] if i < 3 else SLOTS[0]))
        body.append(txt(L + max(w, 2) + 10, y + 22,
                        f"{rate:.1f}   ·   {n} of {d:,} sites", size=11, fill=INK2, tab=True))
    body.append(f'<line x1="{L}" y1="{T-8}" x2="{L}" y2="{T + row_h*len(pairs):.1f}" '
                f'stroke="{BASELINE}" stroke-width="1.5"/>')

    foot, _ = para(24, H - 74, (
        "Q12, previously blocked. The denominator is a SNAPSHOT of the register today; "
        "the numerator is CUMULATIVE across every year FDA has listed a firm. That "
        "understates the rate where the registered base has grown and overstates it "
        "where it has shrunk — a flaw worth naming, not smoothing. Countries with fewer "
        f"than {FLOOR} registered sites are excluded, because one ban there moves the "
        "rate by whole points."), size=10.5, fill=MUTED, chars=142, leading=14)
    body += foot
    out = OUT_DIR / "ban-rate-by-country.svg"
    out.write_text(wrap(W, H, "Import bans per 100 registered sites",
                        "FDA Import Alert 66-40 firms per 100 sites on the current "
                        "drug establishment register, by country.", "\n".join(body)))
    return f"wrote {out.relative_to(OUT_DIR.parents[1])}"


if __name__ == "__main__":
    obs = rows()
    if not obs:
        raise SystemExit("no observations — run `wss derive` first")
    print(chart(obs))
    print(chart_refusal_rate(obs))
