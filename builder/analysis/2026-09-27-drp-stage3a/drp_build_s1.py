"""DRP- stage 3a: DRP-G2 (build identity) and the DRP-S1 artifact (§2.3). Routes nothing.

Two modes, one per process:

  build  -- the shipped `build_from_archive` on the S4-A6 archive with `trim_supply.py`'s pinned
            config and capture (cand_build.py's config exactly), then:
            DRP-G2: the rebuild must equal graph-lba-a6.bin in node order, offsets, neighbours,
            scores bytes, pop_raw and raw fame_lb (compared against the builder's own
            `deserialise` of the file). Exact.
            Then, only if G2 passes: saves the cap's capture (its input adjacency of directed
            rescaled scores, and its unclipped ranking) to OUT/capture.pkl for DRP-G3's
            independent re-derivation, and constructs DRP-S1 by §2.3's rule, serialised by the
            shipped `serialise` to OUT/graph-drp-s1.bin with a sidecar.
  red    -- DRP-G2's red control: the same rebuild at union_top_j 49 must DIFFER from
            graph-lba-a6.bin, or the check is blind. Saves nothing.

§2.3's rule, verbatim in effect:
  1. Centres = lba-a6 nodes with measured fame_lb_pctl >= 0.99 in lba-a6's own frame.
  2. Candidates = the centre's pre-ceiling union partners (own top-50 plus everyone ranking the
     centre in THEIR top-50; trim-supply's SUP-S3) not already its lba-a6 neighbour, lba-a6 nodes,
     measured fame_lb_pctl < 0.90.
  3. Centres in ascending node id. Each walks its candidates strongest first by the shipped trim's
     symmetric strength key (the pair's stronger UNCLIPPED ranking value; ties on lowest partner
     MBID), adding until R = 10 added or the list is exhausted, skipping any candidate whose
     current degree (shipped + added so far) is already 60; a skip does not count toward R.
  4. Score = the pipeline's rescaled score for the pair, symmetrised on the stronger direction,
     exactly as the shipped union emits it (graph.py symmetrise: max of the two directions).
  5. Every shipped edge kept; every edge_type 0; assembled as a Graph and serialised by the
     shipped `serialise`.
  6. Degree <= 50 on shipped edges, <= 60 in total.

Outputs committed: drp_g2.json / drp_g2_red.json (verdicts and field-by-field equality) and
drp_s1_build.json (artifact sha, added-edge count; added edges as node-id pairs with float32
score bytes). No interior name is written anywhere.

    cd builder && PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
      uv run python -u analysis/2026-09-27-drp-stage3a/drp_build_s1.py build   # or red
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import logging
import pickle
import sys
import time
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / "api" / "src"))
sys.path.insert(0, str(HERE.parent / "2026-09-07-degree-ceiling-falsifier"))
sys.path.insert(0, str(HERE.parent / "2026-09-10-lbd-supply"))

MODE = sys.argv[1] if len(sys.argv) > 1 else ""
if MODE not in ("build", "red"):
    print("usage: drp_build_s1.py build|red", file=sys.stderr)
    sys.exit(64)

# ---- pins, carried from trim_supply.py -------------------------------------------------------
ARCHIVE = Path(r"C:\unsung-fast\lbd-archives\S4-A6")
FAME_DIR = Path(r"C:\unsung-fast\lbd-archives\S4-A6-fame")
POPULATION = Path(r"C:\unsung-fast\lbd-archives\population_cxa_mbids.txt")
GRAPH = Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin")
ARCHIVE_MANIFEST_SHA = "950e3ee86e1156bd3c4b389ff5eef4ffabc0972d0bac3f6a2c6d37d74caa4af3"
GRAPH_SHA = "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"
DROP_LIST = "unlistenable_drop_algb_20260809.json"
OUT = Path(r"C:\unsung-fast\drp-stage3a")
S1_GRAPH = OUT / "graph-drp-s1.bin"
CAPTURE = OUT / "capture.pkl"
CENTRE_CUT, PARTNER_BAR, R, TOTAL_CEILING, SHIPPED_CEILING = 0.99, 0.90, 10, 60, 50


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def refuse(msg: str, code: int = 2) -> None:
    print(f"REFUSING: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def write_json(path: Path, obj) -> str:
    text = json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8", newline="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


T0 = time.monotonic()
manifest_path = ARCHIVE / "MANIFEST.json"
m_before = sha256_of(manifest_path)
if m_before != ARCHIVE_MANIFEST_SHA:
    refuse(f"S4-A6 manifest sha256 {m_before} != pin")
g_sha = sha256_of(GRAPH)
g_side = json.loads(GRAPH.with_name(GRAPH.name + ".json").read_text(encoding="utf-8"))["sha256"]
if not (g_sha == g_side == GRAPH_SHA):
    refuse(f"graph-lba-a6.bin sha256 {g_sha}; sidecar {g_side}; pin {GRAPH_SHA}")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
p_sha = sha256_of(POPULATION)
if p_sha != manifest["population"]["file_sha256"]:
    refuse("population file sha256 != archive manifest")
print(f"sha256 OK  S4-A6 MANIFEST.json {m_before}\nsha256 OK  graph-lba-a6.bin {g_sha}\n"
      f"sha256 OK  population {p_sha}", flush=True)

import artistpath_builder.pipeline as pl  # noqa: E402
from artistpath_builder import graph as graph_mod  # noqa: E402
from artistpath_builder.archive import LocalArchive  # noqa: E402
from artistpath_builder.artifact import deserialise, serialise  # noqa: E402
from artistpath_builder.config import CANDIDATE_ALGORITHM, BuilderConfig  # noqa: E402
from artistpath_api.graph_store import GraphStore  # noqa: E402
from dcf_ceiling_sweep import ArchiveWriteRefused, ReadOnlyArchive  # noqa: E402
from lbd_source import LbdBulkSource  # noqa: E402

for mod in (pl, graph_mod):
    if (REPO / "builder" / "src").resolve() not in Path(mod.__file__).resolve().parents:
        refuse(f"{mod.__name__} loaded from {mod.__file__}, not this worktree", 3)
import artistpath_api.graph_store as _gs  # noqa: E402
if (REPO / "api" / "src").resolve() not in Path(_gs.__file__).resolve().parents:
    refuse(f"graph_store loaded from {_gs.__file__}, not this worktree", 3)


class FameOverlayArchive:
    """Copied from cand_build.py via trim_supply.py: similarity from the arm, `fame/` from fame."""

    def __init__(self, similarity, fame) -> None:
        self._similarity = similarity
        self._fame = fame

    def _pick(self, key: str):
        return self._fame if key.startswith("fame/") else self._similarity

    def put(self, key: str, payload: bytes) -> None:
        raise ArchiveWriteRefused(f"drp_build_s1 tried to write {key!r}; both halves are read-only")

    def get(self, key: str):
        return self._pick(key).get(key)

    def has(self, key: str) -> bool:
        return self._pick(key).has(key)

    def keys(self):
        yield from self._similarity.keys()
        yield from self._fame.keys()


CAP: dict = {}
_orig_trim = pl.trimmed_union_cap


def _w_trim(adjacency, top_j, degree_ceiling, *, ranking):
    """Pass-through: records the cap's inputs, returns the shipped function's output unchanged."""
    out = _orig_trim(adjacency, top_j, degree_ceiling, ranking=ranking)
    CAP["trim_in"], CAP["ranking"] = adjacency, ranking
    CAP["top_j"], CAP["ceiling"] = top_j, degree_ceiling
    return out


pl.trimmed_union_cap = _w_trim
DATA = REPO / "builder" / "src" / "artistpath_builder" / "data"
config = BuilderConfig(require_fame=True, algorithm=CANDIDATE_ALGORITHM, drop_unlistenable=True,
                       unlistenable_list_path=DATA / DROP_LIST)
if MODE == "red":
    config = dataclasses.replace(config, union_top_j=49)
print(f"mode {MODE}: cap_strategy={config.cap_strategy} union_top_j={config.union_top_j} "
      f"union_degree_ceiling={config.union_degree_ceiling} damping={config.similarity_damping} "
      f"rescale={config.similarity_rescale}", flush=True)
source = LbdBulkSource(config)
archive = FameOverlayArchive(ReadOnlyArchive(LocalArchive(ARCHIVE)),
                             ReadOnlyArchive(LocalArchive(FAME_DIR)))
blog = logging.getLogger("artistpath_builder")
blog.addHandler(type("H", (logging.Handler,), {
    "emit": lambda self, r: print(f"  builder: {r.getMessage()}", flush=True)})())
blog.setLevel(logging.INFO)
t_build = time.monotonic()
built = pl.build_from_archive(config, archive, source)
pl.trimmed_union_cap = _orig_trim
print(f"build: {len(built.mbids):,} nodes, {int(built.offsets[-1]):,} CSR entries "
      f"({(time.monotonic() - t_build) / 60:.1f} min)", flush=True)

# ---- DRP-G2: field-by-field against the builder's own deserialise of the file --------------------
payload = GRAPH.read_bytes()
ref = deserialise(payload)
eq = {
    "node_order": list(ref.mbids) == list(built.mbids),
    "offsets": np.array_equal(np.asarray(ref.offsets), np.asarray(built.offsets)),
}
same_shape = eq["node_order"] and eq["offsets"]
eq["neighbours"] = same_shape and np.array_equal(np.asarray(ref.neighbours),
                                                 np.asarray(built.neighbours))
eq["scores_bytes"] = same_shape and (np.asarray(ref.scores, dtype="<f4").tobytes()
                                     == np.asarray(built.scores, dtype="<f4").tobytes())
eq["pop_raw"] = eq["node_order"] and list(ref.pop_raw) == list(built.pop_raw)
eq["fame_lb_raw"] = eq["node_order"] and list(ref.fame_lb_raw) == list(built.fame_lb_raw)
all_eq = all(eq.values())
rebuilt_bytes = serialise(built)
eq_informative = {"serialised_bytes_equal_file": rebuilt_bytes == payload,
                  "rebuilt_sha256": hashlib.sha256(rebuilt_bytes).hexdigest()}
del rebuilt_bytes
print(f"G2 fields: {eq}\n   informative: {eq_informative}", flush=True)

if MODE == "red":
    verdict = "PASS (red control fired: union_top_j 49 differs)" if not all_eq else \
        "FAIL (G2 blind: union_top_j 49 reproduced lba-a6)"
    d = write_json(HERE / "drp_g2_red.json", {"mode": "red", "union_top_j": 49, "fields_equal": eq,
                                              "verdict": verdict, **eq_informative})
    print(f"DRP-G2 red control: {verdict}\nwrote drp_g2_red.json sha256 {d}")
    if sha256_of(manifest_path) != m_before:
        refuse("S4-A6 manifest changed during the run", 3)
    sys.exit(0)

verdict = "PASS" if all_eq else "FAIL"
d = write_json(HERE / "drp_g2.json", {"mode": "build", "union_top_j": config.union_top_j,
                                      "fields_equal": eq, "verdict": verdict, **eq_informative})
print(f"DRP-G2: {verdict}\nwrote drp_g2.json sha256 {d}", flush=True)
if not all_eq:
    refuse("DRP-G2 failed: the candidate capture is untrusted; stop (§6)", 3)

# ---- save the capture for DRP-G3's independent re-derivation ---------------------------------
trim_in, ranking = CAP["trim_in"], CAP["ranking"]
OUT.mkdir(parents=True, exist_ok=True)
with CAPTURE.open("wb") as fh:
    pickle.dump({"trim_in": trim_in, "ranking": ranking, "top_j": CAP["top_j"],
                 "ceiling": CAP["ceiling"]}, fh, protocol=pickle.HIGHEST_PROTOCOL)
cap_sha = sha256_of(CAPTURE)
print(f"capture: {CAPTURE} sha256 {cap_sha}", flush=True)

# ---- §2.3: DRP-S1 -----------------------------------------------------------------------------
store = GraphStore.from_bytes(payload)
del payload
n = store.artist_count
mbids = list(store.mbids)
idx = {m: i for i, m in enumerate(mbids)}
fame = list(ref.fame_lb_raw)
pctl = np.asarray(store.fame_lb_pctl, dtype=np.float64)
if not np.array_equal(pctl, GraphStore.fame_percentiles(fame)):
    refuse("store fame_lb_pctl != fame_percentiles(raw fame_lb)", 3)
measured = np.array([v is not None for v in fame], dtype=bool)
off = np.asarray(ref.offsets)
nb = np.asarray(ref.neighbours)
shipped = [set(nb[off[i]:off[i + 1]].tolist()) for i in range(n)]
deg = np.diff(off).astype(np.int64)
if int(deg.max()) > SHIPPED_CEILING:
    refuse(f"shipped degree {int(deg.max())} > 50", 3)

top_j = CAP["top_j"]
keep_top = {u: set(sorted(e, key=lambda v: (-ranking[u][v], v))[:top_j]) for u, e in trim_in.items()}


def strength(u: str, v: str) -> float:
    return max(ranking.get(u, {}).get(v, float("-inf")), ranking.get(v, {}).get(u, float("-inf")))


centres = [i for i in range(n) if measured[i] and pctl[i] >= CENTRE_CUT]  # ascending node id
# Reverse index: rev[c] = everyone who ranks c in THEIR own top-j (the union's rescue direction).
rev: dict[str, set[str]] = {}
for u, ks in keep_top.items():
    for v in ks:
        rev.setdefault(v, set()).add(u)

added: list[tuple[int, int, float]] = []
skips = 0
cur = deg.copy()
for c in centres:
    cm = mbids[c]
    # SUP-S3: an edge (c, v) survives the union iff v is in c's top-j or c is in v's top-j.
    union = {v for v in trim_in.get(cm, {}) if v in keep_top[cm]} | rev.get(cm, set())
    cands = [v for v in union
             if v in idx and idx[v] not in shipped[c] and measured[idx[v]]
             and pctl[idx[v]] < PARTNER_BAR]
    cands.sort(key=lambda v: (-strength(cm, v), v))
    got = 0
    for v in cands:
        if got == R:
            break
        j = idx[v]
        if cur[j] >= TOTAL_CEILING:
            skips += 1
            continue
        # graph.py symmetrise: max of the two directed rescaled scores (0.0 where absent)
        score = max(trim_in.get(cm, {}).get(v, 0.0), trim_in.get(v, {}).get(cm, 0.0))
        added.append((c, j, score))
        cur[c] += 1
        cur[j] += 1
        got += 1
print(f"DRP-S1: centres {len(centres)}; added edges {len(added)}; skips at 60 {skips}; "
      f"max total degree {int(cur.max())}", flush=True)
if int(cur.max()) > TOTAL_CEILING:
    refuse("total degree > 60", 3)

# ---- assemble and serialise (shipped `serialise`, APG1 unchanged) ----------------------------
rows = [dict(zip(nb[off[i]:off[i + 1]].tolist(),
                 np.asarray(ref.scores[off[i]:off[i + 1]], dtype=np.float32).tolist()))
        for i in range(n)]
for c, j, score in added:
    f = float(np.float32(score))
    rows[c][j] = f
    rows[j][c] = f
new_off = np.zeros(n + 1, dtype=np.int32)
new_nb: list[int] = []
new_sc: list[float] = []
for i in range(n):
    for j in sorted(rows[i]):  # graph.py:349's order: ascending neighbour id
        new_nb.append(j)
        new_sc.append(rows[i][j])
    new_off[i + 1] = len(new_nb)
s1 = dataclasses.replace(ref, offsets=new_off, neighbours=np.asarray(new_nb, dtype=np.int32),
                         scores=np.asarray(new_sc, dtype=np.float32),
                         edge_types=np.zeros(len(new_nb), dtype=np.uint8))
blob = serialise(s1)
S1_GRAPH.write_bytes(blob)
s1_sha = hashlib.sha256(blob).hexdigest()
S1_GRAPH.with_name(S1_GRAPH.name + ".json").write_text(json.dumps({
    "sha256": s1_sha, "bytes": len(blob), "derived_from": {"graph-lba-a6.bin": GRAPH_SHA},
    "rule": "DRP- pre-registration §2.3 (DRP-S1: top-1 % centres, partners < 0.90 from the "
            "pre-ceiling union, R = 10, total degree <= 60, added above the ceiling)",
    "capture_sha256": cap_sha, "edge_count": int(new_off[-1]), "added_edges": len(added),
    "not_for_production": True}, indent=1) + "\n", encoding="utf-8")
print(f"wrote {S1_GRAPH} sha256 {s1_sha} ({len(blob):,} bytes)", flush=True)
d = write_json(HERE / "drp_s1_build.json", {
    "artifact_sha256": s1_sha, "capture_sha256": cap_sha, "lba_a6_sha256": GRAPH_SHA,
    "centres": len(centres), "added_edges": len(added), "skips_at_60": skips,
    "csr_entries": int(new_off[-1]),
    "added": [[c, j, np.float32(sc).tobytes().hex()] for c, j, sc in added]})
print(f"wrote drp_s1_build.json sha256 {d}")
if sha256_of(manifest_path) != m_before:
    refuse("S4-A6 manifest changed during the run", 3)
print(f"wall time {(time.monotonic() - T0) / 60:.1f} min")
