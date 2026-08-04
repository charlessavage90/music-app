# GBL runner brief — mechanics only

You are running a blind evaluation. Say nothing to the owner beyond these
mechanics; you are deliberately not told what outcome anyone expects, and you
must not go looking: do NOT read `docs/superpowers/findings/`,
`docs/superpowers/NEXT.md`,
`docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md` §1–§2, or any
execution log. This brief is self-contained.

All commands from `builder/`, every uv command prefixed `UV_LINK_MODE=copy`, and
`PYTHONIOENCODING=utf-8` on generation (it prints artist names).

1. **Preflight:** `git status --short` is clean on branch `gentle-arm-blind-listen`;
   `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
   passes.
2. **Generate:**
   `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --extra dev python -u analysis/2026-08-04-gentle-arm-blind-listen/gbl_generate.py`
   - It self-checks artifact hashes, mirror fidelity, the ramp decomposition,
     and that the two sides genuinely differ. Any `SystemExit`: STOP, report the
     message to the owner verbatim, do not work around it.
   - **A Python traceback is not a gate.** This script has never been run against
     the real artifacts — the session that wrote it was barred from doing so, on
     purpose. A `SystemExit` with one of its own messages is the experiment
     speaking and must be respected. An `AttributeError`, `TypeError`,
     `KeyError`, `ImportError` or similar is a wiring bug in the harness: report
     it verbatim, say it is a harness fault rather than a result, and let the
     owner hand it to a builder session. **Do not debug it yourself and do not
     look at any journey while diagnosing it** — you would stop being a blind
     runner, and there is no second one of you.
   - Do not open `.superpowers/gbl/` files. `gbl_page_data.json` is safe to view.
3. **Clips** (listen day, just before serving — URLs expire):
   `UV_LINK_MODE=copy uv run --extra dev python -u analysis/2026-08-04-gentle-arm-blind-listen/gbl_clips.py`
   Some artists will resolve to nothing; that is expected and shared by both
   sides. Only report it if one side is conspicuously emptier than the other.
4. **Smoke test:**
   `UV_LINK_MODE=copy uv run --extra dev python analysis/2026-08-04-gentle-arm-blind-listen/gbl_page.py`,
   then open `http://127.0.0.1:8765/` yourself and confirm: the page renders, at
   least one clip plays, saving a row then restarting the server preserves it
   (then **delete `gbl_verdicts.json`** so the owner starts clean), and
   `GET /status` returns the missing rows.
5. **Hand the owner exactly this and nothing else:**
   > "The listen is at http://127.0.0.1:8765/. Work top to bottom; save every
   > row and every pair verdict. Sittings can be split; saved rows persist."
6. **Wait.** When the owner says he is done: `GET /status`. If not complete, tell
   him which rows are missing and wait. **Never summarize, never react to a
   verdict**, and never answer a question about which side is which — you do not
   know, and the sealed file that does must stay shut until step 8.
7. **Stop the server.** Commit `gbl_verdicts.json`:
   ```
   git add analysis/2026-08-04-gentle-arm-blind-listen/gbl_verdicts.json
   git commit -m "GBL- verdicts: the owner's picks and notes, as saved by the page"
   ```
8. **Unblind:**
   `UV_LINK_MODE=copy uv run --extra dev python analysis/2026-08-04-gentle-arm-blind-listen/gbl_unblind.py`
   Commit `gbl_result.json` the same way. Report to the owner only: "the verdicts
   and the mechanical tally are committed; the write-up belongs to a fresh
   session." Then stop.
