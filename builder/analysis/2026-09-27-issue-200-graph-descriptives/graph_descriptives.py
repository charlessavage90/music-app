"""Issue #200: two descriptive measurements over the adopted map. Decides nothing.

Closes the two weakest links named in
`../2026-09-25-issue-200-served-fame-vs-listeners/README.md` §3:
  1. depth was tangled with famous endpoints (no mid-scale pair was pressed >= 10 times);
  3. "the map, more than the weights" was inferred from neighbour tables of SERVED
     artists only.

Currency on every figure: FAME PERCENTILE (`fame_lb_pctl`), ListenBrainz listener rank
within each map's OWN measured population, via the shipped
`GraphStore.fame_percentiles` (api/src/artistpath_api/graph_store.py:148). Not
`pop_raw`, not degree.

Measurement A (structural, lba-a6 and lux4, each in its own frame): for every artist
at fame percentile >= 0.90 (top decile) and >= 0.99 (top 1 %), the share of its graph
neighbours below 0.9 and below 0.5.

Measurement B (routing, lba-a6 only): 40 FAMOUS pairs (both endpoints >= 0.95) and 40
MID pairs (both in [0.30, 0.70]); the shipped `find_journey` with default
`ApiConfig()`; all presses KNOWN ("Dig deeper"), victim = most famous interior by
`cre_ladder.victim_key` (cited, not retyped), cumulative, ladder 0..20; median interior
fame percentile recorded at 0, 5, 10, 20 presses.

No alternative weights are run; ApiConfig is not modified. No command-line arguments
are read: every path is hardcoded below.

Run from `api/`:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-27-issue-200-graph-descriptives/graph_descriptives.py

REFUSES (exit 2) if any artifact's sha256 disagrees with its own sidecar, before
reading anything from it.
"""

from __future__ import annotations

import hashlib
import json
import random
import struct
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]  # this worktree
SCRATCH = Path("C:/dev/music-app/builder/scratch")
NEW = SCRATCH / "graph-lba-a6.bin"  # adopted 2026-09-25
NEW_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
OLD = SCRATCH / "graph-lux4.bin"  # served before 2026-09-25
# Comparability only: the JFX reachability critique was measured on this file, not lux4.
JFX_MAP = SCRATCH / "graph-msw-tu50.bin"

# ---- Measurement B draw rule, fixed BEFORE the first run ----
SEED = 20260927
N_PAIRS = 40
FAMOUS_LO = 0.95  # both endpoints fame_lb_pctl >= 0.95
MID_LO, MID_HI = 0.30, 0.70  # both endpoints in [0.30, 0.70]
DEPTHS = (0, 5, 10, 20)
MAX_K = max(DEPTHS)
# Draw rule: pool = measured-fame artists in the band, ascending node id. One
# random.Random(SEED) instance; FAMOUS is drawn first, then MID. Each draw is
# rng.sample(pool, 2) -> (source, target) in that order. A draw is rejected if its
# unordered pair {s, t} was already drawn in the same set (sample() guarantees s != t).
# Draw until N_PAIRS accepted.


def verify(path: Path, expect: str | None = None) -> str:
    """sha256 must equal the sidecar's top-level `sha256` (and `expect` if given)."""
    sidecar = path.with_name(path.name + ".json")
    want = json.loads(sidecar.read_text(encoding="utf-8"))["sha256"]
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != want or (expect is not None and got != expect):
        print(f"REFUSING: {path.name} sha256 {got}; sidecar {want}; expected {expect}",
              file=sys.stderr)
        sys.exit(2)
    print(f"sha256 OK  {path.name}  {got}")
    return got


# ---- identity FIRST: nothing below is read before all checks pass ----
SHA = {NEW: verify(NEW, NEW_SHA), OLD: verify(OLD), JFX_MAP: verify(JFX_MAP)}

# Shipped modules BEFORE cre_ladder, exactly as jfx_route.py does, so the cached
# shipped modules are what cre_ladder's own imports resolve to.
from artistpath_api import pathfinding as _pf_mod  # noqa: E402
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_api.pathfinding import KNOWN, Exclusion, find_journey  # noqa: E402

_API_SRC = (ROOT / "api" / "src").resolve()
_pf_file = Path(_pf_mod.__file__).resolve()
assert _API_SRC in _pf_file.parents, f"pathfinding loaded from {_pf_file}, not {_API_SRC}"

sys.path.insert(0, str(ROOT / "builder/analysis/2026-08-03-cap-reevaluation"))
from cre_ladder import victim_key  # noqa: E402  -- ONLY victim_key is used

_pf_after = Path(sys.modules["artistpath_api.pathfinding"].__file__).resolve()
assert _pf_after == _pf_file, f"pathfinding module replaced after cre_ladder: {_pf_after}"
assert sys.modules["artistpath_api.pathfinding"].find_journey is find_journey
print(f"pathfinding: {_pf_file}")


def raw_fame(payload: bytes, n: int) -> list:
    """`fame_lb` straight from the APG1 metadata blob (GraphStore drops raw values).

    Cursor arithmetic as in ../2026-08-09-jfx-prereg-critique/jfx_s1_reachability.py.
    """
    header = struct.Struct("<4sIIIQ")
    magic, _v, hn, e, meta_len = header.unpack_from(payload)
    assert magic == b"APG1" and hn == n
    cursor = header.size + (hn + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(payload[cursor: cursor + meta_len])
    fame = meta.get("fame_lb")
    assert fame is not None and len(fame) == n, "artifact carries no/short fame_lb"
    return fame


def load(path: Path):
    payload = path.read_bytes()
    store = GraphStore.from_bytes(payload)
    fame = raw_fame(payload, store.artist_count)
    pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
    # Identity check: the store's percentiles ARE the shipped staticmethod's output.
    assert np.array_equal(pctl, GraphStore.fame_percentiles(fame))
    measured = np.array([v is not None for v in fame], dtype=bool)
    return store, pctl, measured


def q(a, p):
    return float(np.percentile(a, p)) if len(a) else float("nan")


# ------------------------------------------------------------------ Measurement A
def measure_a(label: str, store, pctl, measured) -> None:
    n = store.artist_count
    deg = np.diff(store.offsets).astype(np.int64)
    print(f"\n### {label}: N {n:,}  CSR entries {int(store.offsets[-1]):,}  "
          f"measured fame {int(measured.sum()):,}  null fame {int((~measured).sum()):,}")
    for tier, cut in (("top decile (fame pctl >= 0.90)", 0.90), ("top 1 % (fame pctl >= 0.99)", 0.99)):
        centres = np.flatnonzero(measured & (pctl >= cut))
        s9, s5, s9n, s5n, c9, c5, dg, nulls_at = [], [], [], [], [], [], [], 0
        for c in centres:
            nb = store.neighbours[store.offsets[c]: store.offsets[c + 1]]
            m = measured[nb]
            if (~m).any():
                nulls_at += 1
            nm = nb[m]
            dg.append(len(nb))
            b9 = int((pctl[nm] < 0.9).sum())
            b5 = int((pctl[nm] < 0.5).sum())
            c9.append(b9)
            c5.append(b5)
            # headline: null neighbours EXCLUDED from numerator and denominator
            s9.append(b9 / len(nm) if len(nm) else np.nan)
            s5.append(b5 / len(nm) if len(nm) else np.nan)
            # variant: null neighbours INCLUDED, counted below both bars (stored 0.0)
            s9n.append(float((pctl[nb] < 0.9).mean()))
            s5n.append(float((pctl[nb] < 0.5).mean()))
        s9, s5, s9n, s5n = map(np.array, (s9, s5, s9n, s5n))
        c9, c5 = np.array(c9), np.array(c5)
        k = len(centres)
        print(f"\n{tier}: {k:,} artists; median neighbour count {np.median(dg):.0f} "
              f"(p10 {q(dg, 10):.0f}, p90 {q(dg, 90):.0f}); centres with >= 1 null "
              f"neighbour: {nulls_at}; centres with no measured neighbour: "
              f"{int(np.isnan(s9).sum())}")
        print("| bar | share median | p10 | p90 | mean | ZERO below: count | fraction "
              "| median count below | share median, nulls-as-below |")
        print("|---|---|---|---|---|---|---|---|---|")
        for bar, s, cnt, sn in (("< 0.9", s9, c9, s9n), ("< 0.5", s5, c5, s5n)):
            z = int((cnt == 0).sum())
            print(f"| {bar} | {np.nanmedian(s):.4f} | {np.nanpercentile(s, 10):.4f} | "
                  f"{np.nanpercentile(s, 90):.4f} | {np.nanmean(s):.4f} | {z:,} | "
                  f"{z / k:.4f} | {np.median(cnt):.0f} | {np.median(sn):.4f} |")


# ------------------------------------------------------------------ Measurement B
def draw_pairs(rng: random.Random, pool: list[int]) -> list[tuple[int, int]]:
    seen, out = set(), []
    while len(out) < N_PAIRS:
        s, t = rng.sample(pool, 2)
        key = frozenset((s, t))
        if key in seen:
            continue
        seen.add(key)
        out.append((s, t))
    return out


def ladder(store, cfg, key, pctl, measured, s, t) -> dict:
    excludes: list = []
    rec = {"stop": None, "stop_at": None, "depths": {}}
    for k in range(MAX_K + 1):
        res = find_journey(store, s, t, excludes, cfg)
        if res is None:
            rec["stop"], rec["stop_at"] = "no_path", k
            break
        path, rule = res
        interior = path[1:-1]
        if k in DEPTHS:
            vals = [float(pctl[v]) for v in interior if measured[v]]
            rec["depths"][k] = {
                "rule": rule,
                "interior_n": len(interior),
                "null_n": sum(1 for v in interior if not measured[v]),
                "median": float(np.median(vals)) if vals else float("nan"),
            }
        if not interior:
            rec["stop"], rec["stop_at"] = "empty_interior", k
            break
        victim = min(interior, key=key)
        excludes = excludes + [Exclusion(node=victim, reason=KNOWN)]
    return rec


def measure_b(store, pctl, measured) -> None:
    cfg = ApiConfig()
    print(f"\nApiConfig() defaults, read at run time: w_known_ramp_fame_pctl "
          f"{cfg.w_known_ramp_fame_pctl}, w_hop {cfg.w_hop}, w_floor {cfg.w_floor}")
    fame_measured = np.where(measured, pctl, np.nan)  # NaN at nulls, per jfx_g1a_reverify
    key = victim_key(fame_measured, store.pop_raw, store.mbids)

    ids = np.arange(store.artist_count)
    famous_pool = [int(i) for i in ids[measured & (pctl >= FAMOUS_LO)]]
    mid_pool = [int(i) for i in ids[measured & (pctl >= MID_LO) & (pctl <= MID_HI)]]
    rng = random.Random(SEED)
    sets = {"FAMOUS": draw_pairs(rng, famous_pool), "MID": draw_pairs(rng, mid_pool)}
    print(f"seed {SEED}; FAMOUS pool {len(famous_pool):,}; MID pool {len(mid_pool):,}")

    results = {}
    for name, pairs in sets.items():
        t0 = time.time()
        results[name] = []
        for i, (s, t) in enumerate(pairs, 1):
            results[name].append((s, t, ladder(store, cfg, key, pctl, measured, s, t)))
            if i % 10 == 0:
                print(f"  {name} {i}/{len(pairs)}  {time.time() - t0:.0f}s", flush=True)

    for name, rows in results.items():
        print(f"\n### {name}: per pair (median interior fame percentile, nulls excluded; "
              f"'-' = ladder stopped before that depth)")
        print("| # | source (fame pctl) | target (fame pctl) | d0 | d5 | d10 | d20 "
              "| d20 - d0 | interior n d0/d20 | stop rule d0 | ladder stop |")
        print("|---|---|---|---|---|---|---|---|---|---|---|")
        for i, (s, t, r) in enumerate(rows, 1):
            d = r["depths"]
            cell = [f"{d[k]['median']:.3f}" if k in d else "-" for k in DEPTHS]
            delta = (f"{d[20]['median'] - d[0]['median']:+.3f}"
                     if 0 in d and 20 in d else "-")
            ln = f"{d[0]['interior_n'] if 0 in d else '-'}/{d[20]['interior_n'] if 20 in d else '-'}"
            stop = "-" if r["stop"] is None else f"{r['stop']} at k={r['stop_at']}"
            print(f"| {i} | {store.names[s]} ({pctl[s]:.3f}) | {store.names[t]} "
                  f"({pctl[t]:.3f}) | {' | '.join(cell)} | {delta} | {ln} | "
                  f"{d[0]['rule'] if 0 in d else '-'} | {stop} |")

    print("\n### Summary by set x depth (median interior fame percentile per pair)")
    print("| set | presses | pairs with a value | median of pair medians | p10 | p90 "
          "| median interior n | interior nulls excluded |")
    print("|---|---|---|---|---|---|---|---|")
    for name, rows in results.items():
        for k in DEPTHS:
            cells = [r["depths"][k] for _, _, r in rows if k in r["depths"]]
            v = np.array([c["median"] for c in cells])
            v = v[~np.isnan(v)]
            print(f"| {name} | {k} | {len(v)} of {len(rows)} | {np.median(v):.3f} | "
                  f"{q(v, 10):.3f} | {q(v, 90):.3f} | "
                  f"{np.median([c['interior_n'] for c in cells]):.0f} | "
                  f"{sum(c['null_n'] for c in cells)} |")

    print("\n### Paired change, 0 -> 20 presses (d20 median minus d0 median, same pair)")
    print("| set | pairs | median change | p10 | p90 | fell | rose | unchanged "
          "| d20 median < 0.9 | d20 median < 0.5 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for name, rows in results.items():
        dl, d20 = [], []
        for _, _, r in rows:
            d = r["depths"]
            if 20 in d and not np.isnan(d[20]["median"]):
                d20.append(d[20]["median"])
                if 0 in d and not np.isnan(d[0]["median"]):
                    dl.append(d[20]["median"] - d[0]["median"])
        dl, d20 = np.array(dl), np.array(d20)
        print(f"| {name} | {len(dl)} | {np.median(dl):+.3f} | {q(dl, 10):+.3f} | "
              f"{q(dl, 90):+.3f} | {int((dl < 0).sum())} | {int((dl > 0).sum())} | "
              f"{int((dl == 0).sum())} | {int((d20 < 0.9).sum())} of {len(d20)} "
              f"({(d20 < 0.9).mean():.3f}) | {int((d20 < 0.5).sum())} of {len(d20)} "
              f"({(d20 < 0.5).mean():.3f}) |")

    print("\n### Ladder cells (per set)")
    for name, rows in results.items():
        stops = [r["stop"] for _, _, r in rows]
        rules0 = [r["depths"][0]["rule"] for _, _, r in rows if 0 in r["depths"]]
        print(f"{name}: ladders complete to k={MAX_K}: {stops.count(None)}; stopped on empty "
              f"interior: {stops.count('empty_interior')}; stopped on no path: "
              f"{stops.count('no_path')}; stop rule at d0: "
              + ", ".join(f"{u} {rules0.count(u)}" for u in sorted(set(rules0))))


def main() -> None:
    new = load(NEW)
    old = load(OLD)
    jfx = load(JFX_MAP)

    print("\n## Comparability: lux4 vs graph-msw-tu50.bin (the map the JFX critique measured)")
    same_ids = old[0].mbids == jfx[0].mbids
    same_csr = same_ids and bool(
        np.array_equal(old[0].offsets, jfx[0].offsets)
        and np.array_equal(old[0].neighbours, jfx[0].neighbours))
    same_pctl = same_ids and bool(np.array_equal(old[1], jfx[1]))
    print(f"same MBIDs in same order: {same_ids}; identical offsets+neighbours: {same_csr}; "
          f"identical fame_lb_pctl: {same_pctl}")

    print("\n## Measurement A: neighbour shares below fame-percentile bars, each map in its own frame")
    print("Centres: measured-fame artists only (a null is stored as 0.0 and can never "
          "reach 0.90). Headline shares: null neighbours excluded from numerator and "
          "denominator. Variant column: null neighbours kept, counted below both bars.")
    measure_a("lba-a6", *new)
    measure_a("lux4", *old)

    print("\n## Measurement B: routing on lba-a6, shipped find_journey, default ApiConfig()")
    measure_b(*new)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
