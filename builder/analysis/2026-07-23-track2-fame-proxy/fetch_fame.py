"""P4 step 2: fetch Deezer `nb_fan` for the fixed sample, by exact-name artist search.

**This deliberately shares no code with `api/.../clips.py`**, per pre-registration §0.
`clips.py` calls Deezer *track* search, takes the first hit, and never verifies the artist
name — which is the C1 wrong-artist failure mode visible in the code. Reusing it would
import that failure into the quantity the whole sweep is scored on. This module calls
Deezer **artist** search and matches exactly after P5 normalisation, and a name that does
not match is recorded as a failure rather than resolved to something plausible.

**Match failure is a measured outcome, not an error to be worked around.** It doubles as
the C6 matching pilot, and > 20 % of the sample (6 of 29, per §9 A10) is a pre-registered
falsifier. Do not hand-fix a miss; record it.

P5 normalisation, fixed here:

    NFKC  →  fold Unicode dashes/quotes/spaces to ASCII  →  collapse whitespace  →  casefold

then **exact** string equality. NFKC alone is not enough: it leaves U+2010 HYPHEN intact,
and the judged-listen record spells `blink‐182` with one. That is the record's own hyphen
trap (P5), present in live data.

Two modes:

    python fetch_fame.py --probe        # assumption check, out-of-sample names only
    python fetch_fame.py                # fetch the sample; requires labels.json to exist

`--probe` exists because "Deezer artist objects carry `nb_fan`" is an external assumption
verified by nothing in this repo (§0). It checks that against artists **not in the
sample**, so the assumption can be discharged while the owner's labels are still
outstanding and the sample stays unfetched.
"""

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SAMPLE = HERE / "sample.json"
LABELS = HERE / "labels.json"
OUT = HERE / "fan_counts.json"

API = "https://api.deezer.com/search/artist"
LIMIT = 25
PAUSE_S = 0.25  # Deezer's documented limit is 50 requests / 5 s; this is well under
TIMEOUT_S = 20

# Artists deliberately NOT in the sample, used only to check that `nb_fan` exists at all.
PROBE_NAMES = ["Radiohead", "Portishead", "Sault"]

# P5: Unicode punctuation folded to ASCII. Curated rather than derived from Unicode
# categories, so the rule is auditable and cannot shift under a Python version bump.
_FOLD = {
    **{c: "-" for c in "‐‑‒–—―−﹘﹣－"},
    **{c: "'" for c in "‘’‚‛ʼʹ＇"},
    **{c: '"' for c in "“”„‟＂"},
    **{c: " " for c in "              　"},
    "…": "...",
    "​": "",
    "‌": "",
    "‍": "",
    "﻿": "",
}
_FOLD_TABLE = str.maketrans(_FOLD)


def p5_normalise(name: str) -> str:
    """The P5 rule. Deterministic, and the only matching rule this module uses."""
    s = unicodedata.normalize("NFKC", name)
    s = s.translate(_FOLD_TABLE)
    s = re.sub(r"\s+", " ", s).strip()
    return s.casefold()


def search_artist(name: str) -> list[dict]:
    """Deezer artist search. Returns raw candidate rows; does no matching."""
    url = f"{API}?{urllib.parse.urlencode({'q': name, 'limit': LIMIT})}"
    req = urllib.request.Request(url, headers={"User-Agent": "artistpath-fame-proxy/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:  # noqa: S310 - fixed host
        payload = json.loads(resp.read().decode("utf-8"))
    if "error" in payload:
        raise RuntimeError(f"deezer error for {name!r}: {payload['error']}")
    return payload.get("data", [])


def resolve(name: str) -> dict:
    """Exact-match `name` after P5 normalisation. Never falls back to a near miss."""
    target = p5_normalise(name)
    candidates = search_artist(name)
    exact = [c for c in candidates if p5_normalise(c.get("name", "")) == target]

    row: dict = {
        "query": name,
        "normalised": target,
        "candidates_returned": len(candidates),
        "exact_matches": len(exact),
        "top_candidate": candidates[0].get("name") if candidates else None,
    }
    if not exact:
        row["matched"] = False
        row["nb_fan"] = None
        return row

    # More than one artist can carry the same name. Take the largest, and say so —
    # this is a disambiguation failure, not a clean match, and C6 should see it.
    best = max(exact, key=lambda c: c.get("nb_fan", 0))
    row["matched"] = True
    row["deezer_id"] = best.get("id")
    row["deezer_name"] = best.get("name")
    row["nb_fan"] = best.get("nb_fan")
    row["ambiguous"] = len(exact) > 1
    return row


def probe() -> int:
    """Discharge §0's external assumption without touching the sample."""
    sample_names = {
        n
        for members in json.loads(SAMPLE.read_text(encoding="utf-8"))["strata"].values()
        for n in members
    }
    print("Probing that Deezer artist objects carry `nb_fan`.")
    print("Out-of-sample names only; the sample stays unfetched.\n")
    ok = 0
    for name in PROBE_NAMES:
        if name in sample_names:
            raise SystemExit(f"probe name {name!r} is in the sample — would contaminate it")
        row = resolve(name)
        has = row.get("nb_fan") is not None
        ok += has
        print(
            f"  {name:<12} matched={row['matched']!s:<5} "
            f"nb_fan={row['nb_fan']!s:<10} candidates={row['candidates_returned']}"
        )
        time.sleep(PAUSE_S)

    print()
    if ok == len(PROBE_NAMES):
        print("ASSUMPTION HOLDS: nb_fan present on every probe.")
        return 0
    print(f"ASSUMPTION FAILS: nb_fan present on {ok}/{len(PROBE_NAMES)}.")
    print("§5's fallback is Wikipedia pageviews, same protocol, same labels.")
    return 1


def fetch_sample() -> int:
    if not LABELS.exists():
        raise SystemExit(
            f"{LABELS.name} not found.\n"
            "The owner's labels are collected BEFORE any fan count is fetched (§5 protocol\n"
            "step 1, then step 2). Write the labels first."
        )
    sample = json.loads(SAMPLE.read_text(encoding="utf-8"))
    stratum_of = {n: s for s, members in sample["strata"].items() for n in members}

    rows = []
    for name in sorted(stratum_of):
        row = resolve(name)
        row["stratum"] = stratum_of[name]
        rows.append(row)
        print(f"  {name:<22} {row['nb_fan']}")
        time.sleep(PAUSE_S)

    failures = [r for r in rows if not r["matched"]]
    rate = len(failures) / len(rows)
    result = {
        "source": "deezer artist search",
        "sample_size": len(rows),
        "match_failures": len(failures),
        "match_failure_rate": rate,
        "falsifier_fires": rate > 0.20,
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n{len(failures)}/{len(rows)} match failures ({rate:.1%}).")
    if rate > 0.20:
        print("FALSIFIER FIRES (> 20 %): nb_fan is unfit; move to Wikipedia pageviews.")
    for r in failures:
        print(f"  unmatched: {r['query']!r} (top candidate: {r['top_candidate']!r})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe", action="store_true", help="check nb_fan exists, out-of-sample")
    args = ap.parse_args()
    return probe() if args.probe else fetch_sample()


if __name__ == "__main__":
    sys.exit(main())
