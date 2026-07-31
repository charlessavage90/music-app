# Release-tag aggregation coverage (`REL-`)

**Governing document:**
[`docs/superpowers/specs/2026-07-31-release-tag-coverage-preregistration.md`](../../../docs/superpowers/specs/2026-07-31-release-tag-coverage-preregistration.md),
committed **before any measurement ran**. Where this README and the
pre-registration disagree, the pre-registration wins.

**Scope: descriptive.** Adopts nothing, fixes no criterion, changes no weight, default,
currency or vocabulary, and does not amend `TAS-` §1. A frame that passes every bar is a
**candidate** for a future `TAS-` §8 amendment, never an enactment of one.

## The question

For the **33,756 artists carrying no genre label today** — 64.6% of the lower-half band —
does aggregating the tags on their *releases* produce labels? Specifically **in the obscure
tail**: a frame that only thickens labels where labels are already good changes nothing for
`TAS-6`.

## Data: four local files, no API

Every figure is a **census** over all 74,193 nodes. No sampling, no seed, no CI, no noise
band — the dumps are local and every pass is deterministic.

| Source | Path under `builder/scratch/` |
|---|---|
| Adopted artifact | `graph-t15-tiebreakfix.bin` (sha256 asserted on load) |
| MB artist dump | `mb-json-dumps/artist/mbdump/artist` (17.2 GB JSONL) |
| MB release-group dump | `mb-json-dumps/release-group/mbdump/release-group` (18.0 GB JSONL) |
| Discogs releases | `discogs-data-dump/discogs_20260601_releases.xml` (61.6 GB XML) |

**All four are gitignored and live only in the main working tree.** They are not in git and
would not appear in a `git worktree` — point any re-run at `builder/scratch/` explicitly.

The MusicBrainz **release** dump (345 GB) is out of scope and was deleted: release-level tags
measured 13.5% non-empty against release-group's 42.4%, so the album concept is the
aggregation unit, not the pressing.

## Run order — it is not arbitrary

```bash
# 1. REL-7 (fidelity) + REL-2(a) (MBID -> Discogs mapping). measured 2.2 min
#    FIRST, because REL-C1's tolerance IS REL-7's drift figure.
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-31-release-tag-coverage/rel_artist_dump.py

# 2. F1/F2/F3 -- REL-1, REL-5, REL-6.                     measured 2.4 min
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-31-release-tag-coverage/rel_rg_dump.py

# 3. F4/F5 + REL-2 in full.                              measured 22.2 min
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-31-release-tag-coverage/rel_discogs.py

# 4. REL-C1, REL-C2, REL-3.  EXITS NON-ZERO if either check fails,
#    and prints no criterion when it does.
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-31-release-tag-coverage/rel_score.py

# 5. REL-4 -- needs BOTH sources, so it runs last.                <1 min
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-31-release-tag-coverage/rel_union.py

# tests (the dormant term is pinned here)
UV_LINK_MODE=copy uv run --extra dev pytest -q \
    analysis/2026-07-31-release-tag-coverage/
```

`analysis/` is **not** in builder's `testpaths` (deferred by the owner 2026-07-30), so these
tests run only when invoked explicitly.

## Files

| File | What it owns |
|---|---|
| `rel_common.py` | The device: the validity filter (**the dormant term**), label normalisation, aggregation, Jaccard. Imports band membership and `norm_genre` through the `TAS-` chain rather than reimplementing them. |
| `rel_artist_dump.py` | `REL-7`, `REL-2(a)` |
| `rel_rg_dump.py` | `F1`/`F2`/`F3` → `REL-1`, `REL-5`, `REL-6` |
| `rel_discogs.py` | `F4`/`F5` → `REL-2` in full, `REL-4` inputs |
| `rel_score.py` | `REL-C1`, `REL-C2`, `REL-3` |
| `rel_union.py` | `F6` → `REL-4`, plus the cross-source agreement and its vocabulary confound |
| `test_rel_common.py` | Pins the filter, the label rules and the `None`-not-zero Jaccard contract |

`*_raw.json` are gitignored: large, and regenerable from the commands above. Derived
summaries are committed, per the `COH-`/`FPC-`/`TAS-` template.

## Three things worth knowing before reading any output

1. **`F0` is the committed `tas_tags` frame and nothing here redefines it.** The artist dump
   carries artist-level tags for every artist; using them to define "unlabelled" would move
   every coverage figure for a reason unrelated to aggregation. `REL-7` reads them in exactly
   one place and supplies a *tolerance*, never a population.
2. **`REL-C2`'s shuffle is informative for `REL-3` and meaningless for `REL-1`.** Coverage is
   near-invariant under shuffled ownership by construction — a randomly assigned album still
   carries tags. The shuffled coverage figure is printed anyway so that invariance is visible
   rather than assumed. `TAS-AM3` is the worked example of why the axis matters.
3. **Any `F4`/`F5`/`F6` figure quoted without `REL-2` beside it is misreported.** Discogs
   genre is 100% filled because it is a *schema constraint* — a release cannot be submitted
   without one — so the Discogs arm is bounded entirely by mapping and release presence, not
   by tagging effort.
