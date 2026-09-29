"""Quick-look kit for the Dig-deeper exploration. EXPLORATORY: nothing here is evidence.

A *variant* is a Python file defining

    def journey(ctx, s, t, pressed, prev) -> list[int] | None

where `pressed` is the cumulative list of node ids the user has pressed Dig deeper on (oldest
first) and `prev` is the journey shown before the latest press (None at press 0). Optionally it
may define `setup(ctx)` (called once per process, to precompute things; stash results on ctx).

The kit presses Dig deeper on the most famous middle artist each time (the app lets the user pick;
"most famous" is the harshest honest stand-in), for presses 0..10, on 20 fixed pairs (15 famous,
5 mid-fame), and prints journeys at presses 0, 3, 5, 10 plus a summary table.

    cd api && PYTHONIOENCODING=utf-8 uv run python -u ../exploration/kit/qlook.py \
        ../exploration/baseline/today.py --out ../exploration/baseline/runs/today.json [--rate]

`--rate` runs the coherence screen (kit/rate.py) on every step and adds it to the summary.
`--pairs extra.json` swaps the pair set (list of [source_name_or_id, target_name_or_id]).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import statistics
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

KIT = Path(__file__).resolve().parent
ROOT = KIT.parents[1]
sys.path.insert(0, str(ROOT / "builder/analysis/2026-09-27-drp-stage3a"))
sys.path.insert(0, str(KIT))

PRESSES_SHOWN = (0, 3, 5, 10)
MAX_K = 10
N_T1, N_T2, N_MID = 8, 7, 5


class Ctx:
    """Everything a variant needs: the served map, fame percentiles, names, the shipped router."""

    def __init__(self) -> None:
        import drp_common as dc
        from artistpath_api.config import ApiConfig
        self.dc = dc
        self.m = dc.Map(dc.A0_GRAPH, dc.A0_SHA)
        self.store = self.m.store
        self.n = self.m.n
        self.pctl = self.m.pctl          # numpy, nulls at 0.0
        self.pl = self.m.pl              # list version
        self.measured = self.m.measured
        self.off, self.nbr = self.m.off, self.m.nbr
        self.sc = self.store.scores.tolist()
        self.names = list(self.store.names)
        self.key = self.m.key            # victim_key: most famous first
        self.cfg = ApiConfig()
        self.find_journey = dc.find_journey
        self.find_path = dc._pf_mod.find_path
        self.Exclusion, self.KNOWN = dc.Exclusion, dc.KNOWN
        self.id_by_name = {}
        for i, nm in enumerate(self.names):
            self.id_by_name.setdefault(nm.lower(), i)

    def row(self, u):
        a, b = self.off[u], self.off[u + 1]
        return self.nbr[a:b], self.sc[a:b]

    def sim(self, u: int, v: int) -> float:
        nb, sc = self.row(u)
        import bisect
        j = bisect.bisect_left(nb, v)
        return sc[j] if j < len(nb) and nb[j] == v else 0.0

    def known(self, pressed):
        return [self.Exclusion(node=v, reason=self.KNOWN) for v in pressed]

    def lookup(self, x) -> int:
        if isinstance(x, int):
            return x
        return self.id_by_name[x.lower()]


def load_variant(path: str):
    spec = importlib.util.spec_from_file_location(Path(path).stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(Path(path).resolve().parent))
    spec.loader.exec_module(mod)
    return mod


def kit_pairs(ctx, extra=None):
    if extra:
        return [("custom", ctx.lookup(a), ctx.lookup(b)) for a, b in json.loads(Path(extra).read_text(encoding="utf-8"))]
    d = json.loads((ROOT / "builder/analysis/2026-09-27-drp-stage3a/drp_pairs.json").read_text(encoding="utf-8"))
    out = []
    for stratum, n, tag in (("DRP-T1", N_T1, "famous"), ("DRP-T2", N_T2, "famous"), ("DRP-MID", N_MID, "mid")):
        for p in d["strata"][stratum]["pairs"][:n]:
            out.append((tag, p["source"], p["target"]))
    return out


# ---- worker side ---------------------------------------------------------------------------
_W = {}


def _init(variant_path):
    ctx = Ctx()
    mod = load_variant(variant_path)
    if hasattr(mod, "setup"):
        mod.setup(ctx)
    _W["ctx"], _W["mod"] = ctx, mod


def ladder(ctx, mod, s, t, max_k=MAX_K):
    pressed, prev, out = [], None, []
    for k in range(max_k + 1):
        t0 = time.time()
        path = mod.journey(ctx, s, t, list(pressed), prev)
        dt = time.time() - t0
        out.append({"k": k, "path": path, "secs": round(dt, 2)})
        if not path or len(path) <= 2:
            break
        interior = [v for v in path[1:-1] if v not in pressed]
        if not interior:
            break
        pressed.append(min(interior, key=ctx.key))
        out[-1]["victim"] = pressed[-1]
        prev = path
    return out


def _run_pair(args):
    tag, s, t = args
    return tag, s, t, ladder(_W["ctx"], _W["mod"], s, t)


# ---- reporting -----------------------------------------------------------------------------
def describe(ctx, path):
    return " > ".join(f"{ctx.names[v]} ({ctx.pl[v]*100:.0f})" for v in path)


def interior_median(ctx, path):
    vals = [ctx.pl[v] for v in path[1:-1] if ctx.measured[v]]
    return statistics.median(vals) if vals else None


def weakest(ctx, path):
    return min(ctx.sim(u, v) for u, v in zip(path, path[1:]))


def summarise(ctx, rows, ratings=None):
    """Per press: median middle-artist fame pctl (famous / mid pairs), length, weakest link,
    share of middle artists from the top 10% (famous-not-wiped-out), coherence."""
    lines = []
    hdr = f"{'press':>5} | {'fame mid-artists (famous pairs)':>30} | {'(mid pairs)':>11} | {'len':>4} | {'weakest link':>12} | {'top10% share':>12} | {'coherence':>9} | {'bad steps':>9}"
    lines.append(hdr)
    lines.append("-" * len(hdr))
    summary = {}
    for k in range(MAX_K + 1):
        fam, mid, lens, wk, top, coh, bad = [], [], [], [], [], [], []
        for r in rows:
            lad = r["ladder"]
            if k >= len(lad) or not lad[k]["path"]:
                continue
            p = lad[k]["path"]
            im = interior_median(ctx, p)
            if im is not None:
                (fam if r["tag"] == "famous" else mid).append(im)
            lens.append(len(p))
            wk.append(weakest(ctx, p))
            inter = p[1:-1]
            if inter and r["tag"] == "famous":
                top.append(sum(ctx.pl[v] >= 0.9 for v in inter) / len(inter))
            if ratings is not None:
                sc = [ratings.get(step_key(ctx, u, v)) for u, v in zip(p, p[1:])]
                sc = [x for x in sc if isinstance(x, (int, float))]
                if sc:
                    coh.append(sum(sc) / len(sc) / 3.0)
                    bad.append(sum(x <= 1 for x in sc) / len(sc))
        med = lambda xs: statistics.median(xs) if xs else float("nan")
        mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")
        summary[k] = dict(fame_famous=med(fam), fame_mid=med(mid), length=mean(lens), weakest=med(wk),
                          top10_share=mean(top), coherence=mean(coh), bad_steps=mean(bad), n=len(lens))
        s = summary[k]
        lines.append(f"{k:>5} | {s['fame_famous']*100:>30.1f} | {s['fame_mid']*100:>11.1f} | {s['length']:>4.1f} | "
                     f"{s['weakest']:>12.3f} | {s['top10_share']*100:>11.0f}% | {s['coherence']:>9.2f} | {s['bad_steps']*100:>8.0f}%")
    return "\n".join(lines), summary


def step_key(ctx, u, v):
    a, b = sorted((ctx.names[u], ctx.names[v]))
    return f"{a} || {b}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant")
    ap.add_argument("--out", required=True)
    ap.add_argument("--procs", type=int, default=6)
    ap.add_argument("--rate", action="store_true")
    ap.add_argument("--pairs")
    ap.add_argument("--quiet", action="store_true", help="print only presses 0 and 10")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    ctx = Ctx()
    pairs = kit_pairs(ctx, a.pairs)
    t0 = time.time()
    with ProcessPoolExecutor(max_workers=a.procs, initializer=_init, initargs=(str(Path(a.variant).resolve()),)) as ex:
        res = list(ex.map(_run_pair, pairs))
    print(f"# variant {a.variant}   {len(pairs)} pairs   {time.time()-t0:.0f}s", flush=True)
    rows = [{"tag": tag, "source": s, "target": t, "ladder": lad} for tag, s, t, lad in res]

    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    named = {"variant": a.variant, "rows": [
        {**r, "source_name": ctx.names[r["source"]], "target_name": ctx.names[r["target"]],
         "ladder": [{**d, "names": [ctx.names[v] for v in (d["path"] or [])],
                     "pctl": [round(ctx.pl[v], 4) for v in (d["path"] or [])]} for d in r["ladder"]]}
        for r in rows]}
    out.write_text(json.dumps(named, ensure_ascii=False, indent=0), encoding="utf-8")

    ratings = None
    if a.rate:
        import rate
        ratings = rate.rate_run(ctx, rows)

    shown = (0, 10) if a.quiet else PRESSES_SHOWN
    for r in rows:
        print(f"\n## {ctx.names[r['source']]} -> {ctx.names[r['target']]}  [{r['tag']}]")
        for k in shown:
            if k < len(r["ladder"]) and r["ladder"][k]["path"]:
                p = r["ladder"][k]["path"]
                extra = ""
                if ratings is not None:
                    sc = [ratings.get(step_key(ctx, u, v), "?") for u, v in zip(p, p[1:])]
                    extra = "   steps " + "".join(str(x) for x in sc)
                print(f"  p{k:<2} {describe(ctx, p)}{extra}")
            else:
                print(f"  p{k:<2} (none)")
    table, summary = summarise(ctx, rows, ratings)
    print("\n" + table)
    out.with_suffix(".summary.json").write_text(json.dumps(summary, indent=1), encoding="utf-8")
    secs = [d["secs"] for r in rows for d in r["ladder"]]
    print(f"\nrouting time per journey: median {statistics.median(secs):.2f}s  max {max(secs):.2f}s")


if __name__ == "__main__":
    main()
