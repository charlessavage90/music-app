# Use-the-app test queue

**Role: ACTIVE, permanent. A CHECKLIST AND NOTHING ELSE.** The app is at [**https://unsung.fm**](https://unsung.fm).

**How to use it.** Run down the boxes in order, on the device each one names. Report back in one
message: the numbers that failed, what you saw, and a URL for anything broken. Anything you did
not get to is simply still unticked. **A session discharges the items you report and moves them to
[`archive/TEST-QUEUE-discharged.md`](archive/TEST-QUEUE-discharged.md)**, so what is left here is
always what is still to press.

**An empty file is a valid and normal state.** An entry is written only when there is something
you can actually press. Silence never means a session forgot.

**Two rules govern what may be added** — both the owner's, and a session that breaks either has
written the wrong thing:

1. **Only a change he can exercise.** Not "here is what I did this session". That belongs in the
 closeout report and the PR body, which he reads at the time.
2. **Only things that can be found *wrong*** — a defect, a regression, something that does not
 work. **Never "tell me how it feels."** His continuous judgement of the app has no completion
 state, so an entry for it could never be discharged. Where a session genuinely needs his taste,
 that is a designed evaluation with its own pre-registration, not a queue entry.

> **Budget: 70 lines** — a new check past it must displace something. That is the
> pressure working. It reached **255 on 2026-09-12** because sessions appended reasoning instead of
> checks; reasoning belongs in the archive, the PR body or the execution log. Checked at `closeout`
> **B6-budget**. **Never compress a live check to fit** — discharge one, or raise the budget and
> say why.

---

## QUEUED 2026-09-24 — the six UI fixes from your pass (PR #212)

**Where:** on unsung.fm — **deployed 2026-09-24 (`759e80c`), pressable now.** Not on the local
servers, which stay on the `LBA-G5` candidate.

- [ ] 1. **Desktop, landing page.** The "Build the path" button no longer shimmers. The example card
  says "A path, seven stops", and its coloured line runs through the centre of every dot, cyan dot
  at the top, pink at the bottom. The three example chips say 5, 6 and 8 stops.
- [ ] 2. **Desktop, any journey.** The number in the top-right tile equals the number of cards on the
  page, endpoints included, and says "stops". Press play on any card: the bar's "Stop N of M" has
  the same M. Open any card with ›: the panel's "Stop N of M" has the same M.
- [ ] 3. **Desktop, any journey.** Click the Unsung.fm mark top-left: you land on the landing page and
  the clip stops. On the landing page itself the mark does nothing when clicked.
- [ ] 4. **Desktop, open a few panels.** Wrong = a date line ending in a bare dash ("1985–"). Right =
  "since 1985", "until 1990" or "1985–1990". Hover Dig deeper: hand cursor, and it is violet, not pink.
- [ ] 5. **Desktop, no panel open, press play on a middle card:** that artist's panel opens. Now, with
  that panel open, press play on a different card: the panel does not change. Close the panel.
- [ ] 6. **Phone, press play on any card:** no panel opens; the clip plays.
- [ ] 7. **Any width.** Press Dig deeper four or five times so "Artists you skipped" is long, with a
  clip playing. Scroll to the bottom: the last skipped name sits fully above the playing bar.

## QUEUED 2026-09-24 — the issues sweep (PRs #216–#219)

**Where:** on unsung.fm — the same 2026-09-24 deploy, pressable now.

- [ ] 8. **Desktop, clip playing.** Drag the volume slider in the bottom bar: loudness changes, the clip
  does not restart. Play another card: same level. **Phone:** no slider.
- [ ] 9. **Clip playing.** Pause with a keyboard media key or headset button: the play button shows
  Play, not Pause. **Phone:** the lock screen names the artist.
- [ ] 10. **Any journey, clip playing.** Press Dig deeper, then the browser's Back: the audio stops at
  once, not when the old path reappears.
- [ ] 11. **Turn wifi off, press play on a card you have not played.** Wrong = the bar vanishes. Right
  = it stays, says it couldn't reach the preview service, with Retry. Wifi on, Retry: it plays.
- [ ] 12. **Search box, desktop and phone.** Type a name, then press Escape / click or tap elsewhere: the
  list closes. Typing again and clicking a name still picks it.
- [ ] 13. **Take a journey URL and paste the first artist's id over the second.** Wrong = "Something
  went wrong". Right = a sentence saying to pick two different artists.
- [ ] 14. **Press Dig deeper once, copy the URL, delete its last id (and the comma) and reload.** A
  notice says the link looks cut short. The browser tab names both artists.
