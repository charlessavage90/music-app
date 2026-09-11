# `LBD-` blind-listen preparation — retained execution log

**Role: RETAINED EXECUTION LOG for the `LBD-AM5` session: the amendment, the served-population
builds, and the `LBL-` listen materials. ACTIVE. Owns no figures** — the build figures are owned
by `builder/analysis/2026-09-10-lbd-served-population/README.md`; the pair draw's output is its
own committed JSON. Decisions and reasoning, not narration; appended per step so a successor can
pick up at any seam.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
with `LBD-AM1`–`AM4`, and `LBD-AM5` once committed. The blind-listen procedure is `GBL-`'s
(`specs/2026-08-04-gentle-arm-blind-listen-design.md`, its plan, `RUNNER-BRIEF.md`, the run and
write-up logs) with the corrections `findings/2026-08-04-gentle-arm-blind-listen-results.md` §6
records for the next listen, and the `CAU-` confound (`findings/2026-08-05-coherence-audit-results.md`
§2.3). Branch `lbd-listen`, worktree `C:\Users\charl\worktrees\music-app-lbd-listen`, cut from
`origin/main` at `98cd115`.

**Seams named at authoring time** (`CLAUDE.md` rule 3): after Step 1's commit (the amendment is a
governing document; a successor reads it cold); after Step 2 (artifacts identified by checksum in
the figures owner); and the owner's stop at the end of Step 3. The listen itself is run by a fresh
mechanics-only session and written up by a further one — both `GBL-` seams, unchanged.

## Session opening — what was verified before anything was written

- **Repo state:** `main` clean at `98cd115`, PR #115 merged; no other worktree, branch or stash;
  ports 8000/5173 clear. No other session live.
- **Checksums, all matched before any file was read** (2026-09-11 01:12 UTC): `T.parquet`
  `03d47b05…` (= its manifest); `A0.parquet` `f9bd1f83…` (= its manifest); `artist_identity.parquet`
  `02b4c8dd…`; `cxr_added_mbids.txt` `bfed95ef…`, `cxr_preexisting_mbids.txt` `768054b7…`,
  `cxr_residual_mbids.txt` `fa8d85cc…`; `graph-msw-tu50.bin` `43dd82bb…`, `graph-lux4.bin`
  `fd92a735…`, `graph-cxa-adopted.bin` `bc0431c4…`, each equal to its sidecar. `A2.parquet` and
  `ranked_P.parquet` were not verified because nothing here reads them.
- **Grepped before use:** `find_journey` (`pathfinding.py:194`), `Exclusion`/`KNOWN`;
  `ApiConfig.graph_path` defaults to `graph-msw-tu50.bin` and `w_known_ramp_fame_pctl = 0.01`
  (`config.py:49-51, 108`) — **so fame steers journeys and a listenable arm must carry it**;
  `build_from_archive` loads fame from the ARCHIVE through `load_fame(archive, keep)` when
  `require_fame` is set (`pipeline.py:448`, `fame.py:198`, key `fame/<mbid>.json`), after the
  largest-component prune and only into `build_graph`'s metadata; `lb_fame_fetcher` records
  ListenBrainz's per-artist `total_user_count` (`fame.py:246-258`), so a record does not depend on
  which other artists shared its batch; `GraphStore.fame_percentiles` frames percentiles on the
  artifact's own non-null values (`graph_store.py:141`); `check_acceptance`,
  `AcceptanceCriteria` (`acceptance.py:54,259`); `serialise` (`artifact.py:87`);
  `build_manifest`/`write_manifest` (`manifest.py:147,176`); `ClipResolver.resolve(mbid, name,
  deezer_artist_id, index)` returns a `Resolution` with a candidate `count`
  (`clips.py:152,326`); `cre_ladder.victim_key` (`cre_ladder.py:44`) and the `JFX-` precedent of
  calling production `find_journey` directly (`jfx_route.py` header).
- **The served build's own pipeline counts, cited:** MSW execution log line 687 — largest
  component 58,838 **of 59,277**. Read against `pipeline.py:325-417` (drops → scoring → cap →
  symmetrise → prune), that is **439 artists present at the cap step of the served build and
  absent from `V`**. An emitter restricted to `V` removes them from the cap step. Named as an
  exposure in `LBD-AM5`, not treated as constant.

## Step 1 — the pre-measurements, and the pair rule fixed before the draw

**Why the pairs are not `GBL-AM1`'s.** The obvious move — the eight pairs the owner already
approved — would spend the blind: he heard journeys between exactly those artists in `GBL-`,
audited that arm's journeys card by card in `CAU-`, and the served map is that arm's lineage
(`MSW-` adopted it). His `GBL-` notes already record that he could tell the sides apart; a
remembered interior is a stronger tell than a style. So the pool is his same familiarity ranking
with every `GBL-AM1` endpoint removed, and listen 2 gets pairs disjoint from listen 1 for the same
reason.

**Why the rule is mechanical and committed before it runs.** `GBL-` put pair approval with the
owner; this task instructs the session to fix the set. A rule written and committed before its
output exists is the form of that instruction that cannot select on anything: `lbl_pairs.py`'s
docstring is the rule, and its commit precedes the commit of `lbl_pairs.json`. The owner may still
amend the pairs **before any journey exists** without spending the pre-registration.

**What the two measurements returned** (both committed beside their scripts; the amendment carries
the counts it turns on):

- **The drop lists — the one result that changed the configuration.** `LBD-AM4`'s `20260809`
  payload covers `V` but **would drop 31 members of `V`**; the served lineage's own `20260805`
  covers `V` and drops none; the other two drop none. The instruction said "same build configuration
  as the fixed-population A0" *and* "re-measure coverage for this population" — the second exists
  for exactly this case. Building with `20260809` would make listen 1 differ from the served map in
  a second column (31 served artists removed), so `LBD-AM5-3` pins `20260805`. It is `LBD-AM4-3`'s
  principle — use the list that removes nobody from the population — applied to `V`. These are very
  likely the same 31 as `NEXT.md`'s "a rebuild came to silently differ from the live map by 31
  artists"; not checked, because nothing turns on it.
- **`V ∩ P` equals the pinned pre-existing set exactly (58,793); `V − P` = 45.** That is the
  read-validity check.
- **The pair draw:** 125 pool artists, 16 `GBL-AM1` endpoints excluded (the approved set has 16
  distinct endpoints, not 15 as first assumed here), **109 eligible, no other exclusion fired**, 24
  pairs drawn using the pool only to rank 64; four artists skipped a directly-connected candidate;
  every paired artist has ≥ 100 partners inside `V` in `LBD-A0`'s table. `lbl_pairs.json` sha256
  `da2ad2d7…`, rule script `4addf375…`.

**Decisions taken in writing `LBD-AM5`, each the session's (methodology) rather than the owner's:**

- **Two axes, each with its own bar, and d0 inside the tally.** `GBL-` §6.1 says the next protocol
  must state what each row scores or give the axis questions thresholds; asking both per row does
  both. d0 enters the tally because `GBL-`'s reason for excluding it (its intervention was a ramp,
  inert before a press) does not apply to a map swap, and `GBL-` §2.4 is the record that a swap is
  heard at d0. The bar follows `GBL-`'s own scaling rule (0.3 per row, rounded up → 8 of 24).
- **Underpowered is a read, not a footnote** (`GBL-` §6.2): lost rows ≥ the bar on an axis with no
  decisive margin.
- **A split is FAIL**, on `WHAT-GOOD-LOOKS-LIKE` value 8.
- **Clips: up to three per artist, keyed by MBID with the served artifact's Deezer id for both
  sides.** `GBL-` forced name-based clips because its two artifacts disagreed on ids; here every
  presented artist is in `V` and one id source serves both sides, so the app's own id-first path is
  non-differential and closes the wrong-artist class (`BYP-13`) that cost `GBL-` rows. Extra tracks
  answer `CAU-` §2.3.
- **Mechanical reserves instead of an owner swap at the run-state gate.** `GBL-`'s runner had to
  stop and wait for a replacement pair; ordered reserves applied by the script keep the runner
  mechanics-only and no one sees a journey in the process.
- **`LBD-D6` surfaced, not decided.** `NEXT.md` defers `LBD-A4` "before any further `LBD-` arm is
  pre-registered"; `LBD-A5` is such an arm, registered on the owner's instruction. The amendment
  records that it was not preceded by `LBD-A4` and leaves the ruling to him.

**Committed:** the rule and probe at `13410fa`, then `LBD-AM5` with both pre-measurements at
`6e47461` (21:30 −04:00), pushed; draft PR #116 opened. Nothing named by the amendment existed yet.

## Step 2 — derive, emit, build

- **`LBD-A5` derived by `lbd_derive.py` unedited**, through `lbv_derive_a5.py` (which extends its
  `ARMS` table by one entry rather than copying the SQL). `T` verified before reading. **Green check,
  and it is a refusal:** the derived table's dead-end share, absent share and median partner count on
  all four pinned sets must equal the committed curve's (3, 100) cell to float precision — it did, on
  all four. The instrument had cause to go red only if the derivation diverged from the curve's
  ranking, which is the defect it exists to catch; it was not separately shown red.
- **Both archives emitted by the Task 6 emitter unedited**, through `lbv_emit.py`, which verifies the
  emitter's sha against the supply README's record, repoints the population constant at `V`, and
  rewrites only the manifest's `amendment` field (payload bytes untouched). Run strictly one DuckDB
  process at a time (the access-violation trap). Chain wall clock ≈ 6 min in total.
- **Two defects in this session's own first drafts, caught before anything ran on them:** the derive
  wrapper read the curve JSON by a key it does not have (`sets` for `curve`), and `lbv_build.py` let the
  `--map` argument reach a path (Snyk Low, `python/PT`) — fixed by making every path a constant in
  the `MAPS` table; rescan clean.
- **The configuration is asserted, not assumed:** `lbv_build.py` refuses unless every held-constant
  knob equals the served map's recorded configuration and the three drop-list files' bytes equal the
  shas the served lineage's rebuild recorded (`graph-lux4.bin.json`).

## Step 3 (harness) — written while the builds run; nothing generated

- **A tell `GBL-` did not have, found in design and closed:** the two maps name artists from different
  sources — `LBD-A0V` from Task 1's MusicBrainz identity frame, the served map from ListenBrainz's
  neighbour rows. A spelling difference on the same MBID would identify a side. **Every name,
  disambiguation and clip lookup on the page comes from the served map, by MBID, for both sides**;
  every presented artist is a member of `V`, so the served map knows all of them.
- **The press rule is imported, and the import is guarded.** `cre_ladder` puts a frozen copy of the
  api on `sys.path`; `lbl_generate.py` imports the shipped api modules first and refuses if
  `artistpath_api.pathfinding` resolves anywhere but `api/src` (`JFX-`'s import order, now asserted).
- **Generation is exercised on the api's 500-node test fixture, never on the listen's maps** — the
  seam still forbids this session from routing those (`GBL-` harness log §3.4). That retires most of
  `GBL-` harness log §5's residual. **One expectation of mine was wrong and the test says so:** the
  fixture's farthest pair reaches d10 and runs out of interior before d20; the test now asserts the
  ladder's invariants where it reaches, and a new test shows run-state gate (c) firing on that pair,
  beside tests for gates (a) and (b). **54 tests pass.**
- **Committed at `916bc6f`**, pushed.
- **Gate G2 pre-checked, because its failure would otherwise waste a sitting:** `graph-msw-tu50.bin`
  (`43dd82bb…`) and `graph-lux4.bin` (`fd92a735…`) are routing-identical on every array
  `find_journey` reads (`routing_identical`, both verified against their sidecars). It compares
  artifacts only and computes no journey, so it stays inside the seam; the runner's G2 re-runs it.

## Step 2, continued — the first build run was REFUSED by acceptance, on a defect in my bound

**What happened.** `LBD-A0V`'s census build, all three `LBD-AM5-4` fame checks, and the structural
comparison passed; then `check_acceptance` refused the listenable map: *"edge count 1569214 outside
bounds [1052547, 1470950]"*. Nothing was serialised; `LBD-A5V` never started.

**Diagnosis: a unit error in the scaled criteria, not a property of the map.** The census reported
784,607 edges and the refusal 1,569,214 — exactly twice. `hub_stats` counts each connection once
(degree sum / 2); `Graph.edge_count`, and every sidecar's `"edges"` (the served map's 1,315,684
included), count CSR entries in both directions. My physical upper bound, "every node of `V` at the
ceiling", was written `N × c / 2` — connections counted once — and compared against a
both-directions count. In the right unit it is `N × c` = 2,941,900. The lower bound (0.8 × the
sidecar's count) was already in the right unit.

**Why correcting it is not fitting a bound to a build** (`acceptance.py`'s own test: is the new bound
derived from something known independently of the build that went red?): the corrected value comes
from the ceiling and the sidecar's unit, both known before any build, and it is the same physical
ceiling the first draft described in words; the build's 1,569,214 played no part. The refusal also
shows this instrument can go red. **Recorded rather than quietly fixed**, and the result JSON now
names both units, because the same two currencies will otherwise be compared in the README.
