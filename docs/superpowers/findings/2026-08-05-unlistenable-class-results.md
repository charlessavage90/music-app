# The un-listenable class (`ULC-`) — results

**Role: RESULTS OF RECORD for `ULC-`. It owns the `ULC-` figures** — cite it by section and never
restate a number from it elsewhere. Governing document:
[`specs/2026-08-05-unlistenable-class-preregistration.md`](../specs/2026-08-05-unlistenable-class-preregistration.md),
frozen before any count existed, with five amendments all committed before the stage each
affects. Raw data: `builder/analysis/2026-08-05-unlistenable-class/` — `ulc_census.json`,
`ulc_flags.json`, `ulc_exposure.json`, `ulc_discogs_gap.json`, `ulc_validation.json`.

**Nothing is adopted. No default is changed. No shipped code is touched** — nothing under
`api/`, `frontend/` or `builder/src/`.

---

## §0 — Summary, including what cuts against it

The owner chose option B of
[`2026-08-05-coherence-audit-results.md`](2026-08-05-coherence-audit-results.md) §4, scoped across
both data sets. Two things were measured and **they answer differently, which is the main
result**:

- **How many artists have nothing of their own to listen to** — about **1 in 9** on every cleaned
  map, and **slightly fewer** on the candidate data set. On this measure the data-set switch looks
  harmless.
- **How often those artists appear inside a journey** — **never** on the production data across
  48 measured journeys, and **regularly** on the candidate data, reaching **5 of 8 interior cards**
  on one journey after twenty presses.

**Cutting against the headline, and stated here rather than buried:**

1. **`ULC-R1` did not fire and no branch is assigned.** The run state was unmet (95 of 96 slots),
   and separately **the pre-registered statistic cannot see this effect** — §1.3c. The exposure
   comparison is **descriptive**. It may not be reported as a proven difference.
2. **The depth confound is live** (`ULC-AM5`, prereg §3.2): twenty presses is not a matched
   position on two different maps, so part of the exposure gap may be that the candidate map
   simply travels further.
3. **6 validation artists is a thin test set**, and the false-positive rate against *listenable*
   artists is **not measured by this track at all** (`ULC-B3`).
4. The exposure figures rest on **8 pairs**, inherited from `GBL-AM1` and not chosen for this
   question.

---

## §1 — Measured

### 1.1 Run state

| stage | state |
|---|---|
| `ULC-C1` census, five populations | **complete**; re-run end-to-end and every figure identical (determinism check) |
| `ULC-G1` gate | **complete**, branch `separable` |
| `ULC-S2` exposure | **95 of 96 slots.** `B-S0` does not reach depth 20 on Led Zeppelin → Guster |
| `ULC-R1` read | **NOT TAKEN.** Run state unmet; no branch assigned |

All five artifacts were checksum-verified against their manifest sidecars before being read; the
adopted artifact against `findings/2026-07-23-tiebreak-fix-adoption.md`.

### 1.2 `ULC-C1` — how many, and `ULC-G1` — can we detect them

> **`ULC-D2`**, the owner's chosen rule (`ULC-OG3`, `ULC-AM3`): *this artist has never put out
> anything of their own that is more than a single track.*

**`ULC-G1` — *can we pick out the artists he couldn't listen to without flagging huge numbers of
ordinary artists?* Branch: `separable`.** Both clauses met:

| clause | bar | result |
|---|---|---|
| catches the target class | ≥ 5 of 6 | **6 of 6** |
| does not sweep the map | ≤ 20 % of `ULC-P4` | **11.09 %** |

**Share of each map in the class:**

| population | what it is | `ULC-D2` | `ULC-D1` |
|---|---|---|---|
| `ULC-P1` `E-S0` | production data, production connection rule, cleaned | 11.13 % | 5.78 % |
| `ULC-P2` `B-S0` | candidate data, production connection rule, cleaned | 10.49 % | 6.32 % |
| `ULC-P3` `E-S1` | production data, trimmed-union, cleaned | 11.19 % | 5.83 % |
| `ULC-P4` `B-S1` | candidate data, trimmed-union, cleaned | 11.09 % | 6.80 % |
| **`ULC-P5`** | **the artifact the live site serves** | **22.23 %** | 9.95 % |

**`ULC-P5` has no isolating baseline and is reported alone** (prereg §0.3, `ULC-B4`): it predates
the drop wiring and carries **neither** filter. Its rate is roughly double every cleaned cell for
that reason and for no other. **No cross-archive sentence may include it.**

**The two licensed one-knob comparisons** (`ULC-B6` bars all others): `P2` − `P1` = −0.64 pp;
`P4` − `P3` = −0.10 pp. Both **slightly favour the candidate data**.

**The owner's ruling is what caught Brad Delson.** `ULC-D0`, the release-counting predicate,
misses him — one release, so it lets him through. `ULC-D2`, the track-counting one the owner
chose, catches him: that release holds one song.

| validation artist | MB release groups | sole, primary type | >1 track | caught by |
|---|---|---|---|---|
| Rick Davies | 0 | 0 | 0 | D2, D0, D1 |
| John McVie | 0 | 0 | 0 | D2, D0, D1 |
| Dallas Taylor | 0 | 0 | 0 | D2, D0, D1 |
| Joey Kramer | 0 | 0 | 0 | D2, D0, D1 |
| Max Martin | 2 | 0 | 0 | D2, D0, D1 |
| **Brad Delson** | 1 | **1** | **0** | **D2, D1 — not D0** |

**The unknown-track-count ambiguity is moot**, as `ULC-AM3` hoped: ~0.5 % of nodes, and the two
readings differ by 9 artists in every population. No adjudication was needed.

### 1.3 `ULC-S2` — how often they appear in a journey

> **`ULC-C2`:** *when you actually build a journey, how often does one of these artists turn up in
> the middle of it?*

**Mean share of interior cards in the class:**

| arm | map | d0 | deep (d10, d20) |
|---|---|---|---|
| `ULC-A1` | production data, production rule | **0.00 %** | **0.00 %** |
| `ULC-A3` | production data, trimmed-union, gentle ramp | **0.00 %** | **0.00 %** |
| `ULC-A2` | candidate data, production rule | 1.25 % | 6.51 % |
| `ULC-A4` | candidate data, trimmed-union, gentle ramp | 2.50 % | 15.36 % |

Both production-data arms are zero across **all 48 slots**. The candidate exposure is
**concentrated, not spread** — 5 of 16 deep rows carry all of it:

| pair | `A4` d10 | `A4` d20 |
|---|---|---|
| Arcade Fire → America | 2 of 5 | **5 of 8** |
| Tame Impala → Fountains Of Wayne | 3 of 5 | 0 of 2 |
| Young Gun Silver Fox → Eloy | 0 of 7 | 3 of 9 |
| Wishbone Ash → Pink Floyd | 1 of 2 | 0 of 2 |
| the other four pairs | 0 | 0 |

#### 1.3c The pre-registered statistic cannot see this effect — a defect in the design, not the data

`ULC-R1`'s trigger is a **paired median** difference (prereg §3.1). The exposure distribution is
**zero-inflated**: most rows are zero on both sides and a handful carry everything. The median
difference is **0.00 pp**, which would read `no_detectable_difference` for a gap between 0 % and
15 %.

**The statistic was not changed after seeing this, and must not be.** Selecting the measure that
gives the interesting answer, after seeing which one does, is the fishing the pre-registration
exists to prevent, and it would devalue every other figure here. Recorded and left alone.

**Two consequences that travel with any citation of §1.3:**

- **The run-state failure is not what blocks the call.** At 96 of 96 the median would still be ~0
  and the branch would have fired *wrongly*. The missing slot is a footnote; the statistic is the
  problem.
- **A looser reading of prereg §4 exists** — the two comparisons fire independently and `A4` − `A3`
  is complete — **and it is declined**, because it would be adopted after seeing which comparison
  it rescues.

**Any future re-read needs its statistic fixed in advance, in a new pre-registration.**

### 1.4 Why both filters passed the class through — two mechanisms, neither a near miss

**Diagnostic, outside the pre-registration.** It fixes no criterion and feeds no `ULC-` read. It
answers the question the owner raised at the card during the audit itself — *"I don't see any
releases for this artist. I'm surprised they weren't dropped by one of our filters."*

The no-release rule asks *is this artist release-less?* and answers with two signals, **neither of
which requires the release be theirs**:

- `has_release_group` — any MusicBrainz release group crediting them, any role, any type.
- `has_discogs_release` — their Discogs id in the `<artists>` element of any release, **sole or
  not**.

| artist | MB release groups | Discogs releases | of which sole | exempted by |
|---|---|---|---|---|
| Rick Davies | 0 | 1 (*My Kind Of Lady*, with Supertramp) | 0 | Discogs |
| John McVie | 0 | 3 (*Blues Giant*; a Bluesbreakers live album) | 0 | Discogs |
| Dallas Taylor | 0 | **76** (*Déjà Vu* and reissues) | 0 | Discogs |
| Joey Kramer | 0 | 1 (***Drum Loops and Samples***) | **1** | Discogs |
| Max Martin | 2 (excluded type) | 4 | 0 | MusicBrainz |
| Brad Delson | 1 (one track) | **0** | 0 | MusicBrainz |

**This is a second gap, distinct from the one the coherence audit found.** That one is *a single
sole MusicBrainz credit exempts you from both filters* — Brad Delson is the pure case. This one is
*zero MusicBrainz credits plus a non-solo Discogs credit exempts you from both*, and it accounts
for **four of the six**.

**The two rules use different Discogs tests and the looser one guards the emptier class.** The
featured-credit rule requires a *sole-credit* Discogs main-artist release; the no-release rule —
for artists with nothing at all — accepts any credit.

**The obvious fix is insufficient, and this is the most useful single fact here.** Tightening the
Discogs test to require sole credit **still would not catch Joey Kramer**, whose one sole-credited
Discogs release is a **drum sample library**. It is genuinely his, genuinely sole, and it is not
something you put on a journey.

**Confirmed on the cheaper instrument too — with one qualification that matters more than the
confirmation.** Across Discogs *masters* (3.1 GiB against 61.6 GiB for releases, 36 seconds
against 19 minutes — the owner's suggestion): **not one of the six has a single sole-credited
master**, and three have no master at all.

> **Masters alone would have got Joey Kramer backwards, and he is the load-bearing case.** He has
> **0 masters and 1 sole-credited release** — so a masters-only check reports no sole Discogs
> credit, and it is precisely his sole credit, the drum sample library, that shows "require sole
> credit" to be insufficient. This is the tail-coverage loss `NEXT.md`'s standing masters deferral
> predicted ("single-version releases often have no master"), landing exactly on the tail this
> class lives in. **Masters is a cheap screen; releases is what any conclusion resting on an
> artist having nothing must be checked against.**

---

## §2 — What I infer from it, in plain language

*Inference, labelled as such, and written so that someone who has never opened this repo can
disagree with it.*

**Both maps contain these artists at the same rate. Only one of them walks you through them.**

Today's map has never once put an artist-with-nothing-to-play in the middle of a journey — zero,
across 48 journeys. The candidate map does it regularly, and on one journey after twenty presses,
**five of the eight artists between the two you picked were people with nothing you can go and
listen to.**

**This is not a population problem, it is a routing problem.** The candidate map is the one that
actually digs into obscurity when you press *I know them*, and this class lives in obscurity.
**The exposure is the price of the digging** — the coherence cost of the thing that was supposed
to fix novelty, landing on precisely the map that was listened to and audited.

**It reverses the comfortable reading of the count, and the count was reported first.** Counting
artists on the map said the switch was harmless. Counting who you actually meet says otherwise.
Anyone quoting §1.2's rates as reassurance without §1.3 has the story backwards.

**The live site is a separate and worse case, for a boring reason.** It serves an artifact built
before either filter existed, so about **one artist in four and a half** on it has nothing of
their own to play, against one in nine on any cleaned build. That is a fact about software running
today, not about any candidate.

**The filters did not make a bad call — they never looked.** A session drummer credited on *Déjà
Vu* is "not release-less" seventy-six times over.

---

## §3 — Weakest link

**The load-bearing assumption is that having nothing to listen to shows up in credit shape.** It
held on 6 of 6. Six is six.

**What would falsify it:** a predicate fixed from the definition missing most of the known cases.
It did not — but the test set is small, and the pre-registration says plainly that catching what
it should is *not* evidence it spares what it should.

**What I would defend:** the census, the gate, the factor table, and §1.4's mechanism — that last
one follows from the census code's own boolean and is not an inference.

**What I would abandon cheaply:** `ULC-D2` as a *rule*. It is a first hypothesis that survived one
narrow test. Keith Scott passes it on a single 1993 television-theme track, which the owner
himself now considers borderline; a rule would need its own pre-registration and his ruling on
where to cut (`ULC-OG2`).

**The one I would abandon fastest:** any equivalence claim from `ULC-R1`. It did not fire, its
statistic could not have seen the effect, and 16 paired observations would have been thin even if
it had.

---

## §4 — Options and their consequences

**Adoption is not among them** (`ULC-B7`). These are the owner's because each spends his time or
accepts a residual risk.

**A. Fix the filters, then re-census both drop lists.** The most actionable outcome here, it is
independent of the data-set decision, and it shrinks exactly the cost §1.3 measured. **Cost:** the
obvious fix is insufficient (§1.4), so it needs design rather than a one-line change; and both
frozen lists must be re-censused, roughly an hour of dump passes.

**B. Rebuild and deploy on the production data set.** Takes the live site from 22.23 % to about
11 %, and populates the Deezer ids the running artifact lacks — the wrong-artist clip defect is
inert only for want of them. **No crawl, no listen, no adoption decision**, because no routing
changes. **Cost:** essentially none, and it is the only way to separate "the filters and clips got
fixed" from "the map changed" in what the owner experiences. *(The owner tabled this on
2026-08-05 in favour of trying the candidate map live first; recorded as his call, and the
isolation is what it spends.)*

**C. Pre-register a clean re-read of the exposure comparison.** Fix the statistic, swap the one
unreachable pair, re-run, obtain a licensed verdict. **Cost:** a fresh pre-registration and a
cycle, to put a formal label on something already visible. **I do not think it changes any
decision**, and would not recommend it unless one comes to turn on it.

**D. Switch to the candidate data set.** See §4.1 — it is not one action.

### 4.1 "Switch to the new map" is two different actions, and neither has a listen behind it

- **The data only.** One line in `BuilderConfig`, rebuild, deploy. This is `ULC-A2`: exposure
  **6.51 %** against today's 0 %. **Never listened to.**
- **The package that was listened to and audited.** Candidate data **plus** the trimmed-union
  connection rule **plus** the gentle ramp. This is `ULC-A4`: exposure **15.36 %**. **Neither the
  connection rule nor the ramp exists in shipped code** — `BuilderConfig` raises on any
  `cap_strategy` but `mutual_knn`, and no ramp knob appears anywhere under `api/src`. Two
  implementation jobs, not a config flip.

**The blind listen tested the package and returned the null**, whose pre-registered consequence
was *"production stands and Option A closes without adoption."* **Adopting either version is
therefore an override of a standing null or a fresh listen on a new candidate** — the run-once
rule expressly permits the latter. Fixing the filters first makes it a genuinely new candidate.

**No re-crawl is required for any of this.** The full candidate archive is on disk —
`builder/scratch/grt-archive-algb/`, 75,000 responses, verified — and a graph is already built
from it. What remains is rebuild-and-deploy, not fetch.

---

## §5 — Follow-on work, with success conditions

Each is named rather than waved at, per the closeout deferral rule.

| # | Item | Condition |
|---|---|---|
| **`ULC-F1`** | ~~**Drop-list keys must carry population identity, not just algorithm.** `no_release_drop.py:30-33` reasons that "a build's algorithm is its archive identity" — true only while one algorithm means one crawl. Extend the crawl and the lookup **succeeds**, silently handing back a list censused over a smaller population, leaving every new artist unevaluated.~~ **✅ DISCHARGED 2026-08-05 by the `ULF-` filter session**: the frozen payloads carry the archive population (count, sha, members) and `build_from_archive` refuses an archive containing artists the census never evaluated — tested, and exercised against the real archive. Record: the `ULF-` execution log. | ~~**Before any crawl extension.** Do it in the filter session, which is re-censusing both lists anyway; retrofitting later means a third census. Discharged when a mismatched population **refuses to build**, as an uncensused algorithm already does.~~ Condition met as written. |
| **`ULC-F2`** | ~~**The census discards what it learns.** It reuses prior coverage (51,115 of 74,960 artists last time) but never writes back the freshly-censused results, so each expansion re-pays for artists already done.~~ **✅ DISCHARGED 2026-08-05 by the `ULF-` filter session**: the coverage store (`builder/analysis/census-coverage/`) is read and written back by the census; its first run passed dumps for only the 8,137 archive artists no prior census covered, of 98,296. Record: the `ULF-` execution log. | ~~**Same session as `ULC-F1`.** Discharged when a second census over an extended population passes dumps only for genuinely new artists.~~ Demonstrated on first use in the reuse direction; the extended-population direction fires at the first real crawl extension. ~~which `ULC-F3` still blocks~~ — **that blocker is GONE as of 2026-08-08: the extension has happened.** The remaining half now fires at `CEX-` plan Task 11 Step 3, the re-census over the 117,302 population, and is **not yet satisfied**. |
| **`ULC-F3`** | ~~**Crawl resume cannot extend.** `crawl.py:115` rebuilds the frontier as `discovered − done`; both are exactly 75,000, so raising the target produces an empty queue and an immediate exit logging `0 processed` — which reads as success. The frontier beyond 75,000 was never recorded, but is recoverable offline from the archive, since every archived response lists its neighbours.~~ **✅ DISCHARGED 2026-08-08 by the `CEX-` track**, exactly as the diagnosis predicted: the frontier WAS recoverable offline (`refrontier` rebuilt 42,302 from the archive and `CEX-G1` matched the baseline exactly), the bound moved from artists *discovered* to artists *fetched* so it can never be lost again, and the silent-success failure now **refuses**. Records: `builder/analysis/2026-08-08-cex-g1/`. | ~~**Before any crawl extension**, and it blocks one entirely. Discharged when a raised target demonstrably crawls new artists.~~ **Satisfied:** a raised target crawled **42,292 new artists** with 0 failures on 2026-08-08. |
| **`ULC-F4`** | **The `BYP-13` keep-check defect** — the featured-credit keep-check resolves clips by name, with about half its keeps unverifiable. Deferred by the owner 2026-08-05 to its own track; it is a fix, not a measurement, and running it inside this track would have moved the population mid-count. | **Its own track.** Not a blocker for anything above. |

**One expectation, not a measurement:** extending the crawl will probably make this class *larger*,
since discovery is breadth-first from the seeds and extension pushes further into obscurity, where
this class lives. That is an argument for `ULC-F1` and the filter fix preceding more data.

---

## §6 — Bookkeeping this read discharges

- **`ULC-B1`** rates only, never raw counts across populations — honoured.
- **`ULC-B2`** nothing here reopens the `GBL-` null; §4.1 states its consequence rather than
  re-reading it.
- **`ULC-B3`** `ULC-D2` is not presented as a drop rule; its false-positive rate is declared
  unmeasured in §3.
- **`ULC-B4`** `ULC-P5` appears only in sentences about the live site.
- **`ULC-B5`** no causal claim that this class produced the audit's verdicts.
- **`ULC-B6`** no `P4` − `P1` comparison is made.
- **`ULC-B7`** nothing adopted, no default changed, no shipped code touched.
- **`ULC-B8`** the sensitivity ladder is reported in `ulc_census.json` and selected from nowhere;
  `ULC-D1` is reported and fired nothing.
- **`ULC-B9`** the "22 of 23" figure is not used; see §7.

---

## §7 — A correction owed to `2026-08-05-coherence-audit-results.md` §6

**That note owns the `CAU-` figures and the correction belongs in it, appended.** Recorded here so
it is not lost.

§6 reports *"22 of 23 never evaluated by either rule."* **That denominator includes the audit's own
12 planted controls**, which were injected by the harness rather than delivered by routing — so
filter coverage over them is not a meaningful question, and all 12 count as "never evaluated"
trivially.

**The correct figures: 11 real artists, of whom 10 were never evaluated and 1 (Pino Palladino) was
in the featured-credit class and kept.** Reproducible via `ulc_validation.py`.

**§6's conclusion stands** — the class was never looked at — at 90.9 % rather than 95.7 %. **Its
evidence base is half the size it appears**, which mattered here because this track nearly built a
calibration set on it.

**No `CAU-` criterion, gate or branch is affected.** `cau_score.py:62-68` excludes controls and
control-adjacent slots correctly. The defect is confined to that one hand-written check — which is
the third instance of the pattern that note's own §7 names: *a cost declared in one place and not
summed in another.*
