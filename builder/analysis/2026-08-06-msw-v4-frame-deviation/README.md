# MSW-V4 — the fame-percentile frame deviation, in router units

**Question** (`docs/superpowers/plans/2026-08-05-msw-package-adoption.md` Task 10 Step 4,
named deviation 2): the shipped `fame_lb_pctl` frames against the served artifact's own
non-null `fame_lb_raw`; the listened arm's frame was the adopted artifact's
(`cre_common.Ruler`). Derive `|pctl_shipped − pctl_CRE_frame|` over the new artifact's
node set, the per-hop ramp cost difference at r = 0.01 for k ∈ {1, 10, 20}, and those
against the other cost terms' magnitudes on real edges.

**Derivation only. No verdicts, no recommendation.** Reading these against any bar is
the controller's step, and adoption is the owner's.

## Artifacts (both sha256-verified inside the scripts, which exit if either mismatches)

| Role | File | sha256 |
|---|---|---|
| Subject (new candidate) | `builder/scratch/graph-msw-tu50.bin` | `43dd82bb…2be79cc8` |
| CRE frame source (retired/adopted) | `builder/scratch/graph-t15-tiebreakfix.bin` | `4cb84ef9…f061dc8` |

## Scripts

| Script | Output | What it does |
|---|---|---|
| `mv4_frame.py` | `mv4_frame.json` | Parts 1–3 as asked: marginal distribution of the difference, its one-knob-at-a-time decomposition, the ramp cost differences, and every other cost term over all 1,315,684 directed arcs. |
| `mv4_gaps.py` | `mv4_gaps.json` | Supplement: (a) is the remap monotone (can it reorder anyone), (b) level shift vs residual spread, (c) the discrepancy in the gap between **real co-neighbour alternatives**, which is the comparison Dijkstra actually makes. |

Run both from `builder/`:

```bash
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-06-msw-v4-frame-deviation/mv4_frame.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-08-06-msw-v4-frame-deviation/mv4_gaps.py
```

Both import rather than copy: the shipped percentile comes from
`artistpath_api.graph_store.GraphStore.fame_percentiles`, the CRE ruler from
`cre_common.Ruler` / the frozen `fi_stats.Frame` (FAM-AM1.6). `mv4_frame.py` asserts its
recomputed shipped column equals the one `GraphStore` actually serves.

## Method notes and assumptions

- **Raw values are held constant.** Every column maps the *new artifact's own*
  `fame_lb_raw`. Only the frame population and the percentile estimator differ. The union
  snapshot's raw values are used solely to measure value drift, reported separately.
- **The deviation is two knobs, not one** (found by reading the source, not stated in the
  brief): the frame *population* differs **and** the percentile *estimator* differs —
  shipped is `|{f < v}| / (N−1)`, CRE is the mid-rank `(|{f<v}| + (|{f=v}|+1)/2) / N`.
  Decomposed via a third column (CRE's estimator on the new artifact's frame).
- **Nodes absent from the retired artifact** need no special handling for the value
  comparison: `fi_stats.Frame.pctl` maps out-of-frame values by construction (FAM-AM1.6).
  The present/absent split is reported anyway because the populations differ.
- **Nulls are reported separately, not folded in.** Shipped prices a null 0.0 and excludes
  it from the frame; the CRE *device* prices a snapshot-present null at `frame.pctl(0)`
  and a snapshot-absent node at 0.5 (`cre_common` pin 2). That is a distinct deviation
  from the frame deviation MSW-V4 asks about.
- **The floor term is request-dependent** (`floor_raw = min(pop_raw[source],
  pop_raw[target])`, relaxed `floor_relax_known` per press), so it is evaluated at three
  representative floors over the real `pop_raw` of every edge head rather than at one.
- **`w_degree_hub` and `w_known_ramp_fame_pctl` both default to 0.0**, so the degree-hub
  term measures identically zero on every arc and r = 0.01 is a *hypothetical* ramp
  weight, taken from `cre_common.RAMPS["P1a"]`.
- **Sampling stability:** part (c) samples co-neighbour pairs. Re-run at seeds 20260806 /
  77771 / 424242 the gap-error p50 was 0.02219 / 0.02215 / 0.02211 and the k = 20
  exceed-`w_hop` fraction 0.02150 / 0.02161 / 0.02145. Everything else in both scripts is
  a full-population enumeration, not a sample.
