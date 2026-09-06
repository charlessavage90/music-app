# `LUX-4` — streaming links and the artist info card: implementation plan

**Role: ACTIVE — the implementation plan for `LUX-4`. UNSTARTED; no task has run.**
Argues from [`specs/2026-09-03-launch-ux-scope.md`](../specs/2026-09-03-launch-ux-scope.md)
§4, **which governs where the two disagree**; executors read both. **Owns no figures.**
**⚠ `L4-T1` stops for an owner decision and blocks every other task.**

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development`
> (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Put Spotify and Apple Music deep links, and a small card of structured MusicBrainz
facts, onto every journey card — carried in the APG1 artifact as additive keys, with search
links as the fallback wherever no id exists.

**Architecture:** One offline extraction pass over the MusicBrainz artist dump produces two
frozen, sha-pinned package-data maps (links, facts), following the `deezer_ids.py` pattern
exactly. The builder writes them as additive APG1 metadata keys; the API reads them with the
same "may be shorter than N" discipline; the frontend renders link buttons and an info card.
**One rebuild carries both features** — that pairing is the point, and splitting it means a
second rebuild.

**Tech Stack:** Python 3.14 / `uv` (builder, api), FastAPI + Pydantic (api), React 19 + Vite +
TypeScript + Tailwind (frontend), Vitest + Playwright (frontend tests), pytest (Python tests).

**Spec:** [`docs/superpowers/specs/2026-09-03-launch-ux-scope.md`](../specs/2026-09-03-launch-ux-scope.md)
§4 (and §5 for `LUX-E2`, `LUX-E3`, `LUX-E5`). **The plan argues from the spec; executors read
both.** Identifiers here are **`L4-T1`–`L4-T11`** (tasks) and **`L4-D1`–`L4-D3`** (decisions
this plan takes), collision-checked across every ref 2026-09-05.

**Gate status:** `LUX-E1` **RAN 2026-09-05 and returned BYTE-IDENTICAL**
([`builder/analysis/2026-09-05-lux-e1-armb/README.md`](../../../builder/analysis/2026-09-05-lux-e1-armb/README.md)).
`LUX-4` is a **metadata change as priced, not a graph adoption**. This plan may proceed.

---

## Global Constraints

Every task's requirements implicitly include this section. Values are copied verbatim from the
spec, from `CLAUDE.md`, or from source.

**Build reproducibility — the constraint the whole plan turns on.**

- **The rebuild MUST pin both drifted inputs.** `--archive-dir` at
  `scratch/grt-archive-algb.pre-cex-snapshot` and the unlistenable payload at
  `src/artistpath_builder/data/unlistenable_drop_algb_20260805.json`. Building without both
  produces a **different population**, which makes this a graph adoption and not this plan.
- **`--algorithm` is always explicit.** `BuilderConfig.algorithm` defaults to ALG-E while the
  adopted map is ALG-B (`CEX-R5`). Pass `CANDIDATE_ALGORITHM`'s literal string.
- **`--cap-strategy trimmed_union` and `--require-fame`**, the values the live manifest records.
- **No network at build time.** `build_from_archive` is offline by a hard rule and a replay
  test injects a fetcher that raises to prove it. Maps are frozen snapshots, never resolved
  during a build.
- **Byte-identical output for identical input** (spec §9). Every ordering decision stays
  explicit: sorted-MBID order, ties on lowest MBID.

**APG1 format — additive keys only.**

- **`FORMAT_VERSION` stays `1`.** Both parsers check it for strict equality; bumping it stops
  every existing artifact loading, starting with the one the app serves.
- **A new key is OMITTED WHEN EMPTY.** Writing unconditionally changes the bytes of every
  artifact built by the frozen probe mirrors whose shas Track B's identity gate pins.
- **A reader must tolerate absence** (`meta.get(key, [])`, never `meta[key]`).
- **Wire keys cannot be renamed.** New wire keys are chosen once, here, and are permanent.

**Naming — quantities carry their currency.** Any popularity- or degree-derived quantity names
its basis in its identifier (`pop_raw`, `pop_pctl`, `degree_hub_penalty`). Nothing in this plan
introduces such a quantity, but the convention binds if one appears.

**Environment.**

- Prefix every `uv` command with `UV_LINK_MODE=copy`.
- `PYTHONIOENCODING=utf-8` on anything printing artist names.
- `PYTHONUNBUFFERED=1` (or `python -u`) on any long job whose output is redirected — otherwise
  it writes a 0-byte log and looks dead while running perfectly.
- `cd` into the package before running `uv`; each has its own `.venv` and `pyproject.toml`.

**Licensing.** Plain-text or URL links to Spotify and Apple Music need no agreement. **Using
their logos pulls in brand guidelines — start with text or a generic icon** (spec §4.7).

**Out of scope, and settled — do not re-open.**

- **A prose artist description is DROPPED, not deferred** (spec §4.5). Not Wikipedia "for the
  ones that have it" — that is the fame floor, considered and declined with the measurement in
  view. Not LLM-generated — rejected on harm, the hallucination rate being inversely correlated
  with fame.
- **Genre tags are DEFERRED, not dropped** (spec §4.6). `LUX-E6` is their entry condition.

---

## Decisions this plan takes

Each is flagged for the owner to overrule. A session takes them so the plan is executable; none
is smuggled.

**`L4-D1` — two maps, not one.** Streaming links and structured facts ship as **two separate
frozen modules** (`dsp_links.py`, `artist_facts.py`) and **two separate APG1 keys**, despite
coming from one extraction pass. They have different refresh triggers (a link map goes stale
when a DSP relation is added; facts go stale when MusicBrainz corrects a life span) and
different failure modes (a missing link degrades to a search URL; a missing fact hides a line).
One combined blob would couple them and make the `deezer_ids`-style "re-extract before serving a
new population" obligation ambiguous. *Alternative if overruled: one `artist_meta` key holding
a dict per artist — fewer keys, one obligation, but a single stale-ness question for two things
that go stale for different reasons.*

**`L4-D2` — links ship as ids, not URLs.** The artifact stores the platform id tail
(`spotify_ids`, `apple_ids`), exactly as `deezer_ids` does, and the **frontend** composes the
URL. Storing full URLs would bake a hostname into 58,838 entries and into every artifact
forever, and a URL-scheme change would then need a rebuild rather than a frontend edit.
*Alternative if overruled: store URLs and let the frontend render them opaquely.*

**`L4-D3` — the info card renders only fields that are present, with no placeholder rows.**
A missing life span shows nothing, not "Unknown". This mirrors `LUX-3`'s accepted position that
an absent control renders nothing at all, and it is the empty state `LUX-E2` exists to check.
**`L4-T7` measures whether that is good enough** and may send this back. *Alternative if
overruled: a designed empty state per field.*

---

## File structure

**Created:**

| File | Responsibility |
|---|---|
| `builder/src/artistpath_builder/dsp_links.py` | Frozen MBID→{spotify,apple} id maps, sha-pinned. Loader only. |
| `builder/src/artistpath_builder/data/dsp_links_20260905.json` | The link payload (package data). |
| `builder/src/artistpath_builder/artist_facts.py` | Frozen MBID→structured facts map, sha-pinned. Loader only. |
| `builder/src/artistpath_builder/data/artist_facts_20260905.json` | The facts payload (package data). |
| `builder/tests/test_dsp_links.py` | Loader + identity-block tests. |
| `builder/tests/test_artist_facts.py` | Loader + identity-block tests. |
| `builder/analysis/2026-09-05-lux-4-rebuild/` | The rebuild's control and verification, and `LUX-E5`. Figures owner. |
| `frontend/src/components/ArtistInfo.tsx` | The structured-facts line on a card. |
| `frontend/src/components/ArtistInfo.test.tsx` | Its tests. |
| `frontend/src/components/StreamingLinks.tsx` | The link buttons. |
| `frontend/src/components/StreamingLinks.test.tsx` | Its tests. |
| `frontend/src/lib/dspUrls.ts` | id → URL composition, and the search fallback. |
| `frontend/src/lib/dspUrls.test.ts` | Its tests. |

**Modified:**

| File | Change |
|---|---|
| `builder/src/artistpath_builder/acceptance.py` | `L4-T1` — the bounds decision. |
| `builder/analysis/2026-08-02-dsp-ids/dsp_ids.py` | Stop filtering Spotify out; emit structured fields in the same pass. |
| `builder/src/artistpath_builder/graph.py` | `Graph` gains `spotify_ids`, `apple_ids`, `artist_facts`. |
| `builder/src/artistpath_builder/pipeline.py` | Wire the two loaders in, beside `load_deezer_ids()`. |
| `builder/src/artistpath_builder/artifact.py` | Write and read the three additive keys. |
| `api/src/artistpath_api/graph_store.py` | Read them; bounds-checked accessors. |
| `api/src/artistpath_api/models.py` | `ArtistOut` gains the link and fact fields. **Wire contract.** |
| `api/src/artistpath_api/app.py` | Populate the new `ArtistOut` fields. |
| `frontend/src/api/types.ts` | `Artist` gains the same fields. |
| `frontend/src/components/ArtistCard.tsx` | Render `ArtistInfo` and `StreamingLinks`. |

---

## Handoff seams

This plan is 11 tasks, past the ~8–12 point where a controller's context is in long-context
territory however well the work is delegated. **Two seams are chosen here, at authoring time:**

- **After `L4-T6`** — the artifact exists, is verified, and its identity is committed in an
  analysis README. Everything downstream reads a finished artifact rather than a live
  understanding. **This is the primary seam.**
- **After `L4-T9`** — the API is complete and its contract is committed. The frontend tasks
  consume a fixed wire shape.

Append to the retained execution log **per task**, not only at closeout — decisions and
reasoning, not narration.

---

## Task `L4-T1`: unblock the rebuild — the acceptance bounds

**✅ DONE 2026-09-05. Option A, taken by the session — see the correction below.**

**⚠ THE OWNER OVERRULED THE ESCALATION ITSELF, and the rule he set is worth carrying:**
moving a bound so a **new, never-served** artifact can be adopted is risk acceptance and his
(that is what `MSW-` `4b55144` and `CXA-` `c4cfbb1` both were). Moving one to re-admit the
artifact **already in production** is bookkeeping and a session's. The mechanical test: *is
the new bound derived from something known independently of the build that went red?*

**⚠ AND THIS TASK NAMED THE WRONG COMMIT — corrected, because the record must not carry it.**
It said to read the band from `3aa61f0b`. That is the band of the **retired 75k map**
(`node_count=(60_000, 90_000)`, `edge_count=(700_000, 1_100_000)`) and it **rejects the served
map on BOTH bounds** — 58,838 < 60,000 and 1,315,684 > 1,100,000. Following it literally
leaves the rebuild still refused. The band that admitted `graph-msw-tu50.bin` is at
**`4b55144`** (`MSW-` Task 9, ten minutes later): `node_count=(47_000, 71_000)`,
`edge_count=(1_050_000, 1_580_000)`. The trap: the live artifact's manifest records
`git_commit: 3aa61f0b`, because the build ran at that commit and the bounds moved right after
it. **This is why the escalation was not the safeguard — the figure put to the owner was
wrong, and approving it would not have caught that.** Arithmetic against the manifest did.

**Also corrected: BOTH bounds moved, not just the artist count** the error message named. The
`CXA-` edge band admitted `JFX-B` (1,618,164) — the adoption the owner's listening test
rejected — so restoring only the node bound would have left the reverted artifact admissible.

*(Original task text follows, for the record.)*

**⚠ THIS TASK CONTAINS AN OWNER DECISION AND STOPS FOR IT.** Do not pick an option yourself.

**Files:**
- Modify: `builder/src/artistpath_builder/acceptance.py`
- Modify: `builder/src/artistpath_builder/cli.py` (option B only)
- Test: `builder/tests/test_acceptance.py`

**Interfaces:**
- Consumes: nothing.
- Produces: a builder that can serialise a 58,838-artist artifact. Every later build task
  depends on this.

**The problem, measured 2026-09-05.** `cmd_build` runs `check_acceptance` **before**
`serialise`, and `CXA-` Task 1 (`c4cfbb1`) recalibrated the bounds for the extended 117k
population. A **correct** rebuild of the served map is refused and never written:

```
ArtifactRejected: artifact rejected; not written:
  - artist count 58838 outside bounds [70900, 106400]
```

This is the **third `CXA-` leftover** — the `CXR-` revert moved the map and moved none of the
things calibrated around it (the drop-list pointer, the archive, and this). It is **not** a
correctness problem with the graph: acceptance governs whether a build is *admitted*, never
what it *contains*.

**The two options, both fully specified so the choice is mechanical:**

**Option A — recalibrate the bounds to the served population.** Restores the pre-expansion
state, consistent with the revert; makes the default path correct for every future build.
Change `PRODUCTION_ACCEPTANCE`'s artist-count bound back to the band that admitted
`graph-msw-tu50.bin`, taken from the pre-`c4cfbb1` value at commit **`4b55144`** — **read it from
git, never invent a band**. *(This originally read `3aa61f0b`; see the correction at the head
of this task.)*

```bash
git show 4b55144:builder/src/artistpath_builder/acceptance.py | grep -n -A 8 "PRODUCTION_ACCEPTANCE"
```

**Option B — wire the `--criteria` hook the CLI lacks.** `cmd_build` already reads
`getattr(args, "criteria", PRODUCTION_ACCEPTANCE)`, so the code half exists and no argument
supplies it. Add a `--criteria` argument selecting a named criteria set. Leaves the default
wrong but touches no shipped bound.

**Recommendation (a session's, and overrulable): Option A.** The bounds are stale in exactly
the way the drop list and the archive were, and leaving them means every future build of the
served lineage needs a flag to work. Option B preserves a default that is calibrated for a
population that no longer exists.

**⚠ Whichever is chosen, a session must NOT widen a bound to admit its own build.** The
archive's standing warning is that widening removes the protection with nothing going red.
Option A restores a previously-calibrated band read from git; it does not invent one.

- [ ] **Step 1: Put the decision to the owner and wait.** State the two options above in one
      message, with the recommendation and the one-line reason. Do not proceed until answered.

- [ ] **Step 2: Write the failing test** (shown for Option A; for Option B assert the CLI
      accepts and threads `--criteria`).

```python
# builder/tests/test_acceptance.py
def test_served_population_is_admitted():
    """The artifact the app serves must pass its own acceptance gate.

    Regression for the third CXA- leftover: the CXR- revert restored the map
    and left the bounds calibrated for the reverted 117k population, so a
    correct rebuild was rejected before serialise and never written.
    """
    graph = _graph_with(artist_count=58838, edge_count=1315684)
    check_acceptance(graph, PRODUCTION_ACCEPTANCE)  # must not raise
```

- [ ] **Step 3: Run it and confirm it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_acceptance.py::test_served_population_is_admitted`
Expected: FAIL with `ArtifactRejected: artist count 58838 outside bounds [70900, 106400]`

- [ ] **Step 4: Apply the chosen option**, with a comment naming this as revert cleanup and
      citing `builder/analysis/2026-09-05-lux-e1-armb/README.md` §4 for why it was found.

- [ ] **Step 5: Run the full builder suite**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS, including the new test.

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/acceptance.py builder/tests/test_acceptance.py
git commit -m "L4-T1: the served population passes its own acceptance gate again

Third CXA- leftover: the revert restored the map and left the bounds
calibrated for the reverted 117k population, so a correct rebuild was
rejected before serialise. Owner chose option <A|B>."
```

---

## Task `L4-T2`: extend the extraction pass — Spotify and structured fields

**Files:**
- Modify: `builder/analysis/2026-08-02-dsp-ids/dsp_ids.py`
- Create: `builder/analysis/2026-08-02-dsp-ids/dsp_links.json` (new output)
- Create: `builder/analysis/2026-08-02-dsp-ids/artist_facts.json` (new output)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: two JSON payloads consumed by `L4-T3` and `L4-T4`. Shapes fixed below.

**What already exists, verified against source 2026-09-05.** `dsp_ids.py`'s `DSP` host map
**already contains** `open.spotify.com` and `spotify.com` (line 88). It is filtered out one line
later — `if platform not in ("deezer", "apple")` at line 160. The MusicBrainz dump is on disk at
`builder/scratch/mb-json-dumps/artist/mbdump/artist` (17.2 GB), and a record carries every field
this task needs — confirmed by reading one:

```
type: "Group"   country: "US"   disambiguation: "US electronic lounge band"
area:       {"name": "United States", ...}
begin-area: {"name": "San Francisco", ...}
life-span:  {"begin": "1995", "end": null, "ended": false}
```

**Payload shapes — fixed here and depended on by three later tasks:**

```json
// dsp_links.json
{
  "extracted_at": "2026-09-05",
  "population_sha256": "43dd82bb…",        // the artifact this was extracted over
  "spotify_ids_sha256": "…",                // sha256 of json.dumps(sorted(items()), sort_keys=True)
  "apple_ids_sha256": "…",
  "spotify_ids": {"<mbid>": "<id tail>"},
  "apple_ids":   {"<mbid>": "<id tail>"}
}

// artist_facts.json
{
  "extracted_at": "2026-09-05",
  "population_sha256": "43dd82bb…",
  "artist_facts_sha256": "…",
  "artist_facts": {
    "<mbid>": {"type": "Group", "country": "US", "area": "United States",
               "begin": "1995", "end": null, "ended": false}
  }
}
```

**Omit absent fields rather than storing nulls**, except `end`/`ended`, which are meaningful as
`null`/`false`. An artist with no facts at all is **absent from the map**, not present-and-empty
— this keeps the blob small and matches `L4-D3`.

- [ ] **Step 1: Write the failing test for the new host filter**

```python
# builder/analysis/2026-08-02-dsp-ids/test_dsp_ids.py  (new file)
from dsp_ids import host_of, DSP

def test_spotify_is_a_recognised_platform():
    assert DSP[host_of("https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF")] == "spotify"

def test_spotify_is_no_longer_filtered_out():
    from dsp_ids import KEPT_PLATFORMS
    assert "spotify" in KEPT_PLATFORMS
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q analysis/2026-08-02-dsp-ids/test_dsp_ids.py`
Expected: FAIL — `KEPT_PLATFORMS` does not exist.

- [ ] **Step 3: Replace the inline filter with a named constant and add Spotify**

```python
# Was: if platform not in ("deezer", "apple"): continue
# LUX-4 adds spotify. Named rather than inline so the test can assert it and
# so the next platform is a one-line change in one place.
KEPT_PLATFORMS = ("deezer", "apple", "spotify")
...
    if platform not in KEPT_PLATFORMS:
        continue
```

- [ ] **Step 4: Extract the structured fields in the same pass**

Inside the per-record loop that already parses `d`, alongside the relation scan:

```python
        facts = {}
        if d.get("type"):
            facts["type"] = d["type"]
        if d.get("country"):
            facts["country"] = d["country"]
        area = d.get("area") or {}
        if area.get("name"):
            facts["area"] = area["name"]
        span = d.get("life-span") or {}
        if span.get("begin"):
            facts["begin"] = span["begin"]
        # `end` and `ended` are meaningful when falsy: "ended: false" is the
        # positive claim that the artist is still active, which is not the
        # same as the field being absent.
        if span.get("begin") or span.get("end"):
            facts["end"] = span.get("end")
            facts["ended"] = bool(span.get("ended"))
        if facts:
            artist_facts.setdefault(mbid, facts)
```

- [ ] **Step 5: Write both payloads, restricted to the served population**

Reuse the existing `graph` population set the script already builds. Compute each sha the same
way `deezer_ids.py` documents: `sha256(json.dumps(sorted(m.items()), sort_keys=True).encode())`.

- [ ] **Step 6: Run the extraction**

Run:
```bash
cd builder && UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 \
  uv run python analysis/2026-08-02-dsp-ids/dsp_ids.py
```
Expected: completes offline; prints the existing coverage table **plus a Spotify column**, and
writes `dsp_links.json` and `artist_facts.json`. The dump is 17.2 GB, so this is minutes, not
seconds — the unbuffered flag is what stops it looking dead.

- [ ] **Step 7: Record `LUX-E3` — Spotify id coverage**

This is the eval spec §5 owes, and it is free now the extraction has run. Append a section to
`builder/analysis/2026-08-02-dsp-ids/README.md` reporting Spotify coverage **by popularity band**
beside the existing Deezer and Apple columns. Its threshold is **descriptive — none**: it decides
whether the feature is "both services" or "Apple plus search", and nothing else.

**Plain sentence, from the spec:** *how many artists have a Spotify link recorded in
MusicBrainz, and is it better or worse than Apple's?*

- [ ] **Step 8: Commit**

```bash
git add builder/analysis/2026-08-02-dsp-ids/
git commit -m "L4-T2: extract Spotify ids and structured artist facts; LUX-E3 read

One pass over the MusicBrainz dump now keeps spotify alongside deezer and
apple, and emits the structured fields the info card needs. LUX-E3's
coverage read is recorded beside the existing Deezer and Apple columns."
```

---

## Task `L4-T3`: the frozen streaming-link module

**Files:**
- Create: `builder/src/artistpath_builder/dsp_links.py`
- Create: `builder/src/artistpath_builder/data/dsp_links_20260905.json` (copied from `L4-T2`)
- Test: `builder/tests/test_dsp_links.py`

**Interfaces:**
- Consumes: `dsp_links.json` from `L4-T2`.
- Produces: `load_dsp_links() -> tuple[dict[str, str], dict[str, str]]` returning
  `(spotify_ids, apple_ids)`; constants `SPOTIFY_IDS_SHA256`, `APPLE_IDS_SHA256`,
  `DSP_LINKS_PATH`. Consumed by `L4-T5`.

**Read `deezer_ids.py`'s docstring before writing this.** It records why the map is
one-per-artist rather than one-per-archive, and why a missing id must degrade to today's
behaviour rather than to an error. This module is the same shape and must carry the same
standing obligation.

- [ ] **Step 1: Write the failing test**

```python
# builder/tests/test_dsp_links.py
import hashlib, json
from artistpath_builder.dsp_links import (
    APPLE_IDS_SHA256, SPOTIFY_IDS_SHA256, load_dsp_links,
)

def test_payload_matches_its_own_identity_block():
    """A payload that cannot vouch for itself must not be trusted.

    Same discipline as the drop lists: the sha is recorded in the module and
    recomputed here, so a silently swapped file fails the suite rather than
    shipping.
    """
    spotify, apple = load_dsp_links()
    for mapping, expected in ((spotify, SPOTIFY_IDS_SHA256), (apple, APPLE_IDS_SHA256)):
        actual = hashlib.sha256(
            json.dumps(sorted(mapping.items()), sort_keys=True).encode()
        ).hexdigest()
        assert actual == expected

def test_a_missing_artist_is_absent_not_empty():
    spotify, _ = load_dsp_links()
    assert "00000000-0000-0000-0000-000000000000" not in spotify

def test_ids_are_tails_not_urls():
    spotify, apple = load_dsp_links()
    for mapping in (spotify, apple):
        for value in list(mapping.values())[:50]:
            assert not value.startswith("http"), value
            assert "/" not in value, value
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_dsp_links.py`
Expected: FAIL with `ModuleNotFoundError: artistpath_builder.dsp_links`

- [ ] **Step 3: Write the module**

```python
"""Frozen MusicBrainz artist -> Spotify / Apple Music artist id maps
(2026-09-05 snapshot).

WHY IT EXISTS
`LUX-4` puts a "listen on" link on every journey card. MusicBrainz already
records URL relations to both services, so the ids are free and exact -- no
name search, and therefore none of the wrong-same-named-artist risk that
`BYP-13` is about.

ONE MAP FOR ANY ARCHIVE -- and that is NOT the drop-list mistake repeated
A Spotify id is a PROPERTY OF AN ARTIST, exactly as a Deezer id is: an MBID
maps to the same Spotify artist whatever similarity archive is being built.
`no_release_drop.py` is per-archive because it encodes a DECISION ABOUT A
POPULATION; this does not. A missing id degrades to a search URL, which is a
coverage gap and never a wrong answer.

WHY IDS AND NOT URLS (`L4-D2`)
The id tail is stored and the frontend composes the URL. Storing full URLs
would bake a hostname into 58,838 entries and into every artifact forever,
and a URL-scheme change would then need a rebuild rather than a frontend edit.

A DATED SNAPSHOT, like the drop lists and `deezer_ids`
The build must never re-resolve these over the network: `build_from_archive`
is offline by a hard rule and spec section 9 requires byte-identical output
for identical input.

STANDING OBLIGATION -- the same one `deezer_ids.py` carries, and it is
discharged by the same act. Extracted over the ADOPTED artifact's population
(sha 43dd82bb...). Before a DIFFERENT artifact is ever served, re-extract over
its population. An artist outside the extracted population gets no id and
falls back to a search link.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

# sha256 of json.dumps(sorted(<map>.items()), sort_keys=True), reproduced by
# builder/analysis/2026-08-02-dsp-ids/dsp_ids.py.
SPOTIFY_IDS_SHA256 = "<fill from dsp_links.json>"
APPLE_IDS_SHA256 = "<fill from dsp_links.json>"

DSP_LINKS_PATH = Path(__file__).parent / "data" / "dsp_links_20260905.json"


@lru_cache(maxsize=1)
def load_dsp_links() -> tuple[dict[str, str], dict[str, str]]:
    """(spotify_ids, apple_ids), MBID -> platform id tail."""
    payload = json.loads(DSP_LINKS_PATH.read_text(encoding="utf-8"))
    return payload["spotify_ids"], payload["apple_ids"]
```

- [ ] **Step 4: Copy the payload and fill both shas**

```bash
cd builder
cp analysis/2026-08-02-dsp-ids/dsp_links.json \
   src/artistpath_builder/data/dsp_links_20260905.json
python -c "import json;p=json.load(open('src/artistpath_builder/data/dsp_links_20260905.json'));print(p['spotify_ids_sha256']);print(p['apple_ids_sha256'])"
```

Paste both into the module constants.

- [ ] **Step 5: Run the tests**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_dsp_links.py`
Expected: PASS, all three.

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/dsp_links.py \
        builder/src/artistpath_builder/data/dsp_links_20260905.json \
        builder/tests/test_dsp_links.py
git commit -m "L4-T3: frozen Spotify and Apple id maps, sha-pinned

Same shape and same standing obligation as deezer_ids.py: extracted over the
adopted population, never re-resolved at build time, missing id degrades to a
search link."
```

---

## Task `L4-T4`: the frozen artist-facts module

**Files:**
- Create: `builder/src/artistpath_builder/artist_facts.py`
- Create: `builder/src/artistpath_builder/data/artist_facts_20260905.json`
- Test: `builder/tests/test_artist_facts.py`

**Interfaces:**
- Consumes: `artist_facts.json` from `L4-T2`.
- Produces: `load_artist_facts() -> dict[str, dict]`; constant `ARTIST_FACTS_SHA256`.
  Consumed by `L4-T5`.

- [ ] **Step 1: Write the failing test**

```python
# builder/tests/test_artist_facts.py
import hashlib, json
from artistpath_builder.artist_facts import ARTIST_FACTS_SHA256, load_artist_facts

def test_payload_matches_its_own_identity_block():
    facts = load_artist_facts()
    actual = hashlib.sha256(
        json.dumps(sorted(facts.items()), sort_keys=True).encode()
    ).hexdigest()
    assert actual == ARTIST_FACTS_SHA256

def test_an_artist_with_no_facts_is_absent_not_empty():
    """`L4-D3`: absence is the empty state. A present-but-empty dict would
    make the frontend render a blank row it has no way to distinguish."""
    facts = load_artist_facts()
    assert all(v for v in facts.values())

def test_ended_false_is_preserved_not_dropped():
    """"ended: false" is the positive claim that an artist is still active,
    which is not the same as the field being absent."""
    facts = load_artist_facts()
    with_span = [v for v in facts.values() if "ended" in v]
    assert any(v["ended"] is False for v in with_span)
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_artist_facts.py`
Expected: FAIL with `ModuleNotFoundError: artistpath_builder.artist_facts`

- [ ] **Step 3: Write the module** — same shape as `L4-T3`, with this docstring difference:

```python
"""Frozen MusicBrainz structured artist facts (2026-09-05 snapshot).

WHY STRUCTURED FIELDS AND NOT PROSE (spec section 4.5)
A prose description is DROPPED, not deferred. MusicBrainz holds no
biographies; Wikipedia shares the fame floor and would be rich for the famous
and empty for everyone this app exists to find; Last.fm is barred; and
LLM-generated prose was rejected on HARM, because the hallucination rate is
inversely correlated with fame -- it would publish invented biographical
claims about real, often living, often obscure musicians, with the errors
concentrated on the people least able to notice them.

Structured facts orient without pre-empting the verdict -- "German duo,
1993-2008" tells you where you are and gets out of the way -- and they cannot
be wrong. Do not re-open this as "we could just use Wikipedia for the ones
that have it": that IS the fame floor, considered and declined.

Genre tags are DEFERRED, not dropped (spec section 4.6). `LUX-E6` gates them.

Same freezing, sha-pinning and re-extraction obligation as `dsp_links.py`.
"""
```

- [ ] **Step 4: Copy the payload and fill the sha** (as `L4-T3` step 4).

- [ ] **Step 5: Run the tests**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_artist_facts.py`
Expected: PASS, all three.

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/artist_facts.py \
        builder/src/artistpath_builder/data/artist_facts_20260905.json \
        builder/tests/test_artist_facts.py
git commit -m "L4-T4: frozen structured artist facts, sha-pinned

Structured MusicBrainz fields only. Prose is dropped, not deferred; tags are
deferred, not dropped. Reasoning carried in the module docstring."
```

---

## Task `L4-T5`: graph model and pipeline wiring

**Files:**
- Modify: `builder/src/artistpath_builder/graph.py`
- Modify: `builder/src/artistpath_builder/pipeline.py:453-458`
- Test: `builder/tests/test_pipeline.py`

**Interfaces:**
- Consumes: `load_dsp_links()` (`L4-T3`), `load_artist_facts()` (`L4-T4`).
- Produces: `Graph.spotify_ids: list[str]`, `Graph.apple_ids: list[str]`,
  `Graph.artist_facts: list[dict]` — **all three node-indexed and parallel to `mbids`**,
  exactly as `deezer_ids` is. Consumed by `L4-T6`.

**Follow `deezer_ids`'s existing shape exactly.** In `graph.py` it is
`deezer_ids: list[str] = field(default_factory=list)`, defaulted because frozen probe mirrors
construct `Graph` without it. The three new fields are defaulted for the same reason.

- [ ] **Step 1: Write the failing test**

```python
# builder/tests/test_pipeline.py
def test_new_metadata_is_node_indexed_and_parallel_to_mbids(tiny_archive):
    graph = build_from_archive(_config(), tiny_archive, _offline_source())
    assert len(graph.spotify_ids) == len(graph.mbids)
    assert len(graph.apple_ids) == len(graph.mbids)
    assert len(graph.artist_facts) == len(graph.mbids)

def test_an_artist_with_no_link_gets_an_empty_string_not_a_gap(tiny_archive):
    """Parallel-to-mbids means every node has a slot. An absent id is "",
    which the api reads as "fall back to a search link"."""
    graph = build_from_archive(_config(), tiny_archive, _offline_source())
    assert all(isinstance(v, str) for v in graph.spotify_ids)
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_pipeline.py -k metadata`
Expected: FAIL with `AttributeError: 'Graph' object has no attribute 'spotify_ids'`

- [ ] **Step 3: Add the fields to `Graph`**, each with a comment naming `LUX-4` and pointing at
      its module, in the style of the `deezer_ids` comment already there.

- [ ] **Step 4: Wire the loaders in `pipeline.py`**, immediately beside the existing
      `deezer_ids=load_deezer_ids(),` at line 458, projecting each map onto node order:

```python
        # LUX-4. Same build-time-lookup rule as deezer_ids above: frozen
        # snapshots, never resolved over the network. Projected onto node
        # order here so the artifact writer stays a pure serialiser.
        spotify_ids=[spotify.get(m, "") for m in mbids],
        apple_ids=[apple.get(m, "") for m in mbids],
        artist_facts=[facts.get(m, {}) for m in mbids],
```

- [ ] **Step 5: Run the full builder suite**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS. **The offline replay test must still pass** — it injects a fetcher that raises,
proving `build_from_archive` touches no network.

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/graph.py builder/src/artistpath_builder/pipeline.py \
        builder/tests/test_pipeline.py
git commit -m "L4-T5: carry links and facts through the graph, node-indexed"
```

---

## Task `L4-T6`: the additive APG1 keys — write and read

**Files:**
- Modify: `builder/src/artistpath_builder/artifact.py:57-73` (write), `:146-151` (read)
- Test: `builder/tests/test_artifact.py`

**Interfaces:**
- Consumes: `Graph.spotify_ids`, `Graph.apple_ids`, `Graph.artist_facts` (`L4-T5`).
- Produces: APG1 metadata keys **`spotify_ids`**, **`apple_ids`**, **`artist_facts`**. These
  are **wire keys and permanent** — `L4-T8` reads them by these exact names.

**⚠ The additive-key discipline is already written in `artifact.py` and must be followed
exactly.** Read the comment above `if graph.deezer_ids:` before editing. Three rules:

1. **`FORMAT_VERSION` stays `1`** — both parsers check strict equality; bumping stops every
   existing artifact loading, starting with the served one.
2. **Omit when empty** — writing unconditionally changes the bytes of every artifact built by
   the frozen probe mirrors whose shas Track B's identity gate pins.
3. **Read with `.get(key, [])`**, never `meta[key]`.

- [ ] **Step 1: Write the failing test**

```python
# builder/tests/test_artifact.py
def test_new_keys_are_omitted_when_empty():
    """The omission is the design. An artifact built without these maps must
    be byte-identical to one built before they existed -- that is what keeps
    the frozen probe mirrors' pinned shas valid."""
    graph = _graph(artists=3)  # no links, no facts
    blob = json.loads(_metadata_of(serialise(graph)))
    assert "spotify_ids" not in blob
    assert "apple_ids" not in blob
    assert "artist_facts" not in blob

def test_new_keys_round_trip():
    graph = _graph(artists=3, spotify_ids=["a", "", "c"],
                   apple_ids=["", "b", ""],
                   artist_facts=[{"type": "Group"}, {}, {"country": "DE"}])
    back = deserialise(serialise(graph))
    assert back.spotify_ids == ["a", "", "c"]
    assert back.apple_ids == ["", "b", ""]
    assert back.artist_facts == [{"type": "Group"}, {}, {"country": "DE"}]

def test_format_version_is_not_bumped():
    assert FORMAT_VERSION == 1
```

- [ ] **Step 2: Run and confirm failure**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_artifact.py -k new_keys`
Expected: FAIL — `serialise` does not accept or emit the fields.

- [ ] **Step 3: Add the three writes**, each guarded, immediately after the `fame_lb` block:

```python
    # LUX-4. SAME additive-key discipline as deezer_ids and fame_lb above and
    # for the same two reasons: FORMAT_VERSION stays 1 because both parsers
    # check strict equality, and the keys are omitted when empty so every
    # artifact built before LUX-4 -- including the frozen probe mirrors whose
    # shas Track B's identity gate pins -- stays byte-identical.
    #
    # Ids are stored as platform id TAILS, never URLs (`L4-D2`): a hostname
    # baked into 58,838 entries cannot be changed without a rebuild.
    if any(graph.spotify_ids):
        meta["spotify_ids"] = graph.spotify_ids
    if any(graph.apple_ids):
        meta["apple_ids"] = graph.apple_ids
    if any(graph.artist_facts):
        meta["artist_facts"] = graph.artist_facts
```

**Note `any(...)` rather than truthiness of the list** — these lists are node-indexed and so are
*never* empty once `L4-T5` runs; they are full of `""` and `{}` when nothing was extracted.
`if graph.spotify_ids:` would write the key unconditionally and break rule 2.

- [ ] **Step 4: Add the three reads** in `deserialise`, beside `deezer_ids=meta.get(...)`:

```python
        spotify_ids=metadata.get("spotify_ids", []),
        apple_ids=metadata.get("apple_ids", []),
        artist_facts=metadata.get("artist_facts", []),
```

- [ ] **Step 5: Run the full builder suite**

Run: `cd builder && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add builder/src/artistpath_builder/artifact.py builder/tests/test_artifact.py
git commit -m "L4-T6: three additive APG1 keys for links and facts

FORMAT_VERSION stays 1; keys omitted when every slot is empty, so artifacts
built before LUX-4 stay byte-identical and the probe mirrors' pinned shas
remain valid."
```

---

## Task `L4-T7`: rebuild, verify, and `LUX-E5` — **PRIMARY HANDOFF SEAM**

**Files:**
- Create: `builder/analysis/2026-09-05-lux-4-rebuild/verify.py`
- Create: `builder/analysis/2026-09-05-lux-4-rebuild/README.md` (**figures owner**)
- Modify: `docs/README.md` (one row classifying the new directory)

**Interfaces:**
- Consumes: everything from `L4-T1`–`L4-T6`.
- Produces: `builder/scratch/graph-lux4.bin` and its manifest sidecar. **The sha in that
  manifest is what `ARTISTPATH_GRAPH_SHA256` gets set to at deploy — never transcribed by hand
  (`DEP-24`).**

**⚠ This task is a comparison, so it carries a factor table.** The claim under test is *"same
graph, plus three metadata keys."* That is exactly the kind of claim that has been wrong here
before, and a sha alone cannot check it — the sha **must** differ, because keys were added.

| Build | link/fact maps | archive | drop list | expected |
|---|---|---|---|---|
| **Control** | **empty** (maps not wired) | pre-CEX snapshot | `…algb_20260805.json` | **sha == `43dd82bb…`** |
| **Shipping** | populated | pre-CEX snapshot | `…algb_20260805.json` | sha differs; **CSR arrays and all pre-existing metadata identical to control** |

**Held constant, and why the intervention cannot change it:** the archive and the drop list are
pinned per invocation (both are the drifted inputs `LUX-E1` identified); `--algorithm`,
`--cap-strategy` and `--require-fame` are passed explicitly. **The intervention adds metadata
only** — it touches no edge, no score, no node, and `L4-T6`'s writes happen after the graph is
built. The control arm is what proves that rather than assuming it.

- [ ] **Step 1: Run the control build**

Its purpose is to prove `L4-T1`–`L4-T6` changed nothing that reaches the graph. Reuse the
committed probe, which already pins both inputs:

Run:
```bash
cd builder && UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 \
  uv run python analysis/2026-09-05-lux-e1-armb/armb_sha.py
```
Expected: `READ: BYTE-IDENTICAL`. **If this fails, STOP** — something in `L4-T1`–`L4-T6` reached
the graph, and no later step is valid until it is found.

- [ ] **Step 2: Run the shipping build**

```bash
cd builder && UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 \
  uv run artistpath-build build \
    --archive-dir scratch/grt-archive-algb.pre-cex-snapshot \
    --algorithm "session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30" \
    --cap-strategy trimmed_union \
    --require-fame \
    --unlistenable-list src/artistpath_builder/data/unlistenable_drop_algb_20260805.json \
    --out scratch/graph-lux4.bin
```
Expected: writes the artifact **and its manifest**. If it raises `ArtifactRejected`, `L4-T1` was
not completed.

- [ ] **Step 3: Write `verify.py` — the structural comparison**

```python
"""Prove the LUX-4 artifact is the served graph plus three metadata keys.

The sha MUST differ -- keys were added -- so the sha cannot be the check.
This compares everything else, field by field, and fails loudly on any
difference outside the three new keys.
"""
NEW_KEYS = {"spotify_ids", "apple_ids", "artist_facts"}

live = deserialise(Path("scratch/graph-msw-tu50.bin").read_bytes())
new = deserialise(Path("scratch/graph-lux4.bin").read_bytes())

assert new.artist_count == live.artist_count, (new.artist_count, live.artist_count)
assert new.edge_count == live.edge_count
assert new.mbids == live.mbids
assert new.names == live.names
assert new.disambiguations == live.disambiguations
assert new.pop_raw == live.pop_raw
assert new.deezer_ids == live.deezer_ids
assert new.fame_lb_raw == live.fame_lb_raw
assert (new.offsets == live.offsets).all()
assert (new.neighbours == live.neighbours).all()
assert (new.scores == live.scores).all()

live_keys = set(json.loads(_metadata_of(live_bytes)))
new_keys = set(json.loads(_metadata_of(new_bytes)))
assert new_keys - live_keys == NEW_KEYS, new_keys - live_keys
assert live_keys - new_keys == set(), live_keys - new_keys
print("VERIFIED: identical graph; metadata differs by exactly", sorted(NEW_KEYS))
```

- [ ] **Step 4: Run it**

Run: `cd builder && UV_LINK_MODE=copy uv run python analysis/2026-09-05-lux-4-rebuild/verify.py`
Expected: `VERIFIED: …`. **Any assertion failure stops the plan.**

- [ ] **Step 5: `LUX-E5` — metadata blob and boot cost**

**Plain sentence, fixed in the spec before any result existed:** *does the extra artist
information still fit in the memory the running service actually has?*

**Threshold, also from the spec:** must fit within the deployed container's configured memory
with headroom for the existing working set. **If it does not, fields are dropped — starting with
tags, never with `LUX-E2`'s survivors.** (Tags are already deferred, so in practice the first
droppable thing is `artist_facts`' `area`.)

Record in the README: metadata blob bytes and artifact total **before and after**, plus API
resident memory and boot time measured in the deployed configuration. The artifact was 17.8 MB
and the JSON blob is loaded whole at boot.

- [ ] **Step 6: Write the README as figures owner**, carrying the factor table, the control
      result, the verification output, `LUX-E5`'s figures, and the manifest sha. Add its row to
      `docs/README.md`.

- [ ] **Step 7: Commit**

```bash
git add builder/analysis/2026-09-05-lux-4-rebuild/ docs/README.md
git commit -m "L4-T7: rebuild verified as the served graph plus three metadata keys

Control build reproduces 43dd82bb byte-identically, proving L4-T1..T6 reach
no part of the graph. Shipping build differs only by the three new keys,
checked field by field rather than by sha. LUX-E5 recorded."
```

> ### ⛳ HANDOFF SEAM — retire the session here
>
> The artifact exists, is verified, and its identity is committed. Everything downstream reads a
> finished artifact rather than a live understanding. Write the handoff note per `closeout`,
> and start `L4-T8` fresh.

---

## Task `L4-T8`: the API reads the new keys

**Files:**
- Modify: `api/src/artistpath_api/graph_store.py:262-276`
- Test: `api/tests/test_graph_store.py`

**Interfaces:**
- Consumes: APG1 keys `spotify_ids`, `apple_ids`, `artist_facts` (`L4-T6`).
- Produces: `GraphStore.spotify_id(node) -> str | None`, `.apple_id(node) -> str | None`,
  `.facts(node) -> dict`. Consumed by `L4-T9`.

**⚠ Follow the length discipline already in `graph_store.py`, and note it differs by field.**
The existing comment says it exactly: `fame_lb` has its **length checked** because it is indexed
by node id **in the cost function**, where a short list would price one artist as another;
`deezer_ids` **escapes that check only because it is read through a bounds-checked accessor**.

**All three new fields are display-only and are read through bounds-checked accessors**, so they
follow the `deezer_ids` pattern, not the `fame_lb` pattern. Copy `deezer_ids`' accessor at
`graph_store.py:70-71`.

- [ ] **Step 1: Write the failing test**

```python
# api/tests/test_graph_store.py
def test_missing_keys_mean_no_links_not_a_crash():
    """Every artifact built before LUX-4 lacks these keys, including the one
    the app serves today. Absence must degrade to a search link."""
    store = _store_without_lux4_keys()
    assert store.spotify_id(0) is None
    assert store.apple_id(0) is None
    assert store.facts(0) == {}

def test_a_short_list_does_not_read_out_of_bounds():
    """The accessor is the bounds check -- the same reason deezer_ids is
    exempt from the length assertion fame_lb carries."""
    store = _store_with(spotify_ids=["a"], artist_count=3)
    assert store.spotify_id(0) == "a"
    assert store.spotify_id(2) is None

def test_an_empty_slot_reads_as_absent():
    store = _store_with(spotify_ids=["a", "", "c"], artist_count=3)
    assert store.spotify_id(1) is None
```

- [ ] **Step 2: Run and confirm failure**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_graph_store.py -k lux4 -k bounds`
Expected: FAIL — the attributes do not exist.

- [ ] **Step 3: Add the fields and accessors**

```python
    spotify_ids: list[str] = field(default_factory=list)
    apple_ids: list[str] = field(default_factory=list)
    artist_facts: list[dict] = field(default_factory=list)

    def spotify_id(self, node: int) -> str | None:
        if node < len(self.spotify_ids):
            return self.spotify_ids[node] or None
        return None
    # apple_id and facts follow identically; facts returns {} rather than None.
```

And in the loader, beside `deezer_ids=meta.get("deezer_ids", [])`:

```python
            # LUX-4. Same additive-key reasoning as deezer_ids, and the same
            # exemption from fame_lb's length assertion: these are display
            # fields read through bounds-checked accessors, never indexed in
            # the cost function.
            spotify_ids=meta.get("spotify_ids", []),
            apple_ids=meta.get("apple_ids", []),
            artist_facts=meta.get("artist_facts", []),
```

- [ ] **Step 4: Run the api suite**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add api/src/artistpath_api/graph_store.py api/tests/test_graph_store.py
git commit -m "L4-T8: read the LUX-4 keys through bounds-checked accessors"
```

---

## Task `L4-T9`: the wire contract — `ArtistOut`

**Files:**
- Modify: `api/src/artistpath_api/models.py:46-50`
- Modify: `api/src/artistpath_api/app.py`
- Test: `api/tests/test_app.py`

**Interfaces:**
- Consumes: `GraphStore.spotify_id/.apple_id/.facts` (`L4-T8`).
- Produces: **the wire shape `L4-T10` reads.** Fixed here:

```python
class ArtistFacts(BaseModel):
    type: str | None = None      # "Group", "Person", …
    country: str | None = None   # ISO code, e.g. "US"
    area: str | None = None      # human-readable, e.g. "United States"
    begin: str | None = None     # "1995" or "1995-03-01"
    end: str | None = None
    ended: bool | None = None

class ArtistOut(BaseModel):
    mbid: str
    name: str
    disambiguation: str
    popularity: float
    # LUX-4. Additive: a client that ignores them gets exactly the pre-LUX-4
    # behaviour. Ids are platform id TAILS, not URLs (`L4-D2`) -- the frontend
    # composes the URL, and null means "render a search link instead".
    spotify_id: str | None = None
    apple_id: str | None = None
    facts: ArtistFacts | None = None
```

**⚠ `ArtistOut` is consumed by the frontend — this is a wire contract.** Every field is
additive and optional, so no existing client breaks. **`ArtistOut` appears in three places on
the wire** — `PathResponse.artists`, `PathResponse.bypassed`, and `GET /api/artists/{mbid}` —
and all three get the fields for free. Confirm that rather than assuming it.

- [ ] **Step 1: Write the failing test**

```python
# api/tests/test_app.py
def test_path_artists_carry_links_and_facts(client_with_lux4_store):
    body = client_with_lux4_store.post("/api/path", json={"sources": [A, B]}).json()
    first = body["artists"][0]
    assert first["spotify_id"] == "0OdUWJ0sBjDrqHygGUXeCF"
    assert first["facts"]["type"] == "Group"

def test_absent_data_serialises_as_null_not_missing(client_without_lux4_store):
    """A pre-LUX-4 artifact must still serve. The keys are present and null,
    so the frontend has one code path rather than two."""
    body = client_without_lux4_store.post("/api/path", json={"sources": [A, B]}).json()
    assert body["artists"][0]["spotify_id"] is None
    assert body["artists"][0]["facts"] is None

def test_bypassed_artists_carry_them_too(client_with_lux4_store):
    """LUX-2's panel renders ArtistOut, so it gets these for free -- and a
    regression here would be invisible until someone pressed bypass."""
    body = _path_with_one_bypass(client_with_lux4_store).json()
    assert "spotify_id" in body["bypassed"][0]
```

- [ ] **Step 2: Run and confirm failure**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q tests/test_app.py -k links_and_facts`
Expected: FAIL with `KeyError: 'spotify_id'`

- [ ] **Step 3: Add the models and populate them** wherever `ArtistOut` is constructed.
      **Grep first** — `grep -rn "ArtistOut(" api/src/` — and change every site, so the three
      wire positions stay consistent.

- [ ] **Step 4: Run the api suite**

Run: `cd api && UV_LINK_MODE=copy uv run --extra dev pytest -q`
Expected: PASS.

- [ ] **Step 5: Run the Snyk scan** — owed on modified `api/` code per the global instruction.

Run the `snyk_code_scan` MCP tool on `C:\dev\music-app\api`. Fix anything it reports in
first-party shipped code, then rescan until clean. (`snyk` is also on `PATH` as of 2026-09-05.)

- [ ] **Step 6: Commit**

```bash
git add api/src/artistpath_api/models.py api/src/artistpath_api/app.py api/tests/test_app.py
git commit -m "L4-T9: ArtistOut carries streaming ids and structured facts

Additive and optional, so a pre-LUX-4 artifact still serves and an older
client is unaffected. All three wire positions covered."
```

> ### ⛳ SECONDARY HANDOFF SEAM
>
> The API is complete and its contract is committed. The frontend tasks consume a fixed wire
> shape. Retire here if the session has run long.

---

## Task `L4-T10`: frontend — URL composition and link buttons

**Files:**
- Create: `frontend/src/lib/dspUrls.ts`, `frontend/src/lib/dspUrls.test.ts`
- Create: `frontend/src/components/StreamingLinks.tsx`, `.test.tsx`
- Modify: `frontend/src/api/types.ts`, `frontend/src/components/ArtistCard.tsx`

**Interfaces:**
- Consumes: `ArtistOut`'s `spotify_id`, `apple_id` (`L4-T9`).
- Produces: `<StreamingLinks artist={artist} />`. Consumed by `ArtistCard`.

**The search fallback is the point (spec §4.1, option A).** Wherever no id exists, the button
still renders and goes to a **search URL** built from the artist's name. A card must never show
one service and silently omit the other.

**Licensing:** text or a generic icon only. **No Spotify or Apple logos** — that pulls in brand
guidelines (spec §4.7).

- [ ] **Step 1: Write the failing test**

```ts
// frontend/src/lib/dspUrls.test.ts
import { appleUrl, spotifyUrl } from '@/lib/dspUrls';

test('an id produces a deep link', () => {
  expect(spotifyUrl('0OdUWJ0sBjDrqHygGUXeCF', 'Tipsy'))
    .toBe('https://open.spotify.com/artist/0OdUWJ0sBjDrqHygGUXeCF');
});

test('no id falls back to a search link, never to nothing', () => {
  expect(spotifyUrl(null, 'Tipsy'))
    .toBe('https://open.spotify.com/search/Tipsy/artists');
});

test('names are URL-encoded', () => {
  expect(spotifyUrl(null, 'Sigur Rós')).toContain('Sigur%20R%C3%B3s');
});

test('apple falls back to search too', () => {
  expect(appleUrl(null, 'Tipsy')).toBe('https://music.apple.com/search?term=Tipsy');
});
```

- [ ] **Step 2: Run and confirm failure**

Run: `cd frontend && npm test -- dspUrls`
Expected: FAIL — module not found.

- [ ] **Step 3: Write `dspUrls.ts`**

```ts
/**
 * Compose streaming URLs from the platform id tails the artifact carries.
 *
 * The artifact stores ids, never URLs (`L4-D2`), so the hostname lives here
 * and a scheme change is a frontend edit rather than a graph rebuild.
 *
 * A null id NEVER means "no button". It means a search link: the app routes
 * to obscure artists, so the missing-id case is disproportionately the
 * population this exists to serve, and a card that shows one service and
 * silently drops the other reads as the artist being absent from it.
 */
export function spotifyUrl(id: string | null, name: string): string {
  return id
    ? `https://open.spotify.com/artist/${id}`
    : `https://open.spotify.com/search/${encodeURIComponent(name)}/artists`;
}

export function appleUrl(id: string | null, name: string): string {
  return id
    ? `https://music.apple.com/artist/${id}`
    : `https://music.apple.com/search?term=${encodeURIComponent(name)}`;
}
```

- [ ] **Step 4: Run and confirm pass**

Run: `cd frontend && npm test -- dspUrls`
Expected: PASS, all four.

- [ ] **Step 5: Write `StreamingLinks.test.tsx`, then the component**

```tsx
test('both services always render, id or not', () => {
  render(<StreamingLinks artist={{ ...base, spotifyId: null, appleId: 'x' }} />);
  expect(screen.getByRole('link', { name: /spotify/i })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /apple/i })).toBeInTheDocument();
});

test('links open in a new tab without leaking the referrer', () => {
  render(<StreamingLinks artist={base} />);
  const link = screen.getByRole('link', { name: /spotify/i });
  expect(link).toHaveAttribute('target', '_blank');
  expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'));
});
```

Text labels only — no logos. `rel="noopener noreferrer"` on both.

- [ ] **Step 6: Add the fields to `types.ts` and render in `ArtistCard.tsx`**

`Artist` gains `spotifyId: string | null`, `appleId: string | null`, `facts: ArtistFacts | null`
(camelCase — the API layer already maps snake_case at the boundary; **check how
`candidateCount` is mapped and follow it**).

- [ ] **Step 7: Run the frontend suite and the typecheck**

Run: `cd frontend && npm test && npm run build && npm run lint`
Expected: all PASS.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/lib/dspUrls.ts frontend/src/lib/dspUrls.test.ts \
        frontend/src/components/StreamingLinks.tsx frontend/src/components/StreamingLinks.test.tsx \
        frontend/src/api/types.ts frontend/src/components/ArtistCard.tsx
git commit -m "L4-T10: streaming links with a search fallback

Both services always render; a missing id degrades to search, never to an
absent button. Text labels only -- logos pull in brand guidelines."
```

---

## Task `L4-T11`: frontend — the info card, and the deploy note

**Files:**
- Create: `frontend/src/components/ArtistInfo.tsx`, `.test.tsx`
- Modify: `frontend/src/components/ArtistCard.tsx`
- Modify: `infra/README.md` (deploy note)

**Interfaces:**
- Consumes: `Artist.facts` (`L4-T9`, `L4-T10`), and `artist.disambiguation`, which is **already
  on the wire and already rendered** — but only in the search dropdown
  (`ArtistSearch.tsx:139`), never on a journey card. Surfacing it needs no rebuild.
- Produces: nothing downstream.

**`L4-D3`: render only what is present, with no placeholder rows.** A missing life span shows
nothing, not "Unknown". The target reading is the spec's own example — *"German duo ·
1993–2008"*.

- [ ] **Step 1: Write the failing test**

```tsx
test('renders a compact fact line', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: 'Group', area: 'Germany', begin: '1993', end: '2008', ended: true } }} />);
  expect(screen.getByText(/Germany/)).toBeInTheDocument();
  expect(screen.getByText(/1993–2008/)).toBeInTheDocument();
});

test('an active artist shows an open-ended span', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    begin: '1995', end: null, ended: false } }} />);
  expect(screen.getByText(/1995–/)).toBeInTheDocument();
});

test('nothing renders when there are no facts', () => {
  const { container } = render(<ArtistInfo artist={{ ...base, facts: null }} />);
  expect(container).toBeEmptyDOMElement();
});

test('partial facts render without placeholder rows', () => {
  render(<ArtistInfo artist={{ ...base, facts: { type: 'Person' } }} />);
  expect(screen.queryByText(/unknown/i)).not.toBeInTheDocument();
});

test('the disambiguation is shown on the card', () => {
  render(<ArtistInfo artist={{ ...base, disambiguation: 'US electronic lounge band' }} />);
  expect(screen.getByText(/US electronic lounge band/)).toBeInTheDocument();
});
```

- [ ] **Step 2: Run and confirm failure**

Run: `cd frontend && npm test -- ArtistInfo`
Expected: FAIL — module not found.

- [ ] **Step 3: Write the component.** Join present parts with `·`, matching the existing card
      typography (`text-[12.5px]`, `--color-muted`). Use an en dash for the span.

- [ ] **Step 4: Render it in `ArtistCard.tsx`** beneath the track title line, above the `LUX-3`
      control.

- [ ] **Step 5: Run everything**

Run: `cd frontend && npm test && npm run build && npm run lint`
Expected: all PASS.

- [ ] **Step 6: Run the e2e suite** — it needs the API on :8000 with the new artifact.

```bash
# terminal 1
cd api && UV_LINK_MODE=copy ARTISTPATH_GRAPH=../builder/scratch/graph-lux4.bin \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
# terminal 2
cd frontend && npm run test:e2e
```
Expected: PASS. **`e2e/responsive.spec.ts` measures `data-testid="artist-name"`** and must not
regress — the info line adds height to every card, so check the 390px case explicitly.

- [ ] **Step 7: Write the deploy note in `infra/README.md`**

Two things a deployer must know, and the first is new:

1. **The artifact changed.** `ARTISTPATH_GRAPH_SHA256` must be updated from
   `graph-lux4.bin`'s **manifest sidecar** — `DEP-24`, never transcribed by hand. A wrong value
   means the service refuses to boot, which is the design.
2. **Do not deploy under a stale image tag.** The running image is still `994c203`, built before
   the `CXR-` revert, and its baked-in `ApiConfig.graph_path` default names the **rejected**
   artifact. Any image built from HEAD fixes it.

- [ ] **Step 8: Queue the use-the-app test** in `docs/superpowers/TEST-QUEUE.md`, in the
      owner-facing voice that file uses — what to press, what "wrong" looks like, and what is
      expected and not a fault.

- [ ] **Step 9: Commit**

```bash
git add frontend/src/components/ArtistInfo.tsx frontend/src/components/ArtistInfo.test.tsx \
        frontend/src/components/ArtistCard.tsx infra/README.md docs/superpowers/TEST-QUEUE.md
git commit -m "L4-T11: the structured info card, and the deploy note

Renders only present fields with no placeholder rows (L4-D3). Surfaces the
disambiguation on a journey card for the first time -- it was already on the
wire and rendered only in the search dropdown."
```

---

## `LUX-E2` — owed, and BLOCKED. Read before `L4-T11`.

**`LUX-E2` informs this feature's design** — its threshold is *any field below 50% in the lower
half needs a designed empty state, not a blank line* — which is exactly what `L4-D3` decides by
assertion instead of by measurement.

**It cannot be run as written.** The 120-pair `TAS-` sample it names is damaged on the served
map, and the attrition falls almost entirely on the obscure classes — precisely the population
the threshold is stated over. Running it would return the same undefined read `LUX-E4` did.

**Precondition: redraw the sample against the adopted artifact.** That is a deferral with a
condition recorded in `NEXT.md`, and its condition is now due.

**How this plan proceeds without it:** `L4-D3` ships "render only what is present", which is the
cheapest empty state and matches `LUX-3`'s accepted position. If `LUX-E2` later measures a field
below 50% in the lower half, the consequence is a **designed** empty state for that field — a
frontend change to `ArtistInfo.tsx`, not a rebuild. **This is why `L4-D3` is safe to take now**:
the artifact carries the data either way, and only the rendering is in question.

---

## Self-review

**Spec coverage.** §4.1 → `L4-T2`, `L4-T3`, `L4-T4`, `L4-T10`, `L4-T11`. §4.2 → `L4-T2`
(extraction), `L4-T11` (`disambiguation` surfaced). §4.3 → the artifact route is taken; the
standing obligation is carried in both new module docstrings. §4.4 → discharged by `LUX-E1`; the
pins are Global Constraints and the factor table in `L4-T7`. §4.5, §4.6 → recorded as out of
scope and in `L4-T4`'s docstring. §4.7's file table → the File Structure table, plus
`acceptance.py`, which §4.7 could not have known about. §5: `LUX-E3` → `L4-T2` step 7;
`LUX-E5` → `L4-T7` step 5; `LUX-E2` → its own section, blocked with the reason.

**Gaps found and closed while writing.** (a) §4.7's table omits `acceptance.py`, which now
blocks the rebuild — `L4-T1` added. (b) §4.7 omits the deploy's checksum update — `L4-T11`
step 7. (c) Nothing in the spec says `ArtistOut` appears in three wire positions — `L4-T9` says
so and tests the `bypassed` one, which would otherwise regress invisibly.

**Type consistency.** `spotify_ids`/`apple_ids`/`artist_facts` are the APG1 keys and the `Graph`
fields throughout; the API exposes singular `spotify_id`/`apple_id`/`facts` on `ArtistOut`; the
frontend uses camelCase `spotifyId`/`appleId`/`facts`. The plural/singular and snake/camel shifts
are deliberate, happen at named boundaries, and match `deezer_ids` → `candidate_count` →
`candidateCount` precedent.

**Placeholder scan.** Two intentional `<fill from …>` markers, both in `L4-T3`/`L4-T4` step 4,
where the value is a sha that does not exist until the previous step runs and the step says how
to obtain it.
