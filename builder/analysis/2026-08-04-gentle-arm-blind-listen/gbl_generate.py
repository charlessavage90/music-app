"""GBL- journey generation: both arms, gated, sealed/page outputs split.

Spec §2: V0 = adopted production graph + production defaults; G = B-S1 + the
gentle ramp (RAMPS["P1a"], cited). Both arms walk the CRE ladder (the measured
object). Arm identity is written ONLY to the sealed file.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys

from gbl_common import ARMS, DEPTHS, ROOT, TOKENS, in_dir, sealed_path, use_cre

use_cre()
from cre_common import RAMPS, Ruler, load_adopted            # noqa: E402,F401
from cre_gates import load_cell                              # noqa: E402
from cre_ladder import assert_cost_decomposition, victim_key, walk_journey  # noqa: E402
from cre_mirror import MirrorContext                         # noqa: E402
from cre_sweep import config_for, ladder_excludes            # noqa: E402

sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.config import ApiConfig                  # noqa: E402
from artistpath_api.evaluation import path_metrics as _path_metrics  # noqa: E402
from artistpath_api.evaluation import top_degree_node_set    # noqa: E402
from artistpath_api.pathfinding import find_journey          # noqa: E402

G2B_DEPTHS = (1, 10)   # the CRE-G2(b) depths, reused
HUB_FRACTION = 0.01    # top-1% by DEGREE (never fame, never popularity)

# Substrings that would identify an arm. Scanned over the structure this module
# writes -- NEVER over artist names, which the graph supplies and the owner is
# meant to read. "The Cramps" contains "ramp"; "Armstrong" contains "arm".
FORBIDDEN_PAGE_TOKENS = ("V0", '"G"', "B-S1", "ramp", "tiebreakfix",
                         "candidate", "arm", "P1a")

# The page document's complete shape. An unexpected key is a leak on its own,
# whatever its value: it means something wrote a field nobody designed.
PAGE_SCHEMA = {
    "root": {"pairs"},
    "pair": {"key", "a", "b", "rows"},
    "row": {"depth", "L", "R"},
    "side": {"artists"},
    "artist": {"mbid", "name"},
}


def shuffle_tokens(pair_keys: list[str], rng) -> dict[str, dict[str, str]]:
    out = {}
    for k in pair_keys:
        arms = list(ARMS)
        rng.shuffle(arms)
        out[k] = dict(zip(TOKENS, arms))
    return out


def page_row(store, path: list[int]) -> dict:
    return {"artists": [{"mbid": store.mbids[v], "name": store.names[v]}
                        for v in path]}


def frozen_hub_ids(store, hub_mbids: set[str]) -> set[int]:
    """Map a FROZEN hub set into one artifact's node ids.

    `path_metrics` requires a frozen set rather than a per-graph threshold: the
    top-1%-by-degree cutoff moves between builds, so re-deriving it per arm would
    let an arm score better purely by compressing its degree distribution. Node
    ids are not shared between two different artifacts either, so the set travels
    as MBIDs and is mapped here. An MBID absent from this artifact drops out.
    """
    return {i for i, m in enumerate(store.mbids) if m in hub_mbids}


def hidden_metrics(store, ruler, top_set, path) -> dict:
    interior = path[1:-1]
    fame = [ruler.pctl_of(store.mbids[v]) for v in interior]
    pm = _path_metrics(store, path, top_set)
    return {
        "fame_pctl_interior": fame,
        "payload": sum(1 for v in interior if v not in top_set),
        "top1pct_degree_frac": pm.top1pct_degree_frac,
        "length": pm.length,
    }


def _check_keys(node, kind: str) -> None:
    extra = set(node) - PAGE_SCHEMA[kind]
    if extra:
        raise SystemExit(
            f"page data has unexpected {kind} key(s) {sorted(extra)}: only "
            f"{sorted(PAGE_SCHEMA[kind])} are designed, and an undesigned field "
            f"is a leak whatever it holds")


def assert_page_data_clean(doc: dict) -> None:
    """Two independent guards, because either alone has a hole.

    (1) The document's shape is exactly the designed one -- an unexpected key
        fails even if its value looks innocent.
    (2) No forbidden substring appears anywhere WE write. Artist names are
        blanked before the scan: they come from the graph, they are the thing
        the owner is meant to see, and scanning them would abort generation on
        a band called The Cramps.
    """
    _check_keys(doc, "root")
    scrubbed = {"pairs": []}
    for pair in doc["pairs"]:
        _check_keys(pair, "pair")
        rows = []
        for row in pair["rows"]:
            _check_keys(row, "row")
            sides = {}
            for tok in TOKENS:
                _check_keys(row[tok], "side")
                for artist in row[tok]["artists"]:
                    _check_keys(artist, "artist")
                sides[tok] = {"artists": [{"mbid": a["mbid"], "name": ""}
                                          for a in row[tok]["artists"]]}
            rows.append({"depth": row["depth"], **sides})
        # Endpoint names are the owner's own approved artists: blanked too.
        scrubbed["pairs"].append({"key": pair["key"], "a": "", "b": "",
                                  "rows": rows})

    blob = json.dumps(scrubbed, ensure_ascii=False)
    for tok in FORBIDDEN_PAGE_TOKENS:
        if tok in blob:
            raise SystemExit(f"page data leaks arm identity: {tok!r} found")


def _arm_store(arm: str):
    if arm == "V0":
        store = load_adopted()
    else:
        manifest, store = load_cell("B-S1")
        payload = (ROOT / "builder/scratch/cre-cells/B-S1.bin").read_bytes()
        got = hashlib.sha256(payload).hexdigest()
        if got != manifest["sha256"]:
            raise SystemExit(f"WRONG ARTIFACT for G: {got} != manifest")
    return store


def main() -> int:
    approved = json.loads(in_dir("gbl_pairs_approved.json").read_text("utf-8"))
    pairs = [(p["a"], p["b"]) for p in approved["pairs"]]
    if len(pairs) != 8:
        raise SystemExit(f"spec §3 requires 8 pairs, got {len(pairs)}")

    ruler = Ruler()
    sealed = {"arms": {}, "mapping": None, "hub_set_frozen_on": "V0"}
    page = {"pairs": []}

    # Frozen once, on the adopted artifact, and carried into both arms by MBID.
    hub_mbids: set[str] = set()

    per_arm: dict[str, dict] = {}
    for arm in ARMS:
        store = _arm_store(arm)
        measured, device = ruler.arrays(store)
        ctx = MirrorContext.build(store, device)
        cfg = config_for("P0" if arm == "V0" else "P1a")
        if arm == "V0":
            hub_mbids = {store.mbids[i]
                         for i in top_degree_node_set(store, HUB_FRACTION)}
        top_set = frozen_hub_ids(store, hub_mbids)
        api_cfg = ApiConfig()
        key = victim_key(measured, store.pop_raw, store.mbids)
        rows: dict[str, dict] = {}
        for a, b in pairs:
            s, t = store.id_by_mbid[a["mbid"]], store.id_by_mbid[b["mbid"]]
            ladder = walk_journey(store, s, t, cfg, ctx, measured,
                                  store.pop_raw, store.mbids)
            excl = ladder_excludes(ladder, key)
            bad = [d for d in DEPTHS
                   if d >= len(excl) or ladder[d][0] is None]
            if bad:
                raise SystemExit(
                    f"pair {a['name']}|{b['name']} does not reach depths {bad} "
                    f"on one arm: swap the pair (spec §5 run state) before "
                    f"any listen. No read exists yet.")
            depth_rows = {}
            for d in DEPTHS:
                path, kind = ladder[d]
                if arm == "V0":
                    real = find_journey(store, s, t, excl[d], api_cfg)
                    if real is None or list(real[0]) != list(path) or real[1] != kind:
                        raise SystemExit(
                            f"V0 mirror check FAILED at depth {d} for "
                            f"{a['name']}|{b['name']}: mirror and production "
                            f"find_journey disagree")
                else:
                    if d in G2B_DEPTHS:
                        assert_cost_decomposition(
                            store, ctx, cfg, excl[d], path,
                            masked_edge=(s, t) if kind == "forced" else None)
                depth_rows[str(d)] = {
                    "path_mbids": [store.mbids[v] for v in path],
                    "page": page_row(store, path),
                    "metrics": hidden_metrics(store, ruler, top_set, path),
                    "kind": kind,
                }
            rows[f"{a['mbid']}|{b['mbid']}"] = depth_rows
        per_arm[arm] = rows
        sealed["arms"][arm] = {"pairs": rows}

    # Differential check (spec §6): the two arms must not be one artifact twice.
    diff = any(
        per_arm["V0"][k][str(d)]["path_mbids"] != per_arm["G"][k][str(d)]["path_mbids"]
        for k in per_arm["V0"] for d in DEPTHS)
    if not diff:
        raise SystemExit("differential check FAILED: arms identical everywhere")

    rng = random.SystemRandom()
    keys = list(per_arm["V0"].keys())
    mapping = shuffle_tokens(keys, rng)
    sealed["mapping"] = mapping

    for (a, b), k in zip(pairs, keys):
        rows = []
        for d in DEPTHS:
            rows.append({
                "depth": d,
                "L": per_arm[mapping[k]["L"]][k][str(d)]["page"],
                "R": per_arm[mapping[k]["R"]][k][str(d)]["page"],
            })
        page["pairs"].append({"key": k, "a": a["name"], "b": b["name"],
                              "rows": rows})

    assert_page_data_clean(page)
    sealed_path("gbl_sealed.json").write_text(
        json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    in_dir("gbl_page_data.json").write_text(
        json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"generated {len(keys)} pairs x {len(DEPTHS)} depths x 2 arms; "
          f"sealed mapping written; page data clean", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
