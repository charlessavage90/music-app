# F1 — every journey gets at least one stop: design, 2026-07-25

**Role: ACTIVE.** Design for the one open Gate 1 item. Supersedes nothing.

**Requirement, already decided by the owner and not reopened here:** *every journey
needs at least one stop.* Settled 2026-07-25; the success condition is owned by
`../2026-07-25-gate1-clips-and-ux-execution-log.md` **§16** and **is not restated in
this document** — cite §16. Two prior deferral conditions drifted in exactly that
kind of restatement, and one lapsed silently.

**Not path-quality work.** This adds a structural constraint over the *result* and
introduces no new scoring, no new weight, and no rebuild. The cost function,
`ApiConfig` and the graph artifact are untouched. The path-quality pause stands.

---

## 1. The situation, in one paragraph

Ask for two artists who are directly connected and you get two cards and nothing to
press — the bypass buttons are hidden on the endpoints, correctly, so the page is a
dead end. `Radiohead → Weezer` is the reported case. For most such pairs a stop can
be inserted; for a minority it genuinely cannot, because one of the two artists has
only that single connection in the whole graph. Why that happens, and how many are
affected, is owned by `../findings/2026-07-25-mutual-knn-stranding.md` (`MKS-6`) and
is not restated here.

## 2. Mechanism

Run the search as today. **If the result is exactly the two chosen artists**, run it
again with the direct connection between them forbidden.

- A route exists → return it. That is the forced stop.
- No route exists → return the original two-card path, and say so in the response.

The second search runs **only** in the case that already returned two cards, so the
common path costs nothing extra.

**The detour is chosen by the existing cost function, unrestricted.** No new
criterion, no cap on length, no preference for a particular kind of intermediary.
This is the design's central choice and it is what keeps the work outside the pause:
inserting an artist by any *new* rule would be scoring, and scoring is paused.

Consequences accepted deliberately. **The two figures below come from a throwaway
design-time prototype on a sample of 18 pairs, are owned by nothing, and must not be
cited or restated** — they are here to show the shape of the trade, and anything
resting on them needs its own measurement:

- **Detour length varies.** Usually one stop; a sampled pair produced seven, because
  a chain of close matches can price below one distant jump. Not capped — the
  roadmap already records that where a journey stops feeling like one is a
  use-the-app question, and capping now would invent a threshold to answer it.
- **Famous → famous inserts a famous artist.** `Radiohead → Weezer` inserts The
  Beatles. On a sample of 18 adjacent pairs only 2 inserted artists were top-1 % by
  popularity, so this is the exception rather than the rule, but it is real and the
  owner will meet it. Left alone: suppressing it is a scoring preference.

**Bypass is unaffected in mechanism and included in scope.** The rule applies to
every path request, including rerolls, because the requirement is unconditional. The
second search honours hard exclusions exactly as the first does, so a detour is never
built through an artist the user rejected; if exclusions leave no detour, the
fallback applies.

## 3. What the response carries

`PathResponse` gains one field, `stop_rule`, with three values:

| value | meaning | UI today |
|---|---|---|
| `natural` | the least-cost path already had at least one stop | nothing |
| `forced` | the two were neighbours; a stop was inserted | nothing |
| `adjacent_only` | the two are neighbours and nothing connects them both | renders the note |

**Only the router can know this.** Once a stop is inserted the result is
indistinguishable from an ordinary path, so the frontend cannot re-derive it. That is
why the field exists rather than being computed client-side.

`stop_rule` is a **wire contract**, so it is snake_case on the wire and camelCase
(`stopRule`) in the frontend, matching `preview_url` → `previewUrl`. It is not a
popularity- or degree-derived quantity, so the currency-in-the-name convention does
not apply to it.

## 4. What the user sees

For `adjacent_only`, a line **between the two cards**, in the position the owner
selected:

```
┌──────────────────────────────┐
│  Doves                    ▶  │
└──────────────────────────────┘

   These two are next to each other —
   there's no artist in between.

┌──────────────────────────────┐
│  Elbow                    ▶  │
└──────────────────────────────┘
```

Wording is not final and is the owner's to change; the structural requirement is that
the page explains itself rather than presenting a dead end.

`natural` and `forced` render exactly as today. **A forced stop is deliberately not
announced** — the user asked for a journey and got one; labelling it would draw
attention to machinery they have no use for.

## 5. Files

| file | change |
|---|---|
| `api/…/pathfinding.py` | `find_path` gains an optional forbidden edge; new wrapper returns `(path, stop_rule)` |
| `api/…/models.py` | `PathResponse.stop_rule` |
| `api/…/app.py` | call the wrapper; pass the value through |
| `frontend/src/api/types.ts` | `StopRule` type; path result shape |
| `frontend/src/api/client.ts` | `buildPath` returns artists **and** `stopRule` (today line 33 discards everything but `artists`) |
| `frontend/src/hooks/usePath.ts` | `PathState` carries `stopRule` |
| `frontend/src/routes/PathPage.tsx` | pass it to `JourneyList` |
| `frontend/src/components/JourneyList.tsx` | render the note when `adjacent_only` |

`PathStatus.tsx` is **not** the home for this: it renders error states, and this is a
successful result.

## 6. Testing

**Router, over small hand-built graphs** — the existing pathfinding tests' style:

1. Two artists with a common neighbour → three or more cards, `forced`.
2. Two artists whose only link is to each other → two cards, `adjacent_only`.
3. Two artists needing several hops → unchanged path, `natural`.
4. Adjacent pair whose only detour is a hard-excluded artist → two cards,
   `adjacent_only`. Guards that the second search respects exclusions.
5. Adjacent pair where the endpoints themselves are excluded → endpoints still never
   skipped, as today.

**Frontend:** `JourneyList` renders the note on `adjacent_only` and not on the other
two; `client.ts` surfaces `stopRule`. Unit level is sufficient — this is render-on-a-
flag, with none of the timing that made the playback fixes need real Chrome.

**Not a test:** that any *particular* artist gets inserted. That is the cost
function's output and would freeze a path-quality decision into a test.

## 7. Verification against the live graph

Before merge, against the adopted artifact:

- `Radiohead → Weezer` returns three or more cards where it returns two today.
- `Doves → Elbow` returns two cards and `adjacent_only`.
- A handful of ordinary paths are **byte-identical** to their current output —
  nothing but the two-card case may change.

That third check is the important one: the whole design rests on the claim that
non-adjacent paths are untouched, and it is cheap to demonstrate rather than assert.

## 8. Open, and the owner's

- **Wording of the note.** Placeholder above.
- **Whether a seven-stop forced detour feels right.** Only use will answer it; it
  belongs in `TEST-QUEUE.md` with this work, not in a threshold here.
