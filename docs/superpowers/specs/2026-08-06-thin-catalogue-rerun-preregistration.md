# `TCR-` — the thin-catalogue probe, re-run under externally anchored gates

**Role: ACTIVE — governing document for the `TCR-` probe.** Committed **before the dump
counter runs against any gate anchor and before any outcome value exists**; the git commit
timestamp is the evidence, not this sentence.

**Plain-language question** (quoted from `TCE-AM1`, which fixed it): *when the app looks at
**any** artist's ten strongest connections, are artists with nothing of their own recorded
over-represented there compared with the rest of that same artist's list* — and, per
`TCR-C2`, *is it still there in the map the website serves today?*

## Why this document exists — the void, stated plainly

**`TCE-` is VOID.** Its instrument-validation gate `TCE-G1` was evaluated first and alone,
one of four cells failed, and the run stopped at phase 3 of 7. **No outcome value was
computed and none was seen**: there is no `TCE-C1`/`C2`/`C3`/`C4`/`C5`, no `Δ_R`, and no
branch — which is what licenses re-registration rather than amendment. The void run's record
is `builder/analysis/2026-08-06-tce-thin-catalogue/` (result, run log, mis-filing check) and
it **stands untouched**: nothing here re-bands `TCE-G1` or retro-fits anything to it.

**The diagnosis, both halves together** (void-run README §2): the instrument is **correct** —
the dump counter agreed exactly with the live MusicBrainz API on independent check — and the
threshold was **wrong**, a guess reasoned from a *recording* count without checking what it
implies for *release-groups*. The owner ruled Option A on 2026-08-06 (night): re-run under a
**new** pre-registration with gate thresholds anchored on externally measured values, by a
fresh session. That ruling is recorded in `NEXT.md` and
`2026-08-06-HANDOFF-tce-void.md` and is not re-litigated here.

**What carries forward unchanged:** everything `TCE-AM1` and `TCE-AM2` established — the
per-arm attainable ceiling and its band structure, the pinning gate, `C3`/`C4`/`C5` with
their exact nulls and plain sentences, the three mitigations, the barred reads, and the §6
run-state ordering. They were never invalidated; the gate fired before any of them ran.
**What changes:** the instrument-validation gate (`TCR-G1`, redesigned below) and the
explicit tie resolution the void run's structural pass showed was needed.

**Identifier note:** the `TCR-` series is new and was collision-checked with the all-refs
`git grep` sweep (silence on `\bTCR-` across `refs/heads` and `refs/remotes`, 2026-08-06).

**⚠ This is NOT a route to widening the drop rule.** The owner ruled that out 2026-08-06 —
he does not think Andrew VanWyngarden or Zach Condon should have been dropped — and that
ruling is untouched by any result here. (That VanWyngarden serves below as a *gate anchor*
is instrument calibration, not a drop-rule question.) This probe measures whether a link's
*strength* tracks how much of an artist exists; it proposes nothing about whether an artist
appears at all.

---

## 0. The confound that would kill the naive design, and how this avoids it

Carried from `TCE-` §0 unchanged. The naive design compares scores across artists; nothing
establishes that a score of 214 on one artist's list means the same thing as 214 on
another's (`RCC-AM1` paid for this lesson).

> **Every comparison in this probe is WITHIN one reference artist's similar-list, using
> RANK, never raw score.** Cross-artist score comparison appears nowhere and licenses
> nothing.

**The confound that remains points against the hypothesis:** famous artists' strongest
neighbours are plausibly also famous, and famous artists have large catalogues, so the
ambient expectation puts thin artists LOW in a list. A positive result is therefore harder
than chance; a negative or null result is correspondingly weak evidence, and §5 says so.

## 0.1 The dormant term, now with its size measured — and the tie rule that answers it

**`similarity_rescale = p99_log_clip` is not monotone at the top**: clipped edges become
ties, concentrated exactly where this probe looks. The void run measured the size before it
stopped: **one arm B reference artist in five has a score tie spanning the rank-10
boundary** (20.4 %, a structural fact owned by
`builder/analysis/2026-08-06-tce-thin-catalogue/README.md` §4 — carried here as a known
fact, not re-derived). Sort order deciding one top-ten in five is not a residual; it gets a
binding rule:

> **Average-rank tie resolution, exact.** Each list is sorted by (score descending, MBID
> ascending) for determinism. If a maximal block of equal-score entries spans the rank-10
> boundary — sorted positions `a..b` with `a ≤ 10 < b` — then `s = 10 − a + 1` top-ten
> slots belong to the block's `n = b − a + 1` members, of which `t` are thin. Every
> quantity that reads "thin count in the top ten" is computed as its **exact expectation
> under a uniformly random ordering of the block**: `X = x_above + H` with
> `H ~ Hypergeometric(n, t, s)`.
>
> - `TCR-C1`'s `Δ_R` and `TCR-C4`'s `Σ x_R` use `E[X]` (linear, so exact).
> - `TCR-C3` uses `E[M_R] = Σ_h P(H=h) · M(x_above+h)`.
> - `TCR-C5` uses `Σ_h P(H=h) · 1[upper mid-p ≤ 0.05]` as that artist's (fractional)
>   contribution.
>
> This applies to **both arms** (arm A's raw integer scores tie too), and each arm's
> boundary-tie count is reported as run state.

Arm A reads raw archived scores, which the rescale cannot reach; arm B reads the shipped
graph's stored scores, which it does. Handled, not assumed away.

## 1. Population — a CENSUS, not a sample

Unchanged from `TCE-` §1. No sampling, no seed.

- **Arm A reference set:** every artist in the 75,000-artist `ALG-B` archive
  (`builder/scratch/grt-archive-algb/similar/…`, population sha
  `381305a73f7c6a9cba338e207d1a9ae7890709169afa3c4d953944b5fc6477be`) whose archived
  similar-list has **≥ 30 entries**.
- **Arm B reference set:** every artist present in the adopted artifact
  `graph-msw-tu50.bin`, sha
  `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` (manifest-verified),
  with **degree ≥ 30**.

The two reference sets are deliberately different sizes; the difference *is* arm B's
intervention.

## 2. Factor table

| Arm | Edge source | Drop filters applied | Scores rescaled | Isolating baseline |
|---|---|---|---|---|
| **A** | raw ListenBrainz archive | **no** | no | — (baseline) |
| **B** | adopted graph `43dd82bb…` | **yes** (`drop_unlistenable`, `drop_no_release_tail`, `drop_featured_credit`) | yes | **A** |

**A and B differ by two columns**, and the consequence is binding: an A→B difference may
**not** be attributed to the drop filters alone. `TCR-R2` reads it as "something between
the raw feed and the shipped map removes it", never as "the filters remove it".

**Held constant, and why each is genuinely constant under the intervention:**

- **The connection rule (`trimmed_union`).** Classification is by MusicBrainz release-group
  count from a dump the builder never reads; no connection rule can change an artist's
  catalogue.
- **Fame and the `known` ramp.** Router-side, applied at query time; this probe reads
  stored edges and runs no journeys.
- **`pop_raw`.** Unused — popularity here is score-weighted in-degree computed from these
  very edges, so using it would be circular.

## 3. The instrument, and the gates

**Catalogue size** = the number of MusicBrainz **release-groups** on which the artist
appears in `artist-credit`, counted by one streaming pass over the release-group dump dated
**2026-07-29** (`builder/scratch/mb-json-dumps/release-group/mbdump/release-group`). **An
artist is `thin` iff that count is 0.** Existence (vs. a deleted MBID) is established from
the **artist** dump — an artist with zero release-groups is *absent* from the release-group
dump, so that dump alone cannot tell "no releases" from "MBID no longer exists". This
carries the void session's pre-run reimplementation of the coverage gate.

### `TCR-G1` — instrument validation, externally anchored. Evaluated FIRST and ALONE.

**The redesign, and the order is the design.** `TCE-G1` failed because a threshold was a
guessed number; three of its four cells were simultaneously loose enough to pass almost
anything. Here every band is anchored on an externally measured value, and the steps
happened in this order, with the evidence committed:

1. **Validation artists were chosen for unambiguous catalogues** — an artist-name search
   returning exactly one exact-name match, so no known same-name collision can contaminate
   the ground truth. All five below pass that check (recorded in `g1_anchors.json`).
2. **Their release-group counts were fetched from the live MusicBrainz API FIRST** —
   before any band was set and before the dump counter ran against any of them
   (`builder/analysis/2026-08-06-tcr-thin-catalogue-rerun/g1_anchor_fetch.py`, output
   `g1_anchors.json`, fetch timestamp recorded there). The live endpoint (release-group
   browse by artist) counts the same thing the dump counter counts: release-groups on
   whose artist-credit the artist appears — the semantics under which the void run's
   independent check found exact agreement.
3. **Tight required bands were set around those live counts** (table below), with the
   drift tolerance stated and justified.
4. **This document is committed.**
5. **Only then does the counter run against them.**

| Cell | Artist | MBID | Live count (2026-08-06) | **Required of the dump counter** |
|---|---|---|---|---|
| zero-detection | Alana Haim | `3e308b4a-c8d0-4883-8c38-e2953002a882` | **0** | **== 0** |
| small nonzero | Andrew VanWyngarden | `0576e68e-2dd8-41ad-975a-09bdc44422b6` | **4** | **2 – 6** |
| moderate | Leon Bridges | `69d9dfd7-19b7-4a75-8a53-9f733fb5d774` | **37** | **35 – 39** |
| moderate | Khruangbin | `aea4c9b9-9f8d-49dc-b2ca-57d6f26e8634` | **59** | **56 – 62** |
| large | Radiohead | `a74b1b7f-71a5-4011-9441-d0b5e4122711` | **584** | **554 – 614** |

**Tolerance: ± max(2, ⌈0.05 · live⌉) for nonzero cells; the zero cell takes none.** The
dump is 8 days older than the live values, and eight days of editorial drift moves a
catalogue by at most a few entries — 5 % covers even a heavily edited catalogue at
Radiohead's scale. A *broken* counter errs by structure, not by drift: counting releases
instead of release-groups, counting recordings, or dropping a credit class all move a count
by factors, far outside every band. The zero cell is exact because zero-detection is the
point: `thin` is defined as exactly 0.

**Two cells are regression anchors and say so.** Leon Bridges' and Khruangbin's *dump*
counts (37, 59) are already on the committed void-run record, so those cells cannot
surprise; their bands were still set from the independently fetched live values. The
probative cells — where the dump counter has never touched the artist — are Alana Haim,
Andrew VanWyngarden, and Radiohead. **The anchor-choice lesson is itself on the record:**
Andrew VanWyngarden was selected as a *zero* candidate and the live fetch returned 4, which
is exactly the class of guess that voided `TCE-` — caught here by measuring before banding.

**The runner reads the anchor MBIDs and bands from the committed `g1_anchors.json` plus
this table, and records the source in its output** (same provenance rule as `TCE-AM2`'s).

**Any cell failing → the probe is VOID.** Not a weak pass, not a caveat. Void means no
outcome is computed and nothing is reported beyond the gate failure itself.

### Both Laura Lees are DEMOTED to reported run state — not gate cells

A known MusicBrainz mis-filing between the two Laura Lees — the *recording* of *Not Up for
Discussion* under the Khruangbin member, the *release-group* under the 1945 soul singer
(`builder/analysis/2026-08-06-tce-thin-catalogue/miscredit.json`) — contaminates them as
ground truth: `TCE-G1`'s zero cell passed *partly because* of it. **The run reports both
their dump counts as run state, with no pass/fail attached and nothing conditioned on
them.** They stay visible because the Khruangbin member is the motivating case; they decide
nothing.

### `TCR-G2` — coverage floor

**≥ 95 % of neighbours across the arm A reference set must resolve to existence in the
2026-07-29 MusicBrainz artist dump.** Below that, dump and archive describe different
populations and the probe is **VOID**. Between 95 % and 100 %, the figure is reported as
run state and unresolved neighbours are **excluded from both numerator and denominator**,
never silently counted as thin. Reference artists whose list falls below 30 entries after
exclusion leave the census, and every downstream quantity uses **post-exclusion** list
lengths — which discharges mitigation 3 by construction.

### `TCR-G3` — the pinning gate. Per arm, computed from run state before any `Δ_R` is read.

Carried from `TCE-AM1`/`AM2` unchanged. **Record the share of reference artists with
`T_R = 0`** (no thin neighbour anywhere in their list), per arm. **If that share exceeds
0.5 in an arm, `TCR-C1` is a mathematical constant there and NO read of it is licensed for
that arm** — not `enriched`, not `null`. `TCR-C3`–`C5` are unaffected and still read. If it
bars arm B, `TCR-C2` is reported as `no_read_licensed` and the §5 reads rest on
`TCR-C3`/`C4`/`C5` for that arm.

> **⚠ Expect arm B to be the one at risk, and that is not a failure of the run.** The drop
> filters remove artists with nothing of their own to play, which is close to this probe's
> `thin`. A pinned arm B is a finding about the filters, not a broken probe — reported as
> `no_read_licensed`, never as `null`.

## 4. Outcomes

**Every run-state quantity below is PER ARM** (`TCE-AM2`, carried in full): the attainable
ceiling `C`, the `T_R = 0` share, `TCR-C5`'s exact null, and the thin base rate each take
an arm A and an arm B value, written `C_A` / `C_B` and so on, computed from **that arm's
own** `(L_R, T_R)`. Reading arm B against arm A's numbers is a category error: arm A's
lists run to 100 entries, arm B's are capped at 50, and arm B has thin artists largely
removed by the filters that define the arm.

### 4.1 `TCR-C1` — the primary outcome

**Plain sentence (fixed):** *when the app looks at any artist's ten strongest connections,
are artists with nothing of their own recorded over-represented there compared with the
rest of that same artist's list?*

For each reference artist `R` (post-exclusion list, tie rule of §0.1):

```
p_top   = (expected) share of R's ranks 1-10 that are thin
p_rest  = share of R's ranks 11-end that are thin
Δ_R     = p_top − p_rest
```

**`TCR-C1` = the median of `Δ_R` across the reference set, per arm.** Its bands are a
function of run state, carried from `TCE-AM1` unchanged: let `C` be the **attainable
ceiling**, the median over reference artists of

```
min(10, T_R)/10 − (T_R − min(10, T_R))/(L_R − 10)
```

— what `Δ_R` would be if every thin neighbour were crowded into the top ten. `C` depends
only on `(L_R, T_R)`, so it is computable before any `x_R` is looked at.

| `TCR-C1` | Branch |
|---|---|
| **≥ 0.50 · C** | `enriched` |
| **0.25 · C to 0.50 · C** | `indeterminate` — deliberately NEITHER |
| **−0.25 · C to +0.25 · C** | `null` |
| **≤ −0.25 · C** | `depleted` |

**If `C < 0.10`, the scale is finer than the statistic's own lattice and `TCR-C1` is
reported as `no_resolution`, firing no branch.** The middle band names no default and none
may be supplied afterwards. The thin base rate is **run state**, recorded per arm before
`TCR-C1` is read; the committed drop-list class share (24.7 %) is an upper bound on it, not
an estimate of it.

### 4.2 `TCR-C2` — does it survive to what users see?

**Plain sentence (fixed):** *whatever the raw feed does, is it still there in the map the
website serves today?* **`TCR-C2` = `TCR-C1`(arm B)**, read against the same functional
form — fractions of **`C_B`**, never arm A's numeric bands. Stated separately because it is
the decision-relevant half.

### 4.3 The supplementary criteria, with exact nulls — carried from `TCE-AM1` unchanged

| Criterion | Definition | **Exact null** | Bands |
|---|---|---|---|
| **`TCR-C3`** *(primary supplement)* | census **mean** of `M_R = P(X < x_R) + ½·P(X = x_R)` under that artist's own central hypergeometric on post-exclusion `(L_R, T_R)` | **exactly 0.500**, for every base rate and list-length distribution | `≥0.55` enriched · `0.52–0.55` indeterminate · `0.48–0.52` null · `≤0.48` depleted |
| **`TCR-C4`** *(interpretation)* | `Σ x_R / Σ E[x_R]` | **exactly 1.000**, for every base rate | `≥1.5` enriched · `1.2–1.5` indeterminate · `0.8–1.2` null |
| **`TCR-C5`** *(locates concentration)* | share of reference artists with one-sided mid-p `≤ 0.05` | **base-rate dependent — computed exactly from the census's own `(L_R, T_R)` before any `x_R` is read**, per arm, recorded in §6 | ratio to that computed null `≥ 2.0` = concentrated |

**Plain sentences, fixed before any result exists** (quoted from `TCE-AM1`):

- **`TCR-C3`** — *pick an artist at random: how often does their real top ten hold more
  artists-with-nothing-of-their-own than a reshuffle of that same artist's own list would
  give? 0.5 is a coin flip.*
- **`TCR-C4`** — *across everyone, how many times more artists-with-nothing-recorded sit in
  top-ten slots than chance puts there? 1.0 is exactly chance.*
- **`TCR-C5`** — *what share of artists have a top ten too crowded with them to be luck,
  and how does that compare with the share you would get by luck alone?*

**The warned-against statistic, carried so nobody reinvents it:** the naive "share of
artists whose top-10 thin count exceeds its expectation" has a null of 0.33–0.48, not 0.5,
and moves non-monotonically with the base rate. `TCR-C3`'s mid-p form is the fix.

### 4.4 What the mean-based criteria COST, and the three mitigations — all owed, carried unchanged

`TCR-C1`'s blindness to a minority was also robustness; `TCR-C3`/`C4` give it up. Counting
release-groups classifies MusicBrainz editor accounts, placeholders and mis-merged MBIDs as
`thin`, and under a mean they contribute linearly and could produce the entire headline.

1. **Report `TCR-C5` alongside `TCR-C3`**, so "a small effect everywhere" is
   distinguishable from "a large effect in 2 % of cases".
2. **Read the actual top tens of the twenty reference artists contributing most to
   `TCR-C3`.** Metrics and eyeballs, not metrics alone.
3. **Feed the hypergeometric each artist's post-`TCR-G2` list length**, not its raw one
   (discharged by construction in `TCR-G2`, and verified in the run output).

**Pre-registered read of the eyeball check:** if same-name or mis-merged MBIDs dominate the
top contributors, that is **the open same-name POPULATION question surfacing**
(`2026-08-06-cocredit-investigation-execution-log.md` §6 item 1, left open by the Laura Lee
closure) — reported as such, **not as noise and not as the thin-catalogue mechanism
confirmed.** The two mechanisms are different and the eyeball read may not collapse them.

### 4.5 Descriptive, with NO pre-registered read

The gradient (`TCR-C1` at thin-thresholds 1, 2, 5, 10); the full `Δ_R` distribution, not
only its median; per-arm boundary-tie counts. **No branch reads these and they may not
rescue or overturn anything.**

## 5. The read of every result, including the null

**Every read presupposes the run state in §6. No read is licensed before it.**

- **`TCR-R1` — `enriched` in BOTH arms.** The mechanism is real and reaches users. Report
  to the owner with options; **adopt nothing.** Any follow-on is measurement of
  user-visible impact, never a scoring change — B1 established the similarity signal is
  load-bearing.
- **`TCR-R2` — `enriched` in arm A, `null` in arm B.** Something between the raw feed and
  the shipped map removes it (per §2, **not** attributable to the drop filters alone). The
  investigation closes; attribution would be a separate probe and is not owed.
- **`TCR-R3` — `null` in arm A, and it fires only when `TCR-C1` AND `TCR-C3` BOTH land
  null there** (if `TCR-G3` bars the `TCR-C1` read, it rests on `TCR-C3` alone and says
  so). The thin-catalogue hypothesis is wrong; three mechanisms are then ruled out, the
  owner's observation remains unexplained, and the co-credit investigation closes with the
  honest statement that we do not know what produces the class he saw. Arm B is still
  computed and reported; it cannot rescue a null arm A.
- **`TCR-R4` — `depleted` in arm A.** The opposite finding, with §0's confound named as
  the likely cause. Closes.
- **`indeterminate` in either arm** is reported as indeterminate. No branch fires, no
  default is supplied; a bar set afterwards is a new pre-registration.

### Barred reads — these travel with every citation of this document

1. **No adoption follows from any branch.** No default, weight, filter or threshold
   changes on this result.
2. **This does not reopen widening the drop rule.** Closed by the owner 2026-08-06.
3. **Release-group count is a proxy** for "how much of their own work exists" — not listen
   volume, not quality, and looser than the drop rule's sole-credited-and-substantial
   criterion.
4. **Enrichment at the top of a similar-list is NOT "appears in journeys".** This probe
   runs no journeys.
5. **A→B differences are not attributable to the drop filters alone** (§2).
6. **A contaminated-contributor finding from the eyeball read is the same-name population
   question surfacing, not this probe's mechanism confirmed** (§4.4).

## 6. Run state a read presupposes

**Every read in §5 presupposes ALL of the following, in this order. A read taken before
them is void.**

- **`TCR-G1` passed on all five cells**, evaluated first and alone, anchors read from the
  committed `g1_anchors.json`.
- **Both Laura Lees' dump counts recorded as run state** — reported, adjudicating nothing.
- **`TCR-G2` passed**, with the coverage figure and post-exclusion census sizes recorded.
- **The thin base rate computed and recorded per arm** before `TCR-C1` is read.
- **All per-arm run-state quantities computed before any `Δ_R` or `x_R` is read:** the
  `T_R = 0` share (`TCR-G3`), the attainable ceiling `C` (which fixes `TCR-C1`'s bands),
  and `TCR-C5`'s exact null — functions of list membership only, written to disk before the
  outcome pass, and the run records that ordering.
- **BOTH arms computed. Arm A alone licenses nothing** — not `TCR-R3`, not `TCR-R1`. If
  arm B is not run, the probe is incomplete and the correct report is "incomplete", never a
  partial read.
- **The `Δ_R` distribution recorded**, not only its median, and each arm's rank-10
  boundary-tie count recorded.
