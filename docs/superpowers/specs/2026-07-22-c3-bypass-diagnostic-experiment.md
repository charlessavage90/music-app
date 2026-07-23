# C3 bypass diagnostic — experiment protocol

**Role: COMPLETE (experiment protocol, executed).** Stage 0 ran; the A-vs-C question it
feeds is moot until Track 2 lands a cost function a mechanism can reach obscurity through.
Results are in the Phase 1 log §3; the re-run condition is the 2026-07-23
defect-remediation-and-cost-retune spec §4.4.

**Historical protocol text follows — Phase 1, Task 1.** This is the cheapest decisive
experiment for the C3 mechanism choice, run *before* the rest of Phase 1 is planned. It
produces a shortlist and a coherence guardrail; **it does not adopt anything.** Adoption of
any scoring change still requires a blind listen (roadmap; offline metrics have decided the
graph zero times, the ear twice).

Results, when produced, go to `docs/superpowers/findings/`. This file is the protocol only.

**Revision 2 (2026-07-22).** Rewritten after an `ml-graph-analyst` critique of revision 1.
Changes: M3 corrected to geometric mean; overlap coefficient added as a mandatory
degree-neutral co-guardrail (§4.3); the run is split into a cheap **Stage 0 binding
pre-check** and a **Stage 1 full panel**, because the revision-1 `known` form may not bind at
all; held-out replication, bootstrap CIs and a predefined effect size added; workload
stratified by endpoint popularity; M5/M6 redefined. The confounds each change closes are
noted inline.

---

## 1. The decision this changes

C3 must give `known` a real behaviour and stop bypass from collapsing into hub-swapping.
Candidate mechanisms are on the table (§4). We do **not** know which to build, or even whether
the leading `known` form binds. This experiment replays a real bypass workload under each
candidate and measures whether it delivers *more novel artists as bypasses accumulate*
**without** buying that novelty by breaking path coherence — the failure that shelved the
global hub penalty (adjudication §4, claim 40: hub-avoidance bought at a ~tenfold Adamic–Adar
collapse).

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
- **Free hub expressways** — Smiths↔Shins scored exactly 1.0 (p99 ceiling), zero similarity
  cost. Hub-to-hub edges have the highest co-occurrence, so they clip to 1.0 first. A probe
  during protocol review found this affects only a **small minority** of hub-hop edges, so
  the ceiling is a *real but modest* gravity source, not the dominant one — M5 measures its
  size, it is not assumed.

Two gravity sources are in play and the experiment must separate them: (1) genuine hub
topology, which a blunt `w_hub` fights at a coherence cost; (2) the p99 ceiling, which
manufactures free hub hops. The rank transform that removes the ceiling lost a blind listen
(handoff §2), so it is not a free win.

## 3. Two-stage structure

The revision-1 `known` form (§6) may not bind — it can at most halve an already-expensive
diving edge, and may be swamped by the `w_jump` popularity-cliff term for the same structural
reason `w_floor` never binds (adjudication §5.4). Building the full panel before knowing the
mechanism works is premature. So:

- **Stage 0 — binding pre-check (a few lines, run first).** On the owner trace (W1) under V1,
  instrument, per interior node, whether `pop(v) < floor`, and per bypass step the
  **argmin-flip rate** vs V0 — the count of edges whose cheapest-predecessor choice changes
  because of the discount. This single instrument settles two questions at once:
  1. **Does the `known` discount bind at all?** Zero argmin flips ⇒ the form is inert;
     **stop and redesign the mechanism (§6) before Stage 1.** Report "inert" as the finding —
     it is a real result, not a failed experiment.
  2. **Is the `w_floor`-deletion confound real?** Claim 23 proved `w_floor` never binds *on
     the old `known` mechanism* (0/20 paths dipped below floor). The new mechanism is designed
     to push *below* `pop(K)`, i.e. toward the floor. If any interior `pop(v) < floor`, then
     V1 differs from V0 by **two** behavioural knobs (new `known` **and** a floor term that is
     no longer null), and the §4 factor table's "one column" claim fails. If the fraction is
     0, claim 23 transfers and the confound is empirically void.

- **Stage 1 — full panel.** Only if Stage 0 shows the mechanism binds. Runs §4's variants over
  §3.1's workload with §5's metrics and §7's decision rule. If Stage 0 exposed a real floor
  confound, Stage 1 carries `w_floor` as a constant *present* column in both V0 and V1 (or
  adds a V1+floor arm), rather than treating its removal as null.

### 3.1 Workloads (Stage 1)

Run every variant against all three. The owner trace is the ground-truth validation case;
the simulated policies give a distribution rather than an anecdote.

- **W1 — owner trace (case study).** The real accumulating exclusion sets from the 2026-07-22
  session (URLs on file). Does the candidate invert *his* observed collapse? Also the Stage 0
  workload.
- **W2 — hub-targeting auto-bypass.** **200 seeded random connected pairs, stratified by
  endpoint popularity** into popular–popular, popular–obscure, obscure–obscure (report M1/M3
  per stratum — the app's real use is people searching artists they *know*, where `floor`
  binds and hub gravity is highest, so uniform sampling under-weights the regime that
  matters). Split **100 analysis / 100 held-out**. At each step bypass the highest-
  `hub_penalty` interior artist, to **K = min(10, initial_interior)** bypasses (report the K
  distribution; exhaustion correlates with short paths, so a fixed K would silently bias the
  panel toward long hub-heavy paths). Two policies mapping to the two buttons:
  **P-known-hub** and **P-dislike-hub**.
- **W3 — random-interior auto-bypass (control).** As W2 but bypass a uniformly random
  interior artist. Separates "the mechanism reaches novelty" from "any exclusion churns the
  path."

Seeds fixed and recorded (determinism, spec §9). Pairs drawn once and reused across all
variants so the workload is identical per row (paired design — the source of the statistical
power in §7).

## 4. Candidate variants and factor table

`w_known`, the conditional-hub term, and `τ_hub` are **new to C3** (not in `config.py`) and
are defined in §6. `w_floor` deletion is *provisionally* treated as null per claim 23 — but
**Stage 0 verifies this empirically** before Stage 1 relies on it (§3).

| Variant | `known` mechanism | `dislike` mechanism | `w_hub` | Isolating baseline | Diagnostic policy |
|---|---|---|---|---|---|
| **V0 baseline** | floor-relax (inert) | avoidance | 0 | — (control) | — |
| **V1 buttons-only** | obscure-substitution | avoidance | 0 | V0 → isolates `known` fix | P-known-hub |
| **V2 + conditional hub** | obscure-substitution | avoidance + hub-scoped penalty when disliked node is a hub | 0 | V1 → isolates dislike-side change | P-dislike-hub |
| **V3 + global hub** | obscure-substitution | avoidance | >0 (swept) | V1 → isolates a permanent global `w_hub` | P-dislike-hub |

Each variant differs from its named baseline by **exactly one** column (subject to the Stage 0
floor check for V1). **State the diagnostic policy per contrast** so a null under the
irrelevant policy is not misread: V1-vs-V0 is exercised by P-known-hub; V2-vs-V1 and V3-vs-V1
by P-dislike-hub. V3 is a coherence-cost **anchor** — the shelved lever, kept so its cost is
visible on *this* graph rather than argued from memory, not a candidate for shipping a global
value. All variants run on the **same artifact** (`graph-t15-capfix.bin`); `w_hub` is per-graph
normalised and its values are **not** comparable across graphs (adjudication §4.6) — compare
how metrics *respond*, never a shared `w_hub` value.

## 5. Metrics (per path state, i.e. per bypass step)

- **M1 Payload (primary).** Absolute count of non-hub interior artists. "Hub" = `hub_penalty
  ≥ τ`; report at **τ ∈ {0.70, 0.85, 0.95}**. τ = 0.70 is the load-bearing threshold; τ = 0.95
  qualifies so few nodes that M1@0.95 ≈ interior count and is nearly insensitive — report it
  but do not lead on it. Also report a top-1%-by-degree hub definition; if the two disagree on
  the *ranking of variants*, that disagreement is itself a finding.
- **M2 hubfrac (companion).** Interior hubs / interior count. Scale-invariant; keep as the
  normalised companion but never as the primary (roadmap: it ranks the payload case backwards).
- **M3 Adamic–Adar (coherence guardrail).** **Geometric mean over consecutive hops**, exactly
  as `evaluation.py`/`path_metrics` computes it and as claim 40 computed the ~10× collapse.
  *Not* arithmetic mean: geometric mean is dominated by the worst hop, which is the whole point
  — one zero-overlap bridge hop must tank it, or the guardrail is blind to the incoherent-hop
  failure it exists to catch.
- **M3b Overlap coefficient (mandatory degree-neutral co-guardrail).** Geometric mean over
  hops. **Required** by adjudication §4.3: AA carries a measured pro-hub min-degree coupling
  (claim 16), and the `known` mechanism lowers interior degree *by design*, so AA will fall for
  a degree reason, not a coherence reason. Decision rule (§7) requires AA and overlap
  coefficient to **move together**; a candidate that drops AA while holding overlap coefficient
  is lowering degree, not breaking coherence, and is **not** rejected on that basis.
- **M4 Path length (observable, not target).** Diagnostic only (roadmap).
- **M5 Ceiling-saturation on hub hops.** Fraction of hub-to-hub edges *traversed* whose score
  is exactly 1.0 — **pooled over all traversed hub-hop edges across the whole workload**, not
  averaged per path (per-path is frequently 0/0). State τ (use τ = 0.70). Read as a magnitude:
  the review probe found the ceiling saturates only a small minority of hub-hop edges, so this
  quantifies "how much of the gravity is artificial," not a yes/no.
- **M6 Hub-replacement rate (swap-vs-reroute).** Fraction of bypass steps where the removed
  hub's slot is filled by a node with `hub_penalty` within ε of it. This directly measures the
  owner's "circling." **Retained-node overlap alone is insufficient** — it measures churn
  *magnitude*, is inflated by the two fixed endpoints (~`2/length`), and moves with path length
  (M4); report it only as a secondary descriptor.

M1 and M6 plotted against bypass count are the two curves that carry the decision.

## 6. New mechanisms (starting forms; Stage 0 tests whether the `known` form binds)

**`known` obscure-substitution.** For a `known` node K, qualifying substitutes are its direct
neighbours `v` with `pop(v) < pop(K)`. Discount `d(v) = clip(sim(K,v)·(pop(K) − pop(v)), 0, 1)`.
Revision-1 applied this as a multiplicative discount on edges *into* v — **the review found two
defects**: (a) inbound-only discounting is the wrong target, because to route *through* v the
path must also *leave* v via an undiscounted, expensive climb back toward the (usually more
popular) target; (b) `d(v)` applied to every inbound edge of v regardless of source hands a
windfall to any v that already sits on a cheap corridor. **Corrected starting form:** discount
v's **throughput** — apply the factor to both incident edges on the substitution hop — or,
equivalently, fold in a **bounded node reward** subtracted from the path cost when v is
traversed, capped so no edge cost goes `< w_hop` (Dijkstra non-negativity is preserved; a
reward is never a negative edge). `w_known ∈ (0,1]` (start 0.5), swept. K itself stays hard-
excluded. **Stage 0 decides whether this form binds before Stage 1 invests in it.**

**Conditional (signal-scoped) hub penalty.** When a `dislike` targets a node with `hub_penalty
≥ τ_hub`, add a temporary `w_hub_local · hub_penalty(v)` term to edge costs **for that reroll
only**, decaying with each subsequent non-hub bypass. Scoped to the reroll where the user
signalled they want out of hub territory, so default paths keep their coherence. `w_hub_local`
swept on the same grid as V3's `w_hub`.

## 7. Decision rule

The experiment **ranks and shortlists; it does not adopt.** A candidate advances to a blind
listen iff, relative to its isolating baseline under the diagnostic policy (§4):

- **(a) Payload.** M1 rises (or falls less steeply) with bypass count, by a **predefined
  minimum meaningful delta** — anchored to the owner's complaint (he saw ~6→2 at ~10 bypasses),
  so **≥ 1 additional non-hub interior artist at K = 10**. Smaller than that is "within noise,"
  not a win.
- **(b) Coherence.** M3 (geometric AA) stays within a recorded fraction of baseline **and** M3b
  (overlap coefficient) does not fall — no repeat of the claim-40 collapse, and no false
  rejection for the degree reason of §5/M3b.
- **(c) Reproduction.** The **sign** of the M1 and M6 differences **reproduces on the held-out
  100 pairs**. This is the exact discipline claims 41–42 demand: overlap-family effects at this
  scale sign-flipped between analysis and held-out slices, so an effect that does not reproduce
  is noise.

Report per-step paired differences with **bootstrap 95% CIs** across the shared pairs. Advance
the best 1–2 candidates that clear (a)+(b)+(c). **If none clears, that is a valid and important
result** — the mechanism space here is insufficient and C3 needs rethinking, not a blind listen.

M5 answers a separate question: if a large fraction of traversed hub hops are ceiling-saturated,
the p99 fix is worth prioritising as a gravity lever; the review probe suggests it is a minority,
so M5 likely reports "modest" — confirm the magnitude, then leave the p99 fix parked against its
own success condition unless M5 surprises.

## 8. Guardrails and traps

- **Graph identity.** Run on `graph-t15-capfix.bin`; assert sha256 `c8af6e…` at start. A
  conclusion from the wrong artifact looks exactly like a correct one.
- **Determinism.** Fixed, recorded seeds; pairs drawn once and shared across variants.
- **Env.** `UV_LINK_MODE=copy`, `PYTHONIOENCODING=utf-8`, `python -u` for any long run.
- **No figure restatement.** Cite the adjudication by section; do not copy its numbers here or
  into the results doc (docs/README.md, the one rule). The probe numbers referenced above are
  design rationale to be re-measured in Stage 1, not enshrined figures.
- **Reuse the shipped metric code.** M3/M3b must call the same AA / overlap-coefficient
  implementation as `evaluation.py`, not a re-derivation, so the guardrail is comparable to the
  shelving number.

## 9. Non-goals

- Not an adoption decision. The ear decides; this filters what reaches the ear.
- Not a `w_hub` re-tuning for production — V3 is a coherence-cost anchor, not a shipping value.
- Not a test of first-path quality — the Phase 2 sweep covered first paths; this is strictly
  behaviour *under bypass*, the channel that decided the adoption and that no prior measurement
  touched.

## 10. Implementation notes

Offline script under `api/` reusing `graph_store.GraphStore`, `pathfinding.find_path`,
`Exclusion`, the `evaluation.py` metric functions (for M3/M3b), and a variant-parameterised
copy of the cost function. `w_known`, `w_hub_local`, and `τ_hub` live in a throwaway experiment
config, **not** in `ApiConfig`, until a mechanism is chosen — nothing lands in the shipped
config from a diagnostic. Stage 0 emits the per-node `pop(v) < floor` flags and per-step
argmin-flip counts on W1. Stage 1 emits a per-(variant, workload, stratum, step) CSV plus the
M1/M6 curves with bootstrap CIs, analysis and held-out reported separately.
