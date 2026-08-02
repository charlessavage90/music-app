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
ERA_PINNED_CALLERS = (
    "builder/analysis/2026-07-29-algb-trial-build/grt_score.py",
    "builder/analysis/2026-07-29-trial-crawl-calibration/calibrate.py",
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
