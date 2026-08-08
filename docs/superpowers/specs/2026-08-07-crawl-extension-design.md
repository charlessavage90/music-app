# Crawl extension — design (`CEX-`)

**Role: ACTIVE, governing for the `CEX-` track.** Written 2026-08-07, **substantially revised
2026-08-08** — see §10, which records every change and why. Supersedes nothing.

**Owns no figures.** Two directories own them and are cited, never restated:
[`builder/analysis/2026-08-07-cex-frontier/`](../../../builder/analysis/2026-08-07-cex-frontier/README.md)
(the pre-extension baseline, and the `CEXR-1` seeding tests) and
[`builder/analysis/2026-08-08-cxs-growth/`](../../../builder/analysis/2026-08-08-cxs-growth/README.md)
(what growth does to the obscure tail). Project status stays in [`NEXT.md`](../NEXT.md).

**Review of record:**
[`builder/analysis/2026-08-07-cex-frontier/2026-08-07-cex-design-review.md`](../../../builder/analysis/2026-08-07-cex-frontier/2026-08-07-cex-design-review.md)
(`CEXR-`), by an independent session with the source open. **Fourteen findings; all fourteen
are dispositioned in §10.**

**Prefixes collision-checked across every ref:** `CEX-` (this), `CEXR-` (the review), `CXS-`
(the growth probe). `CXT-`, `FRT-` and `SEED-` remain reserved and unused.

**Owner decision, 2026-08-08: the extension proceeds, conditional on the archive snapshot
(`CEX-0`).** The seeding half is removed from the track — see §3.

---

## §0 — Held constant, and why each is genuinely constant

Per `CLAUDE.md`'s factor-table rule, this catches the knob **nobody turned** — a term inert in
the baseline for a reason the intervention removes.

**Genuinely constant, and safe:**

| Held | Why the intervention cannot change it |
|---|---|
| `algorithm` = ALG-B | Fixed per-invocation and guarded on the crawl side: `crawl.py:206` refuses to resume a checkpoint written under another algorithm (`RC-H3`). **⚠ There is no counterpart on the build side — see `CEX-R5`.** |
| `cap_strategy` = `trimmed_union`, `union_top_j` = 50, `union_degree_ceiling` = 50 | Build-time knobs, untouched. The cap question is a **separate track** (§9). |
| `similarity_damping`, every `ApiConfig` cost weight | The API is not modified. No router change is in scope. |
| The APG1 format | Adds no key. |

**⚠ NOT constant, though it looks it. This is the section that matters:**

- **Every artist's `pop_raw` changes.** It is score-weighted in-degree over rescaled scores
  (`pipeline.py:365-375`), so enlarging the population changes it for **every existing
  artist**. Both depth-graduated devices in the cost function — `floor_raw` and `w_jump` — are
  priced in that currency.
- **The p99 similarity rescale moves, and it prices the router's primary term** (`CEXR-3`).
  `rescale_scores` (`pipeline.py:94-110`) normalises on the 99th percentile of **this build's**
  edges, feeding `w_sim·(1−similarity)`. **Two artists whose raw co-occurrence is identical in
  both archives get a different similarity in the new artifact.** Adding millions of
  low-co-occurrence edges pulls the percentile down, raises every rescaled similarity, and
  pushes more edges to saturate at exactly 1.0 — the "free similarity" defect `config.py:169-177`
  carries as open. **In plain terms: the extension may make more hops free, so more of the route
  is decided by tie-breaks than by similarity.** `CEX-M1` exists to measure it.
- **`fame_lb_pctl` is ranked against the served artifact's own population**, so every percentile
  shifts even where raw fame is unchanged. The `known` ramp is priced on it.
- **`degree_hub_penalty` is top-1%-*by-degree*** and its membership is recomputed.
- **The largest-connected-component prune.** It costs 454 artists today. **Measured as benign
  at every population up to 75,000** (`CXS-C2`: 0.06 % of the tracked cohort), but that is a
  measurement at or below today's size, not a guarantee at 117,302.

**Consequence, stated once so no later section can ignore it: no per-artist figure is comparable
between the adopted artifact and any `CEX-` candidate.** See §5.

---

## §1 — What this is

The owner asked to expand the crawl beyond 75,000, for two reasons: **known missing artists**
and **headroom**. Investigation resolved these very differently.

- **`CEX-R1` — growth cannot reach an artist nobody names.** Goose has zero inbound references
  across all 75,000 archived responses; both artists it points at are crawled and shipped and
  neither points back. A breadth-first snowball reaches only artists someone else lists.
  **Raising the target never reaches Goose.**
- **`CEX-R2` — the crawl is stuck, and stuck silently.** `ULC-F3`, reproduced directly:
  `discovered` and `done` are both exactly 75,000, so `crawl.py:115` rebuilds an empty queue,
  `crawl.py:126`'s loop never runs, and the process logs `0 processed` and exits 0. **The
  failure reads as success.** This is the defect the track exists to fix.
- **`CEX-R3` — one of the two "missing" artists was never missing.** Commander Cody is crawled
  and shipped with 4 inbound references. `ArtistSearch.search` (`api/…/search.py:35-39`) is
  literal prefix-or-substring; the map spells him *"& His Lost Planet Airmen"* against the
  queried *"and the Lost Planet Airmen"*. **A search defect, out of scope here** (§9).
- **`CEX-R4` — seeding does not work either, and no selectable cap rule changes that.**
  Established by build, not derivation: see §3.
- **`CEX-R5` — the repo contradicts itself about which algorithm is adopted.** `config.py:17`
  calls ALG-E "the adopted 75k archive's algorithm", but `ApiConfig.graph_path`
  (`api/…/config.py:24`) serves `graph-msw-tu50.bin`, whose manifest records `contribution_3`
  — **ALG-B**. `config.py:17` is the stale side. `config.py:59`, `cli.py:274` and `cli.py:314`
  are downstream of the same rot. **A live defect independent of this track, fixed by `CEX-5`.**

**So: headroom is the crawl. Named artists are not reachable by any lever in this track.**

---

## §2 — The `ULC-F3` fix

### `CEX-1` — `refrontier`, a reconstruction command

New module `builder/src/artistpath_builder/frontier.py`, exposed as
`artistpath-build refrontier`.

- **Parse through the crawler's own `source.parse()`**, as `Crawler._neighbours` does
  (`crawl.py:165-170`). A private parser could drift from discovery.
- **Enumerate through `similar_prefix(config, source)`** (`pipeline.py:119-132`) — the function
  `fame` and `build` already share (`CEXR-7a`). A naive `archive.keys()` walk ingests another
  algorithm's sub-tree *and* the `fame/` keys (`fame.py:97`). Be its **third consumer, not a
  fourth definition**; that divergence class is what `test_pipeline_mirrors.py` guards.
- **UNION into `discovered`, never replace it** (`CEXR-7b`). `discovered ⊇ done` is
  load-bearing — `crawl.py:115` is a set difference against it. The baseline census shows
  **8 artists that were crawled but appear in no response's neighbour list**; a replacing
  rewrite drops them and silently breaks the invariant. *(Goose is the same shape as those
  eight: crawled-or-not, nobody names them.)*
- **Carry the `RC-H3` algorithm guard** (`crawl.py:206`).
- **Back the checkpoint up before rewriting.** 6 MB, and the only record of 75,000 fetches.
- **Idempotent**, written with the sorted, `algorithm`-stamped shape of `_save_checkpoint`
  (`crawl.py:218-229`).

### `CEX-2` — the root cause

`crawl.py:141-146` stops **recording** neighbours once discovery reaches the target. Record
always; bound **fetching** instead, at `crawl.py:126`:

```python
while queue and len(self._done) < self.config.target_artist_count:
    ...
    for neighbour in self._neighbours(payload, mbid):
        if neighbour not in self.discovered:
            self.discovered.add(neighbour)
            queue.append(neighbour)
```

**⚠ This redefines `target_artist_count` (`config.py:64`) from a cap on artists *discovered* to
a cap on artists *fetched*, and switches `<=` to `<`.** Both are intended.

**`CEXR-12`, and it is the clean explanation of why `CEX-T2` goes red:** the existing condition
`len(self.discovered) <= target` is **always true**, because the inner break capped `discovered`
at exactly `target`. Today's crawl only ever stops when the queue empties. **`CEX-2` is not
relocating a bound — it is adding the first one that can fire.**

**Blast radius:** sweep every caller of `--target` and `target_artist_count` and era-pin any
frozen probe depending on the old meaning (`CEX-T5`). Note `--target 0` is silently ignored
(`cli.py:65` uses `if target:`) — `CEXR-13`.

### `CEX-3` — the refusal

After the queue is built and the bootstrap seeded, before the main loop:

```python
if not queue and len(self._done) < self.config.target_artist_count:
    raise FrontierExhausted(...)   # names `refrontier` as the remedy
```

**The highest-value component in the track.** `ULC-F3`'s damage was never that the crawl
stopped — it is that it stopped while printing something indistinguishable from success.

**⚠ `CEXR-5` — it CAN misfire, and the original design's argument was wrong.** That argument
("a genuinely exhausted graph empties its queue *during* the run") does not survive the
checkpoint: `crawl.py:115` rebuilds the queue on every invocation, so a run that legitimately
exhausted the graph saves a checkpoint indistinguishable from the `ULC-F3` state. It would then
raise, recommend `refrontier`, and `refrontier` would faithfully reconstruct the same empty
frontier and change nothing. Two real cases: an idempotent re-run after a completed extension,
and a re-run whose seeds are already in `discovered`.

**Remedy, adopted:** record the terminal condition in the checkpoint — an `exhausted` flag
written when the loop exits with an empty queue — and have the refusal read it.

**`CEXR-14`:** catch `FrontierExhausted` at the CLI boundary (`cli.py:144`) and print the
remedy. A refusal that surfaces as a traceback half-defeats its own purpose.

### `CEX-4` — checkpoint durability

`_save_checkpoint` (`crawl.py:218-229`) is a bare `write_text`, rewritten ~85 times during a
four-hour run. Temp-file-plus-rename (`CEXR-10`). The file also **grows** during the run now,
which is the point of `CEX-2`.

### `CEX-5` — resolve the ALG-E/ALG-B contradiction

Fix `config.py:17`'s comment, and `cli.py:274` / `cli.py:314` ("default config's (mutual_knn
until adoption)", stale since the `MSW-` adoption). **Does not change the `algorithm` default** —
that is the re-crawl decision and it is the owner's (`config.py:56-58`).

---

## §3 — Seeding is REMOVED from this track

**The original §3 argued that a seeded Goose would survive because `trimmed_union` keeps an edge
if either endpoint ranks the other in its top-`j`. That was half the algorithm, and the
conclusion was wrong.** `trimmed_union_cap` (`graph.py:228-237`) then trims every node to the
degree ceiling with **no floor protecting a node's last edge**.

**Falsified twice, by build rather than by argument** (figures owned by the `cex-frontier`
directory):

1. **Matched pair at the adopted cap.** Goose seeded into the archive, everything else held:
   the built graph was **identical** — same node count, same edge count, Goose absent. Seeding
   changed the graph by **zero nodes and zero edges**.
2. **Three ceilings.** Goose is absent at `TUw-50-50`, `TUw-50-100` **and** `TUw-100-100` — the
   last being the most permissive selectable rule, which Track B measured as recovering all but
   6 of the 538 artists the adopted rule excludes. **The ceiling was never the binding
   constraint.**

**Why, in plain terms:** Goose's two connections are faint against extraordinarily crowded
company — 15 against an artist whose hundredth-best is 62, and 11 against one whose
hundredth-best is 770. Doubling the slots does not help when you do not qualify for any of them.
**Any rule loose enough to keep Goose's link keeps thousands of other faint links to those same
popular artists — which is what makes journeys run through the big names, and is the mechanism a
blind listening test condemned.**

**`CEX-T6` is withdrawn** (it asserted Goose would appear). No replacement: the question is
answered, not deferred.

---

## §4 — Sequence, and what refuses at each step

| # | Step | Guard if skipped |
|---|---|---|
| **0** | **Snapshot the archive tree** (1.2 GB; 486 GB free) **and record the newly-added MBID set** | **Owner precondition, 2026-08-08.** The crawl appends into the same algorithm-keyed tree, and afterwards today's graph **cannot be rebuilt from source**. The snapshot is what makes this reversible. |
| 1 | `CEX-1` `refrontier` | — |
| 2 | `CEX-2`–`CEX-4` + tests | — |
| 3 | `CEX-5` doc/comment fix | — |
| 4 | Crawl to 117,302 on ALG-B, `--algorithm` **explicit** | `config.py:59` defaults to **ALG-E** → extends the wrong archive |
| 5 | `fame` over the extended archive, `--algorithm` **explicit** | `require_fame` → **build refuses**; and `_config` defaults to ALG-E → **covers the wrong tree** |
| 6 | Re-census the drop lists over the new population, `--algorithm` **explicit** | `ULC-F1` → **build refuses** (`unlistenable` only — see below) |
| 7 | Build, `--algorithm` **explicit** | **`check_acceptance` rejects on BOTH bounds** |
| 8 | Verification, incl. `CEX-M1` | — |
| 9 | Adoption | — |

**`CEXR-2` — `--algorithm` is required at steps 4, 5, 6 AND 7, not step 4 alone.**
`similar_prefix` (`pipeline.py:119-132`) selects the tree from `config.algorithm`, and both
`archive_artists` (`cli.py:160`) and `build_from_archive` (`cli.py:207`) go through it;
`_config` (`cli.py:67-75`) defaults to `PRODUCTION_ALGORITHM`. **There is no `RC-H3` counterpart
on the build side**, and the drop lists are algorithm-keyed too (`pipeline.py:254,273,292`), so
a defaulted build loads ALG-E's censused lists and could pass acceptance while describing a
population nobody asked for. **Consider a build-side guard rather than relying on the operator.**

**`CEXR-6` — only `unlistenable` is population-guarded. Three siblings are not:**

- `load_drop_mbids` (`pipeline.py:254`) and `load_featured_credit_drop_mbids`
  (`pipeline.py:273`) are algorithm-keyed frozen snapshots. The algorithm is unchanged after the
  extension, so they load the same 75k-era lists and **evaluate none of the new artists,
  silently.**
- `load_deezer_ids()` (`pipeline.py:446`) takes **no population argument at all**. Every new
  artist gets `""` and falls back to name-based clip resolution — the `BYP-13` failure. **Clip
  identity coverage drops across the artifact with nothing objecting.**

**Step 6 resolved (the original was internally inconsistent).** `pipeline.py:279-284` states all
three drop classes are strict subsets and applying all three is identical to applying
`unlistenable` alone; the baseline census bears this out (`on_a_drop_list` equals the
`unlistenable` list size exactly). **So step 6 re-censuses `unlistenable` only**, and the subset
relation is **re-verified over the new population** rather than inherited.

**`CEXR-4` — acceptance rejects on TWO bounds.** `check_acceptance` collects every violation
before raising (`acceptance.py:251-266`): nodes `(47_000, 71_000)` **and** edges
`(1_050_000, 1_580_000)` (`acceptance.py:170-171`). Under a non-reciprocal cap the **edge**
ceiling is breached by the wider margin. **§6's owner decision is about the artifact's whole
shape band, two numbers, not the node ceiling alone.**

**Cost.** Step 4 is ~4 hours (75,000 took ~7.5 h). Step 5 is **seconds** — `fetch_fame` batches
at `MAX_PER_REQUEST = 1000` (`fame.py:57,139`), so the new artists are a few dozen POSTs.
**Step 6 has no rate basis yet and must be costed before the plan is executed (`CEXR-9`):** the
un-listenable keep-check is per-artist against rate-limited services, and `ULC-F2`'s coverage
store means you pay only for genuinely new artists — **which is the entire extension.** If it
lands in hours, §6's seams may move.

**`CEXR-11` — the target restates the frontier rather than bounding it.** 75,000 + 42,302 =
117,302. Two consequences: permanent fetch failures (`crawl.py:193-196`) keep `_done` below
target, so the loop dips into **newly discovered** artists to make up the shortfall, and the
final population's composition therefore depends on the failure count.

**⚠ One expectation, on the record before the run, and NOT refuted by `CXS-`.** The `ULC-`
results (§313 there) expect the class of artists with **nothing of their own to play** to grow,
because discovery pushes further into obscurity. **`CXS-` measured connectedness, not
listenability — different quantities, and neither speaks to the other.** A larger drop list at
step 6 is the predicted outcome, not a fault.

---

## §5 — The comparison is confounded, and no read may pretend otherwise

| Variant | Population | Drop list | Fame coverage | Deezer coverage | p99 scale | Acceptance | Isolating baseline |
|---|---|---|---|---|---|---|---|
| Adopted (`graph-msw-tu50`) | 75,000 | censused at 75,000 | 75,000 | 75,000-era | its own | `(47k,71k)`/`(1.05M,1.58M)` | — |
| `CEX-` candidate | 117,302 | re-censused | 117,302 | **unchanged, so thinner** | moves | widened (owner's) | **none exists** |

**No one-knob baseline exists and none can be built cheaply** — re-censusing is a function of
the population. Conclusions this comparison is **barred from supporting**:

- **It cannot attribute any change to "more artists".** Six columns move.
- **It cannot compare any per-artist figure** — `pop_raw`, `fame_lb_pctl`, `degree_hub_penalty`
  and every rescaled similarity are recomputed over a different population (§0).
- **It cannot be read as evidence on path quality** without a listening test, and none is
  scheduled here.

**What it CAN support:** whether specific named artists are reachable; whether the
nothing-to-play class grew as expected; **clip-identity coverage** (`CEXR-6`); and whether the
app still works.

**`CEX-M1` (new, from `CEXR-3`):** log the **p99 scale and the saturated-edge share** at build
time and compare the two builds. One line; converts an unmeasured risk into a figure. **If the
saturated share rises materially, that is a path-quality change and therefore the owner's, not
a build-log footnote.**

**`ml-graph-analyst` is recommended before step 9** — a comparison spanning graphs of different
structure is exactly its remit. Recommending is a session's job; dispatching is the owner's.

---

## §6 — Seams and owner stops

**Two owner stops.**

- **After step 7 — the acceptance band.** The build *will* be rejected, on **both** bounds.
  `acceptance.py:139` states a new crawl is a new artifact identity, not a bound to widen
  quietly; `MSW-G3` is the worked precedent, and there too the recalibration was the owner's.
  **A session must not widen these.**
- **After step 8 — adoption.**

**Two handoff seams**, at steps 4 and 7. At ~11 tasks this track needs them.

---

## §7 — Checks, split by kind (`CEXR-8`)

**Regression tests — kept, fixture-backed, run in CI:**

| | Condition |
|---|---|
| **`CEX-T2`** | Crawl a fixture archive to a target; assert `discovered` is strictly larger than `done`. **Shown red against today's code before it is kept.** |
| **`CEX-T3`** | `FrontierExhausted` raises on a `discovered == done` checkpoint with a raised target; **does not** raise when seeding supplies new work; **and does not raise when the checkpoint's `exhausted` flag is set** (`CEXR-5`). |
| **`CEX-T4`** | `refrontier` is idempotent, refuses on algorithm mismatch, and **unions rather than replaces** — asserting `done ⊆ discovered` after the rewrite (`CEXR-7b`). |
| **`CEX-T7`** | `refrontier` enumerates via `similar_prefix` and ingests neither another algorithm's sub-tree nor `fame/` keys (`CEXR-7a`). |

**One-shot operational gates — dated, executed once, recorded, never in CI:**

| | Condition |
|---|---|
| **`CEX-G1`** | `refrontier` reproduces the baseline census's `frontier_size` **exactly**. **Must run BEFORE step 4** — the archive is gitignored and this can never pass again once extended. *(Was `CEX-T1`.)* |
| **`CEX-G2`** | The `--target` caller sweep is complete and every frozen probe depending on the old meaning is era-pinned. *(Was `CEX-T5`.)* |

**`CEX-T6` is withdrawn** — see §3.

---

## §8 — Claims check

Every file, function and config value named above was grepped against the repo on
2026-08-07/08 and resolves: `crawl.py:115,120-123,126,141-146,165-170,193-196,206,218-229`;
`config.py:17,56-59,64,97,126,169-177`; `acceptance.py:139,170-171,251-266`;
`fame.py:57,97,128,139`; `cli.py:65,67-75,144,160,207,274,314`;
`pipeline.py:94-110,119-132,254,273,279-284,291-309,355-403,446`; `graph.py:21,228-237`;
`api/…/search.py:35-39`; `api/…/config.py:24`.

**Not yet built — dependencies, not claims:** `frontier.py`, `refrontier`,
`FrontierExhausted`, the checkpoint `exhausted` flag, and `CEX-M1`'s build-time logging.

---

## §9 — Out of scope, deliberately

- **Seeding and the cap rule.** Removed (§3). Whether to change the cap so faintly-connected
  artists can persist is the owner's, touches the adopted `MSW-` package, and is **its own
  track**. Track B priced both sides: ceiling 100 cuts exclusion 538 → 34 and raises famous-pair
  hub transit +75…+152 %.
- **The search defect (`CEX-R3`).** Its own track, needs no rebuild, and is the **only** lever
  that addresses "I cannot find this artist" for artists that are present.
- **`DD-F1`.** Famous journeys never routing through anyone obscure is a **router** finding;
  Track B force-connected famous artists to obscure partners and the router took none of them.
  **No crawl size or cap setting addresses it.**
- **Widening the acceptance bounds.** The owner's, at step 7.
- **`ULC-F4`.** Untouched.

---

## §10 — Amendment log, 2026-08-08

**Two claims of this document were falsified, both by measurement, and both were mine.**

| Change | Why |
|---|---|
| **§3 rewritten; seeding removed; `CEX-T6` withdrawn** | `CEXR-1`. The original argued from the union step and ignored the trim. Falsified by a matched-pair build (zero-node, zero-edge delta) and again at three ceilings. |
| **§4 gains step 0, the archive snapshot** | Owner precondition, 2026-08-08. Makes the one-way append reversible. |
| **§0 gains the p99 rescale row; §5 gains `CEX-M1`** | `CEXR-3`. The largest population-dependent term, and it prices the router's primary term. |
| **§4/§6 name both acceptance bounds** | `CEXR-4`. The original named the node ceiling only; the edge ceiling breaches by more. |
| **§2 `CEX-3` gains the `exhausted` flag; `CEX-T3` extended** | `CEXR-5`. The original's "it cannot misfire" argument was wrong across runs. |
| **§4 gains the unguarded-siblings warning; step 6 resolved to `unlistenable` only** | `CEXR-6`. Also adds clip-identity coverage to §5's readable list. |
| **§2 `CEX-1` gains scope and union constraints; `CEX-T4` gains `done ⊆ discovered`; `CEX-T7` added** | `CEXR-7`. The 8 crawled-but-unnamed artists make the union requirement concrete, and `CEX-G1` alone could not have caught it. |
| **§7 split into regression tests and one-shot gates; `T1`→`G1`, `T5`→`G2`** | `CEXR-8`. |
| **§4 step 6 flagged as uncosted** | `CEXR-9`. The original gave step 4 a rate basis and step 6 an adjective. |
| **`CEX-4` added (atomic checkpoint write)** | `CEXR-10`. |
| **§4 gains the target/frontier note** | `CEXR-11`. |
| **§2 `CEX-2` records that the old bound never fired** | `CEXR-12`, `CEXR-13`. |
| **§2 `CEX-3` gains CLI-boundary handling** | `CEXR-14`. |
| **`CEX-R4`, `CEX-R5` added; `CEX-5` added** | The seeding falsification, and the ALG-E/ALG-B contradiction the review surfaced (`CEXR-2`). |
| **§4's drop-share expectation explicitly NOT refuted by `CXS-`** | `CXS-` measured connectedness; the `ULC-` expectation is about listenability. Recorded so a reader does not read one as the other. |

**What `CXS-` changed, and it is the reason this track proceeds:** an earlier draft of this
session's advice held that growth would crowd the hubs and thin the obscure tail. **Measured, it
does the opposite** — the median less-famous artist gains connections monotonically as the crawl
grows, and hub saturation *falls*. The figures are owned by the `cxs-growth` directory. **One
caveat travels with them and must not be dropped: artists arriving with exactly one connection
quadrupled, and such an artist can end a journey but never appear in the middle of one.**
