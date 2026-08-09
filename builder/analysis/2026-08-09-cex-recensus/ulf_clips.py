"""CEX- re-census, network half: the keep-check over the fresh class members.

FORWARD COPY of `../2026-08-05-ulf-census/ulf_clips.py`, run for plan Task 11
Step 3 over the extended 117,302-artist ALG-B archive. BYTE-IDENTICAL to the
original below this block: `WORKLIST`, `OUT` and `CKPT` are all `HERE`-relative,
so copying the file is the whole of the retargeting and no logic changed.

Copied rather than re-run in place because the original is a FROZEN record: it
would read the stale 2026-08-05 worklist and overwrite its own committed
`ulf_clips.json`, which is the evidence the 2026-08-05 verdicts rest on.

Worklist for this run: 5,684 artists (`ulf_census.json` here owns the funnel).

The criterion is the ADOPTED instrument, verbatim (ULF-2): keep iff a
commercial-DSP link exists (already screened by ulf_census.py — everything on
the worklist has one) AND the app's own Deezer→iTunes resolution resolves a
clip by the artist's name, accepted only on `same_artist` (imported from the
app, never restated). tail_clips.py is the reference implementation; the
resolution functions here are ported from it unchanged.

ONE ADDITION, instrument data and never a criterion (ULF-2): where the MB
record carries a Deezer artist id, the id path runs too and both outcomes are
recorded. The name-only path is the `BYP-13` exposure — for this class a
false rescue is the failure mode — and this field is the deferred `ULC-F4`
track's measurement, collected for free. No read of it is licensed here.

REFUSALS ARE NOT EVIDENCE (ULF-4, inheriting FCF-3): an artist whose lookup
the service refused is not dropped on that refusal. The checkpoint keeps
every refused artist pending; re-run until none remain. The lists freeze only
when every worklist member's outcome is a real answer.

Resumable: ~25 artists per checkpoint write. Expect hours, not minutes; run
with `python -u` (stdout buffers when redirected — three subagents have lost
time to a 0-byte log on a live job).

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-05-ulf-census/ulf_clips.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
for _p in (str(ROOT / "api" / "src"),):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from artistpath_api.clips import same_artist  # noqa: E402

WORKLIST = HERE / "ulf_worklist.json"
OUT = HERE / "ulf_clips.json"
CKPT = HERE / "ulf_clips.checkpoint.json"
CKPT_SCHEMA = 1
CKPT_EVERY = 25

DEEZER_SEARCH = "https://api.deezer.com/search?%s"
DEEZER_ARTIST_TOP = "https://api.deezer.com/artist/%s/top?limit=1"
ITUNES_SEARCH = "https://itunes.apple.com/search?%s"

PAUSE_DEEZER = 0.30
PAUSE_ITUNES = 0.70
BACKOFF = 20.0
UA = "artistpath-ulf-clips/1.0 (+research diagnostic; contact via repo owner)"


class Refused(Exception):
    """The service declined to answer. NOT a miss — see the module docstring."""


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code in (403, 429, 503):
            raise Refused(f"HTTP {e.code}") from e
        raise


def _deezer_quota(body: dict) -> None:
    """Deezer returns 200 with an error envelope when it throttles."""
    err = body.get("error")
    if isinstance(err, dict) and "Quota" in str(err.get("type", "")) + str(
        err.get("message", "")
    ):
        raise Refused(f"deezer quota: {err}")


def name_path(name: str) -> dict:
    """The app's own resolution order and name rule. Refusals propagate."""
    out: dict = {"resolves": False, "source": None, "matched_artist_id": None,
                 "matched_artist_name": None, "refused": []}
    try:
        body = get_json(DEEZER_SEARCH % urllib.parse.urlencode(
            {"q": name, "limit": 5}))
        _deezer_quota(body)
        for row in body.get("data", []):
            artist = row.get("artist") or {}
            if row.get("preview") and same_artist(artist.get("name"), name):
                out.update(resolves=True, source="deezer",
                           matched_artist_id=str(artist.get("id") or ""),
                           matched_artist_name=artist.get("name"),
                           track=str(row.get("title") or ""))
                return out
    except Refused as e:
        out["refused"].append(f"deezer: {e}")
        time.sleep(BACKOFF)
    except Exception as e:  # noqa: BLE001 — a diagnostic records, never raises
        out["refused"].append(f"deezer-error: {type(e).__name__}")

    time.sleep(PAUSE_ITUNES)
    try:
        body = get_json(ITUNES_SEARCH % urllib.parse.urlencode(
            {"term": name, "entity": "song", "limit": 5}))
        for row in body.get("results", []):
            if row.get("previewUrl") and same_artist(row.get("artistName"), name):
                out.update(resolves=True, source="itunes",
                           matched_artist_name=row.get("artistName"),
                           track=str(row.get("trackName") or ""))
                return out
    except Refused as e:
        out["refused"].append(f"itunes: {e}")
        time.sleep(BACKOFF)
    except Exception as e:  # noqa: BLE001
        out["refused"].append(f"itunes-error: {type(e).__name__}")
    return out


def id_path(deezer_id: str) -> dict:
    """Ask the MB-linked Deezer artist directly. No name matching."""
    out: dict = {"resolves": False, "refused": None}
    try:
        body = get_json(DEEZER_ARTIST_TOP % urllib.parse.quote(deezer_id))
        _deezer_quota(body)
        for row in body.get("data", []):
            if row.get("preview"):
                out.update(resolves=True, track=str(row.get("title") or ""))
                return out
    except Refused as e:
        out["refused"] = str(e)
        time.sleep(BACKOFF)
    except Exception as e:  # noqa: BLE001
        out["refused"] = f"error: {type(e).__name__}"
    return out


def main() -> None:
    work = json.loads(WORKLIST.read_text(encoding="utf-8"))["worklist"]
    done: dict[str, dict] = {}
    if CKPT.exists():
        ckpt = json.loads(CKPT.read_text(encoding="utf-8"))
        if ckpt.get("schema") != CKPT_SCHEMA:
            raise SystemExit("checkpoint schema mismatch — delete it only if "
                             "you know why it changed")
        done = ckpt["done"]
        log_prefix = f"resumed with {len(done):,} done; "
    else:
        log_prefix = ""
    print(f"[{time.strftime('%H:%M:%S')}] {log_prefix}"
          f"{len(work):,} on the worklist", flush=True)

    def save() -> None:
        CKPT.write_text(json.dumps(
            {"schema": CKPT_SCHEMA, "done": done}), encoding="utf-8")

    pending_refusals = 0
    for i, item in enumerate(work):
        mbid = item["mbid"]
        rec = done.get(mbid)
        if rec is not None and not rec["name_path"]["refused"]:
            continue  # a real answer; refused ones re-run (ULF-4)
        rec = {"name": item["name"], "deezer": item.get("deezer")}
        time.sleep(PAUSE_DEEZER)
        rec["name_path"] = name_path(item["name"])
        if item.get("deezer"):
            time.sleep(PAUSE_DEEZER)
            rec["id_path"] = id_path(item["deezer"])
        done[mbid] = rec
        if rec["name_path"]["refused"]:
            pending_refusals += 1
        if (i + 1) % CKPT_EVERY == 0:
            save()
            print(f"[{time.strftime('%H:%M:%S')}] {i + 1:,}/{len(work):,} "
                  f"({sum(1 for r in done.values() if r['name_path']['resolves']):,} "
                  f"resolve; {pending_refusals} refusals pending)", flush=True)
    save()

    refused = [m for m, r in done.items() if r["name_path"]["refused"]]
    if refused:
        print(f"\n{len(refused):,} refusals remain — NOT misses (ULF-4). "
              "Re-run this script until none remain; the checkpoint keeps "
              "them pending.", flush=True)
        return

    OUT.write_text(json.dumps({
        "status": ("ULF- keep-check capture, complete — every worklist "
                   "member's outcome is a real answer (ULF-4 satisfied). "
                   "The criterion is name_path.resolves; id_path is "
                   "instrument data for ULC-F4, no read licensed here."),
        "resolved": sum(1 for r in done.values() if r["name_path"]["resolves"]),
        "of": len(done),
        "artists": done,
    }, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {OUT.name}: "
          f"{sum(1 for r in done.values() if r['name_path']['resolves']):,} "
          f"of {len(done):,} resolve", flush=True)


if __name__ == "__main__":
    main()
