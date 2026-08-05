# CAU- coherence audit — how to run it

Governing document:
`docs/superpowers/specs/2026-08-04-coherence-audit-preregistration.md`, frozen before
generation and amended four times before any judgement existed. It wins wherever this
brief disagrees.

**The page is already built.** `cau_build.py` has run; the stimulus and its sealed control
map are on disk. **Do not run `cau_build.py` again** — it would redraw the controls, and
the draw that has been sealed is the one the readings are defined against.

---

## Start it

From `builder/`, in **any** shell — cmd, PowerShell or bash:

```
uv run --extra dev python -u analysis/2026-08-04-coherence-audit/cau_page.py
```

Then open `http://127.0.0.1:8766/`.

> **No `UV_LINK_MODE=copy` / `PYTHONIOENCODING=utf-8` prefix here, deliberately.**
> `VAR=value cmd` is bash syntax and fails in cmd.exe with *"'UV_LINK_MODE' is not
> recognized as an internal or external command"* — which is exactly what happened to the
> owner when this brief was first written in bash form. Neither variable is needed for these
> commands: `UV_LINK_MODE` only suppresses a warning (uv copies by itself since the move off
> OneDrive), and `PYTHONIOENCODING` only matters for scripts that **print artist names**,
> which the server does not. If you ever do need one: cmd `set VAR=value` on a preceding
> line, PowerShell `$env:VAR='copy'`.

Nothing else is running and nothing else needs to be. **There is no clip playback here and
that is deliberate** — a 30-second preview is the instrument this audit exists to replace.

## What you are doing

Sixteen journeys, shown whole, in shuffled order with no labels. Each interior card asks
one question:

> **Does this artist belong on this journey?** — fits / doesn't fit / can't tell

- **Judge the artist against the journey**, not just against the two cards beside it.
- **If you cannot place an artist, go and listen to them properly** — Spotify or anywhere,
  several tracks, as long as it takes. That is the point of the exercise, not a fallback.
- **Tick "I had to look them up"** when you did. It is a declared denominator: results are
  reported both over everything and over the looked-up subset, because the looked-up set is
  the harder population and reporting either alone would mislead.
- Every card carries its **MBID and a MusicBrainz link**, plus a disambiguation where one
  exists. Use them — artist names are not unique, and the app's own name-based lookup picks
  the wrong same-named artist about one card in eleven.
- Endpoints are the two artists you picked. They are shown for context and never judged.
- There is a free-text box per journey for whole-path impressions. **It is not scored** and
  no criterion will be invented from it after the fact.

Judgements save the moment you pick a radio button, and survive stopping the server. Split
it across sittings freely.

## Two things you should know, and neither is a hint

**Some cards are deliberately wrong.** Twelve random artists have been inserted, drawn from
the same graph and matched for obscurity so you cannot spot them by fame, and each sits at
least three hops away from the cards on either side of it. **If you do not reject at least
10 of the 12, the audit declares itself void** — that is the check that stops a green result
meaning nothing. Judge normally; do not go hunting for them.

**You will not be told which cards were excluded from scoring.** Each inserted artist sits
next to exactly one real card, and that real card was judged next to something fake, so it
is dropped. Twelve of the 65 real cards go this way, leaving 53 scored. Fixed in advance.

## When you are done

```bash
curl -s http://127.0.0.1:8766/status
```

`complete: true` means all 77 cards and all 16 journey notes are in. **A partial run
licenses no read** — the scorer refuses rather than reporting a smaller audit.

Then stop the server and hand back. **A fresh session scores and writes it up** — the
reader of results should not be the session that ran them.

## For whoever scores it

```
uv run --extra dev python -u analysis/2026-08-04-coherence-audit/cau_score.py
```

`CAU-G1` is evaluated first and alone; if it fails, nothing else is computed.

**⛔ `cau_owner_notes_SEALED.md` is sealed until your analysis is written AND committed.** It
holds the owner's strong opinions about where this should go — not impressions of what he
heard — and he asked for this ordering himself. Write your own read, commit it, *then* open
the note and respond to it in a separately headed section. Do not silently revise the
analysis above it. Full reasoning in the handoff.

Afterwards,
**remove the `cau_page_data.json` line from `.gitignore` and commit that file** — it is the
stimulus as presented and the judgements cannot be interpreted without it. It is held back
only until the run is over, because diffing it against `gbl_page_data.json` would reveal the
inserted artists.
