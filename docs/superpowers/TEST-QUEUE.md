# Use-the-app test queue

**Role: ACTIVE, permanent.** Things the owner needs to press, and what they found. This is
the async counterpart to the test suites — it catches the defect class that code review and
mocked tests structurally cannot.

> ## 📍 THE APP'S ADDRESS IS `https://unsung.fm`, since 2026-09-03
>
> **Use it in every new entry.** Entries dated before 2026-09-03 name
> `musicapp.cmiller.io` and are left exactly as written — they record what was pressed and
> when, and that name is what was pressed. It is **not** dead: a Cloudflare Redirect Rule
> 301s it to `unsung.fm` with the path preserved, so an old journey link still opens the
> same journey. Nothing below needs re-running because of the move.

> ## ⛔ WRITE AN ENTRY ONLY WHEN THERE IS SOMETHING TO PRESS
>
> **The trigger is a CHANGE THE OWNER CAN EXERCISE, not a closeout.** If a session changed
> nothing he can press, it writes **nothing here** — no entry, no note, no "nothing to test
> this time". **Silence already means nothing is queued**, because this file contains only
> things to do.
>
> **Where the other thing goes.** "Did my app move?", the ports being empty, what the session
> did and why it does not reach the app — all of that belongs in the **closeout report to the
> owner and the PR body**, which he reads at the time. It is a fact about one session, not a
> durable record, and storing it here is what broke this file.
>
> ## ⛔ AND ONLY FOR DEFECTS AND FUNCTIONALITY — NEVER FOR LONG-RUN JUDGEMENT
>
> **Owner ruling, 2026-08-07.** This file is for things that can be found *wrong*: a defect,
> a regression, a thing that does not work. It is **not** for his ongoing evaluation of how
> the app *feels* — where novelty shows up, whether a journey is satisfying after several
> days and weeks of living with it. That evaluation is real, it is continuous, and **he is
> doing it** — but it has no completion state, so an entry for it can never be discharged and
> would sit here forever looking like a lapse.
>
> **So: never queue "tell me how it feels".** He raised this himself when closing the
> `MSW-` map entry: he had fully exercised the new map for defects and found none, while
> still forming a view on the experience — and stated that the second half is not an open
> queue item. Where a session genuinely needs his taste (a blind listen, a
> WHAT-GOOD-LOOKS-LIKE calibration), that is a **designed evaluation with its own
> pre-registration**, not a queue entry.
>
> *Rule changed 2026-08-05, and the measurement is why: **42 of 69 entries were "nothing to
> test", 1,630 lines — 57% of the file**, at an average of 39 lines each, which is about
> three-quarters the length of a real test instruction. The old rule said "one entry per
> closeout", so a session with nothing to queue still had to write something; having written
> something, it justified it; and the write-for-someone-holding-a-mouse rule then filled the
> vacuum with session narrative, because an entry with no test in it has no other content
> available. That is how a test queue became a summary execution log. The forty "nothing to
> test" entries are archived at [`archive/TEST-QUEUE-nil-entries.md`](archive/TEST-QUEUE-nil-entries.md);
> what stays here is what was actually exercised.*

**Newest first. Mark an entry DONE with the date and what it found, or DONE — nothing found.
Do not delete entries; the record of what was exercised is the point.**

> **⚠ HOW TO COUNT WHAT IS ACTUALLY OUTSTANDING — read this before reporting a number.**
> Discharging an entry **prepends a new `## DONE` heading above it** and keeps the original
> `## QUEUED` heading in place, under the line *"Original queued text follows."* The original
> heading is preserved deliberately — it is the record of what was asked — **but it means a
> grep for `## QUEUED` returns discharged entries and over-reports.**
>
> **⚠ SINCE 2026-09-05, DISCHARGED ENTRIES LEAVE THIS FILE** — `closeout` `C1-demote` moves
> them to [`archive/TEST-QUEUE-discharged.md`](archive/TEST-QUEUE-discharged.md). **So the
> over-reporting mechanic described above can no longer occur here**, and counting is just
> counting the entries present. The rule is kept because it still governs both archives, where
> discharged entries do carry both headings — and as a safety net if an entry is ever left in
> place.
>
> **An item is live only if its topmost heading says so.** As of **2026-09-05** that is **ONE
> item**, written 2026-09-04. *(This block read "**ZERO items** — the queue is empty" until
> 2026-09-05, dated 2026-09-01 and never re-counted, while a live entry sat below it. That is
> the incident below repeating inside the warning written to prevent it, which is why the count
> is re-counted at each closeout and never carried forward.)*
>
> **This cost six consecutive closeouts**, each flagging a backlog that did not exist, the
> count itself stale, each carrying the claim into a handoff and into `NEXT.md` without
> re-reading the file. The check that would have caught it — open one and look at what is
> above it — takes about a minute.

> **✅ EXPIRED 2026-07-27 — entries may ask for a phone.** The Gate 2 cutover happened: there
> is a hosted URL and a phone can reach it. *Retained because the constraint's expiry is the
> record: before the cutover the app ran only on the owner's desktop, so a phone entry was not
> merely inconvenient but unrunnable, and would sit here looking untested when it was
> impossible.*

---

## ▶ QUEUED (latest) — 2026-09-04 — one button instead of two, a list of who you skipped, and a way to hear a different song

**Not live yet.** This is on a branch waiting for you to merge it. Once it deploys, three
things on the journey page are different, and one of them is the first thing anyone you share
the app with will see.

### What to exercise — about ten minutes

1. **Build a journey and look at the bottom of a middle card.** There used to be a strip you
   pressed to open a little panel with two choices. Now there is one control, directly on the
   card, and no panel to open. Press it.
2. **Read the wording on that control before you press it.** It is now the entire explanation
   of what the button does — there is no second option to compare it against. If it reads as
   "I don't like this artist", it is wrong: pressing it takes you to someone *similar but less
   well known*, which is close to the opposite.
3. **Press it three or four times, then look below the journey.** There is a new panel listing
   the artists you skipped, most recent first. Check the names are right and in the order you
   pressed them.
4. **Press Back a few times.** The journey and that list should both wind backwards together.
5. **On a card that is playing, look under the song title for a way to hear a different track
   by the same artist.** Press it. You should get a different song by the same person, and the
   card goes quiet — press play again to hear it. **On some artists this will not appear at
   all**, and that is correct: they only have one playable track.
6. **Open a journey link you saved weeks ago.** It must still open the same journey it always
   did.

### What "wrong" looks like

- **Any wording on that one control that sounds like rejecting the artist**, rather than
  digging for someone less known.
- **A skipped artist missing from the list**, listed in the wrong order, or a row that says an
  artist is no longer in the map when they plainly are.
- **An old saved link opening a different journey than it used to**, or not opening at all.
  This is the most serious thing on the list.
- **"Try another track" giving you the same song again**, or appearing on a card and then
  doing nothing.
- **A card left silent with no way to get sound back** after trying another track.

### Two things that are expected and are NOT faults

- **The second button is gone on purpose.** The old one that steered sideways away from a
  sound has been removed; only "dig deeper" remains. Everything underneath it still exists, so
  restoring it later is one small change.
- **For a little while after the deploy, cards may take slightly longer to find their clip.**
  The way clips are remembered changed, so the stored ones are discarded once and rebuilt. It
  settles on its own.

**Paste the URL for anything you find.**

**Wants a closer look than a defect: how the one-button version feels after a few days.** That
is your ongoing evaluation, not a test, and it deliberately does not live in this file.


---

**Discharged entries live in [`archive/TEST-QUEUE-discharged.md`](archive/TEST-QUEUE-discharged.md),
frozen and never edited** — and the entries that queued nothing live in
[`archive/TEST-QUEUE-nil-entries.md`](archive/TEST-QUEUE-nil-entries.md). Neither is work.
**This file holds only what is still to be pressed**, so an empty file below this line is a
valid and common state.
