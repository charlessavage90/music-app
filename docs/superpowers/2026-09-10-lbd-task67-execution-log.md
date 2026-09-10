# `LBD-` Tasks 6–7 — retained execution log

**Role: RETAINED EXECUTION LOG for the `LBD-` build stage (plan Tasks 6 and 7, under
`LBD-AM4`). ACTIVE. Owns no figures** — `builder/analysis/2026-09-10-lbd-supply/README.md`
owns the build-stage figures and `builder/analysis/2026-09-08-lbd-similarity/README.md` §6c
owns the threshold curve. Decisions and reasoning, not narration; appended per task so a
successor can pick up at any seam. Continues
[`2026-09-08-lbd-task34-execution-log.md`](2026-09-08-lbd-task34-execution-log.md), which
closes at the Task 4 owner stop.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
with `LBD-AM4` (its §10 block and §12 row). The plan's Tasks 6–7 are executed as amended;
the plan is not edited. Branch `lbd-build`, worktree `C:\Users\charl\worktrees\music-app-lbd-build`.

## Session opening — what was verified before anything was written

- **Repo state:** `origin/main` at `8aef76a` (PR #113 merged 2026-09-10); no other session's
  changes in the main tree; worktree cut from `origin/main`.
- **Checksums, all matched the handoff's record before any file was read:** `T.parquet`
  `03d47b05…`; `A0.parquet` `f9bd1f83…`; `A2.parquet` `34f92de7…`; `cxr_added_mbids.txt`
  `bfed95ef…`; `cxr_preexisting_mbids.txt` `768054b7…`; `cxr_residual_mbids.txt` `fa8d85cc…`;
  `artist_identity.parquet` `02b4c8dd…`; `graph-cxa-adopted.bin` `bc0431c4…` against its
  sidecar. `A3.parquet` was **not** verified because nothing here reads it (`LBD-AM4-2` bars
  it from building).
- **Grepped before use** (the plan's own claims list, re-resolved in this worktree):
  `FIELD_MBID/NAME/SCORE/COMMENT` and `ListenBrainzSource` (`name`, `edge_type`,
  `request_url`, `parse`, `_rows`) — `sources/listenbrainz.py:19-22, 54-100`;
  `harvest_identities` — same file, reads `name`/`comment` from neighbour rows;
  `similar_prefix` — `pipeline.py:131`; `build_from_archive` — `pipeline.py:169`, the
  nameless drop at 235–246, the `PopulationNotCensused` guard at 303–320, the cap ranking on
  unclipped strengths at ~380; `CANDIDATE_ALGORITHM` — `config.py:26`; `drop_unlistenable`
  (243), `unlistenable_list_path` (259), `require_fame` (132), `union_top_j`/`union_degree_ceiling`
  (107–108); `load_unlistenable_list(algorithm, override_path)` — `unlistenable_drop.py:151`
  and its `UnlistenableList.censused_mbids`; `LocalArchive` — `archive.py:28`; the bridge-arm
  config — `dcf_ceiling_sweep.py:401-407` (`algorithm=CANDIDATE_ALGORITHM`, `require_fame=False`,
  `drop_unlistenable=ulf_path is not None`, `unlistenable_list_path=ulf_path`) and its
  `ReadOnlyArchive` (110–132) and `verify_against_sidecar` (135–155); the `c2a` degree SQL
  — `lbd_reads.py:219-234`, reused verbatim for the curve.
- **One thing the plan says that is no longer how it reads:** Task 6 pins
  `unlistenable_drop_algb_20260805.json`. That is the current default, it censuses 75,000
  artists, and over the fixed population it leaves 29,837 uncovered and would refuse. The
  bridge arms' `20260809` payload is what covers `P`; `LBD-AM4-3` records the measurement.

## Step 1 — `LBD-AM4`, written and committed before anything was emitted

**The decision that shapes everything else: the population is fixed to the `CXA` node set.**
The plan's Task 7 builds over whatever population the arm's pair table names, which the
review measured as a confound in the flattering direction (`LBD-X2`). The ceiling probe had
already shown the alternative: its §4 bridge arms applied the re-censused drop list through
the shipped override and reproduced the `CXA` population to the node, landing on `CXR-P2`'s
ruler. The emitter here does the same thing one step earlier — it never writes an artist or
a neighbour outside `P` — so the drop lists become inert by construction rather than by
luck, and each arm differs from the bridge control in the data alone.

**Measured before writing, not assumed:** the `20260809` payload's censused set covers all
88,685 nodes (0 uncovered), and each of the three drop lists intersects `P` in 0 artists.
So `drop_unlistenable=True` through the override is safe and holds the served map's
filtering constant; this supersedes `LBD-X3`'s `False` for `P` only, and the amendment says
why `LBD-X3` is still right for any other population.

**Why `A3` is barred and `A1` is merely not built.** `A3`'s partner counts (README §6) put its
archive at both directions of every row of `T` held as Python objects in the builder's first
pass — not buildable here — and its pair-level movement on the stratum this track exists for
is within a tenth of a point of `A2`'s. `A1` did not clear `LBD-G2` on the whole set at the
pair level, and a graph-level figure is bounded above by the pair-level one, so building it
cannot change the decision; it stays available.

**Why the population restriction is applied after the rank cut, not by re-ranking inside
`P`.** The arm is defined by §1 as a filter and window over `T` on the full corpus; re-ranking
inside `P` would make "`A0`" a different object from the one `LBD-C2a` was read on. The
emitter filters the sha-pinned derived parquet, so the arm keeps its meaning and the
population becomes the one column that moved between Task 4's read and this one.

**The threshold curve is descriptive and says so three times** in the amendment, because the
obvious misreading — "the curve picked threshold 2" — is a decision the owner has not made.
Its green check is built in: threshold 10 / limit 100 must reproduce README §6's `A0` row and
threshold 0 / limit 100 its `A2` row, or the instrument is wrong.

**Where outputs land:** `C:\unsung-fast\lbd-archives\<arm>\` (NVMe; 88k small files per arm
is the wrong shape for the spinning disk the plan named), consistent with the staging
approval the 2026-09-10 handoff records.
