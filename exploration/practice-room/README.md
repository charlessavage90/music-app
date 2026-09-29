# Practice room (EXPLORATORY)

A local page where you type any two artists and press Dig deeper **side by side** on today's app and
several alternative routers, with 30-second clips. Built 2026-09-28/29 for the Dig-deeper exploration
(`../REPORT.md`). **Nothing it shows is evidence**: it is for hearing variants, not measuring them.

## Start it

```
cd <worktree>\api
$env:PYTHONIOENCODING="utf-8"; uv run python -u ..\exploration\practice-room\server.py
```
Open **http://127.0.0.1:8765** (about 30 s to load the map). Options, set before starting:
- `$env:PR_ALL="1"` adds the four runners-up as extra columns.
- `$env:PR_PORT="8766"` serves on another port, e.g. to test a change while another copy is running.

It needs the api package's environment (`api/.venv`), the served map at
`C:\dev\music-app\builder\scratch\graph-lba-a6.bin` (verified by sha256 at load, via
`builder/analysis/2026-09-27-drp-stage3a/drp_common.py`), and `../kit/qlook.py` for the shared map
loader. Search and clips reuse the api's own `ArtistSearch` and `ClipResolver` by import; nothing in
`api/` is modified. Clips need internet access (Deezer, then iTunes).

**Where the files live:** this folder exists only on branch
`charlessavage90/dig-deeper-exploration` (draft PR #264) until that PR is merged or closed. A future
session starts from that branch, or checks out `exploration/` from it.

## Using it

- Pick two artists, then **Build journeys**. Each column is one router.
- Press **Dig deeper** on any middle card in any column; columns are independent. **Undo press** and
  **Reset** act on one column. **Dig deeper everywhere** presses the most famous middle card in every
  column.
- The number beside each artist is its **fame percentile on the map** (100 = most listened among
  ListenBrainz users). It is *not* Spotify popularity; see the caution below.
- The **note box** under each column saves your note together with the exact journey on screen.

## What gets recorded (all committed; this is the owner's listening record)

- `logs/<date>.jsonl`: one line per journey shown and per note: time, column, pair, press number,
  who was dug past, every artist with fame, and the note text.
- `logs/<date>-notes.md`: the notes rendered readably, **verbatim**, each beside its journey. Regenerate
  with `python exploration/practice-room/notes_md.py <date>`.
- `../pairs-used.txt`: every pair built is appended once. **Formal testing must use pairs not in it.**

## Changing the columns

Edit `variants.py`. Each entry is `(id, column label, variant file under exploration/, one-line plain
description)`. A variant file defines `journey(ctx, s, t, pressed, prev) -> list[int] | None` (the
quick-look kit's interface; see `../README.md`) and optionally `setup(ctx)`. The server replays presses
in order to rebuild a journey, memoised, so a variant may depend on the previous journey (`prev`).

## Cautions for whoever reads the logs

- **The fame score mis-ranks some artists badly.** The owner found it on first use (notes, 2026-09-29).
  Examples: The Format scores 98.4 with 168k Spotify monthly listeners, while Royal Blood scores 86.5
  with 3.1M. Every router here steers by that score, so "less famous" on screen can still mean well
  known to a listener.
- Variants were tuned on the 20 kit pairs; pairs typed here are fresh ground for them.
