"""Repeat `CXR-M3` / `CXR-M4` (the fame-percentile squeeze) on lux4 -> lba-a6.

Closes `findings/2026-09-16-cxr-revert-and-the-s4-population.md` §5 item 2.
Descriptive only: a property of two files, no routing, nothing adopted.

Currency throughout: FAME PERCENTILE (`fame_lb_pctl`, ListenBrainz listener rank
within each artifact's own measured population). Not `pop_raw`, not degree.

Method, pairing, bins and ramp pricing are copied from
`../2026-09-01-cxr-regression-diagnosis/cxr_census.py` (M3) and
`cxr_compression.py` (M4). ONE deliberate departure, reported both ways: CXR-M3/M4
paired over every shared artist, including measured nulls (which
`fame_percentiles` writes as 0.0). Here the headline pairing DROPS any shared
artist null in either map, and the CXR-literal pairing is printed beside it.

Run from `api/` so the SHIPPED GraphStore parses both artifacts:

    cd api && PYTHONIOENCODING=utf-8 uv run python -u \
      ../builder/analysis/2026-09-25-cxr-squeeze-on-lba-a6/squeeze_lba_a6.py

REFUSES (exit 2) if either file's sha256 disagrees with its own sidecar.
Artifacts are read from the main tree (C:/dev/music-app/builder/scratch).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

SCRATCH = Path("C:/dev/music-app/builder/scratch")
OLD = SCRATCH / "graph-lux4.bin"  # previously served
NEW = SCRATCH / "graph-lba-a6.bin"  # adopted 2026-09-25
# Comparability check only: CXR-M3/M4's old frame was this artifact.
CXR_OLD = SCRATCH / "graph-msw-tu50.bin"


def verify(path: Path) -> str:
    """sha256 of the file must equal its sidecar's `sha256`; exit non-zero if not."""
    sidecar = path.with_name(path.name + ".json")
    want = json.loads(sidecar.read_text(encoding="utf-8"))["sha256"]
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    got = h.hexdigest()
    if got != want:
        print(f"REFUSING: {path.name} sha256 {got} != sidecar {want}", file=sys.stderr)
        sys.exit(2)
    print(f"sha256 OK  {path.name}  {got}")
    return got


# ---- identity FIRST: nothing below is read before both checks pass ----
verify(OLD)
verify(NEW)

from artistpath_api.config import ApiConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402


def fame_raw(path: Path) -> list:
    """Raw `fame_lb` list (GraphStore consumes it but does not retain it).

    Same framing as cxr_census.py: the metadata blob is the trailing meta_len bytes.
    """
    payload = path.read_bytes()
    meta_len = int(np.frombuffer(payload[16:20], dtype="<u4")[0])
    meta = json.loads(payload[len(payload) - meta_len :])
    return meta.get("fame_lb") or []


def pct(a: int, b: int) -> str:
    return f"{100.0 * a / b:.2f}%" if b else "n/a"


EDGES = [0.0, 0.2, 0.4, 0.6, 0.8, 0.9, 0.95, 0.99, 1.0001]  # CXR-M4's bins


def m3(p_old: np.ndarray, p_new: np.ndarray, label: str) -> None:
    d = p_new - p_old
    print(
        f"[{label}] n={len(d):,}  median {np.median(d):+.4f}  mean {d.mean():+.4f}  "
        f"rose {pct(int((d > 1e-9).sum()), len(d))}  "
        f"fell {pct(int((d < -1e-9).sum()), len(d))}  "
        f"p10 {np.percentile(d, 10):+.4f}  p90 {np.percentile(d, 90):+.4f}"
    )


def m4(p_old: np.ndarray, p_new: np.ndarray, w: float, label: str) -> None:
    print(f"\n[{label}] CXR-M4 by position in the OLD (lux4) frame")
    print(f"{'old band':<14}{'n':>8}{'old mean':>10}{'new mean':>10}{'shift':>9}")
    for lo, hi in zip(EDGES, EDGES[1:]):
        m = (p_old >= lo) & (p_old < hi)
        if not m.any():
            continue
        print(
            f"{f'{lo:.2f}-{hi:.2f}':<14}{int(m.sum()):>8,}"
            f"{p_old[m].mean():>10.4f}{p_new[m].mean():>10.4f}"
            f"{(p_new[m] - p_old[m]).mean():>+9.4f}"
        )
    mid = (p_old >= 0.40) & (p_old < 0.60)
    famous = p_old >= 0.99
    gap_old = float(p_old[famous].mean() - p_old[mid].mean())
    gap_new = float(p_new[famous].mean() - p_new[mid].mean())
    print(
        f"gap top-1% minus mid-scale: old {gap_old:.4f}  new {gap_new:.4f}  "
        f"({100.0 * (gap_new - gap_old) / gap_old:+.1f}%)"
    )
    for k in (5, 10, 20):
        print(f"  {k:>2} presses: old {w * k * gap_old:.5f}  new {w * k * gap_new:.5f}")
    ceiling = p_old >= 0.999
    print(
        f"top of old frame (>=0.999, n={int(ceiling.sum()):,}): mean shift "
        f"{(p_new[ceiling] - p_old[ceiling]).mean():+.4f}"
    )


def main() -> None:
    cfg = ApiConfig()
    w = cfg.w_known_ramp_fame_pctl
    print(f"w_known_ramp_fame_pctl = {w}  (ApiConfig default)")

    old = GraphStore.load(OLD)
    new = GraphStore.load(NEW)
    assert old.fame_lb_pctl is not None and new.fame_lb_pctl is not None

    old_ids = {m: i for i, m in enumerate(old.mbids)}
    new_ids = {m: i for i, m in enumerate(new.mbids)}
    common = [m for m in new.mbids if m in old_ids]  # CXR pairing order
    only_new = [m for m in new.mbids if m not in old_ids]
    only_old = [m for m in old.mbids if m not in new_ids]

    print("\nPOPULATIONS")
    print(f"lux4    N={len(old.mbids):,}  E(csr)={len(old.neighbours):,}")
    print(f"lba-a6  N={len(new.mbids):,}  E(csr)={len(new.neighbours):,}")
    print(f"shared {len(common):,}  only-lux4 {len(only_old):,}  only-lba-a6 {len(only_new):,}")

    # ---- nulls, and proof they are outside the frame ----
    f_old, f_new = fame_raw(OLD), fame_raw(NEW)
    assert len(f_old) == len(old.mbids) and len(f_new) == len(new.mbids)
    null_old = np.array([v is None for v in f_old])
    null_new = np.array([v is None for v in f_new])
    print("\nMEASURED NULLS (fame_lb is None)")
    print(f"lux4    {int(null_old.sum()):,} of {len(null_old):,}")
    print(f"lba-a6  {int(null_new.sum()):,} of {len(null_new):,}")

    for label, raw, store, nulls in (
        ("lux4", f_old, old, null_old),
        ("lba-a6", f_new, new, null_new),
    ):
        p = store.fame_lb_pctl
        measured = np.array([float(v) for v in raw if v is not None])
        # (a) nulls are written 0.0 and no NaN survives
        assert not np.isnan(p).any()
        assert np.all(p[nulls] == 0.0)
        # (b) the frame is the measured values ONLY: recompute the rank against the
        # measured-only frame and require an exact match on every measured artist.
        frame = np.sort(measured)
        expect = np.searchsorted(frame, measured, side="left") / max(1, frame.size - 1)
        exact = np.array_equal(p[~nulls], np.clip(expect, 0, 1))
        # (c) the counterfactual: had nulls been in the frame (as zeros), ranks shift
        with_nulls = np.sort(np.concatenate([measured, np.zeros(int(nulls.sum()))]))
        alt = np.searchsorted(with_nulls, measured, side="left") / max(1, with_nulls.size - 1)
        print(
            f"{label}: nulls->0.0 {bool(np.all(p[nulls] == 0.0))}; NaN none; "
            f"measured-only frame reproduces shipped pctl exactly: {exact}; "
            f"max |delta| had nulls been framed as 0: {np.abs(alt - expect).max():.2e}; "
            f"min measured pctl {p[~nulls].min():.4f}, max {p[~nulls].max():.4f}; "
            f"measured artists at pctl 0.0: {int((p[~nulls] == 0.0).sum())}"
        )
        assert exact

    ci_old = np.array([old_ids[m] for m in common], dtype=np.int64)
    ci_new = np.array([new_ids[m] for m in common], dtype=np.int64)
    n_o, n_n = null_old[ci_old], null_new[ci_new]
    either = n_o | n_n
    print(
        f"\nshared artists null in lux4 {int(n_o.sum())}, in lba-a6 {int(n_n.sum())}, "
        f"in both {int((n_o & n_n).sum())}, in EITHER (drop out) {int(either.sum())}"
    )
    print(
        f"null among only-lba-a6 {int(null_new[[new_ids[m] for m in only_new]].sum())}, "
        f"among only-lux4 {int(null_old[[old_ids[m] for m in only_old]].sum())}"
    )

    p_old_all = old.fame_lb_pctl[ci_old]
    p_new_all = new.fame_lb_pctl[ci_new]
    keep = ~either

    print("\nCXR-M3  paired fame-percentile shift (lba-a6 minus lux4, each in own frame)")
    m3(p_old_all[keep], p_new_all[keep], "HEADLINE nulls-in-either dropped")
    m3(p_old_all, p_new_all, "CXR-literal all shared")

    m4(p_old_all[keep], p_new_all[keep], w, "HEADLINE nulls-in-either dropped")
    m4(p_old_all, p_new_all, w, "CXR-literal all shared")

    # Where the added artists sit, in the NEW frame (CXR-M5's first line, fame only)
    oi = np.array([new_ids[m] for m in only_new], dtype=np.int64)
    print(
        f"\nonly-lba-a6 artists' fame pctl median {np.median(new.fame_lb_pctl[oi]):.4f}"
        f"  vs shared {np.median(p_new_all):.4f} (both in lba-a6 frame)"
    )

    # ---- comparability: is lux4's fame frame CXR-M4's old frame? ----
    if CXR_OLD.exists():
        verify(CXR_OLD)
        f_cxr = fame_raw(CXR_OLD)
        cxr = GraphStore.load(CXR_OLD)
        print(
            f"\ncomparability: msw-tu50 mbids == lux4 mbids (same order): "
            f"{cxr.mbids == old.mbids};  fame_lb identical: {f_cxr == f_old}"
        )


if __name__ == "__main__":
    main()
