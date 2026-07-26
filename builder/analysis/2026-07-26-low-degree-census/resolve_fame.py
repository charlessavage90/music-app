"""Fame resolution for the degree-1 / degree-2 census, under amendment A11's encoding.

**The instrument is imported, never reimplemented.** A11 names
`../2026-07-24-track2-fame-proxy-wikipedia/fetch_pageviews.py` canonical for the
name -> article rules, and A15 adds `fame.english_article_fallback` as a strict
recall fix on the identical accept clauses. This module calls those functions
unchanged and adds exactly one thing: a thread pool over NAMES.

    F(a) = log10(1 + en.wikipedia pageviews, 2025-07..2026-06)   matched
    F(a) = 0                                                      unmatched (the fame floor)

**Why a pool, and why it is a throughput change rather than an instrument change.**
Measured serially on a 12-name degree-1 sample: ~1.6 s matched, ~11.4 s floored
(the floored path pays A15's 9-language Wikidata fan-out and then the A11 guard).
At ~50 % matched over 12,088 names that is ~22 h serial. The imported functions
hold no module-level mutable state and each call is self-contained over urllib,
so running N names concurrently cannot change any single name's result; the
`PAUSE_S` sleeps inside them still pace each worker. `verify_pool_equivalence.py`
asserts this against a serial run rather than trusting the argument.

**A15 matters more here than anywhere it has been used.** The deliverable is a
fame-RANKED list, so the exact defect A15 fixed — a household name with an
ambiguous short name (Justice, Rainbow, Ye) scored at the floor because
opensearch buries it — would drop that artist out of the list entirely. That is
a silent omission from the thing the owner is being asked to eyeball, which is
why the fallback is on the critical path and not an optimisation.

**The A11 guard is retained for every floored artist, deliberately.** For Track 2
it gated C2 at d15/d20 only. Here it earns its cost differently: an artist with
no English article but a foreign one is exactly the case that makes a fame-ranked
list misleading by OMISSION, and the owner asked for anything of that kind to be
reported. So `foreign_article` runs on every floored name, and the flagged set is
reported as its own section.

Cache is this directory's own file, seeded read-only from the Track 2 scorer's
cache (same instrument, same fixed window, so those rows are identical work
already paid for). The scorer's committed cache is never written to.

Run from `builder/` (resumable — re-running costs only the unresolved names):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-low-degree-census/resolve_fame.py --workers 8
"""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCORER = HERE.parent / "2026-07-24-track2-arm-scorer"
sys.path.insert(0, str(SCORER))

from fame import (  # noqa: E402  — A11/A15 canonical, imported not copied
    FAME_FLOOR,
    english_article_fallback,
    fame,
    foreign_article,
    has_non_latin,
)
from fetch_pageviews import resolve  # noqa: E402

import transport  # noqa: E402  — must be installed before any resolution runs

transport.install()

CACHE = HERE / "fame_cache.json"
SEED = SCORER / "fame_cache.json"

_lock = threading.Lock()


def load_cache() -> dict:
    """This directory's cache, seeded from the scorer's on first run.

    The seed is read-only. Its rows came from the same canonical resolver over
    A11's fixed window (2025-07..2026-06), so they are not stale and not
    re-derivable more cheaply — but the committed file stays untouched.
    """
    cache: dict = {}
    if SEED.exists():
        cache.update(json.loads(SEED.read_text(encoding="utf-8")))
        print(f"seeded {len(cache)} row(s) from the Track 2 scorer cache (read-only)")
    if CACHE.exists():
        own = json.loads(CACHE.read_text(encoding="utf-8"))
        cache.update(own)
        print(f"resumed {len(own)} row(s) from this census's own cache")
    return cache


def save_cache(cache: dict) -> None:
    tmp = CACHE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cache, indent=1, ensure_ascii=False, sort_keys=True),
                   encoding="utf-8")
    tmp.replace(CACHE)


def resolve_one(name: str) -> dict:
    """One name -> one fame row. Identical call sequence to `fame.resolve_all`.

    A nameless node cannot be looked up (an empty query matches nothing) and must
    not read as reach: it is floored like any unmatched artist but marked, so the
    report can exclude it rather than present an artifact defect as an obscure
    discovery. 33 such nodes exist in the adopted artifact (P8b F8).
    """
    if not name.strip():
        return {"matched": False, "nameless": True, "F": FAME_FLOOR,
                "guard": {"non_latin_name": False, "foreign": {"found": False},
                          "potentially_notable": False}}
    row = resolve(name)
    if not row.get("matched"):
        fb = english_article_fallback(name)  # A15 recall fix — on the critical path here
        if fb["found"]:
            row.update(matched=True, article=fb["article"], wikidata=fb["wikidata"],
                       pageviews=fb["pageviews"], months_present=fb["months_present"],
                       via="wikidata_fallback")
        else:
            row["guard"] = {
                "non_latin_name": has_non_latin(name),
                "foreign": foreign_article(name),
            }
            row["guard"]["potentially_notable"] = bool(
                row["guard"]["non_latin_name"] or row["guard"]["foreign"]["found"]
            )
    row["F"] = fame(row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", default=str(HERE / "poll_set.json"),
                    help="poll_set.json (screened) or low_degree.json (all 12,041)")
    # 4 rather than 8: the equivalence check found 8 provoked Wikidata throttling,
    # and although transport.py now retries rather than silently flooring, the
    # cheaper fix is to not provoke it. Measured throughput is still ~4x serial.
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--limit", type=int, default=0, help="resolve at most N new names")
    ap.add_argument("--flush-every", type=int, default=25)
    ap.add_argument("--passes", type=int, default=6,
                    help="retry passes over names left unresolved by network failure")
    args = ap.parse_args()

    doc = json.loads(Path(args.census).read_text(encoding="utf-8"))
    if doc["artifact_sha256"] != "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8":
        raise SystemExit("census was not built from the adopted artifact")

    # poll_set.json carries screen+control; low_degree.json carries the full census.
    rows = (doc["screen"] + doc["control"]) if "screen" in doc else (
        doc["degree_1"] + doc["degree_2"])
    # Resolution is by NAME (Wikipedia has no MBID index) so the unit of work is
    # the distinct name; the join back to nodes is by mbid in report.py (P8b F8).
    names = sorted({r["name"] for r in rows})
    cache = load_cache()
    print(f"{len(names)} distinct name(s) over {len(rows)} nodes")

    # Measured attrition is ~19 % per pass, and a failed name is left uncached rather
    # than floored, so the fix is simply to go round again. Passes run until a pass
    # resolves nothing new, which is the only honest stopping condition: a name that
    # survives that is genuinely unreachable, not merely unlucky, and the report
    # counts it separately rather than scoring it at the fame floor.
    t0 = time.time()
    total = 0
    for pass_no in range(1, args.passes + 1):
        todo = [n for n in names if n not in cache]
        if args.limit:
            todo = todo[:args.limit]
        if not todo:
            print("\nall names resolved")
            break
        print(f"\n=== pass {pass_no}/{args.passes}: {len(todo)} name(s) outstanding ===")
        done = failed = 0
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(resolve_one, n): n for n in todo}
            for fut in as_completed(futures):
                name = futures[fut]
                try:
                    row = fut.result()
                except Exception as exc:
                    failed += 1
                    print(f"  ERR  {name}: {exc}")
                    continue
                with _lock:
                    cache[name] = row
                    done += 1
                    total += 1
                    # Per-name, not per-flush: the first attempt logged only every
                    # 50th completion, leaving throughput unobservable for a quarter
                    # of an hour. A long run must be measurable while it runs.
                    mark = "ok  " if row.get("matched") else (
                        "FLAG" if (row.get("guard") or {}).get("potentially_notable")
                        else "----")
                    print(f"  [{done}/{len(todo)}] {mark} F={row['F']:6.3f}  {name}")
                    if done % args.flush_every == 0:
                        save_cache(cache)
                        rate = total / (time.time() - t0)
                        print(f"  -- {rate:.2f} name/s, {failed} failed this pass --")
        save_cache(cache)
        print(f"  pass {pass_no}: {done} resolved, {failed} failed")
        if done == 0:
            print("  a full pass resolved nothing new; the remainder is unreachable")
            break

    left = [n for n in names if n not in cache]
    save_cache(cache)
    print(f"\nresolved {total} name(s) in {(time.time() - t0) / 60:.1f} min; "
          f"{len(left)} still unresolved")
    if left:
        print("unresolved (reported as such, NOT floored): " + ", ".join(left[:20]))
    print(f"wrote {CACHE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
