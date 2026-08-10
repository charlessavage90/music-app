# `CXA-` — adopting the extended 117k graph

**Role: OPERATIONAL.** The plan for putting `graph-cex-117k.bin` into production. Where
this and the governing documents disagree, they govern:
[`PRODUCT-REQUIREMENTS.md`](../PRODUCT-REQUIREMENTS.md) for what "better" means, and
[`specs/2026-08-09-journey-fame-exposure-preregistration.md`](../specs/2026-08-09-journey-fame-exposure-preregistration.md)
(`JFX-`, as amended by `JFX-AM1`) for what was measured.

**Identifier series `CXA-`** — collision-checked across every ref, zero matches.

**Figures are owned by `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` —
cited, never restated here.**

---

## §0 What this is and is not

**This is an adoption, not an experiment. No arm runs and nothing is measured.** The
measurement happened; `JFX-G1a` and `G1b` both passed, `JFX-C5` passed, and the
pre-registered read was §4 read 5. Figures in the README, cited never restated.

**The owner's decision, taken 2026-08-10, recorded as HIS — do not re-litigate it:**

- **Adopt the extended graph and widen the acceptance bounds.** He accepts the trade
  §3 reserved to him, on the reasoning that the metrics are indicators of direction and
  magnitude and cannot say whether any change is perceptible — so use is the instrument.
- **His revert criterion, stated before adoption so it is a trigger and not a
  rationalisation:** *a noticeably worse product experience on more than half of tested
  journeys*, where "noticeably worse" means **how hard it is to find novel artists**. His
  calibration is the `ALG-E → ALG-B` switch, which he recognised as a clear improvement in
  under five minutes — so the instrument has demonstrated sensitivity at that magnitude.
- **"Improvements needed" is a SEPARATE bucket from "revert".** There are things he would
  want to improve about ALG-B today which will still be present in the new graph.
  Conflating the two is how a revert trigger becomes a wish list.
- **He judges revert unlikely**, given the gradient difference is not established.

**⚠ Adoption makes this graph the baseline.** Both he and this plan assume the realistic
outcome is that it stays. Plan accordingly: the revert path is real but is not the
expected one.

## §0.1 Held constant, and why each is genuinely constant under this change

| Held | Why adoption cannot change it |
|---|---|
| The cost function and every `ApiConfig` weight | Adoption swaps the artifact and the bounds; no router code is touched. **`w_known_ramp_fame_pctl` stays at 0.01** |
| The cap rule (`trimmed_union`, j=50, ceiling=50) | Already adopted at `MSW-`; the 117k artifact was built under it |
| Frontend | Nothing here reaches it |
| The `JFX-` records | Frozen. A result is not edited because it was acted on |

**⚠ NOT constant, and it is the one that bites: the shipped un-listenable payload.**
`JFX-B` was built with `--unlistenable-list …/ulf_droplist_algb.json`, a per-invocation
override. The **shipped default is still the 75k-era payload**. Adoption must repoint it
or every future build silently applies the wrong drop list to the bigger archive. This is
Task 2 and it is the task most likely to be got wrong.

## §1 The owner stops

Two, both explicit, and no task past them proceeds without him.

- **`CXA-S1`** — the acceptance bound values (Task 1). Recalibration is his, per §6 of the
  pre-registration and the `MSW-G3` precedent.
- **`CXA-S2`** — go/no-go before deploying to production (Task 7). Everything before it is
  reversible from git; this is the one that reaches people.

## §2 Tasks

### Task 1 — recalibrate the acceptance bounds (`CXA-S1`, OWNER STOP)

`acceptance.py` documents a protocol and it is stricter than "widen to fit": **tolerance
stays fixed (~±20 %), only the centre moves; every breach is traced to exactly one knob;
the band is checked against four known artifacts, not centred on one; and only the bounds
that actually failed are moved.** *"A new crawl is a new artifact identity, not a bound to
widen quietly."*

**Proposed, ±20 % around the new build:**

```
node_count = (70_900, 106_400)      # was (47_000, 71_000)
edge_count = (1_295_000, 1_942_000) # was (1_050_000, 1_580_000)
median_degree unchanged at (5.0, 25.0) — it PASSED; move only what failed
```

**Both breaches trace to one knob:** the archive going 75,000 → 117,302.

**Sensitivity, three of four artifacts checked and each bound doing work:**

| artifact | nodes | edges | verdict | on which bound |
|---|---:|---:|---|---|
| `JFX-B`, the new build | 88,685 | 1,618,164 | ACCEPT ✓ | — |
| today's adopted `MSW-` map | 58,838 | 1,315,684 | reject ✓ | **nodes** |
| retired pre-`MSW-` mutual-kNN | 74,193 | 898,006 | reject ✓ | **edges** |
| mutual-kNN build of the 117k archive | — | — | **NOT RUN** | — |

**⚠ The fourth artifact was not built.** The protocol names it. It costs ~9 minutes now
the archive is warm. **Either build it or record in the comment that the band was checked
against three, and which one is missing** — do not let the comment imply four.

Write the recalibration comment in the `MSW-` block's own style: what moved, traced to
which knob, which artifacts were checked, and the PREVIOUS values retained inline.
**Leave the era-pinned calibration probe at `analysis/2026-07-23-acceptance-bounds/check.py`
alone** — it is pinned to pre-adoption values by design and must not follow this change.

### Task 2 — ship the censused payload and repoint the default

**The trap, stated before the steps: repoint `CANDIDATE_ALGORITHM`, not
`PRODUCTION_ALGORITHM`.** ALG-B is the adopted lineage and is bound to the constant named
*candidate*; ALG-E is bound to the one named *production* and is not what ships. This is
`SEL-R1`–`R4`, deferred to its own maintenance session and **live until then.** Getting it
backwards half-applies another population's list, which `NoUnlistenableListForAlgorithm`
exists to make fatal — but only when an algorithm is *absent*, not when it is *wrong*.

1. Copy `analysis/2026-08-09-cex-recensus/ulf_droplist_algb.json` into
   `src/artistpath_builder/data/` under the dated convention the directory already uses.
2. Add its sha256 constant beside `CANDIDATE_UNLISTENABLE_DROP_SHA256`, taken from the
   payload's own `sha256_over_sorted_drop_mbids` key — **never transcribed by hand**
   (`DEP-24`'s rule, same reasoning).
3. Repoint `UNLISTENABLE_DROP_LISTS[CANDIDATE_ALGORITHM]` at the new file.
4. **Do NOT touch the ALG-E entry.** `2026-08-09-cex-recensus/README.md` records the
   regenerated ALG-E payload as a **by-product that must not be shipped** — its population
   never changed yet 30 artists became drops and 43 stopped being drops in four days.

**`CXA-G1`:** after this, a build with **no** `--unlistenable-list` override must produce
the same artifact as the overridden one. That is Task 3.

### Task 3 — rebuild through `cmd_build` and prove byte-identity (`CXA-G1`)

Build with the **normal CLI**, `--algorithm alg-b` explicit (`CEXR-2` — there is no
`RC-H3` guard on the build side and a defaulted build reads ALG-E), **no**
`--unlistenable-list`, against widened bounds.

**The gate: the artifact must be byte-identical to `graph-cex-117k.bin`,
sha `bc0431c4…8e7ece46`.** This is what proves Tasks 1 and 2 are correct together — the
right payload is now the default *and* the bounds admit the result. It also discharges §1
of the pre-registration on the shipped path rather than on the diagnostic script.

**If it differs, stop.** A different artifact means the shipped default is not the payload
the measurement was taken on, and every `JFX-` figure stops describing what would ship.
Do not adopt a different artifact on the strength of `JFX-`'s results.

Expect acceptance to **pass** now, and the manifest to record `passed: true` — that is
also the first exercise of the `manifest.py` fix on the real path.

### Task 4 — flip the API default

`ApiConfig.graph_path` → the new artifact. Update the comment block's adoption note in
place: what was adopted, when, and that identity lives in the manifest sidecar — **cited,
never transcribed** (`DEP-24`).

**Do not flip `w_known_ramp_fame_pctl`.** It stays at 0.01. The gradient difference is not
established, so there is nothing here that argues for changing the depth device, and doing
it in the same commit would confound the use-test.

### Task 5 — upload the artifact and sidecar to S3

Versioned in S3, never a database. Both the artifact and its manifest sidecar.

### Task 6 — the image build (`CXA-G2`)

**⚠ `MSW-` Task 12 had NO image-build step, and executing it as written would have shipped
the new map under the old code — leaving the ramp off in production while every check the
plan specified passed.** That is the recorded defect this task exists to prevent.

**`CXA-G2`:** the deployed image must contain the Task 4 commit. Verify from the built
image, not from the branch.

### Task 7 — deploy (`CXA-S2`, OWNER STOP)

**Read `infra/README.md` §4 and §5 before touching anything.** `ARTISTPATH_DEPLOY_GRAPH_KEY`
and `ARTISTPATH_DEPLOY_SIDECAR` are both **required** since `DEP-34-FIX`, so a defaulted
deploy now refuses rather than silently reverting the graph. Set `ARTISTPATH_GRAPH_SHA256`
from the sidecar.

`cdk diff` before `cdk deploy`, and read it. `DEP-34` was caught by exactly that and by
nothing downstream: the `/health` check compares the live service against whichever sidecar
it is handed, so a wholesale revert is self-consistent and passes.

**After deploying, clear the clip cache** if artwork or clips look stale — the `MSW-`
adoption needed 404 stale entries cleared so the change was visible immediately rather than
bleeding in over the 30-day TTL.

### Task 8 — queue the use-test

`TEST-QUEUE.md`, written for someone holding a mouse. **Only what he can press.**

**⚠ The queue file on this branch is STALE relative to `main`**: the discharge of the
2026-08-07 bypass-tray entry landed on `main` via PR #92 and is not on
`crawl-extension-design`, so this branch's topmost heading still reads `QUEUED`. Reconcile
on merge; do not "discharge" it again.

What the entry must say, and the second point is the one that matters:

- **Expect familiar journeys to be DIFFERENT. That is the release, not a fault.**
- **His revert criterion, quoted back to him as he set it** — noticeably worse on more than
  half of tested journeys, measured by how hard it is to find novel artists.
- **Famous-to-famous pairs are where to look hardest.** The one post-hoc signal in `JFX-`
  put the d20 fame drift almost entirely in that stratum, and it is also the easiest case
  for him to judge, because he knows both endpoints.
- **`CLIP-1` exposure probably rises** — ~30,000 more artists, and the newly-crawled
  population's un-listenable class rate was 31.36 % against 24.74 % for the pre-crawl
  75,000. Ask him to name any new examples.
- **Do NOT queue "tell me how it feels."** Owner ruling 2026-08-07: this file is for
  defects and functionality only. His continuous evaluation of the experience is real and
  is explicitly not a queue item.

### Task 9 — documents

`NEXT.md` (rewritten wholesale, not appended), `docs/README.md` rows for this plan and the
`JFX-` results, the handoff, and the retained execution log. **`NEXT.md` owns no figures.**

## §3 What must not be reverted by a well-meaning editor

- **`JFX-B`'s manifest records `DO_NOT_DEPLOY: true`** and the verbatim rejection, because
  it was built against the *old* bounds. After Task 3 the shipped artifact is a **new
  build** whose manifest records a pass. Do not edit the old manifest to match; do not
  deploy the diagnostic artifact.
- **The shallower gradient is NOT established** (`D_B − D_A` spans zero). Adoption was not
  taken in spite of a measured cost; it was taken with no cost demonstrated.
- **The d20 famous-to-famous drift is POST-HOC** and needs its own pre-registration to be
  a claim. It is where to look, not a finding.
- **`w_known_ramp_fame_pctl` stays 0.01.** See Task 4.
- **The ALG-E payload is a by-product that must not ship.** See Task 2 step 4.

## §4 Deferred, with success conditions

- **`SEL-R1`–`R4`** — the constants named for a role that moved. Task 2 is the second time
  this has been a live trap. **Condition: closed when `CANDIDATE_ALGORITHM` no longer means
  the production lineage.** Still the owner's, still its own maintenance session.
- **The rank-asymmetry idea** — an artist who ranks X at #1 while X ranks them #61 is a
  satellite, not a peer; `trimmed_union` keeps the edge and discards the asymmetry. Worked
  case: David Piltch, 86 listeners, degree 49, all famous jazz vocalists, absent from the
  pre-`MSW-` map entirely. **This is the co-credit class three probes failed to attribute.**
  **Condition: needs its own pre-registration, and resuming path-quality work is the
  owner's trigger, never a session's.** Belongs to "improvements", not to this adoption.
- ~~**The fourth acceptance artifact** (Task 1). **Condition: built, or its absence recorded
  in the comment.**~~ **✅ DISCHARGED 2026-08-10 — it was BUILT**, not waived. Mutual k-NN
  over the extended archive: 81,749 artists / 905,558 edges, rejected by the new band on
  **edges** while its node count sits **inside** the node band. Figures owned by
  `builder/analysis/2026-08-10-cxa-acceptance-bounds/README.md`. It established something the
  waiver would have missed: the previous band could not discriminate the cap rule at all, and
  **the new edge floor is the only bound that can.** *(Struck rather than deleted: the record
  that it was tracked and discharged is the point.)*

## §5 Handoff seams

**After Task 3** — the artifact is proven on the shipped path and nothing has been
deployed. Everything to that point is reversible from git.

**Task 7 is an owner stop, not a seam** — do not hand off mid-deploy.
