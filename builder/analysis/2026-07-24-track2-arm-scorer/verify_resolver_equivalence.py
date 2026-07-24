"""Prove the fame.py recall fallback did NOT change the validated proxy.

A11 adopted Wikipedia pageviews with the canonical `fetch_pageviews.resolve`. `fame.py`
adds an English-article recall fallback for names opensearch's top-5 buries (Justice,
Rainbow, Ye). That is defensible as a bug fix ONLY if it leaves the §5 validation sample's
result exactly as validated — every artist the validated resolver matched still matched to
the same article, and every one it failed still fails. The fallback must only ever recover
a match on names the sample did not contain; on the sample itself it must be inert.

This script asserts that, on the committed 29-artist sample, by comparing the fallback's
verdict against the committed `pageview_counts.json` the falsifiers were computed from.
A single divergence means the instrument moved and the validation no longer describes it.

Run:  PYTHONIOENCODING=utf-8 python -u verify_resolver_equivalence.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROXY = HERE.parent / "2026-07-24-track2-fame-proxy-wikipedia"
sys.path.insert(0, str(HERE))

from fame import english_article_fallback  # noqa: E402


def main() -> int:
    counts = json.loads((PROXY / "pageview_counts.json").read_text(encoding="utf-8"))
    rows = counts["rows"]

    changed = []
    checked = 0
    for r in rows:
        if r.get("matched"):
            continue  # a match the validated resolver made; the fallback never runs for it
        checked += 1
        fb = english_article_fallback(r["query"])
        if fb["found"]:
            changed.append((r["query"], fb["article"], fb["pageviews"]))

    print(f"validated sample: {len(rows)} artists, {checked} unmatched by the canonical resolver")
    if changed:
        print(f"\n*** FALLBACK CHANGED {len(changed)} SAMPLE VERDICT(S) — instrument moved ***")
        for q, art, pv in changed:
            print(f"  {q!r} would now match '{art}' ({pv:,} views)")
        print("\nThe §5 falsifiers were computed on the OLD split. If any of these are")
        print("genuine recoveries, the proxy must be re-scored and A11 revisited; if they")
        print("are wrong matches, the fallback is too loose. Either way: STOP.")
        return 1

    print(f"\nAll {checked} sample non-matches STAY non-matches under the fallback.")
    print("The validated matched/unmatched split is preserved byte-for-byte, so the §5")
    print("falsifiers still describe the scoring instrument. The fallback is inert on the")
    print("validation set and strictly additive off it — a recall bug fix, not a proxy change.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
