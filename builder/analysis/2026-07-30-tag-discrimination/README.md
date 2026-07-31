# 2026-07-30 — tag-discrimination probe: swap-rate → edge-turnover transfer function

**Analysis only.** Nothing here builds an artifact, writes to `builder/src`, changes a
default, or adopts anything. The crawl archives are opened through `ReadOnlyArchive`
(`GRT-A1`) inside the Track B helper these scripts reuse.

## What question these answer

`TAS-4` in `docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md`
kills the build-time architecture when "the median artist swaps ≤ 2 of 50". Its own bound
says the *built* consequence of a given swap rate is not derivable from the swap rate,
because mutual k-NN deletes edge (u,v) when **either** endpoint drops it. These scripts
measure that conversion on the real candidate-list and mutuality distribution, so the
threshold can be stated in the quantity it is actually about — and then measure whether
the deleted connections are ones journeys route through.

## Scripts

| script | what it is |
|---|---|
| `td_capture.py` | Runs `_capture_pipeline` from the Track B harness (`cb_run_cells.py:185`) — same code path, same archive, byte-deterministic — and freezes the pre-cap candidate lists + `ranking` values as int-id CSR arrays in an `.npz`. Nothing downstream re-reads the archive. |
| `td_turnover.py` | The transfer function. Reconstructs `mutual_knn_cap`'s top-50 selection over the capture, perturbs the ranking in seven arms (factor table in the module docstring), and reports edge deletions / creations / symmetric-difference turnover against an independent-uniform-drop null built from each arm's own realised drop rates. `--verify` runs the green instrument check. |
| `td_coverage.py` | Holds swap size fixed and varies only the share of artists the reranker touches — the zero-inflated case `TAS-1` expects. Isolates whether the *median* is a safe summary of the quantity `TAS-4` bounds. |
| `td_pathedges.py` | Are the deleted connections the ones journeys use? Routes a pair set with `find_journey` at production `ApiConfig()` weights on the SAME substrate the selection is simulated on, then intersects routed edges with each arm's deleted set. Reports the safety ratio (routed deletion rate ÷ population deletion rate) per regime, per swap size and per pair class, with a split-half stability check and the creation mirror. |

## Instrument check (green)

The reconstructed selection must reproduce a real build **exactly**, not approximately.
It is checked against `builder/scratch/cb-cells/ALG-E-mutual_knn-k50.bin`
(sha256 `73feffa0…a69faa`), edge set for edge set, over that artifact's node set.
`td_turnover.py --verify` runs it; `td_pathedges.py` asserts it before scoring anything.

Both also assert the sha256 of the **adopted** artifact
`builder/scratch/graph-t15-tiebreakfix.bin` (`4cb84ef9…61dc8`) and report how the
substrate differs from it. The adopted artifact predates the nameless-artist drop that
`_assemble` now applies, so the two node sets are not identical; the delta is reported in
the JSON rather than assumed away. `td_pathedges.py` deliberately uses the **one**
substrate for both the selection simulation and the routing, so the intersection is
internally consistent.

## Pair set (td_pathedges only)

Own seed `20260730-tdcal` — **deliberately not** the pre-registered `TAS-5` seed
`20260730-tas`, so this calibration does not consume the pre-registered draw. The three
class definitions mirror spec §3 (`ff` both ≥ 0.99, `fo` one ≥ 0.99 and one < 0.50, `oo`
both < 0.50) over the adopted artifact's percentile fame frame as a fixed reference
population. Fame here is **popularity percentile**, not degree.

## Running

```bash
cd builder
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_capture.py --out <scratch>/alge_capture.npz
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_turnover.py --capture <scratch>/alge_capture.npz --verify
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_coverage.py --capture <scratch>/alge_capture.npz
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_pathedges.py --capture <scratch>/alge_capture.npz --per-class 300
```

`--archive ALG-B` on the capture gives the second slice; the turnover run then needs
`--out …_algb.json` and no `--verify` (the green check is ALG-E's artifact).

Captures are ~2 min (ALG-E) / ~7.5 min (ALG-B) and land in the session scratchpad, not
here — they are large and reproducible. Simulation arms are seconds each; the 900-pair
routing in `td_pathedges.py` is ~10 min.

## Outputs kept here

`td_turnover.json` (ALG-E), `td_turnover_algb.json` (ALG-B second slice),
`td_coverage.json`, `td_pathedges.json`. Figures are read off these, not restated in
this README.

## What these do NOT use

**No tag data.** The tag frame does not exist yet, so the reranking is a synthetic
uniform agreement field with tunable magnitude, deliberately independent of similarity
strength. The arms fix the *size* of the reordering, never its content — so the `MULT-*`
rows say nothing about what λ the real tag signal would need (`TAS-3` names exactly that
hazard). The transfer function itself is a property of the graph's mutuality structure,
which is what makes it reusable whatever the tag frame turns out to look like.
