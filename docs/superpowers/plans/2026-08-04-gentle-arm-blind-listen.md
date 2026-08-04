# Gentle-Arm Blind Listen (`GBL-`) Implementation Plan

**Role: ACTIVE — the operational plan for the `GBL-` blind listen.** The spec
(`../specs/2026-08-04-gentle-arm-blind-listen-design.md`) governs wherever this plan
disagrees.

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the throwaway harness that runs the pre-registered blind listen of
`specs/2026-08-04-gentle-arm-blind-listen-design.md` — pair derivation, journey
generation for both arms, clip resolution, the side-by-side verdict page, sealed
mapping, and the unblind tally.

**Architecture:** Everything lives in `builder/analysis/2026-08-04-gentle-arm-blind-listen/`
and reuses the frozen `CRE-` harness (`cre_common`, `cre_mirror`, `cre_ladder`,
`cre_sweep`, `cre_gates`) plus the frozen API source (`use_frozen("api_src")`) for
`find_journey`, `path_metrics`, and `ClipResolver`. No shipped code changes — the ramp
stays harness-side. Arm-identifying output is split from owner-facing output at write
time: sealed files go to `.superpowers/gbl/` (gitignored), page data carries only
per-pair-shuffled `L`/`R` tokens.

**Tech Stack:** Python 3 stdlib + numpy (builder venv), the frozen CRE/API modules,
vanilla HTML/JS served by `http.server`. No new dependencies.

## Global Constraints

- **The spec governs wherever this plan disagrees:** `docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md`.
- Every `uv` command is prefixed `UV_LINK_MODE=copy`; every command that prints artist names also sets `PYTHONIOENCODING=utf-8`; long jobs use `python -u`.
- Run all commands from `builder/` (its venv). Tests: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q` (builder's pytest does not collect `analysis/` by default — the explicit path is required).
- **No file under `api/`, `frontend/`, or `builder/src/` is modified.** The ramp is not wired into `ApiConfig`.
- **The raw Spotify export never enters the repo.** Its path is always a CLI argument, never a constant.
- **Arm identity never reaches an owner-facing artifact.** Sealed outputs (`.superpowers/gbl/`) are written by scripts and read by no one until `gbl_unblind.py` confirms the §5 run state. Page data and the page itself carry only `L`/`R`.
- **Figures are cited, never restated:** ramp size is `RAMPS["P1a"]` from `cre_common`, never a literal; artifact hashes come from `load_adopted()` / the `B-S1.bin.json` manifest, never transcribed.
- Work lands on branch `gentle-arm-blind-listen` (exists, pushed); commit per task; the PR body follows closeout D5.
- Per the global security instruction: `snyk_code_scan` runs on the new code before the PR is marked ready (Task 8).
- **Handoff seam, named at authoring time:** after Task 8 everything is committed and this plan's sessions are done. The listen itself is executed by a **fresh runner session** from `RUNNER-BRIEF.md` — that session must not have executed this plan and must not read the CRE findings note, `NEXT.md`'s result paragraphs, or spec §1–§2.

## File Structure

```
builder/analysis/2026-08-04-gentle-arm-blind-listen/
  gbl_common.py           # paths, constants, cre-import helper, sealed-dir helper
  gbl_pairs.py            # Spotify export -> ranked familiarity -> candidate pairs
  gbl_generate.py         # ladders for both arms, gates, sealed + page outputs
  gbl_clips.py            # name-based clip resolution for every presented artist
  gbl_page.html           # the side-by-side page (template, __GBL_DATA__ placeholder)
  gbl_page.py             # localhost server: serves page, writes verdicts to disk
  gbl_unblind.py          # run-state check, tally, ear-tracking table
  RUNNER-BRIEF.md         # mechanics-only brief for the fresh runner session
  test_gbl_pairs.py
  test_gbl_generate.py
  test_gbl_clips.py
  test_gbl_page.py
  test_gbl_unblind.py
docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md   # §8 gains GBL-AM1 (Task 3, owner gate)
```

---

### Task 1: `gbl_common.py` — shared constants and import plumbing

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_common.py`
- Test: `builder/analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_common.py`

**Interfaces:**
- Produces: `HERE: Path`, `ROOT: Path`, `SEALED_DIR: Path`, `DEPTHS = (0, 10, 20)`,
  `TOKENS = ("L", "R")`, `ARMS = ("V0", "G")`, `use_cre() -> None` (puts the CRE
  harness dir on `sys.path`), `in_dir(arg: str) -> Path` (bare-filename rule, HERE-anchored),
  `sealed_path(arg: str) -> Path` (bare-filename rule, SEALED_DIR-anchored, creates the dir).

- [ ] **Step 1: Write the failing test**

```python
# test_gbl_common.py
import json

import gbl_common as gc


def test_paths_and_constants():
    assert gc.HERE.name == "2026-08-04-gentle-arm-blind-listen"
    assert gc.ROOT.joinpath("builder").is_dir()
    assert gc.SEALED_DIR == gc.ROOT / ".superpowers" / "gbl"
    assert gc.DEPTHS == (0, 10, 20)
    assert gc.TOKENS == ("L", "R")
    assert gc.ARMS == ("V0", "G")


def test_use_cre_makes_cre_common_importable():
    gc.use_cre()
    import cre_common
    assert cre_common.RAMPS["P1a"] > 0  # cited, not restated


def test_in_dir_rejects_traversal():
    for bad in ("../x.json", "a/b.json", "", ".", ".."):
        try:
            gc.in_dir(bad)
            assert False, f"accepted {bad!r}"
        except ValueError:
            pass
    assert gc.in_dir("x.json") == gc.HERE / "x.json"


def test_sealed_path_creates_dir_and_rejects_traversal(tmp_path, monkeypatch):
    monkeypatch.setattr(gc, "SEALED_DIR", tmp_path / "gbl")
    p = gc.sealed_path("gbl_sealed.json")
    assert p == tmp_path / "gbl" / "gbl_sealed.json"
    assert p.parent.is_dir()
    try:
        gc.sealed_path("../oops.json")
        assert False
    except ValueError:
        pass
```

- [ ] **Step 2: Run to verify it fails**

Run (from `builder/`): `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: FAIL — `ModuleNotFoundError: gbl_common`

- [ ] **Step 3: Implement**

```python
# gbl_common.py
"""Shared paths and constants for the GBL- blind listen harness.

Governing document: docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md.
It wins wherever anything here disagrees with it. Reuses the frozen CRE- harness;
figures (ramp size, sha256s) are imported from it, never restated here.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

CRE_DIR = ROOT / "builder" / "analysis" / "2026-08-03-cap-reevaluation"
SEALED_DIR = ROOT / ".superpowers" / "gbl"   # gitignored; arm-identifying output only

DEPTHS = (0, 10, 20)      # spec §3: d0 anchor + the two deep rows
TOKENS = ("L", "R")
ARMS = ("V0", "G")        # never written into page-facing output


def use_cre() -> None:
    p = str(CRE_DIR)
    if p not in sys.path:
        sys.path.insert(0, p)


def _bare(arg: str) -> str:
    if Path(arg).name != arg or arg in ("", ".", ".."):
        raise ValueError(f"expected a bare filename, got {arg!r}")
    return arg


def in_dir(arg: str) -> Path:
    return HERE / _bare(arg)


def sealed_path(arg: str) -> Path:
    name = _bare(arg)
    SEALED_DIR.mkdir(parents=True, exist_ok=True)
    return SEALED_DIR / name
```

Note the test file also needs the module on `sys.path` — add a `conftest.py` in the
same directory so every test file resolves the harness modules:

```python
# conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
```

- [ ] **Step 4: Run to verify it passes**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen
git commit -m "GBL- harness: shared constants, sealed-dir and CRE import plumbing"
```

---

### Task 2: `gbl_pairs.py` — familiarity ranking and candidate pairs

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_pairs.py`
- Test: `builder/analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_pairs.py`

**Interfaces:**
- Consumes: `gbl_common` (Task 1); `cre_common.load_adopted()`; `cre_gates.load_cell("B-S1")`;
  `artistpath_api.search.normalise(text: str) -> str` (frozen api_src).
- Produces:
  - `rank_familiarity(history: list[dict], library: dict) -> list[dict]` — sorted desc by
    `ms_played`; each row `{"name": str, "ms_played": int, "plays": int, "in_library": bool}`.
    A play counts only if `msPlayed >= 30_000` (a skip is not familiarity).
  - `resolve_in(store, name: str) -> list[int]` — node ids whose `normalise(store.names[i])`
    equals `normalise(name)` (all matches, so ambiguity is visible).
  - CLI writing `gbl_pair_candidates.json` and `gbl_pair_proposal.md` (owner-facing).

- [ ] **Step 1: Write the failing test** (fixtures inline — the real export shapes, copied
  from the owner's files 2026-08-04: history entries carry `artistName`/`msPlayed`,
  library carries `tracks[].artist`)

```python
# test_gbl_pairs.py
from gbl_pairs import rank_familiarity, resolve_in


class FakeStore:
    names = ["Radiohead", "Sigur Rós", "Boards of Canada", "Radiohead"]
    mbids = ["m0", "m1", "m2", "m3"]


def test_rank_familiarity_aggregates_and_filters_skips():
    history = [
        {"artistName": "Songs: Ohia", "msPlayed": 442_106},
        {"artistName": "Songs: Ohia", "msPlayed": 366_826},
        {"artistName": "Songs: Ohia", "msPlayed": 4_249},      # skip: not a play
        {"artistName": "Destroyer", "msPlayed": 16_035},        # skip: not a play
        {"artistName": "The Beta Band", "msPlayed": 200_000},
    ]
    library = {"tracks": [{"artist": "Destroyer", "album": "x", "track": "y", "uri": "u"}]}
    rows = rank_familiarity(history, library)
    by_name = {r["name"]: r for r in rows}
    assert by_name["Songs: Ohia"]["plays"] == 2
    assert by_name["Songs: Ohia"]["ms_played"] == 442_106 + 366_826 + 4_249
    assert rows[0]["name"] == "Songs: Ohia"          # sorted by ms_played desc
    assert by_name["Destroyer"]["in_library"] is True
    assert by_name["Destroyer"]["plays"] == 0        # library alone is not a play
    assert by_name["The Beta Band"]["in_library"] is False


def test_resolve_in_is_accent_insensitive_and_returns_all_matches():
    s = FakeStore()
    assert resolve_in(s, "sigur ros") == [1]
    assert resolve_in(s, "Radiohead") == [0, 3]   # ambiguity stays visible
    assert resolve_in(s, "Nobody") == []
```

- [ ] **Step 2: Run to verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_pairs.py -q`
Expected: FAIL — `ModuleNotFoundError: gbl_pairs`

- [ ] **Step 3: Implement**

```python
# gbl_pairs.py
"""Spotify export -> familiarity ranking -> candidate pairs for GBL-AM1.

Spec §3: endpoints come from the owner's familiarity; the export path is a CLI
argument and the raw export NEVER enters the repo. Follow.json holds followed
users, not artists (spec §3 correction), so the sources are the streaming
history and YourLibrary.json.

Output is a PROPOSAL. The owner approves or amends; the approved list becomes
GBL-AM1 in the spec's §8 plus the committed gbl_pairs_approved.json. Nothing
downstream reads the proposal.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gbl_common import in_dir, use_cre

PLAY_MS = 30_000          # below this a row is a skip, not a listen
PROPOSED_PAIRS = 12       # owner trims/edits to the spec's 8


def rank_familiarity(history: list[dict], library: dict) -> list[dict]:
    agg: dict[str, dict] = {}
    for row in history:
        name = row["artistName"]
        a = agg.setdefault(name, {"name": name, "ms_played": 0, "plays": 0,
                                  "in_library": False})
        a["ms_played"] += int(row["msPlayed"])
        if int(row["msPlayed"]) >= PLAY_MS:
            a["plays"] += 1
    for t in library.get("tracks", []):
        a = agg.setdefault(t["artist"], {"name": t["artist"], "ms_played": 0,
                                         "plays": 0, "in_library": False})
        a["in_library"] = True
    return sorted(agg.values(), key=lambda a: -a["ms_played"])


def resolve_in(store, name: str) -> list[int]:
    use_cre()
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "api" / "src"))
    from artistpath_api.search import normalise

    q = normalise(name)
    return [i for i, n in enumerate(store.names) if normalise(n) == q]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--export", required=True,
                    help='path to the "Spotify Account Data" directory (stays outside the repo)')
    ap.add_argument("--top", type=int, default=150)
    args = ap.parse_args()
    export = Path(args.export)

    history = json.loads(
        (export / "StreamingHistory_music_0.json").read_text(encoding="utf-8"))
    library = json.loads((export / "YourLibrary.json").read_text(encoding="utf-8"))
    ranked = rank_familiarity(history, library)[: args.top]

    use_cre()
    from cre_common import load_adopted
    from cre_gates import load_cell

    v0 = load_adopted()
    _, g = load_cell("B-S1")

    rows = []
    for r in ranked:
        in_v0 = resolve_in(v0, r["name"])
        in_g = resolve_in(g, r["name"])
        rows.append({
            **r,
            "v0_nodes": [{"mbid": v0.mbids[i]} for i in in_v0],
            "g_nodes": [{"mbid": g.mbids[i]} for i in in_g],
            "status": ("ok" if len(in_v0) == 1 and len(in_g) == 1
                       and v0.mbids[in_v0[0]] == g.mbids[in_g[0]]
                       else "ambiguous" if in_v0 and in_g
                       else "missing"),
        })
    usable = [r for r in rows if r["status"] == "ok"]

    # Draft pairs: walk the usable list top-down two at a time so every pair
    # joins two artists the owner demonstrably knows, and adjacent familiarity
    # keeps each pair judgeable end to end (REQ-41). The owner reshuffles freely.
    pairs = [[usable[i]["name"], usable[i + 1]["name"]]
             for i in range(0, min(2 * PROPOSED_PAIRS, len(usable) - 1), 2)]

    in_dir("gbl_pair_candidates.json").write_text(json.dumps({
        "usable": usable, "ambiguous": [r for r in rows if r["status"] == "ambiguous"],
        "missing": [r["name"] for r in rows if r["status"] == "missing"],
        "draft_pairs": pairs,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = ["# GBL pair proposal — approve, strike, or swap; 8 pairs survive\n",
             "| # | A | B | your minutes (A/B) |", "|---|---|---|---|"]
    mins = {r["name"]: round(r["ms_played"] / 60_000) for r in usable}
    for i, (a, b) in enumerate(pairs, 1):
        lines.append(f"| {i} | {a} | {b} | {mins[a]}/{mins[b]} |")
    lines.append("\nArtists you listen to that are missing from one of the two maps "
                 "(cannot be endpoints): " + ", ".join(
                     r["name"] for r in rows if r["status"] == "missing") or "none")
    in_dir("gbl_pair_proposal.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"{len(usable)} usable artists, {len(pairs)} draft pairs; "
          f"wrote gbl_pair_candidates.json + gbl_pair_proposal.md", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: PASS

- [ ] **Step 5: Run against the real export** (this machine has both artifacts; ~1 min)

Run (from `builder/`):
`UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --extra dev python analysis/2026-08-04-gentle-arm-blind-listen/gbl_pairs.py --export "C:/Users/charl/Downloads/my_spotify_data/Spotify Account Data"`
Expected: prints a usable-artist count and writes both output files. Sanity: open
`gbl_pair_proposal.md` and confirm it lists real artist names with minutes.

- [ ] **Step 6: Commit** (the derived candidates are committed; the raw export is not)

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen
git commit -m "GBL- pairs: familiarity ranking from the Spotify export, feasibility in both graphs"
```

---

### Task 3: OWNER GATE — approve the pairs, commit `GBL-AM1`

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_pairs_approved.json`
- Modify: `docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md` (§8)

**This task is a STOP.** Present `gbl_pair_proposal.md` to the owner. Do not proceed to
Task 4's real-data run until he has approved exactly 8 pairs (he may swap in manual
picks; re-run the Task 2 feasibility check on any new name by adding it to the proposal
inputs and re-running the CLI).

- [ ] **Step 1:** Owner approves 8 pairs (his column: they spend his ear).
- [ ] **Step 2:** Write `gbl_pairs_approved.json`:

```json
{
  "pairs": [
    {"a": {"name": "<approved>", "mbid": "<from gbl_pair_candidates.json>"},
     "b": {"name": "<approved>", "mbid": "<from gbl_pair_candidates.json>"}}
  ]
}
```

(8 entries; every mbid copied from `gbl_pair_candidates.json`, never typed by hand.)

- [ ] **Step 3:** Append `GBL-AM1` to the spec's §8: the 8 pairs by name and MBID, the
  file's sha256 (`sha256sum gbl_pairs_approved.json`), and the sentence "Approved by the
  owner on <date>; no journey existed at the time."
- [ ] **Step 4: Commit**

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen/gbl_pairs_approved.json ../docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md
git commit -m "GBL-AM1: the owner-approved eight pairs, committed before any journey exists"
```

---

### Task 4: `gbl_generate.py` — ladders, gates, sealed + page outputs

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_generate.py`
- Test: `builder/analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_generate.py`

**Interfaces:**
- Consumes: `cre_common` (`Ruler`, `RAMPS`, `MAX_DEPTH`, `load_adopted`),
  `cre_gates.load_cell`, `cre_ladder.walk_journey` / `victim_key` / `assert_cost_decomposition`,
  `cre_sweep.ladder_excludes` / `config_for`, `cre_mirror.MirrorContext` / `SweepConfig`,
  frozen `artistpath_api.pathfinding.find_journey` + `ApiConfig`,
  frozen `artistpath_api.evaluation.path_metrics` / `top_degree_node_set`,
  `gbl_pairs_approved.json` (Task 3).
- Produces:
  - `shuffle_tokens(pairs: list[str], rng) -> dict[str, dict[str, str]]` — per pair key,
    `{"L": "V0"|"G", "R": the other}`.
  - `page_row(store, path: list[int]) -> dict` — `{"artists": [{"mbid", "name"}...]}` for
    the **full path including endpoints**.
  - `hidden_metrics(store, ruler, top_set, path) -> dict` — keys `fame_pctl_interior`
    (list, `None` for unmeasured), `payload` (interior count minus top-set members),
    `top1pct_degree_frac`, `length` (from frozen `path_metrics`).
  - CLI writing `gbl_page_data.json` (repo, token-labeled) and sealed
    `gbl_sealed.json` (mapping + arm-labeled journeys + hidden metrics).
  - Gate failures are `SystemExit`, never warnings.

**Gates run inside generation, all hard (spec §6):**
1. **Artifact identity:** `load_adopted()` self-asserts V0's sha; for G, hash
   `builder/scratch/cre-cells/B-S1.bin` and assert it equals the `"sha256"` field of
   `B-S1.bin.json` (idempotent if `load_cell` already checks).
2. **V0 mirror check (this listen's own instrument check, on the adopted substrate):**
   at every presented depth of every pair, the real
   `find_journey(store, s, t, excludes, ApiConfig())` must return the mirror ladder's
   exact path and kind. (`CRE-G1(a)` proved this on `E-S0`; this re-proves it on the
   graph V0 actually serves.)
3. **G ramp decomposition:** `assert_cost_decomposition` at k = 1 and k = 10 per pair
   (the `CRE-G2(b)` form, on the listen's own journeys).
4. **Differential check (§6):** at least one pair differs across arms at some presented
   depth — else the page is serving one artifact against itself.
5. **Run-state precondition:** every pair reaches `termination == "completed"` with all
   of `DEPTHS` walked and feasible on both arms — else `SystemExit` naming the pairs
   (the owner swaps pairs pre-listen via a further amendment; no read exists yet).

- [ ] **Step 1: Write the failing tests** (pure parts — token shuffle, page row, seal
  separation; the gates are exercised by the real run in Step 5)

```python
# test_gbl_generate.py
import json
import random

from gbl_generate import hidden_metrics, page_row, shuffle_tokens


class FakeStore:
    names = ["A", "B", "C", "D"]
    mbids = ["ma", "mb", "mc", "md"]
    pop_raw = [0.9, 0.5, 0.4, 0.2]


class FakeRuler:
    def pctl_of(self, mbid):
        return {"ma": 0.99, "mb": 0.60, "mc": None, "md": 0.10}[mbid]


def test_shuffle_tokens_covers_both_assignments_and_is_per_pair():
    rng = random.Random(7)
    m = shuffle_tokens([f"p{i}" for i in range(64)], rng)
    assert all(set(v.values()) == {"V0", "G"} for v in m.values())
    assert {v["L"] for v in m.values()} == {"V0", "G"}  # both orders occur


def test_page_row_carries_names_and_mbids_only():
    row = page_row(FakeStore(), [0, 1, 3])
    assert row == {"artists": [{"mbid": "ma", "name": "A"},
                               {"mbid": "mb", "name": "B"},
                               {"mbid": "md", "name": "D"}]}


def test_hidden_metrics_payload_and_censoring(monkeypatch):
    import gbl_generate as gg

    class FakePM:
        top1pct_degree_frac = 0.5
        length = 4

    monkeypatch.setattr(gg, "_path_metrics", lambda store, path, top: FakePM())
    m = hidden_metrics(FakeStore(), FakeRuler(), top_set={1}, path=[0, 1, 2, 3])
    assert m["fame_pctl_interior"] == [0.60, None]   # interiors only, None kept
    assert m["payload"] == 1                          # 2 interiors - 1 in top set
    assert m["top1pct_degree_frac"] == 0.5
    assert m["length"] == 4


def test_page_data_never_contains_arm_identifiers():
    # The invariant the whole blind rests on, tested at the JSON level.
    from gbl_generate import assert_page_data_clean
    clean = {"pairs": [{"key": "x|y", "rows": [
        {"depth": 0, "L": {"artists": []}, "R": {"artists": []}}]}]}
    assert_page_data_clean(clean)  # no raise
    for poison in ("V0", "B-S1", "ramp", "tiebreakfix", "candidate"):
        dirty = json.loads(json.dumps(clean))
        dirty["pairs"][0]["note"] = poison
        try:
            assert_page_data_clean(dirty)
            assert False, poison
        except SystemExit:
            pass
```

- [ ] **Step 2: Run to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_generate.py -q`
Expected: FAIL — `ModuleNotFoundError: gbl_generate`

- [ ] **Step 3: Implement**

```python
# gbl_generate.py
"""GBL- journey generation: both arms, gated, sealed/page outputs split.

Spec §2: V0 = adopted production graph + production defaults; G = B-S1 + the
gentle ramp (RAMPS["P1a"], cited). Both arms walk the CRE ladder (the measured
object). Arm identity is written ONLY to the sealed file.
"""
from __future__ import annotations

import hashlib
import json
import random
import sys

from gbl_common import ARMS, DEPTHS, ROOT, TOKENS, in_dir, sealed_path, use_cre

use_cre()
from cre_common import RAMPS, Ruler, load_adopted            # noqa: E402
from cre_gates import load_cell                              # noqa: E402
from cre_ladder import assert_cost_decomposition, victim_key, walk_journey  # noqa: E402
from cre_mirror import MirrorContext                         # noqa: E402
from cre_sweep import config_for, ladder_excludes            # noqa: E402

sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.config import ApiConfig                  # noqa: E402
from artistpath_api.evaluation import path_metrics as _path_metrics  # noqa: E402
from artistpath_api.evaluation import top_degree_node_set    # noqa: E402
from artistpath_api.pathfinding import find_journey          # noqa: E402

G2B_DEPTHS = (1, 10)   # the CRE-G2(b) depths, reused
FORBIDDEN_PAGE_TOKENS = ("V0", '"G"', "B-S1", "ramp", "tiebreakfix",
                         "candidate", "arm", "P1a")


def shuffle_tokens(pair_keys: list[str], rng) -> dict[str, dict[str, str]]:
    out = {}
    for k in pair_keys:
        arms = list(ARMS)
        rng.shuffle(arms)
        out[k] = dict(zip(TOKENS, arms))
    return out


def page_row(store, path: list[int]) -> dict:
    return {"artists": [{"mbid": store.mbids[v], "name": store.names[v]}
                        for v in path]}


def hidden_metrics(store, ruler, top_set, path) -> dict:
    interior = path[1:-1]
    fame = [ruler.pctl_of(store.mbids[v]) for v in interior]
    pm = _path_metrics(store, path, top_set)
    return {
        "fame_pctl_interior": fame,
        "payload": sum(1 for v in interior if v not in top_set),
        "top1pct_degree_frac": pm.top1pct_degree_frac,
        "length": pm.length,
    }


def assert_page_data_clean(doc: dict) -> None:
    blob = json.dumps(doc, ensure_ascii=False)
    for tok in FORBIDDEN_PAGE_TOKENS:
        if tok in blob:
            raise SystemExit(f"page data leaks arm identity: {tok!r} found")


def _arm_store(arm: str):
    if arm == "V0":
        store = load_adopted()
    else:
        manifest, store = load_cell("B-S1")
        payload = (ROOT / "builder/scratch/cre-cells/B-S1.bin").read_bytes()
        got = hashlib.sha256(payload).hexdigest()
        if got != manifest["sha256"]:
            raise SystemExit(f"WRONG ARTIFACT for G: {got} != manifest")
    return store


def main() -> int:
    approved = json.loads(in_dir("gbl_pairs_approved.json").read_text("utf-8"))
    pairs = [(p["a"], p["b"]) for p in approved["pairs"]]
    if len(pairs) != 8:
        raise SystemExit(f"spec §3 requires 8 pairs, got {len(pairs)}")

    ruler = Ruler()
    sealed = {"arms": {}, "mapping": None, "pairs": {}}
    page = {"pairs": []}

    per_arm: dict[str, dict] = {}
    for arm in ARMS:
        store = _arm_store(arm)
        measured, device = ruler.arrays(store)
        ctx = MirrorContext.build(store, device)
        cfg = config_for("P0" if arm == "V0" else "P1a")
        top_set = top_degree_node_set(store, 0.01)
        api_cfg = ApiConfig()
        key = victim_key(measured, store.pop_raw, store.mbids)
        rows: dict[str, dict] = {}
        for a, b in pairs:
            s, t = store.id_by_mbid[a["mbid"]], store.id_by_mbid[b["mbid"]]
            ladder = walk_journey(store, s, t, cfg, ctx, measured,
                                  store.pop_raw, store.mbids)
            excl = ladder_excludes(ladder, key)
            bad = [d for d in DEPTHS
                   if d >= len(excl) or ladder[d][0] is None]
            if bad:
                raise SystemExit(
                    f"pair {a['name']}|{b['name']} does not reach depths {bad} "
                    f"on arm {arm}: swap the pair (spec §5 run state) before "
                    f"any listen. No read exists yet.")
            depth_rows = {}
            for d in DEPTHS:
                path, kind = ladder[d]
                if arm == "V0":
                    real = find_journey(store, s, t, excl[d], api_cfg)
                    if real is None or list(real[0]) != list(path) or real[1] != kind:
                        raise SystemExit(
                            f"V0 mirror check FAILED at depth {d} for "
                            f"{a['name']}|{b['name']}: mirror and production "
                            f"find_journey disagree")
                else:
                    if d in G2B_DEPTHS:
                        assert_cost_decomposition(
                            store, ctx, cfg, excl[d], path,
                            masked_edge=(s, t) if kind == "forced" else None)
                depth_rows[str(d)] = {
                    "path_mbids": [store.mbids[v] for v in path],
                    "page": page_row(store, path),
                    "metrics": hidden_metrics(store, ruler, top_set, path),
                    "kind": kind,
                }
            rows[f"{a['mbid']}|{b['mbid']}"] = depth_rows
        per_arm[arm] = rows
        sealed["arms"][arm] = {"pairs": rows}

    # Differential check (spec §6): the two arms must not be one artifact twice.
    diff = any(
        per_arm["V0"][k][str(d)]["path_mbids"] != per_arm["G"][k][str(d)]["path_mbids"]
        for k in per_arm["V0"] for d in DEPTHS)
    if not diff:
        raise SystemExit("differential check FAILED: arms identical everywhere")

    rng = random.SystemRandom()
    keys = list(per_arm["V0"].keys())
    mapping = shuffle_tokens(keys, rng)
    sealed["mapping"] = mapping

    for (a, b), k in zip(pairs, keys):
        rows = []
        for d in DEPTHS:
            rows.append({
                "depth": d,
                "L": per_arm[mapping[k]["L"]][k][str(d)]["page"],
                "R": per_arm[mapping[k]["R"]][k][str(d)]["page"],
            })
        page["pairs"].append({"key": k, "a": a["name"], "b": b["name"],
                              "rows": rows})

    assert_page_data_clean(page)
    sealed_path("gbl_sealed.json").write_text(
        json.dumps(sealed, indent=2, ensure_ascii=False), encoding="utf-8")
    in_dir("gbl_page_data.json").write_text(
        json.dumps(page, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"generated {len(keys)} pairs x {len(DEPTHS)} depths x 2 arms; "
          f"sealed mapping written; page data clean", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: PASS

- [ ] **Step 5: Commit** (code only — the real-data run is the runner session's, per the
  seam: this plan's sessions must not see G's journeys)

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen
git commit -m "GBL- generation: both arms on the CRE ladder, gated, sealed/page split"
```

---

### Task 5: `gbl_clips.py` — name-based clip resolution, both arms alike

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_clips.py`
- Test: `builder/analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_clips.py`

**Interfaces:**
- Consumes: `gbl_page_data.json` (Task 4); frozen `artistpath_api.clips.ClipResolver` /
  `InMemoryClipCache`, frozen `ApiConfig`.
- Produces: sealed-dir `gbl_clips.json` — `{mbid: {"preview_url", "title", "cover_url"} | null}`.
  Runtime file (preview URLs are signed and expire — `Clip`'s own docstring), regenerated
  on listen day, never committed.

**Non-differential by construction:** every artist resolves via
`resolve(mbid, name, deezer_artist_id="")` — the name-based path — for **both** arms, so
clip quality cannot become an arm tell. (V0's artifact predates `deezer_ids` anyway;
forcing `""` makes the arms symmetric regardless of what B-S1 carries.) `BYP-13` is
live and shared; the page instructs the owner to ignore clip failures unless they
differ by arm (spec §4).

- [ ] **Step 1: Write the failing test** (injected fake fetcher — the resolver is
  injectable by design; no network in tests)

```python
# test_gbl_clips.py
import asyncio

from gbl_clips import resolve_all


def fake_fetch(responses):
    async def fetch(url, params):
        for frag, body in responses.items():
            if frag in url:
                return body
        return {}
    return fetch


DEEZER_HIT = {"data": [{"artist": {"name": "Songs: Ohia"},
                        "title": "Farewell Transmission",
                        "preview": "https://cdn.example/p.mp3",
                        "album": {"cover_medium": "https://cdn.example/c.jpg"},
                        "id": 1}]}


def test_resolve_all_returns_clip_fields_and_none_on_miss():
    out = asyncio.run(resolve_all(
        [("m1", "Songs: Ohia"), ("m2", "Nobody Anywhere")],
        fetch_json=fake_fetch({"deezer.com": DEEZER_HIT}),
    ))
    assert out["m1"]["preview_url"] == "https://cdn.example/p.mp3"
    assert out["m2"] is None
```

(If the fake's response shape doesn't satisfy the real resolver — it may require more
fields — read `ClipResolver.resolve`'s body in `api/src/artistpath_api/clips.py` and
extend `DEEZER_HIT` until the test exercises the genuine parse path. Do not stub the
resolver itself; the point is that the real code runs.)

- [ ] **Step 2: Run to verify it fails**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_clips.py -q`
Expected: FAIL — `ModuleNotFoundError: gbl_clips`

- [ ] **Step 3: Implement**

```python
# gbl_clips.py
"""Resolve one preview clip per presented artist, name-based for BOTH arms.

Output goes to the sealed dir as a runtime file: preview URLs are signed and
expire, so this is re-run on listen day, minutes before serving.
"""
from __future__ import annotations

import asyncio
import json
import sys
import urllib.parse
import urllib.request

from gbl_common import ROOT, in_dir, sealed_path

sys.path.insert(0, str(ROOT / "api" / "src"))
from artistpath_api.clips import ClipResolver, InMemoryClipCache  # noqa: E402
from artistpath_api.config import ApiConfig                        # noqa: E402

CONCURRENCY = 2
DELAY_S = 0.15   # politeness; ~500 artists in 2-3 minutes


def _urllib_fetch(url: str, params: dict) -> dict:
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{url}?{q}" if q else url,
                                 headers={"User-Agent": "artistpath-gbl/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        if resp.status >= 400:
            raise RuntimeError(f"HTTP {resp.status}")
        return json.loads(resp.read().decode("utf-8"))


async def default_fetch(url: str, params: dict) -> dict:
    return await asyncio.to_thread(_urllib_fetch, url, params)


async def resolve_all(artists: list[tuple[str, str]], fetch_json=default_fetch) -> dict:
    resolver = ClipResolver(cfg=ApiConfig(), cache=InMemoryClipCache(),
                            fetch_json=fetch_json)
    sem = asyncio.Semaphore(CONCURRENCY)
    out: dict[str, dict | None] = {}

    async def one(mbid: str, name: str) -> None:
        async with sem:
            try:
                clip = await resolver.resolve(mbid, name, deezer_artist_id="")
            except Exception:
                clip = None   # a clip is decorative; a miss is a silent card
            out[mbid] = (None if clip is None else
                         {"preview_url": clip.preview_url, "title": clip.title,
                          "cover_url": clip.cover_url})
            await asyncio.sleep(DELAY_S)

    await asyncio.gather(*(one(m, n) for m, n in artists))
    return out


def main() -> int:
    page = json.loads(in_dir("gbl_page_data.json").read_text("utf-8"))
    seen: dict[str, str] = {}
    for pair in page["pairs"]:
        for row in pair["rows"]:
            for side in ("L", "R"):
                for a in row[side]["artists"]:
                    seen[a["mbid"]] = a["name"]
    out = asyncio.run(resolve_all(sorted(seen.items())))
    sealed_path("gbl_clips.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    hits = sum(1 for v in out.values() if v)
    print(f"resolved {hits}/{len(out)} artists", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen
git commit -m "GBL- clips: name-based resolution through the app's own resolver, arm-symmetric"
```

---

### Task 6: the page — `gbl_page.html` + `gbl_page.py`

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_page.html`
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_page.py`
- Test: `builder/analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_page.py`

**Interfaces:**
- Consumes: `gbl_page_data.json`, sealed `gbl_clips.json`.
- Produces: `gbl_verdicts.json` (in the analysis dir; committed after the listen) with
  shape `{"rows": {"<pairkey>": {"0": "L"|"R"|"none", "10": ..., "20": ...}},
  "claims": {"<pairkey>": {"q1": "L"|"R"|"none", "q2": "L"|"R"|"none",
  "q2_collapse": str, "notes": str}}}`.
  Server endpoints: `GET /` (page), `POST /verdict` (`{"pair","depth","pick"}`),
  `POST /claims` (`{"pair","q1","q2","q2_collapse","notes"}`), `GET /status`
  (`{"complete": bool, "missing": [...]}`, complete = 8×3 rows + 8 claim sets).

- [ ] **Step 1: Write the failing tests**

```python
# test_gbl_page.py
import json
import threading
import urllib.request

import gbl_page


def _post(port, path, body):
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())


def _get(port, path):
    with urllib.request.urlopen(f"http://127.0.0.1:{port}{path}") as r:
        return r.status, r.read().decode("utf-8")


def _serve(tmp_path):
    page_data = {"pairs": [{"key": "ma|mb", "a": "A", "b": "B", "rows": [
        {"depth": d, "L": {"artists": []}, "R": {"artists": []}}
        for d in (0, 10, 20)]}]}
    clips = {}
    srv = gbl_page.make_server(page_data, clips,
                               verdict_file=tmp_path / "gbl_verdicts.json",
                               port=0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, srv.server_address[1]


def test_verdicts_and_claims_are_persisted_and_status_completes(tmp_path):
    srv, port = _serve(tmp_path)
    try:
        status, body = _get(port, "/")
        assert status == 200 and "GBL" in body
        assert "no Spotify" in body            # the WGLL-bound banner is served

        assert _get(port, "/status")[1].startswith('{"complete": false')
        for d in ("0", "10", "20"):
            _post(port, "/verdict", {"pair": "ma|mb", "depth": d, "pick": "L"})
        _post(port, "/claims", {"pair": "ma|mb", "q1": "L", "q2": "none",
                                "q2_collapse": "", "notes": "n"})
        st = json.loads(_get(port, "/status")[1])
        assert st["complete"] is True

        saved = json.loads((tmp_path / "gbl_verdicts.json").read_text("utf-8"))
        assert saved["rows"]["ma|mb"]["10"] == "L"
        assert saved["claims"]["ma|mb"]["notes"] == "n"
    finally:
        srv.shutdown()


def test_verdict_rejects_unknown_pair_and_bad_pick(tmp_path):
    srv, port = _serve(tmp_path)
    try:
        for bad in ({"pair": "zz", "depth": "0", "pick": "L"},
                    {"pair": "ma|mb", "depth": "0", "pick": "V0"},
                    {"pair": "ma|mb", "depth": "5", "pick": "L"}):
            try:
                _post(port, "/verdict", bad)
                assert False, bad
            except urllib.error.HTTPError as e:
                assert e.code == 400
    finally:
        srv.shutdown()
```

(add `import urllib.error` at the top of the test file)

- [ ] **Step 2: Run to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_page.py -q`
Expected: FAIL — `ModuleNotFoundError: gbl_page`

- [ ] **Step 3: Implement the server**

```python
# gbl_page.py
"""Serves the side-by-side page on localhost and writes verdicts to disk --
the owner's §3.9 improvement request. Stdlib only; throwaway."""
from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from gbl_common import DEPTHS, TOKENS, in_dir, sealed_path

PICKS = (*TOKENS, "none")


def make_server(page_data: dict, clips: dict, verdict_file: Path, port: int = 8765):
    html = (Path(__file__).parent / "gbl_page.html").read_text(encoding="utf-8")
    html = html.replace("__GBL_DATA__", json.dumps(
        {"pairs": page_data["pairs"], "clips": clips}, ensure_ascii=False))
    valid_pairs = {p["key"] for p in page_data["pairs"]}
    state = {"rows": {}, "claims": {}}
    if verdict_file.exists():   # resuming a split sitting keeps prior verdicts
        state = json.loads(verdict_file.read_text("utf-8"))

    def save():
        tmp = verdict_file.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=2, ensure_ascii=False),
                       encoding="utf-8")
        tmp.replace(verdict_file)

    def missing():
        out = []
        for k in valid_pairs:
            for d in DEPTHS:
                if state["rows"].get(k, {}).get(str(d)) is None:
                    out.append(f"{k}:d{d}")
            if k not in state["claims"]:
                out.append(f"{k}:claims")
        return out

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):   # quiet
            pass

        def _send(self, code, body, ctype="application/json"):
            data = body.encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", f"{ctype}; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                self._send(200, html, "text/html")
            elif self.path == "/status":
                m = missing()
                self._send(200, json.dumps(
                    {"complete": not m, "missing": m}))
            else:
                self._send(404, "{}")

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(n))
                pair = body["pair"]
                if pair not in valid_pairs:
                    raise ValueError("unknown pair")
                if self.path == "/verdict":
                    if (str(body["depth"]) not in {str(d) for d in DEPTHS}
                            or body["pick"] not in PICKS):
                        raise ValueError("bad row")
                    state["rows"].setdefault(pair, {})[str(body["depth"])] = body["pick"]
                elif self.path == "/claims":
                    if body["q1"] not in PICKS or body["q2"] not in PICKS:
                        raise ValueError("bad claims")
                    state["claims"][pair] = {
                        "q1": body["q1"], "q2": body["q2"],
                        "q2_collapse": str(body.get("q2_collapse", "")),
                        "notes": str(body.get("notes", ""))}
                else:
                    self._send(404, "{}")
                    return
                save()
                self._send(200, '{"ok": true}')
            except (KeyError, ValueError, json.JSONDecodeError) as e:
                self._send(400, json.dumps({"error": str(e)}))

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main() -> int:
    page_data = json.loads(in_dir("gbl_page_data.json").read_text("utf-8"))
    clips = json.loads(sealed_path("gbl_clips.json").read_text("utf-8"))
    srv = make_server(page_data, clips, verdict_file=in_dir("gbl_verdicts.json"))
    print(f"serving http://127.0.0.1:{srv.server_address[1]}/ -- Ctrl+C to stop",
          flush=True)
    srv.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Write `gbl_page.html`** (vanilla, no external assets; the essentials)

```html
<!-- gbl_page.html -->
<!doctype html>
<meta charset="utf-8">
<title>GBL blind listen</title>
<style>
  body { font-family: system-ui, sans-serif; margin: 1.5rem; max-width: 1100px; }
  .banner { background: #fff3cd; border: 1px solid #ccc; padding: .6rem 1rem; }
  .pair { border-top: 3px solid #444; margin-top: 2rem; padding-top: 1rem; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 1rem 0; }
  .side { border: 1px solid #ccc; padding: .6rem; }
  .card { display: flex; gap: .5rem; align-items: center; margin: .25rem 0; }
  audio { height: 28px; }
  textarea { width: 100%; }
  .done { color: #060; }
</style>
<div class="banner"><b>Blind listen in progress.</b> Judge the artist sequences;
ignore clip failures unless they differ by side. <b>No Spotify or
monthly-listener lookups until every verdict is saved.</b> Depth rows are the
same pair after 0, 10 and 20 presses of “I know them”; listen to each side’s
depths in order.</div>
<div id="app"></div>
<script>
const DATA = __GBL_DATA__;
const PICKS = ["L", "R", "none"];
const app = document.getElementById("app");
for (const pair of DATA.pairs) {
  const div = document.createElement("div");
  div.className = "pair";
  div.innerHTML = `<h2>${pair.a} → ${pair.b}</h2>`;
  for (const row of pair.rows) {
    const r = document.createElement("div");
    r.innerHTML = `<h3>after ${row.depth} presses</h3>`;
    const grid = document.createElement("div");
    grid.className = "row";
    for (const side of ["L", "R"]) {
      const s = document.createElement("div");
      s.className = "side";
      s.innerHTML = `<h4>${side}</h4>` + row[side].artists.map(a => {
        const c = DATA.clips[a.mbid];
        return `<div class="card"><span>${a.name}</span>` +
          (c && c.preview_url
            ? `<audio controls preload="none" src="${c.preview_url}"></audio>`
            : `<em>(no clip)</em>`) + `</div>`;
      }).join("");
      grid.appendChild(s);
    }
    r.appendChild(grid);
    const picks = document.createElement("div");
    picks.innerHTML = PICKS.map(p =>
      `<label><input type="radio" name="pick-${pair.key}-${row.depth}"
        value="${p}"> ${p === "none" ? "no preference" : p}</label> `).join("") +
      ` <button>save row</button> <span class="saved"></span>`;
    picks.querySelector("button").onclick = async () => {
      const sel = picks.querySelector("input:checked");
      if (!sel) return alert("pick a side or no preference first");
      await post("/verdict", { pair: pair.key, depth: String(row.depth),
                               pick: sel.value });
      picks.querySelector(".saved").textContent = "saved ✓";
      picks.querySelector(".saved").className = "saved done";
    };
    r.appendChild(picks);
    div.appendChild(r);
  }
  const claims = document.createElement("div");
  claims.innerHTML = `
    <h3>pair verdict</h3>
    <p><b>Q1 (novelty):</b> As the presses accumulate, which side, if either,
      delivers more artists new to you?
      ${PICKS.map(p => `<label><input type="radio" name="q1-${pair.key}"
        value="${p}"> ${p}</label>`).join(" ")}</p>
    <p><b>Q2 (coherence):</b> Which side, if either, holds together better as a
      journey — each step a sensible next listen?
      ${PICKS.map(p => `<label><input type="radio" name="q2-${pair.key}"
        value="${p}"> ${p}</label>`).join(" ")}</p>
    <p>Did either side collapse into a random walk into obscurity?
      <input size="60" class="collapse"></p>
    <p>Notes (what read as smooth vs jarring — these become the record):<br>
      <textarea rows="4"></textarea></p>
    <button>save pair verdict</button> <span class="saved"></span>`;
  claims.querySelector("button").onclick = async () => {
    const q1 = claims.querySelector(`input[name="q1-${pair.key}"]:checked`);
    const q2 = claims.querySelector(`input[name="q2-${pair.key}"]:checked`);
    if (!q1 || !q2) return alert("answer Q1 and Q2 first");
    await post("/claims", { pair: pair.key, q1: q1.value, q2: q2.value,
      q2_collapse: claims.querySelector(".collapse").value,
      notes: claims.querySelector("textarea").value });
    claims.querySelector(".saved").textContent = "saved ✓";
    claims.querySelector(".saved").className = "saved done";
  };
  div.appendChild(claims);
  app.appendChild(div);
}
async function post(path, body) {
  const r = await fetch(path, { method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body) });
  if (!r.ok) alert("save failed: " + await r.text());
}
</script>
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen
git commit -m "GBL- page: side-by-side blind page, verdicts written to disk (the 3.9 request)"
```

---

### Task 7: `gbl_unblind.py` — run-state check, tally, ear-tracking table

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/gbl_unblind.py`
- Test: `builder/analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_unblind.py`

**Interfaces:**
- Consumes: `gbl_verdicts.json`, sealed `gbl_sealed.json`.
- Produces: `tally(rows, mapping) -> dict` (pure) and `gbl_result.json` — the mechanical
  read only; the four-part write-up is a later session's job, not this script's.

**The spec's §5 sentences are quoted, not paraphrased.** Deep rows are depths 10 and 20;
d0 is excluded; margin ≥ 5 of 16 fires; the three branch sentences come from the spec's
table verbatim.

- [ ] **Step 1: Write the failing tests** (the spec's own worked examples are the cases)

```python
# test_gbl_unblind.py
import pytest

from gbl_unblind import RunIncomplete, tally

MAPPING = {f"p{i}": {"L": ("V0" if i % 2 else "G"),
                     "R": ("G" if i % 2 else "V0")} for i in range(8)}


def rows_with(g_wins: int, v_wins: int):
    """Build 8 pairs x d10/d20 rows: first g_wins deep rows pick G's token,
    next v_wins pick V0's token, remainder 'none'. All d0 rows pick V0's token
    to prove d0 is excluded."""
    picks = (["G"] * g_wins + ["V0"] * v_wins + ["none"] * 16)[:16]
    rows, i = {}, 0
    for k, m in MAPPING.items():
        tok = {v: t for t, v in m.items()}
        rows[k] = {"0": tok["V0"]}
        for d in ("10", "20"):
            p = picks[i]; i += 1
            rows[k][d] = tok[p] if p != "none" else "none"
    return rows


def test_spec_worked_example_9_4_fires_for_g():
    out = tally(rows_with(9, 4), MAPPING)
    assert out["deep_rows"] == 16
    assert out["clear_picks"] == {"G": 9, "V0": 4}
    assert out["margin"] == 5
    assert out["branch"] == "G_better"


def test_spec_worked_example_10_6_is_the_null():
    out = tally(rows_with(10, 6), MAPPING)
    assert out["margin"] == 4
    assert out["branch"] == "no_detectable_difference"


def test_v0_side_fires_symmetrically():
    assert tally(rows_with(2, 8), MAPPING)["branch"] == "V0_better"


def test_d0_rows_never_enter_the_tally():
    out = tally(rows_with(0, 0), MAPPING)
    assert out["clear_picks"] == {"G": 0, "V0": 0}   # despite 8 d0 picks


def test_incomplete_run_refuses_a_read():
    rows = rows_with(9, 4)
    del rows["p3"]["20"]
    with pytest.raises(RunIncomplete):
        tally(rows, MAPPING)
```

- [ ] **Step 2: Run to verify they fail**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen/test_gbl_unblind.py -q`
Expected: FAIL — `ModuleNotFoundError: gbl_unblind`

- [ ] **Step 3: Implement**

```python
# gbl_unblind.py
"""Unblind AFTER all verdicts are on disk: the §5 tally and the §7
ear-tracking table. Mechanical only -- the write-up is a session's job."""
from __future__ import annotations

import json
import statistics
import sys

from gbl_common import DEPTHS, in_dir, sealed_path

DEEP = ("10", "20")
MARGIN = 5           # spec §5: scaled 3-of-10, rounded up
BRANCH_SENTENCES = {  # spec §5, quoted
    "G_better": "The rebuilt app digs, and the journeys still sound like journeys.",
    "V0_better": "Today's app sounds better despite not digging.",
    "no_detectable_difference":
        "My ear cannot tell them apart where the numbers could.",
}


class RunIncomplete(SystemExit):
    pass


def tally(rows: dict, mapping: dict) -> dict:
    missing = [f"{k}:d{d}" for k in mapping for d in map(str, DEPTHS)
               if rows.get(k, {}).get(d) is None]
    if missing:
        raise RunIncomplete(
            f"spec §5 run state unmet -- no read exists. Missing: {missing}")
    picks = {"G": 0, "V0": 0}
    for k, m in mapping.items():
        for d in DEEP:
            p = rows[k][d]
            if p in m:                      # "L"/"R" -> arm; "none" skipped
                picks[m[p]] += 1
    margin = abs(picks["G"] - picks["V0"])
    if margin >= MARGIN:
        branch = "G_better" if picks["G"] > picks["V0"] else "V0_better"
    else:
        branch = "no_detectable_difference"
    d0 = {"G": 0, "V0": 0}
    for k, m in mapping.items():
        p = rows[k]["0"]
        if p in m:
            d0[m[p]] += 1
    return {"deep_rows": len(mapping) * len(DEEP), "clear_picks": picks,
            "margin": margin, "branch": branch,
            "branch_sentence": BRANCH_SENTENCES[branch],
            "d0_anchor_picks_excluded_from_tally": d0}


def ear_tracking(rows: dict, sealed: dict) -> dict:
    """§7: for each deep row with a clear pick, did the picked side also win
    each hidden metric? Fame compares measured interiors only."""
    counts = {"fame_lower": 0, "payload_higher": 0,
              "top1pct_degree_frac_lower": 0, "length_longer": 0, "rows": 0}
    mapping = sealed["mapping"]
    for k, m in mapping.items():
        for d in DEEP:
            p = rows[k][d]
            if p not in m:
                continue
            counts["rows"] += 1
            picked, other = m[p], m[{"L": "R", "R": "L"}[p]]
            a = sealed["arms"][picked]["pairs"][k][d]["metrics"]
            b = sealed["arms"][other]["pairs"][k][d]["metrics"]

            def mean_fame(mm):
                vals = [f for f in mm["fame_pctl_interior"] if f is not None]
                return statistics.mean(vals) if vals else None

            fa, fb = mean_fame(a), mean_fame(b)
            if fa is not None and fb is not None and fa < fb:
                counts["fame_lower"] += 1
            if a["payload"] > b["payload"]:
                counts["payload_higher"] += 1
            if a["top1pct_degree_frac"] < b["top1pct_degree_frac"]:
                counts["top1pct_degree_frac_lower"] += 1
            if a["length"] > b["length"]:
                counts["length_longer"] += 1
    return counts


def main() -> int:
    verdicts = json.loads(in_dir("gbl_verdicts.json").read_text("utf-8"))
    sealed = json.loads(sealed_path("gbl_sealed.json").read_text("utf-8"))
    out = tally(verdicts["rows"], sealed["mapping"])
    out["ear_tracking"] = ear_tracking(verdicts["rows"], sealed)
    out["mapping_unsealed"] = sealed["mapping"]
    out["claims"] = verdicts["claims"]
    in_dir("gbl_result.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"branch: {out['branch']} (margin {out['margin']} of "
          f"{out['deep_rows']} deep rows); wrote gbl_result.json", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q`
Expected: PASS (all tasks' tests)

- [ ] **Step 5: Commit**

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen
git commit -m "GBL- unblind: run-state-gated tally with the spec's margins, ear-tracking table"
```

---

### Task 8: `RUNNER-BRIEF.md`, Snyk scan, PR

**Files:**
- Create: `builder/analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md`

- [ ] **Step 1: Write the brief.** Mechanics only — it must let the runner session act
  without opening any results document. Contents, in order:

```markdown
# GBL runner brief — mechanics only

You are running a blind evaluation. Say nothing to the owner beyond these
mechanics; you are deliberately not told what outcome anyone expects, and you
must not go looking: do NOT read docs/superpowers/findings/, docs/superpowers/NEXT.md,
docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md §1-§2, or any
execution log. This brief is self-contained.

All commands from `builder/`, every uv command prefixed UV_LINK_MODE=copy, and
PYTHONIOENCODING=utf-8 on generation (it prints artist names).

1. Preflight: `git status --short` is clean on branch gentle-arm-blind-listen;
   `UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-08-04-gentle-arm-blind-listen -q` passes.
2. Generate: `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run --extra dev python -u analysis/2026-08-04-gentle-arm-blind-listen/gbl_generate.py`
   - It self-checks artifact hashes, mirror fidelity, the ramp decomposition,
     and that the two sides genuinely differ. Any SystemExit: STOP, report the
     message to the owner verbatim, do not work around it.
   - Do not open .superpowers/gbl/ files. gbl_page_data.json is safe to view.
3. Clips (listen day, just before serving — URLs expire):
   `UV_LINK_MODE=copy uv run --extra dev python -u analysis/2026-08-04-gentle-arm-blind-listen/gbl_clips.py`
4. Smoke test: `UV_LINK_MODE=copy uv run --extra dev python analysis/2026-08-04-gentle-arm-blind-listen/gbl_page.py`,
   open http://127.0.0.1:8765/ yourself: the page renders, at least one clip
   plays, saving a row then restarting the server preserves it (then delete
   gbl_verdicts.json so the owner starts clean). GET /status returns missing rows.
5. Hand the owner exactly this and nothing else:
   "The listen is at http://127.0.0.1:8765/. Work top to bottom; save every
   row and every pair verdict. Sittings can be split; saved rows persist."
6. Wait. When the owner says he is done: GET /status. If not complete, tell him
   which rows are missing and wait. Never summarize, never react to a verdict.
7. Stop the server. Commit gbl_verdicts.json:
   `git add analysis/2026-08-04-gentle-arm-blind-listen/gbl_verdicts.json && git commit -m "GBL- verdicts: the owner's picks and notes, as saved by the page"`
8. Unblind: `UV_LINK_MODE=copy uv run --extra dev python analysis/2026-08-04-gentle-arm-blind-listen/gbl_unblind.py`
   Commit gbl_result.json the same way. Report to the owner only: "the verdicts
   and the mechanical tally are committed; the write-up belongs to a fresh
   session." Then stop.
```

- [ ] **Step 2:** Run `snyk_code_scan` over
  `builder/analysis/2026-08-04-gentle-arm-blind-listen/` (global instruction: new
  first-party Python). Fix any finding using the results context; rescan until clean.
  Record the outcome in the commit message.
- [ ] **Step 3: Commit**

```bash
git add analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md
git commit -m "GBL- runner brief: mechanics-only instructions for the fresh listen session"
```

- [ ] **Step 4:** Open draft PR from `gentle-arm-blind-listen` per closeout D5 (link the
  spec, name the owner gate at Task 3 and the runner seam after Task 8, note that
  `gbl_verdicts.json` / `gbl_result.json` arrive later from the runner session).

---

## Execution order and the two gates

1. Tasks 1–2 (any session) → **Task 3 is an OWNER GATE** (pairs approved, `GBL-AM1`
   committed) → Tasks 4–8.
2. After Task 8: **handoff seam.** The listen is run by a fresh session from
   `RUNNER-BRIEF.md` only. The write-up of `gbl_result.json` is a further fresh
   session's job (same rule the CRE Stage-3 findings followed: the reader of results
   did not run them).

## Self-review record

- **Spec coverage:** §1 decision framing → PR body + brief's silence rules; §2 arms and
  gates → Task 4; §3 pairs → Tasks 2–3 (owner gate), workload depths → Task 4 `DEPTHS`;
  §4 page, frozen Q1/Q2 wording, banner, notes → Task 6 (the HTML carries the spec's
  exact question text); §5 reads/margins/run-state → Task 7 (worked examples are test
  cases); §6 blind protocol → sealed dir (Tasks 1/4), runner brief (Task 8),
  differential check (Task 4 gate 4); §7 hidden metrics + verdicts-to-disk → Tasks 4,
  6, 7. §9 non-goals: no shipped code is touched anywhere.
- **Placeholder scan:** none — every step carries its code or exact command. The one
  deliberate conditional is Task 5's note to extend the fake Deezer response if the real
  parser needs more fields; the instruction says exactly what to do and where to look.
- **Type consistency:** `shuffle_tokens` / `page_row` / `hidden_metrics` /
  `assert_page_data_clean` names match between Task 4 code and tests; `make_server`
  signature matches Task 6 tests; `tally` / `RunIncomplete` match Task 7 tests; sealed
  JSON shape written in Task 4 (`arms.<arm>.pairs.<key>.<depth>.metrics`) is the shape
  Task 7's `ear_tracking` reads; `gbl_verdicts.json` shape written by Task 6 is the
  shape Task 7 consumes.
