"""Apply the FCF- rule and freeze one drop list per censused population.

Governing document (committed before the clip capture existed):
docs/superpowers/specs/2026-08-03-featured-credit-filter-rule.md

This script only APPLIES the committed rule to the committed captures — it
holds no thresholds and makes no calls. It refuses to run from a capture
containing refusals (FCF-3), verifies both worked instances land exactly
where FCF-5 fixed them in advance, and writes the two frozen lists that the
builder wiring copies verbatim into package data:

  fcf_droplist.json        the adopted (ALG-E) population's list
  fcf_droplist_algb.json   the candidate (ALG-B) population's list

The connectivity estimate runs for the adopted population only, exactly as
the no-release lists did (the candidate side has twelve cells and no single
built graph to estimate on).

Run from `builder/`, after fcf_clips.py exits 0:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-featured-credit-filter/fcf_droplist.py
"""

from __future__ import annotations

import json
import sys

from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent

for _sib in ("2026-08-01-label-weighting", "2026-08-02-candidate-tail-census",
             "2026-07-30-track-b-cap-selection"):
    _p = str(HERE.parent / _sib)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from tail_droplist import largest_component_size  # noqa: E402
from ctc_census import candidate_population  # noqa: E402
from cb_metrics import ADOPTED, ADOPTED_SHA  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

CENSUS = HERE / "fcf_census.json"
DISCOGS = HERE / "fcf_discogs.json"
CLIPS = HERE / "fcf_clips.json"
OUT_ADOPTED = HERE / "fcf_droplist.json"
OUT_ALGB = HERE / "fcf_droplist_algb.json"

RULE = (
    "drop iff >= 1 MB release-group credit AND none sole AND no Discogs "
    "main-artist release AND NOT (commercial-DSP link AND a clip resolves "
    "via the app's Deezer->iTunes path)"
)
SNAPSHOT_WARNING = (
    "The clip half is a 2026-08-03 SNAPSHOT, frozen because spec section 9 "
    "requires byte-identical builds and the builder is offline by a hard "
    "rule. A rebuild later applies this date's answer. Re-resolving is a "
    "deliberate act, never a silent build-time refresh."
)

# FCF-5: fixed before any lookup. A run disagreeing with this table is a
# defect in the run, never a reason to edit the table.
EXPECTED = {
    "7e4f57b3-569f-4cde-9ad8-87d9a474fd41": ("田島賢", "drop"),
    "f62c24cd-6101-4588-a3e9-d364fe358cc3": ("TJ Brown", "drop"),
}


def main() -> None:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    discogs = json.loads(DISCOGS.read_text(encoding="utf-8"))
    clips = json.loads(CLIPS.read_text(encoding="utf-8"))

    if clips["refused"] != 0:
        raise SystemExit("FCF-3: the capture records refusals; re-run fcf_clips.py")

    exempt = set(discogs["exempt_mbids_under_discogs_presence"])
    members = set(census["class_mbids"]) - exempt
    keep_by_rule = set(clips["keep_mbids_by_the_rule"])
    print(f"class after exemption {len(members):,}; "
          f"keep by the rule {len(keep_by_rule):,}", flush=True)

    for mbid, (name, expected) in EXPECTED.items():
        actual = "keep" if mbid in keep_by_rule else "drop"
        print(f"FCF-5 check {name}: expected {expected}, actual {actual}", flush=True)
        if actual != expected:
            raise SystemExit(f"FCF-5 violated for {name} -- investigate the run")

    if sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    store = GraphStore.load(ADOPTED)
    adopted = set(store.mbids)
    candidate = candidate_population()

    def freeze(population: set[str], label: str, out: Path,
               connectivity: bool) -> None:
        mine = members & population
        drop = sorted(m for m in mine if m not in keep_by_rule)
        keep = sorted(m for m in mine if m in keep_by_rule)
        print(f"\n{label}: class {len(mine):,} -> drop {len(drop):,}, "
              f"keep {len(keep):,}", flush=True)

        payload: dict = {
            "status": (
                "FCF- rule applied per the committed rule document. Adoption "
                "is the owner's decision; this file is what a yes ships."
            ),
            "rule": RULE,
            "snapshot_warning": SNAPSHOT_WARNING,
            "source": "builder/analysis/2026-08-03-featured-credit-filter/",
            "inputs": {
                "census": "fcf_census.json",
                "discogs": "fcf_discogs.json",
                "clips": "fcf_clips.json",
            },
            "counts": {
                "population": len(population),
                "class_after_exemption": len(mine),
                "drop": len(drop),
                "keep": len(keep),
            },
        }
        if connectivity:
            idx = {m: i for i, m in enumerate(store.mbids)}
            drop_ids = {idx[m] for m in drop}
            before_best, before_out = largest_component_size(store, set())
            after_best, after_out = largest_component_size(store, drop_ids)
            payload["connectivity_estimate_on_the_BUILT_graph"] = {
                "note": ("APPROXIMATE -- a real build recomputes masses, scores "
                         "and the cap with these artists absent, so selection "
                         "shifts. Lower bound on churn, not the build's answer."),
                "largest_component_before": before_best,
                "outside_before": before_out,
                "largest_component_after": after_best,
                "additionally_stranded": after_out,
            }
            print(f"largest component: {before_best} before; {after_best} of "
                  f"{len(store.mbids) - len(drop_ids)} surviving after; "
                  f"additionally stranded {after_out}", flush=True)
        payload["drop_mbids"] = drop
        payload["keep_mbids"] = keep
        out.write_text(json.dumps(payload, indent=1), encoding="utf-8")
        digest = sha256(json.dumps(drop, sort_keys=True).encode()).hexdigest()
        print(f"{out.name}: drop-list sha256 (sorted mbids): {digest}", flush=True)

    freeze(adopted, "ADOPTED (ALG-E)", OUT_ADOPTED, connectivity=True)
    freeze(candidate, "CANDIDATE (ALG-B)", OUT_ALGB, connectivity=False)


if __name__ == "__main__":
    main()
