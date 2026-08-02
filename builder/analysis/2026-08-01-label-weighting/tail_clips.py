"""Does anything actually PLAY for the no-release tail's DSP-linked artists?

DIAGNOSTIC ONLY. Not pre-registered, no bar, licenses nothing, adopts nothing.
Same standing as `tail_sample.py`, `tail_exposure.py` and `tail_signals.py`.

SCOPE, AND WHY IT IS THE 1,402 AND NOT THE 7,686
  The candidate rule the owner is weighing keeps a no-release artist only where
  there is BOTH a commercial-DSP link AND something that plays. An artist with
  no DSP link is cut whatever the clip says, so clip-checking all 7,686 would
  spend hours to answer nothing. Restricting to the 1,402 DSP-linked artists
  makes the run ~20 min AND confines the name-matching hazard below to a fifth
  of the population.

TWO PATHS PER ARTIST, AND THE SECOND IS THE INSTRUMENT CHECK ON THE FIRST
  1. NAME path -- exactly what the app does today: Deezer search, then iTunes,
     accepted only on `same_artist` (imported from the app, never restated).
     This answers "would a card play something", which is the product question.
  2. ID path -- for the 355 artists where MusicBrainz gives a Deezer artist ID,
     ask THAT artist directly for a top track. No name matching anywhere.

  Comparing them measures the hazard the owner flagged rather than warning
  about it. `BYP-13` is a LIVE known defect on this project: a card playing a
  clip by a DIFFERENT ARTIST OF THE SAME NAME. Where the name path resolves but
  lands on a Deezer artist id other than the one MusicBrainz recorded, that is a
  measured instance. That rate is the error bar on every name-resolved figure
  here, and on `tail_sample.json`'s 7-of-20 as well.

REFUSAL IS NOT ABSENCE -- the one distinction this file must not lose
  A 429 or an outage means "we do not know", never "nothing plays" (the G3-A4
  lesson, recorded in `clips.py`). Refusals are counted in their own bucket and
  excluded from every denominator; a run with many refusals is reported as
  incomplete rather than as a low resolution rate.

RESUMABLE
  ~1,750 network calls. A checkpoint is written every 25 artists and the run
  resumes from it, so a dropped connection costs a minute rather than the pass.
"""
from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from hashlib import sha256
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
_TAS = HERE.parent / "2026-07-30-tag-discrimination"
for _p in (_TAS, ROOT / "api" / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from artistpath_api.clips import same_artist  # noqa: E402
from tas_common import ADOPTED, ADOPTED_SHA  # noqa: E402

SIGNALS = HERE / "tail_signals.json"
OUT = HERE / "tail_clips.json"
CKPT = HERE / "tail_clips.checkpoint.json"
CKPT_SCHEMA = 1
CKPT_EVERY = 25

DEEZER_SEARCH = "https://api.deezer.com/search?%s"
DEEZER_ARTIST_TOP = "https://api.deezer.com/artist/%s/top?limit=1"
ITUNES_SEARCH = "https://itunes.apple.com/search?%s"

PAUSE_DEEZER = 0.30
PAUSE_ITUNES = 0.70
BACKOFF = 20.0
UA = "artistpath-tail-clips/1.0 (+research diagnostic; contact via repo owner)"


class Refused(Exception):
    """The service declined to answer. NOT a miss -- see the module docstring."""


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
    if isinstance(err, dict) and "Quota" in str(err.get("type", "")) + str(err.get("message", "")):
        raise Refused(f"deezer quota: {err}")


def name_path(name: str) -> dict:
    """The app's own resolution order and name rule. Refusals propagate."""
    out: dict = {"resolves": False, "source": None, "matched_artist_id": None,
                 "matched_artist_name": None, "refused": []}
    try:
        body = get_json(DEEZER_SEARCH % urllib.parse.urlencode({"q": name, "limit": 5}))
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
    except Exception as e:  # noqa: BLE001 -- a diagnostic records, never raises
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
    """Ask the MusicBrainz-linked Deezer artist directly. No name matching."""
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
    if sha256(ADOPTED.read_bytes()).hexdigest() != ADOPTED_SHA:
        raise SystemExit("artifact mismatch")
    if not SIGNALS.exists():
        raise SystemExit(f"run tail_signals.py first -- {SIGNALS} missing")
    detail = json.loads(SIGNALS.read_text(encoding="utf-8"))["tail_detail"]

    targets = {m: v for m, v in detail.items() if v.get("dsp")}
    print(f"DSP-linked no-release artists to check: {len(targets)}", flush=True)

    done: dict = {}
    if CKPT.exists():
        ck = json.loads(CKPT.read_text(encoding="utf-8"))
        if ck.get("schema") == CKPT_SCHEMA:
            done = ck.get("done", {})
            print(f"resuming: {len(done)} already done", flush=True)
        else:
            print("checkpoint schema mismatch -- starting clean", flush=True)

    def save_ckpt() -> None:
        CKPT.write_text(json.dumps({"schema": CKPT_SCHEMA, "done": done}),
                        encoding="utf-8")

    pending = [m for m in sorted(targets) if m not in done]
    for n, mbid in enumerate(pending, 1):
        v = targets[mbid]
        rec = {"name": v["name"], "dsp": v["dsp"]}
        rec["name_path"] = name_path(v["name"])
        time.sleep(PAUSE_DEEZER)
        dz = (v.get("ids") or {}).get("deezer")
        if dz:
            rec["id_path"] = id_path(dz)
            rec["mb_deezer_id"] = str(dz)
            time.sleep(PAUSE_DEEZER)
        done[mbid] = rec
        if n % CKPT_EVERY == 0:
            save_ckpt()
            print(f"  {n}/{len(pending)} ({len(done)} total)", flush=True)
    save_ckpt()

    c: Counter = Counter()
    for rec in done.values():
        npth = rec["name_path"]
        if npth["refused"]:
            c["name_refused"] += 1
        elif npth["resolves"]:
            c["name_resolves"] += 1
            c[f"name_via_{npth['source']}"] += 1
        else:
            c["name_no_clip"] += 1
        ip = rec.get("id_path")
        if ip is not None:
            if ip.get("refused"):
                c["id_refused"] += 1
            elif ip["resolves"]:
                c["id_resolves"] += 1
            else:
                c["id_no_clip"] += 1
            # the BYP-13 measurement: both paths answered, name path landed on
            # a Deezer artist other than the one MusicBrainz recorded
            if (not ip.get("refused") and not npth["refused"]
                    and npth["resolves"] and npth["source"] == "deezer"):
                c["comparable"] += 1
                if npth["matched_artist_id"] and rec.get("mb_deezer_id"):
                    if npth["matched_artist_id"] != rec["mb_deezer_id"]:
                        c["name_matched_WRONG_artist"] += 1
                    else:
                        c["name_matched_right_artist"] += 1

    denom = c["name_resolves"] + c["name_no_clip"]
    result = {
        "scope": ("DIAGNOSTIC ONLY -- not pre-registered, no bar, licenses "
                  "nothing. Restricted to the DSP-linked subset of the "
                  "no-release tail; see the module docstring for why."),
        "substrate": {"file": ADOPTED.name, "sha256": ADOPTED_SHA},
        "checked": len(done),
        "counts": dict(c),
        "name_resolution_rate_excluding_refusals": (
            round(c["name_resolves"] / denom, 4) if denom else None),
        "byp13_wrong_artist_rate": (
            round(c["name_matched_WRONG_artist"] / c["comparable"], 4)
            if c["comparable"] else None),
        "reading_notes": [
            "Refusals are excluded from denominators. A refusal means 'we do "
            "not know', never 'nothing plays' (G3-A4).",
            "byp13_wrong_artist_rate is measured ONLY where MusicBrainz gave a "
            "Deezer artist id AND the name path resolved via Deezer, so it is "
            "a rate over a subset and carries that subset's bias.",
            "A clip resolving does NOT make an artist journey-worthy: the "
            "owner rejected 5 of the 7 clip-resolving artists in his sample.",
        ],
        "per_artist": done,
    }
    OUT.write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
    print("\ncounts:", json.dumps(dict(c), indent=1))
    print("wrote", OUT)
    if not c["name_refused"] and not c["id_refused"]:
        CKPT.unlink(missing_ok=True)
        print("checkpoint removed (clean run)")
    else:
        print("⚠ refusals present -- checkpoint RETAINED; re-run to fill them in")


if __name__ == "__main__":
    main()
