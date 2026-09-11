# LBL runner brief — listen 1, mechanics only

You are running a blind evaluation. **Say nothing to the owner beyond these mechanics.** You are
deliberately not told what anyone expects, and you must not go looking. **Do not read:**
`docs/superpowers/findings/`, `docs/superpowers/NEXT.md`, any handoff or execution log under
`docs/superpowers/`, `docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`,
anything under `builder/analysis/2026-09-10-lbd-served-population/`, `lbl_maps.json`, or anything
under `.superpowers/lbl/`. This brief is self-contained. `lbl_listen1_page_data.json` is safe to view.

**No Spotify, monthly-listener or ListenBrainz lookups by you or on the owner's behalf until step 9.**

Work in the worktree `C:\Users\charl\worktrees\music-app-lbd-listen`, from `builder/`. Prefix every
uv command with `UV_LINK_MODE=copy`, and use `PYTHONIOENCODING=utf-8` on anything that prints names.

1. **Preflight.** `git status --short` is clean on branch `lbd-listen`, and
   `UV_LINK_MODE=copy uv run --extra dev --with duckdb pytest analysis/2026-09-10-lbd-blind-listen -q`
   passes.

2. **Generate.**
   `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-09-10-lbd-blind-listen/lbl_generate.py --listen 1`
   - It checks six things and stops with its own message if one fails. **A `SystemExit` carrying
     one of its messages is the experiment speaking: stop, report the message to the owner
     verbatim, do not work around it.**
   - **Lines saying a slot was "replaced by the next reserve" are normal**, not failures — the
     script swaps a pair it cannot use for a pre-committed reserve by itself. Report nothing about them.
   - **If it stops with "reserves are exhausted"**, that is a normal outcome, not a fault: report it
     and wait for the owner to supply a pair.
   - **A Python traceback is not a gate.** An `AttributeError`, `TypeError`, `KeyError`,
     `ImportError` or similar is a wiring fault in the harness: report it verbatim, say it is a
     harness fault rather than a result, and let the owner hand it to another session. **Do not
     debug it yourself and do not look at any journey while diagnosing it** — you would stop being
     a blind runner, and there is no second one of you.

3. **Clips — just before serving.** Preview links expire after about fifteen minutes.
   `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-09-10-lbd-blind-listen/lbl_clips.py --listen 1`
   Some artists resolve to nothing; that is expected. It prints silent card slots for L and R —
   **mention it to the owner only if one side is conspicuously emptier than the other.**

4. **Smoke test.**
   `UV_LINK_MODE=copy uv run python analysis/2026-09-10-lbd-blind-listen/lbl_page.py --listen 1`,
   then open `http://127.0.0.1:8765/` in a real browser yourself and confirm: the page renders; at
   least one clip plays; on a card with more than one track, "another track" switches it; **answering
   both questions on one row and pressing the page's own "save row" button writes through** (read
   `lbl_listen1_verdicts.json` to see it); after stopping and restarting the server, `GET /status`
   no longer lists that row. Then stop the server, **read the whole of `lbl_listen1_verdicts.json`
   to confirm it holds only your smoke-test answer, and delete it** so the owner starts clean.
   Re-run step 3 if more than a few minutes have passed, then start the server again.

5. **Hand the owner exactly this and nothing else:**
   > "The listen is at http://127.0.0.1:8765/. Work top to bottom: answer both questions and save
   > every row, then save each pair. Clips expire after about fifteen minutes — tell me when you
   > take a break or come back and I'll refresh them. Sittings can be split; saved answers persist."

6. **Refreshing clips, whenever he asks or returns from a break:** stop the server, re-run step 3,
   start the server again, and tell him "clips refreshed — reload the page." Saved answers survive
   this; a page reload alone does not refresh clips.

7. **Wait.** When he says he is done, `GET http://127.0.0.1:8765/status`. If it is not complete,
   tell him which rows or pairs are missing and wait. `/status` is the authority on completeness,
   not a read of the file. **Never summarise, never react to an answer, and never answer a question
   about which side is which** — you do not know, and the file that does stays shut until step 9.

8. **Stop the server and commit the answers and the stimulus as presented**, then push:
   ```
   git commit -m "LBL- listen 1: the owner's answers, as saved by the page, and the page data" -- analysis/2026-09-10-lbd-blind-listen/lbl_listen1_verdicts.json analysis/2026-09-10-lbd-blind-listen/lbl_listen1_page_data.json
   git push
   ```
   (`git add` those two paths first if git reports them untracked.)

9. **Unblind.**
   `UV_LINK_MODE=copy uv run python analysis/2026-09-10-lbd-blind-listen/lbl_unblind.py --listen 1`
   Commit `analysis/2026-09-10-lbd-blind-listen/lbl_listen1_result.json` the same way and push.
   Report to the owner only: **"the answers and the mechanical tally are committed; the write-up
   belongs to a fresh session."** Then stop.
