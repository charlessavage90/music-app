# The owner's F3 / F6 bypass trace — captured and resolved

**Discharges prerequisite P1** of the Track 2 pre-registration. The owner supplied both
URLs directly on 2026-07-23. *(The execution log had recorded that they lived in the
branch/PR thread; they did not — no PR carries any comment. Correction is in the log.)*

Artifact: `graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`, asserted in-script.
All 44 MBIDs across both URLs resolve in the adopted artifact.

**Currency warning.** Percentiles below are **in-graph popularity**, not fame — log §2.11
establishes the two diverge at the top, which is why the sweep is scored on an external
proxy. Here they happen to agree, and that agreement is itself worth noting (see §3).

---

## 1. What the URLs are

Both carry **the same endpoints**, and F3's bypass lists are a strict prefix of F6's. This
is **one continuous walk**, captured twice:

| | endpoints | depth |
|---|---|---|
| **F3** | Miles Davis → Daft Punk | 15 bypasses (4 dislike, 11 known) |
| **F6** | Miles Davis → Daft Punk | 42 bypasses (26 dislike, 16 known) |

**The interleaving is not recoverable.** `dislike` and `known` are separate URL
parameters, so the order *within* each list survives but the sequence *between* them does
not. Irrelevant to the sweep, whose protocol is all-`known` with a scripted victim rule,
but it bounds what this trace can be replayed as.

## 2. F3's example is literally in the URL

The owner's stated unacceptable case for F3 was "Bowie → Pink Floyd → Beatles, all
famous-for-famous". Known presses **#10, #11, #12** are, in order: **David Bowie**,
**Pink Floyd**, **The Beatles**. The record's prose and the URL agree exactly — a rare
case where a reported impression is independently confirmable after the fact.

## 3. Every artist bypassed across 42 presses sits above the 97.7th percentile

The minimum over all 42 is **The Hives at 0.9773**; the other 41 are ≥ 0.9819. The list
is Ye, Bon Jovi, PJ Harvey, Bruno Mars, Ella Fitzgerald, Tom Waits, Eminem, Michael
Jackson, Muse, The Beatles, Led Zeppelin, Nirvana, David Bowie, Pink Floyd, Beyoncé,
The Beach Boys …

**What this is evidence for, stated carefully.** It is the *rejected* set, not the
*offered* set — these are artists the owner chose to bypass, so it cannot show that the
router never offered anything obscure. Indeed F6 records that he did eventually reach
Max Richter and Ólafur Arnalds, and neither appears here, because he did not bypass them.

What it does show is that **through 42 consecutive bypasses the router kept re-offering
the very top of the distribution**, which is direct experiential support for F2 and log
§2.9 on the repaired graph, in the owner's own session rather than a scripted walk.

**A note on the two currencies, since this project has been caught by them three times.**
Every name above is genuinely famous, so here in-graph popularity and real fame *coincide*.
That is not a refutation of §2.11 — §2.11's point is that the top percentile band also
contains lo-fi and synthwave artists who are *not* famous. The band is a mix; this trace
happens to have drawn the famous part of it. The sweep still needs the external proxy.

## 4. Consequence for the pre-registration: pair 8 collides with pair 1

Pre-registration §2.3 lists pair 1 as **Miles Davis → Daft Punk** (canonical listen pair,
log §3.8) and pair 8 as "the owner's F6 bypass pair, captured under P1". **They are the
same pair.** As specified, the analysis set would contain seven distinct pairs, not eight.

Handled by amendment **A7** — see the pre-registration §9. Summary: the §2.3 substitution
rule is applied (pair 8 → **Nirvana → CROOVE**, the head of the pre-registered ordered
reserve), and pair 1 inherits pair 8's rationale, since it *is* the trace pair.
