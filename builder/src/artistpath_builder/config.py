"""All builder tunables. No magic numbers anywhere else in the package."""

from __future__ import annotations

from dataclasses import dataclass

from artistpath_builder import __version__

CONTACT_EMAIL = "charlessavagemiller@gmail.com"


@dataclass(frozen=True, slots=True)
class BuilderConfig:
    # --- source ---------------------------------------------------------
    # Confirmed working against the live endpoint in Task 1.
    algorithm: str = (
        "session_based_days_7500_session_300_contribution_5"
        "_threshold_10_limit_100_filter_True_skip_30"
    )
    similar_artists_url: str = "https://labs.api.listenbrainz.org/similar-artists/json"
    sitewide_artists_url: str = "https://api.listenbrainz.org/1/stats/sitewide/artists"

    # --- crawl ----------------------------------------------------------
    target_artist_count: int = 75_000
    # Task 1 measured X-RateLimit: 30 requests per 5s window (~6/s).
    # Deliberately under it: this crawl runs once, and being throttled costs
    # more than being slow.
    requests_per_second: float = 5.0
    max_retries: int = 5
    timeout_seconds: float = 30.0
    checkpoint_every: int = 500

    # --- graph ----------------------------------------------------------
    max_neighbours_per_artist: int = 50

    # --- output ---------------------------------------------------------
    graph_version: str = "v1"

    @property
    def user_agent(self) -> str:
        return f"artistpath-builder/{__version__} ({CONTACT_EMAIL})"

    @property
    def request_delay_seconds(self) -> float:
        return 1.0 / self.requests_per_second
