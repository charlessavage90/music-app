"""`CRE-D1` -- the banding read. Stage 0, CONFIRMATORY.

**Plain (prereg §4):** does the map already connect well-known artists to each other
on *thinner* shared-genre evidence than it connects obscure artists to each other?

**This run is confirmatory, not exploratory.** §9 discloses that the pre-run critique
measured **+0.08** on this substrate -- the opposite sign to the hypothesis -- so the
**expected branch is `not_supported`**. That expectation is committed here before the
figure is read, and the disclosure travels in the output.

**`CRE-AM1` leaves `CRE-D1` untouched:** the measure is the *rarity*-weighted `W4`
agreement (Σ idf over ∩ ÷ Σ idf over ∪), with **no** within-artist vote weighting.
Vote weighting belongs to `S2`'s ceiling ranking only.

---

## Divergence from `cre_probe3b.py`, recorded per plan pin 5

Pin 5 says the aggregation follows the probe, **but where the probe and the prereg's
words disagree, the words govern.** They disagree on aggregation, and the words are
followed here:

- **The probe pools every labelled edge in a band and takes a MEDIAN difference.**
- **The prereg's §4 words require size-matching:** `(min, max)` endpoint label-set-size
  cells, only cells with **≥ 30 edges in each band** contribute, per-cell difference is
  the popular-band **mean** minus the obscure-band **mean**, and the overall figure is
  the **edge-weighted mean** of per-cell differences.

So the headline number here is **not** directly comparable to the probe's +0.08: it is a
size-matched mean-of-means where the probe's was a pooled median. Both are reported
below -- the probe's pooled form is recomputed as `probe_form_pooled_median_difference`
so the divergence is visible as a figure rather than only as a sentence.

Two things the probe and the words agree on, checked rather than assumed: `five_frames()`
returns `W4` keyed on exactly the adopted artifact's node set, so the plan pin 5 idf form
(`idf_table(frames["W4"], n_artists=<adopted node count>)`) and the probe's inline
document-frequency count are the **same population** -- no idf divergence exists, and no
label receives a negative rarity weight under either.

**One device pin, made reversible rather than argued:** §4 weights the overall mean by
"the cell's contributing edge count", which does not say whether that is the popular
count, the obscure count, or their sum. **Sum is used.** The full per-cell table
(`cells`) is committed with both counts, so any other weighting is recomputable from the
output without re-running anything.
"""
from __future__ import annotations

import json
import math
import sys
import time
from collections import defaultdict

import numpy as np

from cre_common import ADOPTED_SHA, Ruler, in_dir, load_adopted, use_frozen

use_frozen("tag_disc", "rel")
from tas_frame_split import five_frames  # noqa: E402
from tas_weighting import idf_table, weighted_agreement  # noqa: E402

POPULAR_MIN = 0.75      # both endpoints >= 0.75
OBSCURE_MAX = 0.50      # both endpoints <= 0.50
CELL_MIN_EDGES = 30     # per band, per (min,max) size cell
READABLE_MIN = 500      # labelled edges per band
SUPPORTED_AT = -0.05

DISCLOSURE = (
    "Confirmatory, not exploratory: the pre-run critique measured +0.08 on this "
    "substrate (prereg §9 disclosure) and the expected branch is 'not supported'. "
    "Note the probe's +0.08 is a POOLED MEDIAN difference; the prereg's words "
    "specify a size-matched mean-of-means, which is what 'difference' is here."
)


def main() -> int:
    t0 = time.time()
    store = load_adopted()
    ruler = Ruler()
    n = len(store.mbids)
    measured, _ = ruler.arrays(store)

    frames = five_frames()
    w4 = frames["W4"]
    idf, _df = idf_table(w4, n_artists=n)
    labels = [w4.get(m, set()) for m in store.mbids]
    size = np.array([len(s) for s in labels], dtype=np.int64)
    print(f"W4 over the artifact: {(size > 0).sum()}/{n} labelled "
          f"({(size > 0).mean():.4f})   {time.time() - t0:.0f}s", flush=True)

    # Undirected surviving edge set, u < v (the probe's extraction, which the
    # prereg's words agree with).
    deg = np.diff(store.offsets).astype(np.int64)
    src = np.repeat(np.arange(n, dtype=np.int64), deg)
    dst = np.asarray(store.neighbours, dtype=np.int64)
    und = src < dst
    u, v = src[und], dst[und]

    fam_ok = ~np.isnan(measured[u]) & ~np.isnan(measured[v])
    popular = fam_ok & (measured[u] >= POPULAR_MIN) & (measured[v] >= POPULAR_MIN)
    obscure = fam_ok & (measured[u] <= OBSCURE_MAX) & (measured[v] <= OBSCURE_MAX)
    labelled = (size[u] > 0) & (size[v] > 0)

    bands = {}
    for name, mask in (("popular", popular), ("obscure", obscure)):
        total = int(mask.sum())
        lab = int((mask & labelled).sum())
        bands[name] = {
            "edges_in_band": total,
            "labelled_edges": lab,
            # Every D1 sentence must carry this (prereg §4).
            "labelled_edge_share": (lab / total) if total else None,
            "readable": lab >= READABLE_MIN,
        }
        print(f"  {name}: {total} edges, {lab} labelled "
              f"({bands[name]['labelled_edge_share']:.4f})", flush=True)

    # --- per-edge agreement, bucketed by (min,max) label-set size -----------
    def collect(mask):
        by_cell: dict[tuple[int, int], list[float]] = defaultdict(list)
        flat: list[float] = []
        undefined = 0
        for e in np.flatnonzero(mask & labelled):
            a, b = labels[u[e]], labels[v[e]]
            w = weighted_agreement(a, b, idf)
            if w is None:            # every idf in the union is 0
                undefined += 1
                continue
            cell = (min(len(a), len(b)), max(len(a), len(b)))
            by_cell[cell].append(w)
            flat.append(w)
        return by_cell, flat, undefined

    pop_cells, pop_flat, pop_undef = collect(popular)
    obs_cells, obs_flat, obs_undef = collect(obscure)

    # --- size-matched cells: >= 30 edges in EACH band -----------------------
    rows = []
    for cell in sorted(set(pop_cells) & set(obs_cells)):
        p, o = pop_cells[cell], obs_cells[cell]
        contributes = len(p) >= CELL_MIN_EDGES and len(o) >= CELL_MIN_EDGES
        rows.append({
            "size_min": cell[0], "size_max": cell[1],
            "popular_n": len(p), "obscure_n": len(o),
            "popular_mean": float(np.mean(p)), "obscure_mean": float(np.mean(o)),
            "difference": float(np.mean(p) - np.mean(o)),
            "contributes": contributes,
        })
    contributing = [r for r in rows if r["contributes"]]
    weights = [r["popular_n"] + r["obscure_n"] for r in contributing]
    difference = (
        float(sum(r["difference"] * w for r, w in zip(contributing, weights))
              / sum(weights))
        if contributing else None
    )

    readable = bands["popular"]["readable"] and bands["obscure"]["readable"]
    if difference is None or not readable or not contributing:
        branch = "unreadable"
    elif difference <= SUPPORTED_AT:
        branch = "supported"
    else:
        branch = "not_supported"

    consequence = {
        "supported": (
            "The D1-branch cells of §0.2 EXIST (B-S2-P0, E-S2-P1a, B-S2-P1a) and a "
            "router-side tag pricing arm becomes eligible BY §8 AMENDMENT WRITTEN "
            "BEFORE IT IS BUILT. That amendment is NOT this plan's to write: PAUSE "
            "and hand to the owner-facing flow."
        ),
        "not_supported": (
            "The D1-branch cells of §0.2 DO NOT EXIST and no router-side tag arm "
            "does. E-S2-P0 is branch-proof and runs regardless."
        ),
        "unreadable": (
            "Unreadable: the D1-branch cells DO NOT EXIST, as for not_supported. "
            "E-S2-P0 is branch-proof and runs regardless."
        ),
    }[branch]

    doc = {
        "read": "CRE-D1",
        "role": "Stage-0 confirmatory banding read; expected branch 'not_supported'.",
        "disclosure": DISCLOSURE,
        "measure": ("rarity-weighted W4 agreement (sum idf over intersection / sum "
                    "idf over union); NO within-artist vote weighting -- CRE-AM1 "
                    "leaves CRE-D1 untouched"),
        "substrate": "adopted artifact, undirected surviving edge set (u < v)",
        "artifact_sha256": ADOPTED_SHA,
        "ruler_frame_n": ruler.frame_n,
        "n_artists_for_idf": n,
        "aggregation": {
            "form": ("prereg §4 words: size-matched (min,max) label-set-size cells, "
                     ">= 30 edges in EACH band, per-cell difference = popular mean - "
                     "obscure mean, overall = edge-weighted mean of per-cell "
                     "differences"),
            "cell_weight": "popular_n + obscure_n (device pin; per-cell table "
                           "committed so any other weighting is recomputable)",
            "divergence_from_cre_probe3b": (
                "The probe pools each band and takes a MEDIAN difference, with no "
                "size-matching. The prereg's words govern (plan pin 5), so the "
                "headline 'difference' here is a size-matched mean-of-means and is "
                "NOT directly comparable to the probe's +0.08. The probe's pooled "
                "form is recomputed as probe_form_pooled_median_difference."
            ),
        },
        "bands": bands,
        "readable": readable,
        "readability_bar_labelled_edges_per_band": READABLE_MIN,
        "cells_total": len(rows),
        "cells_contributing": len(contributing),
        "cell_min_edges_per_band": CELL_MIN_EDGES,
        "difference": difference,
        "supported_at_or_below": SUPPORTED_AT,
        "branch": branch,
        "consequence": consequence,
        "probe_form_pooled_median_difference": (
            float(np.median(pop_flat) - np.median(obs_flat))
            if pop_flat and obs_flat else None
        ),
        "undefined_agreement_edges": {"popular": pop_undef, "obscure": obs_undef},
        "cells": rows,
        "seconds": round(time.time() - t0, 1),
    }
    out = in_dir("cre_d1.json")
    out.write_text(json.dumps(doc, indent=2), encoding="utf-8")
    print(f"\nwrote {out.name}  ({doc['seconds']}s)")
    print(f"  cells: {len(contributing)} contributing of {len(rows)} shared")
    print(f"  size-matched difference (prereg form) = {difference}")
    print(f"  probe form (pooled median)            = "
          f"{doc['probe_form_pooled_median_difference']}")
    print(f"  readable: {readable}")
    print(f"  BRANCH: {branch}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
