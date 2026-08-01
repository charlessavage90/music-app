"""Style-column quality filters: the owner's gradient vs cross-source folding.

DIAGNOSTIC, NO BARS. Owner-directed 2026-08-01 after the `WGT-` grid closed.
Asks which of two rival explanations for the style column's measured cost
survives measurement:

  the gradient    -- the rare end of the style vocabulary is junk, so any
                     union with styles dilutes the signal (owner's read,
                     recorded in STYLE-VOCABULARY.md);
  fragmentation   -- MB and Discogs spell the same genre differently
                     ("drum n bass" / "drum and bass"; "rhythm & blues";
                     "hiphop" / "hip hop"), so cross-source agreement is
                     mechanically missed and unions inflate. A measurement
                     artifact, not a fact about styles.

FIVE VARIANTS of the style column, each against the baseline differing by
exactly the style column's content, plain Jaccard only (the committed
directions live on plain):

  floor400 / floor200  -- styles with >= N carriers (the owner's bands)
  mbx                  -- styles that also appear in the MB vocabulary (naive)
  folded               -- ALL sources folded through the variant key below,
                          styles unfiltered; two isolations (onto W1f, onto
                          W4f), because the folded arm is the one that could
                          overturn a recorded direction.

THE FOLD, applied after the frozen `norm_genre` (which already handles case,
diacritics, hyphens/underscores and the " music" suffix -- checked, not
assumed): "&" -> "and"; standalone token "n" -> "and"; slash-compounds split
into their parts ("rnb/swing" -> rnb + swing; also MB's "pop/rock" class,
which the committed genre whitelist already excludes -- the split is for the
two Discogs styles and any future widening); then the SPACELESS join as the
matching key, so "hip hop" == "hiphop". A two-entry hand map covers what
mechanics cannot: prog rock -> progressive rock, rnb/r&b -> rhythm and blues.

REPRODUCTION GUARD: the unfolded W0 and W1 baselines must reproduce the
committed `wgt_grid.json` plain cells exactly; nothing is read otherwise.

Run from `builder/` (~25 min):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-01-label-weighting/wgt_style_filters.py \
        --capture <path>/alge_capture.npz
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
_REL = HERE.parent / "2026-07-31-release-tag-coverage"
for _p in (_TAS, _REL):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from tas_common import GLOBAL_NEUTRAL_FALLBACK, graph_mbids  # noqa: E402
from tas_signal import iqr  # noqa: E402
from tas_weighting import spearman  # noqa: E402
from td_turnover import Capture  # noqa: E402

from wgt_grid import CAPTURE_SHA  # noqa: E402
from wgt_tables import df_of, source_columns  # noqa: E402

OUT = HERE / "wgt_style_filters.json"

HAND_FOLDS = {
    "progrock": "progressiverock",
    "rnb": "rhythmandblues",
    "randb": "rhythmandblues",
}


def fold_label(lab: str) -> list[str]:
    """Variant key(s) for one already-norm_genre'd label. Slash splits."""
    parts = lab.split("/") if "/" in lab else [lab]
    out = []
    for p in parts:
        p = p.replace("&", " and ")
        toks = ["and" if t == "n" else t for t in p.split()]
        key = "".join(toks)
        if key:
            out.append(HAND_FOLDS.get(key, key))
    return out


def fold_sets(sets: dict[str, set[str]]) -> dict[str, set[str]]:
    return {m: {k for lab in s for k in fold_label(lab)} for m, s in sets.items()}


def union(a: dict[str, set[str]], b: dict[str, set[str]]) -> dict[str, set[str]]:
    return {m: a.get(m, set()) | b.get(m, set()) for m in a.keys() | b.keys()}


def plain_pass(cap: Capture, labels: dict[str, set[str]],
               population: set[int] | None) -> tuple[dict, set[int]]:
    """Plain-Jaccard spread + pooled redundancy on the fixed population.

    Mirrors the committed signal_on shape: raw values only, per-list iqr,
    pooled (strength, agreement) spearman. Returns stats and the scorable
    owner set (used once, to fix the population off W0).
    """
    sets = [labels.get(m, set()) for m in cap.mbids]
    spreads, pairs = [], []
    scorable: set[int] = set()
    for u in range(cap.n):
        lo, hi = int(cap.offsets[u]), int(cap.offsets[u + 1])
        if lo == hi or not sets[u]:
            continue
        own = sets[u]
        got = []
        for pos in range(lo, hi):
            cand = sets[int(cap.s_cand[pos])]
            if not cand:
                continue
            got.append((float(cap.s_rank[pos]), len(own & cand) / len(own | cand)))
        s = iqr([v for _r, v in got])
        if s is None:
            continue
        scorable.add(u)
        if population is not None and u not in population:
            continue
        spreads.append(s)
        pairs.extend(got)
        if u % 20000 == 0:
            print(f"    {u}/{cap.n}", flush=True)
    x = np.array([r for r, _ in pairs])
    y = np.array([v for _, v in pairs])
    return ({"median_iqr": round(statistics.median(spreads), 4) if spreads else None,
             "spearman_vs_similarity": round(spearman(x, y), 4) if len(x) > 2 else None,
             "lists": len(spreads)},
            scorable)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture", required=True)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()

    digest = hashlib.sha256(Path(args.capture).read_bytes()).hexdigest()
    if digest != CAPTURE_SHA:
        raise SystemExit(f"capture sha mismatch: {digest}")
    cap = Capture(Path(args.capture))

    committed = json.loads((HERE / "wgt_grid.json").read_text(encoding="utf-8"))

    src = source_columns()
    w0, f1 = src["F0_artist_page"], src["F1_mb_release_groups"]
    f4, f5 = src["F4_discogs_genre"], src["F5_discogs_style"]
    w1 = union(w0, f1)
    style_df = df_of(f5)
    w0_vocab = set().union(*w0.values())

    # ---- fold bookkeeping: what merges, and what becomes MB-matched ----
    folded_style_vocab = {k for s in fold_sets(f5).values() for k in s}
    w0f_vocab = {k for s in fold_sets(w0).values() for k in s}
    newly_matched = sorted(
        lab for lab in style_df
        if lab not in w0_vocab
        and any(k in w0f_vocab for k in fold_label(lab)))
    fold_stats = {
        "style_labels_unfolded": len(style_df),
        "style_keys_folded": len(folded_style_vocab),
        "w0_vocab_unfolded": len(w0_vocab),
        "w0_keys_folded": len(w0f_vocab),
        "discogs_only_styles_becoming_mb_matched": len(newly_matched),
        "examples": newly_matched[:15],
    }
    print(f"fold: {len(style_df)} styles -> {len(folded_style_vocab)} keys; "
          f"{len(newly_matched)} Discogs-only styles now match MB", flush=True)

    # ---- baselines, with the reproduction guard ----
    print("[W0] population pass", flush=True)
    w0_stats, scorable = plain_pass(cap, w0, None)
    print("[W1] baseline", flush=True)
    w1_stats, _ = plain_pass(cap, w1, scorable)
    for name, got, want in (
            ("W0", w0_stats, committed["frames"]["W0"]["cells"]["plain"]),
            ("W1", w1_stats, committed["frames"]["W1"]["cells"]["plain"])):
        if abs(got["median_iqr"] - want["median_iqr"]) > 5e-5 or \
           abs(got["spearman_vs_similarity"] - want["spearman_vs_similarity"]) > 5e-5:
            raise SystemExit(f"reproduction FAILED on {name}: {got} != {want}")
        print(f"  reproduction PASS on {name}", flush=True)

    def filtered(pred) -> dict[str, set[str]]:
        return {m: {lab for lab in s if pred(lab)} for m, s in f5.items()}

    results: dict = {"fold": fold_stats, "variants": {}}

    def isolate(tag: str, base_stats: dict, base_labels, style_col) -> None:
        print(f"[{tag}]", flush=True)
        arm_stats, _ = plain_pass(cap, union(base_labels, style_col), scorable)
        results["variants"][tag] = {
            "baseline": base_stats, "with_styles": arm_stats,
            "spread_delta": round(arm_stats["median_iqr"] - base_stats["median_iqr"], 4),
            "redundancy_delta": round(
                arm_stats["spearman_vs_similarity"]
                - base_stats["spearman_vs_similarity"], 4),
        }
        v = results["variants"][tag]
        print(f"  spread {v['spread_delta']:+.4f}  redundancy "
              f"{v['redundancy_delta']:+.4f}", flush=True)

    isolate("floor400_onto_W1", w1_stats, w1,
            filtered(lambda lab: style_df[lab] >= 400))
    isolate("floor200_onto_W1", w1_stats, w1,
            filtered(lambda lab: style_df[lab] >= 200))
    isolate("mbx_onto_W1", w1_stats, w1,
            filtered(lambda lab: lab in w0_vocab))

    w1f, f5f = fold_sets(w1), fold_sets(f5)
    print("[W1f] folded baseline", flush=True)
    w1f_stats, _ = plain_pass(cap, w1f, scorable)
    isolate("folded_onto_W1f", w1f_stats, w1f, f5f)

    w4f = union(w1f, fold_sets(f4))
    print("[W4f] folded second baseline", flush=True)
    w4f_stats, _ = plain_pass(cap, w4f, scorable)
    isolate("folded_onto_W4f", w4f_stats, w4f, f5f)

    committed_reference = {
        "unfolded_styles_onto_W1_from_grid": {
            "spread_delta": round(
                committed["frames"]["W5"]["cells"]["plain"]["median_iqr"]
                - committed["frames"]["W1"]["cells"]["plain"]["median_iqr"], 4),
            "redundancy_delta": round(
                committed["frames"]["W5"]["cells"]["plain"]["spearman_vs_similarity"]
                - committed["frames"]["W1"]["cells"]["plain"]["spearman_vs_similarity"],
                4),
        }}

    Path(args.out).write_text(json.dumps({
        "note": "Diagnostic, no bars, owner-directed. Plain Jaccard only; the "
                "committed WGT- verdicts stand on their own substrate. The folded "
                "variants change the NORMALISER, not the vocabulary choice, and "
                "nothing here amends TAS- section 1.",
        "capture_sha256": digest,
        "committed_reference": committed_reference,
        **results,
    }, indent=1), encoding="utf-8")
    print(f"\nwrote {args.out}", flush=True)


if __name__ == "__main__":
    main()
