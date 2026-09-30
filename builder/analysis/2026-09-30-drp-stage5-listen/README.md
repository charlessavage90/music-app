# `DSL-` blind listen harness — today's app vs `DRP-S1P3` (stage 5 of the #200 remedy)

**Role: ACTIVE harness.** Governing document: `DRP-AM7` in
`docs/superpowers/specs/2026-09-27-issue-200-depth-remedy-preregistration.md` §14, including its seam-5A
review. It wins wherever this directory disagrees with it. **Adapted by copy** from
`../2026-09-22-lba-a6-blind-listen/` (the `LAL-` listen), which stays frozen. From there it imports
only pure functions (`lal_prescreen.draw`, `rank_key`; `lal_pool_am7.presented_endpoints`) and reads
pool and pair files as sha-pinned data. **Routing is the lattice's own code, imported unchanged**
(`dsl_journeys.py` → `drp_sweep.run_ladder`, `drp_sweep.load_map`), so `DSL-G1` tests the code that
produced the stage-3 result. **Owns no figures.**

Every input pin is a sha256 of **LF-normalised** bytes (`dsl_common.sha256_lf`). The repo checks out
with `autocrlf=true`, so a working copy's raw bytes are not the committed blob's identity.

## Who runs what — none of them the designing session (`DRP-AM7-5`)

| session | runs | may NOT |
|---|---|---|
| **designer** (wrote `DRP-AM7`, built this harness: seams 5A–5B) | tests only; never a real map | run the preparation, the listen or the write-up |
| **preparation** (seam 5C) | `dsl_g1.py`, then `dsl_prescreen.py`; shows the owner the 12 pairs **by endpoint name only** and applies his strike with `dsl_pairs_final.py`; pins `DSL_PAIRS_SHA` in `dsl_common.py` by commit; then `dsl_generate.py --dry-run` (writes nothing) | run the listen or the write-up: it has seen side-labelled output |
| **runner** (fresh, mechanics only; seam 5D) | `RUNNER-BRIEF.md`: `dsl_generate.py`, `dsl_clips.py`, `dsl_page.py` | read anything on the brief's do-not-read list; run `dsl_unblind.py` |
| **write-up** (further fresh; seam 5E) | `dsl_unblind.py`, then the findings note | — works in the runner's worktree, where `.superpowers/dsl/` holds the sealed mapping |

All commands run from `api/` (its environment carries the shipped router the lattice imports):
`cd api && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u ../builder/analysis/2026-09-30-drp-stage5-listen/<script>`.
Tests: `uv run --extra dev pytest ../builder/analysis/2026-09-30-drp-stage5-listen -q`.

**The two artifacts are read by absolute path** through the lattice's loader:
`C:/dev/music-app/builder/scratch/graph-lba-a6.bin` (today's) and
`C:/unsung-fast/drp-stage3a/graph-drp-s1.bin` (the extra-connections map). Each is verified against
its sidecar and its pin, and `DRP-S1` is refused unless `DRP-G3` passed on it.

## Files

| file | written by | side-labelled? |
|---|---|---|
| `dsl_g1.json` | `dsl_g1.py` — `DSL-G1`'s verdict, counts only | no |
| `dsl_prescreen.json`, `dsl_prescreen.md` | `dsl_prescreen.py` | **YES — runner must not read** |
| `dsl_pairs_drawn.json` | `dsl_prescreen.py` — 4 + 2 per tier, before the strike | no |
| `dsl_pairs.json` | `dsl_pairs_final.py` — after the strike; sha pinned in `dsl_common.DSL_PAIRS_SHA` | no |
| `dsl_page_data.json` | `dsl_generate.py` — what the page shows | no (leak-guarded) |
| `.superpowers/dsl/dsl_sealed.json`, `dsl_clips.json`, `dsl_clip_tells.json` | `dsl_generate.py`, `dsl_clips.py` | **YES — sealed** |
| `dsl_verdicts.json` | `dsl_page.py`, as he saves | no |
| `dsl_result.json` | `dsl_unblind.py` (write-up session) | yes — after the unblind |

## For the write-up session

Run `dsl_unblind.py` only once `/status` was complete and the runner's commit of `dsl_verdicts.json`
exists. It refuses before the full run state (`DRP-AM7-7`). Its three reads are independent and tested
so: the verdict (`DSL-R1`–`R4`) reads picks and the clip box only; `DSL-P` reads recognition marks
only; `DSL-E` reads weak-step marks only. Each of `DSL-P` and `DSL-E` has three outcomes (fires /
does not fire / unreadable), and the sentence for each comes from `DRP-AM7-8`/`-9`. Everything under
`descriptive_only` decides nothing (`DRP-AM7-10`); the barred reads are `DRP-AM7-11`'s.
