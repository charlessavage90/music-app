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
> **An item is live only if its topmost heading says so.** As of **2026-09-01 (later)** that
> is **ZERO items — the queue is empty, and that is a valid and common state.** The
> revert-confirmation entry at the top was discharged by the owner the same day. The 2026-08-10 extended-map entry
> below it is DONE: the owner ran it and it **fired his revert criterion**, which is the
> first time an entry in this file has done so. *(The count is re-counted at each closeout
> rather than carried forward, per the incident below.)*
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

## ✅ DONE — 2026-09-04 — RUN BY THE OWNER; NOTHING FOUND

**He validated the site works as expected at the new address**, including the two things
that could not be checked from outside: **clips on middle cards play**, and **journeys
rebuild** when the buttons are pressed. Nothing wrong reported.

**This discharges the entry below. Do not queue it again** — the address move is confirmed
end to end from a real browser.

## ▶ QUEUED (latest) — 2026-09-03 — the app has a new address

**The app now lives at `https://unsung.fm`.** Nothing about the app itself changed — same
code, same map, same buttons. Only the address moved, and the old one still works: every link
you or anyone else has ever shared redirects to the new address and lands on the same journey.

### What to exercise — two minutes

1. **Open `https://unsung.fm` in a browser that has never seen it** (a private window is
   enough). Build one journey.
2. **Play a clip on a card in the middle.** This is the one thing that could not be checked
   from outside: the page and the search were confirmed working by machine, but nothing
   proved a clip actually plays from the new address.
3. **Press each of the two buttons on a middle card once**, and check the journey rebuilds.

### What "wrong" looks like

- **A blank white page**, or the words "the app did not load".
- **A card that will not play** where the same artist played before.
- **A link you had saved that does not open**, or that opens a *different* journey than it
  used to — the address change was supposed to carry the whole link across, including your
  button presses.

### One thing that is expected and is NOT a fault

**The short "How do I change the path?" explainer will open again**, once, even though you
dismissed it long ago. Browsers file that "already seen it" note under the website's address,
and the address changed, so it starts fresh. Dismiss it once more and it stays gone.

**Paste the URL for anything you find.**

## ✅ DONE — 2026-09-01 — CONFIRMED BY THE OWNER; NOTHING FOUND

> **His words:** *"I've confirmed the old map is live."*
>
> **What that settles.** The revert landed and the app is serving the map he had before
> 10 August. He reported **nothing wrong** — no journey still feeling like the last three
> weeks, no blank page, no card that would not play, no broken saved link. On this file's
> convention, that is **DONE — nothing found**.
>
> **What it does not settle, and this is not a lapse.** He confirmed identity and reported no
> defect; he did not report back on the three sub-checks individually, and **no session should
> write as though he had.** In particular, "is it back to how it was" as a *feeling* is his
> continuing long-run evaluation, which this file explicitly does **not** hold (owner ruling,
> 2026-08-07, above) — so its absence here is correct and must not be re-queued.
>
> **The unexplained half stays unexplained.** Nothing measured accounts for the *first*
> journey being worse before any press, and this discharge does not close it. It is recorded
> in `NEXT.md` and in both 2026-09-01 records; **do not quietly drop it.**

*Original queued text follows.*

## ▶ QUEUED (latest) — 2026-09-01 — the old map is back

**`https://musicapp.cmiller.io` is running the map it ran before 10 August again** — 58,838
artists, the one you had until three weeks ago. It is already deployed and verified from
outside; nothing is running on your machine. **Nothing else changed**: same code, same
buttons, same landing page, only the map moved back.

### What to exercise — ten minutes, and it is a confirmation, not an evaluation

1. **Two or three of the journeys that felt wrong**, and press **Dig deeper** ten or more
   times on each. The question is narrow: **is it back to how it was**, not whether it is
   good.
2. **Play a few cards in the middle.** The clip cache was left alone, so anything that
   played before should still play.
3. **The front page**, including the artist dropdown and the coloured dot behind it — that
   fix is frontend and was **not** reverted, so it should still be right.

### What "wrong" looks like

- **A journey that still feels like the last three weeks** rather than like before them.
  That would mean the map was not what made it worse, and I would want to know immediately.
- **A blank white page**, or a card that will not play where it played before.
- **An error page from a link you had saved** from the last three weeks. Some of those
  journeys ran through artists that only exist in the bigger map, so a saved link can now
  point at somebody who is not there. Expected, but tell me how often it happens.

**Paste the URL for anything you find.**

> **Why it went back**: it did not measurably help and it measurably cost. The artists the
> extension added have **a small fraction of the connections** the artists already there have,
> and a large minority of them have only one — which means they could never appear in the
> middle of a journey at all. And adding them **flattened the scale the app uses to tell
> "somebody you might not know" from "somebody everybody knows"**. Every figure behind those
> two sentences is owned by
> `builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md` — read it there.

---

## ✅ DONE — 2026-09-01 — RUN BY THE OWNER, AND IT FIRED THE REVERT CRITERION

> **His words:** *"The app with the crawl extension is noticeably worse than the old version
> — it's much harder to find unknown artists."* Asked where it goes wrong, he said it is
> **worse on both**, before pressing anything and while digging, and that **the digging is
> where it is noticeable**; he also noted that comparing single first journeys is weak
> evidence because there is only one data point per pair and "unfamiliarity" is not a precise
> measurement.
>
> **That is the criterion he set on 2026-08-10, in the words he set it in.** He instructed
> the revert; it was executed and verified live the same day — `/health` reports the previous
> map's identity and a journey builds through the public address.
>
> **⚠ The measurements did not contradict him, and one of them predicted this.** The
> acceptance gate the extended map passed was a **"the map is broken" stop-gate**: it
> **permitted materially more presses of *Dig deeper* to reach the same obscurity than the
> old map needed**, and the extended map used materially more. **Passing it never meant "no
> worse."** Both figures — what the gate permitted and what the map realised — are owned by
> the `JFX-` results README, `JFX-G1` section.
>
> **The mechanism was measured after the revert** and is owned by
> `builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`. One half of his report is
> **unexplained**: nothing measured accounts for the first journey being worse before any
> press, and `JFX-C1` found no change at depth 0 across 297 pairs.
>
> **`CLIP-1` — no new examples were reported**, and the entry asked for them by name. It
> stays open and unchanged.

*Original queued text follows.*

## QUEUED — 2026-08-10 — the map is bigger, and it is live

**`https://musicapp.cmiller.io` is now running a map built from a much bigger collection —
about 88,700 artists instead of about 58,800.** It is already deployed. Nothing is running
on your machine.

### The one thing to know before you start

**Journeys between artists you know well will be DIFFERENT from yesterday. That is the
release, not a fault.** There are roughly 30,000 more artists for a journey to travel
through, so routes that were the only way across before now have competition. Do not report
"this journey changed" as a defect — report it if the change makes it *worse*, which is a
different judgement and is the one below.

### Your own test, in your own words

You set this before any of it was adopted, so it is quoted back rather than paraphrased:

> **a noticeably worse product experience on more than half of tested journeys**, where
> "noticeably worse" means **how hard it is to find novel artists**.

Your calibration was the last map switch, which you recognised as a clear improvement in
under five minutes — so the instrument is known to be sensitive at that size of change.

**"Things I would improve" is a SEPARATE bucket from "revert."** There are things you
already wanted to improve about the current map and they will still be there. Keeping those
two apart is the whole point; otherwise a revert trigger quietly becomes a wish list.

### What to exercise — twenty minutes

1. **Three or four journeys between artists you know well**, and press **Dig deeper** ten or
   more times on each. That is the button this whole release is about: does the middle keep
   getting less familiar, or does it stall, or wander somewhere with no connection to where
   you started?
2. **Lean hardest on famous-to-famous pairs** — two artists you would both call well known.
   That is where the one unexplained signal in the measurements sat, and it is also the case
   you can judge best, because you know both ends.
3. **Play the cards in the middle**, not just the ends.
4. **On a phone as well.**
5. **The front page: open the artist dropdown and check the little coloured dot in the box
   below is now behind it, not in front.** That is the fix you found and verified locally on
   2026-08-08 — this is the first time it has been on the live site.

### What "wrong" looks like

- **A card with nothing to play**, or a card that plays but is not that artist's own music —
  a guest spot or someone else's remix. **This is `CLIP-1` and I expect it to get MORE
  common, not less**: the artists newly added are more obscure, and 31% of them have nothing
  playable of their own against 25% of the ones already there. **Name any new examples you
  hit** — Albert Hammond Jr. and Metric were your two. How often it happens is what decides
  whether it is worth fixing.
- **The middle stops making sense** — artists with no audible relation to either end.
- **Pressing Dig deeper stops changing anything**, or changes it randomly rather than digging
  further out.
- **The dropdown still sitting behind the dot** on the front page.
- **A blank white page.** Old unused files were deleted from the server in this publish, and
  a blank page would mean one was still needed. Reload once; if it persists, tell me
  immediately — it is a one-command fix.

### What "right" looks like

Journeys build quickly, every card plays, and the further you press the less familiar the
middle gets **without losing the thread** between your two artists.

**Paste the URL for anything you find** — the whole journey is in the address bar.

> **Rollback is one command and a few minutes.** The previous map is still in the bucket,
> untouched, along with the one before it.
>
> Detail: `docs/superpowers/2026-08-10-cxa-adoption-execution-log.md`.

---

<!-- "(latest)" stripped 2026-08-10: only the newest entry carries it, per the convention
     above. This entry's content is unchanged and still accurate. -->
## ✅ DONE — 2026-08-07 — the two buttons have moved, and the website looks different

> ### ✅ RUN BY THE OWNER 2026-08-08 — fully functional, and it found ONE defect.
>
> **His words:** *"the new site UI and changed buttons are fully functional."* **The serious
> thing this entry existed to catch — a familiar pair giving a DIFFERENT journey — did not
> happen**, which is the confirmation that mattered, since the release was supposed to move
> nothing about routing.
>
> **⚠ ONE DEFECT FOUND, AND IT IS FIXED: the landing page's indicator dots.** Typing in the
> **From** box opens the matching-artist list downward over the **To** box — and the To box's
> **green dot showed through the list** instead of being hidden behind it.
>
> **A genuine stacking bug, not a cosmetic slip.** The list and the dot were both on the same
> layer (`z-10`), and the two boxes are plain siblings with nothing between them starting a new
> layering context. When two things claim the same layer the browser breaks the tie on document
> order — and the second box's dot comes *later* in the document than the first box's list, so
> the dot won. The list now sits a layer above every field decoration.
>
> **Verified by reproducing it, not by looking.** The regression test samples the actual
> rendered pixel where the dot sits: against the shipped code that pixel is *exactly* the dot's
> green, and after the fix it is the list's background. ⚠ **An earlier version of that test used
> the obvious tool (`elementFromPoint`) and PASSED against the broken code** — the dot is
> click-through, so hit-testing cannot see it however it is painted. Recorded because it would
> otherwise have shipped as a green guard standing over a live defect.
>
> **Branch `landing-dot-z-order`. Not yet deployed** — the fix is on a branch, so the live site
> still shows the dot until it is merged and published.
>
> **NOT covered by this pass and still open:** `CLIP-1` — a card can play the right artist and
> the wrong impression of them (Albert Hammond Jr., Metric). No new examples were reported.

*Original queued text follows.*

## QUEUED — 2026-08-07 — the two buttons have moved, and the website looks different

**The app on `https://musicapp.cmiller.io` looks different from this morning.** It is already
live and nothing is running on your machine. **The artists you get have not changed** — no
routing, no map, no weighting was touched, so a journey you build now goes through the same
people it would have yesterday. If a familiar pair gives you a *different* journey, that is
wrong and it is the most important thing you could tell me.

### The one thing to know before you start

**The two buttons are no longer on the card.** Each artist in the middle now has a quiet strip
across the bottom of their card reading **"Reroute from here"**. Press it and two choices open
underneath: **Steer away** and **Dig deeper**. They are the same two buttons you have always
had, one press further in, and they are no longer red and green — because both of them rebuild
the entire journey, and the two colours suggested they were opposites.

### What to exercise — fifteen minutes

1. **Build a journey and press "Reroute from here" on somebody in the middle.** Then press
   **Dig deeper**. Watch what happens on screen as it rebuilds — you should get a message
   telling you what it is doing, long enough to actually read, and then the artists that
   changed should glow for a moment. **Tell me if that glow marks artists you can see did not
   change**, or misses ones that did.
2. **Do that eight or ten times on the same journey.** This is the part I am least sure of:
   whether the extra press each time becomes annoying when you are digging repeatedly.
   **That is a judgement only you can make and I would like it.**
3. **Look at the front page.** New wording, and three ready-made journeys underneath the two
   boxes. **Press one of them.** They should behave exactly like a journey you typed in
   yourself — shareable link, back button, everything.
4. **Look at whether the two boxes on the front page invite you to type in them.** You said
   they looked switched off. They should now look raised, with a small coloured dot in each.
5. **On a phone as well.** The two choices sit side by side on a computer and stack on a
   phone; both should be easy to hit with a thumb.

### What "wrong" looks like

- **A familiar pair giving you a different journey.** Nothing about routing changed, so this
  would be serious.
- **The strip appearing on the first or last card.** Those are the two artists you chose;
  there is nothing to reroute.
- **The message about what it is doing landing on top of something else**, or vanishing before
  you can read it.
- **The glow marking everybody**, or marking nobody after a rebuild that clearly changed the
  middle.
- **A ready-made journey landing on an error page.** That would mean one of those six artists
  is no longer in the map, which is a real thing that can happen and nothing automatic can
  catch it.
- Anything that stopped playing. Clips were not touched, so a silent card would be unrelated —
  tell me anyway.

### What "right" looks like

The journey is the same, the strip is easy to find, pressing a choice visibly does something,
and the front page makes it obvious what to do first.

**Paste the URL for anything you find** — the whole journey is in the address bar.

> **Still open and unchanged:** a card can play the right artist and the wrong impression of
> them — a guest appearance or someone else's remix. Albert Hammond Jr. and Metric were your
> examples. Not fixed, still your call.
>
> Detail: `docs/superpowers/2026-08-07-bypass-tray-ux-execution-log.md`.

---

## ✅ DONE — 2026-08-07 — the missing artwork is fixed, and it changed what the pictures are

> ### ✅ RUN BY THE OWNER 2026-08-07 — "Yes, all good." Nothing found.
>
> **Every card had a picture.** The defect he reported on 2026-08-06 is confirmed fixed in
> use, on the live site, by the person who reported it — which is the only evidence that
> closes it, since the fault was invisible to every automated check (the clip resolved
> perfectly; only the image was missing).
>
> **The album-cover change is ACCEPTED.** The entry offered to revert to artist portraits at
> the cost of artwork going missing for roughly half of artists; he did not take it. Cards
> show album covers, deliberately, and that is now the settled behaviour rather than a
> pending choice.
>
> **`CLIP-1` is untouched by this and stays open** — a card can still play the right artist
> and the wrong impression of them. No new examples were reported beyond Albert Hammond Jr.
> and Metric. Still his call whether it is worth fixing.

*Original queued text follows.*

## QUEUED — 2026-08-06 (later) — the missing artwork is fixed, and it changed what the pictures are

**You reported that the artwork on the cards was hit and miss while the music played fine. That
was a real fault, it is fixed, and the fix is already on the website.** Nothing is running on
your machine.

**Run this together with the entry below rather than separately.** That one asks you to press
the new map; this one only changes what you see while you do it. Both are on
`https://musicapp.cmiller.io`, and doing them in one sitting saves you a second twenty minutes.

### The one thing to know before you look

**The pictures are now album covers instead of photographs of the artist.** That is deliberate
and it is the fix — the artwork the app could reliably get hold of for every artist was the
album cover, not the portrait. Some cards always showed album covers, so this also makes them
consistent with each other for the first time. **If you would rather have portraits, say so** —
it is a real choice and it can go back, at the cost of the artwork going missing again for
about half the artists.

### What to exercise — five minutes, alongside the entry below

1. **Build any journey and look at every card, including the middle ones.** Every card should
   have a picture. A plain grey square where a picture should be is the fault returning.
2. **Press "know them already" ten or more times** and keep watching the pictures as the middle
   of the journey gets less familiar. This is where the fault used to show up most, because it
   is where you meet artists the app had not looked up before.
3. **Try a few artists you would call obscure.** They were the worst affected.

### What "wrong" looks like

- **A grey square with no picture**, on any card.
- **A picture that clearly belongs to a different artist.** This would be new and would matter.
- Anything that stopped playing. Nothing about the music was touched, so a silent card would
  be unrelated — but tell me anyway.

### What "right" looks like

Every card has artwork, it appears about as fast as it used to, and it keeps up as you press
your way deeper into the journey.

**Paste the URL for anything you find** — the whole journey is in the address bar.

> **Still open and unchanged:** a card can play the right artist but the wrong impression of
> them — a guest appearance or someone else's remix instead of their own music. Albert Hammond
> Jr. and Metric were your two examples. **That is not fixed and is still your call**; note any
> more you hit.
>
> Detail: `docs/superpowers/2026-08-06-clip-cover-art-execution-log.md`.

---

## ✅ DONE — 2026-08-07 — the new map is LIVE on the website

> ### ✅ RUN BY THE OWNER 2026-08-07 — fully exercised on **desktop and mobile**, no defects, no regressions.
>
> **His words:** *"from a defect, product functionality issue standpoint, I've fully tested
> the new map on desktop and mobile, and I've found no defects or regressions (aside from the
> missing album art defect that's already been resolved)."*
>
> **This is the release check for the `MSW-` map switch, and it passes.** The adoption was an
> owner override of the `GBL-` null — taken knowingly, never evidence-backed — so this is the
> first evidence of any kind that the new map holds up in real use by a person. It does not
> retrospectively license the null, and must not be recorded as doing so.
>
> **Read this as a platform-level confirmation, not a per-step one.** He confirmed desktop and
> mobile and made an explicit no-defect / no-regression claim, which is stronger than the
> "nothing surfaced" passes elsewhere in this file — but he did not walk the five numbered
> steps individually and this record does not claim he did.
>
> **⚠ What is deliberately NOT discharged here, and is not owed:** his continuing evaluation
> of the *experience* — where novelty appears, how the map feels over days and weeks. He is
> doing that and taking notes, and he ruled that **it is not an open test-queue item.** See
> the rule at the top of this file, which was written from that ruling. **Do not re-queue it.**

*Original queued text follows.*

## QUEUED — 2026-08-06 — the new map is LIVE on the website

**This is the real one.** Everything you tested locally this morning is now what
`https://musicapp.cmiller.io` serves, to you and to anyone you send it to. Nothing is running
on your machine that matters any more.

**It is already deployed and already checked mechanically.** The live engine is serving the new
map — matched on checksum, artist count and edge count against the file it was built from — and
the "dig deeper" behaviour is switched on. A journey built through the live site returns
sensible results, every card tried resolved a clip, and pressing "know them already" changes the
middle of the journey at every press.

### What to exercise — twenty minutes

1. **Two or three journeys between artists you know well.** Expect them to be **different from
   last week** — that is the point of this release, not a fault. The old map is gone.
2. **Play the cards in the middle**, not just the ends.
3. **Press "know them already" ten or more times on one journey.** This is the button the whole
   release is about. Watch whether the middle keeps getting less familiar, or stalls, or starts
   wandering somewhere with no connection to where you started.
4. **Do it on a phone too.** Nothing about the layout changed, but this is the first time the
   new map has been on a real device.
5. **Send someone a link** mid-journey and check it lands on that exact journey.

### What "wrong" looks like

- **A card with nothing to play** — silent or stuck. That class was filtered out, so one
  appearing is a genuine finding, not bad luck.
- **A card that plays something, but not that artist's own music.** This is `CLIP-1`, already
  known and deliberately not fixed yet — the examples were Albert Hammond Jr. playing a track
  he guests on, and Metric playing a remix. **Note names if you hit more**, because how often
  it happens is what decides whether it is worth fixing.
- **The middle stops making sense** — artists with no audible relation to either end.
- **Pressing the button stops changing anything**, or changes it randomly rather than digging
  further out.

### What "right" looks like

Journeys build quickly, every card plays, and the further you press the less familiar the
middle gets **without losing the thread** between your two artists.

**Report anything by name, and paste the URL** — every journey is in the address bar, so a link
reproduces exactly what you saw however long afterwards.

> **Rollback, if something is badly wrong:** the previous map is still in the bucket untouched
> and redeploying it is one command. Ask and it takes a few minutes.
>
> **Nothing is running on your machine.** The two local servers from the morning were stopped
> and both ports are free — you asked to use the live app from here on, since **it records what
> you do to CloudWatch and a local server does not.** So this test leaves a trace that can be
> looked at afterwards, which the local one never did.
>
> Detail: `docs/superpowers/2026-08-05-msw-execution-log.md`, the Task 11 and 12 sections.

---

## ✅ DONE — 2026-08-06 — the new map on your machine: PRESSED, and it decided the release

> ### ✅ RUN BY THE OWNER 2026-08-06. He pressed it, and it produced a go.
>
> **This entry existed to be the decision, and it was.** He tested enough tracks to say move
> forward, and the map switch went to production the same day — see the newer entry above,
> which owns what is now live.
>
> **One finding came out of it, and it is logged rather than fixed: `CLIP-1`.** A clip can be
> the right artist and still be the wrong impression of them — a guest credit or someone
> else's remix instead of the artist's own work. He named two: **Albert Hammond Jr.**, whose
> card played *"Cinnamon (feat. Albert Hammond Jr.)"* from a Damiano David album, and
> **Metric**, which played *"Help I'm Alive (BYNX Rework)"* rather than any Metric original.
>
> **It is not new and it is not a regression** — the new map did not cause it. It surfaced now
> because journeys pass through less-famous artists more often, and because the earlier
> listening work taught him what to look for. It is **distinct from** the wrong-artist fault
> (a different artist of the same name) and from the artists-with-nothing-to-play class (both
> already handled). Recorded with its condition in
> `docs/superpowers/2026-08-05-msw-execution-log.md`; **whether it is worth fixing is his
> call**, since the fix trades how often a clip is available against how representative it is.
>
> ~~**The two local servers this entry left running are now redundant** — the live site serves
> the same thing. Nothing owns them and they are still up; they can be stopped whenever.~~
> **✅ BOTH STOPPED on the owner's instruction at `76d3b82`, and both ports are free.** He is
> using the live site from here on, because it records what he does and a local server does
> not. *(Struck rather than deleted: "they are still up" was true when written and is what
> makes the disposition auditable. Corrected 2026-08-06 (later) — a closeout audit found it
> still reading in the present tense.)*

*Original queued text follows.*

## QUEUED — 2026-08-06 (night) — the new map is running on your machine and waiting for you to press it

**This is the decision, not a check afterwards.** Nothing has been adopted and nothing has been
deployed. The website is untouched and still serves the old map. What is running is a **local**
copy of the app on the new map, with the new "dig deeper" behaviour switched on — set up so you
can decide whether to keep it.

**It is already started. Open `http://localhost:5173` and it should just work.**

If the page does not load, nothing is broken — the two local servers were left running and one
may have stopped. They can be restarted from the commands in `CLAUDE.md`; ask and it takes a
minute.

### What to do

1. **Build a journey between two artists you know well.** Anything you like; a pair you have
   strong feelings about is more useful than an unfamiliar one.
2. **Play a few of the cards in the middle.** Not just the first — the middle of the journey is
   where all of this work lands.
3. **Press "know them already" repeatedly — ten times or more on the same journey.** This is the
   button that matters. Use it rather than "not for me": it is the one that pushes hardest on
   what changed, because it is what asks the app to go further from the obvious.
4. **Watch whether the middle keeps getting less familiar the more you press**, or whether it
   stalls, or starts wandering somewhere that no longer feels connected to where you started.
5. **Do it on two or three different journeys**, since the thing being tested varies a lot from
   one pair to another.

### What "wrong" looks like

- **A card with nothing to play.** The clip is silent, missing, or the card just sits there.
- **A card that plays something, but not that artist's own music.** This is the important one
  and it is the reason this test exists rather than a script. We found one during checking: a
  session bassist whose card played a charity single he appeared on. It plays perfectly, so
  every automatic check says it is fine — **only a person listening can tell that it is not
  really that artist's music.** If a card feels like that, note the name.
- **The middle stops making sense** — artists with no audible relationship to either end.
- **Pressing the button stops changing anything**, or changes it in a way that feels random
  rather than further out.

### What "right" looks like

Journeys build quickly, every card plays, and the further you press the less familiar the middle
gets **without losing the thread** between your two artists.

**Report anything you find by name.** Every journey is in the address bar, so pasting the URL is
enough to reproduce whatever you saw, however long afterwards.

> **Left running for you** (nothing owns them; they survive this session ending):
> the app on port **5173**, pid 199836, and the server behind it on port **8000**, pid 249336 —
> both started 2026-08-06 08:24, after the last commit, so they serve the work being tested.
> The deeper-digging behaviour is a **local override only**; no committed setting was changed,
> and stopping those two processes returns everything to today's behaviour.
>
> Detail, for whoever wants it: `docs/superpowers/2026-08-05-msw-execution-log.md`, the Task 10
> sections.

---

## ✅ DONE — 2026-08-02 (evening) — the wrong-artist clip fault now has a fix built, and the website got a tidy-up you can check in ten seconds
<!-- "(latest)" stripped 2026-08-02 (night): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

> ### ✅ CHECKED BY THE OWNER 2026-08-02 — nothing found.
>
> The live site is functional after the `--prune` pass: **journeys build and clips play.**
> The two deleted files were genuinely orphaned, as the pre-flight predicted. **Nothing is
> owed on this entry.**
>
> The rest of this entry is unchanged and still describes work that is **dormant until a
> graph is rebuilt** — the clip fix ships when a map carrying the artist links does.

**Nothing is running.** All four ports were checked and are empty; no server was started and
none was left behind. **A journey you build now is identical to one from this morning** — no
routing, no graph, no weighting, no cost function changed.

**One thing did change on the live website, and it is the only thing here worth your time.**
Two leftover files from the old design were still sitting on the server, unused since the
redesign went live. They are now deleted. **This should be invisible** — but it is the one
change today that touched the thing you actually use, so:

> **Open `https://musicapp.cmiller.io` in a browser that has never seen it** (a private
> window is enough), build one journey, and play a clip. If the page loads, looks right and
> plays, it is fine. **If you get a blank page or a missing-file error, tell me immediately**
> — that would mean the wrong files were deleted, and it is a one-command fix.

Everything else below is built but **dormant until a map is rebuilt**.

**The fault where a card plays a clip by a different artist of the same name.** You have seen
this. It was measured at roughly one card in eleven, of the ones we could check. The app finds
music by searching the artist's *name*, so when two artists share a name it can pick the wrong
one — and it cannot tell, because the name matches perfectly.

**MusicBrainz records, for many artists, a direct link to their page on the music service.**
The app now uses that link first and only falls back to searching by name when there isn't
one. A direct link cannot land on the wrong artist, because it doesn't search at all.

- **On the artists you actually get shown, about nine in ten have such a link.** That is much
  better than it sounds from the raw numbers, because the app tends to show well-known artists
  and they are the ones with links.
- **It is not a complete fix, and one thing surprised us.** MusicBrainz occasionally links to a
  *duplicate* page rather than the real one — we found a "Radiohead" page with 473 followers
  and nothing on it, and an "Orbital" page with 20 followers that *does* have tracks. The first
  harmlessly falls back to searching by name. The second would play something worse than the
  search would have found. **On balance it is clearly a gain, but it is not a guarantee**, and
  I had told you earlier it was — that was wrong and I have corrected it.
- **You will not hear any of this until a map is rebuilt.** The links travel inside the map
  file, and the one being served does not have them yet.

**Nothing else is proposed for you to test.** The next real entry comes when a map is actually
rebuilt — which is when all of this, and the artist cleanup from yesterday, become audible at
the same time.

Detail, if you want it:
`docs/superpowers/2026-08-02-deezer-id-clip-resolution-execution-log.md`.

---

## N/A — 2026-08-02 — the cleanup you decided on is now built in; still nothing changes until a rebuild

**Nothing to exercise, and nothing is running.** All four ports were checked and are empty;
no server was started and none was left behind. No routing, no graph, no weighting, no cost
function, and not one line of the app or the website changed. **A journey you build now is
identical to one from yesterday.**

**What happened, in plain terms.** Yesterday you decided to remove the roughly seven
thousand "ghost" artists — the ones with no records to their name that a music service
can't play either. That decision was written down but not yet built into anything. Today it
was.

- **The map-builder now applies your rule automatically.** The next time a map is built,
  those artists are gone. **No map has been rebuilt, so you would still see no difference
  today.**
- **We worked out the same list for the alternative data set** — the one that would come
  from changing the collection setting. It turned out that data has slightly *more* ghost
  artists than today's, and they are slightly deader: fewer of them have a page on any
  music service, and fewer of those have anything that actually plays. That supports the
  rule rather than undermining it, and it means both versions of the map can now be cleaned
  to the same standard, which is what makes any future comparison between them fair.
- **We also fixed an internal bookkeeping problem we created ourselves.** Adding the
  cleanup meant some of our own measurement tools quietly stopped matching the real
  map-builder. Nothing was wrong with any past result, but a future one could have been.
  There is now a check that fails loudly if it happens again.

**One thing worth thirty seconds, because it is about what you hear today.** The fault
where a card plays a clip by a different artist of the same name showed up again in this
data — about one in sixteen of the cases we could check, against about one in eleven last
time. Those two numbers are close enough to be the same number measured twice; what they
tell us is that the fault is real and roughly this common. It is unrelated to everything
above and still unfixed.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes — realistically, when a map is actually rebuilt.

**✅ THE REDESIGN ENTRY IS NOW DONE, 2026-08-02** — run by the owner the same day, everything
passed, and the iPhone script came back clean and killed `G3-F2`, a HIGH "blocking if
confirmed" finding in the Gate 2 → 3 review. That entry owns the result. **Nothing was queued
at the time this was written; the evening entry above has since added a ten-second check.**

*(This entry originally said the redesign was still the live one to run, and it was for the
five days before it was discharged.)*

Detail, if you want it: `docs/superpowers/2026-08-02-tail-drop-wiring-execution-log.md`.

---

## N/A — 2026-07-29 — we built a trial map with the new setting; the app is untouched
<!-- "(latest)" stripped 2026-07-30: only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise. No web servers are running** — all four ports were checked and are
empty. No routing, no graph, no weighting, no cost function, and not one line of the app or
the website changed. **A journey you build now is identical to one from this afternoon.** The
trial map that got built is a scratch file nothing points at; the app still uses the same map
it did this morning.

> ### ✅ THE OVERNIGHT RUN FINISHED — and it is worth thirty seconds
>
> **It completed cleanly: 75,000 artists collected, nothing failed, and the irreplaceable
> existing collection was untouched.** A map was then built from it in 78 seconds. **The app
> is still using the old map, nothing has been adopted, and there is still nothing to test.**
>
> **What the new map shows, in plain terms.** It is genuinely a *different* map rather than
> a better or worse version of the same one — nearly a third of today's artists never appear
> in it at all, and it reaches roughly as many artists we have never seen.
>
> - **It cuts far more artists off the map entirely: 6,499 against 800.** Among the obscure
>   artists it does reach, it strands about **7%**, where today's setting strands **0.08%**.
>   That is yesterday's worry, confirmed at full size.
> - **R.E.M. ends up with 6 connections, down from 47.** Pixies drops to 3, The xx to 1.
> - **And the safety check does not notice any of it — the map built and passed.** The check
>   looks at the most popular artists, and these artists lose so much popularity along with
>   their connections that they drop off the list before it looks. That blind spot is now
>   confirmed rather than suspected. It is not a reason to weaken the check.
>
> **All of that is at one particular setting of a knob nobody has tuned yet**, and the probe
> from last night showed that knob moves the stranding a great deal. Tuning it is the next
> piece of work, it needs no more downloading, and **nothing is decided.**
>
> *(The note below is from when it was still running, and is kept as sent.)*
>
> ### ⚠ ONE THING IS RUNNING OVERNIGHT, and you started it deliberately
>
> **A full data-gathering run for the new setting**, begun late on 2026-07-29 at your
> instruction. It is **collecting only** — it downloads similar-artist data into a scratch
> folder and **builds no map, changes no setting, and touches nothing the app uses.** The
> app is unaffected while it runs and unaffected when it finishes.
>
> - **Expect roughly 7½ hours**, so it may still be going when you wake. That is fine.
> - **If it stopped early** — laptop slept, network dropped — **just run the same command
>   again.** It resumes from where it got to and re-downloads nothing.
> - **The irreplaceable existing collection cannot be harmed by it**: the new data is
>   filed separately, which is one of the things built today.
> - **When it finishes, nothing happens automatically.** Turning it into a map is a
>   separate 29-second step, and *using* that map is a further decision that still owes a
>   listening test.
>
> Command, log location and morning checks: the execution log below, and the handoff.

**What happened, in plain terms.** This afternoon we measured the price of switching to the
new setting. Tonight we did the engineering that had to happen before anyone *could* switch,
then built a small trial map with the new setting to see what actually breaks.

**Three things are worth knowing, and the third is the one that surprised us.**

- **The artists with missing names are now dropped automatically, and you were right to say
  drop them.** You checked three of them by hand and MusicBrainz says "artist not found" for
  all three — they are deleted entries that live on in the similarity data. So repairing
  them was never actually possible. A full rebuild of today's map now completes and passes
  its own safety checks, which it refused to do before.
- **The thing we predicted would break, breaks — but worse than we thought and quieter.**
  Under the new setting R.E.M. goes from 47 connections down to **6**. We expected that. What
  we did not expect is that **the safety check that exists to catch exactly this does not
  notice.** The check looks at the most popular artists — but an artist that loses its
  connections also loses its popularity, so R.E.M. quietly drops off the list the check
  examines before the check runs. It is a blind spot, and we only found it by building the
  thing rather than reasoning about it.
- **The new setting cuts more artists off the map entirely.** Roughly twice as many as the
  current setting, at the small scale we tested. That is the same worry as this afternoon's,
  now seen in a built map rather than estimated.

**Also honest about our own work, twice over.** A safety wrapper stopped us from accidentally
writing into the irreplaceable collection of artist data — it turned out our own assumption
about that data was wrong, and the wrapper caught it rather than a person. And a routine
end-of-work check found that one test we had written was passing without actually testing
anything; it took three attempts to write one that genuinely fails when the code is broken.
Both are fixed and both are recorded.

**One thing we could not do:** the security scanner needs you to log in (`snyk auth`), so it
has not run over tonight's code. It is written down in every commit rather than quietly
skipped.

**None of this decides anything.** Whether to rebuild the map with the new setting is still
your call and still parked. What changed tonight is that it is now *possible* to do, and the
price is measured instead of guessed.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-29-graph-rebuild-track-a-execution-log.md`.*

## ✅ DONE 2026-08-02 — 2026-07-28 (night) — the redesign is finished, and it is LIVE

> ### ✅ RUN BY THE OWNER 2026-08-02. Everything passed, and the iPhone half settled a Gate 3 blocker.
>
> **All six desktop checks passed**, on desktop and phone including narrow window widths.
> Journeys he knows well were **unchanged**, which was the most valuable thing to confirm.
> Both bypass messages appear and differ per button; the explainer collapses, persists and
> re-expands; shared links land on the right journey mid-path. The loading screen works but
> **is often too fast to see** — worth knowing before anyone measures or redesigns it.
>
> **⚠ The iPhone script is DISCHARGED, and it falsified `G3-F2`.** That finding is HIGH and
> **"blocking if confirmed"** in the Gate 2 → 3 review
> ([`findings/2026-07-27-gate2-gate3-team-review.md`](findings/2026-07-27-gate2-gate3-team-review.md)),
> and the review named exactly this test to settle it: *"one tap on a real device confirms or
> kills it."* All three questions came back clean — **clips play**, the bottom bar clears the
> home indicator, and the keyboard leaves artist names alone.
>
> **What that does and does not mean.** The worst reading — *no clip ever plays on iPhone and
> the app never says why* — is **dead**. But the code was not changed to achieve it:
> `usePlayer.ts:49` still awaits the URL before `player.play(url)` at line 60, which is the
> pattern the review flagged. So the finding's *description* was accurate and only its
> *consequence* is removed, and this rests on iOS's current tolerance rather than on the code
> being correct by construction. It is evidence, not a guarantee, and a future iOS could
> tighten it.
>
> **One item from this entry was NOT covered and is still the owner's call:** the cosmetic
> overlap where "Steering around that sound" lands on top of the open explainer on a first
> visit. He reported both working and did not mention it. Still a one-line change if wanted.

<!-- Updated after the deploy: this entry was written while the redesign was local-only and
     carried two PIDs. It is now published, so the local servers are stopped and every check
     below runs against the real address — including the phone half, whose trigger has fired. -->

**This is the other half of the entry below, and it is the real one.** The app you sent me a
mockup of is now built end to end **and it is on the website**. Everything below runs against
**`https://musicapp.cmiller.io`** — nothing is running on your machine and nothing needs to be.

**Nothing about *which artists* you get has changed.** No routing, no graph, no weighting, no
cost function — **a journey you build now is the same journey as this morning's.** Not one line
of the router was touched. That is the most valuable thing to confirm, because the app looks
different enough that you will be inclined to trust it less.

### The address, and what was already checked mechanically

**`https://musicapp.cmiller.io`** — no username, no password. Old `d2n3xqz3pttguf…` links still
redirect and keep their place in the journey, confirmed after this deploy.

**Checked already, so you don't have to:** the live engine is running the same artist map as
your machine (matched on checksum, artist count and edge count); a journey built against the
live site returned **the identical eight artists in the identical order** as the same journey
locally; a shared journey link opens cold; and the page loads with **no browser errors**.

### What to exercise — twenty minutes

1. **The front screen.** New type, a rounded search box, a pill "Find path" button, and a line
   at the bottom about clip length. Then **drag the window narrow**, to about a third of your
   screen, and look again.
2. **Two or three journeys you know well.** These **must be unchanged**. Same artists, same
   order. If a familiar pair gives you a *different* journey, something is wrong and it is the
   most important thing you could tell me.
3. **The new loading screen.** This is the one you have never seen: your two artists at top and
   bottom with shimmering placeholders between them, and a line reading *"Listening for the
   steps between them…"*. It replaces the old plain "Building your path…". **On a fast machine
   against a warm engine it may flash past** — the honest way to see it is to build a path
   between two obscure artists, or just watch the top of the screen as you press Find path.
4. **Press both bypass buttons, several times.** The app now *says what it is doing*, and says
   something different for each: **✕ Not for me** → "Steering around that sound"; **✓ I know
   them** → "Digging for someone newer". The old journey **stays on screen, dimmed**, while the
   new one is found — it no longer blanks out.
5. **The new explainer.** Above every journey there is now a line saying how many artists are in
   between, and a fold-out **"What do the two buttons do?"** — open on your first visit. It says
   the thing that has always been true and has never been written down anywhere: **either button
   rebuilds the whole journey, not just the card you pressed.** Press **"Got it"**, then reload
   the page: **it should stay shut.** Press the question again and it should open.
6. **Copy a journey's address mid-way through and open it in a new tab.** It should land on that
   exact journey. This is the shared-link case, and it now has a proper loading screen instead
   of a bare line.

**What "wrong" looks like:** a familiar pair giving a *different* journey; the explainer
re-opening after you dismissed it; a bypass press blanking the page instead of dimming it; the
wrong message for the button you pressed; an artist's name squeezed to nothing in a narrow
window; or clips that no longer play.

### One thing I noticed and deliberately did not change

**On a first visit, the "Steering around that sound" message lands on top of the open
explainer box** rather than over the journey — because on a first visit the explainer is open and
takes that space. Once you press "Got it" it sits where it was designed to. It is cosmetic, it
is the design as drawn rather than a fault, and **moving it is your call** — say the word and it
is a one-line change.

### ✅ TRIGGER FIRED — the phone half is runnable now

**It was deferred on "the next publish", and that publish has happened.** Open
`https://musicapp.cmiller.io` on your phone. The phone layout was exercised at phone width by a
machine — the two bypass buttons drop onto their own row and the artist's name gets the full
width — but that checks the *rules*, not a real device. **On a phone, check the journey is
readable and both bypass buttons are hittable with a thumb.**

### ⚠ Still owed, and this work does not touch it: the iPhone script

**This is now the live location for it** — it is carried forward from the entry below, which has
never been run. **Nobody has ever opened this app on an iPhone**, and three questions are
unanswered:

1. **Does a clip play at all?** iOS refuses to play audio unless a real tap starts it. **The very
   first tap on a play button answers this.** If it is silent, everything else is moot.
2. **Does the bar at the bottom clear the home indicator**, or is it tucked underneath?
3. **Does the keyboard leave artist names alone** as you type them — accents, odd capitalisation?

**Why it needs a person:** if clips silently fail on iOS, the app looks like it is working
perfectly and just happens to have no sound. No error, no message, and nothing in any log
distinguishes that from an artist we genuinely have no clip for. **A borrowed iPhone for ten
minutes settles it. Nothing else will.** It needs the live site — which is now up, so there is
nothing left blocking it.

**Best bug report:** the URL from the address bar, and a screenshot if it is a layout problem.

*Detail: `docs/superpowers/2026-07-28-frontend-mockup-adoption-execution-log.md`.*

## ✅ DONE (section 2) 2026-08-02 — 2026-07-28 — the password is gone, and there is one thing only an iPhone can answer
<!-- "(latest)" stripped 2026-07-28 evening: only the newest entry carries it, per the
     convention below. Section 2 — the iPhone script — was DISCHARGED 2026-08-02; see the
     note below and the newer entry, which owns the result. -->

> **✅ SECTION 2 IS DISCHARGED, 2026-08-02 — the iPhone script was run and all three questions
> came back clean.** It was carried forward into the newer entry at the top of this file and
> run there; that entry owns the result and what it settled (`G3-F2`). Sections 1 and 3 were
> not run as written, but section 1's substance — familiar journeys unchanged, shared links
> landing correctly — was covered by the newer entry's checks 2 and 6. Section 3 is
> informational rather than a test.
>
> *(Original note, retained: "STILL OUTSTANDING as of 2026-07-28 night… the single most
> valuable unrun test on this project." It was, for five days.)*

**The address is `https://musicapp.cmiller.io` and there is nothing to type.** No username, no
password, no dialog. Send it to someone and they just open it.

**You have already confirmed the password is gone** — new device, incognito window — so that half
is done. What follows is everything else.

**Nothing about *which artists* you get has changed.** No routing, no graph, no weighting, no cost
function, and not one line of the app itself was touched. **A journey you build today is the same
journey as yesterday's.** That is the single most valuable thing to confirm, because four separate
pieces of plumbing moved underneath it.

**Old links still work.** Anything you sent anyone at the old `d2n3xqz3pttguf...` address now
redirects to the new one and keeps its place in the journey — including which artists had been
bypassed. Worth testing with a link you actually sent someone earlier.

### 1. The ordinary run — ten minutes

1. **Two or three journeys you know well.** They must be unchanged.
2. **Play clips and press both bypass buttons** several times.
3. **Send yourself a journey link** from the new address, open it fresh.
4. **Dig out an old link** if you have one, and confirm it lands on the journey rather than an
   error page.
5. **Type a nonsense address** like `/nowhere` — expect a short page with a way back.

**What "wrong" looks like:** a familiar pair giving a *different* journey; a link landing on an
error; a page saying "this request did not arrive through the front door" (that means something is
genuinely broken — tell me); or clips that no longer play.

### 2. The iPhone script — the one thing nothing else can answer ⚠

**This is not optional and it is not covered by anything above.** Your phone run in July was an
Android Pixel. **Nobody has ever opened this app on an iPhone.** Three things are unanswered, and
the first one is the one that matters:

1. **Does a clip play at all?** iOS refuses to play audio unless a real tap starts it, and the app
   may or may not satisfy that rule. **The very first tap on a play button answers this.** If it
   is silent, everything else is moot.
2. **Does the bar at the bottom clear the home indicator**, or is it tucked underneath?
3. **Does the keyboard leave artist names alone** as you type them — accents, odd capitalisation?

**Why it needs a person and not a test:** if clips silently fail on iOS, the app looks like it is
working perfectly and just happens to have no sound. There is no error, no message, and nothing in
any log distinguishes that from an artist we genuinely have no clip for. **A borrowed iPhone for
ten minutes settles it. Nothing else will.**

### 3. What is new underneath, in case you notice it

- **There is a limit on how fast one person can build journeys** — about ten in ten seconds. You
  will not reach it in normal use; you got nowhere near it even when deliberately hammering it.
  If you ever do, journeys briefly stop loading and then recover on their own.
- **The site now sits behind Cloudflare.** That is what enforces the limit, and it is what
  replaced the job the password was quietly doing.

**Best bug report:** the URL from the address bar, and a screenshot if it is a layout problem.
For the iPhone questions, just tell me which of the three failed.

*Detail: `docs/superpowers/2026-07-28-password-removal-execution-log.md`. Runbook: `infra/README.md`
§1a and §8a.*

## DONE — 2026-07-27 — the app is on the internet, and this is the first real run

**DONE 2026-07-27 — PASSED on everything exercised, on a real phone, and it exposed one
inert piece of code.** Exercised by the owner on an **Android Pixel** against the live site.

**Confirmed:**

- **The password box lets someone *in*.** He signed in before doing anything else. This is
  the first time in the project's history that has been witnessed by a human in a browser —
  every check before the cutover proved only that the site *refuses*.
- **No collision with the gesture bar at the bottom.** See the finding below for what this
  does and does not prove.
- **All buttons, and multiple bypasses, worked as expected on the phone.**
- **Paths appear unchanged** — the single most valuable step in the entry, since the whole
  cutover was supposed to move nothing about routing.

**⚠ RETRACTED — the mangled artist descriptions were never real.** The owner reported that
The Beatles has *always* rendered correctly, live and in dev, and he is right. Read straight
out of the adopted artifact (sha256 `4cb84ef9…`, checked against its sidecar) the
disambiguation is `UK rock band, “The Fab Four”` — correct UTF-8, correct curly quotes.
Decoding those same bytes as cp1252 reproduces `â€œThe Fab Fourâ€` exactly. **The mangling
was in the tool that read the live response, not in the artifact and not in the app.**

This is the **second** time console mojibake has been mistaken for corrupt data here — see
`findings/2026-07-19-listenbrainz-probe.md:298`, which recorded the same conclusion. It
removes one of the reasons that had been accumulating for a graph rebuild. Corrected in
`NEXT.md`; the two Track C records are annotated in place rather than rewritten.

**⚠ Found while verifying the above, and it is not a user-visible fault today.** The bar at
the bottom reserves space for the phone's system bar with
`env(safe-area-inset-bottom)` (`frontend/src/components/PlayerBar.tsx:10`) — but
`frontend/index.html:6` does **not** set `viewport-fit=cover`, and without it that value is
**0 in every browser, on every device, including iPhones**. So the reservation has never
been exercised because as written **nothing can exercise it**; it is inert code, not
untested code.

The bar clears the system bar anyway, which is why the pass is genuine: without
`viewport-fit=cover` the browser already shrinks the page to avoid the inset, so the
default does the job the reservation was written to do. **The risk is latent, not live** —
it bites only if someone later adds `viewport-fit=cover` believing the reservation is
covering them. Recorded, not fixed; no fix is proposed.

**NOT covered by this pass, and it is not a criticism of it — an Android device cannot
answer these:**

- **iOS Safari rendering, and the iPhone home indicator specifically.** Question 2 of this
  entry was written in iOS terms; a Pixel exercises a real browser and a real gesture bar,
  which is genuinely more than any emulator did, but it is not Safari.
- **Question 3 — does the keyboard leave artist names alone.** This was always an iOS
  autocorrect behaviour and is unrunnable on Android.
**Steps 3–6 then reported separately, all PASSED — so this is a per-step confirmation of
all six**, the strongest shape this file records:

- **Clips played**, exercised against the standard suite: pausing, bypassing, and letting one
  clip run into the next. Behaviour consistent with the local dev app.
- **The shared journey link works, and this is the headline.** He sent a path link to a
  person who had **never signed in**; after authenticating, that exact path appeared. It had
  never been proven in a browser before, only mechanically, and this is the first evidence
  that sharing works end to end **for a recipient rather than for its author** — which is
  the whole point of Gate 2.
- **`/nowhere` showed the correct page with a link back.**
- **A wrong password names `artistpath`** on the refusal page, confirming `RMD-11` in use.

**Still not covered — iOS.** An Android device cannot answer these, and it is not a
criticism of the run:

- **iOS Safari rendering, and the iPhone home indicator specifically.** Question 2 was
  written in iOS terms; a Pixel exercises a real browser and a real gesture bar, which is
  more than any emulator managed, but it is not Safari.
- **Question 3 — does the keyboard leave artist names alone.** Always an iOS autocorrect
  behaviour; unrunnable on Android.

*Original queued text follows.*

## QUEUED — 2026-07-27 — the app is on the internet, and this is the first real run
<!-- "(latest)" stripped 2026-07-27 on completion, per the convention below: only a live
     QUEUED entry carries it. -->

**This is the first entry in this file with a URL in it.** The app is live. Open it from
anything — your desktop, your phone, someone else's machine.

**Address:** `https://d2n3xqz3pttguf.cloudfront.net`
**Username:** `artistpath` — **Password:** the one in `infra/.env.deploy` on this machine.

**Nothing about *which artists* you get has changed.** No routing, no graph, no weighting, no
cost function. It is the same artist map as your desktop copy, checked mechanically on three
separate counts. **A journey you build on the website is the same journey you would have got
on your machine this morning** — that is the single most valuable thing to confirm.

**Nothing is running on this machine and nothing needs to be.** No local servers were left
behind. Everything below happens against the website.

### The headline: the phone half is finally runnable

**This is what has been waiting since 26 July.** Three things could never be answered without
a real device, and all three are still unanswered:

1. **Is it actually usable in your hand?** Can you read every artist's name, and hit the right
   bypass button with a thumb?
2. **Does the bar at the bottom clear the home indicator**, or is it tucked underneath? Space
   is reserved for it, but a desktop browser reports that space as zero, so **that reservation
   has never once been exercised by anything.**
3. **Does the keyboard leave artist names alone?** Type a few with accents or odd
   capitalisation. This is an iPhone behaviour and cannot be simulated on a desktop at all.

### What to exercise

1. **Two or three journeys you already have a feel for**, on the desktop first. These must be
   unchanged. If a familiar pair gives you a *different* journey, something is wrong.
2. **The same thing on your phone.** Then the three questions above.
3. **Play clips and press both bypass buttons a few times**, on both. The clips come from the
   same music service as before.
4. **Send yourself a journey link** — copy the address bar mid-journey, open it fresh. It
   should land you on that exact journey rather than an error. **This one has never been
   proven in a browser**, only mechanically, and it is the thing that makes sharing work at
   all.
5. **Type a nonsense address** on the end, like `/nowhere`. You should get a short page with a
   link back, not a blank screen.
6. **Get the password wrong once, deliberately.** The refusal page should tell you the
   username is `artistpath`. **When you share this with someone, send them the address and
   the password only** — the page tells them the rest.

### What "wrong" would look like

A familiar pair giving a *different* journey; a shared link landing on an error instead of the
journey; a blank white page with no text at all; the refusal page not naming the username; on
the phone, an artist's name squeezed to nothing, or the bottom bar tucked under the home
indicator; clips that no longer play.

**If you ever see the words "the app did not load, reload the page"** — that is a message
working as intended, not a new fault. Tell me if you see it, though.

### Two things now true out there that were not

- **The thing on the internet no longer tells browsers a page on your own machine may read
  from it.** That was the exposure you accepted on 27 July rather than publish twice. It is
  fixed *out there* now, confirmed by checking the live site before and after rather than
  assuming.
- **Publishing is now one command instead of three typed in a particular order.** The order
  mattered and nothing enforced it; getting it wrong gave returning visitors a blank page and
  was invisible to whoever published. It is now checked automatically, ten different ways.

**Known and unchanged:** artists with only one connection still cannot appear in the middle of
a journey. Clip playback defects are closed and unrelated.

**One cosmetic fault I found and did not fix**, so it does not surprise you: some artists'
short descriptions show mangled punctuation — The Beatles reads `UK rock band, â€œThe Fab
Fourâ€` in the search dropdown. It is in the artist map itself, so fixing it means rebuilding
the map, which is your call rather than mine.
<!-- ⚠ RETRACTED 2026-07-27: this paragraph is WRONG. The artifact is correct UTF-8; the
     mangling was in the tool that read the live response. See the RETRACTED note in the DONE
     marker at the top of this entry. Left in place because it is the text you were sent. -->

> **⚠ The paragraph immediately above is RETRACTED and was never true** — see the DONE
> marker at the top of this entry. Kept because it is what was queued.

**Best bug report:** the URL from the address bar, and a screenshot if it is a layout problem.

*Detail: `docs/superpowers/2026-07-27-gate2-track-c-execution-log.md`.*

## DONE — 2026-07-26 — the search box you caught, on the desktop

**DONE 2026-07-26 — PASSED on all five steps, run before the merge.** Exercised by the owner
against every numbered step individually:

1. **His own defect — confirmed resolved.** Typing over a chosen artist now un-chooses them
   and "Find path" goes dead until one is picked again.
2. **No journey changes noticed** on familiar pairs — the step this entry existed for, and
   the one that matters most, since seven pieces of the app were touched and none of them
   was supposed to move the routing.
3. **No change to clips or playback behaviour.**
4. **The narrow window shows the responsive layout working as intended.**
5. **A nonsense address shows the new error page with a link back.**

**This is a per-step confirmation, not "nothing surfaced"** — the stronger of the two shapes
this file records, and the same standard as the Track A entry below rather than the weaker
passes above it.

**What it does NOT discharge: the deferred phone section at the bottom of this entry.** A
narrow desktop window exercises the layout *rules*; it cannot exercise Safari's rendering,
the iOS keyboard, or the home-indicator spacing — the emulator reports that spacing as zero,
so the code path reserving it remains unexercised by anything. That section keeps its trigger
(the Gate 2 cutover) and is not closed by this pass.

*Original queued text follows.*

## QUEUED — 2026-07-26 — the search box you caught, on the desktop

**⚠ Corrected before it was run.** This entry originally asked you to open the app on your
phone. **You cannot** — the app runs only on this desktop and there is no address a phone
could reach. The phone half is now a deferred section at the bottom with its trigger named,
and everything under "what to exercise" is runnable on the desktop today. The mistake is
recorded so the next entry does not repeat it.

**Nothing about *which artists* you get has changed.** No routing, no graph, no weighting, no
cost function. Any journey you built this morning is the same journey now. Seven separate
things changed and none of them is the router.

**The one you already know about.** You found this today: put two artists in, press "New
path", type a different artist over one of the pre-filled names, press "Find path" — and it
took you to the *old* artist. It now refuses. The moment you type over a chosen artist, the
"Find path" button goes grey until you pick someone from the dropdown again. **The button
going dead is the whole message** — there is no new wording to look for.

Worth knowing, because it changes what to expect: this was never about the dropdown being
slow. Waiting for it never helped. Only *clicking a name in it* ever chose an artist, and it
still is.

**The big change is one you cannot properly see yet.** Until today there was no phone layout
at all — on an iPhone the artist's name was squeezed to nothing by the two bypass buttons
sitting beside it. Now those buttons take a row of their own underneath the artist and the
name gets the full width. **On a desktop nothing should look any different from yesterday**,
and that is the only half you can check today.

**You can preview the phone layout without a phone, and it is worth thirty seconds:** make
your browser window very narrow — drag it in until it is roughly a third of your screen — and
look at a journey. Below a certain width the two bypass buttons should drop onto their own
line and the artist's name should stay readable. That checks the layout rules themselves. It
does **not** check anything specific to a real phone, which is why the section at the bottom
exists.

**Four smaller things you may never see, which is the intention.**

- A search that *failed* now says so, instead of looking identical to a search that found
  nobody.
- A request that never comes back now gives up after a while and offers you a "Try again"
  button, instead of sitting on "Building your path…" forever.
- A card that cannot actually start playing now stops claiming to play.
- A mistyped or truncated link now lands on a page with a way back, instead of a blank screen.
- A phone keyboard should stop "correcting" artist names as you type them. **Not checkable
  here** — it needs a real phone.

**What to exercise — all of this works on the desktop:**

1. **Your own defect.** Build a journey, press "New path", type over one of the filled-in
   names, and try to press "Find path" straight away. It should be **greyed out** until you
   choose a name from the dropdown. Then choose one and confirm it goes where you asked.
   This is the main thing to confirm.
2. **Two or three familiar journeys**, as a regression check. These must be unchanged — the
   most valuable step in this entry, because seven pieces of the app were touched and none of
   them was supposed to move the routing.
3. **Play a few clips and press both bypass buttons a few times.** Nothing here was meant to
   change, including the artwork on each card.
4. **Drag the window narrow** and look at a journey, per above.
5. **Type a nonsense address** — something like `localhost:5173/nowhere`. You should get a
   short page saying there is nothing there, with a link back, rather than a blank screen.

**What "wrong" would look like:** a familiar pair giving you a *different* journey; "Find
path" staying live after you type over an artist, or staying grey after you pick a new one;
a card that no longer plays when it used to; missing cover artwork; the bypass buttons
failing to drop onto their own line in a narrow window; or a nonsense address still showing
a blank page.

**Known and unchanged:** artists with only one connection still cannot appear in the middle of
a journey. Clip playback defects are closed and unrelated.

**Best bug report:** the URL from the address bar, and a screenshot if it is a layout problem.

### ✅ TRIGGER FIRED 2026-07-27 — was DEFERRED until the app was live on AWS

**The cutover has happened and there is now a URL a phone can open, so this is runnable.**
**It has been folded into the newest entry at the top of this file** — run it there, with the
address and password, rather than here. This section is left in place because the entry it
belongs to records what was and was not covered by the desktop pass.

*Original text follows.* Three things can only be answered on a real device, and all three
were unverified when this was written — and still are:

1. **Is it actually usable in your hand?** Can you read every artist's name, and hit the right
   bypass button with a thumb?
2. **Does the bar at the bottom clear the home indicator**, or is it tucked underneath? The
   code reserves space for it, but a desktop browser reports that space as zero, so the
   reservation has never been exercised.
3. **Does the keyboard leave artist names alone?** Type a few with accents or odd
   capitalisation. This is an iOS behaviour and cannot be simulated here at all.

**There is one way to bring this forward if you want it**, and it is optional: the dev server
can be told to accept connections from other devices on your wifi, which would let your phone
open it directly. It needs a Windows Firewall allow on first run. Say the word and I will set
it up — otherwise this waits for the deploy, which is the next track anyway.

*Detail: `docs/superpowers/2026-07-26-gate2-track-d-execution-log.md`.*

## DONE — 2026-07-26 — six fixes under the bonnet, and one you can see

**DONE 2026-07-26 — PASSED on every step, and it found a defect that is not Track A's.**
Exercised by the owner. **No regression:** familiar journeys unchanged (the step this entry
existed for), same-artist correctly refused, clips and all four controls — both bypass
buttons, "New path", "Reset path" — behaving as expected.

**Unlike the two preceding entries, this record carries per-step confirmation**, not "nothing
surfaced": the owner reported against the numbered checks individually. That makes it the
strongest pass in this file, and specifically it is direct evidence for check 1, which no
test can supply.

**Found in use, and it is pre-existing rather than new.** Typing over an already-chosen artist does not un-choose them: the box holds the typed text and
the page holds the previously selected artist, and nothing reconciles the two. "Find path"
stays enabled and routes to the **old** artist. The "New path" prefill did not introduce this —
it removed what was masking it (before, the button began disabled, so you had to pick from the
dropdown at least once). **It is not a race with the autocomplete**: waiting for the dropdown
does not help, only clicking an entry in it does. Not attributable to Track A; `pathfinding.py`
was never edited.

*Original queued text follows.*

## QUEUED — 2026-07-26 — six fixes under the bonnet, and one you can see
<!-- Retained original text of the DONE entry above. "(latest)" was stripped 2026-07-26:
     two headings in this file claimed it at once, which is ambiguous at a glance. Only the
     newest QUEUED entry carries "(latest)". -->

**⚠ This is the retained original text of an entry already marked DONE above. Do not run it
as a fresh entry.**

**Ten minutes, no waiting. Both servers are already running and nothing owns them**, so
they will outlive this session and every terminal. Started **after** the last commit, so
they serve today's code:

| what | address | PID |
|---|---|---|
| the app | **http://localhost:5173** | 211432 |
| the service behind it | http://127.0.0.1:8000 | 231092 |

Open the first one in a browser and it works. **If you want them gone**, stop those two
PIDs — nothing else will.

The app was rebuilt today for the first time in a while, so this is a regression check
first and a new-feature check second.

**Nothing about *which artists* you get has changed.** No routing, no graph, no weighting,
no cost function. Any journey you built yesterday is the same journey today — that is the
main thing to confirm, because six separate pieces of the app were touched.

**The one change you can actually see.** Putting the *same* artist in both boxes used to
give you a single card and nothing to do. It now refuses, with a message asking you to
pick two different artists. That was a real defect: a journey with one stop and no
destination is not a journey.

**Two failures you will no longer meet, and probably never noticed.** A card whose track
information came back incomplete from the music service used to break that card outright;
it now just plays, or stays quiet. Same for a hiccup in the clip store. Both used to be
errors. You cannot easily provoke either on purpose — the point is that nothing new
should break.

**One limit that is new.** After about two hundred bypass presses on a single journey the
app will now stop accepting more. Your longest recorded run was a hundred, so you should
never reach it, but it is there deliberately — an unlimited list let a single request cost
the server an unbounded amount of work.

**What to exercise:**

1. **Two or three journeys you already have a feel for.** These must be unchanged. This is
   the most valuable thing in this entry — if a familiar pair produces a *different*
   journey, something is wrong, because nothing about routing was supposed to move.
2. **Put the same artist in both boxes.** You should get a clear refusal, not a single card.
3. **Play clips on several cards, and press both bypass buttons a few times.** The clip
   machinery was reorganised underneath — the behaviour should be identical to yesterday.
4. **Press "New path" and "Reset path" once each**, as a quick regression on the controls
   you confirmed last time.

**What "wrong" would look like:** a familiar pair giving you a *different* journey; a card
that no longer plays when it used to; the same-artist case still giving you one card; any
error message you have not seen before; or a bypass press that does nothing.

**One thing you will notice in the terminal, and it is deliberate.** The server now prints
a line of dense JSON every time you build a journey or play a card. That is the new
record-keeping, and it is the point of today's work — it is what will let us answer
questions about how the app behaves once other people are using it. It is not an error,
and it is not noise to be fixed.

**Known and unchanged:** artists with only one connection still cannot appear in the middle
of a journey. Clip playback defects are closed and unrelated.

**Best bug report:** the URL from the address bar.

*Detail: `docs/superpowers/2026-07-26-gate2-track-a-execution-log.md`.*

## DONE — 2026-07-26 — journeys now always have someone in the middle

**DONE 2026-07-26 — PASSED, no notes.** Exercised by the owner; nothing wrong found and
nothing worth commenting on. **This discharges F1** — its condition was an observation,
and this is that observation. Gate 1's last item is closed.

**Recorded caveat, per this file's precedent.** The report was "exercised and passed", so
the record does **not** carry which pairs were tried, nor whether the `Doves → Elbow`
"next to each other" line was seen. Read this as *no defect surfaced in ordinary use*,
not as a per-step confirmation of the three numbered checks.

**Two questions this entry asked are still unanswered, and a pass is not an answer to
them:** how long a forced detour may get before a journey stops feeling like a journey
(uncapped, deliberately), and whether routing two famous artists through a third famous
one reads as reasonable or as lazy. Both are owner-judgement questions that no
measurement settles; they carry forward.

*Original queued text follows.*

## QUEUED — 2026-07-25 — journeys now always have someone in the middle

**Ten minutes, no waiting.** Pick two artists who are very close to each other —
`Radiohead → Weezer` is the one you reported, and any two artists you'd expect to
sit right next to each other will do.

**What changed.** Before, a pair like that gave you two cards and nothing to press.
Now the app routes around the direct connection and puts at least one artist in
between. Nothing else about paths changed — any journey that already had someone in
the middle is exactly the journey you got yesterday.

**What to exercise:**

1. **`Radiohead → Weezer`.** It should now have at least one artist between them.
2. **Two or three pairs you already have a feel for**, as a regression check. These
   should be unchanged.
3. **A pair that is very close but obscure** — try `Doves → Elbow`. This one *cannot*
   be given a stop: Elbow has exactly one connection in the whole graph and it is to
   Doves. You should get two cards **plus a line saying they're next to each other
   and there's nobody in between**. The line appearing is the thing to check.

**Two things worth your opinion, because no measurement can settle them:**

- **How long is too long?** Forcing a way round can produce a longer journey than you
  asked for. Usually it is one extra artist, but it can be a lot more. If that feels
  wrong, say so; it is capped at nothing right now, deliberately.
- **Famous pairs get a famous stop.** `Radiohead → Weezer` routes through The
  Beatles. That is the cheapest way round, not a preference. Worth knowing whether it
  reads as reasonable or as lazy.

**What "wrong" would look like:** a pair that still gives you two cards with no
explanation; a journey between two artists you know that has *changed* when it should
not have; or the "next to each other" line showing up on a normal journey.

**Best bug report:** the URL from the address bar.

---

## DONE — 2026-07-26 — the three playback fixes from your last run

**DONE 2026-07-26 — PASSED, no notes.** Exercised by the owner; no defect found. The three
playback defects found in the 2026-07-25 use run (a finished clip skipping the next artist;
audio surviving "← New path"; audio surviving a bypass or "↺ Reset path") are **confirmed
in use and closed.**

**Recorded caveat.** As above, the record does not carry per-step confirmation — this is
*nothing surfaced across ordinary use*, not five individually witnessed checks. The
riskiest failure this entry guarded against (cards no longer playing at all) would have
been unmissable, so a clean pass is strong evidence on that one specifically.

*Original queued text follows.*

## QUEUED — 2026-07-25 — the three playback fixes from your last run

**Ten minutes, no waiting.** This covers what your last run found. Nothing about *which
artists* you get has changed — no routing, no cost function, no graph.

**What to exercise:**

1. **Play a clip and let it run to its end, twice over.** Each time, the card that starts
   next should be **the one immediately below** the one that just finished. Previously it
   jumped over one artist every time.
2. **While a clip is playing, press "← New path".** The audio should stop the instant you
   press it. Previously it kept playing.
3. **While a clip is playing, press "↺ Reset path".** Same — silence on the press, not when
   the new path finishes loading.
4. **While a clip is playing, press a bypass button.** Same again.
5. **Quick regression, because the fix touched the player itself:** play a card, pause it on
   the card, resume it. It must carry on from where it stopped rather than restart. Then
   check a clip still plays at all — the riskiest version of this fix silenced the app
   completely, and it was caught in testing rather than in use.

**What "wrong" would look like:** an artist skipped when a clip ends; audio continuing after
any of those three buttons; a resumed clip restarting from the beginning; or cards that no
longer play at all.

**Known and unchanged:** a card with no clip is silent by design and is stepped over when a
clip ends — that is correct, not a skip. A path with only your two artists still offers no
bypass buttons; that is the zero-intermediary case, and you have decided every journey needs
at least one stop. **⚠ 2026-07-25: that is now BUILT — see the newest entry at the top of
this file. If you are running this older entry after the fact, expect an artist in between.**

*Detail: the execution log's §18.*

## DONE — 2026-07-25 — does a clip still play after the tab has been open a while

**DONE 2026-07-25 — PASSED. C2 is closed.** Tested in one tab after the wait: an unplayed
card, a previously played card, and a card left paused all played correctly. That exercises
the whole chain against the live service — the browser asks for a new link, the server
re-signs it, the audio plays — which is what no test could do.

**Found while testing, and now fixed** (see the entry above): a finished clip skipped the
next artist; "New path" did not stop the audio; and bypass / "Reset path" silenced it only
once the new path had loaded.

*Original queued text follows.*

## QUEUED — 2026-07-25 — does a clip still play after the tab has been open a while

**This unblocks the entry below, which is kept for the record.** The reason it could not pass
has been fixed: the page now asks for a fresh link **at the moment you press play**, instead
of relying on the one it was handed when the card first appeared. A failure to play also
retries once, silently, with a newly issued link.

**What to exercise, and it needs patience rather than attention:**

1. **Open a path and leave the tab open for at least twenty minutes.** Do not reload, do not
   navigate away, do not press anything. Twenty minutes is chosen because a link now
   measurably dies at fifteen, so anything shorter proves nothing.
2. **Come back and press play on a card you have not played yet.** It should play normally.
3. **Then press play on a card you *did* play at the start.** Same expectation.
4. **Let a clip run to its end** and check the next card starts on its own.
5. **Pause a card, wait a few minutes, press play again.** It should resume where it stopped,
   not restart from the beginning — and it should not go silent.

**What "wrong" would look like:** silence, or a visibly stuck play button, on a card that
worked when the page was fresh. Also a clip that jumps back to the start when you resume it
after a pause — that would mean the fix broke the pause behaviour you confirmed earlier.

**Known and not a defect:** cards that were silent from the beginning stay silent. That is
the wrong-artist fix declining to play a stranger, and it is unrelated to this.

**Best bug report:** the URL from the address bar, plus roughly how long the tab had been
open.

*Detail: the execution log's §17. The original blocking notice follows.*

## ⛔ SUPERSEDED — 2026-07-25 — was BLOCKED; the cause is now fixed, see above

**Found by a live check against the real music service, after this entry was written and
before any of it was run.** Question 1 (does the clip play the right artist) is fine and
worth doing. **Question 2 — does it still play an hour later — cannot pass yet, and would
fail for a reason that has nothing to do with what it is testing.**

**What is actually true.** The server half works, and it was verified live rather than
argued: asking twice for the same artist returns the same song with a freshly signed link
both times. That is the fix doing exactly its job. **The browser half is incomplete.** The
page only asks for a new link when a card is first drawn. If you leave the tab open and come
back, nothing on the page ever asks again, so it still holds the link it was given at the
start — and those links now measurably last **15 minutes**, not the "under an hour" the
record assumed. Pressing play after an hour would give you silence: the original bug,
unchanged, on a page whose server has already been fixed.

**So running it now would tell you "the fix failed" when the fix works.** That is the worst
kind of result — a real-looking answer pointing at the wrong thing.

**What is needed:** the page must ask for a fresh link at the moment you press play, rather
than relying on the one it was handed when the card appeared. That is a small piece of
design work, not a typo, and it has not been done.

**Question 1 is unaffected — run that whenever you like.** It needs no waiting: open a path,
press play on several cards, and listen for whether the voice matches the name on the card.

*Detail: the execution log's §15.*

## DONE — 2026-07-25 — do the clips play the right artist, and do the buttons behave

**DONE 2026-07-25, question 1 only. No defect found; one pre-existing issue re-surfaced.**

- **Clips: nothing wrong found.** Every artist card the owner tested played an artist matching
  the card. **Recorded caveat, and it matters:** he could not recall which artists produced
  wrong clips before, so this is "nothing jumped out across the cards I happened to meet",
  not "the known failure is gone". A weaker signal than a targeted retest, and correctly so.
- **The targeted retest was then run session-side, against the live service**, because it is
  mechanical and needs no ear. The roadmap's own worked example — the band whose name is also
  a song title by a different artist — now returns a track **by the band**, where it
  previously returned the same-named song by the rapper. That is the documented failure case,
  exercised end-to-end through the running API, and it passes. Together with the live
  verification in the execution log's §15, **C1 is confirmed in use and closed.**
- **C2 remains fixed-not-closed** — its question is the blocked one above, and the browser
  half is still incomplete.
- **Zero intermediaries, reported unprompted: Radiohead → Weezer produced a two-card path
  with nothing between them and nothing to press.** Not a new defect and not caused by the
  UX work — it is the known famous→famous case, recorded 2026-07-23, never fixed. See §16 of
  the execution log; the owner's expectation that it had been fixed is itself the finding.
- The remaining interface items (pause on a card, audio stopping on bypass, the two controls
  at the top, bypass hidden on the end cards) were not separately reported on.

*Original queued text follows.*

## QUEUED — 2026-07-25 — do the clips play the right artist, and do the buttons behave

**Scope note: the "does it still work an hour later" question is NOT part of this entry.**
It was, and it has been split out and blocked — see the entry above. Everything below can be
done in ten minutes with no waiting.

**This one is app-facing, and it is the first entry in a while that is.** One clip defect and
six interface changes. Nothing about *which artists* you get changed — no routing, no cost
function, no graph. The journey between any two artists is the same journey as yesterday;
only the audio and the buttons are different.

**The question this entry exists to answer, and it needs you rather than a test:**

> **Does the clip play the artist whose name is on the card?** Previously the app searched
> the catalogue and took the first result — but that search matches *song titles* as well as
> artist names, so searching for the band The Format returned a song *called* "The Format"
> by a rapper, and played that. Now the app checks the returned track really belongs to the
> artist on the card.

**A deliberate trade you should know about before it looks like a bug.** When no track
matches the artist, the card is now **silent instead of playing a stranger** — and a card
whose clip fails to load for any other reason goes silent too, rather than showing an error.
So you will meet some cards with no audio that previously played something. That is the fix
working. Worth reporting only if it happens to artists you would expect any streaming
service to have.

**What to exercise:**

1. **Any path, and press play on several cards.** The one thing to watch is whether the
   voice you hear plausibly belongs to the name on the card. Obscure artists are where this
   was worst, so a path that digs is more informative than a famous one.
2. **The pause button on a card.** It only ever worked on the bar at the bottom of the
   screen; pressing it on the card itself used to restart the track from the beginning. It
   should now pause, and pressing again should resume from where it stopped.
3. **Press a bypass button and listen.** Audio from the old path should stop when the new
   one arrives, rather than playing over it.
4. **Look at the first and last cards.** The two artists you chose no longer offer "not for
   me" or "I know them" — rejecting them never made sense, since the whole journey is
   defined by them.
5. **The two controls at the top of a path.** "← New path" takes you back to picking two
   artists, **with the pair you were just on already filled into the boxes** — so swapping
   one end for a new artist does not mean retyping both. "↺ Reset path" throws away every
   bypass you have pressed and puts you back on the original path between the same two
   artists; it only appears once you have pressed something. Before this, the only way off
   a path page was the browser's Back button.

**What "wrong" would look like:** a clip that plays an obviously different artist; a card
whose pause button still restarts the track; audio from a bypassed path continuing to play;
a bypass button on the first or last card; "New path" arriving at empty boxes, or with a
dropdown of search results already covering the page. Also worth a mention: **a path with
only your two artists and nothing in between now offers no bypass buttons at all** — that is
expected given the change, but it leaves you with nothing to press, and it is the known
zero-intermediary case (a famous-to-famous pair that needs no one in between) rather than a
new defect.

**Best bug report:** the URL from the address bar, plus the artist name on the card if a
clip played the wrong person.

## DONE — 2026-07-23 — pre-Track-2 guards: a rename through the whole cost path

**DONE 2026-07-23 — nothing found, which is the expected outcome.** No behaviour change
was intended and none was observed. Owner's summary: "everything seems stable and
functions similar to other tests."

- **Search (reported first — it is the first action a real user takes).** Order looks
  correct, and one case is strongly confirmational: typing `The ` returns The Beatles,
  The Rolling Stones, The Strokes, The Beach Boys. `My ` returns My Chemical Romance,
  My Bloody Valentine, My Morning Jacket, then unfamiliar artists. **This is the most
  discriminating evidence in the run** — search ranks on the renamed popularity quantity,
  and if that read had been crossed with degree or with any other value, a prefix shared
  by many artists is exactly where the wrong ones would surface first. They did not.
- **Two familiar paths:** no discernible difference or issues. **Recorded caveat:** the
  owner was not closely inspecting path content, so this is "nothing jumped out", not a
  path-quality judgement — a weaker signal than the search result, and correctly so, since
  path *quality* is Track 2's question and not this entry's.
- **Repeated bypass, both buttons:** pressed `known` repeatedly and `dislike` repeatedly,
  no issues on either.

**What this does and does not license.** It clears the rename as a regression: the guards
work is safe to merge. It says nothing about whether paths are *good* — the F2 complaint
(more bypasses do not surface more obscure artists) is untouched and remains Track 2's
objective.

*Original queued text follows.*

## QUEUED — 2026-07-23 — pre-Track-2 guards: a rename through the whole cost path

**Expected outcome: nothing changes.** This is a regression check, and a short one.

**What changed.** No behaviour, by intent. A lot of quantities in the routing code were
renamed so their names say what they measure, and the builder gained a check that refuses
to produce a graph missing famous artists. **The graph itself is untouched** — same
adopted artifact, same checksum, no rebuild. The routing sums the same numbers in the
same order; only the labels on them moved. (Detail, if wanted: execution log,
"Pre-Track-2 guards".)

**Why it is worth ten minutes anyway.** A rename can swap two quantities inside a
calculation and still pass every test, because the tests check the routing on tiny
made-up graphs where two quantities that differ in the real world happen to be equal.
Nothing automated checks whether real paths between real artists still feel right. That
is the only thing this queue entry is for.

**What to exercise:**

1. **Any two paths you already have a feel for.** Miles Davis → Daft Punk, or whatever
   you used last time. They should be the same paths you saw yesterday.
2. **On one of them, press "know them already" five or six times in a row.** Use that
   button rather than "not for me" — both were touched, but "know them already" pushes
   hardest on the changed code, so it is where a mistake would show first. Then press
   "not for me" two or three times on a fresh path, just to cover the other button.
3. **Search two or three artists.** Search orders its results by popularity, which was
   one of the quantities touched — so the check is simply that the obvious match comes
   first, not buried under obscure artists with similar names.

**What "wrong" would look like:** paths that are *different* from what you remember for
the same two artists — that is the whole signal here, since nothing was supposed to
change. Also: bypass no longer lengthening or reaching further; search results in an
odd order (e.g. obscure artists ranked above famous ones). A "no path" without
exclusions remains structurally impossible and would be a real defect.

**Clips (C1/C2) are still known, unrelated, and untouched.**

**Best bug report:** the URL from the address bar.

## DONE — 2026-07-23 — tie-break fix adopted: famous-artist neighbourhoods changed

**DONE 2026-07-23. No regression; no defect attributable to the fix.** Radiohead is
searchable and routable (absent before); famous-artist neighbourhoods behave as
score-ranked. Six findings recorded in
`2026-07-23-repair-and-retune-execution-log.md` under "Track 1 — use-the-app results",
each with a success condition. Headline: the owner confirmed by ear that **more bypasses
do not surface more obscure artists** (F2) — direct experiential confirmation of §2.9 on
the repaired graph, and the primary Track 2 motivation. One new standalone item: F1,
zero-intermediary famous→famous paths (a new surface the fix exposed, candidate for a
min-length guard). A stale API server on :8000 was found serving the *pre-fix* graph and
cleared before testing — noted so a future tester checks the port first.

*Original queued text follows.*

## QUEUED — 2026-07-23 — tie-break fix adopted: famous-artist neighbourhoods changed

**What changed.** The graph the app routes on. The §2.8 tie-break fix is in: top-k
selection now ranks unclipped strengths, so ceiling-saturated famous artists keep their
genuinely strongest neighbours instead of the lowest-MBID ones. ~0.4 % of nodes change
neighbours; everything else is verified identical
(`findings/2026-07-23-tiebreak-fix-adoption.md`). The dev API now boots the full
adopted artifact by default — the 5k fixture is retired, so what you test is what
the record measured.

**What to exercise:**

1. **Search Radiohead.** It was absent from the previous graph entirely; it must now be
   searchable and routable. This is the headline change — worth ten seconds.
2. **Routes that end at or pass through very famous artists** (The Beatles, Coldplay,
   Muse, Nine Inch Nails…). Their neighbourhoods went from ~4–7 arbitrary survivors to
   ~50 score-ranked ones, so first paths and bypaths around them may genuinely differ.
3. **A couple of ordinary mid-popularity paths** as a regression check — these should
   feel unchanged (their neighbourhoods are untouched).

**What "wrong" would look like:** a "no path" without exclusions (structurally
impossible, so a real defect); an artist that was searchable yesterday now absent;
famous-endpoint paths that feel *worse* than before. Clip bugs remain known, unrelated,
and queued (C1/C2).

**Best bug report:** the URL from the address bar.

## DONE — 2026-07-23 — one labelled inference needs your ear, and nothing else

**DONE 2026-07-23, verdict: "No, mostly unknown."** The §2.11 inference is confirmed —
in-graph popularity does not mean fame at the top of the distribution, so a success
criterion phrased as an in-graph popularity percentile is gameable. Consumed by
`specs/2026-07-23-defect-remediation-and-cost-retune-design.md` §1 and §4.3 (the next
experiment is scored on an external fame proxy instead). The optional
Metallica → Taylor Swift bypass walk was not run — §2.9 already measured that channel.

**No shipped code changed.** The Phase 1 defect work (§2.8–§2.12) was measurement and record
only. This entry exists for **one question a metric cannot answer**, and it should take five
minutes rather than twenty.

**The question: do these feel well-known to you?**

> saib. · Purrple Cat · sleepy fish · Leavv · idealism · Miami Nights 1984 · Lazerhawk ·
> Stonebank · Toonorth

**Why it matters.** Every one of them scores in the **top 1–3 % by popularity** in the
adopted graph — the same band as The Beatles — because popularity here is score-weighted
co-listening and lo-fi/synthwave artists are playlist staples (§2.11).

§2.11 records, **explicitly labelled as inference and never tested**, that they would *not*
feel well-known to you. A great deal now rests on that:

- If they **do not** feel well-known → the popularity metric does not mean fame at the top,
  and any success criterion of the form "reaches below the Nth popularity percentile" is
  **gameable**. A tuning run could satisfy it by routing you from Metallica into synthwave
  and report success. §2.12 says the next experiment must be scored some other way.
- If they **do** feel well-known → the metric is fine, the gameability concern drops, and
  the next experiment gets much simpler to specify.

**How to check.** Search each in the app. You do not need to route anywhere — the question is
purely whether the name registers. Clips will help; clip defects are known and irrelevant here.

**Optionally, if you have longer:** route `Metallica → Taylor Swift` and press *know them
already* repeatedly. §2.9 measured that twenty bypasses never produce an interior artist
below the ~95th popularity percentile on either graph tested. Seeing that failure directly is
worth more than the table.

**What "wrong" would look like:** nothing here can be wrong in the defect sense — no code
changed. The only outcome is your verdict on the nine names, which settles a question the
record currently carries as an assumption.

---

## DONE — 2026-07-22 — Phase 2 adoption (`capfix`)

**DONE.** Phase 1 log §3.1 records the owner completed this: no regressions found; only
missing artists were already known to be absent.

*Original queued text follows.*

## QUEUED — 2026-07-22 — Phase 2 adoption (`capfix`)

**What changed.** The graph the app routes on. `cap_strategy` is now `mutual_knn` (an edge
survives only if each endpoint ranks the other in its top-k), which cuts the edge count to
roughly a fifth of the old graph. Nothing in the API or frontend changed.

**Nothing to prepare on this machine** — the dev graph is already rebuilt from the adopted
artifact and verified routing (`Miles Davis → Ella Fitzgerald → Mariah Carey → Justin
Timberlake → Daft Punk`). Just start the two processes and use it.

On any *other* machine, or after `git clean`, rebuild it first — it is gitignored:

> **⚠ SUPERSEDED 2026-07-23 — do not follow the command below.** The 5k fixture is
> retired and `graph-t15-capfix.bin` is no longer the adopted artifact. The API now
> defaults to the adopted 75k artifact (`graph-t15-tiebreakfix.bin`); see
> `findings/2026-07-23-tiebreak-fix-adoption.md`. Nothing needs building for dev use.

```bash
cd builder && UV_LINK_MODE=copy uv run artistpath-build fixture \
  --graph scratch/graph-t15-capfix.bin --out scratch/graph-5k.bin --size 5000
```

The seed no longer needs specifying: the fixture now seeds from the most popular artist by
default. It did not, briefly, and the resulting dev graph contained no famous artists at
all — see execution log §19. If a rebuilt graph cannot find The Beatles, that regression is
back.

**What to exercise:**

1. **Ordinary paths between artists you know well.** The blind test covered this and found
   the arms mostly similar without bypass — so this is a regression check, not a discovery
   run. Two or three paths is enough.
2. **Bypass, repeatedly, on the same path.** This is the priority. It is the channel that
   decided the adoption and the one no metric covers.
3. **Search for obscure artists.** Mutual k-NN prunes hardest in the obscure tail, and the
   largest-connected-component step runs after it.

**What "wrong" would look like:**

- **A "no path" result.** This should be impossible — the graph is pruned to its largest
  connected component, so a no-path result can only come from user exclusions. If one
  appears without exclusions, that is a real defect, not a tuning question.
- **An artist that used to be searchable and is now absent.** Retention was 98.93 %, so
  roughly 800 artists did leave the graph. Expected in the aggregate; worth knowing if it
  hits someone you would actually search for.
- **Bypass failing to lengthen or diversify** across many rerolls — the failure mode the
  losing arm showed.
- Clip bugs (wrong artist, dead audio) are **known, unrelated, and live in both arms**.
  They are Phase 1's work (C1, C2). Not worth reporting again unless they look different.

**Best bug report:** the URL from the address bar. All path state lives in it
(`/path/:from/:to?dislike=…&known=…`), so it reproduces the exact path and bypasses.

**Note on scope.** The owner has already used both arms extensively in the blind test. This
entry is deliberately light: it is a post-adoption sanity check, not a repeat of that
session.

---

## DONE — 2026-07-26 — can you find the artists you'd actually type?

**DONE 2026-07-26 — PASSED, nothing found.** Exercised by the owner; no artist reported as
unfindable, none reported as needing a second spelling, and no journey reported as
returning only the two typed artists.

**What this does and does not settle.** A null here is the weakest of the three results
recorded today, and deliberately so: the entry's value was in what it *found*, and the
record does not carry which names were typed. So it does **not** close `CNS-1` (an artist
can be stored under one name with no aliases, so it is unfindable under the name a user
would type — Pretenders / The Pretenders). It says only that the failure did not surface
on the names the owner happened to try. `CNS-1` stays open on the strength of its own
worked example, which is a direct observation and outranks a non-observation here.

Likewise it does not measure whether low-connection artists can be delivered mid-journey —
that question moved to a committed-walk measurement rather than an app session.

*Original queued text follows.*

## Queued 2026-07-26 — can you find the artists you'd actually type?

**Status: QUEUED.** Nothing was changed in the app, so this is not a regression check. The
census that prompted it was read-only. This asks one thing the census structurally cannot:
whether the app can be *reached* for artists you know.

**Why it is worth twenty minutes.** Roughly one in six artists in the graph holds one or two
connections, and one connection means the app can never put that artist in the middle of a
journey — it can only ever appear if you type it yourself. Well-known names are in that
group. Separately, a band can be stored under a different spelling of its name than the one
you would type, and then it looks absent.

**What to exercise:**

1. **Search for ten or fifteen artists you'd genuinely want to hear.** Type the name the way
   you'd say it out loud, not a corrected version. If nothing comes up, try it without a
   leading "The", and try the other spelling you'd expect. **Note both the ones that need a
   second attempt and the ones you cannot find at all** — the second attempt is the finding.
2. **Pick two artists you know are related, and see whether the journey between them offers
   anyone in the middle.** Then try the same pair the other way round.
3. **Try a few of the artists listed in the census report** — open
   `builder/analysis/2026-07-26-low-degree-census/REPORT.md` and take a handful of names from
   the top of either list. These are artists the app is unlikely ever to introduce you to.
   **Search each one and then try to build a journey that passes through it.** Use the second
   list rather than the first if you only have time for one: those artists have two
   connections, so they *can* appear in the middle, which makes a failure more interesting
   than a guaranteed one.

**What "wrong" would look like:**

- **An artist you'd definitely search for that returns nothing at all.** Worth reporting
  regardless of cause.
- **An artist you can only find on the second or third spelling.** This is the specific thing
  being looked for, and it is easy to dismiss as your own typo. It is not.
- **A journey that keeps returning just the two artists you typed**, with nobody in between.
- **The same well-known artist appearing over and over** across different journeys.

**What is already known and not worth reporting again:** that some artists have only one
connection is measured and expected — the question is only whether it bites on artists you
care about. Clip playback is closed and unrelated.

**Best bug report:** for search, just the text you typed and what you expected. For a journey,
the URL from the address bar — all path state lives in it, so it reproduces exactly.

**Detail, for anyone who wants it:** `docs/superpowers/2026-07-26-low-degree-census-execution-log.md`.
