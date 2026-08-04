"""Shared paths, constants and the fame ruler for the `CRE-` cap re-evaluation.

**Governing document (experimental):**
`docs/superpowers/specs/2026-08-03-cap-reevaluation-preregistration.md` -- frozen
`3d7b7d6`, amended by `CRE-AM1` and `CRE-AM2`. It wins wherever anything here
disagrees with it.
**Operational document:** `docs/superpowers/plans/2026-08-03-cap-reeval-execution-plan.md`
(task `CRE-T1`).

**The ruler (prereg §0.3), restated by citation, never re-derived.** The currency is
`fame_lb_pctl`: the frame is the adopted artifact's non-null `fame_lb_raw` values
(N = 74,151, asserted here as `CRE-G1c`), the union snapshot supplies raw values,
percentiles are mapped out-of-frame, and a value above the frame maximum takes the
maximum's percentile (`FAM-AM1.6`, implemented in the frozen `fi_stats.Frame`, which
is imported rather than copied).

**Retired-currency bar.** No `CRE` module may read `tas_common.fame_frame` or
`cb_metrics.fame_frame` -- both are the pop-percentile / worldly-fame era currency,
retired 2026-08-02. Nothing here imports either.

**Plan pin 2 -- ruler-null nodes are TWO classes, priced separately as a DEVICE input.**
The union snapshot's key set is exactly (adopted node set) union (`ALG-B`-MK50 node
set). So:

- a node **present** in the snapshot with a null value was fetched and ListenBrainz
  recorded no listeners -- below the measurement floor, which under the
  novelty-likelihood construct genuinely is maximal obscurity. Priced `frame.pctl(0)`.
- a node **absent** from the snapshot was never in the fetch population at all -- a
  population artifact, not a listener count. Priced at the no-information neutral
  prior **0.5**, so the device neither seeks nor avoids artists whose obscurity is
  simply unknown.

The analyst measured the *value* choice within the null class as operationally inert
(< 0.25 % of one hop), but the *class* choice as worth 1-2.5 whole hops against
measured p5-p10 artists at r2 and depth. This is a **device** input only: scoring
never treats either class as a value (`FAM-AM1.8`), which is why `pctl_of` returns
`None` and `device_pctl_of` is a separate method.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

_FROZEN = {
    "track2_sweep": ROOT / "builder/analysis/2026-07-23-track2-sweep",
    "track_b": ROOT / "builder/analysis/2026-07-30-track-b-cap-selection",
    "tag_disc": ROOT / "builder/analysis/2026-07-30-tag-discrimination",
    "rel": ROOT / "builder/analysis/2026-07-31-release-tag-coverage",
    "wgt": ROOT / "builder/analysis/2026-08-01-label-weighting",
    "fame": ROOT / "builder/analysis/2026-08-02-fame-instrument",
    "wav": ROOT / "builder/analysis/2026-08-03-within-artist-votes",
    "api_src": ROOT / "api/src",
}


def use_frozen(*names: str) -> None:
    for n in names:
        p = str(_FROZEN[n])
        if p not in sys.path:
            sys.path.insert(0, p)


ADOPTED = ROOT / "builder/scratch/graph-t15-tiebreakfix.bin"
# Source: the tiebreak-fix-adoption findings' checksum, as pinned by
# run_arms_t3.py and fi_union_snapshot.manifest.json. Asserted, never trusted.
ADOPTED_SHA = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"

SNAPSHOT = _FROZEN["fame"] / "fi_union_snapshot.json"
SNAPSHOT_MANIFEST = _FROZEN["fame"] / "fi_union_snapshot.manifest.json"
PAIRS = _FROZEN["track_b"] / "cb_pairs.json"
FAMOUS_CLASSES = ("ff-top01pct", "ff-top1pct")

FRAME_N = 74_151                    # CRE-G1c
RAMPS = {"P1a": 0.01, "P1b": 0.03}  # prereg §3.3
EXTREME_RAMP = 1.0                  # CRE-G2(a), instrument-only
MAX_DEPTH = 20
C1_BAND = range(10, 21)
QUANT_FLOOR = 0.015
MATERIAL = 0.05
BOOTSTRAP_B = 10_000
BOOTSTRAP_SEED = 20260803


def in_dir(arg: str) -> Path:
    """run_arms_t3.py's bare-filename rule; closes the Snyk traversal class."""
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename in {HERE}, got {arg!r}")
    return HERE / arg


def load_adopted():
    use_frozen("api_src")
    from artistpath_api.graph_store import GraphStore

    payload = ADOPTED.read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != ADOPTED_SHA:
        raise SystemExit(f"WRONG ARTIFACT: expected {ADOPTED_SHA}, got {got}")
    return GraphStore.from_bytes(payload)


class Ruler:
    """The §0.3 ruler row, and nothing else."""

    def __init__(self) -> None:
        use_frozen("fame", "track_b")
        from fi_stats import Frame  # the committed FAM-AM1.6 implementation

        manifest = json.loads(SNAPSHOT_MANIFEST.read_text(encoding="utf-8"))
        digest = hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest()
        if digest != manifest["sha256"]:
            raise SystemExit("fi_union_snapshot.json does not match its manifest")
        raw = json.loads(SNAPSHOT.read_text(encoding="utf-8"))

        store = load_adopted()
        vals = np.array(
            [raw[m] for m in sorted(store.mbids) if raw.get(m) is not None],
            dtype=np.int64,
        )
        self._frame = Frame(vals)
        self.frame_n = self._frame.n
        if self.frame_n != FRAME_N:
            raise SystemExit(
                f"CRE-G1c FAILED: ruler frame N {self.frame_n} != {FRAME_N}"
            )
        # Pin 2's two unmeasured classes, priced separately. A key PRESENT with
        # value null was fetched and LB recorded no listeners: below the
        # measurement floor, frame.pctl(0). A key ABSENT was never in the fetch
        # population (the snapshot is exactly adopted UNION ALG-B-MK50 -- a
        # population artifact, not a listener count): neutral prior 0.5.
        self.device_null_pctl = float(self._frame.pctl(np.array([0]))[0])
        self.device_absent_pctl = 0.5
        self._null_keys = {m for m, v in raw.items() if v is None}

        keys = [m for m in raw if raw[m] is not None]
        pctls = self._frame.pctl(np.array([raw[m] for m in keys], dtype=np.int64))
        self._pctl = dict(zip(keys, (float(p) for p in pctls)))
        self.min_measured_pctl = float(min(self._pctl.values()))

    def pctl_of(self, mbid: str) -> float | None:
        return self._pctl.get(mbid)

    def status_of(self, mbid: str) -> str:
        if mbid in self._pctl:
            return "measured"
        return "null" if mbid in self._null_keys else "absent"

    def device_pctl_of(self, mbid: str) -> float:
        p = self._pctl.get(mbid)
        if p is not None:
            return p
        return (self.device_null_pctl if mbid in self._null_keys
                else self.device_absent_pctl)

    def arrays(self, store) -> tuple[np.ndarray, np.ndarray]:
        """(measured-with-nan, device) fame arrays aligned to node ids."""
        measured = np.full(len(store.mbids), np.nan)
        device = np.empty(len(store.mbids))
        for i, m in enumerate(store.mbids):
            p = self._pctl.get(m)
            if p is not None:
                measured[i] = p
            device[i] = self.device_pctl_of(m)
        return measured, device


def famous_pairs() -> list[tuple[str, str, str]]:
    doc = json.loads(PAIRS.read_text(encoding="utf-8"))
    pairs = [tuple(t) for t in doc["triples"] if t[0] in FAMOUS_CLASSES]
    if len(pairs) != 22:
        raise SystemExit(f"expected 22 famous pairs, got {len(pairs)}")
    return pairs
