# C3 `known` mechanism — blind listen workload

**Role: ACTIVE (evaluation protocol). Phase 1.** Decides, by ear, between the two
redesigned `known`-mechanism shapes that Stage 0 proved bind but that offline metrics
**cannot** separate (AA/OC collapse while `mean_common_neighbours` rises — adjudication §4.3
degree-coupling, confirmed live). This is the arbiter; the offline diagnostic feeds it, it
does not feed the offline diagnostic. Per project norms the ear has decided the graph twice
and offline metrics zero times.

Workload design is the owner's (2026-07-22), refined below.

---

## 1. The decision this makes

Which shape should the `known` button take:

- **A — additive node reward.** Bounded reward subtracted when the path traverses a
  similar-but-more-obscure cousin, cap allowing edge cost → 0. Single coherent Dijkstra.
  Stage 0: binds, reaches obscurity, but **keeps ceiling hub hops** alongside the rewards.
- **C — hard waypoint.** Routes source → best-similarity obscure cousin → target. Stage 0:
  binds by construction, **hub-free and coherent on deep bypass**, but forces an incoherent
  detour on shallow bypass. (Cost-based "route-aware" selection was tried and **rejected** on
  the owner trace — minimising detour cost selects hub-adjacent cousins, because the free
  ceiling hub hops are the cheapest routes, so it gets captured by the very expressway it
  should escape. C therefore uses the naive best-similarity cousin.)

The ear decides which is the better *journey* and — the load-bearing question — which makes
**hubs decline as bypasses accumulate** (owner's stated target, handoff §5). Refinement of the
selection rule is deferred to the winning shape; it is not settled here.

## 2. Why offline can't decide it (so this must)

Stage 0's coherence metrics disagreed by construction: the mechanisms lower interior degree
*by design*, which mechanically depresses AA and inflates `overlap_coefficient`'s reciprocal-
degree denominator, while raw `mean_common_neighbours` moves the other way. No offline metric
is trustworthy in exactly the regime the mechanism targets. The perceptual question — "is this
a good journey, and do hubs thin out as I bypass?" — is the only one that resolves it.

## 3. Workload

**Pairs — 4, stratified by endpoint popularity** (the stratum Stage 0 could not clear is
popular↔popular, where the obscurity floor binds and hub gravity is highest):

| # | stratum | notes |
|---|---|---|
| 1 | popular ↔ popular | the real-use case; worst for hub gravity |
| 2 | popular ↔ obscure | asymmetric, like the owner's Shins→Wishbone Ash trace |
| 3 | obscure ↔ obscure | tail behaviour, where mutual-kNN prunes hardest |
| 4 | popular ↔ popular, different genre families | long journey, more hub temptation |

Concrete artists chosen at generation time; recorded in the results doc. The owner must know
the endpoints (they are his choice in real use) but **not** which mechanism produced which
path.

**Bypass policies — weighted toward `known`, because A and C only change `known`:**

- **P1 all-`known`, hub-targeted (PRIMARY).** At each step bypass the highest-`hub_penalty`
  interior artist with `known`. This is the discriminator — it exercises exactly the mechanism
  under test, on exactly the hubs the complaint is about.
- **P2 mixed 50/50, hub-targeted (SECONDARY).** Alternate `known`/`dislike` on the top hub.
  Realistic mixed use.
- **P3 all-`dislike` (CONTROL, sanity only).** A and C are **identical** under all-`dislike`
  (neither changes dislike behaviour), so this cannot discriminate them — it is a check that
  nothing regressed, not a comparison. State this to the listener so a null is not misread.

**Snapshots — at 5, 10, 15, 20 bypasses** per (pair, policy). The bypass-depth axis is the
whole point: the target is a *monotone* decline in hubs across depth, not a hub-free first
path.

## 4. What the listener hears

For each (pair, policy, snapshot): the **A path** and the **C path**, presented **blind** and
in randomised order (no mechanism label, no metric shown). The current-production path (V0) is
included as a hidden third anchor on the primary policy only, so "neither beats today" is a
possible and recordable verdict.

Per pair×policy, the listener hears the depth sequence **in order** (5 → 10 → 15 → 20) for a
given arm, because the judgement is about *how the journey evolves with bypass depth*, not
about a single snapshot. Arms are shuffled; depth order within an arm is preserved.

## 5. Blind protocol (per project norms)

- The session that runs the listen says **nothing beyond the bare mechanics** and is held
  **ignorant of the expected outcome**. No framing, no "A is the reward form," no metric
  readout. (How-to-present-results §Exception.)
- Mechanism→label mapping is generated, sealed, and revealed only after all verdicts are
  recorded.
- The listener judges against `WHAT-GOOD-LOOKS-LIKE.md` — preference calibration, **not**
  criteria — and states, per pair×policy: (a) better arm, or "no preference"; (b) whether hubs
  thinned with depth; (c) any degenerate behaviour (incoherent hop, dead clip, absurd length).

## 6. Recorded but hidden until after the verdict

For every path in the set, compute and store `PathMetrics` (payload = non-hub interior count
at τ=0.70, hubfrac, AA, overlap_coefficient, mean_common_neighbours, ceiling_hops, length).
**Not shown during the listen.** Afterwards, check which offline metric — if any — tracked the
ear. If one does, it earns a place in future automated evaluation; if none does, that is itself
the finding (offline evaluation of bypass quality is not yet possible) and the roadmap's
"bypass hub-decline metric" success condition stays open.

## 7. Delivery — what must be built first

A throwaway **listen harness**, not shipped code:

- Implement A and C behind a query flag in a local API build (`?mech=A|C|V0`), reusing
  `find_path` for V0 and the Stage 0 `dijkstra`/`waypoint` functions for A/C. **Not** merged
  into `ApiConfig` or `pathfinding.py` until a shape wins.
- A generator that, given a pair and policy, walks the hub-targeted bypass sequence and emits
  the path URL at each snapshot for each arm — so the owner opens real app pages with real
  clips (clip resolution is unchanged and shared across arms).
- The generator records the sealed label mapping and the hidden `PathMetrics`.

## 8. Non-goals / guardrails

- Not a re-test of a settled question — this is the *first* evaluation of the redesigned
  mechanism, not a re-run of anything (execution log §15 forbids re-testing an unwelcome
  result; this is a new mechanism).
- Not a selection-rule bake-off — A vs C is a **shape** decision; the losing shape is dropped,
  the winner's selection rule is refined afterward.
- Run on `graph-t15-capfix.bin` (sha256 `c8af6e…`), asserted at generation.
- The all-`dislike` control cannot discriminate A/C by construction — never read its null as a
  verdict.
- Clips are known-buggy (Phase 1 C1/C2) and **shared across arms**, so a dead clip is not a
  differentiator — instruct the listener to ignore clip failures unless they differ by arm.
