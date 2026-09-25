# `LBD-S4` adoption at `LBA-A6` — retained execution log

**Role: ACTIVE, retained.** Appended **per task**, not at closeout. Decisions and reasoning, not
narration — this is what makes the session replaceable rather than precious.

**Governing document:** [`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), §11's `LBA-AM1`–`LBA-AM4` read before §3, §4, §5, §7 or §8.
**It owns no figures**; candidate figures are owned by this session's `builder/analysis/` directory
when one exists. **Status is `NEXT.md`'s**, never restated here.

**Scope, from the owner, 2026-09-21.** Task 1 — the `LBA-AM4` amendment. Task 2 — §8 items 1–3, the
candidate build, and nothing else. **Hard bars he set:** generate no journey on either map, design
no listen, do not deploy, do not change `ApiConfig.graph_path`, re-read no `LBD-` or `LBA-`
criterion, both `LBL-` verdicts run-once and final, and the `P` drop payload is
`unlistenable_drop_algb_20260809.json` and no other.

---

## Task 1 — `LBA-AM4`, the unblinded use gate (`LBA-G5`)

**Committed before any build work began**, which is the property the amendment exists to have.

### What was decided, and why

**Identifiers.** `LBA-AM4` and `LBA-G5` were both swept across every local and remote ref before
minting, per `CLAUDE.md`'s collision rule — `git grep -lE` over `refs/remotes refs/heads` limited
to `*.md`, never the working directory. Both silent. `LBA-G5` is minted because `CLAUDE.md`
requires every gate to carry its own effect size under its own identifier; calling the new stage
"the use gate" without one would have made it unciteable.

**§8 is NOT renumbered, deliberately.** The gate sits between items 3 and 4 as a marked insertion
that leaves items 1–4 with their numbers. The alternative — making the listen item 5 — would have
silently falsified every document already written that says *"§8's four items"*, which includes
stage-3 README §9's options B, C and D, all three of them frozen. §11's own rule is that an
amendment is added *beside* the text it qualifies rather than edited into it.

### Two corrections to the owner's brief, both made before writing

Recorded because both were going into a pre-registration, which is the document class whose entire
value is that it was committed before results, and a false premise inside one is not recoverable
later.

**1. The `CXR-` detection latency — the correction was mine and it was WRONG, and the owner's
original brief was right.** Four documents state the revert criterion fired *"after three weeks of
use"*. I read that as time-to-detect and told the owner his "within the first hour" premise was
contradicted by the record. **He corrected it: he noticed within minutes; the three weeks was
availability** — he was away, and as the app's only user he left it until he had time to roll back.
**None of the four documents says which quantity it measures**, which is exactly why the misreading
was available. The correction goes forward into `LBA-AM4` rather than into the four documents, all
of which are COMPLETE or HISTORICAL and are therefore never edited (`docs/README.md`'s rule, and
`session-start` MT1's).

**This changed the amendment's argument, not just a date.** "A short period is the cheapest
detector" is a claim about cost; "detected within minutes, by use, and by no instrument in advance"
is a claim about *sensitivity*, and only the second makes a two-day bound defensible rather than
merely convenient.

**2. `LBA-A3` differs from the candidate in TWO columns, not one.** The brief described the
fallback as differing "in population only". §2.1's own baseline column says `V` → `P` moves
population **and** the drop-list payload (`…20260805` vs `…20260809`), and its boxed warning is
explicit that the column is real even where its effect is zero — the `20260809` payload would drop
31 members of `V`. The fallback is unaffected and remains sound; what changes is what the amendment
is permitted to claim about the comparison, and it now says two columns. Accepted by the owner
without objection.

### The owner's two inputs, recorded verbatim

Given 2026-09-21, **before he had seen a single journey on any `LBA-` map** — no candidate build
existed, and no arm carried `fame_lb` at all. **No draft criteria were offered to him**: the
`CXA-` precedent's value is that the trigger is his words and not a rationalisation, and giving him
wording to react to is the one act that would have contaminated it.

- **Criterion:** *"a noticeably worse product experience on more than half of tested journeys"*,
  meaning **novel artists become more difficult to surface OR novelty is traded for coherence**
  (novel artists surface but the path's coherence suffers as a result).
- **Period:** **2 days of actual app use, maximum.**

⚠ **The second limb is new.** The 2026-08-10 `CXA-` criterion had the novelty limb alone, so a
candidate trading coherence for novelty would have passed it and fires this one. Recorded as his
difference, not as a session's paraphrase of the older criterion.

### Claims verified from source before the amendment cited them

Per `CLAUDE.md`'s rule that every function, file and config value a document names is grepped
before it is relied on:

| claim | verified |
|---|---|
| `graph_store.fame_percentiles` is the ranking device | `api/src/artistpath_api/graph_store.py:141`, called at `:329` |
| a fame-free artifact has **no** ranking, not a degenerate one | `graph_store.py:329` — `fame_lb_pctl=… if fame_lb else None` |
| `require_fame` is the builder knob `LBA-D5` pinned | `builder/…/config.py:132`, consumed `pipeline.py:448` |
| the `P` payload name | `builder/…/unlistenable_drop.py:101`; used in stage 2's `s4_build_A*.json` |
| `LBA-A3` = `LBD-A5V` is built, serialised and fame-carrying | `C:\unsung-fast\lbd-artifacts\LBD-A5V.bin` + sidecar, on disk |
| every relative link in the amendment resolves | checked programmatically, none broken |

### What Task 1 does not do

No build, no journey, no listen design, no default changed, no shipped code touched, no `LBD-` or
`LBA-` criterion re-read. `ApiConfig.graph_path` untouched.

---

## Task 2 — the candidate build, §8 items 1–3

**Figures are owned by [`../../builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md`](../../builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md)
and by the two result JSONs beside it. None is restated here or in `NEXT.md`.**

### The one design decision that mattered: fame must not be fetched into stage 2's archive

The shipped `fame` stage writes `fame/<mbid>.json` **into the archive it is given**. Stage 2's
`S4-A6` archive is a pinned instrument input behind committed stage-2 and stage-3 results, so
running the stage against it would have mutated a pinned artifact and silently invalidated every
figure those two stages recorded — the failure would have made no noise at all.

**Resolution, and it is reuse rather than invention:** the fame records go into a separate
directory, and the build composes the two halves read-only through a `FameOverlayArchive`. That is
`lbv_build.py`'s pattern (`LBD-AM5-4`), which did the same thing for `LBD-A0V` and `LBD-A5V`. Both
halves are wrapped in `ReadOnlyArchive` (`GRT-A1`) and the overlay refuses writes itself, so the
composition cannot become the hole in the guard. `S4-A6`'s `MANIFEST.json` sha256 is asserted
**before and after** both the fetch and the build.

### Step 6 of the refresh procedure is NOT owed at `P`, and the reasoning is recorded because a frozen document reads the other way

Stage-3 README §9 option C says a `P`-row go commits to *"a re-census and a fame fetch over a
larger population"*. **The re-census half does not fire here.** `unlistenable_drop_algb_20260809.json`
already censused `P` with **0 uncovered** (`LBD-AM4-3`; the `LBD-` prereg §10 table records it),
which is why stage 2 could build this arm with the filter `on, inert (20260809)` in the first
place. `LBA-G3` fired on the **union** of all nine populations — overwhelmingly the `U` row — not
on `P`. Option C's step 6 is the general refresh step for a *new* population, not a prerequisite
for this candidate. That is methodology and therefore this session's; it is written down because
the frozen document reads the other way and a later reader will hit the same sentence.

### The structural proof is one sha256, deliberately

The candidate is re-serialised with its five additive lists emptied and compared to
`LBA-A6-bare.bin`, which stage 2 produced from its own build by exactly that method
(`s4_bare_copy.py`). Byte equality proves node **order** and all four CSR arrays plus names,
disambiguations and `pop_raw` in a single comparison. The field-by-field comparison against stage
2's `LBA-A6.bin` runs as well, because a sha tells you **that** something moved and never
**which**.

### A defect in this session's own instrument, found and fixed before the result was reported

**The first run's acceptance table was incomplete.** `acceptance_report` tabulated the four bounds
its author expected to matter and silently omitted the global `median_degree` band — which
**failed**. The shipped `check_acceptance`'s own output named three failures; the table named two.
Nothing downstream would have caught it, because the table looked complete.

**It was caught only because the script prints the shipped check's verdict verbatim beside its own
table.** That redundancy was not foresight — it was there to quote the canonical wording — and it
is the reason this is a corrected instrument rather than a wrong report.

**The fix is structural, not a patched row.** The report now mirrors `check_acceptance` check for
check, and asserts its covered field set against `AcceptanceCriteria`'s dataclass fields, so a
criterion added later cannot go untabulated. It also refuses if its own `failing` list disagrees
with whether the shipped check raised. **A hand-written list of "the bounds that matter" is the
same defect class as a restated figure that has gone stale** — this project's standing rule
applied to a table instead of a number. The build was re-run from scratch rather than the JSON
patched; it is deterministic, so the figures reproduce.

### Bars honoured

No journey generated on either map. No listen designed (`LBA-D3`). No deploy. `ApiConfig.graph_path`
untouched. No `LBD-` or `LBA-` criterion re-read. Both `LBL-` verdicts untouched. The `P` drop
payload is `unlistenable_drop_algb_20260809.json` and no other. Nothing written under
`builder/scratch/`. Pairing is recorded in the result JSON rather than inferred from the config
(`LBD-D6`).

### Stopped, deliberately, at §8 item 2

The candidate fails `PRODUCTION_ACCEPTANCE`. **No bound was widened and none is proposed**; the
script refuses `--serialise` unless `--acceptance-ruling` carries a decision the owner has actually
given. **§8 item 3 (manifest pinning) is therefore not reached** — it operates on a serialised
artifact, and there is none. Both items resume in minutes once he rules.

---

## Task 3 — the owner's acceptance ruling, 2026-09-21

**His ruling:** recalibrate to admit the candidate, per §8 item 2 — move only the bounds that
fail, take the new centre from the stage-2 node and CSR counts for `LBA-A6`, keep the tolerance at
about ±20 %, preserve the edge floor, record the change and its basis here.

**This is the `MSW-`/`CXA-` case, not the 2026-09-05 cleanup.** A bound is moving so a NEW,
never-served artifact can be adopted. That is risk acceptance and his, by his own `LUX-4` ruling.

### The basis, and why it satisfies "independent of the build that went red"

The centres are read from
[`builder/analysis/2026-09-14-lbd-s4-stage2/README.md`](../../builder/analysis/2026-09-14-lbd-s4-stage2/README.md)
§3b, which recorded **87,394 artists / 2,490,728 CSR entries** for `LBA-A6` on 2026-09-15 — a
different build, recorded six days before the candidate existed. The candidate was separately
proved byte-identical to it (candidate README §3a), so the figures describe the same map without
being derived from the artifact that was rejected.

**`median_degree`: only the ceiling failed and only the ceiling moved.** Its basis is the same §3b
row — 2,490,728 / 87,394 = 28.50 mean degree, ×1.2 = 34.2, taken as 34. **The floor stays at 5.0**,
which is the half that catches a graph that lost most of its nodes. The four §2.8
failure-signature detectors all passed on the candidate and none is touched.

### The edge floor is "preserved" in the sense that matters, and it now does all the work

The band raises the edge floor from 1,050,000 to 1,990,000, which **strengthens** the cap-rule
protection rather than trading it away. Checked against the same known artifacts: all three
must-reject rows are still rejected, and **every one of them is rejected on the edge bound alone**
— the recalibrated node band admits all three, `JFX-B` included.

**Consequence for the test suite, and it is not tidying.** The three synthetic isolating rows were
built to fail exactly one bound under the *old* band and stopped doing so under the new one:
`NODE_CEILING_ONLY = (80_000, 1_300_000)` now sits *inside* the node band and below the edge floor,
so it would have been rejected on the wrong bound and the test would have stayed green while
testing nothing. That is precisely the vacuity its own comment was written about, and the rows were
re-derived.

### ⚠ The accepted cost, recorded in three places so it cannot be rediscovered as a mystery

**The new bounds reject the currently-served map (58,838 / 1,315,684) and reject `LBA-A3` =
`LBD-A5V` (57,932 / 1,681,254), the fallback `LBA-G5` would revert to.** The builder cannot
reproduce what the app serves today while these bounds stand. That is the `LUX-E1` drift shape
deliberately re-entered.

**It was raised before the ruling and he ruled anyway**, which is his call. It is recorded in
`acceptance.py`'s own comment, **asserted as a test** rather than left implicit, and filed in
`NEXT.md`'s deferral registry. The remedy, if the use gate fails or the candidate is not adopted,
is to restore the `PREVIOUS (MSW- restore 2026-09-05)` line before rebuilding either map.

The assertion is the part worth keeping: when this next bites it will present as a **recorded
decision with a named remedy**, not as a mystery rejection of a build everyone expects to work —
which is exactly how `LUX-E1` presented, and it cost a session to diagnose.

**Full builder suite: 292 passed.**

---

## Task 4 — the owner's id re-extraction ruling, 2026-09-21

**His ruling:** before the use gate runs, re-extract `deezer_ids`, `spotify_ids`, `apple_ids` and
`artist_facts` over the candidate's node set, following `deezer_ids.py`'s docstring and the
`LUX-4` pattern — re-extract over the population, ship as dated package data, **never edit the
existing dated files in place.** Report the wall clock first if it projects beyond a few hours.

**Projection, reported before starting: minutes, not hours.** Both frozen extractors are
**offline** passes over the local 17 GB MusicBrainz artist dump — `~2 minutes` and `"minutes"` in
their own docstrings — and the dump was still on disk. No network, so nothing depends on a third
party answering. It did not approach the threshold, so no stop was taken. **Actual: 2.2 minutes**,
2,945,470 dump rows, all 112,855 population artists matched.

### The frozen rules are IMPORTED, not copied

`cand_ids_extract.py` imports `DSP`, `host_of`, `id_tail`, `is_artist_url`, `normalise_id` and
`facts_of` from `2026-09-05-lux4-extract/lux4_extract.py`. Copying them would have been the moment
a parsing rule could drift silently from the map it vouches for; importing makes drift impossible.

### ⚠ ONE KNOB, and the one I deliberately did not turn

**Only the population changes.** In particular **Deezer keeps `dsp_ids.py`'s original rule** — a
numeric tail, with no `is_artist_url` check. `lux4_extract.py` added that artist-vs-album check for
Spotify and Apple on 2026-09-05 and it was never back-ported to Deezer. Adding it here would
probably be an improvement *and* would make this a two-column change, after which no coverage
difference could be attributed to the population alone. **Filed as a deferral instead**, with the
condition that it must not ride along with a population change.

### The population is a SUPERSET of what he asked for, and the reason is a regression he did not ask me to accept

He said "the candidate's actual node set". I extracted over **candidate ∪ served ∪ every key the
three shipped maps already held** (112,855 artists). The candidate keeps 57,909 of the served
map's 58,838 artists but not all of them, so a candidate-only extraction would have **silently
dropped ids for 929 artists the served map still contains**. The dump read dominates the cost, so
the superset is free. Both frozen extractors used a superset for the same reason.

**The script refuses if the result is not strictly additive** — if any MBID the shipped maps held
is missing from the new map, it exits rather than writing, because over a superset population that
could only mean a parsing rule moved. It passed.

### Test pins re-recorded, not deleted

`test_deezer_ids.py` pinned the 2026-08-02 map's count and sha and failed, correctly. Re-pinned
with the previous values kept in the comment and the reason recorded. The additive guard is what
makes the new count safe to pin: it can only ever have grown.

**Builder 292 passed, api 295 passed.** Snyk on the new module: 0 issues.

### This PARTIALLY discharges `NEXT.md`'s `LUX-4`-armed deferral

The deferral is *"before an `ALG-B` artifact is ever served, re-extract over its population"*.
**It is discharged for the `LBA-A6` candidate's population only.** The served lineage's own
re-extract **remains armed**: `graph-msw-tu50.bin` is still served, and while the new maps cover
every artist it contains, the deferral's condition is about the lineage and not about this
candidate. A session that reads this as fully discharged has over-read it.

---

## Task 5 — the rebuild, §8 item 3, and two of this session's own defects

**Figures: the candidate README.** The artifact is `LBA-A6-candidate.bin` — a NEW name, chosen so
that stage 2's `LBA-A6.bin`, a pinned input behind committed results, cannot be overwritten.

### The structural proof survived the re-extraction, which is the point of it

Rebuilt with the new package data: the bare re-serialisation is **still byte-identical** to stage
2's `LBA-A6-bare.bin`, and the eight structural fields are unchanged. **Neither fame nor the new id
maps moved the map.** The four metadata id lists differ, as they must.

### `DEP-24` is honoured mechanically rather than by care

`ARTISTPATH_GRAPH_SHA256` is **read back out of the written sidecar** and verified against the
file on disk before the run is called a success. Nothing transcribes it, and nothing carries it
from the variable that wrote it.

### Two guards on serialisation, and they ask different questions

`--serialise` refuses without `--acceptance-ruling` — *did he decide?* — and refuses again if
`check_acceptance` still rejects the build — *was the decision actually implemented in
`acceptance.py`?* Keeping them separate is what makes it impossible for a ruling about
**recalibrating bounds** to be discharged by **bypassing the check**, which is a different act
with the same immediate effect.

### Defect 1 — I guessed an attribute name instead of reading it

The first serialising run built for 11.7 minutes, passed every check, wrote the artifact and the
sidecar, and then died on `store.fame_lb`, which `GraphStore` does not have. It keeps
**`fame_lb_pctl`**, the percentile ranking.

**The correction is better than what I intended.** The check now asserts the *ranking* is present
and correctly sized — which is the exact quantity `LBA-AM4` says the candidate acquires at §8 item
1 and that no `LBA-` arm could measure. A candidate with no fame ranking would make `LBA-G5` test
something other than what the amendment says it tests.

⚠ **And the resulting number needs its caveat carried.** `fame_percentiles` gives a measured null
**0.0** — maximal obscurity under the novelty construct — while excluding it from the frame, so no
NaN survives and the count equals N. **It is not the measured count**, which is 87,391 of 87,394.
Both are in `cand_build.json`; a reader taking the first for the second would conclude the
instrument measured three artists it did not.

### Defect 2 — a closing line that printed a false statement

The script ended by printing *"STOPPING before serialisation"* unconditionally, so the successful
serialising run announced that it had stopped before serialising, in the same output that recorded
the artifact and its checksum. Harmless to the artifact and corrosive to the record — the run log
is what a later session reads. Made conditional.

**Both defects are the same shape as the acceptance-table one earlier in this session:** an
instrument reporting something other than what it did. None of the three touched an artifact; all
three touched what the record would have said about one.

---

## Task 6 — `LBA-G5` PASSES and the owner ADOPTS, 2026-09-25

*Session of 2026-09-25, branch `charlessavage90/candidate-map-adoption-decision`. Scope from the owner:
"I've tested the candidate map locally enough to make a decision on its use."*

### The gate verdict, in his words, verbatim

> The gate passes: the general user experience is improved compared to the live production graph.
> Specifically:
> - journeys as a whole are *more* coherent
> - novel artists often show up earlier and at least as frequently as the live graph (one note on this below)
> - Treating this as a separate point - the two things above hold true together as well. The novel
>   artists are more often more coherent picks than the live graph
> - One thing about the live graph became more clear when I was able to exercise it side by side with
>   the candidate: the novel artists it produces are frequently the class of "solo / contributing"
>   artists (e.g. a guitarist from a famous band releasing a single solo album). Frequently might be
>   my perception, but it did feel like the first 1-3 novel artists that appear in a path in the live
>   map are in that class, and when you bypass them, it returns to known artists
> - The one note I had on novel artists in the candidate graph is that when I looked them up on
>   spotify, those novel artists were not "obscure" - they were often fairly popular on spotify
>   (500k+ monthly listens), just not known to me. Based on the product requirements / WGLL, this is a
>   pass regardless, but in the future, I'd like to explore whether we can "deepen" obscurity by
>   adjusting the routing within the graph, especially after multiple "dig deeper" presses
>
> 2. We adopt. Clear decision based on the results

**Read against his pre-written criterion (`LBA-AM4`), not re-scored:** neither limb fires. The first
limb, *novel artists become more difficult to surface*, is contradicted by his second bullet. The
second limb, *novelty traded for coherence*, is contradicted by his third bullet. The
more-than-half effect size is never reached. **`LBA-G5` PASSES**, and per `LBA-AM5` that licenses
only the adoption decision, which he took in the same message. `LBA-AM4` bar 1 still holds: his
bullets are a use verdict, not a measurement of path quality, and **no figure may be derived from
them.**

**His observation about the retired map** (the solo/contributing-artist class among its first
novel artists) is recorded here as his, and **he marks it as a possible perception**. It is a lead,
not a finding. No instrument has measured it.

**His forward note** (the candidate's novel artists are often widely listened on Spotify, and he
wants to explore deepening obscurity after several Dig-deeper presses) is the question in **issue
#200**. It is recorded there as a comment. It is his to trigger, per the path-quality rule.

### The pair log, and the #215 exclusion

`builder/analysis/2026-09-22-lba-a6-blind-listen/lba_g5_pair_log.md` is now filled, derived by
`lal_g5_pairs.py`, not by hand. The script gained `--exclude "FROM → TO"` (`drop_pairs`, applied
**before** folding so a dropped pair's rerolls cannot attach to a neighbouring journey; test added).
**He confirmed he never ran Miles Davis → Daft Punk**, so the whole pair is dropped, not only #215's
journey ids. I checked this before relying on it: every event of that pair falls in `api-part4.log`
lines 89–277, and its journey ids are exactly #215's seven plus `unknown`. So the two rules select
the same events.

### Adoption, mechanically

- **`ApiConfig.graph_path` now defaults to `../builder/scratch/graph-lba-a6.bin`.** That file is
  `LBA-A6-candidate.bin` copied under a served name into the main tree's `builder/scratch/` with its
  sidecar. The sidecar names no file, so the copy is the same artifact. **After the copy I checked
  the sha256 and byte count against the sidecar, and both match.** It carries the same five additive
  metadata keys as the production artifact `graph-lux4.bin`, so no clip or streaming-link field is
  lost.
- **Issue #138 closes on the adopted branch.** The calibration target and the served map are one
  artifact. The rejection test is kept, reworded, and renamed `…previous_served_map…`: rebuilding the
  old map, for example to roll back, still needs the previous bounds restored first.
- **The landing samples moved, as the e2e spec says they will after an adoption.** Re-measured
  through the shipped app in-process on the candidate, never against the gate's :8000 listener
  (#215's lesson). Two of three chips are unchanged. Bad Bunny → Chappell Roan went from 8 stops to 3,
  and the desktop teaser re-routed. The constants follow the router. **Whether those remain the right
  showcase pairs is a content question and his** (issue filed).
- **The builder's lineage comment was corrected.** It said the adopted map descends from the ALG-B
  crawl archive. The adopted map's similarity now comes from a ListenBrainz-dump archive, and its
  rebuild is the pre-registration's §6.

**Not done by this task: the production deploy.** `infra/README.md` §4 with `GRAPH=graph-lba-a6.bin`,
both `s3 cp` lines, and the post-deploy sidecar check (§7). It is outward-facing, so it runs on his go.
