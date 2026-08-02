"""`FAM-6` tail-ordering sample: the draw, and the owner's blind checklist.

Governing document:
  docs/superpowers/specs/2026-08-02-fame-instrument-adoption-preregistration.md
  §8 `FAM-AM3` (the criterion) and `FAM-AM1`.4a (identity confirmed before any
  listener figure is read) and `FAM-AM1`.6 (the percentile, exactly).

WHAT THIS IS. `FAM-6` asks whether the ruler orders the OBSCURE QUARTER the way
a hand read of Spotify does. It is a WGLL instrument, so all three of that
document's bounds are honoured here mechanically rather than by care:

  bound 1 -- the draw is fixed by seed BEFORE anyone looks at it, and this
             script is the committed procedure, so the sample cannot be
             reselected after a disappointing read;
  bound 2 -- identity is confirmed against the MusicBrainz disambiguation
             BEFORE any listener figure is read (the `BYP-13` guard: the hand
             reads are Spotify NAME lookups, and a name lookup on a renamed or
             colliding artist silently returns a different entity, failing
             TOWARD a spurious discovery);
  bound 3 -- the owner's reads are written down in full before any comparison
             exists, and the comparison is computed by script, not by eye.

BLINDNESS IS ENFORCED BY WHAT THIS SCRIPT WRITES, NOT BY INTENTION
  Two outputs, deliberately asymmetric:

  `fi_tail_sample.json`  -- the machine record. Carries the stratum, so the
                            draw is auditable and reproducible. Carries NO
                            `fame_lb_raw` and NO `fame_lb_pctl` for any artist:
                            the sample file is read by whoever prepares the
                            comparison, and a value here would put the answer
                            in front of the person assembling the question.

  `fi_tail_checklist.md` -- the OWNER-FACING sheet. Carries no ruler value, no
                            percentile, and NO STRATUM. The stratum IS a
                            percentile band, so printing "stratum 1 / 2 / 3"
                            would rank the sheet for him in the exact currency
                            the test is meant to check independently. The
                            replacement rule in `FAM-AM3` ("the next alternate
                            in its stratum") still has to work on paper, so
                            each row carries an OPAQUE GROUP LETTER whose
                            mapping to the strata is a seeded permutation held
                            only in the JSON. Three unordered labels carry the
                            grouping without carrying the order.

THE DRAW, EXACTLY
  Population: the DELIVERABLE union (the 93,067-MBID union minus the two frozen
  sha-pinned drop lists, per `FAM-AM2`.1) restricted to non-null values with
  `fame_lb_pctl < 0.25`. Strata are the percentile bands (0, 1/12], (1/12, 1/6],
  (1/6, 1/4) -- the last is open at 0.25 because the POPULATION rule is
  `< 0.25`, and where the two phrasings disagree the population rule governs.
  Each stratum's members are MBID-SORTED before sampling, so the draw depends
  on the seed and nothing else -- not on dict order, not on artifact node order.
  Seed 20260802, fixed in `FAM-AM3`.

  15 primaries (5 per stratum) + 10 ordered alternates, drawn 4/3/3 and
  interleaved round-robin so the alternate ORDER is stratum-balanced while each
  stratum's own subsequence stays in draw order -- which is what the
  replacement rule consumes.

Run from `builder/` (no network):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/fi_tail_sample.py
"""

from __future__ import annotations

import json
import random
import urllib.parse
from pathlib import Path

import numpy as np

# Frame is the `FAM-AM1`.6 percentile machinery, imported rather than copied so
# the sample and the validation figures cannot drift apart. sha256_file comes
# with it; importing fi_stats runs no computation (everything is under main()).
from fi_stats import (  # noqa: E402
    CANDIDATE,
    CANDIDATE_SHA,
    NEW_SNAPSHOT,
    Frame,
    sha256_file,
)

from artistpath_builder.artifact import deserialise  # noqa: E402

HERE = Path(__file__).parent
ANALYSIS = HERE.parent

ADOPTED = ANALYSIS.parent / "scratch" / "graph-t15-tiebreakfix.bin"
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

SNAPSHOT_SHA = "d9d6d5d340a81875dd795067d6332a40d813ebfb5b8258048290c27f34662ae8"

# The two frozen drop lists. Sha-pinned for the same reason the artifacts are:
# `FAM-AM2`.1 inherits them as frozen, and a re-census re-opens that read.
DROP_LISTS = (
    ("tail_droplist", ANALYSIS / "2026-08-01-label-weighting" / "tail_droplist.json",
     7_035),
    ("ctc_droplist", ANALYSIS / "2026-08-02-candidate-tail-census" / "ctc_droplist.json",
     9_501),
)

DEEZER_IDS = ANALYSIS / "2026-08-02-dsp-ids" / "dsp_ids.json"

SEED = 20260802
PRIMARIES_PER_STRATUM = 5
ALTERNATES_PER_STRATUM = (4, 3, 3)  # 10 total, round-robin interleaved

STRATA = (
    (1, 0.0, 1.0 / 12.0),
    (2, 1.0 / 12.0, 1.0 / 6.0),
    (3, 1.0 / 6.0, 0.25),
)

OUT_JSON = HERE / "fi_tail_sample.json"
OUT_MD = HERE / "fi_tail_checklist.md"


def stratum_of(p: float) -> int | None:
    """Half-open on the left, closed on the right -- (lo, hi]. Stratum 3 is
    open at 0.25 because the population rule is `fame_lb_pctl < 0.25`."""
    for k, lo, hi in STRATA:
        if lo < p <= hi and p < 0.25:
            return k
    return None


def main() -> None:
    if sha256_file(ADOPTED) != ADOPTED_SHA:
        raise SystemExit("adopted artifact sha256 mismatch -- refusing to draw")
    if sha256_file(CANDIDATE) != CANDIDATE_SHA:
        raise SystemExit("ALG-B candidate artifact sha256 mismatch -- refusing to draw")
    if sha256_file(NEW_SNAPSHOT) != SNAPSHOT_SHA:
        raise SystemExit("union snapshot sha256 mismatch -- refusing to draw")

    snapshot = json.loads(NEW_SNAPSHOT.read_text(encoding="utf-8"))

    adopted = deserialise(ADOPTED.read_bytes())
    candidate = deserialise(CANDIDATE.read_bytes())
    adopted_set = set(adopted.mbids)
    candidate_set = set(candidate.mbids)
    union = adopted_set | candidate_set

    # Name/disambiguation come from whichever artifact holds the artist; the
    # adopted one wins where both do, because it is the shipped identity.
    meta: dict[str, tuple[str, str]] = {}
    for g in (candidate, adopted):
        for i, m in enumerate(g.mbids):
            meta[m] = (g.names[i], g.disambiguations[i])

    dropped: set[str] = set()
    for label, path, expected in DROP_LISTS:
        payload = json.loads(path.read_text(encoding="utf-8"))
        mbids = payload["drop_mbids"]
        if len(mbids) != expected:
            raise SystemExit(f"{label}: {len(mbids)} drop_mbids, expected {expected}")
        dropped |= set(mbids)
        print(f"{label}: {len(mbids):,} drop_mbids", flush=True)

    deliverable = union - dropped
    print(f"union {len(union):,}  dropped(union of both lists) {len(union & dropped):,}"
          f"  deliverable {len(deliverable):,}", flush=True)

    # The frame: the ADOPTED artifact's non-null values, `FAM-AM1`.6. Note the
    # frame is NOT the deliverable set -- the percentile's frame is fixed by §1
    # and changing it would be an amendment, never a side effect of this draw.
    frame_values = [snapshot[m] for m in sorted(adopted_set)
                    if snapshot.get(m) is not None]
    frame = Frame(np.array(frame_values, dtype=np.int64))
    print(f"frame: {frame.n:,} non-null adopted values", flush=True)

    by_stratum: dict[int, list[str]] = {k: [] for k, _, _ in STRATA}
    non_null_deliverable = 0
    for m in sorted(deliverable):
        v = snapshot.get(m)
        if v is None:
            continue
        non_null_deliverable += 1
        p = float(frame.pctl([v])[0])
        k = stratum_of(p)
        if k is not None:
            by_stratum[k].append(m)

    for k, lo, hi in STRATA:
        print(f"stratum {k} ({lo:.5f}, {hi:.5f}]: {len(by_stratum[k]):,} artists",
              flush=True)
    population = sum(len(v) for v in by_stratum.values())
    print(f"population (deliverable, non-null, pctl < 0.25): {population:,}"
          f"  of {non_null_deliverable:,} non-null deliverable", flush=True)

    rng = random.Random(SEED)
    primaries: list[tuple[int, str]] = []
    alternates_by_stratum: dict[int, list[str]] = {}
    for idx, (k, _, _) in enumerate(STRATA):
        members = by_stratum[k]  # already MBID-sorted
        want = PRIMARIES_PER_STRATUM + ALTERNATES_PER_STRATUM[idx]
        if len(members) < want:
            raise SystemExit(f"stratum {k} holds {len(members)} < {want} artists")
        drawn = rng.sample(members, want)
        primaries.extend((k, m) for m in drawn[:PRIMARIES_PER_STRATUM])
        alternates_by_stratum[k] = drawn[PRIMARIES_PER_STRATUM:]

    # Round-robin the alternates: stratum-balanced overall order, each
    # stratum's own subsequence still in draw order.
    alternates: list[tuple[int, str]] = []
    for r in range(max(ALTERNATES_PER_STRATUM)):
        for k, _, _ in STRATA:
            if r < len(alternates_by_stratum[k]):
                alternates.append((k, alternates_by_stratum[k][r]))

    # Opaque group letters for the owner-facing sheet: a seeded permutation, so
    # the sheet carries the GROUPING (which the replacement rule needs) without
    # carrying the ORDER (which is the answer).
    letters = ["P", "Q", "R"]
    rng.shuffle(letters)
    group_of = {k: letters[i] for i, (k, _, _) in enumerate(STRATA)}

    # Presentation order of the primaries is shuffled too, so the sheet's own
    # row order does not reconstruct the strata.
    present = list(range(len(primaries)))
    rng.shuffle(present)

    deezer = json.loads(DEEZER_IDS.read_text(encoding="utf-8"))["deezer_ids"]

    def row(k: int, m: str, role: str, order: int) -> dict:
        name, disamb = meta[m]
        if m in adopted_set and m in candidate_set:
            source = "both"
        elif m in adopted_set:
            source = "adopted"
        else:
            source = "ALG-B-only"
        return {
            "mbid": m,
            "name": name,
            "disambiguation": disamb or None,
            "stratum": k,
            "role": role,
            "order": order,
            "group_letter": group_of[k],
            "deezer_artist_id": deezer.get(m),
            "source_population": source,
            "musicbrainz_url": f"https://musicbrainz.org/artist/{m}",
            "spotify_search_url":
                "https://open.spotify.com/search/"
                + urllib.parse.quote(name, safe="") + "/artists",
        }

    rows = [row(k, m, "primary", i + 1) for i, (k, m) in enumerate(primaries)]
    rows += [row(k, m, "alternate", i + 1) for i, (k, m) in enumerate(alternates)]

    OUT_JSON.write_text(json.dumps({
        "governing_document":
            "docs/superpowers/specs/"
            "2026-08-02-fame-instrument-adoption-preregistration.md",
        "criterion": "FAM-6 (FAM-AM3) -- tail-ordering concordance",
        "carries_no_ruler_value":
            "By design: no fame_lb_raw and no fame_lb_pctl appears in this file "
            "or in fi_tail_checklist.md. The stratum is here (the draw must be "
            "auditable) and deliberately NOT on the owner's sheet, where it "
            "would rank the rows in the very currency under test.",
        "seed": SEED,
        "draw_procedure":
            "MBID-sorted members per stratum; random.Random(20260802); strata "
            "sampled in order 1,2,3 with 9/8/8 drawn each (5 primaries then "
            "4/3/3 alternates); alternates interleaved round-robin; then the "
            "group letters permuted and the primary presentation order "
            "shuffled from the same RNG. Reproducible by re-running this file.",
        "population_definition":
            "deliverable union (93,067-MBID union minus tail_droplist and "
            "ctc_droplist, FAM-AM2.1) with a non-null fame_lb_raw and "
            "fame_lb_pctl < 0.25, percentile per FAM-AM1.6 over the adopted "
            "frame's non-nulls",
        "counts": {
            "union": len(union),
            "dropped_from_union": len(union & dropped),
            "deliverable": len(deliverable),
            "deliverable_non_null": non_null_deliverable,
            "frame_non_null": frame.n,
            "population_pctl_lt_0.25": population,
            "per_stratum": {str(k): len(by_stratum[k]) for k, _, _ in STRATA},
        },
        "strata_definition": {
            str(k): f"({lo!r}, {hi!r}]" for k, lo, hi in STRATA
        },
        "group_letter_map_NOT_FOR_THE_CHECKLIST":
            {str(k): group_of[k] for k, _, _ in STRATA},
        "substrate": {
            "snapshot": {"file": NEW_SNAPSHOT.name, "sha256": SNAPSHOT_SHA},
            "adopted": {"file": ADOPTED.name, "sha256": ADOPTED_SHA},
            "candidate_alg_b": {"file": CANDIDATE.name, "sha256": CANDIDATE_SHA},
            "drop_lists": [str(p.relative_to(ANALYSIS)) for _, p, _ in DROP_LISTS],
        },
        "sample": rows,
    }, indent=1, ensure_ascii=False), encoding="utf-8")

    # ---------------- the owner-facing sheet ----------------
    prim = [r for r in rows if r["role"] == "primary"]
    alts = [r for r in rows if r["role"] == "alternate"]

    def block(n: str, r: dict) -> list[str]:
        lines = [
            f"### {n}. {r['name']}",
            "",
            f"- **MusicBrainz says:** {r['disambiguation'] or '*none recorded*'}",
            f"- **MusicBrainz page:** {r['musicbrainz_url']}",
            f"- **Spotify search:** {r['spotify_search_url']}",
        ]
        if r["deezer_artist_id"]:
            lines.append(
                "- **Deezer page** (same artist, recorded in MusicBrainz — useful "
                "if the Spotify search is ambiguous): "
                f"https://www.deezer.com/artist/{r['deezer_artist_id']}")
        lines += [
            f"- **Group:** {r['group_letter']}",
            "",
            "**monthly listeners:** ______________________",
            "",
            "- [ ] could not confirm identity",
            "- [ ] no Spotify page",
            "",
        ]
        return lines

    md = [
        "# Fifteen artists to look up by hand",
        "",
        "Fifteen artists, drawn at random by a script before anyone looked at "
        "them. For each one: **find the artist on Spotify and write down the "
        "monthly listeners.**",
        "",
        "**Nothing on this sheet tells you anything about these artists.** No "
        "scores, no rankings, no counts of ours — that is the whole point. Our "
        "number for each of them already exists and is deliberately not here, "
        "so that what you write down cannot be nudged by it.",
        "",
        "## How to do a row",
        "",
        "1. **Check who it is before you read any number.** Open the "
        "MusicBrainz link and the Spotify search. Does the Spotify artist page "
        "match — the description above, the albums, the era, the country? "
        "Artists share names, and a Spotify name search will happily hand you a "
        "completely different act. (This has already burned us once: a card "
        "reading *FERG* played music by an unrelated artist of the same name, "
        "and a hand read went into the record as a discovery it was not.)",
        "2. **Only once you are satisfied it is the same artist, read the "
        "monthly listeners and write the number down.**",
        "3. **Write a number for every row you confirm** — including the ones "
        "that look tiny or that you have never heard of. A row left blank is a "
        "row we lose.",
        "4. If you **cannot tell whether it is the same artist**, tick *could "
        "not confirm identity* and leave the number blank. If the artist has "
        "**no Spotify page at all**, tick *no Spotify page*.",
        "",
        "## Replacements",
        "",
        "**Do the fifteen numbered rows first.** Only if one of them fails "
        "(either box ticked) do you replace it: go to the *Replacements* "
        "section at the bottom and take the **first unused replacement carrying "
        "the same group letter** as the row that failed.",
        "",
        "The group letters **P**, **Q** and **R** are arbitrary labels. They "
        "exist only so a replacement is drawn from the same place the failed "
        "row was, and they say nothing about the artists.",
        "",
        "---",
        "",
        "## The fifteen",
        "",
    ]
    for n, i in enumerate(present, 1):
        md += block(str(n), prim[i])

    md += [
        "---",
        "",
        "## Replacements — only if a numbered row above failed",
        "",
        "Use these **in the order listed**, matching the group letter of the "
        "row you are replacing. Note which numbered row each one stands in for.",
        "",
    ]
    for n, r in enumerate(alts, 1):
        md += block(f"R{n}", r)

    md += [
        "---",
        "",
        "*Drawn by `builder/analysis/2026-08-02-fame-instrument/fi_tail_sample.py`, "
        "seed 20260802, committed before the draw was looked at.*",
        "",
    ]
    OUT_MD.write_text("\n".join(md), encoding="utf-8")

    print(f"\nwrote {OUT_JSON.name} ({len(rows)} rows: {len(prim)} primary, "
          f"{len(alts)} alternate) and {OUT_MD.name}")


if __name__ == "__main__":
    main()
