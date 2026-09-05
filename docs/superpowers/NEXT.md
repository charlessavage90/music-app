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
> ⚠ **The app is still NAMED "Artist Path" in the UI.** Only the address moved. A rename to
> "Unsung" is scoped but unapproved — do not assume it has happened.

**Last updated: 2026-09-05.** Two independent pieces of work have addresses. **`LUX-1`,
`LUX-2` and `LUX-3`** — branch `launch-ux-1-3`, **PR #101**; **PR #100 is superseded by it
rather than sitting beside it** (`launch-ux-1-3` was cut from `status-depth0-ruling`, so
#100's commits are already inside #101). And the **2026-09-05 doc-layer maintenance** —
branch `next-md-merge-status`, **PR #102**, which changed **no app code** and therefore
cannot affect a deploy or a test.

**THE REMAINING ACTIONS ARE THE OWNER'S, in this order — and per the rule above, this file
does not record how far down the list he has got.** `gh pr list` answers the merge questions;
`infra/README.md` and `/health` answer the deploy one.

1. **Merge PR #101**, and close #100. **Merge PR #102** whenever — it gates nothing and
   nothing gates it.
2. **Deploy.** ⚠ **Merged is not deployed here** — deploys are manual and there is no CI
   ([`infra/README.md`](../../infra/README.md)). Until this happens the live site serves what
   it served before the merge. The execution log's deploy note applies: the clip cache's item
   shape changed, so every live entry misses once and rebuilds.
   **⚠ It also clears a latent hazard, recorded 2026-09-05.** The running image is still
   `994c203`, built 2026-08-10 **before** the `CXR-` revert — so its baked-in
   `ApiConfig.graph_path` default still names **`graph-cxa-adopted.bin`, the REJECTED
   artifact**. Nothing is served wrong: production passes `ARTISTPATH_GRAPH` and
   `ARTISTPATH_GRAPH_SHA256` explicitly per deploy, and `DEP-34-FIX` makes a synth without
   `ARTISTPATH_DEPLOY_GRAPH_KEY` refuse. But it is a live instance of the `DEP-34` class — an
   image that reaches for the rejected map if it ever boots without the env var. HEAD's default
   is already back at `graph-msw-tu50.bin`, so **any image built from HEAD fixes this**; do not
   deploy this branch under a stale image tag.
3. **Run the queued use-the-app test** — **not exercisable until 2 has happened.** The test
   queue holds ONE live item, written 2026-09-04.

~~**Independent of all three and blocking nothing:** run `snyk auth`.~~ **DONE 2026-09-05, and
the scan it was owed for is discharged.** `api/` and `frontend/` both scanned clean of
shipped-code findings; the five reported are a self-labelled test fixture constant and four in
`frontend/design/**`, which is committed canvas exports referenced from nothing in `src/`,
`index.html` or `vite.config.ts` and so never enters the bundle. **`snyk` is now on `PATH`**
via `npm install -g snyk` — the MCP server's own bundled CLI is version-pathed and named
`snyk-win.exe`, so adding *that* to `PATH` would not have worked; both CLIs share
`~/.config/configstore/snyk.json`, so one auth covers both.

**Work a future session picks up, none of it blocking any of the above.** All three are
recorded where they will be found rather than only here: **(a)** make a graph's manifest
record *which* drop lists built it — the deferral table below carries the mechanism and the
condition, and the owner asked for it to be another session's work; **(b)** run `LUX-E1` with
`LUX-E1-AM1`'s second arm, which is the informative one; **(c)** `docs/README.md`'s row
discipline, also in the deferral table, deferred on his explicit decision. Entry point for all
three: the handoff [`2026-09-05-HANDOFF-doc-layer.md`](2026-09-05-HANDOFF-doc-layer.md).

**What shipped, and the one promise it rests on.** `LUX-1` removes the second bypass button
while **keeping the mechanism, the wire contract and the `?dislike=` URL parameter** — so
every link ever shared still resolves. `exclusions.ts` and `pathfinding.py` both have **zero
diff** across the whole branch and that is load-bearing. `LUX-2` adds the skipped-artists
panel and stops the router silently discarding an unrecognised MBID. `LUX-3` lets a listener
try another track by the same artist. Entry point: the handoff
[`2026-09-04-HANDOFF-lux-1-3.md`](2026-09-04-HANDOFF-lux-1-3.md); reasoning:
[`2026-09-04-lux-1-3-execution-log.md`](2026-09-04-lux-1-3-execution-log.md), which owns the
ten rulings, the deferrals and **an operational deploy note** (the clip cache's item shape
changed, so every live entry becomes a miss once — also in `infra/README.md`).

**`LUX-E4` RAN, ITS READ WAS UNDEFINED, AND IT IS NOW CLOSED — owner ruling 2026-09-05.** The
read stands as written: the denominator was empty, no lower-half artist reached a card, and
**no document may soften that into a pass.** What was retired is the **threshold**, which was
mis-specified — it named a re-prioritisation trigger for an outcome that costs nothing.
`LUX-3`'s control renders only when there is a second track to offer, so its absence draws
nothing at all and degrades exactly as a silent card already does. No result the eval could
return would change whether `LUX-3` ships. **It is not to be re-run, and this is not an open
owner decision.** Reasoning and the verified code gate are in §5 of the scope document.

**Two things survive that closure, and neither is `LUX-E4`.** First, **the committed `TAS-`
120-pair sample is damaged on the served map**, attrition falling almost entirely on the two
obscure classes — that now blocks **`LUX-E2`**, whose threshold *does* have teeth, and the
warning has been moved onto `LUX-E2` itself where a session running it will see it. Second,
the empty denominator is **`DD-F1`, already in the record and not a new finding**: `TAS-6`'s
routing half measured zero sub-decile interiors on this same sample on 2026-07-30, on the
adopted artifact. **Do not re-open it as a fresh path-quality question from here** — a
clip-availability eval on a damaged sample at depth zero is the wrong instrument for it, and
`DD-F1`'s currency split (binds in popularity, does not transfer to fame) is already settled.
Figures owned by `builder/analysis/2026-09-04-lux-e4-candidate-counts/README.md` and by
`findings/2026-07-30-tag-discrimination.md`, cited never restated.

**⚠ THE REVERT MOVED THE MAP BUT NOT THE DROP LIST — measured 2026-09-05.** `CXA-` Task 2
repointed the ALG-B unlistenable drop list default at a payload re-censused over the extended
population, and the `CXR-` revert did not repoint it back. **Nothing served is affected** — the
API never reads a drop list and the artifact is prebuilt — but **a rebuild from HEAD would drop
31 artists that are in the live map**. Figures owned by
[`builder/analysis/2026-09-05-lux-e1-drift-source/README.md`](../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md),
cited never restated. **Whether to repoint the default back or accept the 31 is his one-line
choice, and it is still open** — `LUX-E1` pinned the old list per invocation and moved no
default. *(`LUX-E1-AM1` added the isolating arm; `LUX-E1-AM2` then found the archive drift the
factor table had wrongly held constant. Both ran as B′ — see the discharge above.)*

**✅ `LUX-E1` RAN 2026-09-05 AND ITS GATE ON `LUX-4` IS DISCHARGED.** Arm B′ — the archive and
the drop list both pinned to what the live map was built with — rebuilt **byte-identically**.
So a rebuild *does* reproduce the live map, and **`LUX-4` is a metadata change as priced, not a
graph adoption.** Determinism holds. Figures owned by
[`builder/analysis/2026-09-05-lux-e1-armb/README.md`](../../builder/analysis/2026-09-05-lux-e1-armb/README.md),
cited never restated. `LUX-4` is still **unstarted**, and the `LUX-1..3` plan still deliberately
excludes it — do not start it from there — but it is no longer blocked.

**⚠ THREE `CXA-` LEFTOVERS, not one. The revert moved the map and moved none of them.** The
drop-list pointer was known; `LUX-E1` found the other two. **(a)** The ALG-B **archive tree**
gained 73,877 response files after the live map was built, so an unpinned rebuild reads the
extended crawl — the pre-expansion state survives as `grt-archive-algb.pre-cex-snapshot`.
**(b)** The **acceptance bounds** were recalibrated for the extended population, so
`artistpath-build build` now **REJECTS a correct rebuild of the served map** before serialising
it. **(b) blocks `LUX-4`**, which must rebuild to add its fields and lands on the same
population. Neither is a correctness problem with the graph. **Which fix is his** —
recalibrate the bounds to the served population, or wire the `--criteria` hook `cmd_build`
already reads but no argument supplies; **a session must not widen a bound to admit its own
build.**

**Everything else open is his to trigger and none of it blocks anything:** **Option C**
(same-name population probe), **`SEL-`**, **closing or keeping the 2026-07-29
famous-to-famous defect ruling**, the **three candidate path-quality fixes in the `CXR-`
README** (each needs its own pre-registration), and **renaming the app to "Unsung"** — scoped,
unapproved, and needing two decisions from him about the landing copy. The UI still says
"Artist Path".

**Do not re-litigate, and do not re-discharge:** the 2026-09-03 address test (**run and passed
2026-09-04**), either 2026-09-01 entry, or the depth-0 half of his revert report — **ruled
2026-09-04 (owner) NOT a defect and NOT open work**, on the grounds that a single offhand
report with no mechanism behind it is not a factual assessment. That closed it as an item and
**overturned no measurement**: `CXR-P3`'s null and the diagnosis README's "unexplained by
anything here" both remain exactly true and must not be edited. Reopening it is his trigger,
and the evidence would be more than one user reporting it after launch. Equally, do not
re-queue "tell me how it feels" — his long-run evaluation is continuous and `TEST-QUEUE.md`
explicitly does not hold it (owner ruling, 2026-08-07).

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
| ✅ **Track B runs and reads** (`CB-5`/`CB-6`) | **DISCHARGED 2026-07-30** — run to completion; results note is the record. Struck, kept for the record. |
| ✅ **`CRS-A5` endpoint re-verification** | **DISCHARGED 2026-07-30** — one request at scoring time, 200, companion delivered descriptive-only. Struck. |
| ⚠ **A graph's manifest cannot say WHICH drop lists built it** — it records the flags (`drop_unlistenable: true`) and the override pointer (`null` when the default is used), never the resolved file. `null` means *"whatever the default was that day"*, and the default is mutable: `CXA-` Task 2 moved the ALG-B unlistenable default and the `CXR-` revert did not move it back, which is how a rebuild came to silently differ from the live map by 31 artists. **All three drop families share the identical `dict[algorithm → Path]` pattern**, so `no_release` and `featured_credit` are the same trap unsprung. | **Before any rebuild is compared to another, and ideally before `LUX-E1` runs** — it makes that eval self-evidencing rather than requiring the hand analysis of 2026-09-05. **The fix:** record the resolved filename **and the sha256 of the file's bytes** for each family actually applied, and log both at build **start** so an unintended mismatch shows in the first seconds rather than after ~23 minutes. Hash the bytes rather than reuse the payloads' own hash keys — they are inconsistent (`sha256_over_sorted_mbids`, `sha256_over_sorted_drop_mbids`, and `featured_credit` carries none). **Purely additive and cannot block a build**; the sidecar is written after the artifact is serialised, so it cannot perturb a sha or confound `LUX-E1`. **Whether a build should also REFUSE on a mismatch is the owner's** — a hard gate can kill a long build at the end and needs an escape hatch; decide it after `LUX-E1`, when we know whether mismatches are rare or routine. Mechanism and figures: [`builder/analysis/2026-09-05-lux-e1-drift-source/`](../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md). |
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

