"""Shared loading for the coherence tag probe (COH-).

SCOPE: a ONE-DAY FALSIFICATION PROBE, descriptive in the CS-P0 sense. It
fixes no criterion, adopts nothing, and changes no weight, default, or
document that defines "better". A pre-registration is owed before any
criterion is built on whatever survives.

THE ARGUMENT UNDER TEST (fame-proxy execution log §7)
  Phase 1 §3.8 hardened into "do not proxy coherence with a metric". The
  record supports something narrower: both failed metrics (Adamic-Adar,
  overlap coefficient) were co-neighbour counts on the similarity graph --
  they audited the thing they were derived from. No metric in an INDEPENDENT
  currency has ever been tried against the owner's ear, and his verbatim
  verdict notes (Phase 1 §3.9) are genre/era/scene judgments.

  Tag/genre data is that independent currency -- IF it covers the graph.
  §7's honest warning, measured here before anything is built: tag coverage
  may thin in exactly the obscure tail where the Wikipedia fame proxy is
  already blind (FPC-3: 27.4% EN-article coverage in the lower-half band).
  That would be the same failure mode twice, and it is the kill condition.

THE FAME FRAME IS IMPORTED, NOT COPIED
  Band membership must be identical to Track B's and the FPC probes' or
  nothing here is comparable with either. The import chain (fp_common ->
  cb_metrics) carries the adopted artifact's sha256 assertion with it.

GENRE NORMALISATION IS FROZEN HERE, ONCE
  Step 2's pre-registered scoring rule cites this function; it is defined
  before any coverage number exists and must not move afterwards. MusicBrainz
  says "hip hop", Wikidata's genre labels often end in " music" ("rock
  music"): casefold, hyphens/underscores to spaces, collapse whitespace,
  ASCII-fold diacritics, strip one trailing " music".
"""

from __future__ import annotations

import json
import sys
import time
import unicodedata
import urllib.request
import urllib.error
from pathlib import Path
from typing import Any

HERE = Path(__file__).parent
_FPC = HERE.parent / "2026-07-30-fame-proxy-coverage"
if str(_FPC) not in sys.path:
    sys.path.insert(0, str(_FPC))

from fp_common import (  # noqa: E402,F401
    USER_AGENT,
    BAND_ORDER,
    graph_mbids,
    load_partial,
    post_json,
    run_batches,
    save_partial,
)
from cb_metrics import ADOPTED, ADOPTED_SHA, BANDS, band_of, fame_frame  # noqa: E402,F401

FPC_WIKIDATA = _FPC / "fp_wikidata.json"

MB_URL = "https://musicbrainz.org/ws/2/artist/{mbid}?inc=genres+tags&fmt=json"
# MusicBrainz asks for <= 1 req/s on average. Sleep is enforced by the fetch
# itself so no caller can accidentally hammer the endpoint.
MB_PAUSE = 1.1


def norm_genre(label: str) -> str:
    """One vocabulary for MB genre names and Wikidata P136 labels. Frozen."""
    s = unicodedata.normalize("NFKD", label).encode("ascii", "ignore").decode()
    s = s.casefold().replace("-", " ").replace("_", " ")
    s = " ".join(s.split())
    if s.endswith(" music"):
        s = s[: -len(" music")]
    return s


def get_json(url: str, *, attempts: int = 5, timeout: int = 60) -> tuple[int, Any]:
    """GET with backoff on 429/5xx. Returns (status, payload-or-None).

    404 is a real answer here (deleted MBIDs exist in the artifact -- the
    nameless-node class), so it is returned, not raised.
    """
    delay = 2.0
    last: Exception | None = None
    for _ in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return 404, None
            last = exc
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            time.sleep(float(retry_after) if retry_after else delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError) as exc:
            last = exc
            time.sleep(delay)
            delay *= 2
    raise RuntimeError(f"gave up after {attempts} attempts: {last}")


def fetch_mb_artists(
    mbids: list[str], done: dict[str, Any], out_path: Path, *, label: str
) -> dict[str, Any]:
    """One artist per request at MB_PAUSE, checkpointed every 50.

    Records {"status", "genres", "tags"} per MBID; genre/tag names are stored
    raw (normalisation happens at read time, so the raw record stays honest).
    """
    pending = [m for m in mbids if m not in done]
    print(f"{label}: {len(done)} already done, {len(pending)} to fetch", flush=True)
    for i, mbid in enumerate(pending, 1):
        status, payload = get_json(MB_URL.format(mbid=mbid))
        record: dict[str, Any] = {"status": status}
        if payload is not None:
            record["genres"] = [g["name"] for g in payload.get("genres", [])]
            record["tags"] = [t["name"] for t in payload.get("tags", [])]
        done[mbid] = record
        if i % 50 == 0 or i == len(pending):
            save_partial(out_path, done)
            print(f"  {label} {i}/{len(pending)}", flush=True)
        time.sleep(MB_PAUSE)
    return done


def mb_genre_set(record: dict[str, Any] | None) -> set[str]:
    if not record or record.get("status") != 200:
        return set()
    return {norm_genre(g) for g in record.get("genres", [])}


def mb_tag_set(record: dict[str, Any] | None) -> set[str]:
    if not record or record.get("status") != 200:
        return set()
    return {norm_genre(t) for t in record.get("tags", [])}
