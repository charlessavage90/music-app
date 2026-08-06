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
