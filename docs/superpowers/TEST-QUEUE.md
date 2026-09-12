# Use-the-app test queue

**Role: ACTIVE, permanent. A CHECKLIST AND NOTHING ELSE.** The app is at **https://unsung.fm**.

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

> **Budget: 70 lines, and it is at 70**, so a new check must displace something. That is the
> pressure working. It reached **255 on 2026-09-12** because sessions appended reasoning instead of
> checks; reasoning belongs in the archive, the PR body or the execution log. Checked at `closeout`
> **B6-budget**. **Never compress a live check to fit** — discharge one, or raise the budget and
> say why.

---

## ▶ LIVE NOW — one pass, about 20 minutes, phone first

*Everything below is deployed and exercisable. It merges the three entries queued 2026-09-04 and
2026-09-08, which all went live before you read this and overlapped heavily. Full original notes,
and the reason each check exists: [`archive/TEST-QUEUE-notes-2026-09.md`](archive/TEST-QUEUE-notes-2026-09.md).*

**On your phone**

- [ ] **1. First screen.** New name, logo and typeface, plus a line saying how many artists are on the map. It should read roughly 58,000. **A missing line is a failure**, because that number is read live from the server.
- [ ] **2. A ready-made journey from the front page.** Count the artists between the two ends. It should match the number of steps the button claimed.
- [ ] **3. A journey card.** Artwork, name, track, play, and a `›`. **Dates, or Spotify and Apple links, still on the card itself means the new layout did not ship.**
- [ ] **4. Press `›` on a middle artist.** A panel slides up. It holds the artist's details, both streaming links, "try another track" and reroute. Close it with the ✕ and with a press outside it. **Both must work.**
- [ ] **5. The line under each song title**, on several cards. Then find one where it is **missing entirely** and note who.
- [ ] **6. Both streaming links, from inside the panel** — once on a well-known artist, once on the most obscure artist in the journey. The obscure one is where a wrong match shows up.
- [ ] **7. Reroute from inside the panel**, five or six times, across different journeys. Read the wording on the control before the first press. Then look **below the journey** for the list of who you skipped.
- [ ] **8. Press play.** The bottom bar should name the track, show a moving line, count seconds, and say which stop you are on.
- [ ] **9. Press Share**, then open the link in a new tab. Same journey, **including any rerouting you had already done**.
- [ ] **10. Does a clip actually play?** No test here can answer this. It is the whole reason this file exists.

**Either device**

- [ ] **11. Press Back a few times** after rerouting. Each press should undo one reroute.
- [ ] **12. Open a journey link you saved weeks ago.** It should still open the same journey.
- [ ] **13. On a laptop, the Escape key closes the panel**, and Share says "Link copied".

**What "wrong" looks like anywhere:** a blank white screen, a broken image where the logo should
be, a panel that will not close, a clip that plays the wrong artist, or a shared link that opens a
different journey from the one you were looking at.

---

## ⚠ Two questions that are NOT defect checks

**Flagged 2026-09-12: these sit against rule 2 above and are the owner's to strike or keep.** They
were queued before that rule was applied to them, and both have a completion state, which is why
they were not simply deleted.

- [ ] **Reroute now takes two presses instead of one.** Does the second press read as a cost, or as a safeguard against pressing it by accident?
- [ ] **The clock says 0:29 where the card says 0:30.** That is the true length of what Deezer sends, left honest rather than rounded. Say if you would rather they agreed.
