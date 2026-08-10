"""`JFX-` stage 2: the pair set, `JFX-C4`, `JFX-C5` — everything that needs NO routing.

**Why this runs before the routing harness exists.** Three pre-registered quantities
are pure set operations over the two artifacts' node sets, and one of them is a
**stop**:

- **`JFX-C5`** — *Have famous artists been pushed out?* — fires §4 read 6, **"stop,
  independent of everything above"**, at a bar of 95% (§3, REQ-33). It costs seconds.
- **`JFX-C4`** — *How many more artists can now appear in a journey at all?* — the
  coverage half of the trade §3 reserves to the owner.
- **`AM1.8`'s added report row** — the direct count `|A \\ B|`, which no criterion owns
  and which `C5` is structurally blind to (`C5` looks only at the famous end; the loss
  the mechanisms produce is of obscure, low-degree artists).
- **§2 stage 2** — materialise the pair set: walk the committed candidates **in their
  committed order** and take the **first 100 per stratum present in both artifacts**.
  Report the skipped count; a non-trivial number means the extension REMOVED artists.
  **No redraw on a shortfall** (§2) — the stratum runs short and says so.

So if `C5` fails, the routing harness never needs to be written. That ordering is the
only thing here that is a judgement call rather than the document's instruction.

**Currency.** Strata and the `C5` tier are measured on **`JFX-A`'s** raw `fame_lb`, a
fixed ruler chosen before results exist (§2, §0.1(a)). Nulls are excluded from the
endpoint pool: an artist without a measurement cannot be placed in a fame stratum
(§2's null rule; a null is a measured absence, never a floor — `FAM-AM1.8`).

Reports only. Adopts nothing, deploys nothing, routes nothing.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "api/src"))
sys.path.insert(0, str(HERE))

from artistpath_api.graph_store import GraphStore  # noqa: E402

from jfx_s1_reachability import (  # noqa: E402
    EXPECTED_SHA as ARM_A_SHA,
    GRAPH as ARM_A,
    _raw_fame_from_metadata,
)

ARM_B = ROOT / "builder/scratch/graph-cex-117k.bin"
CANDIDATES = (
    ROOT / "builder/analysis/2026-08-09-jfx-preregistration/jfx_candidate_pairs.json"
)
OUT = HERE / "jfx_pairset.json"

PER_STRATUM = 100        # §2: 100 analysed per stratum, from 150 candidates
C5_TOP_FRACTION = 0.01   # §3: top-1%-by-fame in JFX-A
C5_BAR = 0.95            # §3, REQ-33: below this, the system eliminates famous artists


def load_arm(path: Path, expected_sha: str | None) -> tuple[GraphStore, list, str]:
    """Load an artifact and assert its identity. `B`'s sha comes from its sidecar.

    `session-start` §C: several graphs exist in `builder/scratch/` and they are NOT
    interchangeable; a conclusion drawn from the wrong artifact looks exactly like a
    correct one. `A`'s sha is pinned in source. `B` has no pinned sha — it is built
    by this track — so it is checked against the manifest the build wrote beside it,
    which also proves the pair (artifact, manifest) belong together.
    """
    if not path.is_file():
        raise SystemExit(f"missing artifact: {path}")
    payload = path.read_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    if expected_sha is None:
        sidecar = path.with_suffix(path.suffix + ".json")
        if not sidecar.is_file():
            raise SystemExit(f"no manifest sidecar beside {path.name}")
        manifest = json.loads(sidecar.read_text(encoding="utf-8"))
        expected_sha = manifest["sha256"]
        acceptance = manifest.get("acceptance", {})
        if acceptance.get("passed") is not False:
            print(f"  ⚠ {path.name}: manifest does not record the expected "
                  f"acceptance REJECTION — check this is the JFX- diagnostic build")
    if sha != expected_sha:
        raise SystemExit(
            f"WRONG ARTIFACT {path.name}: expected {expected_sha}, got {sha}"
        )
    store = GraphStore.from_bytes(payload)
    return store, _raw_fame_from_metadata(payload), sha


def main() -> int:
    print("=" * 72)
    print("JFX- stage 2 — pair set, C4, C5. No routing.")
    print("=" * 72 + "\n")

    a_store, a_fame, a_sha = load_arm(ARM_A, ARM_A_SHA)
    print(f"JFX-A  {ARM_A.name}  {a_store.artist_count:,} nodes  {a_sha[:12]}…")
    b_store, b_fame, b_sha = load_arm(ARM_B, None)
    print(f"JFX-B  {ARM_B.name}  {b_store.artist_count:,} nodes  {b_sha[:12]}…\n")

    a_ids = set(a_store.mbids)
    b_ids = set(b_store.mbids)
    both = a_ids & b_ids
    only_a = a_ids - b_ids
    only_b = b_ids - a_ids

    # ---- JFX-C4 (coverage) and AM1.8's |A \ B| report row ------------------
    print("JFX-C4 — how many more artists can appear in a journey at all?")
    print(f"   in JFX-A only:  {len(only_a):,}")
    print(f"   in both:        {len(both):,}")
    print(f"   in JFX-B only:  {len(only_b):,}")
    print(f"   net change:     {b_store.artist_count - a_store.artist_count:+,}")
    print(f"\nAM1.8 report row — the direct count |A \\ B|: {len(only_a):,}")
    print("   (no criterion owns this; C5 is structurally blind to it, because")
    print("    the loss these mechanisms produce is of obscure, low-degree artists)\n")

    # ---- JFX-C5 (the floor) ------------------------------------------------
    # JFX-A's own raw fame, nulls excluded — the fixed ruler (§2).
    a_raw = np.array(
        [np.nan if v is None else float(v) for v in a_fame], dtype=np.float64
    )
    measured = ~np.isnan(a_raw)
    cut = np.quantile(a_raw[measured], 1.0 - C5_TOP_FRACTION)
    top = [
        a_store.mbids[i]
        for i in np.flatnonzero(measured & (a_raw >= cut))
    ]
    survived = sum(1 for m in top if m in b_ids)
    share = survived / len(top) if top else 0.0
    c5_pass = share >= C5_BAR

    print("JFX-C5 — have famous artists been pushed out?  (FLOOR, REQ-33)")
    print(f"   JFX-A's top-1%-by-fame pool: {len(top):,} artists (cut {cut:,.0f})")
    print(f"   still present in JFX-B:      {survived:,} ({share * 100:.2f}%)")
    print(f"   bar: {C5_BAR * 100:.0f}%  →  {'PASS' if c5_pass else '**FAIL**'}\n")

    # ---- §2 stage 2: the pair set -----------------------------------------
    doc = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    strata: dict[str, list] = {}
    skipped: dict[str, int] = {}
    short: list[str] = []
    print("§2 stage 2 — the pair set, committed order, first 100 per stratum")
    for stratum in sorted(doc["strata"]):
        taken, missed = [], 0
        for a, b in doc["strata"][stratum]:
            if len(taken) == PER_STRATUM:
                break
            if a in both and b in both:
                taken.append([a, b])
            else:
                missed += 1
        strata[stratum] = taken
        skipped[stratum] = missed
        flag = ""
        if len(taken) < PER_STRATUM:
            short.append(stratum)
            flag = "  ⚠ SHORT — reported, NOT topped up (§2: no redraw)"
        print(f"   {stratum}: {len(taken):3d} pairs, {missed:3d} candidates "
              f"skipped{flag}")
    total_skipped = sum(skipped.values())
    candidates = sum(len(v) for v in doc["strata"].values())
    print(f"\n   total candidates skipped: {total_skipped} of {candidates}")
    print("   §2 asks for this count because a NON-TRIVIAL one would mean the")
    print("   extension removed artists the adopted map has. Read it against")
    print(f"   |A \\ B| = {len(only_a):,} above; the two measure the same loss.")
    print("   No threshold is applied here — §2 asks for the number reported, and")
    print("   inventing a bar after seeing it would be a criterion, not a report.")

    OUT.write_text(json.dumps({
        "status": "JFX- stage 2. No routing, no outcome statistic.",
        "governing": "specs/2026-08-09-journey-fame-exposure-preregistration.md §2/§3",
        "arms": {
            "JFX-A": {"artifact": ARM_A.name, "sha256": a_sha,
                      "nodes": a_store.artist_count},
            "JFX-B": {"artifact": ARM_B.name, "sha256": b_sha,
                      "nodes": b_store.artist_count},
        },
        "JFX-C4": {
            "only_in_A": len(only_a), "in_both": len(both),
            "only_in_B": len(only_b),
            "net": b_store.artist_count - a_store.artist_count,
        },
        "AM1.8_direct_count_A_minus_B": len(only_a),
        "JFX-C5": {
            "top_fraction": C5_TOP_FRACTION, "cut": float(cut),
            "pool": len(top), "survived": survived, "share": share,
            "bar": C5_BAR, "pass": bool(c5_pass),
        },
        "pair_set": {
            "per_stratum_target": PER_STRATUM,
            "strata": strata,
            "skipped": skipped,
            "short_strata": short,
        },
    }, indent=1), encoding="utf-8")
    print(f"\nwrote {OUT.name}")

    if not c5_pass:
        print("\n" + "=" * 72)
        print("JFX-C5 FAILED — §4 read 6: STOP, independent of everything above.")
        print("REQ-33 is not tradeable. Do not proceed to routing without the owner.")
        print("=" * 72)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
