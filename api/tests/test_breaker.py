"""The catalogue circuit breaker (G3-A4 / G3-S2).

PW-3 stopped one request costing three calls to a refusing service. This stops
the NEXT thousand requests each costing one, which is what actually lets the
block clear.

Time is injected rather than slept, so these are deterministic and instant. A
breaker tested with real sleeps is a breaker whose cooldown nobody re-checks.
"""

from artistpath_api.breaker import CatalogueBreaker


class FakeClock:
    def __init__(self):
        self.t = 1000.0

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


def test_a_healthy_source_is_never_open():
    b = CatalogueBreaker(threshold=3, cooldown_s=60.0, now=FakeClock())
    assert not b.is_open("deezer")


def test_it_opens_only_after_the_threshold_is_reached():
    # Off-by-one matters here: opening at the first failure would silence every
    # card for a minute over one transient error, which is worse than the
    # defect being fixed.
    b = CatalogueBreaker(threshold=3, cooldown_s=60.0, now=FakeClock())
    b.record_failure("deezer")
    b.record_failure("deezer")
    assert not b.is_open("deezer")
    b.record_failure("deezer")
    assert b.is_open("deezer")


def test_it_closes_again_once_the_cooldown_has_passed():
    clock = FakeClock()
    b = CatalogueBreaker(threshold=2, cooldown_s=60.0, now=clock)
    b.record_failure("deezer")
    b.record_failure("deezer")
    assert b.is_open("deezer")
    clock.advance(59.0)
    assert b.is_open("deezer"), "closed early — the cooldown is not being honoured"
    clock.advance(2.0)
    assert not b.is_open("deezer")


def test_a_success_clears_the_count():
    # Without this, scattered failures over hours eventually trip the breaker
    # on a service that is working perfectly well.
    b = CatalogueBreaker(threshold=3, cooldown_s=60.0, now=FakeClock())
    b.record_failure("deezer")
    b.record_failure("deezer")
    b.record_success("deezer")
    b.record_failure("deezer")
    assert not b.is_open("deezer")


def test_the_two_catalogues_are_independent():
    # The whole value of the fallback is that one service being down leaves the
    # other usable. A breaker keyed on nothing would delete that.
    b = CatalogueBreaker(threshold=1, cooldown_s=60.0, now=FakeClock())
    b.record_failure("deezer")
    assert b.is_open("deezer")
    assert not b.is_open("itunes")


def test_the_request_after_a_cooldown_is_the_probe_and_a_failure_reopens():
    # There is no separate half-open state: the next real request IS the probe.
    # If it fails, the breaker must re-open immediately rather than admitting
    # another `threshold` requests to a service still refusing us.
    clock = FakeClock()
    b = CatalogueBreaker(threshold=2, cooldown_s=60.0, now=clock)
    b.record_failure("deezer")
    b.record_failure("deezer")
    clock.advance(61.0)
    assert not b.is_open("deezer")
    b.record_failure("deezer")
    assert b.is_open("deezer"), (
        "a failed probe let the count restart from zero, so a dead catalogue "
        "is called `threshold` times per cooldown instead of once"
    )
