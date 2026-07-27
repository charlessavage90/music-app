# Alpha Rollout Roadmap

**Date:** 2026-07-21
**Role: AUTHORITATIVE and ACTIVE** — the gate structure and phase ordering. **This is the one
plan in `plans/` that is still live**; every other is executed and says so. It holds no
figures, and it does not state current status: for that read [`../NEXT.md`](../NEXT.md).
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
- The clip-expiry bug was **invisible to both code review and tests** — tests mock HTTP, so a URL that expires part-way through a session is indistinguishable from one that doesn't. (The lifetime was later measured; the figure is owned by `../2026-07-25-gate1-clips-and-ux-execution-log.md` §15.)
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

### C2 — Clips silently die after a while

> **✅ FIXED AND CLOSED 2026-07-25 (PR #19 server side, PR #20 browser side), confirmed in
> use.** Read `../2026-07-25-gate1-clips-and-ux-execution-log.md` §15–§18 before this
> section. **Two corrections to what follows:** the lifetime was measured at a specific
> value that §15 owns — *"past the first hour"* below is a loose inference from the raw
> observation, and materially too generous. And the fix needed a **browser** half as well as
> a server one: the page must ask for a URL at the moment of play, not when the card is
> drawn. The 30-day cache described below no longer holds URLs at all.

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

> **⚠ STATUS, 2026-07-25 — read before acting on this list.** "C3 leads this phase" is
> **superseded**: C3 is path-quality work, and path-quality work is **PAUSED by owner
> decision** (`../2026-07-25-HANDOFF-track2f-and-headroom.md` §0). Do not delete `w_floor`
> or `floor_relax_*`. **Clips and all four UX items are DONE and CLOSED**, confirmed in use
> — `../2026-07-25-gate1-clips-and-ux-execution-log.md` §15–§19. **The one open Gate 1 item
> is F1, below.**

- **Bypass (C3) — first:** delete `w_floor` and `floor_relax_*`; implement real
  differentiation and progressive path lengthening; add the path-level tests QA found
  missing. Carries the routing-weight work from Task 0 Step 6. — **PAUSED, see banner.**
- **Clips:** artist matching (C1); cache redesign — identity vs signed URL (C2) — **DONE
  and CLOSED 2026-07-25.**
- **Frontend UX** (all from dogfooding): "start over" / new-path control on the path page; card pause button (only the bottom bar works); stop audio on recompute; hide both bypass buttons on the **start and end** artists — **DONE 2026-07-25.**
- **F1 — a journey with no artists between the two you chose.** Added 2026-07-25; discovered
  2026-07-23 as a surface the tie-break fix exposed. **The owner has decided every journey
  needs at least one stop**, and **it is now BUILT** (PR #23; record
  `../2026-07-25-f1-minimum-stop-execution-log.md`). Never inside the path-quality pause.
  **NOT discharged** — its condition is an observation, and that is the queued use-the-app
  entry. Success condition and reasoning:
  `../2026-07-25-gate1-clips-and-ux-execution-log.md` §16 — cite it, do not restate it.

**Carried in from Phase 2, with success conditions:**

- **The p99 ceiling defect survives adoption.** The adopted arm keeps `p99_log_clip`, which
  saturates ~1 % of edges at exactly 1.0 at zero similarity cost. The rank transform that
  removes it *lost* a blind listening test, so the defect is real but not obviously worth
  fixing by that route. **Success condition:** either a rescale that removes the ceiling and
  wins or ties a blind listen, or an explicit recorded decision to keep the ceiling.
- **Bypass hub-decline is unmeasured.** The owner's stated target (execution log §16) is
  that successive bypasses — especially of hubs — yield *progressively fewer* hubs, not that
  first paths avoid hubs. No metric covers this; the Phase 2 sweep never measured bypass at
  all, yet bypass is what decided the adoption test. **Success condition:** a
  discovery-payload-versus-bypass-count measurement exists and C3's fix moves it.

  **Measure the payload, not the ratio.** Hubs are not a cost that accumulates — they are
  slots that failed to deliver. What the product delivers is artists the listener does not
  already know, so the primary is the **absolute count of non-hub interior artists**, per
  path, plotted against bypass count. A worked case, from the owner: an 11-artist path with
  4 hubs delivers 7 novel artists and beats a 4-artist path with 3 hubs delivering 1 —
  despite having *more* hubs.

  This is why hub **count** is the wrong primary (it ranks that case backwards) and why
  `hubfrac` alone is insufficient (it ranks it correctly but is scale-invariant, reporting
  roughly 0.5 → 0.28 where the delivered value went 1 → 7). Keep `hubfrac` as the
  normalised companion. Payload also resists length-padding for free: a path that lengthens
  by adding hubs adds no payload, so the curve stays flat.

  **Open, decide when building it:** "non-hub" is a structural proxy for "novel", and the
  two diverge — the owner called Vulfpeck a hub, which is almost certainly outside the top
  1 % by degree. Perceived hub-ness is taste-relative; measured hub-ness is structural.
  Offline you can only have the proxy. Bypass telemetry (Phase 7, worth pulling forward)
  measures the real thing.

  **Path length is an observable, not a target.** Track it alongside payload as a
  diagnostic, but it has a ceiling set by attention rather than by graph structure — at some
  point a journey stops feeling like one. No offline metric will find that boundary. It
  belongs in `TEST-QUEUE.md`, discovered by use.

- **Bypass substitution — an unresolved lead, deliberately scoped small.** In the adoption
  test the owner observed `d025` responding to bypass by swapping the rejected artist for
  another well-known one while leaving the rest of the path intact — the fingerprint of a
  graph with dense local alternatives, where a near-equivalent stand-in is always available.
  **Scope honestly: one path, 3–4 of 8–12 bypasses, mid-sequence, and not consistent for
  that arm.** It is far too thin to explain the verdict and is recorded only so it is not
  lost.

  A plausible mechanism exists — `d025` retains materially more edges than `capfix` despite
  the same mutual k-NN cap, because the cap selects top-K by score and damping changes
  scores — but it is unsupported at this evidence level. **Cheap check if it matters:**
  node overlap between the pre-bypass and post-bypass path. If one arm retains n−1 of n
  nodes while another reroutes, the behaviour is systematic; if not, it was a property of
  one region of the graph. Currently those two cannot be distinguished.

- **C3 modifies the channel that decided the adoption.** ⚠️ The blind test discriminated on
  bypass behaviour, not on first paths — on three no-bypass comparisons the arms looked
  similar (execution log §16). The comparison was **fair**: both arms ran identical API
  code, so the only difference was the graph. But that code contains C3 — `w_floor` is a
  no-op and `known` degrades to a bare hard exclusion — so the verdict describes how the
  two graphs behave under a *partially broken* bypass. C3's fix changes bypass routing
  materially, and the behaviour that separated the arms may not separate them the same way
  afterwards.

  **This is a watch item, not a redo, and the distinction matters:** re-testing because a
  result was unwelcome is forbidden (execution log §15). Re-testing because the mechanism
  under it changed is a different question. `graph-t15-capfix.bin` and `graph-t15-d025.bin`
  both still exist with recorded checksums, so the check is cheap if it is warranted.
  **Success condition:** after C3 lands, either confirm by use that bypass behaviour still
  favours the adopted graph, or record an explicit decision that the pre-C3 comparison
  stands. Do not let it lapse unexamined.

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
- ~~Clip failures degrade to 204 rather than HTTP 500 (currently `raise_for_status` escapes past the iTunes fallback)~~ **DONE 2026-07-25**, pulled forward out of this phase because the C2 change made it urgent: re-signing added a network call to the cache-hit path, so a rate-limit during the queued use-the-app check would have produced dead cards indistinguishable from that check failing. Record: [`../2026-07-25-gate1-clips-and-ux-execution-log.md`](../2026-07-25-gate1-clips-and-ux-execution-log.md) §12.
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

### Gate 2 → 3 entry condition, added 2026-07-24: answer the content-curation question

**Owner's decision, and it must be answered explicitly before this gate opens — even if the
answer is "not yet".** Should the app filter artist names that are offensive, or junk?

There is no technically correct answer, which is why it is recorded as a gate condition rather
than a task. What makes it gate-scoped: **at personal use a junk or offensive name is a
curiosity; at public launch it is a different risk category** — and this app's premise routes
users through precisely the obscure stratum where upstream curation is weakest.

Two measured facts to decide against, both from 2026-07-24 (record and figures:
[`../2026-07-23-repair-and-retune-execution-log.md`](../2026-07-23-repair-and-retune-execution-log.md)):

- **Non-artist entities are still present.** `jesus2099`, a MusicBrainz editor account, is a
  node with degree 31 — the case the 2026-07-21 architecture review named, and one the shipped
  placeholder filter structurally cannot reach.
- **There is no discovery mechanism.** Both known instances were found by accident. A
  username-shaped scan returns 152 nodes of which most are **real artists** (`Sad13`,
  `Soccer96`, `MNL48`), so the remedy is a periodic report for human skim — never an automated
  name filter, which would delete real artists.

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

Every path view fires ~8–10 clip lookups, and preview URLs are short-lived (lifetime measured; `../2026-07-25-gate1-clips-and-ux-execution-log.md` §15 owns the figure, and it is *shorter* than assumed here) — so caching cannot absorb the load. A public spike would hammer Deezer, get us rate-limited, and **fail every clip for everyone simultaneously**.

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
| Chart-aggregation fame sources (kworb-class) | **Top-tail instrument where the job is mid-band.** Probe §6d already separates famous from obscure reliably and is imprecise in the middle; the pre-registration's §5 names mid-fame discrimination as the regime the proxy's job lives in. Coverage is not thin at random — it is thinnest where discrimination is needed. A second reason, **weaker and stated as such**: charts measure *current commercial activity* (a flow), not fame (a stock), so a universally-known but inactive artist scores near zero — worsening the residual risk amendment A11 already accepted. **That second reason rests on an unverified reading**; if kworb's extended pages carry cumulative or historical aggregates rather than current positions, it weakens. **The first reason is decisive on its own and does not depend on it.** Surveyed 2026-07-26. |
| Historical third-party artist datasets (Kaggle-class snapshots) | Same top-tail defect, plus **unknown construction** — a popularity column that cannot be traced to a definition is the input class that has produced three wrong conclusions here. Staleness is the lesser problem and bites hardest in the mid-band. Surveyed 2026-07-26. |

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
