# Launch UX scope — four features, scoped and undesigned

**Role: ACTIVE — the governing scope document for the `LUX-` set.** Identifiers **`LUX-`**
(features `LUX-1`–`LUX-4`, evals `LUX-E1`–`LUX-E6`), collision-checked across every ref
2026-09-03 — `LUX`, `PUB`, `UXL`, `CLP`, `INF`, `RHP`, `SDL`, `BYX` all free; `ACL` taken.

**This is a SCOPE document, not a pre-registration and not an implementation plan.** No
experiment has run, nothing is adopted, no default is changed, no code is written. It
records four owner decisions taken 2026-09-03 in a brainstorming session, what the repo
already contains that bears on each, and the evals a future session owes **before** the
decision each eval gates. A session picking this up writes the plan; it does not inherit one.

**It owns no figures.** Coverage figures are cited from
`builder/analysis/2026-08-02-dsp-ids/` (`dsp_ids.json`, `delivered_coverage.json`) and
`findings/2026-07-31-release-tag-coverage.md`, each of which owns its own. Scoring figures
stay in `findings/2026-07-21-scoring-adjudication.md`. Nothing here restates any of them.

---

## §0 Why this exists, and what the owner decided

The domain `unsung.fm` was cut over 2026-09-03 and public sharing (Reddit, LinkedIn) is now
in view. The owner opened a brainstorming session on **user experience only** — explicitly
not the technical side of launching — and took four decisions. Each is recorded below with
the reasoning that produced it, because none of it survives in a diff.

**The decisions are his and are made.** What is open is design, sequencing, and the evals.

| | Decision, 2026-09-03 |
|---|---|
| `LUX-1` | **Remove the `dislike` bypass button.** Keep the mechanism and the wire contract. |
| `LUX-2` | **Build the route history panel.** Frontend first, then move the bypassed artists onto the path response. |
| `LUX-3` | **Let a user try a different clip by the same artist.** Index parameter, candidate list in the cache. |
| `LUX-4` | **Streaming links from MusicBrainz relations, in the artifact, with search links as the fallback** — plus an artist info card built from **structured MusicBrainz fields only**. Genre tags deferred. A prose description is **dropped, not deferred.** |

---

## §1 `LUX-1` — remove the "Steer away" button

### The decision

Ship one bypass button. `dislike` disappears from the UI. **The router, the wire contract
and the `?dislike=` URL parameter all stay**, so links already shared keep resolving and the
change is one commit to reverse.

### Why

The owner's stated reason: two buttons — "Steer away" and "Dig deeper" — are confusing, and
the app's purpose is finding less well-known artists, which is what `known` is for.

The repo agrees that this control is hard to word. `2026-08-07-bypass-tray-ux-execution-log.md`
§2.1 records the previous round: the supplied design said "Not this step", the owner objected,
and the design's **own** annotation named "Rebuild from here" *"the strongest cure for the swap
misread"*. This is the second wording crisis on the same control.

### What is actually lost, stated plainly

`dislike` is the only device in the app that moves a path **sideways** — away from a region of
the similarity graph. It is the sum of three things in
`api/src/artistpath_api/pathfinding.py`:

- `avoidance_map()` — a soft penalty on the bypassed artist's neighbours, decaying by hop
  (`avoid_penalty`, `avoid_decay`, `avoid_radius` in `ApiConfig`, priced by `w_avoid`).
  **Nothing else produces lateral movement.**
- a weaker obscurity-floor relaxation than `known` (`floor_relax_dislike` vs
  `floor_relax_known`, both in `ApiConfig`, applied in `effective_floor_raw()`).
- **no** fame ramp — `w_known_ramp_fame_pctl` is multiplied by the `known` count only.

`known` by design routes to a **highly similar and more obscure** artist (`REQ-27`). So after
this change, a user who means *"I don't like this"* and presses the one remaining button gets
**more of the same corner, less famous**. That is the one real cost, it was stated to the
owner, and he took the decision with it in view.

**The mitigating fact:** nobody has ever pressed these buttons except the owner. There is no
usage evidence either way, and there cannot be before launch. Shipping the simple control and
restoring the second one on demand is the reversible order; shipping two and removing one
after people have learned them is not.

### What changes

| File | Change |
|---|---|
| `frontend/src/components/ArtistCard.tsx` | Drop the `dislike` button (~line 162). |
| `frontend/src/components/PathIntro.tsx` | Drop the "Steer away" paragraph; re-word the surviving one. |
| `frontend/src/components/RerollNotice.tsx` | Drop the `dislike` notice string. Its comment explains the notices are accurate to the router — keep that true. |
| `frontend/src/lib/exclusions.ts` | **No change.** `decodeExclusions` must keep reading `?dislike=`. |
| `api/` | **No change.** |

**Estimate: an afternoon**, frontend only. A session's judgement, not a measurement.

### The copy carries more weight than it did

With one button, its label is the whole explanation of what bypass does. It must not read as
"I don't like this" — that is the intent the surviving mechanism serves worst. Wording is the
owner's; `PathIntro.tsx`'s existing text is the starting point, not a constraint.

---

## §2 `LUX-2` — the route history panel

### The decision

Build the panel from the owner's mockup: one row per press, most recent first, "Original
route" at the bottom, and the caption that Back undoes any of it. **`LUX-2a` frontend-only
first, then `LUX-2b`** moving the bypassed artists onto the path response.

### Why it is cheap, and why `LUX-1` makes it cheaper

Three of the four things the panel needs already exist:

- **Back already works.** `PathPage.go()` calls `navigate()` without `replace`, so every press
  pushes a history entry. The mockup's caption is true as written today.
- **"Original route"** is the base URL with no exclusion parameters.
- **The press list** is in the URL.

The obstacle is that `frontend/src/lib/exclusions.ts` encodes exclusions as **two** comma
lists — `?dislike=…&known=…`. Order is preserved *within* a list and **lost across them**, so
today's URL cannot reconstruct the interleaved chronology the mockup draws.

**`LUX-1` dissolves this.** With one signal there is one list, and `addExclusion` already
appends in press order. No URL change, no contract change, no legacy decode path.

> ⚠ **If `LUX-1` is ever reversed, this panel needs a single ordered URL parameter**
> (`?via=k:MBID,d:MBID,…`) with the two-list form still decoded for old links. The API needs
> no change either way: `PathRequest.exclude` is already an ordered array and the router is
> order-independent (`avoidance_map` takes a max; the ramp takes a count).

### The missing piece: names

A bypassed artist is hard-excluded, so they are **absent from the path response**. The panel
needs their names.

- **`LUX-2a`** — one call per bypassed artist to the existing `GET /api/artists/{mbid}`
  (`app.py`, returns `ArtistOut`). No API change. Works on a cold load of a shared link.
- **`LUX-2b`** — add the bypassed artists to `PathResponse`. `_to_exclusions()` in `app.py`
  already resolves each MBID to a node, so this is a few lines. Saves the round trips and
  gives the not-in-graph case somewhere to go.

> **A defect this feature makes visible for the first time.** `_to_exclusions()` **silently
> drops** an MBID that is not in the graph. A shared link carrying a stale or bogus MBID
> therefore builds a path as if that press never happened — today invisibly, and after this
> feature as a row that lies or a row that vanishes. `LUX-2b` is where that gets decided;
> it must be decided, not inherited.

**Estimate: half a day for `LUX-2a`, half a day for `LUX-2b`.**

### The honest note on what the panel becomes

The mockup gets its variety from two verbs. After `LUX-1` every row reads the same way, and
the panel is a **list of artists you skipped** rather than a route history. That is still the
only place bypassed artists are visible at all — today they vanish without trace — and the
caption teaching that Back is safe and the URL is the whole state is the most useful thing a
first-time visitor can learn. Design it as what it is.

---

## §3 `LUX-3` — a different clip by the same artist

### The decision

Let the user cycle to another track by the artist on the card. Index parameter on the clip
endpoint; the candidate list held in the cache.

### Why it is nearly free

**All three resolvers in `api/src/artistpath_api/clips.py` already fetch a list and throw
almost all of it away.** `clip_search_limit` (`ApiConfig`) is requested from each provider,
and `_from_deezer_artist()`, `_from_deezer()` and `_from_itunes()` each loop and `return` on
the first playable row.

`TrackIdentity` deliberately holds **no signed URL** — only `source` and `track_id` — and
`_preview_url()` re-signs per identity, per source. An alternate track therefore needs no new
upstream call pattern: it is the same re-sign that already happens on every cache hit.

### What changes, and where the cost is

The cost is the **cache shape**. `ClipCache.get(mbid) -> TrackIdentity | None` holds exactly
one track, and `DynamoClipCache` writes it as flat attributes.

- `ClipCache` protocol and both implementations move to a candidate list.
- `DynamoClipCache` item shape changes. **There is a precedent in the same file**: pre-`C2`
  items are treated as a miss and overwritten, and the 30-day TTL (`clip_ttl_days`) drains
  the old shape unaided. Use it; do not write a migration.
- `GET /api/artists/{mbid}/track` gains an index and returns a **candidate count**.
- Frontend gains the control and holds the index in component state.

**Estimate: one to two days**, most of it the cache and its tests.

### Three things it must get right

1. **The control disappears when there is nothing to cycle to.** Thin catalogues are a
   studied population here (`TCE-`/`TCR-`); some obscure artists have exactly one playable
   track, and they are exactly the artists the app exists to deliver. This is why the
   endpoint returns a count rather than the frontend guessing.
2. **Quality degrades with each press.** Deezer's `/artist/{id}/top` is popularity-ranked, so
   candidate 2 is genuinely the second-best-known track; iTunes search relevance is murkier.
   The control should read as *try another*, never as a deep well.
3. **Keep it out of the URL.** The path is the shareable artifact; the clip is incidental,
   and per-artist clip indices would bloat the query string at depth. **The cost is real and
   is accepted:** Back will not restore a clip choice, which sits slightly against the
   caption `LUX-2` puts on the page. Owner-level call, recorded as taken.

### Why this one matters most for the product

The app asks a listener to judge an unknown artist on one 30-second clip. If that clip is
unrepresentative — a live cut, a remix, an outlier — the artist is rejected and neither the
user nor the project ever finds out. That is a **discovery failure**, not a cosmetic one, and
of the four items this is the one most directly serving what the app is for.

---

## §4 `LUX-4` — streaming links and the artist info card

Two features, one extraction pass, one artifact decision. **They are scoped together
deliberately**: both read the same MusicBrainz dump, and discovering after the fact that a
second rebuild is needed for one more field is the failure this pairing prevents.

### §4.1 The decision

- **Deep links to Spotify and Apple Music from MusicBrainz URL relations**, shipped as
  **additive APG1 keys** alongside `deezer_ids` (**option C**), with **search links as the
  fallback** wherever no id exists (**option A**).
- **An artist info card built from structured MusicBrainz fields only** — `type`, area/country,
  life span, and the `disambiguation` the artifact already carries.
- **Genre tags deferred.** Not dropped.
- **A prose description dropped.** Not deferred. See §4.5.

### §4.2 What already exists

`builder/analysis/2026-08-02-dsp-ids/dsp_ids.py` **already scans the MusicBrainz artist dump
for streaming-service URL relations, and its host map already includes `open.spotify.com` and
`music.apple.com`** — it then filters the results down to Deezer and Apple. Spotify is one
line of filter away. The script is offline, read-only, and runs in about two minutes; the
dump is on disk at `builder/scratch/mb-json-dumps/artist/mbdump/artist`.

`builder/src/artistpath_builder/deezer_ids.py` is the **pattern to copy**: a frozen, dated,
sha-pinned MBID→id map, extracted over the adopted artifact's population, shipped as package
data, never re-resolved at build time. Read its docstring before writing anything — it
records why the map is one-per-artist rather than one-per-archive, and why a missing id must
degrade to today's behaviour rather than to an error.

Coverage was **already measured** for Deezer and Apple, by population band and by delivered
card: `dsp_ids.json` and `delivered_coverage.json` own those figures. **Spotify was never
counted.** That is `LUX-E3`.

`disambiguation` is **already in the artifact, already on the wire in `ArtistOut`, and already
rendered** — but only in the search dropdown (`frontend/src/components/ArtistSearch.tsx:139`),
never on a journey card. Surfacing it is free and needs no rebuild.

### §4.3 Why C rather than serving the map from the API

The cheaper option was shipping the id map as a data file in the API package: no artifact
rebuild, no new checksum, no deploy ceremony. It was rejected for a reason that only shows up
later.

`deezer_ids.py` carries a **standing obligation** in its own docstring: re-extract over the
new population before a new artifact is served. Put Spotify and Apple in the artifact and
they inherit that obligation, in the same place, discharged by the same act. Put them in the
API and there is a **second** population-drift obligation with a different shape, keyed to a
population that will silently diverge from whatever graph is being served — and its failure
mode is invisible: links quietly missing for artists a later crawl added.

The owner's reasoning for accepting the rebuild cost: **there are essentially no users, and
invasive work belongs before a public launch, not after.** That reasoning is sound and is
recorded as accepted.

### §4.4 ⚠ The blocking unknown — a rebuild may not reproduce the live map

**This is the one thing that must be settled before `LUX-4` is planned, and it was surfaced
in the same session as a correction to an earlier, wrong cost estimate.**

Option C was priced as *"the same graph plus two metadata keys"*. That may be false today.

- The live artifact `graph-msw-tu50.bin` was built 2026-08-06 and is **ALG-B lineage** —
  `CEX-5` (commit `37dddbc`) verified that against the artifact's own manifest sidecar rather
  than against the plan, and corrected `config.py`, which had said otherwise.
- **`CXA-` Task 2 (commit `7404a4c`, 2026-08-10) repointed `CANDIDATE_ALGORITHM`'s
  unlistenable-filter payload** — ALG-B's — from the 75,000-era census to the 117,302-artist
  one. Its own message states the hazard it fixed: *"Every future build would have applied
  the wrong drop list to the bigger archive, silently."*

That payload **is** the drop list, which decides which artists exist in the graph.
Determinism (spec §9) guarantees identical output for identical *input*, and an input changed
in git after the live artifact was built.

**If a rebuild does not reproduce `43dd82bb…`, `LUX-4` is not a metadata change — it is a
graph adoption**, which is the operation that was reverted on 2026-09-01 after the owner's
own listening test, and which needs acceptance gates and his ear. That is a very different
thing to have in flight immediately before a public launch.

A second, sharper edge in the same area: `BuilderConfig.algorithm` still **defaults to ALG-E**
while the adopted map is ALG-B, deliberately (`CEX-5`). Every operational build must pass
`--algorithm` explicitly or it builds the wrong lineage outright.

**`LUX-E1` settles this and gates `LUX-4`.** The owner's instruction, 2026-09-03: address it
in implementation rather than in this session.

### §4.5 Why the prose description is dropped rather than deferred

MusicBrainz holds no biographies. Each realistic source fails, and they fail differently:

- **Wikipedia / Wikidata** — `COH-2` (`findings/2026-07-30-coherence-tag-probe.md`) measured
  precisely this and found tag coverage shares **Wikipedia's fame floor**, with the tag union
  beating Wikipedia's tail figure. The card would be rich for the famous and empty for
  everyone the app exists to find.
- **Last.fm** — barred. `specs/2026-07-19-artist-path-alpha-design.md` §1 states it must
  never become load-bearing, and `REQ-44` gates anything downstream.
- **LLM-generated** — rejected on harm, not cost. The hallucination rate is **inversely
  correlated with fame**: the less source material exists, the more is invented, and the app's
  entire purpose is routing to artists with the least source material. It would publish
  fabricated biographical claims about real, often living, often obscure musicians, on a
  public domain, with the errors concentrated on the people least able to notice or correct
  them.

There is also a product argument, and it is why this is *dropped* rather than parked: the
premise of the app is that you judge an artist **by listening**, in thirty seconds. Prose
competes with the clip for attention and pre-empts the verdict. Structured facts orient
without pre-empting — *"German duo · 1993–2008"* tells you where you are and gets out of the
way — and they cannot be wrong.

> **Do not re-open this as "we could just use Wikipedia for the ones that have it."** That is
> the fame floor, and it was considered and declined with the measurement in view.

### §4.6 Why genre tags are deferred rather than shipped

The tag coverage question is **already answered and the answer is committed**:
`findings/2026-07-31-release-tag-coverage.md` owns the figures — artist tags as they stand
(`F0`), plus MusicBrainz release-group genres (`F1`, which passed `REL-1`), plus Discogs
(`F6`), each by popularity band. **Read the lower-half rows there before reviving this.** The
tail coverage is what deferred it: an info card field that is usually blank for obscure
artists needs a designed empty state before it needs a pipeline.

Reviving tags means productionising an analysis-stage aggregation, which is a track of its
own. It is deferred, and `LUX-E6` is its entry condition.

### §4.7 What changes

| Package | Change |
|---|---|
| `builder/analysis/2026-08-02-dsp-ids/dsp_ids.py` | Stop filtering Spotify out; extract the structured fields in the same pass. |
| `builder/src/artistpath_builder/` | A frozen sha-pinned map module per the `deezer_ids.py` pattern; artifact writes the additive keys. |
| `api/…/graph_store.py` | Read the additive keys, with the same "may be shorter than N" discipline `deezer_ids` already uses. |
| `api/…/models.py` | `ArtistOut` gains the link and info fields. **Wire contract — the frontend consumes it.** |
| `frontend/` | The info card; link buttons; the `disambiguation` already available. |

**Estimate: two to three days after `LUX-E1` returns**, plus a deploy. If `LUX-E1` comes back
red, re-scope before estimating — it is a different piece of work.

**Licensing:** plain text or URL links to Spotify and Apple Music need no agreement. Using
their **logos** pulls in brand guidelines. Start with text or a generic icon.

---

## §5 Evals owed

Each carries a plain sentence fixed here, **before any result exists**, so a later report
whose wording drifts from it is as visible as a moved number. Owner-facing text quotes the
sentence, never the bare identifier.

### `LUX-E1` — can the live map be rebuilt from HEAD? **(gates `LUX-4`)**

Rebuild from the same archive at the ALG-B lineage with today's builder; compare the sha to
the live artifact's `43dd82bb…` recorded in `NEXT.md`. One knob differs by construction — the
builder's own state — and nothing else may be varied.

- **Plain sentence:** *does building the map again today, from the same data, produce the
  exact same map the site is serving right now?*
- **Threshold: byte-identical, or not.** There is no partial credit and no "close enough": a
  differing sha means a different population.
- **Read — identical:** `LUX-4` is what it was priced as. Proceed.
- **Read — different:** `LUX-4` is a **graph adoption**. Stop, and put two things to the
  owner: whether to adopt whatever HEAD now builds (which needs its own pre-registration and
  his ear), or to ship the links from the API package instead, accepting §4.3's second
  drift obligation. **Do not proceed on a session's own judgement.**
- Read-only with respect to anything served; writes a candidate artifact to
  `builder/scratch/` and adopts nothing. ~23 min.

#### `LUX-E1-AM1` — a second, isolating arm. Amended 2026-09-05, **before either arm ran.**

**Why:** the default arm's answer is now knowable from source, and it is RED. `CXA-` Task 2
(`7404a4c`) repointed the ALG-B **unlistenable drop list** default at a payload re-censused
over the extended 117k population, and the `CXR-` revert moved the map without moving that
pointer. Measured on the served graph's own population: **31 artists that are in the live map
would be newly dropped, and none return** — figures owned by
[`builder/analysis/2026-09-05-lux-e1-drift-source/README.md`](../../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md),
cited never restated. A 31-node difference is a different population, and this eval has no
partial credit.

**So running the default arm alone now buys nothing** — it would spend 23 minutes confirming
a foregone conclusion, and its "different" read sends the question to the owner as an
open-ended graph adoption when the cause is already identified.

**The arm to add is its isolating baseline — differing by exactly one column:**

| Arm | unlistenable ALG-B payload | everything else | baseline |
|---|---|---|---|
| **A (original)** | HEAD's default (`…algb_20260809.json`) | HEAD | — |
| **B (new)** | pinned to `…algb_20260805.json`, the list the live map was built with | HEAD | A |

**Held constant, and why the intervention cannot change it:** the archive, the algorithm
(`--algorithm` ALG-B explicitly, `CEX-R5`), every cap and rescale knob, and both other drop
families — `7404a4c` touched only the unlistenable family, checked. `ce47106` (`SEL-`) already
added the per-invocation payload override, so arm B needs no new code and no default is moved
to run it.

- **Plain sentence for arm B:** *if we build the map again using the exact artist-exclusion
  list the live map was built with, do we get the live map back byte for byte?*
- **Threshold: byte-identical to `43dd82bb…`, or not.** Same standard as arm A.
- **Read — B identical:** the drop-list pointer was the **only** build-side drift. `LUX-4` is
  a metadata change as priced, and the owner has a genuine one-line choice: repoint the
  default back, or accept 31 artists dropped. **Both are his; a session takes neither.**
- **Read — B different:** something beyond the drop list moved and is not yet identified.
  **Stop and find it before proposing anything** — the original "different" read then applies
  in full, and `LUX-4` is a graph adoption.
- **Run B first if only one is run.** A is predicted and B is diagnostic.

⚠ **Neither arm adopts anything, and neither may repoint a default.** Arm B pins its payload
per invocation precisely so the committed default is untouched while it runs.

### `LUX-E2` — per-field delivered coverage **(informs `LUX-4` design)**

Over the 120 committed `TAS-` pairs (`builder/analysis/2026-07-30-tag-discrimination/tas_pairs.json`,
40 ff / 40 fo / 40 oo), reusing `delivered_coverage.py`'s shape: for each proposed field and
each link target, the fraction of **interior** cards carrying it, by popularity band.

- **Plain sentence:** *on the artist cards a user actually sees, how often is each new piece
  of information actually there — and does it vanish for the obscure artists the app exists
  to find?*
- **Threshold:** any field below **50%** in the lower half needs a **designed empty state**,
  not a blank line. This is a design trigger, not a kill.
- Endpoints are excluded — they are the user's own picks, per `delivered_coverage.py`'s note.
- **⚠ BLOCKER — FIX THE SAMPLE BEFORE RUNNING THIS.** The 120-pair `TAS-` file this eval names
  is **damaged on the currently-served map**: a large minority of pairs can no longer be routed
  because an endpoint is absent from the graph, and the loss falls almost entirely on the two
  obscure classes. Figures owned by
  `builder/analysis/2026-09-04-lux-e4-candidate-counts/README.md` §2a — cited, never restated.
  **This threshold is stated over the lower half, which is precisely the population the damage
  removes**, so running as written would report a denominator that is empty or near-empty and
  return the same undefined read `LUX-E4` did. Either redraw the sample against the adopted
  artifact first, or report UNDEFINED — **never a pass**. Carried here 2026-09-05 from `LUX-E4`
  below, where a session running this eval would not have seen it.

### `LUX-E3` — Spotify id coverage **(informs `LUX-4`)**

The count `dsp_ids.py` has never produced, by band, alongside the Deezer and Apple figures it
already owns.

- **Plain sentence:** *how many artists have a Spotify link recorded in MusicBrainz, and is it
  better or worse than Apple's?*
- **Threshold:** none — descriptive. It decides whether the feature is "both services" or
  "Apple plus search", and nothing else.

### `LUX-E4` — candidate-count distribution **(gates `LUX-3`'s worth, not its correctness)**

Same 120-pair sample: for each interior artist, how many playable candidates the resolver
finds, split by band **and by resolution route** (deezer-id / deezer-name / itunes).

> ⚠ **This eval, when it ran, found the 120-pair `TAS-` sample itself damaged on the
> currently-served map** — a large minority of the pairs can no longer be routed at all, with
> the loss concentrated almost entirely in the two obscure pair classes. Any later session
> reusing this sample, including for `LUX-E2` above, inherits the same hole silently unless it
> checks first. See `builder/analysis/2026-09-04-lux-e4-candidate-counts/README.md`, which owns
> the figures — this is a qualitative pointer only, nothing here restates them.

- **Plain sentence:** *for how many of the cards a user sees does a "try another track"
  button appear at all — and does it disappear exactly for the obscure artists?*
- **Read — undefined (denominator empty).** ⚠ **Added 2026-09-04, after the run, and it is an
  admission rather than a result:** no branch below anticipated the population simply not
  being delivered, and that is exactly what happened. **A threshold whose denominator is
  empty is reported as UNDEFINED and never as a pass**, and the same holds for every other
  eval in this section. `LUX-E4`'s own run is the worked example —
  `builder/analysis/2026-09-04-lux-e4-candidate-counts/README.md` owns it.
- **Threshold:** if fewer than **half** of lower-half cards carry ≥ 2 candidates, `LUX-3`
  serves famous artists and not the ones the app is for. That is a **re-prioritisation
  trigger and the owner's call**, never a session's decision to drop it.
- **⚠ THRESHOLD RETIRED 2026-09-05 (owner). `LUX-E4` IS CLOSED AND MUST NOT BE RE-RUN.**
  The read above stands unchanged — it was and remains **undefined**, never a pass. What is
  retired is the *threshold*, because it was **mis-specified**: it names a re-prioritisation
  trigger for an outcome that costs nothing. `LUX-3`'s control is gated
  `playable && candidates > 1` (`frontend/src/components/ArtistCard.tsx`), so when there is
  nothing to cycle to **the element does not render** — no blank line, no placeholder, no
  stranded card. It degrades exactly as a silent card already does today. The component's own
  comment states the accepted position in advance: *"an artist with exactly one playable track
  is the population this app exists to deliver"*. There is therefore no result the eval could
  return that would change whether `LUX-3` ships or stays, and re-running it buys nothing.
  **Contrast `LUX-E2`, whose threshold is NOT retired and does have teeth** — a missing field
  there leaves a blank line in the card layout, and crossing 50% buys a designed empty state,
  which is a real change to what someone builds.
- **Do not re-open the empty denominator as a new question.** That zero is **`DD-F1`**, already
  measured and long in the record — not a discovery of this run. `TAS-6`'s routing half measured
  a baseline of zero sub-decile journey interiors on **this same 120-pair sample** on
  2026-07-30, five weeks earlier and on the adopted artifact
  (`findings/2026-07-30-tag-discrimination.md`, which owns that figure; `tas_guard.py:111`
  early-returns on it). See also `PRODUCT-REQUIREMENTS.md` §8 for the `REQ-37`/`DD-F1`
  structural conflict, and the `JFX-` reachability read for the currency split — `DD-F1` binds
  in **popularity** and does not transfer to **fame**, and both halves travel together.
  A session that reads `LUX-E4`'s empty denominator as a fresh path-quality signal has
  rediscovered a known defect through a clip-availability eval, on a sample too damaged to
  support it.

### `LUX-E5` — metadata blob and boot cost **(gates `LUX-4` shipping)**

Metadata blob bytes and artifact total before and after; API resident memory and boot time in
the deployed configuration. The artifact is 17.8 MB today and the JSON blob is loaded whole at
boot.

- **Plain sentence:** *does the extra artist information still fit in the memory the running
  service actually has?*
- **Threshold:** must fit within the deployed container's configured memory with headroom for
  the existing working set. If it does not, fields are dropped — **starting with tags, never
  with `LUX-E2`'s survivors.**

### `LUX-E6` — tag vocabulary sanity **(entry condition for the deferred tag work)**

A sample read of the actual tag strings that would render.

- **Plain sentence:** *are these labels fit to show the public as written, or do they need an
  allowlist first?*
- **Threshold:** descriptive. MusicBrainz tags are user-submitted; the read decides whether
  reviving tags costs a curation stage on top of the aggregation stage.

---

## §6 Sequencing

Dependency order, not priority order. Each earlier item makes a later one cheaper or safer.

1. **`LUX-1`** — frontend only, reversible, and it removes `LUX-2`'s only obstacle.
2. **`LUX-2a` then `LUX-2b`** — frontend, then the small API addition.
3. **`LUX-3`** — self-contained; `LUX-E4` alongside, not before.
4. **`LUX-4`** — last, and **`LUX-E1` first**. It is the only item with an unresolved
   question underneath it, and the only one that touches the served artifact.

**A natural handoff seam sits between item 3 and item 4** (`CLAUDE.md`, "Plans over ~8 tasks
must name their own handoff points"). Items 1–3 are frontend and API work with no artifact
involvement; item 4 is a builder, artifact and deploy track with its own gate. Retire the
session there rather than discovering the boundary inside `LUX-4`.

---

## §7 The `PRODUCT-REQUIREMENTS.md` amendment, ready to apply

**Not applied here, deliberately.** The PRD states what the app does; editing it before
`LUX-1` ships would make it describe something untrue. **The implementing session applies
this in the same commit as the code**, and re-checks the highest `REQ-` number first — it was
`REQ-44` on 2026-09-03.

Per that document's own convention, superseded entries are **struck in place, never deleted.**

**§7 "The `dislike` signal"** — mark `REQ-30`, `REQ-31` and `REQ-32` retired, with this note:

> ⚠ **RETIRED 2026-09-03 (owner), on shipping `LUX-1`.** The `dislike` button is removed from
> the UI; the mechanism, the wire contract and the `?dislike=` URL parameter remain, so these
> three requirements describe code that still exists and is no longer reachable from the
> product. They are retired, **not overturned** — if the second signal is ever restored, they
> govern it again as written. Scope: `specs/2026-09-03-launch-ux-scope.md` §1.

**§3 "Bypass behaviour"** — `REQ-13`–`REQ-19` are unaffected and must not be edited. They are
written about bypass as such, not about two signals.

**Two new entries**, numbers to be confirmed at apply time:

> **REQ-45 (Must)** — The bypass control **must not read as a rejection of the artist**. With
> a single signal, a press routes to a highly similar and more obscure artist (`REQ-27`), which
> is the wrong answer to *"I don't like this"*. Wording that invites that reading is a defect.

> **REQ-46 (Should)** — Artists removed by a bypass **should remain visible to the user**.
> Before `LUX-2` they vanish without trace, which makes a press unreviewable and unexplainable.

---

## §8 What is closed, and must not be re-litigated

- **A prose artist description.** Dropped on the grounds in §4.5, with the measurement in
  view. Not a deferral.
- **Last.fm as a source.** Barred by `specs/2026-07-19-artist-path-alpha-design.md` §1 and
  gated by `REQ-44`. Nothing in this scope changes that.
- **The two-button bypass.** The owner's decision, taken with the lateral-movement cost
  stated. Reversal is his trigger, not a session's.
- **Clip choice in the URL.** Declined in §3, with the cost accepted.

**Open and NOT closed:** whether genre tags are ever shipped (§4.6, `LUX-E5`/`LUX-E6`), and
whether a restored second bypass signal is wanted after real use.

---

## §9 Weakest link

Every effort figure here is a session's judgement from reading the code, **not a measurement**,
and none of them survives `LUX-E1` coming back red.

The load-bearing assumption across `LUX-2`, `LUX-3` and `LUX-4` is that **press depths stay in
single digits**. It is why no scroll, collapse or pagination is designed for the history panel,
why N name lookups are acceptable, and why the candidate list is small. At the twenty-press
depths used in testing it fails — but `REQ-17` states those are test instruments and not use
cases, so this is a deliberate bound, not an oversight. **What would falsify it:** real users
after launch pressing far deeper than the owner does. Telemetry already emits `dislike_count`
and `known_count` per path request (`app.py`), so the evidence will arrive on its own.

The assumption behind `LUX-1` — that "I don't like this" is a rare enough intent to leave
unserved — has **no evidence and cannot have any before launch.** It is the single claim here
most likely to be wrong, and the reason the mechanism is kept rather than deleted.
