"""CEX- re-census, assembly: freeze one drop list per population.

FORWARD COPY of `../2026-08-05-ulf-census/ulf_droplist.py`, run for plan Task 11
Step 3 over the extended 117,302-artist ALG-B archive. Copied rather than re-run
in place for the same reason as its two siblings here: the original writes its
payloads beside itself and would overwrite a frozen record.

THREE DIFFERENCES FROM THE ORIGINAL, and they are the only ones:
  * `STAMP` names this run (it is written into the coverage store as `clip_src`).
  * the payload's `censused` date, which the original hardcodes as 2026-08-05.
  * outputs land in THIS directory, which follows from the copy.

⚠ ONLY THE ALG-B PAYLOAD IS A CANDIDATE FOR SHIPPING. This script writes both
populations because the worklist carries both, but ALG-E's archive never changed
(75,000 artists, population sha identical across both censuses) and its shipped
list is sha-pinned in `unlistenable_drop.py`. The ALG-E payload regenerated here
is a BY-PRODUCT: prior ULF- verdicts are not among the carried ones, so its
class members were re-resolved against Deezer today, and clip availability moves.
Shipping it would reverse adopted verdicts on a population nobody re-crawled —
which is exactly what this file's own `snapshot_warning` cautions against. The
sha pin is what stops that happening by accident; do not update it to match.

Runs only when `ulf_clips.json` exists — which the clip stage writes only
when zero refusals remain (ULF-4) — and assembles, per population:

  drop = class members whose verdict is drop, where a verdict is
         (a) carried frozen from a prior list (ULF-3),
         (b) mechanical — no name to search or no DSP link (keep requires
             a DSP link AND a resolving clip; either absence decides), or
         (c) fresh — the keep-check ran and the clip did not resolve.
  keep = everyone else in the class, each carrying its clip provenance
         INCLUDING whether the id path also resolved (ULC-F4's instrument
         data, ULF-2 — recorded, never read here).

The payload's `population` block is the `ULC-F1` identity: count, sha256
over the sorted MBIDs, and the members — the archive artist set, which is
what `unlistenable_drop.py` refuses against. The lists then ship as package
data; the copy step and pinned shas live in the wiring, not here.

Also writes the clip outcomes back to the coverage store (`ULC-F2`), so a
future census reuses them instead of re-resolving.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-ulf-census/ulf_droplist.py
"""

from __future__ import annotations

import json
import time

from hashlib import sha256
from pathlib import Path

from artistpath_builder.config import PRODUCTION_ALGORITHM

HERE = Path(__file__).parent
COVERAGE = HERE.parent / "census-coverage" / "ulf_coverage.json"
WORKLIST = HERE / "ulf_worklist.json"
CLIPS = HERE / "ulf_clips.json"

STAMP = "cex-recensus-2026-08-09"
RULE = (
    "drop iff no sole-credited substantial MB release group (ULC-D2: "
    "primary-type Album/EP/Single, no secondary types, >= 1 release of >= 2 "
    "tracks; unknown track count is not substantial) AND NOT (commercial-DSP "
    "link AND a clip resolves via the app's Deezer->iTunes name path). Prior "
    "no-release and featured-credit verdicts carry frozen (ULF-3). Rule "
    "document: docs/superpowers/specs/2026-08-05-unlistenable-filter-rule.md"
)


def population_sha(mbids) -> str:
    return sha256(json.dumps(sorted(mbids), sort_keys=True).encode()).hexdigest()


def main() -> None:
    if not CLIPS.exists():
        raise SystemExit(
            "ulf_clips.json does not exist — the clip stage has not "
            "completed with zero refusals. Nothing freezes early (ULF-4)."
        )
    work = json.loads(WORKLIST.read_text(encoding="utf-8"))
    clips = json.loads(CLIPS.read_text(encoding="utf-8"))["artists"]

    verdicts: dict[str, dict] = {}
    for m, v in work["carried_verdicts"].items():
        verdicts[m] = {"verdict": v["verdict"], "why": f"carried:{v['src']}"}
    for m in work["mechanical_drops"]["no_name"]:
        verdicts[m] = {"verdict": "drop", "why": "no_name"}
    for m in work["mechanical_drops"]["no_dsp"]:
        verdicts[m] = {"verdict": "drop", "why": "no_dsp"}
    for m, rec in clips.items():
        keep = rec["name_path"]["resolves"]
        verdicts[m] = {"verdict": "keep" if keep else "drop",
                       "why": "clip_resolves" if keep else "clip_missing"}

    outputs = {}
    for alg, class_members in work["classes"].items():
        unresolved = [m for m in class_members if m not in verdicts]
        if unresolved:
            raise SystemExit(
                f"{alg}: {len(unresolved)} class members have no verdict "
                f"(e.g. {unresolved[:5]}) — the worklist and the clip "
                "capture disagree; nothing freezes."
            )
        drop = sorted(m for m in class_members
                      if verdicts[m]["verdict"] == "drop")
        keep = sorted(m for m in class_members
                      if verdicts[m]["verdict"] == "keep")
        population = work["populations"][alg]
        manifest = work["population_manifest"][alg]
        actual_sha = population_sha(population)
        if actual_sha != manifest["sha256_over_sorted_mbids"]:
            raise SystemExit(f"{alg}: worklist manifest disagrees with its "
                             "own population — regenerate the census")
        keep_provenance = {}
        for m in keep:
            rec = clips.get(m)
            if rec is None:
                continue  # carried keep; its provenance is the prior list's
            keep_provenance[m] = {
                "source": rec["name_path"]["source"],
                "matched_artist_id": rec["name_path"]["matched_artist_id"],
                "deezer_recorded": rec.get("deezer"),
                "id_path_resolves": (rec.get("id_path") or {}).get("resolves"),
            }
        payload = {
            "rule": RULE,
            "censused": "2026-08-09",
            "snapshot_warning": (
                "The clip half mixes frozen prior snapshots (2026-08-01/03, "
                "carried per ULF-3) with a fresh capture, deliberately: "
                "re-resolving a prior verdict could reverse an adopted one. "
                "spec section 9 requires byte-identical builds and the "
                "builder is offline by a hard rule, so this file is data."
            ),
            "population": {
                "algorithm": alg,
                "count": manifest["count"],
                "sha256_over_sorted_mbids": actual_sha,
                "mbids": sorted(population),
            },
            "counts": {
                "population": manifest["count"],
                "class": len(class_members),
                "drop": len(drop),
                "keep": len(keep),
                "drop_carried": sum(1 for m in drop
                                    if verdicts[m]["why"].startswith("carried")),
                "drop_no_name": sum(1 for m in drop
                                    if verdicts[m]["why"] == "no_name"),
                "drop_no_dsp": sum(1 for m in drop
                                   if verdicts[m]["why"] == "no_dsp"),
                "drop_clip_missing": sum(1 for m in drop
                                         if verdicts[m]["why"] == "clip_missing"),
                "keep_carried": sum(1 for m in keep
                                    if verdicts[m]["why"].startswith("carried")),
                "keep_fresh": sum(1 for m in keep
                                  if verdicts[m]["why"] == "clip_resolves"),
            },
            "keep_clip_provenance": keep_provenance,
            "drop_mbids": drop,
            "keep_mbids": keep,
        }
        payload["sha256_over_sorted_drop_mbids"] = sha256(
            json.dumps(sorted(drop), sort_keys=True).encode()
        ).hexdigest()
        suffix = "alge" if alg == PRODUCTION_ALGORITHM else "algb"
        out = HERE / f"ulf_droplist_{suffix}.json"
        out.write_text(json.dumps(payload, indent=1, ensure_ascii=False),
                       encoding="utf-8")
        outputs[alg] = out
        print(f"{out.name}: class {len(class_members):,} -> drop "
              f"{len(drop):,}, keep {len(keep):,} "
              f"(list sha {payload['sha256_over_sorted_drop_mbids'][:16]}…, "
              f"population sha {actual_sha[:16]}…)", flush=True)

    # ULC-F2: the clip outcomes join the coverage store.
    store = json.loads(COVERAGE.read_text(encoding="utf-8"))
    for m, rec in clips.items():
        art = store["artists"].setdefault(m, {})
        art["clip_resolves"] = rec["name_path"]["resolves"]
        art["clip_id_path_resolves"] = (rec.get("id_path") or {}).get("resolves")
        art["clip_src"] = STAMP
    COVERAGE.write_text(json.dumps(store, indent=1, sort_keys=True),
                        encoding="utf-8")
    print(f"coverage store updated with {len(clips):,} clip outcomes "
          f"[{time.strftime('%H:%M:%S')}]", flush=True)


if __name__ == "__main__":
    main()
