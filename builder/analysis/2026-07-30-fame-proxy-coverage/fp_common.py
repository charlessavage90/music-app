"""Shared loading for the fame-proxy coverage probes.

SCOPE: these probes are DESCRIPTIVE scope checks in the CS-P0 sense -- they
measure coverage and agreement of candidate fame instruments. They fix no
criterion, run no arm, and license no currency change. A pre-registration is
owed before any criterion is built on any instrument measured here.

WHY THIS DIRECTORY EXISTS
  The adopted fame proxy (English-Wikipedia pageviews, Track 2 prereg §5/A11)
  FAILED its own pre-registered coverage falsifier: 9 of 29 match failures
  against a >6 bar, recorded verbatim as "pageviews is unfit per §5" in
  ../2026-07-24-track2-fame-proxy-wikipedia/README.md. It was adopted anyway
  under A11 by scoring unresolvable artists at the fame FLOOR. That floor has
  since cost twice: A12 had to strip C6 from gating, and A18 recorded the
  blank-name confound (33 nameless nodes read as maximal obscurity, 2.7x
  concentrated in the bottom decile, absent from the control).

  The floor collapses the whole obscure tail into one value -- the region the
  product exists to serve. These probes measure what two alternatives cover.

THE FAME FRAME IS IMPORTED, NOT COPIED
  Band membership must be identical to Track B's or nothing here is comparable
  with it. cb_metrics.fame_frame asserts the adopted artifact's sha256, so the
  assertion travels with the import.
"""

from __future__ import annotations

import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable

HERE = Path(__file__).parent
_TRACK_B = HERE.parent / "2026-07-30-track-b-cap-selection"
if str(_TRACK_B) not in sys.path:
    sys.path.insert(0, str(_TRACK_B))

from cb_metrics import ADOPTED, ADOPTED_SHA, BANDS, band_of, fame_frame  # noqa: E402,F401

# Contact address is required by both Wikimedia's and MetaBrainz's user-agent
# policies. Neither endpoint is ours; identify honestly or get blocked.
USER_AGENT = "artistpath-research/1.0 (charlessavagemiller@gmail.com)"

BAND_ORDER = [name for name, _lo, _hi in BANDS]


def graph_mbids() -> list[str]:
    """Every MBID in the adopted artifact, sorted. Deterministic batching."""
    frame = fame_frame()
    return sorted(frame)


def load_partial(path: Path) -> dict[str, Any]:
    """Resume support: these are long network jobs against third-party APIs.

    A crash at artist 60,000 must not re-fetch the first 60,000 -- that is
    rude to the endpoint as well as slow.
    """
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_partial(path: Path, data: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data), encoding="utf-8")
    tmp.replace(path)


def post_json(
    url: str,
    body: bytes,
    headers: dict[str, str],
    *,
    attempts: int = 5,
    timeout: int = 120,
) -> Any:
    """POST with exponential backoff on 429/5xx.

    Backoff rather than bare retry: a tight retry loop against a rate-limited
    public endpoint is the failure mode that gets a project blocked.
    """
    delay = 2.0
    last: Exception | None = None
    for _ in range(attempts):
        try:
            req = urllib.request.Request(url, data=body, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
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


def run_batches(
    items: list[str],
    size: int,
    done: dict[str, Any],
    fetch: Callable[[list[str]], dict[str, Any]],
    out_path: Path,
    *,
    pause: float,
    label: str,
) -> dict[str, Any]:
    """Batch, fetch, checkpoint, repeat. Prints progress; use `python -u`."""
    pending = [m for m in items if m not in done]
    print(f"{label}: {len(done)} already done, {len(pending)} to fetch", flush=True)
    for start in range(0, len(pending), size):
        chunk = pending[start : start + size]
        began = time.time()
        done.update(fetch(chunk))
        # Absent keys must be recorded as absent, or a resume re-requests them
        # forever and the coverage denominator silently changes.
        for mbid in chunk:
            done.setdefault(mbid, None)
        save_partial(out_path, done)
        print(
            f"  {label} {min(start + size, len(pending))}/{len(pending)}"
            f"  ({time.time() - began:.1f}s)",
            flush=True,
        )
        time.sleep(pause)
    return done
