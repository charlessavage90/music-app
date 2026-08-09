"""All builder tunables. No magic numbers anywhere else in the package."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from artistpath_builder import __version__

CONTACT_EMAIL = "charlessavagemiller@gmail.com"

# The live endpoint's `algorithm` parameter is a CLOSED ENUM of exactly these
# six values — validated 2026-07-29 (CS-P0e; probes and the 400s they returned
# are recorded in
# builder/analysis/2026-07-29-cap-selection-sim/cs_p0e_algorithms.json).
# Arm labels ALG-A..ALG-F are the AS pre-registration's. Do not add values:
# anything outside this set returns HTTP 400.
PRODUCTION_ALGORITHM = (  # ALG-E — the ORIGINAL production crawl's algorithm
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
# ⚠ ALG-B is the ADOPTED map's lineage: graph-msw-tu50.bin was built from the
# ALG-B archive (its manifest records contribution_3), and ApiConfig.graph_path
# serves it. `algorithm` below still DEFAULTS to ALG-E, deliberately — flipping
# that default is the re-crawl decision and is the owner's — so every command
# touching the adopted lineage must pass --algorithm explicitly. CEX-R5.
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

# How the neighbour cap is applied. Both are implemented in graph.py; the
# deleted "pre_symmetrise" is deliberately absent rather than listed-and-
# rejected, so that adding a strategy here can never reinstate it by accident.
PERMITTED_CAP_STRATEGIES = ("mutual_knn", "trimmed_union")


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
    #
    # "trimmed_union" was ADDED 2026-08-05 with the map switch and ADOPTED as
    # the default 2026-08-06 (MSW-): top-j union, then a hard degree ceiling
    # (Track B's `TUw-50-50`, cell B-S1). It is non-reciprocal, which is the
    # whole point — see trimmed_union_cap in graph.py. Adopting it does NOT
    # reopen pre_symmetrise, which remains deleted on evidence.
    #
    # Flipped from "mutual_knn" in one commit with require_fame below and
    # ApiConfig.w_known_ramp_fame_pctl. Frozen probes under builder/analysis/
    # that reproduce pre-adoption figures are era-pinned to "mutual_knn" at
    # their own construction sites; see builder/analysis/README.md.
    cap_strategy: str = "trimmed_union"
    # Knobs for cap_strategy="trimmed_union"; ignored under mutual_knn, which
    # uses max_neighbours_per_artist above. Defaults are Track B's selected
    # cell (j = 50, ceiling = 50).
    union_top_j: int = 50
    union_degree_ceiling: int = 50

    # Require a fame record for every artist in the built graph, and REFUSE to
    # build otherwise (MSW-G3). This is the ULC-F1 shape applied to a new
    # quantity: a lookup that quietly succeeds over a smaller population than
    # the one being built leaves new artists unevaluated — for a drop list that
    # means under-filtering, for fame it means an artist priced by a default in
    # a cost function that routes on the price.
    #
    # ON as of the MSW- adoption, 2026-08-06. It was OFF until then, and
    # deliberately so: until the router read fame
    # (ApiConfig.w_known_ramp_fame_pctl), a fame-less build was genuinely
    # valid and defaulting this on would have asserted a requirement that was
    # not yet true. That requirement is now true, so this asserts it.
    #
    # Flipped with cap_strategy above and the ramp, in one commit. The two
    # independent guards still stand and neither relies on this default: the
    # shipped artifact was built with it explicitly on, and the api refuses at
    # boot if the ramp is live over a fameless artifact.
    #
    # ⚠ An archive with no `fame` stage run against it now REFUSES to build.
    # That is the point, but it means any harness replaying a pre-adoption
    # archive must pin require_fame=False at its own construction site — the
    # three under builder/analysis/ that call build_from_archive are pinned.
    require_fame: bool = True

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

    # Apply the featured-credit filter: drop an artist who is credited on
    # release groups but never as the sole artist, has no Discogs main-artist
    # release, and fails the same keep-check as the no-release rule (a
    # commercial-DSP link AND a clip resolves). These artists exist in the
    # graph only through shared credits — quarter-weight co-listens on other
    # artists' tracks (LBS-1) — and the no-release rule never evaluates them
    # because credits count as release groups. Rule document:
    # docs/superpowers/specs/2026-08-03-featured-credit-filter-rule.md (FCF-);
    # the lists are frozen 2026-08-03 snapshots (featured_credit_drop.py).
    #
    # A flag for the same one reason as drop_no_release_tail: the drop moves
    # every surviving artist's popularity marginal, so a build-side experiment
    # holds it explicitly on or off in a factor table. Turning it off is an
    # experimental control, never a shipping configuration.
    drop_featured_credit: bool = True

    # Apply the un-listenable filter (ULF-, 2026-08-05): drop an artist who
    # has never put out anything of their own that is more than a single
    # track (ULC-D2), unless a commercial-DSP link exists AND a clip
    # resolves. Supersedes the two drops above WITHOUT reversing either —
    # both classes are strict subsets and their frozen verdicts carry — so
    # with all three flags on, this rule's list is the one doing the work.
    # The older flags stay functional for era-pinned probes (ULF-3 defers
    # their retirement with a success condition). Rule document:
    # docs/superpowers/specs/2026-08-05-unlistenable-filter-rule.md; lists
    # and the ULC-F1 population manifest in unlistenable_drop.py.
    #
    # A flag for the same one reason as its siblings: the drop moves every
    # surviving artist's popularity marginal, so a build-side experiment
    # holds it explicitly on or off in a factor table. Turning it off is an
    # experimental control, never a shipping configuration.
    drop_unlistenable: bool = True

    # Per-invocation override for WHICH un-listenable payload to apply, for
    # the case the algorithm-keyed default cannot express: two populations of
    # the SAME algorithm, which is what a crawl extension produces. `None`
    # keeps the shipped default. Bypasses the lookup rather than substituting
    # within it, so an uncensused algorithm can also be built from an explicit
    # payload — the ULC-F1 population check still runs either way.
    #
    # Deliberately NOT a repointed default: the guard in pipeline.py refuses
    # on artists OUTSIDE the censused set, so a LARGER list applied to a
    # smaller archive passes silently. Repointing would therefore have changed
    # every future build from the pre-crawl snapshot without saying so, on
    # verdicts that drift as clip availability moves. Flipping the default is
    # an adoption decision and belongs in the adoption commit. SEL- findings
    # 2026-08-09; MSW- Task 9's --require-fame is the precedent.
    unlistenable_list_path: Path | None = None

    # --- output ---------------------------------------------------------
    graph_version: str = "v1"

    def __post_init__(self) -> None:
        # Phase 2 spec §8 risk 4: the losing option is deleted, not left as a
        # permanently supported mode. Named explicitly so a config carried over
        # from a Phase 2 sweep script fails loudly instead of silently
        # selecting a strategy whose code has been removed.
        if self.cap_strategy not in PERMITTED_CAP_STRATEGIES:
            raise ValueError(
                f"cap_strategy={self.cap_strategy!r} is not supported. "
                f"Permitted: {', '.join(sorted(PERMITTED_CAP_STRATEGIES))}. "
                "'pre_symmetrise' lost Phase 2 and was removed — it is not "
                "reinstated by the addition of 'trimmed_union'. See execution "
                "log §16."
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
