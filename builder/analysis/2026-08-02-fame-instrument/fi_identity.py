"""`FAM-3` and `FAM-4` identity resolution -- name -> MBID, BEFORE any ruler value.

Governing document:
  docs/superpowers/specs/2026-08-02-fame-instrument-adoption-preregistration.md
  §3 (`FAM-3`, `FAM-4`) and §8 `FAM-AM1`.4(a): "before any ruler value for these
  artists is read, every hand-read artist is resolved to an MBID via the
  MusicBrainz disambiguation procedure".

WHY IDENTITY COMES FIRST, AND WHY IT IS A SEPARATE SCRIPT
  `FAM-4` compares the owner's hand-read Spotify monthly listeners against the
  ruler. Those hand reads were Spotify NAME lookups, and a name lookup does not
  return an entity -- it returns whatever act holds that string today. `BYP-13`
  is the worked example: the card read "FERG", the graph node is A$AP Ferg, and
  the Spotify name search returned an unrelated artist with 23 monthly
  listeners, which entered the record as the deepest discovery in either run
  before it was caught. The failure direction is the dangerous one: a name
  collision flatters the result.

  So this script resolves names to MBIDs and stops. It reads NO fame_lb value
  for any artist and never opens the snapshot. Keeping it out of the same
  process as the comparison is what makes "identity first" a fact about the
  code rather than a promise about the order somebody ran things in.

EVIDENCE, THREE INDEPENDENT KINDS, ALL RECORDED PER ROW
  1. The artifact's own MusicBrainz disambiguation string, plus how many other
     artists in the artifact carry the same name (exactly, and after
     normalisation) -- that count IS the ambiguity, not a proxy for it.
  2. The artist's strongest similarity neighbours. A folk-rock band whose
     nearest neighbours are The Byrds and The Zombies is not a Japanese idol
     group of the same name, and no disambiguation string is needed to say so.
  3. For `FAM-4` only: whether the MBID appears in the bypass exclusion lists
     of the very runs the hand reads came from. Those URLs are transcribed in
     the findings document §10 and are parsed here rather than retyped. A hit
     is decisive -- it is the node the app actually put in front of him.

  Plus a MusicBrainz web lookup, fired by a MECHANICAL RULE rather than by
  judgement: any row where the artifact records no disambiguation, or where
  more than one artifact artist shares the normalised name. Rate-limited to
  1 request/second per MusicBrainz's terms.

Run from `builder/` (network: ~20 light requests, 1/second):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/fi_identity.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
if str(ROOT / "api" / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "api" / "src"))

from artistpath_api.graph_store import GraphStore  # noqa: E402

ADOPTED = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

USE_RUN = ROOT / "docs" / "superpowers" / "findings" / "2026-07-25-bypass-depth-use-run.md"

USER_AGENT = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"
MB_LOOKUP = "https://musicbrainz.org/ws/2/artist/%s?fmt=json"
MB_PAUSE = 1.05  # MusicBrainz: 1 request/second, and we are a guest here

OUT_FAM4 = HERE / "fi_fam4_identity.json"
OUT_FAM3 = HERE / "fi_fam3_identity.json"

# ---------------------------------------------------------------------------
# The hand reads, transcribed from `findings/2026-07-25-bypass-depth-use-run.md`
# §2 (`BYP-1`, run 1) and §3 (`BYP-10`, run 2). `hand_read` is the string as it
# appears in that document -- NOT reinterpreted, NOT rescaled -- so a reader can
# check this table against the source by eye. `flagged` records that the
# document itself marks the row suspect.
# ---------------------------------------------------------------------------
HAND_READS = [
    {"name": "Lykke Li", "hand_read": "15M", "run": 1, "press": 29},
    {"name": "The Human League", "hand_read": "6M", "run": 1, "press": 35},
    {"name": "NOFX", "hand_read": "1M", "run": 1, "press": 37,
     "note": "also unfamiliar in run 2 at press 60; the document records the "
             "same 1M figure in both tables, one artist, one read"},
    {"name": "Porcupine Tree", "hand_read": "500k", "run": 1, "press": 59},
    {"name": "Television", "hand_read": "372k", "run": 1, "press": 83,
     "note": "run 1's floor figure (BYP-3)"},
    {"name": "Boards of Canada", "hand_read": "1M", "run": 1, "press": 84},
    {"name": "Beach House", "hand_read": "14.8M", "run": 1, "press": 98},
    {"name": "New Order", "hand_read": "8.8M", "run": 2, "press": 41},
    {"name": "Love", "hand_read": "571k", "run": 2, "press": 65,
     "note": "no clip resolved (BYP-12); a generic name, and the record holds a "
             "name-search for \"Love\" returning Sean Combs (FAM-AM1.4a)"},
    {"name": "Captain Beefheart & His Magic Band", "hand_read": "235k",
     "run": 2, "press": 65},
    {"name": "FERG", "hand_read": "23", "run": 2, "press": 89, "flagged": True,
     "flag_reason":
         "BYP-13: the document marks this row NOT a discovery. The graph node "
         "is A$AP Ferg; the hand read is an unrelated Spotify artist of the "
         "same name. FAM-4 excludes the FERG/A$AP Ferg class by name (§3).",
     "excluded_from_FAM_4": True},
    {"name": "10cc", "hand_read": "6.7M", "run": 2, "press": 91},
    {"name": "Blood Red Shoes", "hand_read": "168k", "run": 2, "press": 93,
     "note": "run 2's floor figure (BYP-3, BYP-10)"},
    {"name": "Black Rebel Motorcycle Club", "hand_read": "716k", "run": 2,
     "press": 93},
    {"name": "Quantic", "hand_read": "2.3M", "run": 2, "press": 100},
    {"name": "Nightmares on Wax", "hand_read": "1.7M", "run": 2, "press": 100},
]

# `FAM-3`'s nine, fixed in §3 and forward-only (`FAM-AM1`.5 leaves the list
# unchanged). No hand-read value exists for these -- the criterion is a
# percentile bar, not a concordance.
FAM3_NAMES = [
    "Radiohead", "The Beatles", "Metallica", "Coldplay", "Muse",
    "R.E.M.", "Pixies", "PJ Harvey", "Pink Floyd",
]


def norm(s: str) -> str:
    """Fold to letters and digits. Deliberately aggressive: it OVER-collides,
    so a collision count of 1 under it is a strong statement, and the exact
    count is reported separately."""
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def exclusion_lists(md: str) -> dict[str, list[str]]:
    """MBIDs from the reproducible-state URLs in §10, parsed not retyped."""
    out: dict[str, list[str]] = {}
    for line in md.splitlines():
        line = line.strip()
        if not line.startswith("http://localhost:"):
            continue
        parsed = urllib.parse.urlsplit(line)
        # Which state this is: the path holds the endpoints, the query the
        # exclusions. Label by port + exclusion counts so two states of the
        # same run stay distinguishable.
        q = urllib.parse.parse_qs(parsed.query)
        for param, values in q.items():
            mbids = [x for v in values for x in v.split(",") if x]
            key = f"{parsed.netloc}:{param}:{len(mbids)}"
            out[key] = mbids
    return out


def mb_lookup(mbid: str) -> dict:
    req = urllib.request.Request(MB_LOOKUP % mbid,
                                 headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as resp:
        d = json.loads(resp.read().decode("utf-8"))
    span = d.get("life-span") or {}
    return {
        "name": d.get("name"),
        "disambiguation": d.get("disambiguation") or None,
        "type": d.get("type"),
        "country": d.get("country"),
        "begin": span.get("begin"),
        "end": span.get("end"),
    }


def main() -> None:
    digest = sha256(ADOPTED.read_bytes()).hexdigest()
    if digest != ADOPTED_SHA:
        raise SystemExit(f"adopted artifact mismatch: {digest} != {ADOPTED_SHA}")
    store = GraphStore.load(ADOPTED)
    print(f"adopted artifact: {len(store.mbids):,} artists", flush=True)

    exact: dict[str, list[int]] = {}
    normed: dict[str, list[int]] = {}
    for i, n in enumerate(store.names):
        exact.setdefault(n, []).append(i)
        normed.setdefault(norm(n), []).append(i)

    excl = exclusion_lists(USE_RUN.read_text(encoding="utf-8"))
    print("exclusion lists parsed from §10: "
          + ", ".join(f"{k}" for k in sorted(excl)), flush=True)
    where: dict[str, list[str]] = {}
    for key, mbids in excl.items():
        for pos, m in enumerate(mbids, 1):
            where.setdefault(m, []).append(f"{key}#{pos}")

    lookups = 0

    def resolve(name: str, use_runs: bool) -> dict:
        nonlocal lookups
        ex = exact.get(name, [])
        nm = [i for i in normed.get(norm(name), []) if i not in ex]
        candidates = ex + nm
        row: dict = {
            "artifact_exact_name_matches": len(ex),
            "artifact_normalised_name_matches": len(ex) + len(nm),
            "candidates": [],
        }
        for i in candidates:
            m = store.mbids[i]
            neigh = sorted(store.neighbours_of(i), key=lambda t: -t[1])[:6]
            cand = {
                "mbid": m,
                "artifact_name": store.names[i],
                "artifact_disambiguation": store.disambiguations[i] or None,
                "exact_name_match": i in ex,
                "top_neighbours": [store.names[j] for j, _ in neigh],
            }
            if use_runs:
                cand["in_bypass_exclusion_lists"] = where.get(m, [])
            row["candidates"].append(cand)

        # Mechanical MusicBrainz trigger: no disambiguation recorded, or more
        # than one artifact artist shares the normalised name.
        need_mb = (len(candidates) != 1
                   or store.disambiguations[candidates[0]] in (None, ""))
        row["musicbrainz_lookup_fired"] = bool(need_mb and candidates)
        row["musicbrainz_lookup_rule"] = (
            "fired: no disambiguation recorded in the artifact, or >1 artifact "
            "artist shares the normalised name" if need_mb else
            "not fired: exactly one artifact artist, and it carries a "
            "disambiguation string")
        if need_mb:
            for cand in row["candidates"]:
                try:
                    cand["musicbrainz"] = mb_lookup(cand["mbid"])
                except Exception as e:  # noqa: BLE001 -- evidence, never fatal
                    cand["musicbrainz"] = {"error": str(e)}
                lookups += 1
                time.sleep(MB_PAUSE)
        return row

    # ------------------------- FAM-4 -------------------------
    fam4_rows = []
    for hr in HAND_READS:
        print(f"  resolving (FAM-4): {hr['name']}", flush=True)
        r = resolve(hr["name"], use_runs=True)
        exact_only = [c for c in r["candidates"] if c["exact_name_match"]]
        in_run = [c for c in exact_only if c["in_bypass_exclusion_lists"]]

        if len(exact_only) == 1:
            resolved = exact_only[0]["mbid"]
            basis = "unique exact name match in the adopted artifact"
        elif len(in_run) == 1:
            resolved = in_run[0]["mbid"]
            basis = ("several artists share the name; exactly one appears in "
                     "the bypass exclusion lists of the runs the hand read "
                     "came from")
        else:
            resolved = "CANNOT_CONFIRM"
            basis = ("no unique exact name match and no unique hit in the run "
                     "exclusion lists")

        ev = [f"{basis}."]
        for c in exact_only:
            ev.append(
                f"[{c['mbid']}] artifact name {c['artifact_name']!r}, "
                f"disambiguation "
                f"{c['artifact_disambiguation'] or 'none recorded'}; strongest "
                f"similarity neighbours: {', '.join(c['top_neighbours'])}"
                + (f"; appears in the run exclusion lists at "
                   f"{', '.join(c['in_bypass_exclusion_lists'])}"
                   if c["in_bypass_exclusion_lists"] else
                   "; not present in any run exclusion list")
                + (f"; MusicBrainz: {c['musicbrainz']}" if "musicbrainz" in c
                   else ""))
        if r["artifact_normalised_name_matches"] > len(exact_only):
            near = [c for c in r["candidates"] if not c["exact_name_match"]]
            ev.append(
                "near-name collisions under normalisation, recorded and NOT "
                "resolved to: "
                + "; ".join(f"{c['artifact_name']!r} "
                            f"({c['artifact_disambiguation'] or 'no disambiguation'})"
                            for c in near))

        fam4_rows.append({
            "hand_read_name": hr["name"],
            "hand_read_value_as_recorded": hr["hand_read"],
            "source_run": hr["run"],
            "source_press": hr["press"],
            "flagged_suspect_by_findings_doc": bool(hr.get("flagged")),
            "flag_reason": hr.get("flag_reason"),
            "excluded_from_FAM_4_by_prereg": bool(hr.get("excluded_from_FAM_4")),
            "note": hr.get("note"),
            "resolved_mbid": resolved,
            "evidence": " ".join(ev),
            "detail": r,
        })

    # ------------------------- FAM-3 -------------------------
    fam3_rows = []
    for name in FAM3_NAMES:
        print(f"  resolving (FAM-3): {name}", flush=True)
        r = resolve(name, use_runs=False)
        exact_only = [c for c in r["candidates"] if c["exact_name_match"]]
        if len(exact_only) == 1:
            resolved = exact_only[0]["mbid"]
            basis = "unique exact name match in the adopted artifact"
        else:
            resolved = "CANNOT_CONFIRM"
            basis = f"{len(exact_only)} artists share this exact name"
        ev = [f"{basis}."]
        for c in exact_only:
            ev.append(
                f"[{c['mbid']}] artifact name {c['artifact_name']!r}, "
                f"disambiguation "
                f"{c['artifact_disambiguation'] or 'none recorded'}; strongest "
                f"similarity neighbours: {', '.join(c['top_neighbours'])}"
                + (f"; MusicBrainz: {c['musicbrainz']}" if "musicbrainz" in c
                   else ""))
        if r["artifact_normalised_name_matches"] > len(exact_only):
            near = [c for c in r["candidates"] if not c["exact_name_match"]]
            ev.append(
                "near-name collisions under normalisation, recorded and NOT "
                "resolved to: "
                + "; ".join(f"{c['artifact_name']!r} "
                            f"({c['artifact_disambiguation'] or 'no disambiguation'})"
                            for c in near))
        fam3_rows.append({
            "hand_read_name": name,
            "hand_read_value_as_recorded": None,
            "flagged_suspect_by_findings_doc": False,
            "resolved_mbid": resolved,
            "evidence": " ".join(ev),
            "detail": r,
        })

    header = {
        "governing_document":
            "docs/superpowers/specs/"
            "2026-08-02-fame-instrument-adoption-preregistration.md",
        "step": "FAM-AM1.4(a) identity confirmation -- runs BEFORE any ruler "
                "value for these artists is read",
        "carries_no_ruler_value":
            "No fame_lb_raw and no fame_lb_pctl appears here for any artist; "
            "this script never opens the snapshot.",
        "substrate": {"file": ADOPTED.name, "sha256": ADOPTED_SHA},
        "musicbrainz_lookups": {
            "count": lookups,
            "note": "total across BOTH output files -- one shared rate-limited "
                    "pass at 1 request/second; per-row, `musicbrainz_lookup_"
                    "fired` says whether this row spent one",
        },
    }
    OUT_FAM4.write_text(json.dumps({
        **header,
        "criterion": "FAM-4 -- hand-read concordance (load-bearing)",
        "hand_read_source":
            "docs/superpowers/findings/2026-07-25-bypass-depth-use-run.md "
            "§2 (BYP-1, run 1) and §3 (BYP-10, run 2); values transcribed as "
            "the strings that document records",
        "exclusion_list_source":
            "§10 reproducible-state URLs, parsed from the document rather than "
            "retyped; a key is netloc:param:count",
        "rows": fam4_rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    OUT_FAM3.write_text(json.dumps({
        **header,
        "criterion": "FAM-3 -- top-end sanity (smoke test, FAM-AM1.5)",
        "hand_read_source": "none -- FAM-3's list is fixed in §3 of the "
                            "pre-registration and carries no hand-read value",
        "rows": fam3_rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    unresolved4 = [r["hand_read_name"] for r in fam4_rows
                   if r["resolved_mbid"] == "CANNOT_CONFIRM"]
    unresolved3 = [r["hand_read_name"] for r in fam3_rows
                   if r["resolved_mbid"] == "CANNOT_CONFIRM"]
    print(f"\nwrote {OUT_FAM4.name} ({len(fam4_rows)} rows) and "
          f"{OUT_FAM3.name} ({len(fam3_rows)} rows); "
          f"{lookups} MusicBrainz lookups")
    print(f"CANNOT_CONFIRM -- FAM-4: {unresolved4 or 'none'}; "
          f"FAM-3: {unresolved3 or 'none'}")


if __name__ == "__main__":
    main()
