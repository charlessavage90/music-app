# Execution log — `DRP-` stage 3a, the instruments (#200)

**Role: ACTIVE — the retained execution log for stage 3a** of
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
(`DRP-`), §8. Appended per task. It owns no status (`NEXT.md` does) and restates no figure the
committed outputs own: each entry points at its output file.

**Governs:** the pre-registration's body (execute-from-body since `DRP-AM5`). **Go:** the owner's
stage-2 go, 2026-09-27, in session ("Just go as designed", after being shown §10's weakest link and
the option of stopping at Seam A); relayed to
[#244](https://github.com/charlessavage90/music-app/issues/244#issuecomment-5861972775) by this
session. ⚠ `DRP-AM5-I2` says his go lands on #244 **posted by him**; the session's relay does not
meet that, and the owner has been asked to post his own line. Until he does, cite the relay as a
relay.

**Seam A (the end of this log's scope):** every gate outcome (`DRP-G1`, `G1r`, `G2`, `G3`, `G6`,
`G7`, `G10`), the `DRP-S1` artifact sha and `N_noise` committed. Nothing in 3b–3d runs from this
session's context unless the seam is crossed cleanly.

**Code and outputs:** [`builder/analysis/2026-09-27-drp-stage3a/`](../../builder/analysis/2026-09-27-drp-stage3a/).
Gitignored state (the `DRP-S1` artifact, the build capture, anything name-bearing past the
endpoints) lives under `C:\unsung-fast\drp-stage3a\`; its sha256s are committed.

---

## Task 1 — the pair set (§4). 2026-09-27

- `drp_pairs.py` drew `DRP-T1`, `DRP-T2`, `DRP-MID` (40 each, seed 20260928, §4's rule) and
  regenerated the `DRP-C8` replication set (graph-descriptives' FAMOUS draw, seed 20260927).
  Output: `drp_pairs.json` (endpoints only: node ids, MBIDs, names, percentiles). Its sha256 is
  printed by the script and recorded in the commit that adds it.
- **Committed before any cell is swept**, as §4 requires. No journey was routed to draw it.
- Snyk code scan of the directory: 0 issues.
