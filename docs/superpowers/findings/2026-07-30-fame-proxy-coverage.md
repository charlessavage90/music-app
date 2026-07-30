# What the fame ruler can and cannot see — coverage of three instruments

**Role: ACTIVE analysis record. OWNS ONE MEASUREMENT SERIES** — the fame-instrument
coverage and agreement tables, whose data lives in
`../../../builder/analysis/2026-07-30-fame-proxy-coverage/` and is cited here, not
restated elsewhere. Scoring and path-quality figures remain owned by
`2026-07-21-scoring-adjudication.md`. Identifiers **`FPC-`**, collision-checked against
the whole repository 2026-07-30.

**Scope: DESCRIPTIVE SCOPE PROBES, in the `CS-P0` sense. Nothing is adopted, no criterion
is fixed, no arm ran, and no currency changed.** A pre-registration is owed before any
criterion is built on any instrument here. **Track B is untouched** — it scores in
in-graph popularity percentiles against a fixed adopted frame.

**Each probe's expectations and read thresholds were committed before it ran**; the git
timestamps are the evidence. **Two of three predictions were refuted**, and the refutations
are the most useful part of this document.

---

## 0. The correction this document owes, stated first

The case that opened this line of work was that the Wikipedia fame floor is **actively
corrupting** fame-currency measurements. **That is not what the measurement says, and the
overstatement was mine.**

`FPC-2` shows the floor barely touches what the router actually delivers, and its reach
*falls* with bypass depth rather than rising. `FPC-1` shows the instrument is reporting
correctly in the overwhelming majority of cases — those artists really do have no article.
**Track 2's reads are not invalidated by anything here.**

What survives is narrower and still worth acting on: `FPC-3`. The blindness is **latent**.
It binds on the graph's population, not on current routed output — and it would begin
binding precisely when the product starts succeeding at the thing `REQ-37` and `DD-F1`
demand.

**`FPC-9` then measured that last clause instead of leaving it as an inference, and it
fired.** On the most obscure route this artifact admits, **38.7%** of delivered interiors
are invisible to the fame ruler. So both halves are true and neither may be quoted without
the other: *the ruler is adequate for what the router does today, and goes blind on more
than a third of what it would deliver if the obscurity work succeeded.*

## 1. Findings

### `FPC-1` — the floor is mostly real, not an artifact of name matching

*(Plain: when the fame ruler says "no article", it is almost always right.)*

Of Track 2's 185 artists scored at the floor, 179 are checkable against the artifact by
unique name. **10 have an English article after all; 169 genuinely have none.** So
**5.6% of the checkable floor was resolution failure**, not obscurity.

*Prediction status: I expected this to be much larger. It is not.*

### `FPC-2` — the floor barely reaches routed output, and it FALLS with depth

*(Plain: the artists the app actually shows you are almost never ones the fame ruler is
blind to — and the deeper you press bypass, the less true it gets.)*

Pooled across Track 2's eleven arms, the share of **distinct routed interiors** with no
English article runs **5.3% at bypass depth 0 down to 2.4% at depth 20**, monotonically.
By delivered slots, 10.1% down to 6.7%. ListenBrainz covers **100%** of routed interiors
at every depth.

**Pre-committed read: `< 10%` at every depth means "a refinement, not a defect."** That
verdict stands on the distinct measure at every scored depth.

*Prediction status: **REFUTED.** I predicted the share would rise with depth.*

**The mechanism is the interesting part**, and it corroborates rather than contradicts the
record: the router never descends far enough to enter the blind region. That is `§2.9`'s
finding and `DD-F1`'s, arriving from a third direction.

### `FPC-9` — on the most obscure route the graph admits, the ruler goes blind on 38.7%

*(Identifier allocated after `FPC-8`; placed here because it is `FPC-2`'s test. Nothing is
renumbered.)*

*(Plain: today's router stays famous, so the fame ruler copes. Push the router as hard
toward obscure artists as this graph physically allows, and more than a third of the
artists it hands you are ones the ruler cannot rank at all.)*

`FPC-2`'s weakest link was that it rested on Track 2's famous-skewed pair set. Track 3's
committed paths test it on more obscure pairs **and** carry a `LIMIT` arm — the
`w → ∞` min-sum-percentile route, the most obscure path the graph admits, not a tuned
candidate but the ceiling.

| arm | distinct interiors | no EN article | LB covered | median interior pctl |
|---|---|---|---|---|
| production, d5–d20 | 131–155 | 6.3–8.4% | 100% | 0.982–0.986 (top 10%) |
| **`LIMIT`, all depths** | 62 | **38.7%** | **100%** | **0.6072 (upper half)** |

**Pre-committed read: `≥ 25%` on the `LIMIT` arm makes `FPC-2`'s verdict CONDITIONAL on
production's current pricing.** It is 38.7%. The verdict is conditional.

This is the finding that changes what the coverage numbers mean. `FPC-3`'s latent blindness
is no longer an inference from the population — it is a measured property of the route the
router would take if the obscurity work succeeded. **The instrument fails exactly where the
product is trying to go**, and the criteria that would judge that work are the ones that go
blind.

Bounded, and stated in the probe before it ran: this is bounded by *this artifact*. A graph
rebuilt to carry famous→obscure edges would move the reachable route again, and no
measurement here anticipates that.

### `FPC-3` — but 55% of the artifact is invisible to the ruler

*(Plain: for more than half the artists in the graph, the fame ruler returns the same
value — "unknown" — so it cannot rank them against each other at all.)*

**40,822 of 74,193 artists (55.0%)** carry no English Wikipedia article. By band:

| band | artists | LB covered | has Wikidata | has EN article | any language |
|---|---|---|---|---|---|
| top 0.1% | 75 | 100.0% | 100.0% | 100.0% | 100.0% |
| top 1% | 667 | 100.0% | 100.0% | 99.6% | 100.0% |
| top 10% | 6,678 | 100.0% | 88.0% | 83.0% | 86.6% |
| upper half | 29,677 | 100.0% | 67.0% | 57.0% | 64.1% |
| lower half | 37,096 | **99.9%** | 36.7% | **27.4%** | 34.3% |

**This is the finding that survives §0's correction.** `FPC-2` says the blindness is not
currently binding; this says the graph is more than half in the dark, which is where any
successful obscurity push has to go.

### `FPC-4` — ListenBrainz popularity covers the tail; nothing else here does

*(Plain: the ListenBrainz table returns a real number for essentially every artist,
including ones with a dozen listeners.)*

**74,151 of 74,193 (99.94%)**, 42 nulls in the whole artifact, and **99.9% in the bottom
band** against Wikipedia's 27.4%. MBID-keyed, so no name-resolution step exists to fail.
`POST /1/popularity/artist`, 1,000 artists per request, whole graph in ~75 requests.

This is the instrument the alpha design `§4.1` named in advance — *"a real ListenBrainz
artist-popularity table, should one become obtainable, is a drop-in improvement"* — and it
did not exist when `§6a`–`§6f` eliminated every alternative on cost.

### `FPC-5` — multilingual coverage adds more than I predicted, and still does not fix the floor

*(Plain: counting every language's Wikipedia rather than just English rescues a few
thousand artists, and leaves nearly half the graph still dark.)*

Coverage gained by counting any language rather than English alone: **0.0 / 0.5 / 3.6 /
7.1 / 6.8 percentage points** by band, top to bottom — roughly **4,600 artists**, moving
the floor from 55.0% to about 48.8%.

*Prediction status: **REFUTED.** I predicted under 5 points anywhere and named over 5
points as the refuting condition. It is 7.1 and 6.8 in the two largest bands.* The
200-artist pilot that suggested 2 points understated it.

⚠ **Stated before the run and still binding:** this sample **is** the artifact's own
population, which is ListenBrainz-skewed, so non-Western artists are under-represented
before anything is measured. That biases this read *toward* under-counting the multilingual
gain. It is evidence about our graph, not about Wikipedia.

### `FPC-6` — the two external instruments agree only weakly, at every level

*(Plain: how many people play an artist on ListenBrainz and how many encyclopedias write
about them are not the same thing, and knowing one tells you surprisingly little about the
other.)*

Spearman between LB distinct listeners and language-Wikipedia count: **pooled 0.4365**;
within band **+0.385 / +0.480 / +0.502 / +0.319 / +0.208** top to bottom.

The pooled figure is conditioned on having an article at all, which compresses it — so
read it as a floor on disagreement, not a measure of it. **They are not substitutes.**

*Prediction status: partly wrong. I predicted strong pooled agreement with weak within-band
agreement; agreement is weak at both levels.*

### `FPC-7` — resolution failure is small but script-skewed, and one case is severe

*(Plain: the ten artists the old name search missed are mostly ones whose names are not
written in the Latin alphabet — and one of them is a global phenomenon.)*

The 10 recovered artists concentrate in non-Latin scripts and unusual characters. **初音ミク
(Hatsune Miku) carries 50 language Wikipedias and was scored at the fame floor as maximally
obscure.** Others: 黒沢ともよ (16), 洲崎綾 (14), A‐WA (13, a non-standard hyphen).

Small in count, wrong in a specific and correlated direction, and **eliminated outright by
the MBID join** — `P434` *is* the MusicBrainz artist ID.

### `FPC-8` — the magnitude question

*Running at the time of writing; read fixed in `fp_magnitude.py` before execution: ≥10% of
sampled artists moving ≥20 rank percentiles between English-only and all-language pageviews
makes multilingual a materially different instrument; <5% means English is an adequate
stand-in. A high pooled correlation is pre-committed as **not** closing the question,
because the defect being looked for is a misranked tail underneath a strong aggregate.*

## 2. The identity finding, separable from everything else

Name search fails in **two** directions. It misses artists — and it can resolve to the
**wrong** artist and return a confident, bogus value. The graph carries the live instance:
it holds **GOOSE** (Belgian dance/electro, `6849ebec-…`) and **not** Goose (US jam band,
`b925a474-…`), so a name-keyed lookup for "Goose" scores the wrong band. A missing value is
a null you can see; a wrong value is not.

`P434` removes the class. **This holds whatever is decided about currency**, and it is the
cheapest thing here to act on.

Cost note: query **Wikidata for `P434`**, do not crawl MusicBrainz for its external links —
1 req/s is ~21 hours for the artifact; batched against WDQS it is minutes.

## 3. Weakest link

**`FPC-2`'s weakest link was tested and it fired** — see `FPC-9`. What remains weak is
`FPC-9` itself: it rests on **62 distinct interiors from one arm on twelve pairs**, and the
`LIMIT` route is a construct nobody proposes shipping. It is a ceiling, not a forecast. Its
value is that it bounds the question — no router on this artifact can deliver more
obscurity than that — and a ceiling is exactly what a latent-risk claim needs.

**What would falsify `FPC-9`'s reading:** a realistic candidate device that reaches
materially more obscurity than production *without* approaching the `LIMIT` route's
interior percentiles. Track B's `R2` result — quota edges present at famous nodes and
declined at production weights — is the nearest live evidence, and it points at the router,
not the ruler.

**What I would defend cheaply:** `FPC-3` and `FPC-4` — both are counts over the whole
artifact against two APIs, and neither depends on a fame claim, a pair set, or a router.
**What I would abandon on one contrary measurement:** `FPC-6`'s reading that the
instruments are complements rather than substitutes, which leans on a correlation
conditioned on article presence.

**And the standing hazard, unchanged by any of this:** ListenBrainz and English Wikipedia
under-represent the same artists by ~10× against outside references (measured on one pair,
2026-07-30). **Their agreement is a shared blind spot, not corroboration.** Neither can
audit the other, and no instrument here can settle it.

## 4. What this does not establish

- **Nothing about coherence.** No offline proxy for it exists (`SYN-6`); fame is not
  coherence.
- **Nothing about validity.** Coverage is not correctness — an instrument can cover
  everyone and order them wrongly.
- **Nothing that licenses a currency change.** That touches every fame-scored criterion and
  forces a separate decision about whether prior results are re-read.
- **Nothing about artists absent from the graph.** Goose is not in the artifact, so no
  instrument here scores it.
- **No claim that any Track 2 or Track 3 verdict changes.** `FPC-1` and `FPC-2` point the
  other way.
