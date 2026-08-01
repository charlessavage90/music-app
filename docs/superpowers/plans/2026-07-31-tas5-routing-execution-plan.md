# `TAS-5` routing-side execution plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Role: ACTIVE.** Supersedes **Tasks 5, 6 and 7's routing halves** of
[`2026-07-30-tag-discrimination-probe.md`](2026-07-30-tag-discrimination-probe.md), which
remains authoritative for Tasks 1–4 and for Task 7's **selection** halves (all executed).
Where the two disagree about the routing side, this document governs. The governing
*experimental* document is and remains the pre-registration
[`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](../specs/2026-07-30-tag-discrimination-probe-preregistration.md),
which **wins wherever this plan disagrees with it.**

**Goal:** Run `TAS-5` (*would a genre term change the journeys the app builds?*) and
`TAS-6`'s routing half (*does it cost obscurity?*) on the adopted artifact, with an
instrument check that can actually fire.

**Architecture:** A harness-local fork of the production pathfinder with one added per-edge
term, run over a fresh pre-registered pair draw at five weights. No rebuild, no config
change, no API change, no blind listen.

**Tech Stack:** Python 3.12, numpy, `uv`; the committed `TAS-` harness under
`builder/analysis/2026-07-30-tag-discrimination/`; the API's `GraphStore`, `ApiConfig` and
`find_path` imported read-only.

**Task identifiers are `TAS-R1`…`TAS-R4`** — a new series, namespaced and verified unused
across the repo. They are **not** criteria (`TAS-1`…`TAS-6`) and **not** amendments
(`TAS-AM1`…`TAS-AM5`). Nothing committed is renamed.

---

## Why this plan exists rather than executing the old Tasks 5–7

The inherited tasks were written before Tasks 1–4 ran. Five things in them no longer
describe reality, and one is a trap rather than merely stale. Verified against the code on
2026-07-31:

| # | Inherited text | Reality |
|---|---|---|
| 1 | Task 7 Step 5: *"`red_check` reports large swap and path-change rates under randomised labels. If it does not, **stop**"* | **This is the check `TAS-AM3` withdrew as unachievable.** Following it would mean "fixing" the harness until it fires, which the handoff explicitly forbids. **The trap.** |
| 2 | Task 7 **Create:** `tas_guard.py`; consumes `tas_select.simulate_top_k` | `tas_guard.py` **exists** (Task 7's selection halves ran). `simulate_top_k` **never existed** — the real interface is `Capture` + boolean mask; see `test_tas_select.py`'s docstring. |
| 3 | Task 6 Step 3 calls `neutral_for(...)` | **Not imported** in the draft's import line. `NameError` on first run. |
| 4 | Task 6 `main()` recomputes the `w_coh = 0` baseline inside the weight loop | 5× redundant routing. `td_pathedges.json` records 900 pairs costing 609.5 s, so this is real time. |
| 5 | Task 6's green check uses three hard-coded fixture pairs | Too weak to serve as `TAS-AM5`'s equivalence proof — see below. |

Everything else in the inherited Tasks 5–6 was checked and **does** resolve:
`tas_common.{HERE, ADOPTED, ADOPTED_SHA, fame_frame, graph_mbids, neutral_for,
resolved_agreement}` (re-exported from `cb_metrics`), `tas_signal.edge_class`,
`tas_tags.label_sets`, `GraphStore.{from_bytes, mbids, pop_raw, degree_hub_penalty,
neighbours_of}`, and every `ApiConfig` weight named in the cost function.

---

## The gap that must be closed before any arm runs

**`TAS-AM3`'s scope clause does not transfer to the routing side, and the reason is
`TAS-AM2`.**

`TAS-AM3` says the routing-side red check is "the same pair, with `find_path_coh` in place
of the ranking path and the `w_coh` grid in place of λ". But `TAS-AM3a` passes on two
conditions — bit-identity against `td_turnover.mask_multiplicative`, and reproduction of the
committed `TD-2` figures — and **both of those live on the pre-cap `ALG-E` capture.**
`TAS-AM2` puts `TAS-5` on the **adopted artifact** and states the standing constraint that
**no read may compare a capture-side figure against an artifact-side one.**

So there is no committed artifact-side reference for the routing check to be identical to,
and the one artifact-adjacent calibration that exists — `td_pathedges.json` — is itself
measured on `ALG-E-mutual_knn-k50.bin`. Borrowing it would cross the exact line `TAS-AM2`
draws.

**This must be resolved by an amendment written before `TAS-5` runs, not by a session
picking a threshold at execution time.** `TAS-AM3` and `TAS-AM4` both had to disclose that
they were written after results existed; `TAS-AM5` does not have to, and that is worth more
than the hour it costs. **Task `TAS-R1` writes and commits it. No arm runs before that
commit lands** — the git timestamp is the evidence, and it is the part that cannot be
reconstructed afterwards.

---

## Global Constraints

Copied verbatim from the pre-registration. Every task's requirements implicitly include this
section.

- **Substrate: `TAS-5` and `TAS-6`'s routing half run on the ADOPTED artifact** (`TAS-AM2`).
  Assert `ADOPTED_SHA` on load. Never the capture.
- **No read may compare a capture-side figure against an artifact-side one** (`TAS-AM2`).
  The two differ by 36 artists and 193 edges.
- **Grid: `w_coh ∈ {0, ¼, ½, 1, 2} × w_sim`.** `w_sim` is `ApiConfig.w_sim`, currently 3.0 —
  read it, never hard-code it.
- **`w_coh` does not exist in `ApiConfig` and this plan does not add it.** It is
  harness-local. Shipping it would be a config default change, which is an adoption, which
  this probe does not license.
- **Kill for the router-side architecture: only if journeys are unchanged in EVERY class at
  every weight.** A pooled bar is explicitly rejected.
- **"Unchanged" means the identical artist sequence, in order, endpoints included.** A path
  of the same length through different artists is a change; so is the same set in a
  different order. **Path cost is NOT part of the comparison** — it necessarily moves
  whenever `w_coh > 0`, and reading that as an effect would be an artefact of the instrument.
- **`TAS-6` is reported, never a success signal. Adverse at a ≥ 10% reduction.** The
  selection half is already adverse and **that bars an adoption recommendation regardless of
  anything this plan produces.**
- **No outcome read is licensed on a partial grid** (§5). A half-run `TAS-5` is worth zero,
  not half. Any arm left unrun is listed by name in the findings.
- **No bar may move now that results exist.** `TAS-AM5` fixes its reads before it runs.
- **A `TAS-5` null is WEAK evidence about tags specifically** and must not be reported as
  "tags do not work" — three consecutive router repricings have already returned nulls.
- **Environment:** `UV_LINK_MODE=copy` on every `uv` command; `PYTHONIOENCODING=utf-8` on
  anything printing artist names; `python -u` on every long run. **Never pipe a long
  unattended run through `tail`** — it buffers progress away and a slow run becomes
  indistinguishable from a hung one (execution log §13.5).
- **`np.load` on an `.npz` is LAZY.** Materialise every array once, outside any loop.
- All commits use a pathspec: `git commit -- <paths>`. Never `-A`, never `--amend`.

---

## File Structure

| File | Responsibility |
|---|---|
| `specs/…-preregistration.md` §8 | **Modify** — append `TAS-AM5`. The only spec change. |
| `analysis/…/tas_pairs.py` | **Create** — the pre-registered pair draw, classes carried end to end. |
| `analysis/…/tas_route.py` | **Create** — `find_path_coh`, the equivalence check, and `TAS-5`. |
| `analysis/…/tas_route_guard.py` | **Create** — `TAS-AM5`'s liveness and null control, plus `TAS-6`'s routing half. **A new file, not an edit to `tas_guard.py`**, which is committed evidence for the selection side and must not be disturbed. |
| `analysis/…/test_tas_pairs.py`, `test_tas_route.py`, `test_tas_route_guard.py` | **Create** — unit tests. |

`analysis/…` is `builder/analysis/2026-07-30-tag-discrimination/`.

---

### Task `TAS-R1`: Write and commit `TAS-AM5` — before anything runs

**Files:**
- Modify: `docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md` (append to §8)

**Interfaces:**
- Consumes: nothing.
- Produces: the fixed reads every later task is measured against.

- [ ] **Step 1: Append the amendment**

Append verbatim to §8, after `TAS-AM4`:

```markdown
### `TAS-AM5` — the routing-side instrument check, constructed rather than inherited

**⚠ WRITTEN BEFORE ANY ROUTING RESULT EXISTS**, unlike `TAS-AM3` and `TAS-AM4`. What
existed when this was written: all of `TAS-1`…`TAS-4`, `TAS-6`'s selection half, and
`TAS-AM3a`/`b`. **No `TAS-5` arm had been run and no routing figure of any kind existed.**
This is stated so a later reader can price it differently from the two amendments above.

**Why `TAS-AM3`'s scope clause cannot simply be applied.** `TAS-AM3` says the routing red
check is `TAS-AM3a`/`b` "with `find_path_coh` in place of the ranking path". But
`TAS-AM3a` passes on bit-identity against `td_turnover.mask_multiplicative` and on
reproducing the committed `TD-2` figures — **both on the pre-cap `ALG-E` capture.**
`TAS-AM2` puts `TAS-5` on the **adopted artifact** and forbids comparing a capture-side
figure with an artifact-side one. There is therefore no committed artifact-side reference
to be identical to, and `td_pathedges.json` is not one: it is measured on
`ALG-E-mutual_knn-k50.bin`.

`TAS-AM3a`'s *property* is what transfers: **prove the device registers a large change,
against a fixed external reference rather than a judgement call, and prove the code path
IS the verified one rather than resembling it.** Both clauses below preserve that property
on the correct substrate. Neither introduces a threshold.

#### `TAS-AM5a` — equivalence *(replaces `TAS-AM3a`'s clause (i) for the routing side)*

*Plain: prove the copy of the router used for this experiment is the real router, by
checking it returns the app's own answer on every journey we test.*

At `w_coh = 0`, `find_path_coh` must return a path **identical to production
`find_path(store, source, target, [], cfg)`** — same node sequence, in order — for
**every pair in the §3 draw**, on the adopted artifact. Not a sample and not a fixture:
the full draw, the real artifact.

**Any single mismatch voids every `TAS-5` figure.** This is what licenses the fork's
omission of `excludes`, `avoidance_map`, `effective_floor_raw` and `forbidden_edge`: the
omission is *proved* equivalent rather than argued to be.

#### `TAS-AM5b` — liveness *(replaces `TAS-AM3a`'s clause (ii) for the routing side)*

*Plain: prove the genre term can move a journey, by turning it up until it is the only
thing that matters and checking the journey goes exactly where it then should.*

The reference is computed independently rather than borrowed, which is what removes the
judgement call. Run plain Dijkstra over the adopted artifact with the per-edge cost
`(1 − agreement(u, v))` **alone** — every other term dropped — and record, per pair, the
optimal total. Then run `find_path_coh` at a **dominating** weight
`w_coh = 10^6 × w_sim`.

**Passes only if, for every pair in the draw, the total `(1 − agreement)` along
`find_path_coh`'s returned path equals the independently computed optimum to within
1e-9.**

**Totals are compared, not node sequences**, and deliberately: at a dominating weight the
remaining terms act purely as a tie-break among equally coherent paths, so requiring an
identical sequence would fail on ties that are not defects. The total is exact, tie-safe,
and threshold-free.

**A failure here means the term is not reaching the cost function at all** — the inert-harness
failure `TAS-AM3a` was built to catch, in the form it takes on this side.

#### `TAS-AM5c` — the null control *(the routing analogue of `TAS-AM3b`; NOT a gate)*

*Plain: check any change we see comes from genres sitting where they actually sit, rather
than from any label-shaped nudge at all.*

Permute label sets **among labelled artists only**, holding fixed exactly which artists
carry labels — reusing `tas_guard.permuted_labels_among_labelled`, the same function and
the same one-knob argument as `TAS-AM3b`. Re-run the full `w_coh` grid over the draw and
report the per-class path-change rate.

**Reads, fixed here before it runs, and deliberately identical to `TAS-AM3b`'s:**

- **A small null change rate is the CORRECT result and is not a failure.**
- **If the null reaches ≥ 50% of the real path-change rate at any weight**, `TAS-5`'s
  change cannot be attributed to genre structure, and every `TAS-5` figure must be
  reported carrying that caveat.
- **If the null stays below 50%, report the ratio and nothing more. No claim about tags is
  licensed by this control.**

#### Scope of this amendment

**Nothing else moves.** No criterion, bar, weight, default, currency, vocabulary or
substrate changes. `TAS-6`'s adverse selection-side verdict is untouched and still bars an
adoption recommendation per §5. §1's vocabulary stays the `COH-2` union genre; `TAS-AM4`'s
candidate frames are **not** used here.
```

- [ ] **Step 2: Verify the anchors it names still resolve**

Run:
```bash
cd /c/dev/music-app && grep -n "permuted_labels_among_labelled" builder/analysis/2026-07-30-tag-discrimination/tas_guard.py
```
Expected: one `def` at line ~92. If absent, stop — `TAS-AM5c` names a function that does not exist and the amendment is wrong before it is committed.

- [ ] **Step 3: Commit — this timestamp is the evidence**

```bash
git commit -m "TAS-AM5: the routing-side instrument check, written before any routing result exists" -- docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md
```

**Do not proceed to `TAS-R2` until this commit exists.**

---

### Task `TAS-R2`: The pair draw

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_pairs.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_pairs.py`

**Interfaces:**
- Consumes: `tas_common.{HERE, fame_frame, graph_mbids}`; `tas_signal.edge_class`.
- Produces: `draw_pairs() -> list[tuple[str, str, str]]` — `(mbid_a, mbid_b, class_label)`,
  classes `ff`/`fo`/`oo`; module constants `SEED`, `PER_CLASS`, `MIN_READABLE_PER_CLASS`;
  writes `tas_pairs.json`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_pairs.py
"""The pre-registered TAS-5 draw -- the properties that must not drift."""

from __future__ import annotations

from tas_pairs import MIN_READABLE_PER_CLASS, SEED, draw_pairs


def test_pairs_carry_their_class_label():
    # CRS-A1: Track B's draw discarded class labels and three pre-registered
    # quantities became uncomputable until it was fixed mid-flight.
    pairs = draw_pairs()
    assert all(len(p) == 3 for p in pairs)
    assert {p[2] for p in pairs} <= {"ff", "fo", "oo"}


def test_draw_is_deterministic_under_the_committed_seed():
    assert draw_pairs() == draw_pairs()


def test_the_seed_is_the_pre_registered_one():
    # td_pathedges.py deliberately used a DIFFERENT seed so it would not consume
    # this draw. Consuming it here is the intended use; using any other seed
    # would mean TAS-5 did not run on the pre-registered pair set.
    assert SEED == "20260730-tas"


def test_every_class_meets_the_readability_floor_or_is_reported_unreadable():
    pairs = draw_pairs()
    for cls in ("ff", "fo", "oo"):
        n = sum(1 for p in pairs if p[2] == cls)
        assert n >= MIN_READABLE_PER_CLASS or n == 0


def test_no_pair_joins_an_artist_to_itself():
    assert all(a != b for a, b, _ in draw_pairs())
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_pairs.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_pairs'`

- [ ] **Step 3: Write the implementation**

```python
# tas_pairs.py
"""The TAS pair set -- fresh draw, this probe's own (spec section 3).

OBSCURE-ENDPOINT CLASSES ARE INCLUDED BY THE OWNER'S EXPLICIT TRIGGER,
2026-07-30. NEXT.md parks the `x lower` redraw as his call; this pulls it, for
this probe only. Track B's committed draw is untouched and its classes stay the
record for its own reads.

CLASSES CARRIED END TO END (CRS-A1): Track B's draw returned a sorted set and
discarded each pair's class, making three pre-registered quantities uncomputable
until it was fixed mid-flight. Every pair here carries its label.

NO ATTRITION GUARD, AND NONE IS NEEDED. Track B restricted its draw to pairs
routable in every compared cell because its cells were DIFFERENT GRAPHS. Nothing
here is rebuilt: TAS-5 routes ONE graph under different weights. Only the largest
connected component is retained, so a path exists between any two artists the
draw can offer and no cell can lose a pair.

SEED: this IS the pre-registered seed. td_pathedges.py used `20260730-tdcal`
deliberately so its calibration run would not consume this draw.
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
    mbids = sorted(m for m in graph_mbids() if m in frame)
    rng = random.Random(SEED)
    buckets: dict[str, set[tuple[str, str, str]]] = {"ff": set(), "fo": set(), "oo": set()}
    attempts = 0
    while any(len(v) < PER_CLASS for v in buckets.values()) and attempts < 2_000_000:
        attempts += 1
        a, b = rng.sample(mbids, 2)
        cls = edge_class(frame[a], frame[b])
        if len(buckets[cls]) < PER_CLASS:
            lo, hi = sorted((a, b))
            buckets[cls].add((lo, hi, cls))
    out: list[tuple[str, str, str]] = []
    for cls in ("ff", "fo", "oo"):
        pairs = sorted(buckets[cls])
        out.extend(pairs if len(pairs) >= MIN_READABLE_PER_CLASS else [])
    return out


def main() -> None:
    pairs = draw_pairs()
    counts = {c: sum(1 for p in pairs if p[2] == c) for c in ("ff", "fo", "oo")}
    OUT.write_text(
        json.dumps(
            {
                "seed": SEED,
                "per_class_target": PER_CLASS,
                "min_readable_per_class": MIN_READABLE_PER_CLASS,
                "counts": counts,
                "unreadable": [c for c, n in counts.items() if n == 0],
                "pairs": pairs,
            },
            indent=1,
        ),
        encoding="utf-8",
    )
    print(counts, flush=True)


if __name__ == "__main__":
    main()
```

**Note on `sorted(...)` at the top of `draw_pairs`:** `graph_mbids()` order must not depend
on dict insertion order for the seed to be reproducible across runs. The inherited draft
omitted this.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_pairs.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Run it and record any unreadable class**

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_pairs.py`
Expected: `{'ff': 40, 'fo': 40, 'oo': 40}`. **Any class reported unreadable is named in the
findings and never pooled into another.**

- [ ] **Step 6: Commit**

```bash
git commit -m "TAS-R2: the pre-registered TAS-5 pair draw, classes carried end to end" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task `TAS-R3`: `find_path_coh`, the equivalence check, and `TAS-5`

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_route.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_route.py`

**Interfaces:**
- Consumes: `artistpath_api.pathfinding.find_path`, `artistpath_api.config.ApiConfig`,
  `artistpath_api.graph_store.GraphStore`; `tas_common.{HERE, ADOPTED, ADOPTED_SHA,
  neutral_for, resolved_agreement}`; `tas_pairs.draw_pairs`; `tas_tags.label_sets`.
- Produces: `find_path_coh(store, source, target, cfg, labels, w_coh) -> list[int] | None`;
  `agreement_cost_of(path, store, labels) -> float`; `load_adopted() -> GraphStore`; writes
  `tas_route.json`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_route.py
"""find_path_coh -- the properties that must not drift.

These are UNIT tests on a synthetic store. TAS-AM5a's equivalence check is a
separate, stronger thing: the FULL draw against the REAL artifact, run by
tas_route.main(). Passing these does not discharge it.
"""

from __future__ import annotations

import numpy as np
import pytest

from tas_route import agreement_cost_of, find_path_coh


class FakeStore:
    """Three-node line graph: 0 -- 1 -- 2, plus a detour 0 -- 3 -- 2."""

    def __init__(self):
        self.mbids = ["a", "b", "c", "d"]
        self.pop_raw = np.array([0.5, 0.5, 0.5, 0.5], dtype=np.float32)
        self.degree_hub_penalty = np.zeros(4, dtype=np.float32)
        self._adj = {
            0: [(1, 0.9), (3, 0.9)],
            1: [(0, 0.9), (2, 0.9)],
            2: [(1, 0.9), (3, 0.9)],
            3: [(0, 0.9), (2, 0.9)],
        }

    def neighbours_of(self, node_id):
        return iter(self._adj[node_id])


@pytest.fixture
def cfg():
    from artistpath_api.config import ApiConfig

    return ApiConfig()


def test_zero_weight_ignores_labels_entirely(cfg):
    store = FakeStore()
    rich = {"a": {"rock"}, "b": {"rock"}, "c": {"rock"}, "d": {"jazz"}}
    bare: dict[str, set[str]] = {}
    assert find_path_coh(store, 0, 2, cfg, rich, 0.0) == \
        find_path_coh(store, 0, 2, cfg, bare, 0.0)


def test_a_dominating_weight_routes_through_the_agreeing_neighbour(cfg):
    # Both detours cost the same on every production term; only genre differs.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"rock"}, "c": {"rock"}, "d": {"jazz"}}
    path = find_path_coh(store, 0, 2, cfg, labels, 1e6 * cfg.w_sim)
    assert path == [0, 1, 2], "the coherence term did not reach the cost function"


def test_an_unlabelled_candidate_is_not_demoted(cfg):
    # THE NEUTRAL RULE (spec section 1): a bare artist takes the per-artist
    # median, never zero. Zero is a positive claim of dissimilarity, and
    # unlabelled artists are disproportionately obscure -- demoting them would
    # push DD-F1 the wrong way.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"jazz"}, "c": {"rock"}}  # d is bare
    path = find_path_coh(store, 0, 2, cfg, labels, 1e6 * cfg.w_sim)
    assert path == [0, 3, 2], "the bare candidate was demoted below a known mismatch"


def test_agreement_cost_of_sums_one_minus_agreement_along_the_path(cfg):
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"rock"}, "c": {"rock"}, "d": {"jazz"}}
    # 0->1 and 1->2 both agree exactly: (1 - 1.0) + (1 - 1.0) == 0.0
    assert agreement_cost_of([0, 1, 2], store, labels) == pytest.approx(0.0)


def test_source_equals_target_returns_the_single_node(cfg):
    assert find_path_coh(FakeStore(), 2, 2, cfg, {}, 1.0) == [2]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_route.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_route'`

- [ ] **Step 3: Write the implementation**

```python
# tas_route.py
"""TAS-5: would a coherence term change the journeys the app builds?

SUBSTRATE: THE ADOPTED ARTIFACT (TAS-AM2). TAS-5 asks what the APP routes today,
so it runs on graph-t15-tiebreakfix.bin, sha-asserted on load -- never on the
pre-cap ALG-E capture that TAS-2/TAS-3/TAS-4 use. TAS-AM2's standing constraint:
NO READ MAY COMPARE A CAPTURE-SIDE FIGURE AGAINST AN ARTIFACT-SIDE ONE.

THE PATHFINDER IS FORKED, NOT PATCHED. find_path_coh is a copy of
api/src/artistpath_api/pathfinding.py find_path with ONE added term:

    + w_coh * (1 - agreement(u, v))

w_coh DOES NOT EXIST in ApiConfig and this file does not propose adding one. It
is harness-local. Shipping it would be a config default change, which is an
adoption, which this probe does not license.

THE FORK OMITS excludes, avoidance_map, effective_floor_raw and forbidden_edge
because no arm uses a bypass. That omission is PROVED equivalent by TAS-AM5a --
identical paths to production find_path at w_coh = 0 over the FULL draw -- not
argued to be. If TAS-AM5a fails, nothing this file produces counts.

KILL for the router-side architecture: only if journeys are unchanged in EVERY
class at every weight. A pooled bar is explicitly rejected -- a small overall
change concentrated in famous-to-famous is a signal worth chasing, and
famous-to-famous is where DD-F1 lives.

UNCHANGED means the identical artist sequence, in order, endpoints included. Path
COST is not compared: it necessarily moves whenever w_coh > 0, and reading that
as an effect would be an artefact of the instrument.

STANDING CAUTION: three consecutive attempts to change router behaviour by
changing prices returned nulls (Track 2's repricing family, Track 3b's
thresholded toll, Track B's R2 quota edges declined at production weights). A
TAS-5 null is WEAK evidence about tags specifically and must not be reported as
"tags do not work"; TAS-3 and TAS-4 are what distinguish the two.
"""

from __future__ import annotations

import hashlib
import heapq
import json

from tas_common import ADOPTED, ADOPTED_SHA, HERE, neutral_for, resolved_agreement
from tas_pairs import draw_pairs
from tas_tags import label_sets

OUT = HERE / "tas_route.json"
WEIGHT_MULTIPLES = [0.0, 0.25, 0.5, 1.0, 2.0]
CLASSES = ("ff", "fo", "oo")


def load_adopted():
    """The adopted artifact, sha-asserted. A wrong artifact looks like a right one."""
    from artistpath_api.graph_store import GraphStore

    payload = ADOPTED.read_bytes()
    got = hashlib.sha256(payload).hexdigest()
    if got != ADOPTED_SHA:
        raise SystemExit(f"artifact sha mismatch: expected {ADOPTED_SHA}, got {got}")
    return GraphStore.from_bytes(payload)


def _neutral_and_neighbours(store, u: int, labels: dict[str, set[str]]):
    """One artist's neighbour list and its per-artist neutral value.

    THE NEUTRAL IS PER-ARTIST, VIA THE ONE RESOLUTION PATH -- not a hardcoded
    constant. An earlier draft inlined 0.15 here, which would have made the
    routing arm use a different neutral rule from the selection arm while both
    documents claimed they shared one.
    """
    neighbours = list(store.neighbours_of(u))
    u_set = labels.get(store.mbids[u], set())
    cand_sets = [labels.get(store.mbids[v], set()) for v, _ in neighbours]
    return neighbours, u_set, neutral_for(u_set, cand_sets)


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
        neighbours, u_set, neutral = _neutral_and_neighbours(store, u, labels)
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


def agreement_cost_of(path, store, labels) -> float:
    """Total (1 - agreement) along a path. TAS-AM5b's comparison quantity."""
    total = 0.0
    for u, v in zip(path, path[1:]):
        _, u_set, neutral = _neutral_and_neighbours(store, u, labels)
        total += 1.0 - resolved_agreement(
            u_set, labels.get(store.mbids[v], set()), neutral
        )
    return total


def equivalence_check(store, cfg, labels, pairs, index) -> dict:
    """TAS-AM5a: w_coh = 0 must reproduce production find_path EXACTLY, on every pair."""
    from artistpath_api.pathfinding import find_path

    mismatches = []
    for a, b, _cls in pairs:
        s, t = index[a], index[b]
        if find_path_coh(store, s, t, cfg, labels, 0.0) != find_path(store, s, t, [], cfg):
            mismatches.append([a, b])
    return {
        "pairs_checked": len(pairs),
        "mismatches": mismatches,
        "passes": not mismatches,
    }


def main() -> None:
    from artistpath_api.config import ApiConfig

    cfg = ApiConfig()
    store = load_adopted()
    labels = label_sets()
    index = {m: i for i, m in enumerate(store.mbids)}
    pairs = [p for p in draw_pairs() if p[0] in index and p[1] in index]

    equiv = equivalence_check(store, cfg, labels, pairs, index)
    print(f"TAS-AM5a equivalence: {equiv['passes']} "
          f"({len(equiv['mismatches'])} mismatches / {equiv['pairs_checked']})", flush=True)
    if not equiv["passes"]:
        raise SystemExit(
            "TAS-AM5a FAILED -- the fork is not production's path. "
            "Every TAS-5 figure is void. Do not proceed."
        )

    # The baseline is computed ONCE, not once per weight.
    baseline = {
        (a, b): find_path_coh(store, index[a], index[b], cfg, labels, 0.0)
        for a, b, _ in pairs
    }

    per_weight: dict[str, dict[str, dict]] = {}
    for mult in WEIGHT_MULTIPLES:
        w_coh = mult * cfg.w_sim
        by_class: dict[str, list[bool]] = {c: [] for c in CLASSES}
        for a, b, cls in pairs:
            arm = find_path_coh(store, index[a], index[b], cfg, labels, w_coh)
            by_class[cls].append(baseline[(a, b)] != arm)
        per_weight[str(mult)] = {
            cls: {
                "n": len(v),
                "changed": sum(v),
                "changed_share": round(sum(v) / len(v), 4) if v else None,
            }
            for cls, v in by_class.items()
        }
        print(f"  w_coh={mult}x w_sim: "
              + ", ".join(f"{c} {per_weight[str(mult)][c]['changed']}/"
                          f"{per_weight[str(mult)][c]['n']}" for c in CLASSES),
              flush=True)

    kills = all(
        cell["changed"] == 0
        for mult, classes in per_weight.items()
        if mult != "0.0"
        for cell in classes.values()
    )

    result = {
        "substrate": {"file": ADOPTED.name, "sha256": ADOPTED_SHA,
                      "note": "ADOPTED ARTIFACT per TAS-AM2. Never compare against a "
                              "capture-side figure."},
        "pair_seed": "20260730-tas",
        "weight_multiples_of_w_sim": WEIGHT_MULTIPLES,
        "w_sim": cfg.w_sim,
        "tas_am5a_equivalence": equiv,
        "per_weight": per_weight,
        "tas5_kills": kills,
        "kill_rule": "TAS-5 kills ONLY if unchanged in EVERY class at EVERY weight. "
                     "A pooled bar is explicitly rejected.",
    }
    OUT.write_text(json.dumps(result, indent=1), encoding="utf-8")
    print(json.dumps({"tas5_kills": kills}, indent=1), flush=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_route.py -v`
Expected: PASS (5 tests)

- [ ] **Step 5: Reconcile the fork against production line by line**

Diff `find_path_coh` against `api/src/artistpath_api/pathfinding.py:76-149`. Confirm the
only differences are (a) the added `w_coh` term and (b) the omission of `excludes`,
`hard`, `banned`, `avoid` and `effective_floor_raw`. **Confirm the omission is still
sound:** production computes `cfg.w_avoid * avoid.get(v, 0.0)` which is exactly `0.0` with
no exclusions, and `effective_floor_raw` with no exclusions returns `max(0.0,
base_floor_raw)` which equals `base_floor_raw` because `pop_raw` is non-negative. **Do not
take this reconciliation as proof — `TAS-AM5a` in Step 6 is the proof.** If any read later
needs bypass depth, port those branches rather than approximating them.

- [ ] **Step 6: Run it — `TAS-AM5a` gates everything after it**

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_route.py`
Expected: `TAS-AM5a equivalence: True (0 mismatches / 120)`, then per-class change counts at
each of five weights, then `tas5_kills`. Roughly 10–15 minutes — `td_pathedges.json` records
900 pairs at 609.5 s, and this is 120 pairs × 5 weights plus the equivalence pass.

**If `TAS-AM5a` reports any mismatch the run aborts by design. Do not edit the check to pass
it — find the drift between the fork and production.**

- [ ] **Step 7: Commit**

```bash
git commit -m "TAS-R3: TAS-5 router simulation, with TAS-AM5a equivalence over the full draw" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

### Task `TAS-R4`: `TAS-AM5b`, `TAS-AM5c`, and `TAS-6`'s routing half

**Files:**
- Create: `builder/analysis/2026-07-30-tag-discrimination/tas_route_guard.py`
- Test: `builder/analysis/2026-07-30-tag-discrimination/test_tas_route_guard.py`

**`tas_guard.py` is NOT modified.** It is committed evidence for the selection side, its
`tas_guard.json` is the record `TAS-6`'s adverse verdict rests on, and re-running it to add
routing output would rewrite that file. The two functions needed from it are imported.

**Interfaces:**
- Consumes: `tas_route.{find_path_coh, agreement_cost_of, load_adopted}`;
  `tas_guard.{permuted_labels_among_labelled, is_adverse}`; `tas_common.fame_frame`;
  `tas_pairs.draw_pairs`; `tas_tags.label_sets`.
- Produces: writes `tas_route_guard.json` with `tas_am5b_liveness`, `tas_am5c_null_control`
  and `tas6_routing_half`.

- [ ] **Step 1: Write the failing test**

```python
# test_tas_route_guard.py
"""TAS-AM5b/c and TAS-6's routing half -- the properties that must not drift."""

from __future__ import annotations

import numpy as np
import pytest

from tas_route_guard import agreement_only_path, sub_decile_interior_count


class FakeStore:
    def __init__(self):
        self.mbids = ["a", "b", "c", "d"]
        self.pop_raw = np.array([0.9, 0.5, 0.9, 0.05], dtype=np.float32)
        self.degree_hub_penalty = np.zeros(4, dtype=np.float32)
        self._adj = {
            0: [(1, 0.9), (3, 0.1)],
            1: [(0, 0.9), (2, 0.9)],
            2: [(1, 0.9), (3, 0.1)],
            3: [(0, 0.1), (2, 0.1)],
        }

    def neighbours_of(self, node_id):
        return iter(self._adj[node_id])


def test_agreement_only_path_ignores_similarity_entirely():
    # 0->3->2 has terrible similarity but perfect genre agreement; the
    # agreement-only reference must take it regardless.
    store = FakeStore()
    labels = {"a": {"rock"}, "b": {"jazz"}, "c": {"rock"}, "d": {"rock"}}
    path, cost = agreement_only_path(store, 0, 2, labels)
    assert path == [0, 3, 2]
    assert cost == pytest.approx(0.0)


def test_sub_decile_interior_count_excludes_endpoints():
    # TAS-6 routing half counts INTERIOR artists below the tenth percentile.
    # An obscure ENDPOINT is the user's own choice, not something routing supplied.
    frame_pctl = {"a": 0.99, "b": 0.40, "c": 0.99, "d": 0.05}
    assert sub_decile_interior_count([[0, 3, 2]], ["a", "b", "c", "d"], frame_pctl) == 1
    assert sub_decile_interior_count([[3, 1, 0]], ["a", "b", "c", "d"], frame_pctl) == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_route_guard.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'tas_route_guard'`

- [ ] **Step 3: Write the implementation**

```python
# tas_route_guard.py
"""TAS-AM5b (liveness), TAS-AM5c (null control), and TAS-6's routing half.

SUBSTRATE: THE ADOPTED ARTIFACT (TAS-AM2), same as tas_route.py. TAS-6's two
halves measure the two architectures separately AND ARE NEVER COMBINED: the
selection half in tas_guard.json is on the ALG-E capture, this one is on the
artifact, and TAS-AM2 forbids comparing across that line.

TAS-6 IS REPORTED, NEVER A SUCCESS SIGNAL. Adverse at a >= 10% reduction. The
SELECTION half is ALREADY ADVERSE and bars an adoption recommendation whatever
this file reports.

TAS-AM5b IS NOT THE WITHDRAWN RED CHECK. The original -- shuffle labels, demand
large change -- was withdrawn as UNACHIEVABLE by TAS-AM3: randomising labels
destroys overlap rather than randomising it, so every correct null control must
report a small number. DO NOT "FIX" THIS TO MAKE A SHUFFLE FIRE.

tas_guard.py IS NOT MODIFIED. It holds the committed selection-side record.
"""

from __future__ import annotations

import heapq
import json

from tas_common import HERE, fame_frame
from tas_guard import is_adverse, permuted_labels_among_labelled
from tas_pairs import draw_pairs
from tas_route import (
    WEIGHT_MULTIPLES,
    agreement_cost_of,
    find_path_coh,
    load_adopted,
    _neutral_and_neighbours,
)
from tas_route import CLASSES
from tas_tags import label_sets

OUT = HERE / "tas_route_guard.json"
DOMINATING_MULTIPLE = 1e6
SUB_DECILE = 0.10
NULL_SEED = 909
TOLERANCE = 1e-9


def agreement_only_path(store, source, target, labels):
    """Dijkstra with cost = (1 - agreement) ALONE. TAS-AM5b's independent reference.

    Every production term is dropped, so the optimum here is computed WITHOUT
    find_path_coh -- which is what makes it an external reference rather than the
    instrument checking itself.
    """
    if source == target:
        return [source], 0.0
    dist = {source: 0.0}
    prev: dict[int, int] = {}
    pq: list[tuple[float, int]] = [(0.0, source)]
    while pq:
        d, u = heapq.heappop(pq)
        if u == target:
            break
        if d > dist.get(u, float("inf")):
            continue
        neighbours, u_set, neutral = _neutral_and_neighbours(store, u, labels)
        for v, _sim in neighbours:
            from tas_common import resolved_agreement

            nd = d + (1.0 - resolved_agreement(
                u_set, labels.get(store.mbids[v], set()), neutral))
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                prev[v] = u
                heapq.heappush(pq, (nd, v))
    if target not in prev:
        return None, float("inf")
    path = [target]
    while path[-1] != source:
        path.append(prev[path[-1]])
    return path[::-1], dist[target]


def sub_decile_interior_count(paths, mbids, frame_pctl) -> int:
    """Interior artists below the tenth fame percentile, endpoints excluded.

    ENDPOINTS ARE EXCLUDED DELIBERATELY: an obscure endpoint is the user's own
    choice, not something the router supplied. TAS-6 asks what routing delivers.
    """
    total = 0
    for path in paths:
        for node in path[1:-1]:
            if frame_pctl.get(mbids[node], 1.0) < SUB_DECILE:
                total += 1
    return total


def main() -> None:
    from artistpath_api.config import ApiConfig

    cfg = ApiConfig()
    store = load_adopted()
    labels = label_sets()
    frame = fame_frame()
    index = {m: i for i, m in enumerate(store.mbids)}
    pairs = [p for p in draw_pairs() if p[0] in index and p[1] in index]

    # ---- TAS-AM5b: liveness against an independently computed reference ----
    dominating = DOMINATING_MULTIPLE * cfg.w_sim
    failures = []
    for a, b, _cls in pairs:
        s, t = index[a], index[b]
        ref_path, ref_cost = agreement_only_path(store, s, t, labels)
        arm = find_path_coh(store, s, t, cfg, labels, dominating)
        if arm is None or ref_path is None:
            failures.append([a, b, "no path"])
            continue
        got = agreement_cost_of(arm, store, labels)
        if abs(got - ref_cost) > TOLERANCE:
            failures.append([a, b, round(got - ref_cost, 12)])
    liveness = {
        "dominating_w_coh_multiple_of_w_sim": DOMINATING_MULTIPLE,
        "pairs_checked": len(pairs),
        "failures": failures,
        "passes": not failures,
        "compares": "TOTAL (1 - agreement) along the path, NOT the node sequence -- "
                    "tie-safe and threshold-free (TAS-AM5b).",
    }
    print(f"TAS-AM5b liveness: {liveness['passes']} "
          f"({len(failures)} failures / {len(pairs)})", flush=True)
    if not liveness["passes"]:
        raise SystemExit(
            "TAS-AM5b FAILED -- the coherence term is not reaching the cost "
            "function. Every TAS-5 figure is void. Do not proceed."
        )

    # ---- TAS-6 routing half + TAS-AM5c null control, over the real grid ----
    null_labels = permuted_labels_among_labelled(labels, NULL_SEED)

    def grid(lab) -> dict:
        base = {(a, b): find_path_coh(store, index[a], index[b], cfg, lab, 0.0)
                for a, b, _ in pairs}
        out: dict[str, dict] = {}
        for mult in WEIGHT_MULTIPLES:
            w_coh = mult * cfg.w_sim
            by_class = {c: [] for c in CLASSES}
            paths = []
            for a, b, cls in pairs:
                arm = find_path_coh(store, index[a], index[b], cfg, lab, w_coh)
                by_class[cls].append(base[(a, b)] != arm)
                if arm:
                    paths.append(arm)
            out[str(mult)] = {
                "changed_share_by_class": {
                    c: round(sum(v) / len(v), 4) if v else None
                    for c, v in by_class.items()
                },
                "changed_share_pooled_FOR_THE_NULL_RATIO_ONLY": round(
                    sum(sum(v) for v in by_class.values())
                    / sum(len(v) for v in by_class.values()), 4),
                "sub_decile_interiors": sub_decile_interior_count(
                    paths, store.mbids, frame),
            }
            print(f"  w_coh={mult}x: {out[str(mult)]['changed_share_by_class']}", flush=True)
        return out

    print("real frame:", flush=True)
    real = grid(labels)
    print("null frame (labels permuted among labelled artists only):", flush=True)
    null = grid(null_labels)

    baseline_sub_decile = real["0.0"]["sub_decile_interiors"]
    tas6 = {
        "baseline_sub_decile_interiors": baseline_sub_decile,
        "by_weight": {
            mult: {
                "sub_decile_interiors": cell["sub_decile_interiors"],
                "adverse": is_adverse(baseline_sub_decile, cell["sub_decile_interiors"]),
            }
            for mult, cell in real.items() if mult != "0.0"
        },
        "note": "ROUTING half only. The SELECTION half is in tas_guard.json, on the "
                "ALG-E capture, and TAS-AM2 forbids comparing the two. The selection "
                "half is ADVERSE and bars adoption regardless of this.",
    }

    ratios = {
        mult: round(
            null[mult]["changed_share_pooled_FOR_THE_NULL_RATIO_ONLY"]
            / real[mult]["changed_share_pooled_FOR_THE_NULL_RATIO_ONLY"], 4)
        if real[mult]["changed_share_pooled_FOR_THE_NULL_RATIO_ONLY"] else None
        for mult in real if mult != "0.0"
    }
    null_control = {
        "seed": NULL_SEED,
        "null_over_real_ratio_by_weight": ratios,
        "reaches_half_at_any_weight": any(r is not None and r >= 0.5
                                          for r in ratios.values()),
        "read": "A SMALL null is the CORRECT result, not a failure. If the ratio "
                "reaches 0.5 at any weight, TAS-5's change cannot be attributed to "
                "genre structure and every figure carries that caveat. Below 0.5: "
                "report the ratio and NOTHING MORE -- no claim about tags is "
                "licensed by this control (TAS-AM5c).",
    }

    OUT.write_text(json.dumps({
        "substrate": {"note": "ADOPTED ARTIFACT per TAS-AM2."},
        "tas_am5b_liveness": liveness,
        "tas_am5c_null_control": null_control,
        "tas6_routing_half": tas6,
        "real_grid": real,
        "null_grid": null,
    }, indent=1), encoding="utf-8")
    print(json.dumps({"tas6_routing": tas6["by_weight"],
                      "null_ratios": ratios}, indent=1), flush=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd builder && UV_LINK_MODE=copy uv run python -m pytest analysis/2026-07-30-tag-discrimination/test_tas_route_guard.py -v`
Expected: PASS (2 tests)

- [ ] **Step 5: Run it**

Run: `cd builder && UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u analysis/2026-07-30-tag-discrimination/tas_route_guard.py`
Expected: `TAS-AM5b liveness: True`, then the real grid, then the null grid, then `TAS-6`'s
routing half and the null ratios. Roughly 25–35 minutes: two full grids plus the liveness
pass. **Run it in the foreground or with `run_in_background`; never through `tail`.**

- [ ] **Step 6: Confirm `tas_guard.json` was not touched**

Run: `git status --short builder/analysis/2026-07-30-tag-discrimination/tas_guard.json`
Expected: **empty.** If it shows modified, the selection-side record has been overwritten —
restore it from HEAD before committing.

- [ ] **Step 7: Commit**

```bash
git commit -m "TAS-R4: TAS-AM5b/c and TAS-6's routing half on the adopted artifact" -- builder/analysis/2026-07-30-tag-discrimination/
```

---

## What is NOT in this plan, and why

- **Task 8 (findings and the owner-facing read) is deliberately excluded.** §5 licenses no
  outcome read until the full grid has run and `TAS-1`…`TAS-6` are all in hand. Writing the
  findings is the *next* session's work, and this plan's completion is a natural seam:
  its output is committed JSON rather than a live understanding.
- **No `TAS-4`/`TAS-6` re-run against `TAS-AM4`'s enriched frames.** `TAS-AM4` read 5
  licenses a recommendation only. §1's vocabulary is untouched here.
- **No rebuild, no config default change, no blind listen.** All three are adoptions or
  spend the owner's ear.

## Handoff seam

**This plan is 4 tasks and does not need an internal handoff point.** If it grows — most
likely because `TAS-AM5a` or `TAS-AM5b` fails and the fork needs real debugging — the seam
is **after `TAS-R3`**, whose output (`tas_route.json`) is a committed artifact rather than a
live understanding.

## Self-Review

**Spec coverage.** §1's device (routing form, the neutral rule, the `w_coh` grid) →
`TAS-R3`. §2's `TAS-5` (per-class kill, "unchanged" definition, cost excluded) → `TAS-R3`.
§2's `TAS-6` routing half (sub-decile presence, fixed reference frame, 10% adverse bar) →
`TAS-R4`. §3's pair set (fresh draw, classes end to end, no attrition guard) → `TAS-R2`.
§4's green check → `TAS-AM5a` in `TAS-R3`. §4's red check → `TAS-AM5b`/`c` in `TAS-R1` and
`TAS-R4`. `TAS-AM2`'s substrate rule → asserted on load in `TAS-R3`, restated in both
JSON outputs. §5's reads → deferred to Task 8 by design, stated above.

**Placeholder scan.** One prose-only step remains: `TAS-R3` Step 5's line-by-line
reconciliation, which is a human diff rather than code, and it is explicitly not load-bearing
— `TAS-AM5a` is the proof. Every other step carries runnable content.

**Type consistency.** `find_path_coh(store, source, target, cfg, labels, w_coh)` is defined
in `TAS-R3` and consumed with that signature in `TAS-R4`. `agreement_cost_of(path, store,
labels)`, `load_adopted()`, `_neutral_and_neighbours(store, u, labels)`, `WEIGHT_MULTIPLES`
and `CLASSES` are all defined in `tas_route.py` and imported by name in `tas_route_guard.py`.
`permuted_labels_among_labelled(labels, seed)` and `is_adverse(baseline, arm)` match
`tas_guard.py`'s committed signatures.
