# Why the low-degree artists are low-degree - 2026-07-26

**Role: the measurement record for this directory. It owns every figure below;
cite this file, do not restate its numbers.** Read-only throughout: no rebuild,
no routing change, no adoption, nothing proposed.

Artifact: `graph-t15-tiebreakfix.bin`, sha256 `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`,
asserted before any figure was computed.

## The question

The census counted the artists the app can never introduce anyone to (one
connection) or can only reach down a single corridor (two). That set is
**12088** artists, and the ask was to separate two causes:

- **CAP-STRANDED** - the artist had a full list of candidates who *are* in the
  graph, and almost none of them ranked it back. The both-ways rule destroyed
  its connections, and a different rule would give them back.
- **CRAWL-FRONTIER** - the artist sits at the edge of the snowball crawl, so few
  of its candidates are in the graph at all. Its low degree would persist under
  any cap rule.

**The headline is that the second category, as phrased, is nearly empty** - and
what fills its place is a third cause that neither the crawl nor the cap rule
can address. The two-way split that was asked for is given first and in full,
then the refinement.

## Measured

Population: every artifact node with degree <= 2 - **12088** artists
(74193 nodes in the graph, 74993 in
the builder's candidate population after 7
placeholder entities are dropped).

Columns, throughout:

| column | meaning |
|---|---|
| **offered** | how many similar artists the source named for this artist at all |
| **usable** | how many of those were themselves crawled, so the builder could use them |
| **judged** | usable, capped to k = 50 - the list the both-ways rule judged |
| **back** | how many of them ranked this artist back - the modelled degree |
| **listed by** | how many artists list it, whether or not it lists them |

**`deg` is the artifact's own degree and `back` is the model's count of the same
thing.** They agree for all but ten artists (gate 4 below), so a row where they
differ is that residual showing, not a contradiction - `deg` is the authoritative
one.

`offered` vs `usable` is what separates a crawl problem from a source problem,
and `listed by` is what separates *stranded by the rule* from *beyond any
rule's reach*: an artist thirty others list is one a one-directional rule would
rescue; an artist only one other lists is not.

### How many candidates each artist actually had

| usable candidates | artists | share |
|---|---:|---:|
| 1-2 | 3641 | 30.1% |
| 3-5 | 2482 | 20.5% |
| 6-10 | 1474 | 12.2% |
| 11-20 | 1055 | 8.7% |
| 21-49 | 869 | 7.2% |
| 50+ (full list) | 2567 | 21.2% |

## The split that was asked for

**The boundary is my choice, and it is this: an artist is CRAWL-FRONTIER if the
builder had 10 usable candidates or fewer.**

The anchor is the graph's own median degree, which is 9. An
artist with 10 usable candidates or fewer could not reach that
median even under a rule that kept every single one, so for those the cap rule
is not the remedy. Above the line the artist had enough material to be
ordinarily connected, and the both-ways requirement is what took it away.

| population | artists | share |
|---|---:|---:|
| CRAWL-FRONTIER (usable <= 10) | 7597 | 62.8% |
| CAP-STRANDED (usable > 10) | 4491 | 37.2% |

**Because the boundary is a choice, here is every other choice.** Read this
before quoting the split: the two populations are a continuum.

| boundary | CRAWL-FRONTIER | CAP-STRANDED |
|---|---:|---:|
| usable <= 2 | 3641 (30.1%) | 8447 (69.9%) |
| usable <= 3 | 4808 (39.8%) | 7280 (60.2%) |
| usable <= 5 | 6123 (50.7%) | 5965 (49.3%) |
| usable <= 7 | 6894 (57.0%) | 5194 (43.0%) |
| usable <= 10 | 7597 (62.8%) | 4491 (37.2%) |
| usable <= 15 | 8270 (68.4%) | 3818 (31.6%) |
| usable <= 20 | 8652 (71.6%) | 3436 (28.4%) |
| usable <= 25 | 8926 (73.8%) | 3162 (26.2%) |
| usable <= 30 | 9095 (75.2%) | 2993 (24.8%) |
| usable <= 40 | 9357 (77.4%) | 2731 (22.6%) |
| usable <= 49 | 9521 (78.8%) | 2567 (21.2%) |

Two fixed points bound the table and neither depends on my choice:

- **3641 artists (30.1%) had two usable candidates or
  fewer.** They could not have exceeded degree 2 under *any* selection rule.
- **2567 artists (21.2%) had a full 50-candidate list.**
  Meat Loaf's case exactly.

## The refinement: cause (b) is not what it says it is

**CRAWL-FRONTIER as defined above conflates two situations that have nothing in
common.** Splitting it on whether the *source* had anything to offer:

| population | artists | share | what it means |
|---|---:|---:|---|
| CAP-STRANDED | 4491 | 37.2% | full candidate list, the rule discarded it |
| SOURCE-THIN | 7393 | 61.2% | the source named <= 10 similar artists in the first place |
| CRAWL-FRONTIER | 204 | 1.7% | the source named plenty; the crawl had not reached them |

**The crawl frontier explains 1.7% of the
set, not 62.8%.** For the artists below the line,
the median number offered by the source is
3 and the median usable is
3 - practically everything the
source named had already been crawled. The crawl did its job. The source simply
does not know much about these artists.

That matters because the three have different remedies: crawling further reaches
the smallest group, changing the cap rule reaches the middle one, and the
largest group is reached by neither.

### What SOURCE-THIN actually means - checked, because the obvious reading is wrong

The tempting conclusion is *the similarity source knows nothing about these
artists, and nothing in this project's control changes that*. **That is wrong,
and the check that shows it is cheap.** The source is queried with a fixed
algorithm string (`BuilderConfig.algorithm`) carrying two parameters we chose:

- **`limit_100`** - at most 100 similar artists per request. 39.1% of all 75,000
  crawled artists return exactly 100, so the limit binds for a large minority.
  **It cannot produce a short list**: truncation only shortens long ones to 100.
  So it does not touch this finding.
- **`threshold_10`** - pairs below a co-occurrence threshold are not returned at
  all. **This does produce short lists**, and it is the reason a SOURCE-THIN
  artist is thin.

So the accurate statement is **not** "the source has no data on these artists"
but "the source has no data on these artists *above the threshold we asked for*".
Re-crawling at a lower threshold is inside this project's control. What it would
yield has **not** been measured, and it would mean a full re-crawl plus edges
resting on weaker evidence - so this is a named option with an unmeasured payoff,
not a recommendation.

For completeness: 188 of the 75,000 archived responses are empty, and the longest
possible response is 100 by construction.

## What cuts against the cap-stranded share

The obvious reading of the cap-stranded number is *a different rule would give
those artists their connections back*. **The `listed by` column complicates
that, and it is why that column was measured.**

| listed by | artists | share |
|---|---:|---:|
| 1 artist | 5472 | 45.3% |
| 2-4 | 5485 | 45.4% |
| 5-9 | 710 | 5.9% |
| 10-29 | 360 | 3.0% |
| 30 or more | 61 | 0.5% |

**90.6% of the set is listed by four artists or fewer**, and
45.3% by exactly one. Even the most permissive change
available - keeping every one-directional candidate - would leave most of these
artists with a handful of connections at most.

A floor of zero is not reported because it cannot occur: a node with at least
one connection is necessarily listed by at least one artist, so `listed by` >=
degree >= 1 by construction, not by measurement.

### ...and what cuts back the other way

**Quoting the paragraph above on its own would mislead.** The causes are almost
perfectly stratified by popularity, so the small rescuable population is
precisely the one anyone would ever notice.

| band, by in-graph popularity | listed by, median | listed by >= 10 | cap-stranded |
|---|---:|---:|---:|
| top 50 | 51 | 48 (96%) | 98% |
| top 100 | 33 | 96 (96%) | 97% |
| top 500 | 12 | 345 (69%) | 99% |
| top 1000 | 8 | 418 (42%) | 99% |
| top 2000 | 5 | 421 (21%) | 98% |
| all 12088 | 2 | 421 (3%) | 37% |
| lowest 1200 | 1 | 0 (0%) | 7% |

**All 421 of the rescuable artists sit in the top 2000 by popularity**
(421 of 421), and 48 of the top 50 are rescuable. The
least popular 1200 contain **none** of them.

So the honest statement is both halves at once:

- **By count**, the set is dominated by artists the similarity source barely
  covers, and neither the crawl nor the cap rule addresses them.
- **By who anyone would recognise**, the set is dominated by artists with full
  candidate lists discarded by the both-ways rule, and a rule change is exactly
  what would reach them.

Which of those matters more depends on whether the goal is to fix a population
or to fix the artists a person actually meets. That is not a measurement
question and this document does not answer it.

## The lists

Ranked by in-graph popularity **to choose whose names to show, and for nothing
else** - popularity ranks nothing here (Phase 1 log 2.11). It is sound as a
screen only because popularity is accumulated *before* the cap, so the
reciprocity rule destroys degree and leaves popularity untouched.

### Top 50 CAP-STRANDED - the rule discarded these

Full candidate lists, almost none reciprocated. A different cap rule reaches these.

| # | artist | deg | offered | usable | judged | back | listed by |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Manu Chao | 2 | 100 | 100 | 50 | 2 | 321 |
| 2 | Nada Surf | 1 | 100 | 100 | 50 | 1 | 169 |
| 3 | Sparks | 2 | 100 | 96 | 50 | 2 | 184 |
| 4 | Calexico | 1 | 100 | 100 | 50 | 1 | 168 |
| 5 | Crowded House | 2 | 100 | 99 | 50 | 2 | 116 |
| 6 | Billy Bragg | 2 | 100 | 100 | 50 | 2 | 117 |
| 7 | t.A.T.u. | 1 | 100 | 100 | 50 | 1 | 82 |
| 8 | Guano Apes | 2 | 100 | 99 | 50 | 2 | 56 |
| 9 | ANOHNI and the Johnsons | 2 | 100 | 100 | 50 | 2 | 74 |
| 10 | Aloe Blacc | 2 | 100 | 100 | 50 | 2 | 77 |
| 11 | The Cult | 1 | 100 | 100 | 50 | 1 | 30 |
| 12 | Ailee | 1 | 100 | 100 | 50 | 1 | 65 |
| 13 | Nick Jonas | 2 | 100 | 99 | 50 | 2 | 35 |
| 14 | Dontcry | 2 | 100 | 99 | 50 | 2 | 30 |
| 15 | Django Django | 1 | 100 | 100 | 50 | 1 | 75 |
| 16 | Meat Loaf | 1 | 100 | 100 | 50 | 1 | 35 |
| 17 | Elbow | 1 | 100 | 100 | 50 | 1 | 44 |
| 18 | Tom Jones | 2 | 100 | 100 | 50 | 2 | 48 |
| 19 | Craig David | 1 | 100 | 100 | 50 | 1 | 65 |
| 20 | Charlotte Gainsbourg | 1 | 100 | 100 | 50 | 1 | 65 |
| 21 | Alabama Shakes | 2 | 100 | 100 | 50 | 2 | 53 |
| 22 | Kid Rock | 2 | 100 | 98 | 50 | 2 | 57 |
| 23 | Lucid Green | 2 | 100 | 96 | 50 | 2 | 12 |
| 24 | The Streets | 1 | 100 | 100 | 50 | 1 | 81 |
| 25 | Young Galaxy | 2 | 100 | 100 | 50 | 2 | 57 |
| 26 | Cheat Codes | 2 | 100 | 100 | 50 | 2 | 51 |
| 27 | C4C | 1 | 100 | 97 | 50 | 1 | 17 |
| 28 | trxxshed | 1 | 100 | 92 | 50 | 1 | 14 |
| 29 | Scissor Sisters | 1 | 100 | 100 | 50 | 1 | 45 |
| 30 | Daniel Johnston | 2 | 100 | 99 | 50 | 2 | 51 |
| 31 | Tinashe | 2 | 100 | 100 | 50 | 2 | 36 |
| 32 | Ella Henderson | 1 | 100 | 100 | 50 | 1 | 38 |
| 33 | The Sounds | 2 | 100 | 100 | 50 | 2 | 58 |
| 34 | Refeeld | 2 | 100 | 95 | 50 | 2 | 5 |
| 35 | Melodiesinfonie | 1 | 100 | 100 | 50 | 1 | 24 |
| 36 | Timber Timbre | 1 | 100 | 100 | 50 | 1 | 53 |
| 37 | GWAR | 1 | 100 | 96 | 50 | 1 | 30 |
| 38 | Hoffy Beats | 1 | 100 | 94 | 50 | 1 | 7 |
| 39 | The Cat Empire | 1 | 100 | 99 | 50 | 1 | 51 |
| 40 | Simian | 1 | 100 | 99 | 50 | 1 | 53 |
| 41 | Joe Cocker | 2 | 100 | 100 | 50 | 2 | 21 |
| 42 | School of Seven Bells | 2 | 100 | 100 | 50 | 2 | 42 |
| 43 | Lissie | 1 | 100 | 99 | 50 | 1 | 42 |
| 44 | Akira Yamaoka | 2 | 100 | 100 | 50 | 2 | 68 |
| 45 | Tokyo Police Club | 2 | 100 | 100 | 50 | 2 | 33 |
| 46 | The Guess Who | 2 | 100 | 100 | 50 | 2 | 15 |
| 47 | Katrina and the Waves | 1 | 100 | 99 | 50 | 1 | 23 |
| 48 | DeVotchKa | 2 | 100 | 100 | 50 | 2 | 42 |
| 49 | Echosmith | 1 | 100 | 100 | 50 | 1 | 16 |
| 50 | The B‐52s | 2 | 100 | 100 | 50 | 2 | 18 |

### Top 50 CRAWL-FRONTIER - the crawl had not reached these

The source named more than 10 similar artists but few were crawled. Only 204 artists are in this group at all.

| # | artist | deg | offered | usable | judged | back | listed by |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | Susie Ledge | 2 | 12 | 10 | 10 | 2 | 10 |
| 2 | María Conchita Alonso | 1 | 16 | 10 | 10 | 1 | 5 |
| 3 | West Point Band | 2 | 14 | 10 | 10 | 2 | 2 |
| 4 | Electronic Visions | 2 | 11 | 10 | 10 | 2 | 2 |
| 5 | Supire | 2 | 17 | 9 | 9 | 2 | 4 |
| 6 | Gentry Ice | 2 | 13 | 8 | 8 | 2 | 2 |
| 7 | LAUR | 2 | 11 | 10 | 10 | 2 | 2 |
| 8 | Boogrov | 2 | 12 | 8 | 8 | 2 | 2 |
| 9 | Menog | 2 | 14 | 10 | 10 | 2 | 2 |
| 10 | リツカ | 2 | 11 | 8 | 8 | 2 | 2 |
| 11 | Bongo Chilli | 2 | 12 | 5 | 5 | 2 | 2 |
| 12 | Mush | 2 | 12 | 10 | 10 | 2 | 2 |
| 13 | Talamanca | 2 | 12 | 9 | 9 | 2 | 2 |
| 14 | Sound Online | 2 | 11 | 10 | 10 | 2 | 2 |
| 15 | DrumTalk | 2 | 13 | 8 | 8 | 2 | 2 |
| 16 | Lewis McCallum | 2 | 15 | 7 | 7 | 2 | 2 |
| 17 | Patti Murin | 2 | 16 | 10 | 10 | 2 | 2 |
| 18 | マリア・カデンツァヴナ・イヴ | 2 | 13 | 10 | 10 | 2 | 2 |
| 19 | Rosie Gaines | 1 | 11 | 7 | 7 | 1 | 1 |
| 20 | Sierpien | 1 | 12 | 10 | 10 | 1 | 1 |
| 21 | Doug Johns | 2 | 15 | 10 | 10 | 2 | 2 |
| 22 | Bishop Morocco | 2 | 11 | 6 | 6 | 2 | 2 |
| 23 | Sophie Holt | 2 | 11 | 6 | 6 | 2 | 2 |
| 24 | Dil Withers | 2 | 11 | 9 | 9 | 2 | 2 |
| 25 | Libra | 1 | 11 | 10 | 10 | 1 | 1 |
| 26 | K-Alexi | 2 | 11 | 5 | 5 | 2 | 2 |
| 27 | Jace | 2 | 11 | 10 | 10 | 2 | 2 |
| 28 | Charles Xavier | 2 | 13 | 10 | 10 | 3 | 3 |
| 29 | Alfie Boe | 2 | 11 | 8 | 8 | 2 | 2 |
| 30 | Catfish Haven | 2 | 12 | 8 | 8 | 2 | 2 |
| 31 | The Nines | 1 | 21 | 10 | 10 | 1 | 1 |
| 32 | Matt Adey | 2 | 12 | 10 | 10 | 2 | 2 |
| 33 | Paolo Mojo | 2 | 13 | 7 | 7 | 2 | 2 |
| 34 | Kuryakin | 2 | 23 | 4 | 4 | 2 | 2 |
| 35 | Supreme Team | 1 | 11 | 10 | 10 | 1 | 1 |
| 36 | Maiya James | 1 | 11 | 10 | 10 | 1 | 1 |
| 37 | Klaus Veen | 2 | 16 | 9 | 9 | 2 | 2 |
| 38 | Laurence Rosenthal | 2 | 11 | 10 | 10 | 2 | 2 |
| 39 | Chong the Nomad | 2 | 13 | 9 | 9 | 2 | 2 |
| 40 | Beat Assassins | 1 | 13 | 10 | 10 | 1 | 1 |
| 41 | Marc Hartman | 2 | 17 | 7 | 7 | 2 | 2 |
| 42 | Qari | 2 | 12 | 10 | 10 | 2 | 2 |
| 43 | Miou Amadée | 2 | 12 | 8 | 8 | 2 | 2 |
| 44 | Diakof | 2 | 15 | 5 | 5 | 2 | 2 |
| 45 | Mr. M. & M | 2 | 11 | 6 | 6 | 2 | 2 |
| 46 | Sidney Barnes | 2 | 11 | 10 | 10 | 2 | 2 |
| 47 | Ashley Thomas | 1 | 14 | 9 | 9 | 1 | 1 |
| 48 | Gargantuan Music | 2 | 11 | 10 | 10 | 2 | 2 |
| 49 | Kelly James Wyse | 2 | 11 | 10 | 10 | 2 | 2 |
| 50 | Евгений Королёв | 1 | 11 | 8 | 8 | 1 | 1 |

### Top 50 SOURCE-THIN - the source barely knows these

Nothing in this project's control changes these: the similarity data itself is thin.

| # | artist | deg | offered | usable | judged | back | listed by |
|---:|---|---:|---:|---:|---:|---:|---:|
| 1 | IHF | 2 | 2 | 2 | 2 | 2 | 68 |
| 2 | Ichika Nito | 1 | 1 | 1 | 1 | 1 | 49 |
| 3 | Puzzle | 1 | 3 | 3 | 3 | 3 | 37 |
| 4 | MysDiggi | 2 | 5 | 5 | 5 | 2 | 27 |
| 5 | Noc.V | 2 | 8 | 8 | 8 | 2 | 9 |
| 6 | Сивый Яр | 1 | 1 | 1 | 1 | 1 | 12 |
| 7 | Os Ipanemas | 2 | 10 | 8 | 8 | 3 | 16 |
| 8 | DJ Daddy | 1 | 1 | 1 | 1 | 1 | 11 |
| 9 | Les Quatre Étoiles | 1 | 1 | 1 | 1 | 1 | 16 |
| 10 | Eric Bloom | 1 | 3 | 3 | 3 | 1 | 8 |
| 11 | Spira me | 1 | 6 | 6 | 6 | 1 | 10 |
| 12 | T.Nava | 2 | 2 | 2 | 2 | 2 | 5 |
| 13 | Oak | 2 | 6 | 6 | 6 | 2 | 4 |
| 14 | ManMan Savage | 2 | 6 | 6 | 6 | 2 | 7 |
| 15 | Muph | 1 | 3 | 3 | 3 | 1 | 7 |
| 16 | The TnT Boys | 2 | 10 | 6 | 6 | 2 | 3 |
| 17 | DR€W ¥ORK | 1 | 2 | 2 | 2 | 1 | 6 |
| 18 | Solo 45 | 2 | 9 | 8 | 8 | 2 | 2 |
| 19 | Mickey Petralia | 1 | 10 | 10 | 10 | 1 | 1 |
| 20 | S-TRO | 2 | 8 | 8 | 8 | 2 | 2 |
| 21 | 5 Step Sound Team | 2 | 9 | 9 | 9 | 2 | 2 |
| 22 | Noyes | 2 | 9 | 8 | 8 | 2 | 2 |
| 23 | Aya Peard | 2 | 7 | 7 | 7 | 2 | 2 |
| 24 | Mark Josher | 2 | 10 | 10 | 10 | 2 | 2 |
| 25 | Tim Larkin | 2 | 8 | 8 | 8 | 2 | 2 |
| 26 | Coughee Brothaz | 1 | 2 | 2 | 2 | 1 | 6 |
| 27 | Timaya | 2 | 7 | 7 | 7 | 2 | 2 |
| 28 | 大島保克 | 2 | 9 | 9 | 9 | 2 | 2 |
| 29 | Larkin | 1 | 10 | 10 | 10 | 1 | 1 |
| 30 | Silas Green | 2 | 8 | 8 | 8 | 2 | 2 |
| 31 | Aceilux | 2 | 10 | 10 | 10 | 2 | 2 |
| 32 | Dean Garcia | 2 | 10 | 8 | 8 | 2 | 2 |
| 33 | Pastor Brady Blade, Sr. | 2 | 7 | 7 | 7 | 2 | 2 |
| 34 | Ansiktet | 2 | 8 | 8 | 8 | 2 | 2 |
| 35 | David Myles | 2 | 8 | 8 | 8 | 2 | 2 |
| 36 | rouri404 | 2 | 10 | 10 | 10 | 2 | 2 |
| 37 | Lauren Edman | 2 | 10 | 10 | 10 | 2 | 2 |
| 38 | ロフト tapes | 2 | 10 | 10 | 10 | 2 | 2 |
| 39 | 김창훈 | 1 | 9 | 9 | 9 | 1 | 1 |
| 40 | Popa Wu | 2 | 6 | 6 | 6 | 2 | 2 |
| 41 | The Chromatics | 2 | 5 | 5 | 5 | 2 | 2 |
| 42 | The Werks | 2 | 7 | 6 | 6 | 2 | 2 |
| 43 | 鈴木ななこ | 2 | 7 | 7 | 7 | 2 | 2 |
| 44 | Downtown Binary | 2 | 8 | 8 | 8 | 2 | 2 |
| 45 | Mike Lesirge | 2 | 7 | 5 | 5 | 2 | 2 |
| 46 | Micah Gaugh | 1 | 2 | 2 | 2 | 1 | 4 |
| 47 | Tia Thomas | 2 | 8 | 8 | 8 | 2 | 2 |
| 48 | Max Bruch | 2 | 9 | 9 | 9 | 2 | 2 |
| 49 | やなわらばー | 1 | 8 | 8 | 8 | 1 | 1 |
| 50 | Falco Lombardi | 2 | 9 | 9 | 9 | 2 | 2 |

## What this does not establish

- **The causes are not exclusive, and the split reports which one binds.** An
  artist with 15 usable candidates and one connection lost fourteen to the rule
  *and* had a thin list. Every figure is about the binding constraint.
- **It says nothing about whether a different rule would be better.**
  `mutual_knn` won a blind listen, and dropping reciprocity restores unbounded
  degree (`MKS-5b`). Nothing here is evidence for a redesign.
- **`listed by` is not a promise.** It counts one-directional candidates; it does
  not model any specific alternative rule, and no alternative rule was run.
- **The names are the graph's own**, so an artist stored under a different
  spelling appears under that spelling (`CNS-1`).

## Gates, and the one residual

1. The artifact sha256 is asserted before any figure is computed.
2. The 2026-07-25 candidate model's own gate - six artists whose predicted
   neighbour sets must match the shipped graph - runs **twice**: unmodified, and
   again after the builder's placeholder exclusion is applied.
3. The uncapped candidate count is consistent with the capped list for **all
   12088** artists: 0 mismatches. This is the gate that matters most, because
   the candidate count is what the split keys on.
4. The modelled degree equals the artifact's own degree for **12078 of 12088**.

**The residual is 10 artists (0.08%), each off by one
connection.** Two candidate causes were investigated and both are settled: the
builder drops MusicBrainz placeholder entities before ranking and the 2026-07-25
model did not (**fixed here - it accounted for 7 of the original 17**), and the
builder drops rows carrying no similarity score while that model keeps them as
zero (**measured: there are no such rows in the archive, 0 of 4,234,499**). The
remaining ten sit at the rank-50 boundary of a partner's list. They were left
there deliberately: the split keys on the candidate count, which gate 3 verifies
exactly, and every degree quoted here is the artifact's own, not the model's.

