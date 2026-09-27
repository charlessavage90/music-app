"""Issue #200: is the top-1 % wall on lba-a6 in the archived supply, or made by the trim? Decides nothing.

For the most-listened 1 % (and top decile) of artists on `graph-lba-a6.bin`, count candidate
neighbours below 0.9 and below 0.5 fame percentile at each successive step of the ONE build that
produced that map, and report how many the trim discarded.

Instrument: the SHIPPED `build_from_archive`, with `cand_build.py`'s exact config and archive
wrapping (`ReadOnlyArchive` on both halves, `FameOverlayArchive`, `require_fame=True`, drop list
`unlistenable_drop_algb_20260809.json`). Names in the `artistpath_builder.pipeline` module
namespace are wrapped with PASS-THROUGH functions that record inputs and outputs and return the
original's result unchanged: `trimmed_union_cap`, `largest_component`, `harvest_identities`,
`load_drop_mbids`, `load_featured_credit_drop_mbids`, `load_unlistenable_list`. The final graph's
node order and CSR offsets/neighbours are ASSERTED equal to `graph-lba-a6.bin` as read by the
shipped api `GraphStore`; the script refuses (exit 3) otherwise.

The trim loop is re-implemented ONLY to attribute each ceiling deletion to the endpoint whose
ceiling removed it, and to expose the pre-ceiling union (SUP-S3). The re-implementation's output
is asserted identical to the shipped function's output on the whole graph (exit 3 otherwise).

Every fame percentile: shipped `GraphStore.fame_lb_pctl` (asserted equal to
`GraphStore.fame_percentiles` on the raw `fame_lb`), lba-a6's own frame. Nulls cannot be centres
and are excluded from numerator and denominator as candidates (counted).

Stage table (identifier series SUP-):
  SUP-S0  centre's raw archived list (P-filtered, <= 100), all entries
          -- everyone the listening data names as similar, as it arrived in the archive.
  SUP-S1  S0 restricted to lba-a6 nodes ("pre-trim supply")
          -- the similar artists who are on the map at all.
  SUP-S2  centre's own top-50 (top_j) by the cap's ranking, restricted to nodes
          -- the ones it ranks highly enough to claim itself.
  SUP-S3  union before the ceiling: own top-50 plus rescued edges, restricted to nodes
          -- everyone connected before the fifty-connection limit is applied.
  SUP-S4  after the ceiling trim.
  SUP-S5  after the component prune = served (asserted equal to lba-a6's row).

No command-line arguments. Refuses (exit 2) on any sha mismatch before reading anything.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-27-issue-200-trim-supply/trim_supply.py
"""
from __future__ import annotations

import hashlib
import json
import logging
import struct
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))
sys.path.insert(0, str(HERE.parent / "2026-09-10-lbd-supply"))

ARCHIVE = Path(r"C:\unsung-fast\lbd-archives\S4-A6")
FAME_DIR = Path(r"C:\unsung-fast\lbd-archives\S4-A6-fame")
POPULATION = Path(r"C:\unsung-fast\lbd-archives\population_cxa_mbids.txt")
GRAPH = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
ARCHIVE_MANIFEST_SHA = "950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3"
GRAPH_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
DROP_LIST = "unlistenable_drop_algb_20260809.json"
BARS = (0.9, 0.5)
TIERS = (("top 1 %", 0.99), ("top decile", 0.90))
# Expected post-trim zero counts (owned by ../2026-09-27-issue-200-graph-descriptives/README.md §1 A).
EXPECT_S5_ZERO = {("top 1 %", 0.9): (381, 874), ("top 1 %", 0.5): (706, 874),
                  ("top decile", 0.9): (629, 8740), ("top decile", 0.5): (3106, 8740)}


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def refuse(msg: str, code: int = 2) -> None:
    print(f"REFUSING: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


# ---- identity FIRST ----------------------------------------------------------------------------
T0 = time.monotonic()
manifest_path = ARCHIVE / "MANIFEST.json"
m_before = sha256_of(manifest_path)
if m_before != ARCHIVE_MANIFEST_SHA:
    refuse(f"S4-A6 manifest sha256 {m_before} != pin {ARCHIVE_MANIFEST_SHA}")
g_sha = sha256_of(GRAPH)
g_side = json.loads(GRAPH.with_name(GRAPH.name + ".json").read_text(encoding="utf-8"))["sha256"]
if not (g_sha == g_side == GRAPH_SHA):
    refuse(f"graph-lba-a6.bin sha256 {g_sha}; sidecar {g_side}; pin {GRAPH_SHA}")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
p_sha = sha256_of(POPULATION)
if p_sha != manifest["population"]["file_sha256"]:
    refuse(f"population file sha256 {p_sha} != manifest {manifest['population']['file_sha256']}")
print(f"sha256 OK  S4-A6 MANIFEST.json {m_before}")
print(f"sha256 OK  graph-lba-a6.bin    {g_sha} (== sidecar == pin)")
print(f"sha256 OK  population file     {p_sha} (== archive manifest)")

# ---- shipped modules ---------------------------------------------------------------------------
import artistpath_builder.pipeline as pl  # noqa: E402
from artistpath_builder import graph as graph_mod  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from dcf_ceiling_sweep import ArchiveWriteRefused, ReadOnlyArchive  # noqa: E402
from lbd_source import LbdBulkSource  # noqa: E402

for mod in (pl, graph_mod):
    f = Path(mod.__file__).resolve()
    if (REPO / "builder" / "src").resolve() not in f.parents:
        refuse(f"{mod.__name__} loaded from {f}, not this worktree", 3)
import artistpath_api.graph_store as _gs  # noqa: E402
if (REPO / "api" / "src").resolve() not in Path(_gs.__file__).resolve().parents:
    refuse(f"graph_store loaded from {_gs.__file__}, not this worktree", 3)
print(f"builder pipeline: {Path(pl.__file__).resolve()}")
print(f"api graph_store:  {Path(_gs.__file__).resolve()}")


class FameOverlayArchive:
    """Copied from cand_build.py: similarity from the arm's archive, `fame/` from the fame dir."""

    def __init__(self, similarity, fame) -> None:
        self._similarity = similarity
        self._fame = fame

    def _pick(self, key: str):
        return self._fame if key.startswith("fame/") else self._similarity

    def put(self, key: str, payload: bytes) -> None:
        raise ArchiveWriteRefused(f"trim_supply tried to write {key!r}; both halves are read-only")

    def get(self, key: str):
        return self._pick(key).get(key)

    def has(self, key: str) -> bool:
        return self._pick(key).has(key)

    def keys(self):
        yield from self._similarity.keys()
        yield from self._fame.keys()


# ---- pass-through capture wrappers in the pipeline namespace -----------------------------------
CAP: dict = {}
_orig = {name: getattr(pl, name) for name in (
    "trimmed_union_cap", "largest_component", "harvest_identities", "load_drop_mbids",
    "load_featured_credit_drop_mbids", "load_unlistenable_list")}


def _w_trim(adjacency, top_j, degree_ceiling, *, ranking):
    out = _orig["trimmed_union_cap"](adjacency, top_j, degree_ceiling, ranking=ranking)
    CAP["trim_in"] = adjacency
    CAP["ranking"] = ranking
    CAP["top_j"], CAP["ceiling"] = top_j, degree_ceiling
    CAP["trim_out"] = out
    return out


def _w_lc(adjacency):
    out = _orig["largest_component"](adjacency)
    CAP["lc_in_nodes"] = set(adjacency)
    CAP["lc_out"] = out
    return out


def _w_hi(payloads):
    out = _orig["harvest_identities"](payloads)
    CAP["identities"] = out
    return out


def _w_ldm(algorithm):
    out = _orig["load_drop_mbids"](algorithm)
    CAP["no_release"] = set(out)
    return out


def _w_lfc(algorithm):
    out = _orig["load_featured_credit_drop_mbids"](algorithm)
    CAP["featured"] = set(out)
    return out


def _w_lul(algorithm, path):
    out = _orig["load_unlistenable_list"](algorithm, path)
    CAP["unlistenable"] = set(out.drop_mbids)
    return out


pl.trimmed_union_cap = _w_trim
pl.largest_component = _w_lc
pl.harvest_identities = _w_hi
pl.load_drop_mbids = _w_ldm
pl.load_featured_credit_drop_mbids = _w_lfc
pl.load_unlistenable_list = _w_lul

# ---- the build (cand_build.py's config, exactly) -----------------------------------------------
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
config = BuilderConfig(require_fame=True, algorithm=CANDIDATE_ALGORITHM, drop_unlistenable=True,
                       unlistenable_list_path=DATA / DROP_LIST)
print(f"config: cap_strategy={config.cap_strategy} union_top_j={config.union_top_j} "
      f"union_degree_ceiling={config.union_degree_ceiling} damping={config.similarity_damping} "
      f"rescale={config.similarity_rescale} filter_special_purpose={config.filter_special_purpose} "
      f"drop_no_release_tail={config.drop_no_release_tail} "
      f"drop_featured_credit={config.drop_featured_credit} drop_unlistenable={config.drop_unlistenable}")
source = LbdBulkSource(config)
archive = FameOverlayArchive(ReadOnlyArchive(LocalArchive(ARCHIVE)),
                             ReadOnlyArchive(LocalArchive(FAME_DIR)))


class _Cap(logging.Handler):
    def emit(self, record) -> None:
        print(f"  builder: {record.getMessage()}", flush=True)


blog = logging.getLogger("artistpath_builder")
blog.addHandler(_Cap())
blog.setLevel(logging.INFO)
t_build = time.monotonic()
built = pl.build_from_archive(config, archive, source)
print(f"build: {len(built.mbids):,} nodes, {int(built.offsets[-1]):,} CSR entries "
      f"({(time.monotonic() - t_build) / 60:.1f} min)", flush=True)
for name, fn in _orig.items():  # restore
    setattr(pl, name, fn)
missing = {"trim_in", "trim_out", "lc_out", "identities", "no_release", "featured",
           "unlistenable"} - set(CAP)
if missing:
    refuse(f"capture incomplete: {missing}", 3)

# ---- the reproduction assertion ----------------------------------------------------------------
payload = GRAPH.read_bytes()
store = GraphStore.from_bytes(payload)
if list(store.mbids) != list(built.mbids):
    refuse("built node order != graph-lba-a6.bin", 3)
if not np.array_equal(np.asarray(store.offsets), np.asarray(built.offsets)):
    refuse("built CSR offsets != graph-lba-a6.bin", 3)
if not np.array_equal(np.asarray(store.neighbours), np.asarray(built.neighbours)):
    refuse("built CSR neighbours != graph-lba-a6.bin", 3)
print("REPRODUCTION: built node order, offsets, neighbours == graph-lba-a6.bin (shipped GraphStore): True")


def raw_fame(buf: bytes, n: int) -> list:
    """`fame_lb` from the APG1 metadata blob (copied from graph_descriptives.py)."""
    header = struct.Struct("<4sIIIQ")
    magic, _v, hn, e, meta_len = header.unpack_from(buf)
    assert magic == b"APG1" and hn == n
    cursor = header.size + (hn + 1) * 4 + e * 4 + e * 4 + e * 1
    meta = json.loads(buf[cursor: cursor + meta_len])
    fame = meta.get("fame_lb")
    assert fame is not None and len(fame) == n
    return fame


N = store.artist_count
fame = raw_fame(payload, N)
del payload
pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
if not np.array_equal(pctl, GraphStore.fame_percentiles(fame)):
    refuse("store fame_lb_pctl != fame_percentiles(raw fame_lb)", 3)
measured = np.array([v is not None for v in fame], dtype=bool)
mbids = list(store.mbids)
idx = {m: i for i, m in enumerate(mbids)}
nodes = set(mbids)
print(f"lba-a6: N {N:,}  CSR entries {int(store.offsets[-1]):,}  null fame {int((~measured).sum())}")


def served(i: int) -> set[str]:
    return {mbids[j] for j in store.neighbours[store.offsets[i]: store.offsets[i + 1]]}


# ---- consistency of captures -------------------------------------------------------------------
trim_in, trim_out, ranking = CAP["trim_in"], CAP["trim_out"], CAP["ranking"]
known_final = set(trim_in)
if CAP["lc_out"] != nodes:
    refuse("largest_component output != lba-a6 node set", 3)
bad = [m for m in nodes if set(trim_out[m]) != served(idx[m])]
if bad:
    refuse(f"{len(bad)} nodes whose ceiling-trim row != served row (e.g. {bad[:2]})", 3)
print("S4 rows == served rows for every node: True")

# ---- re-implementation of the trim, for S3 and deletion attribution ----------------------------
top_j, ceiling = CAP["top_j"], CAP["ceiling"]
keep: dict[str, set[str]] = {}
for node, edges in trim_in.items():
    ranked = sorted(edges, key=lambda dst: (-ranking[node][dst], dst))
    keep[node] = set(ranked[:top_j])
pre: dict[str, set[str]] = {node: set() for node in trim_in}
for node, edges in trim_in.items():
    for dst in edges:
        if dst in keep[node] or node in keep.get(dst, set()):
            pre[node].add(dst)
            pre.setdefault(dst, set()).add(node)
S3 = {k: set(v) for k, v in pre.items()}


def strength(u, v):
    return max(ranking.get(u, {}).get(v, float("-inf")), ranking.get(v, {}).get(u, float("-inf")))


remover: dict[tuple[str, str], str] = {}  # (node, victim) and (victim, node) -> processing node
for node in sorted(pre, key=lambda n: (-len(pre[n]), n)):
    excess = len(pre[node]) - ceiling
    if excess <= 0:
        continue
    doomed = sorted(pre[node], key=lambda v: (strength(node, v), graph_mod._desc(v)))[:excess]
    for victim in doomed:
        pre[node].discard(victim)
        pre[victim].discard(node)
        remover[(node, victim)] = node
        remover[(victim, node)] = node
if set(pre) != set(trim_out) or any(pre[k] != set(trim_out[k]) for k in pre):
    refuse("re-implemented trim != shipped trimmed_union_cap output", 3)
print(f"re-implemented trim == shipped trimmed_union_cap output on all {len(pre):,} nodes: True")
del pre

# ---- reasons for non-node S0 entries -----------------------------------------------------------
prefix = pl.similar_prefix(config, source)
payload_mbids = set()
for key in archive._similarity.keys():
    if key.startswith(prefix) and key.endswith(".json"):
        m = key[len(prefix):-len(".json")]
        if "/" not in m:
            payload_mbids.add(m)
identities = CAP["identities"]
special = {m for m, (_n, d) in identities.items() if pl.is_special_purpose(d)} \
    if config.filter_special_purpose else set()
nameless = {m for m, (n, _d) in identities.items() if not n.strip()} | (payload_mbids - identities.keys())
k = payload_mbids - special - nameless
nr = CAP["no_release"] & k
k -= nr
fc = CAP["featured"] & k
k -= fc
ul = CAP["unlistenable"] & k
k -= ul
if k != known_final:
    refuse("reconstructed known set != trimmed_union_cap input node set", 3)
print(f"reconstructed pre-Pass-1 drops reproduce the cap's input node set: True "
      f"({len(known_final):,} artists; payloads {len(payload_mbids):,}; "
      f"special {len(special & payload_mbids)}, nameless {len(nameless & payload_mbids)}, "
      f"no-release {len(nr)}, featured {len(fc)}, un-listenable {len(ul)} among payload-holders; "
      f"component prune {len(known_final - nodes)})")
population = set(POPULATION.read_text(encoding="utf-8").split())
print(f"population P: {len(population):,} MBIDs")


def reason(m: str) -> str:
    if m in nodes:
        return "node"
    if m not in population:
        return "outside P"
    if m in special:
        return "special-purpose"
    if m in nameless:
        return "nameless / no identity row"
    if m not in payload_mbids:
        return "no archived payload of its own"
    if m in nr:
        return "no-release-tail drop"
    if m in fc:
        return "featured-credit drop"
    if m in ul:
        return "un-listenable drop (20260809)"
    if m in known_final:
        return "lost to largest-component prune"
    return "UNEXPLAINED"


REASONS = ("outside P", "special-purpose", "nameless / no identity row",
           "no archived payload of its own", "no-release-tail drop", "featured-credit drop",
           "un-listenable drop (20260809)", "lost to largest-component prune", "UNEXPLAINED")

# ---- rescue direction index: who ranks c in their own top-50 -----------------------------------
rescuers: dict[str, set[str]] = {}
for u, ks in keep.items():
    for c in ks:
        rescuers.setdefault(c, set()).add(u)


def q(a, p):
    return float(np.percentile(a, p)) if len(a) else float("nan")


def dist(a) -> str:
    a = np.asarray(a, dtype=float)
    return (f"median {np.median(a):.0f}  p10 {q(a, 10):.0f}  p90 {q(a, 90):.0f}  "
            f"mean {a.mean():.2f}  min {a.min():.0f}  max {a.max():.0f}")


def below(m: str, bar: float) -> bool | None:
    """True/False for a measured node; None for a null (excluded) or a non-node."""
    i = idx.get(m)
    if i is None or not measured[i]:
        return None
    return bool(pctl[i] < bar)


RESULT: dict = {}
S0_cache: dict[str, list[str]] = {}
for tier, cut in TIERS:
    centres = [mbids[i] for i in np.flatnonzero(measured & (pctl >= cut))]
    K = len(centres)
    print(f"\n{'=' * 100}\n## {tier} (fame percentile >= {cut}, lba-a6 frame): {K:,} centres")
    raw_len, raw_len_all, s0_len, s1_len, dup_centres = [], [], [], [], 0
    reasons = Counter()
    centres_with_reason = Counter()
    null_cand = Counter()
    per = {bar: {s: [] for s in ("S1", "S2", "S3", "S4", "S5", "R", "R_only", "R_surv",
                                 "U", "S1_surv", "del_self", "del_nbr", "S1_in_S2",
                                 "S1_notS2_rescued")} for bar in BARS}
    for c in centres:
        pay = archive.get(prefix + c + ".json")
        rows = source.parse(pay)
        raw_len_all.append(len(rows))
        s0 = [r.mbid for r in source.parse(pay, exclude_mbid=c)]
        if len(set(s0)) != len(s0):
            dup_centres += 1
        raw_len.append(len(s0))
        s0set = set(s0)
        seen_r = set()
        for m in s0set:
            r = reason(m)
            reasons[r] += 1
            if r != "node" and r not in seen_r:
                centres_with_reason[r] += 1
                seen_r.add(r)
        s1 = s0set & nodes
        s1_len.append(len(s1))
        s2 = keep.get(c, set()) & nodes
        s3 = S3.get(c, set()) & nodes
        s4 = set(trim_out[c]) & nodes
        s5 = served(idx[c])
        if s4 != s5:
            refuse(f"S4 != S5 for centre {c}", 3)
        resc = rescuers.get(c, set()) & nodes
        if not s3 <= (s1 | resc):
            refuse(f"S3 not within S1 ∪ rescuers for centre {c}", 3)
        for st, s in (("S1", s1), ("S3", s3), ("S5", s5)):
            null_cand[st] += sum(1 for m in s if not measured[idx[m]])
        for bar in BARS:
            b = {m for m in s1 if below(m, bar)}
            d = per[bar]
            d["S1"].append(len(b))
            d["S2"].append(sum(1 for m in s2 if below(m, bar)))
            b3 = {m for m in s3 if below(m, bar)}
            d["S3"].append(len(b3))
            d["S4"].append(sum(1 for m in s4 if below(m, bar)))
            d["S5"].append(sum(1 for m in s5 if below(m, bar)))
            d["S1_surv"].append(len(b & s5))
            d["S1_in_S2"].append(len(b & s2))
            d["S1_notS2_rescued"].append(len((b - s2) & resc))
            rb = {m for m in resc if below(m, bar)}
            d["R"].append(len(rb))
            d["R_only"].append(len(rb - b))
            d["R_surv"].append(len(rb & s5))
            d["U"].append(len(b | rb))
            deleted = b3 - s5
            d["del_self"].append(sum(1 for m in deleted if remover.get((c, m)) == c))
            d["del_nbr"].append(sum(1 for m in deleted if remover.get((c, m)) == m))
            if len(deleted) != d["del_self"][-1] + d["del_nbr"][-1]:
                refuse(f"unattributed ceiling deletion at centre {c}", 3)

    print(f"\n(a) SUP-S0 raw archived list length (self-row excluded): {dist(raw_len)}")
    print(f"    rows incl. any self-row: total {sum(raw_len_all):,} vs excl. {sum(raw_len):,}; "
          f"centres with duplicate MBIDs in S0: {dup_centres}")
    print(f"    SUP-S1 length (S0 on the map): {dist(s1_len)}")
    tot = sum(reasons.values())
    print(f"\n    S0 entries by fate (pooled over {K:,} centres, {tot:,} entries):")
    print("    | fate | entries | share of S0 | centres with >= 1 |")
    print("    |---|---:|---:|---:|")
    print(f"    | lba-a6 node (-> S1) | {reasons['node']:,} | {reasons['node'] / tot:.4f} | — |")
    for r in REASONS:
        print(f"    | {r} | {reasons[r]:,} | {reasons[r] / tot:.4f} | {centres_with_reason[r]:,} |")
    if reasons["UNEXPLAINED"]:
        refuse("some S0 entries have no recorded fate", 3)
    print(f"    null-fame candidates excluded (entries, pooled): S1 {null_cand['S1']}, "
          f"S3 {null_cand['S3']}, S5 {null_cand['S5']}")

    RESULT[tier] = {}
    for bar in BARS:
        d = {k2: np.asarray(v) for k2, v in per[bar].items()}
        print(f"\n### {tier}, candidates below {bar} fame percentile (lba-a6 frame)")
        print(f"(b) below-bar count in SUP-S1: {dist(d['S1'])}")
        print("\n| stage | median | p10 | p90 | mean | ZERO: count | ZERO: fraction |")
        print("|---|---:|---:|---:|---:|---:|---:|")
        zeros = {}
        for st in ("S1", "S2", "S3", "S4", "S5"):
            a = d[st]
            z = int((a == 0).sum())
            zeros[st] = (z, z / K)
            print(f"| SUP-{st} | {np.median(a):.0f} | {q(a, 10):.0f} | {q(a, 90):.0f} | "
                  f"{a.mean():.2f} | {z:,} | {z / K:.4f} |")
        for st, lab in (("R", "rescue: below-bar nodes ranking the centre in THEIR top 50"),
                        ("R_only", "rescue, not already in S1"),
                        ("R_surv", "rescue candidates surviving to S5"),
                        ("U", "union candidate set S1 ∪ rescue")):
            a = d[st]
            z = int((a == 0).sum())
            zeros[st] = (z, z / K)
            print(f"| {lab} | {np.median(a):.0f} | {q(a, 10):.0f} | {q(a, 90):.0f} | "
                  f"{a.mean():.2f} | {z:,} | {z / K:.4f} |")
        s1tot, s1s = int(d["S1"].sum()), int(d["S1_surv"].sum())
        has = d["S1"] > 0
        share_pc = d["S1_surv"][has] / d["S1"][has]
        print(f"\n(c) S1 below-bar candidates surviving to S5: pooled {s1s:,} of {s1tot:,} "
              f"({s1s / s1tot if s1tot else float('nan'):.4f}); per-centre share median "
              f"{np.median(share_pc) if len(share_pc) else float('nan'):.4f} over {int(has.sum()):,} "
              f"centres with >= 1")
        print(f"    of S1 below-bar: in own top-50 (S2) {int(d['S1_in_S2'].sum()):,}; "
              f"outside own top-50 but rescued {int(d['S1_notS2_rescued'].sum()):,}; "
              f"neither {s1tot - int(d['S1_in_S2'].sum()) - int(d['S1_notS2_rescued'].sum()):,}")
        rtot, rs = int(d["R"].sum()), int(d["R_surv"].sum())
        print(f"    rescue direction: pooled {rtot:,} below-bar rescuers, {rs:,} survive the "
              f"ceiling ({rs / rtot if rtot else float('nan'):.4f}); not already in S1: "
              f"{int(d['R_only'].sum()):,}")
        dself, dnbr = int(d["del_self"].sum()), int(d["del_nbr"].sum())
        print(f"    S3 below-bar candidates deleted by the ceiling: {dself + dnbr:,} "
              f"(by the centre's own ceiling {dself:,}; by the neighbour's ceiling {dnbr:,})")
        exp = EXPECT_S5_ZERO[(tier, bar)]
        got = (zeros["S5"][0], K)
        ok = got == exp
        print(f"    S5 zero count reproduces graph-descriptives §1 A {exp[0]} of {exp[1]}: {ok}")
        if not ok:
            refuse(f"S5 zero {got} != graph-descriptives {exp}", 3)
        RESULT[tier][bar] = {"zeros": zeros, "median_S1": float(np.median(d["S1"])), "K": K}

# ---- reading rule (fixed before the run) -------------------------------------------------------
print(f"\n{'=' * 100}\n## Reading rule (fixed before the run)")
for tier, _cut in TIERS:
    for bar in BARS:
        r = RESULT[tier][bar]
        zpre, zpost = r["zeros"]["S1"][1], r["zeros"]["S5"][1]
        c1 = r["median_S1"] >= 1 and zpre <= zpost / 3
        c2 = zpre >= 2 * zpost / 3
        pre_share = zpre / zpost if zpost else float("nan")
        head = tier == "top 1 %" and bar == 0.9
        v = ("SUP-R1" if c1 else "SUP-R2" if c2 else "SUP-R3") if head else "(no verdict)"
        print(f"{tier}, bar {bar}: Z_pre {r['zeros']['S1'][0]}/{r['K']} = {zpre:.4f}; "
              f"Z_post {r['zeros']['S5'][0]}/{r['K']} = {zpost:.4f}; median S1 below-bar "
              f"{r['median_S1']:.0f}; Z_pre/Z_post {pre_share:.4f} (trim share {1 - pre_share:.4f}); "
              f"R1 clause {c1}; R2 clause {c2}; verdict {v}")

m_after = sha256_of(manifest_path)
if m_after != m_before:
    refuse("S4-A6 manifest changed during the run", 3)
print(f"\nS4-A6 MANIFEST.json sha256 after the run unchanged: True")
print(f"wall time {(time.monotonic() - T0) / 60:.1f} min")
