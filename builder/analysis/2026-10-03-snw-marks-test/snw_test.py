"""`SNW-`: the `DSL-` listen's weak-step marks against three step measures (#271). RUN ONCE.

Governing document: `docs/superpowers/specs/2026-10-03-issue-271-shared-neighbours-marks-preregistration.md`.
It wins wherever anything here disagrees with it. Every constant below is fixed there, beside its
plain sentence, and was committed before any session read which steps carry marks.

**Run by a fresh session that did not design this test**, once, after the pre-registration and this
script are committed and `experiment-reviewer`'s findings are resolved (`SNW-RS`). It refuses to run
twice: an existing `snw_result.json` stops it.

What it reads, and nothing else:
  * `dsl_page_data.json`  — each journey's artists, per row and side token (L/R);
  * `dsl_verdicts.json`   — ONLY `rows[pair][depth]["weak"]` (`DSL-W`). Picks, strength,
    identification, recognition marks, ticks and notes are never read (`DRP-AM7-11`: no re-tally);
  * `dsl_result.json`     — ONLY `mapping_unsealed` (which side was which) and `maps` (their shas).
All three are pinned to their blobs at commit 273ec27.

The three measures (`SNW-M1`..`M3`) are restated from source, never imported from `exploration/`:
  M1 similarity        the stored edge score u->v in the map the step was shown from;
  M2 shared neighbours  |N(u) & N(v)| / max(1, deg u + deg v - |N(u) & N(v)|), the same map
                        (`exploration/r2-nsim/r2nsim_core.py` `_shared`, `jac`);
  M3 model rater        `exploration/kit/rate.py`'s 0-3 rating of the unordered name pair, its cache
                        read as pinned data, misses rated with its prompt restated verbatim.

Two steps (`SNW-RS`), from `api/`:

    PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      ../builder/analysis/2026-10-03-snw-marks-test/snw_test.py --rate-only   # reads no answer
    PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy uv run python -u \\
      ../builder/analysis/2026-10-03-snw-marks-test/snw_test.py               # the one read
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DSL_DIR = ROOT / "builder" / "analysis" / "2026-09-30-drp-stage5-listen"
PREREG = ROOT / "docs" / "superpowers" / "specs" / "2026-10-03-issue-271-shared-neighbours-marks-preregistration.md"
RESULT = HERE / "snw_result.json"

# ---- pinned inputs (SNW-IN) --------------------------------------------------------------------
INPUT_COMMIT = "273ec2715cbf828347b30e652ce406ad298150a7"
INPUT_BLOBS = {   # git blob ids at INPUT_COMMIT; checked with `git hash-object` (autocrlf-aware)
    "dsl_verdicts.json": "e5b474afeb42fa4c3c7cade64c92c320a440ca00",
    "dsl_page_data.json": "f923b0bf734a8c768272a9316d464cc0af5d559f",
    "dsl_result.json": "019140ec792753a000955597f89a239eb055a156",
}
ROLES = ("incumbent", "challenger")   # today's app; the candidate (`DRP-S1P3`)
MAPS = {   # absolute path, sha256 of the file's bytes (#271; `dsl_common`/`drp_sweep` pins)
    "incumbent": (Path("C:/dev/music-app/builder/scratch/graph-lba-a6.bin"),
                  "28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b"),
    "challenger": (Path("C:/unsung-fast/drp-stage3a/graph-drp-s1.bin"),
                   "418fe6660795f735c7dfe1960e65300c15f4401db2a15186fb6439d646dda15f"),
}
RATER_CACHE_SRC = ROOT / "exploration" / "kit" / "step_cache.jsonl"
RATER_CACHE_SRC_SHA_LF = "af527bb9b858b01b88ed8b42762bf8efcc07070fd700c78ebc32f2735daad54a"
RATER_CACHE_OWN = HERE / "snw_rater_cache.jsonl"   # this test's fresh ratings; append-only
RATING_PASSES = HERE / "snw_rating_passes.jsonl"   # one line per --rate-only pass (SNW-RS step 1)
DEPTHS = ("5", "10", "20")
TOKENS = ("L", "R")
N_PAIRS = 8

# ---- the bar (SNW-F), fixed in the pre-registration --------------------------------------------
MEASURES = ("similarity", "shared_neighbours", "rater")
C_FLOOR = 0.65                    # SNW-F1
FAMILY_ALPHA = 0.05
MEASURE_ALPHA = FAMILY_ALPHA / len(MEASURES)   # SNW-F2: 1/60 per measure
MIN_MARKED_PER_SIDE = 5           # SNW-U
N_DRAWS = 20_000                  # SNW-N
SEED = 271
RATER_MAX_UNSCORABLE_MARKED = 0.10   # SNW-V: more than max(1 step, 10 %) of a side's marks unscorable ->
                                     # the rater's outcome is not compared with M1/M2
RATING_MAX_PASSES = 3                # SNW-RS step 1's stopping rule

# ---- the rater, restated verbatim from exploration/kit/rate.py ---------------------------------
RATER_MODEL = "sonnet"
RATER_BATCH = 40
SYSTEM = (
    "You are a music expert with deep knowledge of artists across all genres, eras and countries, "
    "including obscure ones. You rate artist-to-artist transitions in a listening journey. "
    "Answer only in the exact format requested."
)
PROMPT_HEAD = """For each numbered pair below, rate how naturally the second artist follows the first in a
listening journey (like consecutive songs on a well-made radio station or playlist):

3 = same scene or clearly kindred sound; an obvious next track
2 = plausible neighbour; a listener of one would likely enjoy the other
1 = a stretch; some thread connects them but it is a jump
0 = jarring or unrelated
U = you genuinely do not know one of the artists well enough to judge (use sparingly; judge from
    your best knowledge plus the metadata where you reasonably can)

Metadata in brackets is MusicBrainz type / country / start year / disambiguation where known.
Reply with one line per pair, exactly "<number> <rating>", nothing else.

"""


class Refused(SystemExit):
    """A run-state or identity check failed: no read exists."""


# ================================================================================================
# inputs
# ================================================================================================
@dataclass
class Journey:
    key: str
    depth: str
    token: str
    role: str
    path: list[str]            # MBIDs, endpoints included
    weak: list[int]            # step indices; step i joins path[i] and path[i+1]

    @property
    def n_steps(self) -> int:
        return len(self.path) - 1


def weak_marks_only(verdicts: dict) -> dict:
    """The ONLY projection of the answer file this test reads: rows[pair][depth]["weak"]."""
    return {pair: {d: {t: list(entry["weak"][t]) for t in TOKENS} for d, entry in depths.items()}
            for pair, depths in verdicts["rows"].items()}


def side_mapping_only(result: dict) -> tuple[dict, dict]:
    """The ONLY projection of the unblind result this test reads."""
    return result["mapping_unsealed"], {r: result["maps"][r]["sha256"] for r in ROLES}


def build_journeys(page_data: dict, weak: dict, mapping: dict) -> list[Journey]:
    """Every presented journey with its marks. Refuses unless all 8 x 3 x 2 are present and every mark
    names a real step (`SNW-RS`)."""
    if len(page_data["pairs"]) != N_PAIRS:
        raise Refused(f"run state: {len(page_data['pairs'])} pairs in the page data, not {N_PAIRS}")
    out = []
    for pair in page_data["pairs"]:
        key = pair["key"]
        if set(mapping.get(key, {})) != set(TOKENS) or set(mapping[key].values()) != set(ROLES):
            raise Refused(f"run state: no side mapping for {key}")
        rows = {str(r["depth"]): r for r in pair["rows"]}
        if set(rows) != set(DEPTHS):
            raise Refused(f"run state: {key} lacks a depth")
        for d in DEPTHS:
            for t in TOKENS:
                path = [a["mbid"] for a in rows[d][t]["artists"]]
                try:
                    marks = weak[key][d][t]
                except KeyError as e:
                    raise Refused(f"run state: no weak-step answer for {key} d{d} {t}") from e
                if any(not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(path) - 1
                       for i in marks):
                    raise Refused(f"run state: a weak mark on {key} d{d} {t} names no step")
                out.append(Journey(key, d, t, mapping[key][t], path, sorted(set(marks))))
    return out


# ================================================================================================
# the three measures
# ================================================================================================
def edge_similarity(store, u: int, v: int) -> float:
    """`SNW-M1`: the stored score on u->v. Refuses if u, v are not connected in this map."""
    lo, hi = int(store.offsets[u]), int(store.offsets[u + 1])
    row = store.neighbours[lo:hi]
    j = int(np.searchsorted(row, v))
    if j >= len(row) or int(row[j]) != v:
        # rows may be unsorted in a hand-built store; fall back to a scan before refusing
        hits = np.nonzero(row == v)[0]
        if not len(hits):
            raise Refused(f"identity: a shown step is not a connection of its map ({u}->{v})")
        j = int(hits[0])
    return float(store.scores[lo + j])


def shared_neighbours(store, u: int, v: int) -> float:
    """`SNW-M2`, restated from `r2nsim_core._shared`: inter = common neighbours of u and v (the map is
    symmetric with no self-loops, so this is A@A's (u, v) entry); jac = inter / max(1, deg u + deg v -
    inter). Note u is in N(v) and v in N(u), so each counts in the denominator and never in inter."""
    nu = store.neighbours[int(store.offsets[u]):int(store.offsets[u + 1])]
    nv = store.neighbours[int(store.offsets[v]):int(store.offsets[v + 1])]
    inter = len(np.intersect1d(nu, nv, assume_unique=True))
    return inter / max(1, len(nu) + len(nv) - inter)


def rater_key(name_u: str, name_v: str) -> str:
    a, b = sorted((name_u, name_v))
    return f"{a} || {b}"


def load_rater_cache(*paths: Path) -> dict:
    """rate.py's `load_cache`: one JSON object per line, later lines win, bad lines skipped."""
    out: dict = {}
    for p in paths:
        if not p.exists():
            continue
        for line in p.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    d = json.loads(line)
                    out[d["k"]] = d["r"]
                except Exception:
                    pass
    return out


def rater_meta(store, v: int) -> str:
    """rate.py's `meta`, verbatim in effect."""
    f = store.facts_of(v)
    bits = [f.get("type"), f.get("country") or f.get("area"), (f.get("begin") or "")[:4] or None]
    dis = store.disambiguations[v] if v < len(store.disambiguations) else ""
    if dis:
        bits.append(dis)
    return ", ".join(b for b in bits if b)


def parse_ratings(text: str, n: int) -> dict[int, int | str]:
    """rate.py's parse: lines "<number> <rating>", 0-3 or U; index is 0-based."""
    got: dict[int, int | str] = {}
    for m in re.finditer(r"^\s*(\d+)[.):]?\s+([0-3]|U)\b", text, re.M):
        i = int(m.group(1)) - 1
        if 0 <= i < n:
            r = m.group(2)
            got[i] = int(r) if r.isdigit() else "U"
    return got


def call_model(lines: list[str]) -> str:   # pragma: no cover - needs the CLI
    claude = shutil.which("claude.cmd") or shutil.which("claude") or "claude"
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run(
            [claude, "-p", "--model", RATER_MODEL, "--system-prompt", SYSTEM, "--tools", "",
             "--setting-sources", "", "--strict-mcp-config", "--no-session-persistence",
             "--output-format", "text"],
            input=PROMPT_HEAD + "\n".join(lines), capture_output=True, text=True, encoding="utf-8",
            cwd=td, timeout=600)
    return r.stdout


def rate_missing(todo: list[tuple[str, str, str, str, str]], call=call_model) -> dict:
    """todo: (key, name_u, meta_u, name_v, meta_v). Batches of 40, two attempts each (rate.py), every
    answer appended to this test's own cache. Returns {key: rating} for what came back."""
    out = {}
    for b in range(0, len(todo), RATER_BATCH):
        batch = todo[b:b + RATER_BATCH]
        lines = [f"{i+1}. {nu} [{mu}]  ->  {nv} [{mv}]" for i, (_k, nu, mu, nv, mv) in enumerate(batch)]
        got: dict = {}
        for _attempt in range(2):
            got = parse_ratings(call(lines), len(batch))
            if len(got) >= len(batch) * 0.9:
                break
        rated = {batch[i][0]: r for i, r in got.items()}
        with RATER_CACHE_OWN.open("a", encoding="utf-8") as fh:
            fh.write("".join(json.dumps({"k": k, "r": r}, ensure_ascii=False) + "\n" for k, r in rated.items()))
        out.update(rated)
    return out


# ================================================================================================
# scoring every step instance
# ================================================================================================
@dataclass
class Steps:
    """One row per step instance (journey, index). Values are NaN where a measure cannot score."""
    journey: np.ndarray        # int, index into the journey list
    index: np.ndarray          # int, step index within the journey
    side: np.ndarray           # int, 0 = incumbent, 1 = challenger
    end: np.ndarray            # bool, the step touches an endpoint
    in_today: np.ndarray       # bool, the connection also exists in today's map
    marked: np.ndarray         # bool
    values: dict[str, np.ndarray] = field(default_factory=dict)
    ident: list = field(default_factory=list)   # (role, sorted mbid pair), for the dedupe read
    rater_provenance: dict = field(default_factory=dict)


def score_steps(journeys: list[Journey], stores: dict, rater_lookup) -> Steps:
    """`rater_lookup(list of (store, u, v)) -> list of rating|None` is injected so tests need no CLI."""
    rows = []
    for j, jr in enumerate(journeys):
        st = stores[jr.role]
        ids = [st.id_by_mbid[m] for m in jr.path]
        for i, (u, v) in enumerate(zip(ids, ids[1:])):
            rows.append((j, i, ROLES.index(jr.role), i in (0, jr.n_steps - 1), i in jr.weak, st, u, v,
                         jr.path[i], jr.path[i + 1]))
    today = stores["incumbent"]
    s = Steps(journey=np.array([r[0] for r in rows]), index=np.array([r[1] for r in rows]),
              side=np.array([r[2] for r in rows]), end=np.array([r[3] for r in rows]),
              in_today=np.array([_in_map(today, a, b) for *_x, a, b in rows]),
              marked=np.array([r[4] for r in rows]))
    s.values["similarity"] = np.array([edge_similarity(r[5], r[6], r[7]) for r in rows])
    s.values["shared_neighbours"] = np.array([shared_neighbours(r[5], r[6], r[7]) for r in rows])
    def rater_triple(r):
        a, b = r[8], r[9]
        if a in today.id_by_mbid and b in today.id_by_mbid:   # the page's own source (`artist_source`)
            return today, today.id_by_mbid[a], today.id_by_mbid[b]
        return r[5], r[6], r[7]
    ratings = rater_lookup([rater_triple(r) for r in rows])
    s.values["rater"] = np.array([float(x) if isinstance(x, int) else np.nan for x in ratings])
    s.ident = [(r[2], tuple(sorted((r[8], r[9])))) for r in rows]
    return s


def _in_map(store, a: str, b: str) -> bool:
    if a not in store.id_by_mbid or b not in store.id_by_mbid:
        return False
    u, v = store.id_by_mbid[a], store.id_by_mbid[b]
    return bool(np.any(store.neighbours[int(store.offsets[u]):int(store.offsets[u + 1])] == v))


def make_rater_lookup(cache: dict, rate=None):
    def lookup(triples):
        do_rate = rate or rate_missing   # resolved at call time
        keys = [rater_key(st.names[u], st.names[v]) for st, u, v in triples]
        todo, seen = [], set()
        for k, (st, u, v) in zip(keys, triples):
            if k not in cache and k not in seen:
                seen.add(k)
                todo.append((k, st.names[u], rater_meta(st, u), st.names[v], rater_meta(st, v)))
        fresh = do_rate(todo) if todo else {}
        lookup.provenance = {"unique_pairs": len(set(keys)), "from_pinned_cache": len(set(keys)) - len(todo),
                             "rated_fresh": len(fresh), "unanswered": len(todo) - len(fresh)}
        merged = {**cache, **fresh}
        return [merged.get(k) for k in keys]
    lookup.provenance = {}
    return lookup


# ================================================================================================
# the statistic and its null (SNW-C, SNW-N)
# ================================================================================================
def _journey_blocks(steps: Steps):
    for j in np.unique(steps.journey):
        yield j, np.nonzero(steps.journey == j)[0]


def _strata(steps: Steps, by_position: bool = True):
    """`SNW-C`'s comparison groups: one journey's END steps, and the same journey's MIDDLE steps
    (SNR-1: position is not held constant by the journey alone). `by_position=False` gives the
    journey-only grouping, reported under `SNW-D`."""
    key = steps.journey * 2 + steps.end.astype(int) if by_position else steps.journey
    for k in np.unique(key):
        yield k, np.nonzero(key == k)[0]


def concordance_draws(steps: Steps, measure: str, marks: np.ndarray, side: int | None = None,
                      by_position: bool = True):
    """For each draw (row of `marks`, a bool matrix draws x steps), the concordance numerator and
    denominator: over every (marked, unmarked) pair of SCORABLE steps in the same journey AND the same
    position class (end / middle), 1 if the marked step's value is lower, 0.5 if equal. Returns
    (wins, pairs), each per draw. `side` restricts to one side's journeys."""
    vals = steps.values[measure]
    D = marks.shape[0]
    wins, pairs = np.zeros(D), np.zeros(D)
    for j, idx in _strata(steps, by_position):
        if side is not None and steps.side[idx[0]] != side:
            continue
        ok = idx[~np.isnan(vals[idx])]
        if len(ok) < 2:
            continue
        x = vals[ok]
        S = (x[:, None] < x[None, :]).astype(float) + 0.5 * (x[:, None] == x[None, :])
        M = marks[:, ok].astype(float)
        wins += np.einsum("da,ab,db->d", M, S, 1.0 - M)
        pairs += M.sum(1) * (len(ok) - M.sum(1))
    return wins, pairs


def ratio(wins, pairs):
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(pairs > 0, wins / np.where(pairs > 0, pairs, 1), np.nan)


def null_marks(steps: Steps, n_draws: int, seed: int) -> np.ndarray:
    """`SNW-N`: each draw places every stratum's own number of marks (a journey's end steps, or its
    middle steps) uniformly at random among that stratum's steps, independently across strata.
    Draws x steps, bool."""
    rng = np.random.default_rng(seed)
    out = np.zeros((n_draws, len(steps.marked)), dtype=bool)
    for _j, idx in _strata(steps):
        k = int(steps.marked[idx].sum())
        if k == 0:
            continue
        r = rng.random((n_draws, len(idx))).argsort(1) < k
        out[:, idx] = r
    return out


def readable_marks(steps: Steps, measure: str, side: int) -> int:
    """`SNW-U`: marked scorable steps on this side in strata that also hold an unmarked scorable step."""
    vals = steps.values[measure]
    n = 0
    for _j, idx in _strata(steps):
        if steps.side[idx[0]] != side:
            continue
        ok = idx[~np.isnan(vals[idx])]
        m = steps.marked[ok]
        if m.any() and (~m).any():
            n += int(m.sum())
    return n


def p_value(null: np.ndarray, x: float) -> float:
    null = null[~np.isnan(null)]
    return (1 + int(np.sum(null >= x))) / (1 + len(null))


def evaluate(steps: Steps, n_draws: int = N_DRAWS, seed: int = SEED) -> dict:
    """The firing rule `SNW-F` per measure, and its chance-firing rate `SNW-CH` computed on the SAME
    null draws (so the family-wise rate carries the measures' correlation)."""
    observed = steps.marked[None, :]
    draws = null_marks(steps, n_draws, seed)
    out: dict = {"n_draws": n_draws, "seed": seed, "measures": {}}
    fires_by_draw = {}
    for m in MEASURES:
        c_obs = {k: float(ratio(*concordance_draws(steps, m, observed, side))[0])
                 for k, side in (("pooled", None), ("today", 0), ("candidate", 1))}
        c_null = ratio(*concordance_draws(steps, m, draws))
        side_null = {k: ratio(*concordance_draws(steps, m, draws, side)) for k, side in (("today", 0), ("candidate", 1))}
        readable = {k: readable_marks(steps, m, side) for k, side in (("today", 0), ("candidate", 1))}
        is_readable = all(n >= MIN_MARKED_PER_SIDE for n in readable.values())
        p = p_value(c_null, c_obs["pooled"])
        f1 = c_obs["pooled"] >= C_FLOOR
        f2 = p <= MEASURE_ALPHA
        f3 = c_obs["today"] > 0.5 and c_obs["candidate"] > 0.5
        fires = is_readable and f1 and f2 and f3
        outcome = "unreadable" if not is_readable else ("fires" if fires else "does_not_fire")
        # chance: the same rule applied to each null draw
        sorted_null = np.sort(c_null[~np.isnan(c_null)])
        ge = len(sorted_null) - np.searchsorted(sorted_null, np.nan_to_num(c_null, nan=-1), side="left")
        p_draw = (1 + ge) / (1 + len(sorted_null))
        fd = ((np.nan_to_num(c_null, nan=-1) >= C_FLOOR) & (p_draw <= MEASURE_ALPHA)
              & (np.nan_to_num(side_null["today"], nan=-1) > 0.5)
              & (np.nan_to_num(side_null["candidate"], nan=-1) > 0.5)) if is_readable else np.zeros(n_draws, bool)
        fires_by_draw[m] = fd
        out["measures"][m] = {
            "C": c_obs, "p_pooled": p, "readable_marks": readable, "readable": is_readable,
            "F1_floor": f1, "F2_null": f2, "F3_both_sides_agree": f3, "outcome": outcome,
            "chance_firing_rate": float(fd.mean()),
            "null_pooled_C_quantiles": {q: float(np.nanquantile(c_null, q)) for q in (0.5, 0.95, 1 - MEASURE_ALPHA)},
        }
    out["chance_any_measure_fires"] = float(np.any(np.vstack(list(fires_by_draw.values())), 0).mean())
    return out


# ================================================================================================
# descriptive reads (SNW-D): decide nothing
# ================================================================================================
def shifted_marks(steps: Steps, by: int) -> np.ndarray:
    """Every mark moved `by` steps along its journey; a mark that would leave the journey is dropped."""
    out = np.zeros(len(steps.marked), dtype=bool)
    for _j, idx in _journey_blocks(steps):
        for pos in np.nonzero(steps.marked[idx])[0]:
            if 0 <= pos + by < len(idx):
                out[idx[pos + by]] = True
    return out


def unstratified_auc(vals: np.ndarray, marked: np.ndarray) -> float | None:
    ok = ~np.isnan(vals)
    a, b = vals[ok & marked], vals[ok & ~marked]
    if not len(a) or not len(b):
        return None
    return float(((a[:, None] < b[None, :]).sum() + 0.5 * (a[:, None] == b[None, :]).sum()) / (len(a) * len(b)))


def repeat_share(steps: Steps) -> dict:
    """Share of each side's step instances whose connection is shown more than once on that side."""
    from collections import Counter
    c = Counter(steps.ident)
    out = {}
    for i, r in enumerate(ROLES):
        idx = [k for k, key in enumerate(steps.ident) if key[0] == i]
        out[r] = (sum(c[steps.ident[k]] > 1 for k in idx) / len(idx)) if idx else None
    return out


def descriptive(steps: Steps) -> dict:
    out: dict = {"decides": "nothing (SNW-D)"}
    one = lambda mk, m, side=None: float(ratio(*concordance_draws(steps, m, mk[None, :], side))[0])  # noqa: E731
    one_jo = lambda mk, m: float(ratio(*concordance_draws(steps, m, mk[None, :], None, False))[0])  # noqa: E731
    for m in MEASURES:
        d: dict = {}
        d["shift_controls"] = {f"{by:+d}": one(shifted_marks(steps, by), m) for by in (-1, 1)}
        sub = {}
        for name, mask in (("end_steps", steps.end), ("middle_steps", ~steps.end)):
            keep = Steps(steps.journey[mask], steps.index[mask], steps.side[mask], steps.end[mask],
                         steps.in_today[mask], steps.marked[mask], {m: steps.values[m][mask]})
            sub[name] = float(ratio(*concordance_draws(keep, m, keep.marked[None, :]))[0])
        d["by_position"] = sub
        cand_today = (steps.side == 1) & steps.in_today
        keep = Steps(steps.journey[cand_today], steps.index[cand_today], steps.side[cand_today],
                     steps.end[cand_today], steps.in_today[cand_today], steps.marked[cand_today],
                     {m: steps.values[m][cand_today]})
        d["candidate_steps_also_in_todays_map"] = float(ratio(*concordance_draws(keep, m, keep.marked[None, :]))[0])
        # dedupe: one row per (side, connection); marked if marked on any instance
        seen: dict = {}
        for i, key in enumerate(steps.ident):
            v, mk = seen.get(key, (steps.values[m][i], False))
            seen[key] = (v, mk or bool(steps.marked[i]))
        d["unique_connections_auc_by_side"] = {}
        for i, r in enumerate(ROLES):
            items = [(v, x) for (sd, _c), (v, x) in seen.items() if sd == i]
            vals = np.array([v for v, _ in items], dtype=float)
            mk = np.array([x for _, x in items], dtype=bool)
            d["unique_connections_auc_by_side"][r] = unstratified_auc(vals, mk) if items else None
        d["within_journey_ignoring_position"] = one_jo(steps.marked, m)
        out[m] = d
    out["head_to_head_pooled_C_minus_similarity"] = {
        m: one(steps.marked, m) - one(steps.marked, "similarity") for m in MEASURES if m != "similarity"}
    out["counts"] = {"step_instances": int(len(steps.marked)), "marked": int(steps.marked.sum()),
                     "by_side": {r: {"steps": int((steps.side == i).sum()),
                                     "marked": int(steps.marked[steps.side == i].sum())}
                                 for i, r in enumerate(ROLES)},
                     "rater_unscorable": int(np.isnan(steps.values["rater"]).sum()),
                     "repeat_share_by_side": repeat_share(steps)}
    # SNW-M3 / §5.2: the rater is compared like-for-like with M1 and M2 only if it scored at least
    # 90 % of each side's marked steps
    share, ok = {}, True
    for i, r in enumerate(ROLES):
        mk = steps.marked & (steps.side == i)
        lost = int(np.isnan(steps.values["rater"][mk]).sum())
        share[r] = {"unscorable_marked": lost, "marked": int(mk.sum())}
        ok &= bool(mk.any()) and lost <= max(1, RATER_MAX_UNSCORABLE_MARKED * int(mk.sum()))
    out["rater_unscorable_marked_by_side"] = share
    out["SNW-V_rater_comparable_with_map_measures"] = ok
    return out


# ================================================================================================
# run state and identity (SNW-RS, SNW-IN)
# ================================================================================================
def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_lf(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def check_run_state() -> None:
    if RESULT.exists():
        raise Refused("run-once: snw_result.json exists. This test has run; no second read exists (SNW-RS).")
    for p in (PREREG, Path(__file__).resolve()):
        rel = p.relative_to(ROOT).as_posix()
        if not _git("log", "-1", "--format=%H", "--", rel):
            raise Refused(f"run state: {rel} is not committed")
        if _git("status", "--porcelain", "--", rel):
            raise Refused(f"run state: {rel} differs from its commit")


def check_inputs() -> None:
    for name, blob in INPUT_BLOBS.items():
        got = _git("hash-object", (DSL_DIR / name).relative_to(ROOT).as_posix())
        if got != blob:
            raise Refused(f"identity: {name} is blob {got}, not the pinned {blob}")
    if sha256_lf(RATER_CACHE_SRC) != RATER_CACHE_SRC_SHA_LF:
        raise Refused("identity: exploration/kit/step_cache.jsonl is not the pinned cache")


def load_store(role: str):
    from artistpath_api.graph_store import GraphStore
    path, sha = MAPS[role]
    got = sha256_file(path)
    if got != sha:
        raise Refused(f"identity: {path} is {got}, not the pinned {sha}")
    return GraphStore.load(path)


def rating_passes() -> list[dict]:
    if not RATING_PASSES.exists():
        return []
    return [json.loads(x) for x in RATING_PASSES.read_text(encoding="utf-8").splitlines() if x.strip()]


def rating_should_stop(passes: list[dict]) -> str | None:
    """`SNW-RS` step 1: stop after a pass that left nothing unanswered, after a pass that added no new
    answer, or after RATING_MAX_PASSES passes. None means another pass is owed."""
    if not passes:
        return None
    last = passes[-1]
    if last["unanswered"] == 0:
        return "nothing left unanswered"
    if last["rated_fresh"] == 0:
        return "the last pass added no new answer"
    if len(passes) >= RATING_MAX_PASSES:
        return f"{RATING_MAX_PASSES} passes made"
    return None


def no_marks(page_data: dict) -> dict:
    """An all-empty weak map, so the rating step can build journeys without reading any answer."""
    return {p["key"]: {d: {t: [] for t in TOKENS} for d in DEPTHS} for p in page_data["pairs"]}


def main(argv: list[str] | None = None) -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--rate-only", action="store_true",
                    help="SNW-RS step 1: rate every shown step the cache lacks. Reads NO answer file; "
                         "may be repeated until the rater has answered what it will")
    args = ap.parse_args(argv)
    check_run_state()
    check_inputs()
    page = json.loads((DSL_DIR / "dsl_page_data.json").read_text("utf-8"))
    mapping, map_shas = side_mapping_only(json.loads((DSL_DIR / "dsl_result.json").read_text("utf-8")))
    for r in ROLES:
        if map_shas[r] != MAPS[r][1]:
            raise Refused(f"identity: the listen recorded {r}'s map as {map_shas[r]}, not {MAPS[r][1]}")
    stores = {r: load_store(r) for r in ROLES}
    if args.rate_only:
        passes = rating_passes()
        stop = rating_should_stop(passes)
        if stop:
            raise Refused(f"rating step finished: {stop}. Commit the rater cache and the pass log, then score.")
        journeys = build_journeys(page, no_marks(page), mapping)
        lookup = make_rater_lookup(load_rater_cache(RATER_CACHE_SRC, RATER_CACHE_OWN))
        steps = score_steps(journeys, stores, lookup)
        record = {"pass": len(passes) + 1, **lookup.provenance, "repeat_share_by_side": repeat_share(steps)}
        with RATING_PASSES.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        print(f"[snw] rate-only pass {record['pass']}: {json.dumps(record)}; no answer file was read", flush=True)
        return 0
    if not rating_should_stop(rating_passes()):
        raise Refused("run state: the rating step (--rate-only) has not finished under its stopping rule")
    for f in (RATER_CACHE_OWN, RATING_PASSES):
        if f.exists():
            rel = f.relative_to(ROOT).as_posix()
            if not _git("log", "-1", "--format=%H", "--", rel) or _git("status", "--porcelain", "--", rel):
                raise Refused(f"run state: commit {f.name} after the rating step, before the read")
    weak = weak_marks_only(json.loads((DSL_DIR / "dsl_verdicts.json").read_text("utf-8")))
    journeys = build_journeys(page, weak, mapping)
    print(f"[snw] {len(journeys)} journeys; maps verified; inputs pinned", flush=True)
    # SNW-RS: the scoring run never calls the model; anything the rating step left unanswered is unscorable
    lookup = make_rater_lookup(load_rater_cache(RATER_CACHE_SRC, RATER_CACHE_OWN), rate=lambda todo: {})
    steps = score_steps(journeys, stores, lookup)
    steps.rater_provenance = lookup.provenance
    out = {"test": "SNW-", "governing": PREREG.relative_to(ROOT).as_posix(),
           "harness_commit": _git("log", "-1", "--format=%H", "--", Path(__file__).resolve().relative_to(ROOT).as_posix()),
           "inputs": {"commit": INPUT_COMMIT, "blobs": INPUT_BLOBS,
                      "maps": {r: {"path": str(MAPS[r][0]), "sha256": MAPS[r][1]} for r in ROLES},
                      "rater_cache_sha256_lf": RATER_CACHE_SRC_SHA_LF, "rater_model_alias": RATER_MODEL,
                      "rater_provenance": steps.rater_provenance},
           "result": evaluate(steps), "descriptive_only": descriptive(steps)}
    RESULT.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    for m, r in out["result"]["measures"].items():
        print(f"[snw] {m}: {r['outcome']}", flush=True)
    print("[snw] wrote snw_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
