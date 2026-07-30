"""RC runner -- fetches the sampled candidates' own lists. COLLECT ONLY.

Governed by `docs/superpowers/specs/2026-07-29-reciprocity-sampling-preregistration.md`
and its amendment `RC-A1`, both committed before this ran. This script computes no
criterion and makes no comparison; `rc_score.py` does that from the raw records written
here, so scoring can be re-run or independently reviewed without re-hitting the service.

What it collects, and why that is the whole measurement. A built edge (u,v) needs each
endpoint in the other's top-50 (mutual k-NN). The seeds' own lists are already committed
in `../2026-07-29-cap-selection-sim/as_raw_records.json` for both arms, fetched
2026-07-29 -- so `top50(u)` is free. What is missing is the other direction: for a sample
of `u`'s candidates, does `u` appear in *their* top-50. That is what this fetches.

Arms (RC §0 factor table). One request parameter differs and nothing else:
  RC-ARM-P  contribution_5  -- production; AS calls it ALG-E. Archive-first: every
                              response for a crawled artist already exists on disk.
  RC-ARM-B  contribution_3  -- ALG-B. Live, always.

Nothing is written to any archive (AS precedent, deliberate): `build` stays offline and
the replay test still proves it. That also sidesteps `RC-H3` entirely -- the archive key
does not encode the algorithm, so writing ALG-B responses beside production ones would
poison the archive for every future build.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-29-reciprocity-sampling/rc_run.py
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlencode

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api" / "src"))
sys.path.insert(0, str(ROOT / "builder" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
ARCHIVE = ROOT / "builder" / "scratch" / "graph-archive"
AS_RECORDS = ROOT / "builder" / "analysis" / "2026-07-29-cap-selection-sim" / "as_raw_records.json"
OUT = HERE / "rc_raw_records.json"

ENDPOINT = "https://labs.api.listenbrainz.org/similar-artists/json"
RC_SEED = 20260729  # RC §2 -- fixed before the run; the draw is reproducible
M_SAMPLE = 10  # RC §3, unchanged by RC-A1
K = 50  # RC §0 held constant: BuilderConfig.max_neighbours_per_artist
PAUSE_SECONDS = 0.4  # matches the AS runner; gentler than the crawler's 5/s

# The two arms, by the AS label whose records we reuse for the seed side.
ARM_OF_AS_LABEL = {"ALG-E": "RC-ARM-P", "ALG-B": "RC-ARM-B"}
ALGORITHM = {
    "RC-ARM-P": (
        "session_based_days_7500_session_300_contribution_5"
        "_threshold_10_limit_100_filter_True_skip_30"
    ),
    "RC-ARM-B": (
        "session_based_days_7500_session_300_contribution_3"
        "_threshold_10_limit_100_filter_True_skip_30"
    ),
}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def top_k(candidates: list[dict], k: int = K) -> list[str]:
    """The k neighbours a build would rank first, by the production ordering.

    `mutual_knn_cap` ranks on UNCLIPPED strengths and breaks ties on lowest MBID
    (`graph.py`), and at similarity_damping 0.0 `damped_strength` is log1p(cooc) --
    strictly monotone in the raw response score, verified at pipeline.py:218-226. So
    ordering by raw score here is order-equivalent to the real build. RC §0.
    """
    ranked = sorted(candidates, key=lambda c: (-float(c["score"]), c["mbid"]))
    return [c["mbid"] for c in ranked[:k]]


def fetch(mbid: str, algorithm: str) -> tuple[int, bytes]:
    query = urlencode({"artist_mbids": mbid, "algorithm": algorithm})
    request = urllib.request.Request(
        f"{ENDPOINT}?{query}",
        headers={"User-Agent": "artistpath-analysis/1.0 (RC reciprocity sampling)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read()
    except Exception as exc:  # noqa: BLE001 -- recorded, never silently retried
        return -1, repr(exc).encode()
    finally:
        time.sleep(PAUSE_SECONDS)


def main() -> int:
    actual = sha256_of(GRAPH)
    if actual != EXPECT:
        print("ARTIFACT MISMATCH -- refusing to run", file=sys.stderr)
        return 2

    from artistpath_builder.config import BuilderConfig
    from artistpath_builder.sources.listenbrainz import (
        ListenBrainzSource,
        harvest_identities,
    )

    source = ListenBrainzSource(BuilderConfig())
    as_payload = json.loads(AS_RECORDS.read_text(encoding="utf-8"))
    if as_payload.get("artifact_sha256") != EXPECT:
        print("AS records were taken on a different artifact -- refusing", file=sys.stderr)
        return 2

    # --- seed side: free, already fetched today, both arms -------------------
    seeds: dict[str, dict] = {}
    for entry in as_payload["records"]:
        arm = ARM_OF_AS_LABEL.get(str(entry["arm"]))
        if arm is None or entry.get("status") != 200 or "candidates" not in entry:
            continue
        record = seeds.setdefault(
            str(entry["mbid"]),
            {
                "mbid": entry["mbid"],
                "name": entry["name"],
                "stratum": entry["stratum"],
                "own_pctl": entry["own_pctl"],
                "arms": {},
            },
        )
        candidates = entry["candidates"]
        record["arms"][arm] = {
            "n_candidates_returned": len(candidates),
            "top_k": top_k(candidates),
        }

    usable = {
        mbid: rec
        for mbid, rec in seeds.items()
        if set(rec["arms"]) == {"RC-ARM-P", "RC-ARM-B"}
    }
    print(f"seeds with both arms present: {len(usable)} of {len(seeds)}", flush=True)

    # --- draw the candidate sample, per seed per arm ------------------------
    # Seeded per (arm, seed) so the draw is reproducible and independent of the
    # order the seeds happen to be iterated in.
    #
    # The pool is the UNFILTERED top-k: the special-purpose filter needs
    # disambiguation, which is not known until payloads are fetched, and the AS
    # seed records carry mbid and score only. rc_score.py drops any drawn
    # candidate that turns out to be a placeholder, from numerator and
    # denominator alike and identically in both arms, and reports the counts.
    wanted: dict[str, set[str]] = {"RC-ARM-P": set(), "RC-ARM-B": set()}
    for mbid, rec in sorted(usable.items()):
        for arm, arm_rec in rec["arms"].items():
            pool = arm_rec["top_k"]
            digest = hashlib.sha256(f"{RC_SEED}:{arm}:{mbid}".encode()).digest()
            rng = np.random.default_rng(int.from_bytes(digest[:8], "big"))
            take = min(M_SAMPLE, len(pool))
            chosen = (
                [pool[i] for i in rng.choice(len(pool), size=take, replace=False)]
                if take
                else []
            )
            arm_rec["sampled"] = sorted(chosen)
            arm_rec["sampled_is_exhaustive"] = len(pool) <= M_SAMPLE
            wanted[arm].update(chosen)

    print(
        f"candidate lists needed: RC-ARM-P {len(wanted['RC-ARM-P'])}, "
        f"RC-ARM-B {len(wanted['RC-ARM-B'])}",
        flush=True,
    )

    # --- collect candidate lists -------------------------------------------
    # RC-ARM-P is archive-first; RC-ARM-B is always live. Cached by (arm, mbid),
    # so a candidate sampled for several seeds is fetched once.
    collected: dict[str, dict[str, dict]] = {"RC-ARM-P": {}, "RC-ARM-B": {}}
    # (name, disambiguation) per MBID, harvested from every payload seen. This is
    # the only source of disambiguation available: there is no per-artist metadata
    # endpoint, and the adopted artifact cannot supply it because the build drops
    # special-purpose entities before emitting, so they are absent by construction.
    # RC §0 requires the filter be applied identically to both arms, from harvested
    # disambiguation, with the drop counts reported -- rc_score.py does that.
    identities: dict[str, tuple[str, str]] = {}
    counts = {"archive_hit": 0, "live_fetch": 0, "failed": 0}
    started = time.time()
    total = len(wanted["RC-ARM-P"]) + len(wanted["RC-ARM-B"])
    done = 0

    for arm in ("RC-ARM-P", "RC-ARM-B"):
        for mbid in sorted(wanted[arm]):
            payload: bytes | None = None
            origin = "live"
            if arm == "RC-ARM-P":
                path = ARCHIVE / "similar" / source.name / f"{mbid}.json"
                if path.is_file():
                    payload = path.read_bytes()
                    origin = "archive"
                    counts["archive_hit"] += 1
            if payload is None:
                status, body = fetch(mbid, ALGORITHM[arm])
                counts["live_fetch"] += 1
                if status != 200:
                    counts["failed"] += 1
                    collected[arm][mbid] = {
                        "status": status,
                        "body_head": body.decode("utf-8", "replace")[:200],
                    }
                    done += 1
                    continue
                payload = body

            try:
                neighbours = source.parse(payload, exclude_mbid=mbid)
            except Exception as exc:  # noqa: BLE001 -- loud, never guessed at
                counts["failed"] += 1
                collected[arm][mbid] = {"status": 200, "parse_error": repr(exc)}
                done += 1
                continue

            # Full list, not top-k: selecting top-k is a SCORING decision (the
            # special-purpose filter has to be applied before the cut, and its
            # identities are only known once payloads are in hand). The runner
            # collects; rc_score.py decides. Same split as the AS harness.
            collected[arm][mbid] = {
                "status": 200,
                "origin": origin,
                "n_candidates_returned": len(neighbours),
                "candidates": [{"mbid": n.mbid, "score": n.score} for n in neighbours],
            }
            identities.update(harvest_identities([payload]))
            done += 1
            if done % 100 == 0:
                rate = done / max(1e-9, time.time() - started)
                print(
                    f"  {done}/{total}  ({rate:.1f}/s, "
                    f"~{(total - done) / max(rate, 1e-9) / 60:.1f} min left, "
                    f"archive {counts['archive_hit']}, live {counts['live_fetch']})",
                    flush=True,
                )

    payload_out = {
        "governing_document": (
            "docs/superpowers/specs/2026-07-29-reciprocity-sampling-preregistration.md"
        ),
        "artifact_sha256": actual,
        "endpoint": ENDPOINT,
        "rc_seed": RC_SEED,
        "m_sample": M_SAMPLE,
        "k": K,
        "algorithms": ALGORITHM,
        "seed_source": "analysis/2026-07-29-cap-selection-sim/as_raw_records.json (RC-A1)",
        "collection_counts": counts,
        "seeds": usable,
        "candidate_lists": collected,
        "identities": {m: list(v) for m, v in sorted(identities.items())},
    }
    OUT.write_text(json.dumps(payload_out), encoding="utf-8")
    print(
        f"\nwritten: {OUT} ({OUT.stat().st_size / 1e6:.1f} MB)\n"
        f"archive hits {counts['archive_hit']}, live fetches "
        f"{counts['live_fetch']}, failures {counts['failed']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
