"""A per-source circuit breaker for the clip catalogues (G3-A4 / G3-S2).

PW-3 stopped a single request costing three calls to a service that is already
refusing us. This stops the next thousand requests each costing one, which is
what actually lets a rate-limit block clear instead of being continuously
renewed.

Per-process and unsynchronised across instances. That is adequate at
`max_size=2` and it is deliberate: a breaker shared through DynamoDB would be a
write on every clip request, which is the load it exists to avoid. With two
instances the worst case is twice the configured rate — still bounded, and far
below the fan-out it replaces.

Time is injected so the cooldown is testable without sleeping.
"""

from __future__ import annotations

import time
from collections.abc import Callable


class CatalogueBreaker:
    def __init__(
        self,
        threshold: int,
        cooldown_s: float,
        now: Callable[[], float] = time.monotonic,
    ) -> None:
        self._threshold = threshold
        self._cooldown_s = cooldown_s
        self._now = now
        self._failures: dict[str, int] = {}
        self._opened_at: dict[str, float] = {}

    def is_open(self, source: str) -> bool:
        """Is this source in its cooldown, and therefore not to be called?"""
        opened = self._opened_at.get(source)
        if opened is None:
            return False
        if self._now() - opened >= self._cooldown_s:
            # Cooldown served: let ONE request through as a probe.
            #
            # The failure count is deliberately NOT reset here. There is no
            # separate half-open state because the next real request IS the
            # probe: leaving the count at the threshold means a single further
            # failure re-opens immediately, so a catalogue that is still down
            # costs one call per cooldown. Resetting the count instead would
            # admit a further `threshold` requests every cooldown, which for a
            # permanently dead service is five calls a minute rather than one.
            self._opened_at.pop(source, None)
            return False
        return True

    def record_failure(self, source: str) -> None:
        count = self._failures.get(source, 0) + 1
        self._failures[source] = count
        if count >= self._threshold:
            self._opened_at[source] = self._now()

    def record_success(self, source: str) -> None:
        """Clear the count.

        Without this, scattered failures over hours accumulate and eventually
        trip the breaker on a service that is working perfectly well.
        """
        self._failures.pop(source, None)
        self._opened_at.pop(source, None)
