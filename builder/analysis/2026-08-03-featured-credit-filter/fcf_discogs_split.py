"""Split the Discogs exemptions: sole-credit vs shared-credit-only.

OWNER-PROMPTED MEASUREMENT, 2026-08-03. His spot checks found exempted
artists whose Discogs record is "credited on" / "one song on a collaboration
album" — which fcf_discogs.py's presence test cannot distinguish: it exempts
on ANY appearance in a release-level <artists> block, with no sole-credit
requirement, an asymmetry with the MB side of FCF-1 (which requires a sole
release-group credit). Error direction is exemption-only, but its SIZE was
never measured. This measures it.

Per exempted class member, over the full Discogs releases XML:
  sole    releases whose <artists> block is exactly this artist (and not
          Various Artists) -- unambiguous own-release evidence
  shared  releases where the artist appears in <artists> beside others

An exempted member with sole == 0 is exempt purely through shared album
credits — the suspect class. If the predicate is amended on this evidence,
that is an explicit FCF- amendment with post-result disclosure, never a
quiet edit; this script only measures.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-featured-credit-filter/fcf_discogs_split.py
"""

from __future__ import annotations

import json
import sys
import time
import xml.etree.ElementTree as ET

from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).parent

_CTC = HERE.parent / "2026-08-02-candidate-tail-census"
_TRACK_B = HERE.parent / "2026-07-30-track-b-cap-selection"
for _p in (str(_CTC), str(_TRACK_B)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ctc_census import DISCOGS_RELEASES, candidate_population, pass_artist  # noqa: E402
from cb_metrics import ADOPTED, ADOPTED_SHA  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

CENSUS = HERE / "fcf_census.json"
DISCOGS_JSON = HERE / "fcf_discogs.json"
OUT = HERE / "fcf_discogs_split.json"

# Discogs' Various Artists — a release credited to it carries a curator's
# framing, not any one artist's. Same constant as rel_common.DISCOGS_VARIOUS.
VARIOUS = "194"


def split_pass(wanted: set[str]) -> tuple[dict[str, int], dict[str, int]]:
    """One streaming pass: per Discogs id, sole vs shared <artists> credits."""
    sole: dict[str, int] = defaultdict(int)
    shared: dict[str, int] = defaultdict(int)
    began = time.time()
    seen = 0
    context = ET.iterparse(str(DISCOGS_RELEASES), events=("start", "end"))
    _event, root = next(context)
    for event, elem in context:
        if event != "end" or elem.tag != "release":
            continue
        seen += 1
        artists = elem.find("artists")
        if artists is not None:
            ids = [node.findtext("id") for node in artists]
            ids = [i for i in ids if i]
            for artist_id in ids:
                if artist_id not in wanted:
                    continue
                if len(ids) == 1 and artist_id != VARIOUS:
                    sole[artist_id] += 1
                else:
                    shared[artist_id] += 1
        elem.clear()
        root.clear()
        if seen % 2_000_000 == 0:
            print(f"  discogs: {seen:,} releases "
                  f"({(time.time() - began) / 60:.1f} min)", flush=True)
    print(f"  split pass done: {seen:,} releases in "
          f"{(time.time() - began) / 60:.1f} min", flush=True)
    return dict(sole), dict(shared)


def main() -> None:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    discogs = json.loads(DISCOGS_JSON.read_text(encoding="utf-8"))
    exempt = set(discogs["exempt_mbids_under_discogs_presence"])
    print(f"exempted members: {len(exempt):,}", flush=True)

    signals = pass_artist(exempt)
    did_of = {
        m: rec["discogs"] for m, rec in signals.items() if rec.get("discogs")
    }
    missing = exempt - set(did_of)
    if missing:
        # Exemption required a Discogs id, so every exempted member has one.
        raise SystemExit(f"{len(missing)} exempted members lost their id")

    sole, shared = split_pass(set(did_of.values()))

    sole_members = {m for m, d in did_of.items() if sole.get(d, 0) > 0}
    shared_only = exempt - sole_members

    from hashlib import sha256 as _sha256  # noqa: PLC0415
    if _sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    adopted = set(GraphStore.load(ADOPTED).mbids)
    candidate = candidate_population()

    def block(population: set[str], label: str) -> dict:
        mine = exempt & population
        out = {
            "exempt": len(mine),
            "by_sole_credit": len(mine & sole_members),
            "shared_credit_only": len(mine & shared_only),
            "shared_only_share": round(len(mine & shared_only) / len(mine), 4)
            if mine else None,
        }
        print(f"{label}: exempt {out['exempt']:,} -> sole {out['by_sole_credit']:,}, "
              f"shared-only {out['shared_credit_only']:,} "
              f"({100 * (out['shared_only_share'] or 0):.1f}%)", flush=True)
        return out

    payload = {
        "status": (
            "OWNER-PROMPTED MEASUREMENT. Splits the Discogs exemptions into "
            "sole-credit vs shared-credit-only. Measures; amends nothing."
        ),
        "exempt_members": len(exempt),
        "union": {
            "by_sole_credit": len(sole_members),
            "shared_credit_only": len(shared_only),
            "shared_only_share": round(len(shared_only) / len(exempt), 4),
        },
        "adopted": block(adopted, "ADOPTED (ALG-E)"),
        "candidate": block(candidate, "CANDIDATE (ALG-B)"),
        "shared_only_mbids": sorted(shared_only),
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nshared-credit-only exemptions: {len(shared_only):,} of "
          f"{len(exempt):,} ({100 * len(shared_only) / len(exempt):.1f}%)",
          flush=True)
    print(f"-> {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
