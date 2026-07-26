"""Assert the thread pool changes throughput only, never a resolution.

`resolve_fame.py` runs the A11/A15 canonical resolver concurrently over names.
The argument that this is safe — the imported functions hold no module-level
mutable state, so a name's result cannot depend on what else is in flight — is
checked here rather than trusted, because the whole deliverable's ordering rests
on it.

Method: resolve the same names twice, once serially and once through the pool,
and assert the fame-bearing fields are identical. Bypasses both caches so the
network path actually runs.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-low-degree-census/verify_pool_equivalence.py
"""

from __future__ import annotations

import json
import random
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from resolve_fame import resolve_one  # installs transport.py's retry on import

HERE = Path(__file__).resolve().parent
WORKERS = 4  # the value resolve_fame.py actually runs at

# Fields that decide the deliverable: whether the artist is on the list at all,
# and where it ranks. `months_present` is included because it is the auditing
# handle on a sparse obscure artist.
FIELDS = ("matched", "article", "pageviews", "F", "months_present", "via")


def comparable(row: dict) -> dict:
    out = {k: row.get(k) for k in FIELDS}
    guard = row.get("guard")
    if guard is not None:
        out["potentially_notable"] = guard["potentially_notable"]
        out["non_latin_name"] = guard["non_latin_name"]
        out["foreign_found"] = guard["foreign"]["found"]
    return out


def main() -> int:
    doc = json.loads((HERE / "low_degree.json").read_text(encoding="utf-8"))
    names = sorted({r["name"] for r in doc["degree_1"] if r["name"].strip()})
    random.seed(4242)
    # Deliberately mixed: a matched name costs ~1.6 s and a floored one ~11 s,
    # and the floored path is the one with the deep Wikidata fan-out, so a
    # sample of only matched names would not exercise the risk.
    sample = random.sample(names, 10)
    print(f"sample of {len(sample)}: {', '.join(sample)}\n")

    serial = {n: comparable(resolve_one(n)) for n in sample}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        pooled = dict(zip(sample, (comparable(r) for r in pool.map(resolve_one, sample))))

    bad = [n for n in sample if serial[n] != pooled[n]]
    for n in sample:
        mark = "DIFFER" if n in bad else "same  "
        print(f"  {mark}  F={serial[n]['F']:>7.3f}  {n}")
    if bad:
        for n in bad:
            print(f"\n{n}\n  serial {serial[n]}\n  pooled {pooled[n]}")
        raise SystemExit(f"\nFAIL — {len(bad)} name(s) differ; the pool is not neutral")
    print(f"\nPASS — {len(sample)}/{len(sample)} identical serial vs pooled")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
