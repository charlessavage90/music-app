"""DRP- stage 3a: DRP-G3 (arm construction invariants), its red controls, and DRP-C10's
structural counts. Routes nothing.

DRP-G3 (§6), fires on the DRP-S1 artifact if any of:
  (a) the sub-graph of edges present in lba-a6 != lba-a6's CSR (neighbours and score bytes, row
      for row);
  (b) node set, pop_raw or fame_lb_pctl != lba-a6's by MBID;
  (c) any added edge failing §2.3's rule (centre >= 0.99, partner measured < 0.90, both lba-a6
      nodes, not a shipped edge);
  (d) any node's shipped degree > 50 or total degree > 60;
  (e) largest component != lba-a6's node set;
  (f) any edge_type other than 0;
  (g) the CSR not symmetric, or an edge's score differing between its two directions;
  (h) any row not sorted by neighbour id (graph.py:349's order);
  (i) an independent re-derivation of the added-edge set and its float32 score bytes from the same
      capture, written HERE without importing the construction code, differing from the artifact's;
  (j) raw fame_lb differing from lba-a6's by MBID.
Red control: a copy with one added edge dropped, and separately one with one added edge's score
moved by one float32 ulp, must each fire it.

DRP-C10 (§5), descriptive, the structural half (the frontier count per pair needs band journeys,
so it is computed at 3c): added edges; centres gaining >= 1; top-1 % artists with no neighbour
below 0.9 counting added edges; skips at the 60 bound (from the build record); added edges per
partner (max and distribution); the added partners' fame_lb_pctl distribution.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-27-drp-stage3a/drp_g3.py
"""
from __future__ import annotations

import hashlib
import json
import pickle
import sys
from collections import Counter, deque
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
from artistpath_api.graph_store import GraphStore  # noqa: E402
from artistpath_builder.artifact import deserialise  # noqa: E402  -- the shipped reader only

A0 = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
A0_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
OUT = Path(r"C:\unsung-fast\drp-stage3a")
S1 = OUT / "graph-drp-s1.bin"
CAPTURE = OUT / "capture.pkl"
BUILD = json.loads((HERE / "drp_s1_build.json").read_text(encoding="utf-8"))


def sha(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def refuse(msg: str) -> None:
    print(f"REFUSING: {msg}", file=sys.stderr, flush=True)
    sys.exit(2)


a0_sha, s1_sha, cap_sha = sha(A0), sha(S1), sha(CAPTURE)
if a0_sha != A0_SHA:
    refuse("lba-a6 sha mismatch")
if s1_sha != BUILD["artifact_sha256"] or s1_sha != json.loads(
        S1.with_name(S1.name + ".json").read_text(encoding="utf-8"))["sha256"]:
    refuse("DRP-S1 artifact sha != build record / sidecar")
if cap_sha != BUILD["capture_sha256"]:
    refuse("capture sha != build record")
print(f"sha256 OK  lba-a6 {a0_sha}\nsha256 OK  DRP-S1 {s1_sha}\nsha256 OK  capture {cap_sha}")

a0_bytes = A0.read_bytes()
s1_bytes = S1.read_bytes()
A = deserialise(a0_bytes)
Sg = deserialise(s1_bytes)
a0_store = GraphStore.from_bytes(a0_bytes)
s1_store = GraphStore.from_bytes(s1_bytes)
del a0_bytes, s1_bytes
n = len(A.mbids)
pctl = np.asarray(a0_store.fame_lb_pctl, dtype=np.float64)
measured = np.array([v is not None for v in A.fame_lb_raw], dtype=bool)
a_off, a_nb = np.asarray(A.offsets), np.asarray(A.neighbours)
a_sc = np.asarray(A.scores, dtype="<f4")
a_rows = [{int(a_nb[k]): a_sc[k:k + 1].tobytes() for k in range(a_off[i], a_off[i + 1])}
          for i in range(n)]

# ---- (i)'s independent side: re-derive the added edges from the capture -------------------------
with CAPTURE.open("rb") as fh:
    cap = pickle.load(fh)
T, RK, J = cap["trim_in"], cap["ranking"], cap["top_j"]
node_of = {m: i for i, m in enumerate(A.mbids)}
# Own top-j: a stable descending sort on ranking with MBID ascending as the tie-break, computed
# with numpy argsort here rather than the construction's sorted(key=...).
top = {}
for u, e in T.items():
    ks = list(e)
    if not ks:
        top[u] = set()
        continue
    vals = np.array([RK[u][k] for k in ks], dtype=np.float64)
    order = np.lexsort((np.array(ks, dtype=object).astype(str), -vals))
    top[u] = {ks[o] for o in order[:J]}
rescuers: dict[str, list[str]] = {}
for u, ks in top.items():
    for v in ks:
        rescuers.setdefault(v, []).append(u)
expect: dict[tuple[int, int], bytes] = {}
deg_now = np.diff(a_off).astype(np.int64)
for c in range(n):  # ascending node id
    if not (measured[c] and pctl[c] >= 0.99):
        continue
    cm = A.mbids[c]
    partners = set(v for v in T.get(cm, ()) if v in top[cm]) | set(rescuers.get(cm, ()))
    pool = []
    for v in partners:
        j = node_of.get(v)
        if j is None or j in a_rows[c] or not measured[j] or not (pctl[j] < 0.90):
            continue
        st = max(RK.get(cm, {}).get(v, -np.inf), RK.get(v, {}).get(cm, -np.inf))
        pool.append((-st, v, j))
    pool.sort()
    took = 0
    for _negst, v, j in pool:
        if took == 10:
            break
        if deg_now[j] >= 60:
            continue
        s = np.float32(max(T.get(cm, {}).get(v, 0.0), T.get(v, {}).get(cm, 0.0))).tobytes()
        expect[(min(c, j), max(c, j))] = s
        deg_now[c] += 1
        deg_now[j] += 1
        took += 1
del T, RK, cap, top, rescuers
print(f"independent re-derivation: {len(expect)} added edges")


def gate(off, nb, sc, et, mbids, pop_raw, fame_pctl, fame_raw) -> list[str]:
    """Every DRP-G3 condition over one artifact's arrays; returns the violations."""
    v: list[str] = []
    if list(mbids) != list(A.mbids):
        return ["(b) node set / order differs"]
    if not np.array_equal(np.asarray(pop_raw, dtype=np.float64), np.asarray(A.pop_raw, dtype=np.float64)):
        v.append("(b) pop_raw differs")
    if not np.array_equal(fame_pctl, pctl):
        v.append("(b) fame_lb_pctl differs")
    if list(fame_raw) != list(A.fame_lb_raw):
        v.append("(j) raw fame_lb differs")
    if (np.asarray(et) != 0).any():
        v.append("(f) edge_type other than 0")
    rows = []
    for i in range(n):
        ids = nb[off[i]:off[i + 1]].tolist()
        if ids != sorted(ids) or len(set(ids)) != len(ids):
            v.append(f"(h) row {i} not sorted/unique")
        rows.append({j: sc[k:k + 1].tobytes() for j, k in zip(ids, range(off[i], off[i + 1]))})
    added = {}
    for i in range(n):
        ship = {j: b for j, b in rows[i].items() if j in a_rows[i]}
        if ship != a_rows[i]:
            v.append(f"(a) shipped sub-row {i} differs")
        if len(rows[i]) > 60:
            v.append(f"(d) total degree {len(rows[i])} > 60 at {i}")
        if len(a_rows[i]) > 50:
            v.append(f"(d) shipped degree > 50 at {i}")
        for j, b in rows[i].items():
            if rows[j].get(i) != b:
                v.append(f"(g) asymmetric edge {i}-{j}")
            if j not in a_rows[i]:
                added[(min(i, j), max(i, j))] = b
    for (i, j) in added:
        hi, lo = (i, j) if pctl[i] >= pctl[j] else (j, i)
        if not (measured[hi] and pctl[hi] >= 0.99 and measured[lo] and pctl[lo] < 0.90):
            v.append(f"(c) added edge {i}-{j} fails §2.3's rule")
    if added != expect:
        v.append(f"(i) added-edge set/score bytes differ from the independent re-derivation "
                 f"({len(set(added) ^ set(expect))} pairs in the symmetric difference; "
                 f"{sum(1 for k in set(added) & set(expect) if added[k] != expect[k])} score mismatches)")
    seen = np.zeros(n, dtype=bool)
    q = deque([0])
    seen[0] = True
    while q:
        u = q.popleft()
        for w in rows[u]:
            if not seen[w]:
                seen[w] = True
                q.append(w)
    if not seen.all():
        v.append(f"(e) not one component: {int((~seen).sum())} nodes unreachable")
    return v


s_off, s_nb = np.asarray(Sg.offsets), np.asarray(Sg.neighbours)
s_sc = np.asarray(Sg.scores, dtype="<f4").copy()
s_et = np.asarray(Sg.edge_types)
s_pctl = np.asarray(s1_store.fame_lb_pctl, dtype=np.float64)
real = gate(s_off, s_nb, s_sc, s_et, Sg.mbids, Sg.pop_raw, s_pctl, Sg.fame_lb_raw)
print(f"DRP-G3 on the artifact: {len(real)} violations {real[:5]}")

# ---- red controls ---------------------------------------------------------------------------------
first = sorted(expect)[0]
i0, j0 = first
# (1) one added edge dropped (both directions)
keep = np.ones(len(s_nb), dtype=bool)
for a, b in ((i0, j0), (j0, i0)):
    lo, hi = s_off[a], s_off[a + 1]
    keep[lo + int(np.flatnonzero(s_nb[lo:hi] == b)[0])] = False
d_off = np.zeros_like(s_off)
d_off[1:] = np.cumsum([int(keep[s_off[i]:s_off[i + 1]].sum()) for i in range(n)])
red_drop = gate(d_off, s_nb[keep], s_sc[keep], s_et[keep], Sg.mbids, Sg.pop_raw, s_pctl, Sg.fame_lb_raw)
# (2) one added edge's score moved by one float32 ulp (both directions, so symmetry still holds)
u_sc = s_sc.copy()
for a, b in ((i0, j0), (j0, i0)):
    lo, hi = s_off[a], s_off[a + 1]
    k = lo + int(np.flatnonzero(s_nb[lo:hi] == b)[0])
    u_sc[k] = np.nextafter(u_sc[k], np.float32(np.inf), dtype=np.float32)
red_ulp = gate(s_off, s_nb, u_sc, s_et, Sg.mbids, Sg.pop_raw, s_pctl, Sg.fame_lb_raw)
print(f"red control, one added edge dropped: {len(red_drop)} violations {red_drop[:3]}")
print(f"red control, one score moved one ulp: {len(red_ulp)} violations {red_ulp[:3]}")
verdict = ("PASS" if not real and red_drop and red_ulp else
           "FAIL (construction)" if real else "FAIL (red control did not fire: the gate is blind)")
print(f"DRP-G3: {verdict}")

# ---- DRP-C10, structural half --------------------------------------------------------------------
per_node = Counter()
for i, j in expect:
    per_node[i] += 1
    per_node[j] += 1
centres = [i for i in range(n) if measured[i] and pctl[i] >= 0.99]
partners = sorted({(j if pctl[i] >= 0.99 else i) for i, j in expect})
gained = sum(1 for c in centres if per_node[c] > 0)
per_partner = np.array([per_node[p] for p in partners])
partner_pctl = np.array([pctl[p] for p in partners])


def walled(off, nb) -> int:
    return sum(1 for c in centres
               if not any(measured[w] and pctl[w] < 0.90 for w in nb[off[c]:off[c + 1]]))


def qs(a):
    return {"min": float(a.min()), "p10": float(np.percentile(a, 10)), "median": float(np.median(a)),
            "p90": float(np.percentile(a, 90)), "max": float(a.max()), "mean": float(a.mean())}


c10 = {
    "added_edges": len(expect),
    "centres": len(centres), "centres_gaining_ge1": gained,
    "top1pct_no_neighbour_below_0.9": {"lba_a6": walled(a_off, a_nb), "drp_s1": walled(s_off, s_nb),
                                        "cited": "trim-supply README / graph-descriptives §1 A (381 of 874 post-trim)"},
    "skips_at_60": BUILD["skips_at_60"],
    "added_per_centre": qs(np.array([per_node[c] for c in centres])),
    "distinct_partners": len(partners),
    "added_per_partner": qs(per_partner) | {"distribution": dict(sorted(Counter(per_partner.tolist()).items()))},
    "partner_fame_lb_pctl": qs(partner_pctl) | {
        "below_0.5": int((partner_pctl < 0.5).sum()), "below_0.7": int((partner_pctl < 0.7).sum()),
        "in_[0.8,0.9)": int(((partner_pctl >= 0.8) & (partner_pctl < 0.9)).sum())},
    "frontier_count_per_pair": "computed at stage 3c from the band journeys (it needs them)",
}
print(json.dumps(c10, indent=1))
text = json.dumps({"artifact_sha256": s1_sha, "lba_a6_sha256": a0_sha, "capture_sha256": cap_sha,
                   "violations": real, "red_drop_violations": len(red_drop),
                   "red_ulp_violations": len(red_ulp), "verdict": verdict, "DRP-C10": c10},
                  indent=1) + "\n"
(HERE / "drp_g3.json").write_text(text, encoding="utf-8", newline="\n")
print(f"wrote drp_g3.json sha256 {hashlib.sha256(text.encode()).hexdigest()}")
