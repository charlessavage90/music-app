"""`MSW-V1` — did the un-listenable filter actually remove the artists the
coherence audit could not listen to?

Task 10 Step 1 of `plans/2026-08-05-msw-package-adoption.md`. This is the check
`CAU-` §3 weakest-link 2 asked for: the filter's census said these artists have
nothing playable, and this asks whether the filter's REAL-WORLD behaviour agrees
on a built artifact rather than on a census.

THE SIX CORE NAMES are the distinct artists behind eight of the nine `CAU-C3`
CAN'T TELL slots plus Rick Davies's DOESN'T FIT slot (findings §1, the CAU-C3
table). Nine SLOTS, seven distinct artists: Brad Delson and Dallas Taylor hold
two slots each, and the seventh is Four Tet, who is deliberately NOT a core name
— he was listened to and understood, and declined on bio grounds rather than on
having nothing to play. Four Tet is reported here as context and cannot fire the
stop branch.

Names are resolved to MBIDs through the OLD candidate artifact's metadata, not
by hand: both artifacts are built from the same archive, so the old one is the
right dictionary. Ambiguous names are recorded as ambiguous rather than
silently taking the first hit — `BYP-13` is exactly the failure of assuming a
name identifies an artist.

Figures are owned by this script's committed JSON output and by the MSW-
execution log's Task 10 section. Cited, never restated.
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "builder" / "src"))

from artistpath_builder.artifact import deserialise  # noqa: E402

OLD = ROOT / "builder" / "scratch" / "graph-algb-full.bin"
NEW = ROOT / "builder" / "scratch" / "graph-msw-tu50.bin"

# Preconditions. The old artifact's sha is from its manifest sidecar; the new
# one's is the identity recorded in the MSW- execution log's Task 9 section.
# Several graphs exist in scratch/ and they are NOT interchangeable — a
# conclusion drawn from the wrong one looks exactly like a correct one.
SHA = {
    OLD: "d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f",
    NEW: "43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8",
}

# Distinct artists behind the CAU-C3 slots. Reason strings are the owner's own
# words from findings §1, quoted so the verdict can be read beside what he said.
CORE_NAMES = {
    "Rick Davies": "could not find his solo work anywhere he could listen",
    "Max Martin": 'only findable "solo work" is a musical; otherwise a writer/producer',
    "Brad Delson": "one release with one song on MB, and it cannot be found anywhere",
    "Joey Kramer": "Aerosmith drummer; no solo work findable",
    "Dallas Taylor": "no releases visible at all",
    "John McVie": "no solo releases",
}

# Reported, never decisive. Present-with-releases is a legitimate outcome here.
CONTEXT_NAMES = {
    "Four Tet": "listened and understood; declined on bio grounds, not on silence",
}


def load(path: Path):
    payload = path.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != SHA[path]:
        raise SystemExit(
            f"{path.name}: sha256 {actual}, expected {SHA[path]} — refusing to "
            "draw a conclusion from an unidentified artifact"
        )
    return deserialise(payload)


def resolve(graph, name: str) -> list[str]:
    """Every mbid carrying this exact name. A list, because names are not keys."""
    return [m for m, n in zip(graph.mbids, graph.names) if n == name]


def main() -> int:
    old, new = load(OLD), load(NEW)
    new_nodes = set(new.mbids)

    rows = []
    for names, is_core in ((CORE_NAMES, True), (CONTEXT_NAMES, False)):
        for name, reason in names.items():
            mbids = resolve(old, name)
            if not mbids:
                rows.append(
                    {
                        "name": name,
                        "mbid": None,
                        "core": is_core,
                        "in_old": False,
                        "in_new": False,
                        "verdict": "not_in_old_artifact",
                        "audit_reason": reason,
                    }
                )
                continue
            for mbid in mbids:
                in_new = mbid in new_nodes
                rows.append(
                    {
                        "name": name,
                        "mbid": mbid,
                        "core": is_core,
                        "ambiguous_name": len(mbids) > 1,
                        "in_old": True,
                        "in_new": in_new,
                        # A core name surviving is the stop branch. For context
                        # names, surviving is a legitimate outcome and is not.
                        "verdict": (
                            ("SURVIVED" if is_core else "present_legitimately")
                            if in_new
                            else "dropped_by_filter"
                        ),
                        "audit_reason": reason,
                    }
                )

    survivors = [r for r in rows if r["core"] and r["verdict"] == "SURVIVED"]
    result = {
        "check": "MSW-V1",
        "old_artifact": {"name": OLD.name, "sha256": SHA[OLD], "nodes": old.artist_count},
        "new_artifact": {"name": NEW.name, "sha256": SHA[NEW], "nodes": new.artist_count},
        "core_names_checked": len(CORE_NAMES),
        "core_survivors": len(survivors),
        # The plan's stop branch: "If any of the six core names survives, stop
        # and report to the owner before Task 11."
        "stop_branch_fires": bool(survivors),
        "rows": rows,
    }

    out = Path(__file__).with_name("msw_v1_named_artists.json")
    out.write_text(json.dumps(result, indent=2) + "\n")

    for r in rows:
        tag = "core" if r["core"] else "ctxt"
        print(f"  [{tag}] {r['name']:<14} {r['verdict']}")
    print(f"\ncore survivors: {len(survivors)} — stop branch fires: {bool(survivors)}")
    print(f"wrote {out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
