# Mutual k-NN stranding — measurements, 2026-07-25

Backs `docs/superpowers/findings/2026-07-25-mutual-knn-stranding.md`, which owns
the interpretation. **Both scripts are read-only**: they read the adopted artifact
and the crawl archive, and write nothing. No rebuild is involved.

| script | reads | produces |
|---|---|---|
| `degree_and_bridges.py` | adopted APG1 artifact | degree-by-popularity table (`MKS-4`), bridge/no-detour counts (`MKS-6`), name collisions (`MKS-7`) |
| `reciprocity.py` | crawl archive | who reciprocates and who is dropped (`MKS-1`, `MKS-2`), survival-rate sample (`MKS-3`) |

```bash
# from api/
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-25-mutual-knn-stranding/degree_and_bridges.py

# from builder/
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  analysis/2026-07-25-mutual-knn-stranding/reciprocity.py
```

## Both scripts self-gate, and that is the point

`degree_and_bridges.py` asserts the artifact **sha256** before reading a byte —
several graphs live in `builder/scratch/` and are not interchangeable.

`reciprocity.py` models `pipeline.build_from_archive`'s cap, so it is only as good
as that model. It therefore **validates its predictions against the shipped graph**
for six artists and exits non-zero on any mismatch. The first version of this
analysis was wrong twice — `k` taken as 15 from the `t15` run tag when
`BuilderConfig.max_neighbours_per_artist` is **50**, and the candidate list not
filtered to crawled artists — and both errors produced fluent, plausible output.
The disagreement with the graph is what exposed them. Finding §5 has the detail.

**If the builder changes, this model must be re-checked, not trusted.** In
particular it assumes `similarity_damping = 0.0`, where ranking by the raw
ListenBrainz score reproduces the builder's order; at non-zero damping it must
apply `damped_strength` instead. The validation gate will catch this, which is
what it is for.
