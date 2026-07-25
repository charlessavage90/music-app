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
(all path state lives in the URL, so they reproduce exactly).

> **CORRECTION 2026-07-23.** This entry said "the branch/PR thread holds them."
> **It does not** — PRs #7, #8 and #9 have zero comments between them, checked via
> `gh`. The URLs exist only in the owner's chat message from that session and in his
> browser history. Recording the correction rather than quietly fixing the sentence,
> because "it is safe elsewhere" is exactly the belief that loses something: the
> deferral was accepted on the strength of a durable copy that was never made.
> **Consequence for P1:** the pair-8 endpoints must come from the owner or from
> browser history; if neither yields them, §2.3's substitution rule fires
> deterministically (Nirvana → CROOVE) and no judgement is required.

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
| ~~`CLAUDE.md` and `api/README.md` both restate `ApiConfig` cost-weight defaults~~ **DISCHARGED 2026-07-23** by the pre-Track-2 guards (G2): both converted to citations, and `ApiConfig` now states in-file that it is the only definition. Came due early because G2 was editing that text anyway. |
| Low-severity role/status drift: Phase 2 log header rationale, revised-plan in-file role, "Consequences for the paused work" heading, pre-fix `file:line` pointers in the Phase 1 log, two 2026-07-19/20 design specs still "ready for implementation" | **Sweep at the next closeout**, or when a reader is actually misled — none change what a session would *do*. |

## Pre-Track-2 guards (2026-07-23)

Executing `plans/2026-07-23-pre-track2-guards.md` — six structural guards that had to
land between the Track 2 pre-registration and the Track 2 sweep. **Not Track 2**; no arm
has run and no harness was written.

**Branch decision.** Fresh branch `phase1-pre-track2-guards` off `main`, not an extension
of `phase1-repair-and-retune`: that branch merged as PR #7 and `main` already carries
Track 1, so extending it would have re-proposed merged commits.

**P7 answered by the owner (2026-07-23): ≥ 1 intermediary IS a product invariant.**
"Every path must have at least one artist in between the start and end." This discharges
the labelled INFERENCE in pre-registration §4 — the guard is confirmed, not inferred.
The guard itself is **not implemented here**; it ships with whichever Track 2 arm is
adopted (pre-registration §4 gives the mechanics: mask the direct edge and re-run).

### G1 — artifact acceptance assertions at build time

**Where it runs, and why not in `build_from_archive`.** New module
`builder/src/artistpath_builder/acceptance.py`, called from `cli.cmd_build` *before*
`serialise`. `build_from_archive` is exercised throughout the suite with miniature
archives whose graphs cannot satisfy production invariants; the invariants describe an
emitted **artifact**, and `cmd_build` is the emission point. Criteria are a frozen
dataclass (`PRODUCTION_ACCEPTANCE`) so the canonical set and every bound sit in one
named place.

**No CLI escape hatch.** `main()` takes `criteria` as a keyword argparse cannot set.
A `--skip-acceptance` flag would be reached for at exactly the moment the guard matters.
Tests substitute scaled criteria in-process.

**What the three checks catch, and what they do not.** Measured against both real
artifacts — the adopted one and `graph-t15-capfix.bin`, which log §2.8 records as
reproducing the defective arm exactly (script and figures:
`builder/analysis/2026-07-23-acceptance-bounds/`):

- **Canonical presence** and the **famous-degree floors** are the §2.8 detectors. The
  top-25-by-popularity median degree separates the two artifacts by roughly a factor of
  five; the chosen floor sits about midway between them in ratio terms.
- **Global shape bounds do NOT separate them**, and are not claimed to. Log §2.8 says so
  directly ("the global shape does not move") — N, E and whole-graph median degree agree
  to a fraction of a percent across the defect. They are recorded in code as a
  **regression tripwire for a different failure** (a build silently losing much of the
  graph). Stating this rather than quietly picking loose bounds is the plan's own
  instruction.

**Demonstrated against a negative case, twice.** In-suite
(`tests/test_acceptance.py`): the same miniature archive built through the pre-Track-1
path — one knob, whether `mutual_knn_cap` ranks clipped or unclipped scores, the same
intervention log §2.8 used — deletes 6 of 10 famous artists from the component, and the
check rejects it. At full scale: the adopted artifact is accepted, capfix is rejected on
all three §2.8 detectors. **At miniature scale `k = 4` caps every degree at 4, so only
deletion is visible there**; the degree floors are demonstrated by the full-scale script
and by unit tests over hand-built graphs.

**Knock-on: pre-registration P2 is now a no-op.** The canonical set includes every
endpoint of pre-registration §2.3 (analysis set, held-out set, ordered reserve), and all
24 were verified to resolve in the adopted artifact during bound selection — with
`Nirvana` carrying the known duplicate (2 nodes; highest-popularity rule applied). The
Track 2 session should **not** re-verify endpoint presence by hand. Pair 8 (the owner's
captured bypass pair) is still unidentified under P1 and is therefore not represented.

### G2 — put the currency in the name

**Renamed in shipped code** (`api/src`, `builder/src`, plus `api/eval` — see below):
`popularity` → `pop_raw` on both `GraphStore` and builder `Graph`; `hub_penalty` →
`degree_hub_penalty`; `w_hub` → `w_degree_hub`; `hubfrac` → `top1pct_degree_frac`;
`mean/max_interior_pop` → `…_pop_raw`; `hub_node_set` → `top_degree_node_set`;
`effective_floor` → `effective_floor_raw`; local `pop_u`/`pop_v`/`floor` →
`pop_raw_*`/`floor_raw`; builder `indegree` → `score_weighted_indegree`.
`pop_pctl` is reserved and unused — Track 2's percentile machinery takes it.

#### The `user_count` near-miss — recorded as a near-miss, not as a comment fix

`ArtistStats.user_count` was documented as "distinct listeners — the popularity signal
(spec 4.1)", and `graph.py` carried "Distinct listeners, not plays". Neither is true:
`pipeline.py` sets that field to `round(score_weighted_indegree * 1000)`, and **no
listener data enters the build at all** — the per-artist listeners endpoint was
eliminated as a popularity source during Task 1 (findings §6d–6f) and the name and
comments outlived the design that justified them. Renamed to `pop_indegree_scaled`, with
the history in the comment; a third copy of the same false claim in
`builder/tests/test_graph.py` was corrected at closeout.

**Nothing is invalidated.** The *values* were always correct — this is a naming and
documentation defect, not an arithmetic one, and every measurement taken on this field
stands.

**But it is the same error class as §2.6/§2.11/§2.12 located where it does the most
damage, and that is why it is recorded here rather than in a commit message.**
`docs/README.md`'s standing rule is that **the code is the truth about the code — where a
document and the source disagree, the source wins.** Here the source was lying about its
own units, so the tiebreaker was compromised **in the same direction as the documents it
exists to adjudicate**.

Concretely, the near-miss: §2.11 established popularity ≠ fame by reasoning that lo-fi
producers are playlist staples accumulating high co-listening in-degree. Anyone checking
that reasoning against a field labelled "distinct listeners — the popularity signal"
would have concluded the argument was **wrong** — the numbers would have looked like
listener counts, for which the lo-fi mechanism does not obviously hold. That defect could
have **blocked or delayed §2.11**, not merely coexisted with it. §2.11 survived because
nobody performed the check the project's own rule prescribes.

**What follows for the next session:** "verify the claim against the source" is necessary
and not sufficient. When the source is a *name or a comment* rather than an expression,
it is a document like any other and carries the same drift risk. Trace to the assignment.

**Two names are exempt, and had to be.** The `popularity` key in the APG1 metadata blob
is the **builder↔api wire contract** — renaming it invalidates every existing artifact,
including the adopted one, which the plan forbids rebuilding. The `popularity` field in
the API's JSON response is consumed by the frontend (`frontend/src/api/types.ts`).
Both keep their wire names, commented at the definition; only in-memory identifiers
carry the currency.

**Where the plan was wrong about the repo, and what it cost.** G2 says to leave
`builder/analysis/` alone because those scripts are frozen records. Correct — but the
plan assumed that meant renaming shipped code was safe for them. It is not: **sixteen
frozen scripts import the shipped classes and read these attributes**, and four import
`hub_node_set` by name. A plain rename breaks all of them at import or attribute access.
Resolution: shipped code keeps **read-only aliases** under the old names (properties, so
nothing can be written through them) plus one module-level alias for the function.
Verified mechanically — all **80** symbols imported from shipped code across every
script in `builder/analysis/` resolve, and the aliases were smoke-tested against the
adopted artifact. The first draft of the mapping README claimed nothing imported
`hub_node_set`; the grep that checked it found four. Recorded because "I checked" and
"I asserted" are the distinction the §2.13 reversal pattern is about.

**The aliases have an expiry condition, decided by the owner 2026-07-23 — they are not
permanent.** Every deferral here gets a success condition, and a compatibility layer with
none would persist by default rather than by decision, leaving the next session unable to
tell a load-bearing alias from leftover scaffolding.

| Deferred | Success condition — due when |
|---|---|
| **Remove the read-only compatibility aliases** (`GraphStore.popularity`, `GraphStore.hub_penalty`, `PathMetrics.hubfrac` / `mean_interior_pop` / `max_interior_pop`, `Graph.popularity`, module-level `evaluation.hub_node_set`) | **When the `builder/analysis/` scripts are formally retired.** They exist for exactly one reason — keeping those frozen records runnable — so retirement of the scripts is what makes them leftover. Until then they are load-bearing and must not be removed as tidying. Guarded by `api/tests/test_frozen_script_aliases.py` and the builder-side equivalent; deleting the aliases means deleting those tests in the same change. Rejected alternative: "permanent, because the scripts are permanent." Defensible, but it makes the layer unfalsifiable — nothing would ever prompt a review. |

**`api/eval/` was out of the plan's stated scope and had to come along.** It is live
tooling, not a frozen record (`api/tests/test_diagnostics.py` covers it), and it imports
`hub_node_set` and constructs `GraphStore(popularity=…)` — an alias cannot cover a
constructor kwarg. Updated in full.

**A serialisation trap, recorded in the mapping README.** Aliases are Python attributes
and do not appear in `dataclasses.asdict` or `summarise()` output, so result JSON written
before today (`api/eval/results-*.json`, `listen_secret.json`) carries `"hubfrac"` and
`"mean_interior_pop"` while a fresh run emits the new keys. Any script comparing old JSON
to new output must map the keys itself.

**Deferral discharged:** "CLAUDE.md and `api/README.md` both restate `ApiConfig`
cost-weight defaults" (Track 1 closeout table) — both converted to citations, and
`ApiConfig` now says in-file that it is the only definition. While doing it, found
CLAUDE.md's cost formula was **missing the `w_degree_hub` term entirely**; corrected.

### G3, G4 — two rules added to CLAUDE.md

G3: the factor table gains a required third section — *held constant, and why each is
genuinely constant under the intervention* — with pre-registration §0's `w_floor` finding
as the worked example. G4: no experimental arm runs until a pre-registration is committed,
same worked example. Both are short by design; the existing rule earns its keep by being
short.

### G5 — bookkeeping

**(a)** Note added to pre-registration §1.2 resolving the collision between guard G
(applied in all arms) and mirror-and-verify (byte-identity against shipped `find_path`,
which has no G) on the two direct-edge pairs. Sequence: verify with G **off**, then enable
G uniformly. Log §3.10's "non-identical means stop" applies to the verification step only.
The owner's P7 answer is recorded in the same place.

**(b)** Both new documents registered in `docs/README.md` under Active.

### G6 — two guards deliberately deferred

*(A third deferral from this work — removing the G2 compatibility aliases — is recorded
in the G2 section above, next to the aliases it governs. Three deferrals total.)*

| Deferred | Why not now | Success condition — due when |
|---|---|---|
| **Named-entity check as standing practice** — showing the owner the *names* a perceptual metric produces, not just the number | Pre-registration §5 already implements a stronger version for the fame proxy: 29 artists labelled into three buckets **without seeing fan counts**, scored for rank agreement and catastrophic inversions. A parallel practice invented now would duplicate it. | **After §5 runs.** Generalise its protocol into `closeout` (as an adoption-time step) and into `TEST-QUEUE.md`'s format, with its measured performance attached. |
| **Artifact provenance registry** — every gitignored `.bin` carries its full build configuration and code commit, and any cross-artifact comparison must cite the rows and count the differing columns | Track 2 Stage A holds the artifact fixed and asserts its sha256, so the post-hoc-comparison confound is not live. The checksum table in Phase 1 log §5 is adequate for now. G1 also narrows the gap: a rebuilt artifact must now pass acceptance before it exists. | **When pre-registration §2.4 R0 or R2 fires** and a builder arm (p99 rescale, or the deferred `cap_strategy`) is scheduled — that is when new artifacts appear and log §2.2's two- and three-knob comparison errors become possible again. |

### P8 — `ml-graph-analyst` protocol review landed (2026-07-23)

Run separately from the guards work, against the pre-registration and the working tree.
Record: `findings/2026-07-23-track2-protocol-analyst-review.md` (owns its §2 figures);
measurements committed to `builder/analysis/2026-07-23-track2-protocol-review/`.
Registered in the doc map. **Its O-series observations and PR-series recommendations are
the Track 2 session's to act on** — not restated here, and none was actioned by the guards
work.

Three of its items bear on the guards directly, recorded because they are corroboration
from a reader who had the code open:

- **O6 independently confirms P2 is discharged** — its M4 resolved all 12 pre-registered
  pairs in the adopted artifact, matching G1's canonical-set verification. The
  pre-registration's §7 still *lists* P2 as outstanding; the execution log and the review
  both say otherwise.
- **O8 independently confirms the mirror-and-verify / guard-G contradiction** that G5(a)
  found and fixed, and adds one consequence the note does not cover: with G applied to P,
  **no comparison anywhere in the design is against shipped behaviour on pairs 4–5**, so
  the C5 no-regression inspection cannot see the d0 change the owner would notice there.
- **O5 records that G2's rename hazard materialised** — the review read the working tree
  mid-rename, so §0's `file:line` citations are correct against HEAD and stale against the
  tree. Exactly the hazard G2's plan named. No action needed; the mapping table covers it.

**O3 is a consequence of G3, not a defect in it.** `w_degree_hub` is missing from §1.2's
constants table. It is genuinely constant under every intervention here (a zero weight
cannot be un-zeroed by turning another knob), so it is a completeness gap against the
dormant-term rule this work added — the rule finding its first omission on the document
that motivated it.

### Closeout (2026-07-23)

**Mutation-tested the new guard rather than observing it pass.** Four mutants, all killed:
disabling the canonical-presence check (2 tests red), the famous median-degree floor (2),
the minimum-degree floor (1), and removing the `check_acceptance` call from `cmd_build`
(1). The last one matters most — it proves the guard is wired into the emission point,
not merely importable.

**Gap found and closed at closeout:** nothing covered the compatibility aliases, so a
future rename could have broken the frozen `builder/analysis/` scripts silently, surfacing
only when someone tried to reproduce an old result. Added
`api/tests/test_frozen_script_aliases.py` (and a builder-side equivalent in
`test_graph.py`), including an assertion that the aliases are **read-only** so they cannot
become a second way to write the same quantity. The builder alias is asserted in the
builder's own suite, not the API's — importing `artistpath_builder` from `api/tests` would
create exactly the coupling the APG1 format exists to avoid.

**Doc audit (`doc-auditor`) found two HIGH defects, both caused by this work, both fixed:**

- `CLAUDE.md`'s **orient table** — the first thing a fresh session reads — still named
  `hubfrac` / `hub_penalty` / `w_hub` in the row warning about currency confusion. The row
  telling you to check your currency was itself out of date.
- `.claude/agents/ml-graph-analyst.md`'s cost formula **omitted the degree-hub term
  entirely** and used the old names. This file is auto-loaded, and my own `.claude/` grep
  missed it precisely because the defect was an *omission* — the term wasn't there to
  match. A grep for stale names cannot find a missing one; that is the lesson.

Two further ACTIVE documents carried stale identifiers and were corrected in place
(`docs/README.md`, and the pre-registration's §0 `pop_v`). Historical plans keep their
original names deliberately — renaming inside a frozen record would falsify it.

**Snyk:** `builder/src`, `api/src` and `api/eval` clean. The three Medium DOM-XSS findings
in `builder/analysis/.../listen.html` are the pre-existing owner-accepted ones (Phase 1 log
§7.1 item 3) and are untouched.

**Suites:** builder 112 passed, api 120 passed, frontend 31 passed. The frontend run is
the check that matters for the rename — it is what confirms the API's JSON response
contract still says `popularity`.

**No config default was left unflipped (closeout A4):** this work added no runtime knob.
`PRODUCTION_ACCEPTANCE` is the default and only the test suite substitutes it; the
`w_degree_hub` change is a rename, not a new switch.

**Artifact provenance (closeout D3): nothing was rebuilt.** The adopted artifact is
unchanged at sha256 `4cb84ef9…b061dc8`, and `graph-t15-capfix.bin` (`c8af6eac…`) was read
only as the negative case. Both asserted in-script before every measurement. The committed
500-node test fixtures are untouched and still valid — the APG1 format did not change,
which is exactly why the wire key had to keep its name.

### Use-the-app result (owner, 2026-07-23) — the rename is clear

**Nothing found; the expected outcome.** Full record in `TEST-QUEUE.md`. Summary:
"everything seems stable and functions similar to other tests."

The load-bearing part is the **search** check, which the owner ran first on the reasoning
that search is the first action a real user takes. Typing `The ` returned The Beatles,
The Rolling Stones, The Strokes, The Beach Boys. That is the run's most discriminating
evidence: search ranks on the renamed popularity read, and a high-frequency prefix is
precisely where a crossed wire would put the wrong artists at the top. It did not.

Two familiar paths showed no discernible difference, and repeated bypass on both buttons
was clean. **Caveat recorded rather than smoothed over:** the owner was not closely
inspecting path content, so the path result is "nothing jumped out", not a quality
judgement. That is the right depth for a regression check and the wrong depth to cite as
evidence about path quality — which is Track 2's question, still open, F2 untouched.

## Track 2 — cost-function retune

*(No arm has run. No path has been routed. The harness does not exist.
Read the Track 1 use-the-app results above first: F2 is the objective, F1 is
settled as a guard, and F3–F6 are the criteria the sweep is judged on.)*

### Pre-registration amended for analyst D1–D3 (2026-07-23)

Branch `track2-prereg-amendments` off `main`. **Five amendments (A1–A5) to
`specs/2026-07-23-track2-preregistration.md`, committed before any arm ran** —
index in its new §9, each also marked inline at the passage it changes.

**Why these three and not the rest.** D1, D2 and D3's first half are settled by
**arithmetic over the artifact**, not by argument, and all three would have
produced arms that provably could not move:

- **D1** — P3's rule forces `s_max` one grid step below the ceiling, so T1's toll
  came to **1.42 % of `w_hop`** (re-measured independently this session, matching
  the review). The rule and the goal were in conflict: "bind only on saturated
  edges" and "have a magnitude" cannot both come from one threshold on `sim`.
  Fixed by decoupling them — an additive toll on score-exactly-1.0 edges, at two
  pre-registered magnitudes (7.5× and 30× `w_hop`), which is also what makes a T1
  null mean something.
- **D2** — at `config.py`'s relax constant the floor hits zero at 6–7 bypasses
  while C1 scores at d ≥ 10, so **FL1/FL2 were numerically identical to W in every
  scored cell**. §2.4's R3 designated them as its remedy, so that branch was
  unreachable. Fixed with a relax constant pre-registered in the pre-registration
  rather than read from config, plus early snapshots (free — the walk visits every
  depth anyway).
- **D3** — added read **R6**, and made the percentile level mean-matched so J-cur
  is genuinely one column, with diagnostic arm **A1u** holding the unnormalised
  variant.

**The prediction is on the record before the arms run, which is the point.**
The review's D3 inference — that percentile arms will move ΔF the *wrong way*,
because top-decile compression cheapens lateral famous↔famous moves faster than it
cheapens exits — is now R6, with a free falsifier (**A1 beats A0 on C1**). The
sweep therefore tests the review as well as the design, and neither outcome can be
narrated after the fact.

**A new measurement, and it changed the amendment.**
`builder/analysis/2026-07-23-track2-toll-calibration/` (owns its figures; discharges
review **PR-C**). Its **Q4 was not anticipated by the review**: ceiling saturation is
rare across the graph but **near-universal among this sweep's endpoints** — 22 of 24
carry at least one ceiling edge, eight are saturated on all 50 neighbours, against a
mean of 3.5 for top-1%-by-degree nodes generally. Two consequences:

1. It cuts **in favour** of T1 — the toll binds exactly where the sweep routes, so a
   T1 null is informative rather than merely uninformative.
2. It bounds the **S-mag column**, which nobody had flagged: where all 50 exits sit at
   similarity 1.0, `w_sim · (1 − sim)` is an identical constant across them, so S-mag
   **cannot discriminate on the first hop** out of those eight endpoints. Recorded in
   §1.3 so A3/A5 are not read as "the dive barrier alone" without the caveat.

**What was deliberately not done.** D4–D7 and PR-A/PR-B are **untouched and open**,
tabulated with success conditions in §9's closing table so no one reads the amendment
set as discharging the review. The highest-value one is **PR-A**: run **A0 vs P first,
as a gate**, not as one arm among fifteen — if A0 ≢ P the factorial must be re-anchored
with floor fully crossed, which is a redesign better found before fourteen other arms
than after. P2 was marked discharged in §7 (it had remained listed as outstanding
despite three independent verifications).

Run count 13 → 15. No change to the primary outcome, any effect-size threshold, the
pair sets, or the attack analysis.

**A6 added after external review of the ordering.** §5's scoring rule (analyst D5) was
initially left in the open column, due "before §5 runs". That was wrong on sequencing, for
a reason worth recording: **the owner's labels are reusable across proxies but not across
samples.** §5 already anticipates re-running verbatim against Wikipedia pageviews if Deezer
fails — same labels, no re-asking. But if the *scoring rule* turns out to need a different
sample, he has by then thought about the problem, and a second pass is contaminated by his
first. A defective interpretation rule therefore does not merely delay P4; it can spend the
resource P4 exists to acquire. A6 landed in this amendment set instead.

### Track 2 execution order (fixed 2026-07-23, before any step ran)

Recorded because the order is not obvious and one step is easy to skip.

| # | Step | Note |
|---|---|---|
| 1 | **This amendment set** (A1–A6) | Done. G5(a)'s mirror-verify sequencing already landed with the pre-Track-2 guards — **it is not outstanding**, and re-deriving it would be waste. |
| 2 | **Build the minimal mirror; verify byte-identity against production `find_path` with guard G OFF** | The log §3.10 gate, and **the only step where failure means stop, the harness is wrong**. §1.2's G5(a) note scopes that instruction to this step alone. |
| 3 | **Enable G uniformly across all arms including P** | Per §1.2. Carries analyst **O8**'s consequence: with G applied to P, no comparison anywhere is against shipped behaviour on pairs 4–5, so C5's no-regression inspection cannot see the d0 change the owner would notice there. |
| 4 | **A0 vs P** on the full pair × depth grid | Settles the factorial's shape. Report alongside it the fraction of examined nodes carrying a non-zero floor term (PR-A). |
| 5 | Scoring and the remaining arms | Built against a shape that is by then known. |

**P4 runs in parallel, starting now.** It sits outside this chain entirely — it needs no
harness, only the fixed name list, ten minutes of the owner's time, and an artist-search
fetcher that must **not** reuse `clips.py` (§0). Its latency is owner-availability, not
compute, so steps 2–4 proceed while it is outstanding.

**Step 4 is a test whose pre-registered expectation is "no difference", and that is
deliberate.** Stating it now so a pass is not misread later: **a pass is the good outcome
and costs exactly one arm.** The alternative it buys insurance against — discovering
mid-sweep that eight factorial cells are anchored on a constant that was never constant —
is the expensive one. This project has already been saved once by a pre-registered null
being read as informative rather than disappointing (log §2.13 C5); this is the same
discipline applied earlier in the chain.

### P1 discharged — and the answer collided with pair 1 (2026-07-23)

The owner supplied both URLs. Resolved against the adopted artifact in
`builder/analysis/2026-07-23-f6-trace-capture/` (owns its figures); all 44 MBIDs resolve.

**Both URLs carry the same endpoints and F3's bypass lists are a strict prefix of F6's**,
so this is one continuous walk captured at 15 bypasses and again at 42 — not two traces.
The pair is **Miles Davis → Daft Punk**, which is already **pair 1** of the analysis set.
Amendment **A7** applies §2.3's substitution rule (pair 8 → Nirvana → CROOVE) and lets
pair 1 inherit the trace rationale. **A7's trigger was interpreted, not executed** — the
rule fires on "unrecoverable" and this pair was recovered-and-duplicated — so it is
flagged in both the pre-registration and here as the judgement call it is. Reversal costs
nothing before any arm runs; the alternative is seven analysis pairs, described as seven.

**Two things the capture gives that the prose record could not:**

1. **F3's example is verbatim in the URL.** The owner reported the unacceptable case as
   "Bowie → Pink Floyd → Beatles". Known-presses #10, #11, #12 are David Bowie, Pink
   Floyd, The Beatles, in that order. A reported impression independently confirmed after
   the fact — rare here, and worth noting as a point *for* capturing URLs rather than
   summarising sessions.
2. **All 42 bypassed artists sit above the 97.7th in-graph popularity percentile**
   (minimum: The Hives, 0.9773). Direct support for F2 and log §2.9 from the owner's own
   session rather than a scripted walk. **Stated carefully:** this is the *rejected* set,
   not the *offered* set, so it cannot show the router never offered anything obscure —
   F6 records that he did reach Max Richter and Ólafur Arnalds, and neither appears here
   precisely because he did not bypass them.

**A currency note, since this is the project's recurring trap.** Every one of those 42 is
genuinely famous, so here in-graph popularity and real fame coincide. That does **not**
soften §2.11: its point is that the same top band *also* holds lo-fi and synthwave artists
who are not famous. The band is a mixture and this trace drew the famous part of it. The
external proxy is still required.

**Also recoverable, and worth knowing: the interleaving is not.** `dislike` and `known`
are separate URL parameters, so order within each list survives but the sequence between
them is lost. Irrelevant to the sweep (all-`known`, scripted victim) but it bounds what
this trace could ever be replayed as, and it is a small argument for a future single
ordered bypass parameter if replay ever matters.

### Step 43 — the snap-back reconstructed, and a design choice validated

The owner supplied one further URL, one bypass past F6, not knowing whom he had bypassed.
It is F6 plus one appended `dislike`, so it reconstructs exactly. Record:
`builder/analysis/2026-07-23-f6-trace-capture/` §5 (owns its figures).

He bypassed **Nancy Sinatra**. The path went from a **nine**-interior corridor —
Frank Sinatra → Nancy Sinatra → Ennio Morricone → Hans Zimmer → Clint Mansell →
Max Richter → Ólafur Arnalds → Tycho → deadmau5 — to a **four**-interior fallback:
Nina Simone → Leonard Cohen → Simon & Garfunkel → Queen. **Queen and Simon & Garfunkel
are the two artists he named in his F6 report**, so the reported snap-back is confirmed
to the artist.

**The load-bearing result: the in-graph metric cannot tell those two paths apart.**
Minimum interior percentile 0.9829 versus 0.9820; medians 0.9940 versus 0.9909. Where it
differs it marginally *favours the snap-back*. Max Richter (0.9862) and Ólafur Arnalds
(0.9908) score as *more* popular than Queen (0.9820).

**Why this matters more than one trace normally would.** §2.11 established
popularity ≠ fame at artist level, and the nine-names verdict confirmed it at artist
level. This is the first **path-level** demonstration, and it is on the exact contrast
Track 2 is built to produce: a success criterion phrased in in-graph percentile would
score the path he valued and the path he rejected as **indistinguishable**. The
pre-registration already scores C1/C2 on an external fame proxy — so this **validates a
choice already made** rather than prompting a new one. It also raises the cost of P4
failing: with no fit proxy there is no fallback metric that can see this contrast, which
strengthens §5's terminal fallback (owner-labelling) from "expensive but honest" to
"expensive and apparently necessary".

**Three observations, labelled as observations — n = 1, none pre-registered:**

1. **The corridor had a single entrance.** One bypass did not substitute one artist; it
   destroyed the route from Frank Sinatra onward. No second-cheapest way into the corridor
   existed, so the router fell back wholesale. If it generalises, the §1.5 **F5**
   diagnostic is the nearest instrument and it currently looks for the opposite pattern.
2. **Payload collapsed 9 → 4.** Attack 5 / WHAT-GOOD #2 in the wild rather than argued.
   **C4** exists for this and its threshold would flag a drop of five.
3. **The floor had been dead for ~35 bypasses** at both states (zero from about bypass
   5–6). Analyst **D2** observed in a real session rather than derived.

None of these enters the record as a finding; per §2.4's interpretation discipline they
are post-hoc and would need an `ml-graph-analyst` check to become one. They are recorded
because they are cheap, and because item 1 may be worth a diagnostic the sweep does not
currently carry.

### Steps 2–4 executed (2026-07-23) — and the A0 branch fired

**Step 2 — mirror built, gate PASSED.** `builder/analysis/2026-07-23-track2-sweep/`
(owns its figures). 212 cells across all 12 pairs, byte-identical to shipped `find_path`
with guard G off. The verification was written and run **before** the mirror existed; it
failed on the missing module, then passed. Two pairs walked zero depths — Radiohead → The
Beatles and Muse → Coldplay resolve direct, so with G off there is no interior and no
victim. That is G5(a)'s contradiction in empirical form, and the reason the G-off-then-G-on
sequence exists.

Byte-identity needed three deliberate choices, recorded because "same algorithm" would not
have sufficed: production's exact term-summation order (float addition is not associative),
optional terms applied inside branches rather than as `+ 0.0`, and `(cost, node)` heap
entries so ties break on node id identically.

**Step 3 — guard G enabled uniformly.** Both arms below carry it.

**Step 4 — A0 vs P: identity FAILED, on one cell in 252.**

| | |
|---|---|
| Cells compared | 252 |
| Identical | **251** |
| Divergent | **Miles Davis → Daft Punk at d0**, and nothing else — that pair is identical at d1–d20 |

At d0 the un-relaxed floor is 0.6726. **P** routes through Dean Martin (0.6668); **A0**
through Michael Bublé (0.6563). Both dip below the floor — the floor does not prevent the
dip, it picks the shallower one, and buys a sixth interior doing it.

**The load-bearing measurement (PR-A, discharged).** Floor-term firing rate by depth,
pooled over all 12 pairs: **51.3 % at d0**, 14.3 % at d1, 2.1 % at d2, 0.12 % at d3,
0.005 % at d4, 0.001 % at d5, and **exactly 0.000 % at every depth from d6 to d20**.

**What follows — three findings, the first two settled:**

1. **Adjudication claim 23's mechanism is falsified, its conclusion nearly survives.**
   Claim 23 said the floor never fires because `w_jump` stops paths dipping below it.
   Paths do dip below it, and the term fires on half of all relaxations at d0. What holds
   is only the outcome: 1 changed cell in 252. **This belongs in the adjudication's §6
   claim table** — flagged, not edited here, since that document owns it.
2. **§0's confound cannot occur in the scored window, and this is now measured rather than
   argued.** The relaxed raw floor reaches zero after `ceil(base_floor / 0.15)` `known`
   bypasses *regardless of arm*, and `max(0, 0 − pop_raw_v) = 0` thereafter — so it is zero
   for every raw-floor arm at every scored depth (C1 at d ≥ 10, C2 at d15/d20). The term
   cannot "switch on only in the arms that work". **Raw floor only** — the FL arms' pctl
   floor with the A2 relax constant is alive to ~d18–20 by design and is untouched by this.
3. **Where the floor does live is d0–d2 — exactly where C5's no-regression inspection
   looks.** So it is not irrelevant; it is relevant precisely where no *scored* criterion
   operates.

**Stopped here deliberately.** §1.4 requires the design revision be recorded before
proceeding, so no further arm has run. This is also a **material mid-flight amendment and
therefore a handoff seam** by the CLAUDE.md rule — the next session reads a governing
document that has changed, which is the condition the rule was written for.

### The exposure map — what the floor change actually touches

*Owed before any escalation, per the CLAUDE.md rule added 2026-07-23. Building it first
would have dissolved most of what was escalated.* One row per pre-registered criterion:
does the floor change cross it, where, and what was measured there.

| Criterion | What it reads | Crosses the floor? | Measurement |
|---|---|---|---|
| **C1** | ΔF at ≥ 10 bypasses | **No** | Floor term identically zero at ≥ 7 bypasses for every raw-floor arm; P ≡ A0 at every depth ≥ 5 on all 12 pairs, both victim policies |
| **C2** | absolute reach at 15 / 20 | **No** | as C1 |
| **C3** | within-arm, 5 vs 20 | **No** | Every factorial cell A0–A7 has the floor **off**, so C3 is read inside an arm with no floor term at all. Even switched on, path exposure at 5 bypasses is zero |
| **C4** | interior count at ≥ 10 | **No** | P ≡ A0 throughout that range |
| **C5** | first path, vs P | **YES** | 1 pair of 12 differs, stable across both victim policies — pair 1, one interior substituted, 6 → 5 |
| **C6** | proxy coverage | **No** | not a routing quantity |

**One criterion crosses, and its fix costs zero extra runs.** A0 *is* production with the
floor switched off, and its full grid already exists.

### Decision — mine, and taken

**Keep the floor off across the factorial (option 2), and report C5's first-path
inspection against both P and A0.** No extra runs; one dated amendment.

Stated per the CLAUDE.md rule on whose decision is whose: this is **methodology and run
counts**, which is not the owner's column. The earlier version of this section tabled three
options and handed them over — that was an abdication, and it is recorded as one.

Why not the alternatives: **option 1** (cross the floor fully) roughly doubles the sweep,
and the analyst review measured that its added cells do **not** buy a clean one-knob floor
effect at depth — what they differ by there is *trajectory inheritance*, not a live floor.
**Option 3** (floor-on cells to 5 bypasses only) would miss that inheritance entirely.
What would change the decision: a demonstration that the d0–d2 asymmetry propagates into
C1/C2 cells for some arm — the review looked and found P ≡ A0 at every depth ≥ 5 on both
victim policies.

### Corrections to the step-4 write-up, from the review

Four of them, all mine, and two change what a reader would conclude:

1. **The unconditional dead-bound is 7 `known` bypasses, not 6.** `ceil(base/0.15)` is 7 on
   7 of the 12 pairs, which carry a strictly positive floor at 6. The measured zero at 6 was
   a **routing** fact for the arms tested, not arithmetic. Scored depths are unaffected —
   the claim was over-broad in span, not wrong where it was used.
2. **"The added cells can differ only at d0–d5" was false.** Floor-value invariance is not
   floor-*effect* invariance: a changed first path changes which artist gets bypassed, and
   that carries forward. Measured at 2 of 12 pairs still differing after twenty bypasses
   for the diagnostic twins, stable across both victim policies.
3. **The 51 % figure does not show what I used it to show.** A relaxation is an *edge
   examined during search*, not an artist on the finished path — reachable is not binding.
   It cannot falsify a claim about paths.
4. **Claim 23 contains no mechanism, so "its mechanism is falsified" is not a coherent
   statement.** The `w_jump` sentence belongs to **log §2.12**; the pre-registration §0
   cites the two jointly, which is where the conflation came from.

**What should enter the adjudication's claim table** (flagged, not edited — that document
owns it): claim 23's "no path dips below the floor" **does not transfer** to this artifact
and pair set; the headline is **nearly upheld** — refuted as an absolute, upheld at one
changed cell in 252. The original measurement is **not** retracted. And log §2.12's
mechanism is **refined, not demolished**: removing `w_jump` deepens the dip 24×, so
`w_jump` *bounds* the dip rather than preventing it.

### Two findings from the review that change later reads

- **The FL arms' C3 gradient is substantially manufactured by their own device.** The
  percentile floor sits at ≈ 0.74–0.75 at 5 bypasses and 0 at 20 on all 12 pairs, so an FL
  arm passing C3 is **not** the same evidence as a floor-off cell passing it. This needs to
  be attached to §2.4's R3 read before any FL arm is interpreted.
- **"The floor dies after five bypasses" is true of the scripted protocol, not of the
  shipped product.** Under all-`dislike` (relax 0.08) the raw floor survives to 12
  bypasses; 13 is the universal any-mix bound. Relevant to C3 landing, not to Stage A.

### The gate had no effect size, and that is the general lesson

The A0 gate was an exact-identity test over 252 cells whose failure branch roughly doubles
the sweep. It fired on **one** cell, at a depth no criterion scores, and got the identical
reading a 200-cell divergence would have got. Every *outcome* criterion in the
pre-registration carries a threshold; its **gates carried none**. Now a CLAUDE.md rule.
Amendment **A8** gives the remaining gates effect sizes.

**If A0 ≠ P, that is a pre-registered branch firing, not scope creep.** §1.4's A0 row
already requires re-anchoring on P with floor as a fully crossed column — sixteen cells
plus attachments, outside the stated budget. The session that hits it should write a
**second dated amendment** and treat it as the design working as intended. Framing it now
so it is not experienced as a late discovery or an admission.

### Session resumed from the mid-track handoff (2026-07-23) — bookkeeping cleared, P4 put to the owner

Picked up cold from `2026-07-23-HANDOFF-track2.md`, cold-read verified against the owner
before acting (three small gaps found, all in the handoff's own git bookkeeping — HEAD and
commit count stale, PR title stale — none in the technical record; the handoff was sound
where it mattered). **Convention fixed this session: one committer, and it is the session,
not the consultant.** The three modified meta-files (`CLAUDE.md`, both `SKILL.md`) are a
**consultant session's** in-flight edits, deliberately left uncommitted and out of every
commit here.

Work done, in order, each committed separately:

1. **PR #9 title and body rewritten** to cover all ten commits and both gate outcomes
   including the A0 failure. It had described only the first commit's D1–D3 scope.
2. **Adjudication claim 23 amended** for the A0 result — the wording the A0 gate review
   settled but nobody had applied. Refuted as an absolute, *nearly upheld* as an outcome
   (1 changed cell in 252), original measurement not retracted. **Also fixed a
   table-rendering defect:** the claim table has four columns, so the fifth-cell amendments
   on claims 23 and 35 were dropped by the renderer — claim 35's 2026-07-22 amendment had
   been invisible in rendered markdown since it was written. Both now sit inside the verdict
   cell. *(This is the CLAUDE.md "blast radius includes every document that describes the
   quantity" rule in miniature: the amendment was present in source and absent on screen.)*
3. **Amendment A10 — §5's fame-proxy sample fixed and committed before any label**
   (`builder/analysis/2026-07-23-track2-fame-proxy/`). Two defects, both found by deriving
   the sample against the repo rather than reading the prose, both unrecoverable after
   labelling (the A6 argument again — labels reusable across proxies, not across samples):
   - **S1 and S3 overlapped by four artists.** saib., Purrple Cat, idealism and Miami
     Nights 1984 are in S1's nine *and* were listed in S3. "~33" was **29 distinct**; the
     four would have been double-counted in every pooled statistic and read under two
     strata §5 interprets differently. S3 is now the two F6 reaches only, **n = 2, counts
     not AUC**. Its purpose is unharmed — testing §2.11's inference is what S1 does.
   - **§5's claim that S1's labels "already exist" is false** at three-bucket granularity.
     The record holds one collective verdict ("mostly unknown"), assigns no artist to a
     bucket, never splits *heard of* from *never heard of* (where B_unk lives), and by
     "mostly" implies one of the nine was known without saying which. The nine are labelled
     with everyone else; S1-anchors-the-unknown-end becomes a result, not an assumption.
     Original verdict **not** retracted — it settled §2.11 and nothing more was asked of it.
   - **S2's twelve fixed by a mechanical rule** (three named exemplars, then each judged
     pair's least/most/median in-graph-popular interior, ties on lowest MBID) rather than
     hand-picked. `pop_raw` spreads, never scores. **Selection is itself evidence:** Whitney
     Houston is the *least* in-graph-popular interior of two of three pairs (0.5124) and
     Nick Drake the *most* popular of one (0.7400, above Frank Sinatra and Ella Fitzgerald)
     — §2.11 reproduced inside the sample built to test it. Match-failure falsifier now
     fires at **6**, not 7 (proportion unchanged, denominator 29 not 33).
4. **Blind label sheet emitted** in a sorted-then-seeded-shuffle order
   (`blind_order.json`, seed 20260723), committed so the strata — S1 insular, S4
   off-platform — do not leak grouping to the owner, and so the answer→stratum mapping is
   auditable rather than reconstructed. Put to the owner; **he is labelling now.**
5. **The Deezer fetcher built, P5-tested, probed** (`fetch_fame.py`, `test_p5.py`). Artist
   search with exact P5 match, **shares no code with `clips.py`** (§0). P5 unit-tested
   including the U+2010 trap and a guard that NFKC alone does not fix it. `--probe`
   discharged §0's one external assumption against out-of-sample names (Radiohead /
   Portishead / Sault): **`nb_fan` present on all three, 27k–4.06M**, so the field exists
   and has ranking range. **The sample stays unfetched until the labels land** — §5's
   protocol order (label, then fetch), and it is load-bearing: match failure is a *measured*
   quantity, so silently swapping an unresolvable name would corrupt what C6 measures.

**Ordering deviation, taken as methodology, not asked:** the handoff proposed fetcher →
put-to-owner. Reversed to put-to-owner → fetcher, because the owner's ten minutes need only
the name list, §5 numbers labelling as step 1 for a reason, and building the fetcher while
he labels loses nothing. Snyk `snyk_code_scan` clean on all fame-proxy code and re-run over
the four other new analysis packages (0 issues each).

**State at this point:** P4 blocked on owner labels. Unblocked and not yet done — P6
percentile tie-handling machinery, the §5 scoring code (buildable, not runnable until
labels + counts exist), C1–C6 computation (needs scored arms), and the D4/D6/D7 + C3-anchor
(handoff 1b) amendment. No arm has run. Artifact untouched, sha256 `4cb84ef9…b061dc8`.

### P4 resolved — Deezer `nb_fan` FAILS §5; Wikipedia is the pre-registered next proxy (2026-07-23)

Owner labelled the 29 blind the same session. Recorded in `labels.json` via
`record_labels.py` (keyed by blind position, auditable). Fetched and scored;
`builder/analysis/2026-07-23-track2-fame-proxy/` owns all figures. **Committed before any
narration** — the falsifiers were pre-registered, and firing inconveniently is not licence
to relitigate them.

**Two of the four falsifiers fired:**

| §5 test | Result | Falsifier | |
|---|---|---|---|
| Primary — AUC(know-well > heard-of), S4 excluded | **0.680** (n=5 vs 5) | < 0.70 | **FIRES** |
| Catastrophic inversions outside S4 | **2** | > 1 | **FIRES** |
| Spearman (diagnostic, non-gating) | 0.697 pooled | — | — |
| B_unk | valid at 199,337 (81 % never-heard below) | none exists | clear |
| Match failure | 3.4 % (CROOVE only, an S4 off-platform case) | > 20 % | clear |

The two inversions: **Paul Simon (244k)** and **Death Cab for Cutie (199k)** are *know well*
but sit below **Diana Krall (833k)**, *never heard of*. Mechanism is a Deezer market/genre
skew, not noise: Paul Simon and Death Cab are under-followed on Deezer relative to their
fame; Diana Krall (jazz-pop, older record-buying audience) is over-followed relative to how
known she is. **Popularity ≠ fame again, on a third population** — this is the same failure
the in-graph number has (§2.11) and the same the trace showed at path level (step-43),
reproduced on Deezer follower counts.

**The AUC miss is marginal (0.68 vs 0.70) and rests on two artists; it was NOT argued away,
deliberately.** The 0.70 line was committed before the labels existed precisely so a
near-miss cannot be relitigated post-hoc. The inversion falsifier fired outright. Both mean
the same thing: `nb_fan` is unfit at this granularity.

**A10 was vindicated twice by the labels themselves:** (1) S1 came back **all nine
"never heard of"** — the earlier collective "mostly unknown" was actually *fully* unknown at
three-bucket granularity, so assuming the buckets would have been wrong; (2) S2's spread put
**Nick Drake (most in-graph-popular interior of pair 1) at only "heard of"** while
**Whitney Houston (least popular of two pairs) at "know well"** — the popularity/fame
inversion the mechanical selection surfaced is confirmed in the owner's own labels.

**Pre-registered response (§5): re-run the identical protocol against Wikipedia pageviews,
same labels, no re-asking.** This is methodology, not an owner decision — the labels are
committed and reusable across proxies (the reusability A6 bought). Handed off here rather
than executed **because Wikipedia matching is materially harder than Deezer's and deserves
a fresh session**, not because it is blocked.

### Next unit — the Wikipedia pageviews proxy (self-contained; fresh-session task)

Everything it needs is committed. Concrete shape:

- **`score.py` is already proxy-agnostic** — it reads `labels.json` + a `fan_counts.json`
  shaped file and applies the four §5 falsifiers. Point it at a Wikipedia-counts file and it
  scores unchanged. Do **not** re-collect or re-shuffle labels; `blind_order.json` and
  `labels.json` are fixed.
- **The hard part is name → article resolution**, which Deezer did not have. Wikipedia needs
  a title lookup (MediaWiki `opensearch`/`query`), and it carries disambiguation and
  cross-language cases the sample deliberately contains: **林俊傑 → "JJ Lin", EGOIST, CROOVE,
  Wishbone Ash, saib./idealism/Purrple Cat** (lo-fi acts that may have no article at all — a
  no-article is a *legitimate* proxy outcome, not a match to force). English Wikipedia
  pageviews are the right target for an English-speaking owner; state that choice.
- **Metric:** monthly pageviews over a fixed, pre-stated window via the Wikimedia REST
  pageviews API, summed or averaged — fix the rule before fetching, and assert it, exactly
  as Deezer fixed exact-match-after-P5 first.
- **Match failure is still a measured falsifier** (> 6 of 29). A no-article artist counts as
  a failure; do not hand-resolve it.
- **If Wikipedia also fails:** the §5 terminal fallback is owner-labelling of every
  evaluated-path artist — that spends real owner time and **is** his decision. Do not enter
  it without putting it to him.

**Still open beyond P4** (unchanged): P6 percentile machinery, the C1–C6 arm harness, and
the D4/D6/D7 + C3-anchor amendment. All wait on a fit proxy. No arm has run. Artifact
untouched, sha256 `4cb84ef9…b061dc8`.

---

### Consulting-pass deferrals — documentation layer (2026-07-24)

A consulting session on doc sprawl and context cost left two edits **applied** and two
findings **deferred**. Recorded here so they survive the worker handoffs and come due on
their own; they are documentation hygiene, not Track 2 experimental work.

**Applied (on disk, in the meta-file edits carried across this handoff):**

- **A standing-layer budget + displacement rule.** `CLAUDE.md` + `memory/` + both
  `SKILL.md` bodies load unconditionally and grew 661 → ~1,440 lines in two days with every
  addition justified. `CLAUDE.md` now states the layer is budgeted and additions are
  displacement-only; `closeout` **D6** enforces it from the diff, and D6 is in the
  mid-flight scaling because a handoff is when the delta is both non-zero and needed by the
  successor.
- **Rules do not get expiry conditions** (a hypothesis put to the consultant and killed):
  the rules are invariants; what grows is the incident narrative attached to them, which is
  load-bearing. D6 prices that growth instead.

**Deferred — due when Track 2 *adoption* is recorded (a worker handoff does NOT satisfy this):**

| Deferred | Why it waits | Success condition — due when | Owner |
|---|---|---|---|
| **Supersede Phase 1 log §2** — its correction notices now exceed its live content; write a short successor stating the surviving position, mark the original HISTORICAL, retain for audit | It is a live citation target for the in-flight Track 2 pre-registration; rewriting it mid-experiment risks a retraction, not a cleanup | **Track 2 adoption recorded** in this log | A short doc-editing session acting on the next `doc-auditor` (B1) report — **not** a Track 2 worker; minimum-scaling close |
| **Relocate `CLAUDE.md` "Writing and reviewing plans here"** (~107 lines, 23% of the file) out of the standing layer, behind a pointer + the factor-table rule inline | It is the worked example the Track 2 pre-registration cites; moving it while the experiment is read cold by an incoming worker is the same timing hazard | **Track 2 adoption recorded** in this log | Same doc-editing session; this is the offsetting subtraction for the +lines D6 will show at this handoff |

---

### Closeout B1 — doc-auditor (2026-07-24, fresh session)

Ran as the handoff's stated first action. Two HIGH defects, both verified against source,
both genuinely open (not live citation targets), both fixed (commit `5dbd9eb`):

- **`docs/README.md` did not list `2026-07-24-HANDOFF-track2.md`**, and still described the
  2026-07-23 handoff as ACTIVE. A cold session reading the map would have missed the newer
  handoff. Added the row; marked the 2026-07-23 one SUPERSEDED.
- **`WHAT-GOOD-LOOKS-LIKE.md` (AUTHORITATIVE) still used `hubfrac`** (pre-2026-07-23 name)
  at two points describing the payload companion metric. Renamed to `top1pct_degree_frac`.

MEDIUM/LOW findings left as-is and reported to owner, not actioned: stale names in the
frozen Phase-1/Phase-2 logs (deliberate; Phase 1 log §2 is the deferred citation target
above), the pre-registration's amendment-table order (cosmetic, in-flight citation target),
and a handoff-sequencing non-issue.

### P4 fallback RESOLVED — Wikipedia pageviews FAILS §5 on coverage; terminal fallback reached (2026-07-24)

Built and ran the pre-registered second proxy. Figures owned by
`builder/analysis/2026-07-24-track2-fame-proxy-wikipedia/` (README + `score.json`).
**Committed before any narration** (`7cbc31d`) — the falsifiers were pre-registered.

**Result: one falsifier fires, and it is the coverage one — but Wikipedia passes the two
Deezer failed.** AUC 0.720 (clear; Deezer 0.68), 0 catastrophic inversions outside S4
(clear; Deezer 2), valid B_unk — but **match failure 9 of 29 (31 %) fires** (> 6 of 29).
**The two proxies are unfit for opposite reasons:** Deezer sees everyone and misranks the
mid-fame band; Wikipedia ranks well but is blind to the obscure tail — 8 of the 9 failures
are the S1 lo-fi/synthwave stratum, which is *exactly* the band Track 2 must reach (F2).
An artist absent from English Wikipedia is the kind of artist the sweep wants to route
toward, so a proxy that cannot score that stratum cannot set C1/C2's reach criteria however
well it ranks the rest. The coverage falsifier measures the real deficiency; it is **not
argued away**, mirror-image to Deezer's near-miss AUC not being argued away.

**All 9 failures verified genuine** (audited: for each, no opensearch candidate satisfies
identity + performer + musicality). Miami Nights 1984 has no article at all; `idealism`
resolves only to the philosophy concept and an unrelated album; the rest resolve only to
wrong-spelling/wrong-entity candidates the identity clause correctly rejects (CROOVE →
Russell Crowe, sleepy fish → Johnny Pearson, Leavv → an Italian film).

**The resolver, and two corrections caught before any score was computed** (both
identity-directed, not outcome-directed — the AUC was not looked at until the resolver was
correct; this matters for the pre-registration discipline):

1. `--probe` (out-of-sample, §0 discipline) killed the **bare-top-hit** rule: Portishead
   and Sault resolve to the *town*, so a strict top-hit fails famous acts whose name is a
   place — biasing against fame, fatal for an AUC test.
2. The first sample run killed **musicality-alone**: it accepted fuzzy garbage that happens
   to be musical. Fixed with an **identity** clause (the Wikidata entity must actually carry
   the query name as a label/alias in any language — which also lets 林俊傑 → JJ Lin via its
   zh alias) and a **performer** clause defined by *excluding works* rather than
   whitelisting band types (a whitelist wrongly rejected Wishbone Ash, typed "rock band").

**`score.py` was parametrised, not duplicated** (`--counts/--labels/--value-key/--out`);
defaults reproduce the Deezer `score.json` **byte-identical** (verified via `git diff`), so
the four falsifiers are computed by the same code for both proxies. This also makes the
handoff's claim that `score.py` was "already proxy-agnostic" literally true — it was not
(the paths and the `nb_fan` key were hardcoded); a small over-claim, recorded because "I
checked" vs "I asserted" is the §2.13 distinction.

**Where this leaves Track 2 — the terminal fallback, and it is the owner's call.** Both
pre-registered proxies have now fired at least one §5 falsifier. Per §5 the terminal
fallback is **owner-labelling of the evaluated-path artists only** (bounded: the sweep
touches at most a few hundred distinct interiors; labels reusable across arms), with C1
degrading to the labelled ordinal scale. **That spends real owner time and is his
decision** — put to him, **not entered**. No sweep arm has run; still open beyond P4 are P6
percentile machinery, the C1–C6 harness, and the D4/D6/D7 + C3-anchor amendment. Adopted
artifact untouched, sha256 `4cb84ef9…b061dc8`. Snyk clean on the new code and the modified
`score.py`.

### Obscure-tail attractor question — analyst run: NOT graph-limited (2026-07-24)

The owner asked whether the graph is over-biased toward synthwave/lo-fi in the obscure
region such that fame-reducing paths funnel into it regardless of start genre (would make
Track 2's goal graph-limited, not tuning-limited). Answered myself first with a cheap probe
(the 10 known lo-fi "unknowns" sit at the 97th–99th `pop_raw` percentile — top of the
distribution, not the tail — and form a dense blob, ~44 % shared neighbours), then ran the
`ml-graph-analyst`. Record: `builder/analysis/2026-07-24-obscure-tail-attractor/` (owns its
figures).

**Verdict: tuning-achievable, NOT graph-limited.** Graph is cleanly genre-modular (Louvain
0.884, 68 communities). The chillhop/lo-fi community (comm40) is real and dense but **small
(424 nodes, 0.57 %)**, sits at the 96th–99th `pop_raw` percentile (low external fame, high
in-graph popularity), and is 97 % internal. Funnel test with the **shipped `find_path`**:
across 110 cross-genre pairs, **0 of 586 interiors** land in comm40 (0.00× vs a 0.83 %
null); repeated-`known` fame-descent stays *within* each genre corridor while `pop_raw`
falls ~0.80→0.50; a control pair actually heading to lo-fi *does* enter it, so the test
discriminates. **Independently spot-checked** (Metallica→Miles Davis, Johnny Cash→Aphex
Twin, Beatles→Eminem: 0 blob interiors, sensible famous bridges) — claim holds.

**Load-bearing caveat, carried into A11 and the sweep:** the whole test is in the shipped
**raw-popularity** currency, and the blob is *high* raw-popularity, so the raw floor points
away from it — part of *why* the funnel is zero. A **fame-currency** floor (the sweep's
actual intervention) is the untested lever; it could surface these high-pop/low-fame lo-fi
artists on downtempo-adjacent paths. The blind listen is the coherence arbiter.

### P4 CLOSED — owner adopts Option C; pre-registration A11 committed (2026-07-24)

Presented both proxies' results and two owner-requested free explorations (absence-as-signal
and the attractor analysis). **The owner mis-stated a preference for B, then corrected to C**
on the sunk-time reasoning (B's labelling premium exceeds the exposure it insures against;
C's failure is a cheap re-score, not a shipped defect, and cannot pass the blind listen).

**Decision recorded as the owner's:** the fame proxy for C1/C2 is **Wikipedia pageviews with
an unmatched interior scored at the fame floor (0)** — §5's owner-labelling terminal fallback
is **not** taken. Residual risk (a foreign/historically-notable absent artist scored obscure)
accepted, with a d15/d20 guard (owner one-glance check of *potentially-notable* unmatched
interiors: non-Latin name, or a non-English article exists). **Formalised as pre-registration
amendment A11, committed before any factorial arm runs** — the timestamp is the gate. A11
partially discharges D4 and carries the raw-vs-fame currency caveat above.

**This is a material amendment to the governing document → a handoff seam** (CLAUDE.md rule).
The fame-proxy track is closed; the sweep (P6 percentile machinery, the C1–C6 harness with
the absence-as-floor + guard encoding, D4/D6/D7 + C3-anchor amendment, then the arms) is the
next, fresh chunk. No factorial arm has run. Artifact untouched, sha256 `4cb84ef9…b061dc8`.

### Closeout B1 — doc-auditor at the sweep seam, and a status correction (2026-07-24)

Second B1 of the day, run as the handoff's stated first action: the earlier one
(commit `5dbd9eb`, above) predates A11, the P4 closure entries, and the two new
`builder/analysis/` directories, so it had not seen the material changes.

**One HIGH defect, and it is a defect of the class B1 exists for — a claim carried forward
by copying rather than checking.** **P6 (the percentile machinery) was recorded as open work
in three documents and has been built since execution-order step 2.** It is
`MirrorContext.build` in `builder/analysis/2026-07-23-track2-sweep/mirror.py` — average rank
over N with ties averaged, plus A3's `jump_scale_pctl` mean-matching ratio — committed in
`2dedefd` and covered by the byte-identity gate that licensed the mirror. The three:
pre-registration §0 (resolution table) and §7 (prerequisite P6), and the 2026-07-24 handoff
§2. **The entry above ("P4 CLOSED") repeats it too**, in its closing list of what the sweep
still contains; it is left standing as written, because a dated log entry is an audit trail
and this correction is the amendment to it.

**How it survived.** §0 and §7 were written before any step ran and were true then. Step 2
built the machinery inside the harness while leaving `pop_pctl` unused in `api/src` —
correctly, since shipped code is not edited before adoption — so the one mechanical check a
session would reach for (*is `pop_pctl` used anywhere?*) returns clean and **confirms the
stale reading**. Every document after that copied the prerequisite list forward rather than
re-checking it. This is the B1 rationale in its exact stated form: a grep cannot find a
defect whose evidence is an absence, and the session that wrote the handoff had no reason to
doubt a line it had inherited.

**Cost of not catching it: the next session builds a percentile machine that already exists,
or stops to ask why the harness disagrees with its own pre-registration.** Neither is
expensive alone; the second is a session boundary.

**Fixed** in the pre-registration (§0 row, §7 P6 row — both marked as corrections, not
amendments; no design changed) and in the handoff §2.

**One MEDIUM, fixed:** the pre-registration's front banner still read "ten amendments
(A1–A10)" while §9 enumerated eleven. A11 was marked inline and indexed but the banner was
not updated — the mirror-image of the omission defect, and the reason the banner carries its
own "a reader who lands mid-document never sees this" note.

**Nothing else found.** The auditor's remaining items are pre-existing and already recorded:
no `builder/` top-level README, the frozen analysis scripts' pre-rename aliases (deliberate,
mapping in `builder/analysis/README.md`), and older `builder/analysis/` directories not
systematically re-checked. No escalation list — every finding was adjudicable from the
record.

**No figures moved. No arm has run.** Adopted artifact untouched, sha256 `4cb84ef9…b061dc8`.

### Seams named before the sweep is built (2026-07-24)

Written at authoring time per the CLAUDE.md rule, **before any scorer code exists**, because
a seam that lives only in a session's chat evaporates at the next handoff — and this track
has had two handoffs arrive unpredictably. Two seams, one nearer than the other, plus a
correction to how the further one was first stated.

**1. The near seam: the scorer is a handover object, and P8b lands on it.**

The remaining Stage A work does not fit one session, and the boundary does not need to be
judged by feel — **the pre-registration already names it.** §7's P8 records "P8b — the review
of the *harness* — is not yet due: no harness exists." The C1–C6 scorer **is** that harness
(the mirror is the *router*; the scorer is the *measurement*), so **P8b comes due the moment
the scorer is committed and before any arm is scored.** A deferred prerequisite coming due is
exactly what `session-start` §B tells a session to check for, and it falls here.

So the sequence is: **build the scorer → commit it → P8b review → then arms.** The scorer is
a committed, validated artifact, which is the cheap kind of handover object; and it puts the
session that built the measuring instrument on the far side of a boundary from the session
that reads the measurements, which is the pre-registration's own discipline applied one level
down.

**A second structural fact about the run, recorded so it is not discovered at arm nine.**
The 15 runs are **not** one batch. §1.4's attachment arms are defined as *W + one knob*, and
**W is chosen from the factorial results by rule R1**. So the run is two stages with a
data-dependent gate between them: P + A0–A7 + A1u + X (11 runs) → compute C1 per cell → apply
R1 → T1a, T1b, FL1, FL2 (4 runs). R1 is mechanical and pre-registered, so this is a
sequencing constraint rather than a decision point, but a session planning "run 15 arms" as a
single job has mis-planned it.

**2. The far seam: nobody who has seen an arm result administers the blind listen — and the
protocol already solves this better than by personnel.**

First, a correction to how this session first stated it. It located the constraint at the
scorer ("whoever built it holds a prior"). That under-states it: **anyone who runs the sweep
sees arm results, because that is what running it means.** The constraint is *whoever has
seen an arm result is ineligible to administer the listen*, and it binds unconditionally —
including on a session that scrupulously formed no view. This session is additionally
ineligible for the weaker, personal reason (it has twice written down a prediction that a
fame-currency floor may surface lo-fi acts on downtempo-adjacent paths), but that is the
lesser fact.

**Second, and this is why the seam is cheaper than either framing suggested: the question was
already solved here, twice, and solved structurally rather than by personnel.**
`specs/2026-07-22-c3-known-mechanism-blind-listen.md` §5 and §7 make blindness a property of
the **artifact**, not of the administrator: the arm→label mapping is *generated, sealed, and
revealed only after all verdicts are recorded*, the generator emits real app URLs so the
owner uses the product rather than a report, and the administering session is held to "nothing
beyond the bare mechanics." That survives a handoff, and it does not depend on anyone's
self-report of what they know — which a personnel rule always does.

**What sealing does not cover, stated rather than assumed.** Sealing prevents *label* leakage,
not *content recognition*. A session that has seen the arm outputs can often identify an arm
from the artists on the path, which unseals the mapping from the inside. That residual is
exactly what personnel separation buys, and it is small and cheap — so: **adopt the existing
sealed-mapping protocol as the primary device, and treat "a session that has seen arm results
does not administer" as a secondary guard that costs one planned boundary.** Do not re-derive
the protocol; it is written and it has decided the graph twice.

**Neither seam is a reason to slow down now.** The scorer is the next unit either way; naming
the boundaries at authoring time is what makes them cheap when they arrive.

### A12 — C6 stops gating; §2.2's recalibration discharged (2026-07-24, before any arm)

Found while reading §1–§6 in full to write the arm scorer, which is what that read was for.

**A11 inverted what C6 measures, and A11 recorded "no change to §2.2".** C6's ≥ 90 %
coverage floor existed to close §3's Attack 4: under the original encoding an unmatched
interior was **dropped from scoring**, so an arm routing into hard-to-match obscure artists
would have its best evidence silently deleted. A11 changed unmatched to **scored at the fame
floor**. Nothing is dropped now, so the mechanism C6 guarded no longer exists — and the
quantity C6 measures has changed sign.

**The measurement** (owned by `builder/analysis/2026-07-24-track2-arm-scorer/`): every
artist the owner recognises resolves to an English Wikipedia article — *know well* 7/7,
*heard of* 6/6 — and the stratum he does not recognise barely does: **S1, 1 of 9**. So match
failure now marks the obscurity Track 2 exists to reach. Left gating, C6 caps an arm near
**5.6 %** obscure interiors against a famous-heavy P, while **C2 is passed *by* unmatched
artists** (F = 0 sits below B_unk by construction). Two criteria pulling opposite ways on one
quantity.

**Owner's decision, and it is his because it is about the product rather than the
methodology:** the app should route to artists with **no** English Wikipedia article —
"definitely", and he noted the question should not have needed asking.

**He was right, and the diagnosis is worth recording because it is a routing defect, not a
one-off.** `WHAT-GOOD-LOOKS-LIKE.md`'s first value already says *"the product delivers
artists the listener does not already know."* This session did not read it. Two structural
reasons, both fixable:

1. **The standing layer states mechanism, not purpose.** `CLAUDE.md`'s "What this is"
   describes cards, least-cost paths, clips and two bypass signals — end to end, what the app
   *does*. A session can hold all of it and not know that delivering unknown artists is the
   **point** rather than a property of a good path.
2. **The document that says so declares itself out of scope.** Its orient-table trigger is
   "read it before running a blind listen or interpreting a verdict", and its own header calls
   it calibration for the blind test. A session designing a **success criterion** is doing
   neither, honours that scoping, and misses value #1 — which is not listen-calibration at all
   but the product's purpose, and governs any threshold.

**Fix owned by the consultant session** (it is mid-flight in `CLAUDE.md` and the skills; a
second writer there is the collision `session-start` §C warns about): a purpose line in "What
this is", and widen the `WHAT-GOOD-LOOKS-LIKE` trigger to **before designing a success
criterion**. This session commits it when they are done. **Displacement note for D6:** the
purpose line is net-new and nothing comes out for it; the argument for paying it is that this
is the second routing failure today — P6 was the first — and both were a session inheriting a
description instead of checking the thing itself.

**A12, committed before any arm runs.** C6 is removed from the gating set and becomes a
per-arm and per-cell **report** (it still measures how much of a score rests on the absence
assumption). The gating remnant is A11's **d15/d20 notability guard**, which must be
*discharged* rather than merely reported — that is where the residual risk actually lives.
Attack 4 is **not** simply closed: an arm whose reach is concentrated in unmatched artists is
scored almost entirely on the absence assumption. Residual accepted on A11's reasoning — a
scoring-lens error is a cheap re-score and cannot ship, because the listen gates adoption.

**§2.2's one permitted recalibration is discharged and does not fire.** Band gap **6.161**
under A11's encoding, **1.093** under the conservative matched-only reading; the rule fires
only below 1.0. No threshold changes. Carried forward: at 1.093, **C1's −1.0 threshold is
almost exactly one of the owner's perception bands** — so C1 asks for the middle interior to
drop about one full step in how well he would know them.

**No arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`. Work is on branch
`track2-sweep`, off `main`.

### Sanity-checking A12 against the new purpose line — the residual is two-sided (2026-07-24)

The consulting session added `CLAUDE.md`'s "What it is for" paragraph and asked this session
to check its own **A12** against it rather than take the assurance that nothing changed.
Doing the check rather than reasoning about it found something neither session had.

**The purpose paragraph carries two consequences.** The first — *a criterion capping how
obscure the app may go is pointed the wrong way by default* — is A12 exactly; A12 is its
direct application and needs no change. **The second is the one that bites:** *global
notability is a proxy for the wrong quantity — the target is unknown **to this listener**,
not unknown to everyone.*

**Measured against the committed labels + pageview counts.** A11 names one residual — an
**absent** artist wrongly scored obscure — and its d15/d20 guard is built for it. The
mirror-image case had no guard and is commoner: of the artists labelled *never heard of*,
**three score above B_unk** and are counted as famous rather than as reach — **Diana Krall,
Perry Como, Max Richter**. That is 3 of 16 overall and **3 of the 7 the proxy can actually
see**, so where Wikipedia has data on someone the owner does not know, it lands on the wrong
side of his own line about **43 %** of the time. The reverse occurs once (Wishbone Ash,
*know well*, below B_unk).

**A12's rule does not change, and the direction is the reason.** The error is
**conservative** — an artist he would enjoy discovering is counted as *not* reach — so it
can only make **C2 harder** to pass. A proxy error that under-credits success cannot
manufacture a false winner; it can only hide a real one. C1 and C3 never touch B_unk (both
continuous medians), so only C2's absolute clause is exposed, and all three misses are
near-misses at the band edge (F 5.48–5.50 vs B_unk 5.379).

**Recorded as a pre-registered read rather than a redesign.** If C2 lands at **3 of 8** —
one pair short — check first whether any d15/d20 interior in the failing pairs sits within
~0.15 log10 above B_unk; that is this residual, not a shortfall. Written down now so it is a
look-up later instead of a post-hoc rescue, which is the distinction §2.4 exists to enforce.

**Process note, since it is the transferable part.** The consultant's own instruction was
*sanity-check this yourself rather than take my word for it*, and the check paid — not by
overturning its claim, which was correct, but by finding the unstated half of a residual on
the way. "Verify one load-bearing claim before building on a report" is a `session-start`
rule aimed at incoming reports; this is the same rule applied to a *concurrent* session's
assurance, and it earned its keep twice today.

**No arm has run.** Artifact untouched.

### WGLL values 8–9 checked against every Track 2 criterion — A14 (2026-07-24)

The cold-read adjudicator widened `WHAT-GOOD-LOOKS-LIKE.md`'s trigger to **"before
designing anything that scores a path"** and added two values, with the asymmetry now stated
in both `CLAUDE.md` and the doc map: **no threshold may be read off WGLL, but a criterion
that contradicts a value in it is wrong.** That makes it a checkable rule, so it was checked
against all of C1–C7 rather than assumed compatible.

**Result: nothing contradicts. Two additions, both non-gating, and one item flagged for the
owner.**

**Value 8 (novelty is delivered *through* coherence, not traded against it) changes
nothing, and confirms two existing choices.** §1.5 already records AA and the overlap family
as *diagnostics only, never gating* — value 8 says those two were the **worst** predictors of
the owner's verdict, so the pre-registration had this right in advance. §6 item 1 already
concedes coherence has no offline metric and the listen decides. What value 8 does raise is
the standing of **F5 (confinement)** and the **repeated-interior report**: they are the only
offline proxies for Attack 2, which §3 already declines to close. It also supplies a pointer
worth obeying — Phase 1 log **§3.9's verbatim verdict notes are the only description of what
the owner means by coherent**; if a coherence metric ever looks tempting, start there rather
than inventing one.

**Value 9 (reducing famous artists is the live problem; eliminating them would be an
over-correction; the bypass is the mechanism meant to carry obscurity) reaches three
places.**

1. **C3 is value 9's own criterion, restated.** "The more bypasses, the more obscure the path
   becomes while staying coherent" *is* the within-arm depth gradient. Value 9 promotes C3
   from one criterion among four to the mechanism the owner is actually describing. No change
   to its threshold.
2. **C5's inspection gains the target it lacked** (A14b). It was "inspect every changed d0
   path, no numeric threshold." Value 9 says what to inspect *for*: does d0 fame still track
   the endpoints? A reshaped first path that keeps two superstars mostly-popular is expected;
   one that makes it obscure is the over-correction, and is a finding rather than a pass.
3. **A free diagnostic the pre-registration did not have** (A14a): per-arm, the relationship
   between endpoint fame and d0 interior fame. Costs nothing — every path and every fame
   value is already computed. **Weak, and labelled so:** the pair set is famous-heavy by
   design, so only The Shins → Wishbone Ash and Nirvana → CROOVE give any spread, and §6
   item 4 already records obscure→obscure as untested entirely.

**One apparent conflict, checked, and it dissolves — recorded because the check is the
point.** §2.4 **R3** permits the gradient requirement to move to Stage B if FL1/FL2 also fail
C3. First reading: that contradicts value 9, which names bypass-carried obscurity as the
mechanism. It does not — **Stage B *is* the bypass-mechanism experiment**, so relocating the
gradient there is value 9's own remedy, not a departure from it.

**What survives is narrower, and is the owner's to weigh, not this session's.** R3 also says
"C1/C2 remain binding for Stage A adoption regardless" — so Stage A could adopt an arm that
fails C3, before Stage B exists, shipping a router whose obscurity is **static rather than
bypass-carried**. Value 9 disfavours that. It is not a criterion contradicting a value, so
the "criterion is wrong" rule does not fire and nothing is being changed on this basis; and
the blind listen would very likely catch it. **Flagged, not actioned.**

**Method note.** This session's first pass through value 9 produced the R3 conflict as a
finding, and it was wrong. Writing out why before reporting it is what caught it — the same
"answer it yourself and write the answer down" step that dissolved the earlier escalation.
The near-miss is recorded because the finding would have been plausible, load-bearing, and
false.

**No arm has run.** Artifact untouched.

### The two tightened process rules applied to the scorer — A16, and a B5 clean check (2026-07-24)

The cold-read adjudicator (now retired) tightened three standing-layer rules and flagged two
as touching the in-flight scorer. Both applied here rather than filed.

**Factor-table rule → A16, and it caught a live defect.** The rule now requires a package
comparison to name the conclusion it is *barred* from supporting **and** to confirm no
read-of-results claims it — "a disclaimer nothing later reads is not a control." Applying it
to **FL1 vs P** (the one package comparison in the arms table) found that **R5 made the
barred claim**: "retain them if an FL arm is the winner — in which case the floor would then
be load-bearing." An FL arm "winning" is judged against P, so that sentence attributes a
*floor* effect to a comparison that changed the floor **and** everything W carries — exactly
the attribution §1.4 says comes only from the one-column chain. Corrected: the floor is
load-bearing only where **FL1 beats W** (not P) on a criterion W fails, characteristically
C3's gradient; an FL arm that beats only P while tying W means W's static knobs did the work
and the floor is deleted. **R3 was checked and is clean** — it already frames the FL arms as
the vs-W gradient remedy and A8 already warns their gradient is partly self-manufactured.
The rule earned its keep: the gap was a real one, present since the reads were first written,
and invisible until the rule forced the barred-conclusion to be named next to the read that
violated it.

**B5 config-figure rule → checked, does not bind.** B5 now requires an inline restatement of
a `config.py` clamp figure to cite adjudication §5.4 rather than be skipped. The scorer
restates none: its only constants are the pre-registered §2.2 thresholds (cited to §2.2 in
`score.py`), B_unk is read at runtime from the committed proxy `score.json`, and the cost
weights live in `mirror.py`, not here. Recorded in the scorer README rather than passed over
in silence — which is the behaviour the tightened B5 asks for.

**Displacement rule → noted, no action owed.** The third change makes a net-new standing-
layer addition the owner's call, not a session's. This session added nothing net-new to the
standing layer (`CLAUDE.md`, skill bodies): the `CLAUDE.md` purpose paragraph it wanted was
*rejected* for the WGLL-trigger route instead, and its `memory/` edits were status updates to
existing pointers, not growth. So the rule constrains future work rather than requiring a
retraction here.

**No arm has run.** Artifact untouched.

### Closeout at the scorer/P8b seam (2026-07-24)

Full-ritual seam closeout — the work touched the cost-function evaluation apparatus. This
session built the Stage A scorer, took the pre-registration A11 → A16, and committed two
retired consultant sessions' work under their attributions. Distillation of what is not
already in the per-task entries above:

**The arc, in one line.** Picked up at the fame-proxy/sweep seam (P4 just closed, A11
committed), ran closeout B1, resolved a merge race (PR #9/#10 landed while B1 ran), then
built the scorer — and building it forced five amendments, each caught before any arm ran.

**Decisions that reversed or corrected an earlier position:**
- **A12 reversed A11's "no change to §2.2".** A11 recorded that it changed nothing downstream;
  building the scorer showed it had inverted what C6 measures (unmatched went from *dropped*
  to *scored*, so coverage now marks the obscurity the sweep seeks). C6 stops gating.
- **A16 corrected R5**, which had attributed a floor effect to the FL1-vs-P *package*
  comparison — the barred conclusion the factor-table rule (tightened this session by the
  adjudicator) exists to catch. Routed through FL1-vs-W.
- **A15 corrected the resolver**, not the pre-registration: famous acts with common-word names
  (Justice, Rainbow, Ye) scored at the fame floor and poisoned P's own baseline medians. Fixed
  by recall fallback, proven byte-identical on the §5 validation sample.

**Defects found in the pre-registration itself (not the code):** R5's barred attribution
(A16); D7 never pre-registered as a uniform drop (A13); C6's gate premise dissolved by A11
(A12). All three were latent and invisible until the scorer forced each to be stated next to
what it governed — the recurring lesson that an apparatus makes its own spec's gaps legible.

**A near-miss recorded** (WGLL A14 check): the first pass produced an R3-vs-value-9 conflict
as a finding; it was false (Stage B *is* the bypass mechanism). Writing out why before
reporting caught it — the "answer it yourself and write it down" step.

**Gate outcomes:** no experimental gate reached — no arm has run. The mirror byte-identity
gate and A0-vs-P gate were passed in prior sessions and not re-run. **P8b (harness review) is
now due** and is the next unit's first step.

**Operational measurements with no other home:** the full stage-1 grid is ~40 s of compute
(0.3 s per arm-pair walk × 11 arms × 12 pairs), against §1.4's "on the order of an hour"
estimate — conservative by two orders of magnitude. The A11 notability guard flags **1 of 9**
on the known-unmatched sample (CROOVE only), so it does not drown the owner's one-glance check.

**B5 disposition:** the band-gap figures (owned by `builder/analysis/2026-07-24-track2-arm-scorer/`)
are restated at the A12 discharge point in this log and in the pre-registration; both are
point-of-decision restatements citing the owning dir, which the tightened B5 permits. No other
scorer figure is restated outside its owner.

**D6 standing-layer delta this session: 0 net-new by this session.** The branch's
`CLAUDE.md`/`.claude` changes (+16/+67) are the consultant and adjudicator sessions' work,
committed under their attributions. This session added nothing to the standing layer; its
`memory/` edits were status updates to existing pointers (memory total 354 lines). Per the
tightened D6, net-new standing-layer additions are the owner's call — none were made.

**No arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`.

### Closeout B1 — doc-auditor at the scorer seam (2026-07-24)

Ran as part of the seam closeout. **One MEDIUM, two LOW; no HIGH, and no escalation list —
every finding was adjudicable from the record.** A marked improvement on the day's earlier
B1 passes, consistent with the docs being written per-amendment this session rather than
reconstructed at closeout.

- **MEDIUM (fixed):** A14's amendment-table row ended "· A14 note below", a dangling
  forward-reference — no such note exists, and A14's row is self-contained (unlike A11/A12/
  A15, which genuinely needed "in full" sections). A defect of omission, exactly the class
  B1 exists for. Fixed by replacing the dead pointer with a precise §1.5 cross-reference and
  an explicit "no separate section: this row is self-contained."
- **LOW (fixed):** the active `2026-07-24-track2-arm-scorer/` harness was reachable from
  `docs/` only at one hop (via the handoff), not catalogued. Added a note to
  `builder/analysis/README.md` marking it as the one **live, non-frozen** directory — which
  also corrects that file's opening "everything here is frozen, not a tool" claim, now that
  an exception exists.
- **LOW (no action, recorded):** the superseded fame-proxy handoff's P6 strikethrough
  formatting (cosmetic, on an audit-retained superseded doc) and the "SUPERSEDED"/"Supersedes"
  phrasing pair in the doc map (unambiguous on read). Polishing a superseded document is not
  worth the churn; the auditor marked both optional.

**Regression check passed:** the previous B1's fixes (P6 discharged in three docs, amendment
banner count) remain in place. Cold-start navigation test passed.

**No arm has run.**

### P8b dispatched — the harness review, on branch `track2-arms` (2026-07-24)

Fresh session, picked up at the scorer/P8b seam. `session-start` ran clean: tree on `main` at
`0cd6c70` (PR #11 merged, `track2-sweep` deleted), no concurrent session, artifact identity
re-verified as `4cb84ef9…` against the handoff, test queue holding nothing stale. Working
branch **`track2-arms`**, off `main`, pushed at the first commit.

**P8b is the gate, and it was dispatched rather than deferred.** §7 lists the prerequisites as
blocking all arms, and P8b flipped from "not yet due" to due the moment the scorer was
committed. The builder session is barred from self-reviewing it, so this is the first session
able to discharge it.

**The brief was bounded in two ways that matter, and both are recorded because they are
protocol, not preference:**

- **The reviewer may run arm `P` only.** Any factorial or attachment arm run before P8b is
  discharged would break the pre-registration gate — and would additionally make the reviewer
  blind-listen-ineligible under the eligibility line. Static reading plus arithmetic over the
  artifact is the intended method; the P8 review's highest-value findings (D1–D3) were exactly
  that, and were arithmetic showing whole arms provably could not move.
- **Derivation, not judgement.** The remit excludes whether the experiment is worth running and
  which candidate to adopt. Those are the owner's, per CLAUDE.md's decision table.

**Five items named for the reviewer**, four of them pre-existing open findings rather than new
worries: C2's near-non-discrimination on this pair set (production itself scores the threshold
minimum, so C1/C3 carry the load); **D4's residual** — §9's still-open table says the d15/d20
notability guard remains to be wired into the **C2 scoring path**, and the scorer README
describes it as living in `fame.py`, which is a discrepancy the review is asked to settle;
A13's uniform infeasible-cell drop actually defeating arm-correlated missingness; arms provably
incapable of moving; and **A8's floor column verified off in code**, since a dormant `w_floor`
switching itself on inside the diving arms is the confound this whole design was restructured
around.

**No arm has run.** Artifact untouched.

### Nameless artists — the owner's product argument, and a tripwire ahead of the remediation (2026-07-24)

**Raised by the owner** off P8b's F8, which had noted 33 blank-named nodes only as a hazard to
*fame keying*. His argument was the product one F8 did not make: a nameless artist cannot be
entered as an endpoint, cannot yield a clip, and would be a poor card to show in a discovery
tool regardless. **He is right on all three, and the third is worse than stated.**

**Confirmed in code, not inferred:**

- **Unsearchable by construction** — `search.py` returns `[]` for an empty query, and
  `"".startswith(q)` is false for every non-empty query. No keystroke can surface one.
- **Clipless** — `clips.py:89` passes the name itself as the provider query string.
- **Not inert.** Degree runs to 28 and `pop_raw` to 0.5055 — mid-to-high. These sit *inside*
  the similarity structure as ordinary routing waypoints, so the one way they can reach a user
  is the worst one: a blank interior card the bypass buttons still operate on.

**Cause — a default, not a parse failure.** `pipeline.py:245` reads
`name=identities.get(mbid, ("", ""))[0]`, and a name is only ever observed when the artist
appears as *someone else's* neighbour (`sources/listenbrainz.py`: no per-artist metadata
endpoint exists), with `row.get(FIELD_NAME) or ""` accepting a missing one silently. Nothing
downstream objected — the same gap `acceptance.py` was created to close, one instance on.

**Blast radius measured: 36 of 74,193 (0.049 %).** Dropping the 33 and re-pruning to the
largest component loses 3 further nodes, singletons that hung off a blank one.

**Scope closed, and one adjacent class deliberately excluded.** All 33 are truly empty — no
whitespace-only variants, and none of MusicBrainz's placeholder strings (`[unknown]`,
`Various Artists`, `[no artist]`) are present at all. **111 nodes whose names are only digits
or punctuation are NOT in this class and were left alone:** `69` is a Carl Craig alias,
`7038634357` a real project name. They are searchable and clip-resolvable, so the argument does
not reach them, and a tidy-looking regex here would eat real artists.

**Sequencing — the fix is right, rebuilding now is not.** A new artifact invalidates the mirror
byte-identity verification, the A0 gate's 252 cells, production's baseline fame medians (what
every arm is scored against), the fame cache seeded with P's 156 interiors, and P8b's own
measurements — Track 2 restarts from before the A0 gate. Against that: 0.049 % of nodes, in a
**relative** comparison between arms on one fixed graph. A change that small flipping a ranking
would mean the ranking was noise. **Rebuild is gated to Track 2 adoption**, when one happens
anyway if a candidate wins.

**The remediation is an OPEN OWNER DECISION — drop, or backfill names from a new source.**
Backfill could recover up to 36 real artists but needs a data source the crawler does not have.
Recommended: drop, at 0.049 %. **The owner deferred it 2026-07-24 after confirming it does not
block progress** — and it does not, because the tripwire and the remediation separate.

**What landed instead: the tripwire, in `acceptance.py`.** An unconditional zero-blank-names
check — no criterion, because zero is the only defensible count, and it therefore fires against
the scaled-down test set too. It quotes the **mbid**, since a blank name cannot identify itself
in an error message. Three tests added; full builder suite 115 passed.

**This deliberately rejects a production rebuild until the remediation lands.** That is the
forcing function, and it is safe because `check_acceptance` runs at the emission point
(`cli.py:118`) and **not** inside `build_from_archive` — so no test and nothing in the sweep
path touches it, and no production build is due before adoption. Success condition recorded at
the check itself: owner picks, remediation lands, check passes on rebuild. **Weakening the check
to unblock a build is the one wrong response.**

**Guarding the gap in the sweep meanwhile,** since today's artifact still contains all 33: fame
keyed by **mbid** rather than name (P8b F8's fix, owed regardless), and **a blank-named interior
must not count as obscurity reach** — it is an artifact defect, not a discovery success, and
crediting one would let an arm bank a win on a card that renders empty.

**A blank card is user-visible today** (33 of 74,193, paths 4–6 hops, so rare and never yet
reported). Queued for the test queue rather than hotfixed: changing the router mid-experiment
costs more than the rare empty card does.

**No arm has run.** Artifact untouched.

### P8b discharged: four code fixes, three amendments, and one correction to my own reasoning (2026-07-24)

**P8b's verdict:** fit to run stage 1 as-is; **not** fit to run stage 2 (no executable path for
the attachment arms). Fourteen findings, two HIGH. The mirror was re-verified byte-identical on
all 212 cells, so the router is sound. Review and its measurements:
`builder/analysis/2026-07-24-track2-p8b-harness-review/` (owns its figures).

**Three of its claims were checked against the code before being acted on**, per the
verify-one-claim rule, and all three held: `score.py` never read `potentially_notable`;
`stage2()` had no caller and `run_arms.py` asserted arm names against `STAGE1` only; 33
blank-named nodes, reproduced exactly.

**Code fixes (commits `87101b3`, `d743c1c`).** F8 fame keyed by mbid, not name — resolution
stays name-based since Wikipedia can only be queried by name, and the cache stays name-keyed
since two nodes with one name share an article. F2 the A11 notability guard reaches C2's
scoring path, narrowed to the interiors a pass rests on. F3 stage 2 runnable, with A13's
uniform drop spanning the stage boundary. F9 the isolating one-column contrasts computed
rather than declared.

**Regression evidence:** production re-walked and re-scored with **every criterion value
identical** — C1 0.000, C2 4/8, C3 0.164, C4 5.38, coverage 96.4 %, W still A7. A correctness
fix that was not supposed to move the answer did not move it.

**Two defects found in my own work, both worth recording because neither was in P8b:**

1. **F9's first cut mis-attributed the contrasts.** Package-ness is a property of the *pair*,
   not the arm: A6/A7's declared baselines are A2/A4 (one column away), while the packages are
   A6/A7 **vs A0**. Keying off the arm name stamped the clean contrasts as unattributable.
   Both blocks are now computed, so A7 appears twice with different figures and different
   warnings. The irony is exact: `PACKAGE_CONTRASTS` had sat unread since the harness was
   written, which made it the disclaimer-nothing-reads that A16's rule exists to catch — one
   level below where A16 caught it.
2. **The F8 guard was under-implemented, and directionally so** — caught by a consulting pass,
   not by me. F8's success condition asks for an assertion *failing loud*; I shipped a
   per-criterion **node** exclusion, and only in C2, leaving blank interiors in C1's and C3's
   medians at F = 0. See the A18 entry below: a node-level exclusion improves whichever arm
   produced the blank, invisibly, and only the treatment arms have any.

**Three amendments, all before any arm ran — A17, A18, A19.**

**A17** records P8b's six *reading* bounds. Two are worth restating here because they change
what a result licenses: **C2 is a one-sided regression guard, not a discriminator** (P scores
exactly its 4/8 minimum, so any arm meeting C1 meets C2 by construction) — so §3's Attack 1 is
**re-attributed to C1's magnitude**, and its closure now rests on one criterion rather than
two. And **X does not bound what §1.4 claims**: its jump term is symmetric, so zeroing it
unprices climbing as well as diving, and X measures as *more* pop-ascending one hop out than
the arm it bounds. R0's null therefore may not be read as "the family is exhausted" unless X's
fame profile turns out lowest — a free falsifier once stage 1 runs.

**The one owner decision in this batch was put to him and declined.** P8b offered either
reporting C2 honestly as a regression guard (free, methodology, mine) or **amending C2's
threshold now that production's baseline is known** (post-baseline threshold change, his). I
took the free option and left the threshold as written, because loosening a threshold after
seeing the baseline is the move pre-registration exists to prevent. The concession is recorded
rather than buried.

**A18 replaces the justification for deferring the rebuild, and this is the substantive
correction of the day.** The nameless-artists entry above defended the deferral with "0.049 %
of nodes, in a relative comparison between arms". **That is the reasoning for a random
0.049 % and it is wrong here.** The measurements were already in P8b when I wrote it: blank
names are **2.7× concentrated in the bottom popularity decile** — the stratum the diving arms
aim at — they resolve to **F = 0** (maximal reach, satisfying C2 by construction and dragging
C1/C3 toward passing), **P contains zero blank interiors**, and the A11 notability guard
structurally cannot flag one. So it is a **bias with a known sign, absent from the control and
present preferentially in the arms under test** — the "held constant, and why each is genuinely
constant under the intervention" failure, the same shape as the `w_floor` catch that
restructured this design.

**The deferral is still correct; it is correct for a different reason.** It is safe *because
the guards neutralise the exposure*, not because the exposure is small — remove a guard and it
becomes unsafe immediately. Recorded as a row in §1.2's constants table whose "why" is a
warning rather than a reason, which is the honest place for a term that is held constant by a
guard rather than by nature.

**The guard is now cell-level:** a scored cell containing a blank interior is dropped from
**every arm or from none** (A13's rule, second cause), with a fail-loud default and the uniform
drop as the **pre-registered** response — fixed before stage 1, not chosen after seeing which
arm trips it. `verify_c2_guards.py` asserts the two properties the design turns on: the drop
removes the cell from the **control** as well as the treatment, and the bias it replaces points
toward passing.

**A19 gates the blind listen** on zero blank-named interiors, with its response pre-registered:
substitute from §2.3's ordered reserve applied to **both** arms; accept-and-record if the
reserve is exhausted; **rebuild explicitly rejected**, because it changes the substrate and the
listen would stop testing what the offline pass selected. A blank card has no name *and* no
clip and would land preferentially on the candidate — a directional confound on the one
measurement that cannot cheaply be re-run, and §6 already spends its "one burned listen" on
Attack 2.

**D4 fully discharged** (its C2-scoring-path remnant, by F2's fix). **A second exposure D4
never named** — a blank name, which the notability flag cannot catch — is closed separately by
A18.

**The drop-vs-backfill deferral now has a first step and a success condition**, recorded in the
pre-registration rather than executed: scan the archive for those 33 MBIDs before deciding.
**Code reading already excludes the interesting reading** — `harvest_identities` iterates every
archived response's rows, `_rows` filters nothing, and the rule is *prefer the first non-empty
name*, so nothing in the build discards an available name. That downgrades the scan from
decisive to confirmatory, and I said so rather than leaving the more attractive possibility
open. It retains value as a falsifier: if those MBIDs never appear as rows at all, that
contradicts their degree-28 presence in a mutual-kNN graph and something else is wrong. Two
alternatives recorded as rejected while the reasoning is fresh — a placeholder name (makes them
*searchable*, widening the blast radius) and filtering at API load (breaks the APG1 contract and
the largest-connected-component guarantee that makes "no path" attributable to user exclusions
alone).

**No arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`.

### `jesus2099` is still a node — Task 11 is complete for placeholders only (2026-07-24)

**Record-only entry from a consulting session; no batch work.** One item in it was a live open
loop and is now closed by measurement.

**CONFIRMED, and it was worth the one query.** `jesus2099` — a MusicBrainz **editor account**,
and the motivating case named by the 2026-07-21 architecture review — **is still a node in the
adopted artifact**: index 54722, mbid `bcb4411c-346b-4450-b660-39a9faad74c0`, **degree 31**,
`pop_raw` 0.3846 (mid-to-high), disambiguation `'shamo'`.

**Why the shipped filter cannot catch it.** `is_special_purpose` (`pipeline.py:45`) matches a
regex against the **disambiguation** field only, and is documented as "MusicBrainz placeholder
entities". `'shamo'` carries no such marker, so no amount of tuning that predicate reaches an
editor account — the field simply does not hold the information.

**So the record needs correcting where it reads as closed.** Phase 2 Task 11 shipped an entity
filter and the review's prescription was "entity filter first"; both are satisfied **for
placeholders**. The artifact contains **zero** nodes with a `special purpose` disambiguation, so
the filter demonstrably worked on its own class — P8b's finding that the placeholders are gone,
confirmed here independently. The editor-account case was never covered and was not re-checked
after Task 11. **Task 11 is complete for placeholders only.**

**Not filed as a defect in the filter.** It is a coverage gap with no machine-readable
definition available: nothing in the archive distinguishes an editor account from an artist.
That is what makes the next item the right shape.

### Three recorded lines on entity curation — where the blank-name drop belongs (2026-07-24)

**Record-only. Not this batch; the first two are not due until the rebuild seam.**

**1. The blank-name drop belongs INSIDE the existing entity filter, not beside it.**
`filter_special_purpose` / `is_special_purpose` already own this seam in `build_from_archive`,
with a config toggle and a two-directional test pattern. Three predicates, one stage:
MusicBrainz placeholders (shipped), **empty names** (F8, pending the owner's drop-or-backfill
decision), and a **curated MBID denylist** for the residue with no machine-readable definition —
editor accounts, mis-ingested non-artists. **This is not new policy:** the Phase 2 design
already names "an interior node whose disambiguation **or absent-name** marks it as a
non-musical entity" as a bad-path signal, and `badpath.py` already emits `non-musical interior
entity: unnamed node {node}`. So dropping the 33 **completes** the entity filter rather than
adding a mechanism — and `jesus2099` is the first denylist entry, ready-made.

**Denylist hygiene, if one lands:** data file not code; reason + date per entry; a missing entry
**reports rather than fails** (an artifact must not become unbuildable because an MBID vanished
upstream); and growth past a few dozen means some subset actually had a definition and wants a
predicate instead.

**2. There is no discovery mechanism, and that is the real gap.** Both known instances were
found **by accident** — `jesus2099` from reading a tuned path, the 33 blanks from a harness
review. Curation is therefore bounded by what the owner happens to trip over. The missing piece
is a periodic report surfacing suspicious nodes for one human skim.

**Measured caveat on that report, because the obvious heuristic is noisy.** A username-shaped
scan (letters then 2+ trailing digits, no spaces) returns **152 nodes**, and the top of the list
is mostly **real artists** — `Sad13` (Sadie Dupuis), `Soccer96`, `MNL48` ("Filipino girl
group"), `Skech185` ("US emcee from Chicago"). So this must be a **report for human skim, never
an automated filter**; a regex here would delete real artists, the same trap as the 111
digit/punctuation-only names deliberately left alone earlier today.

**3. Offensive artist names are the owner's product decision, with a gate-scoped success
condition.** No technically correct answer exists. **Success condition: answered explicitly
before Gate 2 → 3, even if the answer is "not yet."** At personal use a junk or offensive name
is a curiosity; at public launch it is a different risk category — and the app's premise routes
users through exactly the obscure stratum where upstream curation is weakest.

### Costing the eventual rebuild — the spec's warning holds, its stated mechanism does not (2026-07-24)

The consultant flagged the Phase 2 spec's warning that removing nodes "perturbs every mass
slightly and therefore every score" — written for 7 nodes, against 33 — and asked whether it
still applies given scoring changes since. **Checked in code: the conclusion holds and is
strengthened, but the mechanism named is inoperative.**

- **The mass channel is DEAD in the adopted configuration.** Exclusion does happen before mass
  is computed (`pipeline.py:137`, and excluded nodes are filtered out of neighbour lists before
  the sum), so the spec described the ordering correctly. But mass reaches a score only through
  `damped_strength`'s `strength -= damping * (log mass_a + log mass_b)`, and the adopted
  `similarity_damping` is **0.0** — damping was tested at 0.25/0.5/0.75 and rejected. A zero
  coefficient means **mass cannot move any score.** The warning predates that rejection.
- **The live channel is the p99 rescale, which was not named.** `similarity_rescale` is
  `"p99_log_clip"`, and `rescale_scores` takes `scale = np.percentile(raw, 99)` over the
  **global** flattened score array. Removing edges moves that percentile, which rescales **every
  edge score in the graph**. The graph-wide-perturbation conclusion therefore survives — by a
  different route, and one sized by how much the removed edges shift the 99th percentile rather
  than by what mass they carried.
- **A third channel, also unnamed: popularity.** `score_weighted_indegree` loses the removed
  nodes' out-edge contributions, so their **neighbours'** `pop_raw` shifts — and `pop_raw` feeds
  the cost function directly (`w_jump·|Δpop_raw|`, the floor) and the percentile array the
  mirror builds at harness start.

**Scale of the exposure, measured:** the 33 blanks touch **448 of 898,006 directed edges
(0.0499 %)**; adding `jesus2099` makes it **510 (0.0568 %)**. Small, but graph-wide by
construction rather than confined to the removed nodes.

**Which strengthens gating the rebuild to adoption, exactly as the consultant argued.** A
rebuild is not "remove 36 nodes and re-verify"; it produces a new score distribution and a new
popularity array, so every figure measured against `4cb84ef9…` — the A0 gate's 252 cells, P's
baseline medians, the fame cache's node identities — describes the old artifact. **Deferred
measurement, due at the rebuild seam:** the actual p99 shift and the resulting score-delta
distribution. Cheap once a rebuild is happening anyway, and meaningless before.

**No arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`.

### The discovery-report signals must be external to the graph — and the naive clip test fails on `jesus2099` (2026-07-24)

**Record-only, from a consulting pass; amends the discovery-report line recorded above.
Not for the current batch.**

**The amendment is accepted, and the reasoning is the durable part.** A username-shaped scan is
**retired** — by my own measurement, which returned 152 nodes whose visible top were real
artists. Three results now say one thing: blank-named nodes at degree up to 28,
`jesus2099` at degree 31 and `pop_raw` 0.3846, and 111 digit-only names that are mostly real.

**The common cause, and it is the reason no predicate will fix this.** A non-artist entity that
accumulates genuine listener co-occurrence is **graph-structurally indistinguishable** from an
obscure real artist. Popularity here is score-weighted in-degree — it measures "people played
this alongside other things" — which an editor account with a following earns honestly. **The
distinguishing information is not in the graph; it is a fact about the outside world.** Any
report built on degree, popularity, connectivity or name shape will keep returning Sadie Dupuis.

**So the signals must be external, and Track 2 has already built all of them:** no clip
resolves; no Wikipedia presence (the adopted fame proxy); non-trivial degree, i.e. actually
routable. Intersect the three, scope to nodes that can appear as a **path interior** (the only
ones a user can see, already recorded by the sweep, already seeded into the fame cache), and it
is largely a join over sweep byproducts rather than new work. Still a report for human skim,
**never an automated filter** — the 152-node result raises the stakes on that, it does not lower
them.

**Tested before recording, and the naive form of the key signal FAILS.** The proposal predicted
`jesus2099` "should return nothing on both" providers. Measured against the live endpoints:

| Query | Deezer top artist | iTunes top artist | "no clip" fires? |
|---|---|---|---|
| **`jesus2099`** | **`Mr.UNSTABLE`** | *(none)* | **NO — Deezer returns a match** |
| `saib.` | `saib.` | `Saib` | no (correct — real) |
| `Purrple Cat` | `Purrple Cat` | `Bcalm & Purrple Cat` | no |
| `sleepy fish` | `Sleepy Fish` | `Afternoon Bike Ride & Sleepy Fish` | no |
| `Leavv` · `Miami Nights 1984` · `Lazerhawk` · `Stonebank` · `Toonorth` | own name | own name | no |
| `idealism` | `SwuM` *(wrong)* | `Idealism` | no — **saved by the fallback** |

**Two things follow, and the first would have sunk the report silently.**

1. **"No clip resolves" must be "no provider returns a NAME-MATCHING artist."** `jesus2099`
   resolves a clip — for `Mr.UNSTABLE`. That is the known **C1 wrong-artist clip defect**
   acting as camouflage: the naive test would have passed the one entity the report exists to
   catch. The fix is free — the fame proxy already owns a name-matching rule (`name_matches`,
   plus P5's NFKC + punctuation folding), so the report reuses it rather than inventing one.
2. **Wikipedia-absence is NOT the discriminating signal for this population, and the clip
   signal carries all the weight.** The nine S1 anchor artists are owner-confirmed **real**,
   genuinely obscure, and **8 of 9 are Wikipedia-absent** — so that signal alone flags every
   one of them. They are excluded only by resolving a clip. Which means the intersection works
   *because* of the clip test, and getting the clip test right is load-bearing rather than
   incidental.

**Controls chosen deliberately, and this is why the test was worth running:** the S1 nine are
the hardest available case — real, obscure, and Wikipedia-absent, i.e. they trip two of the
three proposed signals. A design that survives them survives the population it will actually
be run over.

### Rebuild seam: the p99 shift goes FIRST, because it can come out exactly zero (2026-07-24)

**Record-only ordering note; accepted as stated.** The measurement is computable now without a
rebuild — drop the 510 affected edges from the raw score array and re-take
`np.percentile(raw, 99)` — and deferring it is right, since it changes no decision before
adoption.

**But it goes first at the seam, not alongside the rest, because it is the only one of the
three channels that can be exactly zero.** The 99th percentile over a discrete distribution
with roughly 5,300 distinct values need not move when 0.057 % of edges leave.

- **If it does not move:** the score array is unchanged and the blast radius collapses to the
  popularity array plus the removed nodes. A substantial amount of re-verification becomes
  **reusable rather than redone**.
- **If it moves:** every edge is rescaled and everything downstream needs redoing anyway.

Either way it **sizes all the remaining work**, so it precedes that work rather than
accompanying it. Recorded as the first step of the rebuild seam, alongside the archive scan for
the 33 MBIDs (which the drop-vs-backfill decision needs, and which is confirmatory rather than
decisive — see the pre-registration's deferral entry).

**No arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`.

### STAGE 1 RUN — result is R0, a full null, and A17(c)'s falsifier FIRED (2026-07-24)

**The first experimental arms of Track 2 have run.** Artifact `4cb84ef9…b061dc8`, unchanged.
11 arms × 12 pairs × 21 depths, 158 s. **Zero guard-infeasible cells**, so A13's uniform-drop
path is still unexercised (P8b listed that as undeterminable without a run; it remains so).
Fame: 235/239 matched (98.3 %); **zero blank-named interiors**, so A18's cell guard did not
fire and the `--blank-cells` default never triggered. Figures owned by
`builder/analysis/2026-07-24-track2-arm-scorer/scores.json`.

**Outcome: R0 — full null.** C1's threshold is mean ΔF ≤ −1.0 with ≥ 75 % of cells negative.
The best arm reaches **−0.053 at 54 %**. That is not a near miss; it is roughly **one twentieth**
of the pre-registered effect, and no arm exceeds −0.053.

**Worse than null on three criteria — and C2 caught it, which is A17(a) vindicated within
hours.** Production reaches below B_unk in 4 of 8 pairs; **every arm that moves paths reaches
1 or 2 of 8**. A17(a) demoted C2 from discriminator to one-sided regression guard on the
grounds that any arm passing C1 would pass C2 by construction — and its remaining job, catching
a candidate that goes *backwards*, is exactly the job it did. C3's gradient also degrades
(P 0.164 → arms 0.021–0.090) and C4's payload fails on the percentile arms (5.38 → 3.58
interiors, against a 4.38 floor): **the arms that move most make paths shorter and less
obscure.**

**A17(c)'s falsifier fired, and this is the most consequential line in the run.** X is **not**
the lowest fame profile: mean pooled interior fame **A3 5.861 < A0 5.880 = P 5.880 < … < X
5.932**. Production itself is more obscure than the corner arm built to bound the family. So
per A17(c), **R0 licenses only "these fifteen configurations do not move it" and does NOT
license "the repricing family is exhausted."** Had P8b not measured X's symmetric jump term
three days before the arms ran, this null would have been written up as a much stronger claim
than the data supports — the amendment was committed before any arm and earned its keep
immediately.

**What R0 licenses, quoted from §2.4 as pre-registered:** firing spec §5's recorded triggers —
the p99 ceiling-rescale arm (builder) and/or revisiting the deferred `cap_strategy`, each with
its own pre-registration. **Does NOT license:** re-litigating the `capfix` adoption, mutual
k-NN, or anything in log §4/§4.1; shipping any arm anyway; or quietly weakening the thresholds.

**F6 confirmed exactly.** A0 is **identical to P on every scored statistic** (C1 0.000, C2 4/8,
C3 0.164, C4 5.38) and differs in 1 of 72 analysis cells, at d0 — a depth no gating criterion
reads. P8b F6 predicted precisely this: P's raw floor is dead at every depth C1 and C2 score,
so A0's C1 row measures exclusion-history carryover, not a floor contrast.

**Structural findings from the paths themselves, before fame entered:** no two arms produce
identical path sets (so no arm is degenerate), and the pairwise cell-difference matrix shows
**the currency swap is the dominant factor** — P/A0/A3 cluster within 4 cells of each other,
A2/A6 within 7, and the five percentile arms within 3–18 of each other but 48–58 from P. The
isolating one-column contrasts (P8b F9's machinery, first real use) put currency alone at
−0.033 and every subsequent knob at −0.008 to −0.012, i.e. the factorial's later columns add
almost nothing on top of the currency change.

**A sign visible before scoring, worth recording as the shape of the null:** all **76** newly
visited artists resolved a Wikipedia article, with F between 4.6 and 6.6. The arms did not
route anywhere obscure; they rearranged famous artists. Every arm's pooled median interior fame
sits in **5.86–5.97** against a B_unk of **5.379** — the whole grid lives above the owner's
"would not know them" band, and the total spread across all eleven arms is ~0.1 fame units.

**No threshold was touched, and none will be.** Stage 2 has not run; R1's fallback selects
**W = A7** (no cell moved C1 in the right direction), which is the fallback firing as designed
rather than a selection.
