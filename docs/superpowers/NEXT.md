# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. **One exception: the
STANDING FACT block below is preserved in place across every rewrite** — it is a durable fact
about the deployment, not status, and it is the only thing here that a rewrite must carry
forward rather than replace.

**"Rewritten wholesale" means the outgoing block LEAVES, and that is not what happened for
five weeks.** Sessions rewrote the top block and demoted the old one into an archive kept
inline, then went on annotating those archived blocks at each closeout — so the file grew
monotonically from 150 lines on 2026-07-30 to **2,063** on 2026-09-05, of which 1,738 were
superseded status. **The outgoing block now moves to
[`NEXT-ARCHIVE.md`](NEXT-ARCHIVE.md) and is frozen there**, and anything in it that still
binds is distilled into the registries below *before* it goes — that distillation is the step
whose absence made keeping the whole block feel necessary. `closeout` `A2-next` owns the
procedure. **This document** is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
Track B's live in `findings/2026-07-30-track-b-cap-selection-results.md` (and its raw
`cb_scores.json`); the adopted graph's stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited, never restated.

**It owns no git state either, and that is the same rule, not a second one.** Merge state,
which branches exist, what commits landed — `git` and `gh` are authoritative for all of it,
and `session-start` §C checks them anyway. **The cadence writes this file BEFORE the merge**
(work → `closeout` → the owner merges), so any merge state written here is false by
construction within the hour, and every fresh session then opens by reporting a discrepancy
that is really the process working. So: name the branch and PR number as **addresses**, and
write the owner's remaining actions as an **ordered sequence** — never as a position in one.
**A session finding this file silent on merge state has found the design, not a defect.**

> ## 📍 STANDING FACT — THE APP'S ADDRESS IS `https://unsung.fm`, since 2026-09-03
>
> The domain was bought 2026-09-02 and cut over 2026-09-03: ACM certificate swapped,
> CloudFront alias flipped, `viewer_function.js` re-synthed. **`musicapp.cmiller.io` 301s here
> with the path preserved**, so every link already shared still works. Status blocks below
> dated before 2026-09-03 name the old host and are left as written — they record what was
> live at the time. **This note survives a `closeout` rewrite: it is a standing fact about the
> deployment, not status.** The runbook is `infra/README.md` §1a.
>
> ⚠ **The app is still NAMED "Artist Path" in the DEPLOYED UI.** Only the address moved. The
> rename to "Unsung.fm" was **approved 2026-09-08** and is built on the `UXR-` branch — do not
> assume it has been deployed.

**Last updated: 2026-09-12, at the `LBD-AM6` preparation of `LBL-` listen 2.** **Nothing a
listener sees changed in this work** — the live site is as the 2026-09-08 deploy left it, and
`TEST-QUEUE.md`'s three entries are still his to press, untouched here.

**`LBL-` listen 2 is PREPARED and UNRUN.** The owner chose the route on 2026-09-12: keep the
registered comparison — `LBD-A0V` against `LBD-A5V`, *does accepting a connection two listeners
support, instead of four, give better journeys?* — and **re-draw the pairs**, with the six
instrument fixes listen 1's findings note §4 asked for. Committed as **`LBD-AM6`**, before any
listen-2 journey existed. Branch `lbl-listen2-prep`, **PR #122** (addresses only; `gh` says where
they are).

**What changed, in plain terms.** Listen 1 tied because the pairs were too easy, not because the
maps are alike — most rows he could not call were rows where he knew every artist on both sides.
So candidate pairs were screened, before the amendment was written, on two properties: the journey
must be long enough to have a shape at every depth on both maps, and the two maps must actually
disagree. Survivors were then ranked by how few of the artists in between he already knows. **The
screen never looked at which map was better, only at how much they differed** — a screen that
preferred one map's journeys would have hand-picked the pairs that map wins on. Counts are owned by
[`../../builder/analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.md`](../../builder/analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.md)
and restated nowhere.

**Every read is unchanged.** `LBL-R1`–`LBL-R4`, their listen-2 plain sentences, the margin bar and
the row count are exactly as `LBD-AM5-5` registered them. Each row now also asks whether the two
questions pulled him in opposite directions, and how strong each pick was — **and the tally does
not read the strength.** A tally that did would be a different read wearing the same names.

**`LBD-D6` is RULED** (2026-09-12; quoted verbatim in `LBD-AM6-7`): `LBD-A4` is **waived for
listen 2 and enforced before `S4`**.

⛔ **No session starts the listen on its own initiative, and the session that prepared it may
neither run it nor write it up** — it has seen journeys labelled by map. Entry point:
[`2026-09-12-HANDOFF-lbl-listen2-prep.md`](2026-09-12-HANDOFF-lbl-listen2-prep.md).

**What stays open whichever way listen 2 reads:** stopping the `LBD-` track remains a complete
outcome, and `S4` — the adoption decision proper (population rule, API sizing, fame source, refresh
procedure) — remains its own pre-registration and rebuild. ⚠ **No listen outcome adopts anything**,
and `REQ-41` bars reading a tie as equivalence.

**THE REMAINING ACTIONS ARE THE OWNER'S, in this order — and per the rule above, this file
does not record how far down the list he has got.**

1. **Run the three queued use-the-app tests** — live since the 2026-09-08 deploy. Nothing
   here changed them.
2. **Merge PR #122.**
3. **Decide whether to spend listen 2.** Everything is prepared; it costs his ear and a sitting.
4. **When he does:** a fresh, mechanics-only session runs `RUNNER-BRIEF.md` end to end, and a
   further fresh session writes up the result.

---

**Superseded status blocks live in [`NEXT-ARCHIVE.md`](NEXT-ARCHIVE.md), frozen and never
edited.** They are history, never status; nothing in this document depends on reading them.
Anything from them that still binds is in the registries below.

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). **`DD-F1` remains a defect, not an accepted limitation** — Track B's `R2`
read measured where it can and cannot be moved; the results note owns that reading.

## PARKED — owner's explicit decision; his trigger, never a session's
- **Option C** (the same-name population probe), **`SEL-`**, **closing or keeping the
  2026-07-29 famous-to-famous defect ruling**, and **the three candidate path-quality fixes in
  the `CXR-` README** (each needs its own pre-registration) — all open, none blocking, all his
  trigger. *(Carried from the 2026-09-08 status block, distilled 2026-09-10.)*

- ~~**Whether the fame instrument is fixed BEFORE or AFTER the graph work**~~ — **RULED
  AND DONE 2026-08-02: before, and it was.** The `FPC-2`/`FPC-9` pairing rule stays for
  reading that record. Struck, kept for the record.
- ~~**Whether a currency change re-reads prior fame-scored results**~~ — **RULED
  2026-08-02: NO re-read.** Prior results stand in their measured currency;
  cross-currency comparisons barred. Struck, kept for the record.
- **The coherence thread** — execution log
  [`2026-07-30-fame-proxy-coverage-execution-log.md`](2026-07-30-fame-proxy-coverage-execution-log.md)
  §7. **Its instrument half was probed 2026-07-30 and the kill gate fired** (`COH-`,
  above): §7's own warning — tag coverage thins in the same tail — measured true at
  band level, so no tag-based instrument gets built on this artifact's population as
  measured. What remains parked, still the owner's trigger: the **structural half**
  (the cost function assumes coherence is additive along edges while
  `PRODUCT-REQUIREMENTS`'s second clause is not — untouched, unproposed), and any
  **reopening of the instrument line on a route-population gate** (`COH-3`'s 74.2%
  on delivered interiors is the recorded argument; a reopening is a new
  pre-registration designed cold, never a re-read of the fired gate).
  **⚠ The third strand was UNPARKED 2026-07-30 and has since CONCLUDED** — the `TAS-` tag
  discrimination probe ran to all eight tasks and found **neither architecture has an adoption
  case** (see "Closed" below). *Corrected 2026-09-05: this read "it is the live work; see
  'Next' above" for five weeks, and that pointer now dangles — the block it named is in
  `NEXT-ARCHIVE.md`.* Its caveats below were all carried into the
  pre-registration rather than lost: the reordering limit is stated in `TAS-4`'s bound, the
  self-audit circularity is why the track has no offline scoreboard and ends at a blind
  listen, and the Track-B-shaped cost is why `TAS-` measures before proposing a rebuild.
  **One caveat was measured and turned out to understate the case:** the strand assumed
  selection "reorders candidate lists", which is true — but `TD-2` measured that reordering
  converts to roughly twice as much map change as per-artist counting suggests, because
  every swap also *creates* a connection. Retained below as written.
  *(Original text, superseded on status only:)*
  **A third strand, owner-raised 2026-07-30 after the probe and explicitly flagged
  worth a future session: tag-aware neighbour SELECTION at build time, at the top of
  the graph.** The probe's kill was about *scoring paths*; selection lives where
  candidates are many and labels near-total (top bands 94–100%, `COH-2`), and barely
  operates where labels are dark — the coverage failure and this use are close to
  complementary. Three caveats travel with it: it *reorders* candidate lists and
  cannot add famous→obscure supply (that stays with candidate supply and router
  pricing); tags spent on construction are spent as an evaluator — §7's self-audit
  circularity in new clothes, leaving the 11 blind verdicts as the only independent
  check; and picking it up is Track-B-shaped work — a selection-rule change, so a
  rebuild, a pre-registration with a factor table, and a blind listen (`REQ-38`).
  `COH-5` makes the data side cheap (~47 min for a full tag frame).
- **The cap-rule decision for any rebuild** — Track B's `R1` is its input; adoption of
  any rule owes the blind listen.
- ⚠ ~~**`ALG-B` adoption**~~ — **THIS ALREADY HAPPENED. Corrected 2026-09-05.** `ALG-B` is
  the **adopted map's lineage** and has been since 2026-08-06 — `graph-msw-tu50.bin` was built
  from the `ALG-B` archive (its manifest records `contribution_3`) and `ApiConfig.graph_path`
  serves it. Stated in source, at `builder/…/config.py`: *"⚠ ALG-B is the ADOPTED map's
  lineage."* Left in the parked list it would send a cold session to re-decide a month-old
  decision. **What is still open and must not be conflated with it:** `BuilderConfig.algorithm`
  still *defaults* to ALG-E deliberately, so every command touching the adopted lineage passes
  `--algorithm` explicitly (`CEX-R5`) — flipping that default is the **re-crawl** decision, it
  is his, and it is the entry in "Must not be changed" below. Whether the `REQ-38` blind listen
  this row claimed was owed was ever spent is **his to say, not this document's**; the original
  inputs (Track B's `R0`/`R2`/`R3`, `RC-R1`'s stranding figures) stand as written.
- **The router-side pricing track** (plan §0 ruling 2) — `R2`'s `ALG-E` null is its
  motivating evidence: the quota edges exist and production weights decline them. Needs
  its own pre-registration, which must consume `TB-P5H-7`.
- **The candidate-pool product decision** — whether a shortened-but-obscure bypass
  candidate (Track 3's DD-A2 or a TB arm) ships at all.
- **The one-statistic cross-track recompute** that must precede any DD-vs-TB comparison.
- **Any blind listen on a router-only candidate** — deferred to the full stack.
- **Re-evaluating bounded-degree itself** (router-priced unbounded graphs) — Track B's
  `UC` reference rows now give it measured baselines; his trigger; owes its own blind
  listen.

**Owner actions, all three discharged 2026-08-02 — kept struck for the record.** *(Heading
corrected 2026-09-05: it read "Still owed by the owner" over three items marked done.)*

1. ✅ **The use-the-app test — DONE 2026-08-02.** The redesign entry was run in full against
   `https://musicapp.cmiller.io`, desktop and phone. Everything passed; journeys he knows well
   were **unchanged**, which was the check that mattered. One incidental finding worth
   carrying: **the loading screen is often too fast to see**, so nothing should be measured or
   redesigned on the assumption a user experiences it.
2. ✅ **The iPhone script — DONE 2026-08-02, and it settled a Gate 3 blocker.** All three
   questions clean: clips play, the bottom bar clears the home indicator, artist-name typing is
   unaffected. **`G3-F2` is FALSIFIED** — see the gate table below.
3. ✅ **The `--prune` publish pass — DONE 2026-08-02.** Two orphaned assets from the
   pre-redesign build deleted; live site verified afterwards. See the deferral table for the
   pre-flight a successor should repeat.

~~**One action is owed by the owner: merging draft PR #69.**~~ *(Discharged — #69 merged
2026-08-03 at `2e3b017`. Struck 2026-09-05, having read as a live owner action for a month.
**Current owner actions live in the top block, never here.** This section is the
parked-decision registry; status accumulating in it is what made the whole document grow.)*

~~**Nothing is queued in [`TEST-QUEUE.md`](TEST-QUEUE.md).**~~ *(FALSE since 2026-09-04;
struck 2026-09-05. **This document must not state the queue's contents at all** — the same rule
as merge state. `TEST-QUEUE.md` owns it, `session-start` reads it, and an entry is live only if
its **topmost** heading says so.)*

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.
*(Verified 2026-09-05 — still the password-removal plan's only unrun task.)*

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). **One blocker removed 2026-08-02: `G3-F2` is FALSIFIED** — HIGH, "blocking if confirmed", and the review named the deciding test (*"one tap on a real device confirms or kills it"*). Clips play on a real iPhone. ⚠ **Read what that does not mean:** the code was NOT changed to achieve it — `usePlayer.ts:49` still awaits the URL before `player.play(url)` at line 60, which is exactly the pattern the review flagged. The finding's *description* was accurate; only its *consequence* is removed, and it rests on iOS's current tolerance rather than on the code being correct by construction. **Do not cite this as "the iOS play path is correct."** The rest of the blocking set (`G3-A1`–`G3-A4`, `G3-S1`–`G3-S3`, `G3-Q1`, `G3-Q2`, `G3-F1`) is untouched. |

## Closed — do not re-plan or re-investigate

- **Track B's cells and reads are closed.** Builds are byte-deterministic and the raw
  outputs are committed — do not re-run cells to "check"; re-running is only ever
  instrument work under a harness change that re-fires `CRS-G1`.
- **`R2`'s `ALG-E` null must not be cited as "the quota rule cannot fix `DD-F1`"** — it
  is "the router declines the quota edges *at production weights*"; the pricing track
  above owns the difference.
- **`PS100` ≡ `MK100`, byte-identical, both archives** (`LBS-3`) — one graph, never two
  data points. And **`proximity_select` at bound 50 measured materially worse on
  stranding on both archives** — do not re-propose it as a candidate without new grounds.
- **The pair-set attrition decision is closed** — the `× lower` classes are unreadable
  per `CRS-G3` at the committed draw; a redraw is a new §8 amendment designed cold, the
  owner's trigger if he wants obscure-endpoint path reads.
- **The source `algorithm` parameter is a CLOSED ENUM of six values** (`CS-P0e`);
  `limit` ≤ 100, `threshold` ≥ 10, production already at both edges. Parameter semantics
  are `LBS-`'s, from source (`findings/2026-07-30-lb-algorithm-semantics.md`).
- **`CS-P0c` must not be cited as "no cap rule can fix `DD-F1`"** — scoped to own-list
  selection; the prereg's §0 table owns per-family bearing.
- **The `--target`-capped trial crawl is RETIRED for `AS-H2`** (only).
- **Track 2, Track 2F and the ceiling toll are exhausted nulls. Do not re-run any.**
- **Track 3's and Track 3b's results are closed** — do not re-run their arms or
  re-litigate TB-R2.
- **The routing-side toll family is closed for descent claims**; any explicit
  length-preserving constraint is a new device needing its own pre-registration
  consuming `TB-P5H-7`.
- **Loosening the both-ways cap without a simulated bound was rejected (`MKS-5b`) — and
  Track B is that simulation, now RUN.** Its results note is the record.
- **Famous-pair first-path fame is barred as a scoring criterion** (PLA-R1); Track B's
  prereg resolved its applicability and `CRS-C5` measured presence, not fame.
- **The nameless-artist question is decided** (drop; implemented, `GR-1`).
- **The builder-side p99 rescale stays parked** (DD-R2's trigger never fired).
- **The OneDrive migration is COMPLETE**; the old tree is an archive.
- **`G3-A5`, `G3-A2`, `G3-S7`** closed as recorded; **`G3-A3` does not fire**.
- **`RMD-6`, `RMD-11`, `RMD-12`, `RMD-13`, `FRO-1`, `FRO-4`**, the `DEP-33` blockers, the
  Gate 1 clip work, **Track 1**.
  - ⚠ **One exception:** `BYP-13` — a card playing a clip by a *different artist of
    the same name*. Not path work and not inside any pause. The builder carries
    MusicBrainz-recorded Deezer artist ids in the APG1 metadata blob and the api resolves by
    identity before falling back to name search.
    **⚠ CORRECTED 2026-09-05. This entry read "a fix is BUILT and is INERT until a rebuild"
    and "the defect is unchanged in the running app, which serves a pre-2026-08-02 artifact
    with no ids". Both have been FALSE since 2026-08-06**, when the `MSW-` rebuild landed:
    the served artifact `graph-msw-tu50.bin` (sha `43dd82bb…`) carries **`deezer_ids` for all
    58,838 artists**, read from the artifact's own metadata blob rather than inferred.
    **The fix is LIVE.** It is *reduced*, not closed — the id path inherits MusicBrainz's
    link accuracy; the link-quality row in the deferral table is unaffected and still
    governs.

## Must not be changed, and each has a reason
- **`LBD-G1` fired (2026-09-09) and was overridden by owner decision (`LBD-AM3`, 2026-09-10)
  after a diagnosis.** The 0.5844 reading and the 0.60 floor both stand; the arms were read
  anyway. Never cite `LBD-C1` as "passed", and never re-read that gate on the dated corpus for
  the record — `C1-DIAG-1` is a diagnostic. `--created-before` in `lbd_similarity.py` is
  likewise diagnostic and is never set for an arm.
- **`LBD-AM4` (2026-09-10): the build-stage population is an EXPERIMENTAL CONTROL, not a
  population rule.** `LBD-A0`/`A2` were built over exactly the extended map's 88,685 artists so
  each differs from the ceiling probe's bridge control in the data alone; `S4` decides the
  shipped population separately. **`drop_unlistenable=True` via the `20260809` override
  supersedes `LBD-X3`'s `False` for that population ONLY** (measured inert: zero drops in both
  builds); `LBD-X3` stays right for any arm over the table's own population. **`LBD-A3` is
  barred from building**, not deferred. And the `A0`-vs-served-map gap is a bundle of lineage
  terms — never cite it as the reimplementation's effect.
- **`LBD-AM5` (2026-09-10) and the `LBL-` listen 1 (2026-09-11): the same shape, one level up.**
  The served population `V` is an **experimental control, not a population rule** — `S4` still
  owns the shipped population, the fame source, API sizing and a refresh procedure, and **no
  listen outcome adopts anything.** **`LBD-X4` and `LBD-X5` travel with every listen-1
  sentence**: 439 artists took part in the served build's cap step and could not in
  `LBD-A0V`'s, and the served-vs-`LBD-A0V` data gap is a bundle (corpus age, the absent
  `filter_True`, today's mapping, the uncredited band-member class, our tie-break) — **no
  attribution to "the data", and none inside the bundle.** **The listen-1 verdict may not be
  re-listened** (`GBL-` §5's run-once rule); a further listen is a new amendment on new pairs. **`LBD-AM6` (2026-09-12) is that amendment**, and adds two bars of its
  own: the pairs were selected on the **magnitude** of the two maps' difference and on
  unfamiliarity, **never on direction** — a screen that saw direction would invalidate the listen;
  and **`LBD-X6`**, listen 2's result may not be generalised to the cheaper pairing form until
  `LBD-A4` has run and `R10` has been read. **Pick strength is recorded but never tallied.**
  The drop list for `V` is the served lineage's `20260805` file, never `LBD-AM4`'s `20260809`,
  which would drop 31 served artists. **The owner's closing note changed no number** — the
  findings note's §1.5 carries the arithmetic — and his "slight"/"strong" wording is not a
  strength coding and must not be tallied as one.
- **`top1pct_degree_mass_frac` is saturation-degenerate** (2026-09-08): where at least 1 % of
  nodes sit at the degree bound it reduces to the bound over a hundred times mean degree and
  cannot see edge arrangement. The `DCF-` README's forward note names which of its own arms the
  measure is valid on; its numbers are untouched.
- **`CRS-C3` was structurally unable to fire on any selectable Track B cell** (2026-09-08), so
  its null carried no information about concentration. Track B's results document is unedited
  and carries the correction at its head. It says nothing about `CRS-C4`, overturns none of
  Track B's conclusions, and is not evidence about any cap rule.
- **Pin `--archive-dir scratch/grt-archive-algb.pre-cex-snapshot` for any build of the served
  lineage.** The ALG-B archive tree gained tens of thousands of response files after the served
  map was built; an unpinned rebuild reads the extended crawl (`CXA-` leftover).
- **Rulings of 2026-09-04, not to be re-litigated or re-discharged:** the 2026-09-03 address
  test (run and passed), either 2026-09-01 test-queue entry, and the depth-0 half of the
  owner's revert report — NOT a defect and NOT open work. That closed them as items and
  overturned no measurement: `CXR-P3`'s null and the diagnosis README's "unexplained by anything
  here" remain exactly true. And do not re-queue "tell me how it feels" (owner ruling,
  2026-08-07): his long-run evaluation is continuous and `TEST-QUEUE.md` does not hold it.

- **`max_size=2` (`stack.py`)** — the **cost ceiling**, the only automatic spend control.
- **App Runner is excluded from CDK tagging** — tagging forces a replacement that cannot
  succeed; pinned by `test_app_runner_is_deliberately_left_untagged`.
- **The ACM validation `CNAME` at Cloudflare** — delete it and the certificate silently
  fails to renew in ~13 months.
- **The rate limit is `10 / 10 s`, not `30 / 60 s`** — see `infra/README.md` §1a.
- **The `acceptance.py` blank-name check** — do not weaken it to unblock a build. And
  `GRT-P2` stands: the guard is blind to a severe famous-artist collapse at any scale;
  strengthening it is an unclaimed design question, not part of Track B.
- **The mirror's two device knobs (`w_known_ramp_pctl`, `w_known_thresh_pctl`) stay 0.0.**
- **`BuilderConfig.algorithm` still carries `contribution_5`**; changing it *is* the
  re-crawl decision. (Verified 2026-09-05: `PRODUCTION_ALGORITHM` = ALG-E, `…contribution_5…`.)
- ⚠ **`cap_strategy` is `trimmed_union`, NOT `mutual_knn`** — corrected 2026-09-05. This entry
  read `mutual_knn` because it was written before `MSW-` flipped it on 2026-08-06, and the
  block recording that flip was demoted into the archive without the registry being updated.
  It is the first distillation defect the split found, and it is the exact shape the archive
  header warns about. The live knobs are **`union_top_j = 50` and `union_degree_ceiling = 50`**;
  `max_neighbours_per_artist = 50` is still set but is **ignored under `trimmed_union`**, so
  reading it as the live degree bound is wrong. `mutual_knn` remains supported, and every
  pre-2026-08-06 figure was measured under it — **check which rule a claim is in.**

## Deferred, with conditions

| Finding | Condition |
|---|---|
| **The plan for `DLS-` items 4–6** (restructure `CLAUDE.md`; rebuild the map around role lines and add the lint checks; slim the rituals). The owner answered `DLS-Q1`–`Q6` on 2026-09-11 ([findings §5a](findings/2026-09-10-documentation-layer-strategy.md)). **It also carries three items:** `CLAUDE.md` prose the harness now enforces or makes redundant (the `UV_LINK_MODE=copy` prefix; "never use `docs/reference/`"); `closeout` D6 counting `.claude/rules/*.md` files that have no `paths:`, which load in every session; and item 3's unbuilt remainder, a hook refusing commits on `main`, which the owner has not been asked about. | **After the `DLS-T1` read and the live `LBD-` session's next closeout.** Written by a fresh session from the findings document, with a handoff point between each item. The D6 fix is due earlier if any rule without `paths:` is added. |
| **The APG1 lockstep tests (PR #118) pin only the fixture's four base metadata keys.** The committed fixture has no `deezer_ids`, `fame_lb`, `spotify_ids`, `apple_ids` or `artist_facts`, so those stay covered only by each package's own hand-built tests. | **The next time the committed fixtures are regenerated (`closeout` D2):** regenerate with those keys populated and re-derive the api test's pinned values. |
| **The `DLS-T1` read** (*when a session opens a plan or a spec, does a rule scoped to those folders arrive in its context without anyone asking for it?*). The instrument is armed by the `doc-strategy` PR: **do not remove `.claude/rules/plans.md` or the `InstructionsLoaded` logging hook before this is read.** | **Three qualifying sessions after merge, or 2026-09-24**, whichever comes first — read per [`findings/2026-09-10-documentation-layer-strategy.md`](findings/2026-09-10-documentation-layer-strategy.md) §6. **One dated observation is already banked and the read must consume it:** the `LBL-` write-up session opened a spec repeatedly and the rule did **not** load (its own `instructions-loaded.jsonl` shows only the two session-start `CLAUDE.md` entries) — **but it read through Bash, not the `Read` tool**, so the observation cannot separate "the rule never fires" from "it fires only on a `Read`-tool open". **What the read still needs is a qualifying session that opens a spec with the `Read` tool.** Written up in [`2026-09-11-lbl-listen1-read-execution-log.md`](2026-09-11-lbl-listen1-read-execution-log.md) §5. |
| ✅ **`LBD-M1` (population per arm)** | **DISCHARGED 2026-09-10** — reported descriptively by fame band for both built arms, figures owner §2. Struck, kept for the record. |
| **`LBD-A4` (the pairing arm)** — still unrun; `LBD-AM4-2` said so and no read here depended on it. | **Before any `S4` arm is pre-registered** — ~~before any further `LBD-` arm~~, **narrowed 2026-09-12 by the owner's `LBD-D6` ruling**, quoted verbatim in `LBD-AM6-7`: `LBD-A4` is **waived for listen 2 and enforced before `S4`**, because both listen-2 maps were derived with ListenBrainz's own pairing semantics — the faithful form `LBD-A4` measures the cheaper form against — so no `LBD-A4` result can change either map or listen 2's read. `LBD-A4` must run and **`R10` must be read** before any `S4` arm is pre-registered, and **every `S4` arm records which pairing semantics it uses and why**, per `LBD-D6`. **Still unrun; `LBD-D6` itself is now RULED.** One bar travels with it meanwhile — `LBD-X6`: listen 2's result may not be generalised to the cheaper pairing form until `LBD-A4` has run and `R10` has been read. |
| **`LUX-E2`** — blocked on the damaged `TAS-` sample; per-field population coverage is **not** a substitute read. | **A repaired sample.** Nothing in flight repairs it. |
| **`ULC-F4`** — the un-listenable keep-check measures the name-search route while the app resolves by identity first, so both drop lists drop artists the app can play. | **The owner's**: a re-census, a rebuild and its own pre-registration. Nothing blocks on it. |
| **Snyk has not scanned the FROZEN modules under `builder/analysis/`** — credentials expired 2026-09-07, the MCP server failed to connect 2026-09-08 and 2026-09-10 (morning); **it connected 2026-09-10 (evening) and the build-stage scripts added that day were scanned and are clean** (one Medium fixed by binding paths as DuckDB parameters); the pre-existing frozen modules remain unscanned; the owner accepted and deferred scanning for everything there on the grounds that none of it is live. His hands, not a decision: it opens a browser. | **Promotion of anything under `builder/analysis/` into shipped code** — which nothing proposes. |
| ⚠ **ARMED since 2026-09-08 — `LUX-4` merged and no rebuild has happened; the next rebuild of the served lineage must carry the re-extract.** **A slice of served artists carry NO recorded Deezer id**, so the api cannot take its identity-first clip path for them and falls back to **name search** — the `BYP-13` exposure the id path exists to close. Cause: the shipped id map was extracted over a population that predates the served map, which was built later from a further ALG-B crawl. Counts, the expected recovery, and why it is not fixed inside `LUX-4`: [`builder/analysis/2026-09-05-lux4-extract/README.md`](../../builder/analysis/2026-09-05-lux4-extract/README.md) §4. | **The first rebuild after `LUX-4` merges.** Until then, refreshing that key would change the artifact's existing `deezer_ids` and break `L4-T7`'s control arm, whose whole job is to prove `LUX-4` touches nothing that already existed. **A SESSION'S WORK, NOT AN OWNER DECISION** — the fix is obvious, the sequencing is methodology, and only the deploy needs his hands. The work: re-extract with `deezer` added to `KEPT_PLATFORMS` over the three-artifact population, ship it as dated package data, rebuild, take the new checksum to a deploy. **Metadata-only: no listening test and no acceptance risk**, because it changes no node, edge or score. |
| ✅ **Track B runs and reads** (`CB-5`/`CB-6`) | **DISCHARGED 2026-07-30** — run to completion; results note is the record. Struck, kept for the record. |
| ✅ **`CRS-A5` endpoint re-verification** | **DISCHARGED 2026-07-30** — one request at scoring time, 200, companion delivered descriptive-only. Struck. |
| ~~⚠ **A graph's manifest cannot say WHICH drop lists built it**~~ ✅ **DISCHARGED 2026-09-06 by `L4-T1b`** — `resolve_build_inputs` records the resolved filename and a sha256 over each applied drop list's bytes, plus the archive directory, and `log_build_inputs` prints them at build **start**. First exercised on the `LUX-4` build, whose manifest is the first here that can say which files produced it. **Recording only; a mismatch is NOT a refusal — the owner's decision, 2026-09-06.** Noted at both code sites that a gate here *could* fire in the first seconds, since both inputs are known before any work, so the "kills a long build at the end" worry applies to the acceptance bounds and not to this check; the reason to wait is that a reflexively-reached escape hatch removes the protection it guards. **A session must not add the gate on its own.** *Struck, not deleted: the condition fired twice — unhonoured on 2026-09-05, honoured here — and that history is the evidence the tracking worked.* Original text follows. |
| ⚠ **A graph's manifest cannot say WHICH drop lists built it** — it records the flags (`drop_unlistenable: true`) and the override pointer (`null` when the default is used), never the resolved file. `null` means *"whatever the default was that day"*, and the default is mutable: `CXA-` Task 2 moved the ALG-B unlistenable default and the `CXR-` revert did not move it back, which is how a rebuild came to silently differ from the live map by 31 artists. **All three drop families share the identical `dict[algorithm → Path]` pattern**, so `no_release` and `featured_credit` are the same trap unsprung. | **Before any rebuild is compared to another, and ideally before `LUX-E1` runs** — it makes that eval self-evidencing rather than requiring the hand analysis of 2026-09-05. **The fix:** record the resolved filename **and the sha256 of the file's bytes** for each family actually applied, and log both at build **start** so an unintended mismatch shows in the first seconds rather than at the end. ⚠ **CONDITION FIRED 2026-09-05 AND WAS NOT HONOURED — recorded rather than quietly re-deferred.** The condition read *"before any rebuild is compared to another, and ideally before `LUX-E1` runs"*; `LUX-E1` then ran and two rebuilds **were** compared, without this. The consequence is exactly what the deferral predicted: the comparison needed a **hand analysis** to establish which drop list and which archive each build used, because no manifest could say. **Re-deferred deliberately, with a tightened condition: before the `LUX-4` rebuild (`L4-T7`), which is the next rebuild comparison and is already planned.** *(The stale "~23 minutes" was struck here too — the live manifest records ~40 s for a whole build.)* Hash the bytes rather than reuse the payloads' own hash keys — they are inconsistent (`sha256_over_sorted_mbids`, `sha256_over_sorted_drop_mbids`, and `featured_credit` carries none). **Purely additive and cannot block a build**; the sidecar is written after the artifact is serialised, so it cannot perturb a sha or confound `LUX-E1`. **Whether a build should also REFUSE on a mismatch is the owner's** — a hard gate can kill a long build at the end and needs an escape hatch; decide it after `LUX-E1`, when we know whether mismatches are rare or routine. Mechanism and figures: [`builder/analysis/2026-09-05-lux-e1-drift-source/`](../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md). |
| **`docs/README.md` restates its documents rather than routing to them** — 336 KB, the largest document in the project, 95% table rows, **275 rows at a median 1,180 characters**, and the file `CLAUDE.md` tells every session to read first. A probe of its longest rows against the documents they describe found **15/19, 25/25 and 17/17** of a row's identifiers also present in the document. That is the one-document rule violated in prose, and it drifts the same way — the 2026-09-04 audit found a HIGH where the document had been updated and its row had not. | **The owner's trigger; he deferred it deliberately on 2026-09-05.** ⚠ **The fix is NOT to strip the map** — the summaries earn their place by letting a reader decide whether to open a 105 KB execution log, and compressing live prose to make a number go down is the damage this project has already paid for twice. What is missing is a **rule for what belongs in a row**: role, supersession, what it owns, and the one thing a reader must not get wrong. Applying it going forward costs nothing; retrofitting the **22 rows over 2,000 characters** is about an hour and captures most of the win. Rewriting all 275 is not worth it. Measurements owned by the 2026-09-05 handoff. |
| **`FPC-9`'s falsifier — an obscure-endpoint pair set for floor reach** | **If any realistic candidate device reaches materially more obscurity than production.** `FPC-9` used Track 3's `LIMIT` arm, a ceiling rather than a shippable route, and rests on 62 interiors from one arm on twelve pairs. Falsified by a device that reaches more obscurity *without* approaching `LIMIT`'s interior percentiles. |
| ✅ **`PRODUCT-REQUIREMENTS.md`'s Definitions section does not quantify the proxy's blindness** | **DISCHARGED 2026-08-02 — the condition fired and the edit landed.** The currency decision was made; the Definitions entry now carries `FPC-3`/`FPC-9`'s extent inside the retirement paragraph of the worldly-fame construct (owner-ratified edit). Struck, kept for the record. |
| ✅ **Full-graph MBID-keyed fame values** (`fp_fame_mbid --build`) | **CLOSED 2026-08-02 — the path is known-unreachable, not deferred again.** The currency decision adopted the LB proxy and **retired the worldly-fame construct**, so the condition ("adopts the MBID-keyed proxy") can never fire. Reopening requires a worldly-fame instrument to exist at all, which `RCS-` measured as currently unachievable. Struck, kept for the record. |
| ✅ **MusicBrainz tag/genre coverage as a coherence instrument** | **DISCHARGED 2026-07-30** — the coherence tag probe ran exactly this check and its kill gate fired (`COH-2`, vocabulary-robust per `COH-6`); the retrodiction stayed unrun. Struck, kept for the record. |
| ✅ **Adding `analysis` to builder's `testpaths`** | **DECLINED BY THE OWNER 2026-08-01 — closed, not deferred again.** Its condition fired at the closeout retiring the `TAS-` probe, and he ruled: **frozen code should not be tested by default.** `testpaths` stays `["tests"]` (`builder/pyproject.toml:25`); probe tests run only when a directory is named explicitly. The reasoning is durable rather than circumstantial — probe tests guard research code nothing ships and nobody will edit again, so collecting them would gate unrelated builder merges on a frozen artifact's committed JSON or a vanished scratch capture. **A future probe does not reopen this**; it inherits the same answer. Struck, kept for the record. *(This row carried a count of "34" until 2026-07-30; it was stale, and the count was never this document's to own — read it off `pytest analysis/ -q`.)* |
| ✅ **Replacing mutual k-NN with a tag-based degree limiter** | **DISCHARGED 2026-08-03 — the owner triggered it** (design-inputs family (c), 2026-08-02) **and it now has its cold-designed pre-registration**: `CRE-S2` (tag-guided ceiling on the union source, one-column isolated, `CRE-AM1`'s vote weighting inside it), with the family's premise tested by `CRE-D1` before the full arm set exists. Struck, kept for the record. |
| ✅ **`TAS-4` is not believable until the red instrument check runs** | **DISCHARGED 2026-07-31 for the SELECTION side** — the original check was withdrawn as unachievable (`TAS-AM3`) and its replacement `TAS-AM3a` passed at every λ. Struck, kept for the record. |
| ✅ **`TAS-5` is not believable until the ROUTING-side red check runs** | **DISCHARGED 2026-08-01.** `TAS-AM3`'s scope clause could not supply it — its pass conditions live on the pre-cap capture while `TAS-AM2` puts `TAS-5` on the artifact — so `TAS-AM5` constructed one, written **before any routing figure existed**. `TAS-AM5a` (equivalence) and `TAS-AM5b` (liveness) both passed on the full draw. Struck, kept for the record. |
| ✅ **Task 8 — the `TAS-` findings document is unwritten** | **DISCHARGED 2026-08-01 (latest)** — `findings/2026-07-30-tag-discrimination.md`, with the owner-facing read in execution log §17. Both conditions honoured on the page: `TAS-AM5c`'s caveat is carried at `TAS-5`'s section head and repeated at its figures, and `TAS-6`'s routing half is marked **VACUOUS** with its mechanism (`tas_guard.py:111`) rather than read as a pass. Struck, kept for the record. |
| **`TAS-6`'s routing half is unmeasurable on the committed draw** | **If, and only if, an obscure-endpoint draw is ever made for routing.** Its baseline is zero sub-decile interior artists, so no reduction can be measured and "not adverse" is a division-by-zero artifact. Not a defect of the run — a property of what production routing delivers, and a corroboration of `DD-F1`. |
| ✅ **Rarity-weighted agreement is a measured candidate device** | **MEASURED IN FULL 2026-08-01 by the `WGT-` probe** — the single-frame diagnostic became a 15-cell grid; the `WGT-` findings own the result and the device recommendation (rarity over `W4`, input-only). The trigger half stands: adopting any weighted device changes §1, an §8 amendment, the owner's call. Struck as a deferral, kept for the record. |
| **`W4` was never evaluated as a `TAS-` candidate frame** | **If the owner triggers a vocabulary change.** Now further supported: the `WGT-` grid evaluated `W4` under two weighting schemes and it remains the dominant frame; the style column is closed with a mechanism (`WGT-` findings §3a). A `W4` adoption would still be a new §8 amendment designed cold. |
| **Discogs alias expansion** | **If a frame amendment is ever triggered.** Discogs attribution goes through one MB-sourced ID; alias releases are invisible, so every Discogs figure is a lower bound (identical in every cell — no comparison threatened). `discogs_20260701_artists.xml` is already on disk; expansion is an exact ID join, no download, no name matching. |
| **The Discogs `masters` export** | **Iff Discogs support-counting is ever wanted.** Irrelevant to every presence-based use (unions are reissue-proof by construction) and would *lose* tail coverage (single-version releases often have no master); but it is the album-grain collapse that avoids the pressing confound (`WGT-4c`) if Discogs evidence counts are ever proposed. **Owner spot check 2026-08-01 (DSotM, 1000+ releases):** individual pressings accrete stray labels beyond the master's (`art rock`, `classic rock`, `pop rock` beside the master's two) — so the release-built frames carry mild curatorial noise a master build would not, the flip side of the coverage loss. Recorded; changes no measured verdict. |
| ✅ **The no-release-tail product decision** | **DECIDED BY THE OWNER 2026-08-01 — a drop rule is ADOPTED and the list is frozen.** Keep a release-less artist only where a commercial-DSP link exists **and** a clip resolves; **7,035 of 7,686 dropped, 651 kept** (`builder/analysis/2026-08-01-label-weighting/tail_droplist.json`, drop-list sha256 `d876c7ba…`). Struck as an open question; the wiring row below is what remains. |
| ✅ **The drop list is wired into the builder** | **DONE 2026-08-02, PR #62.** `drop_no_release_tail` (default on) applies the frozen list in `pipeline.py` beside the nameless drop, before the mass computation; the list ships as package data pinned by sha256. All three carried constraints are commented at their definitions. **The flag is an experimental control, never a shipping option** — it exists so a build-side experiment can hold the drop constant in a factor table, and so frozen probes can be era-pinned. Struck, kept for the record. |
| ✅ **One list, applied to any archive** | **DISCHARGED 2026-08-02 (latest) — both halves, the per-archive list and the refusal.** The list is selected by `config.algorithm`, which already decides which archive sub-tree a build reads, so a build's algorithm *is* its archive identity and no new `BuilderConfig` field was needed (the mirrors guard stays quiet, and `PERMITTED_ALGORITHMS[1]` still resolves for every frozen probe). Both censused populations ship as sha-pinned package data — `ALG-E` 7,035, `ALG-B` 9,501. The four **uncensused** algorithms raise `NoDropListForAlgorithm` rather than borrowing a list; the refusal is conditional on `drop_no_release_tail` being on, so the era-pinned probes that build uncensused populations with it off are untouched. **The magnitude of the averted defect, since the row understated it:** the two lists share only **2,712** MBIDs, so applying today's to an `ALG-B` build would have dropped **4,323** artists that rule keeps *and* missed **6,789** it drops. Mutation-tested — reinstating the old one-list behaviour turns five tests red. Struck, kept for the record. |
| ✅ **Whether the drop rule needs re-validating on the candidate population** | **RULED BY THE OWNER 2026-08-02: NO, and the reasoning is durable rather than circumstantial.** The rule does not rest on which artists are in the graph. It rests on three claims that hold for any population: release-less artists are generally poor recommendations to surface; the reason not to drop *all* of them is that MusicBrainz is incomplete, not that they are good (**both keepers in his 20 were real artists MB had simply failed to document**); and the DSP-link-plus-clip check is the best false-positive catcher available. **The decisive point is the one that closes it:** a measured false-positive rate on the candidate would change nothing, because no second refinement mechanism exists — so the follow-up question ("and then what?") has no answer, and dropping a large number of bad recommendations is a strong trade even carrying some false positives. **A future session must not propose a second hand sample on transferability grounds.** Distinct from the *magnitude* question — if a candidate tail were a far larger share of its population, that is a different-sized intervention, and `analysis/2026-08-02-candidate-tail-census/` measures it. |
| ⚠ **The Deezer id path inherits MusicBrainz's link accuracy — it is not "strictly better"** | **Before `BYP-13` is described as closed, and before any figure is put on the improvement.** MusicBrainz sometimes links an artist to a *duplicate* Deezer page rather than the real one. Two observed by hand: Radiohead's recorded link has 473 followers and **0 albums** (so it serves nothing and falls back to name search — fails safe), and Orbital's has **20 followers and does serve tracks** — where the id path would replace a correct name-search result with a worse one. Sampled over 60 delivered artists carrying an id: **59 of 60 serve a track from the id**, and 6 of those are thin pages, of which most are *genuinely* obscure artists rather than duplicates. So the new failure mode is real but small against the 9.4% / 6.1% it removes; **the net is clearly positive and the direction of every individual case is not guaranteed.** A session must not restate this as "strictly better by construction" — that claim was made on 2026-08-02 before this was measured, and is withdrawn. Cheap targeted mitigation if wanted: validate links for the top popularity decile only (~7,400 lookups), where a duplicate is both most detectable (expected follower count is high) and most damaging (those artists are delivered most often). |
| ✅ **The Deezer id map covers only the adopted population** | **DISCHARGED 2026-08-02 — the map now covers the UNION of both populations**, so the cap re-evaluation cannot trip a coverage condition mid-experiment. 93,067 artists (adopted 74,193 + `ALG-B` 68,467, overlapping), **39,465 ids**. The `ALG-B` graph used is the 2026-07-30 full build (sha `d008a2b5…`, manifest-verified), which predates the drop rule and the nameless fix and is therefore a **superset** of any final `ALG-B` build — safe by construction, since an MBID absent from a build is a no-op, and the same reasoning the candidate tail census used. Adopted-population coverage is unchanged at 34,988 / 47.2%, which is the consistency check that the union did not perturb it; `ALG-B`-only artists cover 4,477 of 18,874 (**23.7%**), consistent with that population being deader. An artist outside the union still falls back to name search. Struck, kept for the record. |
| **The Deezer id map is a dated snapshot and will age** | **Whenever it is next questioned; no automatic trigger exists.** Frozen 2026-08-02 because `build_from_archive` is offline by a hard rule and spec §9 requires byte-identical builds. A link that goes stale 404s, which `_get` treats as a miss rather than a refusal, so the card degrades to name search rather than going silent (pinned by `test_a_stale_id_falls_back_to_name_search_rather_than_giving_up`). Refreshing is a deliberate act with its own decision. |
| ✅ **The featured-credit residual class in the release filter** — artists kept because credits count as release groups, while having no primary-artist existence (two worked instances: 田島賢, TJ Brown; mechanism closed via `LBS-1`'s 0.25 featured weight) | **EXECUTED AND ADOPTION-RULED 2026-08-03 — the `FCF-` rule; see the top block.** The detector ran on the release-**group** dump (cheaper than the release dump the original row guessed at), the keep-check ran with zero refusals, `FCF-AM1` closed the shared-credit exemption gap the owner's spot checks found, and the lists ship as package data behind `drop_featured_credit`. The calibration hand-review was **declined at adoption**. Struck, kept for the record. |
| **Known-press telemetry as the novelty proxy's long-run validator** | **When enough `known` presses exist to read.** Named in the Definitions entry and `NOV-` §3; nothing to build now. |
| **A worldly-fame instrument does not exist** | **Accepted; claims in that currency are barred until one does** (Definitions ruling). Reopen only if a product need for worldly fame appears — the `RCS-` corpus and its committed hand values are the reusable starting point. |
| **The TJ Brown late hand read** (8,274 monthly listeners, ruler 218) | **Usable by a future corpus at design time only** — never a post-hoc addition to a read set (log §5a). |
| **`REQ-Q1`'s telemetry revisit condition FIRED and was not taken** | **The owner's call, separately from anything here** — whether live telemetry converges on the offline currency now that a per-mbid source exists. Flagged in the requirements text itself. |
| **Apple/iTunes ids are measured but not shipped** | **If the residual `BYP-13` rate after the Deezer path is judged too high.** Adding them takes delivered-artist coverage from **92.9% to 94.1%** of card impressions — 1.2 points — and the Apple-id-to-iTunes-lookup path has never been run here, unlike the Deezer one (`tail_clips.py:137`). Figures: `builder/analysis/2026-08-02-dsp-ids/dsp_ids.json`. |
| **A blind listen isolating the post-drop graph** (`REQ-38`) | **ANSWERED BY THE OWNER 2026-08-02: not now, and this is a deferral with a condition rather than an open question.** ⚠ **The previous wording — "whether the post-drop graph *owes* a blind listen" — misread `REQ-38`, and a session must not restore that framing.** Read from source, `REQ-38` says blind listening is the **primary evaluation method** and offline metrics must not override listener judgment: a rule about **how a judgment is made when one is being made**, not a debt every graph change incurs. No isolated adoption decision about the post-drop graph is pending, so nothing triggers it. **The owner's decisive argument, and it stands on its own:** every outcome leads to the same place — a pass adopts, and a failure still would not revert to delivering release-less artists, only change the exclusion mechanism. A test whose branches share a direction is not informing a decision. **Corroborating evidence he did not cite:** `TAS-` measured **zero** bottom-decile interior artists across 120 journeys, and the release-less tail sits overwhelmingly in that region — so the dropped artists were largely never delivered, and the drop's audible effect is second-order (shifted marginals, ~109 stranded of 74,193). **The one real cost, named rather than dismissed:** if the cap re-evaluation yields a rebuild, the drop is permanently confounded with the cap change and only the combined result is ever heard. That is why the option is preserved rather than closed. **Condition to spend it:** if the post-drop graph is ever proposed for adoption **as the only change** (the cap re-evaluation returns no rebuild), **or** if a combined rebuild sounds worse and the cause needs decomposing. **The instrument is already preserved** — `drop_no_release_tail` exists as an experimental control so a build can hold the drop constant in a factor table, so deferring costs no future capability. Distinct from the rule's own acceptance, which is closed. |
| **The label-affinity / clustering data asset** | **The owner's trigger.** `wgt_release_raw.json` side-collected record-label credits, countries and years per graph artist; nothing consumes it. His style-vocabulary read adds: for the curated Discogs styles, carrier count alone tracks usability — the clustering idea keeps its value for the open MB tag space, where frequency separates nothing. |
| **Tag clustering as a junk-label filter, owner-raised 2026-08-01** | **Unmeasured; the owner's trigger.** The current whitelist keeps a tag only if MusicBrainz classifies it as a genre — an ontology decision, which is why `british invasion` is discarded despite binding coherent artists. The owner's proposal: a real label's carriers cluster in the map, a junk label's scatter. Frequency alone cannot separate them, since `seen live` and a genuine niche genre are both rare. |
| **One new Snyk Low finding per module added under `builder/analysis/`** — *but only for modules taking a CLI path argument.* **The three added 2026-08-02 (`dsp_ids.py`, `delivered_coverage.py`, `id_quality.py`) contribute NONE**, the same reason `tail_exposure.py` did not: no CLI argument, so no input reaches a path. Full `builder/` scan at that closeout returns **32** — 27 Path Traversal Lows, 3 DOM-XSS in `listen.html`, 2 XML-parser Mediums (row above). *(2026-08-03 later: `wav_read.py` adds **2** of the same class — `--capture`/`--out` — recorded at its pre-registration commit; the eleven `cre_probe*.py` scripts add none, no CLI path arguments.)* | **Recorded, not fixed; extending the acceptance is the owner's.** A CLI `--out` path flows into `pathlib.Path` — the same class as the 13 already accepted here, **now 11 in the `TAS-` directory plus 6 in the `WGT-` directory** (`wgt_grid.py` ×2, `wgt_release_read.py` ×2, `wgt_style_filters.py` ×2). *(Corrected 2026-08-01 latest: this row said **4** and omitted `wgt_style_filters.py`'s two, which a re-scan surfaced. `tail_exposure.py` added the same day contributes **none** — it takes no CLI argument, so no input reaches a path.)* It cannot be meaningfully sanitised: captures deliberately live *outside* the repo, so confining the path breaks intended usage. |
| ✅ **Tag-aware selection increases the map's total edge count** | **DISCHARGED 2026-08-03 — the condition fired and was satisfied as this row's own text prescribes**: the `CRE-` pre-registration states the owner's sole-source constraint (LB similarity the only source of edge existence; tags only re-order, re-weight or remove), under which the union bounds the count above and the `TAS-4` growth mechanism cannot operate. Struck, kept for the record; the corrected `w_degree_hub` half below stays live reading. *(Original condition:)* **Before any rebuild pre-registration is written.** Opened by `TAS-4`: Jaccard is symmetric, so genre-sharing artists promote each other and creations exceed deletions at every λ. Mutual k-NN bounds each artist's own list, not the count of mutual pairs, so mean degree rises. Execution log §9.4/§9.5. **⚠ CORRECTED 2026-08-02 — this row previously said `w_degree_hub` "is dormant *because of the current graph's top-degree set*", which reads as the `w_floor` dormant-term confound about to repeat. It is not.** Checked from source: `w_degree_hub = 0.0` (`api/…/config.py:83` — cited as `:54` until 2026-09-05) and the term is a plain multiplication in the cost function (`pathfinding.py:160` — cited as `:135` until 2026-09-05), with no environment override anywhere — weights are not env-driven. **At a zero coefficient the graph's top-degree set cannot make the term fire, so it cannot switch itself on in the arms that succeed.** What *is* live is a decision, not a confound: the *reason* the weight is zero rests on a property of today's graph (§2.6 — the top-1%-by-degree set is largely insular micro-genre artists, so penalising them is not what you want), and a different connection rule changes that set. **So a rebuild pre-registration should decide `w_degree_hub` deliberately and record the decision — it does not need a control against the term waking up on its own.** |
| **The 11 blind verdicts as a falsifier for any future coherence instrument** | **If the owner reopens the instrument line** (route-population gate, `COH-3`). The corpus is unconsumed; any scoring against it must be pre-registered cold, and `ct_retrodict.py`'s committed-but-unrun rule counts as the first attempt for reporting purposes. `SYN-7` binds. |
| **42 ListenBrainz nulls and 24 MBIDs refused as ambiguous** | **Accepted, won't chase.** Both are recorded in the probe JSON. Reopen only if a criterion is built that depends on those specific artists being scored. |
| **The `× lower` path-read redraw** | **If the owner asks for obscure-endpoint path reads under candidate rules** — a new §8 amendment designed cold; the committed draw's famous classes stay the record. |
| ✅ **The `REL-` release-dump union pass** | **CLOSED 2026-07-31 — the path is known-unreachable, not deferred again.** Its §7 condition was "if and only if `REL-1` lands in 45.0–49.9%". `REL-1` cleared the bar outright, so the condition can never fire for this run. Reopening needs a new pre-registration designed cold. Struck, kept for the record. *(Correction 2026-08-01: this row and the frozen spec's §7 both said the 345 GB dump "was deleted after measurement" — **it was not**; it is on disk at `builder/scratch/mb-json-dumps/release/`, 322 GB, verified. The closure never depended on the deletion and stands. The `WGT-` pre-registration reads the dump for a different question — evidence strength, not coverage — designed cold as this row requires.)* |
| **Whether `REL-`'s frame is taken into `TAS-`** | **The owner's trigger, unchanged.** A `TAS-` §1 vocabulary change is an amendment to a frozen document and a rebuild spends his ear (`REQ-38`). **The cheap read this row asked for has now RUN** — execution log §15, figures `tas_frame_split.json`. It does not settle the trigger, but it changes which frame a decision would be about: the Discogs **style** column, not the coarse genre column, is what costs discrimination, and `W4` (`W1` + Discogs genre only) dominates the previously-evaluated `W6` on reach, spread and redundancy alike. **`W6` should not be the candidate any future amendment names.** `REL-3`'s fidelity median still governs, and nothing measured says `W4` is good enough to adopt. |
| **`REL-3`'s ratio bar is degenerate and must not be reused as written** | **Before any successor pre-registration expresses a bar as a multiple of a null.** The null median was exactly zero, so "≥ 3× the null" was satisfied by a division by zero. A ratio bar needs a stated floor on the denominator, or a difference bar instead. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase**; reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**; reopen if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **Three Snyk MEDIUMs, same rule** — `rel_discogs.py:87`, `ctc_census.py:173` **and `fcf_discogs_split.py:63`**, insecure XML parser (CWE-611) on `xml.etree.ElementTree.iterparse` over local dumps. *(This row named only the first until 2026-08-02, when a full `builder/` scan found the second; the third was found at the 2026-08-03 closeout scan and the analysis below applies identically to all three — fixing one alone would make the instances inconsistent for no exposure change.)* | **INVESTIGATED 2026-08-02, and it splits in two. Accepting the residual is the owner's, as with every row above.** Snyk reports one finding but its message names two hazards ("vulnerable to XXE and DDOS"), and they do not have the same answer here. **Tested empirically on this interpreter (3.12.13) rather than argued from the rule's title:** ① **XXE — NOT APPLICABLE.** An external entity pointing at a local file is *refused outright*: `ParseError: undefined entity`. Nothing leaks. **The cited CWE-611 is not reachable**, which also matches the rule's own scope (*"Python < 3.11"*) against this project's `>= 3.12`. ② **Entity expansion — REACHABLE.** An 11-level billion-laughs shape expanded to 8,192 characters, so the DoS half is real in principle. **Exposure for ② is the argument, and it is the same one the 13 Lows were accepted on:** the input is a 57 GB third-party dump sitting on local disk, read by a frozen offline probe; making it hostile requires local write access, which is a larger problem than a research script consuming memory, and no service parses it. **Deliberately NOT fixed:** the remedy is `defusedxml`, a new dependency, and editing a frozen probe would fire the "13 pre-existing findings" row's own reopen condition. The probe stays frozen. Probe script retained at `builder/analysis/2026-08-02-dsp-ids/` is unrelated; the XXE test itself was throwaway and its result is recorded here rather than kept as code. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Track B's harness complied throughout (`ReadOnlyArchive`). **Condition fired again 2026-07-30** — the `TAS-`/`TD-` capture reads the archive through the same Track B helper and therefore through `ReadOnlyArchive`; complied, verified at closeout. **Stays open**: it is a standing condition on future harnesses, not a one-off to discharge. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| ✅ **`TB-P5H-7`** | **DISCHARGED 2026-08-03 — the condition fired and was consumed.** The `CRE-` pre-registration is the successor router-pricing pre-registration, and it consumes the item as the source requires: the joint descent × delivered-payload outcome has its own pre-registered read (`CRE-C4`, read jointly with `CRE-C1` in every `CRE-R`; `CRE-R3` is the outcome class). Struck, kept for the record. |
| **The candidate-pool recompute** | **If the owner picks up the parked candidate decision.** |
| ✅ The `--prune` publish pass | **DONE 2026-08-02.** Ran `sync_frontend.py --prune --skip-build` through the module, so it kept the `FRO-1` pass ordering and the between-passes content-type probe. **Two orphans deleted** — `assets/index-C-9fM9tV.js` and `assets/index-C4yz7h5J.css`, the pre-redesign 2026-07-27 build. The bucket is now 7 objects. **The pre-flight that made it safe, and a successor should repeat it:** `--skip-build` publishes `frontend/dist` *as it stands*, so a stale or different `dist/` would have pruned the assets the live page names. Verified first that `dist/index.html` referenced exactly the two hashed assets the **live** page referenced, then ran `aws s3 sync … --delete --dryrun` to see the deletion list before running it for real. Verified after: bucket contents, `200` plus correct `Content-Type` for html/js/css/woff2/svg, and a live search returning Radiohead. Struck, kept for the record. |
| **The rate limit's headroom** | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:12` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |

