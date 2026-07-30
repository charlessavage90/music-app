"""COH-4, PRE-REGISTERED: one tag-based path score against the 11 blind verdicts.

RUNS ONLY IF ct_mb_sample's kill gate said PROCEED. Committed before any
coverage number exists, which is deliberately stronger than the gate requires:
nothing below can have been shaped by a result.

THE CORPUS IS A FALSIFIER, NEVER A TRAINING SET
  n = 11 (Phase 1 §3.8: 3 pairs x 4 bypass depths, one no-preference row
  excluded). There is no held-out set, so the rule below is scored ONCE. If
  it fails, that is the result. A second rule would be a new commit, reported
  as a second attempt. n = 11 can refute; it cannot confirm -- beating the
  bar promotes the idea to "worth a real test", never to a criterion.

SYN-7 BINDS
  Both listening verdicts date to 2026-07-22, before five of the nine
  calibration values existed. Agreement measured here is agreement with the
  owner's preferences AS OF THEN.

THE SCORING RULE, FROZEN
  Genre set G(a): normalised MusicBrainz genres UNION normalised Wikidata
  P136 labels (ct_common.norm_genre -- frozen in the step-1 commit).
  Step similarity s(u,v): Jaccard |G(u) & G(v)| / |G(u) | G(v)|, defined
  only when both sets are non-empty; otherwise the pair is UNSCORABLE.
  Path score: LEXICOGRAPHIC (min s over scorable adjacent pairs, then mean s
  over scorable adjacent pairs). Higher is better.

  Plain sentence, fixed now per CLAUDE.md: "A journey is scored by its single
  most jarring adjacent step -- the neighbouring pair whose genre lists share
  the least -- with the average step breaking ties; the metric agrees with
  the owner when the journey he picked has the least-bad worst step of the
  three he saw."

  Why min-then-mean and not a sum: the §7 argument. The failed metrics were
  edge sums; the owner's notes discard journeys on a single bad step ("the
  Avril Lavigne and Blink-182 hops felt wrong", "a leap that should have at
  least a step in between") and then choose on overall feel. A min is not
  expressible as an additive edge cost, which is exactly the class §7 says
  the instrument must live in. No free parameters, so nothing to tune
  against n = 11.

  Missing data: a row is READABLE only if every arm has at most one
  unscorable adjacent pair. Unreadable rows are excluded and reported; the
  denominator shrinks and is printed. Unscorable pairs never score 0 --
  missing-as-worst is the fame floor's collapse repeated in a new currency.

AGREEMENT COUNTING, AND THE BAR RECOMPUTED UNDER THE SAME COUNT
  His pick agrees iff its score is lexicographically STRICTLY greater than
  both other arms' (ties count against us). The §3.8 bar (adamic_adar 3/11,
  overlap_coefficient 3/11) is RECOMPUTED from the corpus's recorded hidden
  metrics under this same strict-max counting so the comparison is
  like-for-like; expectation: both reproduce 3/11, and payload (max) /
  ceiling_hops (min) reproduce 8/11 as context. If a reproduction differs
  from §3.8's published figure, both numbers are reported and the recomputed
  one is the bar -- fix the comparison, never the rule.

READ, FIXED BEFORE EXECUTION
  - Tag score agreement > recomputed AA and OC agreement: the topology-only
    claim is REFUTED in its strong form; the idea is promoted to "worth a
    pre-registered real test" and nothing more.
  - Tag score agreement <= that bar: the independent currency did no better
    than the metrics that failed; the §3.8 hardening stands and this line
    stops.
  - Chance line ~1/3 (3 arms): stated so 4/11 is read as "cleared a low bar",
    not as evidence of tracking. >= 8/11 would match the best in-currency
    metrics ever measured here; anything between is reported without spin.
  - Prediction, falsifiable: the rule clears the bar (>= 4/11). No prediction
    beyond that; genuinely uncertain.

Run from `builder/` (after the gate passes):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-coherence-tag-probe/ct_retrodict.py
"""

from __future__ import annotations

import json
import urllib.parse
from typing import Any

from ct_common import (
    HERE,
    USER_AGENT,
    fetch_mb_artists,
    load_partial,
    mb_genre_set,
    norm_genre,
    post_json,
    save_partial,
)

LISTEN = HERE.parent / "2026-07-22-c3-bypass-mechanisms" / "listen_secret.json"
GATE = HERE / "ct_coverage.json"
MB_RAW = HERE / "ct_path_tags_raw.json"
P136_RAW = HERE / "ct_path_p136_raw.json"
OUT = HERE / "ct_retrodict.json"

# Phase 1 §3.8's verdict table, verbatim. Metallica d5 was a recorded
# no-preference (A and V0 identical paths) and is excluded there, not here.
VERDICTS: dict[tuple[str, int], str] = {
    ("Miles Davis", 5): "V0",
    ("Miles Davis", 10): "A",
    ("Miles Davis", 15): "A",
    ("Miles Davis", 20): "A",
    ("The Shins", 5): "A",
    ("The Shins", 10): "A",
    ("The Shins", 15): "V0",
    ("The Shins", 20): "V0",
    ("Metallica", 10): "C",
    ("Metallica", 15): "C",
    ("Metallica", 20): "C",
}

# Context metrics from the corpus's hidden block: (key, direction). The bar
# metrics are AA and OC; payload and ceiling_hops are context only.
HIDDEN = [
    ("adamic_adar", max),
    ("overlap_coeff", max),
    ("payload", max),
    ("ceiling_hops", min),
]

LABEL_QUERY = """SELECT ?mbid ?genreLabel WHERE {
  VALUES ?mbid { %s }
  ?item wdt:P434 ?mbid .
  ?item wdt:P136 ?genre .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}"""


def fetch_p136_labels(mbids: list[str]) -> dict[str, list[str]]:
    done: dict[str, Any] = load_partial(P136_RAW)
    pending = [m for m in mbids if m not in done]
    if pending:
        values = " ".join('"%s"' % m for m in pending)
        body = urllib.parse.urlencode(
            {"query": LABEL_QUERY % values, "format": "json"}
        ).encode()
        payload = post_json(
            "https://query.wikidata.org/sparql",
            body,
            {
                "User-Agent": USER_AGENT,
                "Accept": "application/sparql-results+json",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            timeout=240,
        )
        for m in pending:
            done.setdefault(m, [])
        for row in payload["results"]["bindings"]:
            done[row["mbid"]["value"]].append(row["genreLabel"]["value"])
        save_partial(P136_RAW, done)
    return done


def genre_sets(paths_artists: list[list[dict]]) -> dict[str, set[str]]:
    mbids = sorted({a["mbid"] for path in paths_artists for a in path})
    mb = load_partial(MB_RAW)
    mb = fetch_mb_artists(mbids, mb, MB_RAW, label="path-artists")
    p136 = fetch_p136_labels(mbids)
    return {
        m: mb_genre_set(mb.get(m)) | {norm_genre(x) for x in p136.get(m, [])}
        for m in mbids
    }


def path_score(path: list[dict], genres: dict[str, set[str]]) -> tuple:
    """(min, mean) over scorable adjacent pairs; None if too many unscorable."""
    sims: list[float] = []
    unscorable = 0
    for u, v in zip(path, path[1:]):
        gu, gv = genres[u["mbid"]], genres[v["mbid"]]
        if not gu or not gv:
            unscorable += 1
            continue
        sims.append(len(gu & gv) / len(gu | gv))
    if unscorable > 1 or not sims:
        return ()
    return (min(sims), sum(sims) / len(sims))


def main() -> None:
    gate = json.loads(GATE.read_text(encoding="utf-8"))
    if "PROCEED" not in gate["gate"]["verdict"]:
        raise SystemExit("kill gate did not pass; this script must not run")

    corpus = json.loads(LISTEN.read_text(encoding="utf-8"))
    all_paths = [
        arm_block["artists"]
        for pair in corpus["pairs"]
        for depth_block in pair["depths"].values()
        for arm_block in depth_block.values()
    ]
    genres = genre_sets(all_paths)

    rows: list[dict] = []
    tag_agree = 0
    hidden_agree = {k: 0 for k, _ in HIDDEN}
    readable = 0
    for pair in corpus["pairs"]:
        arm_of = {token: arm for arm, token in pair["mapping"].items()}
        for depth, by_token in pair["depths"].items():
            pick = VERDICTS.get((pair["from"], int(depth)))
            if pick is None:
                continue
            scores = {
                arm_of[t]: path_score(block["artists"], genres)
                for t, block in by_token.items()
            }
            row: dict = {
                "pair": f"{pair['from']} -> {pair['to']}",
                "depth": int(depth),
                "picked": pick,
                "scores": {a: list(s) for a, s in scores.items()},
            }
            if any(s == () for s in scores.values()):
                row["readable"] = False
                rows.append(row)
                continue
            readable += 1
            row["readable"] = True
            others = [s for a, s in scores.items() if a != pick]
            row["tag_agree"] = all(scores[pick] > s for s in others)
            tag_agree += row["tag_agree"]
            for key, direction in HIDDEN:
                vals = {
                    arm_of[t]: block["_hidden_metrics"][key]
                    for t, block in by_token.items()
                }
                best = direction(vals.values())
                agrees = vals[pick] == best and list(vals.values()).count(best) == 1
                row[f"{key}_agree"] = agrees
                hidden_agree[key] += agrees
            rows.append(row)

    result = {
        "readable_rows": readable,
        "excluded_rows": len(rows) - readable,
        "tag_score_agreement": tag_agree,
        "recomputed_bars": hidden_agree,
        "verdict": (
            "BAR CLEARED -- promoted to 'worth a pre-registered real test', nothing more"
            if tag_agree > max(hidden_agree["adamic_adar"], hidden_agree["overlap_coeff"])
            else "BAR NOT CLEARED -- the §3.8 hardening stands; this line stops"
        ),
        "rows": rows,
    }
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")

    print(f"readable rows: {readable} of {len(rows)}")
    print(f"tag path score agreement: {tag_agree}/{readable}")
    for key, _ in HIDDEN:
        print(f"  {key} (recomputed, same counting): {hidden_agree[key]}/{readable}")
    print(f"\n{result['verdict']}")
    print(f"-> {OUT.name}")


if __name__ == "__main__":
    main()
