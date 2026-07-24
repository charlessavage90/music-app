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
| **Named-entity check as standing practice** — showing the owner the *names* a perceptual metric produces, not just the number | Pre-registration §5 already implements a stronger version for the fame proxy: 33 artists labelled into three buckets **without seeing fan counts**, scored for rank agreement and catastrophic inversions. A parallel practice invented now would duplicate it. | **After §5 runs.** Generalise its protocol into `closeout` (as an adoption-time step) and into `TEST-QUEUE.md`'s format, with its measured performance attached. |
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
