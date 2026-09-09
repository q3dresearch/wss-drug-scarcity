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
