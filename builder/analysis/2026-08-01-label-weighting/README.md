# The label weighting and evidence probe (`WGT-`), 2026-08-01

**Governing document:**
[`docs/superpowers/specs/2026-08-01-label-weighting-probe-preregistration.md`](../../../docs/superpowers/specs/2026-08-01-label-weighting-probe-preregistration.md)
— committed before any figure existed. **Figures live in
[`docs/superpowers/findings/2026-08-01-label-weighting-probe.md`](../../../docs/superpowers/findings/2026-08-01-label-weighting-probe.md)**
and are cited, never restated, including by this file.

**The question:** once rare labels count for more than common ones, and well-evidenced
labels for more than drive-by ones, do genre labels tell an artist's candidates apart
better — and does the Discogs style column stop hurting? (It does not; the findings own
the verdicts and the mechanism.)

**Substrate:** the pre-cap `ALG-E` capture (`TAS-AM2`, selection side), regenerated via
`../2026-07-30-tag-discrimination/td_capture.py` into a session scratchpad — it is not
committed and dies with the session. Every consumer verifies its sha against the recorded
value before reading anything.

## Scripts

| Script | What it does | Output |
|---|---|---|
| `wgt_evidence.py` | The two dump passes the committed parses discarded data for: `--artist-pass` keeps MB artist-page **vote counts** per label (~2.3 min); `--release-pass` streams the 322 GiB MB release dump once for the `WGT-4` readings, plus the descriptive side-collection (record labels, countries, years) nothing consumes yet. Resumable; checkpoint schema versioned. | `wgt_artist_votes.json`, `wgt_release_raw.json` |
| `wgt_grid.py` | The main run: four instrument checks (`WGT-0a`–`0d`), the fame-leak gate (`WGT-1`, which **fixes the evidence table before any cell**), then the 15 cells (five frames × `plain`/`rarity`/`evidence`) with the singleton diagnostic riding along. `--with-release` is the `evidence⁺` re-run and never ran — `WGT-4` excluded `EV-R`. | `wgt_grid.json` |
| `wgt_release_read.py` | The three `WGT-4` scoping readings and the pre-registered four-branch decision rule. Refuses to run while the release-pass checkpoint exists (a partial-pass number is not a `WGT-4` figure). | `wgt_release_read.json` |
| `wgt_tables.py` | `WGT-5`: per-frame and per-source vocabulary tables, and the owner's style-frequency eyeball artifact. | `wgt_tables.json`, `STYLE-VOCABULARY.md` |
| `wgt_style_filters.py` | Owner-directed follow-up, bar-less: five style-column quality filters (carrier floors, MB intersection, fold-normalised on two isolations) testing two rival mechanisms for the style verdict. Fold rules unit-checked in-module. | `wgt_style_filters.json` |
| `tail_sample.py` | **Outside the pre-registration by its §8**: the 20-artist no-release tail sample for the owner's manual review, fixed seed, stratified by popularity band, with the app's own clip-resolution check per artist. | `tail_sample.json`, `TAIL-SAMPLE.md` |
| `tail_signals.py` | **Outside the pre-registration, DIAGNOSTIC ONLY, no bar, licenses nothing.** One streaming pass over the 17.2 GiB MB artist dump, no network: external-link, Discogs-link, genre-tag and artist-**type** counts for the no-release tail **and for the rest of the graph as the baseline** — a bare tail figure is uninterpretable. Also scores four candidate filter rules against the owner's own 20 verdicts, parsed from `TAIL-SAMPLE.md`. ~4 min. | `tail_signals.json` |
| `tail_clips.py` | **Outside the pre-registration, DIAGNOSTIC ONLY, no bar, licenses nothing.** Does anything actually *play* for the 1,402 DSP-linked tail artists? Two paths per artist: the **name** path (the app's own Deezer→iTunes order, accepted on `clips.same_artist`, imported never restated) and, where MusicBrainz gives a Deezer artist ID, an **ID** path with no name matching. Their disagreement is a **measured `BYP-13` rate**. Refusals are bucketed separately and excluded from every denominator (`G3-A4`); resumable checkpoint every 25. ~45 min, ~1,750 calls. | `tail_clips.json` |
| `tail_exposure.py` | **Outside the pre-registration, DIAGNOSTIC ONLY, no bar, licenses nothing.** Asks the question `TAIL-SAMPLE.md` cannot: does the app ever *deliver* a no-release artist mid-journey? Routes 400 pairs per class × two seeds through production `find_path` on the **adopted artifact** (map side, `TAS-AM2`) and reports the rate per pair class, plus the structural bounds and the delivered artists by name. **Two hard instrument checks abort the run:** the artifact sha, and the population reproducing `TAIL-SAMPLE.md`'s committed 7,686. ~13 min. | `tail_exposure.json` |

## The two owner-authored records in this directory

`TAIL-SAMPLE.md` carries the owner's 20 verdicts (18 of 20 not journey-worthy) and
`STYLE-VOCABULARY.md` carries his vocabulary calibration read. Both are **preference
records** in the `WHAT-GOOD-LOOKS-LIKE` sense: no threshold may be read off them, and a
criterion contradicting them is wrong.

## Instrument checks

`WGT-0a` (unit weights reproduce `plain` bit-identically), `WGT-0b` (the committed
`tas_weighting` and `tas_frame_split` figures reproduce exactly before any new figure is
read), `WGT-0c` (λ = 0 changes nothing), `WGT-0d` (capture sha matches the recorded
value). A failure stops the probe; results produced before a fix are void.

## Running

From `builder/`, in the pre-registration §9's order:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-01-label-weighting/wgt_evidence.py --artist-pass
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-01-label-weighting/wgt_grid.py --capture <path>/alge_capture.npz
# the release pass (~50 min) and its readings:
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-01-label-weighting/wgt_evidence.py --release-pass
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-01-label-weighting/wgt_release_read.py --capture <path>/alge_capture.npz
```

The two tail scripts are independent of the `WGT-` order above and need no capture — they
read the adopted artifact and the committed `REL-` dumps:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-01-label-weighting/tail_exposure.py
```

Use absolute paths when launching in background shells — the working directory persists
across calls here and misfired three launches in the original run.

No script here has pytest tests by design (the frozen-probe precedent); the instrument
checks are the tests, and their red capacity was demonstrated at closeout — see the
execution log §3.
