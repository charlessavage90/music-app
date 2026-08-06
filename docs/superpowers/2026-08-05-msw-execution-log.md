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

---

## Task 8 — fame coverage over the candidate archive

### Step 1: the snapshot is backed up, and the backup was read back

`fi_union_snapshot.json` (~93k artists, gitignored, single-machine) and its manifest are
copied to:

```
s3://artistpathstack-artifactbucket7410c9ef-b7lbgisct423/backups/analysis/2026-08-02-fame-instrument/
```

**Verified by round-trip, not by the upload exiting 0** — both objects were downloaded back
and `sha256sum`'d. The snapshot returns `d9d6d5d3…62ae8`, identical to the local file **and**
to the `sha256` its manifest sidecar records, so the backup is confirmed against the
instrument's own identity rather than against itself.

**Why this bucket, and the risk that had to be excluded.** The plan says "the S3 archive
bucket (or any second machine)". No archive bucket exists — `--s3-bucket` is a parameter the
crawler takes, not a provisioned resource — and no second machine is reachable from here. The
only bucket available is the **live production artifact bucket**, which holds exactly the
served graph and its sidecar at its root. So the backup goes under a `backups/analysis/`
prefix that cannot be mistaken for a served artifact, and two properties were checked before
writing rather than assumed: **versioning is Enabled** (an overwrite is recoverable) and
**there is no lifecycle configuration** (nothing expires the backup silently). A future
session must not read this prefix as artifact provenance — nothing here is servable.

### Deviation from the plan's Step 2 invocation: `--seed-date`

The plan's command omits `--seed-date`, which defaults to `"unknown"` and is passed straight
through as the `fetched` stamp on every seeded record (`cli.py`, `cmd_fame` → `seed_fame`).
Step 4 of this same task requires the snapshot date as part of the artifact's identity, and
Task 9 Step 3 puts it in the manifest sidecar — so the command as written defeats its own
next step, for all ~93k seeded records. Corrected here by passing
`--seed-date 2026-08-02`, taken from the manifest sidecar's `fetch_date`, never from memory.

**Also recorded because it changes how the run is supervised:** the plan presents Step 2
(seed) and Step 3 (fetch the remainder) as two commands, but `cmd_fame` seeds and then falls
straight through into `fetch_fame` in a single invocation. There is no natural pause between
"the seed landed" and "an hour of network fetching starts". The stage is resumable and
idempotent, so this costs nothing — but the seed report must be read *from the run's own
output*, not from a separate step that does not exist.

### ⚠ The plan's Task 8 command omits `--algorithm`, and would have fetched nothing while exiting 0

**This is the defect worth carrying forward from this task.** The candidate archive is an
**ALG-B** tree, and `similar_prefix` partitions by algorithm: production (ALG-E) keeps the
flat `similar/listenbrainz/` layout, every other algorithm gets a sub-tree. `--algorithm`
defaults to `None`, so `_config` leaves `BuilderConfig.algorithm` at `PRODUCTION_ALGORITHM` —
and `archive_artists` then strips the *production* prefix, finds `/` still in the remainder,
and skips every key.

Measured directly against the real archive rather than argued:

| `fame` invocation | prefix enumerated | artists found |
|---|---|---|
| **as the plan writes it** (no `--algorithm`) | `similar/listenbrainz/` | **0** |
| with `--algorithm` ALG-B | `similar/listenbrainz/session_…contribution_3…/` | **75,000** |

**The failure is silent, and the plan's own completion check cannot catch it.** `cmd_fame`'s
guard is `report.total != len(mbids)`; with an empty population that is `0 != 0`, so the
command **seeds ~93k records, fetches nothing, and returns 0**. Step 3's stated criterion —
*"`fetched + skipped` must equal the archive population"* — is satisfied **vacuously** by
`0 == 0`. Task 9's build would eventually have failed on an empty graph, but only after
Task 8 had reported done, with the cause several steps behind it.

**This is the same class the Seam 2 closeout named** — a green check that cannot go red — and
it is the third instance on this branch. The transferable form: *a completion criterion
phrased as an equality between two derived counts passes trivially when both are zero.* Such
a check needs a non-zero floor, not just equality. Corrected here by passing `--algorithm`
explicitly; the run's own report is recorded below against the known population of 75,000,
which is the non-zero floor the plan's check lacked.

### Steps 2–4: the run, 2026-08-05

One invocation, from `builder/`, exit 0:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u -m artistpath_builder.cli fame \
  --archive-dir ./scratch/grt-archive-algb \
  --algorithm session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30 \
  --seed ./analysis/2026-08-02-fame-instrument/fi_union_snapshot.json \
  --seed-sha d9d6d5d340a81875dd795067d6332a40d813ebfb5b8258048290c27f34662ae8 \
  --seed-date 2026-08-02
```

| Quantity | Value |
|---|---|
| Archive population (ALG-B tree) | **75,000** |
| Seeded from the snapshot | 93,067 imported, 0 already present |
| Already recorded when the fetch began | 70,011 |
| **Fetched fresh** | **4,989**, of which **1,066 null** |
| Reported total | **75,000** — equals the population |
| Fetch elapsed | 8 s |

**Fetch date for the fresh records: 2026-08-05. Seeded records carry 2026-08-02**, from the
snapshot manifest's `fetch_date`. Both belong in the Task 9 manifest sidecar — the fame data
behind this artifact is **two-dated, not one**, which the plan's single-date phrasing does
not anticipate.

**The completion criterion is met non-vacuously**: 70,011 + 4,989 = 75,000, against a
population independently measured at 75,000 before the run.

**The archive now holds more fame records than it has artists — deliberately, and it is
harmless.** The snapshot spans the union of two *pruned artifact* populations, so 23,056 of
its records are for artists absent from this archive. `load_fame` reads by mbid for the
graph's nodes; surplus records are never consulted. Recorded so a future reader does not read
98,056 records over a 75,000-artist archive as a coverage defect.

**The fresh 4,989 are far more likely to be null than the seeded population** — 1,066 of
4,989 against the snapshot's own null share (`fi_union_snapshot.manifest.json`, cited not
restated). Expected direction rather than a surprise: these are exactly the artists *both*
prior artifacts pruned away, so they are the obscure tail. It matters downstream because
nulls price at percentile 0.0 — maximal obscurity — so this tail arrives already at the floor
of the ramp's range. A property Task 10 should expect rather than discover.

**A cosmetic defect found and deliberately not fixed:** `fame seed: …` is logged twice, from
`seed_fame` and again from `cmd_fame`'s call site. One execution, two lines — the counts
reconcile exactly, so nothing ran twice. Task 8 is specified *no source changes*, and a
gratuitous edit to shipped code outside a task's remit is its own defect class; deferred as a
one-line deletion for whichever task next touches `cli.py`.

### Coverage measured directly, not inferred from the run's report

`load_fame` was called over the full enumerated population and **returned without raising**,
which is the same call `build` makes — so Task 4's `require_fame` refusal will pass on this
archive for the reason it is supposed to, not by luck:

| Quantity | Value |
|---|---|
| Fame records resolved | **75,000 of 75,000** |
| Null (measured zero listeners) | **5,150** (6.9 %) |
| Non-null | 69,850 |
| Non-null min / median / max listeners | 1 / 1,668 / 455,551 |

The 5,150 nulls decompose as 1,066 from this run's fresh fetches and the remainder from the
seed — consistent with the fresh tail being the obscurer population, as above.

### D6 — accepted by the owner, 2026-08-05; and re-measured at Task 8

The ~86 characters of standing-layer growth (the APG1 additive-key clause) are **accepted**.
`CLAUDE.md` stands as committed; nothing to edit. The Seam 2 D6 row is discharged.

**Absolute figures at `f7c0117`, measured against this machine's own memory directory:**

| Layer | Total | Delta vs `main` | This session |
|---|---|---|---|
| Unconditional | **45,569** characters | +236 | **0** |
| Conditional | **2,459** lines | +42 | **0** |

The +236 / +42 **independently reproduces the Seam 2 session's reported split**, which is a
corroboration of its arithmetic rather than a new cost. Task 8 touched no standing-layer file.

### Verification of Tasks 1–7, at the owner's instruction

He asked that the previous session's work be checked as this one proceeds rather than taken
on the handoff's word. Everything below was **exercised, not read** — and where a check could
have passed vacuously, it was perturbed until it went red.

| Claim (handoff) | How it was tested | Result |
|---|---|---|
| 220 builder + 254 api tests pass | Both suites run | **Confirmed**, exact counts |
| Five knobs at their old defaults | Read from `config.py` on both sides | `mutual_knn`, `require_fame=False`, `w_known_ramp_fame_pctl=0.0`, `graph_path` still the adopted artifact |
| Percentile frame is the artifact's own population; nulls excluded and priced 0.0 | `fame_percentiles` called on crafted inputs, **then perturbed** | **Confirmed and load-bearing** |
| `trimmed_union` port pinned to the frozen Track B implementation | Ran the pin, **then perturbed the ceiling** | **Confirmed non-vacuous** |
| Additive key leaves existing artifacts valid | Loaded the **real served artifact** under the new code | **Confirmed** |
| Boot refuses when the ramp is live over a fameless artifact | Called the real `create_app` both ways | **Confirmed, seen red and green** |

**The two perturbations worth keeping.** (1) With eight nulls beside two measured artists,
excluding nulls from the frame keeps the lesser-listened artist at 0.0; *counting* them would
put it at 0.89 — near-famous. The exclusion is not a tidiness choice, it is the difference
between "obscure" and "famous" for a poorly-covered population. (2) The frozen-cap pin
compares 258 edges over 60 nodes and diverges to 202 when the ceiling is moved by one, so it
is a real comparison rather than two empty results agreeing.

**A correction against this session's own work, recorded because the record should show it:**
the boot-refusal check was first written by re-stating the guard's condition inline instead of
calling `create_app`. That proves the condition is true, not that the code acts on it — it
would have passed identically had the `raise` been deleted. Redone against the real factory.
Same defect class as the vacuous tests this branch keeps finding, committed by the session
looking for them.

**Nothing found wrong in Tasks 1–7.** The two defects this session found are both in the
**plan's Task 8 text** (the missing `--algorithm`, the missing `--seed-date`), not in the
previous session's code.

### Mid-flight closeout at Task 8 — what the checks found

**B1 — `docs-lint` hard checks passed; the `doc-auditor` found one MEDIUM, real and fixed.**
`docs/README.md`'s row for *this log* still described only Tasks 1–7 and had gone silent on the
Seam 2 closeout and Task 8 — a defect of **omission**, which is the class no grep finds. Fixed
here rather than escalated: the record had every fact needed. The auditor independently
reconciled the Task 8 counts, including the null split, and confirmed the citations to
`ULC-` §4.1 and the snapshot manifest are citations rather than restatements.

**B5 caught one against this session's own work.** The plan's Task 8 Step 3 had been annotated
with the run's counts inline — a restatement of figures this log owns. Converted to a citation.
**It was correct, and that is exactly why it is a defect**: a correct restatement is how drift
starts. `.claude/` was swept explicitly and is untouched by this work.

**A3 — conditions re-tested against reality, not merely confirmed to exist.** `ULC-F3` was the
one at risk, since this session ran a network fetch: it blocks *crawl extension*, and the `fame`
stage writes to the `fame/` prefix without extending the artist frontier, so it is untouched and
correctly still open. `ULC-F4` and `ULF-3` not due — and `ULF-3`'s first half comes due at Task
12, so the next closeout must **re-test** it rather than copy it forward.

**A5 — no listeners on 8000 or 5173.** This session started none; the API was never booted
(`GraphStore` was loaded in-process for verification only). **Nothing left running.**

**A4 — inapplicable by design, stated rather than skipped.** Unshipped work is this plan's
premise until Task 11; no knob this session added, because it added none.

**D2/D3 — D2 falls away** (no artifact changed, fixtures untouched). **D3 applies and is
discharged**: the only uncommittable state is the archive's `fame/` subtree and the S3 backup,
both with locations and the seed sha recorded above. **No graph artifact was built**, so there
is no new checksum to record — which is precisely why this session stopped before Task 9.

**C1 — nothing written to `TEST-QUEUE.md`, and that is the correct discharge.** Nothing the
owner can press changed: no artifact built, no default flipped, no frontend file touched.

---

## Task 9 — the candidate artifact

### A third defect in the plan's commands, and the pattern behind all three

**The plan's Task 9 build command would have produced a FAMELESS artifact while exiting 0.**
It passes `--cap-strategy trimmed_union` and nothing else. But `require_fame` defaults to
`False`, `pipeline.py` calls `load_fame` only `if config.require_fame`, and `artifact.py`
writes the `fame_lb` key only `if graph.fame_lb_raw` — so the whole fame path is skipped and
the artifact silently omits the key the adoption exists to ship. Acceptance does not check
fame. The first thing that would have caught it is the API's boot refusal at Task 10 Step 3,
**three steps and one adoption decision downstream of the cause.**

The plan's own Step 1 is unrunnable for the same reason: it asks for a build that refuses with
`MissingFameError`, and with `require_fame=False` that build succeeds.

**The fix is per-invocation, and the obvious fix is the forbidden one.** Flipping the
`require_fame` default here would break Task 11 Step 0's ordering — `grt_score.py`,
`calibrate.py` and `cre_build.py` all construct `BuilderConfig` without pinning it, and an
unpinned flip makes all three **refuse to build** against archives that have never had the
`fame` stage run. The Seam 2 handoff names this explicitly ("do not 'fix' it to `True` before
Task 11"), and `config.py`'s own comment reaches it independently ("*the artifact shipped by
that adoption is built with it explicitly on*"). So: a `--require-fame` **`store_true`** flag.
It can only ever turn the guard ON from the command line — once the default flips at adoption,
omitting it inherits `True`, and a CLI able to silently switch the guard *off* is the one thing
this must not offer.

**Two flags were needed, not the one the plan anticipated.** `p_build` carried only `--out`,
`--algorithm` and the archive args; `BuilderConfig` has no env-driven loading at all, so
`require_fame` was unreachable from the CLI by any route. `--cap-strategy` needs no CLI-side
validation — `__post_init__` already rejects anything outside `PERMITTED_CAP_STRATEGIES`.

**The pattern, which is the finding worth keeping.** All three defects found on this branch —
Task 8's missing `--algorithm`, Task 8's missing `--seed-date`, Task 9's missing fame flag —
are **one defect, not three**: the plan's Task 8 and 9 commands were written before Tasks 3
and 4 built the CLI they invoke, and were never reconciled against it afterwards. That is an
**unreconciled dependency**, not bad luck, and it is invisible to prose review because each
command is individually plausible. Two of the three fail *silently* — exit 0 with the wrong
output — which is what makes the class expensive.

**So the check was done once for the whole remaining plan instead of three more times.** Every
flag, env var, named symbol and endpoint field in Tasks 10–12, swept against the actual
parsers and source:

| Checked | Outcome |
|---|---|
| `ARTISTPATH_DEPLOY_GRAPH_KEY` / `ARTISTPATH_DEPLOY_SIDECAR` | both real in `infra/app.py`; `infra/README.md:52-53` accurate |
| `/health` reports sha, artists **and edges** (Task 12 Step 3) | all three present |
| Era-pin sites `grt_score.py:145,155`, `calibrate.py:232`, `cre_build.py:389` | all four exact |
| `test_default_graph_path_points_at_an_artifact` (`test_config.py:18`) | exact |
| `ulc_exposure.py`, `graph-algb-full.bin` + sidecar (Task 10) | all present |
| `RAMPS["P1a"] = 0.01` (Task 11's ramp value) | confirmed as the cited source |

**The class is structurally exhausted at Task 9**, and that is checkable rather than hopeful:
all three instances were *builder-CLI invocations*, and Task 9 Step 2 is the plan's last one.
Tasks 10–12 invoke pytest, npm, git, `aws` and cdk — tools the plan did not author ahead of
building.

**Two findings from the sweep that are live rather than reassuring:**

1. **`w_known_ramp_fame_pctl` is NOT env-surfaced.** `ApiConfig` reads only `graph_path`,
   `graph_sha256`, `origin_secret`, the CORS list and the clip-cache pair from the
   environment. Task 10 Step 3 hedged ("via env if surfaced, else a one-line local override")
   and **the second branch is the live one**. Known before Task 10 rather than during it.
2. **Two stale line numbers, both cosmetic** (symbol correct, offset wrong): `cre_build.py`'s
   `gate()` cited at 410, actually **399**; `drop_unlistenable` cited at `config.py:192`,
   actually **224**. Consistent with the plan's own header warning that its line numbers have
   drifted; anchor on symbols.

### Step 1 — `MSW-G3` fired for the first time, and it fired correctly

Radiohead's fame record (`a74b1b7f-…`, 455,551 listeners) was moved out of the candidate
archive and a real `build` was run — not the condition re-stated inline, which is the vacuous
shape this branch keeps finding and which the previous session caught itself committing.

The build ran the full pipeline and **refused**:

```
artistpath_builder.fame.MissingFameError: 1 artists in this build have no fame record:
a74b1b7f-71a5-4011-9441-d0b5e4122711. The fetch population and the build population have
diverged — run the `fame` stage against this archive. Refusing to build rather than pricing
them by default.
```

Exit 1, **no artifact written**, refusal raised at `pipeline.py:434` before `check_acceptance`.

**One deviation from the plan's wording, recorded rather than corrected:** it asks for a
refusal "naming the artist", and the message names the **MBID**, not the name. `load_fame`
works over mbids and never loads the identity map, so a name is not available at the raise
site. The MBID is the actionable handle — it is what indexes `fame/` — so this is a wording
inaccuracy in the plan, not a defect in the guard.

**The choice of artist was de-risked rather than assumed:** had Radiohead been pruned out of
`keep`, `load_fame` would never have asked for it and the build would have *succeeded*, making
the check inconclusive-looking-like-a-pass. Confirmed present in the old candidate artifact
(`graph-algb-full.bin`, 68,467 nodes) first.

**The archive was restored and the restoration verified**, not assumed: 98,056 records, the
file byte-identical to its recorded contents, and no stray red-check artifact left behind.

**Filter and component counts observed during the refused run** (reproduced identically by the
real build below): 7 special-purpose entities filtered, 27 nameless, 9,501 no-release-tail,
1,940 featured-credit and 4,248 un-listenable dropped; largest component 58,838 of 59,277.

### Step 2 — the build was REJECTED BY ACCEPTANCE. No artifact exists.

**This stops the plan and goes to the owner, per Task 9 Step 2's own instruction ("a failure
stops this plan and goes to the owner; do not route around it"). It was not routed around.**

```
artistpath_builder.acceptance.ArtifactRejected: artifact rejected; not written:
  - artist count 58838 outside bounds [60000, 90000]
  - edge count 1315684 outside bounds [700000, 1100000]
```

**No artifact and no manifest were written** — `cmd_build` calls `check_acceptance` *before*
`serialise` and `write_bytes`. Verified on disk: neither `graph-msw-tu50.bin` nor its sidecar
exists. **There is therefore no sha256 to record, and the handoff's "commit the sha in the
same session as the build" instruction is moot rather than skipped** — the failure mode it
guards against (an unidentifiable artifact) cannot arise from a build that wrote nothing.

Steps 3–4 (manifest, determinism spot-check) are unreachable and were not attempted.

#### What passed, and this is positive evidence rather than an inference

`check_acceptance` **accumulates every problem into one list and raises once** — it does not
short-circuit. So a rejection naming only the two global bounds establishes that everything
else was checked and passed on this graph:

- **zero nameless artists**;
- **all canonical names present** in the largest component;
- **top-25-by-popularity median degree ≥ 25.0** — the §2.8 signature detector, the check the
  module exists for, **green**;
- **top-25-by-popularity minimum degree ≥ 8** — the "Radiohead one step short of deletion"
  check, **green**;
- **median degree inside [5.0, 25.0]**.

The bounds that failed are, in the module's own words, *"a REGRESSION TRIPWIRE, NOT a §2.8
DETECTOR … deliberately generous"*, catching *"a build that silently loses a large share of
the graph"*. Their comment also anticipates this situation directly: *"Update them
deliberately when the crawl target changes; a new crawl is a new artifact identity, not a
bound to widen quietly."*

#### Property, not bug — reconciled against the listened arm to within 30 nodes

The listened arm is `CRE-` cell **B-S1** (`TUw-50-50` = trimmed union j=50, ceiling 50) — the
package `GBL-` heard and `CAU-` audited. Its recorded build diagnostics are owned by
`builder/analysis/2026-08-03-cap-reevaluation/cre_builds.json` and read from it here:

| | B-S0 (mutual k-NN, same archive) | **B-S1 — the listened arm** | **This build** |
|---|---|---|---|
| Artists | 58,851 | 63,056 | **58,838** |
| Edges | 732,832 | 1,379,944 | **1,315,684** |
| `drop_no_release_tail` / `drop_featured_credit` | on / on | on / on | on / on |
| `drop_unlistenable` | — did not exist — | — did not exist — | **ON** |

Both breaches are explained by knobs that were chosen deliberately, and the arithmetic closes:

1. **The edge ceiling was never compatible with the trimmed-union rule.** B-S1 recorded
   **1,379,944** edges — further above the 1,100,000 ceiling than this build is. The listened
   arm would have been rejected by this same criterion. Mutual k-NN on the *same archive*
   (B-S0) gives 732,832, comfortably inside. The rule is non-reciprocal by construction, which
   is the whole point of it; roughly doubling the edge count is its defining property, not a
   regression. **This breach has nothing to do with the un-listenable filter.**
2. **The node floor is breached by the un-listenable filter, and only by it.** B-S1 sat at
   63,056 — *inside* the bound. This build sits at 58,838, a fall of **4,218** against a
   filter that dropped **4,248** artists; the 30-node gap is the 27 nameless drops plus
   largest-component boundary effects. The filter is **named deviation 1** and is *the change
   the owner is adopting for*.

The two shared drop counts are **identical** to B-S1's (9,501 no-release-tail, 1,940
featured-credit), which is independent corroboration that this build reproduces the listened
arm on every knob except the one named deviation.

**Conclusion: the build is structurally the thing the owner chose, and the bounds are
calibrated for the map it replaces.** Nothing here indicates a defective build.

#### `ml-graph-analyst` deliberately NOT dispatched here

Task 10 Step 4 carries a conditional property-or-bug trigger for structural metrics moving
beyond what B-S1 predicts. **They did not move beyond it — they landed on it, to within 30
nodes**, from the committed record, with a one-knob explanation for each breach. Dispatching
to re-derive an answer already established in this section would be escalating settled
reasoning, which `CLAUDE.md` names as its own failure. **`MSW-V4` remains pre-authorised by
the owner and unrun**: its inputs include the new artifact, which does not exist, so it is
blocked rather than declined and runs at Task 10.

#### Whose decision this is

**The owner's, for two independent reasons**: the plan routes acceptance failure to him by
name, and widening a safety bound so an adoption can proceed is risk acceptance on an
adoption-adjacent guard. The options and their consequences are in the report to him; this
log takes no position on which to take, and **no bound was edited.**

### The owner took Option A, 2026-08-06 — recalibrate deliberately, and on the record

**His decision, taken on the report above.** Recorded as his, because moving a safety bound so
an adoption can proceed is risk acceptance and not a session's call.

**The weakest link named in that report was closed BEFORE acting on it**, not left standing:
`gbl_generate.py:136` reads `builder/scratch/cre-cells/B-S1.bin` directly (spec §2: *"V0 =
adopted production graph + production defaults; G = B-S1 + the ramp"*), and that file's sha256
is **byte-identical** to the `9da39621…` recorded in `cre_builds.json`. So the comparator in
the reconciliation above is the literal artifact the owner listened to, not a near-neighbour.

**What changed, and the principle.** Only the two bounds that actually failed. `median_degree`
passed and was left alone; every famous-degree criterion — the module's actual §2.8 detector —
is untouched.

| Bound | Was (retired 75k map) | Now (candidate map) |
|---|---|---|
| `node_count` | 60,000 – 90,000 | **47,000 – 71,000** |
| `edge_count` | 700,000 – 1,100,000 | **1,050,000 – 1,580,000** |

**The tolerance is unchanged at about ±20 %; only the centre moved.** The old band sat at
roughly −19 %/+21 % around the retired map's 74,193 artists and −22 %/+22 % around its 898,006
edges. The new band holds the same fractions around the candidate map. That is what preserves
the tripwire's sensitivity to its actual quarry — *"a build that silently loses a large share
of the graph"* — rather than widening it into uselessness, which a union band spanning both
maps would have done.

**Checked against four known artifacts rather than centred on one**, which is the check that
makes this a calibration and not an accommodation:

| Artifact | Inside the new band? | Correct? |
|---|---|---|
| This build (58,838 / 1,315,684) | yes | yes |
| **B-S1, the listened arm** (63,056 / 1,379,944) | **yes** | yes — the thing he approved must pass |
| Retired 75k map (74,193 / 898,006) | no | yes — post-adoption it is the wrong shape |
| Mutual k-NN on the candidate archive (58,851 / 732,832) | no | yes — wrong connection rule |

### A consequence found before it bit: the frozen calibration probe

`builder/analysis/2026-07-23-acceptance-bounds/check.py` imports `PRODUCTION_ACCEPTANCE` and
**asserts it ACCEPTS the retired 75k artifact**, failing loudly otherwise. Recalibrating would
have made that probe report *"ADOPTED was rejected but must be accepted"* — destroying the
demonstration it exists for, which is the top-25 median-degree **separating statistic**, not
the global bounds at all.

**Era-pinned rather than followed**, using the same pattern and for the same reason as Task 11
Step 0's three `BuilderConfig` callers: a `PRE_MSW_ACCEPTANCE = replace(PRODUCTION_ACCEPTANCE,
node_count=…, edge_count=…)` holding the pre-adoption values. Everything else, **including the
separating statistic itself, still tracks shipped code** — only the two era-dependent bounds
are frozen. Its docstring was corrected in the same edit, because it claimed to run
`PRODUCTION_ACCEPTANCE` and no longer does.

**Noted, not fixed, and pre-existing:** that script's `ROOT` still points at the OneDrive path
the tree left on 2026-07-27, so it has been non-runnable at its hardcoded location since the
move. Out of this task's remit, and its own docstring calls it *"a record of what was
executed, not a maintained tool"*. The era-pin makes it correct; it does not make it runnable.

### Step 2 (second attempt) — the artifact exists

```
wrote ./scratch/graph-msw-tu50.bin: 58838 artists, 1315684 edges (22.4 per artist), 17.8 MB, 39s
```

**Identity — this log owns it, and the sidecar is the source (`DEP-24`; never transcribed by
hand):**

| | |
|---|---|
| Artifact | `builder/scratch/graph-msw-tu50.bin` |
| **sha256** | **`43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`** |
| Bytes | 17,773,958 |
| Built at | 2026-08-06T04:45:10Z, from `git_commit` `3aa61f0` |

The sha was **read from the sidecar and independently recomputed from the file** — the two
match, as do the byte counts. Recorded and committed in the **same session as the build**, per
the standing instruction, before any further work.

**Sidecar confirms every intended setting**: `cap_strategy: trimmed_union`, `require_fame:
true`, all three drop filters `true`, `union_top_j: 50`, `union_degree_ceiling: 50`.

**`fame_lb` landed, verified by loading the artifact** rather than inferred from the flag:
58,838 entries for 58,838 nodes (full coverage), 58,746 non-null, 92 nulls, and Radiohead's
value **455,551 — identical to its archive record**, which also confirms the Step 1 restoration
was faithful. The null count is far below the fetch population's 5,150 because nulls are
disproportionately the obscure artists the drop filters and largest-component prune remove.

### Step 4 — determinism confirmed

Built a second time to `graph-msw-tu50-determinism.bin` from the same archive with the same
flags. Both runs produced sha256
`43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` — **byte-identical**, so
spec §9 holds for this artifact under `trimmed_union` + `require_fame`, which is the first time
that combination has been exercised.

**The duplicate was then deleted.** It was byte-identical to the retained artifact, so nothing
was lost, and this project's recorded pain is that *"several graphs exist and they are not
interchangeable"* — an 18 MB twin with a near-identical name adds to exactly that. The
comparison is the record; the second file is not.

**Task 9 is complete.** Steps 1–5 all done: `MSW-G3` exercised red, artifact built and
identified, manifest written, determinism confirmed, committed.

---

## Task 10 — verification

### `MSW-V1` — PASSED. The stop branch does NOT fire.

**Figures owned by `builder/analysis/2026-08-05-msw-verification/msw_v1_named_artists.json`**,
written by `msw_verify.py`. Both artifacts are sha-verified inside the script, which exits
rather than proceeding on a mismatch — several graphs live in `scratch/` and a conclusion drawn
from the wrong one looks exactly like a correct one.

**All six core names were present in the old candidate artifact and are absent from the new
one.** No name was ambiguous, so `BYP-13`'s "a name is not an identifier" trap did not arise
here — recorded because the script checks for it rather than assuming it away.

| Name | in old | in new | verdict |
|---|---|---|---|
| Rick Davies | yes | no | dropped by filter |
| Max Martin | yes | no | dropped by filter |
| Brad Delson | yes | no | dropped by filter |
| Joey Kramer | yes | no | dropped by filter |
| Dallas Taylor | yes | no | dropped by filter |
| John McVie | yes | no | dropped by filter |
| *Four Tet (context, cannot fire the branch)* | yes | **yes** | present legitimately |

**The plan says "nine named artists" and lists six; both are right and the discrepancy is
worth writing down** rather than silently resolving. `CAU-C3`'s table holds **nine SLOTS across
seven distinct artists** — Brad Delson and Dallas Taylor occupy two each, plus Rick Davies's
second slot in the DOESN'T FIT column. The seventh artist is Four Tet, who is deliberately not
a core name: findings §1 records that he *listened and understood*, declining on bio grounds
rather than on having nothing to play. **His surviving is the correct outcome, not a miss.**

**Red control — the check can fail.** Re-run with the "new" artifact pointed at the *old*
unfiltered one, **6 of 6 core names SURVIVE and the stop branch fires.** So the pass is a real
discrimination, not six lookups that would have returned "absent" whatever was loaded. This is
the same discipline `MSW-G3` got at Task 9 Step 1, and for the same reason.

**What this settles, in plain terms:** the artists the owner could not judge in the coherence
audit *because there was nothing of theirs to listen to* are gone from the map — and the one he
could listen to is still there. It is the real-world confirmation `CAU-` §3's second
weakest-link asked for, on a built artifact rather than on a census.

**What it does not settle:** that no *other* artist of this class survives. Six names is the
audit's sample, not a census of the map, and `MSW-V1` was never scoped to be one.

### `MSW-V4` — the frame-deviation bound. Derivation only; no read fires.

Dispatched to `ml-graph-analyst` with the plan's verbatim question, pre-authorised by the
owner. **Figures owned by `builder/analysis/2026-08-06-msw-v4-frame-deviation/`**
(`mv4_frame.json`, `mv4_gaps.json`, with `README.md` and the two scripts) — cited here, never
restated as new. Both artifact checksums were verified inside its scripts.

**It returned a PREMISE CORRECTION, and that is the most valuable thing in it.** The plan
describes deviation 2 as a change of frame *population*. The **estimator differs too**:

- shipped (`graph_store.py::fame_percentiles`): `|{f < v}| / (N_nonnull − 1)`
- `CRE-` (frozen `fi_stats.Frame`, `FAM-AM1.6`): `(|{f < v}| + (|{f = v}| + 1)/2) / N_nonnull`,
  with values above the frame maximum capped at `pctl(max)`

**This session verified the shipped half against source rather than accepting the report**:
`np.searchsorted(frame, values, side="left") / max(1, frame.size - 1)` is exactly the claimed
form. The analyst did not work around the discrepancy — it decomposed the two knobs with a
third column and showed the **estimator contributes essentially nothing** (median 5.8e-05)
while the population knob is the whole effect. Reported as one knob, the attribution would
have been wrong.

**A second premise it checked and cleared:** raw values did not drift. 56,080 of the non-null
nodes appear in the `CRE-` snapshot with an **identical integer, zero differing** — so none of
the measured difference is a value change.

**The three results that matter, in the plan's own terms:**

1. **Nobody swaps places.** Both rulers are monotone in the same raw value across all 18,641
   distinct values — checked by enumeration, not assumed. The frame swap is a monotone
   re-mapping and **cannot reorder two artists**. The device's ordering of "who is the obscure
   option here" is untouched.
2. **The device is uniformly slightly weaker, not differently aimed.** Shipped percentiles run
   lower for **99.6 %** of nodes, median shift ≈ 0.09. At the adopted `r = 0.01` and twenty
   presses that is ≈ 0.018 per hop against a median static hop cost of ≈ 1.49 — about **1.2 %**,
   just under the cost of one extra hop.
3. **The "it's just an offset" reading fails at the top of the scale**, and the analyst said so
   against its own headline: the residual after removing the shift reaches 0.091, because the
   `CRE-` frame caps 39 distinct raw values at one percentile and shipped does not.

**A finding that is NOT deviation 2, and must not be filed under it.** 21 nodes are null in the
new artifact *and* absent from the `CRE-` snapshot. Shipped prices them **0.0** (measured zero
listeners = maximal obscurity); the `CRE-` device would have priced them **0.5**. That 0.5 gap
is the largest single discrepancy anywhere in the measurement — 0.10 of cost per hop at twenty
presses, five times `w_hop`.

**This is consistent with the plan and is not a defect.** Deviation 3 says the harness's
"absent from snapshot → neutral 0.5" class *cannot arise in a shipped artifact*, and it does
not: shipped semantics are 0.0 by construction. What the measurement adds is that **the
comparison to the listened arm carries a 0.5 gap for those 21 artists** — true and worth
knowing, and deviation 3's "same direction as `frame.pctl(0)`" holds for the other 71 nulls
(difference 6.7e-06) but **not** for these 21. Recorded precisely rather than smoothed into
deviation 2's bound.

**Its own weakest link, carried forward rather than dropped:** cost magnitudes do not predict
route changes. **No path was run and none was decoded.** A 1.2 % per-hop shift can still flip a
route between two near-tied candidates, and nothing here bounds how often. The analyst named
the measurement that would (paired `find_journey` runs over a fixed pair set under both
percentile columns, paths decoded), stated it was not what it was asked for, and stopped
instead of quietly extending scope — the right call. It also volunteered that its co-neighbour
gap figures are the weakest thing it produced, being degree-weighted samples of *available*
alternatives rather than of near-ties.

**No read fires on any of this.** `MSW-V4` is a bound for the Seam 3 report; whether the
deviation is acceptable is the owner's Task 11 call.

### Mid-flight closeout at Task 10 (2 of 4) — what the checks found

**Tier: mid-flight retirement** — A1, A2-mid, A3, A5, B1, B5, D1-mid, D3, D6, D7. **B2
(reachability), B3 (vacuous-test spot check) and B4 (prose-versus-code) were deliberately NOT
run and travel with the work**: all three want a finished artifact, and Task 10 is half done.

**A3 caught a condition that had come due — and it is the check working exactly as designed.**
Task 8 deferred the duplicated `fame seed: …` log line with the condition *"whichever task next
touches `cli.py` — likely Task 9"*. **Task 9 is that task**, and this session had already
touched `cli.py` twice without noticing. Discharged here: `seed_fame` emits the line itself, so
the call-site copy in `cmd_fame` was removed and a comment records why. This is precisely the
A3 failure mode the skill warns about — *"a satisfied condition that nobody read is
indistinguishable from an open item"* — caught only because the second question was asked
rather than the first.

**B5 found one stale figure, and it was deliberately NOT fixed in place.**
`specs/2026-07-29-algb-trial-build-preregistration.md` §3 restates the acceptance node bound as
"60,000–90,000", which the recalibration above made stale. It is a **pre-registration whose
value is that it is frozen**, and **its argument is unaffected** — a 3,000-node graph fails the
new floor as surely as the old — so only the quoted range is out of date. The correction went
into `docs/README.md`'s row for it, per the frozen-document rule. The sweep covered `.claude/`
explicitly; nothing there describes the builder CLI, the acceptance criteria or the graph's
shape in a way this work invalidated.

**A4 — inapplicable, stated rather than skipped.** The two knobs this session added
(`--cap-strategy`, `--require-fame`) are **per-invocation CLI flags, not config defaults**, and
that is the point of them: flipping the defaults is Task 11's commit and is the owner's stop.
Unshipped work is this plan's premise until then.

**A5 — no listeners on 8000 or 5173.** This session started no server and left none. Nothing
to stop, nothing to relaunch: **C1 queued nothing**, so no queued test needs one.

**C1 — nothing written to `TEST-QUEUE.md`, and that is the correct discharge.** Nothing the
owner can press changed: no default flipped, no artifact adopted, the app still serves the
artifact it served yesterday, and no frontend file was touched. The "did my app move?" answer
goes in the closeout report and the PR body, where he reads it at the time.

**D2 falls away on its own condition.** The committed 500-node fixtures derive from the
**adopted** artifact, and nothing was adopted — the new artifact is gitignored scratch. No
fixture is stale.

**D3 — discharged.** The only uncommittable state is the artifact and its sidecar; its sha256
is recorded above, read from the sidecar and independently recomputed, and committed in the
same session as the build.

**D6 — zero delta, in both layers.** 45,569 characters unconditional / 2,459 lines conditional,
**byte-identical to the Task 8 measurement**, which makes this the third independent
reproduction of those figures. This session touched no standing-layer file: `CLAUDE.md` is
correct as committed and its "Graph shape" section becomes false only at Task 11, where its
correction is already listed. **Nothing is owed to the owner on this.**

**B1 — `docs-lint` hard checks passed; the `doc-auditor` found NOTHING.** 27 `CAND`
figure-restatement candidates, every one a pre-existing threshold in a preregistration spec
and none introduced by this diff — checked file by file against the diff rather than assumed.
The auditor was told the lint had run so it spent its budget on the semantic half, and it
verified the load-bearing claims **against source**: both CLI flags present with
`--require-fame` a `store_true`, both defaults still at `mutual_knn`/`False`, the recalibrated
bounds as logged, `PRE_MSW_ACCEPTANCE` correctly implemented in the frozen probe, and the
seven-term cost function in `.claude/agents/ml-graph-analyst.md` complete against
`pathfinding.py` — that last being the exact defect-of-absence that agent definition was
corrected for on 2026-07-23. It also confirmed the three-link handoff chain reads **forwards**.

**A clean audit is recorded as a clean audit, not as an absence of one.** This branch's
previous audit (Task 8) found a real MEDIUM — a `docs/README.md` row silent on work that had
happened — and that finding was actioned. **B5's stale-figure finding above is this session's
one documentation defect, and the auditor did not find it**, which is worth recording: it sits
in a document outside the diff and was reached by the figure sweep rather than by the audit.
The two checks are not substitutes, which is what the skill says and what this run
demonstrates.

---

## Task 10 continued — the successor session, 2026-08-06 (later)

Picked up mid-flight per the handoff. The cold-read check was run and confirmed by the owner
before anything was touched; he confirmed the `MSW-V2` → `MSW-V3` → Seam 3 sequencing and
**authorised folding in one extra measurement** — the journey-diff `MSW-V4` named and declined
to run. That is `MSW-V2B` below.

### `MSW-V2` — exposure to the un-listenable class, post-fix. A report row; no read fires.

**Figures owned by `builder/analysis/2026-08-05-msw-verification/msw_v2_exposure.json`** —
cited here, never restated. Script: `msw_v2_exposure.py`. The frozen
`ulc_exposure.py` was **not edited**; its statistic, depth constants and bootstrap seed are
**imported** from it, so the number is produced by the same object that produced the
comparator. `ulc_exposure.branch` is deliberately **not** imported — it applies `ULC-` §3.1's
pre-registered branch table, which was written for a different comparison.

**One knob against the comparator.** The factor table is in the script's docstring: `MSW-V2`'s
baseline is `ULC-A4` (cell `B-S1`), and the two differ in exactly one column,
`drop_unlistenable` `False → True`. Cap rule (`TUw-50-50`), archive (`ALG-B`), pricing (`P1a`),
pair set (the eight `GBL-AM1`), depths, instrument and fame column are all held.

**The held-constant term the factor table would have missed, and why it is genuinely
constant.** `require_fame` is `False` for `B-S1` and `True` for the new artifact. It is inert
for structure, and this was **verified against source rather than inferred from node counts**:
`pipeline.py:434` reads fame *after* `keep` is fixed, so it cannot add or remove a node. It
changes the metadata blob only.

**A precondition was asserted before any journey was walked, because the measurement could
have been vacuous.** The shipped drop payload and `ULC-D2` are different objects censused over
different populations, so it was not obvious the class could still appear at all. It can:
**2,802 of `ULC-D2`'s members survive into the new artifact** (counts in the JSON). Had that
intersection been empty, a 0 % share would have been structurally guaranteed and reporting it
as a result would have been meaningless — the script exits saying so rather than printing the
zero.

**Run state MET, 24 of 24 slots.** All sixteen pair endpoints survive the filter; none of the
eight pairs was lost.

**The comparator's own run state was NOT met and that is inherited, not repaired.** `ULC-`'s
run was 95/96 and `ULC-R1` never fired there. No `ULC-` read is revived here; any slot the
comparator lacks is dropped from the pairing and named, never filled or averaged around.

**⚠ The paired median reads zero and the mean moves by double digits. Both are in the JSON and
neither may be reported alone.** The class is **concentrated in a minority of journeys**, not
spread across them: of the 16 deep slots, **10 are identical, 4 improve sharply, and 2 get
worse**. A paired median over mostly-identical slots therefore reads 0.00 while the mean falls
by ~10 pp. This is **`ULC-R1`'s recorded statistic defect reproducing exactly** — `ULC-` results
name it as a design defect and deliberately did not patch it, and it is **not patched here
either**. The script reports median, mean and the three sign counts together, with the caveat
stored beside the figure so it cannot travel without it.

**Two slots got WORSE and the summary must carry them.** Tame Impala → Fountains Of Wayne at
d20 and Led Zeppelin → Guster at d20 both gained class members the comparator did not have.
Named in the JSON per slot.

**The under-count, stated up front rather than found in the read.** 46,382 of the new
artifact's 58,838 nodes were **never in `ULC-D2`'s census population** and cannot be counted
however un-listenable they are. So a low share is evidence the **known** class was removed and
is **not** evidence that none remains. The figure is stored beside the share.

**Five class members still reach an interior**, one slot each, and they are named in the JSON
rather than only counted — Jack Antonoff, James Mercer, Josh Kaufman, Maynard James Keenan,
Pino Palladino. Producers, session players and front-men of bands: **the same shape `CAU-C3`
described**, not a new class. No read fires on this; it is a report row for Seam 3.

### `MSW-V2B` — does the frame deviation change what the router CHOOSES? Yes, at depth.

**Not in the plan.** Folded in on the owner's authorisation. This is the measurement `MSW-V4`
named, declined to run, and carried as its own weakest link: *"cost magnitudes do not predict
route changes. No path was run and none was decoded."* **Figures owned by
`builder/analysis/2026-08-05-msw-verification/msw_v2b_journey_diff.json`** — cited here, never
restated. Script: `msw_v2b_journey_diff.py`. Run with the **shipped router**
(`artistpath_api.pathfinding.find_journey`), not the mirror.

**One knob: the `fame_lb_pctl` column the ramp reads.** Shipped (the new artifact's own
population) against `CRE-`'s ruler column (framed on the retired adopted artifact — the frame
the **listened** arm ran under). Same store, edges, scores, `pop_raw`, `degree_hub_penalty`,
config, exclusions and pairs; one array swapped with `dataclasses.replace`.

**The press sequence is held constant and derived once from the shipped arm.** Letting each arm
pick its own victim would have been a second knob — the arms would then differ by route *and*
by which artist was pressed. Holding it also matches the app, where the **user** picks the card
they know, so the press sequence is an input to the router rather than an output of it.

**⚠ HYPOTHETICAL UNTIL TASK 11.** The measurement runs at `w_known_ramp_fame_pctl = 0.01`
(`P1a`). At the shipped default of `0.0` the ramp is **not added at all**, so the two arms are
identical **by construction** and the measurement would be vacuous. This says nothing about
what the app does today.

**Both controls behaved, which is what makes the result readable.**

- **GREEN anchor at `k = 0`:** identical on every pair in both sets, as it must be — with no
  presses the ramp is not added. A divergence there would have meant the harness was comparing
  something other than the fame column.
- **RED control:** one arm's column replaced by its own reversal (`1 − p`) makes journeys
  diverge at every pressed depth. **The comparison can go red**, so the zeros below are
  evidence rather than a dead wire. This is `CRE-G1(a)`'s lesson applied — a green run from a
  comparison that has never gone red is not evidence.

**The result, and it splits — both halves travel or neither does.**

- On the **22 `CRE-` famous pairs** (all 22 resolve in the new artifact): **0/22 differ at one
  press, 4/22 at ten, 10/22 at twenty.** Nearly half the journeys change at depth.
- On the **eight `GBL-AM1` pairs — the ones actually listened to** — the effect is close to
  absent: **0/8 at one press, 1/8 at ten, 0/8 at twenty.**

**The second bullet cuts against the first and is stated with it deliberately.** The pairs
whose verdicts are on the record barely move; the broader famous set moves a lot. Neither set
is the "right" one — the listened set is small and was chosen for the owner's familiarity, and
the famous set was never listened to.

**The differences are substantive, not tie-break cosmetics.** Decoded and read: Young Gun
Silver Fox → Eloy at ten presses routes *Future Islands → Romy → Disclosure → Nathan East*
under the shipped frame and *Real Estate → Grizzly Bear → Thom Yorke → Muse* under the `CRE-`
one. Different music, not a reordering.

**This closes the question the handoff named as "the most decision-relevant thing not
measured".** `MSW-V4` bounded the deviation at ≈1.2 % of a hop and could not say whether that
flips routes. It does — rarely at one press, often at twenty. **No read fires**: no threshold
was pre-registered for this and none is supplied. It is a bound for the Seam 3 report.

**Its own weakest link.** The press sequence is derived from the shipped arm under one victim
rule; a different rule could give a different divergence rate, and nothing here bounds that.
And "the journeys differ" is not "the journeys are worse" — **this measurement carries no
quality judgement in either direction**, which is the owner's, and is not evidence for or
against adoption on its own.

### `MSW-V3` — boot and press. The app works on the new artifact, under both configurations.

**Two boots, because the plan asks for the Task 11 configuration and one field is not
env-surfaced.** `config.py` reads env for `graph_path`, the sha, the origin secret, CORS and
the clip cache — **not** `w_known_ramp_fame_pctl`. The plan allows "a one-line local override
noted in the log": it was a factory module **in the session scratchpad**, outside the repo,
constructing the same app as `build_default_app` with one field replaced. **`config.py` was not
touched and no default was flipped** — the owner's hard stop on Task 11 stands, and killing the
process returns the app to `0.0`.

- **Ramp OFF (`w_known_ramp_fame_pctl = 0.0`, today's shipped default), port 8000.**
- **Ramp ON (`0.01`, `P1a` — what Task 11 would adopt), port 8001.**

**Both boot clean and `/health` reports the right artifact:** sha `43dd82bb…`, 58,838 artists,
1,315,684 edges — **matching the sidecar**, which is the Task 12 Step 3 check performed early
and locally. The boot guard that refuses a live ramp over a fameless artifact did not need to
fire; this artifact carries fame.

**Playwright e2e: 5 of 5 passed** (`fallback`, `responsive`, `path`, and both `playback`
specs), against the new artifact through the Vite proxy. **Run at the shipped default**, so it
exercises the artifact and the app, not the ramp.

**Three pairs pressed to ten, five depths each, both configurations** — The War On Drugs →
Sigur Rós, The Killers → The Beatles, Tame Impala → Fountains Of Wayne (MBIDs taken **verbatim
from `gbl_pairs_approved.json`**; two of three were wrong when first guessed from the name,
which is `BYP-13` exactly, caught before it reached a result). **The interior changed at every
press step, on every pair, in both configurations.** Raw records in the scratchpad, summarised
here.

**Clips: every card on every final path resolved — zero dead cards.** And the resolution was
checked past the JSON: the returned `preview_url`s fetch **HTTP 206, `audio/mpeg`, real bytes**.

**⚠ AUDIBILITY IS NOT CONFIRMED AND IS NOT CLAIMED.** This session cannot listen. "A URL that
returns audio bytes" is what was verified; whether it *sounds* like anything is the owner's
hand test, and the standing instruction is to say so rather than claim it.

**The most owner-relevant thing the hand test found, and it is a concrete instance of what
`MSW-V2` counted.** In the ramp-off run **Pino Palladino** — who **is** in `ULC-D2` — reached
an interior card on Tame Impala → Fountains Of Wayne at ten presses. His clip resolves happily
to **"We Are The World (Live)"**: a charity ensemble recording, not his own work. So **"the
clip resolves" is not the same property as "this artist has something of their own"**, and the
dead-card check cannot see the difference. That is the `CAU-C3` complaint arriving through a
card that passes every automated check.

**One reading explicitly NOT taken.** The ramp-on run showed **zero** `ULC-D2` artists across
its 41 interior cards against one in the ramp-off run's 42. **That is not evidence the ramp
reduces exposure** — three pairs is a hand check, not a measurement, and `MSW-V2` is the
measurement. Recorded so the number cannot be picked up later as though it were one.

**Consistent with `MSW-V2B`:** the two configurations produce different journeys at depth and
identical ones at `k = 0`, which is what a ramp that is not added at `k = 0` must do.

### B2, B3 and B4 — the three checks the handoff deferred, now that the artifact is finished

**Suites and scan first:** **224 builder, 254 api, both green** — the handoff's counts,
unchanged; no shipped file was touched. Playwright 5/5. **Snyk `snyk_code_scan` over
`builder/analysis/2026-08-05-msw-verification`: 0 issues.**

**B4 found a real defect, and it was in THIS session's own work.** `msw_v2_exposure.py`'s
docstring claimed two held-constants were verified at run time — the cap rule "read off the new
artifact's sidecar and the `B-S1` manifest row" and the archive "asserted below via the
node-set relationship". **Neither assertion existed in the code.** That is exactly `B4`'s
documented shape: a docstring asserting a property the code beside it does not have.

**Fixed by making the code true rather than the prose smaller**, because the guard is worth
having: `assert_one_knob()` now reads both committed records and refuses to run unless the cap
rule matches (`trimmed_union`, `union_top_j` 50, `union_degree_ceiling` 50,
`max_neighbours_per_artist` 50), the comparator really is `ALG-B`, and **the drop flags differ
in exactly `drop_unlistenable` and nothing else**. The factor table's one-knob claim is now
checked rather than believed. The archive half was **not** mechanically checkable from this
script, so the docstring was corrected to say so and point at the Task 9 build record instead of
claiming an assertion that cannot exist. Figures unchanged by the fix.

**B3 — both new guards were deliberately broken and both went red.**

- The one-knob assertion, pointed at `E-S1` instead of `B-S1`, refuses: *"E-S1 is data_set
  ALG-E, not ALG-B"*. It is not a check that passes on anything handed to it.
- `MSW-V2B`'s red control was tested from the other direction: an arm compared **against
  itself** does **not** fire it. Combined with the reversed-column run that does, this shows the
  control discriminates rather than always firing — which is what makes the real green result
  evidence rather than an artefact.

**B2 — no orphans, and the question was asked rather than assumed.** `msw_verify.py`,
`msw_v2_exposure.py` and `msw_v2b_journey_diff.py` have **zero inbound imports**, which matches
the established `builder/analysis/` pattern (`mv4_frame.py` likewise). They are standalone
run-once probes whose value is their committed JSON output; they are **finished, not
abandoned**. The one live inbound import in the sweep is this session's own —
`msw_v2_exposure` importing `ulc_exposure`, which is the "import rather than copy" the plan
asked for, confirmed working.

### Closeout at Seam 3 — what the checks found

**Tier: full ritual** (the work touched the graph and the cost function), at a **seam** rather
than mid-flight, so `A2` rather than `A2-mid` and `D1` rather than `D1-mid`.

**`A4` — nothing was flipped, and that is the intended state, not an omission.**
`cap_strategy` is `mutual_knn`, `require_fame` is `False`, `w_known_ramp_fame_pctl` is `0.0`,
and `graph_path` still names the previously adopted artifact. **Seam 3 is the owner's stop
before any flip**, so per `A4` this work is explicitly **not closed** — it is parked at its
designed decision point. The only place the new configuration runs is a scratchpad factory
override behind a detached local server.

**`A3` — no deferred condition came due, and each was re-tested rather than re-read.**
`ULC-F3` (crawl resume cannot extend) is untouched — no crawl extension was attempted.
`ULC-F4` is its own track. **`ULF-3`'s first half is satisfied by Task 12, and Task 12 has not
run**, so it stays open and must be **re-tested** at the next closeout rather than copied
forward — which is the failure mode `A3` names.

**One new deferral, with its condition, per the standing rule.** The un-listenable census
covers 12,456 of the artifact's 58,838 nodes; the rest cannot be assessed by `MSW-V2`.
**Condition: before Gate 2, or immediately if the owner's hand test finds more than one card of
the Pino Palladino shape.** It is option D in the Seam 3 report and therefore his to schedule.

**`B1` — `docs-lint` hard checks PASSED; the `doc-auditor` found ONE HIGH, and it was real.**
32 `CAND` figure-restatement candidates, every one checked against this session's diff and
**none introduced by it** — the single candidate in a file this session touched (`0.08` in
`TEST-QUEUE.md`) sits in a 2026-07 entry and predates the diff, verified with
`git diff HEAD` rather than assumed.

The auditor's finding: **`NEXT.md`'s entry-point pointer still called the superseded mid-flight
handoff "the current handoff"**, contradicting the same block's own header, the new handoff's
role line and `docs/README.md`. Fixed, and the redundant second pointer this session had added
nearby was folded into it. **This is the defect class `B1` exists for**: the session that
rewrote the block believed it had updated the block, and its own reading confirmed that belief.

**`B5` found a defect of ABSENCE, and it is the more valuable of the two.**
`.claude/agents/ml-graph-analyst.md:50` states that the degree-hub and ramp weights "both
default to 0.0, so both terms are inert unless deliberately set." **True today, false the
moment Task 11's Step 1 lands** — and that file is auto-loaded on dispatch, so a graph analyst
would be told the ramp is inert while the app routes on it. **It was on no era-pin list**, and
**no grep could have found it**: the sentence is not wrong yet. Added to the plan as **Task 11
Step 0b** and to the handoff's owed list. **It was deliberately NOT corrected now**, because it
is currently accurate. Same file and same failure shape as the 2026-07-23 incident `CLAUDE.md`
records, which is why the sweep looked there first.

**`D4` — 224 builder, 254 api, 107 frontend across 18 files, Playwright 5/5. All green, all
run, none asserted from memory.** Snyk `snyk_code_scan` over the new analysis code: **0
issues.**

**`D2` — inapplicable on its own condition, stated rather than skipped.** This session touched
**no shipped source and no committed fixture**; the artifact format did not change (`fame_lb`
was already additive at Task 7). Verified from `git diff 1e5f197..HEAD --name-only`, not
assumed.

**`D3` — discharged.** The only uncommittable state is the candidate artifact and its sidecar;
its sha256 is recorded in the Task 9 section and was **independently recomputed** this session
before any conclusion was drawn from it, and again inside every script that loads it.

**`D6` — zero delta, in both layers. 45,569 characters unconditional / 2,459 lines
conditional** — **byte-identical to the Task 8 and Task 10 measurements**, making this the
fourth independent reproduction of those figures. This session touched no standing-layer file.
**`CLAUDE.md` still needs no correction** and its "Graph shape" section becomes false only at
Task 11, where its correction is already listed. **Nothing is owed to the owner on this.**

**`A5`/`C1`, decided together.** `C1` queued an entry — there **is** something to press, and
the owner said he will press it before starting the next session. Two **detached** servers were
therefore left up (ports 8000 and 5173, PIDs in the handoff and the queue entry), both started
after HEAD so they serve the work being tested, and both verified answering before being
believed. The session-owned background shells they replaced were stopped first, so nothing can
wake a retired session.

---

## Task 11 — ADOPTION. The three defaults are flipped, 2026-08-06

**The owner gave the go at Seam 3** after pressing the local app himself, and asked for the
rest of the plan including the production deploy. Seam 3 is discharged.

### The override, recorded in the fixed words Task 11 Step 3 pre-committed

> This adoption overrides the `GBL-` null (margin 3 vs bar 5; pre-registered consequence
> "production stands"). The owner took it knowingly on 2026-08-05, on `CAU-`'s coherence pass
> at his bar and the un-listenable filter fix, which make the deployed package a new candidate
> under the run-once rule. Neither `GBL-` nor `CAU-` licensed it; his authority did.

It is also written at the `w_known_ramp_fame_pctl` definition in `api/…/config.py`, so a
reader of the knob meets it without reading this log.

### What flipped

| Knob | Was | Now |
|---|---|---|
| `ApiConfig.graph_path` | `graph-t15-tiebreakfix.bin` | `graph-msw-tu50.bin` |
| `ApiConfig.w_known_ramp_fame_pctl` | `0.0` | `0.01` (`P1a`, source `cre_common.py`'s `RAMPS`) |
| `BuilderConfig.cap_strategy` | `mutual_knn` | `trimmed_union` |
| `BuilderConfig.require_fame` | `False` | `True` |

Four knobs, not three: `require_fame` was always part of the same commit and the plan's own
prose says so, but the "three defaults" phrasing in Task 11's title counts the API's two as
one. Recorded because the count is quoted elsewhere.

### Three defects in the plan's own Task 11, all found by executing it

**1. Step 0's era-pin list was complete for its stated reason and incomplete in fact.** The
three named callers (`grt_score.py`, `calibrate.py`, `cre_build.py`) are exactly the analysis
scripts that call `build_from_archive`, which is where both `cap_strategy` (dispatch at
`pipeline.py:390`) and `require_fame` (`pipeline.py:434`) are read — that much was verified by
sweep, not assumed. But a **fourth** caller reads the default without going through
`build_from_archive`: `2026-07-25-ceiling-ordering-headroom/measure_headroom.py:69` asserts
`config.cap_strategy == "mutual_knn"` on a bare `BuilderConfig()`, having reimplemented the cap
itself. Left alone the flip makes that assert fire and the frozen probe stops running. Pinned,
not deleted: the assert stays the guard it was, and the pin is what keeps it true.

**2. Step 1's named test could not have caught what it was named for.** The plan says to
update `api/tests/test_config.py:18` (`test_default_graph_path_points_at_an_artifact`) by
"updating the expected name", and Step 2 says "the api default-graph test pins the new name".
It pinned no name: the whole assertion was `.endswith(".bin")`, which passes for every artifact
ever built. There was nothing to update and the test could not have failed on a stale default —
which is precisely what `closeout` relies on it for. Rewritten to pin the name.

**3. The blast radius on the test suites was not anticipated anywhere in the plan, and it was
97 tests.** 46 builder + 51 api, all failing on the two new guards firing exactly as designed:
`require_fame=True` refusing archives with no `fame` stage, and `create_app` refusing a live
ramp over a fameless artifact. **No guard was weakened to make a test pass.** Three shapes of
fix, and the choice per site was "what is this test's subject?":

- **Pin the unrelated knob off**, following this repo's existing factor-table-control idiom
  (the `drop_unlistenable` pins already in those files). Used where fame or the cap is not the
  subject — the drop-rule files, replay, CORS, the origin gate, routes, smoke.
- **Make the archive meet the shipping requirement.** `test_cli.py` builds through `main`, and
  `--require-fame` is `store_true` by design, so there is no flag to turn it off — the right
  fix is a `fame/` stage in the test archive, the same shape as the ULF- fixture list that file
  already installs. The alternative would have meant weakening a protected claim.
- **Flip the default-pinning assertions rather than deleting them.** Four tests existed to
  assert the defaults were still off (`test_the_default_knob_is_off`,
  `test_default_strategy_is_still_mutual_knn`, `test_fame_is_not_required_by_default`,
  `test_phase2_adopted_defaults`). Adoption is the commit they were written for. Each now pins
  the adopted value, so a silent change to a shipped default is still a test failure.

### Two confounds the flip introduced inside the test suites, both silent

Neither would have failed a test. Both would have made a passing test stop testing its subject
— the `w_floor` shape from `CLAUDE.md`'s dormant-term rule, appearing in test code:

1. **`test_trimmed_union_supplies_more_edges_than_mutual_knn`** built its "mutual" arm as
   `_build(tmp_path / "m", max_neighbours_per_artist=5)`, inheriting `cap_strategy` from the
   default. After the flip both arms are `trimmed_union` and the test compares the rule against
   itself. Now pinned explicitly.
2. **`test_acceptance.py::_build`** injects its defect by monkeypatching
   `graph_mod.mutual_knn_cap` — a function the `trimmed_union` path never calls. On the new
   default the `defective` arm builds a healthy graph, and `test_tiebreak_defect_is_rejected`
   fails for a reason with nothing to do with acceptance. Now pinned to `mutual_knn`.

Both are the same lesson the plan's Step 0 recorded for shipped code, reproducing one layer
down in tests nobody listed.

### Step 0b — the agent definition

`.claude/agents/ml-graph-analyst.md:50` said `w_degree_hub` and `w_known_ramp_fame_pctl` "both
default to 0.0, so both terms are inert unless deliberately set." True until this commit, false
after it. Corrected in the same commit, per the Seam 3 closeout's `B5` finding. It is auto-loaded
on dispatch, so leaving it stale would have told a graph analyst the ramp was inert while the
app routed on it.

### `CLAUDE.md`'s Graph shape section

Corrected in the same commit, as Step 0 requires. It described mutual k-NN as the shipped rule.
It now names `trimmed_union` as shipped, keeps mutual k-NN as supported, and carries the
comparison warning — every pre-2026-08-06 figure was built under the other rule, so the rule a
claim is in has to be checked before two graphs are compared. **D6: +333 characters on the unconditional layer** (45,569 -> 45,902), all of it this
section.** That growth is the owner's call and is reported to him rather
than assumed; the correction itself was not optional, only its size.

### `CLIP-1` — logged by the owner during his Seam 3 hand test. NOT addressed, deliberately.

**He raised it while pressing the app and asked for it to be logged for work after this plan.
Nothing here acts on it.** It is not new to this work and not a regression — the `MSW-` package
neither caused it nor made it worse. It surfaced now because the new map routes through
less-famous artists, so the class is met more often, and because the `CAU-` and `ULC-` work
taught him what to look for.

**`CLIP-1`: a clip can be the right artist and still be the wrong impression of them.** The
resolver's job is "find a track by this artist", and it succeeds; what it does not do is prefer
a track that is *theirs*. Two examples he named:

- **Albert Hammond Jr.**, reached as an interior card, resolved to *"Cinnamon (feat. Albert
  Hammond Jr.)"* — an album track of Damiano David's. Spotify lists both as main artists and it
  is Hammond Jr.'s top track there, so this is **not** a `BYP-13` wrong-artist collision. The
  identity is right; the choice is poor.
- **Metric**, resolved to *"Help I'm Alive (BYNX Rework)"* rather than any Metric original.

**Why it is its own thing and not a duplicate of anything already open.** `BYP-13` is a
*different artist of the same name* — an identity failure, and the `deezer_ids` work addresses
it. `ULC-`/`ULF-` cover artists with **nothing of their own to play at all**, and the filter
removes them. `CLIP-1` is the case where the artist is correct and their catalogue is real, but
the top-ranked track is a guest appearance or someone else's remix. **No existing filter or
check can see it**, and the Pino Palladino case in the Seam 3 report is its close cousin from
the other side: there, "the clip resolves" was not "this artist has music of their own".

**Its condition, so it is not an unranked backlog item:** it becomes actionable when a resolver
change is next opened, or immediately if the owner reports it on a pair he cares about. It is
**not scheduled**, and whether it is worth fixing is his call — the fix is a ranking preference
inside clip resolution (prefer tracks where the artist is the sole or primary credit, fall back
to what is chosen today), and it trades clip *availability* against clip *representativeness*,
which is a product judgement rather than a correctness one.

**Not measured.** Two observed instances is not a rate, and no figure is claimed here.

---

## Task 12 — DEPLOYED. The map switch is live, 2026-08-06

**`https://musicapp.cmiller.io` now serves the adopted package.** Everything below was
verified mechanically rather than by eye.

### The defect in Task 12, and it is the serious one

**The plan's Task 12 has no image-build step.** Its three steps are upload → `cdk deploy` →
verify, citing `infra/README.md:259-269` for the upload and `:52-53` for the deploy variables.
It skips **§3, "Build and push the image"**, entirely.

`w_known_ramp_fame_pctl` is a **code default with no environment variable** — it is baked into
the container. `ARTISTPATH_DEPLOY_GRAPH_KEY` swaps the *artifact* at deploy time and nothing
else. So executing Task 12 as written would have shipped **the new map running under the old
code**: `cap_strategy` and the artifact would have changed, and the `known` ramp — the half the
owner actually pressed and approved — would have stayed at `0.0` in production.

**Every check the plan specifies would have passed.** `/health` reports the graph sha, artist
count and edge count; it reports nothing about the router. The failure would have presented as
"the new map is live and the digging feels weaker than it did locally", which is a judgement
call about taste rather than a visible fault — the shape this project has repeatedly recorded
as the expensive one.

Caught by asking what the deploy actually replaces, not by any step in the plan. The image was
built, and then **checked rather than assumed** before being pushed:

```
docker run --rm --entrypoint python artistpath-api:a06ab58 -c "…"
ramp   : 0.01
graph  : ../builder/scratch/graph-msw-tu50.bin
```

### What was done, in order

1. **Artifact + sidecar uploaded** to `artistpathstack-artifactbucket7410c9ef-b7lbgisct423` as
   `graph-msw-tu50.bin` / `.json`. Completeness verified per §4: S3 `ContentLength` 17,773,958
   equals the sidecar's `bytes`. **The previous artifact's keys were left in place**, which is
   the rollback path — §9 is a redeploy with the old `ARTISTPATH_DEPLOY_GRAPH_KEY`.
2. **Image built and pushed** as `artistpath-api:a06ab58` (digest `sha256:d8b76267…`), tagged
   by commit per §3's never-`latest` rule.
3. **Stack deployed** with `ARTISTPATH_DEPLOY_IMAGE_TAG=a06ab58`,
   `ARTISTPATH_DEPLOY_GRAPH_KEY=graph-msw-tu50.bin`, `ARTISTPATH_DEPLOY_SIDECAR` pointing at
   the sidecar. All nine required variables were confirmed resolved **before** the deploy ran,
   because §1's recorded failure mode is silently-unset variables surfacing as `app.py` naming
   whichever secret it checks first. Deploy output was written to a file, not the terminal:
   `cdk` prints the site credential base64-encoded and the output is not safe to paste.

### Verification (§8)

- **`/health` matches the sidecar mechanically** — the runbook's own assertion script, on
  sha256, artist count and edge count. Not read by eye (`DEP-24`).
- **`SiteUrl` → 301**, **App Runner's public URL → 403** on `/api/artists/search` (`TR-7`
  working), **`musicapp.cmiller.io` → 200**.
- **The running image is `a06ab58`**, read back from the App Runner service description rather
  than assumed from the push. Service `RUNNING`.
- **The ramp is provably live, and the boot guard is what proves it.** `create_app` refuses to
  start when `w_known_ramp_fame_pctl != 0.0` over an artifact with no fame. The service is
  `RUNNING` on an image whose default is `0.01` — so the served artifact carries fame *and* the
  ramp is priced. No separate probe was needed; the guard built at Task 6 does the work.
- **End to end through the public front door:** a Radiohead → Miles Davis journey built, then
  "know them already" pressed five times. **The interior changed at every press.** Clips
  resolved on the cards tried.
- **§5a log retention: already 90 days** on both log groups. It only needs re-running when the
  service is *recreated*, and this deploy updated it in place.
- **§6 frontend sync: not required.** No file under `frontend/` was touched by any `MSW-` task,
  so the deployed SPA is already current. Stated rather than skipped silently.

### One environment note worth keeping

**Cloudflare refuses `urllib`'s default User-Agent with a 403** while `curl` passes. A live
check driven from Python therefore fails in a way that looks exactly like `TR-7`'s deliberate
refusal, on the one hostname where `TR-7` is *not* supposed to fire. Set a browser User-Agent.
Costs a minute to diagnose and looks like a security finding until it is.

### Closeout at adoption — what the checks found

**Full ritual**, since this touched the artifact, the cost function and production.

**`A3` — and its second question fired.** `ULF-3`'s condition is two-part and its **first half
has now come due**: *a shipped build has routed on a `ULF-` list* is **satisfied** (the deployed
artifact was built with `drop_unlistenable=True`, read off the sidecar). The second half —
*the era-pinned probes naming the old flags are retired or re-pinned* — is **not**:
`grt_score.py`, `calibrate.py` and `cre_build.py` still name `drop_no_release_tail` and
`drop_featured_credit`. **Re-tested against reality rather than copied forward**, which is what
the previous handoff explicitly asked for. Stays open, now half-due. `ULC-F3` and `ULC-F4` not
due. New: `CLIP-1` (condition in its own section) and the fixture deferral below.

**`A4` — the default-flip check is the whole of Task 11**, and all four are flipped, deployed
and pinned by test.

**`B3` — the highest-yield check, and it was run rather than reasoned about.** All six
default-pinning assertions were verified to go **red** when the defaults are reverted: the three
builder pins (`test_adopted_defaults`, `test_default_strategy_is_the_adopted_trimmed_union`,
`test_fame_is_required_by_default_since_adoption`) and the three api pins
(`test_default_graph_path_points_at_the_adopted_artifact`,
`test_the_default_knob_is_the_adopted_value`,
`test_boot_allows_the_ramp_over_an_artifact_that_carries_fame`). Both config files were restored
from git afterwards. **This matters more than usual here**, because these six are the only
mechanical guard against a future silent un-flip.

**`B5` — found a defect `Step 0b` missed, in the same file, for the third time.**
`.claude/agents/ml-graph-analyst.md:19` still described the graph as filtered by **mutual k-NN**.
Step 0b corrected line 50 (the ramp) and stopped there; nothing pointed at line 19, because the
plan's obligation named a line rather than a file. **This is the 2026-07-23 failure shape
exactly** — that file, a description going stale, invisible to a grep for the identifier that
changed, since `cap_strategy` never appears in the sentence. Fixed. **The generalisable lesson
is that an era-pin obligation should name the FILE, never the line.**

**`B1` — lint green on hard checks; `doc-auditor` found three defects, all real.** Two were
already fixed while it ran (`NEXT.md`'s top block, the seam-3 handoff's own role line). The
third was **`docs/README.md` still stating "the app now routes on `graph-t15-tiebreakfix.bin`"**
— a HIGH, and one neither the lint nor `B5`'s greps caught, because the sentence is about the
*old* artifact and contains no stale identifier. Its map row now carries the supersession and
points at the log's Task 9 section for the live artifact's identity. The auditor also confirmed
`CLIP-` collides with nothing.

**`B2`** — no modules created; only `config.py` edits in both packages. **`B4`** — the two claims
this session restated from the plan were checked against source rather than trusted:
`cre_build.py`'s `gate()` does compare its `mutual_knn_cap` mirror against a live
`build_from_archive` (so the pin prevents a false mirror-divergence), and `measure_headroom.py`
does reimplement the cap directly at line 149.

**`D2` — the committed fixtures now predate the adopted graph, and this is a DEFERRAL rather
than a skip.** `api/tests/fixtures/*.bin` carry no `fame_lb`, which is why four api modules pin
the ramp off. **Condition: regenerate when a test needs to exercise fame over real data, or
before the next artifact adoption, whichever comes first.** Not done here deliberately —
regenerating changes what every fixture-dependent assertion asserts, and folding that into an
adoption commit would mix two unrelated sources of test churn.

**`D3`** — the adopted artifact is gitignored, so its sha256 and counts live in the Task 9
section, the manifest sidecar, and the PR body. The **previous** artifact's S3 keys were left in
place deliberately as the rollback path.

**`D6` — and a unit correction worth recording.** **Unconditional: 45,569 -> 45,902 characters,
+333**, all of it `CLAUDE.md`'s Graph shape correction. **Conditional: 2,459 -> 2,465 lines,
+6**, all of it `ml-graph-analyst.md`'s body. **An intermediate report of "+909 characters" was
wrong** — it used `wc -c` on the file, which counts bytes, so every CR under `core.autocrlf` and
every multi-byte character (the em-dashes and `§` in that section) inflated it. D6 specifies
`tr -d '\r' | wc -m` for exactly this reason and the corrected figure is less than half. **The
error direction is the dangerous one**: it over-reports growth, which invites paying for it by
compressing live prose — the move D6 names as damage with a receipt.

Both edits are **corrections of false statements**, the first row of D6's table: `CLAUDE.md`
said mutual k-NN was the shipped rule and `ml-graph-analyst.md` said the ramp was inert. Neither
was optional. But **neither fits in "roughly the same size"** — the true statement has to
distinguish two rules where the false one named one — so per D6 they are **reported as growth
and the decision is the owner's**, not booked as a free correction.

**`A5`/`C1`, decided together.** `C1` queued an entry: the live site is the thing to press.
**The two detached servers from the morning are now redundant** — production serves the same
configuration and the queued test needs nothing local. A5's table says close them. **They were
deliberately left running anyway**, because the owner said he was still testing tracks and asked
to be told before anything is shut down; his instruction outranks the default. Ports, PIDs and
the one-line disposition are in the closing message, the handoff and the queue entry.
