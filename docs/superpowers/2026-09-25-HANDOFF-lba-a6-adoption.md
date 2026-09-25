# Handoff — `LBA-G5` passed and `LBA-A6` adopted, 2026-09-25

**⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-25 by [`2026-09-25-HANDOFF-lba-a6-deploy.md`](2026-09-25-HANDOFF-lba-a6-deploy.md).** ~~ACTIVE — this is the CURRENT handoff. Nothing supersedes it.~~ Supersedes
[`2026-09-23-HANDOFF-lal-listen-read.md`](2026-09-23-HANDOFF-lal-listen-read.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** Everything is committed on `charlessavage90/candidate-map-adoption-decision`. Nothing
is in flight: no background job, and no server this session started. The retained log is
[`2026-09-21-lbd-s4-a6-adoption-execution-log.md`](2026-09-21-lbd-s4-a6-adoption-execution-log.md)
Task 6. This note is a delta against it.

**Which documents are now wrong, and in which direction**
- `infra/README.md` §4 still names `graph-lux4.bin` as the served artifact. That is **correct until
  the deploy**. Its ⚠ block says to correct it after the deploy, and the deploy session owns that.
- Every script under `builder/analysis/` that names `graph-msw-tu50.bin` as "the served map" is
  frozen and was correct when it ran. Leave them all.

**Overturned — must not be reverted by a well-meaning editor**
- **Search ranks an exact name match first.** Do not "simplify" it back to prefix-by-popularity.
  On this map, doing so offers Miles Davis Quintet before Miles Davis (Task 6, the e2e section).
- **`test_the_previous_served_map_and_the_fallback_are_outside_the_current_bounds` is kept on
  purpose.** #138 is closed by adoption, but rebuilding the old map (for example, to roll back)
  still needs the previous bounds restored first.
- **The landing constants follow the router.** Bad Bunny → Chappell Roan at 3 stops is measured,
  not a typo. Whether to keep that pair is #233, and it is his.

**Already updated, so do not re-edit:** `ApiConfig.graph_path`; the builder lineage comment;
`acceptance.py`'s resolution note; the candidate README banner; the two `docs/README.md` rows;
the pair log; the #200 comment.

**What is not in the durable record:** the two `LBA-G5` servers from 2026-09-24 (API :8000, Vite
:5173, started detached from `C:\dev\music-app`) were **stopped at this closeout**. They served
code older than this branch, and nothing queued needs them. `start-servers.ps1` in
`C:\unsung-fast\lbd-artifacts\lba-g5-logs\` brings them back, but it points at the candidate
file, not at `builder/scratch/`.
