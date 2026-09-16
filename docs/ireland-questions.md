# What Ireland's authorisation register opens up

`ie.hpra.products` joined this repo on 17 September 2026. It is not another
shortage list — it is the first **denominator**.

Every other source here says what is *missing, refused, recalled or inspected*.
None says what is *authorised*. 10,335 human and 1,991 veterinary products, with
2,545 distinct active substances and **2,297 full ATC codes**, answer that.

## The join, measured before it was sold

| existing source | its values | overlap with Ireland's substances |
| --- | ---: | ---: |
| `tga.shortages.au` `active_ingredient` | 288 | **234 — 81%** |
| FDA `active_ingredients` | 70 | 29 — 41% |
| `ansm.shortages.fr` `substance` | 186 | **22 — 12%** |

**Australia joins on substance names. France does not**, and the reason is
visible in the data: ANSM writes `acide acétylsalicylique` where Ireland writes
`acetylsalicylic acid`. Name matching is not a language-independent key.

**ATC is the fix, and Ireland is the only source here that carries full codes** —
2,297 distinct at levels 4 and 5 (`A01AA01`), against `atc_level1`'s 14
top-level categories elsewhere. The France join therefore stays blocked until an
ATC code is attached on the ANSM side. That is a real limit, not a to-do.

## New questions this makes askable

| # | question | status |
| --- | --- | --- |
| IE1 | **What share of authorised substances are ever short?** | Answerable for Australia now: 234 joinable substances against a 2,545-substance denominator. Every shortage count in this repo has so far been a numerator with no denominator |
| IE2 | **Is "authorised but not marketed" a pre-shortage state?** | **2,032 of 10,335** Irish human products are explicitly `Not marketed`, and a further 4,573 are `Unknown`. Needs two captures to see whether a move into `Not marketed` precedes a shortage elsewhere |
| IE3 | **Which therapeutic classes carry the most shortage risk?** | ATC levels 4–5 give a real hierarchy. Currently this repo can only group by 14 top-level categories, which is too coarse to act on |
| IE4 | **Do withdrawals cluster by authorisation holder?** | A `PAHolder` leaving Ireland would show as several products vanishing together — visible only across captures |
| IE5 | **Does a substance short in Australia lack Irish authorisation at all?** | Answerable today for the 81% that join. A substance short everywhere and authorised nowhere is a different problem from one short in one market |

## X1 — resolved, and it cuts against us

**HPRA does publish its withdrawals.** Settled 17 September 2026 by reading the
withdrawn page's own request body, which is in the page source:

```
{"id":null,"skip":0,"take":10,"query":null,"order":"LastUpdated DESC",
 "status":"Withdrawn","filters":{...}}
```

`"status": "Withdrawn"` is the answer. `sfapi.hpra.ie/api/HumanApprovedProducts`
has a status dimension the bulk XML does not, and HPRA serves withdrawn products
through it.

**So the claim "nobody records this" is false, and this repo must not make it.**

**What we cannot do is read it.** That endpoint returns 403 with a **zero-byte
body** to an honest client — identical for the key in the query string, the
URL-encoded key, and an `x-functions-key` header. A wrong key returns 401 with a
message; a zero-byte 403 is a WAF refusing non-browser clients. Reading it means
impersonating a browser, which this fleet does not do.

### What that does to the questions above

**IE2 and IE4 lose their premise.** Both assumed departures are invisible. They
are not invisible — they are *unreadable by us*. Those two are now bounded: we
can still observe a product leaving the XML, but we cannot claim that observation
is the only record of it.

**IE1, IE3 and IE5 are untouched.** They use the register as a denominator and a
therapeutic classification, and neither depends on withdrawals being unpublished.

### Why the capture is kept anyway

Two requests a month buys a **machine-readable** departure record that HPRA
offers only through an app we are refused. That is the availability argument —
retention exists, our access does not — and it is a narrower claim than the one
this source was built on.

**Retire on either of:** `sfapi.hpra.ie` answering an honest client, or HPRA
publishing a withdrawn list in the blob store. Both make the capture redundant
immediately.

## Nearly half the register is of unknown market status

`MarketInfo` on the human list: **Marketed 3,730 / Not marketed 2,032 /
Unknown 4,573**. Any denominator built from this register has to say which of
those three it counts, and IE1 above uses all authorised products regardless —
the alternative readings are not interchangeable.
