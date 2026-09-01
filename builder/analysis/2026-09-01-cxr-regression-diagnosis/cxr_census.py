"""`CXR-` — descriptive census of the two artifacts, run 2026-09-01.

Answers `CXR-P1`, `CXR-P2` and `CXR-P3` from `PREDICTIONS.md`, which was committed
before this ran. Nothing here routes, adopts, or fixes a criterion: every figure is a
property of the two files on disk.

Run from `api/` so the shipped `GraphStore` parses both artifacts:

    cd api && UV_LINK_MODE=copy uv run python \
      ../builder/analysis/2026-09-01-cxr-regression-diagnosis/cxr_census.py

The parser is the SHIPPED one, deliberately: a second implementation here could
disagree with what the API actually loads, which is the class of defect the `JFX-`
mirror re-verification exists to catch.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from artistpath_api.graph_store import GraphStore

SCRATCH = Path(__file__).resolve().parents[3] / "builder" / "scratch"
OLD = SCRATCH / "graph-msw-tu50.bin"  # JFX-A, the adopted map, now live again
NEW = SCRATCH / "graph-cxa-adopted.bin"  # CXA-, adopted 2026-08-10, reverted 2026-09-01


def degrees(store: GraphStore) -> np.ndarray:
    """Out-degree per node, straight off the CSR offsets."""
    return np.diff(store.offsets).astype(np.int64)


def fame_raw(path: Path) -> list[int | None]:
    """The raw `fame_lb` list, which GraphStore consumes but does not retain.

    Read through the shipped parser's own framing so the offsets cannot drift:
    header is magic(4) + version(4) + n(4) + e(4) + meta_len(4), then the CSR
    arrays, then the metadata blob. Rather than re-derive that, reuse the fact
    that the blob is the trailing `meta_len` bytes.
    """
    payload = path.read_bytes()
    meta_len = int(np.frombuffer(payload[16:20], dtype="<u4")[0])
    meta = json.loads(payload[len(payload) - meta_len :])
    return meta.get("fame_lb") or []


def pct(part: int, whole: int) -> str:
    return f"{100.0 * part / whole:.2f}%" if whole else "n/a"


def main() -> None:
    old = GraphStore.load(OLD)
    new = GraphStore.load(NEW)

    old_ids = {m: i for i, m in enumerate(old.mbids)}
    new_ids = {m: i for i, m in enumerate(new.mbids)}
    common = [m for m in new.mbids if m in old_ids]
    added = [m for m in new.mbids if m not in old_ids]
    lost = [m for m in old.mbids if m not in new_ids]

    print("=" * 72)
    print("POPULATIONS")
    print("=" * 72)
    print(f"old  {len(old.mbids):>7,} artists   {len(old.neighbours):>10,} csr entries")
    print(f"new  {len(new.mbids):>7,} artists   {len(new.neighbours):>10,} csr entries")
    print(f"common {len(common):>5,}   added {len(added):>6,}   lost {len(lost):>4,}")

    d_old, d_new = degrees(old), degrees(new)
    print(f"\nmean degree  old {d_old.mean():6.2f}   new {d_new.mean():6.2f}")

    # ---- CXR-P2: are the newly added artists cul-de-sacs? ----
    print()
    print("=" * 72)
    print("CXR-P2  degree of added vs pre-existing artists, IN THE NEW ARTIFACT")
    print("=" * 72)
    added_idx = np.array([new_ids[m] for m in added], dtype=np.int64)
    common_idx_new = np.array([new_ids[m] for m in common], dtype=np.int64)
    d_added, d_common_new = d_new[added_idx], d_new[common_idx_new]

    hdr = f"{'set':<16}{'n':>8}{'median':>9}{'mean':>9}{'p10':>7}{'p90':>7}{'deg<=2':>9}"
    print(hdr)
    for label, arr in (("added", d_added), ("pre-existing", d_common_new)):
        print(
            f"{label:<16}{len(arr):>8,}{np.median(arr):>9.1f}{arr.mean():>9.2f}"
            f"{np.percentile(arr, 10):>7.0f}{np.percentile(arr, 90):>7.0f}"
            f"{pct(int((arr <= 2).sum()), len(arr)):>9}"
        )
    ratio = np.median(d_added) / max(1e-9, np.median(d_common_new))
    print(f"\nmedian ratio added/pre-existing = {ratio:.3f}   (CXR-P2 fires below 0.50)")

    # Paired: did the pre-existing artists themselves lose connections?
    d_common_old = d_old[np.array([old_ids[m] for m in common], dtype=np.int64)]
    delta = d_common_new.astype(np.int64) - d_common_old.astype(np.int64)
    print(
        f"pre-existing artists, paired degree change old->new: "
        f"median {np.median(delta):+.1f}  mean {delta.mean():+.2f}  "
        f"lost connections {pct(int((delta < 0).sum()), len(delta))}"
    )

    # ---- CXR-P1: is the fame ruler diluted? ----
    print()
    print("=" * 72)
    print("CXR-P1  fame-ruler coverage (measured listener counts)")
    print("=" * 72)
    f_old_raw, f_new_raw = fame_raw(OLD), fame_raw(NEW)
    if not f_new_raw:
        print("new artifact carries NO fame_lb at all -- ramp inert. Stop.")
        return
    measured_new = np.array([v is not None for v in f_new_raw])
    measured_old = (
        np.array([v is not None for v in f_old_raw])
        if f_old_raw
        else np.zeros(len(old.mbids), bool)
    )
    print(
        f"old artifact measured {int(measured_old.sum()):,} of {len(measured_old):,} "
        f"({pct(int(measured_old.sum()), len(measured_old))})"
    )
    print(
        f"new artifact measured {int(measured_new.sum()):,} of {len(measured_new):,} "
        f"({pct(int(measured_new.sum()), len(measured_new))})"
    )
    added_measured = measured_new[added_idx]
    null_share = 1.0 - added_measured.mean()
    print(
        f"\nADDED artists: {int(added_measured.sum()):,} measured, "
        f"{int((~added_measured).sum()):,} null "
        f"({100.0 * null_share:.2f}% null)"
    )
    print(f"CXR-P1 is REFUTED as a mechanism at >= 70% null -> {null_share >= 0.70}")

    # ---- CXR-M3: paired fame-percentile shift for artists in both maps ----
    print()
    print("=" * 72)
    print("CXR-M3  fame percentile, paired over the artists present in BOTH maps")
    print("=" * 72)
    if old.fame_lb_pctl is None or new.fame_lb_pctl is None:
        print("one artifact carries no fame percentile; skipping")
    else:
        p_old = old.fame_lb_pctl[np.array([old_ids[m] for m in common])]
        p_new = new.fame_lb_pctl[common_idx_new]
        d = p_new - p_old
        moved = np.abs(d) > 1e-9
        print(
            f"median {np.median(d):+.4f}   mean {d.mean():+.4f}   "
            f"moved {pct(int(moved.sum()), len(d))}   "
            f"rose {pct(int((d > 1e-9).sum()), len(d))}"
        )
        print(f"p10 {np.percentile(d, 10):+.4f}   p90 {np.percentile(d, 90):+.4f}")
        print("(CXR-P1's confirming half wants a median above +0.02)")

    # ---- CXR-P3: was the popularity currency re-censused? ----
    print()
    print("=" * 72)
    print("CXR-P3  pop_raw, paired over the artists present in BOTH maps")
    print("=" * 72)
    q_old = old.pop_raw[np.array([old_ids[m] for m in common])].astype(np.float64)
    q_new = new.pop_raw[common_idx_new].astype(np.float64)
    dq = q_new - q_old
    print(
        f"median {np.median(dq):+.4f}   mean {dq.mean():+.4f}   "
        f"median |delta| {np.median(np.abs(dq)):.4f}   "
        f"rose {pct(int((dq > 1e-9).sum()), len(dq))}"
    )
    print(f"p10 {np.percentile(dq, 10):+.4f}   p90 {np.percentile(dq, 90):+.4f}")
    print("(CXR-P3 fires at median |delta| > 0.01)")

    # The floor is anchored on the endpoints, so what matters for a first
    # journey is how much min(pop_raw[a], pop_raw[b]) moved -- reported for the
    # famous end of the scale, where the owner says he looked hardest.
    top = q_old >= np.percentile(q_old, 99)
    print(
        f"\ntop 1% by old pop_raw (n={int(top.sum()):,}): "
        f"median delta {np.median(dq[top]):+.4f}"
    )
    print(f"added artists' pop_raw: median {np.median(new.pop_raw[added_idx]):.4f}, "
          f"vs pre-existing {np.median(new.pop_raw[common_idx_new]):.4f}")


if __name__ == "__main__":
    main()
