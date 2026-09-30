# DSL runner brief — mechanics only

You are running a blind evaluation. **Say nothing to the owner beyond these mechanics.** You are
deliberately not told what anyone expects, and you must not go looking. There is no second one of
you: anything that unblinds you ends the listen.

## Do not read

- `docs/superpowers/findings/`, `docs/superpowers/NEXT.md`, and any handoff or execution log under
  `docs/superpowers/`
- `docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md`
- everything under `exploration/`
- anything under `builder/analysis/` whose directory name contains `drp` **other than this one**, and
  anything under `builder/analysis/2026-09-22-lba-a6-blind-listen/` except as this brief's commands
  import it
- GitHub issues and pull requests for this work (#200, #244, #249, #137 and their PRs)
- **`dsl_prescreen.json`, `dsl_prescreen.md` and `dsl_prescreen.py`** in this directory: they record,
  per pair and depth, what each side's journey looked like. Matching them against the page unblinds
  the listen.
- anything under `.superpowers/dsl/`, and `dsl_result.json` if it ever exists

This brief is self-contained. **Safe to view:** `dsl_pairs.json` (endpoint names only),
`dsl_page_data.json` (what the page shows), and `dsl_verdicts.json` (his answers — only in step 4's
smoke check and step 7's completeness check).

**No Spotify, monthly-listener or ListenBrainz lookups by you or on the owner's behalf.** You do not
unblind. A further fresh session does that after you have stopped.

## Where to work

**One worktree, and it must outlive you.** The sealed side mapping is written inside the tree you
run in, it is gitignored, and the write-up session reads it from there:

```bash
git -C C:/dev/music-app fetch
git -C C:/dev/music-app worktree add C:/Users/charl/worktrees/music-app-dsl-runner -b dsl-listen-run origin/main
```

(If the owner tells you the preparation branch is not merged yet, branch from the branch he names
instead.) **Do not remove this worktree.** Work from its `api/`, whose environment runs this harness.
Prefix every uv command with `UV_LINK_MODE=copy`, and use `PYTHONIOENCODING=utf-8` on anything that
prints names. The two graph artifacts are read by absolute path; you do not copy them.

## Steps

1. **Preflight.** `git status --short` is clean, and
   `UV_LINK_MODE=copy uv run --extra dev pytest ../builder/analysis/2026-09-30-drp-stage5-listen -q`
   passes.

2. **Generate.**
   `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_generate.py`
   - It loads two large graphs and routes 16 journeys to twenty presses each; allow several minutes.
   - It checks its gates and stops with its own message if one fails. **A `SystemExit` carrying one
     of its messages is the experiment speaking: stop, report the message to the owner verbatim, and
     do not work around it.**
   - **Lines saying a slot was "replaced by a reserve" are normal**, not failures. Report nothing
     about them.
   - **"reserves are exhausted"** is a normal outcome, not a fault: report it and wait for the owner.
   - **A Python traceback is not a gate.** An `AttributeError`, `TypeError`, `KeyError`,
     `ImportError` or similar is a wiring fault: report it verbatim, say it is a harness fault rather
     than a result, and let the owner hand it to another session. **Do not debug it and do not look
     at any journey while diagnosing it.**

3. **Clips — just before serving.** Preview links expire after about fifteen minutes.
   `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_clips.py`
   Some artists resolve to nothing. That is expected, and the page shows "no clip found" on those
   cards. It prints silent card slots for L and R. **Mention this to the owner only if one side is
   conspicuously emptier than the other.**

4. **Smoke test.**
   `UV_LINK_MODE=copy uv run python ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_page.py`, then
   open `http://127.0.0.1:8765/` in a real browser yourself and confirm:
   - the page renders, and at least one clip plays; on a card with more than one track, "another
     track" switches it;
   - every middle card has an "I know this artist" tick, and there is a "this step doesn't fit" tick
     between every two cards, including next to the first and last artist;
   - **the "can you tell which side is the new version" question is hidden until both the coherence
     and novelty answers are chosen on that row, and appears once they are;**
   - answering everything, ticking one "I know this artist" and one "this step doesn't fit", ticking
     "I have marked every artist I know on this row", then pressing the page's own "save row" button,
     writes through (read `dsl_verdicts.json`: the row holds the two marks);
   - **a row with a pick but no strength refuses to save, and so does a row with no new-version
     answer, and so does a row without the "I have marked every artist I know" tick;**
   - after stopping and restarting the server, `GET /status` no longer lists that row, and reloading
     the page shows it as saved.

   Then stop the server, **read the whole of `dsl_verdicts.json` to confirm it holds only your
   smoke-test answer, and delete it** so the owner starts clean. Re-run step 3 if more than a few
   minutes have passed, then start the server again.

5. **Hand the owner exactly this and nothing else:**
   > "The listen is at http://127.0.0.1:8765/. Work top to bottom. As you listen, tick 'I know this
   > artist' on every middle card you recognise, and 'this step doesn't fit' wherever the journey
   > jumps somewhere it shouldn't. Each row then asks which side holds together better and which
   > gives you more new artists, how strong each pick was, and — once those are answered — whether
   > you can tell which side is the new version. A row will not save until all of that is answered
   > and you've ticked that you marked every artist you know. Clips expire after about fifteen
   > minutes — tell me when you take a break or come back and I'll refresh them. Sittings can be
   > split between pairs; saved answers persist."

6. **Refreshing clips, whenever he asks or returns from a break:** stop the server, re-run step 3,
   start the server again, and tell him "clips refreshed — reload the page." Saved answers survive
   this, but ticks on a row he has not yet saved do not, so ask him to save any row he is part-way
   through first. A page reload alone does not refresh clips.

7. **Wait.** When he says he is done, `GET http://127.0.0.1:8765/status`. If it is not complete, tell
   him which rows are missing and wait. `/status` is the authority on completeness. **Never
   summarise, never react to an answer, never compute or mention a tally, and never answer a question
   about which side is which.** You do not know, and the file that does stays shut.

8. **Stop the server and commit the answers and the stimulus as presented**, then push:
   ```
   git commit -m "DSL-: the owner's answers, as saved by the page, and the page data" -- ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_verdicts.json ../builder/analysis/2026-09-30-drp-stage5-listen/dsl_page_data.json
   git push -u origin dsl-listen-run
   ```
   (Both files are new, so `git add` them by path first.) Report to the owner only: **"the answers are
   committed on `dsl-listen-run`; the unblind and the write-up belong to a fresh session, which works
   in `C:/Users/charl/worktrees/music-app-dsl-runner` because the sealed mapping is there."** Then
   stop. **Do not run `dsl_unblind.py`.**
