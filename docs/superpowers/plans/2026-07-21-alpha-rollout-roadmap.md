# Alpha Rollout Roadmap

**Date:** 2026-07-21
**Supersedes:** ad-hoc phase lists. This is the current plan of record.
**Inputs:** three expert reviews (architect / QA / ML-graph), an ML follow-up review, an objective path-quality harness, and the first real dogfooding session.

---

## Rollout gates

Work is organised by **three release gates**, each with a different quality bar. The bar is not moving — these are sequential gates, and knowing which gate a task belongs to is how we avoid gold-plating.

1. **Gate 1 — Personal use.** Charles uses it regularly and enjoys it. Runs locally.
2. **Gate 2 — Friends & family.** ~5–20 known people, deployed on AWS.
3. **Gate 3 — Public.** Reddit-scale traffic, hostile inputs, real cost.

---

## Meta-lesson: sequence review after use, not before

Three expert reviewers read the code and found real defects. **Twenty minutes of actual use surfaced an entire class they all missed, including the single most severe bug of the session.**

- All three reviewers were backend-focused; none flagged a frontend defect. Dogfooding found four.
- The clip-expiry bug was **invisible to both code review and tests** — tests mock HTTP, so a URL that expires in an hour is indistinguishable from one that doesn't.
- The hub problem took ~90 minutes of graph analysis to establish; dogfooding confirmed it in three rerolls.

**Practice going forward: dogfood before the next review round.** Reviewers answer "is this code sound"; only use answers "is this product right".

---

## Confirmed diagnoses (root causes, do not re-investigate)

### C1 — Clip plays the wrong artist
Deezer's general search matches **song titles as well as artists**, and we take `data[0]` blindly. Searching `The Format` returns:

1. track "The Format" by **AZ** (a hip-hop artist) ← what we played
2. "Holy Roller" by **The Format** ← correct
3. "On Your Porch" by **The Format**

Graph resolution was correct; only the clip was wrong. **Fix:** match the returned track's artist name against the requested artist rather than taking the top hit.

### C2 — Clips silently die after ~an hour
Deezer preview URLs are **signed and time-limited** (`hdnea=exp=…`). Measured: a URL fetched at 09:41 had already expired by 10:12. We cache them for **30 days**. Every cache hit past the first hour serves a dead URL; the CDN returns an error page and the browser blocks it — the `OpaqueResponseBlocking` seen in the console log.

**Fix:** cache the **track identity** (stable) separately from the **signed URL** (volatile); re-resolve the URL per request. This also delivers the "play a different song" feature nearly free, since we hold a track list.

### C3 — `w_floor` is a no-op; "know them already" has no real behaviour
`w_floor` is a provable no-op — it reproduces the no-floor result to every digit, because routes never dive below `min(pop_source, pop_target)`, so the floor never binds. Delete `w_floor` and `floor_relax_*`, and give `known` a real behaviour.

**Corrected:** an earlier version of this entry claimed the two bypass signals are *behaviourally identical at runtime*. That is wrong — `dislike` still applies `avoidance_map`; only `known` degrades to a plain hard exclusion. See `../findings/2026-07-21-scoring-adjudication.md` §5.4–5.5.

### C4 — Hub-seeking: cause not established
**This entry has been substantially overturned. Do not act on any figure previously recorded here.** The single quantitative record is now [`../findings/2026-07-21-scoring-adjudication.md`](../findings/2026-07-21-scoring-adjudication.md); the design that follows from it is [`../specs/2026-07-21-phase2-path-quality-design.md`](../specs/2026-07-21-phase2-path-quality-design.md).

In brief, and cited rather than restated:

- The `+0.725` score/degree correlation is **unreproducible** and substantially tautological (§5.1–5.2).
- Hub-seeking is **not established as scoring-caused** — score-free BFS is 2.68× enriched on the same null, and the full router has the *lowest* max interior degree of the three routers tested (§5.3). The configuration-model rewire is the outstanding experiment.
- The `similarity_damping ≈ 0.25` prescription and its projected figures were never measured against a built artifact (§6, claim 27).
- The "damps before `log1p`" ordering bug is **real in current code but was not the cause** of the cosine rejection: the cosine artifact was built by a commit that had no `log1p` at all (§1, §2.1).
- The primary defect is the **p99 clip**, which creates zero-cost edges in every build — for the share of routed hops that cost zero similarity, see `../findings/2026-07-21-scoring-adjudication.md` §2.5 — with damping deciding only whether they point at the famous core or at micro-cliques (§2.5). **Still true after Phase 2:** the adopted arm keeps this rescale, and the defect is carried to Phase 1 above.

---

## Gate 1 — Personal use

### Phase 1: Make it actually work

**C3 leads this phase.** `w_floor` is a no-op and `known` degrades to a bare hard
exclusion — that is a *pathfinding defect*, not a UX item, and filing it under "bypass"
next to button fixes is part of why it sat unscheduled behind sixteen tasks of graph work
(revised plan §6). It is a direct contributor to the founding complaint: rerolls returning
artists at the same popularity band.

- **Bypass (C3) — first:** delete `w_floor` and `floor_relax_*`; implement real
  differentiation and progressive path lengthening; add the path-level tests QA found
  missing. Carries the routing-weight work from Task 0 Step 6.
- **Clips:** artist matching (C1); cache redesign — identity vs signed URL (C2)
- **Frontend UX** (all from dogfooding): "start over" / new-path control on the path page; card pause button (only the bottom bar works); stop audio on recompute; hide both bypass buttons on the **start and end** artists

**Carried in from Phase 2, with success conditions:**

- **The p99 ceiling defect survives adoption.** The adopted arm keeps `p99_log_clip`, which
  saturates ~1 % of edges at exactly 1.0 at zero similarity cost. The rank transform that
  removes it *lost* a blind listening test, so the defect is real but not obviously worth
  fixing by that route. **Success condition:** either a rescale that removes the ceiling and
  wins or ties a blind listen, or an explicit recorded decision to keep the ceiling.
- **Bypass hub-decline is unmeasured.** The owner's stated target (execution log §16) is
  that successive bypasses — especially of hubs — yield *progressively fewer* hubs, not that
  first paths avoid hubs. No metric covers this; the Phase 2 sweep never measured bypass at
  all, yet bypass is what decided the adoption test. **Success condition:** a hub-incidence-
  versus-bypass-count measurement exists and C3's fix moves it.

### Phase 2: Path quality — ✅ COMPLETE (2026-07-22)

Adopted **`capfix`**: `cap_strategy="mutual_knn"`, `similarity_rescale="p99_log_clip"`,
`similarity_damping=0.0`, entity filter on. Chosen by the owner in a blind listening test
(execution log §16); the losing options are deleted and raise.

- Graph rebuild: entity filter ✅ done. **Damping (C4) was tested and rejected** — d = 0.25 /
  0.5 / 0.75 all built and evaluated, and the undamped arm won. The prediction above that
  damping was needed did not survive measurement.
- Harness: `hubfrac` ✅ done. **Neighbour-set Jaccard was not adopted as the primary
  objective** — the overlap-family metrics proved unstable at these effect sizes and sign-
  flipped between slices (adjudication §6 claims 41–42).
- **Path export / logging** ✅ done (`api/eval/`).

Figures: `../findings/2026-07-22-phase2-sweep-results.md`. Do not restate them here.

**Gate 1 does not need:** deployment, CI, observability, auth, scale work.

---

## Gate 2 — Friends & family

### Phase 3: Robustness
- Clip failures degrade to 204 rather than HTTP 500 (currently `raise_for_status` escapes past the iTunes fallback)
- Artifact **length validation** at load (silent corruption on a truncated S3 fetch)
- Non-blocking DynamoDB (sync boto3 currently stalls the async event loop)
- Input guards: `from == target`, invalid `reason` coercion
- Basic observability: request logging, path latency, clip success rate — enough to know it broke for someone

### Phase 4: CI + tests
- CI pipeline running all three suites
- Missing regression tests: bypass differentiation, path-may-lengthen, determinism tie-break, smoothness-beats-BFS, clip failure modes
- Make E2E CI-runnable (committed fixture, stubbed clips, no live APIs)

**On bypass differentiation — assert the right thing.** The QA review found that `KNOWN` only ever reaches the floor helper and never a path-level test, and concluded you could delete the avoidance logic entirely with every test still green. The test gap is real, but its meaning has since changed: `dislike` **does** apply `avoidance_map` at runtime — it is working code that nothing covers, not dead code. Only `known` degrades to a plain hard exclusion, because the floor it relaxes never binds (C3). So the test to write asserts that `dislike` and `known` produce **different** paths from the same inputs, and that `dislike` steers around the neighbourhood rather than just excluding one node. A test written to the original framing would assert the wrong thing. See `../findings/2026-07-21-scoring-adjudication.md` §5.4–5.5.

### Phase 5: Deploy
- Dockerfile, `/health` endpoint
- **Real S3 graph loading** with `GRAPH_VERSION` (currently a local file path; the "swap the graph via one env var" story is unimplemented)
- CDK: App Runner, S3, DynamoDB, CloudFront
- GitHub OIDC + deploy workflow

**Rationale for CI before deploy:** with one user you notice regressions; with friends you don't — and a deploy pipeline needs something to gate on.

**Gate 2 does not need:** high concurrency, cost alarms, abuse handling.

---

## Gate 3 — Public

### Phase 6: Scale & cost
- Pathfinding performance: **result caching first** (queries are deterministic), then `scipy.sparse.csgraph` for the no-exclusion case. Pure-Python Dijkstra is GIL-bound, so concurrent heavy queries serialise
- Concurrency testing (untested; the whole design bets on one shared in-memory graph)
- Autocomplete index (currently an O(N) scan over 75k names per keystroke, on the same thread as pathfinding)
- **Clip-API rate-limit strategy** — see risk below
- Cost alarms

### Phase 7: Product depth
- Change-the-clip (pick a different song per artist)
- **Bypass telemetry** as real ground truth — which cards get rerolled is far more valuable than any offline metric, and costs one log line
- Per-hop "why" (needs genre/tag data)

---

## Known risk: the clip architecture has a Gate-3 ceiling

Every path view fires ~8–10 clip lookups, and preview URLs expire hourly — so caching cannot absorb the load. A public spike would hammer Deezer, get us rate-limited, and **fail every clip for everyone simultaneously**.

Not solved now. But the Gate-1 cache redesign (C2) must not foreclose the options: caching track **identity** separately from the **signed URL** keeps proxying or pre-signing available later. A five-minute design consideration now versus a rewrite at Gate 3.

---

## Dropped permanently

| Item | Why |
|---|---|
| `w_hub` tuning | Damping achieves the same hub reduction *while improving* quality. Term stays in code, dormant at 0.0. |
| Session-data ground truth | Multi-week acquisition; bypass telemetry (Phase 7) is better and free. |
| Bidirectional Dijkstra | Wrong lever — the constant factor is interpreted Python. Caching first. |
| Binary hub-traversal metric | Confounded by path length; replaced by hubfrac. |
| Artifact metadata format, `S3Archive.has()` efficiency, typed-edge rewiring | Cosmetic or only relevant to work not scheduled. |

---

## Open judgment calls

1. **Does Gate 1 need the Phase 2 rebuild?** The hub problem was confirmed as bothersome in use, so probably yes — but it could slide to Gate 2 for a working-but-repetitive app sooner.
2. **Phase 4 vs Phase 5 order.** CI is currently scheduled before deploy. If seeing it live matters more, deploy can go first; at Gate-2 scale the regression risk is tolerable.

---

## Reference

- Reviews and path-quality evidence: `docs/superpowers/findings/2026-07-21-architecture-review-and-path-baseline.md`
- Data-sourcing decisions: `docs/superpowers/findings/2026-07-19-listenbrainz-probe.md`
- Design: `docs/superpowers/specs/2026-07-19-artist-path-alpha-design.md`
- Harness: `api/eval/run_baseline.py`, `api/eval/tune_weights.py`, `api/src/artistpath_api/evaluation.py`

**Best bug-report artifact:** the **URL from the address bar** — all state lives in it (`/path/:from/:to?dislike=…&known=…`), so it reproduces the exact path and bypasses. Pair with the browser console for audio issues. Saved HTML is not needed.
