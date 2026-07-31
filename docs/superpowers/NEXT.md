# What is the next action?

**Role: AUTHORITATIVE for project status and sequencing.** This is the only document that
states what to do next. `CLAUDE.md` points here and does not restate it; so does
`memory/roadmap-pointer.md`. Where a handoff or an execution log disagrees with this
document about status, **the fresher of those two wins and this document is stale** — fix it
rather than working around it.

**Maintenance.** Rewritten wholesale at `closeout`, not appended to. It is short by design:
if it is growing, status is being narrated instead of pointed at. It **owns no figures** —
Track B's live in `findings/2026-07-30-track-b-cap-selection-results.md` (and its raw
`cb_scores.json`); the adopted graph's stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited, never restated.

**Last updated: 2026-07-31, at the `REL-` release-tag coverage probe's closeout. `TAS-` is unchanged and still owes Tasks 5–8.**

---

## Next

> ## The RELEASE-TAG COVERAGE PROBE (`REL-`) is COMPLETE. **`REL-1` PASSED — release aggregation clears `COH-2`'s 50% bar in the obscure tail. Nothing adopted. The next action is the OWNER'S.**
>
> Entry point is the current handoff:
> [`2026-07-31-HANDOFF-release-tag-coverage.md`](2026-07-31-HANDOFF-release-tag-coverage.md).
> Governing document:
> [`specs/2026-07-31-release-tag-coverage-preregistration.md`](specs/2026-07-31-release-tag-coverage-preregistration.md)
> (`REL-`) — **read its §8 first**; both amendments correct the same conflation and
> **`REL-AM2` was written after the headline figure was known and says so.** Figures:
> [`findings/2026-07-31-release-tag-coverage.md`](findings/2026-07-31-release-tag-coverage.md).
>
> **A parallel investigation commissioned by the owner, not a continuation of `TAS-`.** It
> asked whether aggregating an artist's *release* tags labels the artists carrying no genre
> label today. Census over all 74,193 artists from local dumps; no API, no sampling.
>
> **`REL-1` and what cuts against it must be quoted together** — the same pairing rule as
> `COH-2`/`COH-3` and `FPC-2`/`FPC-9`. The bar cleared and the coverage gain lands in the tail
> (`REL-6` not adverse); **but `REL-3`'s fidelity median is modest, its ratio bar is a
> degenerate pass, and a large minority of the unlabelled tail is reached by neither source.**
> Read the findings' §0 and `REL-3` together before acting.
>
> **`REL-4` inverted the design's framing:** Discogs — the arm expected to be awkward — is the
> stronger source in the obscure tail, and the two independent sources agree on at least one
> label for nearly every artist they both reach. That agreement is the strongest thing in the
> record.
>
> **Nothing adopted, no criterion fixed, no weight, default, currency or vocabulary changed,
> no rebuild, no blind listen spent. `TAS-` §1's vocabulary is UNTOUCHED** — a passing frame is
> a *candidate* for a `TAS-` §8 amendment, never an enactment. **It says nothing about whether
> `TAS-6` would flip**, which needs a rebuild this probe does not license.
>
> ---
>
> ## The TAG DISCRIMINATION PROBE (`TAS-`) is UNCHANGED and STILL LIVE — Tasks 1–4 of 8, plus Task 7's selection-side halves and `TAS-AM3`. **`TAS-6` is ADVERSE, which bars adopting the BUILD-TIME architecture. The instrument question is resolved and `TAS-4` is believable. Tasks 5–8 unrun; the next action is the OWNER'S — see below.**
>
> Its handoff remains authoritative for that track's internals:
> [`2026-07-30-HANDOFF-tag-discrimination.md`](2026-07-30-HANDOFF-tag-discrimination.md).
> Governing document is the pre-registration
> [`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md)
> (`TAS-`), which **wins wherever the plan disagrees**. **Read its §8 first:** `TAS-AM1`
> withdraws `TAS-4`'s original bar as **false** and `TAS-AM2` fixes the substrate per
> criterion.
>
> **The owner picked up the third coherence strand on 2026-07-30** — tag-aware neighbour
> selection, parked below until then. The probe tests the assumption both candidate
> architectures share: whether genre agreement discriminates between the candidates an
> artist already has, or merely restates the similarity score. **Nothing adopted, no
> criterion fixed, no weight, default or currency changed, no rebuild, and no blind listen
> spent.** Two owner decisions taken and recorded: the goal is **coherence, not obscurity**,
> and `TAS-4`'s materiality bar is **1% edge turnover**.
>
> **The architecture question — build-time selection vs router-side pricing — is
> deliberately still OPEN**, and the probe exists to inform it. `TAS-4` has now answered the
> build-time half and **did not kill it** — figures in
> `builder/analysis/2026-07-30-tag-discrimination/tas_select.json`, reasoning in §9 of the
> execution log. **`TAS-5` (the router half) is unrun, so the comparison the decision needs
> does not exist yet**, and per the pre-registration's §5 a `TAS-5` result read without
> `TAS-4` beside it — or vice versa — is uninterpretable.
>
> **⚠ TWO STOP-LEVEL RESULTS, both 2026-07-30, both recorded in execution log §10.**
>
> **1. `TAS-6` is ADVERSE** (*"does this make the app worse at reaching unknown artists"*).
> Famous→obscure connections fall at every λ and cross the 10% bar at the top two. Per the
> pre-registration's §5 this **bars any recommendation to adopt, whatever `TAS-4` and `TAS-5`
> show** — it is not outweighed by `TAS-4` having survived. Its denominator is thin; read
> `tas_guard.json` before judging materiality, and note that **no bar may be revisited now
> that a result exists**.
>
> **2. ✅ The red check is RESOLVED — `TAS-4`'s figures ARE believable.** The original check
> was **withdrawn as unachievable** by **`TAS-AM3`** (§8): a Jaccard-overlap device cannot
> produce large change on a randomised label frame, because randomising labels destroys
> overlap rather than randomising it. Its replacement, **`TAS-AM3a`**, passes at every λ —
> the ranking path is **bit-identical** to `td_turnover`'s verified one and reproduces the
> committed `TD-2` figures to five decimals. **Discharged for the SELECTION side only; the
> routing side still owes its own**, and `TAS-AM3` specifies it.
>
> **`TAS-AM3b`'s null control corrected the withdrawn check, against tags** — holding fixed
> which artists are labelled roughly doubles the null, so the withdrawn version had
> overstated how much of `TAS-4`'s turnover came from genre structure. Attribution is still
> not unsafe. **Read `TAS-AM3b`'s clause before quoting the ratio: below the threshold it is
> reported and nothing more, and no claim about tags is licensed by it.**
>
> **`TAS-AM3` is the first amendment appended AFTER results existed** — it says so at its
> head and names the hazard. Read that disclosure before relying on it.
>
> **Tasks 5–8 are still NOT started.** Execution log §11.
>
> The coherence tag probe, Track B and the fame-proxy probes are **COMPLETE and their
> records are untouched and remain accurate**; the coherence-tag-probe handoff is superseded
> **on next actions only**.
>
> **Coherence tag probe** (branch `coherence-tag-probe`) — a one-day falsification
> probe of the §7 coherence thread, owner-directed. **Its kill gate fired: tag/genre
> coverage thins in the obscure tail the way Wikipedia's does, and the pre-registered
> retrodiction against the 11 blind verdicts was never run — the verdicts remain an
> unconsumed falsifier.** Findings:
> [`findings/2026-07-30-coherence-tag-probe.md`](findings/2026-07-30-coherence-tag-probe.md)
> (`COH-`). **`COH-2` (the band-level kill) and `COH-3` (the delivered-route
> counterpoint) must be quoted together — either alone gives the wrong answer**, the
> same pairing rule as `FPC-2`/`FPC-9`. Nothing adopted, no criterion fixed, neither
> open decision below settled.
>
> **Track B** — results of record:
> [`findings/2026-07-30-track-b-cap-selection-results.md`](findings/2026-07-30-track-b-cap-selection-results.md).
> The two parked decisions below now have the pre-registered recommendation input it
> existed to produce; **both still owe a blind listen (`REQ-38`) regardless of the
> numbers.**
>
> **Fame-proxy coverage** (branch `fame-proxy-coverage`, PR #53) — descriptive scope
> probes, **nothing adopted, no criterion fixed, no currency changed, Track B untouched**.
> Findings: [`findings/2026-07-30-fame-proxy-coverage.md`](findings/2026-07-30-fame-proxy-coverage.md)
> (`FPC-`). **Read its §0 first: it corrects the premise the work began from** — the
> Wikipedia floor is *not* actively corrupting fame-currency measurements, and **no Track 2
> or Track 3 verdict changes.** What it did establish is a **sequencing** question, now
> parked below.
>
> **Nothing is queued for a working session.**

**The requirements baseline is unchanged since 2026-07-29:**
[`PRODUCT-REQUIREMENTS.md`](PRODUCT-REQUIREMENTS.md) (`REQ-`) governs where it and
[`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) disagree (its §10 lists the
disagreements). **`DD-F1` remains a defect, not an accepted limitation** — Track B's `R2`
read measured where it can and cannot be moved; the results note owns that reading.

## PARKED — owner's explicit decision; his trigger, never a session's

- **Whether the fame instrument is fixed BEFORE or AFTER the graph work** — the sequencing
  question `FPC-9` raised. The ruler is adequate for what the router does today (`FPC-2`)
  and blind on 38.7% of what it would deliver on the most obscure route the graph admits
  (`FPC-9`), so **the criteria that would judge a successful obscurity push are the ones
  that go blind during it.** The retiring session's position, argued in the handoff: do it
  first. **`FPC-2` and `FPC-9` must be quoted together; either alone gives the wrong
  answer.**
- **Whether a currency change re-reads prior fame-scored results** — must be fixed *before*
  any recompute, never after seeing one. `FPC-1`/`FPC-2` say nothing currently needs it.
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
  **⚠ The third strand is NO LONGER PARKED — the owner picked it up 2026-07-30 and it is
  the live work; see "Next" above.** Its caveats below were all carried into the
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
- **`ALG-B` adoption** — Track B's `R0`, `R2`, `R3` (`CRS-C6`) are its inputs, beside
  `RC-R1`'s stranding figures; adoption retires the existing path-quality figures and
  owes a blind listen (`REQ-38`).
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

**Still owed by the owner, unchanged:**

1. **The use-the-app test** — [`TEST-QUEUE.md`](TEST-QUEUE.md), the **QUEUED (latest)**
   entry (the redesign, against `https://musicapp.cmiller.io`), including the phone half.
2. **The iPhone script** — carried inside that entry; still the single most valuable unrun
   test on the project.
3. **The `--prune` publish pass** — ripe since 2026-07-29; see the deferral table.

`PW-9` (concurrency ladder) remains gated on the owner's approval and blocks nothing.

## Gate state

| Gate | State |
|---|---|
| **Gate 1 — personal use** | **DONE and discharged.** One live exception (`BYP-13`). |
| **Gate 2 — friends & family** | **DONE, and the password that defined it is now off.** |
| **Gate 3 — public** | **NOT OPEN.** The Gate 2→3 review's blocking set still gates it: [`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md). |

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
  - ⚠ **One exception, live:** `BYP-13` — a card playing a clip by a *different artist of
    the same name*. Not path work and not inside any pause.

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
  re-crawl decision. Likewise `max_neighbours_per_artist = 50` and
  `cap_strategy = "mutual_knn"` — **Track B was analysis-only and moved no default.**

## Deferred, with conditions

| Finding | Condition |
|---|---|
| ✅ **Track B runs and reads** (`CB-5`/`CB-6`) | **DISCHARGED 2026-07-30** — run to completion; results note is the record. Struck, kept for the record. |
| ✅ **`CRS-A5` endpoint re-verification** | **DISCHARGED 2026-07-30** — one request at scoring time, 200, companion delivered descriptive-only. Struck. |
| **`FPC-9`'s falsifier — an obscure-endpoint pair set for floor reach** | **If any realistic candidate device reaches materially more obscurity than production.** `FPC-9` used Track 3's `LIMIT` arm, a ceiling rather than a shippable route, and rests on 62 interiors from one arm on twelve pairs. Falsified by a device that reaches more obscurity *without* approaching `LIMIT`'s interior percentiles. |
| **`PRODUCT-REQUIREMENTS.md`'s Definitions section does not quantify the proxy's blindness** | **When, and only when, a currency decision is made.** Its current sentence ("blind in the modern-obscure tail") is *true*, so adding `FPC-3`/`FPC-9`'s extent is growth in the owner's own requirements layer, not a correction. Raised by the doc-auditor 2026-07-30 and deliberately not actioned. |
| **Full-graph MBID-keyed fame values** (`fp_fame_mbid --build`) | **If a currency decision adopts the MBID-keyed proxy.** ~33k pageview requests, ~3–4 h, resumable. The `--validate` path already answered the decision-relevant question; the build is only needed once something scores against it. |
| ✅ **MusicBrainz tag/genre coverage as a coherence instrument** | **DISCHARGED 2026-07-30** — the coherence tag probe ran exactly this check and its kill gate fired (`COH-2`, vocabulary-robust per `COH-6`); the retrodiction stayed unrun. Struck, kept for the record. |
| **Adding `analysis` to builder's `testpaths`** | **Deferred by the owner 2026-07-30.** Every analysis test passes, so it would work cleanly, but it changes what every builder `pytest` run collects. **Revisit if any `TAS-` test needs to gate a merge, or at the closeout that retires the `TAS-` probe.** Until then `TAS-` tests run only when invoked explicitly. *(This row carried a count of "34" until 2026-07-30; it was stale, and the count is not this document's to own — read it off `pytest analysis/ -q`.)* |
| **Replacing mutual k-NN with a tag-based degree limiter** | **Owner-raised 2026-07-30, ruled SEPARATE and explicitly NOT ruled out.** Needs its own pre-registration designed cold; mixing it with `TAS-` would make every attribution ambiguous. Track B's `R1a` corroborates the premise — reciprocity in isolation at k = 100 was null on both archives. **Condition: if the owner triggers it**, as with every other cap-adjacent decision. |
| ✅ **`TAS-4` is not believable until the red instrument check runs** | **DISCHARGED 2026-07-31 for the SELECTION side** — the original check was withdrawn as unachievable (`TAS-AM3`) and its replacement `TAS-AM3a` passed at every λ. Struck, kept for the record. |
| **`TAS-5` is not believable until the ROUTING-side red check runs** | **Before any `TAS-` finding is written.** `TAS-AM3` specifies it as `TAS-AM3a`/`b` with `find_path_coh` in place of the ranking path. Still owed; the routing harness does not exist yet. |
| **Tag-aware selection increases the map's total edge count** | **Before any rebuild pre-registration is written.** Opened by `TAS-4`: Jaccard is symmetric, so genre-sharing artists promote each other and creations exceed deletions at every λ. Mutual k-NN bounds each artist's own list, not the count of mutual pairs, so mean degree rises. `w_degree_hub` is dormant *because of the current graph's top-degree set*, and the pre-registration's held-constant row saying so is **scoped to this probe, which rebuilds nothing — it does not transfer to a rebuild.** Execution log §9.4/§9.5. |
| **The 11 blind verdicts as a falsifier for any future coherence instrument** | **If the owner reopens the instrument line** (route-population gate, `COH-3`). The corpus is unconsumed; any scoring against it must be pre-registered cold, and `ct_retrodict.py`'s committed-but-unrun rule counts as the first attempt for reporting purposes. `SYN-7` binds. |
| **42 ListenBrainz nulls and 24 MBIDs refused as ambiguous** | **Accepted, won't chase.** Both are recorded in the probe JSON. Reopen only if a criterion is built that depends on those specific artists being scored. |
| **The `× lower` path-read redraw** | **If the owner asks for obscure-endpoint path reads under candidate rules** — a new §8 amendment designed cold; the committed draw's famous classes stay the record. |
| ✅ **The `REL-` release-dump union pass** | **CLOSED 2026-07-31 — the path is known-unreachable, not deferred again.** Its §7 condition was "if and only if `REL-1` lands in 45.0–49.9%". `REL-1` cleared the bar outright, so the condition can never fire for this run, and the 345 GB dump was deleted after measurement. Reopening needs a new pre-registration designed cold. Struck, kept for the record. |
| **Whether `REL-`'s frame is taken into `TAS-`** | **The owner's trigger.** A `TAS-` §1 vocabulary change is an amendment to a frozen document and a rebuild spends his ear (`REQ-38`). The retiring session's position is in the `REL-` handoff and is *not yet*: `REL-3`'s fidelity median is what should govern, and a cheap read on whether coarse agreement suffices for what `TAS-` does — answerable against the committed `TAS-` harness with no rebuild — should come first. |
| **`REL-3`'s ratio bar is degenerate and must not be reused as written** | **Before any successor pre-registration expresses a bar as a multiple of a null.** The null median was exactly zero, so "≥ 3× the null" was satisfied by a division by zero. A ratio bar needs a stated floor on the denominator, or a difference bar instead. |
| **The `LBS` `filter` token's meaning** | **Accepted, won't chase**; reopen only if a permitted value differing in `filter` ever needs one-knob attribution. |
| **13 pre-existing Snyk findings under `builder/analysis/`** | **Accepted, won't fix**; reopen if a frozen probe is un-frozen and edited, or `listen.html` is ever served. |
| **The production archive is not closed under one-hop neighbours** (`GRT-A1`) | **Before any future harness points a crawler at `builder/scratch/graph-archive/`** — wrap it read-only. Track B's harness complied throughout (`ReadOnlyArchive`). **Condition fired again 2026-07-30** — the `TAS-`/`TD-` capture reads the archive through the same Track B helper and therefore through `ReadOnlyArchive`; complied, verified at closeout. **Stays open**: it is a standing condition on future harnesses, not a one-off to discharge. |
| **`ALG-B` edge quality / blind listen** | **If the owner picks up the re-crawl** (`REQ-38`). |
| **`TB-P5H-7`** | **If any successor bypass-device or router-pricing pre-registration is written.** |
| **The candidate-pool recompute** | **If the owner picks up the parked candidate decision.** |
| The `--prune` publish pass | **Ripe since 2026-07-29** — `sync_frontend.py --prune --skip-build` once nobody still holds the previous `index.html`. |
| **The rate limit's headroom** | **Before sharing beyond friends and family.** |
| **The front-door secret has no rotation procedure** | **If it is ever suspected leaked.** |
| **App Runner's CLI tags vanish if the service is replaced** | **After any deploy that recreates the service** — `infra/README.md` §7. |
| The near-geodesic ensemble re-read (PLA-R1's weakest link) | **Absorbed into DD-P1.** |
| Medium CSRF in `react-router@7.18.1` | Only if the app adopts React Router's unstable RSC APIs. |
| `env(safe-area-inset-bottom)` at `PlayerBar.tsx:10` is inert | Only if someone adds `viewport-fit=cover`. |
| Reading the request stream to bound chunked bodies | The Content-Length guard covers every reachable path. |
| **`G3-S4`'s disclosure half** — what the app records about visitors | **The owner's call.** |
