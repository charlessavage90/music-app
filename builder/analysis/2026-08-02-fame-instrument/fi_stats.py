"""FAM-1 / FAM-2 / FAM-5 validation figures over the frozen union snapshot.

Governing document:
  docs/superpowers/specs/2026-08-02-fame-instrument-adoption-preregistration.md
  (`FAM-`), §3 as amended by `FAM-AM1`.1/.2/.6.

FIGURES ONLY, NO VERDICTS. This script computes numbers and writes them to
`fi_validation.json`; reading them against the pre-registered bars is the
controller's step, not this script's. Nothing here prints or stores a value
keyed to an artist NAME: `FAM-3` and `FAM-4` read named artists and are gated
behind an identity-confirmation step this script deliberately does not perform,
so every quantity below is an aggregate.

THE PERCENTILE, EXACTLY AS FIXED IN `FAM-AM1`.6
    fame_lb_pctl(v) = (|{f < v}| + (|{f = v}| + 1) / 2) / N_nonnull
  where `f` ranges over the ADOPTED frame's non-null `fame_lb_raw` values and
  `N_nonnull` is that non-null count -- NOT the frame size. For `v` above the
  frame maximum, `pctl(v) = pctl(max)`. "Lower half" is `{fame_lb_pctl < 0.5}`
  and never a sorted-index split, because artists tie across the boundary value
  and membership must not depend on sort stability.

  `ALG-B`-only artists are outside the frame and receive the percentile their
  raw value would occupy in it (§1). So their TIE ATOMS are counted over their
  own population while their PERCENTILES map through the adopted frame -- both
  shares are reported for every remainder statistic, because the two
  denominators answer different questions and neither alone is the figure.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-08-02-fame-instrument/fi_stats.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
_TRACK_B = HERE.parent / "2026-07-30-track-b-cap-selection"
if str(_TRACK_B) not in sys.path:
    sys.path.insert(0, str(_TRACK_B))

from cb_metrics import ADOPTED, ADOPTED_SHA, BANDS, band_of, fame_frame  # noqa: E402

from artistpath_builder.artifact import deserialise  # noqa: E402

SCRATCH = HERE.parents[1] / "scratch"
CANDIDATE = SCRATCH / "graph-algb-full.bin"
CANDIDATE_SHA = "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f"

NEW_SNAPSHOT = HERE / "fi_union_snapshot.json"

# The retained 2026-07-30 snapshot: `FAM-5`'s comparator, never merged into the
# new one (§1, "no splicing of two dates"). Pinned by sha because it is
# uncommitted and a re-fetch over it would silently change the comparison.
OLD_SNAPSHOT = HERE.parent / "2026-07-30-fame-proxy-coverage" / "fp_listenbrainz.json"
OLD_SNAPSHOT_SHA = "c47fbd2260eaf76473a24348785c42ba87d457ced216b6999e036971cebe6fbf"

EXPECTED_UNION = 93_067
EXPECTED_REMAINDER = 18_874

OUT = HERE / "fi_validation.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for blk in iter(lambda: fh.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Rank correlation with average ranks over ties (scipy-free).

    Verbatim from fam_probe.py, the critique probe, so the two are comparable.
    """
    def rank(x: np.ndarray) -> np.ndarray:
        order = np.argsort(x, kind="mergesort")
        s = x[order]
        r = np.empty(len(x), dtype=np.float64)
        i = 0
        while i < len(s):
            j = i
            while j + 1 < len(s) and s[j + 1] == s[i]:
                j += 1
            r[order[i: j + 1]] = (i + j) / 2.0 + 1.0
            i = j + 1
        return r

    ra, rb = rank(a.astype(np.float64)), rank(b.astype(np.float64))
    ra = ra - ra.mean()
    rb = rb - rb.mean()
    denom = float(np.sqrt((ra * ra).sum() * (rb * rb).sum()))
    if denom == 0.0:
        return float("nan")  # a band with no variation on one side
    return float((ra * rb).sum() / denom)


class Frame:
    """The adopted frame's non-null value distribution, and pctl() over it."""

    def __init__(self, values: np.ndarray):
        self.n = int(len(values))
        cnt = Counter(values.tolist())
        self.uniq = np.array(sorted(cnt), dtype=np.int64)
        self.counts = np.array([cnt[int(v)] for v in self.uniq], dtype=np.int64)
        # |{f < v}| for each distinct v present in the frame.
        self.less = np.concatenate([[0], np.cumsum(self.counts)[:-1]])
        # pctl at each distinct value present.
        self.pctl_at = (self.less + (self.counts + 1) / 2.0) / self.n
        self.max_pctl = float(self.pctl_at[-1])

    def pctl(self, values: np.ndarray) -> np.ndarray:
        v = np.asarray(values, dtype=np.int64)
        idx = np.searchsorted(self.uniq, v, side="left")
        # |{f < v}| works for present and absent values alike: searchsorted-left
        # lands on the first frame value >= v, so everything before it is < v.
        below = np.where(idx > 0, self.less[np.clip(idx - 1, 0, None)]
                         + self.counts[np.clip(idx - 1, 0, None)], 0)
        present = (idx < len(self.uniq)) & (self.uniq[np.clip(idx, 0, len(self.uniq) - 1)] == v)
        eq = np.where(present, self.counts[np.clip(idx, 0, len(self.uniq) - 1)], 0)
        out = (below + (eq + 1) / 2.0) / self.n
        # Above the frame maximum, pctl(v) = pctl(max) -- FAM-AM1.6.
        return np.where(v > self.uniq[-1], self.max_pctl, out)


def atom_stats(values: np.ndarray, denom_own: int, denom_frame: int,
               top_k: int = 5) -> dict:
    """Tie-atom structure of one population, under BOTH denominators."""
    if len(values) == 0:
        return {"population": 0}
    cnt = Counter(values.tolist())
    ordered = cnt.most_common()
    largest_v, largest_c = ordered[0]
    top = ordered[:top_k]
    return {
        "population": int(len(values)),
        "distinct_values": len(cnt),
        "largest_tie_atom_artists": int(largest_c),
        "largest_tie_atom_value": int(largest_v),
        "largest_tie_atom_share_of_own_population": largest_c / denom_own,
        "largest_tie_atom_share_of_adopted_nonnull": largest_c / denom_frame,
        "top5_tie_atom_artists": int(sum(c for _, c in top)),
        "top5_tie_atom_values": [int(v) for v, _ in top],
        "top5_share_of_own_population": sum(c for _, c in top) / denom_own,
        "top5_share_of_adopted_nonnull": sum(c for _, c in top) / denom_frame,
    }


def main() -> None:
    if sha256_file(OLD_SNAPSHOT) != OLD_SNAPSHOT_SHA:
        raise SystemExit("2026-07-30 comparator snapshot sha256 mismatch")
    if not NEW_SNAPSHOT.exists():
        raise SystemExit(f"{NEW_SNAPSHOT.name} not found -- run fi_fetch.py first")
    if sha256_file(CANDIDATE) != CANDIDATE_SHA:
        raise SystemExit("ALG-B candidate artifact sha256 mismatch")

    new = json.loads(NEW_SNAPSHOT.read_text(encoding="utf-8"))
    old_raw = json.loads(OLD_SNAPSHOT.read_text(encoding="utf-8"))
    # The 2026-07-30 capture stored {"users", "listens"}; this one stores the
    # integer directly. Same quantity, different container.
    old = {m: (None if v is None else v["users"]) for m, v in old_raw.items()}

    frame_pop = fame_frame()  # asserts ADOPTED_SHA; mbid -> pop_raw PERCENTILE
    adopted_mbids = set(frame_pop)
    candidate_mbids = set(deserialise(CANDIDATE.read_bytes()).mbids)
    remainder_mbids = candidate_mbids - adopted_mbids

    if len(new) != EXPECTED_UNION:
        raise SystemExit(f"snapshot has {len(new):,} keys, expected {EXPECTED_UNION:,}")

    # ---------------- FAM-1: coverage ----------------
    def coverage(mbids: set[str]) -> dict:
        vals = [new.get(m) for m in mbids]
        non_null = sum(1 for v in vals if v is not None)
        missing_key = sum(1 for m in mbids if m not in new)
        return {
            "population": len(mbids),
            "non_null": non_null,
            "null": len(mbids) - non_null,
            "absent_key": missing_key,
            "non_null_share": non_null / len(mbids),
        }

    fam1 = {
        "union": coverage(adopted_mbids | candidate_mbids),
        "adopted_population": coverage(adopted_mbids),
        "alg_b_only_remainder": coverage(remainder_mbids),
        "expected_remainder_population": EXPECTED_REMAINDER,
    }

    # ---------------- the frame, and every percentile ----------------
    adopted_vals = np.array(
        [new[m] for m in sorted(adopted_mbids) if new.get(m) is not None],
        dtype=np.int64,
    )
    frame = Frame(adopted_vals)
    adopted_pctl = frame.pctl(adopted_vals)

    rem_sorted = sorted(remainder_mbids)
    rem_vals = np.array(
        [new[m] for m in rem_sorted if new.get(m) is not None], dtype=np.int64
    )
    rem_pctl = frame.pctl(rem_vals) if len(rem_vals) else np.array([])

    # ---------------- FAM-2: tail resolution ----------------
    def fam2_for(values: np.ndarray, pctls: np.ndarray, label: str) -> dict:
        own_n = int(len(values))
        overall = atom_stats(values, own_n, frame.n)
        decile = values[pctls < 0.10]
        lower = values[pctls < 0.50]
        block = {
            "population_non_null": own_n,
            "overall": overall,
            "bottom_decile_pctl_lt_0.10": atom_stats(
                decile, max(1, len(decile)), frame.n
            ),
            "lower_half_pctl_lt_0.50": atom_stats(
                lower, max(1, len(lower)), frame.n
            ),
        }
        # Quantisation step in fame_lb_pctl space actually experienced by this
        # population: the largest jump between consecutive distinct values it
        # holds. Reported alongside the prereg's largest-atom/N form because the
        # two coincide on the frame and diverge on the remainder.
        uv = np.unique(values)
        if len(uv) > 1:
            p = frame.pctl(uv)
            block["max_consecutive_mapped_pctl_gap"] = float(np.diff(p).max())
            below_decile = p < 0.10
            if below_decile.sum() > 1:
                block["max_consecutive_mapped_pctl_gap_bottom_decile"] = float(
                    np.diff(p[below_decile]).max()
                )
        block["label"] = label
        return block

    fam2 = {
        "adopted_frame": fam2_for(adopted_vals, adopted_pctl, "adopted frame"),
        "alg_b_only_remainder": fam2_for(rem_vals, rem_pctl, "ALG-B-only remainder"),
        "frame_n_nonnull": frame.n,
        "note": "largest_tie_atom_share_of_adopted_nonnull is the prereg's "
                "quantisation step (largest tie atom / N_nonnull); on the "
                "remainder the same atom is also reported over the remainder's "
                "own population.",
    }

    # ---------------- FAM-5: snapshot stability ----------------
    old_vals = np.array(
        [old[m] for m in sorted(old) if old.get(m) is not None], dtype=np.int64
    )
    old_frame = Frame(old_vals)

    overlap = sorted(
        m for m in old
        if old.get(m) is not None and m in new and new.get(m) is not None
    )
    o = np.array([old[m] for m in overlap], dtype=np.int64)
    nw = np.array([new[m] for m in overlap], dtype=np.int64)
    d_pctl = np.abs(frame.pctl(nw) - old_frame.pctl(o))

    bands = {}
    for name, lo, hi in BANDS:
        members = [i for i, m in enumerate(overlap)
                   if (b := band_of(frame_pop.get(m, -1.0))) == name]
        if not members:
            bands[name] = {"n": 0}
            continue
        idx = np.array(members)
        bands[name] = {
            "n": len(members),
            "spearman_old_vs_new": spearman(o[idx], nw[idx]),
            "p99_abs_delta_fame_lb_pctl": float(np.percentile(d_pctl[idx], 99)),
            "max_abs_delta_fame_lb_pctl": float(d_pctl[idx].max()),
        }

    fam5 = {
        "old_snapshot": {"file": OLD_SNAPSHOT.name, "sha256": OLD_SNAPSHOT_SHA,
                         "keys": len(old),
                         "non_null": int(len(old_vals))},
        "overlap_non_null_mbids": len(overlap),
        "spearman_overall_descriptive": spearman(o, nw),
        "abs_delta_fame_lb_pctl": {
            "p50": float(np.percentile(d_pctl, 50)),
            "p95": float(np.percentile(d_pctl, 95)),
            "p99": float(np.percentile(d_pctl, 99)),
            "max": float(d_pctl.max()),
            "share_exceeding_0.01": float((d_pctl > 0.01).mean()),
        },
        "by_band": bands,
        "band_definition": "cb_metrics.BANDS over the adopted artifact's "
                           "pop_raw percentile (in-graph popularity), not fame",
        "value_movement_descriptive": {
            "unchanged_raw": int((o == nw).sum()),
            "increased_raw": int((nw > o).sum()),
            "decreased_raw": int((nw < o).sum()),
        },
    }

    payload = {
        "governing_document":
            "docs/superpowers/specs/"
            "2026-08-02-fame-instrument-adoption-preregistration.md",
        "computed": "FAM-1, FAM-2 (per FAM-AM1.2), FAM-5 (per FAM-AM1.1). "
                    "FAM-3 and FAM-4 are NOT computed here: they read named "
                    "artists and are gated behind FAM-AM1.4's identity "
                    "confirmation.",
        "verdicts": None,
        "snapshot": {
            "file": NEW_SNAPSHOT.name,
            "sha256": sha256_file(NEW_SNAPSHOT),
            "keys": len(new),
        },
        "substrate": {
            "adopted": {"file": ADOPTED.name, "sha256": ADOPTED_SHA},
            "candidate_alg_b": {"file": CANDIDATE.name, "sha256": CANDIDATE_SHA},
        },
        "percentile_definition":
            "(|{f<v}| + (|{f=v}|+1)/2) / N_nonnull over the adopted frame's "
            "non-null fame_lb_raw; pctl(v>max) = pctl(max); lower half is "
            "{fame_lb_pctl < 0.5} (FAM-AM1.6)",
        "FAM-1": fam1,
        "FAM-2": fam2,
        "FAM-5": fam5,
    }
    OUT.write_text(json.dumps(payload, indent=1, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=1, sort_keys=True))
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
