"""The FCF- keep-check's network half: clip resolution for the class.

Governing document (committed BEFORE this ran — the freeze point):
docs/superpowers/specs/2026-08-03-featured-credit-filter-rule.md

Population: the census class minus the Discogs-exempt members (FCF-1). Only
DSP-linked members are looked up — the keep-check's first clause cuts the rest
regardless of clip (FCF-2), and their records here say so rather than being
absent. The resolver is the adopted rule's, imported and never restated
(tail_clips.name_path / id_path); the id path is instrument data, not the
criterion.

FCF-3: refusals are not evidence. If any lookup was refused, this script
KEEPS its checkpoint, writes no summary, and exits non-zero — re-run it until
every outcome is a real answer. The droplist writer (fcf_droplist.py) refuses
to run from a capture containing refusals.

Run from `builder/` (resumable; ~45 min per 1,400 targets):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-featured-credit-filter/fcf_clips.py
"""

from __future__ import annotations

import json
import sys
import time

from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent

for _sib in ("2026-08-02-candidate-tail-census", "2026-08-01-label-weighting",
             "2026-07-30-track-b-cap-selection"):
    _p = str(HERE.parent / _sib)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ctc_clips import dsp_links, names_from_cells  # noqa: E402
from tail_clips import PAUSE_DEEZER, id_path, name_path  # noqa: E402
from cb_metrics import ADOPTED, ADOPTED_SHA  # noqa: E402

from artistpath_api.graph_store import GraphStore  # noqa: E402

CENSUS = HERE / "fcf_census.json"
DISCOGS = HERE / "fcf_discogs.json"
OUT = HERE / "fcf_clips.json"
CKPT = HERE / "fcf_clips.checkpoint.json"
CKPT_EVERY = 25


def adopted_names(wanted: set[str]) -> dict[str, str]:
    """mbid -> display name from the sha-verified adopted artifact."""
    actual = sha256(ADOPTED.read_bytes()).hexdigest()
    if actual != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {actual} != {ADOPTED_SHA}")
    store = GraphStore.load(ADOPTED)
    return {
        mbid: store.names[i]
        for i, mbid in enumerate(store.mbids)
        if mbid in wanted
    }


def main() -> None:
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    discogs = json.loads(DISCOGS.read_text(encoding="utf-8"))

    exempt = set(discogs["exempt_mbids_under_discogs_presence"])
    members = sorted(set(census["class_mbids"]) - exempt)
    print(f"class after Discogs exemption (FCF-1): {len(members):,}", flush=True)

    signals = dsp_links(set(members))
    targets = sorted(m for m in members if signals[m]["dsp"])
    print(f"DSP-linked, needing a lookup (FCF-2): {len(targets):,}; "
          f"~{len(targets) / 1400 * 45:.0f} min", flush=True)

    # Names are what the app would display (FCF-2): the adopted artifact first,
    # the ALG-B cells for members it does not carry.
    names = adopted_names(set(targets))
    missing = {m for m in targets if m not in names}
    if missing:
        names.update(names_from_cells(missing))

    done: dict[str, dict] = {}
    if CKPT.exists():
        done = json.loads(CKPT.read_text(encoding="utf-8"))["done"]
        print(f"resuming: {len(done):,} already checked", flush=True)

    pending = [m for m in targets if m not in done]
    for n, mbid in enumerate(pending, 1):
        name = names.get(mbid, "")
        record: dict = {"name": name, "dsp": signals[mbid]["dsp"]}
        time.sleep(PAUSE_DEEZER)
        record["name_path"] = name_path(name) if name.strip() else {
            "resolves": False, "refused": ["no name"], "matched_artist_id": None
        }
        deezer_id = signals[mbid]["ids"].get("deezer")
        if deezer_id:
            time.sleep(PAUSE_DEEZER)
            record["id_path"] = id_path(deezer_id)
            record["mb_deezer_id"] = deezer_id
        done[mbid] = record
        if n % CKPT_EVERY == 0 or n == len(pending):
            CKPT.write_text(json.dumps({"done": done}), encoding="utf-8")
            print(f"  {n:,}/{len(pending):,} checked", flush=True)

    refused = sorted(
        m for m, r in done.items()
        if not r["name_path"].get("resolves") and r["name_path"].get("refused")
    )
    if refused:
        print(f"FCF-3: {len(refused):,} lookups were refused -- not evidence. "
              f"Checkpoint kept; re-run this script.", flush=True)
        raise SystemExit(1)

    resolves = sorted(m for m in targets if done[m]["name_path"]["resolves"])

    # BYP-13 instrument read: name path landed on a DIFFERENT Deezer artist
    # than MB recorded. Reported, not part of the criterion.
    checked = [r for r in done.values()
               if r.get("mb_deezer_id") and r["name_path"].get("matched_artist_id")]
    wrong = [r for r in checked
             if r["name_path"]["matched_artist_id"] != r["mb_deezer_id"]]

    payload = {
        "status": (
            "FCF-2 capture. The rule document was committed before any row "
            "here existed; fcf_droplist.py applies it, this file records it."
        ),
        "class_after_exemption": len(members),
        "dsp_linked_targets": len(targets),
        "resolves": len(resolves),
        "refused": 0,
        "byp13_wrong_artist": {
            "checked": len(checked),
            "wrong": len(wrong),
            "rate": round(len(wrong) / len(checked), 4) if checked else None,
        },
        "keep_mbids_by_the_rule": resolves,
        "records": done,
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    CKPT.unlink(missing_ok=True)
    print(f"\nkeep-check: {len(resolves):,} of {len(targets):,} DSP-linked "
          f"members resolve; class of {len(members):,}", flush=True)
    print(f"-> {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
