# What the reference product actually does — a source review of BoilTheFrog

**Role: AUTHORITATIVE for its own interpretation; OWNS NO FIGURES.** Every quantity belongs
to `../../../builder/analysis/2026-07-27-boilthefrog-reconstruction/REPORT.md`, whose
sections are cited as §(a)–§(i). **Cite that report for any number.**

**Read-only. Nothing is adopted, proposed, pre-registered or rebuilt; no threshold is set,
no arm is designed, no config was touched. Path-quality work is paused by owner decision and
this document is not a resume signal.** Resuming is the owner's trigger.

Identifiers are namespaced **`BTF-n`** — verified unused across the repository before
allocation. Nothing committed is renamed or renumbered.

**Subject.** `github.com/plamere/BoilTheFrog` at `1f2cb60`, plus the author's two writeups
([2012](https://musicmachinery.com/2012/02/26/boil-the-frog/),
[2013](https://musicmachinery.com/2013/01/02/boil-the-frog-2/)). BoilTheFrog is named as the
reference product in `../WHAT-GOOD-LOOKS-LIKE.md` values 2 and 9. It is **EXTERNAL** material
in `docs/README.md`'s sense — this document is ours; the code it describes is not.

**Why this was worth doing.** Value 9 carried an explicit standing caveat — *"His
characterisation of boilthefrog; not independently verified against the article"* — and the
reference is invoked in two of the nine calibration values. It had never been read.

---

## 1. The finding that matters most

### `BTF-1` — the famous artists are near-leaves, and that is what makes fame track the endpoints

*(Plain: in BoilTheFrog, Ed Sheeran is connected to four artists. Drake is connected to four.
The app therefore cannot route you through them unless you asked for them — there is almost
nothing to route through.)*

§(c). The most popular artists in BoilTheFrog's graph sit **at or below the graph's mean
degree**, several with an in-degree of zero. The correlation between popularity and degree is
weakly positive, and the most-connected artists are **mid-popularity** — session musicians,
orchestras, musical-theatre performers — not the famous ones.

The mechanism is one design decision. Each artist keeps only its **four** neighbours closest
to it **in popularity** (§(d) variant A). A pop-100 artist can therefore only be chosen by
other pop-100 artists, and there are very few of those, so the "everyone points at The
Beatles" in-degree accumulation cannot occur.

**This is the structural half of value 9, and it was not previously known.** Value 9 records
that fame tracked the endpoints and attributes it to the router. §(g) shows the router term
exists — but §(c) shows the *graph* is doing at least as much work: famous artists are
structurally almost unusable as intermediate stops.

**Contrast with artistpath, stated carefully.** These are **different currencies** and the
comparison is qualitative only: BoilTheFrog's `popularity` is Spotify's 0–100 figure;
artistpath's `pop_raw` is score-weighted in-degree, log-scaled (`CLAUDE.md`, "Popularity =
score-weighted in-degree"). Phase 1 log §2.11 is explicit that neither is fame. What can be
said without a currency claim is structural: in artistpath the very famous hold **many**
connections (`MKS-5` records the Beatles holding the full 50), and the router climbs toward
popular artists far more often than the graph's own edges do (`ASC-1`). In BoilTheFrog there
is no comparable ascent available, because the destination of such a climb has degree 4.

---

## 2. The two values that name BoilTheFrog

### `BTF-2` — value 9's first clause is CONFIRMED, from primary sources and by measurement

*(Plain: the owner remembered correctly that in BoilTheFrog two famous artists gave a famous
path and two obscure ones gave an obscure path.)*

Three independent confirmations, and the caveat in value 9 can be lifted on this clause:

1. **The author's design statement**, in the app's own "How does it really work?" text
   (`new-web/index.html:171-174`) and repeated in both blog posts: *"priority is given to
   paths that travel through artists of similar popularity. If you start and end with a
   popular artist, you are more likely to find a path that takes you though other popular
   artists, and if you start with a long-tail artist you will likely find a path through
   other long-tail artists."*
2. **The code**: the entire edge weight is `1 + |Δpopularity|` (§(g)).
3. **Measurement**: §(e), interior popularity tracks the endpoint band across four pairs.

> **And the author's stated *purpose* for the term cuts directly against this project's
> goal.** The 2013 post says the popularity weighting stops paths that
> *"venture into back alleys that no music fan should dare to tread."* **The term artistpath
> shares with BoilTheFrog (`w_jump`) was designed to suppress obscurity.** artistpath now
> asks a near-identical term to permit obscurity on demand. That is not an argument that
> `w_jump` is wrong — value 9 says endpoint-tracking is *wanted* — but the provenance is
> worth knowing before anyone reprices it.

### `BTF-3` — value 2's second clause is NOT supported by the reference product it names

*(Plain: value 2 says each bypass press should make the path both longer and more full of
artists you don't know, and names BoilTheFrog as the product that did this. BoilTheFrog does
not do it. Pressing bypass there re-routes locally, then stops changing anything.)*

§(e). Simulated over twelve presses per pair: paths lengthen barely or not at all (9 → 10,
14 → 14), interior popularity drifts down slightly and **non-monotonically** — one pair rose
before falling and ended exactly where it started — and three of four pairs reach a **fixed
point**, returning an identical path for every subsequent press.

The cause is visible in the code and needs no measurement. BoilTheFrog's bypass is a
**single-signal, node-local soft penalty** with no radius and, decisively, **no relaxation of
any popularity term**. The router re-routes around the excluded artist *at the same
popularity level*, because nothing in the cost function has changed. Once it has found a
stable detour, further presses on artists off that detour do nothing.

**What this does and does not license.**

- It does **not** make value 2 wrong. Value 2 is the owner's preference; preferences do not
  need precedent, and `WHAT-GOOD-LOOKS-LIKE.md` says in terms that it records preference and
  not evidence. Value 2 also already carries its own honest flag — *"the owner flagged it
  himself as gut instinct rather than data-driven."*
- It **does** mean value 2 cannot be justified by appeal to BoilTheFrog, and that the
  sentence *"Reference product: boilthefrog"* is doing work it cannot bear.
- It means artistpath's **two-signal bypass is genuinely novel**, not a re-implementation.
  The reference product has one signal and no depth-graduated device whatsoever. Whatever is
  wrong with `dislike` and `known`, it is not that a working precedent was mis-copied.

**Weakest link, and I would abandon this cheaply:** the press model. `known-like` bypasses
the most *popular* interior artist as a proxy for the most *recognised* one, which
Phase 1 log §2.11 says is not the same thing. Both press models nonetheless show the same
saturation, and the reconstruction reaches obscurity **more** easily than the real app did
(§(a)), so the direction is conservative. What would falsify it: a press policy under which
the ladder does not saturate.

> **This is an inference about the reference, not about artistpath's own bypass.** No
> artistpath path was routed for this document. `BYP-3` and `BYP-9` are the record of what
> artistpath's bypass does, and nothing here re-reads them.

---

## 3. The graph-construction question the resume brief is blocked on

### `BTF-4` — a reciprocity-free, degree-bounded graph exists — but it does not answer `SYN-6`

*(Plain: BoilTheFrog never requires two artists to name each other, and its graph still has
no giant hubs. That is exactly the combination we were told nobody has built. It turns out
its data could not have produced giant hubs in the first place, so it does not settle our
question.)*

`SYN-6` states that separating *reciprocity* from *bounded degree* "needs a `cap_strategy`
that does not exist", and that no artifact has ever been built which a listener could use to
tell them apart. BoilTheFrog applies **no reciprocity test at all** and is nonetheless tightly
degree-bounded (§(b)) — so it presents as the missing strategy.

**It is not, and the factor table is what shows why.** §(d): even with the cap removed
entirely, BoilTheFrog's max degree stays small, because its source returns **at most twenty**
candidates per artist (§(a)). The regime `MKS-5b` and Phase 1 log §2.10 are about —
where dropping the both-ways rule *restores unbounded degree* — **cannot arise in
BoilTheFrog's data**. Its bounding is a property of the source, not a demonstration of a rule.

**So `MKS-5b` stands entirely unanswered, and this document does not weaken it.** A short
source list is not a cap strategy artistpath can adopt.

**What does survive, and it is a genuinely new option.** §(d)'s A-vs-B contrast differs by
exactly one column — the **selection criterion** at a fixed cap. Choosing each artist's
neighbours by *popularity proximity* rather than by *similarity rank* **halves the maximum
degree and reduces the ≤ 2-connection share by about a third**, on identical crawl data, with
no reciprocity test in either arm. The two criteria share under a fifth of their edges (§(i)).

**Why that is worth recording during a pause.** The resume brief's §1 decision is framed as
*build a bounded degree floor, or not*, with *do nothing* as the alternative. This is a
**third option that neither the brief nor `SYN-1`'s three-cause table contains**: change what
the cap *selects* rather than how many it keeps or who it rescues. It is builder-side, it
needs no new data, and — unlike the degree floor — it attacks stranding and hub degree with
the same knob.

**Four things it is not.** It is **not a proposal**; nothing is pre-registered and the pause
is intact. It is **not evidence it would work on artistpath's graph** — different source,
different list lengths, different similarity semantics, and artistpath's popularity is a
different currency from Spotify's. It does **not** answer the resume brief's §2 blocker
(arithmetic vs pricing), which no measurement here touches. And it would be a **rebuild**,
which is the owner's call and is currently blocked behind the nameless-artist decision.

### `BTF-5` — the reference product strands artists too, and roughly as often

*(Plain: about one in ten artists in BoilTheFrog's graph has two connections or fewer —
similar to ours. The difference is who they are: theirs are all at the very bottom of the
popularity range, ours include artists people have heard of.)*

§(b) and §(c). The headline share of ≤ 2-connection artists is broadly comparable to what
`MKS-3` records for artistpath, which was not what I expected before measuring. **The
distributions are what differ.** In BoilTheFrog, stranding is concentrated almost entirely in
the lowest popularity band and is essentially absent above it. In artistpath, `SYN-2` and
`STC-3` record the opposite shape — a minority cause by headcount, but the dominant cause
among artists a listener would recognise, which is the whole reason the stranding work
happened.

**So "BoilTheFrog did not strand artists" would be false, and worth not saying.** What it did
was strand only artists at the edge of its membership cut. `STC-3`'s reading rule — that
neither the headcount half nor the recognisability half may be quoted alone — applies here as
well.

**Caveat that bites this item specifically:** the omitted `skip_artists_with_no_tracks` filter
(§(a)) would have removed nodes predominantly from that bottom band, so BoilTheFrog's true
stranding share is **lower** than the reconstruction's, and this item understates the
contrast.

---

## 4. Two items outside path work

### `BTF-6` — the clip-identity defect class is structurally absent from the reference

*(Plain: `BYP-13` — a card playing a song by a different artist with the same name — cannot
happen in BoilTheFrog, because it asks for tracks by artist ID rather than by name.)*

§(h). BoilTheFrog's graph is keyed on Spotify artist IDs and its clips are fetched with
`spotify.artist_top_tracks(artist['id'])` — **the same identifier space**. artistpath's
resolver takes `(mbid, artist_name)` and searches Deezer and then iTunes **by name string**
(`api/src/artistpath_api/clips.py:186,236-273`), so the graph's identity and the clip
source's identity are joined on a human-readable label.

**That join is the root of the class**, not the particular collision. `BYP-13` (FERG /
A$AP Ferg) and C1's original band-name/song-title case are two symptoms of it. `clips.py:42`
already carries a belongs-to check for C1, which is a mitigation of the join rather than a
removal of it.

**Not a recommendation.** BoilTheFrog had a single-vendor catalogue that supplied similarity,
identity and audio together; artistpath deliberately does not, and the ListenBrainz probe
(`2026-07-19-listenbrainz-probe.md` §6d–6f) records why importing an outside catalogue
wholesale was eliminated. Recorded so that `BYP-13` is understood as **structural and
bounded**, not as a bug that a better name-matcher closes.

### `BTF-7` — `de_norm` is a ready-made answer to `CNS-1`

*(Plain: the Pretenders problem — an artist being unfindable under the name users know it by
— has a twenty-line solution in the original.)*

§(h). `search.py::de_norm` normalises identically at index time and at query time, and among
other things **strips a leading "the "**. `CNS-1` records exactly this failure ("Pretenders"
stored, "The Pretenders" typed). It also handles accents, apostrophes and periods, and `&`
versus "and" — its own test list is `N'sync`, `D'Angelo`, `R. Kelly`, `Beyoncé`,
`Emerson, Lake & Palmer`.

**Search-side only, and that is the point:** it needs no alias data, no rebuild, and no graph
change, so it sits **outside** the path-quality pause and outside the rebuild block. Whether
it fits artistpath's search is unexamined here — `api/src/artistpath_api/search.py` was not
read for this document, and a normaliser that collapses too aggressively creates collisions
of its own, which is `BTF-6`'s hazard in a different place.

---

## 5. A method note, because it is the fourth instance

### `BTF-8` — the reference product's headline mechanism never ran

*(Plain: BoilTheFrog's own description says it chooses each artist's song so consecutive
songs have similar energy. That code was never switched on, and in the Spotify era the energy
value it needed was a constant.)*

§(f). Defined in all three front-ends; **commented out** in one and **never called** in the
other two. What ships is a random pick among the artist's top tracks. Independently, the
Spotify-era crawler wrote a hardcoded `0.5` for every track's energy and the 2018–20 pipeline
never stored the field at all — so it would have been a no-op had it been called.

**Two consequences.**

- **It removes a candidate explanation for why BoilTheFrog felt good.** Whatever produced the
  "seamless" quality the owner remembers, it was not track-level energy smoothing. That
  narrows the credit to graph construction (`BTF-1`) and the popularity-continuity term
  (`BTF-2`) — the two things this document can evidence.
- **It is the same defect class this project keeps finding**, in a shipped product with a
  large audience, undetected for six years: a mechanism that is documented, believed, and
  inert. `FMS-P1`, `TR-2`, `TKB-4` and the `DEP-33` review's ten green mutations are the
  in-project instances.

**And this document reproduced it while writing about it.** §(d)'s factor table contains a
vacuous cell — two variants that are byte-identical by construction, so their comparison is
not a null result but not a comparison at all. It was caught by **running** the table and
seeing two identical columns, not by review, which is the same way `TKD-2` and `TKA-1` were
caught. The cell is recorded in §(d) rather than deleted.

---

## 6. What this does not establish

- **Nothing about whether artistpath should change.** No artistpath weight, graph or config
  was touched or evaluated. No arm was designed and nothing is pre-registered.
- **Nothing that settles the resume brief's §2 blocker.** Arithmetic-versus-pricing is
  untouched; `BTF-4` is about graph construction, which is upstream of that question.
- **Nothing at listening-verdict strength.** No path was heard. Every quality claim about
  BoilTheFrog here is structural or measured, never aesthetic.
- **No claim that BoilTheFrog is better.** It is a different product with a different goal —
  §(g)'s missing similarity term and `BTF-2`'s "back alleys" quote both point at a router
  built to *avoid* the thing artistpath exists to deliver.
- **No currency equivalence.** Spotify popularity and artistpath's `pop_raw` are not the same
  quantity and no figure was carried across.

## 7. Calibration — which item I expect to be wrong

**`BTF-3` is the most likely of these to be overturned**, and the reason is its instrument
rather than its data. The press policy is a simulation of a human click. If a real user's
bypass choices differ from "most popular interior artist" and from "uniformly random" in some
structured way — and value 5 suggests they do, since users press `known` on artists they
personally recognise — the ladder might not saturate as it does here.

**What would falsify it:** a press policy under which interior popularity keeps descending
past twelve presses without reaching a fixed point.

**What I would defend cheaply:** `BTF-1` and `BTF-2`. Both are arithmetic over the original's
committed data plus the author's own stated design, and neither depends on a press model or a
fame proxy. **What I would abandon on one contrary measurement:** `BTF-3`'s saturation claim,
and `BTF-5`'s comparability claim, which leans on a share measured under a filter I could not
reproduce.

**One thing I got wrong along the way, recorded because the correction is the useful part.**
I first read `BTF-4` as a demonstration that reciprocity-free degree bounding *works*, which
would have contradicted `MKS-5b` on the strength of an external graph. The factor table
refuted it: removing the cap entirely barely moves the maximum degree, because the source list
is short. The strong reading survived until the control was run, and the control was cheap.

---

*Figures: `../../../builder/analysis/2026-07-27-boilthefrog-reconstruction/REPORT.md`. This
document owns none and supersedes nothing. Nothing adopted; the pause is intact.*
