"""RCS §2 candidate D -- Deezer nb_fan over the 30-row corpus, two identity tiers.

TIER 1 (identity guaranteed by the id path)
  The Deezer artist id recorded in MusicBrainz, taken from
  ../2026-08-02-dsp-ids/dsp_ids.json. GET https://api.deezer.com/artist/{id}
  and read nb_fan off the artist object. Coverage of the corpus was disclosed
  in RCS §3 before any value was fetched: famous 15/15, tail 4/15.

TIER 2 (name-resolved, accepted only on corroborating evidence)
  Needed for the 11 tail artists with no recorded id -- without it D's tail
  region is unreadable before it starts, which is why RCS §2 fixes the
  acceptance procedure here rather than leaving it to be improvised against
  the results.

  The procedure, fixed and mechanical:
    1. MusicBrainz gives the truth side for this artist -- release-group
       titles, country, active years. No Deezer value is looked at first.
    2. Deezer search by name gives up to 5 candidates.
    3. A candidate is accepted ONLY if a normalised release title it carries
       (album or top track) also appears in the artist's MusicBrainz
       release-group titles. Era and country are recorded beside the match as
       context, never as the acceptance itself.
    4. Two candidates matching -> the one with more matched titles; a tie ->
       null (ambiguous). No candidate matching -> null. No MusicBrainz titles
       to match against -> null, because the corroboration cannot be run.

  Name similarity alone is never sufficient. Half this tail is generic-noun
  names ("Statue", "Acer", "DTX", "MISSIN"), which is precisely the population
  where a confident wrong match returns a plausible number and shows up as
  nothing at all.

NULLS AND ZEROS
  No page, or an unresolvable identity, -> null. A resolved page reporting
  nb_fan 0 is a VALUE (RCS §2), the same way a confirmed Spotify page with no
  listeners is a value on the hand side.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/rcs_deezer.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
_FP = HERE.parent / "2026-07-30-fame-proxy-coverage"
if str(_FP) not in sys.path:
    sys.path.insert(0, str(_FP))

from fp_common import USER_AGENT  # noqa: E402

CORPUS = HERE / "fi_corpus.json"
DSP_IDS = HERE.parent / "2026-08-02-dsp-ids" / "dsp_ids.json"
RAW_OUT = HERE / "rcs_deezer_raw.json"
VALUES_OUT = HERE / "rcs_deezer.json"

DEEZER = "https://api.deezer.com"
MB = "https://musicbrainz.org/ws/2"
PAUSE = 1.05  # both endpoints are unauthenticated and rate-limited: <= 1 req/s
SEARCH_CANDIDATES = 5

_NOISE = re.compile(
    r"\s*[\(\[][^)\]]*(remaster|deluxe|edition|version|mono|stereo|expanded|"
    r"anniversary|bonus|live|reissue|explicit|single|ep)[^)\]]*[\)\]]",
    re.I,
)


def norm_title(text: str) -> str:
    """Normalise a release title for comparison across two catalogues.

    Conservative on purpose: it removes formatting and edition furniture, not
    words. Stripping more would raise the false-accept rate, and a false accept
    here is invisible downstream.
    """
    s = unicodedata.normalize("NFKD", text or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = _NOISE.sub("", s.lower())
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return " ".join(s.split())


# Titles too generic to corroborate an identity on their own -- they are the
# artist's own name, or a single ubiquitous word. Excluded from evidence.
def useless_evidence(title: str, artist_name: str) -> bool:
    n = norm_title(title)
    return (not n) or n == norm_title(artist_name) or len(n) < 4 or " " not in n and len(n) < 7


def get_json(url: str, *, attempts: int = 4) -> dict | list | None:
    delay = 2.0
    for _ in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"gave up on {url}")


def deezer(path: str) -> dict | None:
    payload = get_json(f"{DEEZER}{path}")
    time.sleep(PAUSE)
    if isinstance(payload, dict) and "error" in payload and payload["error"]:
        return {"_error": payload["error"]}
    return payload


def mb(path: str) -> dict | None:
    payload = get_json(f"{MB}{path}")
    time.sleep(PAUSE)
    return payload


# --------------------------------------------------------------------------- tier 1

def tier1(deezer_id: str) -> tuple[dict | None, int | None, str | None]:
    page = deezer(f"/artist/{deezer_id}")
    if page is None or "_error" in (page or {}):
        return page, None, "deezer_page_missing_for_recorded_id"
    if "nb_fan" not in page:
        return page, None, "deezer_page_carries_no_nb_fan"
    return page, int(page["nb_fan"]), None


# --------------------------------------------------------------------------- tier 2

def mb_identity(mbid: str) -> dict:
    artist = mb(f"/artist/{mbid}?fmt=json") or {}
    groups = mb(f"/release-group?artist={mbid}&fmt=json&limit=100") or {}
    titles = [g["title"] for g in groups.get("release-groups", [])]
    life = artist.get("life-span") or {}
    return {
        "name": artist.get("name"),
        "country": artist.get("country"),
        "area": (artist.get("area") or {}).get("name"),
        "type": artist.get("type"),
        "begin": life.get("begin"),
        "end": life.get("end"),
        "release_group_titles": titles,
    }


def deezer_titles(artist_id: int) -> tuple[list[str], dict]:
    albums = deezer(f"/artist/{artist_id}/albums?limit=100") or {}
    top = deezer(f"/artist/{artist_id}/top?limit=50") or {}
    titles = [a["title"] for a in (albums.get("data") or [])]
    titles += [t["title"] for t in (top.get("data") or [])]
    return titles, {"albums": albums, "top": top}


def tier2(name: str, mbid: str) -> tuple[dict, int | None, str | None, str | None]:
    """Returns (raw, nb_fan, evidence string, null reason)."""
    identity = mb_identity(mbid)
    mb_norm = {norm_title(t): t for t in identity["release_group_titles"]
               if not useless_evidence(t, name)}

    search = deezer(f"/search/artist?q={urllib.parse.quote(name)}&limit={SEARCH_CANDIDATES}") or {}
    candidates = (search.get("data") or [])[:SEARCH_CANDIDATES]
    raw = {"musicbrainz": identity, "deezer_search": search, "candidates": {}}

    if not mb_norm:
        return raw, None, None, "no_musicbrainz_release_titles_to_corroborate_against"
    if not candidates:
        return raw, None, None, "deezer_search_returned_nothing"

    scored = []
    for cand in candidates:
        titles, blobs = deezer_titles(cand["id"])
        matched = sorted({mb_norm[n] for t in titles
                          if (n := norm_title(t)) in mb_norm})
        raw["candidates"][str(cand["id"])] = {
            "name": cand.get("name"), "nb_fan": cand.get("nb_fan"),
            "nb_album": cand.get("nb_album"), "link": cand.get("link"),
            "deezer_titles": titles, "matched_titles": matched, **blobs,
        }
        if matched:
            scored.append((len(matched), cand, matched))

    if not scored:
        return raw, None, None, "no_candidate_corroborated_by_a_shared_release_title"
    scored.sort(key=lambda s: -s[0])
    if len(scored) > 1 and scored[0][0] == scored[1][0]:
        return raw, None, None, "ambiguous: two Deezer candidates corroborate equally"

    _, cand, matched = scored[0]
    page = deezer(f"/artist/{cand['id']}")
    raw["accepted_artist_page"] = page
    if page is None or "_error" in (page or {}) or "nb_fan" not in page:
        return raw, None, None, "corroborated_candidate_has_no_readable_artist_page"

    era = " / ".join(x for x in [identity.get("country") or identity.get("area"),
                                 (identity.get("begin") or "")[:4]] if x)
    evidence = (f"Deezer id {cand['id']} \"{cand.get('name')}\" "
                f"(search rank {candidates.index(cand) + 1} of {len(candidates)}) shares "
                f"{len(matched)} release title(s) with MusicBrainz {mbid}: "
                f"{'; '.join(matched[:4])}"
                + (f" | MB context: {era}" if era else "")
                + f" | Deezer catalogue {page.get('nb_album')} albums")
    return raw, int(page["nb_fan"]), evidence, None


# --------------------------------------------------------------------------- main

def main() -> None:
    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["rows"]
    ids = json.loads(DSP_IDS.read_text(encoding="utf-8"))["deezer_ids"]

    rows, raw = [], {}
    for r in corpus:
        recorded = ids.get(r["mbid"])
        if recorded:
            page, value, reason = tier1(recorded)
            tier, evidence = 1, None
            raw[r["mbid"]] = {"name": r["name"], "tier": 1,
                              "recorded_deezer_id": recorded, "artist_page": page}
        else:
            blob, value, evidence, reason = tier2(r["name"], r["mbid"])
            tier = 2
            raw[r["mbid"]] = {"name": r["name"], "tier": 2, **blob}
        rows.append({
            "mbid": r["mbid"], "name": r["name"], "region": r["region"],
            "hand_value": r["hand_value"], "tier": tier,
            "deezer_id": recorded if tier == 1 else (
                None if value is None else raw[r["mbid"]]["accepted_artist_page"]["id"]),
            "D": value, "tier2_evidence": evidence, "null_reason": reason,
        })
        print(f"  {r['region']:6} T{tier} {r['name'][:32]:32} "
              f"{'null (' + str(reason) + ')' if value is None else value}", flush=True)
        RAW_OUT.write_text(json.dumps(raw, indent=1, ensure_ascii=False), encoding="utf-8")

    VALUES_OUT.write_text(json.dumps({
        "candidate": "D -- Deezer nb_fan",
        "governing_document":
            "docs/superpowers/specs/2026-08-02-ruler-candidate-shootout-preregistration.md",
        "tier_1": "artist id recorded in MusicBrainz (dsp_ids.json); identity by the id path",
        "tier_2": "Deezer search by name, accepted only on a shared normalised release "
                  "title with the MusicBrainz artist; era/country recorded as context",
        "null_rule": "no page or unresolvable identity -> null; nb_fan 0 on a resolved "
                     "page is a value",
        "non_null": {
            region: sum(1 for x in rows if x["region"] == region and x["D"] is not None)
            for region in ("famous", "tail")
        },
        "tier2_acceptances": [
            {"name": x["name"], "region": x["region"], "deezer_id": x["deezer_id"],
             "D": x["D"], "evidence": x["tier2_evidence"]}
            for x in rows if x["tier"] == 2 and x["D"] is not None
        ],
        "rows": rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    for region in ("famous", "tail"):
        got = sum(1 for x in rows if x["region"] == region and x["D"] is not None)
        t1 = sum(1 for x in rows if x["region"] == region and x["D"] is not None and x["tier"] == 1)
        print(f"{region}: {got}/15 non-null ({t1} tier-1, {got - t1} tier-2)")
    print(f"\n-> {RAW_OUT.name}, {VALUES_OUT.name}")


if __name__ == "__main__":
    main()
