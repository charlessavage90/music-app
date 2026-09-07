"""Prove the LUX-4 artifact is the served graph plus exactly three metadata keys.

The sha MUST differ -- keys were added -- so the sha cannot be the check. Two
independent checks run here instead, and both must pass.

  STRUCTURAL: every field of the deserialised graph compared to the served one,
  and the metadata key sets differenced. Catches a changed node, edge, score or
  pre-existing metadata value.

  SUBTRACTION, and it is the stronger of the two: strip the three new keys from
  the new artifact's metadata, re-serialise the blob with the identical json
  parameters, rebuild the payload, and require it to be BYTE-IDENTICAL to the
  served artifact. Where the structural check compares values, this compares
  bytes -- so it also catches a change in JSON key order, separator choice or
  unicode escaping, none of which alters a single Python value and all of which
  would silently break the "same artifact plus keys" claim.

⚠ WHY THE PLAN'S CONTROL ARM WAS REPLACED. `L4-T7` step 1 said to reuse
`analysis/2026-09-05-lux-e1-armb/armb_sha.py` and expect BYTE-IDENTICAL. That
became impossible at `L4-T5`: that script calls `build_from_archive`, which now
wires the LUX-4 maps unconditionally, so it can never again reproduce
43dd82bb. The plan's factor table lists a control arm with "maps not wired",
and no such arm exists once the maps are wired -- there is no config knob, by
design. `control_empty_maps.py` beside this file restores a real control by
patching the two loaders to return nothing, which is the only remaining way to
build the pre-LUX-4 output from post-LUX-4 code.

Run from `builder/`, after both builds:
    UV_LINK_MODE=copy uv run python analysis/2026-09-05-lux-4-rebuild/verify.py
"""

from __future__ import annotations

import json
import struct
import sys
from hashlib import sha256
from pathlib import Path

from artistpath_builder.artifact import deserialise

HEADER = struct.Struct("<4sIIIQ")
NEW_KEYS = {"spotify_ids", "apple_ids", "artist_facts"}

LIVE = Path("scratch/graph-msw-tu50.bin")
LIVE_SHA = "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8"
NEW = Path("scratch/graph-lux4.bin")


def split(payload: bytes) -> tuple[bytes, dict]:
    """(everything before the metadata blob, the parsed blob)."""
    *_, meta_len = HEADER.unpack_from(payload)
    return payload[: len(payload) - meta_len], json.loads(
        payload[len(payload) - meta_len :].decode("utf-8")
    )


def reserialise(prefix: bytes, meta: dict) -> bytes:
    """Rebuild a payload from a prefix and a metadata dict.

    The json parameters are copied verbatim from `artifact.serialise`. If they
    ever diverge this check fails loudly, which is the correct outcome: it
    would mean this script no longer reproduces what the builder writes.
    """
    blob = json.dumps(
        meta, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    magic, version, n, e, _ = HEADER.unpack_from(prefix)
    head = HEADER.pack(magic, version, n, e, len(blob))
    return head + prefix[HEADER.size :] + blob


def main() -> int:
    for p in (LIVE, NEW):
        if not p.exists():
            print(f"FATAL: missing {p}", file=sys.stderr)
            return 2

    live_bytes = LIVE.read_bytes()
    new_bytes = NEW.read_bytes()

    if sha256(live_bytes).hexdigest() != LIVE_SHA:
        print("FATAL: the served artifact is not the one this eval is defined on")
        return 2

    live, new = deserialise(live_bytes), deserialise(new_bytes)
    problems: list[str] = []

    def check(label: str, ok: bool) -> None:
        print(f"  {'ok  ' if ok else 'FAIL'}  {label}")
        if not ok:
            problems.append(label)

    print("STRUCTURAL")
    check("artist count", new.artist_count == live.artist_count)
    check("edge count", new.edge_count == live.edge_count)
    check("mbids", new.mbids == live.mbids)
    check("names", new.names == live.names)
    check("disambiguations", new.disambiguations == live.disambiguations)
    check("pop_raw", new.pop_raw == live.pop_raw)
    check("deezer_ids", new.deezer_ids == live.deezer_ids)
    check("fame_lb_raw", new.fame_lb_raw == live.fame_lb_raw)
    check("offsets", (new.offsets == live.offsets).all())
    check("neighbours", (new.neighbours == live.neighbours).all())
    check("scores", (new.scores == live.scores).all())
    check("edge_types", (new.edge_types == live.edge_types).all())

    live_prefix, live_meta = split(live_bytes)
    new_prefix, new_meta = split(new_bytes)
    added = set(new_meta) - set(live_meta)
    removed = set(live_meta) - set(new_meta)
    check(f"metadata keys added == {sorted(NEW_KEYS)}", added == NEW_KEYS)
    check("no metadata key removed", removed == set())

    print("SUBTRACTION")
    # ⚠ Compare the CSR arrays WITHOUT the header. The header's uint64 metadata
    # length legitimately differs -- the new blob is bigger -- so a whole-prefix
    # comparison fails on a correct artifact. Caught here on the first run: this
    # check went red while the byte-subtraction below went green, and two checks
    # of the same claim disagreeing is what exposed the bug in the check rather
    # than in the artifact.
    live_magic, live_ver, live_n, live_e, live_j = HEADER.unpack_from(live_bytes)
    new_magic, new_ver, new_n, new_e, new_j = HEADER.unpack_from(new_bytes)
    check(
        "header matches except the metadata length",
        (live_magic, live_ver, live_n, live_e)
        == (new_magic, new_ver, new_n, new_e)
        and new_j > live_j,
    )
    check(
        "CSR arrays are byte-identical",
        new_prefix[HEADER.size :] == live_prefix[HEADER.size :],
    )
    stripped = {k: v for k, v in new_meta.items() if k not in NEW_KEYS}
    rebuilt = reserialise(new_prefix, stripped)
    check("stripping the new keys reproduces the served artifact", rebuilt == live_bytes)
    check("...and therefore its sha", sha256(rebuilt).hexdigest() == LIVE_SHA)

    # The three new keys must themselves be node-indexed, or the api would show
    # an artist someone else's link. Cheap to check here and impossible later.
    print("NEW KEYS")
    for key in sorted(NEW_KEYS):
        check(f"{key} is parallel to mbids", len(new_meta[key]) == len(new.mbids))

    print()
    if problems:
        print(f"FAILED: {len(problems)} check(s): {', '.join(problems)}")
        return 1
    print("VERIFIED: identical graph; metadata differs by exactly", sorted(NEW_KEYS))
    print(f"  served   {len(live_bytes) / 1024 / 1024:>6.1f} MB  sha {LIVE_SHA[:16]}...")
    print(
        f"  lux4     {len(new_bytes) / 1024 / 1024:>6.1f} MB  "
        f"sha {sha256(new_bytes).hexdigest()[:16]}..."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
