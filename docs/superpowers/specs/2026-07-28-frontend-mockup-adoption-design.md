# Frontend mockup adoption: design, 2026-07-28

**Role: COMPLETE — implemented, merged and deployed 2026-07-28.** Design for adopting the
owner's Claude Design mockup as the app's interface. Supersedes nothing. **Still
authoritative for the redesign's *intent*, and its §2 owner decisions are closed** — but it
no longer describes work to be done. ⚠ **The owner changed two landing strings after the
deploy; §7's copy table is annotated in place** and the annotation wins over the rows. Does
**not** state project status — that is [`../NEXT.md`](../NEXT.md).

**Identifier series: `UI-`.** Namespaced deliberately and checked against the repo
(`UI-n` appears nowhere else, 2026-07-28). Forward-only: nothing here renames a
committed identifier.

**Not path-quality work, and the pause is intact.** No routing, no graph, no cost
function, no weight, no rebuild. `ApiConfig`, `BuilderConfig` and the artifact are
untouched. The one API change is an in-memory dictionary lookup that returns a name.

**Not a re-skin.** `frontend/src/index.css` already defines eight theme tokens and the
mockup uses those exact eight values. What changes is type scale, spacing, input
states, and five new structural pieces.

---

## 1. Source of truth, and a dependency

The design is the Claude Design export currently at
`C:\Users\charl\Downloads\Artist Path landing screen` — `Artist Path.dc.html` is the
authoritative file; `browser-window.jsx` is a presentation frame with no app content;
`support.js` is the renderer.

**`UI-1` — the export must be committed before implementation starts.** A design
document whose authority points at a Downloads folder is one cleanup away from being
unverifiable. Copy the three files to `frontend/design/2026-07-28-mockup/` and commit
them. Nothing imports them; they are a reference artifact.

Five screens: mobile landing, mobile journey, mobile building-path, desktop landing,
desktop journey.

**`UI-2` — the mockup's phone frames are illustration, not specification.** The 52px
status bar, the 36px device radius and the `9:41` clock are drawing a phone. They are
not part of the app and must not be implemented. Likewise `@keyframes ap-caret`, which
fakes a text cursor the mockup needs because it has no real `<input>`.

## 2. Decisions the owner has already taken

Recorded so they are not reopened. Each was put to him with its alternatives on
2026-07-28.

| | Decision |
|---|---|
| **`UI-D1`** | **Faithful port of all five screens**, including the skeleton loading screen — not a visual-layer-only restyle. |
| **`UI-D2`** | **Add `GET /api/artists/{mbid}`** so a cold load can name the two endpoint artists, rather than skeletoning them or carrying names in the URL. |
| **`UI-D3`** | **Fixed bottom padding on the player bar; `viewport-fit=cover` is NOT added.** The deferred `env(safe-area-inset-bottom)` finding stays deferred and stays inert. |
| **`UI-D4`** | **A bypass press holds the old path dimmed** rather than replacing it with shimmer. Today's behaviour, kept. |
| **`UI-D5`** | **The message over the dimmed path differs per button**, because the two signals genuinely do different things and the app has never said so. |
| **`UI-D6`** | **A result line above the path is permanent; the button explainer is collapsible**, open on a first visit and remembered as closed once dismissed. |
| **`UI-D7`** | **"X steps" counts the artists in between** — what is visible on screen — not hops. |

Two further decisions were taken as the session's own and stated to him rather than
escalated, on the grounds that both are methodology:

| | Decision |
|---|---|
| **`UI-D8`** | **DM Sans is self-hosted**, not loaded from Google Fonts — a third-party request on the critical render path of a public site, for no gain. |
| **`UI-D9`** | **Approach A** — extend the token set and restyle in place, rather than build a UI primitives layer or move styling into CSS component classes first. |

## 3. Tokens and typography

`frontend/src/index.css` keeps its eight existing tokens **unchanged** and gains eight
more. Named by role, not by shade, so they read at the call site:

| Token | Value | Used for |
|---|---|---|
| `--color-label` | `#6f7580` | uppercase field labels, landing footer text |
| `--color-note` | `#7d838e` | dropdown disambiguation, card eyebrow labels |
| `--color-placeholder` | `#5c626d` | input placeholder |
| `--color-endpoint` | `#3b4048` | endpoint card border |
| `--color-border-hover` | `#343841` | card hover border |
| `--color-inert` | `#20232a` | disabled play button, skeleton base |
| `--color-inert-fg` | `#3c414a` | disabled play glyph |
| `--color-rail-mid` | `#7bb0cf` | the rail gradient's middle stop |

**Font.** `@fontsource-variable/dm-sans` (verified to exist at `5.3.0`, 2026-07-28),
imported in `frontend/src/main.tsx`, exposed as `--font-sans` in the `@theme` block.
The mockup uses weights 400, 500 and 600; a variable font covers all three from one
file. No `<link>` to `fonts.googleapis.com` and no `preconnect` — see `UI-D8`.

**Keyframes** move from the mockup into `index.css`: `ap-shimmer` (skeleton sweep),
`ap-pulse` (the loading subtitle), `ap-grow` (the loading rail). `ap-caret` does not —
see `UI-2`.

## 4. New components

Four files, each with one purpose.

**`PathSkeleton.tsx`** — the building-path screen. Props: the two endpoint artists
(each possibly `null`). Renders the `A → B` heading, the pulsing subtitle, both
endpoint cards, four shimmer rows, the `···` divider, the growing rail, and the footer
line. Display-only: it renders no play buttons and no bypass buttons, matching the
mockup.

**`RerollNotice.tsx`** — the overlay shown over a dimmed path. Props: the reason.
`pointer-events-none` so the bypass buttons stay pressable mid-rebuild — they work
today, and `usePath` aborts a superseded request safely (`usePath.ts:47`).
`aria-live="polite"` so it is announced rather than silent. Three staggered dots
supply the ellipsis, so the strings below carry no literal `…`.

**`PlayButton.tsx`** — the mockup's play and pause are CSS-border triangles and bars,
not the current `▶`/`❚❚` text glyphs. Extracted because it appears at two sizes (40px
on a card, 36px on the bar) with a disabled variant, in four places. **Its
`aria-label` stays exactly `Play`/`Pause`** — nine tests resolve it by that name.

**`PathIntro.tsx`** — the result line and the collapsible explainer. Owns its own
dismissal flag in `localStorage`. Suppressed entirely when `stopRule` is
`adjacent_only`: there is no step count to state and no bypass buttons to explain, and
`JourneyList.tsx:71` already says the useful thing in that case.

## 5. Changed components

**`ArtistSearch.tsx`** — 52px input (54px from `sm`), 19–20px value text, accent focus
ring (`box-shadow: 0 0 0 3px rgba(74,144,217,.14)` plus accent border), and the
dropdown becomes a floating card: 12px radius, 6px padding, a real shadow, 8px-radius
rows, name and disambiguation baseline-aligned.

> **`UI-3` — the label text in markup stays `From` and `To` exactly, and is uppercased
> in CSS.** `getByLabelText('From')` is an exact match; writing `FROM` in the markup
> breaks `ArtistSearch.test.tsx`, `LandingPage.test.tsx`, `e2e/path.spec.ts` and
> `e2e/responsive.spec.ts`. `text-transform` does not change `textContent`.

**`ArtistCard.tsx`** — three variants beyond today's:

- **endpoint** — eyebrow label (`Starting artist` / `Destination artist`, uppercased
  in CSS), 56px art, `--color-endpoint` border, inset top highlight, no bypass row.
  Today endpoints differ only by the absence of bypass buttons.
- **now-playing** — accent tint **and** accent border. Today only the background
  changes (`ArtistCard.tsx:38`).
- **no-preview** — art at 75% opacity and the play button rendered as an inert
  surface with a grey glyph, rather than the whole accent button at 30% opacity.

It also gains `data-testid="artist-name"` — see `UI-5`.

**`JourneyList.tsx`** — the rail gains the middle gradient stop and the `▾` arrowhead
at its foot. The `<ol>`/`<li>` structure is unchanged; see `UI-4`.

**`PlayerBar.tsx`** — the mockup's measurements, fixed bottom padding, and on desktop a
centred 620px strip rather than full-bleed. `env(safe-area-inset-bottom)` is left
exactly as it is (`UI-D3`).

**`LandingPage.tsx`** — 27px heading on mobile, 38px from `sm`, weight 500; 520px
desktop column; pill button with **dark** label text on accent (`#0f1115`, weight 600);
and the footer: three coloured dots joined by rules, then the line in §7.

**`PathPage.tsx`** — orchestrates the states in §8 and tracks the last reroll reason.

## 6. The API addition

`api/src/artistpath_api/app.py` gains one route, reusing the existing `artist_out`
helper (`app.py:104`) and the existing `ArtistOut` model (`models.py:46`):

```python
@app.get("/api/artists/{mbid}")
def get_artist(mbid: str) -> ArtistOut:
    node = store.id_by_mbid.get(mbid)
    if node is None:
        raise HTTPException(404, "unknown artist")
    return artist_out(node)
```

**Register it after `/api/artists/search`** (`app.py:113`). FastAPI matches in
declaration order, so the reverse would make `{mbid}` swallow `search`.

Pure in-memory: one dictionary lookup and four array reads. No network, no
pathfinding, no clip resolution.

**`UI-6` — the Cloudflare rate limit is unaffected and must not be touched.** It
matches `POST /api/path` with `equals`, and `NEXT.md` records that as deliberate. A new
`GET` route does not intersect it.

On the frontend: `getArtist(mbid, signal)` in `api/client.ts` alongside the existing
three callers, and a `useEndpoints(fromMbid, toMbid)` hook that fires **only** when the
path has not already supplied names.

**Track title and artwork need no new route.** `getTrack(mbid)` requires only an MBID,
and both endpoints are always on the path, so those two clip requests happen a moment
later regardless — firing them during the load moves them earlier and they are cached.

## 7. Copy, fixed here

Fixed at definition time so wording cannot be reshaped later to fit an implementation.

> **⚠ Two landing strings were changed by the OWNER on 2026-07-28, after the work shipped.**
> Recorded here rather than rewritten, because the point of this table is that it is frozen:
> the rule it enforces is that a *session* cannot reshape copy, not that the owner cannot.
> - **Landing footer: REMOVED.** The decorative three-dot rail above it stays.
>   `LandingPage.test.tsx` now asserts the line is *absent*, so restoring it is deliberate.
> - **Landing intro** was `Name two artists and hear a smooth path between them.` It is now
>   `Name two artists and hear the route between them. Each step lands on someone their
>   listeners share, so one sound eases into the next.` The brief was to explain the **how**
>   at user level and tie to coherence — and explicitly **not** to promise obscurity, because
>   the first path between two famous artists is expected to be famous
>   (`WHAT-GOOD-LOOKS-LIKE.md` value 9). Obscurity is introduced by the bypass explainer on
>   the journey page, which is unchanged.

| Where | String |
|---|---|
| Landing footer | ~~`Path length varies — 30 seconds each`~~ — **removed, see above** |
| Loading heading | `{from} → {to}` |
| Loading subtitle | `Listening for the steps between them…` |
| Loading footer | `This usually takes a few seconds` |
| Reroll, `dislike` | `Steering around that sound` |
| Reroll, `known` | `Digging for someone newer` |
| Reroll, reset | `Back to the original path` |
| Result line | `We found a path between these artists in {n} step{s}.` |
| Explainer toggle | `What do the two buttons do?` |
| Explainer, ✕ | `Not for me — steers away from that artist and the ones around them, so you get a different sound rather than a near-identical substitute.` |
| Explainer, ✓ | `I know them — digs for someone less familiar, since you've already covered the obvious route.` |
| Explainer, both | `Either one rebuilds the whole journey, so every artist between your two can change — not just the one you pressed.` |
| Explainer dismiss | `Got it` |

The three reroll strings carry **no** trailing ellipsis; the animated dots supply it.
`{n}` is `artists.length - 2` and the singular is `1 step`.

**The two per-signal strings are accurate, not decorative.** `dislike` applies a soft
penalty to the disliked artist's *neighbourhood*, decaying over `avoid_radius` hops;
`known` relaxes the obscurity floor more aggressively. Both are described in
`CLAUDE.md`'s pathfinding section. If either mechanism ever changes, these strings are
wrong and are part of the blast radius.

Unchanged and carried forward: `No preview available`, `▮▮▮ now playing`, and the
`adjacent_only` line at `JourneyList.tsx:71`.

## 8. Path page states

| `usePath` state | Renders |
|---|---|
| `loading`, `artists.length === 0` | `PathSkeleton`, endpoints from `useEndpoints` |
| `loading`, `artists.length > 0` | the list at 60% opacity + `RerollNotice` |
| `ready` | `PathIntro` + the list |
| `error` | `PathStatus`, unchanged |

`usePath.ts:40` already preserves `prev.artists` across a reroll, which is what makes
row 2 possible without new state. `PathPage` holds the last reason — `dislike`,
`known` or `reset` — set on the press and cleared when the path lands.

A retry after a timeout renders the skeleton, because the error branch sets
`artists: []` (`usePath.ts:45`). That is correct: there is nothing on screen to hold.

## 9. Error handling

Unchanged from today, with one rule added.

> **`UI-7` — a failed endpoint-name lookup is non-fatal and never surfaces.** The
> skeleton falls back to unnamed endpoint cards and the heading is omitted. `POST
> /api/path` is the real request; a decorative lookup must not be able to turn a
> working page into an error page. `useEndpoints` therefore swallows its own failures
> and never feeds `PathStatus`.

## 10. Constraints the implementation must not break

Each is load-bearing and each has a test that fails if it is broken — except `UI-5`,
which is the one that fails for the *wrong reason*.

- **`UI-4` — the journey stays an `<ol>` with one `<li>` per artist.** Three e2e specs
  address cards as `ol li` and index into them (`path.spec.ts:20`,
  `playback.spec.ts:54,65,71,89`, `responsive.spec.ts:19,27`).
- **`UI-5` — replace the `.font-semibold` locator with `data-testid="artist-name"`.**
  `e2e/responsive.spec.ts:38` currently finds the artist name by a literal Tailwind
  class. That is a styling hook doing test duty, and this work moves exactly those
  classes. It survives today only by luck — the mockup's name is also weight 600 — and
  a failure here would look like a layout regression while being nothing of the kind.
  This is the one pre-existing defect this design fixes rather than works around.
- **The bypass markup stays a single copy.** `ArtistCard.tsx:59` carries the reason:
  Playwright strict mode fails on two matching elements, so a separate mobile and
  desktop rendering of the same buttons breaks the e2e suite. Mobile and desktop
  differ by responsive classes on one element, as they do today.
- **`aria-label` values stay `Play` and `Pause`**; the accessible names `not for me`,
  `i know them`, `find path`, `new path`, `reset path`, `clear exclusions` and
  `start a journey` are all resolved by tests and stay as they are.
- **The text `now playing` stays present** — five unit tests assert on it
  (`JourneyList.test.tsx:27,80,85`, `PathPage.test.tsx:129,138`) and
  `playback.spec.ts:54` matches it in `innerText` to locate the playing card.

## 11. Testing

**Every existing test must pass unchanged.** That is the check that the restyle did not
move a hook, and it is worth more here than any new test.

New coverage:

- `PathSkeleton` renders both endpoint names when supplied, and degrades without them.
- `RerollNotice` renders the correct string for each of the three reasons.
- `PathIntro` — the count, the singular, suppression under `adjacent_only`, and that
  dismissal persists across a remount.
- `PlayButton` — disabled state, and that the label still reads `Play`/`Pause`.
- `GET /api/artists/{mbid}` — a known MBID returns the artist; an unknown one 404s;
  and it does not shadow `/api/artists/search`.

Then, from `frontend/`: `npm run lint`, `npm test`, `npm run build`, and
`npm run test:e2e` with the API running on `:8000`. From `api/`:
`UV_LINK_MODE=copy uv run --extra dev pytest -q`. Then the Snyk `snyk_code_scan` tool
over the modified first-party code, per the standing instruction, fixing and rescanning
until clean.

**Structural tests cannot answer whether this looks right.** A use-the-app entry is
owed at closeout, and it should ask for the landing screen, a first load, a shared
link, and a bypass press specifically.

## 12. What this means at deploy time

Recorded because two standing deferrals intersect this work and neither is obvious from
the diff.

- **`UI-8` — this is the next FRONTEND publish, so the `--prune` deferral comes due.**
  `NEXT.md` carries it with that exact trigger: `infra/src/artistpath_infra/sync_frontend.py`,
  not the next `cdk deploy`. The correction is already recorded there — the Track B
  handoff had wrongly attributed the trigger to `PW-5`'s deploy.
- **The API change means an App Runner deploy.** `NEXT.md` defers "App Runner's CLI tags
  vanish if the service is replaced" against exactly that. The two `tag-resource` calls
  are in `infra/README.md` §7. A routine deploy should not *recreate* the service, so
  this is a check rather than an expected cost.
- **App Runner stays excluded from CDK tagging.** `test_app_runner_is_deliberately_left_untagged`
  pins it and must not be deleted; `NEXT.md` records that tagging it forces a
  replacement that cannot succeed.

## 13. Out of scope

Named so they are not picked up in passing.

- `viewport-fit=cover` and the inert `env(safe-area-inset-bottom)` — `UI-D3`.
- Anything touching routing, the graph, the cost function, or clip resolution.
- `BYP-13` (a card playing a clip by a different artist of the same name). Live, and
  unrelated to this work.
- A UI primitives layer. If the interface grows past this, that is the right move
  *then*, on evidence.
- Gate 3. Removing the password was not Gate 3 and neither is this; the Gate 2→3
  blocking set is unchanged by a restyle.

## 14. Weakest link

**The design's load-bearing assumption is that the mockup's palette and the app's
tokens are the same eight values.** That was read off `index.css:3-12` and the export's
inline styles on 2026-07-28 and is what makes this a restyle rather than a re-skin. If
it is wrong anywhere, the diff is larger than described but nothing in the approach
changes.

**The thing most likely to go wrong in execution is `UI-5`'s class**, or another
test-to-styling coupling like it that has not been found. One was found by reading; a
second would surface as a test failing for a reason unrelated to what it tests. The
mitigation is §11's first line — run the existing suite before writing any new test.
