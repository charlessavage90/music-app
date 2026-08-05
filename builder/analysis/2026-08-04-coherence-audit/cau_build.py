"""CAU- build: extract the G arm's deep journeys, insert the red control, seal it.

Reads the committed GBL- page data and the unblinded mapping, keeps ONLY the G
side at depths 10 and 20, inserts CAU-AM2-compliant random artists, and splits
output two ways:

  cau_page_data.json  -- what the owner sees. Carries no injection identity.
  .superpowers/cau/cau_sealed.json  -- which slots are injected, and how hard.

CAU-CORR1: injected artists are INSERTED between two existing cards, never
substituted for one. All 65 real interior slots survive and are judged; the 12
controls are additional. 77 judgements total.

Five self-checks, each a SystemExit rather than a silent pass. Run once.
"""
from __future__ import annotations

import json
import random
import sys

from cau_common import (CELL, DEEP, MIN_INJECT_DISTANCE, N_INJECT, PRESENTED_REAL,
                        SCORED_REAL, gbl_file, in_dir, sealed_path, slot_id,
                        use_cre)

use_cre()
from cre_common import Ruler                      # noqa: E402
from cre_gates import load_cell                   # noqa: E402

SEED = 20260804          # committed; the draw is reproducible
N_JOURNEYS = 16          # spec §2

PAGE_SCHEMA = {
    "root": {"journeys"},
    "journey": {"id", "artists"},
    # CAU-AM4: mbid + disambiguation so the owner can identify the RIGHT artist.
    # Leaks nothing -- one arm, and controls carry the same fields.
    "artist": {"mbid", "name", "role", "disambiguation"},
}
ROLES = {"endpoint", "interior"}


def g_deep_journeys(page: dict, mapping: dict) -> list[dict]:
    """The G arm only, depths 10 and 20, in committed order."""
    out = []
    for p in page["pairs"]:
        m = mapping[p["key"]]
        side = {m["L"]: "L", m["R"]: "R"}["G"]
        for row in p["rows"]:
            if row["depth"] not in DEEP:
                continue
            out.append({
                "id": f"{p['key']}@d{row['depth']}",
                "artists": [dict(a) for a in row[side]["artists"]],
            })
    return out


def _band(ruler, mbid, width):
    """The obscurity band an artist sits in. None is its own band -- an artist the
    ruler cannot read must be matched by another the ruler cannot read, or the
    injection is detectable by the absence of a reading rather than by the music."""
    v = ruler.pctl_of(mbid)
    return None if v is None else (max(0.0, v - width), min(1.0, v + width))


def _in_band(ruler, mbid, band):
    v = ruler.pctl_of(mbid)
    if band is None:
        return v is None
    return v is not None and band[0] <= v <= band[1]


def _within(store, seeds: set[int], hops: int) -> set[int]:
    """Every node reachable from `seeds` in at most `hops` hops, inclusive."""
    seen, frontier = set(seeds), set(seeds)
    for _ in range(hops):
        nxt = set()
        for v in frontier:
            lo, hi = int(store.offsets[v]), int(store.offsets[v + 1])
            nxt.update(int(n) for n in store.neighbours[lo:hi])
        frontier = nxt - seen
        seen |= frontier
    return seen


def pick_injections(journeys, store, ruler, rng):
    """CAU-AM1: at most one injection per journey. CAU-CORR1: inserted, not
    substituted. CAU-AM2: the injected artist must sit at distance >=
    MIN_INJECT_DISTANCE from BOTH cards it will be placed between, so it cannot
    coincidentally belong there.

    `insert_at` is an index into the ORIGINAL journey: the injected artist ends up
    between artists[insert_at - 1] and artists[insert_at]. Band widenings are
    RECORDED per injection so a later reader can see how hard each control was.
    """
    idx = {m: i for i, m in enumerate(store.mbids)}
    eligible = [j for j in journeys if len(j["artists"]) >= 3]
    if len(eligible) < N_INJECT:
        raise SystemExit(
            f"only {len(eligible)} journeys have an interior; cannot place "
            f"{N_INJECT} injections one per journey")
    all_nodes = list(range(len(store.mbids)))
    out = {}
    for j in rng.sample(eligible, N_INJECT):
        arts = j["artists"]
        # CAU-AM3: endpoint-adjacent ONLY. at=1 puts the control between the first
        # endpoint and the first interior; at=len-1 puts it between the last
        # interior and the second endpoint. Either way one of its two neighbours
        # is an endpoint, which is never judged -- so exactly one real card is
        # touched, and that card is excluded from scoring.
        insert_at = rng.choice((1, len(arts) - 1))
        left, right = arts[insert_at - 1], arts[insert_at]
        seeds = {idx[a["mbid"]] for a in (left, right) if a["mbid"] in idx}
        if len(seeds) != 2:
            raise SystemExit(
                f"a flanking artist of the insertion point in {j['id']} does not "
                f"resolve in {CELL}; the distance condition cannot be checked and "
                f"must not be skipped")
        banned = _within(store, seeds, MIN_INJECT_DISTANCE - 1)
        banned |= {idx[a["mbid"]] for a in arts if a["mbid"] in idx}

        width, widenings = 0.05, 0
        band = _band(ruler, right["mbid"], width)
        while True:
            pool = [v for v in all_nodes
                    if v not in banned and _in_band(ruler, store.mbids[v], band)]
            if pool:
                break
            widenings += 1
            if band is None or widenings > 6:
                pool = [v for v in all_nodes if v not in banned]
                if not pool:
                    raise SystemExit(
                        f"no candidate in {CELL} satisfies the CAU-AM2 distance "
                        f"condition for {j['id']}")
                break
            width *= 2
            band = _band(ruler, right["mbid"], width)

        pick = rng.choice(pool)
        out[j["id"]] = {
            "journey": j["id"],
            "insert_at": insert_at,
            "between": [left["name"], right["name"]],
            "injected_mbid": store.mbids[pick],
            "injected_name": store.names[pick],
            "band_widenings": widenings,
            "min_distance_from_neighbours": MIN_INJECT_DISTANCE,
        }
    return out


def apply_injections(journeys, injections):
    """Insert, then record the FINAL slot id of each control -- positions after
    the insertion point shift by one, and the scorer keys on final positions."""
    for j in journeys:
        inj = injections.get(j["id"])
        if not inj:
            continue
        at = inj["insert_at"]
        j["artists"].insert(at, {"mbid": inj["injected_mbid"],
                                 "name": inj["injected_name"]})
        inj["slot"] = slot_id(j["id"], at)
        # CAU-AM3: the ONE real card this control touches. The other neighbour is
        # an endpoint. Judged by the owner, discarded by the scorer.
        n = len(j["artists"])
        contaminated = [k for k in (at - 1, at + 1)
                        if 0 < k < n - 1]        # exclude both endpoints
        if len(contaminated) != 1:
            raise SystemExit(
                f"CAU-AM3 violated in {j['id']}: control at {at} touches "
                f"{len(contaminated)} real cards, expected exactly 1")
        inj["excluded_slot"] = slot_id(j["id"], contaminated[0])
    return journeys


def to_page(journeys, rng, disamb):
    """Shuffled order, no pair or depth label (CAU-AM1), roles marked,
    disambiguation attached (CAU-AM4)."""
    out = []
    for j in journeys:
        n = len(j["artists"])
        out.append({
            "id": j["id"],
            "artists": [{"mbid": a["mbid"], "name": a["name"],
                         "disambiguation": disamb.get(a["mbid"], ""),
                         "role": "endpoint" if i in (0, n - 1) else "interior"}
                        for i, a in enumerate(j["artists"])],
        })
    rng.shuffle(out)
    return {"journeys": out}


def assert_page_clean(page: dict, injections: dict) -> None:
    """The page must carry no injection identity and no undesigned field. Artist
    NAMES are deliberately not scanned -- the graph supplies them and the owner is
    meant to read them (the GBL- 'The Cramps' precedent)."""
    def keys(node, kind):
        extra = set(node) - PAGE_SCHEMA[kind]
        if extra:
            raise SystemExit(
                f"page data has unexpected {kind} key(s) {sorted(extra)}: an "
                f"undesigned field is a leak whatever it holds")
    keys(page, "root")
    for j in page["journeys"]:
        keys(j, "journey")
        for a in j["artists"]:
            keys(a, "artist")
            if a["role"] not in ROLES:
                raise SystemExit(f"unknown role {a['role']!r}")
    blob = json.dumps(page)
    for token in ("inject", "band_widen", "sealed", "control", "insert_at"):
        if token in blob:
            raise SystemExit(f"page data contains {token!r}: injection identity leak")
    for v in injections.values():
        if v["slot"] in blob:
            raise SystemExit(f"page data names sealed slot {v['slot']}: leak")


def main() -> int:
    page_src = json.loads(gbl_file("gbl_page_data.json").read_text("utf-8"))
    result = json.loads(gbl_file("gbl_result.json").read_text("utf-8"))
    _, store = load_cell(CELL)                     # sha-asserted against its manifest
    ruler = Ruler()

    journeys = g_deep_journeys(page_src, result["mapping_unsealed"])

    # 1. The material is what the spec says it is.
    if len(journeys) != N_JOURNEYS:
        raise SystemExit(f"expected {N_JOURNEYS} deep G journeys, got {len(journeys)}")
    real_slots = sum(len(j["artists"]) - 2 for j in journeys)
    if real_slots != PRESENTED_REAL:
        raise SystemExit(
            f"expected {PRESENTED_REAL} real interior slots presented, "
            f"got {real_slots}")

    # 2. Every artist shown must exist in the artifact being audited.
    known = set(store.mbids)
    missing = [a["name"] for j in journeys for a in j["artists"]
               if a["mbid"] not in known]
    if missing:
        raise SystemExit(f"{len(missing)} artist(s) absent from {CELL}: {missing[:5]}")

    rng = random.Random(SEED)
    injections = pick_injections(journeys, store, ruler, rng)

    # 3. One injection per journey, exactly N_INJECT of them.
    if len(injections) != N_INJECT:
        raise SystemExit(f"expected {N_INJECT} injections, got {len(injections)}")

    journeys = apply_injections(journeys, injections)

    # 4. CAU-CORR1: inserting must not have cost a single real slot.
    after = sum(len(j["artists"]) - 2 for j in journeys)
    if after != PRESENTED_REAL + N_INJECT:
        raise SystemExit(
            f"CAU-CORR1 violated: expected {PRESENTED_REAL} real + {N_INJECT} "
            f"control = {PRESENTED_REAL + N_INJECT} interior slots, got {after}. "
            f"Injections must be INSERTED, never substituted for a real artist")
    if len({v["slot"] for v in injections.values()}) != N_INJECT:
        raise SystemExit("two injections collided on one slot id")

    # 4b. CAU-AM3: D_all must come out at exactly the declared 53.
    excluded = {v["excluded_slot"] for v in injections.values()}
    if len(excluded) != N_INJECT:
        raise SystemExit(
            f"two controls share a contaminated slot ({len(excluded)} distinct for "
            f"{N_INJECT} controls); D_all would not be {SCORED_REAL}")
    if PRESENTED_REAL - len(excluded) != SCORED_REAL:
        raise SystemExit(
            f"CAU-AM3 violated: {PRESENTED_REAL} presented - {len(excluded)} "
            f"excluded != {SCORED_REAL} scored")

    disamb = {m: (store.disambiguations[i] or "")
              for i, m in enumerate(store.mbids)}
    page = to_page(journeys, rng, disamb)
    assert_page_clean(page, injections)             # 5. no identity leak

    shown = [a for j in page["journeys"] for a in j["artists"]]
    with_d = sum(1 for a in shown if a["disambiguation"])

    in_dir("cau_page_data.json").write_text(
        json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8")
    sealed_path("cau_sealed.json").write_text(
        json.dumps({"seed": SEED, "cell": CELL, "injections": injections},
                   indent=2, ensure_ascii=False), encoding="utf-8")
    widened = sum(1 for v in injections.values() if v["band_widenings"])
    print(f"{len(page['journeys'])} journeys; {after} judgements "
          f"({PRESENTED_REAL} real presented, {N_INJECT} control); D_all = "
          f"{SCORED_REAL} scored after excluding {len(excluded)} control-adjacent; "
          f"{widened} control(s) needed a band widening; {with_d}/{len(shown)} "
          f"cards carry a disambiguation; sealed map written; page clean",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
