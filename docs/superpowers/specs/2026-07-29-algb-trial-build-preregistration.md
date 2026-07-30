# Pre-registration — the `ALG-B` trial build (`GRT`)

**Role: ACTIVE — governing document for the `GRT` experiment.** Committed **before any arm
runs**; the git commit timestamp is the evidence that it preceded the result. Where this
document and [`../plans/2026-07-29-graph-rebuild-track-a.md`](../plans/2026-07-29-graph-rebuild-track-a.md)
disagree, **this governs** — it is the finer-grained design and is written with GR-4's
figures in hand.

**Identifiers are `GRT-N`**, namespaced and collision-checked across `docs/` and
`builder/` (no prior use). Disjoint from `GR-` (the plan's tasks and its two gates),
`RC-`, `AS-`, `CS-`, `MKS-`, `DD-`, `TB-`, `REQ-`. Assigned once, never renumbered.

**Owns no path-quality figures.** Cites `findings/2026-07-21-scoring-adjudication.md` by
section; build-shape figures for this track live in
[`../2026-07-29-graph-rebuild-track-a-execution-log.md`](../2026-07-29-graph-rebuild-track-a-execution-log.md).

**Nothing here adopts anything.** `BuilderConfig.algorithm` keeps `contribution_5`; the
API keeps booting `graph-t15-tiebreakfix.bin`. This experiment produces evidence for the
owner's parked re-crawl decision and nothing else.

---

## §0 What this experiment is for, and the cheaper thing it is *not*

**The scope check, run before the design and recorded because it changed it.**

`RC` already measured reciprocation under `ALG-B` by sampling, and `RC-A2` diagnosed the
four collapsed famous artists **by hand** — their rank inside their own candidates' lists
is 50–97, or absent. Re-checking any *single* named artist's reciprocation at full
precision is about 101 read-only requests, roughly 90 seconds. **It does not need a
crawl, and this experiment must not be justified by it.**

What sampling structurally cannot reach is **component membership**: whether an artist
survives the largest-connected-component prune depends on the whole graph, not on any
artist's own neighbourhood. That is `RC-H1`, `NEXT.md` defers it to "before any adoption
decision", and it needs a real build.

> **So the one irreplaceable output of this experiment is `GRT-C4` (component
> membership).** Every other read below is a cheap passenger on a crawl being run
> anyway. If `GRT-C4` were dropped, the rest would not justify the spend and this
> document would be withdrawn.

## §1 Factor table

| arm | source algorithm | crawl coverage | drop rule (GR-1) | isolating baseline |
|---|---|---|---|---|
| adopted `graph-t15-tiebreakfix.bin` | ALG-E | full 75k | absent | — (reference only) |
| `GR-4` verification build | ALG-E | full 75k | present | adopted — differs by one column |
| **`A0`** control build | ALG-E | capped 3,000 | present | `GR-4` — differs by one column (coverage) |
| **`AB`** trial build | ALG-B | capped 3,000 | present | `A0` — differs by one column (algorithm) |

**The only comparison licensed for an algorithm claim is `AB` vs `A0`.** `AB` against the
adopted artifact or against `GR-4` differs in **two** columns (algorithm *and* coverage)
and is **barred** from every quantitative claim in this document. This is the confound the
whole `RC` track existed to avoid; do not re-derive stranding rates that way.

**A limit on "matched coverage", stated because it is not exact.** The two arms share a
target, a bootstrap and a procedure, but their BFS frontiers differ — the neighbour lists
differ, so the 3,000 artists reached are not the same 3,000. Reads that compare
*populations* must therefore be **rates or per-artist statistics**, never raw counts of
distinct artists. `GRT-C4` is specified as a rate for exactly this reason.

### Held constant, and why each is genuinely constant under the intervention

- **`max_neighbours_per_artist=50` and mutual k-NN.** No code in this experiment touches
  `graph.py` or the cap call. `MKS-5b` bars changing them without a simulated degree
  bound, and no read here turns on their value being correct — only on it being *the
  same in both arms*, which it is because both arms call the same builder.
- **`similarity_rescale="p99_log_clip"`, `similarity_damping=0.0`.** Untouched. At
  `d = 0` `damped_strength` ignores the mass marginals entirely, so the drop rule cannot
  perturb scores through that route. The p99 scale is still computed per build and so
  differs between arms — which is *correct and required*: it is part of what "a different
  algorithm's graph" means, not a confound to remove.
- **The drop rule (GR-1).** On in **both** arms, because it landed before either runs.
  This is the dormant-term check that the factor-table rule demands: the drop rule is
  precisely the kind of term that could otherwise switch itself on only where a build
  succeeds. It cannot here.
- **`check_acceptance` and `PRODUCTION_ACCEPTANCE`.** Not edited. **Deliberately NOT
  applied whole**, and this is a design decision rather than an omission — see §3.

## §2 The arms, concretely

**`AB` — the trial arm.** `artistpath-build crawl --algorithm <ALG-B> --target 3000`
into a **fresh archive directory** (`builder/scratch/grt-archive-algb/`) with a fresh
checkpoint. GR-3 additionally routes every key into an `ALG-B` sub-tree, so the scoping is
belt and braces.

**`A0` — the control arm.** ALG-E at the same target. It reads the **production archive**,
wrapped in a read-only adapter whose `put` raises.

> **Why the production archive rather than a fresh directory, decided here because the
> plan left it open.** A fresh directory would re-fetch ~3,000 ALG-E responses we already
> hold — an hour of someone else's service for data sitting on disk. Reading the
> production archive costs nothing and fetches nothing, because production crawled the
> same bootstrap to 75,000 and every artist a 3,000-target BFS reaches is already in it.
> The hazard is the opposite one: `Crawler._archive_or_fetch` calls `put` on any artist it
> *doesn't* find, which would write into the irreplaceable archive. **The read-only
> wrapper removes that hazard structurally rather than by hoping**, and it converts
> `GRT-G2` from an after-the-fact check into an impossibility. If the wrapper ever raises,
> that is itself a finding — it means ALG-E's frontier left the production crawl's
> coverage — and the run stops and reports rather than continuing.

Both arms then build via a committed harness (§3), **not** via `cmd_build`.

## §3 Why the reads bypass `cmd_build`, and what replaces it

A capped 3,000-node graph **cannot** satisfy `PRODUCTION_ACCEPTANCE`: `node_count` alone
requires 60,000–90,000. Running `cmd_build` would refuse both arms for a reason that has
nothing to do with the algorithm, and there is deliberately no CLI escape hatch
(`cli.main`'s docstring — the `criteria` keyword is in-process only, by design).

So the harness calls `build_from_archive` directly and evaluates **the two clauses
`RC-P2` named, individually**, at their production values:

- `famous_min_degree_floor = 8`, over `famous_sample = 25` top-by-popularity nodes;
- the 24 `canonical_names` present in the largest component.

Imported from `artistpath_builder.acceptance`, never retyped — a transcribed threshold is
a threshold that drifts.

## §4 Gates

Each carries its own effect size, per the standing rule that a gate without one fires the
expensive response on noise.

| Gate | Plain sentence | Effect size | If it fires |
|---|---|---|---|
| **`GRT-G1`** — archive safety | *"the irreplaceable production archive holds exactly as many files after the run as before."* | **Binary.** Any write at all is a failure; the archive cannot be re-gathered, so there is no tolerable amount. | Stop. Report. Do not continue to the reads. Structurally prevented by the read-only wrapper, and checked anyway because a structural guarantee that is never verified is a belief. |
| **`GRT-G2`** — arm integrity | *"both arms actually finished fetching what they set out to fetch."* | **≥ 95% HTTP 200** per arm, matching `AS-G1`'s bar. Below that the arm is void, not merely noisy. | Void arm. Re-run or abandon; do not read a partial arm. |
| **`GRT-G3`** — readability | *"the artists each read depends on had all their own candidates fetched, so their degree is decided by the data and not by where the crawl stopped."* | **Per-read, not global.** A read whose subject is not in the readable core is **void for that subject** and reported as void — never as a result. | Report the void explicitly. Do not substitute a nearby artist, and do not pool. |

`GRT-G3` is the gate the calibration exists to serve
(`builder/analysis/2026-07-29-trial-crawl-calibration/`): a capped crawl's readable core
is structurally famous, which is fatal for obscure-artist questions and **ideal** for
these, which are all famous-side. At target 3,000 the calibration recorded 75 closed
artists in the top 0.1% band — measured under ALG-E, so it is an expectation for `AB`,
not a guarantee, which is exactly why `GRT-G3` is a gate rather than an assumption.

## §5 Criteria and reads

Every criterion carries its plain-language sentence, **fixed here before any result
exists**. Owner-facing text quotes the sentence beside the identifier.

### `GRT-C1` — R.E.M.'s degree against the floor

*Plain: "under the new setting, does R.E.M. end up with fewer connections than the map's
safety check allows?"*

**Measured:** R.E.M.'s degree in the `AB` build, against `famous_min_degree_floor = 8`.
**Effect size:** the floor is the threshold; below 8 confirms, at or above refutes.
**Run state presupposed:** `AB` built, `GRT-G3` satisfied *for R.E.M. specifically*.

- **Confirms `RC-P2`** if degree < 8 (or R.E.M. is absent from the graph entirely).
- **Refutes `RC-P2`** if degree ≥ 8. Then the sampled prediction did not survive a build,
  and that is a real correction to the record — report it as prominently as a confirmation.
- **Void** if R.E.M. is not in the readable core. Do not read its degree at all.

### `GRT-C2` — the canonical-names clause

*Plain: "under the new setting, do any of the 24 artists the build insists on keeping fall
out of the map?"*

**Measured:** which of the 24 `canonical_names` are absent from `AB`'s largest component,
and the same for `A0`. **Effect size:** any name absent from `AB` **but present in `A0`**
is attributable to the algorithm. A name absent from **both** is a coverage artifact of the
3,000 cap and is reported as such, never as an ALG-B failure.

### `GRT-C3` — the top-25 degree clauses

*Plain: "under the new setting, do the most popular artists in the map still have enough
connections — both the typical one and the worst one?"*

**Measured:** median and minimum degree over the top 25 by popularity, both arms, against
`famous_median_degree_floor = 25.0` and `famous_min_degree_floor = 8`.
**Effect size:** the two floors are the thresholds. Report **both arms side by side** — a
floor failure that `A0` shares is a capped-scale artifact, not an algorithm effect. This
is the clause `RC-C3` passed in sampling; a build disagreeing with the sampled estimate is
itself worth recording (`rc_posthoc.py` vs `rc_score.py` precedent: neither is a bug in
the other).

### `GRT-C4` — component membership (`RC-H1`) — **the primary outcome**

*Plain: "under the new setting, what share of artists get cut off from the main map
entirely — so they could never appear in the middle of a journey?"*

**Measured:** `1 − (largest component size ÷ pre-prune node count)`, both arms, **as a
rate** (see §1's coverage caveat — raw counts are barred). Reported **stratified by fame
band**, all five bands kept separate and no band pooled — `AS-H1`'s discharge condition,
which binds this document as a successor algorithm pre-registration. A band with fewer
than 30 readable members is reported as under-populated and **not** read, following
`RC-G2`.

**Effect size:** `AB`'s exclusion rate exceeding `A0`'s by **≥ 2× in any band with ≥ 30
readable members** is material stranding — the same shape of bar `RC-R1` used. A
difference below that is reported with its figure and read as **not decisive**, not as
"no effect".

**Reference point, not a baseline:** GR-4's full ALG-E build excluded 800 of 74,957
(1.07%). That is a different coverage regime and is quoted for orientation only; the
comparison that counts is `AB` vs `A0`.

### `GRT-R0` — the null

*Plain: "the new setting turns out not to cut off materially more artists than the current
one, at this scale."*

If `GRT-C4` is not decisive in any readable band **and** `GRT-C1` refutes, then the trial
build has removed two of the re-crawl's blockers. **This is a real and useful outcome, not
a failed experiment**, and the summary must not frame it as disappointing. It does **not**
license adoption: `REQ-38` still owes a blind listen, `RC-R1`'s measured candidate-supply
stranding still stands on its own evidence, and nothing here measures whether ALG-B's
edges are any *good* (`REQ-38`, `AS-H2`'s third deferral).

**This read presupposes both arms built and `GRT-G2` passed on both.** A null read on one
arm is not a null.

## §6 What this experiment is barred from concluding

- **Any quantitative `AB`-vs-production-artifact claim** (two-knob confound, §1).
- **Any claim that ALG-B is better or worse overall.** `NEXT.md`: "no summary may keep one
  half without the other" — ALG-B's famous-end lift (`AS-C1`, `AS-C5`) and its obscure-end
  supply loss (`RC-R1`) are both standing findings and neither is touched here.
- **Any `k` change.** `RC-A2` shows the cap and the algorithm interact; that is strand 3's
  territory and `MKS-5b` requires a simulated bound first.
- **Any adoption language, and any statement about what the owner should do.** The
  re-crawl is parked and is his trigger.

## §7 Cost, measured today

| Input | Value | Source |
|---|---|---|
| Per-request latency | mean **0.617 s**, median 0.430 s, max 1.359 s | 12 read-only requests, 2026-07-29, both algorithms, this session |
| Inter-request delay | **0.2 s** | `BuilderConfig.request_delay_seconds` = 1 / 5.0 |
| Per-artist cost | **0.817 s** | sum |
| **`AB` (3,000 fetched)** | **≈ 41 minutes** | — |
| **`A0` (3,000, archive-served)** | **≈ seconds** | zero fetches expected; any fetch trips the read-only wrapper |
| Build, each arm | ~2 s | GR-4 measured 29 s for 75k; a 3,000-node build is far smaller |

Latency was re-measured because the record spans 0.141 s (during the production crawl) to
~0.85 s (`RC`, 2026-07-29) — a 6× spread that makes any inherited budget meaningless.

**Target 3,000 rather than 5,000**, decided on the calibration: the top-0.1% readable core
is **75 artists at both targets**, so the extra 27 minutes buys nothing on the famous side,
which is where every read here lives. The obscure side is unreachable at any of these
targets — that is precisely why the capped crawl was retired for `AS-H2` — and no read
here asks it to be reached.

## §8 Amendments

*(Appended below, never edited above this line. Pre-run amendments are marked
`GRT-A<n> (pre-run)`; post-run ones `(post-hoc)` and are not permitted to change any
threshold or read.)*

### `GRT-A1` — the control arm gets an overlay archive

**Status: pre-run for `AB` (which has not run); mid-collection for `A0`, which aborted
without producing any scored result. Changes collection plumbing only. No threshold, no
criterion, no read, and no effect size is touched.**

**§2's stated assumption is refuted by measurement, and this amendment exists to record
that before fixing it.** §2 said: "every artist a 3,000-target BFS reaches is already in
[the production archive], because production crawled the same bootstrap to 75,000." The
first `A0` attempt disproved it. After ~1,400 artists processed, the BFS reached
`4365b045-388b-42a5-91b5-b860dbcbf9f7`, which is **not** among the archive's 75,000
responses, and `ReadOnlyArchive` refused the write and aborted the run — the behaviour
§2 specified for exactly this case.

**What it means, and it is a finding in its own right: the production archive's 75,000
responses are not closed under one-hop neighbours.** Even a small fresh crawl escapes
their coverage quickly. The likely mechanism is that the production crawl was resumed
repeatedly, and `Crawler.crawl` rebuilds a resumed frontier as `sorted(discovered − done)`
rather than in BFS order — so production's particular 75,000 is not the *breadth-first*
first 75,000, and a fresh BFS takes a different route out. **Not verified**: the
production checkpoint no longer exists in this tree (only the archive does), so its
`discovered` set cannot be consulted, and the mechanism above is a hypothesis while the
absence itself is measured fact.

**`GRT-G1` held.** The archive was counted at 75,000 files before and after, and the
refused artist is confirmed absent — nothing was written. The structural guard did the
job it was specified for.

**The fix: `OverlayArchive`.** Reads fall through to the production archive; writes go to
`builder/scratch/grt-overlay-alge/`. The production archive stays unwritable *by
construction*, so `GRT-G1`'s guarantee is unchanged rather than relaxed. The count of
overlay writes is recorded (`overlay_writes`) and is itself the measurement of how far
`A0`'s frontier leaves production's coverage.

**Why not the alternative.** Running `A0` entirely fresh would re-fetch ~3,000 responses
already on disk, costing ~41 minutes of someone else's service to obtain data we hold.
The overlay fetches only what is genuinely missing.

**Consequence for the reads, stated because it is not nil.** `A0` is now a mixture of
archived responses (up to nine days old) and fresh ones. `RC-G1` measured that drift and
found it small — 0 of 200 seeds differed from their archived top-50 by more than 5
members — so this is recorded as a known, bounded impurity in the control arm, not
waved away. It does **not** affect `AB`, which is fetched fresh throughout.
