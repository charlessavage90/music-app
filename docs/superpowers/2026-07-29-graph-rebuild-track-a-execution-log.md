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

## §9 Owed, and not discharged

- **`snyk_code_scan` has NOT been run** on any of the three code diffs — the Snyk CLI is
  unauthenticated in this environment and authenticating is a browser flow only the owner
  can complete. The global instruction requires it on new first-party code. Owed on
  GR-1/GR-2/GR-3; recorded in each commit message rather than left implicit.
