# Handoff — Dig-deeper exploration, for the review session, 2026-09-29

**Role: ACTIVE — this is the CURRENT handoff for the exploration.** It is *not* in the
`docs/superpowers/` handoff chain and does not state project status: for that read
[`docs/superpowers/NEXT.md`](../docs/superpowers/NEXT.md). EXPLORATORY: nothing here is evidence
(the owner's brief; see `REPORT.md`'s first line).

**Where this lives:** branch `charlessavage90/dig-deeper-exploration`, draft PR #264. Nothing is on
`main`. Start the review session from that branch.

## What the owner wants from the next session
He has used the practice room on three pairs and wants a fresh session to review **the results, his
feedback, and the options** with him. What goes to formal testing, if anything, is his call.

## Read in this order
1. `REPORT.md`: what died, the four finalists as a listener hears them, what cuts against them.
2. **`practice-room/logs/2026-09-29-notes.md`**: **his 31 notes, verbatim**, each beside the journey on
   screen. The raw log, `logs/2026-09-29.jsonl`, holds every journey shown (119) as well.
3. `practice-room/README.md`: how to run the room again, add columns and read the logs.
4. `ROUND1.md`, then `r2-*/NOTES.md` for any finalist he wants to go deeper on (each NOTES owns its
   own figures).

## Not in any other file (the coordinator's, labelled as such)
- **His fame-score observation, checked against the map (measured, nothing inferred).** ListenBrainz
  listener counts behind the fame score: Led Zeppelin 338,485 (100.0), The Format 76,325 (98.4),
  Royal Blood 10,147 (86.5), Death Cab for Cutie 306,617 (99.9), Motion City Soundtrack 102,750 (99.0),
  Imagine Dragons 140,793 (99.4), Greta Van Fleet 6,934 (81.5), Morgan Wallen 6,826 (81.2),
  Chappell Roan 12,212 (88.5), Bad Bunny 15,885 (91.0). The artists were hand-picked, not sampled.
  The fame proxy's adoption record is `docs/superpowers/PRODUCT-REQUIREMENTS.md`, Definitions (lines
  63–81 as of this commit). **Form your own view of what it implies**; the coordinator's reading was
  given to the owner in conversation and is deliberately not written here.
- **The rater** is Sonnet, called through the local `claude` CLI (`kit/rate.py`). Its ratings are
  cached per artist pair in `kit/step_cache.jsonl`, and every coherence figure depends on it.
- **The kit's press policy** always pressed the most famous middle artist, often the card next to an
  endpoint. The owner pressed freely, so his experience and the kit's numbers are not the same test.
- **Decided against:**
  - A third round. The brief's stop rule (2–4 variants that clearly dig and pass the screen) was met.
  - The "shaped toll" as a finalist. It is similar to the fame ladder and the slowest candidate (about 1.3–2.6 s per journey; r2-shaped/NOTES.md);
    it stays available as a runner-up (`PR_ALL=1`).
- **Not done, deliberately:**
  - No GitHub issues were filed and `NEXT.md` was not edited. The brief keeps exploration out of
    the formal record, and what enters it is the review session's question to put to the owner.
  - The review session is the address of every open item below.

## Open items (address: the review session)
- Which finalist(s), if any, go to formal testing, on pairs not in `pairs-used.txt`.
- Whether the fame score's mis-ranking (his observation, above) must be dealt with first. Every
  finalist steers by it.
- **What the coordinator would do next if continuing:** combine the fame ladder with the
  shared-neighbours step measure, *after* checking the fame score against a second source across
  the whole map. His notes on Led Zeppelin → The Format at presses 7–10 cut against every finalist,
  which the 20-pair kit numbers did not predict:
  - Local repair and Fame ladder: "no novelty".
  - Shared neighbours: "jumped back out of novelty" at press 10.
  - Fame toll: the press-10 note names two artists with millions of monthly listeners.

## In flight
Nothing. No server is running (closeout stopped the practice room; its log was verified copied
first), and no subagent is running.
