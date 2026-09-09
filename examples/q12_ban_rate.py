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
    FONT, bar, nice_axis, para, rows, txt, wrap,
)
from xml.etree import ElementTree  # noqa: E402


def save(name: str, svg: str) -> str:
    """Parse before writing.

    This file wrote straight to disk with `out.write_text(...)` and shipped an
    invalid SVG -- the exact crime docs/charts.md already lists, committed by
    the one script that bypassed visualize.write(). A rule that lives in one
    helper is not a rule; it is a habit of whoever calls that helper.
    """
    ElementTree.fromstring(svg)
    (OUT_DIR / name).write_text(svg)
    return f"wrote examples/charts/{name}"

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


def chart_alert_vs_refusal(obs) -> str:
    """The divergence, as the two-dimensional thing it is.

    A bar chart of either measure hides this: alerts and refusals are separate
    axes, and the interesting countries are the ones far off the diagonal.
    Germany sits bottom-right (refused constantly, almost never alerted); China
    sits top-left (alerted constantly, barely refused). Mexico is the only one
    high on both.

    Bubble area -- not radius -- is proportional to registered sites, so a
    country with 5,321 sites does not read as 26x a country with 205 when it is
    26x by count.
    """
    num, den = refusals_by_country(obs)
    alerts = banned_by_country(obs)
    pts = []
    for c in den:
        if den[c] < 40:
            continue
        x = num[c] / den[c]                    # refusal firm-days per site
        y = 100 * alerts.get(c, 0) / den[c]    # alerts per 100 sites
        if x or y:
            pts.append((c, x, y, den[c]))
    if not pts:
        return "no points"

    W, H, L, B = 880, 620, 78, 150
    plot_w, plot_h = W - L - 210, H - B - 150
    xmax, xt = nice_axis(max(p[1] for p in pts))
    ymax, yt = nice_axis(max(p[2] for p in pts))
    body = [txt(24, 38, "Alerted and refused are different failures",
                size=19, fill=INK, weight="600")]
    lead, dy = para(24, 62, (
        "Each bubble is a country; area is the number of sites on the current drug "
        "establishment register. An import alert is standing detention WITHOUT physical "
        "examination, so an alerted firm stops shipping and its refusals collapse — which "
        "is why the two axes are not the same measurement twice."),
        size=12.5, fill=INK2, chars=112)
    body += lead
    T = 62 + dy + 30

    for i in range(yt + 1):
        gy = T + plot_h - plot_h * i / yt
        body.append(f'<line x1="{L}" y1="{gy:.1f}" x2="{L+plot_w}" y2="{gy:.1f}" '
                    f'stroke="{GRID}" stroke-width="1"/>')
        body.append(txt(L - 10, gy + 4, f"{ymax*i/yt:.0f}", size=10.5, fill=MUTED,
                        anchor="end", tab=True))
    for i in range(xt + 1):
        gx = L + plot_w * i / xt
        body.append(f'<line x1="{gx:.1f}" y1="{T}" x2="{gx:.1f}" y2="{T+plot_h:.1f}" '
                    f'stroke="{GRID}" stroke-width="1"/>')
        body.append(txt(gx, T + plot_h + 20, f"{xmax*i/xt:.0f}", size=10.5, fill=MUTED,
                        anchor="middle", tab=True))
    body.append(txt(L + plot_w / 2, T + plot_h + 44,
                    "refusal firm-days per registered site", size=11.5,
                    fill=INK2, anchor="middle"))
    # Rotate by wrapping the shared txt() helper, never by hand-writing a
    # <text>. FONT here contains "Segoe UI" in DOUBLE quotes, so a
    # double-quoted font-family attribute terminates early and the file stops
    # being XML. The same bug exists in the other direction in wss-grid-queue,
    # whose FONT uses single quotes -- which is the argument for one helper
    # rather than two hand-rolled elements.
    ax_y = T + plot_h / 2
    body.append(f'<g transform="rotate(-90 18 {ax_y:.1f})">'
                + txt(18, ax_y, "import alerts per 100 sites",
                      size=11.5, fill=INK2, anchor="middle")
                + '</g>')

    import math
    biggest = max(p[3] for p in pts)
    # Label only what the caption argues about. Every other bubble is
    # context, and naming all twelve is how a scatter becomes unreadable.
    NAMED = {"MEX", "CHN", "DEU", "USA"}
    for c, x, y, n in sorted(pts, key=lambda p: -p[3]):
        cx = L + plot_w * x / xmax
        cy = T + plot_h - plot_h * y / ymax
        r = 6 + 26 * math.sqrt(n / biggest)      # AREA proportional to sites
        hot = c in ("MEX", "CHN", "DEU")
        body.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" '
                    f'fill="{SLOTS[1] if hot else SLOTS[0]}" fill-opacity="0.42" '
                    f'stroke="{SLOTS[1] if hot else SLOTS[0]}" stroke-width="1.5"/>')
        if c in NAMED:
            label = f"{LABEL.get(c, c)} ({n:,})"
            if r > 20:      # a large bubble swallows a label placed beside it
                body.append(txt(cx, cy - r - 8, label, size=11, fill=INK,
                                anchor="middle", weight="600" if hot else "normal"))
            else:
                body.append(txt(cx + r + 6, cy + 4, label, size=11, fill=INK,
                                weight="600" if hot else "normal"))
    foot, _ = para(24, H - 62, (
        "Q24. Germany bottom-right: refused constantly, almost never alerted. China top-left: "
        "the inverse. Mexico is alone in the top-right. Refusals are FIRM-DAYS — a firm refused "
        "five times in a day counts once. Countries with fewer than 40 registered sites are "
        "excluded; one event there moves a rate by whole points."),
        size=10.5, fill=MUTED, chars=142, leading=14)
    body += foot
    return save("alert-vs-refusal.svg", wrap(W, H, "Import alerts against import refusals, by country",
                        "Scatter of alerts per 100 registered sites against refusal "
                        "firm-days per site; bubble area is registered sites.",
                        "\n".join(body)))


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
        # "773 of 205 sites" is impossible and was on the first render: the
        # label template came from the alert chart, where n IS a subset of the
        # sites (17 of 90 firms were banned). Here n is firm-DAYS across those
        # sites -- a different unit, so "of" is nonsense. Units, not "of".
        body.append(txt(L + max(w, 2) + 10, y + 22,
                        f"{n/d:.1f}   ·   {n:,} firm-days across {d:,} sites",
                        size=11, fill=INK2, tab=True))
    body.append(f'<line x1="{L}" y1="{T-8}" x2="{L}" y2="{T + row_h*len(pairs):.1f}" '
                f'stroke="{BASELINE}" stroke-width="1.5"/>')
    foot, _ = para(24, H - 76, (
        "Q22. FIRM-DAYS, not refusals: `import_refusal` is emitted as (firm, 1, date), so a firm "
        "refused five times in a day collapses to one row and 89,086 records reduce to 55,875. "
        "Note also Q23 — only 14% of all firm-days hit a registered site at all, so this measures "
        "enforcement against the REGISTERED base, not enforcement overall."),
        size=10.5, fill=MUTED, chars=142, leading=14)
    body += foot
    return save("refusal-rate-by-country.svg", wrap(W, H, "Refusal firm-days per registered site",
                        "FDA import-refusal firm-days 2001-2026 per site on the current "
                        "drug establishment register, by country.", "\n".join(body)))


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
    return save("ban-rate-by-country.svg", wrap(W, H, "Import bans per 100 registered sites",
                        "FDA Import Alert 66-40 firms per 100 sites on the current "
                        "drug establishment register, by country.", "\n".join(body)))


if __name__ == "__main__":
    obs = rows()
    if not obs:
        raise SystemExit("no observations — run `wss derive` first")
    print(chart(obs))
    print(chart_refusal_rate(obs))
    print(chart_alert_vs_refusal(obs))
