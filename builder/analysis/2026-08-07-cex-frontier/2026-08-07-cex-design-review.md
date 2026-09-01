# `CEX-` design review — claims checked against the repo, 2026-08-07

**Role: REVIEW of [`docs/superpowers/specs/2026-08-07-crawl-extension-design.md`](../../../docs/superpowers/specs/2026-08-07-crawl-extension-design.md).**
Not authoritative and not governing — the spec governs the track; this records what its
claims do and do not survive contact with the source. **It owns no figures.** Every number
below is either cited from [`cex_frontier.json`](cex_frontier.json) / [`README.md`](README.md),
which own them, or is arithmetic over those and is labelled as derived.

**Method.** Read-only. `README.md`, the spec, and the source the spec names:
`crawl.py`, `config.py`, `cli.py`, `pipeline.py`, `graph.py`, `acceptance.py`, `fame.py`.
Nothing was executed and nothing was rebuilt. Per `CLAUDE.md`, this is the
"check this plan's claims against the repo" reading, not a prose review.

**Identifiers.** Findings are `CEXR-n`. Prefix collision-checked across every ref
(`refs/remotes` + `refs/heads`, `*.md`) on 2026-08-07 — free. It is deliberately not one of
`CXT-` / `FRT-` / `SEED-`, which the spec reserved for the track itself.

**What the spec gets right, so this is not read as a verdict on the document:** §0 exists
and names four genuinely-not-constant terms; §5 names the conclusions the comparison is
barred from supporting; `CEX-T2`'s shown-red-first requirement is the right shape;
excluding `CEX-R3` from the track is correct. The findings below are almost all of one
kind — things the spec asserts *about the repo* that the repo does not quite support.

---

## Critical

### `CEXR-1` — the seeding remedy probably dies at the degree ceiling, and §3 never looks at that step

§3 argues Goose survives because `trimmed_union` keeps an edge if *either* endpoint ranks
the other within top-`j`. That is the union step, and it is not the step that decides.
`trimmed_union_cap` (`builder/src/artistpath_builder/graph.py:228-237`) then trims **every**
node to `union_degree_ceiling` = 50 by deleting whole edges, ordered by symmetric pair
strength, **with no floor protecting a node's last edge**:

```python
doomed = sorted(result[node], key=lambda v: (strength(node, v), _desc(v)))[:excess]
for victim in doomed:
    result[node].pop(victim, None)
    result[victim].pop(node, None)
```

`strength(u, v)` is `max(ranking[u][v], ranking[v][u])`, and `ranking` is the **pre-symmetrise**
directed adjacency (`pipeline.py:382-385`). `cex_frontier.json` records
`named_artists.goose-jam-band.goose_in_phish_list` as **false**, so `ranking[Phish][Goose]`
does not exist and `strength` falls back to `-inf` on that side. The pair's strength is
therefore Goose's own value alone.

*Derived, from figures the census owns:* the README records Goose's score against Phish, and
`phish_lowest_score` / `phish_list_length` record where Phish's own hundred-artist list
bottoms out. At `similarity_damping = 0.0`, `damped_strength` is `log1p(cooc)`
(`pipeline.py:76-79`), so the Goose–Phish pair strength is `log1p(15) ≈ 2.77` against a floor
of `log1p(62) ≈ 4.14` for the weakest edge Phish contributes from its own list. Phish's
top-`j` = 50 are all in the union by construction and all stronger than that floor — they
fill the ceiling of 50 on their own, before a single inbound edge is considered.

**If that holds, Goose loses Phish and (a fortiori, being weaker) Fleet Foxes, is isolated,
and is removed by `largest_component`. `CEX-T6` fails and `CEX-R1`'s remedy does not work.**
The spec's strongest structural claim — "This is a dependency on the `MSW-` adoption, not a
coincidence" — rests on half the algorithm.

**Remedy, and it is the cheapest thing in this document.** Compute Phish's 50th-strongest
surviving edge strength in the adopted artifact and compare it to `log1p(15)`. Offline,
minutes, decisive. Per the cheapest-experiment-first rule this belongs **before** step 4,
not at `CEX-T6` after a four-hour crawl and a census. If it fails, the track needs a design
answer — a ceiling that never isolates a node, seeding artists whose top-ranked neighbour is
less crowded, or accepting that seeding does not reach everyone either.

### `CEXR-2` — only step 4 is guarded on `--algorithm`; steps 5, 6 and 7 need it as much

`similar_prefix` (`pipeline.py:119-132`) selects the archive tree from `config.algorithm`,
and both `archive_artists` (which `fame` uses, `cli.py:160`) and `build_from_archive`
(`cli.py:207`) go through it. `_config` (`cli.py:67-75`) defaults to `PRODUCTION_ALGORITHM`.
So an `--algorithm`-less `fame` or `build` reads the **flat production tree**, not the
ALG-B sub-tree.

§4's guard column attaches this to step 4 alone. It applies identically to 5, 6 and 7, and
there it is worse: `crawl.py:206`'s `RC-H3` checkpoint guard has **no counterpart on the
build side**. The three drop lists are algorithm-keyed too (`pipeline.py:254,273,292`), so a
defaulted build would load ALG-E's censused lists and could pass `check_acceptance` while
describing a population nobody asked for.

Underneath it is a live contradiction the plan will trip over. `config.py:17` says
`PRODUCTION_ALGORITHM` (ALG-E, `contribution_5`) is "**the adopted 75k archive's algorithm**".
`cex_frontier.json`'s `algorithm` field and `archive` path are both `contribution_3` — ALG-B,
`CANDIDATE_ALGORITHM` — and the census README names `graph-msw-tu50.bin` as the adopted
artifact built from it. **One of those is stale, and "default is production's" currently
means two different things depending on which you read.** `cli.py:274` ("default is
production's (ALG-E)") and `cli.py:314` ("default config's (mutual_knn until adoption)",
stale since the `MSW-` adoption) are downstream of the same rot.

**Remedy.** Resolve which document is stale and fix it; then make every step of §4 carry
`--algorithm` explicitly, and consider whether the build side wants an `RC-H3`-shaped guard
of its own rather than relying on the operator.

---

## High

### `CEXR-3` — §0 misses the term that prices the dominant cost: the p99 rescale

`rescale_scores` (`pipeline.py:94-110`) computes `scale = np.percentile(raw, 99)` over
**every edge in the build**, then maps each edge to `min(1, log1p(v)/log1p(scale))`. That
normaliser is a function of the population, and it feeds `w_sim·(1−similarity)` — the primary
term in the router.

§0 lists `pop_raw`, `fame_lb_pctl`, `degree_hub_penalty` and the component prune. It does not
list this one, and it is the largest of them: **two artists whose raw co-occurrence is
identical in both archives get a different similarity in the new artifact**, because the
scale moved underneath them.

*Inference, labelled as such:* the extension adds several million low-co-occurrence directed
edges, which pulls the 99th percentile **down**, which raises every rescaled similarity,
which pushes **more** edges to saturate at exactly 1.0. Those cost zero — the "free
similarity" defect `config.py:169-177` calls the primary defect and carries as open. In plain
terms: **the extension is likely to make more hops free, so more of the route is decided by
tie-breaks than by similarity.** §5 says the comparison cannot speak to path quality, so as
the track is written nothing would notice this happening.

**Remedy.** Log the p99 and the saturated-edge share at build time and compare the two
builds. It is one line and it converts an unmeasured risk into a figure.

### `CEXR-4` — acceptance will reject on **two** bounds, not one

§4 step 7 and §6 name only the node bounds `(47_000, 71_000)` (`acceptance.py:170`).
`check_acceptance` collects every violation before raising (`acceptance.py:251-266`), and
`edge_count` is bounded at `(1_050_000, 1_580_000)` (`acceptance.py:171`).

*Derived from `cex_frontier.json`'s `artifact` block:* the adopted artifact sits near the
centre of both bands, and the extension raises the crawled population by about 1.56×. Under
a cap rule that is non-reciprocal by construction, the edge ceiling is breached by a wider
margin than the node ceiling, not a narrower one. §8's claims check cites
`acceptance.py:170-171`, so line 171 was read and its consequence was not carried into §4/§6.

**Why it matters beyond tidiness:** §6 frames step 7 as an owner decision about *the node
ceiling*. It is a decision about the artifact's whole shape band, with two numbers, and
`acceptance.py:141-158` (the `MSW-G3` recalibration) is the worked precedent for how to take
it. Presenting the narrower question would be handing over a decision he cannot fully see.

### `CEXR-5` — `CEX-3` **can** misfire; "it cannot" is only true inside one process

§2 argues that a genuinely exhausted graph is distinguishable because "the queue empties
*during* the run, not at startup". That distinction does not survive the checkpoint.
`crawl.py:115` rebuilds the queue from `discovered − done` on **every** invocation, and a run
that legitimately exhausted the graph saves a checkpoint where that difference is empty. The
next invocation is then indistinguishable from the `ULC-F3` state: it raises
`FrontierExhausted`, recommends `refrontier`, and `refrontier` faithfully reconstructs the
same empty frontier and changes nothing.

Two concrete cases: an idempotent re-run of `crawl` after a completed extension, and a re-run
with `--seed-file` whose seeds are already in `discovered`.

**Remedy.** Record the terminal condition in the checkpoint — an `exhausted` flag written
when the loop exits with an empty queue — and have the refusal read it, so the two states are
distinguishable across runs. Worth doing precisely *because* §2 is right that this is the
highest-value component in the track.

### `CEXR-6` — `unlistenable` is guarded on population; the other three frozen snapshots are not

`pipeline.py:291-304` gives `drop_unlistenable` the `ULC-F1` `PopulationNotCensused` guard,
checked against `archive_population` captured pre-drop (`pipeline.py:188`). Nothing
equivalent protects:

- **`load_drop_mbids`** (`pipeline.py:254`) and **`load_featured_credit_drop_mbids`**
  (`pipeline.py:273`) — algorithm-keyed frozen snapshots. The algorithm is still ALG-B after
  the extension, so they load the same 75k-era lists and evaluate **none** of the new
  artists, silently.
- **`load_deezer_ids()`** (`pipeline.py:446`) — takes **no population argument at all**. Every
  new artist gets `""`, so their cards fall back to name-based clip resolution, which is
  exactly the `BYP-13` failure (a clip by a different artist of the same name). Coverage
  drops across the artifact with nothing objecting.

§0's row "`fame_lb` and `deezer_ids` already exist as additive keys" is true about the
*format* and is being read as true about *coverage*, which it is not. §5's "what it can
support" should gain a row for clip-identity coverage.

**Relatedly, §4 step 6 is internally inconsistent.** It says re-census "`unlistenable` +
`featured_credit`" and is silent on `no_release`. `pipeline.py:279-284` says all three classes
are strict subsets and "applying all three is identical to applying this one" — and
`cex_frontier.json`'s `gap_75k_to_artifact` bears that out today, with `on_a_drop_list`
equal to the `unlistenable` list size exactly. Under that reading, re-censusing
`featured_credit` is unnecessary; under the other, `no_release` is missing from the step.
Pick one — and if `featured_credit` *is* re-censused separately, the subset relation has to
be re-verified over the new population rather than inherited.

---

## Medium

### `CEXR-7` — `refrontier` needs two constraints §2 does not state, and `CEX-T1` cannot catch the second

`CEX-1` says it "reads every archived response, unions the neighbours, writes the true
`discovered` set back".

**(a) Scope.** It must enumerate through `similar_prefix(config, source)` (`pipeline.py:119`),
which exists so that `fame` and `build` share one definition of "this algorithm's tree". A
naive `archive.keys()` walk ingests another algorithm's sub-tree *and* the `fame/` keys
(`fame.py:97`) into an ALG-B checkpoint. Make `refrontier` the third consumer of that
function, not a fourth definition of the rule — that divergence class is what
`test_pipeline_mirrors.py` exists to guard.

**(b) Union, not replace — and the census proves this is real, not hypothetical.**
`discovered ⊇ done` is load-bearing: `crawl.py:115` computes a set difference against it.
*Derived from `cex_frontier.json`:* `reconstruction.distinct_mbids_referenced` is **eight
fewer** than `checkpoint.done` plus `reconstruction.frontier_size`. Those eight are artists
that were crawled but appear in **no** response's neighbour list — bootstrap entries nobody
names. A `refrontier` that *replaces* `discovered` with the neighbour union drops them, and
`discovered` stops being a superset of `done`.

**And `CEX-T1` would still pass.** The frontier is computed as a set difference, and those
eight are in `done`, so they are excluded either way — the reconstruction reports the right
`frontier_size` while having broken the invariant. `CEX-T1` needs a second assertion:
`done ⊆ discovered` after the rewrite.

### `CEXR-8` — `CEX-T1` and `CEX-T6` are one-shot operational gates, not regression tests

"`refrontier` reproduces `reconstruction.frontier_size` exactly" is only meaningful against
the pre-extension archive. After step 4 it can never pass again, and the archive is
gitignored so it can never run in CI. `CEX-T6` is likewise a one-shot check against a built
artifact. §7 lists both in one table beside `CEX-T2`–`T4`, which are genuine fixture-backed
tests.

**Remedy.** Split the table into *regression tests (kept, fixture-backed)* and *one-shot
gates (dated, executed once, recorded)*, and state as a constraint — not merely as sequence
position — that `CEX-T1` must run before step 4.

### `CEXR-9` — step 6's "minutes" has no rate basis, unlike step 4's

Step 5 checks out and the spec is right about it: `fetch_fame` batches at
`MAX_PER_REQUEST = 1000` (`fame.py:57,139`) with a `request_delay_seconds` pause, so the new
artists are a few dozen POSTs. Seconds.

Step 6 is a different shape. The un-listenable keep-check is per-artist — a commercial-DSP
link *and* a resolving clip — so re-censusing the new population is tens of thousands of
external lookups against rate-limited services. `ULC-F2`'s coverage store means you only pay
for genuinely new artists, and *that is the whole extension*. §4 gives step 4 an explicit
rate basis and gives step 6 an adjective.

**Remedy.** Cost step 6 the same way step 4 is costed. If it lands in hours rather than
minutes, §6's handoff seams may want to move.

### `CEXR-10` — the checkpoint is rewritten non-atomically ~85 times during step 4

`_save_checkpoint` (`crawl.py:218-229`) is a bare `write_text`. §2 makes the argument itself —
"that 6 MB file is the only record of 75,000 completed fetches and there is no second copy" —
as grounds for backing up before `refrontier`, then does not apply it to a four-hour run that
rewrites the same file every `checkpoint_every` fetches. A crash or a full disk mid-write
truncates it.

Recovery exists (`refrontier`, off the archive), so this is not fatal — but temp-file-plus-
rename is a two-line fix. Note also that the file grows substantially during the run:
`discovered` now keeps growing past the target, which is the entire point of `CEX-2`.

### `CEXR-11` — the target equals the frontier exactly, so it is non-binding

*Derived:* `checkpoint.done` plus `reconstruction.frontier_size` is the spec's 117,302. So
the run is "crawl the reconstructed frontier to exhaustion" and the target restates that
rather than bounding it.

Two consequences worth writing down. Permanent fetch failures (`crawl.py:193-196`) keep
`_done` below the target, so the loop dips into **newly discovered** artists to make up the
shortfall — the final population's composition depends on the failure count. And a reader
will assume the number was chosen; say what it is for under the redefined meaning.

---

## Low

### `CEXR-12` — the `<=` → `<` change is unremarked, and the old condition never fired at all

`crawl.py:126` reads `len(self.discovered) <= target`. Because the inner break at
`crawl.py:142-143` caps `discovered` at exactly `target`, that condition is **always true** —
today's crawl only ever stops when the queue empties. So `CEX-2` is not relocating a bound,
it is adding the first real one, and it silently switches the comparison operator too. Say
so; it is also the clean explanation of why `CEX-T2` will go red against today's code.

### `CEXR-13` — `--target 0` is silently ignored

`_config` (`cli.py:65`) uses `if target:`. Irrelevant in practice, but `CEX-T5`'s sweep runs
straight through it.

### `CEXR-14` — `FrontierExhausted` surfaces as a traceback

Raised inside `Crawler.crawl`, uncaught by `cmd_crawl` (`cli.py:144`). Given that the whole
point of `CEX-3` is that the failure previously read as success, catch it at the CLI boundary
and print the remedy rather than a stack trace.

---

## Weakest link in this review

**`CEXR-1` is the one to attack first, and it is the one I would abandon most cheaply.** It
turns on Phish's surviving edge-strength distribution in the adopted artifact, which I have
not measured — I read the ceiling algorithm and the census's `goose_in_phish_list: false` and
derived the rest. If Phish's union degree happens to sit at or below the ceiling, or if
enough of its inbound edges are weaker than `log1p(15)`, the edge survives and §3 is right as
written. That is a ten-minute offline measurement and it should be made before anything else
in this track is built.

`CEXR-2`, `CEXR-6` and `CEXR-7`(b) I would defend as they stand: they are read directly off
the source and, for `CEXR-7`(b), off this directory's own JSON.

The rest of the review assumes the census figures are correct. It does not re-derive them.

---

## Whose decision

**Mine, and I would take them:** running the `CEXR-1` measurement; resolving the ALG-E/ALG-B
documentation contradiction in `CEXR-2`; every remedy in the Medium and Low sections, which
are bookkeeping and guard placement.

**The owner's, and here is why each is his rather than mine:**

- **The acceptance band (`CEXR-4`).** `acceptance.py:139` makes it his by construction — a new
  crawl is a new artifact identity — and it is two numbers, not the one §6 names.
- **If `CEXR-1` confirms: whether seeding is worth changing the cap rule.** That touches the
  adopted `MSW-` package and what a path is allowed to look like, which is the definition of
  "what counts as better".
- **`CEXR-3`'s consequence, if measured and real.** More zero-cost hops is a path-quality
  change, and path quality is settled by his ear, not by a build log.
