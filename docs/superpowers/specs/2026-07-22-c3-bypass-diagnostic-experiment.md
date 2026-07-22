# C3 bypass diagnostic — experiment protocol

**Role: ACTIVE (experiment protocol). Phase 1, Task 1.** This is the cheapest decisive
experiment for the C3 mechanism choice, run *before* the rest of Phase 1 is planned. It
produces a shortlist and a coherence guardrail; **it does not adopt anything.** Adoption of
any scoring change still requires `ml-graph-analyst` review and a blind listen (roadmap;
offline metrics have decided the graph zero times, the ear twice).

Results, when produced, go to `docs/superpowers/findings/`. This file is the protocol only.

---

## 1. The decision this changes

C3 must give `known` a real behaviour and stop bypass from collapsing into hub-swapping.
Three candidate mechanisms are on the table (below). We do **not** know which to build. This
experiment replays a real bypass workload under each candidate and measures whether it
delivers *more novel artists as bypasses accumulate* **without** buying that novelty by
breaking path coherence — the exact failure that shelved the global hub penalty
(adjudication §4, claim 40: hub-avoidance bought at a ~tenfold Adamic–Adar collapse).

Output: the 1–2 candidates worth carrying to a blind listen, plus a measured answer to
whether the p99 ceiling is a material source of hub gravity.

## 2. Background (the observed failure)

From owner dogfooding, 2026-07-22, on `graph-t15-capfix.bin` (sha256 `c8af6e…`), a
Shins → Wishbone Ash path bypassed ~15 times. Reconstructed against the full graph:

- **Payload collapsed as bypasses accumulated** — non-hub interior artists fell from ~6 to
  ~2 while path length *shortened* 11 → 7. The inverse of the stated target (handoff §5:
  successive bypasses, especially of hubs, should yield *progressively fewer* hubs).
- **Hub-for-hub swapping** — bypassing Aerosmith (hub, via `dislike`) returned Pearl Jam
  (parallel hub); a stable spine with a rotating hub slot ("circling").
- **Free hub expressways** — Smiths↔Shins scored exactly 1.0 (p99 ceiling), i.e. zero
  similarity cost. Hub-to-hub edges have the highest co-occurrence, so they clip to 1.0
  first — a *hypothesised* material contributor to hub gravity, measured in M5 below.

Two gravity sources are in play and the experiment must separate them: (1) genuine hub
topology, which a blunt `w_hub` fights at a coherence cost; (2) the p99 ceiling, which
*manufactures* free hub hops and may be the cleaner target — but the rank transform that
removes it lost a blind listen (handoff §2), so it is not a free win either.

## 3. Workloads

Run every variant against all three. The owner trace is the ground-truth validation case;
the simulated policies give a distribution rather than an anecdote.

- **W1 — owner trace (case study).** The real accumulating exclusion sets from the 2026-07-22
  session (URLs on file). Does the candidate invert *his* observed collapse?
- **W2 — hub-targeting auto-bypass.** Over M = 100 seeded random connected pairs, to
  K = 10 bypasses each: at each step bypass the highest-`hub_penalty` interior artist. Two
  policies, mapping to the two buttons: **P-known-hub** and **P-dislike-hub**.
- **W3 — random-interior auto-bypass (control).** Same as W2 but bypass a uniformly random
  interior artist. Separates "the mechanism reaches novelty" from "any exclusion churns the
  path."

Seeds fixed and recorded (determinism, spec §9). Pairs drawn once and reused across all
variants so the workload is identical per row.

## 4. Candidate variants and factor table

`w_floor` deletion is treated as behaviourally null — it is a *proven* no-op (adjudication
§5.4, claim 23), so removing it changes no measured quantity and is not a varying column.
`w_known` and the conditional-hub term are **new to C3** (they do not exist in `config.py`
today) and are defined in §6.

| Variant | `known` mechanism | `dislike` mechanism | `w_hub` | Isolating baseline |
|---|---|---|---|---|
| **V0 baseline** | floor-relax (inert) | avoidance | 0 | — (control) |
| **V1 buttons-only** | obscure-substitution | avoidance | 0 | V0 → isolates `known` fix |
| **V2 + conditional hub** | obscure-substitution | avoidance + hub-scoped penalty when the disliked node is a hub | 0 | V1 → isolates dislike-side change |
| **V3 + global hub** | obscure-substitution | avoidance | >0 (swept) | V1 → isolates a permanent global `w_hub` |

Read across each row: every variant differs from its named baseline by **exactly one**
column. V3 is included as an anchor — it is the shelved lever, kept so its coherence cost is
visible on *this* graph rather than argued from memory. All variants run on the **same
artifact** (`graph-t15-capfix.bin`); `w_hub` is per-graph normalised and its values are
**not** comparable across graphs (adjudication §4.6) — compare how metrics *respond*, never a
shared `w_hub` value.

## 5. Metrics (per path state, i.e. per bypass step)

- **M1 Payload (primary).** Absolute count of non-hub interior artists. "Hub" = `hub_penalty
  ≥ τ`; report at **τ ∈ {0.70, 0.85, 0.95}** because the threshold is a soft proxy for
  "novel" (roadmap: owner called Vulfpeck a hub though it is not one structurally). Also
  report top-1%-by-degree as a second hub definition; if the two disagree on the ranking of
  variants, that disagreement is itself a finding.
- **M2 hubfrac (companion).** Interior hubs / interior count. Scale-invariant; keep as the
  normalised companion but never as the primary (roadmap: it ranks the payload case
  backwards).
- **M3 Adamic–Adar (guardrail).** Mean over consecutive hops. This is the coherence floor
  that a naive `w_hub` breaks; any payload gain must be read against its AA cost.
- **M4 Path length (observable, not target).** Tracked as a diagnostic only (roadmap).
- **M5 Ceiling-saturation on hub hops.** Fraction of hub-to-hub edges *traversed* whose
  score is exactly 1.0. Tests the §2 hypothesis that the ceiling is a material gravity
  source — before any effort is spent removing it.
- **M6 Bypass node-overlap.** Retained-node fraction between path at step *t* and *t+1*.
  Distinguishes "hub swap" (high overlap, one slot rotates) from genuine reroute — the
  measure the roadmap's bypass-substitution lead asked for.

M1 and M6 plotted against bypass count are the two curves that carry the decision.

## 6. New mechanisms (starting forms; exact values are what the experiment sweeps)

**`known` obscure-substitution.** For a `known` node K, qualifying substitutes are its
direct neighbours `v` with `pop(v) < pop(K)`. Discount `d(v) = clip(sim(K,v)·(pop(K) −
pop(v)), 0, 1)`. Apply as a **multiplicative discount on the positive cost of edges into v**:
`cost' = cost · (1 − w_known · d(v))`, with `w_known ∈ (0,1]` (start 0.5). This keeps every
edge cost `≥ w_hop > 0`, so **Dijkstra's non-negativity is preserved** — a reward must never
be a negative edge. K itself is still hard-excluded.

**Conditional (signal-scoped) hub penalty.** When a `dislike` targets a node with
`hub_penalty ≥ τ_hub`, add a temporary `w_hub_local · hub_penalty(v)` term to edge costs
**for that reroll only**, decaying with each subsequent non-hub bypass. Scoped to the reroll
where the user signalled they want out of hub territory, so default paths keep their
coherence. Starting `w_hub_local` swept on the same grid as V3's `w_hub`.

## 7. Decision rule

The experiment **ranks and shortlists; it does not adopt.** A candidate advances to a blind
listen iff, relative to its isolating baseline: **(a)** M1 rises (or falls less steeply) with
bypass count under the hub-targeting policies, **and (b)** M3 (Adamic–Adar) stays within a
recorded fraction of baseline — no repeat of the claim-40 collapse. Report the payload-vs-AA
tradeoff for every variant; advance the best 1–2. If no candidate satisfies (a)+(b), that is
a valid and important result — it means the mechanism space explored here is insufficient and
C3 needs rethinking, not a blind listen.

M5 answers a separate question: if a large fraction of traversed hub hops are ceiling-
saturated, the p99 fix is worth prioritising as a gravity lever; if not, it can stay parked
against its own success condition.

## 8. Guardrails and traps

- **Graph identity.** Run on `graph-t15-capfix.bin`; assert sha256 `c8af6e…` at start. A
  conclusion from the wrong artifact looks exactly like a correct one.
- **Determinism.** Fixed, recorded seeds; pairs drawn once and shared across variants.
- **Env.** `UV_LINK_MODE=copy`, `PYTHONIOENCODING=utf-8`, `python -u` for any long run.
- **No figure restatement.** Cite the adjudication by section; do not copy its numbers here
  or into the results doc (docs/README.md, the one rule).
- **`ml-graph-analyst` checkpoint.** Recommended to critique *this protocol* before the run
  (it defines new metrics and leans on Adamic–Adar), and again on the results before any
  candidate is called a winner. Derivation, not judgement.

## 9. Non-goals

- Not an adoption decision. The ear decides; this filters what reaches the ear.
- Not a `w_hub` re-tuning for production — V3 is a coherence-cost anchor, not a candidate for
  shipping a global value.
- Not a test of first-path quality — the Phase 2 sweep already covered first paths; this is
  strictly about behaviour *under bypass*, the channel that decided the adoption and that no
  prior measurement touched.

## 10. Implementation notes

Offline script under `api/` reusing `graph_store.GraphStore`, `pathfinding.find_path`,
`Exclusion`, and a variant-parameterised copy of the cost function. `w_known`,
`w_hub_local`, and `τ_hub` are added to a throwaway experiment config, **not** to
`ApiConfig`, until a mechanism is chosen — nothing lands in the shipped config from a
diagnostic. Emits a per-(variant, workload, step) CSV plus the M1/M6 curves.
