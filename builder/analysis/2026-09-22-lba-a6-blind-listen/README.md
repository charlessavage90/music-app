# `LAL-` blind listen harness — served map vs the `LBA-A6` candidate

**Role: ACTIVE harness.** Governing document: `LBA-AM6` in
`docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md` §11 — it wins wherever this
directory disagrees with it. **Adapted by copy** from `../2026-09-10-lbd-blind-listen/`, which stays
frozen as the record of listens 1 and 2; no code is imported from there, only its two pair files are
read, sha-pinned, as data. **Owns no figures.**

## Who runs what — three sessions, none of them the designing one (`LBA-AM6-5`)

| session | runs | may NOT |
|---|---|---|
| **preparation** | `lal_pin_maps.py`, `lal_prescreen.py`, the owner's strike via `lal_pairs_final.py`, a `lal_generate.py --dry-run` wiring check (writes nothing) | run the listen or the write-up — it has seen map-labelled output |
| **runner** (fresh, mechanics only) | `RUNNER-BRIEF.md`: `lal_generate.py`, `lal_clips.py`, `lal_page.py` | read anything on the brief's do-not-read list; run `lal_unblind.py` |
| **write-up** (further fresh) | `lal_unblind.py`, then the findings note | — works in the runner's worktree, where `.superpowers/lal/` holds the sealed mapping |

## Files

| file | written by | map-labelled? |
|---|---|---|
| `lal_maps.json` | `lal_pin_maps.py`, from the sidecars | roles only |
| `lal_prescreen.json`, `lal_prescreen.md` | `lal_prescreen.py` | **YES — runner must not read** |
| `lal_pairs_drawn.json` | `lal_prescreen.py` — 8 primaries + 4 reserves, before the strike | no |
| `lal_pairs.json` | `lal_pairs_final.py` — after the strike; sha pinned in `lal_common.LAL_PAIRS_SHA` | no |
| `lal_page_data.json` | `lal_generate.py` — what the page shows | no (leak-guarded) |
| `.superpowers/lal/lal_sealed.json`, `lal_clips.json` | `lal_generate.py`, `lal_clips.py` | **YES — sealed** |
| `lal_verdicts.json` | `lal_page.py`, as he saves | no |
| `lal_result.json` | `lal_unblind.py` (write-up session) | yes — after the unblind |

**The ladder is one module, `lal_journeys.py`, imported by both the pre-screen and generation**, so
"the pre-screen generates exactly as `LBA-AM6-3` will" is true by construction.

## For the write-up session

Run `lal_unblind.py` only once `/status` was complete and the runner's commit of `lal_verdicts.json`
exists. It refuses before the full run state (`LBA-AM6-7`), and its verdict is tested invariant to
every assignment of `LAL-Q3`, `LAL-Q4` and `LAL-K` (`test_lal_listen.py`). Everything under
`descriptive_only` decides nothing (`LBA-AM6-8`); the barred reads are `LBA-AM6-10`'s.
