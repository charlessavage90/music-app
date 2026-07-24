"""P4 step 1: fix the fame-proxy validation sample, deterministically, before labels.

Pre-registration §5 defines the sample in prose over four strata. This script turns that
prose into a committed artifact, because two of the four strata were not actually pinned
by it and one was wrong. See `README.md` for the two defects; in short:

  * S1 and S3 **overlap by four artists** as written, so "~33 artists" is 29 distinct.
  * §5's claim that S1's labels "exist" is false at the granularity §5's own scoring
    needs — the record holds one collective verdict ("mostly unknown"), never a
    per-artist assignment to the three buckets.

Both are fixed by amendment A10 (pre-registration §9), committed before any label is
collected. This script is the A10 sample.

S2's twelve are selected by a rule fixed here rather than hand-picked, so the choice is
reproducible and not answerable to the result. The rule spans the strata §5 names:

    1. the three exemplars §5 names outright (Whitney Houston, Paul Simon, Kylie Minogue)
    2. each judged pair's **least** in-graph-popular interior
    3. each judged pair's **most** in-graph-popular interior   ("superstar endpoints-class")
    4. each judged pair's **median** in-graph-popular interior

filled in that order, skipping any artist already selected and taking the next artist by
the same rule when a slot collides. Ties on `pop_raw` break on lowest MBID, per the
project's determinism rule.

**In-graph popularity is used only to SPREAD the sample, never to score it.** That is the
whole point of P4: `pop_raw` is not fame, and §5 exists to find an external quantity that
is. Selecting on it is safe — and, as it happens, informative: it places Whitney Houston
at the bottom of two pairs and Nick Drake at the top of one.

Run from `api/`:
    UV_LINK_MODE=copy uv run python ../builder/analysis/2026-07-23-track2-fame-proxy/fix_sample.py
"""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "api" / "src"))

GRAPH = ROOT / "builder" / "scratch" / "graph-t15-tiebreakfix.bin"
EXPECT = "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
LISTEN = ROOT / "builder" / "analysis" / "2026-07-22-c3-bypass-mechanisms" / "listen_public.json"
OUT = Path(__file__).resolve().parent / "sample.json"

# S1 — the nine names from the settled test-queue item (2026-07-23 entry). Verbatim.
S1 = [
    "saib.",
    "Purrple Cat",
    "sleepy fish",
    "Leavv",
    "idealism",
    "Miami Nights 1984",
    "Lazerhawk",
    "Stonebank",
    "Toonorth",
]

# S3 — F6's named reaches. §5 also listed four §2.11 insular-stratum artists here; all
# four are already in S1, so they are S1 members and are NOT double-counted (A10).
S3 = ["Max Richter", "Ólafur Arnalds"]

# S4 — Attack 3 stress cases: plausibly-off-platform fame. Verbatim from §5.
S4 = ["Wishbone Ash", "Chuck Berry", "The Byrds", "林俊傑", "EGOIST", "CROOVE"]

# S2 exemplars named outright by §5.
S2_NAMED = ["Whitney Houston", "Paul Simon", "Kylie Minogue"]


def load_store():
    from artistpath_api.graph_store import GraphStore

    digest = hashlib.sha256(GRAPH.read_bytes()).hexdigest()
    if digest != EXPECT:
        raise SystemExit(f"artifact mismatch: {digest}")
    print(f"artifact ok: {GRAPH.name} sha256 {digest[:8]}...{digest[-7:]}\n")
    return GraphStore.load(str(GRAPH))


def pair_interiors(store, pair):
    """Every distinct interior of a judged pair, as (pop_raw, mbid, name), sorted."""
    seen: dict[str, str] = {}
    for arms in pair["depths"].values():
        for arm in arms.values():
            for a in arm["artists"][1:-1]:
                seen[a["mbid"]] = a["name"]
    rows = []
    for mbid, name in seen.items():
        node = store.id_by_mbid.get(mbid)
        if node is None:  # not in the adopted artifact; cannot be spread on
            continue
        rows.append((float(store.pop_raw[node]), mbid, name))
    rows.sort(key=lambda r: (r[0], r[1]))  # ties on lowest MBID
    return rows


def select_s2(store, pairs):
    """The twelve, by the rule fixed in this module's docstring."""
    chosen: list[str] = []
    provenance: dict[str, str] = {}

    def take(name, why):
        if name not in chosen:
            chosen.append(name)
            provenance[name] = why
            return True
        return False

    for name in S2_NAMED:
        take(name, "§5 named exemplar")

    ranked = {p["label"]: pair_interiors(store, p) for p in pairs}

    def by_rule(rows, index_fn, why):
        """Walk outward from the rule's index until an unselected artist is found."""
        order = index_fn(rows)
        for i in order:
            if take(rows[i][2], why):
                return rows[i]
        return None

    for label, rows in ranked.items():
        by_rule(rows, lambda r: range(len(r)), f"least popular interior, {label}")
    for label, rows in ranked.items():
        by_rule(rows, lambda r: range(len(r) - 1, -1, -1), f"most popular interior, {label}")
    for label, rows in ranked.items():
        mid = len(rows) // 2
        order = sorted(range(len(rows)), key=lambda i: (abs(i - mid), i))
        by_rule(rows, lambda r, o=order: o, f"median popular interior, {label}")

    return chosen[:12], provenance, ranked


def main():
    store = load_store()
    listen = json.loads(LISTEN.read_text(encoding="utf-8"))
    s2, prov, ranked = select_s2(store, listen["pairs"])

    for label, rows in ranked.items():
        print(f"{label}: {len(rows)} interiors, pop_raw {rows[0][0]:.4f} .. {rows[-1][0]:.4f}")
    print()

    strata = {"S1": S1, "S2": s2, "S3": S3, "S4": S4}
    seen: set[str] = set()
    for name, members in strata.items():
        for m in members:
            if m in seen:
                raise SystemExit(f"stratum overlap not resolved: {m} in {name}")
            seen.add(m)

    sample = {
        "artifact_sha256": EXPECT,
        "listen_graph": listen["graph"],
        "strata": strata,
        "s2_provenance": prov,
        "distinct": len(seen),
    }
    OUT.write_text(json.dumps(sample, ensure_ascii=False, indent=2), encoding="utf-8")

    for name, members in strata.items():
        print(f"{name} ({len(members)}):")
        for m in members:
            note = f"   — {prov[m]}" if m in prov else ""
            print(f"    {m}{note}")
        print()
    print(f"{len(seen)} distinct artists -> {OUT.name}")


if __name__ == "__main__":
    main()
