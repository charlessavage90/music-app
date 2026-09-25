# The `CXR-` revert read against the `S4` population arms

**Role: ACTIVE — a READ OF THE COMMITTED RECORD. It owns no figures, and nothing in it is a
finding.** Every quantity is cited by section from the document that owns it and is restated
nowhere here. Nothing below was measured for this note; no probe ran, no artifact was opened,
no arm was scored.

**It recommends no route and selects no arm.** `LBA-D2` reserves the strength threshold to the
owner at the go/no-go stop and `LBA-D3` bars designing a listen before it — both in
[`../specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../specs/2026-09-14-lbd-s4-adoption-preregistration.md)
§1. Resuming path-quality work is the owner's trigger, never a session's.

**Why it exists.** The question *"would a map over the extended crawl's population, built from
our own ListenBrainz recomputation, carry the regression that got the extended map reverted?"*
is answerable in three separate pieces from documents already committed, and the three pieces
have three different answers. Collapsing them into one is the error this note exists to prevent.

**Mints no identifiers.** Every identifier below belongs to `CXR-`, `LBA-`, `LBD-`, `JFX-`,
`CXA-`, `GBL-`, `LBL-` or `REQ-` and is used as those documents use it.

**Figures owners cited here, never restated:**

| owner | what it owns |
|---|---|
| [`../../../builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`](../../../builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md) | the `CXR-` diagnosis |
| [`../../../builder/analysis/2026-09-14-lbd-s4-stage3/README.md`](../../../builder/analysis/2026-09-14-lbd-s4-stage3/README.md) | `LBA-M2`–`M5` and the stage-3 reads |
| [`../../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md`](../../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md) | `LBA-M1`, the builds, `LBA-G1`/`G2` |
| [`../specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../specs/2026-09-14-lbd-s4-adoption-preregistration.md) | the `LBA-` design, its exposures and its bars |

---

## 1. What the revert was for, in one plain sentence

> **The owner used the bigger map for three weeks and judged that it had got noticeably harder
> to find artists he didn't already know — worst of all while pressing *Dig deeper* — and that
> was the test he had written down and handed to himself before the map was ever adopted.**

Source: the `✅ DONE — 2026-09-01 — RUN BY THE OWNER, AND IT FIRED THE REVERT CRITERION` entry in
[`../archive/TEST-QUEUE-discharged.md`](../archive/TEST-QUEUE-discharged.md), which records his
words, his answer that it was worse **both** before pressing anything and while digging, and that
the digging is where it was noticeable. The criterion it fired against is quoted in
[`../plans/2026-08-10-cxa-graph-adoption.md`](../plans/2026-08-10-cxa-graph-adoption.md) §0,
recorded as his before adoption.

**Two things keep that sentence arguable rather than settled**, and both are in the same entry.
The revert was instructed on a **judgement**; every figure in the `CXR-` diagnosis was taken
*after* the map was already out of production, which that document states in its own header. And
he attached his own caveat in the same breath: comparing single first journeys is weak evidence,
there is one data point per pair, and "unfamiliarity" is not a precise measurement.

---

## 2. The mechanism splits three ways, and the split is the substance

The `CXR-` diagnosis describes **two interlocking mechanisms** and one half of the owner's report
that it explicitly does not explain. Read as a question of *where each lives*, they separate:

### 2a. The dead-end half lives in the similarity EDGES over `P`

`CXR-P2` (with `CXR-M5` inside it) measures the added artists' connection counts in
`graph-cxa-adopted.bin`, and the diagnosis's *"How the two halves interlock"* section states the
consequence: the map gained artists the router wants and mostly cannot reach.

**Reading:** this presented as a fact about a *population* — "the artists the extension added are
thin" — but thinness is not a property an artist has. It is a property of the similarity lists
the archive happened to hold for that artist. `CXR-P2` measured one artifact, built from one edge
source. *Plainly: they were dead ends in that map, and "was a dead end in that map" is a different
claim from "is a dead end".*

The diagnosis's own *"What is NOT established here"* section keeps this honest in the other
direction too: no figure there says which artists a journey actually delivers.

### 2b. The fame-ruler half lives in POPULATION MEMBERSHIP itself

`CXR-P1` establishes that the added artists carry listener data (the session's committed
prediction was the opposite, and the diagnosis says so); `CXR-M3` gives the paired shift over the
artists in both maps; `CXR-M4` shows the shift is a **squeeze rather than a level change** and
prices it in the ramp's own units.

This half is edge-independent, and that can be read from shipped source rather than inferred:
`GraphStore.fame_percentiles` (`api/src/artistpath_api/graph_store.py:141`) frames the ruler
on **this artifact's own non-null `fame_lb` values**, with the docstring giving the reason; its
inputs are per-artist listener counts keyed by MBID, and **no edge is an input to it**. The ramp
that consumes it is applied at `api/src/artistpath_api/pathfinding.py:130-132` and `:170`.

The `LBA-` pre-registration reaches the same place independently: §2.5 `LBA-X1` lists
`fame_lb_pctl` among four population-relative quantities that recompute over each arm's own node
set, and names it — *"this is … the `CXR-P1` mechanism."*

*Plainly: the app's sense of "obscure" is a ranking within whoever is on the map, so enlarging the
map re-prices everybody, and the artists already at the famous end have nowhere to go.*

### 2c. The depth-0 half is unexplained, and is not localised anywhere

`CXR-P3` did not fire, and the diagnosis states that nothing it measured accounts for the first
journey being worse and declines to stretch its figures to cover it. The doc map records that half
as closed on 2026-09-04 **by owner ruling that his single offhand report was unreliable — not by a
mechanism being found.**

⚠ **`CXR-P3` does not transfer to a recomputed map, and it is easy to assume it does.** It is a
finding about a switch that left the old map's edges almost entirely intact — `CXR-P2`'s own
section records that the pre-existing artists were not harmed. That precondition does not hold
where every edge is recomputed.

---

## 3. A `P`-population map from our own recomputation: one answer per half

`LBA-A4`–`A6` are *every artist the deeper crawl found*, at the four-, three- and two-listener
bars respectively — their sentences are fixed in the pre-registration §2.2 and quoted in stage 3
§0d. Their node counts and connection counts are stage 2 §3b.

### 3a. The dead-end half — MEASURED, and measured as largely removed

Stage 3 §2a's `P` row reports the same statistic over the same pinned added set that `CXR-P2`
reports, in the same unit, and stage 3's version is the **harsher** of the two: it counts an
artist absent from the map as zero connections, where `CXR-P2` had every added artist present by
construction. Stage 3 §2b marks the only two one-column threshold attributions the whole design
admits, and both are on that row; the within-arm control moves in the same direction and by less.

**Reading:** the quantity that diagnosed this half moves substantially in the direction that would
undo it. *Plainly: the artists the deeper crawl found are not dead ends when the connections are
worked out from listening data instead of taken from the old lists.*

⚠ **Three bars travel with that reading and none of them is optional.** §9 of the
pre-registration bars any routing or path-quality claim beyond `LBA-M1`'s d0 query cost, which
measures what a query costs to serve and never whether the answer is good (stage 2 §3c).
`LBA-X3` records that the degree ceiling absorbs supply. And `REQ-38` makes the blind listen
primary. **A fixed dead-end share is a necessary condition for this half being gone, not a
sufficient one.**

### 3b. The fame-ruler half — CARRIED BY CONSTRUCTION, and measured by no `LBA-` arm

An `LBA-A4`–`A6` map holds essentially the `P` cohort (stage 2 §3b's node counts against the
population rules in pre-registration §2.1; stage 3 §2c's `nodes(arm) − V` stratum), the added
cohort's listener counts are the same numbers keyed by the same MBIDs, and `fame_percentiles`
re-ranks over whoever is present. So the re-pricing recurs for the same reason and at
approximately the same size.

**This rests on documents and a source reading, not on any figure that exists.** `LBA-D5`
(pre-registration §3) builds every arm with `require_fame=False` and fetches no fame at all;
`LBA-X7` (§2.5) states that the fame ruler used for banding exists only for artists the served map
contains, so nothing in stage 3 §1d says anything about the artists an arm adds. **No `LBA-` arm
measured this half, and the design says so rather than leaving it to be discovered.**

### 3c. The depth-0 half — CANNOT BE SAID EITHER WAY

Beyond §2c's point that `CXR-P3` does not transfer: these arms replace every edge and every
similarity score. Stage 3 §1a and §1c quantify what that does to today's served artists'
neighbour lists, and §1b's `R_avail` column separates *choosing differently* from *being forced
to*. A map that chooses differently everywhere has different first journeys everywhere — different
from the reverted map **and** from the one live today. The comparison the `CXR-` half left open is
not merely unresolved here; it is a different comparison.

### 3d. The top line

The thing that was reverted was a **listening judgement**. Stage 3 §8 names this as its own
weakest link — nothing in the `LBA-` arms has been heard — and the standing trap the `CXR-`
diagnosis leaves for every future map switch is that a map switch is never a "more artists, same
routing" change, whatever the node-set arithmetic says. **One half is measured better, one half
recurs unmeasured, one half is unknowable. That is the whole answer, and it does not reduce.**

---

## 4. The extended map was adopted with no blind listen, and none was deferred

**This section is a reading of the record. It is not a finding, and it is not a criticism of the
`CXA-` decision** — §4a is the part that cuts against reading it as an oversight.

### 4a. What the adoption rested on, in its own words

[`../plans/2026-08-10-cxa-graph-adoption.md`](../plans/2026-08-10-cxa-graph-adoption.md) §0 names
the measurement it stands on and it is `JFX-` only — `JFX-G1a`, `G1b` and `JFX-C5`, with the
pre-registered read identified. The same section records the owner's decision as his, **including
his reasoning: the metrics are indicators of direction and magnitude and cannot say whether any
change is perceptible — so use is the instrument.** It records his revert criterion in the same
breath, and his calibration for it: the `ALG-E → ALG-B` switch, which he recognised as a clear
improvement in under five minutes.

**So the absence of a listen was not an omission. Use was chosen, deliberately and on the record,
as the instrument that a listen would otherwise have been.**

That plan's §3 (*what must not be reverted*) and §4 (*deferred, with success conditions*) between
them enumerate what was not established and what was carried forward. **A listen appears in
neither.** Its §0.1 held-constant table is where the cap rule for the adopted artifact is
recorded — which §5 below picks up as an open verification.

### 4b. What the gate it passed actually meant

The `JFX-` pre-registration
([`../specs/2026-08-09-journey-fame-exposure-preregistration.md`](../specs/2026-08-09-journey-fame-exposure-preregistration.md))
carries a **⚠ QUALIFIED, NOT CORRECTED, 2026-09-01** block at its head. It states that the design,
its thresholds and its discipline are unaffected and **the run was not wrong** — what changed is
what the result licenses. `JFX-G1b` is a **stop-gate, not a quality bar**: it permits the new map
to need materially more digging than the old one to reach the same obscurity, and **passing it
never meant "no worse."** The same block records that these gates were not built to catch the
fame-ruler mechanism.

### 4c. The first listener judgement the map received

It is the `✅ DONE — 2026-09-01` entry in
[`../archive/TEST-QUEUE-discharged.md`](../archive/TEST-QUEUE-discharged.md) — three weeks of use,
after deployment, which is §1 above.

### 4d. The reading, labelled

**The only instrument on this project's record that has ever detected a *Dig deeper* degradation
of this kind is a pre-registered use period with a revert criterion fixed in advance.** That is
one detection, by one instrument, on one map switch.

**No document establishes whether a 24-row blind listen would or would not detect it.** Twenty-four
rows is this project's standing listen shape — eight pairs across three depths, per
[`../2026-08-04-gbl-run-execution-log.md`](../2026-08-04-gbl-run-execution-log.md) §1 and the two
`LBL-` listens — and nobody has asked what that instrument's sensitivity is to *this* effect. Two
things on the record bear on it without settling it: `REQ-41` makes "no difference" in unfamiliar
territory uninformative rather than evidence of equivalence, and listen 1's read
([`../2026-09-11-lbl-listen1-read-execution-log.md`](../2026-09-11-lbl-listen1-read-execution-log.md))
records how few of its rows carried a clear pick on both axes and names the pair draw as the
instrument's limit. **Neither says a listen would miss this. Neither says it would catch it.**

⚠ **This is not an argument for or against running one**, and it names no protocol. `LBA-D3`
reserves that design to a later amendment after a go.

### 4e. The nearest listen in time, and why it does not cover this

`GBL-` ran **2026-08-04**, six days before the adoption
([`../2026-08-04-gbl-run-execution-log.md`](../2026-08-04-gbl-run-execution-log.md); harness at
`../../../builder/analysis/2026-08-04-gentle-arm-blind-listen/`). Its design
([`../specs/2026-08-04-gentle-arm-blind-listen-design.md`](../specs/2026-08-04-gentle-arm-blind-listen-design.md))
§1 fixes what it was on — the `B-S1-P1a` arm: the `ALG-B` data set, the `trimmed_union` cap rule
and the gentle `known` ramp — **and names, in the same section, the two decisions its verdict does
not make: adoption, and whether the candidate data set's advantage justifies the re-crawl it
implies.** The re-crawl is the crawl extension. **The listen excluded it by name.**

Two cautions before anyone leans on `GBL-` anyway: its run log §5 records the owner reporting that
**the blind did not hold on his side**, which the runner flagged as the most load-bearing thing in
the log; and both `LBL-` listens read the tie, which `REQ-41` makes uninformative — the
pre-registration §9 bars reading either as a pass or a failure.

---

## 5. Two open verifications

Both are **open**. Neither has been run, and this note does not run them or ask for them.

> **Forward note, 2026-09-25: item 2 is CLOSED.** The magnitude is owned by [`../../../builder/analysis/2026-09-25-cxr-squeeze-on-lba-a6/README.md`](../../../builder/analysis/2026-09-25-cxr-squeeze-on-lba-a6/README.md), measured on the adopted `LBA-A6` map. **§3b's construction argument is confirmed with a figure.** Item 1 remains open.

1. **The cap fields, read from `graph-cxa-adopted.bin`'s own manifest sidecar.** §3a's comparison
   between stage 3 §2a and `CXR-P2` requires that both artifacts were capped by the same rule at
   the same two values. That is asserted by `../plans/2026-08-10-cxa-graph-adoption.md` §0.1's
   held-constant table and matched against the pre-registration §2.3's held-constant row — **two
   documents, not the artifact.** If they are wrong about how that artifact was built, §3a's
   reading collapses entirely. **Open condition: closed when the cap fields are read out of the
   sidecar itself and agree.**
2. **A `fame_percentiles` recomputation over an `LBA-A4`–`A6` node set, repeating `CXR-M3` and
   `CXR-M4`'s paired shift.** §3b is a construction argument with no figure under it. The listener
   counts already exist by MBID, so this needs no fetch — but it is a measurement nobody has taken,
   and `LBA-D5` is why no arm took it. **Open condition: closed when the paired shift and its
   by-position decomposition exist over an arm's own node set, whereupon §3b is either confirmed
   with a magnitude or overturned.**

---

## 6. What this note does not do

- **It recommends no route and selects no arm or threshold.** `LBA-D2` and `LBA-D3` are the
  owner's rulings and are not touched.
- **It owns no figures**, and it re-reads no criterion: every `CXR-`, `JFX-`, `LBA-` and `LBD-`
  identifier is read exactly as the document that owns it reads it. Pre-registration §9's barred
  reads all stand.
- **It makes no routing or path-quality claim**, and nothing here licenses one — §9 again.
- **It closes nothing.** The depth-0 half stays closed the way the record closed it, by owner
  ruling and not by mechanism.
