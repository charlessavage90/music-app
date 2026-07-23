# Repair + retune — execution log

**Role: ACTIVE.** The retained execution log for the work governed by
`specs/2026-07-23-defect-remediation-and-cost-retune-design.md`. Appended
per task, not only at closeout. Figures: artifact identity lives in
`findings/2026-07-23-tiebreak-fix-adoption.md`; defect mechanics live in the
Phase 1 log §2.8. This log records decisions and deviations, not numbers.

## Track 1 — tie-break remediation (2026-07-23)

- **T1** `mutual_knn_cap` gained an optional `ranking` argument (membership
  by ranking, scores from adjacency; ValueError on node-set mismatch;
  `ranking=None` is the old behaviour, byte-for-byte). TDD; all builder
  graph tests pass.
- **T2** `build_from_archive` passes the unclipped `scored_adjacency`
  strengths as the ranking. New regression test reproduces the §2.8
  ceiling-saturation regime in miniature and asserts the slot goes to the
  genuinely stronger neighbour; a second test pins emitted scores to the
  clipped values. Full builder suite green, including byte-identity replay.
- **T3** 75k rebuild ×2 (determinism confirmed by identical sha256), then
  `analysis/2026-07-23-tiebreak-fix-verification/verify.py`: Arm 2 topology
  reproduced; shared-edge scores bit-identical to capfix; popularity
  ordering preserved. No deviations: the rebuild reproduced the reference
  experiment's node and edge counts exactly (figures in
  `findings/2026-07-23-tiebreak-fix-adoption.md`), and the verification
  script printed ALL CHECKS PASSED.
- **T4** Adopted. Identity: `findings/2026-07-23-tiebreak-fix-adoption.md`.
  The 5k dev fixture is retired (spec §1 decision 4): `ApiConfig.graph_path`
  defaults to the adopted 75k artifact, smoke-checked through the default
  (Radiohead + Beatles present, path routes). The only api edit in Track 1
  is that default; routing code untouched. No frontend changes. The smoke
  check routed `Radiohead -> The Beatles` as a direct edge, and the API
  suite passed 116 tests. TEST-QUEUE entry queued.
- **T5** Closed out Track 1: Snyk `snyk_code_scan` run over the repo found
  3 Medium DOM-XSS issues, all in `builder/analysis/2026-07-22-c3-bypass-mechanisms/listen.html`
  — the pre-existing trio accepted by the owner 2026-07-23 (Phase 1 log
  §7.1 item 3). None of the six files changed on this branch
  (`builder/src/artistpath_builder/graph.py`, `pipeline.py`, the two test
  files, `builder/analysis/2026-07-23-tiebreak-fix-verification/verify.py`,
  `api/src/artistpath_api/config.py`) produced any finding. No code changes
  were made in this task. `docs/README.md` and `CLAUDE.md`'s orient table
  are repointed at Track 2.
- **Seam:** Track 1 ends here per spec §2. Track 2 (cost-function retune)
  starts from the spec §4 + this log + the adoption findings doc, with its
  own plan, an `ml-graph-analyst` protocol review, and a pre-registration
  that fixes the primary effect size and pair set before any arm runs.

### Track 1 — use-the-app results (owner, 2026-07-23)

The owner ran the TEST-QUEUE famous→famous check on the adopted graph. The
headline confirmation is positive: Radiohead is searchable and routable
(absent entirely before the fix), and famous-artist neighbourhoods now behave
as score-ranked rather than MBID-arbitrary. **No regression found; no defect
attributable to the tie-break fix.** Six findings, all recorded with success
conditions per closeout A3. Five are Track 2 inputs; one is a new standalone
product requirement.

**The recurring decision — "is each of these a metric or code?" — is settled
as a default:** with one exception, these are **Track 2 evaluation criteria,
not behaviour-specific code.** Rationale, from the record itself: §3.7 already
tried a behaviour-specific `known` mechanism (the multiplicative discount) and
it failed *structurally* — wrong shape, could not undercut the near-zero-cost
hub expressway at any strength. The banked lesson is that the durable lever is
the cost function and bolt-on special-cases get captured by the same
expressway. Hard-coding "known must return a less-famous artist" would
re-introduce that rejected class. The exception (F1) is a structural product
invariant, not a quality gradient, so it is the one candidate for a guard.

| # | Finding | Metric or code | Success condition |
|---|---|---|---|
| **F1** | **Zero-intermediary paths.** Famous→famous now often resolves to a *direct* edge (Radiohead→The Beatles; Muse→Coldplay), giving a 2-card path with no journey. A **new surface Track 1 exposed, not a regression** — restoring famous artists' ~50 score-ranked neighbours, which are largely other famous artists (§2.10 assortativity), makes direct famous↔famous edges common. | **Candidate code guard** (a minimum-intermediary requirement) — the one item here that is a structural invariant, not a tuning gradient. **Decide guard-vs-tuning:** confirm "a journey needs ≥1 stop" as a requirement, then check whether Track 2 tuning makes direct paths rare before adding a guard (a forced detour through a non-mutual-strongest node may cost coherence). Distinct from the already-tracked roadmap Phase 1 UX item "hide bypass on start/end cards." **Due:** before Track 2's success criterion is finalised, since a min-length guard changes what the sweep optimises. |
| **F2** | **Stuck in famous artists — bypasses do not get more "creative."** Owner's strong impression: more bypasses should surface *more obscure* nodes; they do not. **This is direct experiential confirmation of §2.9 on the repaired graph, and the single most important result of the session.** Confirms Track 1 correctly did *not* touch stratification (§2.10 predicted the tie-break fix moves it by nothing) — so this is Track 2's motivation, not a Track 1 shortfall. | **Metric** — this *is* the Track 2 objective. | **The primary Track 2 success criterion:** successive bypasses yield a materially lower external-fame profile at increasing depth (spec §4.3). Owner's ear now corroborates the percentile finding. |
| **F3** | **`known` should route to a *less-famous* neighbour.** Occasional 1:1 swaps on `known` are acceptable **only when the substitute is less famous** (his example of the unacceptable case: Bowie→Pink Floyd→Beatles, all famous-for-famous). Not an endorsement of 1:1 swapping as the mechanism. | **Metric / criterion** (the `known` gate currency, already spec §4.2). | Track 2 candidate's `known` bypass lowers the substitute's external fame vs the bypassed artist; scored on the external fame proxy, not in-graph popularity (§4.3). |
| **F4** | **`dislike` should 1:1-swap much *less* than `known`.** The two signals must behave differently; `dislike` steers around a neighbourhood, so a bare substitution is a stronger tell of failure there than for `known`. | **Metric / criterion.** | Track 2 evaluation asserts `dislike` and `known` produce different paths from identical inputs, and `dislike` reroutes rather than substitutes (already a planned path-level test, roadmap Phase 4). |
| **F5** | **Long-path local deviation is acceptable in isolation, a defect only if repeated.** On long paths (>~9), a bypass sometimes changes only ~3 nodes near the bypass point — the owner considers this *correct* (a local deviation to accommodate one bypass), and a defect **only if several bypasses in a row confine changes to the same node group.** He did **not** see the defect form this run — local deviations resolved into larger changes within 1–2 further bypasses, as expected. | **Metric / calibration** — a diagnostic, not a target. | Track 2 diagnostic: track node-overlap between consecutive bypass results; flag only *sustained* confinement to one region, not single instances. |
| **F6** | **Coherence wobble at the obscure end.** Force-disliking repeatedly *did* reach genuinely obscure artists (first time in testing), but coherence was uncertain — soundtracks, neoclassical/ambient (Max Richter, Ólafur Arnalds) appeared, and a single further bypass snapped back to very famous (Queen, Simon & Garfunkel). The "snap back" is the stratification's signature; the wobble is the coherence dimension Track 2 must hold *while* reaching down. | **Metric / criterion.** | Track 2 candidate reaches the obscure tail **without** a coherence collapse and **without** immediately snapping back to the famous stratum on the next bypass. Coherence is judged by the blind listen (offline metrics do not track it — Phase 1 log §4). |

**Bypass sample URLs** for F3 and F6 are in the owner's 2026-07-23 test message
(all path state lives in the URL, so they reproduce exactly). Not pasted here —
the branch/PR thread holds them; if a durable copy is needed for Track 2's pair
set, capture them into the Track 2 plan when it is written.

### Closeout — doc audit (2026-07-23)

The `doc-auditor` was run at closeout after an initial judgement call to skip it was
**overruled by the owner** — correctly. The per-task and whole-branch reviews audited the
*diff*; the doc audit audited the *whole doc set*, and found six High-severity defects in
files this session never touched. Recording the lesson: **a session that edits documents
cannot substitute diff review for a doc audit** — the stale claims were in the files it
did *not* touch.

**Fixed this session** (commit `914f6c4`, plus memory files outside the repo):

- **Auto-loaded memory was the worst class.** Three memory files (`roadmap-pointer`,
  `project-state`, `crawl-resume`) plus the `MEMORY.md` index still said Phase 1 was
  PAUSED with the decision outstanding, named `capfix` as adopted, and pointed
  `ARTISTPATH_GRAPH` at the original pre-Phase-2 graph. Memory loads into *every*
  session, so a cold session would have received that simultaneously with the correct
  in-repo status. Rewritten as pointers, figures stripped per the memory rule.
- `2026-07-22-HANDOFF-phase1.md` — Role ACTIVE, no in-file supersession, still said
  "Next action: plan Phase 1" and named capfix + checksum as "the adopted one" under a
  *"still live"* heading. Banner + inline dated corrections added.
- Phase 1 log — §2.1's unmarked present-tense "the one the app currently routes on";
  §6's two mutually contradictory bullets; two mid-document `(ADOPTED)` markers on
  capfix. **Adjudication on the markers:** they sit in *dated measurement* tables where
  capfix genuinely was adopted, so they were **date-scoped, not reassigned** — history
  preserved, while a `grep ADOPTED` no longer returns the superseded artifact as current.
- Root `README.md` — a stale edge count (the pre-Phase-2 figure, ~4.5× off). Reworded to
  cite rather than restate, per the figures rule.
- `docs/README.md` — four unmapped documents added; the roadmap row's "live work queue"
  framing corrected; **restated figures converted to citations** (the Phase 1 log owns
  them and says so explicitly, so the restatements were violations even while correct).
- Two C3 specs flipped ACTIVE → COMPLETE; the Track 1 plan gained a COMPLETE banner
  (checkboxes deliberately left unticked as the historical record).
- `CLAUDE.md`'s `ARTISTPATH_GRAPH` description (still framed as "5k dev → 75k prod") and
  `.claude/agents/ml-graph-analyst.md`'s instruction to put probe scripts in a scratchpad
  — the latter contradicted the convention the record paid for when scripts were nearly
  lost to a scratchpad clean.

**Deferred, with success conditions:**

| Item | Success condition |
|---|---|
| No `builder/README.md` (the other two packages have one) — pre-existing gap, not caused by this work | **When `builder/` is next worked on substantively** (i.e. Track 2's cap-strategy work, if it ever runs) — or accept permanently if the package README convention is dropped. |
| `CLAUDE.md` and `api/README.md` both restate `ApiConfig` cost-weight defaults | **Due when Track 2 changes any weight** — it will invalidate both copies at once, which is the moment to convert them to citations. |
| Low-severity role/status drift: Phase 2 log header rationale, revised-plan in-file role, "Consequences for the paused work" heading, pre-fix `file:line` pointers in the Phase 1 log, two 2026-07-19/20 design specs still "ready for implementation" | **Sweep at the next closeout**, or when a reader is actually misled — none change what a session would *do*. |

## Track 2 — cost-function retune

*(not started — next session begins here. Read the Track 1 use-the-app results
above first: F2 is the objective, F1 is a guard decision that must precede the
success-criterion spec, and F3–F6 are the criteria the sweep is judged on.)*
