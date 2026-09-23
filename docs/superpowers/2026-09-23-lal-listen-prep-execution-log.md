# Execution log — `LAL-` blind listen PREPARATION (`LBA-AM6-2`, `-11`; `LBA-AM7`), 2026-09-23

**Role: RETAINED EXECUTION LOG. ACTIVE. Owns no figures** — the pre-screen outputs own their counts
(`builder/analysis/2026-09-22-lba-a6-blind-listen/lal_am7_prescreen.json`, and the superseded first
run's `lal_prescreen.json`), and **both are MAP-LABELLED: a runner or write-up session must not read
them for the listen.** Governing text: `LBA-AM6` and `LBA-AM7` in
`specs/2026-09-14-lbd-s4-adoption-preregistration.md` §11. Branch `lba-a6-listen-prep`, PR #133.

**This session is barred from running the listen and from the write-up** (`LBA-AM6-5`): it ran the
pre-screens and a generation dry-run. It showed the owner endpoint names only — never an interior,
length or map.

## Decisions, with reasoning

1. **One ladder module (`lal_journeys.py`) imported by both the pre-screen and generation.**
   `LBA-AM6-2` step 6 requires the pre-screen to generate *"exactly as `LBA-AM6-3` will"*; a shared
   module makes that true by construction instead of by two copies agreeing. Listen 2 had the
   pre-screen import the generator; here the generator carries the sealing and page code, which the
   pre-screen has no business importing.
2. **Generation ASSERTS Gates D and N rather than substituting on them.** They are deterministic and
   were passed at the pre-screen, so a failure means the maps or the code moved — which is a stop,
   not a reason to reach for a reserve. Only (a), (b) and Gate L substitute (`LBA-AM6-3`).
3. **The unblind is the WRITE-UP session's alone** (`LBA-AM6-5`). Listen 2's runner brief had the
   runner run it; this brief stops at committing the answers. Consequence: **the runner's worktree
   holds the sealed mapping and must outlive the runner** — the brief names one fixed path and says so.
4. **Names, disambiguations and clip ids come from one source per ARTIST** (candidate artifact where
   it holds the artist, else served) — `LBA-AM6-6`'s "an artist sounds the same whichever map put
   them on the page". Listen 2 could use the served map for everything because every presented
   artist was in `V`; the candidate adds artists, so it cannot.
5. **`FORBIDDEN_PAGE_TOKENS` omits a bare `A6`** — it is a hex digraph and occurs inside MBIDs; the
   guard uses `lba-a6` and `candidate` instead.
6. **A `--dry-run` was added to generation and run by this session** after the strike: every gate,
   the page build and the leak guard, writing nothing. It spends nothing — the runner's own run deals
   sides afresh from a system random source — and it moves a wiring fault from listen day, where the
   runner may not debug, to here.
7. **The G6 Deezer-id refusal was run at preparation, before any journey**, so that if it would fire
   it fires where it costs nothing. It did not fire.

## Defect found in the plan — `LBA-AM6-2`'s pool premise, now `LBA-AM7`

Shown the first draw by endpoint name, **the owner did not recognise 11 of the 16 endpoints in the
eight pairs they occupied** — playlist singles. Verified in source: the pool
(`gbl_pair_candidates.json`, `GBL-` era) was ranked by minutes from Spotify's short
`StreamingHistory_music_0.json`; the premise *"both endpoints are artists he demonstrably knows"*
(`REQ-41`) was never checked with him, in this listen or the three before it. He pointed at his
**extended history** (2014–2026) on `D:\unsung-large-data\`, which no script had read. `LBA-AM7`
rebuilt the pool (breadth-ranked by distinct tracks, 150 names vetted by him) and the familiarity
list, **committed with its scripts before either ran** (`1e70fde`). Every read, gate and bar of
`LBA-AM6` is unchanged. The first draw is superseded and kept as the record; no journey on it was
shown to anyone.

**Author disclosure, recorded in the amendment:** `LBA-AM7` was written by this session after it
had seen the first pre-screen's counts and the drawn endpoint names — not any per-pair row. The rule
reads neither map except for name-to-MBID membership.

**The earlier three listens** carry the same unchecked premise; their verdicts stand (run-once).
`LBA-AM7-5`'s pointer rows landed in `docs/README.md` the same day (`92a4231`) — **discharged**.

## Gate outcomes

| gate | outcome |
|---|---|
| sidecar identity, all three artifacts | passed (pinned by `lal_pin_maps.py`, `lal_maps.json`) |
| pre-screen committed before first run | yes — `27e587a` before the first run; `1e70fde` before `LBA-AM7`'s |
| first draw (`LBA-AM6-2`) | 12 selected; **fails at the owner's strike** (8 of 12 pairs had an unknown endpoint) → `LBA-AM7` |
| `LBA-AM7` draw | 12 selected; **owner struck none** |
| G6 Deezer ids | 0 conflicts |
| generation `--dry-run` | every gate passed, 0 substitutions, nothing written |

## Personal data

The extended history carries IP addresses and timestamps. `lal_pool_am7.py` keeps four fields per
record and commits **only per-artist derived counts** (`lal_am7_candidates.json`) and MBIDs. The
auto-mode classifier blocked the first write of that script; the owner approved it explicitly.

## Provenance (D3)

Artifacts are pinned in `builder/analysis/2026-09-22-lba-a6-blind-listen/lal_maps.json`, written by
script from their sidecars — cite that file, not a copy. The post-strike pair file is pinned by
`lal_common.LAL_PAIRS_SHA`.

## Prose corrections that cannot go in the code

`lal_prescreen_am7.py`'s docstring says membership is part of what it imports "unchanged" from
`lal_prescreen.py`. **Membership is re-checked locally, in `pool_from_known`** — same rule, not the same
code. The docstring is left as written because that file's sha256 is pinned in the pre-screen output it
produced (`lal_am7_prescreen.json`), and editing it would break that record.

## Operational

Each pre-screen took roughly an hour on this machine (one ladder of 21 `find_journey` calls per map
per pair); run it in the background with `python -u`.

## Closeout measurements

- **Standing context layer (D6):** unchanged by this session — no edit to `CLAUDE.md`, `.claude/` or
  memory. Measured against the memory directory `C:/Users/charl/.claude/projects/C--dev-music-app/memory`:
  unconditional 50,977 characters, conditional 2,726 lines. Delta: 0 in both.
- **B3:** three invariants deliberately broken — the tally reading `LAL-K`, Gate D passing on any
  depth, the ranking reversed — and each turned its test red; originals restored.
- **B1:** `docs-lint` hard checks passed; the auditor's one finding (`lal_clips.json` missing from the
  runner's do-not-read list) was a misread of an ambiguous README cell — the file is written under
  `.superpowers/lal/`, which the list covers — and the cell now gives the full path.
- **B6:** `NEXT.md` and `docs/README.md` were already over budget before this session and remain so;
  this session's net additions to them are status and map rows, not reasoning.
