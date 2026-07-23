# Defect remediation and cost-function retune — design

**Role: ACTIVE spec. Written 2026-07-23.** This design resumes the work paused by
[`../2026-07-22-phase1-execution-log-and-graph-defect.md`](../2026-07-22-phase1-execution-log-and-graph-defect.md)
(read its §2, §2.12 first — that document owns every figure this spec relies on; nothing
is restated here). It makes the outstanding §2 decision per the owner's instruction of
2026-07-23 and defines two tracks: repair the §2.8 tie-break defect in the builder, then
retune the router's cost function on the repaired graph. It supersedes nothing; the
`capfix` adoption stays closed (log §4.1).

---

## 1. Decision inputs (owner, 2026-07-23)

Recorded here because three open questions in the record were answered today:

1. **Route chosen: repair + retune** (this spec). The owner instructed: remediate the
   logged defect and, more importantly, materially improve the app's ability to generate
   good paths. Of the three routes left open by log §2.13, this takes the cost-function
   route **and** the §2.8 builder fix; the `cap_strategy` redesign stays deferred.
2. **The nine-names test-queue item is DONE: "mostly unknown."** The §2.11 inference is
   confirmed — in-graph popularity does not mean fame at the top of the distribution.
   Consequence: no success criterion in this work may be phrased as an in-graph
   popularity percentile alone (log §7.1 item 5 is settled by §4.3 below).
3. **Listening-test policy relaxed.** The owner: the Phase 2 log §15–17 prohibition on
   further listening tests "may be too strong — we should continue to run new listening
   tests where appropriate going forward." Re-testing a *closed verdict* because it was
   unwelcome remains forbidden; a new candidate on a new finding may be listened to.
   A pointer note goes into the Phase 2 log at §15.
4. **The 5k dev fixture is retired; dev defaults to the full 75k artifact.** Raised by
   the owner (a deferred point from a prior session, never revisited): the 5k graph's
   small shape makes manual results hard to trust. Confirmed against the record — unit
   tests run on the two committed 500-node fixtures, not on it; it represents the
   obscure tail worst (Phase 1 log §3.1 already abandoned it for testing); and its
   seeding once produced a famous-artist-free dev graph (Phase 2 log §19). The full
   artifact builds in ~30 s and loads fine at boot. `ApiConfig.graph_path` defaults to
   the adopted artifact by name and is flipped at each adoption; the `fixture` command
   survives only for the committed unit-test fixtures.

---

## 2. Goal

Two failures, two tracks:

- **Track 1 (defect):** the adopted artifact's most popular artists are among its least
  connected, caused by the MBID tie-break ranking p99-clipped scores (log §2.8). Fix the
  builder so top-k selection ranks unclipped strengths; rebuild; adopt.
- **Track 2 (product):** routed paths never surface an artist below the ~95th popularity
  percentile at any bypass depth, because the cost function prices stratum exits
  correctly and declines them (log §2.12). Retune the pricing — including its
  *currencies* — on the repaired graph, give `known` a real mechanism, and adopt only
  what survives a blind listen.

Track boundary is a **named handoff seam**: Track 1 ends with a committed, checksummed,
adopted artifact and an updated test queue. A fresh session can start Track 2 cold from
this spec plus the plan.

---

## 3. Track 1 — builder remediation of the §2.8 tie-break

### 3.1 Change

`build_from_archive` (`builder/src/artistpath_builder/pipeline.py`) currently rescales
scores (`rescale_scores`, p99 clip) and *then* calls `mutual_knn_cap`, whose top-k
`sorted(..., key=lambda pair: (-pair[1], pair[0]))` ranks the clipped values — so a
famous artist's fully-saturated list is decided entirely by the lowest-MBID tie-break
(log §2.8).

**Fix:** `mutual_knn_cap` gains an explicit ranking input so selection ranks the
**unclipped damped strengths** (the `scored_adjacency` values that already exist in
`build_from_archive` before rescaling) while the emitted edge scores remain the rescaled
ones. Equivalently: the *cap decides membership on unclipped order; the artifact still
carries clipped scores*. This is exactly the log §2.8 Arm 2 intervention, validated
there by one-knob replay.

Invariants that must hold:

- **Emitted scores unchanged in kind** — still `p99_log_clip` output, p99 computed once
  over the full uncapped array (unchanged code path).
- **Popularity unchanged** — in-degree is summed pre-cap (`pipeline.py`, before
  `mutual_knn_cap`), so the popularity vector is invariant to this change.
- **Determinism preserved** — the MBID tie-break stays for genuinely tied unclipped
  strengths; every ordering rule of spec §9 is untouched.
- **No behavioural API change** — the APG1 contract is untouched. The only api-package
  edit in Track 1 is the `ApiConfig.graph_path` *default* flipping to the adopted
  artifact (decision input 4); routing code is untouched.

### 3.2 Verification

1. **Unit tests** on `mutual_knn_cap`: ranking follows the ranking input, not the
   emitted score; tie-break on MBID still applies within genuine ties; behaviour with
   the ranking input omitted (or required — plan decides the signature) is explicit.
2. **Replay determinism test** still passes (byte-identical rebuild from the same
   archive).
3. **Full rebuild from the 75k archive**, then assert against log §2.8 Arm 2's recorded
   topology: same N and E as Arm 2, Radiohead present in the LCC at its recorded degree,
   The Beatles / Coldplay / R.E.M. at theirs, and the global shape unmoved (median
   degree and frac-below-8 as recorded). The existing `rankfix` artifact's recorded
   checksum is the expected identity if the build is byte-reproducing; if it differs,
   the topology assertions govern and the discrepancy is investigated before adoption.
4. **Checksum recorded** in the findings record and the PR body (artifacts are
   gitignored; the checksum is their only identity).

### 3.3 Adoption

- **No blind listen for Track 1.** Log §4.1 closed this: capfix vs rankfix have
  identical stratification and identical tail behaviour; a listen would burn the
  owner's ear on a null. Adoption is by structural equivalence, recorded checksum, and
  the owner's ordinary use afterwards.
- Flip `ApiConfig.graph_path`'s default to the adopted 75k artifact (decision input 4 —
  the 5k dev fixture is retired) and smoke-check via that default: Radiohead and The
  Beatles findable, a path routes between them. Update the dev-run guidance in
  `CLAUDE.md` and the three READMEs.
- Append a TEST-QUEUE entry: famous-endpoint neighbourhoods are the thing that changed —
  search Radiohead (now present), route through Beatles-class endpoints, bypass around
  them.

### 3.4 Risk

Small and bounded: the change is validated by intervention, the global shape is known
not to move, and only ~0.4 % of nodes (ceiling-saturated pools) can change neighbours.
The residual risk is a build-procedure mismatch versus the Arm 2 replay — covered by
§3.2's topology assertions.

---

## 4. Track 2 — cost-function retune on the repaired graph

### 4.1 Problem being priced away

Log §2.12: a single dive out of the famous stratum costs on the order of half the raw
popularity range under `w_jump`, versus `w_hop` per hop to stay inside; on
ceiling-saturated edges `sim = 1.0` zeroes the `w_sim` term at any weight, so the hub
expressway is invisible to weight sweeps. `w_floor` is inert as a symptom of the same
pricing (log §2.12), and `known` currently degrades to a bare hard exclusion (log §3.3).

### 4.2 Experiment design

**Harness:** the log §3.10 mirror-and-verify method, unchanged — mirror production
`find_path`, assert byte-identical paths with all new knobs at neutral, then enable
knobs. No shipped code is edited until adoption. Scripts live under
`builder/analysis/` with a README, per the established convention.

**Knobs (factor-table columns; the plan carries the full table):**

| knob | neutral | what it tests |
|---|---|---|
| `w_jump` currency | raw \|Δpop\| | percentile \|Δpctl\| — raw popularity's top decile spans half the range, so raw-currency `w_jump` overprices stratum exits precisely at the top (log §2.12) |
| `w_jump` magnitude | current default | strength of the popularity-cliff penalty under each currency |
| `w_sim` magnitude | current default | the dive-hop barrier (log §3.7: `w_sim` dominates genuine dive-hop cost) |
| expressway toll | off | a similarity-cost floor binding only on ceiling-saturated edges (e.g. `sim_eff = min(sim, s_max)`), pricing the expressway without a rescale rebuild |
| `known` gate currency | raw drop | percentile/rank-based substitute admission — a raw-drop gate cannot express "less famous" at the top (log §2.12) |

One row per variant, isolating baseline named per row, per the CLAUDE.md factor-table
rule. Percentiles are computed once from the artifact's popularity array at harness
start (and at API boot if adopted) — rank over N, deterministic.

**Pre-registration:** the primary outcome, effect direction, and the read of each
possible result are written before the sweep runs (the log §2.13 C5 discipline).

### 4.3 Success criterion (settles log §7.1 item 5)

Scored on an **external fame proxy, never in-graph popularity**: Deezer artist fan
counts (`nb_fan`), fetched only for artists that appear in evaluated paths, cached to
disk, matched by verified artist name (the C1 wrong-artist failure mode applies to
artist search too — exact-name match required, mismatches excluded rather than
guessed). Fallback proxy if Deezer coverage proves inadequate: Wikipedia pageviews.
Rationale: the owner's nine-names verdict confirms in-graph popularity conflates fame
with playlist co-listening at the top, which makes any in-graph percentile criterion
gameable in both recorded currencies (log §2.11, §2.12).

- **Primary (pre-registered):** on a fixed pair set with scripted `known`-bypass
  sequences, the candidate's substitute and interior artists show a materially lower
  external-fame profile than production's at the same bypass depths. The exact effect
  size and pair set are fixed in the plan before any arm runs.
- **Guards:**
  - *No-regression:* no-bypass paths on the fixed pair set stay stable (node overlap
    against production; any change is inspected, not assumed benign).
  - *Coherence is not scored offline.* AA and overlap-family metrics are recorded as
    diagnostics only — the record shows they do not track the owner's ear. Coherence is
    decided by the blind listen.
  - *Dislike unaffected:* `dislike` keeps neighbourhood avoidance; assert its paths
    are unchanged by `known`-mechanism knobs.

### 4.4 The `known` mechanism (C3 proper)

After a winning cost configuration exists: re-run the Stage-0 binding check on it (the
log §3.7 warning — the old clearance does not transfer), then re-pose the A-vs-C
question (additive reward vs hard waypoint) **on that substrate**, since both prototypes
were previously tuned where no mechanism could reach obscurity. The gate uses the
percentile currency from §4.2. `w_floor` and `floor_relax_*` are deleted as part of
landing the chosen mechanism (roadmap C3), not before.

### 4.5 Blind listen and adoption

One blind listen: final candidate vs current production, on the Track 1 artifact, using
the existing harness with two required fixes first — secrets written outside the repo or
gitignored (log §7.1 item 4), and verdicts written to disk rather than copy-pasted (log
§7 deferral, owner-requested). Session hygiene per the Phase 2 log §15: the running
session stays ignorant of the token→arm mapping.

Adoption = the owner's verdict. Only then do the winning weights, currencies, and the
`known` mechanism land in `ApiConfig` / `pathfinding.py`, with path-level tests
(roadmap Phase 4's "assert the right thing" note: `dislike` and `known` must produce
different paths from the same inputs).

### 4.6 Review gate

`ml-graph-analyst` reviews the experiment spec and harness before the sweep runs —
both prior reviews of this experiment class found protocol defects (log §3.5, §3.7).
The analyst derives; the owner judges.

---

## 5. Out of scope, with recorded triggers

- **p99 ceiling rescale (builder).** Deferred behind a measured trigger: if the winning
  arm's cost decomposition still shows ceiling hops dominating winning paths, that is
  the roadmap's carried success-condition trigger and a rescale arm is scheduled then.
  The expressway toll (§4.2) is the cheap probe of whether the ceiling binds.
- **`cap_strategy` redesign.** Stays deferred (log §2.13 C6); the analyst's Part 2
  remains gated on code that does not exist.
- **Clips (C1/C2) and frontend UX.** Roadmap items, untouched here. Clip defects are a
  known listen confound; the prior listen recorded them as non-material to verdicts.
- **Duplicate artist names / MBID coupling in source data.** Unchanged deferrals (log
  §7.1 item 2).

---

## 6. Weakest links

1. **Deezer `nb_fan` as fame.** Unvalidated against the owner's perception. Cheap
   check before relying on it: the nine names plus a dozen artists from the judged
   paths, ranked by `nb_fan` — if that ranking contradicts the owner's ear, switch
   proxy before the sweep, not after.
2. **Percentile currency helps the top and may hurt the middle.** Percentile gaps are
   large mid-distribution where raw gaps are small; the no-regression guard exists for
   exactly this, and magnitude knobs are swept jointly with currency.
3. **The A-vs-C outcome was pair-dependent last time** and may stay pair-dependent on
   the new substrate; if so, the honest outcome is recording that neither dominates and
   shipping the simpler shape.
