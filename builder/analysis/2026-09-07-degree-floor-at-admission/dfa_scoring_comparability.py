"""`DFA-` follow-up: is `top1pct_degree_mass_frac` comparable across these arms?

ARITHMETIC ONLY. Reads `dfa_results.json` and the `DCF-` records beside it,
builds no graph, adopts nothing, recommends nothing. It answers four questions
that were put to the ml-graph-analyst:

  1. Do own-set and fixed-reference scoring rank the arms the same way?
  2. Is a difference of that size meaningful, given tie-domination?
  3. For the one arm whose SHAPE differs, how much of the own-vs-fixed gap is
     shape and how much is the reference set?
  4. What is the measure comparable across?

THE CENTRAL IDENTITY, and everything else follows from it. When at least 1% of
nodes sit AT the degree ceiling C -- i.e. `nodes_tied_at_the_top1pct_boundary`
>= `top1pct_cut_size`, which is true of every shipped-ceiling arm here by a
factor of ~10 -- every node in the top 1% by degree has degree exactly C, so

    top1pct_degree_mass_frac = round(N/100) * C / (2E)
                             = C / (100 * mean_degree)

exactly, for ANY graph in that regime, whatever the rest of its degree
distribution looks like. The measure carries no information about hub structure
there; it is a reparameterisation of mean degree. That is the null model and the
measurement at once, which is why no enrichment ratio can be formed.

Run from this directory:
    UV_LINK_MODE=copy uv run python dfa_scoring_comparability.py
"""

from __future__ import annotations

import json
from math import exp, factorial, log
from pathlib import Path

HERE = Path(__file__).parent
DCF = HERE.parent / "2026-09-07-degree-ceiling-falsifier"


def top_k_degree_sum(hist: dict[str, int], k: int, largest: bool = True) -> int:
    """Sum of the k largest (or smallest) degrees, exactly, from a histogram."""
    total, left = 0, k
    for deg in sorted((int(d) for d in hist), reverse=largest):
        take = min(hist[str(deg)], left)
        total += take * deg
        left -= take
        if left == 0:
            break
    return total


def poisson_upper_95(observed: int) -> float:
    """Smallest lambda with P(X <= observed) <= 0.05."""

    def p_le(k: int, lam: float) -> float:
        return sum(exp(-lam) * lam**i / factorial(i) for i in range(k + 1))

    lo, hi = 0.0, 1000.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if p_le(observed, mid) > 0.05:
            lo = mid
        else:
            hi = mid
    return hi


def main() -> None:
    arms = json.loads((HERE / "dfa_results.json").read_text(encoding="utf-8"))["arms"]
    control = arms[0]
    ctrl_own = control["whole_graph"]["top1pct_degree_mass_frac"]
    ref_size = control["whole_graph"]["top1pct_cut_size"]  # 887

    print("=" * 118)
    print("1. OWN-SET vs FIXED-REFERENCE, and the closed form of each")
    print("=" * 118)
    hdr = (
        f"{'arm':<22}{'N':>7}{'E':>9}{'cut':>5}{'ties/cut':>9}"
        f"{'own':>9}{'cut*C/2E':>10}{'C/100mdeg':>11}"
        f"{'fixed':>9}{'own-ctl':>10}{'fix-ctl':>10}{'own/fixed':>10}"
    )
    print(hdr)
    for a in arms:
        wg, hist = a["whole_graph"], a["degree_histogram"]
        n, e, cut = wg["nodes"], wg["edges"], wg["top1pct_cut_size"]
        own = wg["top1pct_degree_mass_frac"]
        fixed = a["fixed_reference_concentration"][
            "top1pct_degree_mass_frac_fixed_reference"
        ]
        ties = wg["nodes_tied_at_the_top1pct_boundary_degree"] / cut
        print(
            f"{a['label']:<22}{n:>7}{e:>9}{cut:>5}{ties:>8.1f}x"
            f"{own:>9.5f}{cut * 50 / (2 * e):>10.5f}{50 / (100 * wg['mean_degree']):>11.5f}"
            f"{fixed:>9.5f}{own - ctrl_own:>+10.5f}{fixed - ctrl_own:>+10.5f}"
            f"{own / fixed:>10.5f}"
        )

    print()
    print("=" * 118)
    print("2. AMBIGUITY OF THE FIXED-REFERENCE FIGURE UNDER ADMISSIBLE TIE-BREAKS")
    print("   own-set mass is EXACTLY tie-break invariant (all boundary nodes share")
    print("   one degree), so only the fixed-reference column has a range.")
    print("=" * 118)
    print(
        f"{'arm':<22}{'2E':>10}{'max held':>10}{'max frac':>10}{'measured':>10}"
        f"{'sample deficit':>16}{'D_pop 95%':>11}{'width':>9}{'vs control':>11}"
    )
    for a in arms:
        wg, hist = a["whole_graph"], a["degree_histogram"]
        td = 2 * wg["edges"]
        cap = top_k_degree_sum(hist, ref_size)  # 887 largest degrees in this arm
        fixed = a["fixed_reference_concentration"][
            "top1pct_degree_mass_frac_fixed_reference"
        ]
        # The record rounds to 5dp, so take the CONSERVATIVE (largest) deficit
        # consistent with the printed figure.
        held_lo = min(cap, (fixed - 5e-6) * td)
        deficit = max(0.0, ref_size * 50 - held_lo)
        if deficit > 200:
            # Not a tie-break artefact: the reference nodes genuinely lost
            # degree in this arm, so the exchangeability extrapolation is void.
            tail = f"{deficit:>15.1f} {'n/a':>10} {'n/a':>8}"
        else:
            d_pop = poisson_upper_95(int(deficit)) / (ref_size / 9526)
            tail = f"{deficit:>15.1f} {d_pop:>10.0f}{d_pop / td:>9.6f}"
        print(
            f"{a['label']:<22}{td:>10}{cap:>10}{cap / td:>10.6f}{fixed:>10.5f}"
            f"{tail}{fixed - ctrl_own:>+11.5f}"
        )

    print()
    print("=" * 118)
    print("3. THE ONE ARM WHOSE SHAPE DIFFERS: F=2 ascending order")
    print("=" * 118)
    asc = [a for a in arms if "ascending" in a["label"]][0]
    hist, td = asc["degree_histogram"], 2 * asc["whole_graph"]["edges"]
    n897 = top_k_degree_sum(hist, asc["whole_graph"]["top1pct_cut_size"])
    n887 = top_k_degree_sum(hist, ref_size)
    held = asc["fixed_reference_concentration"][
        "top1pct_degree_mass_frac_fixed_reference"
    ] * td
    gap = (n897 - held) / td
    print(f"  own numerator (top {asc['whole_graph']['top1pct_cut_size']}) = {n897}")
    print(f"  own numerator (top {ref_size})                = {n887}")
    print(f"  fixed-reference held                  = {held:.0f}")
    print(f"  denominator 2E                        = {td}  (SHARED by both scorings)")
    print(f"  gap own - fixed = {gap:.5f}")
    print(
        f"    cut-size component   {(n897 - n887) / td:.5f}"
        f"  ({100 * (n897 - n887) / (n897 - held):.1f}% of the gap)"
    )
    print(
        f"    membership component {(n887 - held) / td:.5f}"
        f"  ({100 * (n887 - held) / (n897 - held):.1f}% of the gap)"
    )
    num_r, den_r = n897 / 44350, 1618164 / td
    print(
        f"  own(asc)/own(control) = {num_r:.4f} (numerator) x {den_r:.4f} (1/edges)"
        f" = {num_r * den_r:.4f};"
        f"  log share: edges {100 * log(den_r) / log(num_r * den_r):.1f}%,"
        f" numerator {100 * log(num_r) / log(num_r * den_r):.1f}%"
    )
    sup = sum(int(k) * v for k, v in hist.items() if int(k) > 50)
    nsup = sum(v for k, v in hist.items() if int(k) > 50)
    print(
        f"  nodes above degree 50: {nsup}, holding {sup} endpoints"
        f" = {100 * sup / td:.2f}% of all endpoints, {100 * sup / n897:.1f}% of the"
        f" own top-1% numerator"
    )

    print()
    print("=" * 118)
    print("4. THE SATURATION IDENTITY ON THE `DCF-` CEILING ARMS (cited, not restated")
    print("   -- the figures are that probe's; only the identity is computed here)")
    print("=" * 118)
    for name in ("dcf_results.json", "dcf_results_bridge.json"):
        path = DCF / name
        if not path.is_file():
            print(f"  {name}: absent")
            continue
        for a in json.loads(path.read_text(encoding="utf-8"))["arms"]:
            wg = a["whole_graph"]
            c, mdeg = wg["max_degree"], wg["mean_degree"]
            ident = c / (100 * mdeg)
            ties = wg["nodes_tied_at_the_top1pct_boundary_degree"] / wg["top1pct_cut_size"]
            state = "saturated" if ties >= 1 else "NOT saturated"
            print(
                f"  {name:<24} maxdeg {c:<6} ties/cut {ties:>6.2f}x  {state:<13}"
                f" C/(100*mean_degree) = {ident:.5f}  measured = "
                f"{wg['top1pct_degree_mass_frac']:.5f}  ratio {wg['top1pct_degree_mass_frac'] / ident:.4f}"
            )


if __name__ == "__main__":
    main()
