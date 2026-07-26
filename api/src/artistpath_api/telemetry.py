"""Structured-JSON telemetry on stdout.

App Runner ships stdout to CloudWatch Logs with no configuration, which is why
this is the whole telemetry mechanism and there is no client, no buffer and no
new infrastructure (DEP-2).

Events carry FACTS, never computed metrics. Routing is deterministic, so any
quality metric can be derived offline from the logged inputs against the frozen
top-1%-by-degree set — and choosing which metric production computes would be a
scoring decision taken while path-quality work is paused (DEP-7).
"""

from __future__ import annotations

import json
import re

# Bounded and charset-restricted because the value arrives in a client-supplied
# header and lands in a log line that analysis will parse (DEP-27).
_JOURNEY_ID = re.compile(r"^[A-Za-z0-9-]{8,64}$")

UNKNOWN_JOURNEY = "unknown"


def safe_journey_id(raw: str | None) -> str:
    """Return the id if it is well-formed, else a constant placeholder."""
    if raw and _JOURNEY_ID.match(raw):
        return raw
    return UNKNOWN_JOURNEY


def emit(event: dict) -> None:
    """Write one event as a single line of JSON.

    json.dumps, never string formatting: a value containing a newline and JSON
    punctuation would otherwise inject a second, fabricated record into the
    telemetry this exists to collect.
    """
    print(json.dumps(event, separators=(",", ":"), default=str), flush=True)
