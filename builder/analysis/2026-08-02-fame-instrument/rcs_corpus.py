"""RCS §1 -- assemble the 30-row hand-read corpus by derivation.

No new measurement and no new owner time: every value here already exists in a
committed file. This script only joins them into one shape the scorers can read.

  famous region (15)  fi_fam4_identity.json  -- rows with
                      excluded_from_FAM_4_by_prereg false (FERG is the one
                      exclusion; NOFX is already a single row, the identity
                      document having merged its two reads). Hand values are
                      recorded as display strings ("15M", "372k") and are
                      parsed to integers here.
  tail region (15)    fi_read6.json rows     -- already parsed integers, the
                      owner's 2026-08-02 checklist reads. MBIDs come from
                      fi_tail_sample.json, joined by name exactly as fi_read6.py
                      itself joins them.

CROSS-CHECKS (all fatal, because a silent corpus defect poisons both candidates)
  * exactly 15 + 15 rows, MBIDs unique across the whole corpus
  * the famous parsed values equal fi_read34.json's already-parsed `hand`
    column artist-for-artist -- the parser is checked against a committed
    parse rather than trusted
  * the tail set equals fi_read6.json's rows exactly, by name and by value

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/rcs_corpus.py
"""

from __future__ import annotations

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "fi_corpus.json"

FAM_SOURCE = "fi_fam4_identity.json (2026-07-25 bypass-run hand reads, identity-confirmed under FAM-AM1.4a)"
TAIL_SOURCE = "fi_read6.json (owner's 2026-08-02 tail checklist reads, committed d318089)"

_SUFFIX = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000}


def parse_hand(text: str) -> int:
    """'15M' -> 15000000, '14.8M' -> 14800000, '372k' -> 372000, '23' -> 23.

    Deliberately strict: anything the pattern does not cover raises rather than
    guessing, because a mis-parsed arbiter value is invisible downstream.
    """
    s = text.strip().replace(",", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)\s*([kKmMbB]?)", s)
    if not m:
        raise SystemExit(f"unparseable hand-read value: {text!r}")
    value = float(m.group(1)) * _SUFFIX.get(m.group(2).lower(), 1)
    if value != int(value):
        raise SystemExit(f"hand-read value is not a whole number: {text!r}")
    return int(value)


def famous_rows() -> list[dict]:
    doc = json.loads((HERE / "fi_fam4_identity.json").read_text(encoding="utf-8"))
    rows = []
    for r in doc["rows"]:
        if r["excluded_from_FAM_4_by_prereg"]:
            continue
        rows.append({
            "mbid": r["resolved_mbid"],
            "name": r["hand_read_name"],
            "region": "famous",
            "hand_value": parse_hand(r["hand_read_value_as_recorded"]),
            "hand_value_as_recorded": r["hand_read_value_as_recorded"],
            "hand_source": FAM_SOURCE,
        })
    return rows


def tail_rows() -> list[dict]:
    read6 = json.loads((HERE / "fi_read6.json").read_text(encoding="utf-8"))
    sample = json.loads((HERE / "fi_tail_sample.json").read_text(encoding="utf-8"))
    by_name = {r["name"]: r["mbid"] for r in sample["sample"]}
    rows = []
    for r in read6["rows"]:
        if r["name"] not in by_name:
            raise SystemExit(f"tail row not in the draw sample: {r['name']!r}")
        rows.append({
            "mbid": by_name[r["name"]],
            "name": r["name"],
            "region": "tail",
            "hand_value": int(r["hand"]),
            "hand_value_as_recorded": str(r["hand"]),
            "hand_source": TAIL_SOURCE,
        })
    return rows


def check(corpus: list[dict]) -> dict:
    fam = [r for r in corpus if r["region"] == "famous"]
    tail = [r for r in corpus if r["region"] == "tail"]
    if (len(fam), len(tail)) != (15, 15):
        raise SystemExit(f"corpus is {len(fam)} famous + {len(tail)} tail, expected 15 + 15")
    mbids = [r["mbid"] for r in corpus]
    if len(set(mbids)) != 30:
        raise SystemExit("duplicate MBID in the corpus")

    # the parser, checked against a committed parse of the same strings
    read34 = json.loads((HERE / "fi_read34.json").read_text(encoding="utf-8"))
    committed_fam = {a["name"]: a["hand"] for a in read34["FAM_4"]["artists"]}
    mine = {r["name"]: r["hand_value"] for r in fam}
    if mine != committed_fam:
        diff = {k: (mine.get(k), committed_fam.get(k))
                for k in set(mine) | set(committed_fam) if mine.get(k) != committed_fam.get(k)}
        raise SystemExit(f"famous hand values disagree with fi_read34.json: {diff}")

    read6 = json.loads((HERE / "fi_read6.json").read_text(encoding="utf-8"))
    committed_tail = {r["name"]: int(r["hand"]) for r in read6["rows"]}
    mine_tail = {r["name"]: r["hand_value"] for r in tail}
    if mine_tail != committed_tail:
        raise SystemExit("tail rows do not match fi_read6.json exactly")

    return {
        "famous_rows": len(fam),
        "tail_rows": len(tail),
        "distinct_mbids": len(set(mbids)),
        "famous_values_match_fi_read34": True,
        "tail_rows_match_fi_read6": True,
        "zero_hand_rows": sorted(r["name"] for r in corpus if r["hand_value"] == 0),
    }


def main() -> None:
    corpus = famous_rows() + tail_rows()
    checks = check(corpus)
    payload = {
        "governing_document":
            "docs/superpowers/specs/2026-08-02-ruler-candidate-shootout-preregistration.md",
        "section": "RCS §1 -- the corpus (truth side)",
        "carries_no_candidate_value":
            "No W or D value appears here. This file is the arbiter side only.",
        "derivation": {
            "famous": FAM_SOURCE,
            "tail": TAIL_SOURCE,
            "mbid_join_for_tail": "fi_tail_sample.json, by name, as fi_read6.py joins it",
        },
        "hand_read_currency": "Spotify monthly listeners",
        "checks": checks,
        "rows": corpus,
    }
    OUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(checks, indent=2, ensure_ascii=False))
    for r in corpus:
        print(f"  {r['region']:6} {r['name'][:36]:36} {r['hand_value']:>10}  {r['mbid']}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
