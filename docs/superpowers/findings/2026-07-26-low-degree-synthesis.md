# What the three low-connection measurements add up to — 2026-07-26

**Role: an INTERPRETATION of committed measurements. AUTHORITATIVE for nothing, and it
owns no figures.** Every quantity below belongs to the document or directory cited beside
it. Nothing here is a new measurement, and where this document and a cited one disagree,
**the cited one wins.**

Read-only. **Nothing is adopted, nothing is proposed, no threshold is set, no arm is
designed.** Path-quality work is paused by owner decision and **this document is not a
resume signal** — it assembles readings that already exist in the record and does not
argue for acting on any of them.

Identifiers are namespaced **`SYN-n`** — verified unused across the repository before
allocation. **`CNS-` is the census document's own series and is not extended here.**
Nothing committed is renamed or renumbered.

**Provenance.** The reading assembled here came from an independent consulting session
across the three measurements below. It existed nowhere in the repository; that assembly
is this document's only contribution. Items the consulting session proposed that turned
out to be **already recorded** under an existing identifier were dropped rather than
restated — `STC-4`, `STC-6`, `MKS-5b` and `CNS-2` each absorbed one.

**The three sources, none of which interpreted across the others:**

| document | what it owns | figures owned by |
|---|---|---|
| `2026-07-25-mutual-knn-stranding.md` (`MKS-`) | the mechanism, per artist | `builder/analysis/2026-07-25-mutual-knn-stranding/` |
| `2026-07-26-low-degree-census.md` (`CNS-`) | who is affected | `builder/analysis/2026-07-26-low-degree-census/` |
| `2026-07-26-stranding-causes.md` (`STC-`) | why they are affected | `builder/analysis/2026-07-26-stranding-causes/` |

---

## 1. The findings

### `SYN-1` — one symptom, three problems, three costs

*(Plain: the artists the app can barely reach got there three different ways, and fixing
each one costs something completely different.)*

The low-connection population is routinely spoken of as a single problem with a single
fix. It is not. `STC-1` separates it into three causes with nothing in common but the
symptom, and the remedies are not comparable in cost:

| cause | what happened | remedy | what it costs |
|---|---|---|---|
| **CAP-STRANDED** | a full candidate list, discarded by the both-ways rule | a different cap rule | a **rebuild** — but read `STC-4` first |
| **SOURCE-THIN** | the source named almost nobody **above a cut-off this project chose** | re-request at a lower cut-off (`STC-6`) | a **full re-crawl**, and edges resting on weaker evidence |
| **CRAWL-FRONTIER** | the crawl had not reached the candidates | crawl further | smallest group; **not worth doing on its own** |

Shares, the boundary between the populations, and the eleven-row sensitivity table:
`builder/analysis/2026-07-26-stranding-causes/REPORT.md`. **The boundary is the stranding
session's stated choice, not a fact** (`STC-` §3), and the report prints every alternative
so a reader may overrule it. This document does not pick a row.

**What is new here is only the juxtaposition of the three costs.** Each cause is
`STC-1`'s; the observation that a rebuild, a re-crawl and a shrug are being discussed as
though they were one decision is not recorded anywhere else.

### `SYN-2` — against the whole graph, the rule is a small cause, and it is the cause you would meet

*(Plain: the graph rule is a minority cause by headcount and the dominant cause among
artists you would have heard of.)*

Every share in the stranding record is expressed **against the low-connection set**.
Expressed against **the whole artifact** instead, the population attributable to the
both-ways rule is **on the order of six per cent of all nodes** — arithmetic over two
figures the report owns (its cap-stranded count and its node count), not a new
measurement, and quoted only to that precision deliberately.

That reframing cuts both ways at once, which is the point, and `STC-3` is the rule for
reading it: **neither half may be quoted without the other.**

- **By headcount** the rule is a minority cause even within the low-connection set, and a
  small fraction of the graph overall.
- **By who a listener would recognise** it is overwhelming. The report's popularity-band
  table stratifies the causes almost perfectly: at the top of the in-graph popularity
  ordering, essentially the entire band is cap-stranded, and **48 of the top 50 are
  rescuable by the most permissive rule available** — with none at all in the least
  popular band.

> **One precision the consulting framing blurred, and it matters because this project has
> been bitten by exactly this class.** *Cap-stranded* and *rescuable* are two different
> columns of that table. The 48-of-50 figure is the **rescuable** count (artists listed by
> ten or more others); the cap-stranded share of the same band is a different, slightly
> higher number. They nearly coincide at the top and diverge sharply lower down — which is
> `STC-4`'s whole point. Cite the report's table rather than either number in isolation.

**`STC-4` is the strongest thing cutting against reading this as a mandate**, and it is
not restated here: most of the set is named by very few artists, so even the most
permissive rule reaches few of them, and those it does reach are all at the popular end.

### `SYN-3` — the largest lever on the headcount is a parameter we chose

*(Plain: most of these artists are barely connected because of a cut-off we set.)*

`STC-6` established this and filed its success condition. **Nothing about the mechanism is
new here, and this item exists only to rank it against the other two causes:** of the three
in `SYN-1`, the co-occurrence cut-off in `BuilderConfig.algorithm` is the one with the
largest reach by headcount, and it is inside this project's control rather than a limit of
the source. `STC-6` also records that the length limit was **checked and provably cannot**
produce a short list — do not re-open that as an objection.

**Its payoff is unmeasured**, and `STC-6` says so: nobody knows how many artists a lower
cut-off would help, or whether the extra edges would be good ones, and they rest on weaker
evidence by construction. A named option with an unmeasured payoff is not a proposal.

### `SYN-4` — the falsifier, fixed before it could be shaped by a result

*(Plain: if the app already routinely walks you through barely-connected artists, then
being barely connected is not what keeps them off your screen, and most of the reasoning
above stops mattering.)*

`SYN-1`–`SYN-3` all presuppose that a low connection count is what keeps an artist off the
screen. That presupposition is inherited — `DRV-4` states it structurally and the census
measures the population — but **it has never been checked against artists the router
actually delivered.**

**Committed before the measurement, and this is the numeric part.** The graph's own median
degree is 9 (the stranding report), so a degree-blind selection would put roughly **half**
of interior cards below ten connections. Against that null:

- **Expectation:** distinct interior artists with fewer than 10 connections will be a small
  minority — **under 10 %**.
- **The falsifier FIRES at ≥ 25 %.** At that point connection count plainly does not gate
  delivery, and `SYN-1`–`SYN-3` lose most of their motivation — they would still describe
  the graph correctly, but would stop describing anything the user experiences.
- **10 %–25 % is the ambiguous band**, and I will read it as *weakened, not refuted*, and
  say so rather than picking whichever side suits.
- **Second, independent clause:** ≥ 5 % of distinct interior artists at **two or fewer**
  connections also fires it — that is the census population itself, claimed to be
  structurally undeliverable.
- **An instrument gate, not a result:** a **degree-1 artist cannot be an interior card at
  all** (`DRV-4`; census §1). If any appear, my extraction is wrong and the run is void —
  that reading is not available as a finding.

**Stated in advance, because it is the honest half:** the pair set in the committed runs
was pre-registered and skews toward famous endpoints, so a *low* share is the expected
result and is **weak confirmation** of anything. This falsifier can fire meaningfully; it
cannot pass meaningfully. It is worth running only because the failure would be decisive.

### `SYN-5` — a consulting prediction that was right in shape and wrong in cause

*(Plain: the guess about why these artists are barely connected was wrong, and the wrong
part is exactly the part that decides what it would cost to fix.)*

The consulting session predicted that the low-popularity mass of the low-connection set
would be **crawl frontier** — artists whose neighbours were discovered but never fetched.
The shape was right: that mass is real, it is where the headcount lives, and it is not
rule-stranded. **The cause was wrong.** `STC-1` measured the crawl-frontier category and
found it nearly empty; the mass is SOURCE-THIN instead. Size: the stranding report.

**Recorded rather than deleted, because the error is instructive in a specific way.** The
two causes look alike from outside — both are "the artist has almost no candidates" — and
they are indistinguishable without measuring *what the source offered* separately from
*what the crawl had*. But they have completely different remedies: crawling further versus
re-crawling at a different threshold versus nothing. **A prediction can be directionally
right and still point at the wrong bill.**

### `SYN-6` — the ear has endorsed bounded degree; it has never been asked about the both-ways rule

*(Plain: the owner's listening tests told us it was bad to let a handful of artists connect
to thousands of others. He has never been asked what he thinks of the separate rule that two
artists must each name the other.)*

**A derivation from committed documents, not a claim about code.** Nothing was run, routed,
rebuilt or read from source for this. It is an audit of what the two blind listens actually
varied, against their own recorded arm tables, and each leg is verified below.

Two blind listening tests decided the graph. **Neither varied the reciprocity requirement
against a bounded-degree alternative:**

| listen | arms | reciprocity | degree bound | what it can separate |
|---|---|---|---|---|
| Phase 2 log **§12** | `control` (`pre_symmetrise`) v `capfix` (`mutual_knn`) | **differs** | **differs** | a package, not a knob |
| Phase 2 log **§16** | `capfix` v `d025` | **same — both `mutual_knn`** | same | rescale and damping only |

- **§12 is a package comparison, and its own correction notice already says so.** That notice
  records that changing `cap_strategy` changed **two** things at once — reciprocity, and
  whether top-k selection can see the p99 ceiling — and states in terms that the comparison
  "does not establish that the reciprocity rule caused the improvement." The losing arm also
  bounds nothing after symmetrisation, so the winning arm carried reciprocity **and** a degree
  bound against an arm carrying neither. Three columns, not one.
- **§16 held reciprocity constant.** `d025` is `mutual_knn` as well
  (`2026-07-22-phase2-sweep-results.md` §1), so the both-ways test was required on **both**
  arms and the comparison ran on rescale, damping and density.
- **No third listen bears, and this was checked rather than assumed.** The C3
  `known`-mechanism blind listen (`../specs/2026-07-22-c3-known-mechanism-blind-listen.md`)
  decides between two *shapes of the `known` button* with a production anchor, and its §8
  pins **every** arm to a single artifact. Reciprocity is therefore constant across everything
  it served. It is a cost-function comparison on a fixed graph and says nothing about the cap
  rule.

**So the listening evidence supports BOUNDED DEGREE and has never tested RECIPROCITY.** The
distinction is not academic: Phase 1 log **§2.10** records that in this codebase the two are
not separable knobs — dropping the both-ways test restores unbounded degree — and that
separating them needs a `cap_strategy` **that does not exist**. No artifact has ever been built
that a listener could have used to tell them apart, so the gap is structural rather than an
oversight in either protocol.

**What this does not do.** It does not weaken either verdict, does not propose a rule change,
and does not reopen `MKS-5b`, which stands unchanged. Its practical effect is on **`MKS-5b`'s
currency, not its force**: an argument that the *degree bound* must be preserved keeps its
listening support; an argument that the *both-ways rule* won a listen does not have any. Note
that this document's own §4 already states it in the correct currency — "bounded degree is what
`capfix` won its blind listening test for delivering" — so the imprecision this item names lives
elsewhere, not there.

### `SYN-7` — both listening verdicts predate most of the calibration record

*(Plain: the owner gave both of his verdicts on the graph before he had said most of what he
has since said about what makes a path good.)*

**A derivation from committed documents, not a claim about code.** It is a comparison of
datestamps that the documents themselves carry; both were read before writing this.

Both verdicts are dated **2026-07-22** (Phase 2 log §12 and §16). `../WHAT-GOOD-LOOKS-LIKE.md`
dates **values 5, 6 and 7 to 2026-07-23**, and **values 8 and 9 to 2026-07-24** — five of its
nine values, including **novelty is delivered *through* coherence, not traded against it**
(value 8) and **reducing famous artists is the live problem; eliminating them would be an
over-correction** (value 9).

So the project's strongest instrument was read twice **before most of its calibration file
existed.** That is not a defect in either verdict, and it is not a reason to re-run one — the
file grew precisely *because* the record was being used, and value 8 was articulated by the
owner correcting a restatement of value 1. What it bears on is narrower: **a 2026-07-22 verdict
cannot be cited as the owner endorsing a criterion he articulated in 2026-07-23 or 2026-07-24.**
The verdicts are evidence about the arms that were served; they are not evidence about values
that did not yet exist.

**What this does not do.** It does not invalidate, re-open or re-date either verdict, and it is
not an argument for a third listen — Phase 2 log §15 governs that and is untouched here.

## 2. What this document does not establish

- **Nothing about whether any rule change would be better.** No alternative rule was run,
  in any of the three sources or here. `MKS-5b` binds any redesign and is not answered.
- **Nothing about path quality.** No path was routed and no cost weight was read for
  `SYN-1`–`SYN-3`.
- **No new figure.** Every quantity is cited; the only arithmetic is `SYN-2`'s ratio over
  two figures from one report, quoted to one significant figure.
- **It does not rehabilitate the census's withdrawn coverage-gap reading** (`CNS-`, §4),
  and `STC-2` explicitly points the other way on crawl coverage.

## 3. Calibration — which item I expect to fail

**`SYN-2` is the most likely of these to be wrong**, and the reason is a hazard this
project has already been bitten by three times.

Its second half — *the dominant cause among artists you would recognise* — leans on **the
in-graph popularity ordering standing in for fame.** Phase 1 log **§2.11** is explicit that
popularity is not fame at the top of the distribution, and **`CNS-2`** is worse news than
that in this specific case: the fame proxy used to validate the top of that ordering was
itself **materially contaminated by misidentification**, in the direction of *inflating*
fame, and it sorts the wrong rows to the top of exactly the lists a reader eyeballs. Two
readings of the census were withdrawn over it.

**What survives, and why I still think `SYN-2` is worth stating.** The stranding report's
screen is defensible on a narrower ground than fame: popularity accumulates **before** the
cap, so the reciprocity rule cannot manufacture the correlation — the screen rides on a
stage the defect never touches. And the named cap-stranded artists at the top (`MKS-2`'s
worked examples, and the report's list) are recognisable on inspection rather than by
proxy. **So the stratification is real; what is soft is the claim that the ordering ranks
*fame*.**

**What would falsify it:** a population-independent fame source disagreeing with the
in-graph ordering across the top of the cap-stranded list. `CNS-` §4 records that no such
source is currently available and that in-graph popularity and Wikipedia pageviews share a
blind spot in the same direction, so neither can audit the other.

**What I would defend cheaply:** `SYN-1` and `SYN-5` — both are restatements of counts
over the archive and the artifact, and neither depends on any fame claim. **What I would
abandon on one contrary measurement:** `SYN-2`'s second half, and `SYN-3`'s ranking if the
boundary row is moved far enough (the report's sensitivity table shows how far).

**And one methodological error, recorded beside the substantive ones.** A consulting session
proposed settling the deliverability question **by ordinary use of the app** — asking the owner
to build journeys through low-connection artists and report whether they ever appeared. No
amount of use could have settled it: the two candidate mechanisms are indistinguishable from
the user's seat, because an artist that is *arithmetically* short of places to sit between two
others and an artist the router *prices out* both produce the identical experience of never
being offered. That is the confound `2026-07-26-committed-walk-deliverability.md` §5 leaves
open, and it is why the question moved to a committed-walk measurement rather than an app
session (`../TEST-QUEUE.md`, 2026-07-26). **The general form is the part worth keeping: use
cannot discriminate between mechanisms that look the same from outside the app** — which is
worth holding against this project's otherwise sound instinct to reach for use when a
measurement looks expensive.

---

## 4. Opinions — a consulting session's position, not a proposal

**Fenced off deliberately.** Nothing in this section is a finding, a recommendation, or a
plan. It is recorded so that a position taken outside the repository is visible inside it
and can be argued with. **Path-quality work remains paused; none of this is a resume
signal, and no part of it is pre-registered.**

**The both-ways rule should not be loosened.** Dropping the reciprocity test restores
unbounded degree — that is Phase 1 log **§2.10**'s coupling, recorded as `MKS-5b` — and
bounded degree is what `capfix` won its blind listening test for delivering. Trading a
blind-listen win for a headcount improvement in a population the listener may never meet is
the wrong trade, and `STC-4` says the permissive rule would not reach most of that
population anyway.

**The targeted candidate, if anyone ever picks this up, is a bounded degree floor:** restore
a small number of edges **only** for artists left at one or two connections, with a quota on
the *receiving* side so that maximum degree cannot rise. The appeal is that it aims at the
symptom the census actually measured rather than at the rule that caused it.

**Its bound must be demonstrated by simulation before anything is built.** `MKS-5b` is
explicit that a targeted rule *may* escape §2.10's coupling but that this has to be shown,
not assumed — and the simulation is cheap relative to a rebuild, which is the whole argument
for doing it in that order.

---

*Sources are the three documents named at the head. This document owns no figures and
supersedes nothing.*
