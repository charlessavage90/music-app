# `MSW-` map switch — execution log

**Role: ACTIVE, retained.** Reasoning and decisions per task, appended as the work
happens rather than reconstructed at closeout. Status lives in
[`NEXT.md`](NEXT.md); this document owns no status and no figures — the
artifact's figures live in its manifest sidecar, the `ULC-`/`GBL-`/`CAU-` figures in
their own findings notes, cited and never restated.

**Operational document:**
[`plans/2026-08-05-msw-package-adoption.md`](plans/2026-08-05-msw-package-adoption.md).

---

## §0 The authority this work runs on, recorded before anything was built

This adoption is an **owner override of the standing `GBL-` null**. The null's
pre-registered consequence was *"production stands and Option A closes without
adoption"*, margin 3 against a bar of 5.

The owner took the override knowingly on 2026-08-05, having been shown the null and
its margin explicitly, on this reasoning: `CAU-` found the arm's coherence meets his
own bar (by one card); the instrument that produced the null was compromised in the
direction that penalised this arm specifically (a 30-second clip cannot support a
coherence judgement about an unfamiliar artist, and that failure activates only in the
arm delivering unfamiliar artists); the `ULF-` filter fix addresses the largest
identified defect underneath it; and Gate 1's blast radius is himself.

**Neither `GBL-` nor `CAU-` licensed this.** `CAU-` §0 bars comparison with today's app
on any strength, and `GBL-` §5's run-once rule still binds that verdict. The authority
is the owner's and is recorded as his, which is the only thing that must not be
misremembered later.

**A session correction worth keeping:** this session first recommended shipping the
data-only variant (`ULC-A2`) as the cheaper first step. That was wrong and was
withdrawn — `ULC-A2` has never been listened to or audited by anyone, while the full
package is what `GBL-` heard and `CAU-` audited. Shipping the cheaper thing would have
shipped the *unevaluated* thing.

## §1 Scope correction found before any code was written

`ULC-` results §4.1 scoped the package as "two implementation jobs, not a config flip".
Verified against the repo, it is **four**, and the owner was told before he confirmed:

1. the trimmed-union connection rule (`cap_strategy` raised on anything but
   `mutual_knn`),
2. the gentle ramp (no ramp knob anywhere in `api/src`),
3. **`fame_lb_raw` in the artifact** — nothing matching `fame_lb*` existed in
   `builder/src` or `api/src`, and the APG1 metadata blob carried only mbids, names,
   disambiguations, popularity and optionally `deezer_ids`,
4. **fame data for the new population** — the only values in existence came from a
   one-off analysis fetch (`fi_union_snapshot.json`), gitignored and on one machine.

Job 3 is easier than it sounds (`artifact.py` documents the additive-key pattern from
`deezer_ids`); job 4 is harder (`build` is contractually offline, so fame needs a
crawl-shaped stage of its own).

## §2 Named deviations from the listened arm

Recorded in the plan's own section and repeated at each site in code. In brief: the
un-listenable filter is ON (the listened builds predate it); the percentile frame is the
**served artifact's own** non-null values rather than the retired artifact's fixed
experimental ruler; and the harness's "absent from snapshot" null class cannot arise in
a shipped artifact, because Task 4 refuses to build one.

---

## Task 1 — `trimmed_union_cap` ported into shipped builder

Ported from the frozen `cb_build_variants.cap_trimmed_union` (`weakest_first` only;
`banded_quota` lost Track B's selection and is not ported). An equivalence test against
the frozen implementation pins the port, so a transcription slip fails loudly.

**The equivalence test alone was not sufficient, and this is the entry worth keeping.**
Suspecting a green from a new instrument, the tie-break was perturbed (`_desc(v)` → `v`,
which reverses which MBID survives a strength tie) and **all four tests stayed green**.
Random float strengths never tie, so the deletion tie-break was entirely uncovered — by
a test whose whole purpose was to pin the rule. Two tie-specific tests now cover it, and
both go red under that same perturbation; the frozen implementation fails identically,
which is what confirms the ported behaviour matches its real behaviour rather than my
reading of it.

## Task 2 — `cap_strategy="trimmed_union"` wired through the pipeline seam

`PERMITTED_CAP_STRATEGIES` replaces the single-value check. The deleted
`pre_symmetrise` is deliberately *absent* from that tuple rather than listed-and-
rejected, so adding a strategy can never reinstate it by accident; a test asserts it
still raises by name.

**`MSW-G1` passed.** A default (`mutual_knn`) build over a fixed synthetic archive is
byte-identical across the seam change — 60 artists, 910 edges,
`sha256=0f6f85a6a6153776006f0fd4cb50041c8a15255db5d2b997895c9aa65b4c75fe` before and
after. Deliberately not committed as a golden test: a pinned sha in the suite would
break on every unrelated legitimate change to the build. The before/after pair is the
evidence and it lives here. Re-checked after Task 3's prefix extraction — unchanged.

**`test_pipeline_mirrors.py` fired and earned its place.** The two new fields are inert
today, but the guard surfaced that **Task 11's default flip is the build-affecting
event**: `grt_score.py`, `calibrate.py` and `cre_build.py` each construct
`BuilderConfig` without setting `cap_strategy`, so all three would silently change what
they build. `cre_build.py` is the sharp case — its `gate()` compares its mirror against
a live `build_from_archive` for byte-identity, so an unpinned flip would have it
comparing two *different cap rules* and reporting a mirror divergence, which is the
wrong diagnosis for the right symptom. The plan gained Task 11 Step 0 to pin all three;
reasoning is recorded at the site in `RECORDED_FIELDS`.

## Task 3 — the `fame` fetch stage

`builder/src/artistpath_builder/fame.py` plus an `artistpath-build fame` subcommand.
Network to archive, resumable by key presence, seedable from the frozen `FAM-` snapshot.
`build` reads records offline, so the offline-build rule survives the addition of a
network-sourced quantity.

Decisions worth recording:

- **A stored null occupies its key.** ListenBrainz returns not-found artists as explicit
  nulls, so a null is a measured absence, not a gap. Had resume treated it as unfetched,
  every null would be re-fetched on every run forever and the stage would never
  terminate against a population with real absences in it.
- **Absent-from-response is recorded as null too.** Batches above `MAX_PER_REQUEST` are
  silently *truncated* rather than rejected, so a short response must not leave a hole
  the next run reads as "never asked".
- **The seed verifies its sha before writing anything.** The snapshot's sha *is* the
  instrument's identity (`FAM-AM1`.7); an unverified file would put values of unknown
  provenance into an artifact that routes on them. `--seed` without `--seed-sha` is
  refused by the CLI rather than defaulted.
- **Existing records win over a seed**, so the archive's contents do not depend on the
  order the operator happened to run things in.
- **`similar_prefix` / `archive_artists` were extracted rather than copied.** The fame
  stage must enumerate exactly the population `build` will read; a second copy of the
  `RC-H3` algorithm-scoping rule is precisely the divergence class
  `test_pipeline_mirrors.py` exists to catch. `MSW-G1` re-verified after the extraction.

## Task 4 — `build` reads fame offline and refuses an uncovered population

`Graph.fame_lb_raw`, threaded through `build_graph` as a **dict keyed by mbid**, not a
pre-ordered list: node ids are assigned inside `build_graph`, so a caller building the
list itself would be re-deriving that `sorted(...)` and could silently disagree with it.
The alignment is the whole contract — the api indexes this list by node id, and a
mis-ordered list would price every artist as someone else with nothing downstream able
to detect it. A test pins the alignment per node rather than only the length.

`load_fame` is asked for `keep` (the pruned node set), not the whole archive, so an
artist the largest-component step discarded cannot block a build by lacking a value
nothing would have read.

**Deviation from the plan, taken deliberately: `require_fame` defaults to `False`, not
`True`.** Until Task 11 the shipped router does not read fame, so a fame-less build is
genuinely valid and defaulting to `True` would assert a requirement that is not yet
true — and would break every existing synthetic-archive test for a property that does
not yet matter. It is treated exactly as `cap_strategy` is in this same plan: added
inert, flipped in the commit where it becomes true. Two independent guards cover the
gap in the meantime — Task 9's real build passes `require_fame=True` explicitly, and the
api refuses at boot if the ramp is live over a fameless artifact.

One detail that would be easy to get wrong: `build_graph` tests `fame_lb_raw is not
None` rather than truthiness, because a fame dict whose values are **all** None is a
legitimate measurement (nobody in this population has listeners) and must not be
discarded as "empty".

**The mirror guard fired a second time and the answer differed from Task 2's.** Both
Task 2 fields were inert *and stay inert at the flip* for the mirrors themselves; but
`require_fame=True` makes every era-pinned caller **refuse to build**, because none of
their archives has ever had the `fame` stage run against it. That is a harder failure
than a silent output change, and it is recorded in `RECORDED_FIELDS` and folded into
Task 11 Step 0.

## Task 5 — APG1 carries `fame_lb` as an additive key

`deezer_ids`' pattern followed exactly, and the reasons are worth restating because they
are what make this a safe change to a format two packages parse independently:
`FORMAT_VERSION` stays 1 (both parsers check it for **strict equality**, so a bump would
stop every existing artifact loading, starting with the one the app serves today), and
the key is omitted when empty so the frozen probe mirrors' artifacts stay byte-identical.
Tests pin both: the version does not move, and an empty fame list serialises to the same
bytes as a build from before the field existed.

`"fame_lb"` is the **wire** key; the in-memory identifier keeps the full currency
(`fame_lb_raw`). A wire key cannot be renamed without invalidating every artifact
carrying it — the same exemption `popularity` already carries, and commented at the site.

**Truthiness is deliberate here and is the opposite choice to `build_graph`'s.**
`serialise` writes the key when the list is non-empty, so an all-null list IS written: a
population where nobody has recorded listeners is a legitimate measurement, and dropping
it would be indistinguishable from never having measured. `build_graph` tests
`is not None` for the same underlying reason, arrived at from the other direction.

An end-to-end test now covers fetch → archive → build → serialise → deserialise with
nulls interleaved. The two halves were unit-tested independently; the APG1 format is the
contract between packages that share no code, so the chain is where a mismatch would
actually surface.

**Snyk:** `snyk_code_scan` over `builder/src/artistpath_builder` — 0 issues. Run at the
seam rather than deferred to Task 11 as the plan scheduled, because `fame.py` is new
network-facing first-party code and leaving it unscanned across a session boundary is
the wrong side of that trade.

---

# SEAM 1 — the builder side is complete

**State:** Tasks 1–5 done, 220 builder tests pass, `MSW-G1` byte-identical throughout,
Snyk clean, everything committed and pushed to `msw-package-adoption-plan`.

**Nothing is adopted and nothing the owner can press has changed.** Every new capability
is inert behind a default: `cap_strategy` is still `mutual_knn`, `require_fame` is still
`False`, no artifact has been built, and the API has not been touched at all.

**What the next session picks up:** Task 6 (API `GraphStore` reads `fame_lb`, builds
`fame_lb_pctl` at boot) and Task 7 (the ramp term behind a default-off knob), then Seam 2.
The plan is the operational document; this log carries the reasoning and the three
deviations taken so far.

**Owed and carried forward, in one place:**

1. **Task 11 Step 0** — era-pin `cap_strategy="mutual_knn"` and `require_fame=False` in
   `grt_score.py`, `calibrate.py` and `cre_build.py`. Both halves are needed and the
   `require_fame` half is the harder failure (outright refusal to build).
2. **Task 8 Step 1** — back up `fi_union_snapshot.json` before anything else runs. It is
   gitignored, single-machine, and the cheapest-to-lose dependency in this plan.
3. **`MSW-V4`** — the `ml-graph-analyst` dispatch on the percentile-frame deviation, at
   Seam 3, derivation only.

## Task 6 — `GraphStore` reads `fame_lb`, builds `fame_lb_pctl` at boot

Fameless artifacts load unchanged (`fame_lb_pctl is None`) — every artifact built before
today, including the one the app has been serving.

**The frame is the artifact's own non-null values.** Deviation 2, and the reasoning
belongs here rather than only in the plan: the `CRE-` harness framed against the
*previously adopted* artifact, which is right for comparing arms built from different
data — a fixed experimental ruler. A **shipped** ruler pinned to a retired artifact
would go stale at the next adoption and price today's artists against a population that
no longer exists.

Three properties that took thought and would be easy to get wrong in the other
direction:

- **Nulls take percentile 0.0 but are excluded from the frame.** Including them would
  drag every measured artist's rank upward, so a poorly-covered population would look
  uniformly famous — the metric would improve as coverage got worse.
- **Ties take equal ranks** (`searchsorted(side="left")`). Breaking them would invent a
  distinction the instrument did not measure.
- **NaN sorts above everything in `searchsorted`**, so null ranks are written back
  explicitly rather than left with whatever that produced. This is the one that would
  have shipped silently: nulls would have come out at percentile 1.0 — *maximally
  famous* — the exact inversion of what they mean.

Length is validated against the header's N, which `deezer_ids` is not: this list is
indexed by node id inside the Dijkstra loop, so a disagreement is an out-of-bounds read
or a silently mispriced artist rather than a clean failure. `deezer_ids` escapes the
check only because it is read through a bounds-checked accessor.

## Task 7 — the ramp term, behind a default-off knob

`ApiConfig.w_known_ramp_fame_pctl`, default `0.0`, flipped to `0.01` (`P1a`) at
adoption. Semantics copied from `cre_mirror.py` — the implementation the blind listen
and the coherence audit actually ran on — including the target-endpoint exemption.
`create_app` refuses to boot when the ramp is live over a fameless artifact, on the same
philosophy as the graph-sha check: with the ramp on and no fame, every press would
silently do less than it claims, and a feature that looks *weak* rather than *broken* is
the kind that reaches production and stays.

**`MSW-G2` was vacuous as first written, and the correction matters more than the gate.**
The first version measured "no path moves at k = 0" over the 500-node fixture — which
carries no fame — so the ramp term could not fire whatever the code did. Caught by
perturbation, the same way Task 1's hollow test was caught. The gate now runs over a
fame-carrying store and has a **red control** asserting the ramp does move paths on that
fixture when pressed; without it, a green would mean "this fixture is insensitive",
not "the ramp is correctly inert".

**And the rule the gate was written from does not survive contact with this file.** The
mirror states it as "added only when live, never as `+ 0.0`". At k = 0 the multiplier is
exactly `0.0`, so adding the term is *numerically identical* to skipping it — measured,
not assumed: a perturbation applying it unconditionally left every test green even with
fame present. That rule served byte-identity of serialised probe output, which is not
this file's concern. What `MSW-G2` actually guards is the ramp **firing when it should
not**, and it discriminates — a stray `max(1, n_known)` turns three tests red. The
comment at the site says this rather than repeating the inherited phrasing, because a
rule quoted into a context where it is not true is worse than no rule.

**Snyk:** `snyk_code_scan` over `api/src/artistpath_api` — 0 issues.

---

# SEAM 2 — the API side is complete

254 api tests pass, 220 builder tests pass, Snyk clean on both packages.

**Still nothing adopted.** `cap_strategy` is `mutual_knn`, `require_fame` is `False`,
`w_known_ramp_fame_pctl` is `0.0`, `graph_path` still points at the adopted 75k
artifact, and no artifact has been built. The app serves exactly what it served this
morning.

**Next:** Task 8 (fetch fame over the candidate archive — **back up
`fi_union_snapshot.json` first**), Task 9 (build), Task 10 (`MSW-V1`–`V4`), then Seam 3,
which is an owner stop before the adoption flip.

---

## Seam 2 closeout — what the checks found

**B5 caught a repeat of a documented defect, in the same file.**
`.claude/agents/ml-graph-analyst.md` restates the cost function, and this work added a
seventh term to it. `CLAUDE.md` already records *that exact file* losing a whole term to
the 2026-07-23 rename — a defect of **absence**, which no grep for stale identifiers can
find. It recurred. The fix now carries a note at the site telling a future reader that if
`pathfinding.py` has a term the line does not, the line is wrong.

That cascaded into `CLAUDE.md`, where one statement had become outright **false**:
*"`floor_raw` is the only depth-graduated device in the function"* — there are two now.
Corrected along with the cost formula and the APG1 key list. **D6 row 1** (false about the
world → the session's call), and the split is recorded below.

**B3 — three further invariants perturbed, all go red:** the `MSW-G3` refusal, the
null-percentile write-back, and the artifact's omit-when-empty rule. **Five perturbations
across this branch, two of which found tests that could not fail.** That ratio is the
transferable finding: on this work, a green test is not evidence until it has gone red.

**B1 — `doc-auditor` found two MEDIUM defects, both real, both mine.** Line references had
drifted: `config.py`'s `cap_strategy` 81 → 92, `pipeline.py`'s cap seam 352 → 390 — *because
this plan's own execution added lines above them*. Every reference was correct when written.
The one that mattered was **Task 11, unexecuted, naming `config.py:81` for the adoption flip**
— the most consequential edit in the plan, pointing at the wrong line. Line numbers are now
removed rather than maintained, since the plan edits the files it cites; symbol names do not
move. The auditor passed the two things this session could not read cold: the `GBL-` banner
respects `CAU-` §6's barred reads and does not read as the audit rescuing the null, and
check G2 is correctly scoped.

**A3 — conditions re-tested against reality, not just checked for existence.** `ULC-F3`,
`ULC-F4` and `ULF-3` all still open, correctly. **`ULF-3`'s condition gets its first half
satisfied by this track's Task 12** ("a shipped build has routed on a `ULF-` list") — the
next closeout must re-check it rather than copy it forward, which is the failure mode A3
exists to catch.

**A4 — five knobs added, every one at its old default, deliberately.** `cap_strategy`,
`union_top_j`, `union_degree_ceiling`, `require_fame`, `w_known_ramp_fame_pctl`. **The work
is not closed**; Task 11 owns the flips. **A5** — no listeners on 8000 or 5173; this session
started none. **B2** — no orphans. **C1** — nothing written to `TEST-QUEUE.md`, which is the
correct discharge: nothing the owner can press changed. **D2** — the additive key leaves the
committed fixtures valid, covered by a test on each side. **D3** — no artifact built,
adopted or compared; the only hash produced is `MSW-G1`'s, above. **D4** — 220 builder + 254
api + 107 frontend.

### D6 — standing context layer

| Layer | Delta | Unit |
|---|---|---|
| **Unconditional** (`CLAUDE.md` + `MEMORY.md` index + every skill/agent `description:`) | **+236** | characters |
| **Conditional** (skill bodies, agent bodies, memory bodies) | **+42** | lines |

Baseline on `main`: 45,333 characters / 2,417 lines, measured from a worktree so `memory/`
came from this machine's own directory.

The conditional +42 is `doc-auditor`'s check G2 and `ml-graph-analyst`'s seventh term —
paid only by sessions that dispatch those agents. The unconditional +236 splits: **~150 is
strict correction** and taken as the session's call; **~86 is a new clause** on the
additive-key rule (*"the last two are additive keys, omitted when empty, and the version is
NOT bumped for them"*), which is **growth and the owner's**. The case is that a future
session adding a ninth key and bumping `FORMAT_VERSION` breaks every existing artifact
including the served one, and nothing else in the standing layer says so. Declining it is a
one-line deletion and the correction stands without it.
