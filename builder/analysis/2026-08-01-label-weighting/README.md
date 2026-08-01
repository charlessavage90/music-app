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

Use absolute paths when launching in background shells — the working directory persists
across calls here and misfired three launches in the original run.

No script here has pytest tests by design (the frozen-probe precedent); the instrument
checks are the tests, and their red capacity was demonstrated at closeout — see the
execution log §3.
