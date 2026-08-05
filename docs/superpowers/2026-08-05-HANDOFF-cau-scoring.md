# Handoff — the `CAU-` coherence audit is scored and written up, 2026-08-05

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-05-HANDOFF-cau-audit-run.md`](2026-08-05-HANDOFF-cau-audit-run.md) on next actions.
It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam handoff.** The audit is scored, the analysis is committed, the sealed note is opened
and answered, closeout is run. Nothing is in flight, tree clean, no listener on any port.

**Branch** `gentle-arm-blind-listen`, draft PR #77.

---

## What is done

`CAU-` is complete. The results of record are
[`findings/2026-08-05-coherence-audit-results.md`](findings/2026-08-05-coherence-audit-results.md),
**which owns the `CAU-` figures** — cite it by section and never restate a number from it.
Reasoning: [`2026-08-05-cau-scoring-execution-log.md`](2026-08-05-cau-scoring-execution-log.md).
Governing document unchanged:
[`specs/2026-08-04-coherence-audit-preregistration.md`](specs/2026-08-04-coherence-audit-preregistration.md).

**The next action is the OWNER'S and it is a decision, not work** — the findings note's §4
options. No session owes anything.

## Which documents are now wrong, and in which direction

- **Nothing is stale in the direction of overstating.** `NEXT.md` is rewritten and its
  "after scoring" instruction is struck as discharged.
- **The `CAU-` build-and-run chunk has no retained execution log** and never will — see the
  scoring log §1. Its reasoning survives only in the handoff it wrote, the four amendments and
  the commit messages. **Do not backfill it**; reconstructing another session's reasoning from
  commits produces something that reads like a record and is a guess.

## Claims that must NOT be reverted by a well-meaning editor

1. **`CAU-C3` fired, and the findings note both reports its pre-registered reading and argues
   against it.** That is deliberate. Do not resolve the tension by deleting either half — the
   pre-registered sentence is the freeze evidence, and the notes contradict it. A later reader
   is entitled to weigh both.
2. **`D_all` is 53 and it is computed, not asserted.** Verified at `cau_score.py:66-68`. Do
   not "simplify" it to a constant.
3. **The 53 slots were never split by depth**, though the split is trivially computable and
   the owner raised a depth hypothesis after the fact. Refused as a post-hoc denominator. If a
   future session wants it, it needs its own pre-registration — it is not a bug that it is
   missing.
4. **The `GBL-` null is untouched.** Its run-once rule still binds. The owner's sealed note
   says he strongly prefers the rebuilt graph; that is recorded as **his statement** and is not
   a finding, and it does not reopen the null.
5. **Nothing above §5 of the findings note was revised after the sealed note was opened.** The
   owner's framing correction and the filter finding were appended as §6 rather than edited in.
   Preserve that boundary — it is the document's main integrity property.
6. **Nothing is adopted, no default was changed, and no shipped code was touched** by any part
   of `CAU-`.

## What has already been updated — do not re-edit

- `NEXT.md` — rewritten; carries the owner's parked frontier idea with his caveats attached.
- `docs/README.md` — four `CAU-` rows added (prereg, findings, both handoffs) plus this
  chunk's log. The map was missing the whole `CAU-` track until now.
- Two `GBL-` execution logs got the document role marker they lacked. Content untouched.
- `.gitignore` — the `cau_page_data.json` line is gone and the file is committed.

## What I know that is not in the durable record

**One thing, and it is a judgement rather than a fact.** The filter gap in the findings note's
§6 is, in my view, the most actionable thing this whole track produced — more than the
`CAU-C1` pass, which was won by one card. The note presents it as an option; I would put it
first. It is recorded there as a recommendation, so this is emphasis rather than missing
content, but the emphasis would not survive a summary.

**Nothing else.** No figure was computed and left unwritten; no option was entertained and
dropped without being logged in the scoring log §2.

## Owed, and by whom

Nothing is owed by this session. Two items remain open and **neither is `CAU-`**:

- The owner's 2026-08-04 **no-commercialization ruling** is in memory but still not in the
  repo record (it belongs in `PRODUCT-REQUIREMENTS.md`). Flagged at six consecutive closeouts.
- The eight **2026-07-22→27 `TEST-QUEUE.md` entries** remain `QUEUED` and unruled-on. Also six
  consecutive closeouts. **These need an owner ruling, not more work** — discharge or delete.
