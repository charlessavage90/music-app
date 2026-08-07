# Crawl extension — design (`CEX-`)

**Role: ACTIVE, governing for the `CEX-` track.** Written 2026-08-07. Supersedes nothing.
It **owns no figures**: the baseline census is owned by
[`builder/analysis/2026-08-07-cex-frontier/`](../../../builder/analysis/2026-08-07-cex-frontier/README.md)
and is cited here, never restated. Project status stays in [`NEXT.md`](../NEXT.md).

**Prefix `CEX-` collision-checked across every ref (`refs/remotes` + `refs/heads`, `*.md`) —
free.** So were `CXT-`, `FRT-` and `SEED-`, which are therefore available and unused.

---

## §0 — Held constant, and why each is genuinely constant

Per `CLAUDE.md`'s factor-table rule, this section exists to catch the knob **nobody turned**
— a term inert in the baseline for a reason the intervention removes.

**Genuinely constant, and safe:**

| Held | Why the intervention cannot change it |
|---|---|
| `algorithm` = ALG-B | Fixed per-invocation and guarded: `crawl.py:206` refuses to resume a checkpoint written under another algorithm (`RC-H3`). |
| `cap_strategy` = `trimmed_union`, `union_top_j` = 50, `union_degree_ceiling` = 50 | Build-time knobs, untouched by this track. |
| `similarity_damping`, every `ApiConfig` cost weight | The API is not modified. No router change is in scope. |
| The APG1 format | Adds no key. `fame_lb` and `deezer_ids` already exist as additive keys. |

**⚠ NOT constant, though it looks it — and this is the section that matters:**

- **Every artist's `pop_raw` changes.** Popularity here is score-weighted in-degree computed
  over the graph itself, then log-scaled. Enlarging the population changes the in-degree of
  **every existing artist**, so `pop_raw` is not comparable across the two artifacts. Both
  depth-graduated devices in the cost function — `floor_raw` and `w_jump` — are priced in
  that currency.
- **`fame_lb_pctl` is ranked against the served artifact's own population**, so every
  percentile shifts even for artists whose raw fame is unchanged. The `known` ramp is priced
  on it.
- **`degree_hub_penalty` is top-1%-*by-degree*** and its membership is recomputed. A different
  set of artists is penalised.
- **The largest-connected-component prune is near-inert today for a reason this track
  removes.** It costs 454 artists now (analysis README). Extension pushes into obscurity,
  where weakly-linked islands live, so this term can wake up. It is the clearest dormant
  term here and must be measured, not assumed.

**Consequence, stated once so no later section can quietly ignore it: no per-artist figure is
comparable between the adopted artifact and any `CEX-` candidate**, and no side-by-side path
comparison isolates a single knob. See §5.

---

## §1 — What this is, and the two levers

The owner asked to expand the crawl beyond 75,000, for two stated reasons: **known missing
artists**, and **headroom** (the drop filters remove a large share of what is crawled).

The baseline census establishes that these need **two different levers**, and that only one of
them is a crawl:

- **`CEX-R1` — growth cannot reach an artist nobody names.** Goose (the Norwalk jam band) has
  zero inbound references across all 75,000 archived responses. Its only two ALG-B neighbours
  are crawled and shipped, and neither points back. Similarity is not mutual, so a
  breadth-first snowball reaches only artists someone else lists. **Raising the target never
  reaches Goose. Seeding does.**
- **`CEX-R2` — the crawl is stuck, and stuck silently.** `ULC-F3`, reproduced directly:
  `discovered` and `done` are both exactly 75,000, so `crawl.py:115` rebuilds an empty queue,
  `crawl.py:126`'s loop never runs, and the process logs `0 processed` and exits 0. **The
  failure reads as success.**
- **`CEX-R3` — one of the two "missing" artists was never missing.** Commander Cody is
  crawled and shipped. `ArtistSearch.search` (`api/…/search.py:35-39`) is literal
  prefix-or-substring over a normalised name; the map spells him *"& His Lost Planet Airmen"*
  and the query said *"and the Lost Planet Airmen"*, so it returns zero. **Out of scope here**
  — recorded so this track is not credited with fixing it, and so the search fix is not
  bundled into a rebuild it does not need.

**Headroom is the crawl. Named artists are seeding. Search is neither.**

---

## §2 — The `ULC-F3` fix

Three components. The third is the one that matters most.

### `CEX-1` — `refrontier`, a reconstruction command

New module `builder/src/artistpath_builder/frontier.py`, exposed as
`artistpath-build refrontier`. Reads every archived response, unions the neighbours, writes
the true `discovered` set back to the checkpoint.

- **It must parse through the crawler's own `source.parse()`**, reached the same way
  `Crawler._neighbours` reaches it (`crawl.py:165-170`). A private parser could drift from
  discovery, and a frontier that disagrees with the crawler is worse than no frontier.
- **It carries the `RC-H3` algorithm guard** (`crawl.py:206`) and refuses a checkpoint written
  under another algorithm.
- **It backs the checkpoint up before rewriting.** That 6 MB file is the only record of 75,000
  completed fetches and there is no second copy.
- **It is idempotent**, and writes with the sorted, `algorithm`-stamped shape
  `_save_checkpoint` already uses (`crawl.py:218-229`), so determinism is preserved.

### `CEX-2` — the root cause

`crawl.py:141-146` stops **recording** neighbours once discovery reaches the target:

```python
for neighbour in self._neighbours(payload, mbid):
    if len(self.discovered) >= self.config.target_artist_count:
        break                      # the frontier is discarded here
```

Record always; bound **fetching** instead, at `crawl.py:126`:

```python
while queue and len(self._done) < self.config.target_artist_count:
    ...
    for neighbour in self._neighbours(payload, mbid):
        if neighbour not in self.discovered:
            self.discovered.add(neighbour)
            queue.append(neighbour)
```

**⚠ This redefines `target_artist_count` (`config.py:64`) from a cap on artists *discovered*
to a cap on artists *fetched*.** That is the intended meaning — it is what "crawl to 117,000"
means — and it is the only version under which the frontier survives. **Blast radius: the plan
must sweep every caller of `--target` and `target_artist_count` and era-pin any frozen probe
that depends on the old meaning**, per `CLAUDE.md`'s rename rule. The check is not "does the
identifier still appear" but "does every caller still mean what it meant".

### `CEX-3` — the refusal

After the queue is built and the bootstrap seeded, before the main loop:

```python
if not queue and len(self._done) < self.config.target_artist_count:
    raise FrontierExhausted(...)   # names `refrontier` as the remedy
```

**This is the component with the most value per line.** `ULC-F3`'s damage was never that the
crawl stopped — it is that it stopped while printing something indistinguishable from success.

It cannot misfire. Seeding new artists leaves the queue non-empty. A genuinely exhausted graph
is a different condition: the queue empties *during* the run, not at startup.

---

## §3 — Seeding (`CEX-4`)

`crawl.py:120-123` already queues any bootstrap artist not yet in `discovered`, so seeding
needs no new crawler machinery — only a durable list and a way to pass it.

- **`builder/src/artistpath_builder/data/named_seeds.json`**, committed, following the frozen
  drop payloads' convention. Each entry records the MBID, the name, **who named it and when**,
  and the reason. These artists bypass discovery; a later reader must be able to tell that
  Goose is there deliberately.
- **`crawl --seed-file`** merges it with `--bootstrap`.
- **Goose is the first entry**, on the owner's report of 2026-08-07.

**Why seeding works now and would not have a week ago:** `trimmed_union` keeps an edge if
*either* endpoint ranks the other within top-`j`. Goose ranks Phish first, so the Goose–Phish
edge survives and Goose joins the graph connected. Under the retired `mutual_knn` a seeded
Goose would have been fetched and then discarded. **This is a dependency on the `MSW-`
adoption, not a coincidence.**

---

## §4 — Sequence, and what refuses at each step

| # | Step | Guard if skipped |
|---|---|---|
| 1 | `CEX-1` `refrontier` | — |
| 2 | `CEX-2` + `CEX-3` + tests | — |
| 3 | `CEX-4` seed `named_seeds.json` | — |
| 4 | Crawl to 117,302 on ALG-B, `--algorithm` **explicit** | `config.py:59` still defaults to **ALG-E** → extends the wrong archive |
| 5 | `fame` over the extended archive | `require_fame` (`config.py:126`) → **build refuses** |
| 6 | Re-census `unlistenable` + `featured_credit` over the new population | `ULC-F1` → **build refuses** |
| 7 | Build | **`check_acceptance` rejects** — node bounds are `(47_000, 71_000)` (`acceptance.py:170`) |
| 8 | Verification | — |
| 9 | Adoption | — |

**Every refusal above is a guard working.** Three of them exist because someone predicted this
exact operation.

**Cost.** Step 4 is ~4 hours (75,000 took ~7.5 h; 42,302 scales). Steps 5 and 6 are minutes:
`fame` is batched and resumes past existing records (`fame.py:128,139`), and the census
coverage store from `ULC-F2` pays only for genuinely new artists.

**`ULC-F2`'s deferred half is discharged by step 6** — its extended-population direction has
never fired, and this is the first crawl extension to fire it.

**⚠ One expectation, on the record before the run, and it is not a measurement.** The `ULC-`
results carry it (§313 there): extending the crawl will probably make the class of artists
with nothing of their own to play **larger**, because discovery is breadth-first from the
seeds and extension pushes further into obscurity, where that class lives. The owner stated
the same expectation independently on 2026-08-07. **So the headroom this track buys is smaller
than the raw artist count suggests, and a rising drop share is the predicted outcome rather
than a fault.** It is recorded here so that step 6's result cannot be read as a surprise, and
so that nobody later reads a larger drop list as evidence the extension failed.

---

## §5 — The comparison is confounded, and no read may pretend otherwise

Any candidate-vs-adopted comparison differs by **at least four knobs at once**:

| Variant | Population | Drop lists | Fame coverage | Acceptance bounds | Isolating baseline |
|---|---|---|---|---|---|
| Adopted (`graph-msw-tu50`) | 75,000 crawled | censused at 75,000 | 75,000 | `(47k, 71k)` | — |
| `CEX-` candidate | 117,302 crawled + seeds | re-censused at 117,302 | 117,302 | widened (owner's call) | **none exists** |

**No one-knob baseline exists and none can be built cheaply** — re-censusing is a function of
the population, so population and drop lists cannot be varied independently. Per `CLAUDE.md`'s
rule, the conclusions this comparison is **barred from supporting** are named here:

- **It cannot attribute any change to "more artists".** Four things moved.
- **It cannot compare any per-artist figure** — `pop_raw`, `fame_lb_pctl` and
  `degree_hub_penalty` are all recomputed over a different population (§0).
- **It cannot be read as evidence on path quality** without a listening test, and none is
  scheduled here.

**What it *can* support:** whether specific named artists are now reachable, whether the class
of artists with nothing to play grew as expected, and whether the app still works.

**`ml-graph-analyst` is recommended before step 9** — a comparison spanning graphs of different
structure is exactly its remit. Recommending is a session's job; dispatching is the owner's.

---

## §6 — Seams and owner stops

**Two owner stops.** Neither is a checkpoint; both are decisions only he can take.

- **After step 7 — the acceptance bounds.** The build *will* be rejected: an extension lands
  well above the 71,000 node ceiling. `acceptance.py:139` states that **a new crawl is a new
  artifact identity, not a bound to widen quietly**, and `MSW-G3` is the precedent — there too
  the recalibration was the owner's, recorded as his. **A session must not widen these bounds.**
- **After step 8 — adoption.** Whether the larger map ships.

**Two handoff seams**, at steps 4 and 7: the finished crawl leaves a durable archive rather than
a live understanding, and the rejected build leaves a committed identity. At ~9–10 tasks this
track needs them, and choosing them now is far cheaper than discovering one at task 15.

---

## §7 — Success conditions

| | Condition |
|---|---|
| **`CEX-T1`** | `refrontier` reproduces `reconstruction.frontier_size` from the baseline census **exactly**. A disagreement means the reconstruction is wrong. |
| **`CEX-T2`** | The `ULC-F3` regression test — crawl a fixture archive to a target, then assert `discovered` is strictly larger than `done`. **Shown red against today's code before it is kept**, as `DEP-34-FIX`'s three tests were. |
| **`CEX-T3`** | `FrontierExhausted` raises on a `discovered == done` checkpoint with a raised target, and **does not** raise when seeding supplies new work. |
| **`CEX-T4`** | `refrontier` is idempotent, and refuses on algorithm mismatch. |
| **`CEX-T5`** | The `--target` caller sweep is complete: every frozen probe depending on the old discovery-cap meaning is era-pinned at its own construction site. |
| **`CEX-T6`** | Goose appears in the built candidate graph with a surviving edge to Phish. Falsifies `CEX-R1`'s remedy if it does not. |

---

## §8 — Claims check

Every file, function and config value named above was grepped against the repo on 2026-08-07
and resolves, per `CLAUDE.md`'s pre-execution rule: `crawl.py:115,120-123,126,141-146,165-170,206,218-229`;
`config.py:59,64,97,126`; `acceptance.py:139,170-171`; `fame.py:128,139`;
`cli.py:134-147,265-277`; `api/…/search.py:35-39`; the three drop payloads under
`builder/src/artistpath_builder/data/`.

**One thing named above does not exist yet and is a dependency, not a claim:**
`frontier.py`, `refrontier`, `FrontierExhausted`, `--seed-file` and `named_seeds.json` are all
to be built by this track.

---

## §9 — Out of scope, deliberately

- **The search defect (`CEX-R3`).** Shares no code and no artifact with this track. Bundling it
  would make a cheap fix wait on an adoption decision it does not need. Its own track.
- **Widening the acceptance bounds.** The owner's, at step 7.
- **Any router or cost-function change.** None is needed and none is proposed.
- **`ULC-F4`** (the keep-check name-resolution defect) remains its own track and is untouched.
