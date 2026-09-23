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

**Last updated: 2026-09-23, at the `LAL-` listen READ closeout.** **Nothing a listener sees has
changed**: the live site is as the 2026-09-08 deploy left it, `ApiConfig.graph_path` is untouched, and
`TEST-QUEUE.md`'s unticked boxes are still his to press, untouched here.

# THE BLIND LISTEN HAS RUN AND BEEN READ. THE NEXT ACTION IS `LBA-G5`, THE OWNER'S.

**The read is `LAL-R1`, PASS on coherence.** Its plain sentence, frozen in `LBA-AM6-7`: *"Journeys on
the new map are better on coherence, and no worse on the other."* It is run-once and final. The figures,
**the counter-evidence to read beside the verdict (§0)** and the barred reads (§5) are all in
[`findings/2026-09-23-lal-listen-results.md`](findings/2026-09-23-lal-listen-results.md). The current
handoff is [`2026-09-23-HANDOFF-lal-listen-read.md`](2026-09-23-HANDOFF-lal-listen-read.md).

> ## ⚠ Four things about this state that are easy to get backwards
>
> **PASS is not evidence of quality at `LBA-G5`, and `LBA-G5` does not re-read the listen**
> (`LBA-AM6-10`). "No worse" on novelty is a tie at the listen's resolution, not equivalence (`REQ-41`).
> No verdict carries across the three listens.
>
> **The blind is spent.** Journeys on the candidate may now be shown to him. `LBA-G5` is unblinded by
> design.
>
> **The acceptance recalibration still REJECTS the served map and the fallback.** If the candidate
> is not adopted, for any reason, restore `acceptance.py`'s `PREVIOUS (MSW- restore 2026-09-05)` line
> BEFORE rebuilding either map. See the deferral registry below.
>
> **A wrong-artist clip is NOT a `LBA-G5` signal.** It is a property of an id snapshot, not of the
> similarity graph (`LBA-AM4`).

Branch `lal-listen-run`, PR **#135**.

**THE REMAINING ACTIONS, in this order. This file does not record how far down the list anyone has
got.**

1. **The owner:** merge #135. Read the results note's §0 beside the verdict: how much weight it
   carries is his by `LBA-AM6-8`. Decide whether to keep the runner's worktree
   (`C:/Users/charl/worktrees/music-app-lal-runner`). It holds the only copy of the sealed per-journey
   metrics, which nothing further needs. The queued use-the-app tests and `LBD-AM3`'s `LBD-A4` question
   are unchanged and block nothing.
2. **`LBA-G5`**: the owner's two days of use against his own criterion, **logging every artist pair he
   uses** (`LBA-AM5`; the log file is named in `builder/analysis/2026-09-22-lba-a6-blind-listen/RUNNER-BRIEF.md`).
3. **Then adoption, which is the owner's call.**
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
as merge state. `TEST-QUEUE.md` owns it and `session-start` reads it. **Since 2026-09-12 a live
item is an unticked `- [ ]` box** — that file is a checklist now, and the "topmost heading" rule
this note used to give applies only to the two archives, where discharged prose entries keep their
old heading.)*

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
- **Both `LBL-` blind-listen verdicts are RUN-ONCE and FINAL** (`GBL-` §5). Listen 1 (served map
  against `LBD-A0V`, 2026-09-11) and listen 2 (`LBD-A0V` against `LBD-A5V`, 2026-09-13) each read
  **`LBL-R2`, the tie**. Neither may be re-listened on any protocol; **no verdict carries across
  them**; `REQ-41` bars reading either as equivalence; and **neither adopts anything** — `S4` owns
  adoption and `V` is an experimental control, never a population rule. Figures and barred reads:
  [`findings/2026-09-11-lbl-listen1-results.md`](findings/2026-09-11-lbl-listen1-results.md) and
  [`findings/2026-09-13-lbl-listen2-results.md`](findings/2026-09-13-lbl-listen2-results.md) §5.
  ⚠ **`LBD-X6` bars generalising listen 2's result to the cheaper pairing form — and it STILL
  DOES.** Its condition (*"until `LBD-A4` has run and `R10` has been read"*) was **discharged
  2026-09-13**, and `R10` **fired**, so the bar is **confirmed rather than lifted**. Reading the
  met condition as a lifted bar inverts the result.
- **Every `S4` arm records which pairing semantics it uses and why** (`LBD-D6`). This stopped
  being bookkeeping on **2026-09-13**: `LBD-A4` ran and **`R10` fired** on the edge-count half,
  so the pairing form is **load-bearing** and two arms differing in it are not comparable.
  `LBD-R4` is thereby retired as a risk and confirmed as a fact. Figures:
  [`../../builder/analysis/2026-09-13-lbd-a4/README.md`](../../builder/analysis/2026-09-13-lbd-a4/README.md) §§6–7.
  ⚠ **`R10` says the choice MATTERS; it says nothing about which form is BETTER.**
- **`LBD-G1` also fires on `LBD-A4` (2026-09-13), and `LBD-AM3`'s override does NOT name that
  arm** — it enumerates `LBD-A0`–`LBD-A3`. `R10` was read anyway because its bar is a
  *difference between arms*, so a lineage gap common to both cancels; the reasoning is the
  `LBD-A4` README's §5. **Whether the override extends to `LBD-A4` as an ABSOLUTE fidelity
  statement is the owner's and is open.** Do not widen it silently. **`LBD-C1` is not cited as
  passed for either arm.**
- **`LBD-C2a`, `LBD-C2b` and `LBD-M1` were deliberately NOT taken on `LBD-A4`.** Their reads
  (`LBD-G2`, `R4`–`R12`) were pre-registered for the four `T`-derived arms only; taking one now,
  with results in hand, needs an amendment first.
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
| **A clipless artist on one side only is a side tell** — in the `LAL-` listen one such card (Ed O'Brien, today's map) sat on exactly the three rows the owner identified ([results §0, §4.2](findings/2026-09-23-lal-listen-results.md)). The clip rule is artist-keyed, so this is not a map difference, but it marks a side. | **The next blind listen's pre-registration** either adds a per-row count of single-side clipless artists to its pre-screen, or states why not. |
| ⚠ **The 2026-09-21 acceptance recalibration REJECTS the served map and the `LBA-G5` fallback.** `PRODUCTION_ACCEPTANCE` is now centred on the `LBA-A6` candidate; `graph-msw-tu50.bin` and `LBD-A5V` both sit outside it, so **the builder cannot reproduce what the app serves today** — the `LUX-E1` drift shape, deliberately re-entered. Raised before the ruling; the owner ruled anyway, and it is his call. Bounds, basis and the sensitivity table are owned by `acceptance.py`'s own comment; the candidate's figures by `builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md` §6. Asserted by `tests/test_acceptance.py::test_the_served_map_and_the_fallback_are_outside_the_current_bounds`, so it presents as a recorded decision rather than a mystery rejection. | **If `LBA-G5`'s use gate FAILS, or the candidate is not adopted: restore `acceptance.py`'s `PREVIOUS (MSW- restore 2026-09-05)` line BEFORE rebuilding either map**, and delete that test. If the candidate IS adopted, the row closes — the calibration target and the served map become one artifact. |
| **Deezer ids are extracted without the `is_artist_url` check that Spotify and Apple get.** The 2026-09-21 re-extraction kept `dsp_ids.py`'s original numeric-tail rule deliberately, so the only thing changing was the population and a coverage difference could be attributed to it alone. `lux4_extract.py` added the artist-vs-album path check for the other two in 2026-09-05 and it was never back-ported, so a Deezer **album** URL ending in digits is currently kept and shipped as an artist id. | **Whenever the Deezer map is next re-extracted for any other reason.** The fix is one predicate, but it is a second column on any comparison it lands in, so it must not ride along with a population change. |
| **`LBA-G2`'s bar is written `24 GB` and implemented `24 GiB`** — five places in the pre-registration say 24 GB; `LBA_G2_BAR_BYTES = 24 * 1024**3` is 25.77 GB. Stage 1's instrument introduced it and stage 2's forward copy, README and handoff all adopted *"24 GiB"*, making the implementation self-consistent and diverging from the governing document silently. ⚠ **No cell's disposition changes under either reading, with comfortable margin on both sides** — recomputed in bytes at the stage-3 closeout; the arithmetic is in the stage-3 handoff. **Deliberately NOT fixed**: §11's rule is that a bar's value is never edited, and settling which unit governs after the results exist is changing a bar with results in hand. | **The owner's, and only if any future `LBD-` build gate is read.** Nothing is blocked by it and no committed result depends on which reading is taken. |
| ~~**`docs-lint` checks 4, 5 and 6 were never observed to run at the stage-2 closeout**~~ ✅ **DISCHARGED 2026-09-15, minutes after it was written, by the background run that had been launched before it.** The full script completed **exit code 0 with all six checks clean** — checks 4, 5 and 6 print their headers and list candidates beneath, and all three listed **none**. ⚠ **Check 6 is restated figures, and it found nothing**, which is the mechanical confirmation the row below asked for: the four restatements this closeout fixed by hand were the only ones. *(Struck, kept for the record. The row was written on two foreground runs that both timed out partway through check 3; the background run launched earlier had already succeeded and had not been read. The lesson is the row's own: **a timeout is not a result**, and the answer was already on disk.)*
| ~~**`closeout` B2, B3 and B4 were NOT run for `LBD-S4` stage 2**~~ ✅ **DISCHARGED 2026-09-16 at the stage-3 closeout, which is exactly the condition this row named.** **B2:** no orphans — `s3_common.py` and `s4_common.py` are each imported by every measurement script in their directory, `s4_instrument.py` by `s4_build.py`, and every other module is a CLI entry point that ran and left a committed output. **B3:** stage 2 and stage 3 added no tests, so there is nothing to spot-check — **saying so is the discharge**, as this row itself specified. **B4 is the one that paid**: it found that `LBA-G2`'s bar is written **24 GB** in the pre-registration and implemented **24 GiB** in the instrument (see the row below). Every other `LBA-` claim in the stage-2 and stage-3 docstrings checked out against the governing document. *(Struck, kept for the record.)*
| **`_logs/machine_state.tsv` was collected across the stage-2 build chain and NEVER ANALYSED** — 2,760 free-memory samples, taken so that *"was the machine quiet for this build"* would be answerable from the record rather than from anyone's memory. **Nobody has answered it.** The six build records carry the timestamps needed to align it. | **Before any future session compares a `LBA-G2` peak against these six**, or extends the fit with a new point. Until then the six peaks stand as measured and the residuals (README §2b) are the evidence that they are consistent. **Accepted-and-won't-chase is a legitimate discharge here**: the fit's residuals are all under 3 %, which already bounds what machine noise could have contributed. |
| **The `LBA-G1`(b) query-cost result has never been measured on the actual container** — it converts by the Gate 2→3 review's 2.5–3.5× multiplier, which was measured on the **retired 75k artifact**, not the one served today. `LBA-A8` sits at **93 % of the (b) bar** and its p95 is roughly triple the served map's. | **Before anyone concludes the larger maps are fast enough to ship** — that is the claim the conversion supports and the direction it could be wrong in. A direct reading replaces a multiplier taken on a different artifact. **Cheap, and it is a session's work, not an owner decision**, except for the deploy access it needs. Nothing in stage 3 blocks on it. |
| **The `U`-row acceptance floors are UNCALIBRATED and are labelled so** — node floor 50 % of the arm's table count, edge floor `CSR ≥ N`, both gross-loss tripwires. §2.4 records the prune's effect over `U` as unmeasured; stage 2 measured it on **two** cells (84.8 %, 85.5 %). ⚠ **On that row the edge floor cannot see a silent cap-rule revert**, which `acceptance.py`'s `CXA-` note calls the one thing it exists to catch. | **If a third `U` cell is ever built**, revisit whether two-plus-one cells calibrate a floor. **Not before** — two cells is not a calibration, and an 80 % floor would have passed on both only by hindsight. The lost sensitivity is **accepted for experimental control maps** and must be re-decided if any `U` arm is ever a shipping candidate. |
| **The plan for `DLS-` items 4–6** (restructure `CLAUDE.md`; rebuild the map around role lines and add the lint checks; slim the rituals). The owner answered `DLS-Q1`–`Q6` on 2026-09-11 ([findings §5a](findings/2026-09-10-documentation-layer-strategy.md)). **It also carries three items:** `CLAUDE.md` prose the harness now enforces or makes redundant (the `UV_LINK_MODE=copy` prefix; "never use `docs/reference/`"); `closeout` D6 counting `.claude/rules/*.md` files that have no `paths:`, which load in every session; and item 3's unbuilt remainder, a hook refusing commits on `main`, which the owner has not been asked about. | **After the `DLS-T1` read and ~~the live `LBD-` session's next closeout~~ — that half SATISFIED 2026-09-13**, at the `LBL-` listen-2 read closeout; the `DLS-T1` read is still owed.** Written by a fresh session from the findings document, with a handoff point between each item. The D6 fix is due earlier if any rule without `paths:` is added. |
| **Two documents are over the line budgets set for them 2026-09-12** (`closeout` `B6-budget`): this file and `docs/README.md`. Both are the files concurrent sessions collide on, and demoting their accreted history is a wholesale table rewrite, which reconciles badly in either merge order. | **When no second session is live in the tree.** This file: demote the discharged deferral rows to `NEXT-ARCHIVE.md` per `A2-next`. `docs/README.md`: it is `DLS-` item 5, whose gates are all clear. **Deliberately not done 2026-09-12 because the `LBL-` session was live** — not forgotten, and not a judgement that the budgets are wrong. |
| **The APG1 lockstep tests (PR #118) pin only the fixture's four base metadata keys.** The committed fixture has no `deezer_ids`, `fame_lb`, `spotify_ids`, `apple_ids` or `artist_facts`, so those stay covered only by each package's own hand-built tests. | **The next time the committed fixtures are regenerated (`closeout` D2):** regenerate with those keys populated and re-derive the api test's pinned values. |
| **The `DLS-T1` read** (*when a session opens a plan or a spec, does a rule scoped to those folders arrive in its context without anyone asking for it?*). The instrument is armed by the `doc-strategy` PR: **do not remove `.claude/rules/plans.md` or the `InstructionsLoaded` logging hook before this is read.** | **Three qualifying sessions after merge, or 2026-09-24**, whichever comes first — read per [`findings/2026-09-10-documentation-layer-strategy.md`](findings/2026-09-10-documentation-layer-strategy.md) §6. **One dated observation is already banked and the read must consume it:** the `LBL-` write-up session opened a spec repeatedly and the rule did **not** load (its own `instructions-loaded.jsonl` shows only the two session-start `CLAUDE.md` entries) — **but it read through Bash, not the `Read` tool**, so the observation cannot separate "the rule never fires" from "it fires only on a `Read`-tool open". **What the read still needs is a qualifying session that opens a spec with the `Read` tool.** Written up in [`2026-09-11-lbl-listen1-read-execution-log.md`](2026-09-11-lbl-listen1-read-execution-log.md) §5. **2026-09-12 — that arrived and the ambiguity is resolved: the rule fires.** Standing at **1 qualifying session of 3**. ⚠ **The observations, the exclusions and three confounds now live in [findings §6b](findings/2026-09-10-documentation-layer-strategy.md#6b-instrument-log-after-merge--observations-exclusions-and-confounds), which the read must consume** — Bash-read sessions are not qualifying and must not be scored as misses, worktree sessions cannot contribute at all, and three synthetic log rows must be excluded. **The log is gitignored, so §6b is the durable copy. Record new observations there, not here.** |
| ~~**`LBD-A4` (the pairing arm)**~~ — **DISCHARGED 2026-09-13: it RAN, and `R10` WAS READ.** `R10` **fires** on the edge-count half; figures owned by [`../../builder/analysis/2026-09-13-lbd-a4/README.md`](../../builder/analysis/2026-09-13-lbd-a4/README.md) §§5–7. *(Struck, kept for the record. Everything after this dash is the row as it stood, and its "Still unrun" was true when written.)* **`LBD-A4` (the pairing arm)** — still unrun; `LBD-AM4-2` said so and no read here depended on it. **Listen 2 ran and was read on 2026-09-13 under the waiver, exactly as the ruling allows** — and its result therefore carries `LBD-X6`: it holds for ListenBrainz's own pairing semantics and may not be generalised to the cheaper form until this arm has run and `R10` has been read. | **Before any `S4` arm is pre-registered** — ~~before any further `LBD-` arm~~, **narrowed 2026-09-12 by the owner's `LBD-D6` ruling**, quoted verbatim in `LBD-AM6-7`: `LBD-A4` is **waived for listen 2 and enforced before `S4`**, because both listen-2 maps were derived with ListenBrainz's own pairing semantics — the faithful form `LBD-A4` measures the cheaper form against — so no `LBD-A4` result can change either map or listen 2's read. `LBD-A4` must run and **`R10` must be read** before any `S4` arm is pre-registered, and **every `S4` arm records which pairing semantics it uses and why**, per `LBD-D6`. **Still unrun; `LBD-D6` itself is now RULED.** One bar travels with it meanwhile — `LBD-X6`: listen 2's result may not be generalised to the cheaper pairing form until `LBD-A4` has run and `R10` has been read. | | ⚠ **The condition is discharged; the BAR IS NOT.** `LBD-X6` **stands** — `R10` fired, so listen 2's result holds for ListenBrainz's own pairing semantics and may not be generalised to the cheaper form. What is now live instead is `LBD-D6`'s standing requirement, promoted to the *Must not be changed* registry: **every `S4` arm records which pairing semantics it uses and why.** |
| **`LUX-E2`** — blocked on the damaged `TAS-` sample; per-field population coverage is **not** a substitute read. | **A repaired sample.** Nothing in flight repairs it. |
| **`ULC-F4`** — the un-listenable keep-check measures the name-search route while the app resolves by identity first, so both drop lists drop artists the app can play. | **The owner's**: a re-census, a rebuild and its own pre-registration. Nothing blocks on it. |
| ⚠ **CONNECTIVITY BLOCKER CLEARED 2026-09-21** — the MCP server connected and scanned this session's three new modules (0 issues), so the credential/connection failures of 2026-09-08 and 2026-09-10 no longer bar the sweep. The frozen back-catalogue is still unscanned.  **Snyk has not scanned the FROZEN modules under `builder/analysis/`** — credentials expired 2026-09-07, the MCP server failed to connect 2026-09-08 and 2026-09-10 (morning); **it connected 2026-09-10 (evening) and the build-stage scripts added that day were scanned and are clean** (one Medium fixed by binding paths as DuckDB parameters); the pre-existing frozen modules remain unscanned; the owner accepted and deferred scanning for everything there on the grounds that none of it is live. His hands, not a decision: it opens a browser. | **Promotion of anything under `builder/analysis/` into shipped code** — which nothing proposes. |
| ⚠ **ARMED since 2026-09-08 — `LUX-4` merged and no rebuild has happened; the next rebuild of the served lineage must carry the re-extract.** **A slice of served artists carry NO recorded Deezer id**, so the api cannot take its identity-first clip path for them and falls back to **name search** — the `BYP-13` exposure the id path exists to close. Cause: the shipped id map was extracted over a population that predates the served map, which was built later from a further ALG-B crawl. Counts, the expected recovery, and why it is not fixed inside `LUX-4`: [`builder/analysis/2026-09-05-lux4-extract/README.md`](../../builder/analysis/2026-09-05-lux4-extract/README.md) §4. | **The first rebuild after `LUX-4` merges.** Until then, refreshing that key would change the artifact's existing `deezer_ids` and break `L4-T7`'s control arm, whose whole job is to prove `LUX-4` touches nothing that already existed. **A SESSION'S WORK, NOT AN OWNER DECISION** — the fix is obvious, the sequencing is methodology, and only the deploy needs his hands. The work: re-extract with `deezer` added to `KEPT_PLATFORMS` over the three-artifact population, ship it as dated package data, rebuild, take the new checksum to a deploy. **Metadata-only: no listening test and no acceptance risk**, because it changes no node, edge or score. |
| ~~⚠ **A graph's manifest cannot say WHICH drop lists built it**~~ ✅ **DISCHARGED 2026-09-06 by `L4-T1b`** — `resolve_build_inputs` records the resolved filename and a sha256 over each applied drop list's bytes, plus the archive directory, and `log_build_inputs` prints them at build **start**. First exercised on the `LUX-4` build, whose manifest is the first here that can say which files produced it. **Recording only; a mismatch is NOT a refusal — the owner's decision, 2026-09-06.** Noted at both code sites that a gate here *could* fire in the first seconds, since both inputs are known before any work, so the "kills a long build at the end" worry applies to the acceptance bounds and not to this check; the reason to wait is that a reflexively-reached escape hatch removes the protection it guards. **A session must not add the gate on its own.** *Struck, not deleted: the condition fired twice — unhonoured on 2026-09-05, honoured here — and that history is the evidence the tracking worked.* Original text follows. |
| ⚠ **A graph's manifest cannot say WHICH drop lists built it** — it records the flags (`drop_unlistenable: true`) and the override pointer (`null` when the default is used), never the resolved file. `null` means *"whatever the default was that day"*, and the default is mutable: `CXA-` Task 2 moved the ALG-B unlistenable default and the `CXR-` revert did not move it back, which is how a rebuild came to silently differ from the live map by 31 artists. **All three drop families share the identical `dict[algorithm → Path]` pattern**, so `no_release` and `featured_credit` are the same trap unsprung. | **Before any rebuild is compared to another, and ideally before `LUX-E1` runs** — it makes that eval self-evidencing rather than requiring the hand analysis of 2026-09-05. **The fix:** record the resolved filename **and the sha256 of the file's bytes** for each family actually applied, and log both at build **start** so an unintended mismatch shows in the first seconds rather than at the end. ⚠ **CONDITION FIRED 2026-09-05 AND WAS NOT HONOURED — recorded rather than quietly re-deferred.** The condition read *"before any rebuild is compared to another, and ideally before `LUX-E1` runs"*; `LUX-E1` then ran and two rebuilds **were** compared, without this. The consequence is exactly what the deferral predicted: the comparison needed a **hand analysis** to establish which drop list and which archive each build used, because no manifest could say. **Re-deferred deliberately, with a tightened condition: before the `LUX-4` rebuild (`L4-T7`), which is the next rebuild comparison and is already planned.** *(The stale "~23 minutes" was struck here too — the live manifest records ~40 s for a whole build.)* Hash the bytes rather than reuse the payloads' own hash keys — they are inconsistent (`sha256_over_sorted_mbids`, `sha256_over_sorted_drop_mbids`, and `featured_credit` carries none). **Purely additive and cannot block a build**; the sidecar is written after the artifact is serialised, so it cannot perturb a sha or confound `LUX-E1`. **Whether a build should also REFUSE on a mismatch is the owner's** — a hard gate can kill a long build at the end and needs an escape hatch; decide it after `LUX-E1`, when we know whether mismatches are rare or routine. Mechanism and figures: [`builder/analysis/2026-09-05-lux-e1-drift-source/`](../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md). |
| **`docs/README.md` restates its documents rather than routing to them** — 336 KB, the largest document in the project, 95% table rows, **275 rows at a median 1,180 characters**, and the file `CLAUDE.md` tells every session to read first. A probe of its longest rows against the documents they describe found **15/19, 25/25 and 17/17** of a row's identifiers also present in the document. That is the one-document rule violated in prose, and it drifts the same way — the 2026-09-04 audit found a HIGH where the document had been updated and its row had not. | **The owner's trigger; he deferred it deliberately on 2026-09-05.** ⚠ **The fix is NOT to strip the map** — the summaries earn their place by letting a reader decide whether to open a 105 KB execution log, and compressing live prose to make a number go down is the damage this project has already paid for twice. What is missing is a **rule for what belongs in a row**: role, supersession, what it owns, and the one thing a reader must not get wrong. Applying it going forward costs nothing; retrofitting the **22 rows over 2,000 characters** is about an hour and captures most of the win. Rewriting all 275 is not worth it. Measurements owned by the 2026-09-05 handoff. |
| **`FPC-9`'s falsifier — an obscure-endpoint pair set for floor reach** | **If any realistic candidate device reaches materially more obscurity than production.** `FPC-9` used Track 3's `LIMIT` arm, a ceiling rather than a shippable route, and rests on 62 interiors from one arm on twelve pairs. Falsified by a device that reaches more obscurity *without* approaching `LIMIT`'s interior percentiles. |
| **`TAS-6`'s routing half is unmeasurable on the committed draw** | **If, and only if, an obscure-endpoint draw is ever made for routing.** Its baseline is zero sub-decile interior artists, so no reduction can be measured and "not adverse" is a division-by-zero artifact. Not a defect of the run — a property of what production routing delivers, and a corroboration of `DD-F1`. |
| **`W4` was never evaluated as a `TAS-` candidate frame** | **If the owner triggers a vocabulary change.** Now further supported: the `WGT-` grid evaluated `W4` under two weighting schemes and it remains the dominant frame; the style column is closed with a mechanism (`WGT-` findings §3a). A `W4` adoption would still be a new §8 amendment designed cold. |
| **Discogs alias expansion** | **If a frame amendment is ever triggered.** Discogs attribution goes through one MB-sourced ID; alias releases are invisible, so every Discogs figure is a lower bound (identical in every cell — no comparison threatened). `discogs_20260701_artists.xml` is already on disk; expansion is an exact ID join, no download, no name matching. |
| **The Discogs `masters` export** | **Iff Discogs support-counting is ever wanted.** Irrelevant to every presence-based use (unions are reissue-proof by construction) and would *lose* tail coverage (single-version releases often have no master); but it is the album-grain collapse that avoids the pressing confound (`WGT-4c`) if Discogs evidence counts are ever proposed. **Owner spot check 2026-08-01 (DSotM, 1000+ releases):** individual pressings accrete stray labels beyond the master's (`art rock`, `classic rock`, `pop rock` beside the master's two) — so the release-built frames carry mild curatorial noise a master build would not, the flip side of the coverage loss. Recorded; changes no measured verdict. |
| ⚠ **The Deezer id path inherits MusicBrainz's link accuracy — it is not "strictly better"** | **Before `BYP-13` is described as closed, and before any figure is put on the improvement.** MusicBrainz sometimes links an artist to a *duplicate* Deezer page rather than the real one. Two observed by hand: Radiohead's recorded link has 473 followers and **0 albums** (so it serves nothing and falls back to name search — fails safe), and Orbital's has **20 followers and does serve tracks** — where the id path would replace a correct name-search result with a worse one. Sampled over 60 delivered artists carrying an id: **59 of 60 serve a track from the id**, and 6 of those are thin pages, of which most are *genuinely* obscure artists rather than duplicates. So the new failure mode is real but small against the 9.4% / 6.1% it removes; **the net is clearly positive and the direction of every individual case is not guaranteed.** A session must not restate this as "strictly better by construction" — that claim was made on 2026-08-02 before this was measured, and is withdrawn. Cheap targeted mitigation if wanted: validate links for the top popularity decile only (~7,400 lookups), where a duplicate is both most detectable (expected follower count is high) and most damaging (those artists are delivered most often). |
| ~~**The Deezer id map is a dated snapshot and will age**~~ ✅ **DISCHARGED 2026-09-21 by the owner's re-extraction ruling.** Its condition was *"whenever it is next questioned"* and it was questioned: measured at 11.41 % coverage over the artists the `LBA-A6` candidate adds, re-extracted over that population, and shipped as new dated package data. The 2026-08-02 file remains on disk, never edited. *(Struck, kept for the record.)* ⚠ **The row does not reopen for the SERVED lineage** — that re-extract is a separate condition and is still armed. | ~~Whenever it is next questioned; no automatic trigger exists.~~ **Discharged for the candidate population. The served lineage remains armed.** |
| **Known-press telemetry as the novelty proxy's long-run validator** | **When enough `known` presses exist to read.** Named in the Definitions entry and `NOV-` §3; nothing to build now. |
| **A worldly-fame instrument does not exist** | **Accepted; claims in that currency are barred until one does** (Definitions ruling). Reopen only if a product need for worldly fame appears — the `RCS-` corpus and its committed hand values are the reusable starting point. |
| **The TJ Brown late hand read** (8,274 monthly listeners, ruler 218) | **Usable by a future corpus at design time only** — never a post-hoc addition to a read set (log §5a). |
| **`REQ-Q1`'s telemetry revisit condition FIRED and was not taken** | **The owner's call, separately from anything here** — whether live telemetry converges on the offline currency now that a per-mbid source exists. Flagged in the requirements text itself. |
| **Apple/iTunes ids are measured but not shipped** | **If the residual `BYP-13` rate after the Deezer path is judged too high.** Adding them takes delivered-artist coverage from **92.9% to 94.1%** of card impressions — 1.2 points — and the Apple-id-to-iTunes-lookup path has never been run here, unlike the Deezer one (`tail_clips.py:137`). Figures: `builder/analysis/2026-08-02-dsp-ids/dsp_ids.json`. |
| **A blind listen isolating the post-drop graph** (`REQ-38`) | **ANSWERED BY THE OWNER 2026-08-02: not now, and this is a deferral with a condition rather than an open question.** ⚠ **The previous wording — "whether the post-drop graph *owes* a blind listen" — misread `REQ-38`, and a session must not restore that framing.** Read from source, `REQ-38` says blind listening is the **primary evaluation method** and offline metrics must not override listener judgment: a rule about **how a judgment is made when one is being made**, not a debt every graph change incurs. No isolated adoption decision about the post-drop graph is pending, so nothing triggers it. **The owner's decisive argument, and it stands on its own:** every outcome leads to the same place — a pass adopts, and a failure still would not revert to delivering release-less artists, only change the exclusion mechanism. A test whose branches share a direction is not informing a decision. **Corroborating evidence he did not cite:** `TAS-` measured **zero** bottom-decile interior artists across 120 journeys, and the release-less tail sits overwhelmingly in that region — so the dropped artists were largely never delivered, and the drop's audible effect is second-order (shifted marginals, ~109 stranded of 74,193). **The one real cost, named rather than dismissed:** if the cap re-evaluation yields a rebuild, the drop is permanently confounded with the cap change and only the combined result is ever heard. That is why the option is preserved rather than closed. **Condition to spend it:** if the post-drop graph is ever proposed for adoption **as the only change** (the cap re-evaluation returns no rebuild), **or** if a combined rebuild sounds worse and the cause needs decomposing. **The instrument is already preserved** — `drop_no_release_tail` exists as an experimental control so a build can hold the drop constant in a factor table, so deferring costs no future capability. Distinct from the rule's own acceptance, which is closed. |
| **The label-affinity / clustering data asset** | **The owner's trigger.** `wgt_release_raw.json` side-collected record-label credits, countries and years per graph artist; nothing consumes it. His style-vocabulary read adds: for the curated Discogs styles, carrier count alone tracks usability — the clustering idea keeps its value for the open MB tag space, where frequency separates nothing. |
| **Tag clustering as a junk-label filter, owner-raised 2026-08-01** | **Unmeasured; the owner's trigger.** The current whitelist keeps a tag only if MusicBrainz classifies it as a genre — an ontology decision, which is why `british invasion` is discarded despite binding coherent artists. The owner's proposal: a real label's carriers cluster in the map, a junk label's scatter. Frequency alone cannot separate them, since `seen live` and a genuine niche genre are both rare. |
| **One new Snyk Low finding per module added under `builder/analysis/`** — *but only for modules taking a CLI path argument.* **The three added 2026-08-02 (`dsp_ids.py`, `delivered_coverage.py`, `id_quality.py`) contribute NONE**, the same reason `tail_exposure.py` did not: no CLI argument, so no input reaches a path. Full `builder/` scan at that closeout returns **32** — 27 Path Traversal Lows, 3 DOM-XSS in `listen.html`, 2 XML-parser Mediums (row above). *(2026-08-03 later: `wav_read.py` adds **2** of the same class — `--capture`/`--out` — recorded at its pre-registration commit; the eleven `cre_probe*.py` scripts add none, no CLI path arguments.)* | **Recorded, not fixed; extending the acceptance is the owner's.** A CLI `--out` path flows into `pathlib.Path` — the same class as the 13 already accepted here, **now 11 in the `TAS-` directory plus 6 in the `WGT-` directory** (`wgt_grid.py` ×2, `wgt_release_read.py` ×2, `wgt_style_filters.py` ×2). *(Corrected 2026-08-01 latest: this row said **4** and omitted `wgt_style_filters.py`'s two, which a re-scan surfaced. `tail_exposure.py` added the same day contributes **none** — it takes no CLI argument, so no input reaches a path.)* It cannot be meaningfully sanitised: captures deliberately live *outside* the repo, so confining the path breaks intended usage. |
| **The 11 blind verdicts as a falsifier for any future coherence instrument** | **If the owner reopens the instrument line** (route-population gate, `COH-3`). The corpus is unconsumed; any scoring against it must be pre-registered cold, and `ct_retrodict.py`'s committed-but-unrun rule counts as the first attempt for reporting purposes. `SYN-7` binds. |
| **42 ListenBrainz nulls and 24 MBIDs refused as ambiguous** | **Accepted, won't chase.** Both are recorded in the probe JSON. Reopen only if a criterion is built that depends on those specific artists being scored. |
| **The `× lower` path-read redraw** | **If the owner asks for obscure-endpoint path reads under candidate rules** — a new §8 amendment designed cold; the committed draw's famous classes stay the record. |
| **Whether `REL-`'s frame is taken into `TAS-`** | **The owner's trigger, unchanged.** A `TAS-` §1 vocabulary change is an amendment to a frozen document and a rebuild spends his ear (`REQ-38`). **The cheap read this row asked for has now RUN** — execution log §15, figures `tas_frame_split.json`. It does not settle the trigger, but it changes which frame a decision would be about: the Discogs **style** column, not the coarse genre column, is what costs discrimination, and `W4` (`W1` + Discogs genre only) dominates the previously-evaluated `W6` on reach, spread and redundancy alike. **`W6` should not be the candidate any future amendment names.** `REL-3`'s fidelity median still governs, and nothing measured says `W4` is good enough to adopt. |
| **`REL-3`'s ratio bar is degenerate and must not be reused as written** | **Before any successor pre-registration expresses a bar as a multiple of a null.** The null median was exactly zero, so "≥ 3× the null" was satisfied by a division by zero. A ratio bar needs a stated floor on the denominator, or a difference bar instead. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase**; reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**; reopen if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **Three Snyk MEDIUMs, same rule** — `rel_discogs.py:87`, `ctc_census.py:173` **and `fcf_discogs_split.py:63`**, insecure XML parser (CWE-611) on `xml.etree.ElementTree.iterparse` over local dumps. *(This row named only the first until 2026-08-02, when a full `builder/` scan found the second; the third was found at the 2026-08-03 closeout scan and the analysis below applies identically to all three — fixing one alone would make the instances inconsistent for no exposure change.)* | **INVESTIGATED 2026-08-02, and it splits in two. Accepting the residual is the owner's, as with every row above.** Snyk reports one finding but its message names two hazards ("vulnerable to XXE and DDOS"), and they do not have the same answer here. **Tested empirically on this interpreter (3.12.13) rather than argued from the rule's title:** ① **XXE — NOT APPLICABLE.** An external entity pointing at a local file is *refused outright*: `ParseError: undefined entity`. Nothing leaks. **The cited CWE-611 is not reachable**, which also matches the rule's own scope (*"Python < 3.11"*) against this project's `>= 3.12`. ② **Entity expansion — REACHABLE.** An 11-level billion-laughs shape expanded to 8,192 characters, so the DoS half is real in principle. **Exposure for ② is the argument, and it is the same one the 13 Lows were accepted on:** the input is a 57 GB third-party dump sitting on local disk, read by a frozen offline probe; making it hostile requires local write access, which is a larger problem than a research script consuming memory, and no service parses it. **Deliberately NOT fixed:** the remedy is `defusedxml`, a new dependency, and editing a frozen probe would fire the "13 pre-existing findings" row's own reopen condition. The probe stays frozen. Probe script retained at `builder/analysis/2026-08-02-dsp-ids/` is unrelated; the XXE test itself was throwaway and its result is recorded here rather than kept as code. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Track B's harness complied throughout (`ReadOnlyArchive`). **Condition fired again 2026-07-30** — the `TAS-`/`TD-` capture reads the archive through the same Track B helper and therefore through `ReadOnlyArchive`; complied, verified at closeout. **Stays open**: it is a standing condition on future harnesses, not a one-off to discharge. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| **The candidate-pool recompute** | **If the owner picks up the parked candidate decision.** |
| **The rate limit's headroom** | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:12` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |

