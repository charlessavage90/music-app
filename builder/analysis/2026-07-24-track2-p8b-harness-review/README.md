# P8b — `ml-graph-analyst` review of the Track 2 Stage A harness

**Role: ACTIVE analysis record. Owns its figures.** Discharges pre-registration
[`specs/2026-07-23-track2-preregistration.md`](../../../docs/superpowers/specs/2026-07-23-track2-preregistration.md)
§7's **P8b**, the review of the *harness* (P8, the protocol review, is already discharged).
Scope is **derivation, not judgement**: whether the instrument measures what §2 pre-registered
and whether any arm provably cannot move. It says nothing about whether the experiment is
worth running, which candidate to adopt, or how the owner should weigh anything.

**Figures rule.** No figure from
`docs/superpowers/findings/2026-07-21-scoring-adjudication.md`, from
`builder/analysis/2026-07-24-track2-arm-scorer/README.md`, or from either fame-proxy
directory is restated here — those are cited. Every number below is measured by a script in
this directory and is owned here.

**Artifact.** Everything is measured on **`graph-t15-tiebreakfix.bin`**, sha256
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` (asserted by every
script; identity record in `findings/2026-07-23-tiebreak-fix-adoption.md`). Measured off that
artifact: **N = 74,193**, **E = 898,006 directed** (449,003 undirected), degree min 1 /
median 9 / mean 12.10 / p99 44 / max 50.

**No experimental arm was run.** Arm **P** (production) was walked and scored — explicitly
permitted, since P's paths are already in the record and running it is validation. The mirror
byte-identity gate was re-run. `A0`–`A7`, `A1u`, `X`, `T1a`, `T1b`, `FL1`, `FL2` were **not**
run and no unfiltered grid was run.

---

## Scripts

| Script | What it settles | Output |
|---|---|---|
| `probe_artifact.py` | artifact identity/shape; whether `sim >= 1.0` and `sim == 1.0` select the same edges; the A3 mean-matching ratio; duplicate names; **X's bounding claim**; toll magnitude arithmetic | `probe_artifact.json` |
| `probe_name_keying.py` | how exposed the harness's name-keyed fame table is to the artifact's non-unique and blank names | `probe_name_keying.json` |
| `probe_floor_lifetimes.py` | at which snapshot depths each arm's floor term is alive — raw (P) and percentile (FL1/FL2) | `probe_floor_lifetimes.json` |
| `probe_c2_headroom.py` | C2's discriminating power and per-pair margins to `B_unk`, on P | `probe_c2_headroom.json` |
| `probe_c1_sensitivity.py` | whether C1's mean clause can be bought by the absence-as-fame-floor encoding on a minority of cells | `probe_c1_sensitivity.json` |
| — | P's paths / fame / scores, produced with the committed harness unmodified | `paths_P.json`, `fame_P.json`, `scores_P.json` |

Commands are in each script's docstring. All run from `api/` with `UV_LINK_MODE=copy` and
`PYTHONIOENCODING=utf-8`.

---

## Bottom line on the gate

**Fit to run stage 1 as-is. Not fit to run stage 2 — the harness has no executable path for
the four attachment arms (F3).** Two findings must be *stated* before the stage-1 result is
read (F5 on X, F7 on the FL arms) because they change what a read is licensed to conclude;
one (F2) must be wired before a C2 pass on any candidate can be trusted, and it can be wired
after the arms run because it is a scoring-path change and re-scoring costs nothing.

Nothing found here invalidates the mirror, the arm definitions, the uniform-drop rule, or the
fame encoding.

---

## Findings

Severity is about the evidence, not the effort. **BLOCKS** = an arm should not run, or a
result cannot be read, until it is discharged.

### F1 — C2 is dominated by C1 on this pair set; it is a one-sided regression guard, not a discriminator. MEDIUM. Does not block.

**Measured.** P's C2 count equals the threshold minimum exactly, reproducing the arm-scorer
README's flagged figure. New here — the margins. P's four non-reaching analysis pairs sit
**0.0985, 0.2034, 0.2571 and 0.7344 log10** above `B_unk` (Madonna → Bob Dylan, Miles Davis →
Daft Punk, Muse → Coldplay, Radiohead → The Beatles respectively; `probe_c2_headroom.json`).
P's per-pair d15/d20 interior **median** fame runs 4.651–6.651, and a uniform −1.0 median drop
— C1's own threshold — puts the median below `B_unk` on **7 of the 8** analysis pairs
(`probe_c1_sensitivity.py` and the per-pair table in `probe_c2_headroom.json`).

**What this means.** Any arm that meets C1 uniformly satisfies C2 by construction on seven
pairs, against a C2 requirement of four. So C2 supplies no evidence that a candidate is
better; it can only fail one that reaches **fewer** pairs than production. That is a useful
regression guard and a poor discriminator.

**The consequence for §3.** Attack 1 — the famous ladder — is **not** closed by C2 on this
pair set. A ladder that leaves P's four reaching pairs alone passes C2 unchanged while
stepping the other four down within fame. What closes Attack 1 is C1's **magnitude**: −1.0
log10 lands at 4.87 in these units, below the 10th percentile (5.422) of the matched fame
distribution in P's own paths, and below `B_unk`. C3 closes the rest. §3's closing sentence
("the composite … **and** absolute calibrated reach (C2)") over-credits C2.

**Success condition.** Either (a) the run report states C2 as a regression guard and re-attributes
Attack 1's closure to C1's magnitude plus C3 — zero cost, no threshold change, and the option
I would defend; or (b) an amendment restating C2 relative to P (e.g. ≥ P's count + 1), which
is a **threshold change made after seeing the baseline** and so is the owner's call, not the
harness's. (a) requires nothing before arms run.

### F2 — the A11 d15/d20 notability guard is not in the C2 scoring path, and its only implementation reports over the wrong population. HIGH. **BLOCKS reading a C2 pass**; does not block running arms.

**Measured.** `score.py` never reads `potentially_notable` or any `guard` block — grep over
the file returns only docstring mentions of unrelated guards. C2 is `any(F[n] < B …)`, and an
unmatched interior has `F = 0`, so **absence alone satisfies C2**. `fame.py` does compute the
guard, but over `names_from_paths`, which is every name at every depth **including
endpoints**. On P: the single flagged name is **CROOVE** — an *endpoint* of pair 8, which no
criterion scores because all scoring slices `path[1:-1]`. The three unmatched *interiors*
(**Desired**, **HOME**, **TANUKI**, all in Nirvana → CROOVE) are all flagged not-notable, and
pair 8's C2 hit is carried entirely by one of them at F = 0.

**What a C2 pass could then be built on.** Exactly the case A11 named and accepted as
residual: an interior with no English Wikipedia article whom the owner would recognise,
counted as maximal reach with no flag raised — because the flagging runs over the wrong
population and is never joined to the cells C2 reads. §9's still-open table says of D4 "what
remains: implement the guard in the C2 scoring path". It is not implemented.

**Success condition.** `score.py` emits, per arm, the list of `(pair, depth ∈ {15,20},
artist)` where a C2 hit is carried by an **unmatched interior**, each annotated with that
name's `guard` block from `fame.json`; and a winning arm's report requires the owner's
one-glance check over that list rather than over `fame.json`'s whole-name flag list. Two joins
over data the harness already writes; no re-fetch, no re-route.

### F3 — the harness cannot run stage 2. HIGH. **BLOCKS stage 2.** Stage 1 is unaffected.

**Measured.** `run_arms.py --arms T1a` fails at `assert not unknown` →
`AssertionError: unknown arm(s): ['T1a']`. `arms.stage2()` has **no caller anywhere in the
repo** (grep `stage2` across all `*.py`, excluding `.venv`). Two further consequences of the
same gap: `score.py` requires `paths["P"]` and `paths["A0"]` in the same file, and
`drop_infeasible_uniformly` computes its dropped set only over the arms present in **one
invocation** — so walking the attachments into a second file would both crash the scorer and
produce a *different* dropped-cell set, reintroducing across the stage boundary exactly the
arm-correlated missingness A13 exists to prevent.

**Success condition.** A single invocation that walks P, A0, W, T1a, T1b, FL1 and FL2
together, so the uniform drop spans stage 1 and stage 2; `--arms` accepting stage-2 names via
`stage2(W)`; and either that, or an explicit assertion that the two files' dropped-cell sets
are identical. Verifiable by running the smoke path with a stage-2 name and getting a walk
rather than an assertion.

### F4 — T1a/T1b's toll magnitude is W-dependent; §1.4's stated magnitudes hold only if W carries S-mag 3.0. MEDIUM. Does not block.

**Measured.** `mirror.py:178` implements `toll = w_sim · (1 − toll_s)`, faithful to §1.4's
formula. At `w_sim = 3.0` that is **7.5× and 30.0× `w_hop`**, as §1.4's parentheticals say.
At `w_sim = 1.5` it is **3.75× and 15.0× `w_hop`** — and `w_sim = 1.5` is the S-mag level of
cells **A3, A5, A6, A7**, i.e. half the factorial, including **A7, which is R1's fallback W**.

**What this means.** Neither magnitude becomes inert (`w_hop = 0.02`), so a T1 null stays
interpretable — that was A1's whole purpose and it survives. But §1.4's figures must not be
quoted for a W with S-mag 1.5.

**Success condition.** The run report prints the realised toll in `w_hop` units next to W's
`w_sim`, and the T1 read names it.

### F5 — X does not bound what §1.4 says it bounds, and this changes R0's licence. MEDIUM-HIGH. Does not block, but must be stated before the stage-1 result is read.

**Measured.** The jump term is `w_jump · |Δpop_raw|` — **symmetric**, so `w_jump = 0` removes
the price of *climbing* as well as the price of diving. Against the only honest null (in a
symmetrised graph every undirected edge appears in both directions, so the base rate of
pop-ascending directed edges is 50 % by construction — measured **0.4998**):

| Cheapest single hop under… | ascends in popularity | mean Δpop of that hop |
|---|---|---|
| null (all directed edges) | 0.4998 | — |
| A0 / production weights | 0.8261 | +0.0918 |
| **X** (`w_jump = 0`, `w_sim = 1.5`) | **0.8687** | **+0.1172** |

n = 74,193 nodes; ties broken on lowest CSR index, matching the heap's tie behaviour.

**What this means.** X's local preference is **more** pop-ascending than the arm it is meant
to bound, because removing the jump term removes a brake in both directions and the graph's
high-similarity edges point upward in popularity. X is the extreme of the **pricing** axis,
not a lower bound on fame. §1.4's "if X does not move the primary outcome, no arm in this
family can" is an **INFERENCE**, and this measurement points against it; §2.4 **R0**'s
interpretability rests on that inference.

**Weakest link, stated.** This is a one-hop greedy statistic, not a Dijkstra path. It
establishes the mechanism and its sign; it does not establish the magnitude of the path-level
effect, and it was measured on one artifact with no second slice. It is falsified if X in fact
produces the lowest fame profile of any arm — which is free to check once stage 1 runs, and is
exactly the shape of A2.4/R6's "the sweep tests the review as well as the design".

**Success condition.** R0's read re-worded so that a null at X licenses only *"no arm in this
family that prices |Δpop| at ≥ 0 moves the outcome"*, and X's result read against A6/A7 rather
than as an upper bound. A stronger fix — an arm at `w_jump = 0, w_sim = 3.0`, separating the
two axes X currently conflates — is a new arm and therefore a budget decision, the owner's.

### F6 — A0's knob cannot act at any depth C1 or C2 scores. MEDIUM. Does not block; changes how A0's row is read.

**Measured** (`probe_floor_lifetimes.json`). P's raw floor is `min(pop_raw of endpoints)` less
0.15 per `known` bypass, so it reaches zero at a per-pair depth of **4 to 7** across all 12
pairs. Alive at snapshots d0–d3 on all 12; alive at d5 on 8 of 12; alive at **no** snapshot
≥ 7. C1 reads d ∈ {10,15,20} and C2 reads d ∈ {15,20}.

**What this means.** At every depth C1 and C2 score, P's cost function is **identical** to
A0's. A0's C1 statistic against P therefore measures nothing but the divergence of exclusion
histories seeded in d0–d6 — not a live floor term. This is A8's conclusion with a bound
attached, and it independently confirms the a0-gate review's unconditional dead-bound on this
artifact. Note C3 *does* read d5, where P's raw floor is alive on 4 of 8 analysis pairs, so
P's own C3 is not floor-free.

**Success condition.** A0's C1 row labelled "exclusion-history carryover, not a floor
contrast"; and the PR-A "fraction of relaxations carrying a non-zero floor term" reported
**per depth**, because the pooled figure averages depths where the term is live with depths
where it is arithmetically dead (for P on this run the pooled figure is 2.94 % of 16,924,346
relaxations — a number that means little without the depth split).

### F7 — the percentile floor is arithmetically dead at d20 on every pair, so FL1/FL2 share W's cost function exactly at d20. MEDIUM-HIGH. Does not block; sharpens A8 into a bound and constrains R5.

**Measured** (`probe_floor_lifetimes.json`). Base percentile floor ≤ 1.0 by definition;
`floor_relax_known_pctl = 0.05` (pre-registered, A2) × 20 = 1.0. So the percentile floor is
**alive at every snapshot d0–d15 on all 12 pairs** (A2's claim confirmed and tightened — A2
said "through d15 on all 12", which holds) and **zero at d20 on all 12 pairs, without
exception**.

**What this means.**

- C3 is `median(d5) − median(d20)`. The FL device can only **raise d5**; it cannot lower d20,
  because at d20 its cost function *is* W's. Any FL-vs-W difference at d20 is exclusion-history
  carryover. So an FL arm's C3 pass is manufactured at d5 — A8's warning, now bounded rather
  than qualitative.
- Symmetrically, FL1 can only make **C1 less negative** than W's, since C1 reads d10 and d15
  where the floor is alive and raising fame.
- C2's d20 clause gives an FL arm nothing W does not already have.

**Success condition.** R5's FL1-vs-W read states that an FL1 C3 win is a d5 effect, and the FL
report gives d5 and d20 medians **separately** rather than only the drop. (A16 already routes
R5 through FL1-vs-W; this adds *where* in depth the contrast can live.)

### F8 — fame is keyed by artist name, and the artifact does not make names unique. MEDIUM. Does not block stage 1; a live hazard for the arms that dive.

**Measured** on the named artifact. 72,951 distinct names over 74,193 nodes. **1,057 non-blank
names shared by 2+ nodes, covering 2,267 nodes (3.06 % of the graph)** — median popularity
percentile 0.433, degree up to 50, 12.9 % of them below the 10th popularity percentile. And
separately, **33 nodes whose name is the empty string** — median popularity percentile 0.203,
degree up to 28, and **27.3 % of them below the 10th popularity percentile against a 10.0 %
base rate**, i.e. 2.7× concentrated in the tail a diving arm is aimed at.

**What this means.** `fame.py` writes `{name → F}` and `score.py` reads `F[name]`, so two
different artists on a path receive one fame value, and C6's `distinct_interiors` under-counts
by the same collapsing. A blank-named interior resolves to **F = 0** — maximal reach,
satisfying C2 by construction — while `has_non_latin("")` is `False` and a Wikidata label
search for the empty string finds nothing, so the A11 guard does not flag it either.
`run_arms.resolve_names` disambiguates *endpoints* by highest popularity; interiors are
whatever the router visited.

**It did not fire on P**: of the 163 nodes in P's snapshots, none is blank-named and no name is
used by two nodes (`paths_P.json`). Unmeasured for every other arm, and the arms that dive are
the ones aimed at the stratum where blank names concentrate.

**Success condition.** Key fame by **MBID** — `paths.json` already writes `node_mbids` for
every node — carrying the name for display and for the resolver query; plus an assertion in
`score.py` that no scored interior name is blank, failing loud. Neither needs a re-fetch: the
cache is keyed by the string the resolver queried and every non-blank name resolves
identically. Discharged when a run over the full grid reports zero blank-named interiors, or
reports them explicitly.

### F9 — the harness computes only vs-P contrasts; `Arm.baseline` and `PACKAGE_CONTRASTS` have no consumer. MEDIUM. Does not block; it is the A16 pattern recurring one level down.

**Measured.** `score.py` imports only `R1_ELIGIBLE` from `arms`. `Arm.baseline`, `Arm.reading`
and `PACKAGE_CONTRASTS` are never read by any script. `score.py`'s table prints every arm
against **P** only.

**What this means.** The one-column contrasts that §1.4 says attribution comes from — A1 vs
A0, A4 vs A1, A6 vs A2, T1b vs T1a, FL2 vs FL1 — are *recoverable exactly* by subtraction,
because `mean(ΔF_A1) − mean(ΔF_A0)` equals the paired one-column contrast (the P term cancels
cell-wise, and the cell sets are identical after A13's uniform drop). But they are not
computed, and no output labels which comparison a figure came from. `PACKAGE_CONTRASTS` is
today precisely what the tightened factor-table rule calls out: a disclaimer nothing reads.

**Success condition.** `score.py` emits, per arm, ΔF against its `Arm.baseline` as well as
against P, and marks any pair listed in `PACKAGE_CONTRASTS` as package-only in both the
printed table and `scores.json`.

### F10 — three §1.5/§2.2 items have no implementation. LOW-MEDIUM. None blocks stage 1.

**Measured, by grep.** (a) The **held-out confirmation** rule (mean ΔF < 0 and negative in ≥ 3
of 4 held-out pairs, §2.2) — `score.py` partitions the held-out pairs *out* and computes
nothing on them. The walker does route all 12 pairs, so no re-route is needed. (b) **C7 /
§1.5's F4 dislike guard** — `run_arms.walk` always issues `KNOWN`; there is no dislike walk in
the harness, and `score.py`'s docstring says so. Required on P **and** on the winner. (c)
§1.5 says the harness "reuses `evaluation.py`" for the AA/overlap diagnostics — nothing in the
scorer imports it.

**Success condition.** Each either implemented or explicitly deferred with a due-point in the
execution log. (a) and (b) come due after R1 picks W; (c) is a §9 O-series reporting item.

### F11 — R1 is under-specified where cells move C1 but all fail C4; the committed code resolves it, and that resolution is legitimately pre-registered. LOW.

**Measured.** `choose_W` filters to cells with `C4.pass` **and** `mean_dF < 0`, then takes
`min` on `(mean_dF, changed_cols)`. §1.4's fallback fires only "if no cell moves C1's
statistic in the right direction"; the code also fires it when cells move but every one fails
C4. Determinism is clean: ties on `mean_dF` break on `changed_cols` and then on
`R1_ELIGIBLE`'s fixed order. Verified on the P-only run: `viable` is empty, so W = A7 by R1's
fallback, exactly as written.

**Success condition.** Name the resolution in the execution log before the arms run, so it is
not discovered as a surprise at the selection step. The code predating the arms is what makes
it pre-registered rather than post-hoc.

### F12 — `score.py` is documented as offline but cannot run outside the `api` environment. LOW, operational.

**Measured.** Run with a plain interpreter it fails at `from arms import R1_ELIGIBLE` →
`arms` imports `mirror` → `ModuleNotFoundError: No module named 'artistpath_api'`. Its
docstring says "Deterministic, offline, and re-runnable" and gives no invocation. It works
from `api/` under `uv run`.

**Success condition.** The `cd api && UV_LINK_MODE=copy uv run …` invocation in the docstring,
or `R1_ELIGIBLE` moved out of the mirror-importing module.

### F13 — nothing binds `paths.json`, `fame.json` and `scores.json` together. LOW.

**Measured.** `paths.json` records `artifact_sha256`; `fame.json` records no provenance and
`score.py` asserts nothing. A stale `fame.json` fails loudly only if the newer run introduced
a name it lacks (a `KeyError`); otherwise it silently scores.

**Success condition.** `fame.py` writes the sha256 of the paths file it read; `score.py`
asserts it matches.

### F14 — the F5 confinement diagnostic measures snapshot-to-snapshot change, not bypass-to-bypass, and its subset test loosens monotonically. LOW, non-gating.

**Measured, by reading `score.py:114-133`.** §1.5 defines confinement as "≥ 3 consecutive
**bypasses** changing only the same node group". The implementation iterates consecutive
**snapshots** — 0,1,2,3,5,7,10,15,20 — so at the deep end "3 consecutive" spans up to 15
bypasses. And `groups` accumulates the union of every change so far, so the
`changed <= groups[-1]` subset test becomes strictly easier at each step. On P it returns
empty, which is consistent with either "no confinement" or "cannot fire over 8 snapshot
transitions".

**Why it matters despite gating nothing.** It is one of only two offline proxies for §3's
Attack 2, which §3 explicitly declines to close, so a false negative here removes the only
offline visibility of the failure mode the blind listen is the backstop for.

**Success condition.** Either compute it over all 21 depths — the walk visits every depth; only
the *recording* is snapshot-limited (`run_arms.py:186`) — comparing each step against the
immediately preceding step rather than the accumulated union; or state in the report that it is
a snapshot-level accumulating variant and cannot be read as §1.5's definition.

---

## Checked and clean — do not re-check

- **The mirror is still the router.** `verify_mirror.py` re-run today with the committed
  `mirror.py`: **byte-identical on all 212 compared cells** across all 12 pairs, guard G off.
  Term order, the `(cost, node)` heap tie-break, and CSR neighbour order match
  `pathfinding.find_path` line for line; the two direct-edge pairs end at d0 as documented.
- **The stage-1 factorial genuinely holds the floor inert (A8).** `w_floor = 0.0` multiplies
  the penalty; `0.0 × 1.0` (the largest floor penalty this artifact can produce) is exactly
  `0.0` and adding it is exact, so A0–A7, A1u and X execute production's expression with an
  exactly-zero addend. **One labelling caveat:** `floor_mode` stays `RAW` in those cells, so
  `mirror.py` still *computes* the floor and still increments `stats["floor_active"]` — the
  PR-A percentage for a factorial arm is a **shadow** measurement of where the term *would*
  fire, not where it does.
- **FL1/FL2 use the pre-registered relax constant.** `SweepConfig.floor_relax_known_pctl =
  0.05` (A2), not `ApiConfig.floor_relax_known` — the mistake that made the original FL arms
  inert is not repeated. `floor_relax_dislike_pctl` is a harness-only constant absent from the
  pre-registration; it is unreachable under the all-`known` protocol and is commented as such.
- **A13's uniform drop is genuinely uniform within one invocation** (the cross-invocation gap
  is F3): the dropped set is collected over **all** arms first, then applied to **all** arms.
  And **no downstream statistic in `score.py` re-introduces per-arm missingness** — C1 requires
  both P's and the arm's cell (identical after the drop), C2/C3/C4/C6 skip only falsy cells,
  and under guard G a non-`None` path always has ≥ 1 interior, so `cell_median`'s
  empty-interior branch is unreachable. C3 pools *interiors* rather than cells, which weights
  by payload — within-arm only, so it cannot confound a cross-arm comparison.
- **The toll's binding set matches the pre-registration's words.** Max edge score on the
  artifact is exactly 1.0 with **none above it**; 17,574 of 898,006 directed edges (1.96 %) sit
  at exactly 1.0. So `sim >= 1.0` and "score exactly 1.0" select the same edge set.
- **A3's mean-matching is implemented as specified**, over all directed CSR entries:
  mean|Δpop_raw| = 0.07702, mean|Δpctl| = 0.14357, ratio `jump_scale_pctl` = **0.53649**. A1's
  mean jump cost equals A0's exactly (3.851 × `w_hop` under each currency), so J-cur is a
  genuine one-column contrast on scale; A1u's is **1.864×** A1's, which is the scale component
  A1u exists to expose.
- **P6's percentile is deterministic and as specified**: average rank over N with ties
  averaged, `np.argsort(kind="stable")`, range 0.00278–1.0.
- **Determinism verified empirically, not argued.** `run_arms.py --arms P` re-run
  byte-identical (`6849050c…`); `score.py` re-run byte-identical (`dfb9a216…`). The fame step
  made **no network call**: the committed cache (172 entries) covered all 163 of P's nodes.
- **No currency is substituted for another anywhere I looked.** Victim selection uses in-graph
  `pop_raw` per §1.2; the jump/floor percentile is a percentile *of* `pop_raw`; C1–C4 and
  `B_unk` are all in fame units (log10 pageviews, `B_unk` read at runtime from the committed
  proxy `score.json`, not hard-coded); the A14 endpoint-tracking diagnostic uses **fame**, not
  popularity — correct, since WGLL value 9 is about fame; `w_degree_hub = 0.0` and degree
  appears nowhere else in the harness.
- **C1's two clauses are not redundant, and the fraction clause is what protects it.** Flooring
  the 4 largest of P's 24 C1-window cell medians satisfies the mean clause — 17 % of cells,
  against the 75 % negative-fraction requirement. So the absence-as-floor encoding cannot buy a
  C1 pass on a minority of cells. Worth having: the matched fame distribution in P's paths runs
  4.247–7.259 (median 5.995, p10 5.422) with the unmatched floor at 0.0, a **4.25-unit gap with
  nothing in it** — so the fame scale the instrument produces is bimodal, and C1's −1.0 in that
  scale is a large ask within the matched range alone.
- **No arm in `STAGE1` or `stage2(...)` is wholly inert.** A0's knob acts only at d0–d6 (F6);
  the FL arms' only at d0–d15 (F7); A3/A5/A6/A7 carry §1.3's stated first-hop degeneracy at
  ceiling-saturated endpoints. Everything else is live at every scored depth. This is the
  positive answer to the brief's item 4: A1–A3's original inertness is not repeated.
- **`arms.py`'s printed factor table matches §1.4 cell for cell**, including `R1_ELIGIBLE`
  ranging over A0–A7 only, A1u and X marked non-adoptable, and guard G on in every arm
  including P.
- **`verify_resolver_equivalence.py` proves what A15 claims, for the population it tests**: it
  asserts every canonical non-match in the committed 29-artist sample stays a non-match under
  the fallback. It does not — and does not claim to — prove the fallback never returns a
  *wrong* article for a name outside that sample; the identical accept clauses are the argument
  there, and it is an argument, not a test. Not re-run here (network-bound, result committed).

---

## Could not be determined without running an arm — named, not guessed

1. **Whether any arm moves C1, and by how much.** The primary outcome. Nothing here predicts it.
2. **Whether A13's drop path is exercised at all.** P produced **zero** guard-infeasible cells,
   so the uniform-drop code has never run against a real drop. Its logic is verified by reading;
   its behaviour on a real infeasible cell is unmeasured.
3. **Whether F5 confinement or the repeated-interior report ever fires** on a diving arm — F14's
   two explanations for P's empty result cannot be separated without arm data.
4. **Whether X in fact produces the lowest fame profile.** F5 says its bounding claim is not
   established and the local statistic points the other way; only the run settles the
   path-level question.
5. **Whether a blank-named or duplicate-named interior appears in a diving arm's paths** (F8).
   It does not in P's.
6. **Whether the A11 guard would flag anything real** once F2's join exists — on P the only
   flagged name is an endpoint no criterion scores.
