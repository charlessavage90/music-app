# `SNW-` harness — the `DSL-` listen's weak-step marks against three step measures (#271)

**Role: ACTIVE harness, NOT YET RUN.** Governing document:
`docs/superpowers/specs/2026-10-03-issue-271-shared-neighbours-marks-preregistration.md`. It wins
wherever this directory disagrees with it. **Owns no figures** beyond `snw_chance_estimate.json`, the
pre-run synthetic estimate (`SNW-CH0`), and, once run, `snw_result.json`.

| file | what | reads an answer file? |
|---|---|---|
| `snw_test.py` | the test: `--rate-only` (step 1), then the one scoring run (step 3) | step 1 **no**; step 3 reads `dsl_verdicts.json`'s `weak` field only |
| `snw_chance_estimate.py` → `snw_chance_estimate.json` | `SNW-CH0`: chance-firing rate and power on a synthetic layout from findings §3's totals | no |
| `test_snw.py` | synthetic data and the 500-node fixture; no answer file, no real map, no model call | no |
| `snw_rater_cache.jsonl`, `snw_rating_passes.jsonl` | written by step 1 (at most three passes, `SNW-RS`); both committed before step 3 | — |
| `snw_result.json` | written by step 3, once | — |

**Who runs it:** a fresh session, never the designing one, in the order of the pre-registration's §9
(`SNW-RS`). All commands run from `api/`:

```bash
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u ../builder/analysis/2026-10-03-snw-marks-test/snw_test.py --rate-only
PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u ../builder/analysis/2026-10-03-snw-marks-test/snw_test.py
UV_LINK_MODE=copy uv run --extra dev pytest ../builder/analysis/2026-10-03-snw-marks-test -q   # tests
```

**Needs, beyond a fresh worktree:** the two maps at the absolute paths pinned in `snw_test.MAPS`, and the
`claude` CLI on PATH for step 1. The experiment imports nothing from `exploration/`. One test imports
`r2nsim_core.py` to prove the shared-neighbours restatement equal to it, and one reads `rate.py`'s text
to prove the prompt verbatim.
