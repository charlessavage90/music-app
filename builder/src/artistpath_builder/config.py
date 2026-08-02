"""All builder tunables. No magic numbers anywhere else in the package."""

from __future__ import annotations

from dataclasses import dataclass

from artistpath_builder import __version__

CONTACT_EMAIL = "charlessavagemiller@gmail.com"

# The live endpoint's `algorithm` parameter is a CLOSED ENUM of exactly these
# six values — validated 2026-07-29 (CS-P0e; probes and the 400s they returned
# are recorded in
# builder/analysis/2026-07-29-cap-selection-sim/cs_p0e_algorithms.json).
# Arm labels ALG-A..ALG-F are the AS pre-registration's. Do not add values:
# anything outside this set returns HTTP 400.
PRODUCTION_ALGORITHM = (  # ALG-E — the adopted 75k archive's algorithm
    "session_based_days_7500_session_300_contribution_5"
    "_threshold_10_limit_100_filter_True_skip_30"
)
# ALG-B — the named re-crawl candidate (AS log §7); differs from production by
# contribution_3. Named rather than reached by index because it is now a
# selector: it is the second population with a censused no-release drop list
# (no_release_drop.py), and `PERMITTED_ALGORITHMS[1]` cannot say that.
CANDIDATE_ALGORITHM = (
    "session_based_days_7500_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30"
)
PERMITTED_ALGORITHMS = (
    PRODUCTION_ALGORITHM,
    CANDIDATE_ALGORITHM,
    # ALG-A
    "session_based_days_1825_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-F
    "session_based_days_1800_session_300_contribution_3"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-D
    "session_based_days_75_session_300_contribution_5"
    "_threshold_10_limit_100_filter_True_skip_30",
    # ALG-C
    "session_based_days_9000_session_300_contribution_5"
    "_threshold_15_limit_50_skip_30",
)


@dataclass(frozen=True, slots=True)
class BuilderConfig:
    # --- source ---------------------------------------------------------
    # Confirmed working against the live endpoint in Task 1. Changing this
    # DEFAULT is the re-crawl decision itself and is the owner's (NEXT.md);
    # a trial run overrides it per-invocation via `artistpath-build
    # crawl|build --algorithm`.
    algorithm: str = PRODUCTION_ALGORITHM
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

    # How the neighbour cap is applied. ADOPTED: "mutual_knn" — keep an edge
    # only if each endpoint ranks the other in its top-k. Bounds degree at k
    # and stays symmetric.
    #
    # The legacy "pre_symmetrise" strategy (cap each artist's own list, then
    # symmetrise, which bounds nothing after symmetrisation) LOST Phase 2 and
    # has been deleted: it raises rather than being a supported mode, per
    # Phase 2 spec §8 risk 4. Evidence:
    # docs/superpowers/findings/2026-07-22-phase2-sweep-results.md §1, §5
    # and execution log §12, §16 (two blind listening tests).
    cap_strategy: str = "mutual_knn"

    # Popularity correction applied to raw co-occurrence when scoring edges,
    # in log space (see damped_strength in pipeline.py), no centring, no clamp:
    #     score(a,b) = log1p(cooc(a,b)) - similarity_damping * (log(mass(a)) + log(mass(b)))
    # 0.0 = raw association strength (globally rescaled), 0.5 = full cosine.
    #
    # ADOPTED: 0.0, on evidence rather than inheritance. The Phase 2 sweep ran
    # d = 0.0 / 0.25 / 0.5 / 0.75 and the owner chose an undamped arm in a
    # blind listening test against d = 0.25 (execution log §16). See
    # docs/superpowers/findings/2026-07-22-phase2-sweep-results.md §1, §4, §5.
    #
    # This knob is NOT deleted, unlike the two enum knobs above and below.
    # It is a continuous axis, not a two-option switch, and the spec's
    # deletion requirement (§8 risk 4) names only similarity_rescale. Damping
    # above 0 remains reachable and supported.
    #
    # The rationale originally recorded here cited numbers that do not
    # reproduce ("~6x", "2357 vs 277"). Its *conclusion* was nonetheless right:
    # full cosine over-corrects. Routing on graph-75k-cosine.bin returns
    # Miles Davis -> J. K. Simmons -> Hank Levy -> Justin Hurwitz ->
    # Emma Stone, a film cast list. Raising this knob without fixing the
    # rescale below trades one failure mode for another.
    #
    # The primary defect is NOT this knob — it is the p99 clip below, which
    # yields zero-cost edges in every build. Damping decides only where they
    # point: median destination out-degree 719 at d=0 (the famous core), 9 at
    # d=0.5 (micro-cliques). That ceiling defect SURVIVES adoption, because the
    # adopted rescale is still the clip; it is carried to Phase 1 as an open
    # item with a success condition (execution log §6).
    #
    # NOTE, now load-bearing: raising this above 0 while the clip rescale is in
    # use makes the `- 2*log(median_mass)` centring term MANDATORY. Without it,
    # 78.7% of edges clamp to zero at d=0.25 and 99.98% at d=0.5, where the
    # rescale emits nan. The centring term is not currently implemented, so
    # rescale_scores raises on that combination rather than emitting nan.
    #
    # Full record: docs/superpowers/findings/2026-07-21-scoring-adjudication.md
    # Design:      docs/superpowers/specs/2026-07-21-phase2-path-quality-design.md
    similarity_damping: float = 0.0

    # How raw edge strength is mapped into 0-1. ADOPTED: "p99_log_clip",
    # min(1, log1p(v)/log1p(p99)).
    #
    # Adopted with a known defect, not because it is clean: it saturates a
    # small share of edges at exactly 1.0, and those cost w_sim*(1-1.0) == 0 —
    # free similarity. For the measured share of edges and of routed hops, see
    # the adjudication findings §2.5; figures are not restated here. The
    # alternative "percentile_rank" (rank transform, no ceiling tie-mass)
    # removed that defect and still LOST, in a blind listening test the owner
    # judged on path quality (execution log §16). The ceiling defect is
    # therefore carried to Phase 1 as an open item, NOT closed.
    #
    # "percentile_rank" is deleted per spec §8 risk 4 and raises on use.
    # Evidence: docs/superpowers/findings/2026-07-22-phase2-sweep-results.md
    # §1, §4, §5.
    similarity_rescale: str = "p99_log_clip"

    # Drop MusicBrainz placeholder entities ([unknown], [traditional],
    # [no artist], [anonymous], [theatre], [dialogue], [Disney]). Matched on
    # the DISAMBIGUATION field, never the name: 22 nodes have bracketed names
    # and 15 of them are real bands. This is a correctness fix and is worth
    # approximately nothing on hub metrics — see the Phase 2 spec §1.5.
    filter_special_purpose: bool = True

    # Apply the adopted no-release-tail drop rule: keep a release-less artist
    # only where a commercial-DSP link exists AND a clip resolves. 7,035 of the
    # 7,686-artist tail are dropped, from a frozen 2026-08-01 snapshot — see
    # no_release_drop.py for why the list is data rather than a build-time
    # lookup. Owner decision 2026-08-01 (NEXT.md); the rule is ADOPTED and the
    # default is on.
    #
    # It is a flag rather than an unconditional drop for one reason: the drop
    # moves every surviving artist's popularity marginal, so a build-side
    # experiment that needs to isolate its effect can hold it explicitly on or
    # off in a factor table instead of comparing across a silent substrate
    # change. Turning it off is an experimental control, never a shipping
    # configuration.
    drop_no_release_tail: bool = True

    # --- output ---------------------------------------------------------
    graph_version: str = "v1"

    def __post_init__(self) -> None:
        # Phase 2 spec §8 risk 4: the losing option is deleted, not left as a
        # permanently supported mode. Named explicitly so a config carried over
        # from a Phase 2 sweep script fails loudly instead of silently
        # selecting a strategy whose code has been removed.
        if self.cap_strategy != "mutual_knn":
            raise ValueError(
                f"cap_strategy={self.cap_strategy!r} is not supported. "
                "'pre_symmetrise' lost Phase 2 and was removed; 'mutual_knn' "
                "is the only strategy. See execution log §16."
            )
        if self.similarity_rescale != "p99_log_clip":
            raise ValueError(
                f"similarity_rescale={self.similarity_rescale!r} is not "
                "supported. 'percentile_rank' lost Phase 2 and was removed; "
                "'p99_log_clip' is the only rescale. See execution log §16."
            )

    @property
    def user_agent(self) -> str:
        return f"artistpath-builder/{__version__} ({CONTACT_EMAIL})"

    @property
    def request_delay_seconds(self) -> float:
        return 1.0 / self.requests_per_second
