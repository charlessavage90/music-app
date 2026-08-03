"""FAM- union fetch: ListenBrainz `total_user_count` for the union population.

Governing document:
  docs/superpowers/specs/2026-08-02-fame-instrument-adoption-preregistration.md
  (`FAM-`), §1 "The instrument, exactly", plus `FAM-AM1` in §8.

WHAT THIS PRODUCES
  `fi_union_snapshot.json` -- mbid -> `fame_lb_raw` (integer `total_user_count`)
  or null. A null is a MEASURED ABSENCE, not a missing key and not a floor
  value: §1 "Nulls" and `FAM-AM1`.8. The file is gitignored for size; its
  sha256, date and counts live in the committed sidecar
  `fi_union_snapshot.manifest.json`. Per `FAM-AM1`.7 the adopted object IS this
  dated file plus its sha256, so the sidecar is the instrument's identity.

POPULATION -- union, not the adopted frame
  The union of the adopted artifact and the `ALG-B` 2026-07-30 full build,
  93,067 MBIDs, constructed exactly as `../2026-08-02-dsp-ids/dsp_ids.py`
  constructs it and pinned by the same two sha256s. Both are verified before
  any request goes out: several graphs sit in scratch/ and they are NOT
  interchangeable. The count is asserted rather than reported, because a
  changed population silently changes every denominator downstream.

NO CLI ARGUMENTS, deliberately -- every path is a constant here, so no user
input reaches a filesystem call.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/fi_fetch.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
_FP = HERE.parent / "2026-07-30-fame-proxy-coverage"
if str(_FP) not in sys.path:
    sys.path.insert(0, str(_FP))

from fp_common import USER_AGENT, load_partial, post_json, run_batches  # noqa: E402

from artistpath_builder.artifact import deserialise  # noqa: E402

SCRATCH = HERE.parents[1] / "scratch"

# Pinned exactly as cb_metrics.ADOPTED_SHA / dsp_ids.CANDIDATE_SHA.
ADOPTED = SCRATCH / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
CANDIDATE = SCRATCH / "graph-algb-full.bin"
CANDIDATE_SHA = "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f"

EXPECTED_UNION = 93_067

ENDPOINT = "https://api.listenbrainz.org/1/popularity/artist"
# MAX_ITEMS_PER_GET in listenbrainz/webserver/views/api_tools.py: batching above
# it is silently TRUNCATED, not an error (read from master 2026-07-30).
MAX_PER_REQUEST = 1000
PAUSE = 0.5

OUT = HERE / "fi_union_snapshot.json"
MANIFEST = HERE / "fi_union_snapshot.manifest.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def verified_mbids(path: Path, expected_sha: str) -> set[str]:
    actual = sha256_file(path)
    if actual != expected_sha:
        raise SystemExit(f"{path.name} sha256 mismatch: {actual} != {expected_sha}")
    return set(deserialise(path.read_bytes()).mbids)


def fetch(chunk: list[str]) -> dict[str, int | None]:
    body = json.dumps({"artist_mbids": chunk}).encode()
    payload = post_json(
        ENDPOINT,
        body,
        {"User-Agent": USER_AGENT, "Content-Type": "application/json"},
    )
    out: dict[str, int | None] = {}
    for row in payload:
        # Not-found artists come back with counts set to null rather than being
        # omitted, so a null here is a real measured absence.
        out[row["artist_mbid"]] = row.get("total_user_count")
    return out


def main() -> None:
    adopted = verified_mbids(ADOPTED, ADOPTED_SHA)
    candidate = verified_mbids(CANDIDATE, CANDIDATE_SHA)
    union = sorted(adopted | candidate)
    print(
        f"adopted {len(adopted):,}  candidate {len(candidate):,}  "
        f"union {len(union):,}  ALG-B-only {len(candidate - adopted):,}",
        flush=True,
    )
    if len(union) != EXPECTED_UNION:
        raise SystemExit(
            f"union is {len(union):,}, pre-registration says {EXPECTED_UNION:,} "
            "-- refusing to fetch against an unexpected population"
        )

    done = load_partial(OUT)
    run_batches(union, MAX_PER_REQUEST, done, fetch, OUT, pause=PAUSE,
                label="listenbrainz-union")

    # Keys are the union and only the union, in sorted order: a resumed run must
    # not leave a stray key from an earlier population behind.
    snapshot = {m: done.get(m) for m in union}
    OUT.write_text(json.dumps(snapshot), encoding="utf-8")

    nulls = sum(1 for v in snapshot.values() if v is None)
    manifest = {
        "instrument": "ListenBrainz POST /1/popularity/artist -> total_user_count",
        "quantity": "fame_lb_raw",
        "governing_document":
            "docs/superpowers/specs/"
            "2026-08-02-fame-instrument-adoption-preregistration.md",
        "file": OUT.name,
        "sha256": sha256_file(OUT),
        "fetch_date": date.today().isoformat(),
        "mbid_count": len(snapshot),
        "null_count": nulls,
        "non_null_count": len(snapshot) - nulls,
        "population": "union of the adopted artifact and the ALG-B 2026-07-30 "
                      "full build",
        "source_artifacts": {
            "adopted": {"file": ADOPTED.name, "sha256": ADOPTED_SHA,
                        "artists": len(adopted)},
            "candidate_alg_b": {"file": CANDIDATE.name, "sha256": CANDIDATE_SHA,
                                "artists": len(candidate)},
        },
        "alg_b_only_artists": len(candidate - adopted),
        "nulls": "measured absences, preserved as JSON null; never a floor value "
                 "(FAM- section 1, FAM-AM1.8)",
    }
    MANIFEST.write_text(json.dumps(manifest, indent=1), encoding="utf-8")

    print(f"\nwrote {OUT.name}: {len(snapshot):,} mbids, {nulls:,} null "
          f"({nulls / len(snapshot):.4%})")
    print(f"sha256 {manifest['sha256']}")
    print(f"wrote {MANIFEST.name}")


if __name__ == "__main__":
    main()
