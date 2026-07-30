"""CB-P1 (design-time, pre-registration input): does the union family bear on DD-F1?

Governing plan: docs/superpowers/plans/2026-07-30-graph-rebuild-track-b.md.
Run BEFORE CB-4 is written, as one of its design inputs -- this is a probe of
the INPUT DATA (the archives), not of any built cell, so it reads no
comparative result and pre-empts no pre-registered read.

WHY. CS-P0c ("superstars are offered zero sub-decile candidates by the crawl
itself, so no cap rule can select one") scoped every cap rule as choosing from
a node's OWN candidate list -- which was the whole design space when the track
was k-tuning inside mutual k-NN. The trimmed_union family widens the effective
candidate set to

    F's own list  UNION  { X : F appears in X's list }

and CS-P0c never measured the reverse direction. Consultant input 2026-07-30
(items 1 and 2, validated against CS-P0c's text before this probe was written)
asks the two questions that decide whether that widening matters:

  Q1  Do sub-decile artists list superstars inside their own top-j? If yes,
      the union creates exactly the famous->obscure edges DD-F1 says do not
      exist, and the prereg must state per family whether its cells bear on
      DD-F1. If no, CS-P0c's bar covers the union family too.

  Q2  What do those reverse edges SCORE, against the superstar's own list's
      50th-strongest? By CS-P0f symmetry (9,486/9,487 pairs identical both
      directions) every reverse-ONLY edge must score below the superstar's own
      100-capped list's tail, so weakest-first trim at an over-D superstar
      should delete ALL of them whenever its own list supplies >= D edges.
      This probe measures the margin, turning that derivation into a checked
      premise rather than an argument.

Read-only over both archives (the harness's ReadOnlyArchive). Fame currency:
percentile RANK over the ADOPTED artifact (pop_pctl, never pop_raw-as-rank).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-track-b-cap-selection/cb_p1_dd_f1_bearing.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "builder" / "src"))
sys.path.insert(0, str(HERE))

from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import (  # noqa: E402
    PERMITTED_ALGORITHMS,
    PRODUCTION_ALGORITHM,
    BuilderConfig,
)
from artistpath_builder.sources.listenbrainz import ListenBrainzSource  # noqa: E402

from cb_build_variants import ARCHIVES, ReadOnlyArchive  # noqa: E402
from cb_metrics import fame_frame  # noqa: E402

# The CS-P0c five, by mbid (resolved from the adopted artifact by name at run
# time so a typo here cannot silently probe the wrong artist).
SUPERSTARS = ("Radiohead", "The Beatles", "Metallica", "Muse", "Coldplay")

ALGORITHMS = {"ALG-E": PRODUCTION_ALGORITHM, "ALG-B": PERMITTED_ALGORITHMS[1]}
BANDS = (
    ("top 10%", 0.90, 1.0001),
    ("upper half", 0.50, 0.90),
    ("lower half", 0.0, 0.50),
)
TOP_J = 50  # the membership window that matters: trimmed_union's j


def superstar_mbids(frame_names: dict[str, str]) -> dict[str, str]:
    """name -> mbid from the adopted artifact; refuse ambiguity silently."""
    out = {}
    for mbid, name in frame_names.items():
        if name in SUPERSTARS and name not in out:
            out[name] = mbid
    missing = [n for n in SUPERSTARS if n not in out]
    if missing:
        raise SystemExit(f"superstars not resolved from adopted artifact: {missing}")
    return out


def scan(label: str, targets: dict[str, str], frame: dict[str, float]) -> dict:
    """One pass over an archive: who lists each superstar, at what rank/score."""
    config = BuilderConfig(algorithm=ALGORITHMS[label])
    source = ListenBrainzSource(config)
    archive = ReadOnlyArchive(LocalArchive(ARCHIVES[label]))

    if config.algorithm == PRODUCTION_ALGORITHM:
        prefix = f"similar/{source.name}/"
    else:
        prefix = f"similar/{source.name}/{config.algorithm}/"

    target_mbids = set(targets.values())
    name_of = {v: k for k, v in targets.items()}

    # Per superstar: reverse listings, and its own list's score ladder.
    # `own_members` is the load-bearing split: a lister the superstar ALSO
    # lists is a MUTUAL pair (reachable by any own-list rule), while a
    # reverse-ONLY lister is reachable by the union family alone — and by
    # CS-P0f symmetry every reverse-only edge must score below the
    # superstar's own list's tail, which is what Q2 verifies.
    reverse: dict[str, list] = {name: [] for name in SUPERSTARS}
    own_lists: dict[str, list[float]] = {}
    own_members: dict[str, set[str]] = {name: set() for name in SUPERSTARS}
    responses = 0

    for key in sorted(archive.keys()):
        if not key.startswith(prefix) or not key.endswith(".json"):
            continue
        lister = key[len(prefix):-len(".json")]
        if "/" in lister:
            continue
        payload = archive.get(key)
        if payload is None:
            continue
        responses += 1
        neighbours = source.parse(payload, exclude_mbid=lister)
        if lister in target_mbids:
            own_lists[name_of[lister]] = [n.score for n in neighbours]
            own_members[name_of[lister]] = {n.mbid for n in neighbours}
        hits = [
            (idx, n) for idx, n in enumerate(neighbours) if n.mbid in target_mbids
        ]
        for idx, n in hits:
            reverse[name_of[n.mbid]].append(
                {
                    "lister": lister,
                    "lister_pctl": frame.get(lister),  # None = not in adopted frame
                    "rank_in_lister_list": idx + 1,
                    "within_top_j": idx < TOP_J,
                    "score": n.score,
                }
            )

    out: dict = {"responses_scanned": responses, "superstars": {}}
    for name in SUPERSTARS:
        rows = reverse[name]
        ladder = sorted(own_lists.get(name, []), reverse=True)
        floor_50 = ladder[TOP_J - 1] if len(ladder) >= TOP_J else None
        tail = ladder[-1] if ladder else None

        per_band: dict[str, dict] = {}
        for band, lo, hi in BANDS:
            in_band = [
                r for r in rows
                if r["lister_pctl"] is not None and lo <= r["lister_pctl"] < hi
            ]
            top_j = [r for r in in_band if r["within_top_j"]]
            per_band[band] = {
                "listers": len(in_band),
                "within_top_j": len(top_j),
                "max_score": max((r["score"] for r in in_band), default=None),
                "max_score_within_top_j": max(
                    (r["score"] for r in top_j), default=None
                ),
            }
        unresolved = [r for r in rows if r["lister_pctl"] is None]

        # Q2's margin: every reverse-ONLY lister scores below the superstar's
        # own tail by symmetry; the design question is the gap to its 50th.
        # Mutual sub-decile listers are reported separately — they are
        # reachable by ANY own-list rule and say nothing about the union
        # family in particular.
        sub_decile_rows = [
            r for r in rows
            if r["lister_pctl"] is not None and r["lister_pctl"] < 0.90
        ]
        mutual_sd = [r for r in sub_decile_rows if r["lister"] in own_members[name]]
        reverse_only_sd = [
            r for r in sub_decile_rows if r["lister"] not in own_members[name]
        ]
        max_reverse_only = max((r["score"] for r in reverse_only_sd), default=None)

        out["superstars"][name] = {
            "own_list_len": len(ladder),
            "own_list_score_floor_at_50": floor_50,
            "own_list_score_tail": tail,
            "total_listers": len(rows),
            "listers_not_in_adopted_frame": len(unresolved),
            "per_band": per_band,
            "sub_decile_listers": len(sub_decile_rows),
            "sub_decile_listers_within_top_j": sum(
                1 for r in sub_decile_rows if r["within_top_j"]
            ),
            "mutual_sub_decile_listers": len(mutual_sd),
            "reverse_only_sub_decile_listers": len(reverse_only_sd),
            "reverse_only_sub_decile_within_top_j": sum(
                1 for r in reverse_only_sd if r["within_top_j"]
            ),
            "max_reverse_only_sub_decile_score": max_reverse_only,
            # The symmetry+truncation derivation, checked: every reverse-only
            # edge must score below the own-list TAIL, hence below the 50th.
            "q2_reverse_only_all_below_tail": (
                max_reverse_only < tail
                if (max_reverse_only is not None and tail is not None)
                else None
            ),
            "q2_trim50_would_delete_all_reverse_only": (
                max_reverse_only < floor_50
                if (max_reverse_only is not None and floor_50 is not None)
                else None
            ),
        }
    return out


def main() -> None:
    frame = fame_frame()

    # Names come from the adopted artifact too, so resolution shares identity
    # with the frame.
    from artistpath_builder.artifact import deserialise
    from cb_metrics import ADOPTED

    graph = deserialise(ADOPTED.read_bytes())
    frame_names = dict(zip(graph.mbids, graph.names))
    targets = superstar_mbids(frame_names)

    out = {"probe": "CB-P1", "design_time": True, "top_j": TOP_J, "archives": {}}
    for label in ("ALG-E", "ALG-B"):
        print(f"scanning {label}…", flush=True)
        out["archives"][label] = scan(label, targets, frame)
        for name, row in out["archives"][label]["superstars"].items():
            print(
                f"  {label} {name}: {row['sub_decile_listers']} sub-decile listers "
                f"= {row['mutual_sub_decile_listers']} mutual + "
                f"{row['reverse_only_sub_decile_listers']} reverse-only "
                f"({row['reverse_only_sub_decile_within_top_j']} in top-{TOP_J}); "
                f"max reverse-only score {row['max_reverse_only_sub_decile_score']} "
                f"vs own tail {row['own_list_score_tail']} / 50th "
                f"{row['own_list_score_floor_at_50']}",
                flush=True,
            )

    (HERE / "cb_p1_dd_f1_bearing.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )
    print("wrote cb_p1_dd_f1_bearing.json")


if __name__ == "__main__":
    main()
