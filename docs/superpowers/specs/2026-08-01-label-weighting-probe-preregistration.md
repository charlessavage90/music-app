# Pre-registration — the label weighting and evidence probe (`WGT-`)

**Role: ACTIVE pre-registration.** Committed before any `WGT-` figure existed: no script named
in §9 has been written or run, and the commit timestamp is the evidence that this design
preceded its results. The committed figures it *cites* as baselines (`tas_weighting.json`,
`tas_frame_split.json`, the `REL-` findings) all predate it and are named as such.

**Identifier register.** `WGT-` for gates, checks and readings; `EV-` for evidence-table rows.
Weighting schemes are named by **words** — `plain`, `rarity`, `evidence` — deliberately outside
the letter-number namespace, because bare `Q1`-style tokens are already load-bearing in the
Gate 2→3 review documents. Frames reuse the committed `W0`/`W1`/`W4`/`W5`/`W6` definitions
(`builder/analysis/2026-07-30-tag-discrimination/tas_frame_split.py`) by import, never
restated. Collision check run 2026-08-01 by grep over `docs/` and `builder/analysis/`: `WGT-`
and `EV-` appear nowhere.

**What triggered it.** The owner directed this probe on 2026-08-01, after the discussion
recorded in the `TAS-` execution log's successor entries. It consumes the measurement half of
`NEXT.md`'s deferred row *"Rarity-weighted agreement is a measured candidate device"* (his
trigger — pulled for **measurement only**, not for any `TAS-` §1 change) and evaluates `W4`
and `W5` as *grid frames* without consuming the row *"`W4` was never evaluated as a `TAS-`
candidate frame"* — no `TAS-` amendment is made by anything here. The row *"Whether `REL-`'s
frame is taken into `TAS-`"* is untouched.

---

## §0 What this probe is, and the complete list of what it cannot do

*Plain question: once rare labels count for more than common ones, and well-evidenced labels
count for more than drive-by ones, do genre labels tell an artist's candidates apart better —
and does the Discogs style column stop hurting?*

**Diagnostic only.** This probe:

- changes **nothing** in `TAS-`: no §1 vocabulary change, no bar, no criterion or guard
  re-run under any frame, no substrate change;
- adopts nothing, rebuilds nothing, changes no weight, default or currency, and spends no
  blind listen (`REQ-38` stands wherever it stood);
- licenses exactly three outputs: **(a)** the answers to the `WGT-` readings; **(b)** a
  **device recommendation** — a named (frame, scheme) pair, or "binary suffices", or "no
  device is defensible" — as an *input* to the future cap re-evaluation pre-registration,
  which is a separate document that must be designed cold; **(c)** the record corrections in
  §7.

**Relationship to the closed `REL-` union pass.** `NEXT.md` closed *"the `REL-` release-dump
union pass"* because its trigger (`REL-1` landing in 45.0–49.9%) can never fire, and requires
that any reopening be a new pre-registration designed cold. This document is that shape, and
it does **not** reopen the coverage question: `WGT-4` asks about **evidence strength**
(votes, support), a question `REL-` never posed. The coverage verdicts stand untouched.

**No bar in this document may be revisited once any result exists.**

---

## §1 Factor table

Two knobs. Fifteen cells, plus conditional `evidence⁺` variants (§4, `WGT-4`).

| Knob | Values | Source of definition |
|---|---|---|
| **frame** | `W0`, `W1`, `W4`, `W5`, `W6` | committed, `tas_frame_split.py` — by import |
| **scheme** | `plain`, `rarity`, `evidence` | §2 of this document |

**Isolating baselines — every comparison differs by exactly one column:**

| Comparison | Isolates | Baseline rule |
|---|---|---|
| (F, `rarity`) vs (F, `plain`) | rarity weighting, on frame F | same frame, adjacent scheme |
| (F, `evidence`) vs (F, `rarity`) | evidence weighting | same frame, adjacent scheme |
| (`W4`, s) vs (`W1`, s); (`W6`, s) vs (`W5`, s) | the Discogs **genre** column, under scheme s | same scheme, F4-adjacent frames |
| (`W5`, s) vs (`W1`, s); (`W6`, s) vs (`W4`, s) | the Discogs **style** column, under scheme s | same scheme, F5-adjacent frames |
| (F, `evidence⁺`) vs (F, `evidence`) | the `EV-R` row alone, if admitted | same frame, same scheme, one table row |

No read in this document compares across frame *and* scheme simultaneously. **Cross-scheme
magnitude comparisons of the spread statistic are barred** — the scale confound is recorded in
the `TAS-` execution log §15.4 — so every cross-scheme read below is a sign, an ordering, or a
turnover.

### Held constant, and why each is genuinely constant under the intervention

| Term | Why the intervention cannot move it |
|---|---|
| Substrate: the pre-cap `ALG-E` capture (`TAS-AM2`, selection side), regenerated via `td_capture.py` | the knobs touch label frames and the agreement measure only; the capture pipeline reads neither. Sha must equal the `TAS-` execution log §14.1 value (`WGT-0d`) |
| Scored population: `W0`'s scorable set, fixed across all cells | labels only accumulate (`W0` ⊆ every frame), and no scheme unlabels an artist — weights discount, never delete (floor property, §2). Scorability is presence-based and therefore knob-independent |
| λ grid {0, 0.25, 0.5, 1.0, 2.0} and the committed selection simulation (`tas_select.py`'s rule, by import) | fixed inputs to every cell; no knob reaches them |
| The fame frame (`tas_common.fame_frame`), NaN-excluded | consumed only by the leak readings (`WGT-1`, `WGT-4c`); no knob writes to it |
| Styles' zero incremental reach: every style-carrying artist already carries a Discogs genre (`REL-` record) | an analytic property of fixed carrier sets. **No scheme can change reach, only sharpness** — stated here so no read below can claim otherwise |

### Deliberately NOT constant, enumerated per the dormant-term rule

- **The neutral rule is recomputed within every cell**, through the one committed path
  (`tas_common.neutral_for` / `resolved_agreement`). A neutral is a quantile of the cell's
  own agreement distribution; freezing `plain`'s neutrals into weighted cells would price
  unlabelled artists in a foreign currency. Consequence, fixed now: **absolute agreement
  values are not comparable across cells**, and no read below uses one.
- **Singleton amplification.** 514 labels sit on exactly one artist (`tas_weighting.json`
  reading A). A singleton can never create agreement, but it sits in Jaccard unions — and
  rarity gives it the **largest** weight in the vocabulary, so rarity actively *suppresses*
  its carrier's agreements where `plain` merely ignored it. Not presumed a defect — an artist
  with a unique label is arguably less like its candidates — but it is a mechanism that
  exists only in weighted cells, so it gets its own reading (`WGT-6`) instead of being
  discovered as an anomaly.

---

## §2 The device, fixed before any run

- **`plain`**: the committed Jaccard (`tas_common.agreement`), unchanged. This is today's
  device and the control column.
- **Rarity weight per label**, computed per frame F over the full graph population:
  `r(ℓ) = ln(N_F / n_F(ℓ))`, where `n_F(ℓ)` is the count of artists carrying ℓ in F and
  `N_F` the count carrying ≥ 1 label — **pinned to the committed
  `tas_weighting.json` `weighting_under_test` definition**; `WGT-0b` enforces the pin.
- **Weighted agreement** (both weighted schemes), symmetric by construction:

  ```
  A(a,b) = Σ_{ℓ ∈ La∩Lb} r(ℓ)·min(e_a(ℓ), e_b(ℓ))  /  Σ_{ℓ ∈ La∪Lb} r(ℓ)·max(e_a(ℓ), e_b(ℓ))
  ```

  with `e ≡ 1` under `rarity` (absent labels contribute e = 0). Setting `r ≡ 1` and `e ≡ 1`
  reduces this to `plain` exactly — that identity is `WGT-0a`.
- **Evidence strength per (artist, label) assertion**:
  `e(a,ℓ) = ln(1 + s(a,ℓ)) / ln(1 + 8)`, capped at 1. **Floor property:** any carried label
  has `s ≥ 1`, so `e ≥ ln 2 / ln 9 ≈ 0.32` — evidence *discounts* thin assertions to about a
  third weight, it never deletes them, which is what keeps scorability knob-independent (§1).

### The evidence table

**Every row of this table is the owner's to strike before this document is committed. The
values are a first fixture chosen to be arguable, not an optimum.** An ingredient that fails
the `WGT-1` leak gate **degrades to presence (+1)** — the source never vanishes; its
*strength claim* does.

| Row | Signal | Contribution to `s(a,ℓ)` | Plain sentence | Hazard priced |
|---|---|---|---|---|
| `EV-A` | MB **artist-page** tag/genre votes for ℓ | + v (the dump's `count`) | *each vote is one person who bothered* | votes scale with page traffic — fame leak, gated by `WGT-1` |
| `EV-W` | Wikidata **P136** statement of ℓ | + 1 | *a curated single assertion* | no strength signal exists in the source |
| `EV-G` | distinct MB **release groups** of a carrying ℓ | + count of RGs (**RG votes not summed**) | *the artist's own albums keep saying it* | album grain kills reissue inflation by construction. RG votes are excluded to avoid double-counting the same people; dump sampling shows RG tag votes are overwhelmingly 1. **Strikeable decision** |
| `EV-D` | any **Discogs** release of a carrying ℓ (genre or style, per frame) | + 1 flat | *a compulsory form field, one submitter* | Discogs carries no vote data — verified at schema level 2026-08-01; flat by necessity, not by choice |
| `EV-R` | MB **release-level** tags — **CONDITIONAL: this row exists only if `WGT-4` admits it** | candidate form: + distinct releases carrying ℓ; **collapsed to presence-per-RG if `WGT-4c` fires** | *individual pressings keep saying it* | pressing count is plausibly fame-shaped; `WGT-4c` measures that before this row may exist |

- **Fallback:** a frame label whose sources yield `s = 0` (a transport mismatch — e.g. an
  LB-delivered tag absent from the artist dump) takes `s = 1`; the count of fallbacks is
  reported. Label keys are normalised everywhere through the committed `norm_genre`.
- Rarity and evidence are computed from the label data alone; nothing in this table reads
  similarity, degree, or fame.

---

## §3 Instrument checks — all four pass before any other figure is read

A failed check **stops the probe**. The fix is instrument work, recorded in the execution
log; no bar moves; any figure produced before the fix is void.

| Check | Requirement | Plain sentence |
|---|---|---|
| `WGT-0a` **identity** | with `r ≡ 1`, `e ≡ 1`, the weighted path reproduces `plain` agreement and `plain` selection **bit-identically**, every frame, every λ | *set to weigh nothing, the new scale must read exactly like the old one* |
| `WGT-0b` **reproduction** | the (`W0`, `rarity`) cell reproduces `tas_weighting.json`'s committed rank-correlation and turnover figures to their recorded precision, computed the way that script committed them | *the new code must get the already-published number before it is trusted for a new one* |
| `WGT-0c` **forced identity** | λ = 0 selection turnover is exactly 0 in every cell | *when the knob is off, nothing may change* |
| `WGT-0d` **provenance** | the regenerated capture's sha256 equals the `TAS-` execution log §14.1 value; abort otherwise | *we are measuring the same object as last time* |

---

## §4 Two gates that run before the grid is read

### `WGT-1` — the fame-leak gate

*Plain: does counting votes secretly measure how famous an artist is?*

For each **strength ingredient** (`EV-A` votes; `EV-G` RG-count; `EV-R` release-count, if it
comes to exist): Spearman correlation of the per-artist total ingredient mass against the
fame percentile, over artists carrying a fame value.

**Effect size: |ρ| ≥ 0.50 → that ingredient degrades to presence (+1).** Why 0.50: the frame
itself leaks 0.37 through bare label count (`tas_weighting.json` reading B), and that floor
is not removable — it *is* the frame. An ingredient crossing 0.50 adds leak clearly beyond
the floor the device already stands on.

Run state: requires only the evidence parses; runs before any agreement cell is read.
Stated limitation, carried beside every leak figure: the fame frame is blind in the
modern-obscure tail (`FPC-9`), so these correlations are computed exactly where fame is
measurable and not where the leak would matter most. §6 names this as the probe's weakest
link.

### `WGT-4` — the release-level scoping pass

*Plain: was preferring albums over individual pressings the right call, once weighting
matters? The original preference was made under a coverage lens, before weighting was
considered — this gate re-derives or refutes it under the new lens.*

One full streaming pass over the release dump
(`builder/scratch/mb-json-dumps/release/mbdump/release`, 322 GB, present on disk — see §7),
restricted to graph artists. **The pass runs to the end of the dump regardless of any
partial figure; a number from a partial pass is not a `WGT-4` figure.**

| Reading | Measure | Effect size and its anchor |
|---|---|---|
| `WGT-4a` **incremental reach** | artists gaining their **first** label (beyond `F0` ∪ `W6`) from release-level tags | **≥ 742 artists** (1% of the 74,193 census population) → a reach argument for `EV-R` exists. Anchor: the owner's 1%-materiality precedent (`TAS-AM1`), applied to population share. *Plain: do individual pressings know genres for artists nothing else covers?* |
| `WGT-4b` **incremental evidence** | among `W1`-scorable lists, within-list Spearman of `evidence`-scheme agreement **with vs without** the candidate (uncollapsed) `EV-R` | material iff the share of lists with ρ < 0.99 **exceeds 0.25**. Anchor: rarity weighting itself measured 0.247 below 0.99 (`tas_weighting.json` reading C) and was called material — release evidence is material if it moves orderings at least as much as the idea it would ride on. *Plain: do pressings change which candidates look coherent, or just add bulk?* |
| `WGT-4c` **reissue confound** | Spearman of mean releases-per-release-group per artist against fame | **ρ ≥ 0.37** → the pressing channel is at least as fame-shaped as the frame's own known leak (reading B's 0.37) → `EV-R` must collapse to presence-per-RG, making it equivalent to `EV-G` plus nothing. *Plain: do famous albums simply get pressed more?* |

**Decision rule — complete enumeration, fixed now:**

1. `WGT-4a` ≥ bar → `EV-R` earns its row (collapsed form if `WGT-4c` fired), and the reach
   gain is reported per fame band.
2. `WGT-4a` < bar **and** `WGT-4b` material **and** `WGT-4c` < 0.37 → `EV-R` earns its row
   (the evidence argument).
3. `WGT-4a` < bar **and** `WGT-4b` material **and** `WGT-4c` ≥ 0.37 → the ordering movement
   is fame-shaped; `EV-R` is **excluded** and the movement is recorded as a leak finding.
4. `WGT-4a` < bar **and** `WGT-4b` not material → **the release-group preference is
   CONFIRMED under the weighting lens**; `EV-R` never exists; the §7 record correction still
   lands.

**Run-state independence:** the grid does not wait for `WGT-4`. All fifteen cells run with
the table minus `EV-R`. If `EV-R` is admitted, the `evidence` cells re-run as `evidence⁺`
and **both versions are reported** — the pre-`EV-R` run is then the isolating baseline for
exactly one knob, the row's addition (§1's last comparison row).

---

## §5 Grid readings

Run state for every reading here: all four instrument checks passed, all fifteen cells
complete. `WGT-2` is additionally repeated on `evidence⁺` if `EV-R` is admitted, with both
results reported.

### `WGT-2` — the style question

*Plain: once rare labels count for more, do the fine style labels — "indie rock" rather than
"rock" — stop washing the signal out? Or was equal weighting never the reason they hurt?*

For each weighted scheme: the two style isolations (`W5` vs `W1`, `W6` vs `W4`) on spread and
on redundancy (rank correlation with similarity), with the two genre isolations (`W4` vs
`W1`, `W6` vs `W5`) reported beside them. The committed `plain` directions (`tas_frame_split.json`:
styles cost spread and raise redundancy in both isolations; genres do neither) are the
reference.

- **REVERSED** iff, under the scheme, **both** style isolations show spread delta ≥ 0 **and
  both** show redundancy delta ≤ 0 — the committed directions flip, all four. *Plain:
  weighting rescues styles.*
- **NOT REVERSED** iff both isolations keep the committed directions. *Plain: equal
  weighting was not the reason; the style column's cost is intrinsic on this vocabulary* —
  and the `NEXT.md` row naming `W4` (not `W6`) as the frame any future amendment should name
  stands, now on two measurements.
- **UNRESOLVED** iff the isolations disagree — reported as such, no claim licensed.

Sign-based deliberately: magnitudes are scale-confounded across schemes (§1). One scale-free
secondary is reported without a bar: the style:genre contrast within each scheme.
**Whatever the outcome, styles buy no reach — §1's analytic bound — so a REVERSED verdict
re-admits `W5`/`W6` as candidates for future evaluation and nothing more.**

### `WGT-3` — does weighting change what the device does?

*Plain: if labels counted unequally, would different artists actually get picked?*

Per frame, per weighted scheme, against the same frame's `plain` column: within-list rank
correlation of agreement, and selection turnover at each non-zero λ. **Descriptive — no
bar.** Its consumer is the §6 device recommendation. The owner's 1% edge-turnover
materiality line (`TAS-AM1`) is the anchor for *discussing* the numbers, explicitly not a
gate here.

### `WGT-5` — the vocabulary on the table

*Plain: what is actually in these ~600 style labels?*

Deliverables, no bars: per frame, labels by carrier count with rarity weights; the style
column's full frequency table (the owner's requested eyeball artifact); and per-source
rarity distributions — which answers, descriptively, whether one rarity rule over the union
treats the sources sanely or one source dominates. Emitted as a markdown table beside the
JSON.

### `WGT-6` — singleton drag

*Plain: labels only one artist carries get the biggest weights and can only ever count
against their carrier — how much of the weighting's effect is just that?*

Share of union mass contributed by singleton labels, per frame under `rarity`; and `WGT-3`'s
rank correlations recomputed with singletons excluded, reported beside the primary. This
feeds the owner's deferred junk-label clustering idea without measuring clustering here.

---

## §6 Outcome reads — every result has one, including the null

- **Weighting moves nothing** (rank correlations ≈ 1 and turnover ≈ 0 at every λ ≤ 2, every
  frame): the device is insensitive to weighting on this vocabulary. **Binary suffices** —
  the cap re-evaluation prereg should name a binary device and cite this. That is a useful
  answer, not a failure.
- **Rarity moves selection; evidence adds nothing on top** (`evidence` vs `rarity` ≈
  identity): recommend a rarity-only device — simpler, and it needs no dump parses at build
  time.
- **Evidence moves things and its ingredients survived `WGT-1`**: recommend rarity ×
  evidence, with the surviving table quoted in full.
- **`WGT-2` REVERSED**: styles re-enter candidacy for any future frame evaluation — which
  remains a future `TAS-` §8 amendment designed cold, the owner's trigger, unchanged.
- **Any recommendation above is an input to the cap re-evaluation pre-registration and
  nothing else.** Nothing here says any weighted map *sounds* better. Every road to adoption
  runs through that prereg, a rebuild, and the owner's ear (`REQ-38`).

**Weakest link, stated in advance:** the fame frame's blindness (`FPC-9`) sits under every
leak reading. A vote-leak invisible in the blind tail is precisely the leak that would
matter most for obscure routing. Defensible: directions and cross-source contrasts.
Abandoned cheaply: any absolute leak magnitude.

---

## §7 Record corrections carried by this document's commit

- **`NEXT.md`'s closed `REL-` union-pass row says the 345 GB release dump "was deleted after
  measurement". It was not.** The dump is on disk at
  `builder/scratch/mb-json-dumps/release/` (322 GB, verified 2026-08-01). The row is
  corrected in place with a dated note; **the closure itself stands** — it never depended on
  the deletion.
- The frozen `REL-` spec's §7 carries the same false claim and **stays frozen**; the
  correction lives here and in the `NEXT.md` row, never as an edit to a committed
  pre-registration.
- `docs/README.md` gains this spec's classification row.

---

## §8 Out of scope

Any `TAS-` criterion, bar, guard or vocabulary change; any `TAS-6` re-run under any frame or
scheme; any rebuild; any router-side work; any adoption; any blind listen. The junk-label
clustering idea (its own deferral row) is fed by `WGT-5`/`WGT-6` and not measured. The
`REL-` coverage verdicts are not reopened and the union-pass trigger stays dead. The
no-release-artist spot check (the owner's manual tail review) is deliberately **outside**
this pre-registration: it is descriptive product research with no criterion; its draw rule
(fixed seed, stratification by popularity band) lives in its script's header.

---

## §9 Runbook

New directory `builder/analysis/2026-08-01-label-weighting/`. Scripts **to be built** (named
here as dependencies, none exist yet):

- `wgt_evidence.py` — the three MB dump parses keeping vote counts (artist ~17 GB and
  release-group ~17 GB, minutes each at the measured 18 GB / 2.4 min rate), plus the
  `WGT-4` release pass (322 GB, expect 45–90 min at the same rate), resumable via
  `rel_common.save_partial`/`load_partial`. Reads dumps and Discogs raw output; writes only
  under the probe directory. No network.
- `wgt_grid.py` — instrument checks, the fifteen cells, `WGT-1`, `WGT-2`, `WGT-3`, `WGT-6` →
  `wgt_grid.json`.
- `wgt_tables.py` — `WGT-5`'s markdown tables.

Environment: run from `builder/`; `UV_LINK_MODE=copy`; `PYTHONIOENCODING=utf-8`; `python -u`
on the release pass (the buffered-stdout trap). Snyk scan per policy on all new scripts; the
accepted `--out`-path Low class will recur and is recorded under the standing `NEXT.md` row.

Execution order: commit this document → build scripts → `WGT-0a`–`0d` → `WGT-1` → the
fifteen cells → `WGT-4` (the release pass; the owner's manual tail-review hour overlaps
here) → the `EV-R` decision → `evidence⁺` re-runs if admitted → `WGT-2`/`WGT-3`/`WGT-5`/
`WGT-6` reads → findings document.

---

## §10 Amendments

Standing rule, inherited from the `TAS-AM3` precedent: any amendment appended here states at
its head whether it was written before or after the results it touches existed.

### `WGT-AM1` — the rarity denominator gloss (written BEFORE any `WGT-` figure existed; no probe script had been written when this was appended)

§2's gloss of the rarity formula — "`N_F` the count carrying ≥ 1 label" — contradicts the
committed definition the same sentence pins to: `tas_weighting.idf_table` computes
`log(N / carriers)` with **N = all capture nodes, labelled or not**. The pin governs, as §2
already states, so the gloss is corrected: `N_F` is the full node count. Found by reading the
committed code before building the harness; `WGT-0b` would have caught it later as a failed
reproduction, which is the check working, but catching it at the design layer is cheaper and
leaves no window where the document and the code disagree.
