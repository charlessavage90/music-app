"""Step 2: pull ListenBrainz artist popularity for the whole adopted artifact.

WHAT THIS IS, IN THE PROJECT'S OWN CURRENCIES
  NOT a fame source. `total_user_count` is how many LISTENBRAINZ USERS played
  an artist -- the same Western, tech-forward population §6e disqualified
  Deezer for failing to match. It is the authoritative version of the quantity
  in-degree was adopted as a cheap stand-in for: the alpha design §4.1 says in
  terms that "a real ListenBrainz artist-popularity table, should one become
  obtainable, is a drop-in improvement". POST /1/popularity/artist is that
  table, and it did not exist when §6a-§6f eliminated every alternative on
  cost (~23s/call -> ~3 weeks).

  Two properties matter here and are why it is worth measuring:
    - MBID-keyed, so no name resolution step exists to fail.
    - Continuous into the tail. A 200-artist stratified probe returned
      200/200 with ZERO nulls, down to an artist with 12 distinct listeners,
      where the Wikipedia proxy returns a constant floor.

  Two properties bound it, and the report must carry both:
    - It shares the Wikipedia proxy's population blind spot. Measured the same
      day on one pair: both under-represent the same artists by ~10x against
      outside references, so their agreement is NOT corroboration.
    - It is computed on the same corpus as the similarity edges, so unlike
      Wikipedia it cannot serve as an INDEPENDENT audit of our own popularity.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_listenbrainz.py
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from fp_common import HERE, USER_AGENT, graph_mbids, load_partial, post_json, run_batches

ENDPOINT = "https://api.listenbrainz.org/1/popularity/artist"
OUT = HERE / "fp_listenbrainz.json"

# MAX_ITEMS_PER_GET in listenbrainz/webserver/views/api_tools.py, read from
# master 2026-07-30. Batching above it is silently truncated, not an error.
MAX_PER_REQUEST = 1000


def fetch(chunk: list[str]) -> dict[str, dict]:
    body = json.dumps({"artist_mbids": chunk}).encode()
    payload = post_json(
        ENDPOINT,
        body,
        {"User-Agent": USER_AGENT, "Content-Type": "application/json"},
    )
    out: dict[str, dict] = {}
    for row in payload:
        # The endpoint documents that not-found artists come back with counts
        # set to null rather than being omitted -- so a null here is a real
        # measured absence, and must be distinguished from a missing key.
        users = row.get("total_user_count")
        listens = row.get("total_listen_count")
        out[row["artist_mbid"]] = (
            None if users is None else {"users": users, "listens": listens}
        )
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", type=int, default=MAX_PER_REQUEST)
    ap.add_argument("--pause", type=float, default=0.5)
    ap.add_argument("--limit", type=int, default=0, help="first N artists, for a smoke run")
    args = ap.parse_args()
    if args.batch > MAX_PER_REQUEST:
        raise SystemExit(f"--batch above {MAX_PER_REQUEST} is silently truncated")

    mbids = graph_mbids()
    if args.limit:
        mbids = mbids[: args.limit]
    done = load_partial(OUT)
    run_batches(mbids, args.batch, done, fetch, OUT, pause=args.pause, label="listenbrainz")

    hit = sum(1 for m in mbids if done.get(m))
    print(f"\nresolved {hit}/{len(mbids)} ({hit / len(mbids):.1%}) -> {OUT.name}")


if __name__ == "__main__":
    main()
