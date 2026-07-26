# Why the low-degree artists are low-degree — 2026-07-26

**Role: AUTHORITATIVE for its own interpretation; OWNS NO FIGURES.** Every
quantity belongs to `../../../builder/analysis/2026-07-26-stranding-causes/`,
whose `REPORT.md` is the deliverable. **Cite that directory for any number.**

Read-only throughout. No rebuild, no routing change, no config change, nothing
adopted, **nothing proposed**. The path-quality pause is intact and this document
does not touch it.

Identifiers are namespaced **`STC-`**.

Predecessors, and this document does not restate them: the mechanism is
`findings/2026-07-25-mutual-knn-stranding.md` (`MKS-2` is the Meat Loaf worked
example this work generalises), the population is
`findings/2026-07-26-low-degree-census.md`, and the structural consequence is
`DRV-4` in `findings/2026-07-25-consulting-derivations.md`.

---

## 1. What was asked, and the answer that came back

The census established **which** artists the app can never introduce anyone to. It
did not say **why**, and the set was known to mix two causes with nothing in
common but their symptom:

- **CAP-STRANDED** — a full list of candidates who are in the graph, almost none
  of whom rank it back. The both-ways rule destroyed its connections.
- **CRAWL-FRONTIER** — sits at the edge of the snowball crawl, so few of its
  candidates are in the graph at all. Low degree under any cap rule.

**`STC-1` — the second category, as phrased, is nearly empty.** Fewer than two
artists in a hundred are low-degree because the crawl had not reached their
candidates. What actually fills that space is a third cause: the similarity
source named barely any similar artists for them **in the first place**. Counts
and shares: the analysis directory.

The distinction is not pedantry, because the three have different remedies and
two of them are unavailable:

| cause | remedy | cost |
|---|---|---|
| CAP-STRANDED | a different cap rule | rebuild — but see `STC-4` |
| CRAWL-FRONTIER | crawl further | a longer crawl; smallest group |
| SOURCE-THIN | re-request the source at a lower threshold — see `STC-6` | a full re-crawl, and weaker edges |

**`STC-2` — the crawl is not the problem.** For the artists below the boundary,
practically everything the source named had already been crawled. The snowball
did its job; the source does not know much about these artists. This is the
first measurement here that speaks to crawl coverage at all, and it points the
opposite way to the coverage-gap reading the census **withdrew** (`CNS`, §4 of
the census findings) — it is not evidence *for* that withdrawn reading, and must
not be cited as its rehabilitation. Different question, different instrument.

## 2. What I infer from it, in plain language

**What a person using the app would see.** There is a large group of artists —
around one in six of everything in the graph — that the app can never put in the
middle of a journey. Ask why, and there are three answers, and they are not
equally fixable.

For the artists **you would recognise** in that group — Meat Loaf, Elbow, The
Cult, The Streets, Manu Chao, Crowded House, Tom Jones — the data is all there.
Fifty similar artists, all of them in the app, and the app knows about them. The
rule then throws almost all of it away, because it insists both artists name each
other, and a famous artist's neighbours are more listened-to than it is and name
somebody else. **Those are recoverable, and a rule change is what would recover
them.**

For the great majority of the group **by headcount**, the music service named
almost nobody as similar — one or two artists, sometimes none. No cap rule and no
amount of further crawling invents that. **But see `STC-6`: "named almost nobody"
turns out to mean "named almost nobody above a cut-off we chose ourselves", which
is a different and more actionable statement.**

**`STC-3` — so "how big is the problem" has two right answers and they point
opposite ways.** By headcount the set is dominated by artists nobody could fix.
By *who you would actually meet*, it is dominated by artists a rule change would
fix. Both are in the report, adjacent, deliberately: quoting either alone
misleads, and I have written the summary so that neither can be lifted out on its
own.

**`STC-4` — the strongest thing that cuts against a rule change, and it is a real
one.** A natural next thought is "keep the connection if *either* artist names the
other" — the most permissive change available. Measured against that: the large
majority of this whole set is named by four artists or fewer, and around half by
exactly one. So even that change leaves most of them with a handful of
connections. It is only at the popular end that it makes a real difference, and
there it makes a large one — every artist in the set who would clearly benefit
sits in the top sliver by in-graph popularity. Figures: the report's `listed by`
tables.

**This is not a recommendation to make that change.** `mutual_knn` won a blind
listen, and `MKS-5b` records that dropping reciprocity restores unbounded degree,
which is the coupling any redesign has to answer. Nothing here is evidence for a
redesign; it is a measurement of what one would and would not reach.

## 3. Weakest link

**The boundary between "enough candidates" and "not enough" is my choice, and the
split moves if you move it.** It is anchored on the graph's own median degree —
an artist who could not reach the median even if every candidate were kept is not
a cap-rule problem — but that is a judgement, not a fact. **The report prints the
split at eleven different boundaries** so the choice can be overruled by reading a
different row, and two fixed points at the ends do not depend on it at all.

**The falsifier I named was run, and it half-fired.** `STC-1` rests on the gap
between what the source offers and what the crawl had, so a fetch-time truncation
would make a short list an artifact of collection rather than a fact about the
source. Both request parameters were checked against `BuilderConfig.algorithm`
and the archive: the **length limit cannot produce a short list** (it only
shortens long ones, and the pile-up is exactly where that predicts), so `STC-1`
survives it — but the **score threshold can and does**, which is `STC-6` and is
why the remedy table above changed.

What I would defend cheaply: `STC-4` and the popularity stratification —
straightforward counts over the artifact and the archive. What I would abandon on
one contrary measurement: `STC-1`'s *share*, though not its direction, since the
cap-stranded group is measured independently and does not depend on it.

## 4. What this does not establish

- **The causes are not exclusive**; every figure reports which one *binds*.
- **Nothing about whether a different rule is better.** No alternative rule was
  run. `listed by` counts one-directional candidates; it does not model any
  specific rule.
- **Nothing about path quality.** No path was routed and no cost weight was read.
- **The lists are not exhaustive.** They are the top by in-graph popularity, which
  ranks nothing (§2.11) and is used only to choose whose names to show — sound
  here because popularity is accumulated *before* the cap, so the reciprocity rule
  destroys degree and leaves popularity untouched.
- **Names are the graph's own**, so `CNS-1` applies: an artist stored under a
  different spelling appears under that spelling.

## 5. `STC-5` — a limitation found in the instrument, not in the finding

`reciprocity.py` (2026-07-25) models the builder's candidate population as the set
of archived responses. The builder additionally drops MusicBrainz special-purpose
placeholders before ranking. The model therefore ran with a population one member
too large, which can let a placeholder occupy a top-50 slot and push a real
candidate out.

**Corrected here** — this work imports the builder's own `is_special_purpose`
rather than reimplementing it, and runs the six-artist gate before *and* after the
correction. **It does not invalidate `findings/2026-07-25-mutual-knn-stranding.md`:**
the placeholders are a single-digit number of artists in 75,000, far too few to
move any distribution that document reports, and none of its six gated artists is
affected. It is recorded because **any future reuse of that model should apply the
same correction**, and because its own gate could not have caught it.

**Success condition:** if `reciprocity.py` is reused for any measurement whose
result depends on an individual artist's candidate list rather than on a
distribution, the exclusion must be applied first. Discharged by that reuse
applying it, or by the model being retired.

## 6. `STC-6` — "the source knows nothing" is not what SOURCE-THIN means

**This corrects a claim an earlier draft of this document made**, and it is
recorded rather than quietly fixed because the wrong version is the intuitive one
and will be re-derived by the next reader.

The source is queried with a fixed algorithm string, `BuilderConfig.algorithm`,
which carries two parameters **we chose**:

- a **length limit** — at most 100 similar artists per response. A large minority
  of all crawled artists return exactly that many, so it binds often. It **cannot**
  produce a short list, because truncation only shortens long ones. `STC-1` is
  therefore safe from it, and this was checked rather than assumed.
- a **score threshold** — pairs below a co-occurrence cut-off are not returned at
  all. This **does** produce short lists, and it is why a SOURCE-THIN artist is
  thin.

So SOURCE-THIN means "the source named almost nobody **above the threshold we
asked for**", not "the source knows nothing". **Re-crawling at a lower threshold
is inside this project's control**, which the remedy table in §1 originally denied.

**What is not established:** how many artists it would actually help, or whether
the extra edges would be good ones. It is a full re-crawl and the new edges rest
on weaker evidence by construction. **This is a named option with an unmeasured
payoff, not a proposal** — and the pause on path work is unaffected either way.

**Success condition:** if a re-crawl is ever considered for any reason, this
parameter is examined at the same time, because the crawl is the only moment it
can be changed. Discharged by that examination, or by a decision that the current
threshold is correct.

## 7. The residual, and why it was left

The modelled degree equals the artifact's own for all but ten of the measured
artists — the report has the exact counts. Two candidate causes were investigated
and **both are settled by measurement, not by argument**: the placeholder
exclusion above (which accounted for the majority of the original discrepancy),
and a difference in how rows carrying no similarity score are treated (which
**cannot** bite, because the archive contains no such row). `verify_residual.py`
reproduces both.

The remainder sit at the rank-50 boundary of a partner's candidate list. **They
were left there deliberately**, and the reasoning is the one in
`memory/stop-refining-instrumental-artifacts.md`: the split keys on the candidate
count, which is verified exactly for every artist measured, and every degree
quoted anywhere in the report is the artifact's own rather than the model's. A
tenth of a percent of rows, each off by one connection, cannot move any figure
reported. Chasing it further would be refining an instrument past the decision it
changes.

## 8. Nothing is proposed

There is no recommended action in this document, by instruction and on the
merits. `STC-4` measures the reach of a change nobody has proposed, and `STC-6`
names a parameter nobody has proposed changing. Both carry success conditions
rather than recommendations. The fetch-truncation check named in §3 as open was
**run before this document was committed**, and its result is `STC-6`.
