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

    # Popularity correction applied to raw co-occurrence when scoring edges:
    #     sim(a,b) = cooc(a,b) / (mass(a) * mass(b)) ** similarity_damping
    # 0.0 = raw association strength (globally rescaled), 0.5 = full cosine.
    #
    # UNDER REVIEW — 0.0 is NOT a settled default. Do not rely on this comment
    # to justify leaving it alone.
    #
    # This was set to 0.0 citing findings 2026-07-21 §4: "full cosine
    # over-corrects, inflating rare co-occurrences so that tight niche clusters
    # outscore genuine musical neighbours by ~6x". That evidence does not
    # reproduce against the built artifacts. In graph-75k-cosine.bin the cited
    # junk edge ranks 327/337 (score 0.0094) while Miles Davis -> Stan Getz
    # ranks 15/337 (0.222) — a 24x gap in the opposite direction to the claim.
    # The accompanying "2357 vs 277" figure has no source in version control.
    # Findings §5.4 independently retracted the same conclusion.
    #
    # The measured defect is the p99 clip in pipeline.py, not this knob: 34,696
    # edges saturate at exactly 1.0 and their destinations have a median
    # out-degree of 719 against a graph median of 49, so similarity is free
    # into the hub core. See specs/2026-07-21-phase2-path-quality-design.md
    # §1.1-1.2, which schedules the sweep that decides this value.
    #
    # 0.0 is retained only because it is what the current graph was built with.
    # It is not endorsed.
    similarity_damping: float = 0.0

    # --- output ---------------------------------------------------------
    graph_version: str = "v1"

    @property
    def user_agent(self) -> str:
        return f"artistpath-builder/{__version__} ({CONTACT_EMAIL})"

    @property
    def request_delay_seconds(self) -> float:
        return 1.0 / self.requests_per_second
