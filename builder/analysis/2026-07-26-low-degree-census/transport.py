"""Make the canonical resolver's transport reliable under concurrency.

**Why this exists — a directional failure found by `verify_pool_equivalence.py`.**
`fame._wikidata_search` and `fame._entity_with_sitelinks` both end in
`except Exception: return []` / `return {}`. That makes a transient HTTP 429 or
timeout **indistinguishable from "no such entity"**, and under A11's encoding an
unresolvable artist is scored at the fame floor. So throttling does not produce
noise — it produces *obscurity*, silently and in one direction. At 8 workers the
equivalence check caught it live: `Compulsion` resolved to
`Compulsion (band)` (F = 3.801) serially and to the floor (F = 0.000) pooled.

For a fame-RANKED deliverable that failure mode is the worst available one: it
removes an artist from the list rather than misplacing them, so nothing in the
output shows that anything went wrong.

**What this module changes, and what it deliberately does not.** It wraps
`_get_json` in both canonical modules with a retry on *transient* failures only
(429, 5xx, timeouts, connection resets), with exponential backoff and jitter.

  - It does **not** touch the accept criteria. Identity, performer and musical
    are the same three clauses on the same entities; A11's validated
    matched/unmatched split on the §5 sample is untouched by construction,
    because no reject path is reached differently.
  - A **404 is re-raised immediately, never retried** — `pageviews_sum` relies on
    catching it to mean "no pageview data in the window", which is a real answer
    and must stay fast.
  - It can only ever recover a result the canonical serial run would have got.
    It cannot manufacture a match, because it changes no predicate.

This is the same shape of change as A15 itself: a reliability/recall fix on
identical accept clauses, argued to be neutral and then *checked* by a committed
equivalence script rather than asserted.

The committed Track 2 modules are patched at runtime and never edited on disk —
they are the instrument Track 2's figures were produced with, and editing them
would retroactively alter committed work.
"""

from __future__ import annotations

import random
import time
import urllib.error

import fame
from fetch_pageviews import _get_json as _canonical_get_json

# Retried: the server is asking us to slow down, or the connection broke.
# 404 is excluded on purpose (see module docstring).
TRANSIENT_HTTP = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 4
BASE_BACKOFF_S = 0.75
BACKOFF_CAP_S = 8.0  # a single hopeless name must not stall a worker for a minute


def retrying_get_json(url: str) -> dict:
    last: Exception | None = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            return _canonical_get_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code not in TRANSIENT_HTTP:
                raise  # 404 and every other definite answer passes straight through
            last = exc
        except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
            last = exc
        # Full jitter: concurrent workers throttled by the same server must not
        # retry in lockstep, or they re-create the burst that caused the 429.
        time.sleep(random.uniform(0, min(BASE_BACKOFF_S * (2 ** attempt), BACKOFF_CAP_S)))
    # Exhausted. Raise rather than return empty: the caller's `except Exception`
    # would turn an empty result into a fame-floor score, which is the exact
    # silent failure this module exists to prevent. A raised error surfaces as an
    # unresolved name that the next resumable run retries.
    # The real cause is named, not summarised as "transient". Assuming the cause was
    # a 429 without ever logging the status is how this run spent an hour treating an
    # unknown failure as a known one.
    detail = f"{type(last).__name__}: {last}"
    if isinstance(last, urllib.error.HTTPError):
        detail = f"HTTP {last.code} (Retry-After={last.headers.get('Retry-After')!r})"
    raise RuntimeError(
        f"failed after {MAX_ATTEMPTS} attempts [{detail}]: {url}"
    ) from last


def install() -> None:
    """Patch both canonical modules' network entry points. Idempotent."""
    import fetch_pageviews

    fetch_pageviews._get_json = retrying_get_json
    fame._get_json = retrying_get_json
