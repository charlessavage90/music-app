"""Does the bulk candidate filter ever lose a name the canonical resolver matched?

`sparql_candidates.py` is only sound as a cost saving if its recall is at least the
canonical A11/A15 resolver's. If it misses a name the canonical resolver would have
matched, that artist is floored — scored as maximally obscure — and **vanishes from
a fame-ranked list without leaving a trace.** That is the same silent, directional
failure `transport.py` was written for, arriving by a different route, so it is
checked rather than argued.

Ground truth is every name already resolved by the canonical instrument:
  - the Track 2 scorer's committed cache (famous path interiors), and
  - the low-degree names this census resolved before the rate limit stopped it,
    which are the population that actually matters here.

**The test is one-sided, deliberately.** A canonical MATCH with no SPARQL candidate
is a fatal miss and fails the run. A SPARQL candidate with no canonical match is
expected and harmless — it only means that name gets asked, which is the safe
direction and costs a request, not a wrong answer.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-low-degree-census/verify_sparql_recall.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-07-24-track2-arm-scorer"))
sys.path.insert(0, str(HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia"))

from sparql_candidates import candidates_for  # noqa: E402


def ground_truth() -> dict[str, dict]:
    rows: dict[str, dict] = {}
    for path in (HERE.parent / "2026-07-24-track2-arm-scorer" / "fame_cache.json",
                 HERE / "fame_cache.json"):
        if path.exists():
            rows.update(json.loads(path.read_text(encoding="utf-8")))
    return rows


def main() -> int:
    truth = ground_truth()
    matched = sorted(n for n, r in truth.items() if r.get("matched") and n.strip())
    floored = sorted(n for n, r in truth.items()
                     if not r.get("matched") and not r.get("nameless") and n.strip())
    print(f"ground truth: {len(matched)} canonical MATCH, {len(floored)} canonical floor\n")

    print(f"querying candidates for {len(matched)} canonically-matched name(s)")
    cand_matched = candidates_for(matched)
    misses = [n for n in matched if not cand_matched.get(n)]

    print(f"\nquerying candidates for {len(floored)} canonically-floored name(s)")
    cand_floored = candidates_for(floored)
    would_ask = [n for n in floored if cand_floored.get(n)]

    print("\n=== recall (the gating half) ===")
    print(f"canonical matches retained by the filter : "
          f"{len(matched) - len(misses)}/{len(matched)}")
    if misses:
        print(f"\nFATAL — {len(misses)} canonical match(es) have NO SPARQL candidate and "
              "would be silently floored:")
        for n in misses[:40]:
            print(f"  - {n}   (canonical article: {truth[n].get('article')})")
        raise SystemExit("\nFAIL — the filter loses matches; it must not be used to floor.")

    print("\n=== precision (the cost half, not gating) ===")
    print(f"canonical floors the filter still asks about: "
          f"{len(would_ask)}/{len(floored)} "
          f"({100 * len(would_ask) / max(len(floored), 1):.0f} %)")
    saved = len(floored) - len(would_ask)
    print(f"canonical floors the filter answers for free: {saved}/{len(floored)} "
          f"({100 * saved / max(len(floored), 1):.0f} %)")
    print("\nPASS — no canonical match is lost. The filter may be used to floor "
          "candidate-less names.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
