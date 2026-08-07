# B1 — what does `p99_log_clip` leave the router able to distinguish?

**Date:** 2026-08-06 · **DESCRIPTIVE.** No arms, no hypothesis, no threshold, **no
pre-registration, and it licenses no adoption.** It measures the behaviour of a function that
is already shipped, the way one would read a config value. **Anything comparing rescales needs
its own pre-registration.**

**This directory OWNS its figures.** Raw: `rescale_b1.json`. Cite it; never restate them.

Artifact `graph-msw-tu50.bin`, sha `43dd82bb…`. Weights read from shipped `ApiConfig`
(`w_sim`, `w_hop`, `w_known_ramp_fame_pctl`) — cited, never transcribed.

## The question

The router's similarity term is `w_sim × (1 − similarity)`, where `similarity` is the
**rescaled** value in the artifact. So the question is not "how much information does the log
destroy" in the abstract, but **how much cost leverage is left, next to the other terms the
router weighs at the same moment.**

## Verdict: the rescale compresses, but it is NOT the main lever — and that corrects an
## earlier overstatement

**Clipping is minor.** Only **1.45 %** of edges pin at the 1.0 ceiling, and only **2.13 %** of
artists have two or more neighbours tied there. An earlier working claim that the clip
"throws most of the signal away" was **wrong**, and is corrected here rather than quietly
dropped. The log is monotonic, so **ordering survives everywhere except those ties.**

**Compression is real and bounded.** Across a median artist's *entire* neighbourhood — best
neighbour to worst — stored similarity spans **0.193**, i.e. **0.578** of routing cost. That
is the total leverage similarity has over which neighbour is chosen.

**The legible number.** Expressing the `known` ramp in the currency the router actually trades
in — places down a similarity list, median list length **17**:

| `known` presses | Ramp span | Worth this far down the list |
|---|---|---|
| 5 | 0.05 | **1 place** |
| 10 | 0.10 | **2 places** |
| 20 | 0.20 | **5 places** (p25 3, p75 8) |

**Per step this is modest, and it compounds.** Five places out of seventeen at twenty presses
is a real but bounded nudge at each hop; a journey has roughly eight interior cards, and the
ramp is charged at every one. The *outcome* of that compounding is already measured and is not
restated here — see the depth-exposure census, which isolated the ramp against the floor.

## Raw → rescaled, for reference

Sampled 322,901 archived edge scores; **p99 = 839**.

| Raw | Rescaled | Similarity cost |
|---|---|---|
| 25 | 0.484 | 1.548 |
| 100 | 0.685 | 0.944 |
| 200 | 0.788 | 0.637 |
| 400 | 0.890 | 0.329 |
| ≥ 839 | 1.000 | 0.000 |

**A doubling of raw ListenBrainz similarity (200 → 400) is worth 0.31 of cost.** The full ramp
range at twenty presses is 0.20 — about **two-thirds** of a doubling, not "nearly cancels it",
which was the earlier overstatement.

## What this does and does not support

- **Supports:** the router retains meaningful similarity discrimination. A rescale change is
  **not** an obvious win and should not be treated as low-risk.
- **Does not support:** any claim that the rescale causes the class the owner observed. It is
  compatible with that and with the opposite.
- **Open, and it would need a pre-registration:** does an alternative rescale change *which
  artists appear*? Testable without a rebuild — the topology is fixed by `trimmed_union`, so
  only the stored weights would vary, which is a genuine one-knob comparison.

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-08-06-rescale-fidelity/rescale_b1.py
```
