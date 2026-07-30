# Execution log — graph rebuild, Track A (`GR`), 2026-07-29

**Role: ACTIVE** — the retained record of the `GR` track, appended per task rather than
only at closeout. Governing document:
[`plans/2026-07-29-graph-rebuild-track-a.md`](plans/2026-07-29-graph-rebuild-track-a.md).
Branch `graph-rebuild-planning`.

**Owns no path-quality figures.** Scoring and path-quality figures live in
`findings/2026-07-21-scoring-adjudication.md` and are cited by section. The build-shape
figures below are this track's own and are owned here.

**Nothing is adopted. `BuilderConfig.algorithm` still carries `contribution_5`; the API
still boots `graph-t15-tiebreakfix.bin`.**

---

## §1 What ran, and in what order

The plan was written cold from the committed record, then executed inline in the same
session. Entry state: PR #49 merged to `main`, branch cut from the merge.

Order deviation worth recording: **GR-4's baseline step was run first**, before GR-1's
code landed, because it is the only moment the pre-drop refusal can be observed. The plan
anticipated this and named it as an option; it was taken.

## §2 GR-1 — the nameless-artist drop rule

**Baseline, taken before any code changed** (production archive, `cmd_build`):

```
INFO filtered 7 special-purpose entities
INFO largest component: 74193 of 74993 artists
ArtifactRejected: 33 artist(s) carry no name
  (e.g. 06e1ca5b-…, 12df23de-…, 18197573-…) — unsearchable, clipless,
  and renderable only as a blank card
```

The three sample MBIDs match the F8 record
(`builder/analysis/2026-07-24-track2-p8b-harness-review/`) exactly, and the largest
component matches the adopted artifact's 74,193. **The tripwire fired as designed and
nothing was written.**

**Owner evidence that upgraded the decision.** The drop-vs-backfill decision was already
the owner's (2026-07-28). On 2026-07-29 he checked the three most popular nameless MBIDs
against MusicBrainz by hand: **all three return "Artist not found"**. They are deleted or
merged upstream entities that survive in ListenBrainz's similarity data. So backfilling
names by MBID — the declined alternative — was never available at all. Recorded because it
converts a preference into the only implementable option.

Sampled for that check (adopted artifact, sha256 `4cb84ef9…` verified before reading):

| MBID | pop_pctl | degree | neighbourhood |
|---|---|---|---|
| `c9ba47ca-0bd2-4814-966d-ecfb06d032a3` | 0.91 | 11 | Japanese anime/game composers |
| `626d3be1-08a5-4b46-835f-67601919db26` | 0.88 | 14 | indie folk |
| `a55263d7-6ec2-4560-80cb-551bc6c94c9e` | 0.64 | 19 | English folk / Americana |

The blank name is an **upstream data gap, not a parse failure on our side** — the first
artist's neighbours carry CJK names correctly. This is the third time console/encoding
suspicion has been raised about this data and the second time it has been wrong; the
cause here is genuinely absent upstream data.

**Implemented** in `build_from_archive`, beside the special-purpose filter and before the
mass computation, so a dropped artist contributes to no marginal and a neighbour stranded
by the drop falls out at the largest-component prune rather than dangling. No config
knob: `REQ-2` is a Must and zero is the only defensible count, so a switch would be an
escape hatch on the guard.

## §3 GR-2 — algorithm selection

`BuilderConfig` was a frozen dataclass with no way to select the source algorithm and
`cli._config` threaded only `--target`, so **no trial build on a non-default algorithm was
possible** — the gap the RC session recorded and dissolved only because its instrument
constructed the algorithm string itself.

`PRODUCTION_ALGORITHM` and `PERMITTED_ALGORITHMS` now name the closed enum of six values
validated by `CS-P0e`; `--algorithm` is accepted by both `crawl` and `build` (build needs
it because GR-3 keys the archive *read* on it too). An unpermitted value raises
`SystemExit` at the CLI boundary rather than reaching the endpoint for its HTTP 400.

**The default is untouched**, and the test `test_config_default_algorithm_is_production`
pins it: flipping it *is* the re-crawl decision, which is the owner's.

## §4 GR-3 — algorithm-scoped keys (`RC-H3`)

Two hazards, both closed:

- **Archive key.** `similar/listenbrainz/{mbid}.json` did not encode the algorithm, so a
  re-crawl aimed at the existing archive would silently return production data to every
  future build. Production keeps the flat layout — 75,000 irreplaceable responses do not
  get moved, and every existing script finds them there — and every other algorithm gets
  a sub-tree. The flat build skips nested keys, so it cannot sweep a sub-tree in through
  the shared prefix.
- **Checkpoint.** A resumed crawl under a different algorithm would have treated the other
  algorithm's finished artists as done and skipped every one. The checkpoint now carries
  an `algorithm` field and refuses a mismatched resume. A missing field means production,
  so every pre-existing checkpoint still resumes.

## §5 GR-4 — verification rebuild

**Gate `GR-G1` — *"a rebuild of today's map from today's data, with the blank-name artists
dropped, is accepted by the build's own safety checks"* — PASSED.** Binary gate, no
refusal of any kind. The artifact was written, which is itself the evidence:
`check_acceptance` raises before `serialise` is reached.

```
INFO filtered 7 special-purpose entities
INFO dropped 36 nameless artists
INFO largest component: 74157 of 74957 artists
INFO wrote ./scratch/graph-dropnameless-verify.bin: 74157 artists,
     897620 edges (12.1 per artist), 14.7 MB, 29s
```

**Identity** (from the manifest sidecar, never transcribed by hand):
sha256 `73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa`,
built at commit `dd7bbe3`, 28.5 s. **Verification artifact only — not adopted, not
pointed at by anything.** The API still boots `graph-t15-tiebreakfix.bin`.

### Deltas against the adopted artifact (74,193 artists / 898,006 edges — RC log §7)

| Quantity | Adopted | GR-4 | Delta |
|---|---|---|---|
| Artists (largest component) | 74,193 | 74,157 | **−36** |
| Edges | 898,006 | 897,620 | **−386** |
| Pre-prune population | 74,993 | 74,957 | −36 |

### The 36-vs-33 reconciliation, because it looks like a discrepancy and is not

F8 and the baseline refusal both say **33**; the drop rule reports **36**. Both are
correct and they count different populations:

- **33** is blank names in the *emitted* graph — the largest component only, which is all
  `check_acceptance` and F8 ever see.
- **36** is blank names in the *full pre-prune* population, which is where the drop rule
  runs by design (before the mass computation, so a dropped artist perturbs no marginal).

So 3 of the 36 sat outside the largest component already. The arithmetic closes exactly:

```
pre-prune   74,993 − 36 (all blanks)            = 74,957   ✓ observed
component   74,193 − 33 (blanks inside the LCC) = 74,160
observed    74,157  ⇒  3 further nodes left the component
```

**Those 3 are the stranded neighbours the rule was written to catch** — nodes whose only
tie was to a dropped nameless artist, now pruned rather than left dangling as blank-card
dead ends. This is the first direct evidence that the stranding clause does real work on
production data; the unit test proved the mechanism, and here it fires three times.

**Edge delta.** −386, a net decrease. The plan predicted movement in *either* direction,
because removing a nameless artist from a top-50 candidate list promotes the 51st into
the mutual-k-NN cap and can mint new edges. A net loss of 386 against 36 dropped artists
(mean degree ~12, so ~430 edge-ends naively) is consistent with that partial offset. No
figure here needs explaining away.

**Cost, corrected — and `CLAUDE.md` was right.** The build takes **~29 seconds**. RC log
§6 says "~2 minutes"; `CLAUDE.md` says "rebuild in ~30 s". **The RC log is the outlier and
`CLAUDE.md` needs no edit** — noted explicitly so a future sweep does not "correct" the
accurate one to match the stale one. Budget from 29 s.

**This discharges the second half of `acceptance.py`'s standing success condition** ("the
drop rule lands in the build and this check then passes on a rebuild"). The tripwire
stays in place, unweakened, as a standing rule for future crawls.

## §6 GR-5 / GR-6 — the `GRT` trial build

Pre-registration:
[`specs/2026-07-29-algb-trial-build-preregistration.md`](specs/2026-07-29-algb-trial-build-preregistration.md),
committed at `770b3fb` **before any arm ran**; harness (`grt_run.py`, `grt_score.py`)
committed at `26b8160`, **before either produced a result**.

**The scope check changed the design and is recorded in §0 of that document.** `RC-A2`
already diagnosed reciprocation by hand, and re-checking one named artist costs ~101
read-only requests rather than a crawl. The single irreplaceable output is `GRT-C4`,
component membership (`RC-H1`), which sampling structurally cannot reach.

### `GRT-A1` — the control arm's assumption was refuted by its own first run

The pre-registration asserted that a 3,000-target BFS stays inside the production
archive, so the `ALG-E` control could read it for free. **That is false**, and the
structural guard is what caught it: after ~1,400 artists the frontier reached
`4365b045-…`, absent from the archive's 75,000, and `ReadOnlyArchive` refused the write
and aborted rather than silently extending an irreplaceable asset.

**`GRT-G1` held — 75,000 files before and after, nothing written.** Amended to an
overlay (reads fall through to production, writes land in
`builder/scratch/grt-overlay-alge/`), which keeps the production archive unwritable *by
construction* rather than relaxing the guard. Amendment committed before the re-run.

**Measured, and it puts a number on the gap:** the control arm needed **5 overlay writes
across 3,000 artists (0.17%)**. So the production archive is *nearly* closed under
one-hop neighbours but not exactly — enough to abort a naive control arm, not enough to
matter to anything else. The likely mechanism is that a resumed crawl rebuilds its
frontier as `sorted(discovered − done)` rather than in BFS order, so production's 75,000
is not the breadth-first first 75,000. **Unverified**: the production checkpoint no
longer exists in this tree, so its `discovered` set cannot be consulted. The absence is
measured; the mechanism is a hypothesis and is labelled as one.

### `A0` control arm — collection

3,000 discovered, 3,000 fetched, **0 failures**, 5 overlay writes, production archive
75,000 → 75,000. `GRT-G2` (≥95% fetched) passes at 100%.

### `AB` trial arm — collection

3,000 discovered, 3,000 fetched, **0 failures**, 0 overlay writes (it has its own
archive), production archive 75,000 → 75,000. **18.3 minutes** — under the 41-minute
budget, because live latency ran nearer 0.3 s than the 0.617 s measured earlier the same
evening. `GRT-G2` passes at 100%.

### Scorer defect, found before the trial result existed

A dry run of the scorer against `A0` alone — deliberately, while `AB` was still
collecting — exposed that `build_from_archive` reads **every** key under its prefix, so
the control arm was building the whole 74,157-node production graph instead of its
3,000-node capped one. That would have restored the two-column confound the factor table
exists to prevent. Two impossible derived figures are what surfaced it: an exclusion rate
of **−23.76** and a fetch rate of **1.0017**.

Fixed with `SubsetArchive`, applied to both arms symmetrically. **Cross-validated
against an independently written harness:** the corrected control builds 2,959 nodes /
53,902 edges where `builder/analysis/2026-07-29-trial-crawl-calibration/` recorded 2,958
/ 53,900 at the same target — two harnesses, different sessions, agreeing to within one
node. Committed before `AB` finished, so no result could have shaped it.

### Gates

| Gate | Outcome |
|---|---|
| **`GRT-G1`** archive safety | **PASS**, and it earned its keep — see `GRT-A1`. 75,000 files before and after, both arms. |
| **`GRT-G2`** arm integrity | **PASS**, 100% on both arms (bar was 95%). Zero fetch failures across 6,000 requests. |
| **`GRT-G3`** readability | **PASS** for every read taken. Readable core 754 (`A0`) and 785 (`AB`). Every top-25 artist readable in both arms; R.E.M. readable in both. |

### `GRT-C1` — R.E.M. against the degree floor

| | `A0` (ALG-E) | `AB` (ALG-B) |
|---|---|---|
| Degree | 47 | **6** |
| Floor | 8 | 8 |

**`RC-P2`'s degree-collapse prediction is CONFIRMED by a real build**, not merely
sampled. R.E.M. holds 6 connections under `ALG-B` against 47 under the control at
identical coverage.

### `GRT-C2` / `GRT-C3` — the acceptance clauses

Both clauses **pass in both arms**, and `GRT-P2` records why that is not the reassurance
it looks like.

- **`GRT-C2`:** 22 of 24 canonical names present in *both* arms. The two absent — CROOVE
  and Wishbone Ash — are absent from the **control too**, so they are coverage artifacts
  of the 3,000 cap, exactly the attribution the criterion was written to force. **No
  canonical name is lost to the algorithm.** R.E.M. remains in the largest component.
- **`GRT-C3`:** top-25 median degree 46.0 (`AB`) vs 47.0 (`A0`), both far above the 25.0
  floor; minimum 31 vs 34, both far above the 8 floor. `RC-C3`'s sampled pass is
  reproduced by a build.

### `GRT-P2` — the finding that matters most, and it was not predicted

**The predicted build refusal did not happen, and the reason is a blind spot in the
guard.** R.E.M.'s popularity rank falls from **7 of 2,959** to **62 of 2,904** — because
popularity *is* score-weighted in-degree, so an artist that loses its edges loses its
popularity in the same motion. The top-25 sample that `famous_min_degree_floor` inspects
is selected *by popularity*, so R.E.M. drops out of the sample and the floor never
examines it.

**The check is structurally unable to detect the collapse it was written for, once the
collapse is severe enough.** A mild collapse is caught; a total one is invisible. Full
detail and the caveat about production scale: `GRT-P2` in the pre-registration.

### `GRT-C4` — component membership (`RC-H1`), the primary outcome

Exclusion rate = share of an arm's **readable** artists that fall outside the largest
component.

| Band | `A0` (ALG-E) | `AB` (ALG-B) | pre-registered verdict |
|---|---|---|---|
| top 0.1% | 0.0% (75) | 0.0% (72) | not decisive |
| top 1% | 0.0% (326) | 0.87% (229) | not decisive |
| top 10% | 0.0% (290) | 2.02% (198) | not decisive |
| upper half | 0.0% (48) | 1.52% (66) | not decisive |
| lower half | *unread* (10) | 3.33% (30) | unread in one arm |
| **overall, whole population** | **1.37%** | **3.20%** | — |

*(readable members in brackets; `A0`'s lower half is under-populated at 10 and `RC-G2`
refuses to pool it)*

**`GRT-R0`, the pre-registered null, does not fire cleanly and neither does its
alternative** — because the effect size is broken, not because the arms agree.
`GRT-P1` records it: the bar was a **ratio** (`AB ≥ 2 × A0`) and the control's readable
exclusion rate is **exactly zero in every band**, so the ratio is undefined and every
band returned "not decisive" — including the top decile, where `AB` strands 2% of
readable artists and `A0` strands none. **The pre-registered verdict is left standing as
written and the raw figures are reported beside it**; the read is not re-labelled to fit
the result. A successor pre-registration owes an absolute-difference bar or an explicit
zero-baseline rule.

**What can be said without the broken bar:** `ALG-B` excludes readable artists from the
largest component in three of four comparable bands where `ALG-E` excludes none, and its
whole-population exclusion rate is **2.3× the control's** (3.20% vs 1.37%). That is a
real difference in the direction `AS-H2` feared. It is **not** the pre-registered read,
and it must not be quoted as though a threshold had been crossed.

**Coverage caveat, per §1:** the two arms reached different 3,000-artist sets, so these
are rates, never counts. And none of this reaches production scale — the capped crawl's
readable core is structurally famous, which is why `AS-H2` retired it for obscure-artist
questions in the first place. The lower-half band is readable here at exactly 30 members,
the minimum, and only in one arm.

## §7 Test suite

| Point | Result |
|---|---|
| Baseline (AS log §10, recalled then re-run) | 115 passed |
| After GR-1 | 118 passed (+3) |
| After GR-2 | 123 passed (+5) |
| After GR-3 | 128 passed (+5) |

`test_replay.py`'s byte-identical rebuild test passes at every point, which is the
determinism sentinel for the flat production path.

## §7a `GRT-P3` (post-hoc, NOT pre-registered) — ALG-B's measured cost is largely a cap artifact

Run after the closeout, to answer the owner's sequencing question: is there an advantage
to running Track B (cap selection) **before** the re-crawl? Every `ALG-B` measurement in
this track was taken at `k = 50`, and `RC-A2` located the collapsed top-0.1% artists at
rank **50–97** in their own candidates' lists — just outside the cut. So the question is
answerable offline from the trial archive.
Script and figures: `builder/analysis/2026-07-29-algb-trial-build/grt_k_sensitivity.py`.

Degree of the four artists `RC-A2` found reciprocating nothing (floor is 8):

| artist | k=50 | k=60 | k=75 | k=100 | top-100 fully fetched |
|---|---|---|---|---|---|
| R.E.M. | **6** | 10 | 26 | 68 | yes |
| Pixies | 3 | 4 | 9 | 22 | yes |
| The xx | 1 | 3 | 4 | 10 | yes |
| PJ Harvey | 10 | 13 | 25 | 46 | no — lower bound |

Population, same archive: artists below the degree floor fall **26.4% → 19.0% → 13.4% →
7.5%** across those four values of `k`, while mean degree rises **16.3 → 20.4 → 26.7 →
38.2**.

**Both of this track's headline costs for `ALG-B` — R.E.M.'s collapse and the roughly
doubled exclusion rate — are substantially artifacts of `k = 50` rather than properties of
the algorithm.** R.E.M. clears the floor by `k = 60`.

**This is not a licence to raise `k`, and must never be cited as one.** It measures only
the *benefit* side. `MKS-5b` exists because loosening the both-ways cap restores unbounded
degree, and removing unbounded hubs is what `capfix` won its blind listen for — the mean
degree more than doubling across this range is exactly that cost appearing, unpriced. Three
caveats, carried in the script's own docstring: it ranks on raw source scores rather than
the pipeline's damped strengths, it runs on a 3,000-node trial archive rather than the 74k
graph, and it prices no hub cost at all.

**What it licenses is the sequencing conclusion and nothing more:** the cap-selection
simulation is now known to bear directly on the re-crawl decision rather than merely
following it.

## §7b `GRT-P4` (post-hoc) — the full `ALG-B` crawl and build, 2026-07-30

The owner authorised a **full `ALG-B` crawl** overnight after the closeout. It ran to
completion: **75,000 fetched, 0 failures**, 0.83 GB, and the production archive was
untouched at 75,000 (`GR-3`'s scoping is what made this safe to run at all). Checkpoint
and archive both verified as genuinely `ALG-B`, with zero unscoped files.

**Recorded correction: a full crawl is ~7.6 hours at the endpoint's current speed, not the
4¼ hours in the record** — that figure dates from when the endpoint ran ~4× faster.

**The build succeeded and PASSED `check_acceptance`:** 68,467 artists, 811,784 edges, 78 s.
`ALG-B` artifact sha256
`d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f`; the `ALG-E` comparison
build is `GR-4`'s (`73feffa0…`). Both carry the drop rule, so the two differ in exactly one
column. 27 nameless artists dropped here against 36 under `ALG-E` — a different archive
sees a different set of neighbour rows, so a different set of artists never acquires a
name.

### `GRT-P2` — CONFIRMED at production scale

The trial left this open on the grounds that "rank among 2,904 is not rank among 74,000".
It is now measured on a full graph, and the guard is blind exactly as predicted:

| artist | `ALG-E` degree (rank) | `ALG-B` degree (rank) | inside the top-25 sample? |
|---|---|---|---|
| R.E.M. | 47 (5) | **6** (38) | **no** |
| Pixies | 41 (23) | **3** (5,730) | **no** |
| The xx | 35 (38) | **1** (12,317) | **no** |
| Radiohead | 50 (0) | 48 (10) | yes |

**The build passes** — top-25 median degree 45.0 against a floor of 25.0, minimum 28
against a floor of 8, and **no canonical name is missing**. Three of the four artists
`RC-A2` named collapse to single digits, and every one of them has fallen out of the sample
the floor inspects, because losing edges loses the popularity that put them there.
**`acceptance.py` cannot detect this failure mode at any scale.** No change is proposed
here; weakening it is barred and strengthening it is a design question of its own.

### `GRT-C4` — decisive at production scale, where the trial could not be

| | `ALG-E` | `ALG-B` |
|---|---|---|
| Artists cut off the map | 800 | **6,499** |
| Exclusion rate | 1.07% | **8.67%** |

**Ratio 8.12× against a 2× bar — decisively material**, and unconfounded: each rate is
computed inside that arm's own crawled population. `GRT-P1`'s broken ratio bar was a
trial-scale artifact of a zero baseline; at full scale the baseline is non-zero and the
pre-registered bar works as written.

### The confound in this probe's own first draft, caught before reporting

**The two arms' BFS frontiers diverge far more than expected: `ALG-B` never crawled
23,056 (31.1%) of the adopted artifact's artists, and reached ~23k the adopted crawl never
saw.** So measuring "absent from the component" against the adopted frame conflates **never
crawled** with **stranded** — and the first draft did exactly that, reporting 55.8% of
below-median artists "absent" when the stranded share is **7.0%**. Restricted to artists
each arm actually crawled:

| band | `ALG-E` stranded | `ALG-B` stranded | `ALG-B` never crawled |
|---|---|---|---|
| top 0.1% | 0.00% | 0.00% | 0 |
| top 1% | 0.00% | 1.20% | 0 |
| top 10% | 0.01% | 0.73% | 54 |
| upper half | 0.02% | 0.97% | 3,552 |
| **lower half** | **0.08%** | **7.00%** | **19,450** |

`ALG-B` strands the obscure artists it crawls at roughly **88×** production's rate. Both
denominators are kept in the output so the gap stays visible.

### What this does and does not settle

**Settles:** `RC-R1`'s stranding is real, large, and reproduced by a real build;
`RC-P2`'s refusal is refuted for good, with the mechanism (`GRT-P2`) confirmed instead;
`AS-R3` is understated if anything — `ALG-B` is not merely a different graph, it is a
different *population*, 31% disjoint on crawl coverage alone.

**Does not settle, and this is the live question:** every figure above is at **`k = 50`**.
`GRT-P3` measured that `ALG-B`'s stranding is heavily cap-dependent (26.4% → 7.5% below the
degree floor across k = 50 → 100 on the trial archive). **The cap-selection simulation is
now answerable at production scale, offline, from this archive** — which is what the
overnight crawl bought, and it is the decisive next experiment rather than a follow-up.

**Nothing is adopted.** `BuilderConfig.algorithm` still carries `contribution_5`; the API
still boots `graph-t15-tiebreakfix.bin`; the `ALG-B` artifact is a gitignored scratch file
nothing points at. A blind listen is still owed before any adoption (`REQ-38`).

## §8 Closeout record

**D4 — suites run, not recalled:** builder **129 passed**, api **217 passed**, frontend
**107 passed** across 18 files.

**B3 — the vacuous-test spot check earned its place, and it took three attempts.** The
`RC-H3` isolation test was written, broken deliberately, and **stayed green** — twice.

1. Asserting on `mbids` proved nothing: a nested key parses to a bogus mbid nobody lists
   as a neighbour, so mutual k-NN strips its edges and `largest_component` drops it. The
   node list is identical either way.
2. Asserting byte-identity while contaminating with *copies* of the same responses also
   proved nothing: that lifts every artist's in-degree by roughly the same factor and
   `pop_raw` is normalised, so the perturbation cancels exactly.

The third version contaminates **asymmetrically** — a sub-tree node pointing hard at the
graph's least popular artist — and the invariant is real: with **both** guards disabled the
contaminated build **inverts the popularity ordering**, carrying that artist from 0.0 to
1.0.

**And the reason the first two breaks stayed green is itself a finding: the invariant is
defended twice, by `RC-H3`'s nested-key skip *and* by `GR-1`'s orphan clause** (a
nested-key pseudo-mbid has no identity row, so the drop rule removes it as nameless).
Disabling either alone changes nothing. That is recorded in the test's own docstring,
because a future spot check will otherwise re-derive it from scratch and reasonably
conclude the test is vacuous.

**B2 — reachability:** the two new analysis modules are imported by nothing outside their
own directory, which is the established `builder/analysis/` pattern for standalone probes.
Not orphans. Every other changed file is package source or a test.

**B5 — stale descriptions:** `.claude/` describes nothing this work changed (swept for
archive-key, algorithm, nameless and node-count claims). **`CLAUDE.md` needs no edit** —
including its "rebuild in ~30 s", which this track confirms rather than contradicts.

**A4 — default-flip:** `BuilderConfig.algorithm` still carries `contribution_5`, and that
is correct rather than unfinished — flipping it **is** the re-crawl decision and is the
owner's. `--algorithm` is a per-invocation override with no default change, pinned by
`test_config_default_algorithm_is_production`. No other knob was added.

**A5 — processes:** all four ports (8000, 5173, 8138, 8139) swept and **empty**. Nothing
was started detached and nothing was left running; the queued test exercises the deployed
site and needs no local server.

**D3 — provenance.** Nothing adopted. Artifacts produced, all gitignored and all
regenerable:

| Artifact | sha256 / identity |
|---|---|
| `scratch/graph-dropnameless-verify.bin` | `73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa`, built at `dd7bbe3` |
| Adopted artifact (ruler + frame, unchanged) | `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted at run time by the scorer |
| `scratch/grt-archive-algb/` | 3,000 `ALG-B` responses, ~18 min to regenerate |
| `scratch/grt-overlay-alge/` | 5 responses production never held (`GRT-A1`) |

**D6 — the standing context layer:**

| Layer | Unit | Total | Delta this track |
|---|---|---|---|
| Unconditional | characters | **44,113** | **0** |
| Conditional | lines | **2,122** | **0** |

Neither layer was touched: no `CLAUDE.md` edit, no new or changed skill or agent, nothing
written to `memory/`. **These are the totals for the next closeout to compare against.**

**One growth item NOT taken, and it is the owner's call.** `CLAUDE.md`'s builder command
block documents `--target` but not the `--algorithm` flag this track added. The line is
**incomplete, not false**, so it is growth rather than a correction — roughly 60 characters
on the unconditional layer, paid by every future session. Not taken unilaterally.

## §8b Second closeout — after the overnight crawl, 2026-07-30

**D4:** builder **129**, api **217**, frontend **107**. Run, not recalled.

**✅ `snyk_code_scan` — RUN and CLEAN for this work, discharging the item §9 carried
across two closeouts.** The CLI is not on `PATH` in this environment (the same trap
`memory/deploy-environment-traps.md` records for the AWS CLI), but Snyk is available as an
MCP server with its own auth tool; that is the route that works here and is worth knowing
before deferring the check again.

- `builder/src/artistpath_builder/` — **0 issues.** This covers every line `GR-1`, `GR-2`
  and `GR-3` touched.
- `builder/analysis/2026-07-29-algb-trial-build/` — **0 issues.**

**13 findings exist elsewhere under `builder/analysis/`, none of them from this work, and
none fixed — deliberately.** Three Medium DOM-XSS in
`2026-07-22-c3-bypass-mechanisms/listen.html` and ten Low path-traversal in the Track 2
arm scorer and the low-degree census, all of the shape *command-line argument flows into
`pathlib.Path`*. They are **frozen probe scripts** (`CLAUDE.md` names them as such), run
locally by the owner, where the "attacker" supplying the argument is the person typing the
command; `listen.html` is a local listening-test page that is never served. The global
instruction obliges a fix for issues in **newly introduced or modified** code, which these
are not, and editing a frozen probe would break the reproducibility that makes it frozen.
**Recorded rather than actioned, and left with a condition** — see §9.

**B1 — a gap in the FIRST closeout, corrected here.** That pass ran `docs-lint.sh` and
**never dispatched `doc-auditor`**. The skill is explicit that invoking `closeout` *is* the
request for that subagent, and a green lint is not an audit — the lint cannot see a defect
of omission, which is the class that has twice bitten this project. The auditor was
dispatched this time, scoped to the diff and told the lint had already run. Lint itself:
clean, 0 hard failures.

**B5 found two stale figures in live documents, both fixed:**

- **`NEXT.md` still listed the `ALG-B` re-crawl as a parked, un-run item costing 4¼ hours.**
  It has *run*. That is a status error in the document that owns status, and it is the more
  serious of the two. Struck as an action; the **adoption** half stays parked, which is a
  genuinely different decision.
- **The RC execution log §6 says a full build takes "~2 minutes".** It is ~29 s (78 s for
  the larger `ALG-B` archive), measured twice on real builds. That document *owns*
  operational measurements, so a wrong figure there is worse than usual. Annotated in place
  rather than rewritten, per the convention for COMPLETE records. `CLAUDE.md`'s "~30 s" was
  right throughout and is untouched.

Frozen documents carrying the old 4¼-hour figure — the AS pre-registration, the superseded
algorithm-selection handoff, the OneDrive plan — are **deliberately left alone**. A
pre-registration's value is that it is frozen.

**B2:** the four `GRT` probes have zero inbound imports, which is the established
`builder/analysis/` pattern for standalone probes. Not orphans.

**B3:** no new tests were added by the overnight work, so there is nothing new to
break-test. The first closeout's three-attempt spot check stands.

**A4:** still correct and still deliberate — `BuilderConfig.algorithm` carries
`contribution_5`. The re-crawl ran on a **per-invocation override**; no default moved.
**This is the one place the distinction matters most**: an `ALG-B` archive and artifact now
exist on disk, and nothing points at either.

**A5:** all four ports swept, **all empty**. The overnight crawl completed and exited; no
detached process survives it. The queued item exercises the deployed site and needs no
local server.

**D6 — standing context layer, unchanged again:**

| Layer | Unit | Total | Delta |
|---|---|---|---|
| Unconditional | characters | **44,113** | **0** |
| Conditional | lines | **2,122** | **0** |

## §9 Owed, and not discharged

- ✅ ~~**`snyk_code_scan` has NOT been run** on any of the three code diffs.~~
  **DISCHARGED 2026-07-30 — run and CLEAN**: 0 issues across
  `builder/src/artistpath_builder/` and the new analysis probes. See §8b, including the
  route that works here (MCP, not the CLI, which is not on `PATH`). Struck, kept for the
  record.
- **13 pre-existing Snyk findings under `builder/analysis/`, none from this work**
  (3 Medium DOM-XSS in `2026-07-22-c3-bypass-mechanisms/listen.html`; 10 Low
  path-traversal in the Track 2 arm scorer and the low-degree census). **Condition: if any
  of those probe scripts is ever un-frozen and edited, fix its findings then; if
  `listen.html` is ever served rather than opened locally, fix it before that happens.**
  Otherwise **accepted, won't fix** — a legitimate terminal state here, because the
  argument source is the owner's own command line and the page is never served.
