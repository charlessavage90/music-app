"""LBS list-length check -- does the `limit` token govern candidate-list length?

Supports `docs/superpowers/findings/2026-07-30-lb-algorithm-semantics.md` (LBS-3).

The question: `ALG-C` is the only permitted algorithm value with `limit_50`; every
other arm carries `limit_100`. If `limit` were a hard cap on the number of similar
artists returned, ALG-C's candidate lists should top out at 50. The upstream source
(`listenbrainz_spark/similarity/artist.py`, quoted in the findings note) says the
limit is "instructive only, upto 2x number of recordings may be returned", which
predicts ALG-C lists of up to 100 instead.

Reads the committed AS raw records (200 artists x 6 arms, fetched 2026-07-29 under
`specs/2026-07-29-algorithm-selection-preregistration.md`) -- no network, no new
requests. Reports per arm: n responses, min / median / max candidate-list length,
and how many responses sit exactly at the arm's maximum.

Run from `builder/`:
    UV_LINK_MODE=copy uv run python analysis/2026-07-30-lb-source-semantics/lbs_list_lengths.py
"""

from __future__ import annotations

import json
import statistics
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE.parent / "2026-07-29-cap-selection-sim" / "as_raw_records.json"
OUT = HERE / "lbs_list_lengths.json"

ARM_ORDER = ("ALG-E", "ALG-B", "ALG-A", "ALG-F", "ALG-D", "ALG-C")


def main() -> None:
    data = json.loads(RAW.read_text(encoding="utf-8"))

    lengths: dict[str, list[int]] = defaultdict(list)
    for record in data["records"]:
        if record["status"] == 200:
            lengths[record["arm"]].append(len(record["candidates"]))

    result = {
        "source": str(RAW.relative_to(HERE.parents[2])),
        "arms": {arm: data["arms"][arm] for arm in ARM_ORDER},
        "list_lengths": {},
    }
    print(f"{'arm':7} {'n':>4} {'min':>4} {'median':>7} {'max':>4}  at-max")
    for arm in ARM_ORDER:
        values = sorted(lengths[arm])
        row = {
            "n": len(values),
            "min": values[0],
            "median": statistics.median(values),
            "max": values[-1],
            "at_max": sum(1 for v in values if v == values[-1]),
        }
        result["list_lengths"][arm] = row
        print(
            f"{arm:7} {row['n']:>4} {row['min']:>4} {row['median']:>7} "
            f"{row['max']:>4}  {row['at_max']}"
        )

    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT.name}")


if __name__ == "__main__":
    main()
