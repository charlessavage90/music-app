# Handoff — #200 depth-remedy pre-registration committed and critiqued, 2026-09-27

**Role: SUPERSEDED 2026-09-27 (later) on NEXT ACTIONS ONLY** by [`2026-09-27-HANDOFF-drp-amendments.md`](2026-09-27-HANDOFF-drp-amendments.md): `DRP-AM1` is written and the design has been amended through `DRP-AM6`. Its decisions list still stands. Supersedes
[`2026-09-25-HANDOFF-lba-a6-deploy.md`](2026-09-25-HANDOFF-lba-a6-deploy.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** This is a clean handover point: the governing document is committed, and so is its
stage-1 critique. Nothing is in flight: no background job, no server, no half-written file. Branch
`charlessavage90/issue-200-depth-remedy-prereg`, PR #245, tracking issue #244 (these are addresses;
`gh` owns the state). No arm has run, no `DRP-` pair has been drawn, and no default or shipped code
has changed.

**The next action is a session's: write amendment `DRP-AM1`.** It folds the `ml-graph-analyst`
critique ([`../../builder/analysis/2026-09-27-drp-prereg-critique/README.md`](../../builder/analysis/2026-09-27-drp-prereg-critique/README.md),
14 findings `DRP-AM1-F1`–`F14`, 6 observations) into
[`specs/2026-09-27-issue-200-depth-remedy-preregistration.md`](specs/2026-09-27-issue-200-depth-remedy-preregistration.md)
§14. That is methodology, so it is yours, not the owner's. Per §11's rule, quote each changed clause's
original wording beside the change. **Nothing had run when the critique was written, so nothing's
commit-before-results property is spent.** After it is committed: the owner's go on the amended
design (§8 stage 2).

**Verified by this session against the probe outputs:**
- F1 (`U` = 0.0012, so `N_noise` falls back to 0.015 and `DRP-G6` cannot fire);
- F2 (35 of 40 replication pairs sit above 0.985 in the depth window, so RISES is unreachable);
- F8 (partner headroom, 85.8 %).

F4 and F6 follow by arithmetic from the document's own text. **The other nine findings are relayed
unverified: check each against source before acting on it** (`session-start`, "verify one claim").

**Decisions taken here, not to be reverted by a well-meaning editor:**
- **The lattice is 2 supply × 3 pricing.** The owner added a gated-supply arm mid-session and then
  withdrew it into a pre-committed amendment slot, `DRP-SW` (§2.10). **It is not an arm.** Build
  nothing for it and write no harness code for it. Its trigger and its deploy obligation live in
  §2.10, and the reasons it is deferred are in §2.9.
- **Supply adds edges above the ceiling.** It does not reserve slots inside it, so every shipped
  edge survives: the node set, `pop_raw` and the fame frame are unchanged by construction, and
  `DRP-SW` stays buildable. Reasoning: §2.3.
- **The depth window is presses 7–10**, because the floor is zero there for every pair by
  arithmetic (the critique's F-series confirms this, as its `DRP-Q2` answer).
- **Primary currency is plain fame percentile**, not `JFX-AM1`'s log (§3).
- **Stage 3 outputs never name an interior artist** (§8 sealing). That protects both the owner's
  use-gate criterion and the listen.

**Owed by the owner, not by a session:**
- **His use-gate criterion** (§9, OWED). No journey from any cell may be shown to him until it is
  committed. This session gave him five questions to answer and deliberately drafted no wording; it
  must land verbatim.
- **His go at stage 2.**

**Corrected this session:** `NEXT.md`'s parked pricing track said a successor "must consume
`TB-P5H-7`". `NEXT-ARCHIVE.md` records that item discharged by `CRE-` on 2026-08-03; the line now
says its substance binds (carried here as `DRP-C2`).

**What is not in the durable record:** nothing. The owner's two mid-session instructions (add the
gated arm, then defer it) are embodied in §2.9–§2.10, not quoted, because they are design changes,
not rulings.
