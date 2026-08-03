"""The FCF-AM1 incremental keep-check: the shared-credit-only members.

Governing amendment (committed BEFORE this ran):
docs/superpowers/specs/2026-08-03-featured-credit-filter-rule.md, FCF-AM1.

The amendment removes the shared-credit-only Discogs exemptions, so those
members now face the keep-check. This runs it for exactly that increment —
the original capture (fcf_clips.json) is untouched and its members are
asserted disjoint from this one. Same imported resolver, same refusal rule
(FCF-3): refusals keep the checkpoint and exit non-zero.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-featured-credit-filter/fcf_clips_am1.py
"""

from __future__ import annotations

import json
import sys
import time

from pathlib import Path

HERE = Path(__file__).parent

for _sib in ("2026-08-02-candidate-tail-census", "2026-08-01-label-weighting",
             "2026-07-30-track-b-cap-selection"):
    _p = str(HERE.parent / _sib)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from ctc_clips import dsp_links, names_from_cells  # noqa: E402
from tail_clips import PAUSE_DEEZER, id_path, name_path  # noqa: E402

CLIPS = HERE / "fcf_clips.json"
SPLIT = HERE / "fcf_discogs_split.json"
OUT = HERE / "fcf_clips_am1.json"
CKPT = HERE / "fcf_clips_am1.checkpoint.json"
CKPT_EVERY = 25


def adopted_names(wanted: set[str]) -> dict[str, str]:
    from hashlib import sha256  # noqa: PLC0415
    from cb_metrics import ADOPTED, ADOPTED_SHA  # noqa: PLC0415
    from artistpath_api.graph_store import GraphStore  # noqa: PLC0415

    if sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("adopted artifact mismatch")
    store = GraphStore.load(ADOPTED)
    return {
        mbid: store.names[i]
        for i, mbid in enumerate(store.mbids)
        if mbid in wanted
    }


def main() -> None:
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    original = json.loads(CLIPS.read_text(encoding="utf-8"))

    members = sorted(split["shared_only_mbids"])
    overlap = set(members) & set(original["records"])
    if overlap:
        raise SystemExit(
            f"{len(overlap)} amendment members already in the original "
            "capture -- they were exempt, this should be impossible"
        )
    print(f"FCF-AM1 increment: {len(members):,} members", flush=True)

    signals = dsp_links(set(members))
    targets = sorted(m for m in members if signals[m]["dsp"])
    print(f"DSP-linked, needing a lookup: {len(targets):,}; "
          f"~{len(targets) / 1400 * 45:.0f} min", flush=True)

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

    checked = [r for r in done.values()
               if r.get("mb_deezer_id") and r["name_path"].get("matched_artist_id")]
    wrong = [r for r in checked
             if r["name_path"]["matched_artist_id"] != r["mb_deezer_id"]]

    payload = {
        "status": (
            "FCF-AM1 incremental capture. The amendment was committed before "
            "any row here existed; fcf_droplist_am1.py merges it with the "
            "original capture and re-freezes whole."
        ),
        "increment_members": len(members),
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
    print(f"\nincrement keep-check: {len(resolves):,} of {len(targets):,} "
          f"DSP-linked members resolve; increment of {len(members):,}", flush=True)
    print(f"-> {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
