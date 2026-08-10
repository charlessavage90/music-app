# `JFX-` — does the extended map put less famous artists into journeys?

**Role: PRE-REGISTRATION.** The git commit timestamp is the evidence that this preceded the
result; that is the part that cannot be reconstructed afterwards. **No arm runs before this
document and its pair set are committed.**

**Thresholds are SET, by the owner, 2026-08-09 — before any arm ran.** `JFX-G1b` is 67%
(§3). The draft's second placeholder was **withdrawn rather than filled**: `JFX-C2` gates
nothing, so a threshold on it would have decided in advance which differences the write-up
calls material, which is framing dressed as rigour. It is a report row, on the `MSW-V2`
precedent.

Governing: [`PRODUCT-REQUIREMENTS.md`](../PRODUCT-REQUIREMENTS.md) — every criterion here
is anchored on a `REQ-`, none invented. Operational context: plan Task 11 is complete and
stopped at its owner stop; this does not resume it.

**Identifier series `JFX-`** — collision-checked across every ref, zero matches.

**⚠ AMENDED by [`JFX-AM1`](#jfx-am1--the-critique-amendment-2026-08-09) — read it before
§2, §3 and §4, all three of which it changes.** `JFX-AM1` governs where it and the original
text disagree.

---

## `JFX-AM1` — the critique amendment, 2026-08-09

**Committed 2026-08-09, before any arm ran and before any outcome value existed.** No
artifact was built, no pair was routed, no fame statistic was computed. The only measurement
taken is a **static graph property** of the already-adopted artifact (`AM1.1` below), which
is an input to the design, not an outcome of it. **Nothing here is shaped by a result,
because there are none.**

Prompted by an `ml-graph-analyst` critique dispatched at the owner's instruction, plus two
owner corrections and two defects found by the controlling session. **Figures owned by
`builder/analysis/2026-08-09-jfx-prereg-critique/README.md` — cited, never restated.**

### `AM1.1` — the `S1` stratum STAYS in the gate. A proposal to remove it is WITHDRAWN.

The critique proposed removing the famous–famous stratum from `JFX-G1`, on
`PRODUCT-REQUIREMENTS.md` §8's record that *"superstar endpoints have zero edges below the
top popularity decile"* and REQ-37 is *"unachievable on famous-to-famous pairs at any router
setting"*.

**That claim does not transfer, and the proposal was wrong.** It was measured on the
**pre-`MSW-`** artifact under **mutual k-NN**, in **popularity** currency, under the
**retired** worldly-fame construct. Measured on the adopted artifact: in fame currency —
which is what this document scores on — **1.07% of top-decile artists have zero
below-decile neighbours, and at the top 0.2% it is 0.00%**, median 8.

**⚠ `DD-F1` is NOT refuted, and the halves must not be collapsed.** In *popularity*, at the
top 0.2%, **44.07%** of artists still have zero such edges. The finding survives where it
was measured and fails to transfer — exactly the §2.6/§2.11/§2.12 currency trap. **Do not
record `DD-F1` as overturned.**

**⚠ This measures STRUCTURE, not ROUTING.** It licenses "famous endpoints *can* descend",
never "journeys *do* descend" — which is what `JFX-G1` exists to measure.

**All 300 pairs stay. §2's strata are unchanged.**

### `AM1.2` — the fame quantity is LOG-SCALED. Owner decision, 2026-08-09.

**§2's currency rule is amended: the primary statistic is `log10(1 + fame_lb)`, not raw
`fame_lb`.** The `1 +` guards a zero listener count, which is a legitimate non-null value
distinct from a measured absence (`FAM-AM1.8`); at the values in play the distortion is
negligible.

**Why.** Raw counts span 1 to 455,551. A pooled median over three strata is a rank
statistic, so it lands inside `S2` and movement in `S1` or `S3` is invisible to it. Log is a
**fixed monotone transform of the value**, independent of population — so it satisfies §2's
currency rule's *reason* exactly as raw does, and unlike percentile — while making the three
strata commensurable and making `G1b` a ratio of fold-changes.

**⚠ This is not "raw" and it changes what passes**, which is why it is an owner decision and
why it is recorded here rather than applied silently. **Percentile currency remains barred**
(§2, unchanged): cross-arm percentile comparison compares two rulers.

**Consequence for `G1b`, and it is the reason the bar is untouched.** The 67% bar was set on
the translation *"no more than 50% more presses"*. Under raw counts a constant per-press
*proportional* decline is strongly concave, so 67% of the raw drop is reached in a handful of
presses and the bar is far looser than 30 presses. Under log, constant per-press work is a
straight line and the translation holds. **The switch repairs the bar rather than disturbing
it. `G1b` stays at 67%** (see `AM1.9` for what remains).

### `AM1.3` — the instrument is NAMED. Nothing in this document was well-defined without it.

The original fixed the depths, pairs, statistic and criteria, and never said **how a
depth-20 journey is produced**. Each unstated choice changes the primary number.

- **Routing:** `find_journey` semantics, not `find_path`. `cre_ladder.journey()` mirrors it
  deliberately; the committed `walk` helpers mirror `find_path` and "silently unread exactly
  the pairs union arms make adjacent". Both arms are `trimmed_union` with **different**
  adjacency, so a `find_path` harness would drop a different pair set per arm — selection on
  the outcome, in a paired design.
- **Press selection:** the existing convention, `cre_ladder.victim_key` — highest-fame
  interior artist first — **cited, not retyped**.

  **⚠ Named as a limitation, because it is one.** A real user presses whichever card they
  happen to know, which is not this. Under `victim_key` a fame decrease is *partly
  mechanical*: the most famous interior is being deleted twenty times. **`JFX-G1a` is
  therefore a weak test in the absolute** and its force comes almost entirely from the
  **between-arm** comparison in `G1b`, where the mechanical component is present in both arms
  and cancels. **No read may present `G1a` passing as evidence the product works for a
  user.**
- **Ruler frame:** the **production** frame — `graph_store.fame_percentiles`, ranked against
  the served artifact's own population — because §0.1(a)'s confound is a statement about what
  the API does. The `cre_common` frame is fixed against an external snapshot (`FRAME_N =
  74_151`) and would make §0.1(a) **false and uncheckable**.
- **Precondition:** if the CRE mirror supplies any routing code, `CRE-G1(a)`'s byte-identity
  against today's `api/src/artistpath_api/pathfinding.py` is **re-verified first**. The mirror
  was verified 2026-08-03; the seventh cost term landed 2026-08-05.

### `AM1.4` — raw fame is NOT reachable from the serving store.

§2's parenthetical *"in-memory `fame_lb_raw`"* names a **builder** field
(`Graph.fame_lb_raw`). `GraphStore` computes `fame_lb_pctl` at load and **discards the
values** — *"the raw counts are not kept, since nothing routes on them"*. The harness reads
raw fame from the **artifact's APG1 metadata blob** (`fame_lb` key) directly. Found by
writing the code, not by reading the spec.

### `AM1.5` — the pooling is stated, and `G1b` gets an interval that behaves.

**Pooling.** §2 defines the statistic as the paired median *of per-pair differences*; §3
stated the gate over *four pooled levels*. These are different statistics and this project
has already had a **sign flip** from exactly that (`DD-P3H-2`: −0.158 as scored, +0.076 /
+0.020 / +0.020 under three other poolings). **`G1a` and `G1b` are both computed on the §2
definition — the paired median of per-pair differences.** Per-stratum `G1b` ratios are
reported beside the pooled figure as diagnostics.

**`G1b` as a linear contrast.** `R = D_B / D_A` is a ratio whose behaviour is governed by its
denominator's signal-to-noise `t_A`; simulated at n=100, a **genuinely equal** map is
declared broken **42%** of the time at `t_A = 1` and 22% at `t_A = 2`, with the interval
spanning negative values. For `D_A > 0`, `R ≥ 0.67` is algebraically **identical** to:

> **`T = D_B − 0.67 · D_A ≥ 0`**

`T` is a linear contrast, always bounded, and free: the design is already paired across arms
on the same pairs, so one **joint** bootstrap resamples pairs carrying both arms and all four
depths together and recomputes `T` per replicate. **Same bar, same point estimate, same
pass/fail on the point estimate.** Pre-registered: the one-sided bootstrap interval on `T`.
**Report `R̂` as a point estimate; report the interval on `T`, never on `R̂`.**

**`D_A` viability clause — a case the original had no branch for.** The equivalence holds
**only when `D_A > 0`**, and nothing tested it. **`t_A` is reported. `G1b` is evaluated only
when `D_A`'s own bootstrap interval excludes zero.** If it does not: `G1b` is **undefined,
not passed and not fired**, the report says so in those words, and the adoption question
falls to `G1a` plus the gradients. *(This is a live possibility, not a corner case: the ramp
weight is 0.01, and `AM1.9`'s floor exhaustion removes the stronger device after press five.)*

### `AM1.6` — `G1a`: one simultaneous band, and its REQ anchor is corrected.

**The `REQ-37` classification in §3 is WRONG.** §3 states *"REQ-13 and REQ-37 are **Musts**"*.
`REQ-13` is a Must (`PRODUCT-REQUIREMENTS.md` §8, `### Must`); **`REQ-37` is under `###
Expect`**. **`JFX-G1` stands on `REQ-13` alone.**

That matters beyond bookkeeping: `REQ-13`'s wording is a **trend** claim, which licenses the
overall d0→d20 test and **does not license** a requirement that every consecutive step be
non-increasing. The step tests were the half with no anchor *and* the statistically risky
half.

**Multiplicity.** Three step tests plus an overall test, correlated, at nominal coverage:
simulated false-stop rate under a **truly flat** gradient is **7.5–8.2%** against a nominal
5%. **Amended: the three steps are evaluated against a SIMULTANEOUS band via the
max-statistic**, from the same joint bootstrap as `AM1.5` — family-wise error 5%, no extra
data, no extra runs, and less conservative than Bonferroni because it uses the observed
correlation. The overall d0→d20 clause is unchanged.

**Effect size on the step-failure clause.** The original had none, so a rise of three
listeners could stop the adoption — while the estimator's own home (`ulc_exposure.branch()`)
pairs "CI excludes zero" with `EFFECT_PP`. **Amended: a step fails only if its simultaneous
interval excludes zero AND the rise is at least 0.02 in log10 units** (≈ a 4.7% increase in
listener count). Set here, before any arm ran, as the smallest rise that is not measurement
grain; it is deliberately small because this is a catastrophe guard.

### `AM1.7` — `C6` and `C7` get effect sizes, because both fire branches.

§4's reads 7 and 8 fire on the words *"materially more"* and *"materially higher"*, undefined.
Read 7's consequence is that **every one-knob reading in the document is void** — the most
expensive branch here, firing on an undefined trigger. This is the Track 2 A0-vs-P pattern
(`CLAUDE.md`: *"every gate and branch trigger needs its own effect size"*).

The gradients `C1`/`C2`/`C3` correctly have **no** thresholds — REQ-42 makes the obscurity
requirement a gradient with no absolute floor, and §3 argues that explicitly. **`C6` and `C7`
are not gradients; they are validity checks whose branches fire consequences.**

- **`JFX-C6` fires read 7** when the share of paths with a non-zero floor term is **at least
  5 percentage points higher** in `JFX-B` than in `JFX-A`, at any depth.
- **`JFX-C7` fires read 8** when the null share among interior artists is **at least 2
  percentage points higher** in `JFX-B` than in `JFX-A`, at any depth.

Both set before any arm ran. Both are "is this reading contaminated" bars, so they are set
low.

**Read 8 also becomes depth-conditional.** `graph_store.fame_percentiles` assigns
`fame_lb_pctl = 0.0` to null-fame artists, so a null-fame artist pays **zero** ramp toll and
is the cheapest possible interior at every depth — while §2 **excludes** it from the outcome.
As `k` rises the ramp's toll spread grows and pulls routes onto exactly the artists the
statistic discards. **So: if the null share among interiors RISES WITH DEPTH in an arm, that
arm's measured gradient is attenuated and the report must say so.** The original framed this
as a between-arm level difference only.

**`REQ-Q1(a)` is now satisfied, and was not.** It requires any fame-currency scored criterion
to be *"always reported twice — all interiors and matched-only"*. **Added: the primary
statistic is recomputed over journeys with zero null interiors, alongside the headline.** The
`DD-D8` precedent is why this is not cosmetic — there, ~45% of a passing arm's effect was
carried by artists at the fame floor. *(`REQ-Q1(b)`'s A11 notability guard is from the retired
worldly construct; flagged as possibly inapplicable, not asserted either way.)*

### `AM1.8` — three corrections to §0, §2 and `C5`.

- **The intervention is FOUR changes, not three.** §0.1 lists the drop flags as held
  constant because they are `True` in both — but the **payload differs**, and
  `2026-08-09-cex-recensus/README.md` measures **32 artists newly dropped and 30 no longer
  dropped** on the shared population, because `ULF-` re-resolves clip availability. Up to 32
  artists can be absent from `JFX-B` for a reason that is **not the crawl extension**. Moved
  out of "held constant" into §0's intervention list.
- **`C5`'s population is the 58,746 artists WITH a measurement**, not all 58,838 — implied by
  §2's null rule, unstated in `C5`. **And `C5` is a catastrophe guard, not a detector:** under
  a hypergeometric null it fires at 4.5 sd (p ≈ 3e-6), and the loss the mechanisms actually
  produce is of **obscure, low-degree** artists, which `C5` is structurally blind to. **Added
  as a report row: the direct count `|A \ B|`**, which no criterion currently owns.
- **The two null shares in §2 are not comparable as written** — 0.16% is a *post-filter*
  artifact rate, 6.3% is a *pre-filter* archive rate. `JFX-B`'s post-filter share is likely a
  few tenths of a percent. Stated so `C7` is not read against the wrong expectation.

### `AM1.9` — measured: the obscurity floor is spent by press five.

`effective_floor_raw` subtracts `floor_relax_known = 0.15` per press from
`min(pop_raw[source], pop_raw[target])`, clamped at zero. Over the committed candidate pairs
the floor is **fully relaxed by press five for 96–100% of pairs in every stratum**.

**Consequence, binding on §4:** the four depths do **not** sample one mechanism. `d0→d5` has
two devices; `d5→d10` and `d10→d20` have the fame ramp and accumulating exclusions only.
**No read may treat the three steps as homogeneous.**

**And it bears on the 67% bar's reasoning.** §3's caveat said the gradient *"may be"*
front-loaded; it **is**, by construction. `AM1.2`'s log switch removes the arithmetic
component of that; the mechanical component remains, so 67% still corresponds to somewhat
more than 30 presses. **The bar is UNCHANGED** — it is a "the map is broken" bar, and leniency
on a stop-gate sends marginal maps to the owner as a judgement call rather than auto-rejecting
them. **Added instead: the report states the REALISED press-count equivalence beside the
ratio**, so the translation the bar was set on becomes a measured quantity rather than an
assumption.

### `AM1.10` — the estimator wrapper, and the reported units.

`paired_median_ci` (`ulc_exposure.py:72`) multiplies by 100 and names its outputs
`median_diff_pp` / `ci95_pp`, because `ULC-`'s statistic was a share. **JFX's is not**, so as
imported it reports a true difference of 800 as **80,000 "pp"**. The estimator itself is
sound — percentile bootstrap of the median of paired differences, correct index convention,
10,000 draws.

**Amended:** a thin wrapper in the JFX analysis directory divides by 100 and renames the
keys; the frozen script is **imported, never edited**. `BOOTSTRAP = 10_000` is a module
global and comes along with the import.

**A per-statistic seed is pre-registered**, derived from the statistic's own name, so a
result is reproducible from its name alone with no harness state involved.

> **◐ This clause originally justified the seed by claiming a shared `random.Random` would
> "silently change every later interval". Measured, and it does NOT — the claim was
> overstated and is corrected here rather than quietly dropped.** The bootstrap distribution
> of a median over n≈40 is highly discrete, and 10,000 replicates converge the percentiles
> onto the same order statistics whatever the RNG offset; forward and reverse call order give
> **identical** intervals. The mechanism is real and reappears at 50 replicates, which is
> what the test asserts. **So the seed is kept for reproducibility, not because it repairs a
> live defect** — and `test_jfx_stats.py` will fail if the negligibility ever stops holding.

### `AM1.11` — §4 gets a read for the median and the mean disagreeing.

§2 promises both at every depth and calls a divergence *"a finding, not a discrepancy to
reconcile"*; §3 decides the gate on the **median only**; §4 has no branch for them
disagreeing. Simulated, the median has **essentially zero power** when fewer than 50% of
pairs change, with a cliff at exactly 50% — so a concentrated effect produces a **false
stop**, not a false pass.

**Added as read 9:** where the median is null and the mean's interval excludes zero (or the
converse), the report states it explicitly and reports both. **The gate remains decided on
the median** — promoting the mean would change what passes and is the owner's call, not a
bookkeeping fix.

### `AM1.12` — §1's build script did not exist.

§1 says the artifact *"is built by a script that runs `check_acceptance`, CATCHES the
rejection, records it verbatim in the manifest, and serialises anyway"* — present tense, for
something that had never been written. `check_acceptance` exists
(`builder/src/artistpath_builder/acceptance.py:187`) and every caller lets the rejection
propagate. **Written as part of this amendment**; §1's tense is now true.

---

## §0 Factor table

| Arm | Artifact | Archive | Nodes | p99 scale | Isolating baseline |
|---|---|---|---|---|---|
| **`JFX-A`** | `graph-msw-tu50.bin` (adopted) | ALG-B @ 75,000 | 58,838 | 850 | — (reference) |
| **`JFX-B`** | `graph-cex-117k.bin` (to build) | ALG-B @ 117,302 | 88,685 | 769 | `JFX-A` |

**`JFX-B`'s baseline differs by more than one column, and that is deliberate and stated
rather than hidden.** The intervention is *the extended crawl*, which is inseparably three
changes: ~30k new artists available as waypoints, new edges attaching to existing artists,
and every similarity reweighted by the p99 shift. **No arm here isolates them.**

**This is the right design for the question asked** — *what does a person get now* — and the
wrong design for *what did adding artists cause*. A third arm isolating the reweighting
(old archive, p99 forced to 769) would be needed for the second question and **is not run
here**. No read below may attribute an effect to "adding artists" specifically.

## §0.1 Held constant, and why each is genuinely constant under the intervention

| Held | Why the intervention cannot change it |
|---|---|
| Every `ApiConfig` cost weight | Read from config, not from the artifact; both arms served by the same code |
| Cap rule (`trimmed_union`, j=50, ceiling=50) | Set in `BuilderConfig`, identical in both builds |
| All three drop flags | `True` in both; `JFX-B` uses its own censused payload via `--unlistenable-list` |
| The pair set | Fixed and committed before either arm runs (§2) |
| Bypass semantics | Frontend/router behaviour, untouched by either artifact |

### ⚠ Two things are NOT constant, and one of them undermines a naive read of Q3

**(a) The fame ruler changes between arms, and the depth mechanism is priced on it.**
`w_known_ramp_fame_pctl` is priced in **fame percentile**, and percentile is ranked against
**the served artifact's own population**. The two arms have different populations, so *the
same artist has a different percentile in each*. The `known` ramp is the depth mechanism —
so depth behaviour differs between arms partly because the ruler moved, not because the
map got bigger.

This **cannot be removed without departing from what the API actually does**, so it is
accepted and named. Consequence, binding on §4: **`JFX-G1` measures whether the extended
map delivers a depth gradient, never whether adding artists caused a change in it.**

**(b) `w_floor` is dormant in `JFX-A` for a reason `JFX-B` may remove.** The floor term
fires when a path dips below the obscurity floor; `w_jump` normally prevents that. The
extended map makes many more obscure artists available to dip *to*. This is the Track 2
dormant-term pattern exactly: a term inert in the baseline for a reason the intervention
removes is not a constant.

**So it is measured, not assumed.** Both arms report the share of paths where the floor
term is non-zero (`JFX-C6`). If it fires materially more in `JFX-B`, every one-knob reading
below is void and must say so.

## §1 The artifact

`JFX-B` needs `graph-cex-117k.bin`, which does not exist: acceptance rejected before
serialising (artists 88,685 against [47,000, 71,000]; edges 1,618,164 against
[1,050,000, 1,580,000]).

**It is built by a script that runs `check_acceptance`, CATCHES the rejection, records it
verbatim in the manifest, and serialises anyway.** The gate is not modified and the bounds
are not widened.

**The artifact is byte-identical to one `cmd_build` would emit after a bounds change** —
the build is deterministic (spec §9), demonstrated 2026-08-09 when the snapshot rebuild
reproduced the adopted artifact exactly. **So if these results support adoption, this
artifact is the one that ships; no rebuild is required.** Adoption remains a separate
owner decision about the bounds.

## §2 The pair set — fixed before any arm runs

- **Analysed population:** the **intersection** of both artifacts' node sets. A pair with an
  endpoint missing from either arm is not comparable and is excluded.
- **300 pairs analysed, 100 per stratum**, stratified on endpoint fame measured in `JFX-A`
  (a fixed ruler chosen before results exist, per §0.1(a)):
  - **`S1` famous–famous** — both endpoints in the top 10% by `fame_lb`
  - **`S2` mixed** — one in the top 10%, one in the bottom 50%
  - **`S3` obscure–obscure** — both in the bottom 50%

**⚠ The intersection cannot be computed yet, because `JFX-B` does not exist — so selection
is fixed in two stages, and neither stage leaves any discretion.**

1. **Now, before the artifact is built:** draw **150 candidate pairs per stratum** from
   `JFX-A`'s node set with seed **20260809**, sorted by MBID before sampling so the draw does
   not depend on dict ordering. **This list is committed alongside this document** as
   `jfx_candidate_pairs.json`.
2. **After `JFX-B` is built:** walk the committed list **in its committed order** and take
   the **first 100 per stratum whose endpoints are present in both artifacts.** Report how
   many candidates were skipped — a non-trivial number is itself a finding, since it means
   the extension *removed* artists the adopted map has.

**Over-selection exists so a shortfall cannot become a reason to draw more.** Topping up a
stratum after seeing which pairs survived would be selection on the outcome. If any stratum
cannot reach 100 from its 150 candidates, **the shortfall is reported and the stratum runs
short** — no redraw.
- **Depths:** `known` = **0, 5, 10, 20**. `d5` is included because REQ-18 requires novelty
  within a handful of presses, not dozens.

**Currency rule, binding:** the primary statistic uses **raw fame** (the wire key `fame_lb`;
in-memory `fame_lb_raw`), never `fame_lb_pctl`. Percentile is population-relative and
comparing it across two populations compares two different rulers — the error `CLAUDE.md`
records as having caused three wrong conclusions here.

**Null rule, binding, and it carries a known bias direction.** A null fame value is a
**measured absence, never a floor** (`FAM-AM1.8`) and must not be coerced to 0 — doing so
would file every unmeasured artist as maximally obscure. So:

- Artists without a measurement are **excluded from the endpoint pool** (they cannot be
  placed in a fame stratum) and **excluded from the interior fame statistic**.
- **The null share among interior artists is reported per arm and per depth (`JFX-C7`).**

**The two arms are expected to differ here, and the direction is stated in advance so it
cannot be spun afterwards.** The adopted map carries 0.16% nulls (92 of 58,838), while the
`CEX-` fame fetch returned nulls for 6.3% of newly fetched artists — though most of those
are also un-listenable-filter candidates and may not survive into `JFX-B`. Unmeasured
artists are disproportionately obscure, so **excluding them pulls the median fame UPWARD in
whichever arm has more of them.** If `JFX-B`'s null share is the higher, the bias runs
**against** the extension: a `C1` result showing interior fame going *down* would be
strengthened by it, and one showing fame going *up* is partly attributable to it and must
say so.

**Statistic:** paired by pair, both arms. Median interior fame per journey, then the paired
median difference with a bootstrap CI, importing `paired_median_ci` from the frozen `ULC-`
script rather than retyping it. **Interior** = the path minus its two endpoints.

**`ULC-R1`'s known statistic defect is inherited deliberately:** where a class is
concentrated in a minority of journeys, the paired median can read zero while the mean
moves. **Both are reported at every depth**, and a divergence between them is a finding,
not a discrepancy to reconcile.

## §3 Criteria

Each carries its plain-language sentence, fixed here, before any result exists. Owner-facing
text must quote the sentence beside the identifier.

| ID | Plain sentence | Type | REQ |
|---|---|---|---|
| **`JFX-G1`** | *Does pressing "dig deeper" still keep making the middle of the journey less famous, press after press?* | **GATE** | REQ-13, REQ-37 |
| `JFX-C1` | *On the bigger map, is the typical artist in the middle of a journey more famous or less famous than before?* | gradient | REQ-10, REQ-42 |
| `JFX-C2` | *Does that answer differ depending on whether you picked two famous artists or two obscure ones?* | gradient | REQ-34 |
| `JFX-C3` | *Do journeys get longer — and if they do, do they buy more discovery for it?* | gradient | REQ-11, REQ-21, REQ-23 |
| `JFX-C4` | *How many more artists can now appear in a journey at all, or be found in search?* | report | — |
| `JFX-C5` | *Have famous artists been pushed out?* | **FLOOR** | REQ-33 |
| `JFX-C6` | *Did the obscurity-floor rule start firing on the bigger map when it never used to?* | validity check | §0.1(b) |
| `JFX-C7` | *How many artists in the middle have no listener measurement at all, and does that differ between the two maps?* | validity check | §2 null rule |
| `JFX-M1'` | *How often is a hop chosen by a tie-break rather than by how similar two artists actually are?* | report | — |

### `JFX-G1` — the only pass/fail, and its effect sizes

REQ-13 and REQ-37 are **Musts**, not gradients: repeated bypasses must increase delivered
novelty. If the extended map breaks the depth gradient, that is a stop **regardless of how
many artists it adds** — the gradient is the product.

- **`G1a` (absolute).** On `JFX-B`, median interior fame must be **non-increasing** across
  d0 → d5 → d10 → d20, and fame(d20) must be below fame(d0) with the bootstrap CI excluding
  zero. **Fails if any step rises with its CI excluding zero.**
- **`G1b` (relative).** `JFX-B`'s total d0→d20 fame decrease must be at least **67%** of
  `JFX-A`'s. **Fires below that.**

  **Owner-set, 2026-08-09, on this translation** — recorded because the reasoning is what a
  later reader needs, not the number. The bar is equivalent to asking *how many presses may
  it take on the new map to reach the distance twenty presses reaches today*: 67% ≈ **no more
  than 50% more presses** (20 → 30). It is anchored on **REQ-18** (novelty within a handful
  of presses, not dozens): at 67% a 10-press journey becomes 15 and stays a handful, whereas
  the draft's 50% would make it 20 and put it in the dozens REQ-18 rules out. **The session
  proposed 50%, then argued against its own number** on that REQ-18 reading; the owner set
  67%, conditional on the measurement being taken at 20 presses, which it is (§2).

  **This is a "the map is broken" bar, not a "the map is worse" bar** — it stops adoption.
  Disappointing-but-not-stopping is what the reported gradients are for.

  *Caveat on the translation, not on the test: press-count equivalence assumes the gradient
  is roughly even across presses, and it may be steep early and flat later. The test is on
  the total d0→d20 drop. The press framing exists to make the bar intuitive, not to redefine
  it.*

### The gradients — thresholds deliberately absent, and why that is not a gap

**REQ-42 states the obscurity requirement is a gradient that sets no absolute floor.** So
`JFX-C1`, `C2` and `C3` carry **no bar**, by design and by requirement.

**What is pre-registered instead is the measurement and the reservation:** the statistic,
the depths, the strata, the direction that counts as better, and — stated here in advance —
that **the trade between coverage gained (`C4`) and any interior-fame cost (`C1`) is the
owner's judgement at read time.** Declaring the reservation in advance is what makes this a
pre-registration rather than a gap that gets filled once the numbers are in.

**`JFX-C2` carries NO materiality threshold, deliberately.** The draft proposed one (a sign
flip, or a 2× magnitude difference) and it was **withdrawn before commit** on the owner's
agreement. `C2` gates nothing and fires no branch, so a threshold could only decide in
advance which differences the write-up would call material — framing dressed as rigour.
Precedent: `MSW-V2` is recorded as *"a report row, not a gate — no threshold was
pre-registered and none was supplied."*

**Instead: all three strata are reported side by side with their confidence intervals**, and
the reader draws the comparison from the numbers. This is a deliberate narrowing of what
the document decides in advance, not an omission.

**`JFX-C3` read, fixed here per REQ-11/REQ-21:** a length increase is acceptable **only**
where the same stratum also shows an interior-fame decrease. Longer *and* more famous is a
loss on both counts and needs no threshold to read as one.

**`JFX-C5` floor**, per REQ-33: at least **95%** of `JFX-A`'s top-1%-by-fame artists must
still be present in `JFX-B`. Below that, the system is eliminating famous artists.

## §4 The read of every result, including the null

Each read names the run state it presupposes.

**Presupposes: all 300 pairs routed in both arms at all four depths, with `JFX-C6` and
`JFX-C7` both reported.** A read taken before either validity check is available is not
licensed by this document, however clean the headline numbers look.

1. **`G1a` fails** → **stop.** The extended map breaks a Must. Nothing else in this document
   can license adoption, and `C1`/`C4` gains do not offset it.
2. **`G1a` passes, `G1b` fires** → the gradient survives but is materially shallower. **Owner
   decision**, and the exposure map for it is `C1` × `C2` — is the shallowness everywhere, or
   confined to one stratum?
3. **`G1a` and `G1b` both pass, `C1` shows interior fame DOWN** → the extension delivers the
   product goal and adds artists. The trade is not in tension; adoption is a straightforward
   owner call.
4. **Both pass, `C1` shows interior fame UP** → the tension he anticipated: more artists
   available, but journeys skew more famous. **No threshold decides this** (REQ-42); it is
   reported with `C4` beside it and the trade is his.
5. **Both pass, `C1` null** → the map got bigger and journeys did not measurably change. This
   is a real and likely outcome, and it is **not** a failure: `C4`'s coverage gain stands on
   its own, and search coverage is unaffected by routing at all.
6. **`C5` fails** → stop, independent of everything above. REQ-33 is not tradeable.
7. **`C6` shows the floor firing materially more in `JFX-B`** → **every reading above is
   void as a one-knob attribution** and the report must say so in those words.
8. **`C7` shows a materially higher null share in `JFX-B`** → the fame comparison carries a
   known upward bias in `JFX-B` (§2). Reads 3 and 5 survive it and are strengthened by it;
   **read 4 must state that some of the apparent fame increase is the bias, not the map.**

### The two criteria that fire no branch, stated here so neither is orphaned

**`JFX-C4` and `JFX-M1'` are reported under every read above and trigger none of them.** They
carry no threshold and no branch **by design**, not by omission:

- **`JFX-C4` (coverage)** is one half of the trade §3 reserves to the owner. It is reported
  beside `C1` in reads 3, 4 and 5, and it is the reason read 5's null is not a failure.
- **`JFX-M1'` (post-cap saturation)** is the repair of a separate instrument — `CEX-M1`'s
  pre-registered saturated-edge share is vacuous by construction, and this measures the same
  question where it is not. **It bears on no `JFX-` criterion and licenses no `JFX-` read.**
  It is collected here only because the artifact this design builds is the one thing that can
  supply it. **Presupposes: both arms built.** Reported for both, never compared to
  `CEX-M1`'s rescale-time figure, which is measured at a different pipeline stage.

**`JFX-C3`'s read rule lives in §3 and is not repeated here** — a length increase counts only
where the same stratum also shows an interior-fame decrease. It is an interpretation rule
spanning every outcome rather than a branch of any one, which is why it sits beside the
criterion; **this pointer exists so a reader working through §4 does not miss it.**

## §5 What this design cannot support

- **Any claim that *adding artists* caused an effect.** §0 — the arms differ by three things.
- **Any claim about coherence or whether journeys sound good.** No listening is involved. A
  fame improvement is not a quality improvement; REQ-9 puts novelty behind coherence, and
  nothing here measures coherence.
- **Any cross-arm comparison in percentile currency.** §2.
- **Anything about `JFX-A` vs the pre-`MSW-` world.** Out of scope.

## §6 Reserved to the owner

- ~~Both `⚠ OWNER` thresholds above, before this is committed.~~ **DONE 2026-08-09:**
  `G1b` set to 67%; `C2`'s threshold withdrawn as inappropriate to a report row.
- The `C1`/`C4` trade at read time (declared in advance, per §3).
- Whether to widen the acceptance bounds, which is what adoption requires. `MSW-G3` is the
  precedent and there too it was his.
- Whether to build the artifact at all (§1).
