"""`LUX-E4` — for how many cards can the app offer another track?

Governing documents:
  spec  docs/superpowers/specs/2026-09-03-launch-ux-scope.md  (§5, §6)
  plan  docs/superpowers/plans/2026-09-04-launch-ux-1-3.md    (task LUX-T7)

The pre-registered read, fixed in the spec before any result existed and
quoted rather than reworded:

    for how many of the cards a user sees does a "try another track" button
    appear at all -- and does it disappear exactly for the obscure artists?

The threshold, also from the spec (§5): if fewer than HALF of lower-half cards
carry >= 2 candidates, LUX-3 serves famous artists and not the ones the app is
for. That is a RE-PRIORITISATION TRIGGER AND THE OWNER'S CALL. This script
reports the fraction; it decides nothing.

WHAT IS MEASURED
  The 120 committed `TAS-` pairs (40 ff / 40 fo / 40 oo) are routed with
  PRODUCTION weights against the adopted artifact, and the INTERIOR cards are
  resolved through the real `ClipResolver` against the live catalogues.

  Interiors only. Endpoints are excluded because they are the user's own
  picks, not what the app delivered -- the rule and its reasoning are
  ../2026-08-02-dsp-ids/delivered_coverage.py, whose shape this follows.

  Two denominators, as in that predecessor, because they answer different
  questions:
    UNIQUE  -- of the distinct artists shown, how many can offer another track
    CARDS   -- of the card impressions, how many can (a famous artist shown on
               many journeys counts every time)
  The threshold is read on CARDS: "the cards a user sees" is an impression
  count, not a distinct-artist count. Both are written out.

ONE LIVE RESOLUTION PER DISTINCT ARTIST, NOT PER CARD
  The resolver's candidate list is a property of the artist, and the cache
  makes the second resolution of the same mbid return the same count from the
  first one's identities. Resolving each distinct artist once and attributing
  its count to each of its card impressions is therefore identical in outcome
  to resolving per card, and costs a few hundred fewer live calls. Paced,
  serial, and with the resolver's own circuit breaker in place: a block earned
  here is not this experiment's to spend (G3-A4).

ROUTE, AND WHY IT IS SPLIT OUT
  `Resolution.clip.source` says "deezer" or "itunes" and cannot distinguish
  the Deezer ID path from the Deezer name path -- but those two have
  genuinely different relevance behaviour (the id path cannot return a
  different artist of the same name; the name path can only match on an exact
  folded name, so it fails often in the obscure tail). The route is therefore
  read off the LAST outbound URL of each resolve: `_search` returns as soon as
  a source yields rows, so the last call made is the one that answered.

WHAT THE COUNT MEANS SINCE LUX-3
  Candidates are de-duplicated by NORMALISED TITLE (`clips._dedupe_by_title`),
  so a count of 3 means three genuinely distinct titles. It does NOT collapse
  "Song" and "Song (Remastered 2011)"; that is a known bound on this
  measurement and is stated in the README, not fixed here.

Run from `api/` (it loads the adopted artifact through the API's own loader
and uses the API's venv for httpx):

  UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
      ../builder/analysis/2026-09-04-lux-e4-candidate-counts/candidate_counts.py

  --resume   reuse rows already in candidate_counts.json (for restarting after
             a rate-limit stop). Absent, the run starts clean.

This directory OWNS its figures. Cite it; never restate them.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import httpx
import numpy as np

ROOT = Path("C:/dev/music-app")
sys.path.insert(0, str(ROOT / "api" / "src"))

from artistpath_api.artifact_source import load_graph  # noqa: E402
from artistpath_api.clips import (  # noqa: E402
    CatalogueUnavailable,
    ClipResolver,
    InMemoryClipCache,
)
from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.pathfinding import find_journey  # noqa: E402

HERE = Path(__file__).parent
PAIRS = ROOT / "builder/analysis/2026-07-30-tag-discrimination/tas_pairs.json"

# The adopted artifact. Named explicitly rather than imported from ct_common,
# whose ADOPTED still points at graph-t15-tiebreakfix.bin (the pre-MSW map):
# roughly fifteen artifacts sit in builder/scratch/ and they are NOT
# interchangeable. The sha is read from the artifact's own manifest sidecar
# and never transcribed by hand (DEP-24), then enforced by `load_graph`.
ARTIFACT = ROOT / "builder/scratch/graph-msw-tu50.bin"
MANIFEST = ROOT / "builder/scratch/graph-msw-tu50.bin.json"

OUT = HERE / "candidate_counts.json"

# Band boundaries over the fame frame. These are the FIXED bands defined in
# ../2026-07-30-track-b-cap-selection/cb_metrics.py (BANDS); reproduced here
# because that module imports `artistpath_builder` and cannot load in the
# API's venv. A definition, not a figure.
BANDS = (
    ("top 0.1%", 0.999, 1.0001),
    ("top 1%", 0.99, 0.999),
    ("top 10%", 0.90, 0.99),
    ("upper half", 0.50, 0.90),
    ("lower half", 0.0, 0.50),
)
BAND_ORDER = [name for name, _lo, _hi in BANDS]

# Minimum gap between outbound calls to any catalogue. Serial and paced: this
# run makes several hundred live requests to two rate-limited services.
PACE_S = 0.34
# A refusal (429 / 5xx) is retried ONCE after a long backoff, because a single
# blip should not void a twenty-minute run. Past this many, the run aborts and
# reports rather than recording false zeroes -- a measurement quietly taken on
# different terms than the registered ones is worse than no measurement.
MAX_REFUSALS = 3
REFUSAL_BACKOFF_S = 30.0

T0 = time.time()


def log(msg: str) -> None:
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def fame_frame(pop_raw: np.ndarray) -> np.ndarray:
    """Percentile RANK over the adopted artifact -- the fixed frame.

    Currency note: this is a PERCENTILE. `pop_raw` is a VALUE, and the two
    diverge sharply at the top of the distribution (log §2.12).
    """
    pop = np.asarray(pop_raw, dtype=np.float64)
    order = pop.argsort(kind="stable")
    pctl = np.empty_like(pop)
    pctl[order] = np.arange(len(pop)) / (len(pop) - 1)
    return pctl


def band_of(p: float) -> str:
    for name, lo, hi in BANDS:
        if lo <= p < hi:
            return name
    return "lower half"


class PacedFetcher:
    """The production fetcher, paced, with the last URL recorded.

    Status classification is copied deliberately from `app.build_default_app`:
    the resolver must see a 429/5xx as CatalogueUnavailable, or its breaker
    never arms and a refusal reads as "no such track" (G3-A4).
    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client
        self._last_call = 0.0
        self.urls: list[str] = []
        self.refused = False

    def start_resolve(self) -> None:
        self.urls = []
        self.refused = False

    async def __call__(self, url: str, params: dict) -> dict:
        gap = PACE_S - (time.monotonic() - self._last_call)
        if gap > 0:
            await asyncio.sleep(gap)
        self._last_call = time.monotonic()
        self.urls.append(url)
        r = await self._client.get(url, params=params)
        if r.status_code == 429 or r.status_code >= 500:
            self.refused = True
            raise CatalogueUnavailable(f"{r.status_code} from {url}")
        r.raise_for_status()
        return r.json()


def route_of(urls: list[str], cfg: ApiConfig, count: int) -> str:
    """Which catalogue path answered, from the last call `_search` made."""
    if count == 0 or not urls:
        return "none"
    last = urls[-1]
    if last.startswith(cfg.deezer_artist_url):
        return "deezer-id"
    if last.startswith(cfg.deezer_search_url):
        return "deezer-name"
    if last.startswith(cfg.itunes_search_url):
        return "itunes"
    return "other"


def route_pairs(store, cfg, pctl) -> tuple[list[dict], int, int, dict]:
    """Route the 120 pairs and return the interior card impressions.

    Also returns the sample's own attrition, because it is load-bearing here:
    `tas_pairs.json` was drawn against the PRE-MSW artifact, so some of its
    endpoints are no longer in the adopted graph and those pairs cannot be
    routed at all. That loss is not uniform across the three classes, and a
    reader who does not see it would take the band table for a property of
    the router rather than partly a property of the surviving sample.
    """
    pairs = json.loads(PAIRS.read_text(encoding="utf-8"))["pairs"]
    cards: list[dict] = []
    routed = 0
    unroutable: Counter = Counter()
    no_path: Counter = Counter()
    endpoint_bands: Counter = Counter()
    for a, b, cls in pairs:
        si = store.id_by_mbid.get(a)
        ti = store.id_by_mbid.get(b)
        if si is None or ti is None:
            unroutable[cls] += 1
            continue
        result = find_journey(store, si, ti, [], cfg)
        if result is None:
            no_path[cls] += 1
            continue
        path, _stop = result
        routed += 1
        for node in (si, ti):
            endpoint_bands[band_of(float(pctl[node]))] += 1
        # Interiors only -- endpoints are the user's own picks.
        for node in path[1:-1]:
            cards.append({"node": int(node), "cls": cls})
    provenance = {
        "pairs_unroutable_endpoint_absent_by_class": dict(unroutable),
        "pairs_no_path_by_class": dict(no_path),
        "endpoint_bands_of_routed_pairs": dict(endpoint_bands),
    }
    return cards, routed, len(pairs), provenance


async def resolve_all(store, cfg, pctl, todo: list[int],
                      rows: dict[str, dict]) -> bool:
    """Resolve each distinct artist once. Returns False if the run aborted."""
    async with httpx.AsyncClient(timeout=cfg.clip_http_timeout) as client:
        fetch = PacedFetcher(client)
        resolver = ClipResolver(cfg, InMemoryClipCache(), fetch)
        refusals = 0
        for i, node in enumerate(todo, 1):
            mbid = store.mbids[node]
            name = store.names[node]
            deezer_id = store.deezer_id_of(node)

            for attempt in (1, 2):
                fetch.start_resolve()
                resolution = await resolver.resolve(mbid, name, deezer_id, 0)
                if not fetch.refused:
                    break
                refusals += 1
                log(f"catalogue refused on {name!r} "
                    f"(refusal {refusals}/{MAX_REFUSALS})")
                if refusals > MAX_REFUSALS or attempt == 2:
                    write_out(store, cfg, rows, aborted=True)
                    log("ABORTING: a catalogue is refusing us. Partial rows "
                        "written; the run is INCOMPLETE and must not be read "
                        "as the registered measurement.")
                    return False
                log(f"backing off {REFUSAL_BACKOFF_S:.0f}s")
                await asyncio.sleep(REFUSAL_BACKOFF_S)

            p = float(pctl[node])
            rows[mbid] = {
                "mbid": mbid,
                "name": name,
                "pop_pctl": round(p, 6),
                "band": band_of(p),
                "has_deezer_id": bool(deezer_id),
                "count": resolution.count,
                "route": route_of(fetch.urls, cfg, resolution.count),
                "calls": len(fetch.urls),
            }
            if i % 10 == 0 or i == len(todo):
                write_out(store, cfg, rows)
                log(f"{i}/{len(todo)} artists resolved")
    return True


def summarise(rows: list[dict], cards: list[dict],
              mbid_of_node: dict[int, str]) -> dict:
    """Every figure this directory owns. No verdict -- the threshold is read
    in the README and the trigger is the owner's."""
    by_mbid = {r["mbid"]: r for r in rows}

    def blank() -> dict:
        return {"n": 0, "with_any": 0, "with_2plus": 0, "count_sum": 0,
                "counts": Counter()}

    uniq_band: dict[str, dict] = defaultdict(blank)
    card_band: dict[str, dict] = defaultdict(blank)
    card_route: dict[str, dict] = defaultdict(blank)
    card_band_route: dict[str, dict] = defaultdict(blank)
    card_cls: dict[str, dict] = defaultdict(blank)

    def add(bucket: dict, r: dict) -> None:
        bucket["n"] += 1
        bucket["count_sum"] += r["count"]
        bucket["counts"][r["count"]] += 1
        if r["count"] >= 1:
            bucket["with_any"] += 1
        if r["count"] >= 2:
            bucket["with_2plus"] += 1

    for r in rows:
        add(uniq_band[r["band"]], r)

    resolved_cards = 0
    for card in cards:
        r = by_mbid.get(mbid_of_node[card["node"]])
        if r is None:
            continue
        resolved_cards += 1
        add(card_band[r["band"]], r)
        add(card_route[r["route"]], r)
        add(card_band_route[f'{r["band"]} / {r["route"]}'], r)
        add(card_cls[card["cls"]], r)

    def finish(bucket: dict) -> dict:
        n = bucket["n"]
        return {
            "n": n,
            "with_any_candidate": bucket["with_any"],
            "with_2plus_candidates": bucket["with_2plus"],
            "frac_2plus": round(bucket["with_2plus"] / n, 4) if n else None,
            "mean_count": round(bucket["count_sum"] / n, 2) if n else None,
            "count_histogram": dict(sorted(bucket["counts"].items())),
        }

    def finish_all(d: dict) -> dict:
        return {k: finish(v) for k, v in sorted(d.items())}

    all_cards = blank()
    for card in cards:
        r = by_mbid.get(mbid_of_node[card["node"]])
        if r is not None:
            add(all_cards, r)
    all_uniq = blank()
    for r in rows:
        add(all_uniq, r)

    return {
        "cards_total": len(cards),
        "cards_resolved": resolved_cards,
        "unique_artists_resolved": len(rows),
        "all_cards": finish(all_cards),
        "all_unique": finish(all_uniq),
        "cards_by_band": finish_all(card_band),
        "unique_by_band": finish_all(uniq_band),
        "cards_by_route": finish_all(card_route),
        "cards_by_band_and_route": finish_all(card_band_route),
        "cards_by_pair_class": finish_all(card_cls),
    }


_STATE: dict = {}


def write_out(store, cfg, rows: dict[str, dict], aborted: bool = False) -> None:
    cards = _STATE["cards"]
    mbid_of_node = _STATE["mbid_of_node"]
    row_list = list(rows.values())
    out = {
        "measures": (
            "for how many of the cards a user sees does a \"try another "
            "track\" button appear at all -- and does it disappear exactly "
            "for the obscure artists?"
        ),
        "artifact": str(ARTIFACT),
        "artifact_sha256": store.source_sha256,
        "pairs_file": str(PAIRS),
        "pairs_routed": _STATE["routed"],
        "pairs_total": _STATE["pairs_total"],
        "weights": {
            "w_sim": cfg.w_sim, "w_jump": cfg.w_jump, "w_floor": cfg.w_floor,
            "w_hop": cfg.w_hop, "w_avoid": cfg.w_avoid,
            "w_degree_hub": cfg.w_degree_hub,
            "clip_search_limit": cfg.clip_search_limit,
        },
        "note": (
            "Interiors only. Endpoints excluded -- they are the user's own "
            "picks. Candidates are de-duplicated by normalised title, so a "
            "count of 3 means three distinct titles; it does NOT collapse "
            "'Song' and 'Song (Remastered 2011)'. Counts are CENSORED at "
            "clip_search_limit: a row reading 25 means 'at least 25'."
        ),
        "count_ceiling": cfg.clip_search_limit,
        "provenance": _STATE["provenance"],
        "min_interior_pop_pctl": _STATE["min_interior_pop_pctl"],
        "complete": not aborted and len(row_list) == len(_STATE["todo_all"]),
        "aborted": aborted,
        "summary": summarise(row_list, cards, mbid_of_node),
        "rows": sorted(row_list, key=lambda r: r["pop_pctl"]),
    }
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False),
                   encoding="utf-8")


def print_table(summary: dict) -> None:
    def block(title: str, table: dict, order: list[str] | None = None) -> None:
        print(f"\n{title}")
        hdr = (f"{'bucket':<26}{'n':>7}{'>=1':>7}{'>=2':>7}"
               f"{'frac >=2':>10}{'mean':>8}")
        print(hdr)
        print("-" * len(hdr))
        keys = order if order else list(table)
        for k in keys:
            if k not in table:
                continue
            v = table[k]
            frac = v["frac_2plus"]
            print(f"{k:<26}{v['n']:>7}{v['with_any_candidate']:>7}"
                  f"{v['with_2plus_candidates']:>7}"
                  f"{(frac * 100 if frac is not None else 0):>9.1f}%"
                  f"{(v['mean_count'] or 0):>8.2f}")

    block("CARDS (impressions) by popularity band",
          summary["cards_by_band"], BAND_ORDER)
    block("UNIQUE artists by popularity band",
          summary["unique_by_band"], BAND_ORDER)
    block("CARDS by resolution route", summary["cards_by_route"],
          ["deezer-id", "deezer-name", "itunes", "none"])
    block("CARDS by band and route", summary["cards_by_band_and_route"])
    block("CARDS by pair class", summary["cards_by_pair_class"],
          ["ff", "fo", "oo"])
    v = summary["all_cards"]
    print(f"\nALL CARDS  n={v['n']}  >=1: {v['with_any_candidate']}  "
          f">=2: {v['with_2plus_candidates']}  "
          f"frac >=2: {v['frac_2plus']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true",
                    help="reuse rows already in candidate_counts.json")
    args = ap.parse_args()

    sha = json.loads(MANIFEST.read_text(encoding="utf-8"))["sha256"]
    log(f"artifact {ARTIFACT.name}, sha from manifest {sha[:16]}...")
    # Refuses on a mismatch. Several graphs sit in builder/scratch/ and a
    # conclusion drawn from the wrong one looks exactly like a correct one.
    store = load_graph(str(ARTIFACT), sha)
    log(f"loaded {len(store.mbids)} artists")

    cfg = ApiConfig()
    pctl = fame_frame(store.pop_raw)

    cards, routed, total, provenance = route_pairs(store, cfg, pctl)
    log(f"routed {routed}/{total} pairs -> {len(cards)} interior cards")
    log(f"unroutable (endpoint absent from the adopted artifact): "
        f"{provenance['pairs_unroutable_endpoint_absent_by_class']}")

    mbid_of_node = {c["node"]: store.mbids[c["node"]] for c in cards}
    distinct = sorted({c["node"] for c in cards})
    log(f"{len(distinct)} distinct interior artists to resolve")

    rows: dict[str, dict] = {}
    if args.resume and OUT.exists():
        prior = json.loads(OUT.read_text(encoding="utf-8"))
        rows = {r["mbid"]: r for r in prior.get("rows", [])}
        log(f"resuming: {len(rows)} rows already on disk")

    _STATE["cards"] = cards
    _STATE["mbid_of_node"] = mbid_of_node
    _STATE["routed"] = routed
    _STATE["pairs_total"] = total
    _STATE["todo_all"] = distinct
    _STATE["provenance"] = provenance
    _STATE["min_interior_pop_pctl"] = (
        round(min(float(pctl[n]) for n in distinct), 6) if distinct else None
    )

    todo = [n for n in distinct if store.mbids[n] not in rows]
    log(f"{len(todo)} live resolutions, serial, >= {PACE_S}s between calls")

    ok = asyncio.run(resolve_all(store, cfg, pctl, todo, rows))
    if not ok:
        raise SystemExit(2)

    write_out(store, cfg, rows)
    summary = json.loads(OUT.read_text(encoding="utf-8"))["summary"]
    print_table(summary)
    log(f"wrote {OUT.name}")


if __name__ == "__main__":
    main()
