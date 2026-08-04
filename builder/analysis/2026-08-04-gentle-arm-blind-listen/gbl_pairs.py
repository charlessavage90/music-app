"""Spotify export -> familiarity ranking -> candidate pairs for GBL-AM1.

Spec §3: endpoints come from the owner's familiarity; the export path is a CLI
argument and the raw export NEVER enters the repo. Follow.json holds followed
users, not artists (spec §3 correction), so the sources are the streaming
history and YourLibrary.json.

Output is a PROPOSAL. The owner approves or amends; the approved list becomes
GBL-AM1 in the spec's §8 plus the committed gbl_pairs_approved.json. Nothing
downstream reads the proposal.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gbl_common import ROOT, in_dir, use_cre

PLAY_MS = 30_000          # below this a row is a skip, not a listen
PROPOSED_PAIRS = 12       # owner trims/edits to the spec's 8


def rank_familiarity(history: list[dict], library: dict) -> list[dict]:
    agg: dict[str, dict] = {}
    for row in history:
        name = row["artistName"]
        a = agg.setdefault(name, {"name": name, "ms_played": 0, "plays": 0,
                                  "in_library": False})
        a["ms_played"] += int(row["msPlayed"])
        if int(row["msPlayed"]) >= PLAY_MS:
            a["plays"] += 1
    for t in library.get("tracks", []):
        a = agg.setdefault(t["artist"], {"name": t["artist"], "ms_played": 0,
                                         "plays": 0, "in_library": False})
        a["in_library"] = True
    return sorted(agg.values(), key=lambda a: -a["ms_played"])


def _use_api_src() -> None:
    """Guarded, unlike a bare insert: resolve_in is called once per artist per
    store, and an unguarded insert would grow sys.path by several hundred
    duplicate entries over one run."""
    p = str(ROOT / "api" / "src")
    if p not in sys.path:
        sys.path.insert(0, p)


def resolve_in(store, name: str) -> list[int]:
    use_cre()
    _use_api_src()
    from artistpath_api.search import normalise

    q = normalise(name)
    return [i for i, n in enumerate(store.names) if normalise(n) == q]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True,
                    help='path to the "Spotify Account Data" directory (stays outside the repo)')
    ap.add_argument("--top", type=int, default=150)
    args = ap.parse_args()
    export = Path(args.export)

    history = json.loads(
        (export / "StreamingHistory_music_0.json").read_text(encoding="utf-8"))
    library = json.loads((export / "YourLibrary.json").read_text(encoding="utf-8"))
    ranked = rank_familiarity(history, library)[: args.top]

    use_cre()
    from cre_common import load_adopted
    from cre_gates import load_cell

    v0 = load_adopted()
    _, g = load_cell("B-S1")

    rows = []
    for r in ranked:
        in_v0 = resolve_in(v0, r["name"])
        in_g = resolve_in(g, r["name"])
        rows.append({
            **r,
            "v0_nodes": [{"mbid": v0.mbids[i]} for i in in_v0],
            "g_nodes": [{"mbid": g.mbids[i]} for i in in_g],
            "status": ("ok" if len(in_v0) == 1 and len(in_g) == 1
                       and v0.mbids[in_v0[0]] == g.mbids[in_g[0]]
                       else "ambiguous" if in_v0 and in_g
                       else "missing"),
        })
    usable = [r for r in rows if r["status"] == "ok"]

    # Draft pairs: walk the usable list top-down two at a time so every pair
    # joins two artists the owner demonstrably knows, and adjacent familiarity
    # keeps each pair judgeable end to end (REQ-41). The owner reshuffles freely.
    pairs = [[usable[i]["name"], usable[i + 1]["name"]]
             for i in range(0, min(2 * PROPOSED_PAIRS, len(usable) - 1), 2)]

    in_dir("gbl_pair_candidates.json").write_text(json.dumps({
        "usable": usable, "ambiguous": [r for r in rows if r["status"] == "ambiguous"],
        "missing": [r["name"] for r in rows if r["status"] == "missing"],
        "draft_pairs": pairs,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# GBL pair proposal — approve, strike, or swap; 8 pairs survive\n",
             "| # | A | B | your minutes (A/B) |", "|---|---|---|---|"]
    mins = {r["name"]: round(r["ms_played"] / 60_000) for r in usable}
    for i, (a, b) in enumerate(pairs, 1):
        lines.append(f"| {i} | {a} | {b} | {mins[a]}/{mins[b]} |")
    missing_names = [r["name"] for r in rows if r["status"] == "missing"]
    lines.append("\nArtists you listen to that are missing from one of the two maps "
                 "(cannot be endpoints): " + (", ".join(missing_names) or "none"))
    ambiguous_names = [r["name"] for r in rows if r["status"] == "ambiguous"]
    lines.append("\nArtists whose name matches more than one artist, or matches a "
                 "different artist in each map (cannot be endpoints without a "
                 "hand-picked MBID): " + (", ".join(ambiguous_names) or "none"))
    in_dir("gbl_pair_proposal.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(usable)} usable artists, {len(pairs)} draft pairs; "
          f"wrote gbl_pair_candidates.json + gbl_pair_proposal.md", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
