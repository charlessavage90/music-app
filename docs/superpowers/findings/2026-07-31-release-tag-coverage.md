# Release-tag aggregation coverage — the bar cleared, and the second source did the work

**Role: ACTIVE findings record. Owns its figures** (release-tag coverage figures only;
scoring and path-quality figures stay in `2026-07-21-scoring-adjudication.md`, and the
`TAS-` probe's stay in its own record). Identifier series: `REL-`. Probes and raw data:
`builder/analysis/2026-07-31-release-tag-coverage/`. Governing document, committed before
any measurement ran:
[`specs/2026-07-31-release-tag-coverage-preregistration.md`](../specs/2026-07-31-release-tag-coverage-preregistration.md).

**Scope: descriptive.** Nothing here adopts anything, fixes a criterion, or changes a weight,
default, currency or vocabulary. **`TAS-` §1's vocabulary is untouched** — a passing frame is
a *candidate* for a `TAS-` §8 amendment, never an enactment of one. It settles no open owner
decision in `NEXT.md`.

**Every figure is a census** over all 74,193 nodes of the adopted artifact, from four frozen
local files. No sampling, no seed, no confidence interval — and therefore no "within noise of
the bar" escape hatch in either direction.

---

## §0 The headline

*(Plain: for the obscure artists this app exists to surface, we knew the genre of about one
in three. Looking at what they released — rather than at their artist page — takes that to
about seven in ten. Two independent databases agree on the answer for 96.6% of the artists
they both reach. But the labels we recover are in the right region rather than exactly right,
and four in nine of these artists remain unreachable by any of it.)*

`REL-1`'s bar was `COH-2`'s committed 50% — same band, same denominator, same vocabulary
family — and it was fixed in writing **before** the release-existence ceiling was measured.

| | lower-half coverage |
|---|---|
| `F0` — what we know today | **35.4%** |
| `F1` — + MusicBrainz release-group genres | **58.8%** ← `REL-1`, **PASS** |
| `F4` — + Discogs genre instead | 67.9% |
| `F6` — + both | **71.0%** |

**The mechanism the `TAS-` handoff recorded as the argument *for* is true.** MusicBrainz
tagging effort attaches to the album a contributor just added, not to the artist entity: of
obscure unlabelled artists that have an attributable release group, **65.8%** have it tagged.
The pre-registered arithmetic said 41.0% was the break-even. The argument *against* — that the
indifference which left the artist bare left the records bare — is **refuted**.

---

## `REL-1` — the headline gate *(PASS)*

> *Plain: after looking at what they released, for how many of the obscure artists we
> currently know nothing about do we now know a genre?*

Share of **all** artists in each band carrying ≥ 1 label. `COH-2`'s denominator.

| band | n | `F0` | `F1` strict | `F2` wide vocab | `F3` permissive |
|---|---|---|---|---|---|
| top 0.1% | 75 | 100.0% | 100.0% | 100.0% | 100.0% |
| top 1% | 667 | 99.9% | 100.0% | 100.0% | 100.0% |
| top 10% | 6,678 | 93.1% | 98.7% | 98.7% | 99.2% |
| upper half | 29,677 | 68.6% | 87.6% | 87.9% | 90.8% |
| **lower half** | **37,096** | **35.4%** | **58.8%** | 59.2% | 64.9% |

**58.8% against a 50.0% bar.** Judged on `F1`, the conservative frame, exactly as
pre-registered — a frame clearing only under `F3` would have cleared a different bar.

**`F2` adds 0.4 points.** Widening from MusicBrainz's curated `genres` to its raw `tags` buys
almost nothing, which reproduces `COH-6`'s finding at the release level: the problem was never
the choice of vocabulary.

The census independently reproduces `COH-2`'s sampled baseline — 35.4% against its 35.3%.

## `REL-2` — the Discogs ceiling *(descriptive; no Discogs figure may be quoted without it)*

> *Plain: for how many of these artists can we even find a Discogs page — and of those, how
> many actually have records listed?*

Over artists **unlabelled today**:

| band | unlabelled | has a Discogs ID | ID **and** attributable releases |
|---|---|---|---|
| top 1% | 1 | 100.0% | 100.0% |
| top 10% | 464 | 96.3% | 87.5% |
| upper half | 9,332 | 86.9% | 72.6% |
| **lower half** | **23,959** | **70.0%** | **50.3%** |

**The Discogs arm is mapping-bound, not tag-bound, and the numbers prove it exactly.** Discogs
`genre` is 100% filled because it is a **schema constraint** — a release cannot be submitted
without one. So `F4`'s coverage should equal `F0` plus the `REL-2` product applied to the
unlabelled, and it does, to the decimal: 35.4% + (64.6% × 50.3%) = **67.9%**. There is *no*
tagging-effort loss on the Discogs side. Every artist we can find, we can label.

The mapping comes from MusicBrainz's own `discogs` url-rel — **by identifier, never by name**.
Name matching was rejected outright in the pre-registration as the population-mismatch trap
that killed every external popularity source.

## `REL-3` — validity, the held-out check *(PASS, and read the median, not the verdict)*

> *Plain: when we guess an artist's genre from their records, and we already happen to know
> the real answer, how often do we get it right?*

Run over artists **labelled today**, held out and re-derived as if they were not. 34,935
scorable.

| statistic | matched | shuffled null | bar | verdict |
|---|---|---|---|---|
| median Jaccard | **0.250** | 0.000 | ≥ 3× null | PASS *(degenerate — see below)* |
| zero-overlap rate | **12.8%** | 61.5% | ≥ 20 pts better | **PASS by 48.7 pts** |
| share at Jaccard ≥ 0.5 | **21.1%** | — | — | reported |

**The ratio test is a degenerate pass and should not be quoted.** The null median is exactly
0.000, so the pre-registered 3× bar is satisfied by a division by zero. That half of the
criterion is worthless as written; **the zero-overlap comparison is what actually carries
`REL-3`**, and it passes decisively — 61.5% of shuffled artists share *nothing* with the
truth against 12.8% matched. This is real signal, not a base-rate artifact.

**But 0.250 is a modest number and it is the honest headline for fidelity.** Aggregated labels
overlap known labels at about a quarter; only one artist in five reaches half-overlap. The
device lands in the right *region*, it does not recover the artist's genres.

## `REL-4` — does the second source add anything? *(descriptive — and it is the finding)*

> *Plain: does Discogs reach artists MusicBrainz misses, or the same ones twice?*

| band | `F1` | `F6` (both) | **increment** |
|---|---|---|---|
| top 10% | 98.7% | 99.5% | +0.8 |
| upper half | 87.6% | 92.9% | +5.3 |
| **lower half** | **58.8%** | **71.0%** | **+12.2** |

**Where each source reaches, among the 23,959 unlabelled lower-half artists:**

| | artists |
|---|---|
| Discogs only | **4,542** |
| both | 7,507 |
| MusicBrainz only | 1,153 |
| **neither** | **10,757** |

**⚠ `F6`'s 71.0% is a coincidence, not a cap being hit.** The pre-registration's §0 records an
absolute *ceiling* of 71.0% derived from MusicBrainz release existence alone, and `F6`'s
measured coverage lands on the same figure. They are different quantities computed from
different populations — `F6` combines two sources and is not bounded by the MusicBrainz-only
ceiling at all. Flagged because a reader who noticed the match would reasonably conclude the
frame had saturated, and it has not.

**This inverts the framing the probe was designed under.** Discogs was the awkward arm — the
independent source carrying a population-mismatch trap. In the obscure tail it is the
**stronger** one: it reaches four times as many artists alone as MusicBrainz does, and
MusicBrainz adds only 1,153 artists that Discogs misses.

**And the two agree.** On the 13,057 unlabelled artists both sources reach, **96.6% share at
least one label**; median Jaccard 0.400. That agreement is worth more than either coverage
figure, because the sources are genuinely independent — Discogs does not inherit MusicBrainz's
editorial blind spot. It is the strongest thing in this record.

**The vocabulary confound, named rather than buried:** MusicBrainz is a folksonomy ("modern
classical", "post-punk"), Discogs `genre` a closed 15-value list. Exact-match agreement is
depressed by *vocabulary*, not by the sources contradicting each other, which is why the
"share any label" column is the one that survives the gap. **The 0.400 median must not be read
as 60% disagreement.**

## `REL-5` — what the validity filter costs *(descriptive)*

> *Plain: how many artists do we give up on by refusing to guess from compilations and
> collaborations?*

**6.2 points** in the lower half (`F3` 64.9% vs `F1` 58.8%) — close to the 2,730 artists priced
in advance from the release-existence census. Affordable: `F1` clears the bar without it, so
the conservative frame was never bought at the cost of the result.

## `REL-6` — does the gain land in the tail? *(guard — NOT a success signal)*

> *Plain: does this fix the obscure artists we built the app to surface, or mostly the
> nearly-famous ones that were almost covered already?*

Gain in points, `F1` − `F0`: top 0.1% **+0.0**, top 1% +0.1, top 10% +5.6, upper half +19.1,
**lower half +23.4**.

**Not adverse.** The pre-registered adverse condition was a lower-half gain below half the
upper-half gain (< 9.55). The lower half gains *more* than the upper half in absolute points,
and the top bands gain nothing because they had nothing to gain. Under `F6` the tail gain is
**+35.6** against the upper half's +24.3.

**A favourable `REL-6` licenses nothing on its own.** It is a guard.

## `REL-7` — census-scale fidelity of the offline copy *(descriptive)*

Drift between the 2026-07-28 dump and the 2026-07-30 live frame: **0.09%**, with identical
normalised genre sets in **99.7–99.9%** of artists per band. This extends `COH-5`'s fidelity
finding from n = 872 to a census of 74,158. Snapshot drift is not a live explanation for
anything in this record.

Wikidata P136's separate contribution, visible once it stopped hiding inside a number labelled
"drift": **+11.0 points** in the lower half, +14.0 in the upper half.

## Instrument checks

Both passed; **no criterion above was read until they did**, which is why `REL-C1`'s first
failure stopped the run rather than being worked around.

- **`REL-C1`** — the aggregation code path, fed artist-level tags, must recover the LB half of
  the frame set-for-set. **145 of 74,193 disagree (0.20%) against a 0.50% tolerance.** It
  passes with a real residual rather than landing on zero, which is what a check that could
  fail looks like.
- **`REL-C2`** — shuffled ownership. Matched agreement collapses to a 0.000 median and a 61.5%
  zero-overlap rate, so `REL-3`'s signal is not chance. **Its coverage figure came back
  *higher* than the real one (63.5% vs 58.8%)** — the invariance §4 predicted in advance, and
  the reason that figure is barred from being read as evidence about `REL-1`. Shuffling
  ownership relocates coverage; it does not destroy it.

---

## Weakest link

**`REL-1` counts an artist as covered if aggregation yields *any* label, and the median obscure
artist has two release groups.** A single tagged EP can define an artist's genre. `REL-3`'s
0.250 median is the visible consequence. **If the downstream use needs a *confident* label
rather than *some* label, 58.8% is the wrong headline and 21.1% — the share reaching
half-overlap — is closer to the right one.** That is the load-bearing assumption, and it is
the one to attack.

**What I would defend cheaply:** `REL-1`, `REL-2`, `REL-5`, `REL-6`, `REL-7` — counts over a
fixed population from frozen local files, deterministic, no network, no sampling. And `REL-4`'s
96.6% agreement, which two independent databases had to conspire to fake.

**What I would abandon on one contrary measurement:** `REL-3`'s ratio test (already degenerate),
and any reading of the 0.400 agreement median as a fidelity figure rather than a
vocabulary-confounded one.

## What this record cannot conclude

- **Nothing about whether tags track the owner's ear.** No retrodiction, no listening test.
  Coherence still has no validated offline metric, in any currency.
- **Nothing that licenses a criterion, weight, default, currency or vocabulary change.**
- **Nothing about whether `TAS-6` would flip.** That needs a rebuild under a richer frame, which
  this probe does not do and does not license. `TAS-6`'s adverse result is driven by unlabelled
  obscure candidates being squeezed out; this record shows that population *could* shrink from
  64.6% to 29.0% of the lower half, and says nothing about what happens if it does.
- **Nothing about the 10,757 lower-half artists (44.9% of the unlabelled) that neither source
  reaches.** They have no attributable release in either database. No release-aggregation
  method of any kind reaches them.
- **Nothing durable.** Both databases move; these are 2026-06-01 (Discogs) and 2026-07-28/29
  (MusicBrainz) snapshots, and a re-run later is a new measurement.

## Amendments, and their disclosure

Two, both recorded in the pre-registration's §8 with the hazard named at their heads.

- **`REL-AM1`** — `REL-7` compared MusicBrainz genres against `F0` (LB ∪ P136), so its 11.73%
  "drift" was P136's contribution. Written after `REL-7`'s figure existed; **no criterion had a
  number yet.**
- **`REL-AM2`** — `REL-C1` carried the same defect, *and* fixing only the comparand would have
  made it duplicate `REL-7` and exercise no code. **Written after `REL-1` = 58.8% was known,
  which is a weaker disclosure position and is stated as such in the amendment.** What limits
  the damage: the defect was already-disclosed, and the repair made the check **stricter**
  (tolerance 11.73% → 0.50%).

One harness failure with no bearing on any figure: the Discogs collector was killed by the OS
after accumulating ~5M per-release records. Re-run accumulating unions in place; nothing
downstream needed the granularity.
