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

    # How the neighbour cap is applied.
    #   "pre_symmetrise" — legacy: cap each artist's own list, then symmetrise.
    #                      Bounds nothing after symmetrisation.
    #   "mutual_knn"     — keep an edge only if each endpoint ranks the other
    #                      in its top-k. Bounds degree at k, stays symmetric.
    # Retained as a knob only until Phase 2 concludes; delete the loser then
    # (Phase 2 spec §8 risk 4).
    cap_strategy: str = "pre_symmetrise"

    # Popularity correction applied to raw co-occurrence when scoring edges:
    #     sim(a,b) = cooc(a,b) / (mass(a) * mass(b)) ** similarity_damping
    # 0.0 = raw association strength (globally rescaled), 0.5 = full cosine.
    #
    # 0.0 is provisional. It is what the current graph was built with, not a
    # value that has been shown correct.
    #
    # The rationale originally recorded here cited numbers that do not
    # reproduce ("~6x", "2357 vs 277"). Its *conclusion* was nonetheless right:
    # full cosine over-corrects. Routing on graph-75k-cosine.bin returns
    # Miles Davis -> J. K. Simmons -> Hank Levy -> Justin Hurwitz ->
    # Emma Stone, a film cast list. Raising this knob without fixing the
    # rescale below trades one failure mode for another.
    #
    # The primary defect is NOT this knob — it is the p99 clip in pipeline.py,
    # which yields zero-cost edges in every build. Damping decides only where
    # they point: median destination out-degree 719 at d=0 (the famous core),
    # 9 at d=0.5 (micro-cliques). 30-82% of routed hops currently cost zero
    # similarity. Fix the rescale first; this value is decided after that.
    #
    # NOTE: if this is ever raised above 0 while the clip rescale is still in
    # use, the `- 2*log(median_mass)` centring term is MANDATORY. Without it,
    # 78.7% of edges clamp to zero at d=0.25 and 99.98% at d=0.5, where the
    # rescale emits nan. Under a rank rescale the term is inert.
    #
    # Full record: docs/superpowers/findings/2026-07-21-scoring-adjudication.md
    # Design:      docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md
    similarity_damping: float = 0.0

    # Drop MusicBrainz placeholder entities ([unknown], [traditional],
    # [no artist], [anonymous], [theatre], [dialogue], [Disney]). Matched on
    # the DISAMBIGUATION field, never the name: 22 nodes have bracketed names
    # and 15 of them are real bands. This is a correctness fix and is worth
    # approximately nothing on hub metrics — see the Phase 2 spec §1.5.
    filter_special_purpose: bool = True

    # --- output ---------------------------------------------------------
    graph_version: str = "v1"

    @property
    def user_agent(self) -> str:
        return f"artistpath-builder/{__version__} ({CONTACT_EMAIL})"

    @property
    def request_delay_seconds(self) -> float:
        return 1.0 / self.requests_per_second
