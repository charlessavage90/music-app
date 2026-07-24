# Track 2 pre-registration — cost-function retune sweep

**Role: ACTIVE spec. Written 2026-07-23 by a one-shot experiment-design engagement,
before any Track 2 arm has run.** This document fixes the factor table, the primary
outcome, the effect sizes, the pair set, and the read of every possible result —
including the null — for the sweep defined by
[`2026-07-23-defect-remediation-and-cost-retune-design.md`](2026-07-23-defect-remediation-and-cost-retune-design.md) §4.
Where it disagrees with that spec it says so inline; the disagreements are design
corrections, not scope changes, and none reopens anything closed in the Phase 1 log §4/§4.1.

> **⚠ AMENDED 2026-07-23 — five amendments (A1–A5), all made before any arm ran.**
> The `ml-graph-analyst` protocol review
> ([`../findings/2026-07-23-track2-protocol-analyst-review.md`](../findings/2026-07-23-track2-protocol-analyst-review.md))
> found three defects settled by arithmetic over the artifact. **§9 is the amendment
> index**; every affected passage below is also marked inline, because a reader who lands
> mid-document never sees this banner. The pre-registration gate is undisturbed — the
> amendments are themselves committed before any arm runs, and the commit timestamp is
> the evidence. **The review's D4–D7 are NOT addressed here and remain open** (§9).

**Figures rule.** No measured scoring or path-quality figure is restated here. Every
such reference is a citation into `../2026-07-22-phase1-execution-log-and-graph-defect.md`
(hereafter "log") or `../findings/2026-07-21-scoring-adjudication.md` (hereafter
"adjudication"). Numbers that do appear are one of: code constants read from source,
thresholds pre-registered here for the first time, or arm counts.

**Basis.** Conclusions below rest on **code actually read** unless flagged otherwise:
`api/src/artistpath_api/config.py`, `pathfinding.py`, `evaluation.py`, `clips.py`,
`app.py` (path route), `graph_store.py` (`degree_hub_penalty` field — called
`hub_penalty` when this document was written; renamed 2026-07-23 by the
pre-Track-2 guards, see `builder/analysis/README.md` for the full mapping);
`builder/src/artistpath_builder/pipeline.py`, `graph.py`;
`builder/analysis/2026-07-23-popularity-stratification/` (`tail_probe.py`,
`known_viability.py`, README). Claims resting on documents alone are flagged
**[DOC]** — the record here has repeatedly been internally consistent and wrong about
the code, so [DOC] claims carry that risk. Claims labelled **MEASUREMENT** cite a
recorded measurement; **INFERENCE** claims name their falsifier. No new measurement
was taken for this document.

**Housekeeping owed by the working session** (this engagement may not edit other
files): add this document to `docs/README.md`'s map, per its "Adding a document" rule.

---

## 0. Resolution check — what the governing spec names, against the repo

Per the CLAUDE.md rule, everything spec §4 names was grepped. Results:

| Named in spec §4 | Resolves? | Where / note |
|---|---|---|
| `mutual_knn_cap`, `rescale_scores`, `scored_adjacency`, `build_from_archive` | ✔ | `builder/.../graph.py`, `pipeline.py` |
| `find_path`, `ApiConfig.graph_path`, `w_sim` / `w_jump` / `w_floor` / `w_hop`, `floor_relax_known` / `floor_relax_dislike` | ✔ | `api/.../pathfinding.py`, `config.py` |
| log §3.10 mirror-and-verify harness | ✔ | method recorded in log §3.10; prior implementation `builder/analysis/2026-07-22-c3-bypass-mechanisms/stage0.py` |
| Popularity-**percentile** machinery | ✘ not built | Nothing in `api/src` computes popularity percentiles (`evaluation.py`'s only percentile function is over *degree*). Prior probes computed it ad hoc (`tail_probe.py`). To be built in the harness — see prerequisite P6 for the tie-handling rule. |
| Expressway toll (`sim_eff = min(sim, s_max)`) | ✘ not built | Expected — spec proposes it as a harness knob. ~~`s_max` needs a data-derived value (prerequisite P3).~~ **AMENDED 2026-07-23 — see §9 A1.** Both the `min(sim, s_max)` form and P3's rule for setting `s_max` are **withdrawn**: under P3 as written the toll is inert by construction (analyst review D1, re-confirmed at 1.42 % of `w_hop` in `builder/analysis/2026-07-23-track2-toll-calibration/`). Replaced by an additive toll on ceiling edges at two pre-registered magnitudes; definition in §1.4. |
| **The `known` gate ("raw drop")** | ✘ **not in shipped code** | The spec's §4.2 table lists "`known` gate currency, neutral: raw drop" as if a gate ships today. It does not. Shipped `known` is a **hard exclusion plus a floor relaxation feeding a term that never fires** (`pathfinding.py:78,34`; log §3.3). The pop-drop ≥ 0.10 / sim ≥ 0.70 gates exist only in analysis scripts (log §3.10; `known_viability.py`). Consequence: the gate-currency knob **cannot be a column of this sweep** — no Stage A arm can vary it. It belongs to the §4.4 mechanism experiment (Stage B below). |
| Deezer `nb_fan` | ✘ nothing consumes it | `clips.py` calls Deezer **track** search (`config.deezer_search_url = api.deezer.com/search`), whose rows carry an artist object but are fetched for previews, first-hit, **with no name verification** — the C1 wrong-artist failure mode is visible in the code (`clips.py:98-107`). The fame harness needs a separate artist-search fetcher with exact-name matching; it must **not** reuse `clips.py`. That `nb_fan` is available on Deezer artist objects is an **external assumption of mine, verified against neither repo nor record** — confirmed or refuted in the §5 pilot before anything depends on it. |

One further code-vs-record item, load-bearing enough to shape the factor table:

> **`w_floor` is an uncontrolled variable in every arm that succeeds.**
> **MEASUREMENT [DOC]:** `w_floor` never fires in production because `w_jump` prevents
> paths from dipping below the floor in the first place (log §2.12; adjudication §5.4,
> claim 23 — measured on a **pre-Track-1** graph). **Code read:** the term is live in
> the cost (`pathfinding.py:104`, weight 1.0 in `config.py`), `floor =
> min(pop_source, pop_target)` in **raw** popularity, relaxed per bypass by
> `floor_relax_*`. **INFERENCE:** any arm that succeeds at diving — the entire point of
> this sweep — sends `pop_raw_v` (named `pop_v` when this was written) below the raw
> floor, at which point a weight-1.0 raw-currency
> counter-term that was inert in the baseline switches on *only in the arms that work*.
> Left unhandled, every "one-knob" currency or magnitude arm is actually a two-knob
> change (the knob, plus a newly-live floor term). Falsifier: paths in candidate arms
> never dip below `min(pop_s, pop_t) − relax·n` — possible but it would mean the arm
> failed anyway. The governing spec does not mention floor handling in §4.2 at all;
> its §4.4 deletes `floor_relax_*` only at C3 landing, which is after the sweep.
> **This pre-registration therefore adds floor handling as an explicit column** (§1),
> and notes the flip side: the floor + per-bypass relaxation is the **only
> depth-graduated device in the shipped cost function** (everything else is static per
> request; only the exclusion set and the floor know how many bypasses have happened —
> code read, `pathfinding.py`). The primary outcome demands a *depth gradient* (F2),
> so the family needs at least one depth-coupled term, and this is the one that exists.

---

## 1. Factor table

### 1.1 Stage split — a correction to the governing spec

The spec's five knobs conflate two experiments with different substrates:

- **Stage A (this sweep):** cost-function knobs, evaluated with the **shipped bypass
  semantics** (bypass = hard exclusion; `known` vs `dislike` differ only in floor relax
  and avoidance — code read). This is exactly the `tail_probe.py` protocol on new costs.
- **Stage B (spec §4.4, separate pre-registration later):** the `known` mechanism —
  gate currency, additive-reward vs waypoint — run **on the Stage A winner**, after
  re-running the Stage-0 binding check there (log §3.7's warning that clearances do not
  transfer).

The spec's fifth knob (gate currency) is a Stage B column. Keeping it out of Stage A is
not a deferral of the owner's F3 criterion — F3 is scored in Stage B where a substitute
concept exists; Stage A's F2 criterion needs no gate.

### 1.2 Constants across every arm (not columns)

| Fixed | Value | Why it is not a column |
|---|---|---|
| Graph artifact | `graph-t15-tiebreakfix.bin`, sha256 per `../findings/2026-07-23-tiebreak-fix-adoption.md` | Track 1 output; asserted before every run (established script convention) |
| Router | Mirror of production `find_path`, per log §3.10 mirror-and-verify | No shipped code edited before adoption |
| Guard G: ≥ 1 intermediary | Applied in **all** arms including baseline | §4's F1 decision — uniform application keeps it out of the comparison. **Sequencing, added 2026-07-23:** see the note below §1.2. |
| Bypass protocol | All-`known`, victim = most-popular interior (in-graph popularity; ties → lowest node id), walked independently per arm; snapshots **d ∈ {0, 1, 2, 3, 5, 7, 10, 15, 20}** *(amended 2026-07-23, §9 A2 — was {0, 5, 10, 15, 20})* | `tail_probe.py` / log §3.10 precedent. Victim selection deliberately stays in-graph (deterministic, no network); outcomes are scored externally. This currency separation is a modelling choice — see §6. **The walk is 20 bypasses regardless, so every depth is computed anyway; a snapshot is a recording decision, not a compute cost.** The added early depths are where the floor device is alive (§9 A2). |
| `w_hop`, `w_avoid`, avoidance params | Production defaults (`config.py`) | Out of scope for the diagnosed defect |
| `w_degree_hub` | 0.0 (`config.py:44`) | *Added 2026-07-23, §9 A5 — closes analyst O3.* Genuinely constant under every intervention here: **a zero weight cannot be un-zeroed by turning another knob**, so the degree-hub term contributes nothing in any arm. Listed explicitly because the dormant-term rule requires enumerating what is held fixed, not only what is turned — and this table's omission of it was that rule finding its first miss on the document that motivated it. |
| Percentile definition | Rank over N of the artifact's popularity array, computed once at harness start; ties by average rank (P6) | Spec §4.2 |

> **Note added 2026-07-23 (pre-Track-2 guards, G5a) — verify the mirror with guard G OFF,
> then enable it everywhere.**
>
> As written, two requirements collide on the two direct-edge pairs (Radiohead → The
> Beatles, Muse → Coldplay): guard G applies to **all** arms including baseline P (§1.2),
> while P is defined as shipped `find_path` and is the mirror-and-verify target — "the
> mirror must reproduce P byte-identically" (§1.4). On those pairs both cannot hold. Guard
> G changes the path by construction, and shipped code has no G to compare against.
>
> **Sequence, so this is not discovered mid-run:** (1) verify the mirror against production
> `find_path` with **G disabled**, on every pair, and require byte-identity there; (2) then
> enable G uniformly across all arms including P, and run the sweep. Log §3.10 is explicit
> that non-identical paths mean *stop, the harness is wrong* — that instruction applies to
> step 1 only. Without this, a session executing §1.4 literally either concludes
> verification failed or quietly skips the check on the two pairs it matters most for.

> **P7 answered by the owner, 2026-07-23:** "Every path must have at least one artist in
> between the start and end." The §4 INFERENCE is **confirmed**; ≥ 1 intermediary is a
> product invariant, and the falsifier described in §4 did not fire. The guard still ships
> only with the adopted arm — no shipped code changed here.

### 1.3 The columns

Four knobs vary in Stage A. Production values from `config.py`: `w_sim = 3.0`,
`w_jump = 1.0` (raw), `w_floor = 1.0` (raw), toll absent.

| Column | Levels | What it tests |
|---|---|---|
| J-cur: `w_jump` currency | raw \|Δpop\| / percentile \|Δpctl\|, **mean-matched** *(amended 2026-07-23, §9 A3)* | §2.12's mechanism: raw currency overprices stratum exits at the top |
| J-mag: `w_jump` weight | 1.0 / 0.3 | Cliff-penalty strength under each currency |
| S-mag: `w_sim` weight | 3.0 / 1.5 | The dive-hop barrier (log §3.7: `w_sim` dominates genuine dive-hop cost) |
| F: floor handling | **off** (`w_floor = 0`) / **pctl** (floor and relax computed in percentile currency, `w_floor = 1.0`, relax constant **pre-registered here, not read from `config.py`** — §9 A2) | Off isolates the cost knobs; pctl is the depth-graduating device (§0). Production raw floor appears only in P below — a raw floor is already known not to bind (claim 23) and, under a repriced `w_jump`, would fire in the wrong currency by construction. |

> **Amendment 2026-07-23 (§9 A3) — the percentile level is mean-matched by definition.**
> Swapping raw for percentile changes the jump term's overall **scale** as well as its
> **geometry** (analyst review M2 owns the ratio); only the geometry is the intended
> treatment. So J-cur = pctl is *defined* as
> `w_jump_pctl = w_jump_raw × mean|Δpop_raw| / mean|Δpctl|`, with the ratio computed by
> the harness at start-up over all directed CSR entries of the asserted artifact —
> deterministic, and not a constant copied into this document. A scalar cannot remove the
> geometry change (that *is* the treatment); it removes the scale confound, which makes
> A1-vs-A0 a genuine one-column contrast. Arm **A1u** (§1.4) carries the unnormalised
> variant as a diagnostic so the scale component stays visible rather than assumed away.

> **A degeneracy in the S-mag column, stated rather than discovered mid-run**
> *(added 2026-07-23, §9 A5; measurement: `builder/analysis/2026-07-23-track2-toll-calibration/` Q4).*
> Eight of the pre-registered endpoints are **fully ceiling-saturated** — all 50 of their
> neighbours sit at similarity exactly 1.0 — and 22 of 24 carry at least one ceiling edge.
> Where similarity is constant across every exit, `w_sim · (1 − sim)` contributes an
> identical constant to all of them, so **S-mag has no discriminating power on the first
> hop out of those endpoints.** Its treatment effect there acts only through downstream
> hops and through its weight *relative to* the jump term. This does not invalidate the
> column — it bounds what an S-mag result can be attributed to, and it must be recalled
> before reading A3/A5 as "the dive barrier alone".

### 1.4 The arms

**Anchors:**

| Arm | Definition | Isolating baseline | Purpose |
|---|---|---|---|
| **P** | Shipped `find_path`, production config, floor **raw** at 1.0 | — | Mirror-and-verify target: the mirror must reproduce P byte-identically before any knob turns (log §3.10). Also the user-facing comparison baseline for the primary outcome. |
| **A0** | P's weights with `w_floor = 0` (raw currency, J-mag 1.0, S-mag 3.0, toll off) | **P** (one knob: floor off) | Re-verifies claim 23 on the Track 1 graph: pre-registered expectation is **path-identity to P on the full pair×depth grid**. If identity fails, the floor is already live on this artifact, claim 23 does not transfer, and the factorial below is re-anchored on P with floor as a fully crossed column — a design revision, recorded before proceeding. |

**Core factorial** — 2 × 2 × 2 over J-cur × J-mag × S-mag, floor off, toll off. A0 is
the (raw, 1.0, 3.0) cell. In a full factorial every cell has a one-column neighbour;
the table names the primary reading per row.

| Arm | J-cur | J-mag | S-mag | Isolating baseline | Primary reading |
|---|---|---|---|---|---|
| A0 | raw | 1.0 | 3.0 | P | anchor |
| A1 | **pctl** | 1.0 | 3.0 | A0 | currency alone |
| A2 | raw | **0.3** | 3.0 | A0 | cliff strength alone, raw |
| A3 | raw | 1.0 | **1.5** | A0 | dive barrier alone |
| A4 | pctl | **0.3** | 3.0 | A1 | cliff strength under pctl |
| A5 | pctl | 1.0 | **1.5** | A1 | dive barrier under pctl |
| A6 | raw | 0.3 | 1.5 | A2 or A3 | joint magnitude, raw |
| A7 | pctl | 0.3 | 1.5 | A4 or A5 | joint magnitude, pctl |

**One factorial diagnostic, not an attachment** *(added 2026-07-23, §9 A3)*. It hangs off
A1, not off W, which is why it sits here rather than in the table below.

| Arm | Definition | Isolating baseline | Purpose |
|---|---|---|---|
| **A1u** | A1 with the percentile jump term **unnormalised** | A1 (one column: mean-matching on → off) | Diagnostic. Exposes how much of any A1 effect is the currency's **scale** rather than its **geometry** — the confound §1.3's mean-matching note removes. **Not a candidate for adoption**, and not eligible to be W. |

**Attachment arms** — added to cell **W**, where W is chosen by pre-registered rule
R1: *the factorial cell with the largest primary contrast (§2.3 C1 statistic) that does
not violate the payload guard C4; ties → the cell with fewer changed columns from A0;
if no cell moves C1's statistic in the right direction, W := A7 (the most aggressive
cell) so the attachments still get tested.* Rule fixed now; cell chosen by data.
**R1 ranges over the eight factorial cells A0–A7 only** — A1u and X are diagnostics and
are excluded from selection *(clarified 2026-07-23, §9 A3)*.

| Arm | Definition | Isolating baseline | Purpose |
|---|---|---|---|
| **T1a** | W + additive expressway toll: `cost += w_sim · (1 − s_toll)` on every edge whose score is exactly 1.0, with **`s_toll = 0.95`** (toll = 7.5 × `w_hop`) *(amended 2026-07-23, §9 A1)* | W | The probe of whether the p99 ceiling **binds**, at a magnitude capable of changing a routing decision (spec §5's recorded trigger) |
| **T1b** | T1a with **`s_toll = 0.80`** (toll = 30 × `w_hop`) *(added 2026-07-23, §9 A1)* | T1a | Toll magnitude. Makes a T1 null interpretable: a null at 30 × `w_hop` is evidence about the ceiling; a null at an inert magnitude is evidence about nothing. |
| FL1 | W + floor **pctl** (floor = min endpoint *percentile*, `w_floor = 1.0`), relax **`floor_relax_known_pctl = 0.05` per bypass — pre-registered here, NOT `config.py`'s value** *(amended 2026-07-23, §9 A2)* | W | The depth-graduating device: holds d0 high, admits progressively deeper dives per bypass |
| FL2 | FL1 with `w_floor = 3.0` | FL1 | Floor strength — whether the gradient needs a hard wall |
| **X** | Corner: pctl, `w_jump = 0`, `w_sim = 1.5`, floor off, toll off | A7 (one column: J-mag 0.3 → 0) | **Reachability bound, not a candidate.** The cheapest-possible-dive member of the family. If X does not move the primary outcome, no arm in this family can — that is what makes the null in §2.4 R0 interpretable. Never adoptable (INFERENCE: it will wander incoherently; falsified if it both moves fame and survives the listen — a welcome surprise). |

**15 runs total** (P, 8 factorial, A1u, T1a, T1b, FL1, FL2, X) *(amended 2026-07-23 from
13 — §9 A1, A3)*. At the recorded harness cost per `find_path` call (README,
popularity-stratification), the full grid over 8 pairs × 21 calls per walk is on the
order of an hour of compute — still comfortably a single working session. The added
snapshot depths (§9 A2) cost nothing: the walk visits every depth regardless.

> **Why the toll is additive-on-ceiling rather than `min(sim, s_max)`**
> *(amendment rationale, §9 A1; measurement:
> `builder/analysis/2026-07-23-track2-toll-calibration/`).* The two forms differ in what
> they bind on. `min(sim, s_max)` at a pre-registered magnitude would toll every
> near-ceiling edge too, changing the binding set from "the p99 clip's own artifacts" to
> "everything above `s_max`" — which is a different question from the one spec §5 asks.
> The additive form binds on exactly the saturated edges and lets the magnitude be chosen
> independently, which is what D1 requires. **This is not a disagreement with the governing
> spec** — its §4.2 asks for "a similarity-cost floor binding only on ceiling-saturated
> edges" and offers `min(sim, s_max)` only as an *e.g.*; the additive form satisfies the
> stated requirement, which the example form provably could not. Hence no new row in §8.
> **What a toll can and cannot do:** at a fully
> saturated node it adds the same constant to all 50 exits, so it **cannot re-rank them**;
> it makes multi-hop ceiling routes dearer relative to shorter or higher-cost
> alternatives. T1 therefore asks "is the expressway's *cheapness* load-bearing?", not
> "is its *ordering* wrong?" — and that is the question spec §5 records.

**Multi-knob comparisons this design contains, labelled as such:** A6/A7 vs A0 are
two- and three-column packages; they exist to bound the family's joint effect, and a
win there **cannot be attributed to any single knob** — attribution comes only from the
one-column chains (A1–A5, A1u, T1a, T1b, FL1, FL2). FL1 vs P is a package comparison (floor
currency *and* everything W carries); the isolating chain is P → A0 → … → W → FL1.
Any result quoted outside this document must name which comparison it came from.

**What has no isolating baseline, stated per the CLAUDE.md rule:** there is no arm
isolating "floor raw at production strength under a repriced `w_jump`" — deliberately
(§1.3, F row). The design therefore **cannot tell** whether the production raw floor
would have sufficed as the depth device; if FL1/FL2 fail, that question is open, not
answered.

### 1.5 Guards carried by every arm (from spec §4.3, two amended)

- **No-regression at d0:** node overlap of each pair's d0 path vs P, reported per pair;
  every changed d0 path is listed and inspected, not assumed benign. No numeric
  auto-pass threshold — inspection is the spec's own instruction. Note the tension
  honestly: static weights cannot dive at depth while leaving d0 untouched unless the
  floor device (FL arms) carries the depth dependence; a factorial cell that wins C1
  but reshapes d0 paths is expected behaviour to *inspect*, and is precisely why FL1
  exists.
- **AA / overlap-family metrics recorded as diagnostics only** — never gating
  (adjudication §6 claims 41–42; log §4). The harness reuses `evaluation.py` for them.
- **Dislike guard, amended.** Spec §4.3 says "assert `dislike`'s paths are unchanged by
  `known`-mechanism knobs." That is satisfiable in Stage B (gate knobs are
  known-specific) and **vacuously false for Stage A** — cost knobs change every path,
  `dislike`'s included, by construction (code read: one shared cost function).
  Replacement, per F4: a scripted all-`dislike` walk (same victim rule) on P and on the
  winner; assert `dislike` and `known` walks produce different paths from identical
  inputs, and report a substitution-rate diagnostic (fraction of bypasses where the new
  path differs from the old by exactly one interior node). Reported, not gated;
  coherence judgement stays with the listen.
- **F5 confinement diagnostic:** node-set overlap between consecutive snapshot paths;
  flag only *sustained* confinement to one region (≥ 3 consecutive bypasses changing
  only the same node group), not single local deviations.

---

## 2. Pre-registration

### 2.1 Primary outcome

**For each (arm, pair, depth) cell:** the interior artists of the snapshot path (guard G
guarantees ≥ 1 interior). Each artist's fame is `F(a) = log10(1 + fans(a))` under the
**validated** external proxy (validated per §5 — the sweep is not scored until §5's
test has passed or replaced the proxy; the same protocol re-runs against the fallback
proxy verbatim if Deezer fails). Cell statistics: median F, minimum F, interior count.

**Primary contrast (C1):** paired over cells at depth ≥ 10, analysis pair set:
`ΔF = median-F(candidate cell) − median-F(P cell)`.

### 2.2 Effect sizes — fixed now, before any arm runs

Thresholds below are pre-registered designer choices, not measured facts. One
pre-registered recalibration is permitted: after §5's proxy test, all log10 thresholds
are re-expressed in the owner's own band spacing if his "know well"/"never heard of"
bands turn out to be closer than 1 log10 apart (rule: thresholds scale by
`band_gap / 1.0`, where `band_gap` is the difference in median F between those two
labelled buckets). Recalibration happens **before** any arm runs and is recorded in the
execution log.

| # | Criterion | Threshold |
|---|---|---|
| **C1** | Relative depth contrast vs P | mean ΔF over d ≥ 10 cells ≤ **−1.0** (an order of magnitude in fan count), and ΔF < 0 in ≥ **75 %** of those cells |
| **C2** | Absolute reach | in ≥ **4 of 8** analysis pairs, at least one d15-or-d20 interior falls below **B_unk**, the owner-calibrated "would not know them" fame band from §5 |
| **C3** | Within-arm depth gradient (F2's "progressively") | candidate's pooled median F at d20 ≤ pooled median F at d5 **− 0.5** |
| **C4** | Payload guard (WHAT-GOOD #2: fewer-but-obscurer is not a win) | mean interior count over d ≥ 10 cells ≥ P's mean − **1** |
| **C6** | Proxy coverage guard | ≥ **90 %** of each arm's distinct interior artists name-matched to the proxy, and candidate-vs-P coverage gap ≤ **5** points; unmatched names manually resolved where feasible, remaining gaps flagged per cell |

(C5 = no-regression inspection and C7 = dislike/known divergence are the §1.5 guards —
reported, inspected, not thresholded.)

**A winning configuration** passes C1–C4 and C6 on the analysis set, **then**
reproduces direction on the held-out set (mean ΔF < 0 and negative in ≥ 3 of 4
held-out pairs — direction only; the held-out set is too small to re-test magnitude,
which is the adjudication §6 claim 45 lesson), **then** goes to the blind listen
(spec §4.5). Passing offline **selects a candidate; it never adopts one.**

### 2.3 Pair set — fixed now

Endpoint presence in the Track 1 graph is **[DOC]**-attested (log §2.2/§2.11/§2.12
tables, adoption record); prerequisite P2 has the working session verify each by
lookup before any arm runs — substitution rule below if one fails.

**Analysis set (8):**

| # | Pair | Why it is in |
|---|---|---|
| 1 | Miles Davis → Daft Punk | canonical listen pair (log §3.8) |
| 2 | The Shins → Wishbone Ash | canonical; the famous→(relatively) obscure pair |
| 3 | Metallica → Taylor Swift | canonical; the pair where a redesign previously won |
| 4 | Radiohead → The Beatles | F1's direct-edge case; new surface Track 1 exposed |
| 5 | Muse → Coldplay | F1's second direct-edge case |
| 6 | Madonna → Bob Dylan | famous→famous across genre eras |
| 7 | Pink Floyd → Aphex Twin | rock → electronic; both attested well-connected |
| 8 | The owner's F6 bypass pair, captured from his 2026-07-23 test URLs (prerequisite P1) | the only pair with a recorded reach-the-tail-then-snap-back trace |

**Held-out set (4), used only to confirm the winner:** Arctic Monkeys → Johnny Cash;
Michael Jackson → Gorillaz; System of a Down → R.E.M.; The Rolling Stones → Linkin Park.

**Substitution rule** (deterministic, pre-registered): if an endpoint fails P2's lookup
or a pair is unrecoverable (pair 8), substitute the next pair from this ordered reserve:
Nirvana → CROOVE (Nirvana = the higher-popularity duplicate, per the established
duplicate-name handling in the probe scripts); Aphex Twin → Johnny Cash. Substitutions
recorded in the execution log before any arm runs.

**Known weakness, stated:** endpoints are famous-heavy by design (that is where the
defect lives and where users start), with one deliberately obscure-target pair plus
pair 8. The sweep says nothing about obscure→obscure journeys (§6).

### 2.4 The read of each possible result — written before any arm runs

- **R0 — full null (no arm, including corner X, moves C1's statistic materially).**
  Read: the repricing family is exhausted; §2.12's "cost-function problem" diagnosis is
  **incomplete as stated** — the router's refusal is not (only) price-driven within
  reachable weight space. Licenses: firing spec §5's recorded triggers — schedule the
  p99 ceiling-rescale arm (builder) and/or revisit the deferred `cap_strategy`, each
  with its own pre-registration. Does **not** license: re-litigating the `capfix`
  adoption, mutual k-NN, or anything in log §4/§4.1; shipping any arm anyway; or
  quietly weakening the thresholds. A null here is informative *because* this section
  exists — that is the log §2.13 C5 discipline.
- **R1 — corner X moves, all tuned arms null.** Read: the family works but the grid was
  too conservative. Licenses exactly **one** pre-registered follow-up: a single
  interpolation grid between W and X (same pairs, same criteria, logged addendum before
  it runs). Not an open-ended tuning loop.
- **R2 — raw-magnitude arms (A2/A3/A6) move as much as percentile arms (A1/A4/A5/A7).**
  Read: §2.12's *specific* currency mechanism is weakened — cheapening cliffs suffices
  and the currency story was a sufficient-but-not-necessary framing. Record in the log
  against §2.12; prefer the raw-currency winner (fewer moving parts, no percentile
  machinery at API boot).
- **R3 — arms dive (C1, C2 pass) but no gradient (C3 fails) and/or d0 reshaped badly.**
  Read: static repricing lowers the whole profile rather than deepening with bypass
  count — expected for floor-off cells. The FL arms are the pre-registered remedy. If
  FL1/FL2 also fail C3, the family has no working depth device, and the gradient
  requirement **moves to Stage B** (the `known` mechanism becomes the gradient carrier);
  C1/C2 remain binding for Stage A adoption regardless.
  > **Amended 2026-07-23 (§9 A2).** This branch was **unreachable as originally written**:
  > at `config.py`'s `floor_relax_known`, the floor reached zero before the depths C1 and
  > C2 score, making FL1/FL2 numerically identical to W in every scored cell (analyst
  > review D2 — arithmetic, not inference). The remedy was inoperative. With the
  > pre-registered relax constant and the added early snapshots, R3 is now reachable and
  > reads as written. **A second consequence, recorded because it bears on the baseline:**
  > the same arithmetic applies to production **P** in raw currency, so whatever depth
  > gradient P shows inside the C1 window comes from the **exclusion set alone**, not from
  > the floor. P is not a "router with a working depth device" and must not be described
  > as one.
- **R4 — passes offline, loses the blind listen.** Read: fame movement without
  coherence — F6's warning realised. The verdict notes (not the offline metrics) say
  what broke. Next lever is Stage B's mechanism shapes on this substrate — not another
  weight sweep, and not route-aware waypoint selection, which stays rejected (log §4).
- **R5 — passes offline and the listen.** Adopt per spec §4.5 (weights, currency, and
  percentile machinery land in `ApiConfig`/`pathfinding.py` with path-level tests);
  proceed to Stage B (§4.4) on the adopted substrate; delete `w_floor`/`floor_relax_*`
  only per §4.4, or *retain* them if an FL arm is the winner — in which case the spec's
  §4.4 deletion clause is amended, since the floor would then be load-bearing.
- **R6 — the percentile arms move ΔF the *wrong way* (positive) while the raw-magnitude
  arms move it negative.** *Added 2026-07-23 (§9 A4), on the analyst review's D3.*
  This branch exists because the graph's own geometry predicts it is the **modal**
  outcome, and the original §2.4 had no read for it — which is the exact condition under
  which a result gets interpreted post-hoc, the failure mode this section exists to
  prevent. **Mechanism:** percentile currency compresses the top decile and stretches the
  bulk, so lateral famous↔famous moves get *cheaper* faster than exits do; what Dijkstra
  responds to is the price of an exit **relative to the alternative**, and that ratio
  worsens substantially under the percentile swap (review §2 M2 owns the figures).
  **Read:** the currency is not the mechanism — within `w_jump`, the knob that promotes
  diving is **J-mag** (and X's `w_jump = 0`), not J-cur. **Licenses:** preferring the
  raw-currency winner, and recording §2.12's currency framing as **specific to the
  `known` gate** (where it is a threshold on a drop, and the argument is sound) rather
  than to `w_jump` (where it is a price relative to alternatives). **Does not license:**
  re-opening anything in log §4/§4.1, nor treating §2.12 as refuted — its diagnosis is
  about *where* the router declines exits, and R6 would refine the mechanism, not the
  diagnosis. **Falsifier, and it is free:** A1 beats A0 on C1. If it does, the review's
  inference is wrong and is discarded — the sweep tests the review as well as the design.

**Interpretation discipline:** the sections of this log-adjacent record that went wrong
went wrong in interpretation, never measurement (log §2.13). Accordingly: any
conclusion drawn from this sweep beyond R0–R5's pre-written reads is flagged as
post-hoc in the execution log and does not enter the record as a finding without an
`ml-graph-analyst` check (spec §4.6).

---

## 3. Adversarial pass on the success criterion

The spec's §4.3 criterion as written — "materially lower external-fame profile than
production at the same bypass depths" — is **relative-only**, and relative-only is
attackable. Five attacks; the first three cover the three currencies as instructed.

**Attack 1 — the famous ladder (raw currency's ghost, in external units).** A config
steps down within fame: superstar interiors are replaced by merely-very-famous ones
(the owner's own unacceptable case, F3: Bowie → Pink Floyd → Beatles class). Fan counts
drop an order of magnitude; every artist is still someone he knows. The spec's relative
criterion **passes this config.** *Closed by C2:* an absolute-reach clause in the
owner's own calibrated "would not know them" band, which a ladder of household names
cannot satisfy — plus C3 forcing the profile to keep moving with depth.

**Attack 2 — the insular-cluster dive (percentile currency's ghost).** A config
satisfies fame-drop by always routing into one obscure-but-dense cluster (log §2.11's
lo-fi/synthwave stratum from the *in-graph* side; F6's ambient/neoclassical wobble is
the heard version). C1, C2, C3 can all pass while every journey ends in the same
corner regardless of endpoints. *Not fully closable offline.* Mitigations: the F5
confinement diagnostic (§1.5) and a per-arm report of the most-repeated interior
artists across pairs (a config whose top interiors recur across unrelated pairs is
flagged); the blind listen is the actual backstop, and this attack is the standing
reason the offline criterion **selects but never adopts**. **Residual risk accepted:**
an offline pass can still be an owner-fail; the cost of that residual is one burned
listen, not a wrong adoption.

**Attack 3 — the proxy's blind spots (external currency's own ghost).** Whatever
`nb_fan` under-counts becomes a free win: artists the owner knows perfectly well but
whose constituency is off-platform (legacy acts, regional stars — the graph verifiably
contains both, e.g. 林俊傑 and EGOIST in the log §2.2 top-degree list) read as
"obscure," so a config routes through genuinely famous artists the proxy scores low.
*Partially closed by §5:* the validation sample deliberately stresses legacy and
regional strata, and its catastrophic-inversion clause is exactly this attack in test
form. **Residual risk accepted and bounded:** the proxy is validated on ~tens of
artists, not the graph; any specific fame band the §5 test never sampled remains
attackable. If the listen and the offline scores disagree, the proxy is the first
suspect and §5's per-artist labels say where it lied.

**Attack 4 — coverage gaming (the matching seam).** The criterion excludes artists
whose exact-name proxy match fails, and match failure correlates with obscurity
(punctuation traps — the record's own Unicode-hyphen case, Phase 2 log §9 — plus the
known duplicate-name defect, log §2.2). A config routing into hard-to-match obscure
artists gets **its most obscure evidence silently dropped**, and — the sharper edge —
so does the *baseline* comparison if coverage differs between arms. *Closed by C6*
(coverage floor and a cap on the candidate-vs-P coverage gap) plus pre-registered name
normalisation (P5) and manual resolution of the residue. This is also why the harness
must not reuse `clips.py`'s first-hit matching (§0).

**Attack 5 — the shrinking-payload win.** Bypasses shorten paths until two obscure
interiors remain; the median plunges, the journey dies. The owner's own dogfooding
trace is the observed precedent (log §3.2: payload collapsed as length shortened) and
WHAT-GOOD #2 rules it out explicitly ("both, or neither counts"). *Closed by C4* and
the guard G floor of ≥ 1 interior.

**The criterion after the attacks** is the composite of §2.2: relative movement (C1)
**and** absolute calibrated reach (C2) **and** depth gradient (C3) **and** payload
preservation (C4) **and** coverage integrity (C6), with confinement and substitution
reported (F5/C7 diagnostics) and the blind listen holding the coherence dimension no
offline number tracks (log §3.8/§4). Attacks 2 and 3 are **not fully closed**; the
residuals are named above and accepted.

---

## 4. F1 resolved — guard, not tuning

**Decision: minimum-intermediary is a code guard — "a journey has at least one stop"
is a structural product invariant.** In the sweep it is applied in the harness,
identically in every arm including P; at adoption it ships as a code guard regardless
of which arm wins. (The roadmap's "hide bypass on start/end cards" UX item is distinct
and untouched, per the execution log's F1 note.)

**Mechanics** (code-grounded): exclusions are node-based (`pathfinding.py:78`) and
cannot express "forbid this edge," and the endpoints themselves are never excludable.
The guard is therefore: run Dijkstra; if the result is `[source, target]`, re-run with
the single edge source→target masked; the masked re-run's result is the path. (Mirror
implementation is a one-line neighbour filter; the shipped version at adoption belongs
in `find_path`, with a path-level test.)

**What each choice would have done to the sweep — the reason this had to be settled
first:**

- **Left to tuning**, the sweep acquires a second, entangled objective: arms get
  credit/blame for their *direct-path rate* as well as their fame profile. Concretely:
  (a) famous→famous cells that resolve direct have **no interior artists**, so the
  primary outcome is undefined exactly on the F1 pairs, and missingness would correlate
  with arm — a selection confound baked into the design; (b) the only way tuning makes
  a direct sim-1.0 edge lose is to make one near-zero-`w_sim` hop cost more than an
  entire detour (code read: a ceiling edge costs ≈ `w_hop` plus the jump term), which
  means a toll or hop-cost distortion large enough to warp every other path — the tail
  wagging the cost function; and (c) F1 is a *shape* requirement ("no journey"), not a
  fame gradient — tuning optimises the wrong currency for it.
- **With the guard**, the sweep optimises exactly one thing — the fame profile of
  journeys that exist — on a denominator fixed by construction, and arms remain
  comparable on every pair.

**Cost of the guard, stated:** the forced detour may itself read incoherent (the
execution log's F1 row raises precisely this). That cost is uniform across arms, so it
cannot confound the comparison; whether it is *acceptable* is a coherence question, and
coherence is decided by the blind listen, where every path the owner hears will have
been produced under the guard.

**INFERENCE, labelled:** that the owner endorses "≥ 1 stop" as an invariant is inferred
from his F1 report (a 2-card path "with no journey", filed as the one candidate code
guard). Falsifier: he declines the guard when the working session confirms it — in
which case this section reverts to tuning-with-selection-confound *documented as such*
(the pairs 4–5 cells would then be reported outside the primary outcome), and the
sweep's scope narrows. Confirm before the sweep runs; it is one question.

---

## 5. The fame-proxy falsification test (design only — not run here)

**What is being tested:** that Deezer `nb_fan` ranks artists the way the owner's
perception does, well enough to (a) score C1's contrasts and (b) set C2's absolute band
B_unk. The spec's §6.1 sketches this; here is the runnable version.

**Sample (~33 artists, fixed before fetching):**

- The **nine names** from the settled test-queue item (owner verdict already recorded —
  spec §1.2). Their labels exist; they anchor the "unknown" end.
- **Twelve interiors from the judged listen paths** (names are in the committed
  `listen_public.json`), chosen to span the strata the record identifies: superstar
  endpoints-class, the log §2.9 band (e.g. Whitney Houston, Paul Simon, Kylie Minogue),
  and each pair's least-famous interior.
- **Six likely-reach artists** — where winning arms will actually land: F6's named
  reaches (Max Richter, Ólafur Arnalds) and the log §2.11 insular-stratum artists
  (saib., Purrple Cat, idealism, Miami Nights 1984). This directly tests §2.11's
  *inference* that these would not feel famous to the owner — currently unverified.
- **Six stress cases for Attack 3** — plausibly-off-platform fame: Wishbone Ash,
  Chuck Berry, The Byrds, 林俊傑, EGOIST, CROOVE.

**Protocol:**

1. Owner labels each name into three buckets — *know well / heard of / never heard
   of* — **without seeing any fan count** (session hygiene per the blind-listen rules:
   the session collecting labels does not display proxy values).
2. Fetch `nb_fan` for all 33 via Deezer **artist** search, exact-name match after
   pre-registered normalisation (P5). Record match failures — this doubles as the
   matching pilot for C6.
3. Score:
   - **Rank agreement:** Spearman between bucket ordinal and log fan count.
   - **Catastrophic inversions:** count of *know well* artists whose fan count falls
     below any *never heard of* artist's.
   - **Band separation:** B_unk := the largest threshold t such that ≥ 80 % of sampled
     artists below t were labelled *never heard of* (require ≥ 5 artists below t for it
     to count).

**Pre-registered falsifiers — what forces a different proxy:**

- Spearman < **0.6**, or
- more than **2** catastrophic inversions, or
- no valid B_unk exists, or
- artist-search match failure > **20 %** of the sample after normalisation.

Any one fires → `nb_fan` is unfit; re-run the identical protocol (same labels, no
re-asking the owner) against **Wikipedia pageviews** (the spec's named fallback). If
that also fires → no automated proxy is fit at this granularity; terminal fallback is
owner-labelling of evaluated-path artists only (bounded: the sweep touches at most a
few hundred distinct interiors; labels are reusable across arms), and C1's statistic
degrades to the labelled ordinal scale. That outcome would be expensive but honest —
and it must be discovered **before** the sweep, which is the entire point of running
this first.

**Cost:** one short session plus ~10 minutes of owner time; a handful of API calls,
cached to disk.

---

## 6. What this experiment cannot tell you

1. **Whether the winner is better to listen to.** Coherence has no offline metric that
   tracks the owner's ear (log §3.8, §4). The sweep selects; the listen decides.
2. **Anything about the `known` mechanism.** Gate currency, additive-reward vs
   waypoint, substitute quality (F3) — all Stage B, on the winner's substrate, after a
   fresh Stage-0 binding check (log §3.7's non-transfer warning).
3. **Whether the production raw floor could have served as the depth device.** No arm
   isolates it (§1.4, by design).
4. **Mid-distribution regressions beyond the pair set.** The spec's own §6.2 worry —
   percentile gaps are large where raw gaps are small — is checked only on 12 pairs
   with famous-heavy endpoints. Obscure→obscure journeys are untested entirely.
5. **Generalisation beyond `graph-t15-tiebreakfix.bin`.** Weights bind per artifact
   (adjudication §6, claim 40's caveat); a future crawl or rebuild re-opens tuning.
6. **Real-user bypass behaviour.** The scripted policy (all-`known`, most-popular
   victim) is one deterministic strategy; the owner's real traces mix signals and
   victims. Telemetry at volume, not this sweep, settles behaviour-in-use
   (adjudication §6, claim 45).
7. **The guard's coherence price** (§4) — uniform across arms, so invisible to every
   offline comparison here; only the listen sees it.
8. **Proxy validity outside the sampled strata** (§3, Attack 3's residual).
9. **Whether the deferred builder routes (p99 rescale, `cap_strategy`) would do
   better.** T1 probes whether the ceiling *binds*; it does not test a rescale. R0/R2
   only say when those routes become due, per spec §5.
10. **Anything about clips** — except that C1/C2 clip defects remain a listen confound,
    as already recorded (spec §5).

---

## 7. Named prerequisites (working session; none block writing the plan, all block running arms)

| # | Prerequisite | Why |
|---|---|---|
| P1 | Capture the owner's F3/F6 bypass URLs from the 2026-07-23 test message into the Track 2 plan | Pair 8; the execution log says they live only in the branch/PR thread |
| ~~P2~~ | ~~Verify every §2.3 endpoint resolves in the Track 1 artifact~~ **DISCHARGED 2026-07-23 — do not redo.** All 24 endpoints (analysis, held-out, and reserve) verified three times independently: by G1's canonical-set bound selection, by the analyst review's M4, and by the toll-calibration Q4. `Nirvana` carries the known duplicate; highest-popularity rule applied. | Presence is no longer [DOC]-attested. The §2.3 substitution rule stands unused. |
| ~~P3~~ | ~~Measure the largest non-ceiling edge score; set `s_max` just above it~~ **WITHDRAWN 2026-07-23 (§9 A1) — executing it as written produces an inert arm.** Replaced by: pre-registered additive toll magnitudes (§1.4), already measured in `builder/analysis/2026-07-23-track2-toll-calibration/`. **No action remains for the working session.** | The rule and the goal were in conflict: binding "only on ceiling-saturated edges" forces `s_max` one grid step below the ceiling, which forces the toll to ~1.4 % of `w_hop`. Decoupling the binding set from the magnitude resolves it. |
| P4 | Run §5 (proxy validation + matching pilot) to verdict; apply the §2.2 recalibration rule if triggered | Nothing is scored until the proxy survives or is replaced |
| P5 | Fix the name-normalisation rule for proxy matching (NFKC fold + Unicode-punctuation folding, exact match after) | Attack 4; the record's own hyphen trap |
| P6 | Fix percentile tie-handling: average rank over the popularity array, computed once at harness start | Determinism; `np.argsort` alone is order-dependent among ties |
| ~~P7~~ | ~~Confirm the ≥ 1-intermediary invariant with the owner~~ **DISCHARGED 2026-07-23 — do not re-ask.** Owner: *"Every path must have at least one artist in between the start and end."* §4's labelled INFERENCE is confirmed, not inferred; recorded in §1.2's note and the execution log. | §4's labelled inference, now settled |
| P8 | **Half discharged 2026-07-23.** The pre-registration review landed — [`../findings/2026-07-23-track2-protocol-analyst-review.md`](../findings/2026-07-23-track2-protocol-analyst-review.md); its D1–D3 are amended above (§9), its **D4–D7 and PR-A/PR-B remain open** (§9's closing table). **P8b — the review of the *harness* — is not yet due: no harness exists.** | Spec §4.6 — both prior reviews of this experiment class found protocol defects |

---

## 8. Where this document disagrees with the governing spec — index

For the reviewer's convenience; each is argued in place above.

1. **Floor handling must be an explicit factor column** (§0, §1.3). The spec omits it;
   uncontrolled, it un-inerts inside every successful arm and breaks every "one-knob"
   claim in the sweep.
2. **The gate-currency knob cannot be a Stage A column** (§0, §1.1) — the gate it
   modulates does not exist in shipped code; it is Stage B's.
3. **The "dislike unaffected" guard is unsatisfiable as written for cost knobs**
   (§1.5); replaced with the F4 behavioural check.
4. **The relative-only success criterion is attackable in all three currencies**
   (§3); replaced with the C1–C6 composite, with two residuals named and accepted.
5. **§4.4's unconditional deletion of `w_floor`/`floor_relax_*` is premature if an FL
   arm wins** (§2.4 R5) — the floor would then be the shipped depth device, and the
   deletion clause needs amending at adoption rather than assuming.

---

## 9. Amendment index — 2026-07-23, before any arm ran

Five amendments, prompted by the `ml-graph-analyst` protocol review
([`../findings/2026-07-23-track2-protocol-analyst-review.md`](../findings/2026-07-23-track2-protocol-analyst-review.md)).
Each is marked inline at the passage it changes. **The pre-registration gate is intact:**
these were committed before any arm ran, and the commit timestamp is the evidence — which
is the whole mechanism, and the reason an amendment is written and committed rather than
applied silently at run time.

**Why amend rather than execute as written.** Three of the review's findings are
**arithmetic over the artifact, not opinion**: executing §1.4's T1 and FL arms literally
would have produced arms that provably cannot move, and reported their nulls as evidence.
An arm that cannot move is not a conservative test; it is a test whose result was fixed
before it ran.

| # | Amendment | Prompted by | Changes |
|---|---|---|---|
| **A1** | **T1's toll replaced and split into T1a/T1b.** The `min(sim, s_max)` form and P3's rule are withdrawn; the toll is now additive on edges at score exactly 1.0, at two pre-registered magnitudes (`s_toll` 0.95 and 0.80 = 7.5× and 30× `w_hop`). | **D1** | §0 T1 row · §1.4 arms + rationale · §7 P3 |
| **A2** | **The floor device is recalibrated to survive the scored window,** and early snapshots added. `floor_relax_known_pctl = 0.05` is pre-registered here instead of reusing `config.py`'s value; snapshots become d ∈ {0,1,2,3,5,7,10,15,20}. **The constant is chosen so the floor traverses its range over the snapshot span rather than being spent before it:** taking the base floors from review §2 M4, it is still non-zero at every snapshot through **d15 on all 12 pairs**, and through **d19** on the ten pairs whose base percentile floor exceeds 0.95. Deliberately *not* read from `config.py` — reusing the shipped constant is precisely what made the arms inert. | **D2** | §1.2 bypass protocol · §1.3 F row · §1.4 FL1 · §2.4 R3 |
| **A3** | **The percentile currency level is mean-matched by definition,** so J-cur is a genuine one-column contrast; arm **A1u** added to keep the scale component visible. | **D3** (second half) | §1.3 J-cur row + note · §1.4 A1u · run count |
| **A4** | **Read R6 added** — percentile arms moving ΔF positive while raw arms move it negative, with its mechanism, licenses and free falsifier. | **D3** (first half) | §2.4 |
| **A5** | **Two completeness gaps closed:** `w_degree_hub` named in the held-constant table (analyst **O3**), and the S-mag column's degeneracy at ceiling-saturated endpoints stated up front. | O3 + new measurement | §1.2 · §1.3 note |

### What the amendments cost, stated plainly

Run count **13 → 15**; compute still on the order of an hour. No change to the primary
outcome (§2.1), to any effect-size threshold (§2.2), to the pair sets (§2.3), or to the
attack analysis (§3). **No result was in hand when these were written** — no arm has run,
no path has been routed.

### Supporting measurement

`builder/analysis/2026-07-23-track2-toll-calibration/` (README owns its figures Q1–Q4).
It discharges the review's **PR-C** and re-confirms D1's arithmetic independently. Its
**Q4 was not anticipated by the review** and cuts *in favour* of T1: ceiling saturation is
rare in the graph at large but near-universal among this sweep's endpoints, so the toll
binds where the sweep actually routes — which makes a T1 null informative rather than
merely uninformative.

### Still open — this amendment set does NOT discharge the review

**D4, D5, D6, D7 and PR-A, PR-B are untouched.** Anyone reading §9 as "the review has been
addressed" would be wrong. In particular:

| Open item | What it blocks | Success condition — due when |
|---|---|---|
| **PR-A** — run **A0 vs P** on the full pair × depth grid **as a gate, first**, not as one arm among fifteen (review O7) | Whether `w_floor`'s inertness transfers to `graph-t15-tiebreakfix.bin`. If A0 ≢ P, §1.4 requires re-anchoring with floor fully crossed — 16 cells plus attachments, outside the stated budget | **Before the factorial runs.** Report alongside it the fraction of examined nodes carrying a non-zero floor term, so "identity holds but the term is firing" is visible rather than inferred |
| **D4** — C6 protects C1 (a median) but not C2 (an extreme) | Whether a lost obscure interior silently costs a C2 pass | Before scoring: make manual resolution mandatory for unmatched d15/d20 interiors, and pre-register unresolved cells as **C2-indeterminate**, not C2-fail |
| **D5** — §5's Spearman and inversion falsifiers are not interpretable on §5's own purposive sample | The fame-proxy verdict (P4) | Before §5 runs: per-stratum reporting, Spearman additionally within the "heard of" + "know well" subset, inversions as a rate within the stress stratum, tie-corrected variant named |
| **D6** — the held-out gate passes ~31 % of candidates under the null | Only the *labelling* of the held-out step as "confirmation" | Before the winner goes to held-out: either state 0.3125 in §2.2 or tighten to 4-of-4 |
| **D7** — guard G undefined when the direct edge is a bridge | Arm-correlated missingness returning by the back door | Before the sweep: pre-register that a guard-infeasible cell is dropped from **all** arms uniformly and reported |
| **PR-B** — cost decomposition on routed dive hops under both currencies | Settles R6/D3 directly rather than by edge-level marginals | Optional; if R6 fires, this is the confirmatory measurement |
| **O1, O2, O8, O9, O10** — reporting and framing items | Nothing structural; each asks for a sentence or a stratified report | At harness-writing time |
