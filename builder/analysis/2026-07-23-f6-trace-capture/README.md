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

> **Superseded in part by §5, and worth stating because it changes what these URLs are
> worth.** The offered/rejected distinction above is a limit of *this* section's method,
> not of the URLs. `find_path` is a pure, deterministic function of (artifact, endpoints,
> exclusion set, config), and every one of those is either in the URL or pinned by
> checksum — so **the path itself is exactly recoverable**, as §5 demonstrates. The
> *offered* set is therefore obtainable too, for any state we choose to reconstruct. Two
> real caveats survive: the reconstruction is only faithful if the artifact and config
> match what was running in the browser (there is precedent for a stale server on :8000
> serving a pre-fix graph — Track 1 use-the-app notes), and the dislike/known
> **interleaving** is lost, so intermediate states are not directly addressable.

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

---

## 5. Step 43 — the snap-back, reconstructed exactly

The owner later supplied a URL one bypass beyond F6 ("one step further than Max Richter"),
not knowing whom he had bypassed. It is F6 plus exactly one appended `dislike`, so the new
MBID names the artist; and since `find_path` is a pure full regeneration and all state is
in the URL, **both paths reconstruct exactly** (exclusion order is irrelevant — hard
exclusions are a set, and the floor depends only on per-reason counts). Script:
`resolve_step43.py`.

**The artist bypassed was Nancy Sinatra** (in-graph pctl 0.9892).

| | interiors | the path |
|---|---|---|
| **F6, 42 bypasses** | **9** | Frank Sinatra → Nancy Sinatra → Ennio Morricone → Hans Zimmer → Clint Mansell → **Max Richter → Ólafur Arnalds** → Tycho → deadmau5 |
| **step 43** | **4** | Nina Simone → Leonard Cohen → **Simon & Garfunkel → Queen** |

Both between Miles Davis and Daft Punk.

### 5.1 This is F6's reported snap-back, confirmed to the artist

The owner reported reaching Max Richter and Ólafur Arnalds and then "a single further
bypass snapped back to very famous (Queen, Simon & Garfunkel)". Both named artists are in
the step-43 path, in that path and no other. As with §2, a reported impression is
independently confirmed after the fact.

### 5.2 The metric cannot tell the two paths apart — and that is the finding

| | min interior pctl | median interior pctl |
|---|---|---|
| F6 (the reach he valued) | 0.9829 | 0.9940 |
| step 43 (the snap-back) | 0.9820 | 0.9909 |

**In-graph popularity percentile is essentially identical across the two**, and where it
differs it very slightly *favours the snap-back*. Yet one is a nine-artist corridor through
film score and modern classical that the owner experienced as finally reaching the tail,
and the other is a four-artist fallback to household names that he reported as failure.

This is **§2.11 confirmed in the sharpest available form**: the whole neoclassical/ambient
corridor sits in the top ~1.5 % by in-graph popularity. Max Richter is at 0.9862 and
Ólafur Arnalds at 0.9908 — by the in-graph metric they are *more* popular than Queen
(0.9820).

**Consequence, and it is a design validation rather than a new decision.** A success
criterion phrased as an in-graph popularity percentile would score these two paths as
indistinguishable, and would therefore be blind to precisely the contrast Track 2 exists
to produce. The pre-registration already scores C1/C2 on an **external fame proxy** for
this reason (§2.1, on the nine-names verdict). This trace is the first *path-level*
evidence for that choice, where the prior evidence was artist-level.

### 5.3 Two mechanism observations, offered as observations only

Both are n = 1 and neither is a pre-registered outcome. Recorded because they are cheap
and bear on Track 2's reads.

- **The corridor had a single entrance.** Removing one artist did not substitute one
  artist — it destroyed the whole route, from Frank Sinatra onward. The obscure corridor
  was apparently reachable only through Nancy Sinatra at a competitive cost, with no
  second-cheapest way in, so the router fell back to the famous stratum wholesale. If this
  generalises it is a fragility the sweep should be able to see; the §1.5 F5 confinement
  diagnostic is the nearest existing instrument, and it currently looks for the *opposite*
  pattern (changes confined to one region).
- **Payload collapsed 9 → 4 interiors**, which is Attack 5 and WHAT-GOOD #2 observed in
  the wild rather than argued: fewer-but-obscurer is not a win, and here it was not even
  obscurer. Criterion **C4** exists for this and its threshold (mean interior count ≥ P's
  mean − 1) would flag a drop of five.
- **The floor was long dead at both states.** With 16 `known` and 26–27 `dislike`
  bypasses, the relaxed raw floor reached zero around bypass 5–6 and had been inert for
  roughly 35 bypasses. The only depth-graduated device in the shipped cost function was
  contributing nothing across the entire interesting portion of this walk — analyst **D2**,
  observed in a real session rather than derived.
