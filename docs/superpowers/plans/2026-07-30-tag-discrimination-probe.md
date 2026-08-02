# Tag Discrimination Probe (TAS-) Implementation Plan

**Role: ⚠ FULLY DISCHARGED — every task has now run.** Tasks 1–4 executed 2026-07-30 and
their checkboxes are annotated in place; Task 7's **selection** halves ran 2026-07-30;
**Tasks 5, 6 and Task 7's ROUTING halves are SUPERSEDED** by
[`2026-07-31-tas5-routing-execution-plan.md`](2026-07-31-tas5-routing-execution-plan.md)
(which ran them as `TAS-R1`–`TAS-R4`) and **must not be executed from this document — Task 7
Step 5 contains a trap**: it instructs the executor to make the randomised-label red check
fire, which `TAS-AM3` withdrew as unachievable. **Task 8 executed 2026-08-01 (latest)** —
outputs are `findings/2026-07-30-tag-discrimination.md` and execution log §17. Governing
document is the pre-registration beside it
(`specs/2026-07-30-tag-discrimination-probe-preregistration.md`), which **wins wherever
this plan disagrees** — its §8 amendments have already overtaken this plan's Task 4 once.
Status and next action are `NEXT.md`'s, not this document's.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Measure whether genre-label agreement discriminates between the candidates an artist already has, so the choice between build-time selection and router-side pricing can be made on numbers rather than intuition.

**Architecture:** A frozen analysis directory under `builder/analysis/2026-07-30-tag-discrimination/`, following the `COH-`/`FPC-`/`CB-` precedent. Nothing in `builder/src/` or `api/src/` is modified. Nothing is rebuilt: `TAS-4` simulates selection over pipeline intermediates, `TAS-5` routes on the adopted artifact with a harness-local forked pathfinder. The fame frame and genre normalisation are **imported, never reimplemented**, so this record is comparable with `COH-` and Track B.

**Tech Stack:** Python 3.12, `uv`, stdlib only (`urllib`, `json`, `statistics`, `random`) plus `numpy` via the existing artifact reader. No new dependencies.

## Global Constraints

- **Governing document:** `docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md`. Every bar, gate and read comes from it verbatim. **A number that disagrees with the spec means the harness is wrong, not the spec.**
- **The spec is frozen once the first number exists.** Changes after that are append-only §8 amendments, never edits.
- **Every `uv` command is prefixed `UV_LINK_MODE=copy`.** Every command printing artist names adds `PYTHONIOENCODING=utf-8`. Every long-running command uses `python -u`.
- **All commands run from `builder/`** unless stated otherwise.
- **The archive is read-only.** Any harness touching `builder/scratch/graph-archive/` opens it through `ReadOnlyArchive` (`analysis/2026-07-29-algb-trial-build/grt_run.py:90`), per `GRT-A1`.
- **Adopted artifact identity is asserted on load** via the `cb_metrics.ADOPTED` / `ADOPTED_SHA` import chain. A sha mismatch is a hard stop.
- **Raw collector output is gitignored; derived summaries are committed.** Directory `.gitignore` follows `2026-07-30-coherence-tag-probe/`.
- **Identifier series is `TAS-`.** Do not introduce a bare `D1`–`D7` series — the `closeout` skill owns those in the always-loaded context layer.
- **Nothing here adopts anything.** No `BuilderConfig` or `ApiConfig` default is moved by any task.

## File Structure

| File | Responsibility |
|---|---|
| `tas_common.py` | Shared loading; the agreement device and the neutral rule (spec §1). The only file that defines what "agreement" means. |
| `tas_tags.py` | Full-graph tag frame collection over LB batched transport. Resumable. Writes `tas_tags_raw.json`. |
| `tas_signal.py` | `TAS-1` (stratified coverage), `TAS-2` (spread), `TAS-3` (collinearity diagnostic). Carries the two gate reads. |
| `tas_select.py` | `TAS-4` selection simulation over the λ grid. |
| `tas_pairs.py` | The §3 fresh pair draw with class labels and the readability floor. |
| `tas_route.py` | `TAS-5` router simulation; the forked pathfinder and the green instrument check. |
| `tas_guard.py` | `TAS-6` obscurity guard, both architectures; the red instrument check. |
| `README.md` | Directory role, scope limits, what it cannot conclude. |

**Handoff seams, chosen now rather than discovered at task 7.** This plan is 8 tasks, at the boundary where controller context becomes the binding constraint.

- **Seam A — after Task 4.** `TAS-2`'s gate has fired by then. If it kills, the work is *finished*: write findings and stop; Tasks 5–8 never run. If it survives, Task 4's output is a committed artifact, and a fresh session can pick up Task 5 cold.
- **Seam B — after Task 6.** Build-time and router-side answers are both committed; only the guard and the write-up remain.

Append to the retained execution log **per task**, not at closeout — decisions and reasoning, not narration.

---

### Task 1: The agreement device

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_common.py`
- Create: `builder/analysis/2026-07-30-tag-discrimination/README.md`
- Create: `builder/analysis/2026-07-30-tag-discrimination/.gitignore`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_common.py`

**Interfaces:**
- Consumes: `ct_common.norm_genre` (frozen normalisation); `cb_metrics.fame_frame`, `band_of`, `BANDS`, `ADOPTED`, `ADOPTED_SHA`; `fp_common.graph_mbids`, `load_partial`, `save_partial`, `get_json`.
- Produces: `agreement(a: set[str], b: set[str]) -> float | None`; `neutral_for(candidate_sets: list[set[str]]) -> float`; `resolved_agreement(u_set, v_set, neutral) -> float`; `GLOBAL_NEUTRAL_FALLBACK: float`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_common.py
from tas_common import agreement, neutral_for, resolved_agreement


def test_agreement_is_jaccard():
    assert agreement({"rock", "pop"}, {"rock"}) == 0.5
    assert agreement({"rock"}, {"rock"}) == 1.0
    assert agreement({"rock"}, {"jazz"}) == 0.0


def test_agreement_is_none_when_either_side_unlabelled():
    # Spec section 1: missing labels are NOT a claim of dissimilarity.
    assert agreement(set(), {"rock"}) is None
    assert agreement({"rock"}, set()) is None
    assert agreement(set(), set()) is None


def test_neutral_is_median_of_labelled_candidates():
    assert neutral_for([{"rock"}, {"pop"}, {"rock", "pop"}]) is not None


def test_unlabelled_pair_resolves_to_neutral_never_zero():
    # The dormant term of spec section 0: this rule is inert at lambda=0 and
    # active in every arm, so it is pinned by test, not by discipline.
    assert resolved_agreement(set(), {"rock"}, neutral=0.42) == 0.42
    assert resolved_agreement({"rock"}, {"rock"}, neutral=0.42) == 1.0


def test_neutral_falls_back_globally_below_two_labelled_candidates():
    from tas_common import GLOBAL_NEUTRAL_FALLBACK
    assert neutral_for([]) == GLOBAL_NEUTRAL_FALLBACK
    assert neutral_for([{"rock"}]) == GLOBAL_NEUTRAL_FALLBACK
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_common.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_common'`

- [ ] **Step 3: Write the implementation**

```python
# tas_common.py
"""Shared loading and the agreement device for the tag discrimination probe (TAS-).

SCOPE: descriptive. Adopts nothing, fixes no criterion, changes no weight,
default or currency. Governing document:
docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md

THE DEVICE (spec section 1)
  agreement = Jaccard over normalised genre-label sets. The label set is the
  COH-2 union genre: LB genre-whitelisted tags (a faithful transport for MB
  genres, COH-5: 99.9% identical) UNION Wikidata P136, both through the
  FROZEN ct_common.norm_genre. Same vocabulary as the COH- coverage figures,
  so TAS-1 is comparable with them rather than merely adjacent.

THE NEUTRAL RULE IS THE ONE DORMANT TERM
  Where either artist is unlabelled, agreement takes the MEDIAN agreement
  across that artist's own labelled candidates -- NEVER zero. Zero is a
  positive claim of dissimilarity; applied to missing data it would demote
  unlabelled candidates, which are disproportionately the obscure ones, and
  push DD-F1 the wrong way. Per-artist rather than a global constant because
  agreement levels vary by artist: a metal act's candidates nearly all share
  "metal", an eclectic act's share little.

  This rule is INERT at lambda=0 and ACTIVE in every arm -- the same shape as
  w_floor in the Track 2 pre-registration's section 0. It is fixed here,
  before any run, and must not move after a result exists.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

HERE = Path(__file__).parent
_COH = HERE.parent / "2026-07-30-coherence-tag-probe"
if str(_COH) not in sys.path:
    sys.path.insert(0, str(_COH))

from ct_common import (  # noqa: E402,F401
    ADOPTED,
    ADOPTED_SHA,
    BAND_ORDER,
    FPC_WIKIDATA,
    band_of,
    fame_frame,
    get_json,
    graph_mbids,
    load_partial,
    norm_genre,
    save_partial,
)

# Used only where an artist has fewer than two labelled candidates, so no
# per-artist median can be formed. 0.0 is deliberately NOT the fallback.
GLOBAL_NEUTRAL_FALLBACK = 0.15


def agreement(a: set[str], b: set[str]) -> float | None:
    """Jaccard overlap, or None when either side carries no labels.

    None means "unknown", never "dissimilar". Callers resolve it through
    resolved_agreement() so the neutral rule is applied in exactly one place.
    """
    if not a or not b:
        return None
    union = a | b
    return len(a & b) / len(union)


def neutral_for(candidate_sets: list[set[str]]) -> float:
    """Median agreement among an artist's labelled candidates.

    candidate_sets are the label sets of the candidates; the artist's own set
    is not needed because Jaccard against it is what the caller already
    computed. Callers pass the resolved pairwise values.
    """
    values = [s for s in candidate_sets if s]
    if len(values) < 2:
        return GLOBAL_NEUTRAL_FALLBACK
    return statistics.median(len(v & values[0]) / len(v | values[0]) for v in values)


def resolved_agreement(u_set: set[str], v_set: set[str], neutral: float) -> float:
    """agreement() with the neutral rule applied. The ONLY resolution path."""
    value = agreement(u_set, v_set)
    return neutral if value is None else value
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_common.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Write the directory README and .gitignore**

`README.md` states: role (ACTIVE analysis record, owns its figures), the `TAS-` series, the governing spec path, the scope limits copied from spec §6, and that raw collector output is gitignored while derived summaries are committed.

`.gitignore`:
```
tas_tags_raw.json
tas_*_raw.json
__pycache__/
```

- [ ] **Step 6: Commit**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/
git commit -m "TAS-: the agreement device and its neutral rule, pinned by test" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task 2: Full-graph tag frame

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_tags.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_tags.py`

**Interfaces:**
- Consumes: `tas_common.{graph_mbids, load_partial, save_partial, get_json, norm_genre, FPC_WIKIDATA}`; `ct_lb_metadata.parse_artists`.
- Produces: `label_sets() -> dict[str, set[str]]` (MBID → union genre set, every graph node present, empty set where unlabelled); writes `tas_tags_raw.json` and `tas_tags.json`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_tags.py
from tas_tags import merge_union_genre


def test_union_of_lb_and_wikidata_normalised():
    lb = {"genres": ["Hip-Hop"], "tags": ["hip-hop", "east coast"]}
    wd = ["Rock music"]
    assert merge_union_genre(lb, wd) == {"hip hop", "rock"}


def test_missing_sources_give_empty_set_not_error():
    assert merge_union_genre(None, []) == set()
    assert merge_union_genre(None, ["Jazz"]) == {"jazz"}


def test_widest_vocabulary_is_not_used():
    # COH-6: widest union adds ~nothing in the tail. Spec section 1 pins the
    # genre union, so a non-genre tag must NOT leak in.
    lb = {"genres": [], "tags": ["seen live"]}
    assert merge_union_genre(lb, []) == set()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_tags.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_tags'`

- [ ] **Step 3: Write the implementation**

```python
# tas_tags.py
"""TAS tag frame: union-genre labels for every node of the adopted artifact.

TRANSPORT: ListenBrainz batched metadata, 50 MBIDs per request. COH-5 measured
it 99.9% identical to MusicBrainz direct and ~29x faster -- full artifact in
~47 minutes against ~21 hours. LB is a TRANSPORT for MB's data here, not an
independent source; the shared-blind-spot hazard is about FAME signal and does
not transfer to this fidelity question.

VOCABULARY: spec section 1 -- LB genre-whitelisted tags UNION Wikidata P136,
through the frozen ct_common.norm_genre. NOT the widest tag union (COH-6
measured that as near-identical in the tail).

Resumable: re-run after any interruption; it re-fetches nothing.

Run from builder/ (~47 min, unattended):
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_tags.py
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
from typing import Any

from tas_common import (
    FPC_WIKIDATA,
    HERE,
    get_json,
    graph_mbids,
    load_partial,
    norm_genre,
    save_partial,
)

_COH = HERE.parent / "2026-07-30-coherence-tag-probe"
if str(_COH) not in sys.path:
    sys.path.insert(0, str(_COH))
from ct_lb_metadata import parse_artists  # noqa: E402

LB_URL = "https://api.listenbrainz.org/1/metadata/artist/?%s"
BATCH = 50
PAUSE = 0.3
OUT_RAW = HERE / "tas_tags_raw.json"
OUT = HERE / "tas_tags.json"


def merge_union_genre(lb_record: dict | None, wd_labels: list[str]) -> set[str]:
    """Union genre for one artist. Genre-whitelisted only, never all tags."""
    out: set[str] = set()
    if lb_record:
        out |= {norm_genre(g) for g in lb_record.get("genres", [])}
    out |= {norm_genre(label) for label in wd_labels}
    return {s for s in out if s}


def collect() -> dict[str, Any]:
    mbids = graph_mbids()
    done: dict[str, Any] = load_partial(OUT_RAW)
    pending = [m for m in mbids if m not in done]
    print(f"{len(done)} already done, {len(pending)} to fetch", flush=True)
    began = time.time()
    for start in range(0, len(pending), BATCH):
        chunk = pending[start : start + BATCH]
        qs = urllib.parse.urlencode({"artist_mbids": ",".join(chunk), "inc": "tag"})
        status, payload = get_json(LB_URL % qs, timeout=120)
        if status != 200:
            raise RuntimeError(f"LB returned {status}")
        got = parse_artists(payload)
        for m in chunk:
            done[m] = got.get(m)
        save_partial(OUT_RAW, done)
        seen = min(start + BATCH, len(pending))
        if seen % 2500 < BATCH:
            rate = seen / max(time.time() - began, 1e-9)
            print(f"  {seen}/{len(pending)} ({rate:.1f}/s)", flush=True)
        time.sleep(PAUSE)
    return done


def label_sets() -> dict[str, set[str]]:
    """MBID -> union genre set for EVERY graph node; empty where unlabelled."""
    raw = load_partial(OUT_RAW)
    wd_raw = json.loads(FPC_WIKIDATA.read_text(encoding="utf-8")) if FPC_WIKIDATA.exists() else {}
    out: dict[str, set[str]] = {}
    for mbid in graph_mbids():
        wd = wd_raw.get(mbid) or {}
        labels = wd.get("genres", []) if isinstance(wd, dict) else list(wd)
        out[mbid] = merge_union_genre(raw.get(mbid), labels)
    return out


def main() -> None:
    collect()
    sets = label_sets()
    labelled = sum(1 for s in sets.values() if s)
    OUT.write_text(
        json.dumps(
            {"nodes": len(sets), "labelled": labelled,
             "labelled_share": round(labelled / len(sets), 4)},
            indent=1,
        ),
        encoding="utf-8",
    )
    print(f"{labelled}/{len(sets)} labelled -> {OUT.name}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_tags.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Run the collector**

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_tags.py`
Expected: ~47 minutes, resumable, ends with a labelled/total line. **If it stops early, re-run the identical command — it re-fetches nothing.**

- [ ] **Step 6: Verify fidelity against the committed COH sample**

Spot-check that for MBIDs present in `2026-07-30-coherence-tag-probe/ct_lb_metadata_raw.json`, this collector's genre sets match. A mismatch means the vocabulary drifted between the two records and must be resolved before any gate is read.

- [ ] **Step 7: Commit**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/tas_tags.py builder/analysis/2026-07-30-tag-discrimination/test_tas_tags.py builder/analysis/2026-07-30-tag-discrimination/tas_tags.json
git commit -m "TAS-: full-graph union-genre tag frame over LB batched transport" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task 3: TAS-1, TAS-2, TAS-3 — the signal, and both gate reads

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_signal.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_signal.py`

**Interfaces:**
- Consumes: `tas_tags.label_sets`; `tas_common.{agreement, fame_frame, band_of, ADOPTED, ADOPTED_SHA}`; `artistpath_builder.artifact.deserialise`.
- Produces: `edge_class(pu: float, pv: float) -> str` returning `"ff"|"fo"|"oo"`; writes `tas_signal.json` carrying `tas1_coverage_by_class`, `tas2_median_iqr`, `tas3_spearman`, `tas3_identical_order_share`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_signal.py
from tas_signal import edge_class, iqr


def test_edge_class_by_fame_percentile():
    assert edge_class(0.995, 0.996) == "ff"   # both top 1%
    assert edge_class(0.995, 0.30) == "fo"    # one famous, one lower half
    assert edge_class(0.20, 0.30) == "oo"     # both lower half


def test_iqr_of_flat_signal_is_zero():
    assert iqr([0.4, 0.4, 0.4, 0.4]) == 0.0


def test_iqr_detects_spread():
    assert iqr([0.0, 0.2, 0.4, 0.6, 0.8]) > 0.10
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_signal.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_signal'`

- [ ] **Step 3: Write the implementation**

```python
# tas_signal.py
"""TAS-1, TAS-2, TAS-3 -- does the tag signal exist, and does it say anything new?

TAS-1 (gate, NARROW and EXPECTED TO PASS): >= 80% of famous-famous edges
  labelled at both ends. This deliberately does NOT inherit COH-2's coverage
  bar. That bar governed a SENSOR -- an instrument scoring every path, where
  tail blindness returns confident wrong readings. This is an ACTUATOR: where
  labels are missing it does not act, rather than acting wrongly. Silence is
  safe in a way blindness is not. The real hazard -- silence in the tail plus
  action at the top tilting the app famous -- is TAS-6's.
  FAILURE IS NOT A KILL: it means our assumption about where the rule acts is
  wrong, and the device needs redesigning.

TAS-2 (gate): kill only at effectively zero spread -- median IQR < 0.02.
  A spread below 0.10 is a reported weak-signal flag, NOT a kill: at lambda=2
  a 0.10 spread still moves the multiplier ~20%, ample to reorder candidates
  whose strengths differ by less. TAS-4 measures reordering directly and
  decides.

TAS-3 (DIAGNOSTIC, no threshold): is agreement just similarity wearing a
  different hat? If agreement rises with strength then
  strength * (1 + lambda * agreement) returns EXACTLY the order strength
  alone gave, because multiplying by something increasing in strength cannot
  reorder it. Agreement could range widely, pass TAS-2, and lambda still be
  inert at every value. This is what makes a TAS-4/TAS-5 null interpretable.

Run from builder/:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_signal.py
"""

from __future__ import annotations

import json
import statistics

from tas_common import HERE, agreement, band_of, fame_frame
from tas_tags import label_sets

OUT = HERE / "tas_signal.json"
TAS2_KILL_IQR = 0.02
TAS2_WEAK_FLAG_IQR = 0.10
TAS1_FF_GATE = 0.80

TOP_1PCT = 0.99
LOWER_HALF = 0.50


def edge_class(pu: float, pv: float) -> str:
    """ff = both top 1%; oo = both lower half; fo = everything spanning."""
    fam_u, fam_v = pu >= TOP_1PCT, pv >= TOP_1PCT
    low_u, low_v = pu < LOWER_HALF, pv < LOWER_HALF
    if fam_u and fam_v:
        return "ff"
    if low_u and low_v:
        return "oo"
    return "fo"


def iqr(values: list[float]) -> float:
    if len(values) < 4:
        return 0.0
    q = statistics.quantiles(values, n=4)
    return q[2] - q[0]


def main() -> None:
    # The API's reader, not the builder's: TAS-5 uses it too, so both read the
    # graph through one code path. artifact.deserialise returns raw CSR arrays
    # and has no per-node accessor (verified 2026-07-30).
    from artistpath_api.graph_store import GraphStore
    from tas_common import ADOPTED

    store = GraphStore.from_bytes(ADOPTED.read_bytes())
    labels = label_sets()
    frame = fame_frame()

    # --- TAS-1: coverage by edge class -----------------------------------
    counts: dict[str, list[int]] = {"ff": [0, 0], "fo": [0, 0], "oo": [0, 0]}
    for u_idx, mbid_u in enumerate(store.mbids):
        pu = frame.get(mbid_u, 0.0)
        for v_idx, _sim in store.neighbours_of(u_idx):
            mbid_v = store.mbids[v_idx]
            if mbid_v <= mbid_u:
                continue  # each undirected edge once
            cls = edge_class(pu, frame.get(mbid_v, 0.0))
            counts[cls][1] += 1
            if labels.get(mbid_u) and labels.get(mbid_v):
                counts[cls][0] += 1
    coverage = {c: (n / d if d else 0.0) for c, (n, d) in counts.items()}

    # --- TAS-2 / TAS-3: within-list spread and collinearity ---------------
    spreads: list[float] = []
    pairs_for_rho: list[tuple[float, float]] = []
    identical_order = considered = 0
    for u_idx, mbid_u in enumerate(store.mbids):
        u_set = labels.get(mbid_u, set())
        if not u_set:
            continue
        vals: list[tuple[float, float]] = []
        for v_idx, sim in store.neighbours_of(u_idx):
            a = agreement(u_set, labels.get(store.mbids[v_idx], set()))
            if a is not None:
                vals.append((float(sim), a))
        if len(vals) < 4:
            continue
        spreads.append(iqr([a for _s, a in vals]))
        pairs_for_rho.extend(vals)
        considered += 1
        by_sim = [a for _s, a in sorted(vals, key=lambda p: -p[0])]
        if by_sim == sorted(by_sim, reverse=True):
            identical_order += 1

    median_iqr = statistics.median(spreads) if spreads else 0.0
    rho = _spearman(pairs_for_rho) if len(pairs_for_rho) > 2 else 0.0

    result = {
        "tas1_coverage_by_class": coverage,
        "tas1_edge_counts": {c: d for c, (_n, d) in counts.items()},
        "tas1_gate_ff": TAS1_FF_GATE,
        "tas1_passes": coverage["ff"] >= TAS1_FF_GATE,
        "tas2_median_iqr": round(median_iqr, 4),
        "tas2_kills": median_iqr < TAS2_KILL_IQR,
        "tas2_weak_signal_flag": median_iqr < TAS2_WEAK_FLAG_IQR,
        "tas2_lists_considered": considered,
        "tas3_spearman": round(rho, 4),
        "tas3_identical_order_share": round(identical_order / considered, 4) if considered else 0.0,
    }
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    for key, value in result.items():
        print(f"{key}: {value}")


def _spearman(pairs: list[tuple[float, float]]) -> float:
    xs = _ranks([p[0] for p in pairs])
    ys = _ranks([p[1] for p in pairs])
    return statistics.correlation(xs, ys)


def _ranks(values: list[float]) -> list[float]:
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    for rank, idx in enumerate(order):
        ranks[idx] = float(rank)
    return ranks


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_signal.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: ✅ DONE — the invented accessors were replaced**

Verified 2026-07-30. `graph.neighbours_of_index` and `graph.neighbours_with_scores` **do not exist**: `artifact.deserialise` returns raw CSR arrays (`offsets`, `neighbours`, `scores`) with no such methods. The code above now uses the API's `GraphStore` instead, whose real accessors are `mbids`, `pop_raw`, and `neighbours_of(node_id) -> Iterator[tuple[int, float]]`.

That is also the better choice on its own merits: `TAS-1/2/3` and `TAS-5` now read the graph through one code path rather than two, so an inconsistency between them is impossible rather than merely unlikely.

- [ ] **Step 6: Run it and read the two gates**

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_signal.py`

**STOP AND READ THE SPEC §5 GATE READS:**
- `tas1_passes` false → **stop the outcome arms.** Report stratified coverage; the device is aimed at a population that does not exist as described. Do not proceed to Task 4.
- `tas2_kills` true → **the idea is dead in both architectures.** Report the kill, retain the tag frame, skip to Task 8. Tasks 4–7 never run.
- Otherwise → continue, carrying `tas2_weak_signal_flag` and `tas3_*` into every later read.

- [ ] **Step 7: Commit**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/tas_signal.py builder/analysis/2026-07-30-tag-discrimination/test_tas_signal.py builder/analysis/2026-07-30-tag-discrimination/tas_signal.json
git commit -m "TAS-1/2/3: coverage by edge class, within-list spread, collinearity" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task 4: TAS-4 — would selection change? *(Seam A ends here)*

> **⚠ GOVERNED BY `TAS-AM1`.** This task implements the **amended** `TAS-4`: it measures
> **edge turnover** (deletions and creations reported separately), **not** per-artist swaps;
> the median is retired in favour of the mean; and the kill bar is **turnover ≤ 1% at every
> λ**. The original "median ≤ 2 swaps of 50" bar is **withdrawn as false** — `TD-2` measured
> it as admitting ~8.4% of all connections differing. Read §8 `TAS-AM1` before writing code.

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_select.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_select.py`

**Interfaces:**
- Consumes: `tas_common.{resolved_agreement, neutral_for}`; `tas_tags.label_sets`; the frozen capture from `td_capture.py` (already built — do **not** re-run `_capture_pipeline`; `TD-1` froze it as int-id CSR arrays in an `.npz` and nothing downstream re-reads the archive).
- Produces: `simulate_top_k(strengths, label_sets, lam, k, own) -> set[str]`; `edge_turnover(base_sets, arm_sets) -> dict` returning `{"deleted": int, "created": int, "turnover_share": float}`; writes `tas_select.json` with per-λ turnover, deletions, creations, per-class breakdown and the binding-artist share.

**Reuse, do not reimplement.** `td_turnover.py` in the same directory already reconstructs `mutual_knn_cap`'s top-50 selection over the capture and computes symmetric-difference turnover, and its green check (`--verify`) asserts the reconstruction reproduces a real build edge-for-edge. Import its turnover machinery and supply the tag-driven ranking in place of its synthetic perturbation; the only new code is the ranking function.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_select.py
from tas_select import simulate_top_k


def test_lambda_zero_reproduces_strength_order_exactly():
    strengths = {"a": 0.9, "b": 0.5, "c": 0.1}
    labels = {"self": {"rock"}, "a": {"jazz"}, "b": {"rock"}, "c": {"rock"}}
    assert simulate_top_k(strengths, labels, lam=0.0, k=2, own="self") == {"a", "b"}


def test_lambda_can_promote_a_genre_match_past_a_stronger_mismatch():
    strengths = {"a": 0.50, "b": 0.49}
    labels = {"self": {"rock"}, "a": {"jazz"}, "b": {"rock"}}
    assert simulate_top_k(strengths, labels, lam=2.0, k=1, own="self") == {"b"}


def test_unlabelled_candidate_is_not_demoted_to_zero():
    # The neutral rule: an unlabelled candidate must not be treated as a
    # genre mismatch. With a strong strength lead it must survive.
    strengths = {"a": 0.90, "b": 0.40}
    labels = {"self": {"rock"}, "a": set(), "b": {"rock"}}
    assert simulate_top_k(strengths, labels, lam=1.0, k=1, own="self") == {"a"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_select.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_select'`

- [ ] **Step 3: Write the implementation**

```python
# tas_select.py
"""TAS-4: would a tag-aware ranking change which neighbours survive selection?

SIMULATED, NOT BUILT. This measures the INPUT to a rebuild, not its output:
mutual selection means one artist's reordering can delete an edge the other
still ranks, so the built consequence of a given swap rate is not derivable
from here alone. Stated in the spec and repeated because it is the easiest
thing to over-read.

KILL for the build-time architecture (AMENDED, TAS-AM1): if at every lambda
the symmetric-difference EDGE TURNOVER is <= 1%. Plain: if fewer than one
connection in a hundred is different across the whole map, no journey will
change in a way you could notice.

  The original bar -- "median artist swaps <= 2 of 50" -- is WITHDRAWN AS
  FALSE and is not implemented here. TD-2 measured that swap rate as ~8.4% of
  all connections differing (turnover ~= 2.11 x the swap rate: mutual
  selection is near-neutral on deletions, but every swap also PROMOTES a
  neighbour and per-artist swap counting never saw the creations). TD-3
  measured the median as reading 0 while 6.3% of the map moved, because the
  device is inert wherever labels are missing -- the zero-inflated case TAS-1
  exists to expect. TD-4 refuted the remaining defence: routed connections sit
  DEEPER in both endpoints' lists than average, so they are deleted at
  1.09-1.26x the population rate, never below 1.0.

  Report deletions and creations SEPARATELY, and break both out per pair
  class. Famous-famous is the most exposed class per connection and the least
  per journey (those journeys are half as long); a pooled figure hides both.

Selection binds ONLY where an artist's own list exceeds k. The share of such
artists, and of edges incident on them, is reported -- the lever cannot reach
further than that.

Run from builder/:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-tag-discrimination/tas_select.py
"""

from __future__ import annotations

import json
import statistics

from tas_common import HERE, agreement, resolved_agreement
from tas_tags import label_sets

OUT = HERE / "tas_select.json"
LAMBDAS = [0.0, 0.25, 0.5, 1.0, 2.0]
K = 50
TAS4_KILL_TURNOVER = 0.01  # TAS-AM1; owner set this materiality line 2026-07-30


def simulate_top_k(
    strengths: dict[str, float],
    labels: dict[str, set[str]],
    lam: float,
    k: int,
    own: str,
) -> set[str]:
    """Top-k under rank = strength * (1 + lam * agreement).

    Ties break on lowest MBID, matching every other ordering decision in the
    builder (design section 9). At lam=0 the multiplier is exactly 1, so this
    reproduces the production ordering bit for bit.
    """
    own_set = labels.get(own, set())
    # neutral_for, NOT a local reimplementation. tas_common exists so the
    # neutral rule has exactly ONE resolution path; an inline median with a
    # hardcoded fallback here would be a second, free to drift from it, and
    # the rule is the pre-registration's one dormant term.
    neutral = neutral_for(own_set, [labels.get(dst, set()) for dst in strengths])
    ranked = sorted(
        strengths,
        key=lambda dst: (
            -(strengths[dst] * (1.0 + lam * resolved_agreement(
                own_set, labels.get(dst, set()), neutral))),
            dst,
        ),
    )
    return set(ranked[:k])


def main() -> None:
    # TD-1 already froze the capture as int-id CSR arrays. Load it; do NOT
    # re-run _capture_pipeline and do NOT re-read the archive.
    from td_turnover import load_capture, mutual_edge_set

    capture = load_capture()
    ranking = capture.ranking          # mbid -> {dst: strength}
    labels = label_sets()
    binding = {u: s for u, s in ranking.items() if len(s) > K}

    base_sets = {u: simulate_top_k(s, labels, 0.0, K, own=u) for u, s in ranking.items()}
    base_edges = mutual_edge_set(base_sets)

    per_lambda: dict[str, dict] = {}
    for lam in (value for value in LAMBDAS if value > 0):
        arm_sets = {u: simulate_top_k(s, labels, lam, K, own=u) for u, s in ranking.items()}
        arm_edges = mutual_edge_set(arm_sets)
        deleted = len(base_edges - arm_edges)
        created = len(arm_edges - base_edges)
        per_lambda[str(lam)] = {
            "deleted": deleted,
            "created": created,
            "turnover_share": round((deleted + created) / len(base_edges), 5),
            # Mean, never median: TD-3 measured the median reading 0 while
            # 6.3% of the map moved, because the device is inert wherever
            # labels are missing.
            "mean_swaps": round(
                statistics.fmean(K - len(base_sets[u] & arm_sets[u]) for u in binding), 3
            ),
        }

    result = {
        "substrate": "ALG-E-mutual_knn-k50 (TAS-AM1); NOT the adopted artifact",
        "baseline_edges": len(base_edges),
        "binding_artists": len(binding),
        "binding_share": round(len(binding) / len(ranking), 4),
        "per_lambda": per_lambda,
        "kill_threshold_turnover": TAS4_KILL_TURNOVER,
        "tas4_kills": all(
            cell["turnover_share"] <= TAS4_KILL_TURNOVER for cell in per_lambda.values()
        ),
    }
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_select.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: ✅ DONE — the mismatch was larger than predicted, and Steps 1/3 above are superseded by the committed code**

Verified 2026-07-30. **`load_capture` and `mutual_edge_set` do not exist**, and the shortfall
is not the predicted id-mapping step: `td_turnover.py` expresses a selection as a **boolean
mask over one flattened candidate array** and computes turnover by numpy set operations on
packed `u * n + v` edge keys, so `simulate_top_k(...) -> set[str]` over MBID-keyed dicts is a
different **data model**, not a different spelling. The real interface is `Capture(path)`
(int-id CSR: `offsets` / `cand` / `rank` / `mbids`), `mutual_undirected(cap, mask)` and
`swaps_per_node(cap, base, new)`.

The committed `tas_select.py` and `test_tas_select.py` are the record; Steps 1 and 3 above
are kept unedited as the draft they were. All three of the plan's pinned properties survive
in the committed tests, rewritten against the real interface.

The green check **passed**: `exact_match: true` against `ALG-E-mutual_knn-k50.bin`. Note the
real invocation needs `--capture <path.npz>` (required) and, to protect the committed `TD-`
record, `--out` pointed at scratch — `td_turnover.py` runs its full 37-arm sweep after the
verify block and would otherwise overwrite `td_turnover.json`:

Run: `UV_LINK_MODE=copy uv run python -u analysis/2026-07-30-tag-discrimination/td_turnover.py --capture <path.npz> --verify --out <scratch>/td_turnover_reproduced.json`

- [ ] **Step 6: Run it**

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_select.py`
Expected: per-λ turnover with deletions and creations separated, the binding share, and `tas4_kills` against the 1% bar.

- [ ] **Step 7: Commit — SEAM A**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/tas_select.py builder/analysis/2026-07-30-tag-discrimination/test_tas_select.py builder/analysis/2026-07-30-tag-discrimination/tas_select.json
git commit -m "TAS-4: selection simulation over the lambda grid" -- builder/analysis/2026-07-30-tag-discrimination/
```

**Seam A. Append per-task reasoning to the execution log, push the branch, and consider retiring the session here.** Task 4's output is a committed artifact; Task 5 can start cold.

---

### Task 5: The pair draw

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_pairs.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_pairs.py`

**Interfaces:**
- Consumes: `tas_common.{fame_frame, graph_mbids}`; `tas_signal.edge_class`.
- Produces: `draw_pairs() -> list[tuple[str, str, str]]` — `(mbid_a, mbid_b, class_label)`, classes `ff`/`fo`/`oo`; writes `tas_pairs.json`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_pairs.py
from tas_pairs import draw_pairs, MIN_READABLE_PER_CLASS


def test_pairs_carry_their_class_label():
    # CRS-A1: Track B's draw discarded class labels and three pre-registered
    # quantities became uncomputable. Every pair carries its class end to end.
    pairs = draw_pairs()
    assert all(len(p) == 3 for p in pairs)
    assert {p[2] for p in pairs} <= {"ff", "fo", "oo"}


def test_draw_is_deterministic_under_the_committed_seed():
    assert draw_pairs() == draw_pairs()


def test_every_class_meets_the_readability_floor_or_is_reported_unreadable():
    pairs = draw_pairs()
    for cls in ("ff", "fo", "oo"):
        n = sum(1 for p in pairs if p[2] == cls)
        assert n >= MIN_READABLE_PER_CLASS or n == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_pairs.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_pairs'`

- [ ] **Step 3: Write the implementation**

```python
# tas_pairs.py
"""The TAS pair set -- fresh draw, this probe's own (spec section 3).

OBSCURE-ENDPOINT CLASSES ARE INCLUDED BY THE OWNER'S EXPLICIT TRIGGER,
2026-07-30. NEXT.md parks the `x lower` redraw as his call; this pulls it,
for this probe only. Track B's committed draw is untouched and its classes
stay the record for its own reads.

CLASSES CARRIED END TO END (CRS-A1): Track B's draw_pairs returned a sorted
set and discarded each pair's class, making three pre-registered quantities
uncomputable until it was fixed mid-flight. Every pair here carries its label.

NO ATTRITION GUARD, AND NONE IS NEEDED. Track B restricted its draw to pairs
routable in every compared cell because its cells were DIFFERENT GRAPHS.
Nothing here is rebuilt: TAS-4 compares sets without routing and TAS-5 routes
one graph under different weights. Only the largest connected component is
retained, so a path exists between any two artists the draw can offer and no
cell can lose a pair.
"""

from __future__ import annotations

import json
import random

from tas_common import HERE, fame_frame, graph_mbids
from tas_signal import edge_class

OUT = HERE / "tas_pairs.json"
SEED = "20260730-tas"
PER_CLASS = 40
MIN_READABLE_PER_CLASS = 20


def draw_pairs() -> list[tuple[str, str, str]]:
    frame = fame_frame()
    mbids = [m for m in graph_mbids() if m in frame]
    rng = random.Random(SEED)
    buckets: dict[str, list[tuple[str, str, str]]] = {"ff": [], "fo": [], "oo": []}
    attempts = 0
    while any(len(v) < PER_CLASS for v in buckets.values()) and attempts < 2_000_000:
        attempts += 1
        a, b = rng.sample(mbids, 2)
        cls = edge_class(frame[a], frame[b])
        if len(buckets[cls]) < PER_CLASS:
            lo, hi = sorted((a, b))
            buckets[cls].append((lo, hi, cls))
    out: list[tuple[str, str, str]] = []
    for cls in ("ff", "fo", "oo"):
        pairs = sorted(set(buckets[cls]))
        out.extend(pairs if len(pairs) >= MIN_READABLE_PER_CLASS else [])
    return out


def main() -> None:
    pairs = draw_pairs()
    counts = {c: sum(1 for p in pairs if p[2] == c) for c in ("ff", "fo", "oo")}
    OUT.write_text(
        json.dumps({"seed": SEED, "counts": counts,
                    "unreadable": [c for c, n in counts.items() if n == 0],
                    "pairs": pairs}, indent=1),
        encoding="utf-8",
    )
    print(counts)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_pairs.py -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Run it and record any unreadable class**

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_pairs.py`
Expected: counts per class. Any class reported unreadable is named in the findings — never pooled into another.

- [ ] **Step 6: Commit**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/tas_pairs.py builder/analysis/2026-07-30-tag-discrimination/test_tas_pairs.py builder/analysis/2026-07-30-tag-discrimination/tas_pairs.json
git commit -m "TAS: fresh pair draw with class labels, obscure endpoints included" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task 6: TAS-5 — would the journeys change? *(Seam B ends here)*

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_route.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_route.py`

**Interfaces:**
- Consumes: `artistpath_api.pathfinding.find_path`, `artistpath_api.config.ApiConfig`, `artistpath_api.graph_store.GraphStore`; `tas_pairs.draw_pairs`; `tas_tags.label_sets`.
- Produces: `find_path_coh(store, source, target, cfg, labels, w_coh) -> list[int] | None`; writes `tas_route.json` with per-class change rates per weight.

- [ ] **Step 1: Write the failing test — this IS the green instrument check**

```python
# test_tas_route.py
from tas_route import find_path_coh


def test_zero_weight_reproduces_production_paths_exactly(store, cfg, labels):
    from artistpath_api.pathfinding import find_path
    for source, target in [(0, 25), (3, 91), (11, 40)]:
        assert find_path_coh(store, source, target, cfg, labels, 0.0) == \
            find_path(store, source, target, [], cfg)


def test_nonzero_weight_can_change_a_path(store, cfg, labels):
    changed = any(
        find_path_coh(store, s, t, cfg, labels, 5.0)
        != find_path_coh(store, s, t, cfg, labels, 0.0)
        for s, t in [(0, 25), (3, 91), (11, 40)]
    )
    assert changed, "a large coherence weight changed nothing -- harness is inert"
```

Fixtures `store`, `cfg`, `labels` come from `api/tests/`' existing 500-node fixture pattern; follow `api/tests/conftest.py`.

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_route.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_route'`

- [ ] **Step 3: Write the implementation**

```python
# tas_route.py
"""TAS-5: would a coherence term change the journeys the app builds?

THE PATHFINDER IS FORKED, NOT PATCHED. find_path_coh below is a copy of
api/src/artistpath_api/pathfinding.py find_path with ONE added term:

    + w_coh * (1 - agreement(u, v))

w_coh DOES NOT EXIST in ApiConfig and this document does not propose adding
one. It is harness-local. Shipping it would be a config default change, which
is an adoption, which this probe does not license.

KILL for the router-side architecture: only if journeys are unchanged in EVERY
class at every weight. A pooled bar is explicitly rejected -- a small overall
change concentrated in famous-to-famous is a signal worth chasing, and
famous-to-famous is where DD-F1 lives.

UNCHANGED means the identical artist sequence, in order, endpoints included.
Path COST is not compared: it necessarily moves whenever w_coh > 0, and
reading that as an effect would be an artefact of the instrument.

STANDING CAUTION: three consecutive attempts to change router behaviour by
changing prices returned nulls (Track 2's repricing family, Track 3b's
thresholded toll, Track B's R2 quota edges declined at production weights). A
TAS-5 null is WEAK evidence about tags specifically and must not be reported
as "tags do not work"; TAS-3 and TAS-4 are what distinguish the two.
"""

from __future__ import annotations

import heapq
import json

from tas_common import HERE, resolved_agreement
from tas_pairs import draw_pairs
from tas_tags import label_sets

OUT = HERE / "tas_route.json"
WEIGHT_MULTIPLES = [0.0, 0.25, 0.5, 1.0, 2.0]


def find_path_coh(store, source, target, cfg, labels, w_coh):
    """find_path with one added per-edge coherence term. See module docstring."""
    if source == target:
        return [source]
    base_floor_raw = min(float(store.pop_raw[source]), float(store.pop_raw[target]))
    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        pop_raw_u = float(store.pop_raw[u])
        u_set = labels.get(store.mbids[u], set())
        # Per-artist neutral, via the ONE resolution path -- not a hardcoded
        # constant. An earlier draft inlined 0.15 here, which would have made
        # the routing arm use a different neutral rule from the selection arm
        # while both documents claimed they shared one.
        neighbours = list(store.neighbours_of(u))
        neutral = neutral_for(u_set, [labels.get(store.mbids[v], set()) for v, _ in neighbours])
        for v, sim in neighbours:
            pop_raw_v = float(store.pop_raw[v])
            a = resolved_agreement(u_set, labels.get(store.mbids[v], set()), neutral)
            cost = (
                cfg.w_sim * (1.0 - float(sim))
                + cfg.w_jump * abs(pop_raw_u - pop_raw_v)
                + cfg.w_floor * max(0.0, base_floor_raw - pop_raw_v)
                + cfg.w_degree_hub * float(store.degree_hub_penalty[v])
                + cfg.w_hop
                + w_coh * (1.0 - a)
            )
            nd = d + cost
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1]


def main() -> None:
    from artistpath_api.config import ApiConfig
    from artistpath_api.graph_store import GraphStore
    from tas_common import ADOPTED

    cfg = ApiConfig()
    store = GraphStore.from_bytes(ADOPTED.read_bytes())
    labels = label_sets()
    index = {m: i for i, m in enumerate(store.mbids)}
    pairs = draw_pairs()

    per_weight: dict[str, dict[str, dict]] = {}
    for mult in WEIGHT_MULTIPLES:
        w_coh = mult * cfg.w_sim
        by_class: dict[str, list[bool]] = {"ff": [], "fo": [], "oo": []}
        for a, b, cls in pairs:
            if a not in index or b not in index:
                continue
            base = find_path_coh(store, index[a], index[b], cfg, labels, 0.0)
            arm = find_path_coh(store, index[a], index[b], cfg, labels, w_coh)
            by_class[cls].append(base != arm)
        per_weight[str(mult)] = {
            cls: {"n": len(v), "changed": sum(v),
                  "changed_share": round(sum(v) / len(v), 4) if v else None}
            for cls, v in by_class.items()
        }

    kills = all(
        cell["changed"] == 0
        for mult, classes in per_weight.items() if mult != "0.0"
        for cell in classes.values()
    )
    result = {"per_weight": per_weight, "tas5_kills": kills}
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_route.py -v`
Expected: PASS (2 tests). **The first test failing means the fork drifted from production and nothing this file produces counts.**

- [ ] **Step 5: Reconcile the fork against production line by line**

Diff `find_path_coh` against `api/src/artistpath_api/pathfinding.py:76-149`. The fork above omits `excludes`, `avoidance_map`, `effective_floor_raw` and `forbidden_edge` because no arm uses a bypass. **Confirm that omission is still true; if any read needs bypass depth, port those branches rather than approximating them.**

- [ ] **Step 6: Run it**

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_route.py`
Expected: per-class change rates at each weight, and `tas5_kills`.

- [ ] **Step 7: Commit — SEAM B**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/tas_route.py builder/analysis/2026-07-30-tag-discrimination/test_tas_route.py builder/analysis/2026-07-30-tag-discrimination/tas_route.json
git commit -m "TAS-5: router simulation with a harness-local coherence term" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task 7: TAS-6 guard, and the red instrument check

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_guard.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_guard.py`

**Interfaces:**
- Consumes: `tas_select.simulate_top_k`; `tas_route.find_path_coh`; `tas_signal.edge_class`; `tas_common.fame_frame`.
- Produces: writes `tas_guard.json` with `famous_to_obscure_delta` per λ, `sub_decile_presence` per weight, and `red_check`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_guard.py
from tas_guard import randomised_labels, is_adverse


def test_randomised_labels_preserve_the_labelled_share():
    original = {"a": {"rock"}, "b": set(), "c": {"jazz", "pop"}}
    shuffled = randomised_labels(original, seed=1)
    assert sum(1 for v in shuffled.values() if v) == 2
    assert set(shuffled) == set(original)


def test_adverse_at_ten_percent_reduction():
    assert is_adverse(baseline=100, arm=90) is True
    assert is_adverse(baseline=100, arm=91) is False
    assert is_adverse(baseline=0, arm=0) is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_guard.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_guard'`

- [ ] **Step 3: Write the implementation**

```python
# tas_guard.py
"""TAS-6 (obscurity guard) and the RED instrument check.

TAS-6 IS REPORTED, NEVER A SUCCESS SIGNAL. Adverse at a >= 10% reduction in
famous->obscure supply. An adverse TAS-6 BARS any recommendation to adopt,
whatever TAS-4/TAS-5 show, until a router-side answer exists. It is the guard
on the neutral rule: unlabelled artists are disproportionately obscure, so a
careless treatment of missing labels punishes exactly the artists the product
exists to surface.

THE RED CHECK. A measurement that has only ever come back green is not
evidence yet. Fed a randomised tag frame -- same labelled share, labels
shuffled between artists -- the harness MUST report large swap and path-change
rates. If it does not, every green result above is uninterpretable.

Both measurements use the ADOPTED fame frame as a FIXED reference population,
never each arm's own. A variant's own frame would renormalise fame underneath
the comparison (the _log_scaled hazard, graph.py:148).
"""

from __future__ import annotations

import json
import random

from tas_common import HERE, fame_frame
from tas_signal import edge_class

OUT = HERE / "tas_guard.json"
ADVERSE_FRACTION = 0.10


def randomised_labels(labels: dict[str, set[str]], seed: int) -> dict[str, set[str]]:
    """Shuffle label sets between artists, preserving the labelled share."""
    rng = random.Random(seed)
    keys = sorted(labels)
    values = [labels[k] for k in keys]
    rng.shuffle(values)
    return dict(zip(keys, values))


def is_adverse(baseline: int, arm: int) -> bool:
    if baseline == 0:
        return False
    return (baseline - arm) / baseline >= ADVERSE_FRACTION
```

The `main()` reruns `tas_select.simulate_top_k` counting surviving `fo`-class pairs per λ, reruns `tas_route.find_path_coh` counting sub-decile interiors per weight, then repeats both against `randomised_labels` and asserts the red check fired. Write it following the shape of Tasks 4 and 6; every number lands in `tas_guard.json`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_guard.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Run it and check the red check actually fired**

Run: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_guard.py`
Expected: `red_check` reports large swap and path-change rates under randomised labels. **If it does not, stop — every green result in Tasks 3–6 is uninterpretable and the harness must be fixed before anything is written up.**

- [ ] **Step 6: Commit**

```bash
git add builder/analysis/2026-07-30-tag-discrimination/tas_guard.py builder/analysis/2026-07-30-tag-discrimination/test_tas_guard.py builder/analysis/2026-07-30-tag-discrimination/tas_guard.json
git commit -m "TAS-6: obscurity guard, plus the randomised-label red check" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task 8: Findings, and the owner-facing read — ✅ EXECUTED 2026-08-01 (latest)

> **Two deviations from this task as written, both recorded rather than silent.**
>
> 1. **The execution log was not created — it already existed** and has been appended to
>    (`§17`) instead. This task was authored assuming Task 8 followed Tasks 1–7 in one
>    session; in fact five sessions wrote §1–§16 along the way. Only the findings document
>    was new, so `docs/README.md` gained **one** row, not two.
> 2. **Step 2 located two §5 bullets, not one.** "Both survive" fires on the kill bars and
>    "`TAS-6` adverse" fires on the guard, simultaneously and without conflict. The
>    conclusion drawn from their conjunction — that the architecture question is closed
>    rather than the live owner's choice the first bullet anticipates — is **labelled as
>    inference on the page**, per this step's "do not invent a read".

**Files:**
- Create: `docs/superpowers/findings/2026-07-30-tag-discrimination.md` ✅
- ~~Create: `docs/superpowers/2026-07-30-tag-discrimination-execution-log.md`~~ — already existed; appended `§17` ✅
- Modify: `docs/README.md` (classify both new documents) ✅ *(one row — see deviation 1)*

- [x] **Step 1: Write the findings document**

One section per `TAS-1`…`TAS-6`, each opening with its **plain-language sentence quoted verbatim from the spec** — fixed before results existed, so drift is as visible as a moved number. Include a Weakest link section naming what you would defend cheaply and what you would abandon on one contrary measurement, and a "What this cannot conclude" section copied from spec §6.

- [x] **Step 2: Apply the spec §5 read that matches the outcome**

Do not invent a read. Find the bullet in §5 that matches what happened and follow it. If the grid did not complete, name every unrun arm — "not run" must never be readable as "returned nothing".

- [x] **Step 3: Write the owner-facing summary into the execution log**

Four parts, in order: **Measured** (numbers, no adjectives), **What I infer** (plain language — a person who does not know what Jaccard means must be able to disagree with it), **Weakest link**, **Options and their consequences**. Then run the three checks: scan for bare letter-number tokens and give each its sentence; substitute sentences for identifiers and re-read for drift; and ask whether the owner could actually disagree with each claim.

**The summary must name whatever cuts against it.** If `TAS-3` says the signal is redundant with similarity, that belongs in the summary, not a footnote.

- [x] **Step 4: Classify both documents in `docs/README.md`**

Add rows with roles. A findings document that the map does not classify is the defect the doc-auditor has caught three times.

- [x] **Step 5: Commit and open the PR**

> **Branch deviation:** the command below names `tag-discrimination-probe`, which was merged
> (PR #55) long before Task 8 ran. Executed on a fresh branch off `main`,
> **`tas-task8-findings`**, per `CLAUDE.md`'s branch-per-piece-of-work rule.

```bash
git add docs/
git commit -m "TAS-: findings, execution log, and doc map rows" -- docs/
git push -u origin tag-discrimination-probe
```

PR body carries: link to the execution log, every gate outcome **including failures**, deferred findings with success conditions, and what is closed and must not be re-litigated.

- [ ] **Step 6: Run `closeout`**

---

## Self-Review

**Spec coverage.** §0 dormant term → Task 1 (`test_unlabelled_pair_resolves_to_neutral_never_zero`). §1 device and vocabulary → Tasks 1–2. §2 `TAS-1`/`2`/`3` → Task 3; `TAS-4` → Task 4; `TAS-5` → Task 6; `TAS-6` → Task 7. §3 pair set → Task 5. §4 green check → Task 6 Step 1; red check → Task 7. §5 reads → Task 3 Step 6, Task 8 Step 2. §6 limits → Task 8 Step 1. §7 parked items → no task, correctly: they are out of scope by design.

**Known gaps, stated rather than hidden.** Task 7's `main()` is described in prose rather than written out — it is mechanical repetition of Tasks 4 and 6 against a shuffled frame, and writing it out in full would be the "Similar to Task N" anti-pattern in reverse. Its tests and helpers are concrete. Tasks 3, 4 and 6 each carry an explicit **verify-against-source** step because three call sites (`neighbours_of_index`, `_capture_pipeline`, `GraphStore.from_bytes`) were written from the CSR/pipeline shape rather than read off the source; they must be grepped before running, and that is a step in the plan rather than an assumption in it.

**Type consistency.** `label_sets() -> dict[str, set[str]]` is consumed identically in Tasks 3, 4, 6, 7. `simulate_top_k(strengths, labels, lam, k, own)` keeps its signature between Task 4's tests and Task 7's reuse. `edge_class` returns the same three literals everywhere, and `tas_pairs` uses those literals as its class labels.
