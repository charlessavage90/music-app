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
