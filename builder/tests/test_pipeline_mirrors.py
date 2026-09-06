"""Guard: `build_from_archive` has copies, and they diverge silently.

Several probe harnesses under `builder/analysis/` reimplement the pipeline's
stage order so they can inject a different step — `cb_build_variants.py` most
importantly, since Track B's whole cell grid was built through it. Those copies
are frozen on purpose: each reproduces its committed output byte for byte, and
that is what makes the record checkable.

The failure mode is one-sided and quiet. Adding a stage to the shipped pipeline
does not break a mirror; it just makes the mirror describe a build that no
longer exists, while every test stays green. It happened on 2026-08-02 with the
no-release-tail drop. Track B's own identity gate could not catch it, because
that gate pins the harness against the shas it produced in July rather than
against a live `build_from_archive` — a reproduction check, not a fidelity one.

This is the mechanical half of the fix. A build rule almost always arrives as a
`BuilderConfig` field, so pinning the field set forces whoever adds one to look
at the list below and decide, per mirror, whether it needs the new stage or an
explicit era-pin. It is deliberately not complete: a stage added with no config
knob would still slip past, and that half cannot be mechanised.
"""

from dataclasses import fields

from artistpath_builder.config import BuilderConfig

# Known reimplementations of build_from_archive's stage order, 2026-08-02.
PIPELINE_MIRRORS = (
    "builder/analysis/2026-07-30-track-b-cap-selection/cb_build_variants.py",
    "builder/analysis/2026-07-22-cap-ranking-replay/replay.py",
    "builder/analysis/2026-07-25-mutual-knn-stranding/reciprocity.py",
)

# Probes that CALL build_from_archive and are era-pinned to reproduce their
# own committed figures. A new build-affecting default changes what they build.
# cre_build.py added 2026-08-05: it postdates this list, builds through
# defaults, and its cells carry exactly the two 2026-08-03-era drops — the
# ULF- default would have drifted it silently, which is this guard's case.
ERA_PINNED_CALLERS = (
    "builder/analysis/2026-07-29-algb-trial-build/grt_score.py",
    "builder/analysis/2026-07-29-trial-crawl-calibration/calibrate.py",
    "builder/analysis/2026-08-03-cap-reevaluation/cre_build.py",
)

RECORDED_FIELDS = frozenset(
    {
        "algorithm",
        "similar_artists_url",
        "sitewide_artists_url",
        "target_artist_count",
        "requests_per_second",
        "max_retries",
        "timeout_seconds",
        "checkpoint_every",
        "max_neighbours_per_artist",
        "cap_strategy",
        "similarity_damping",
        "similarity_rescale",
        "filter_special_purpose",
        "drop_no_release_tail",
        # Added 2026-08-03 (featured-credit filter). Per-mirror decision at
        # that date: all three mirrors stay deliberately frozen — the same
        # recorded decision as for drop_no_release_tail, since each reproduces
        # committed pre-drop output — and both era-pinned callers now pin
        # drop_featured_credit=False beside the earlier pin.
        "drop_featured_credit",
        # Added 2026-08-05 (un-listenable filter, ULF-). Per-mirror decision:
        # all three mirrors stay deliberately frozen, same recorded reason;
        # all three era-pinned callers (cre_build.py newly listed) pin
        # drop_unlistenable=False beside the earlier pins.
        "drop_unlistenable",
        # Added 2026-08-05 (MSW-, the trimmed-union supply rule). Per-mirror
        # decision AT THIS DATE: nothing changes, because both fields are read
        # only when `cap_strategy == "trimmed_union"` and the DEFAULT is still
        # mutual_knn. All three mirrors stay frozen; all three era-pinned
        # callers keep building exactly what they built yesterday.
        #
        # ⚠ THE FLIP IS THE BUILD-AFFECTING EVENT, NOT THESE FIELDS. When the
        # `cap_strategy` default becomes "trimmed_union" at adoption (MSW-
        # plan Task 11), all three ERA_PINNED_CALLERS silently change what
        # they build: every one constructs BuilderConfig WITHOUT setting
        # cap_strategy, so each inherits the default. They must pin
        # cap_strategy="mutual_knn" beside their existing drop pins in that
        # same commit.
        #
        # cre_build.py is the sharp case and is worth naming: its gate()
        # compares `assemble_cleaned` against a live `build_from_archive` for
        # byte-identity (cre_build.py:410). Its mirror takes an explicit
        # cap_step, so after an unpinned flip that gate would be comparing two
        # DIFFERENT cap rules — and reporting the difference as a mirror
        # divergence, which is the wrong diagnosis for the right symptom.
        "union_top_j",
        "union_degree_ceiling",
        # Added 2026-08-05 (MSW-, fame). Per-mirror decision AT THIS DATE: all
        # three mirrors stay frozen and all three era-pinned callers are
        # unaffected, because the default is False — a build reads no fame and
        # emits no fame key, so output is byte-identical to before the field
        # existed (verified: MSW-G1 unchanged).
        #
        # ⚠ Same forward warning as the two fields above, and the SAME commit:
        # flipping require_fame to True at adoption makes every one of the
        # ERA_PINNED_CALLERS refuse to build, because none of their archives
        # has ever had the `fame` stage run against it. They must pin
        # require_fame=False beside cap_strategy="mutual_knn".
        "require_fame",
        # Added 2026-08-09 (SEL-, the per-invocation ULF- payload override).
        # Per-mirror decision AT THIS DATE: all three mirrors stay frozen and
        # all three era-pinned callers are unaffected. The default is None,
        # which selects the same shipped payload the algorithm lookup already
        # returned, so a build that does not pass the flag is byte-identical to
        # one from before the field existed.
        #
        # ⚠ THE FORWARD WARNING HERE IS THE OPPOSITE SHAPE TO THE THREE FIELDS
        # ABOVE, and copying their wording would be wrong. There is no default
        # flip coming for this field: adopting the extended population repoints
        # CANDIDATE_UNLISTENABLE_DROP_LIST_PATH in unlistenable_drop.py, which
        # this field does not go through. That is deliberate — the whole reason
        # the override is per-invocation is that repointing the default changes
        # every future build from the pre-crawl snapshot SILENTLY, because
        # pipeline.py only refuses on artists outside the censused set and a
        # larger list applied to a smaller archive passes.
        #
        # So the field a future reader must watch is not this one. It is the
        # module constant, and the callers at risk from repointing it are those
        # that build with drop_unlistenable left ON — the era-pinned three pin
        # it False, so they read no list at all and are immune either way.
        "unlistenable_list_path",
        "graph_version",
    }
)


def test_a_new_config_field_forces_a_mirror_check():
    current = {field.name for field in fields(BuilderConfig)}
    added = sorted(current - RECORDED_FIELDS)
    removed = sorted(RECORDED_FIELDS - current)
    assert current == RECORDED_FIELDS, (
        f"BuilderConfig changed (added: {added}, removed: {removed}).\n"
        "If the change affects what a build produces, check each copy of the "
        "pipeline before updating RECORDED_FIELDS:\n  "
        + "\n  ".join(PIPELINE_MIRRORS)
        + "\nand confirm these callers still reproduce their committed "
        "figures, era-pinning them if not:\n  "
        + "\n  ".join(ERA_PINNED_CALLERS)
    )


# --- The other half of the gap: metadata added with NO config knob ----------
#
# This module's docstring says the guard above "is deliberately not complete: a
# stage added with no config knob would still slip past". That is not
# hypothetical -- `deezer_ids` (2026-08-02) and `fame_lb` (2026-08-05) both went
# in that way and neither appears anywhere above, so no per-mirror decision was
# ever recorded for them. `LUX-4` is the same shape: three metadata keys, no
# `BuilderConfig` field, `RECORDED_FIELDS` unchanged, every test green.
#
# A metadata key added to `serialise` DOES change what the ERA_PINNED_CALLERS
# build, because all three call `build_from_archive` and it wires these
# unconditionally. It cannot change an edge, a score or a node -- so it is never
# a path-quality question -- but it does change a sha, which is what those
# probes' reproduction claims rest on.
#
# Pinning the emitted key set is the mechanical half of THAT gap.

RECORDED_METADATA_KEYS = frozenset(
    {
        # Always written.
        "mbids",
        "names",
        "disambiguations",
        "popularity",
        # Additive, omitted when empty. Each changed what the era-pinned
        # callers produce on the day it landed.
        "deezer_ids",  # 2026-08-02, BYP-13. Unrecorded at the time.
        "fame_lb",  # 2026-08-05, MSW-. Unrecorded at the time.
        # LUX-4, 2026-09-06. Per-mirror decision AT THIS DATE: all three
        # PIPELINE_MIRRORS stay frozen -- they reimplement the stage order and
        # do not call `build_from_archive`, so they emit none of these keys and
        # reproduce their committed output unchanged. All three
        # ERA_PINNED_CALLERS *do* call it and so now emit three more keys than
        # when their figures were committed; that is the same condition
        # `deezer_ids` and `fame_lb` already put them in, and it is accepted
        # rather than newly introduced here. No knob is added, for the reason
        # recorded at the deezer_ids call site: these change no edge, no score
        # and no node, so there is nothing for a factor table to hold constant.
        "spotify_ids",
        "apple_ids",
        "artist_facts",
    }
)


def test_a_new_metadata_key_forces_a_mirror_check():
    """The half `test_a_new_config_field_forces_a_mirror_check` cannot see.

    Builds a graph with every optional map populated, so the emitted key set is
    the FULL set `serialise` can produce rather than whatever this fixture
    happens to trigger.
    """
    import json
    import struct

    from artistpath_builder.artifact import serialise
    from artistpath_builder.graph import build_graph
    from artistpath_builder.models import ArtistStats, EdgeType

    a, b = "a" * 36, "b" * 36
    graph = build_graph(
        {a: {b: 1.0}, b: {a: 1.0}},
        [
            ArtistStats(mbid=a, name="A", pop_indegree_scaled=2, listen_count=2),
            ArtistStats(mbid=b, name="B", pop_indegree_scaled=1, listen_count=1),
        ],
        EdgeType.BEHAVIOURAL,
        deezer_ids={a: "1"},
        fame_lb_raw={a: 5, b: None},
        spotify_ids={a: "s" * 22},
        apple_ids={a: "123"},
        artist_facts={a: {"type": "Group"}},
    )
    payload = serialise(graph)
    *_, meta_len = struct.Struct("<4sIIIQ").unpack_from(payload)
    emitted = set(json.loads(payload[len(payload) - meta_len :].decode("utf-8")))

    added = sorted(emitted - RECORDED_METADATA_KEYS)
    removed = sorted(RECORDED_METADATA_KEYS - emitted)
    assert emitted == RECORDED_METADATA_KEYS, (
        f"serialise's metadata keys changed (added: {added}, removed: {removed}).\n"
        "A new key changes the sha every ERA_PINNED_CALLER produces, because "
        "each calls build_from_archive:\n  " + "\n  ".join(ERA_PINNED_CALLERS)
        + "\nIt cannot change an edge, a score or a node, so it is never a "
        "path-quality question. Record the per-mirror decision above before "
        "updating RECORDED_METADATA_KEYS."
    )
