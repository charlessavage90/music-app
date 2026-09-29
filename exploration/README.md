# EXPLORATORY — Dig deeper exploration (2026-09-28)

**Nothing in this folder is evidence.** It is a fast, breadth-first search for ideas that might make
Dig deeper actually dig. Nothing here is cited in `docs/` or adopted directly; anything promising goes
through the formal process on pairs **not** listed in `pairs-used.txt`. Artist names are used freely.

## The quick-look kit (`kit/`)

- `qlook.py VARIANT --out RUN.json [--rate]` — runs a variant (a file defining
  `journey(ctx, s, t, pressed, prev)`) on 20 fixed pairs (15 famous, 5 mid-fame), pressing Dig deeper on
  the most famous middle artist each time, presses 0–10. Prints journeys at presses 0/3/5/10 and a
  per-press table: median fame percentile of the middle artists, length, weakest-link similarity,
  share of middle artists from the top 10 %, coherence.
- `rate.py` — the coherence screen: a model (Sonnet, via the local `claude` CLI) rates each step
  0–3 (3 = obvious next track, 0 = jarring). Cached per artist pair in `step_cache.jsonl`.
- `validate_screen.py` — the screen's fail-check.

Run from `api/`: `PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py ...`

### The screen can fail (checked 2026-09-28 on today's journeys, presses 0 and 10)

| version of each journey | mean step (0–3) | steps rated a stretch or worse |
|---|---|---|
| as routed today | 2.01 | 23 % |
| same middle artists, shuffled | 1.34 | 57 % |
| middle artists swapped for random ones of the same fame | 0.82 | 85 % |

The real journey outscored its shuffled twin in 32/39 (5 ties) and its random twin in 38/39.

### …and on obscure journeys (r1-search's fame-neutral soft-ceiling variant, presses 5 and 10)

| version | mean step (0–3) | stretch or worse |
|---|---|---|
| as routed | 1.83 | 33 % |
| shuffled | 1.38 | 55 % |
| random same-fame swap | 0.76 | 89 % |

Real beat its random twin 40/40, shuffled 32/40 (3 ties); rater "don't know" ≈ 1 %. The screen does
not go blind on obscure artists. It may still be mildly harsher on them, so small coherence gaps
between famous and obscure journeys are read as ties.

## Baseline — today's app (`baseline/today.txt`)

Middle artists of famous-pair journeys sit at the 99th fame percentile at press 0 **and** press 10.
Coherence ≈ 0.68 (mean step ÷ 3), about one step in five rated a stretch or worse.
