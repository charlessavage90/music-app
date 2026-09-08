# Unsung.fm redesign — scope, and the decisions taken over the mockup

**Role: ACTIVE — the governing scope document for the `UXR-` set.** Identifier series
`UXR-` (decisions `UXR-D1`–`UXR-D18`, plan tasks `UXR-T1`–`UXR-T11`), collision-checked
across every ref on 2026-09-08. This document states what the redesign builds, what it
defers, what it drops, and why; the implementation plan
(`plans/2026-09-08-unsung-redesign.md`) argues from it. **Where this document and the
mockup disagree, this document governs.**

**The visual source** is the owner's Claude Design project, direction 1a *"Signal, with docked
artist detail"*, exported verbatim to `frontend/design/2026-09-08-unsung-redesign/`. It was
workshopped by him and he "landed on something I am happy with" (2026-09-08). Its layout,
type, palette and copy are adopted as drawn **except where a decision below says otherwise.**

**What triggered it.** The address is `unsung.fm` since 2026-09-03 while the UI still says
"Artist Path"; a broader rollout (LinkedIn, Reddit) is planned, and the owner wants the name
finalised and the UI redesigned before it. The rename was scoped-and-unapproved in `NEXT.md`
until 2026-09-08; **it is approved now (`UXR-D1`).**

---

## §0 What the mockup knew, and did not

The Design project's "current build" artboard was recreated from `frontend/src` on 2026-09-04
at 02:00. `LUX-1`–`LUX-3` merged that evening (PR #101) and `LUX-4` on 2026-09-07/08 (PRs
#105, #112). So the mockup:

- shows **"Steer away"** and the reroute tray, both removed by `LUX-1`;
- has **no home** for the skipped-artists panel (`LUX-2`, `REQ-46`), "Try another track"
  (`LUX-3`), or the **Apple Music** link (`LUX-4`, which always renders both services);
- has **no loading, error, not-found or adjacent-artists state**;
- says **"75,000 artists"** where the served artifact's manifest says 58,838;
- draws a **Spotify-green** button, where `LUX-4` shipped neutral text links on a licensing
  argument (scope spec §4.7).

None of this blocks anything. It means those elements are *placed* by this document rather
than ported from the mockup — §3 below.

## §1 The assessment the owner decided over

Presented 2026-09-08; his decisions are recorded in §2. Effort is relative to this codebase.

| Mockup element | State on 2026-09-08 | Feasible? | Effort |
|---|---|---|---|
| Unsung name, mark, wordmark, fonts | Scoped, unapproved; UI says "Artist Path" | Yes | Small |
| Docked detail panel / mobile bottom sheet | Facts and links render inline on the card | Yes | Medium |
| "Dig deeper" moved inside the detail | It is the card's footer strip | Yes | Small |
| Share button | Nothing; the URL already is the whole state | Yes | Small |
| Player progress bar and "Stop N of M" | Bar shows name and play/pause; the player exposes no time events | Yes | Small |
| "How it works", "About the map", nav | No such pages or sections | Yes | Small–medium; the copy is his |
| Live artist count badge | `/health` carries the count but is not reachable through CloudFront (only `/api/*` is routed) | Yes, via a new API route | Small |
| Hop counts on sample chips | Pairs hardcoded; counts not | Yes; they drift on every rebuild | Small |
| Reach meter / "low reach" pill | Not built; the mockup derives it from `popularity`, which is raw in-graph popularity — not a rank, not fame | Yes technically; the adopted novelty proxy is one additive field from the wire | Small–medium; a new user-facing construct |
| Genres | Deferred by `specs/2026-09-03-launch-ux-scope.md` §4.6; entry condition `LUX-E6` unrun | Yes, as its own track | Large, plus a rebuild and deploy |
| "Why this stop" prose | Not built; as drawn it is generated prose, dropped by that spec's §4.5 | As drawn, no; a templated sentence from graph facts would be | Medium |
| "Save track" | Not built | **No** — needs a Spotify user login and Spotify track ids; the app has neither, and the mockup's own copy says "no account needed" | — |

## §2 The owner's decisions, 2026-09-08 — verbatim in substance

1. **Unsung rebrand approved, including the new fonts and style.**
2. **Two presses for the reroute approved** (open the detail, then "Dig deeper"). *"This
   design / UX is important, so we may want to revisit."* Not net-new: the app before `LUX-1`
   also took two presses (open the tray, choose).
3. **The additional pages are deferred from this plan**; he will draft their copy; *"know that
   we will add these in the future."*
4. **The reach pill is dropped from scope.** His words: flagging "unusual" artists is
   interesting, but *"reach" does not communicate it, and the pill as designed makes those
   artists seem "worse"* because of the signal-meter glyph. *"At some point in the future we
   can determine if there is a better way to denote the 'obscure' artist finds."* Recorded as a
   deferred product idea, no trigger, his.
5. **Run `LUX-E6`.** Done 2026-09-08 — figures owner
   `builder/analysis/2026-09-08-lux-e6-tag-vocabulary/README.md`. It changes nothing in this
   scope: genres stay deferred (§4 below) and he decides go/no-go on that read separately.
6. **"Why this stop" prose deferred.** The detail shows *the existing `LUX-4` card data*,
   moved from the card into the detail.
7. **"Save track" dropped from scope.**

## §3 Decisions this document takes — the session's, stated so he can overrule them

Each carries the reasoning; overruling one is a one-line instruction, not a re-plan.

- **`UXR-D1` — the name is "Unsung.fm", the wordmark is `unsung` + a dimmer `.fm`, the mark
  is the owner's PNG.** The `<title>` becomes "Unsung.fm", the no-JS fallback in
  `index.html` says it, and every `aria-label` and heading that said "Artist Path" changes.
  The API package, the artifact format and every internal identifier keep the name
  `artistpath` — a product rename, not a codebase rename.
- **`UXR-D2` — the card keeps what a listener needs to *listen*; the detail holds what they
  need *after*.** Card: cover, name, track title · 0:30, play, the detail button, "now
  playing". Detail: the facts line (`ArtistInfo`), both streaming links (`StreamingLinks`,
  unchanged in behaviour), "Play clip", "Try another track", and — interior artists only —
  "Dig deeper". This is decision 6 made concrete: the mockup's "Play this clip / Save track"
  row becomes "Play clip / Try another track", which keeps `LUX-3` reachable.
- **`UXR-D3` — one detail component, two containers.** `ArtistDetail` renders the content;
  at the `lg` breakpoint (1024 px) it is docked in a sticky right column beside the rail; below
  it, it is a bottom sheet with a scrim. The sheet closes on ✕, scrim tap, Escape, and **on any
  path rebuild** (the selected artist may no longer exist). Selection is component state,
  never URL state: the URL is the shareable journey, and "which sheet was open" is not part of
  a journey.
- **`UXR-D4` — the streaming links stay neutral.** No Spotify green, no logos; the `LUX-4`
  licensing rule (scope spec §4.7) is unchanged. The links become two full-width buttons in
  the detail, styled in the app's own palette, labelled "Open on Spotify" / "Open on Apple
  Music", search-fallback behaviour identical.
- **`UXR-D5` — the skipped-artists panel stays, below the journey, restyled.** `REQ-46`
  requires it; the mockup omitting it is §0, not a decision. The bypass explainer
  (`PathIntro`) stays as onboarding and its copy changes to describe the new placement: open
  an artist in the middle, then press Dig deeper.
- **`UXR-D6` — one count currency: "steps" = artists *between* the two chosen (UI-D7),
  everywhere.** The journey title's tile, the result line, the sample chips and the teaser all
  count the same thing. The mockup's chips say "8 hops"; hops is a different currency
  (`path_length − 1`) and is not used in the UI.
- **`UXR-D7` — the sample chips carry hardcoded step counts, measured on the served graph
  2026-09-08, pinned by an e2e test against the live router.** Miles Davis → Radiohead **3**,
  Dolly Parton → Daft Punk **4**, Bad Bunny → Chappell Roan **6**. The alternative — three
  path requests per landing view — spends Dijkstra on every visit for a decoration. The
  existing rule (re-check the pairs after any graph adoption) now has a test that fires.
- **`UXR-D8` — the artist count is live, from a new `GET /api/meta`.** `/health` is off
  `/api` deliberately (App Runner reaches it directly) and CloudFront does not route it, so
  the badge needs a route it can reach. `async def`, three in-memory reads, no I/O — the same
  discipline `/health` carries (`G3-A1`). The badge shows the count **floored to the nearest
  thousand** ("58,000 artists mapped by who listens to whom") and **renders nothing** if the
  request fails (UI-7: a decoration must not be able to break the page).
- **`UXR-D9` — Share uses the Web Share API where it exists and the clipboard where it
  does not**, with "Link copied" shown for two seconds. The shared URL is `location.href`,
  which already carries the whole journey including bypasses. Nothing is added to it.
- **`UXR-D10` — the player bar gains a progress line and "Stop N of M".** N is the playing
  artist's 1-based position among **all M artists including both endpoints** — a third count
  currency, named so it is not confused with `UXR-D6`'s. Position comes from the audio
  element's `timeupdate`; the bar never estimates.
- **`UXR-D11` — both faces are self-hosted through `@fontsource-variable`**, Space Grotesk
  for display (the h1, artist names, the wordmark, numbers in tiles) and DM Sans for body.
  The mockup loads Google Fonts; the app does not — no third-party request on page load, no
  CSP question. Instrument Serif is linked by the mockup and used by nothing; not added.
- **`UXR-D12` — the landing copy is the mockup's, verbatim, superseding the owner's
  2026-08-07 copy.** ⚠ **Assumption, flagged.** The current landing copy is his own words and
  carries a comment forbidding reinstating the mechanism line without asking him; the mockup's
  hero paragraph *does* state the mechanism. He workshopped the mockup himself, so this
  document reads that as the newer instruction. **If that is wrong, say so and `UXR-T3` keeps
  the 2026-08-07 lines under the new type.**
- **`UXR-D13` — the "How it works" strip stays on the landing, with the mockup's copy.** It
  is a section of the landing page, not one of the "additional pages" decision 3 defers. The
  top navigation ("How it works · Sample journeys · About the map") is **not** built until
  those destinations exist.
- **`UXR-D14` — the teaser panel on the desktop landing is static**: "A path, five steps",
  the Miles Davis → Daft Punk journey as measured on the served graph (Nina Simone, Marvin
  Gaye, Daryl Hall & John Oates, Genesis, David Gilmour), with no tags — the mockup's "low
  reach" tags went with decision 4. Same drift rule as `UXR-D7`; same test pins it.
- **`UXR-D15` — the endpoint eyebrows become "You started here" / "You were heading here"**,
  as drawn. Tests that matched "Starting artist" / "Destination artist" change with them.
- **`UXR-D16` — the "recommended" tag on Dig deeper is dropped.** There is one option;
  "recommended" against nothing is noise.
- **`UXR-D17` — the palette moves to the mockup's, as tokens named by role, in one commit,
  with every old token name kept as an alias until the last restyle task removes the unused
  ones.** A token that silently resolves to nothing is transparent, which no test sees.
- **`UXR-D18` — the mark is also the favicon.** The purple bolt in `public/favicon.svg` is
  the Vite template's; it goes.

## §4 Deferred, dropped, and what would reopen each

| item | state | reopens when |
|---|---|---|
| Reach / "unusual artist" marker | **Dropped** (decision 4) | The owner names a way to denote obscure finds that does not read as "worse". His trigger. |
| Genres in the detail | **Deferred** — `LUX-E6` ran 2026-09-08; the deferral in the `LUX-` scope §4.6 stands | The owner reads `LUX-E6` and lifts the deferral; then its own plan, artifact key, rebuild, deploy. |
| "Why this stop" prose | **Deferred** (decision 6); the generated-prose form stays **closed** per `LUX-` scope §4.5 | Only a templated-facts form is on the table, and only if he asks. |
| "Save track" | **Dropped** (decision 7) | Never in this architecture: it needs a user account. |
| Top nav + "About the map" + "Sample journeys" pages | **Deferred** (decision 3) | He delivers the copy. |
| Two-press reroute | **Approved with a revisit note** (decision 2) | Real use after deploy; his trigger. |

## §5 What is closed, and must not be re-litigated here

- **The `LUX-` scope's closed list** (`specs/2026-09-03-launch-ux-scope.md` §8): prose
  descriptions, Last.fm, the two-button bypass, clip choice in the URL. Nothing here reopens
  them, and the Dig deeper relocation is a *placement*, not a second signal.
- **Both streaming services always render** (`LUX-4`, spec §4.1 option A). The mockup's
  Spotify-only detail is §0.
- **`L4-D3` — render only what is present, no placeholder rows.** Moving the facts line does
  not change that.
- **The facts line wraps and never truncates** (`L4-T11`; `e2e/responsive.spec.ts`). The
  detail has more width than the card, which makes this easier, not optional.

## §6 Evaluation owed

**None that ends in a number.** This is a UI change under approved design; its evidence is
the use-the-app queue entry `closeout` writes when it is deployable, and the e2e suite. One
rule from the `LUX-4` log §11 applies with force: **look at the real thing on real data before
believing a green suite about a visual change** — the truncation defect was found by a
screenshot with every suite green. The plan's restyle tasks each end in a screenshot at 390 px
and 1280 px, not only in a test run.

## §7 Deploy shape

Two images, not one: the frontend (`infra/README.md` §6) **and** the API, for `/api/meta`
(`UXR-D8`). The frontend degrades correctly if it lands first — the badge renders nothing. The
`LUX-4` deploy (new artifact, both `s3 cp` lines) is already owed and comes first; nothing
here changes the artifact.

## §8 Weakest link

`UXR-D12`. Everything else is either drawn by the owner or a mechanical consequence of a
decision he took; the landing copy is the one place this document *infers* his instruction
from two sources that disagree. The cost of being wrong is one task's copy, and the check is
one question.
