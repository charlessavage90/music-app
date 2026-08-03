"""Resolve the class members' Discogs ids the REL- census never saw.

DIAGNOSTIC ONLY, second half of the featured-credit census. fcf_census.py
found that Discogs presence is the predicate-deciding column: 2,558 of the
adopted class's 3,961 members have a KNOWN Discogs release-level artist
credit, and 2,167 ids across the union are uncensused by rel_discogs_raw.json
-- including both worked instances (5293127, 5454241). Whether "has a Discogs
release" exempts an artist from the class (the faithful mirror of the adopted
rule's dual-source release signal) cannot be decided while those ids are
unknown, so this resolves them before the rule document freezes anything.

WHY <artists> PRESENCE IS THE RIGHT DISCOGS-SIDE SPLIT
  Discogs puts featured and session credits in <extraartists> and track-level
  blocks; the release-level <artists> block is the main credited artists.
  ctc_census.pass_discogs reads <artists> only (same reader as the adopted
  rule's census), so presence there is Discogs' own primary-ish signal --
  imperfect (joined "A feat. B" credits sometimes land both in <artists>),
  but the error direction is exemption, never an extra drop.

Sources, all local, no network:
  MB artist dump          ~17 GiB    ~2 min   re-derive members' discogs ids
  Discogs releases XML    57.4 GiB  ~21 min   presence for uncensused ids

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-03-featured-credit-filter/fcf_discogs.py
"""

from __future__ import annotations

import json
import sys

from pathlib import Path

HERE = Path(__file__).parent

_CTC = HERE.parent / "2026-08-02-candidate-tail-census"
if str(_CTC) not in sys.path:
    sys.path.insert(0, str(_CTC))

from ctc_census import DISCOGS_RELEASES, pass_artist, pass_discogs  # noqa: E402

CENSUS = HERE / "fcf_census.json"
REL_DISCOGS = HERE.parent / "2026-07-31-release-tag-coverage" / "rel_discogs_raw.json"
OUT = HERE / "fcf_discogs.json"

WORKED = {
    "7e4f57b3-569f-4cde-9ad8-87d9a474fd41": "田島賢",
    "f62c24cd-6101-4588-a3e9-d364fe358cc3": "TJ Brown",
}


def main() -> None:
    if not DISCOGS_RELEASES.exists():
        raise SystemExit(f"missing dump: {DISCOGS_RELEASES}")

    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    members = set(census["class_mbids"])
    print(f"class members: {len(members):,}", flush=True)

    # fcf_census.py did not persist the per-member signal map; re-deriving it
    # costs ~2 min and keeps that file exactly as committed.
    signals = pass_artist(members)

    known = json.loads(REL_DISCOGS.read_text(encoding="utf-8"))
    ids = {
        rec["discogs"]: mbid
        for mbid, rec in signals.items()
        if rec.get("discogs")
    }
    unknown = {i for i in ids if i not in known}
    print(f"discogs ids: {len(ids):,}, uncensused by REL-: {len(unknown):,}",
          flush=True)

    has_release_new = pass_discogs(unknown) if unknown else set()

    def has_discogs_release(mbid: str) -> bool:
        did = (signals.get(mbid) or {}).get("discogs")
        if not did:
            return False
        return bool(known.get(did)) or did in has_release_new

    exempt = sorted(m for m in members if has_discogs_release(m))
    worked = {
        mbid: {
            "name": name,
            "discogs_id": (signals.get(mbid) or {}).get("discogs"),
            "has_discogs_release": has_discogs_release(mbid),
        }
        for mbid, name in WORKED.items()
    }
    for mbid, row in worked.items():
        print(f"worked instance {row['name']} ({mbid[:8]}): "
              f"has_discogs_release={row['has_discogs_release']}", flush=True)

    payload = {
        "status": (
            "DIAGNOSTIC, second census half. Resolves Discogs presence for "
            "every class member so the rule document can fix the predicate."
        ),
        "class_members": len(members),
        "with_discogs_id": len(ids),
        "ids_uncensused_by_REL": len(unknown),
        "ids_resolved_with_release": len(has_release_new),
        "members_with_discogs_release": len(exempt),
        "worked_instances": worked,
        "exempt_mbids_under_discogs_presence": exempt,
        "resolved_ids_with_release": sorted(has_release_new),
    }
    OUT.write_text(json.dumps(payload, indent=1), encoding="utf-8")
    print(f"\nmembers with a Discogs release: {len(exempt):,} of {len(members):,}",
          flush=True)
    print(f"-> {OUT.name}", flush=True)


if __name__ == "__main__":
    main()
