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

**Where:** locally, after merging #212 and pulling `main` in `C:\dev\music-app` — the Vite server on
:5173 picks the new files up on its own; nothing to restart. Not on unsung.fm (not deployed).

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
