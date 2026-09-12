# Test-queue notes — the full prose behind the 2026-09 checklist

**Role: HISTORICAL. Frozen from here on.** This is `TEST-QUEUE.md` as it stood on 2026-09-12,
immediately before it was cut down to a checklist. **Verbatim with one mechanical exception,
stated so nobody has to diff for it:** four relative links reading `archive/TEST-QUEUE-…` were
repointed to `TEST-QUEUE-…`, because this copy sits *inside* `archive/` and those targets are now
its siblings. No other character was changed. **Nothing here is a live
instruction**: the live list is [`../TEST-QUEUE.md`](../TEST-QUEUE.md), and where the two
disagree the checklist governs, because it resolved a contradiction these entries contain.

**Why it was kept.** Three queued entries, none discharged, carrying real reasoning about what
each check is *for*. The checklist keeps every distinct check and drops the paragraphs. This file
is where the paragraphs went, so a session that needs to know why a step exists can read it and
the owner never has to.

**One contradiction it contains, resolved in the checklist, not here.** The 2026-09-08 rename
entry says the Spotify and Apple links have moved off the card into the detail panel, and the
2026-09-08 facts entry still says to look for them at the bottom of the card. **The panel is
correct**, verified 2026-09-12 from the component tests: `ArtistCard.test.tsx` asserts no Spotify
link is rendered, `ArtistDetail.test.tsx` asserts one is.

---

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
> test" entries are archived at [`archive/TEST-QUEUE-nil-entries.md`](TEST-QUEUE-nil-entries.md);
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
> them to [`archive/TEST-QUEUE-discharged.md`](TEST-QUEUE-discharged.md). **So the
> over-reporting mechanic described above can no longer occur here**, and counting is just
> counting the entries present. The rule is kept because it still governs both archives, where
> discharged entries do carry both headings — and as a safety net if an entry is ever left in
> place.
>
> **An item is live only if its topmost heading says so.** As of **2026-09-08** that is **TWO
> items**, written 2026-09-04 and 2026-09-08. **Both are blocked on the same deploy**, and the
> 2026-09-08 one additionally needs a new graph file uploaded — so they are exercisable
> together, in one sitting, once you have deployed. *(This block read "**ZERO items** — the queue is empty" until
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

## ▶ QUEUED (latest) — 2026-09-08 — the app is called Unsung.fm now, and it looks different

**✅ LIVE at https://unsung.fm** — deployed 2026-09-08. The biggest visible change the app has
had: a new name, a new look, and the reroute button has moved. **The two entries below went
live in the same deploy**, so their steps are exercisable too — read their notes first, because
this change moved things they describe.

### What to exercise — about fifteen minutes

1. **Open it on your phone and just look at the first screen.** New name, new logo, new
   typeface, and a line saying how many artists are on the map. That number is read live from
   the server, so if the line is missing entirely something is wrong. It should say roughly
   fifty-eight thousand.

2. **Press one of the ready-made journeys on the front page.** Each claims a number of steps.
   When it loads, count the artists between the two ends — the claim should match. Those
   numbers are written into the page rather than measured on each visit, so a mismatch means
   the map has shifted underneath them and I need to know.

3. **Look at a journey card.** It should carry only what you need in order to listen: artwork,
   name, track, a play button, and a › button. If the country-and-dates line or the Spotify and
   Apple links are still on the card itself, the new layout did not ship.

4. **Press the › on an artist in the middle.** On a phone a panel slides up from the bottom; on
   a laptop it opens beside the journey. That panel is where the artist's details, both
   streaming links, "try another track" and the reroute button now live. **Close it three ways:
   the ✕, a press outside it, and the Escape key on a laptop.** All three should work.

5. **Reroute from inside that panel, five or six times, on different journeys.** This is the
   part to form an opinion about. It takes two presses now instead of one, and you said we may
   want to revisit that. Tell me whether the second press reads as a cost or as a safeguard
   against pressing it by accident.

6. **Press play and watch the bar along the bottom.** It should name the track, show a line
   that moves, count the seconds, and say which stop you are on. The clock says 0:29 where the
   card says 0:30 — that is the real length of what Deezer sends and I left it honest. Say if
   you would rather they agreed.

7. **Press Share.** A phone should offer its usual share sheet; a laptop should say "Link
   copied". Paste it into a new tab and confirm you land on the same journey, including any
   rerouting you had already done.

8. **The one thing nothing here could answer: does a clip actually play on an iPhone.**

**What "wrong" looks like:** a blank white screen, a broken image where the logo should be, a
card still carrying the links and dates, a panel that will not close, or a shared link that
opens a different journey from the one you were looking at.

**Paste the URL for anything you find.**

---

## ▶ QUEUED — 2026-09-08 — every card now says who the artist is, and where to go and hear more

**✅ NOW LIVE — deployed 2026-09-08, so everything below is exercisable.** ⚠ **One thing
moved after this was written:** the country-and-dates line and the two streaming links are
no longer on the card itself — open an artist with the › button and they are in the panel
that appears. Everything else below reads as written.

**Deploy note:** this is the `LUX-4` artifact, so §4 of `infra/README.md` changes `GRAPH` to
`graph-lux4.bin` and both upload lines run. `cdk diff` showing the graph variables change is
*expected here* and is not the `DEP-34` warning firing.

### What to exercise — about ten minutes

1. **Build a journey and read the line under each song title.** It is new. It should say
   things like *Person · United States · 1926–1991* or *English rock band · Group ·
   United Kingdom · 1967–2022* — whatever is actually known about that artist, and nothing
   where nothing is known.
2. **Find a card where that line is missing entirely.** That is correct and expected: it means
   we know nothing structured about them. What is NOT correct is the word "Unknown", a dash, or
   an empty gap where a fact would go.
3. **Look at the bottom of any card for "Spotify" and "Apple Music".** Both should be on
   **every** card, always — including the two artists you chose, and including a card with no
   song playing.
4. **Press both, on a well-known artist.** They should open a new tab straight on that
   artist's page.
5. **Press both on the most obscure artist in the journey** — press "Dig deeper" a few times
   first to find one. Here the links will often go to a **search results page** for their name
   instead of straight to their page. That is correct and is the point. What is wrong is a
   missing button, or a search that plainly searched the wrong words.
6. **Do all of the above on your phone.** These two additions cost every card two extra lines,
   and the phone is where that is felt.
7. **Open a journey link you saved weeks ago.** It must still open the same journey.

### What "wrong" looks like

- **The word "Unknown", "N/A", or a stray dot or dash** where a fact is missing. Missing facts
  should show nothing at all.
- **A fact line cut off mid-word** with a "…". It is meant to wrap onto a second line
  instead. The dates are the part that used to get cut, so check the end of the line.
- **Only one of the two services on a card**, or neither.
- **A link opening the wrong artist.** Worth a close look on anyone with a common name — that
  is the failure this data exists to prevent, arriving by a different route.
- **The page scrolling sideways on your phone**, or an artist's name squeezed thin again.
- **An old saved link opening a different journey.** The most serious thing on this list.

### Two things that are expected and are NOT faults

- **Search links instead of artist pages, on obscure artists.** Not every artist has a
  recorded id on both services, and a search is deliberately better than no button.
- **Cards are slightly taller.** Two lines were added to each one.

**Paste the URL for anything you find.**

## ▶ QUEUED — 2026-09-04 — one button instead of two, a list of who you skipped, and a way to hear a different song

**✅ NOW LIVE — deployed 2026-09-08.** ⚠ **Step 1 below describes the old placement.** The
reroute control is no longer on the card: open an artist with the › button and it is at the
bottom of the panel that appears. Steps 2 and 3 read as written.

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

**Discharged entries live in [`archive/TEST-QUEUE-discharged.md`](TEST-QUEUE-discharged.md),
frozen and never edited** — and the entries that queued nothing live in
[`archive/TEST-QUEUE-nil-entries.md`](TEST-QUEUE-nil-entries.md). Neither is work.
**This file holds only what is still to be pressed**, so an empty file below this line is a
valid and common state.
