"""`DCF-` edge fate — which of our two cap steps kills an edge, by fame band.

THE HYPOTHESIS THIS TESTS (stated before the numbers exist, and it is not mine)
  `trimmed_union` cuts twice. First it keeps an edge only if EITHER endpoint
  ranks the other in its own top fifty (`union_top_j`). Then it trims each
  artist down to fifty connections by deleting its weakest (`union_degree_
  ceiling`). Those two steps should hurt different artists:

    an OBSCURE artist's list is short and points upward at artists it ranks
    highly, so it survives the first cut and loses edges at the TRIM, from the
    famous end;

    a MIDDLE-FAME artist has a full list whose lower half points at other
    middle-fame artists whose lists are also full, so neither ranks the other
    in its top fifty and the edge dies at the FIRST CUT with nothing to rescue
    it.

  If that is right, the union-width cut is costless at the bottom and expensive
  in the middle. Nothing in the record has looked. Reporting the two death
  counts SEPARATELY is the whole point of this script.

WHY THIS IS NOT AN EDIT TO `q4_added_set_supply.py`
  The instrument is that one — same read, same archive-to-artifact decomposition,
  and its reproduction of `CXR-P2`/`CXR-M5` is still the check that the read is
  being taken correctly (`dcf_edge_fate` re-runs that reproduction as its own
  gate below). But `q4` is a COMMITTED probe whose outputs the `LBD-` plan
  review cites, and `cb_build_variants.py`'s standing warning is explicit that a
  changed comparison needs a NEW harness rather than an edit to the old one, or
  the old figures stop being reproducible. So this extends it in place beside
  the sweep, and leaves `q4` exactly as the review ran it.

  ⚠ ONE THING IT FIXES RATHER THAN INHERITS. `q4`'s own weakest link is that
  its top-j step is a RECONSTRUCTION of `trimmed_union_cap`'s first half, not
  the builder's code path. This calls the SHIPPED `trimmed_union_cap` TWICE —
  once with the ceiling set so high it cannot bind (isolating the top-j union
  exactly), once at the shipped ceiling of 50 — so both stages are the shipped
  function's own output and the reconstruction caveat does not apply.

BANDING — three different quantities, and they are not interchangeable
  Bands are FAME PERCENTILE, computed within the served artifact by the shipped
  `GraphStore.fame_percentiles` (0 = nobody on this map has fewer recorded
  listeners; 1 = nobody has more). NOT raw fame (`fame_lb` is a value, never a
  rank), and NOT degree, which is what the sweep's hub classification uses.
  Reading one of these as another has produced three wrong conclusions here
  (§2.6, §2.11, §2.12).

SCOPE
  Descriptive. It measures which edges our construction deletes. It does NOT
  route: no path is built, no criterion is evaluated, and no rule change is
  proposed — the union width is part of the parked cap-rule decision and is the
  owner's (`specs/2026-09-06-own-similarity-design.md` §9).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-09-07-degree-ceiling-falsifier/dcf_edge_fate.py
"""

from __future__ import annotations

import hashlib
import json
import logging
import sys
import time
from collections import defaultdict
from pathlib import Path

from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig
from artistpath_builder.featured_credit_drop import load_featured_credit_drop_mbids
from artistpath_builder.no_release_drop import load_drop_mbids
from artistpath_builder.unlistenable_drop import load_unlistenable_list
from artistpath_builder.graph import (
    largest_component,
    symmetrise,
    trimmed_union_cap,
)
from artistpath_builder.pipeline import damped_strength, is_special_purpose
from artistpath_builder.sources.listenbrainz import (
    ListenBrainzSource,
    harvest_identities,
)

logger = logging.getLogger(__name__)

HERE = Path(__file__).parent
SCRATCH = HERE.parent.parent / "scratch"

# The SERVED map and the archive it was built from. NEXT.md pins the
# `.pre-cex-snapshot` tree for any build of the served lineage — the extended
# sibling gained tens of thousands of payloads after this artifact was built,
# and reading it here would measure a population this artifact never saw.
SERVED = SCRATCH / "graph-msw-tu50.bin"
ARCHIVE_ROOT = SCRATCH / "grt-archive-algb.pre-cex-snapshot"
SUBTREE = ARCHIVE_ROOT / "similar" / "listenbrainz" / CANDIDATE_ALGORITHM

# High enough that the trim provably cannot bind: the largest pre-trim degree
# any ALG-B graph has shown is far below this. Asserted at run time, not
# assumed — if it ever binds, the top-j isolation is silently wrong.
NO_TRIM = 10_000_000

BANDS = [(i / 10, (i + 1) / 10) for i in range(10)]


def band_of(pctl: float) -> int:
    """Index of the fame-percentile band. 1.0 belongs in the top band."""
    return min(9, int(pctl * 10))


def band_label(i: int) -> str:
    lo, hi = BANDS[i]
    return f"{lo:.1f}-{hi:.1f}"


def verify_against_sidecar(path: Path) -> dict:
    sidecar = path.with_suffix(".bin.json")
    manifest = json.loads(sidecar.read_text(encoding="utf-8"))
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != manifest.get("sha256"):
        raise ValueError(
            f"{path.name} sha256 {digest[:12]}… does not match its sidecar. "
            "Artifacts under scratch/ are not interchangeable."
        )
    logger.info("verified %s sha %s…", path.name, digest[:12])
    return manifest


def read_archive_payloads() -> dict[str, bytes]:
    """Read-only, by construction: nothing here can write (GRT-A1).

    Opened by direct iteration rather than through `LocalArchive`, whose
    constructor `mkdir`s its root — a write, and the one thing a probe over an
    irreplaceable archive must not do.
    """
    payloads: dict[str, bytes] = {}
    for path in sorted(SUBTREE.iterdir()):
        if path.suffix == ".json" and path.is_file():
            payloads[path.stem] = path.read_bytes()
    logger.info("read %d payloads (read-only)", len(payloads))
    return payloads


def surviving_population(
    payloads: dict[str, bytes], config: BuilderConfig
) -> tuple[set[str], set[str]]:
    """`known` after the drops, in `build_from_archive`'s documented order.

    Mirrors the shipped stage order and calls the shipped drop loaders, so the
    only thing restated here is the ORDER — the `cb_build_variants.py` pattern.

    ⚠ `drop_unlistenable` is ON here, unlike in the sweep, and the difference is
    not an inconsistency — it is what makes the reproduction gate possible. The
    served artifact's own manifest records `drop_unlistenable: true`, and this
    population IS the one the ULF- census evaluated (the pre-CEX 75,000), so the
    guard does not refuse. The sweep turns it off because its population is the
    EXTENDED crawl, which the census never saw and which the guard therefore
    refuses outright.

    Validated downstream: if this set were wrong, the reconstructed final graph
    would not reproduce the served artifact's edges, and the gate would fail.
    """
    known = set(payloads)
    identities = harvest_identities(payloads.values())

    excluded = {
        mbid
        for mbid, (_name, disambiguation) in identities.items()
        if is_special_purpose(disambiguation)
    } if config.filter_special_purpose else set()
    known -= excluded

    nameless = {m for m, (name, _d) in identities.items() if not name.strip()}
    nameless |= known - identities.keys()
    excluded |= nameless
    known -= nameless

    if config.drop_no_release_tail:
        no_release = load_drop_mbids(config.algorithm) & known
        excluded |= no_release
        known -= no_release

    if config.drop_featured_credit:
        featured = load_featured_credit_drop_mbids(config.algorithm) & known
        excluded |= featured
        known -= featured

    if config.drop_unlistenable:
        ulf = load_unlistenable_list(config.algorithm, config.unlistenable_list_path)
        unevaluated = frozenset(payloads) - ulf.censused_mbids
        if unevaluated:
            raise SystemExit(
                f"{len(unevaluated)} artist(s) were never censused; this probe "
                "is over the SERVED lineage and must not silently under-filter."
            )
        unlistenable = ulf.drop_mbids & known
        excluded |= unlistenable
        known -= unlistenable

    logger.info("known after drops: %d (excluded %d)", len(known), len(excluded))
    return known, excluded


def build_stages(payloads, known, excluded, config, source):
    """The two cap stages, both from the SHIPPED `trimmed_union_cap`."""
    mass: dict[str, float] = {}
    raw_lists = {}
    for mbid in sorted(known):
        neighbours = [
            n for n in source.parse(payloads[mbid], exclude_mbid=mbid)
            if n.mbid not in excluded
        ]
        raw_lists[mbid] = neighbours
        mass[mbid] = sum(n.score for n in neighbours) or 1.0

    damping = config.similarity_damping
    adjacency: dict[str, dict[str, float]] = {}
    for mbid in sorted(known):
        mass_a = mass[mbid]
        adjacency[mbid] = {
            n.mbid: damped_strength(n.score, mass_a, mass[n.mbid], damping)
            for n in raw_lists[mbid]
            if n.mbid in known
        }
    # `ranking` is the same unclipped strengths the pipeline ranks on. The
    # emitted (rescaled) scores are deliberately NOT computed: the p99 clip
    # changes score VALUES and never edge survival, which is all this measures.
    ranking = {m: dict(e) for m, e in adjacency.items()}

    logger.info("pre-cap directed edges: %d", sum(len(e) for e in adjacency.values()))

    after_topj = trimmed_union_cap(adjacency, config.union_top_j, NO_TRIM,
                                   ranking=ranking)
    after_trim = trimmed_union_cap(adjacency, config.union_top_j,
                                   config.union_degree_ceiling, ranking=ranking)
    return adjacency, after_topj, after_trim


def pair_set(adjacency) -> set[tuple[str, str]]:
    """Undirected pairs, deduped."""
    pairs = set()
    for node, edges in adjacency.items():
        for dst in edges:
            pairs.add((node, dst) if node < dst else (dst, node))
    return pairs


def main() -> int:
    started = time.monotonic()
    sys.path.insert(0, str((HERE.parent.parent.parent / "api" / "src").resolve()))
    from artistpath_api.graph_store import GraphStore  # noqa: PLC0415

    manifest = verify_against_sidecar(SERVED)
    served = GraphStore.load(SERVED)
    if served.fame_lb_pctl is None:
        raise SystemExit("served artifact carries no fame_lb; cannot band")
    pctl_of = dict(zip(served.mbids, served.fame_lb_pctl.tolist()))
    served_set = set(served.mbids)

    # Shipped config except `require_fame`, which cannot touch edge survival —
    # fame is metadata, read here from the served artifact instead.
    config = BuilderConfig(algorithm=CANDIDATE_ALGORITHM, require_fame=False)
    source = ListenBrainzSource(config)
    payloads = read_archive_payloads()
    known, excluded = surviving_population(payloads, config)
    adjacency, after_topj, after_trim = build_stages(
        payloads, known, excluded, config, source
    )

    max_pre_trim = max((len(e) for e in after_topj.values()), default=0)
    if max_pre_trim >= NO_TRIM:
        raise SystemExit(
            f"NO_TRIM={NO_TRIM} actually bound (max degree {max_pre_trim}); the "
            "top-j isolation would be wrong. Raise it and re-run."
        )

    final_adj = symmetrise(after_trim)
    keep = largest_component(final_adj)
    final_pairs = {
        (a, b) for (a, b) in pair_set(final_adj) if a in keep and b in keep
    }

    archive_pairs = pair_set(adjacency)
    topj_pairs = pair_set(after_topj)
    trim_pairs = pair_set(after_trim)

    # ---- GATE: does the reconstruction reproduce the SERVED artifact? -----
    # Green half. If `known` or the stage order were wrong, this fails — which
    # is what makes every band figure below trustworthy rather than plausible.
    served_pairs = set()
    for i, mbid in enumerate(served.mbids):
        lo, hi = int(served.offsets[i]), int(served.offsets[i + 1])
        for j in served.neighbours[lo:hi]:
            other = served.mbids[int(j)]
            served_pairs.add((mbid, other) if mbid < other else (other, mbid))
    matched = len(final_pairs & served_pairs)
    gate = {
        "reconstructed_edges": len(final_pairs),
        "served_artifact_edges": len(served_pairs),
        "in_both": matched,
        "only_in_reconstruction": len(final_pairs - served_pairs),
        "only_in_served_artifact": len(served_pairs - final_pairs),
        "exact": final_pairs == served_pairs,
        "agreement": round(matched / max(1, len(served_pairs)), 6),
    }
    # Red half: an instrument never shown to move is not an instrument. The
    # top-j stage MUST hold strictly more edges than the trimmed stage, and the
    # trimmed stage strictly more than the final component.
    gate["red_stages_are_distinct"] = (
        len(archive_pairs) > len(topj_pairs) > len(trim_pairs) >= len(final_pairs)
    )
    logger.info("gate: %s", json.dumps(gate))

    # ---- per-band edge fate, counted in ENDPOINT SLOTS -------------------
    # An edge between band 3 and band 7 is counted once in band 3 and once in
    # band 7, so a band's row reads as "what happened to the edges of the
    # artists in this band". Edge TOTALS are therefore double the pair counts;
    # the pair counts are in the gate above.
    rows = {i: defaultdict(int) for i in range(10)}
    band_artists = defaultdict(int)
    for mbid in served.mbids:
        band_artists[band_of(pctl_of[mbid])] += 1

    # Cross-tab: for an edge that dies at the top-j cut, what band is the OTHER
    # end in? This is the half that says whether mid-fame artists lose links to
    # their own band.
    topj_death_crosstab = {i: defaultdict(int) for i in range(10)}
    OTHER_UNSERVED = "not-in-served-map"

    for a, b in archive_pairs:
        in_topj = (a, b) in topj_pairs
        in_trim = (a, b) in trim_pairs
        in_final = (a, b) in final_pairs
        if in_final:
            fate = "survived"
        elif in_trim:
            fate = "died_at_the_component_prune"
        elif in_topj:
            fate = "died_at_the_degree_trim"
        else:
            fate = "died_at_the_topj_cut"
        for end, other in ((a, b), (b, a)):
            if end not in served_set:
                continue
            i = band_of(pctl_of[end])
            rows[i]["archive_edges"] += 1
            rows[i][fate] += 1
            if fate == "died_at_the_topj_cut":
                key = (
                    band_label(band_of(pctl_of[other]))
                    if other in served_set else OTHER_UNSERVED
                )
                topj_death_crosstab[i][key] += 1

    table = []
    for i in range(10):
        r = rows[i]
        total = r["archive_edges"]
        n = band_artists[i]
        table.append({
            "band": band_label(i),
            "artists": n,
            "archive_edges": total,
            "archive_edges_per_artist": round(total / n, 2) if n else 0.0,
            "died_at_the_topj_cut": r["died_at_the_topj_cut"],
            "died_at_the_degree_trim": r["died_at_the_degree_trim"],
            "died_at_the_component_prune": r["died_at_the_component_prune"],
            "survived": r["survived"],
            "share_died_at_the_topj_cut": round(r["died_at_the_topj_cut"] / total, 5)
            if total else 0.0,
            "share_died_at_the_degree_trim": round(
                r["died_at_the_degree_trim"] / total, 5) if total else 0.0,
            "share_survived": round(r["survived"] / total, 5) if total else 0.0,
            "survived_per_artist": round(r["survived"] / n, 2) if n else 0.0,
        })

    crosstab = {
        band_label(i): dict(sorted(topj_death_crosstab[i].items()))
        for i in range(10)
    }

    out = {
        "probe": "DCF- edge fate — which cap step kills an edge, by fame band",
        "served_artifact": {
            "file": SERVED.name, "sha256": manifest["sha256"],
            "artists": manifest["artists"], "edges": manifest["edges"],
        },
        "archive": {"dir": str(SUBTREE), "payloads": len(payloads)},
        "population": {"known_after_drops": len(known), "excluded": len(excluded)},
        "stage_pair_counts": {
            "archive": len(archive_pairs), "after_topj": len(topj_pairs),
            "after_degree_trim": len(trim_pairs), "final_after_component": len(final_pairs),
        },
        "max_degree_after_topj_before_any_trim": max_pre_trim,
        "gate": gate,
        "counting": "ENDPOINT SLOTS — an edge is counted once for each of its "
                    "two ends, in that end's band. Band totals are therefore "
                    "double the pair counts above.",
        "by_fame_band": table,
        "topj_deaths_by_band_of_the_other_end": crosstab,
        "elapsed_seconds": round(time.monotonic() - started, 1),
    }
    (HERE / "dcf_edge_fate.json").write_text(
        json.dumps(out, indent=2, sort_keys=True), encoding="utf-8"
    )

    print(f"\ngate exact={gate['exact']} agreement={gate['agreement']} "
          f"red={gate['red_stages_are_distinct']}")
    print(f"{'band':>9} {'artists':>8} {'archive':>10} {'top-j died':>11} "
          f"{'trim died':>10} {'survived':>10} {'%topj':>7} {'%trim':>7}")
    for r in table:
        print(f"{r['band']:>9} {r['artists']:>8,} {r['archive_edges']:>10,} "
              f"{r['died_at_the_topj_cut']:>11,} {r['died_at_the_degree_trim']:>10,} "
              f"{r['survived']:>10,} {100 * r['share_died_at_the_topj_cut']:>6.2f}% "
              f"{100 * r['share_died_at_the_degree_trim']:>6.2f}%")
    return 0 if gate["exact"] and gate["red_stages_are_distinct"] else 1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    raise SystemExit(main())
