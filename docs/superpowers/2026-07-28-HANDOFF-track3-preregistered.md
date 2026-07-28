# Handoff — ASC-5 discharged and Track 3 pre-registered, 2026-07-28

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-07-25-HANDOFF-track2f-and-headroom.md`](2026-07-25-HANDOFF-track2f-and-headroom.md) on next
actions, and [`2026-07-28-HANDOFF-redesign-deployed.md`](2026-07-28-HANDOFF-redesign-deployed.md)
**as the document to read first only** — that is a different body of work, this discharges none
of it, and what it says is still owed (the `--prune` pass, the queued use-the-app test, the
iPhone script) is still owed. It does **not** state project status: for that read
[`NEXT.md`](NEXT.md), which owns it.

**This is a seam handoff, not mid-flight.** The work concluded: the ASC-5 re-reads ran with
all gates passing, and the Track 3 pre-registration is committed. Nothing is in flight, no
subagent is running, no server is up. PR **#45** (draft) carries the branch
`asc5-path-ascent-reread`.

## What the successor executes

**Track 3, from [`specs/2026-07-28-track3-depth-descent-preregistration.md`](specs/2026-07-28-track3-depth-descent-preregistration.md), read cold and in full.**
Discharge order is explicit in its §4: **DD-P2 (pair set) → DD-P1 (headroom) → DD-P3
(analyst review) → DD-P4 (harness)** — then and only then arms. The document was written
for a cold reader; where this note and it disagree, it wins.

## Which documents changed direction, and must not be reverted

- **The pause is over** — owner decision 2026-07-28, recorded in the execution log §0.
  `NEXT.md`, `CLAUDE.md`'s orient row, and `memory/` were all corrected; a well-meaning
  editor restoring "PAUSED" from an older copy would be reverting a decision.
- **Famous-pair first-path fame is barred as a criterion** (PLA-R1: structurally unable to
  move). Do not let it back into any future pre-registration, including the rescale's.
- **The nameless-artist decision is MADE: drop, not backfill** — recorded at the tripwire
  (`acceptance.py`). The check stays until the drop rule lands; do not weaken it.
- `findings/2026-07-25-router-ascent-gradient.md` §4 carries the discharge note;
  `docs/README.md` carries the analysis directory's authoritative row. Both already done —
  do not re-edit.

## What I know that was not yet in the durable record (now folded in here)

- **DD-P1's instrument mostly exists**: `asc5_path_ascent.py`'s `bfs_dist` is the geodesic
  half; headroom needs the same BFS on the induced subgraph (top-decile removed, exclusions
  applied) plus P walks on the 8 new pairs (`run_arms.py --arms P` with the new pair list).
- **DD-P4 is an extension, not a rewrite**: the toll lands in the committed
  `2026-07-23-track2-sweep/mirror.py` behind a config field defaulting off; DD-G1 re-runs
  the byte-identity gate because the file gains a term.
- **The fame cache** (`2026-07-24-track2-arm-scorer/fame_cache.json`, 172 entries) covers
  the Track 2 pairs' interiors; the new mid-band pairs will fetch — budget network time,
  and DD-G4 (MBID keying) must land **before** that fetch, not after.
- The serialization defect and the P1/P2 ordering defect are both logged (execution log
  §4, §6) — neither has residue.
