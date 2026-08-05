"""Why did both drop filters pass the target class through? The Discogs half.

DIAGNOSTIC ONLY, and OUTSIDE the ULC- pre-registration: it fixes no criterion,
feeds no ULC- read, and adopts nothing. The pre-registration's gate (ULC-G1) is
already answered. This asks the separate question the census raised -- and the
one the owner raised at the card during the audit itself:

    Dallas Taylor, in his own note: "I don't see any releases for this artist.
    I'm surprised they weren't dropped by one of our filters."

WHAT THE CENSUS DID, read from the code rather than assumed
  ctc_census.main builds the tail as artists carrying NEITHER release signal:
      has_release_group(m)  -- >= 1 MB release group crediting them
      has_discogs_release(m) -- their MB-linked discogs artist id appears in
                                the <artists> element of >= 1 Discogs RELEASE
  Four of the six target artists have ZERO MB release groups (ulc_census.json)
  and none of the six is in the tail, so has_discogs_release must be true for
  them. ctc_census.pass_discogs tests PRESENCE IN <artists>, which is Discogs'
  main-artist credit -- it does NOT test that the release is theirs alone.

  The owner spot-checked John McVie and found no solo release groups or
  releases on Discogs. So whatever is exempting them is not a solo body of
  work. This probe names it.

WHY MASTERS FIRST (the owner's suggestion, 2026-08-05)
  discogs_20260801_masters.xml is 3.1 GiB against 61.6 GiB for the releases
  dump -- 20x cheaper. Masters are Discogs' release-group equivalent. The
  masters pass answers "what does Discogs think they released" cheaply; the
  releases pass is still run afterwards because it is what ctc_census actually
  read, and only it can explain that decision.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-unlistenable-class/ulc_discogs_gap.py
"""

from __future__ import annotations

import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent.parent.parent
SCRATCH = ROOT / "builder" / "scratch"

MB_ARTIST = SCRATCH / "mb-json-dumps" / "artist" / "mbdump" / "artist"
DISCOGS = SCRATCH / "discogs-data-dump"
MASTERS = DISCOGS / "discogs_20260801_masters.xml"
RELEASES = DISCOGS / "discogs_20260601_releases.xml"


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def discogs_ids(mbids: dict[str, str]) -> dict[str, dict]:
    """MB artist dump -> the discogs artist id each target links to."""
    out: dict[str, dict] = {}
    seen = 0
    with MB_ARTIST.open("r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            seen += 1
            if seen % 1_000_000 == 0:
                log(f"  artists scanned: {seen:,}")
            record = json.loads(line)
            mbid = record.get("id")
            if mbid not in mbids:
                continue
            did = None
            dsp = []
            for rel in (record.get("relations") or []):
                url = ((rel.get("url") or {}).get("resource") or "")
                if "discogs.com/artist/" in url:
                    did = url.rstrip("/").split("/")[-1].split("-")[0]
                if any(h in url for h in
                       ("spotify.com", "deezer.com", "music.apple.com", "tidal.com")):
                    dsp.append(url)
            out[mbid] = {"name": mbids[mbid], "discogs_id": did, "dsp_links": dsp}
    log(f"  artists scanned: {seen:,} (done)")
    return out


def scan(path: Path, tag: str, wanted: dict[str, str], label: str) -> dict[str, list]:
    """Discogs XML -> the entries crediting each wanted id in <artists>.

    Memory: clear the root as well as the element. Clearing the element alone
    leaves emptied shells attached and the tree still grows (ctc_census).
    """
    hits: dict[str, list] = {d: [] for d in wanted}
    seen = 0
    began = time.time()
    context = ET.iterparse(str(path), events=("start", "end"))
    _event, root = next(context)
    for event, elem in context:
        if event != "end" or elem.tag != tag:
            continue
        seen += 1
        node = elem.find("artists")
        if node is not None:
            credited = [(a.findtext("id"), a.findtext("name")) for a in node]
            ids = [c[0] for c in credited]
            for did in wanted:
                if did in ids:
                    hits[did].append({
                        "title": elem.findtext("title"),
                        "year": elem.findtext("year"),
                        "n_main_artists": len(ids),
                        "sole": len(ids) == 1,
                        "co_credited": [n for i, n in credited if i != did][:6],
                    })
        elem.clear()
        root.clear()
        if seen % 500_000 == 0:
            log(f"  {label}: {seen:,} scanned ({(time.time() - began) / 60:.1f} min)")
    log(f"  {label}: {seen:,} scanned (done, {(time.time() - began) / 60:.1f} min)")
    return hits


def summarise(hits: dict[str, list], ids: dict[str, dict], label: str) -> dict:
    out = {}
    by_did = {v["discogs_id"]: v["name"] for v in ids.values() if v["discogs_id"]}
    print(f"\n=== {label} ===", flush=True)
    for did, entries in hits.items():
        name = by_did.get(did, did)
        sole = [e for e in entries if e["sole"]]
        out[name] = {
            "discogs_id": did,
            "total": len(entries),
            "sole_credited": len(sole),
            "examples": entries[:5],
        }
        print(f"  {name:16} credited on {len(entries):>4} {label.lower()}, "
              f"of which SOLE-credited: {len(sole)}", flush=True)
        for e in entries[:3]:
            who = "SOLE" if e["sole"] else f"with {', '.join(e['co_credited'][:3])}"
            print(f"        {e['year'] or '????'}  {e['title']}  [{who}]", flush=True)
    return out


def main() -> None:
    validation = json.loads(
        (HERE / "ulc_validation.json").read_text(encoding="utf-8")
    )
    targets = {m: a["name"] for m, a in validation["ULC_V1"].items()}
    four_tet = "3bcff06f-675a-451f-9075-99e8657047e8"
    targets.pop(four_tet, None)  # ULC-AM4: not in the target class
    log(f"targets: {len(targets)} artists")

    log("step 1/3 -- MB artist dump for discogs ids")
    ids = discogs_ids(targets)
    for mbid, rec in ids.items():
        log(f"  {rec['name']:16} discogs_id={rec['discogs_id']} "
            f"dsp_links={len(rec['dsp_links'])}")

    wanted = {rec["discogs_id"]: rec["name"] for rec in ids.values()
              if rec["discogs_id"]}
    if not wanted:
        raise SystemExit("no discogs ids found -- nothing to scan")

    log(f"step 2/3 -- Discogs MASTERS ({MASTERS.stat().st_size / 2**30:.1f} GiB)")
    masters = summarise(scan(MASTERS, "master", wanted, "masters"), ids, "MASTERS")

    log(f"step 3/3 -- Discogs RELEASES ({RELEASES.stat().st_size / 2**30:.1f} GiB) "
        "-- what ctc_census actually read")
    releases = summarise(scan(RELEASES, "release", wanted, "releases"), ids, "RELEASES")

    payload = {
        "status": "diagnostic only -- outside the ULC- pre-registration, no criterion",
        "question": (
            "four of six target artists have zero MB release groups yet none is "
            "in the no-release tail; ctc_census.has_discogs_release must be true "
            "for them. What Discogs entry is doing that?"
        ),
        "artists": ids,
        "masters": masters,
        "releases_what_the_census_read": releases,
    }
    out = HERE / "ulc_discogs_gap.json"
    out.write_text(json.dumps(payload, indent=1, ensure_ascii=False), encoding="utf-8")
    log(f"wrote {out.name}")


if __name__ == "__main__":
    main()
