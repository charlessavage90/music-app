"""Track 2F reported-not-gated diagnostics: TF-D1, TF-D2, and pooled interior fame.

Pre-registration §2.3. Offline, deterministic, artifact asserted before anything is read.

TF-D1 is the direct mechanism measurement and the empirical test of the ban corner: if
`TFX` still uses ceiling edges, those hops were unavoidable, which is a finding rather
than a failure. TF-D2 exists because WHAT-GOOD value 3 records an attention ceiling on
path length that is explicitly unquantified -- so length is reported and flagged, never
scored, and the 2x trigger is the author's reporting choice, stated as such.

Run from `api/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-25-track2f-toll-ladder/diagnostics.py
"""

from __future__ import annotations

import hashlib
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(HERE))

from toll_ladder import CEILING_SCORE  # noqa: E402

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
C1_DEPTHS = ("10", "15", "20")


def main() -> int:
    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    assert digest == EXPECT, f"WRONG ARTIFACT: {digest}"

    from artistpath_api.graph_store import GraphStore

    store = GraphStore.load(GRAPH)
    doc = json.loads((HERE / "paths.json").read_text(encoding="utf-8"))
    assert doc["artifact_sha256"] == digest
    fame = json.loads((HERE / "fame.json").read_text(encoding="utf-8"))["fame"]
    mbids = doc["node_mbids"]

    analysis = [p for p in doc["pairs"] if p not in set(doc["held_out_pairs"])]

    def sim(u: int, v: int) -> float | None:
        for w, s in store.neighbours_of(u):
            if w == v:
                return float(s)
        return None

    out = {}
    for arm in doc["arms"]:
        ceiling_hops = total_hops = 0
        interiors: list[int] = []
        famev: list[float] = []
        for pair in analysis:
            for d, path in doc["paths"][arm][pair].items():
                if not path:
                    continue
                for u, v in zip(path, path[1:]):
                    s = sim(u, v)
                    total_hops += 1
                    if s is not None and s >= CEILING_SCORE:
                        ceiling_hops += 1
                if d in C1_DEPTHS:
                    interiors.append(len(path) - 2)
                # Pooled interior fame, every snapshot depth -- the figure Track 2's
                # execution log quotes per arm, recomputed here for comparability.
                famev += [fame[mbids[str(n)]] for n in path[1:-1]
                          if mbids[str(n)] in fame]
        out[arm] = {
            "TF_D1_ceiling_hops": ceiling_hops,
            "TF_D1_total_hops": total_hops,
            "TF_D1_ceiling_frac": ceiling_hops / max(1, total_hops),
            "TF_D2_mean_interiors_d_ge_10": statistics.mean(interiors),
            "TF_D2_max_interiors_d_ge_10": max(interiors),
            "pooled_median_interior_fame": statistics.median(famev),
            "pooled_mean_interior_fame": statistics.mean(famev),
        }

    p_len = out["P"]["TF_D2_mean_interiors_d_ge_10"]
    print(f"{'arm':<9} {'ceiling hops':>13} {'of total':>9} {'%':>7}  "
          f"{'mean int':>8} {'max int':>8}  {'med fame':>8} {'mean fame':>9}  flag")
    for arm, r in out.items():
        ratio = r["TF_D2_mean_interiors_d_ge_10"] / p_len
        flag = "LENGTH >2x P" if ratio > 2.0 else ""
        print(f"{arm:<9} {r['TF_D1_ceiling_hops']:>13,} {r['TF_D1_total_hops']:>9,} "
              f"{100 * r['TF_D1_ceiling_frac']:>6.2f}%  "
              f"{r['TF_D2_mean_interiors_d_ge_10']:>8.2f} "
              f"{r['TF_D2_max_interiors_d_ge_10']:>8} "
              f"{r['pooled_median_interior_fame']:>8.3f} "
              f"{r['pooled_mean_interior_fame']:>9.3f}  {flag}")

    (HERE / "diagnostics.json").write_text(
        json.dumps({"artifact_sha256": digest, "analysis_pairs": analysis,
                    "length_flag_trigger": "mean interiors > 2x P (author's reporting "
                                           "trigger; WHAT-GOOD value 3 holds no threshold)",
                    "by_arm": out}, indent=1),
        encoding="utf-8")
    print(f"\nwrote {HERE / 'diagnostics.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
