# `TCE-C1` statistic behaviour — pure arithmetic, no data

**What these scripts are:** a derivation of how the `TCE-C1` statistic (census median of
`Δ_R = p_top − p_rest`, pre-registration
`docs/superpowers/specs/2026-08-06-thin-catalogue-edge-preregistration.md` §4.1) behaves as a
function of an unknown thin base rate `b`.

**What they are NOT, and this is binding:**

- They read **no archive, no artifact, no MusicBrainz dump, no fixture**. Every number is
  exact combinatorics over the statistic's own definition.
- They **do not compute the thin base rate** and are not any part of running `TCE-`. `b` is a
  free parameter swept over a grid; the real value remains run state per prereg §6.
- They contain **no result read**. Nothing here fires, rescues or blocks any `TCE-` branch.

## Files

| File | What it computes |
|---|---|
| `tce_c1_behaviour.py` | Exact null distribution of `Δ_R` (mean, median, quantiles, band) over `b × L`; the minimum uniform enrichment odds ratio that moves the census median; median under a concentrated effect; null behaviour of three expectation-relative alternatives |
| `tce_c1_ceiling.py` | The **ceiling** of `TCE-C1` (largest census median attainable under any placement, for a given `b`); the breakdown fraction `f*`; supplementary statistics under concentration; an algebraic check that `Δ_R ≥ 0.10 ⟺ X ≥ E_null[X] + (1 − 10/L)` |

## Run

```bash
cd builder && UV_LINK_MODE=copy uv run python analysis/2026-08-06-tce-c1-statistic-behaviour/tce_c1_behaviour.py
cd builder && UV_LINK_MODE=copy uv run python analysis/2026-08-06-tce-c1-statistic-behaviour/tce_c1_ceiling.py
```

Stdlib only, ~40 s each. Deterministic — no seed, no sampling.

## Models used, and which way their error points

- **Null:** `T_R ~ Binomial(L, b)` thin neighbours per list, placed uniformly at random, so
  `X = (# thin in ranks 1–10) | T ~ Hypergeometric(L, T, 10)`.
- **Enrichment:** Fisher's noncentral hypergeometric with odds ratio `ψ` on top-10 placement.
  `T`'s marginal is unchanged — only *placement* is biased, which is the within-list framing
  prereg §0 requires.
- **List length:** unmeasured here on purpose. Reported per `L ∈ {30, 50, 100}` and for
  `L ~ Uniform{30..100}`. Measuring the real distribution is `TCE-` run state.
- **Conservative direction:** real thin-ness almost certainly clusters across a list rather
  than being i.i.d., which makes `T_R` over-dispersed — *more* artists with `T_R = 0`. Every
  insensitivity result below therefore understates the problem.
