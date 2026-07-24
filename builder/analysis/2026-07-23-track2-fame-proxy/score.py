"""P4 step 3: score the fame proxy per pre-registration §5 (as amended by §9 A6).

Four statistics, and the four pre-registered falsifiers. This module DECIDES nothing about
adoption; it computes and prints. It routes no paths and fetches nothing — it reads
`labels.json` and `fan_counts.json`, both committed.

Falsifiers (any one → `nb_fan` unfit → re-run identical protocol on Wikipedia pageviews):
  * AUC < 0.70 on the primary test (S4 excluded), or
  * > 1 catastrophic inversion outside S4, or
  * no valid B_unk exists, or
  * artist-search match failure > 20 % of the sample after normalisation.
"""

import argparse
import json
import math
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
NEVER, HEARD, KNOW = "never heard of", "heard of", "know well"
ORDINAL = {NEVER: 0, HEARD: 1, KNOW: 2}


def auc(pos: list[float], neg: list[float]) -> float:
    """P(random pos > random neg), ties 0.5. Mann–Whitney, no library."""
    if not pos or not neg:
        return float("nan")
    wins = 0.0
    for a in pos:
        for b in neg:
            wins += 1.0 if a > b else 0.5 if a == b else 0.0
    return wins / (len(pos) * len(neg))


def spearman_tie_corrected(xs: list[float], ys: list[float]) -> float:
    """Pearson of average-rank vectors — the tie-corrected Spearman."""
    def avg_rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        ranks = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            r = (i + j) / 2.0 + 1.0
            for k in range(i, j + 1):
                ranks[order[k]] = r
            i = j + 1
        return ranks

    rx, ry = avg_rank(xs), avg_rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    dx = math.sqrt(sum((a - mx) ** 2 for a in rx))
    dy = math.sqrt(sum((b - my) ** 2 for b in ry))
    return num / (dx * dy) if dx and dy else float("nan")


def b_unk(rows: list[dict]) -> dict:
    """Largest threshold t s.t. >=80% of artists with fan < t are 'never heard of',
    requiring >=5 artists below t. Full sample including S4."""
    vals = sorted(r["nb_fan"] for r in rows if r["nb_fan"] is not None)
    best = None
    for t in vals + [max(vals) + 1]:
        below = [r for r in rows if r["nb_fan"] is not None and r["nb_fan"] < t]
        if len(below) < 5:
            continue
        frac_never = sum(r["bucket"] == NEVER for r in below) / len(below)
        if frac_never >= 0.80:
            best = {"threshold": t, "n_below": len(below), "frac_never": frac_never}
    return best or {"threshold": None, "n_below": 0, "frac_never": None}


def main():
    # Proxy-agnostic: defaults reproduce the Deezer run byte-for-byte; --counts / --value-key
    # point the same falsifier math at the Wikipedia-pageviews file (§5 "identical protocol").
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--counts", type=Path, default=HERE / "fan_counts.json",
                    help="a fan_counts.json-shaped file: rows[].query + a magnitude key")
    ap.add_argument("--labels", type=Path, default=HERE / "labels.json",
                    help="the fixed, committed labels — shared across proxies, never re-collected")
    ap.add_argument("--value-key", default="nb_fan",
                    help="per-row magnitude field: nb_fan (Deezer) or pageviews (Wikipedia)")
    ap.add_argument("--out", type=Path, default=HERE / "score.json")
    args = ap.parse_args()

    labels = json.loads(args.labels.read_text(encoding="utf-8"))
    fans = json.loads(args.counts.read_text(encoding="utf-8"))
    # Internal magnitude carries the generic key `nb_fan` regardless of source, so the pure
    # statistics below are unchanged; the source-specific field name lives only in --value-key.
    fan_of = {r["query"]: r.get(args.value_key) for r in fans["rows"]}

    rows = []
    for name, lab in labels.items():
        rows.append({"name": name, "bucket": lab["bucket"], "stratum": lab["stratum"],
                     "nb_fan": fan_of.get(name)})

    scored = [r for r in rows if r["nb_fan"] is not None]
    print(f"scored {len(scored)}/{len(rows)} (unmatched excluded from magnitude stats)\n")

    # --- Primary: AUC, know-well vs heard-of, S4 excluded ---
    pool = [r for r in scored if r["stratum"] != "S4"]
    kw = [r["nb_fan"] for r in pool if r["bucket"] == KNOW]
    ho = [r["nb_fan"] for r in pool if r["bucket"] == HEARD]
    a = auc(kw, ho)
    print(f"PRIMARY  AUC(know-well > heard-of), S4 excluded: {a:.3f}  (n={len(kw)} vs {len(ho)})")
    print(f"         falsifier AUC < 0.70: {'FIRES' if a < 0.70 else 'clear'}")

    # --- Secondary: tie-corrected Spearman, pooled and per stratum ---
    def sp(subset):
        xs = [ORDINAL[r["bucket"]] for r in subset]
        ys = [math.log10(r["nb_fan"]) for r in subset]
        return spearman_tie_corrected(xs, ys), len(subset)
    rho, n = sp(scored)
    print(f"\nSECONDARY (diagnostic, non-gating)  Spearman rho, pooled: {rho:.3f}  (n={n})")
    for s in ["S1", "S2", "S3", "S4"]:
        sub = [r for r in scored if r["stratum"] == s]
        if len({ORDINAL[r["bucket"]] for r in sub}) < 2:
            print(f"         {s}: n={len(sub)}, single bucket — rho undefined")
        else:
            r_s, n_s = sp(sub)
            print(f"         {s}: rho={r_s:.3f} (n={n_s})")

    # --- Catastrophic inversions: know-well below any never-heard fan count ---
    never_max = max((r["nb_fan"] for r in scored if r["bucket"] == NEVER), default=0)
    never_argmax = next(r["name"] for r in scored if r["nb_fan"] == never_max)
    print(f"\nINVERSIONS  highest never-heard fan count: {never_max} ({never_argmax})")
    inv = [r for r in scored if r["bucket"] == KNOW and r["nb_fan"] < never_max]
    inv_out = [r for r in inv if r["stratum"] != "S4"]
    for r in inv:
        tag = " [S4 — Attack 3 blind spot, not counted]" if r["stratum"] == "S4" else ""
        print(f"         know-well below it: {r['name']} ({r['nb_fan']}){tag}")
    print(f"         catastrophic inversions OUTSIDE S4: {len(inv_out)}")
    print(f"         falsifier > 1: {'FIRES' if len(inv_out) > 1 else 'clear'}")

    # --- Band separation ---
    b = b_unk(scored)
    print(f"\nB_unk  {b}")
    print(f"         falsifier (no valid B_unk): {'FIRES' if b['threshold'] is None else 'clear'}")

    # --- Match failure ---
    rate = fans["match_failure_rate"]
    print(f"\nMATCH  failure rate: {rate:.1%}  falsifier > 20 %: {'FIRES' if rate > 0.20 else 'clear'}")

    fired = []
    if a < 0.70: fired.append("AUC < 0.70")
    if len(inv_out) > 1: fired.append(">1 inversion outside S4")
    if b["threshold"] is None: fired.append("no valid B_unk")
    if rate > 0.20: fired.append("match failure > 20%")
    print("\n" + "=" * 60)
    print(f"FALSIFIERS FIRED: {fired if fired else 'NONE — proxy survives'}")

    out = {
        "auc_primary": a, "auc_n_know": len(kw), "auc_n_heard": len(ho),
        "spearman_pooled": rho, "inversions_outside_s4": len(inv_out),
        "inversion_names_outside_s4": [r["name"] for r in inv_out],
        "never_heard_max": {"fan": never_max, "name": never_argmax},
        "b_unk": b, "match_failure_rate": rate, "falsifiers_fired": fired,
    }
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
