"""Issue #200 step 1: served interior artists during `LBA-G5`, their `fame_lb_pctl` beside
an external audience count, split by how many "Dig deeper" presses preceded the request.

Decides nothing (`LBA-AM4` bar 1: no figure here is a measurement of path quality). It
scopes step 2 by asking whether the CONSTRUCT disagrees with the owner's ear (the proxy
calls an artist obscure that has a large audience elsewhere) or the ROUTING does (the
proxy agrees the artist is widely heard, and the router served them anyway).

Currencies, three and never interchangeable:
  - `fame_lb_pctl` — ListenBrainz listener-count RANK within this map's measured
    population, 0-1 (the adopted novelty-likelihood proxy, `PRODUCT-REQUIREMENTS`).
  - `fame_lb` — the raw ListenBrainz listener count behind that rank.
  - `deezer_fans` — Deezer `nb_fan`, fetched by the Deezer id the map already carries
    (no name matching). NOT Spotify monthly listeners, which is what the owner read and
    which no public API exposes; it stands in for "audience elsewhere" only.
    `deezer_fan_pctl` ranks it within a seeded random sample of the map, so the two
    percentiles can be read against each other.

Inputs: the gate's API stdout (`C:/unsung-fast/lbd-artifacts/lba-g5-logs/api-part*.log`),
every `Miles Davis -> Daft Punk` event dropped (issue #215, the pair log's own exclusion);
the adopted map `graph-lba-a6.bin`, sha-checked against its sidecar (it is the file the
gate served, sha 28311d81...).

Run from `api/` so the SHIPPED GraphStore parses the artifact:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-25-issue-200-served-fame-vs-listeners/served_fame_vs_listeners.py

Deezer responses are cached in `deezer_cache.json` beside this file, so a rerun is offline.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

from artistpath_api.graph_store import GraphStore

HERE = Path(__file__).parent
ARTIFACT = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
GATE_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
LOGS = Path("C:/unsung-fast/lbd-artifacts/lba-g5-logs")
EXCLUDED_PAIR = ("Miles Davis", "Daft Punk")  # issue #215
CACHE = HERE / "deezer_cache.json"
MAP_SAMPLE = 400
SEED = 200
# Depth bands in "Dig deeper" presses before the request. Every press in the gate was
# `known`, so this equals bypass_depth; the script asserts it rather than assuming it.
BANDS = [(0, 0), (1, 4), (5, 9), (10, 99)]


def verify(path: Path) -> None:
    want = json.loads(path.with_name(path.name + ".json").read_text(encoding="utf-8"))["sha256"]
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != want or got != GATE_SHA:
        sys.exit(f"REFUSING: {path.name} sha256 {got}; sidecar {want}; gate served {GATE_SHA}")
    print(f"sha256 OK  {path.name}  {got}")


def gate_events():
    for f in sorted(LOGS.glob("api-part*.log")):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if not line.startswith("{"):
                continue
            try:
                e = json.loads(line)
            except ValueError:
                continue
            if e.get("event") != "path":
                continue
            if (e["source"]["name"], e["target"]["name"]) == EXCLUDED_PAIR:
                continue
            assert e["known_count"] == e["bypass_depth"], "a non-known press: bands need a rethink"
            yield e


def deezer_fans(ids: list[str]) -> dict[str, int | None]:
    cache: dict[str, int | None] = (
        json.loads(CACHE.read_text(encoding="utf-8")) if CACHE.exists() else {}
    )
    todo = [i for i in ids if i and i not in cache]
    for n, did in enumerate(todo, 1):
        req = urllib.request.Request(
            f"https://api.deezer.com/artist/{did}", headers={"User-Agent": "artistpath-analysis/1"}
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                body = json.loads(r.read())
            cache[did] = body.get("nb_fan") if "error" not in body else None
        except Exception as exc:  # noqa: BLE001 - a failed fetch is recorded as absent
            print(f"  deezer {did}: {exc}", file=sys.stderr)
            cache[did] = None
        time.sleep(0.12)  # Deezer allows 50 requests per 5 s
        if n % 50 == 0:
            print(f"  fetched {n}/{len(todo)}")
            CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True), encoding="utf-8")
    CACHE.write_text(json.dumps(cache, indent=0, sort_keys=True), encoding="utf-8")
    return cache


def pctl_within(frame: np.ndarray, v: float) -> float:
    """Share of the map sample with strictly fewer fans, ties counted half."""
    return float((np.sum(frame < v) + 0.5 * np.sum(frame == v)) / len(frame))


def spearman(a, b) -> float:
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> None:
    verify(ARTIFACT)
    store = GraphStore.from_bytes(ARTIFACT.read_bytes())
    idx = {m: i for i, m in enumerate(store.mbids)}

    events = list(gate_events())
    served = []  # (depth, node) per interior per request
    for e in events:
        for stop in e["path"][1:-1]:
            served.append((e["bypass_depth"], idx[stop["mbid"]]))
    uniq = sorted({n for _, n in served})
    print(f"requests {len(events)}  interior cards served {len(served)}  unique artists {len(uniq)}")

    rng = random.Random(SEED)
    with_id = [i for i in range(len(store.mbids)) if store.deezer_id_of(i)]
    sample = rng.sample(with_id, MAP_SAMPLE)
    fans = deezer_fans([store.deezer_id_of(n) for n in uniq + sample])

    def fan(n):
        return fans.get(store.deezer_id_of(n)) if store.deezer_id_of(n) else None

    frame = np.array([fan(n) for n in sample if fan(n) is not None], dtype=float)
    print(f"map sample: {len(frame)}/{MAP_SAMPLE} with a Deezer fan count; "
          f"median {np.median(frame):.0f}")
    pct = store.fame_lb_pctl

    rows = {}
    for n in uniq:
        f = fan(n)
        rows[n] = {
            "name": store.names[n],
            "fame_lb_pctl": round(float(pct[n]), 3),
            "deezer_fans": f,
            "deezer_fan_pctl": None if f is None else round(pctl_within(frame, f), 3),
            "depths": sorted({d for d, m in served if m == n}),
        }

    print("\n## By depth band (per interior card served, repeats counted)")
    print("| Dig-deeper presses | cards | unique | median fame_lb_pctl | median Deezer fans "
          "| median deezer_fan_pctl | cards >= 0.5 on both | < 0.5 fame, >= 0.5 Deezer "
          "| >= 0.5 fame, < 0.5 Deezer | < 0.5 on both | no Deezer count |")
    print("|" + "---|" * 11)
    for lo, hi in BANDS:
        cards = [n for d, n in served if lo <= d <= hi]
        if not cards:
            continue
        fp = [rows[n]["fame_lb_pctl"] for n in cards]
        known = [n for n in cards if rows[n]["deezer_fans"] is not None]
        df = [rows[n]["deezer_fans"] for n in known]
        dp = [rows[n]["deezer_fan_pctl"] for n in known]
        q = {"hh": 0, "lh": 0, "hl": 0, "ll": 0}
        for n in known:
            a = "h" if rows[n]["fame_lb_pctl"] >= 0.5 else "l"
            b = "h" if rows[n]["deezer_fan_pctl"] >= 0.5 else "l"
            q[a + b] += 1
        label = f"{lo}" if lo == hi else f"{lo}-{hi if hi < 99 else '21'}"
        print(f"| {label} | {len(cards)} | {len(set(cards))} | {np.median(fp):.3f} | "
              f"{np.median(df):,.0f} | {np.median(dp):.3f} | {q['hh']} | {q['lh']} | {q['hl']} "
              f"| {q['ll']} | {len(cards) - len(known)} |")

    both = [n for n in uniq if rows[n]["deezer_fans"] is not None]
    rho = spearman([rows[n]["fame_lb_pctl"] for n in both], [rows[n]["deezer_fans"] for n in both])
    both_s = [n for n in sample if fan(n) is not None]
    rho_s = spearman([float(pct[n]) for n in both_s], [fan(n) for n in both_s])
    print(f"\nrank agreement fame_lb_pctl vs Deezer fans: served uniques rho={rho:.2f} (n={len(both)}); "
          f"map sample rho={rho_s:.2f} (n={len(both_s)})")

    # Context, not routing: how famous the endpoints were, and whether less-listened artists
    # sit one hop from what was served. Descriptive of the map; no alternative weights run.
    ends = sorted({idx[e["source"]["mbid"]] for e in events} | {idx[e["target"]["mbid"]] for e in events})
    print("\n## Endpoints the owner picked")
    print("| endpoint | fame_lb_pctl |")
    print("|---|---|")
    for n in sorted(ends, key=lambda n: -pct[n]):
        print(f"| {store.names[n]} | {pct[n]:.3f} |")

    print("\n## One hop from the served artists (per unique served interior, graph neighbours)")
    print("| Dig-deeper presses | unique served | median neighbour count | median share of neighbours "
          "< 0.9 fame_lb_pctl | median share < 0.5 | cards served < 0.9 |")
    print("|---|---|---|---|---|---|")
    for lo, hi in BANDS:
        cards = [n for d, n in served if lo <= d <= hi]
        if not cards:
            continue
        deg, s9, s5 = [], [], []
        for n in set(cards):
            nb = store.neighbours[store.offsets[n]:store.offsets[n + 1]]
            deg.append(len(nb))
            s9.append(float(np.mean(pct[nb] < 0.9)))
            s5.append(float(np.mean(pct[nb] < 0.5)))
        below = sum(1 for n in cards if pct[n] < 0.9)
        label = f"{lo}" if lo == hi else f"{lo}-{hi if hi < 99 else '21'}"
        print(f"| {label} | {len(set(cards))} | {np.median(deg):.0f} | {np.median(s9):.3f} | "
              f"{np.median(s5):.3f} | {below} of {len(cards)} |")

    print("\n## Two hops from the served artists (every unique served interior, pooled)")
    print("| hops | artists reachable | share < 0.9 fame_lb_pctl | share < 0.5 |")
    print("|---|---|---|---|")
    ring = set(uniq)
    seen = set(uniq)
    for hop in (1, 2):
        nxt = set()
        for n in ring:
            nxt.update(int(x) for x in store.neighbours[store.offsets[n]:store.offsets[n + 1]])
        nxt -= seen
        seen |= nxt
        ring = nxt
        arr = np.array(sorted(ring))
        print(f"| exactly {hop} | {len(arr)} | {np.mean(pct[arr] < 0.9):.3f} | {np.mean(pct[arr] < 0.5):.3f} |")

    print("\n## Every unique served interior artist, deepest band first")
    print("| artist | fame_lb_pctl | Deezer fans | deezer_fan_pctl | served at presses |")
    print("|---|---|---|---|---|")
    for n in sorted(uniq, key=lambda n: (-max(rows[n]["depths"]), rows[n]["fame_lb_pctl"])):
        r = rows[n]
        f = "—" if r["deezer_fans"] is None else f"{r['deezer_fans']:,}"
        p = "—" if r["deezer_fan_pctl"] is None else f"{r['deezer_fan_pctl']:.3f}"
        d = ",".join(map(str, r["depths"]))
        print(f"| {r['name']} | {r['fame_lb_pctl']:.3f} | {f} | {p} | {d} |")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
