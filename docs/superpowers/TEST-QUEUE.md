# Use-the-app test queue

**Role: ACTIVE, permanent.** The `closeout` skill appends here; `session-start` reads here
and flags anything that has been sitting untested. This is the async counterpart to the
test suites — it catches the defect class that code review and mocked tests structurally
cannot.

**One entry per closeout. Newest first. Mark an entry DONE with the date and what it
found, or DONE — nothing found. Do not delete entries; the record of what was exercised is
the point.**

> **✅ EXPIRED 2026-07-27 — the constraint below no longer applies, and its trigger is the
> reason.** The Gate 2 cutover has happened: there is a hosted URL and a phone can reach it.
> **Entries may now ask for a phone.** The deferred mobile section further down this file is
> runnable for the first time — see the newest entry.
>
> *Retained for the record:* until the cutover, the app ran only on the owner's Windows
> desktop, so no entry could ask for a phone — there was no hosted URL and a phone cannot
> reach `localhost` on another machine. Such an entry was not merely inconvenient but
> unrunnable, and would sit here looking untested when it was actually impossible. The rule
> was to write the mobile half as an explicitly DEFERRED section with its trigger named.
> Added 2026-07-26, when the Track D entry was queued asking for exactly that.

---

## N/A (latest) — 2026-08-04 (night) — you ran the listening test; the answer is "can't tell", and the reason is worth your attention

**Nothing to exercise, and nothing is running.** The listening page's server was stopped by
the session that ran it; all five ports were checked and are empty. **Not one line of the app
or the website changed, and nothing was adopted.** A journey you build now is identical to
one from this morning.

**What happened, in plain terms.** You listened to eight pairs of artists, three depths each,
two versions side by side, and saved thirty-two verdicts. The rules written down before any
of it existed said: for a result to count, one side has to win by at least five of the sixteen
"after presses" rows. **The new version won by three.** So the written-down answer is "my ear
cannot tell them apart where the numbers could" — and by those same rules, **the rebuilt map
does not get adopted and that idea closes.**

**Three things sit alongside that, and I would rather you heard them from me.**

- **On "did it find me new artists", you picked the new version on all eight pairs out of
  eight.** Not one tie, not one for the old version. That is the single cleanest signal in the
  whole test. It does not overturn the result, because nobody wrote down in advance how big a
  win on that question would count as passing — and picking a bar now, knowing the answer, is
  exactly the thing this project refuses to do.
- **Five of the seven rows where you couldn't decide, you couldn't decide because of clips.**
  Missing clips, clips that were just a song intro, and at least one that was almost certainly
  the wrong artist. You said so in your own notes at the time. So the test did not find the two
  versions similar — **it went partly deaf.** A sixteen-row test that loses five rows to broken
  audio cannot clear a five-row bar.
- **Before you pressed anything, you preferred the new version six to nothing.** The rules
  deliberately keep those rows out of the scoring, and I am not sneaking them back in. But it
  is the biggest number the test produced, and your reason for it was not about obscure
  artists at all — it was that today's app "takes weird detours" when you look at the whole
  path rather than step to step.

**Nothing is proposed for you to test.** What is waiting is a decision, and the write-up lays
out the choices without picking one: accept the answer and stop; treat the clip problem as its
own piece of work before any future listening test is spent; or open the "weird detours"
observation as a fresh question. **The rules also mean this particular test cannot be run
again** — an unwelcome answer stands.

**Still parked, unchanged:** the eight entries from 22–27 July remain queued and unruled-on,
and your ruling that making money is not a goal is still not written into the project's own
records.

Detail, if you want it:
`docs/superpowers/findings/2026-08-04-gentle-arm-blind-listen-results.md`, and the runner's
own record at `docs/superpowers/2026-08-04-gbl-run-execution-log.md`.

---

## N/A — 2026-08-04 (later) — the listening test is built and ready to run; nothing you can press changed
<!-- "(latest)" stripped 2026-08-04 (night): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate, except its
     "your one action is starting that runner session" — that has now happened, the listen
     ran, and all five safety checks passed on first firing; see above. -->


**Nothing to exercise, and nothing is running.** All five ports were checked and are empty;
no server was started and none was left behind. Not one line of the app or the website
changed. **A journey you build now is identical to one from this morning.**

**What happened, in plain terms — and you steered it twice.** The listening test you
ordered now exists as a working thing rather than a plan. You picked the eight pairs of
artists (five from the shortlist, three you recombined yourself to put more distance
between the two ends), and those are locked down in writing with a timestamp proving they
were chosen before a single journey existed. That ordering is the whole point: pairs picked
after seeing the journeys would not be evidence of anything.

**Nothing is proposed for you to test here, and the listening test is not this entry.** It
arrives through its own page, run by a fresh session that knows nothing about what the
numbers predicted. **Your one action is starting that session** and pointing it at
`builder/analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md` — it needs nothing
else, and it must not be told anything else.

**One thing I would rather you heard from me before you sit down to listen.** The program
that builds the journeys has never actually been run. That is deliberate — I was barred
from running it, because a session that has seen the new map's journeys cannot then build
an honest way of judging them blind. The consequence is that its safety checks fire for the
first time in front of you. If one of them stops the run with a clear message, that is the
experiment working and you should be told exactly what it said. If it crashes instead, that
is a broken tool rather than a result, and the session running it is under instructions to
hand it back rather than poke at it — because poking at it means looking at the journeys,
and then we have no blind runner left.

**A related honest caveat about your three recombined pairs.** Nobody has checked that any
pair produces a journey long enough to be worth judging after twenty presses, because
checking means building the journeys, which was the thing I could not do. If a pair falls
short, the program refuses to run and names it, so you would find out before listening
rather than halfway through.

**Two things still parked, neither of them about this:** your ruling that making money is
not a goal is written in my notes but **not yet anywhere in the project's own records** —
worth landing properly. And the eight entries from 22–27 July are still queued and
unruled-on.

Detail, if you want it: `docs/superpowers/2026-08-04-gbl-harness-execution-log.md`.

---

## N/A — 2026-08-04 (evening) — you decided to run the listening test, and its rulebook is written; nothing you can press changed
<!-- "(latest)" stripped 2026-08-04 (later): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate, except its
     "your one action is starting that fresh session" — that has now happened and the
     harness is built; see above. -->

**Nothing to exercise, and nothing is running.** All five ports were checked and are empty
(including the new one the listening page will eventually use); no server was started and
none was left behind. Not one line of the app or the website changed. **A journey you build
now is identical to one from this morning.**

**What happened, in plain terms — and you steered it four times.** You picked which version
of the experiment's winners gets your ears: the gentle setting only. The rulebook for that
listening test is now written and locked before anything runs: what you'll see (the same
side-by-side comparison page you preferred last time, with your picks saved automatically
instead of copy-pasted), which artist pairs (drawn from your own Spotify listening history —
you'll approve the final eight before anything is generated), and what each possible outcome
means — all fixed in advance so no result can bend the rules. Your other three steers: eight
pairs instead of five (with the pass bar raised to match, so the bigger test can't pass on a
weaker signal), the two verdict questions split so "did it dig up new artists" and "did it
still flow" are answered separately, and the next session runs on the other engine.

**Nothing is proposed for you to test here.** The listening test itself is NOT this entry —
it arrives through its own page with its own instructions, run by a session that knows
nothing about what the numbers predicted. Your one action now is starting that fresh
session; the exact line to give it is in
[`2026-08-04-HANDOFF-gbl-plan.md`](2026-08-04-HANDOFF-gbl-plan.md).

**Still parked, unchanged:** the eight entries from 22–27 July remain queued and unruled-on,
and the map-rebuild decision (whether the other data source is worth re-collecting
everything) is untouched by any of this.

Detail, if you want it: `docs/superpowers/2026-08-04-gbl-planning-execution-log.md`, and
the rulebook itself at `docs/superpowers/specs/2026-08-04-gentle-arm-blind-listen-design.md`.

---

## N/A — 2026-08-04 — the map experiment is finished and written up; nothing you can press changed
<!-- "(latest)" stripped 2026-08-04 (evening): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate, except its
     "decision waiting for you" — the listen half of that decision has now been taken;
     see above. -->


**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from yesterday.**

**What happened, in plain terms.** Yesterday's entry said the numbers existed and nobody
had read them. Today a fresh session read them and wrote up what they mean — deliberately
a session that had not run the experiment, so it could not talk itself into liking its own
results. **There is now a written answer, and there is a decision waiting for you.**

**The answer, in one line: the "I know them" button can be made to dig — but only on the
map built from the other data source.** On today's data, nothing we tried moved it at all.
Not pooling both artists' suggestion lists, not doubling the connection budget, not using
style labels, and not the new "each press digs harder" rule. On the other data source, that
last rule works: twenty presses land you on noticeably less well-known artists.

**Three things that cut against it, and I would rather you heard them from me.**

- **The deeper it digs, the less we can see.** These journeys start delivering artists our
  obscurity yardstick has no reading for — none at the start, about one in nine by press ten
  on the gentle setting. Those artists silently drop out of the score, so the improvement is
  measured on the ones we could still see.
- **On the journeys where nothing dropped out, the gentle setting misses the bar** it passed
  overall. It is close, but it is on the wrong side of a line we drew before looking.
- **No number here says any of it sounds good.** Everything measured is *how famous* the
  artists in the middle are. Nothing measures whether they belong next to each other. Only
  your ears can, and none of your listening time has been spent.

**What is waiting on you, and it is a decision rather than a test.** Whether to spend a
blind listen on the gentle setting, on both settings, or on neither — and whether the other
data source's advantage is worth rebuilding the whole map for. The write-up lays out those
options with their consequences and deliberately does not pick one, because adoption and
your ear are yours.

**One housekeeping thing I noticed while checking this file.** Eight entries further down,
from 22–27 July, are still marked as waiting for you and were never ticked off — the capfix
adoption, the tie-break change, four clip and playback checks, and the search box. Several
were probably covered by the run you did on 2 August, but nothing here says so, and I would
rather flag it than guess on your behalf.

Detail, if you want it: `docs/superpowers/2026-08-03-cre-run-execution-log.md` §15–§16, and
the write-up itself at
`docs/superpowers/findings/2026-08-04-cap-reevaluation-results.md`.

---

## N/A — 2026-08-04 (earlier) — the experiment's results are calculated; nothing you can press changed
<!-- "(latest)" stripped 2026-08-04 (later): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from yesterday.**

**What happened, in plain terms.** The map-rebuild experiment had already done the
expensive part — building journeys on all sixteen versions of the map and pressing "I know
them" twenty times on each of twenty-two pairs of artists. Yesterday that was raw
recordings. Today it is arithmetic: for every version of the map we now have the four
numbers the experiment agreed in advance to judge it on. **Those numbers exist and nobody
has read them yet, deliberately.**

**Why nobody has read them.** The rules for this experiment say the person who writes up
what it means must be a fresh session that did not run it — the same reason you would not
let someone mark their own exam. So this session calculated and stopped. **I have not
looked at which version of the map won, and I have not told you.** The write-up is the
next piece of work.

**Two things I found wrong in the notes I inherited, and both are now corrected.** The
previous session left instructions saying the calculation would not need the map files
themselves. It did — one of the four measurements compares journeys against the
most-connected artists on the real map, and that cannot be done from notes. And it had
concluded that a certain internal counter could never possibly fire; checking properly
showed it *can* fire, it simply never did. **The reassuring part of that second one:** it
means no artist you would have been shown was ever scored on a guess. Where we had no
information about how obscure someone was, that person never actually turned up in a
journey.

**Nothing is proposed for you to test, and there is no decision waiting on you** beyond
merging the pull request. The next real entry here comes when a map is actually adopted,
which is still behind a listening test.

Detail, if you want it: `docs/superpowers/2026-08-03-cre-run-execution-log.md` §13–§14.

---

## N/A — 2026-08-03 (later) — the experiment finished its measuring; nothing you can press changed
<!-- "(latest)" stripped 2026-08-04: only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from earlier today.**

**What happened, in plain terms.** The map-rebuild experiment did the expensive part: it
built journeys on all sixteen versions of the map, pressed "I know them" twenty times on
each of twenty-two pairs of artists, and wrote down what came out. That is roughly seven
thousand journeys per version. **None of it has been scored yet** — turning those into an
answer is the last remaining step, and it is deliberately done by a fresh session that did
not run the journeys.

**Two checks came back the way you want before any of that ran.** Our measuring copy of
the journey-builder was shown to return **exactly** what the real app returns, artist for
artist, on every pair — so anything we conclude is about the maps and not about our tools.
And the new "dig deeper" knob was shown to actually move journeys when turned up hard, in
every version where it exists — so if it later turns out to do nothing useful at a sane
setting, that will be a real finding rather than a broken wire.

**One loose end, and it is honest rather than alarming.** We keep two counters for artists
we cannot measure obscurity for: ones we looked up and found nothing, and ones we never
looked up at all. The first counter now demonstrably works. **The second has read zero
everywhere, on every version of the map, so we still cannot tell whether it works or
whether that zero is simply the truth.** There is a cheap check that settles it, written
down for the next session.

**Nothing is proposed for you to test, and there is no decision waiting on you.** The next
real entry here comes when a map is actually adopted, which is still behind a listening
test.

Detail, if you want it: `docs/superpowers/2026-08-03-cre-run-execution-log.md` §9–§11.

---

## N/A — 2026-08-03 (Seam 1) — the big map experiment started running; nothing you can press changed
<!-- "(latest)" stripped 2026-08-03 (later): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from this afternoon.**

**What happened, in plain terms.** The map-rebuild experiment locked in earlier today has
now actually started running, and it got through the first two of its four stages. Eleven
different versions of the map were built — same artists, different rules for deciding who
gets connected to whom — and all of them passed the safety checks. **None of them is in
the app and none will be without your say-so and a listening test.**

**Two questions got answered, and both came out the way we wrote down in advance.**

- **The "dig deeper" knob still does nothing on journeys between two famous artists.**
  We already suspected this. What is new is *why* we can now be sure. We turned that knob
  up to a setting far past anything sane — and it visibly worked, rerouting nineteen of
  twenty-two journeys. And the artists in the middle were **still just as famous**. So it
  is not that the knob is broken or too gentle. There is genuinely nowhere for it to send
  you. That points the whole experiment at the map rather than at the settings, which is
  what it was built to test.
- **Your hunch about genre evidence went the other way.** The idea was that well-known
  artists get connected on *thinner* shared-genre evidence than obscure ones. Measured, it
  is the opposite — and by enough that it is not a close call. That was the expected
  answer (it had been measured once before, in advance, and written down), so nothing is
  lost; it just closes off one branch of the experiment.

**Nothing is proposed for you to test, and there is no decision waiting on you.** The
remaining two stages are the expensive ones — actually pressing the buttons thousands of
times on each version of the map and scoring what comes out. The next real entry here
comes when a map is actually adopted, which is still behind a listening test.

Detail, if you want it: `docs/superpowers/2026-08-03-cre-run-execution-log.md`.

---

## N/A — 2026-08-03 (night) — the experiment's step-by-step run plan is written and independently checked; nothing you can press changed

**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from this afternoon.**

**What happened, in plain terms — and you steered it twice.** The locked experiment
design from earlier today now has its operating manual: a step-by-step plan for actually
running it, written by a fresh session reading the locked design cold, with every
computer check and every stopping point written down before anything runs. You then
asked for the independent numbers check, and it earned its keep three times over: it
caught a self-test that **could never fail** (it compared a formula against itself — so
a broken measuring device would have looked healthy), a group of artists the experiment
would have mislabelled as maximally unknown when really we simply never looked them up,
and one place where the locked design's own tables contradict each other. All three are
fixed in the plan; the contradiction gets a small, no-results-yet correction added to
the locked design as the very first act of the run. As a bonus, the checker measured the
real cost of the experiment: far cheaper than estimated — the expensive part is minutes,
not hours.

**Nothing is proposed for you to test.** Your one action is merging the pull request
(#69) that locks the run plan in; you also chose which engine runs it (a fresh session
on Opus). The next real entry here comes when the experiment actually runs.

Detail, if you want it: `docs/superpowers/2026-08-03-cap-reeval-exec-plan-execution-log.md`.

---

## N/A — 2026-08-03 (later) — the map-rebuild experiment is designed, reviewed and locked; nothing you can press changed
<!-- "(latest)" stripped 2026-08-03 (night): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate, except its
     "next session writes the step-by-step plan" — that has now happened; see above. -->


**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from this morning.**

**What happened, in plain terms — and you steered it three times.** The big experiment
that re-questions how the map gets built is now fully designed and locked in writing
before anything runs: what gets measured (does pressing "I know them" actually dig
toward less famous artists), on both data sets, with every pass/fail line fixed in
advance. You ordered two independent reviews of that design and they earned their keep —
between them they caught a build rule specified in an order known to break, two knob
settings strong enough to wreck journey coherence, and several pass/fail lines that
sat inside measurement noise; all fixed before anything ran. You then asked whether tag
votes were being used — they weren't, in the form you meant, and the quick measurement
you ordered showed your version is a real knob that doesn't just repeat what the
similarity data knows. It failed one written-in-advance check, in a direction you
judged acceptable, and on your ruling it is now part of the design with an honesty
check attached: before any conclusion credits the votes, the same experiment runs with
each artist's votes shuffled among its own tags, and the real version has to beat the
shuffled one.

**Nothing is proposed for you to test.** Your one action is merging the pull request
(#68) that locks all of this in; the next session writes the step-by-step plan and the
experiment itself follows. The next real entry here comes when a map is actually
rebuilt.

Detail, if you want it: `docs/superpowers/2026-08-03-cap-reeval-prereg-execution-log.md`.

---

## N/A — 2026-08-03 — the ghost-contributor cleanup you adopted is built in; nothing changes until a rebuild
<!-- "(latest)" stripped 2026-08-03 (later): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from yesterday.**

**What happened, in plain terms — and you steered it twice.** You had spotted a second
kind of ghost artist: people who are on the map only because they're *credited on other
artists' records* — session players, one-song features — who mostly can't play you the
right person's music. Today that got its own cleanup rule, built the same way as the one
you adopted earlier: an artist in that class is kept only if a music service has a real
page for them and something actually plays. Your two spot-check discoveries shaped it —
the artist with a real Spotify page that MusicBrainz never recorded is written into the
rule as a known, accepted imperfection rather than papered over, and your catch about
"credited on a collaboration album" turned out to describe **half** of the artists the
first version would have waved past, so the rule was amended to check them too. About
2,200 artists come off the next map build; you chose to adopt without a manual review
of the borderline cases, and that choice is recorded.

**Nothing is proposed for you to test.** Nothing changes in the app until a map is
rebuilt — which is now the next piece of work (the map-rebuild experiment this cleanup
was ordered ahead of). Merging the pull request is the switch; you said you'd do that
after this write-up.

Detail, if you want it: `docs/superpowers/2026-08-03-featured-credit-filter-execution-log.md`.

---

## N/A — 2026-08-02 (night) — we changed how we measure "obscure", with your rulings and your hand checks; the app is untouched
<!-- "(latest)" stripped 2026-08-03: only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running.** All four ports were checked and are
empty; no server was started and none was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A
journey you build now is identical to one from this afternoon.**

**What happened, in plain terms — and you were part of every step of it.** The yardstick
we use behind the scenes to judge how obscure an artist is turned out to order artists
poorly — your own Spotify spot-checks are what proved it, twice, against two different
data sources. You then redefined what "obscure" should mean for this app: not "unknown to
the world" but **"probably new to the people who actually use this app."** Under that
definition, the listening-based yardstick was re-tested against your known/unknown marks
and passed cleanly — every artist it called obscure was genuinely new to you — and it is
now the adopted measure for future experiments. Two side-discoveries worth keeping: the
map's most-connected artists were mostly new to you too (the app has far more room to
delight than we assumed), and you found a class of "ghost" contributors that slip past
the artist cleanup rule — written down with a cheap way to detect them, parked for your
go-ahead.

**Nothing is proposed for you to test.** The next real entry comes when something about
the app itself changes — realistically, when the map-rebuild experiment this unblocked
produces one.

Detail, if you want it: `docs/superpowers/2026-08-02-fame-instrument-execution-log.md`.

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

## N/A — 2026-08-01 (evening) — you decided to clean about one artist in ten off the map; nothing changes until a rebuild
<!-- No "(latest)": that marker stays on the live QUEUED redesign entry further down, which
     is still owed. This is N/A — there is nothing here to run. -->


**Nothing to exercise, and nothing is running.** All four ports were checked and are empty;
no server was started and none was left behind. No routing, no graph, no weighting, no cost
function, and not one line of the app or the website changed. **A journey you build now is
identical to one from this morning.**

**What happened, in plain terms.** Two things finished today.

- **The genre investigation is written up and closed.** It ran for three days across several
  sessions and the answer is that neither way of using genre labels is worth adopting. That
  is now a proper document rather than scattered notes, so nobody re-opens it by accident.
- **You made a decision about the "ghost" artists** — the ones that show up in the map with
  no records to their name. About **7,035 of them, roughly one artist in ten, will be
  removed the next time the map is rebuilt.** The rule you settled on keeps an artist with
  no records only if a music service has a real page for them *and* something actually
  plays. Your twenty hand reviews are what decided it.

**Nothing about this is live yet, and that is deliberate.** The list of artists to remove is
written down and frozen, but the map has not been rebuilt, so **you would not see any
difference today**. Removing them also nudges everything else slightly — it is a genuinely
new map rather than the old one with rows deleted — which is why it waits for a proper
rebuild rather than being slipped in.

**One thing we found by accident, and it is about the app you use today.** When a card plays
a clip, the app finds the music by searching the artist's *name*. We were able to check that
against the exact artist in about a hundred and sixty cases, and **roughly one in eleven
played a different artist who happens to share the name.** You had already spotted this
happening once; it is now measured rather than suspected. It is a real fault in what you
hear today, it has nothing to do with the decision above, and there is a more reliable way
to look those clips up if you want it prioritised.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

Detail, if you want it: `docs/superpowers/2026-08-01-label-weighting-execution-log.md` §8.

---

## N/A — 2026-08-01 (later) — we tested whether counting labels unequally helps; the answer closes some doors and opens one

**Nothing to exercise, and nothing is running.** All four ports were checked and are empty;
no server was started and none was left behind. No routing, no graph, no weighting, no cost
function, and not one line of the app or the website changed. **A journey you build now is
identical to one from this morning.**

**What happened, in plain terms.** We asked whether genre labels work better when a shared
rare label ("chillwave") counts for more than a shared common one ("rock"), and when a label
lots of people vouched for counts for more than a drive-by one. Four answers came back, and
you were part of two of them:

- **Counting labels unequally genuinely changes which artists would get connected** — far
  past the bar you set for "matters". So the knob is real. Whether the changed map *sounds*
  better is a question only your ears can answer, and nothing was adopted.
- **The fine style labels are now a closed door, and we finally know why.** We tried five
  different ways of filtering or weighting them — including keeping only the ones you
  picked out as real sub-genres, and fixing the spelling mismatches between the two
  databases. Every version failed the same way, and the reason turned out to be simple:
  **the style labels a person would actually use are the ones the app's similarity data
  already knows.** They add nothing new.
- **Counting individual pressings of albums turned out to smuggle fame in** — famous albums
  get pressed more — so that idea was excluded by a rule we wrote down before seeing any
  number.
- **Your twenty-artist review is now part of the permanent record**, and it is the sharpest
  evidence yet that most of the map's "unknown artists with no releases" are not artists at
  all but leftover credits — session players, one-track features. The two real ones you
  found would be wrongly deleted by any simple cleanup rule, which is exactly why that
  decision is parked for you rather than made.

**What it does not mean.** Nothing has been decided, built or adopted; no listening time
was spent. The one concrete thing waiting on you is a direction call, not a test: whether
the next piece of work is the big map-building re-question, which now has everything it
needs to start.

Detail, if you want it: `docs/superpowers/2026-08-01-label-weighting-execution-log.md`.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

---

## N/A — 2026-08-01 — we finished testing the genre idea, and it did not work

**Nothing to exercise, and nothing is running.** All four ports were checked and are empty; no
server was started and none was left behind. No routing, no graph, no weighting, no cost
function, and not one line of the app or the website changed. **A journey you build now is
identical to one from yesterday.**

**What happened, in plain terms.** We had two ways genres might improve the journeys: change
which artists get connected when the map is built, or leave the map alone and let genre nudge
each step as a journey is put together. We had already found the first one makes the app worse
at reaching obscure artists, which rules it out. This session tested the second.

- **Turning genre on changed almost every journey** — around nine in ten. That looked like a
  strong result.
- **Then we scrambled the genres at random and ran it again. Almost exactly the same journeys
  changed.** So the change was never about genre. It is what happens when you add *any* new
  cost to every step of a long journey — and journeys here run to about a dozen steps for
  obscure artists, where changing one artist anywhere makes the whole thing count as different.
- **We checked the measuring equipment first, both ways**, and it is sound: our copy of the
  route-builder returns exactly what the real app returns when the genre setting is off, and
  when we turn genre up until nothing else matters, journeys go precisely where genre alone
  says they should. So this is a real "no", not a broken instrument.

**One thing we found by accident that is worth telling you.** On the 120 journeys we tested,
the app currently delivers **no artist at all from the least-famous tenth** in the middle of a
journey. Not "few" — none. That is the thing you have called a defect rather than a limitation,
and this is the sharpest measurement of it we have. It also means the safety check we had
written for this experiment could not do anything, since you cannot measure a fall from zero.

**What it does not mean.** Nothing has been decided, built or adopted, and none of this says
your journeys would sound better or worse. That still needs your ears — no offline measurement
can say it, and this session did not spend any of your listening time.

Detail, if you want it: `docs/superpowers/2026-07-30-tag-discrimination-execution-log.md` §16.

---

## N/A — 2026-07-31 — we tested whether genre labels could shape the map, and found a catch

**Nothing to exercise, and nothing is running.** All four ports were checked and are empty; no
server was started and none was left behind. No routing, no graph, no weighting, no cost
function, and not one line of the app or the website changed. **A journey you build now is
identical to one from yesterday.**

**What happened, in plain terms.** We were asking whether genre labels could help decide which
artists get connected to which, when the map is built. Three things came out of it.

- **The idea would change the map a lot.** At the gentlest setting we tried, about one
  connection in six across the whole map would be different. So this is not a change that
  quietly does nothing.
- **But it would make the app slightly worse at reaching obscure artists** — the thing you
  called a defect rather than a limitation. Direct connections from a well-known artist to an
  obscure one drop at every setting, and at the stronger settings they drop enough to trip the
  guard we had written in advance. **That guard blocks us from recommending this, and it does
  so regardless of anything else we found.**
- **A safety check we had designed turned out to be impossible to pass**, for a reason that
  says nothing about the idea. We had planned to scramble the genre labels and confirm the
  measurement still reacted. But scrambling labels does not give artists *random* genres in
  common — it gives them *none* in common, so nothing moves. We replaced it with a check that
  works, and that one passed.

**And separately, the other investigation you commissioned paid off.** Looking at what artists
*released*, rather than at their artist page, roughly doubles how many obscure artists we know
a genre for. We tested whether that richer information still tells artists apart well enough to
be useful, and it does — though it is measurably blunter, and adding the second source costs
more sharpness than it gains reach.

**What it does not mean.** Nothing has been decided, built or adopted, and **none of this says
the journeys would sound better or worse** — no offline measurement can say that. That still
needs your ears.

Detail, if you want it: `docs/superpowers/2026-07-30-tag-discrimination-execution-log.md`
§9–§13.

---

## N/A — 2026-07-30 (latest, late night) — we checked whether genre labels are worth building with; so far, yes

**Nothing to exercise, and nothing is running** — all four ports were checked and are empty,
and both data-gathering jobs have finished and exited. No routing, no graph, no weighting,
no cost function, and not one line of the app or the website changed. **A journey you build
now is identical to one from this morning.**

**What happened, in plain terms.** Last night we asked whether genre labels could be used to
*judge* whether a journey flows well, and the answer was no — too many artists have no
labels. You then asked the different question: could genre labels help *build* the map in the
first place, by influencing which artists get connected to which. That is a separate idea and
it survives so far.

Three things were measured, and all three came back the encouraging way:

- **Where the idea would actually act, the labels are there.** Among connections between two
  well-known artists — the ones you have said matter most — virtually every connection has
  genre labels at both ends. The labels thin out among obscure artists, as before, but there
  the idea simply does nothing rather than doing something wrong.
- **The labels genuinely tell artists apart.** Of the hundred-odd artists similar to any
  given artist, some share far more genre labels with them than others. Had they all looked
  alike, the idea would have been dead on the spot.
- **And this is the one that mattered most: the labels are not just repeating what we
  already know.** The worry was that artists who are similar automatically share genres, in
  which case genre labels add nothing at all. Measured, the overlap between the two is weak,
  and for the overwhelming majority of artists the genre ordering is genuinely different from
  the similarity ordering. There is real room for this to change something.

**What it does not mean.** Nothing has been decided, built, or adopted, and **none of this
says the journeys would sound better** — no offline number can say that, which is why this
idea ends at a listening test or nowhere. The next step measures whether it would actually
change which artists get connected, and after that, whether journeys change at all.

**One correction we made to our own rules before running anything.** The bar we had written
down for "this changes nothing worth caring about" turned out to be far too loose — it would
have let through a change affecting about one connection in twelve across the whole map, and
roughly one journey in three. You set the replacement bar. The old wording is kept in the
document, marked as wrong, rather than quietly deleted.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-30-tag-discrimination-execution-log.md`.*

---

## N/A — 2026-07-30 (night) — we asked whether genre labels could judge journey flow; the answer was no, and we stopped
<!-- "(latest)" stripped 2026-07-30 (late night): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running** — ports 8000 and 5173 were checked and are
empty, and nothing from this work survives it. No routing, no graph, no weighting, no cost
function, and not one line of the app or the website changed. **A journey you build now is
identical to one from this morning.**

**What happened, in plain terms.** You know how you judge journeys by whether each step
*sounds* like a sensible next listen — genre, era, scene. We asked whether the genre labels
that exist on the public music databases cover enough of our artists to build a measure of
that. We wrote down, in advance, the level of coverage below which the idea is dead, and
committed the exact scoring method we would have used — before looking at anything.

- **The idea died at its own bar, and that is the honest result, not a failure.** In the
  obscure half of the map — the part the app exists to explore — roughly two artists in
  three have no genre label anywhere we looked. That is the same hole our fame yardstick
  has, in the same place. Building a "does this journey hang together" measure on labels
  that vanish exactly where journeys get interesting would repeat the mistake we just
  finished measuring, so we stopped at the pre-agreed stopping point.
- **Your mid-run question closed a door properly:** counting *every* label anyone ever
  applied, not just proper genre labels, moves the number barely at all. The dark artists
  have no labels of any kind. So this is not a labelling-choice problem we could tune away.
- **One genuinely useful thing against the grain:** the specific obscure artists a journey
  would actually pass through are labelled about twice as well as the obscure population at
  large. Not enough to un-fire the stopping rule, but it is the first thing any future
  attempt should look at.
- **And your other suggestion paid off:** the fast bulk source you pointed at returns the
  same labels as the slow official one, 99.9% identically, about thirty times faster. If
  labels are ever worth collecting for the whole map, it is under an hour of work now, not
  a day.

**Your listening verdicts from July were never touched.** The scoring method that would
have been tested against them is committed and unused, so that small, irreplaceable set of
judgments is still available, unburned, for any future attempt.

**Nothing is proposed for you to test.** The next real entry here comes when something
about the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-30-coherence-tag-probe-execution-log.md`.*

---

## N/A — 2026-07-30 — we measured how well our "how famous is this artist" yardstick works; the app is untouched
<!-- "(latest)" stripped 2026-07-30 (night): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running** — ports 8000 and 5173 were checked and are
empty, and no Python process from this work survives. No routing, no graph, no weighting,
no cost function, and not one line of the app or the website changed. **A journey you build
now is identical to one from yesterday.**

What happened is measurement only, on the yardstick we use *behind the scenes* to judge how
obscure an artist is when we score experiments. It never touched what you see.

**One thing worth knowing, in case it changes what you'd want tested later:** the yardstick
copes fine with the artists the app currently shows you, and goes blind on more than a third
of the artists it *would* show you if we succeeded at making journeys more obscure. So if a
future change does make journeys reach further into unknown artists, the way we measure that
change may need fixing first. That is a decision waiting for you, not a bug in the app.

**Still owed and unchanged:** the queued entry further down (the redesign, against
`https://musicapp.cmiller.io`), including the phone half. Nothing here displaces it.

**Detail, for anyone who wants it:**
`docs/superpowers/2026-07-30-fame-proxy-coverage-execution-log.md`.

---

## N/A — 2026-07-30 (later) — the experiment ran and is read; the app is untouched

**Nothing to exercise, and nothing is running** — ports 8000, 5173, 8138 and 8139 were
checked and are empty. No routing, no graph, no weighting, no cost function, and not one
line of the app or the website changed. **A journey you build now is identical to one from
yesterday.** Everything below is measurement; nothing was adopted.

**What happened, in plain terms.** The experiment designed yesterday ran end to end today,
under the rules committed before any result existed. Three ways of choosing connections
competed on equal terms, on both the current data and the candidate data:

- **Today's rule lost its first real competition — on map coverage.** A rule that pools
  both artists' suggestion lists and then trims back to the *same* 50-connection budget
  loses **one artist** from the map where today's rule loses **800**, and the
  most-connected artists end up *less* dominant, not more. Whether it *sounds* as good is
  the one thing no offline number can say — a listening test still stands between any of
  this and the app.
- **The candidate data's alarming numbers were mostly our own cut-off, not the data.**
  "R.E.M. drops to 6 connections, 6,499 artists cut off" was measured with our
  must-be-mutual rule at 50. Widen the window, or drop the must-be-mutual requirement,
  and the candidate data keeps nearly everyone.
- **On today's data, journeys between two famous artists cannot be made to pass through
  anyone obscure by any connection rule.** We built maps where every famous artist is
  force-connected to its ten strongest obscure partners, checked those connections exist —
  and the journey-builder routed around every one of them. The way it prices fame jumps
  is the blocker, and that is router work, deliberately out of this experiment's scope.
  On the candidate data, those journeys *do* occasionally dig up someone obscure, even
  under today's rule.
- **One feared cost measured small:** the candidate data's surviving connections lean
  famous by about a third of the bar we set for "matters".

**None of this decides anything.** Which rule any rebuild uses, and whether the candidate
data is adopted at all, are your parked decisions — now with numbers where there were
guesses, and a listening test owed before anything ships either way.

**Nothing is proposed for you to test.** The next real entry here comes when something
about the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-30-track-b-runs-execution-log.md`; the report is
`docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md`.*

## N/A — 2026-07-30 — we designed the experiment that picks the connection rule; the app is untouched
<!-- "(latest)" stripped 2026-07-30 (later): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running** — all four ports were checked and are
empty. No routing, no graph, no weighting, no cost function, and not one line of the app
or the website changed. **A journey you build now is identical to one from yesterday.**

**What happened, in plain terms.** You asked us to re-question the early decision about how
artists get connected on the map — the rule that requires two artists to each rank the
other highly before they get linked, and the cut-off of fifty. Today built the experiment
that puts that question to numbers:

- **We found out what the data supplier's settings actually mean**, from their own code
  rather than a forum post. Two things the forum post said turned out to be wrong, and the
  one setting that separates the candidate map from today's map finally has a definition:
  it limits how much any single listener can contribute to a pair of artists being called
  similar. Lowering it — which is what the candidate map does — means a pair needs **four**
  distinct people to have listened to both, where today three devoted fans are enough.
  That is very plausibly *why* the candidate map cuts off so many obscure artists, though
  that part is reasoned rather than measured.
- **Three ways of choosing connections will now compete on equal terms** — today's rule at
  several cut-offs, and two challengers, one of which can do something today's rule
  provably cannot: keep a few connections from very famous artists down to obscure ones.
  A fourth, no-limit-at-all version runs alongside for reference only.
- **Every measurement rule was written down and committed before any result exists**, so
  no number can quietly reshape what counts as winning. An outside review of the design
  caught two real gaps before anything ran; both are fixed and on the record.

**None of this decides anything.** The experiment itself is the next session's work, its
result is a recommendation, and whether anything ships is your call — after a listening
test, as always.

**Nothing is proposed for you to test.** The next real entry here comes when something
about the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-30-track-b-design-execution-log.md`.*

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

## N/A — 2026-07-29 (earlier) — we measured the price of the new setting; the app is untouched
<!-- "(latest)" stripped 2026-07-29 (night): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->

**Nothing to exercise, and nothing is running** — all four ports were checked and are empty;
nothing was started on this machine and nothing was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A journey
you build now is identical to one from this afternoon.**

**What happened, in plain terms — and it is a mixed answer rather than a good or bad one.**

This afternoon's entry said the setting we currently use is *why* journeys between two famous
artists never dig up anyone obscure, and that switching would mean rebuilding the whole map. It
also flagged one worry: the promising setting seemed to offer *fewer* suggestions for artists
who are already obscure. **That worry was the thing to check before spending four and a quarter
hours, and it checks out badly.**

- **Under the new setting, nearly half of obscure artists would end up with too few
  connections to appear in the middle of a journey at all** — up from about one in seven today.
  Ten of the forty obscure artists we tested came back with **no suggestions whatsoever**.
- **The reason is supply, not rejection.** The new setting simply offers an obscure artist
  fewer artists to connect to — roughly half as many. The connections it does offer actually
  hold up *better* than today's. So this is not something that could be tuned away.
- **And as things stand it would not even build.** The map has a safety check that refuses to
  publish if certain well-known artists go missing. Under the new setting **R.E.M. connects to
  nobody at all**, along with Pixies, The xx and PJ Harvey — so the check would stop it. That
  is a fixable engineering problem, not a dead end, but it is real work that nobody had costed.

**One thing worth knowing about how this was done, because it went wrong in our favour.** The
first tool built for this job could not answer the question — it could only reach famous
artists, when the question was about obscure ones. That was caught by testing the tool before
trusting it, which cost about twenty minutes and saved an hour of fetching plus a wrong answer.
The replacement was cheaper anyway.

**Also honest about a mistake in our own measurement:** the first version of the scoring quietly
skipped the very artists that were worst affected, which made the problem look about half as bad
as it is. Both numbers are recorded side by side rather than just the corrected one.

**None of this decides anything.** Whether to rebuild the map is your call and it is still
parked. What has changed is that its price is now measured instead of guessed.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-29-reciprocity-execution-log.md`.*

## N/A — 2026-07-29 (later) — we found out why famous journeys stay famous; the app is untouched
<!-- "(latest)" stripped 2026-07-29 (latest): only the newest entry carries it, per the
     convention below. This entry's content is unchanged and still accurate. -->


**Nothing to exercise, and nothing is running** — all four ports were checked and are empty;
nothing was started on this machine and nothing was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A journey
you build now is identical to one from this morning.**

**What happened, in plain terms — and it is genuinely good news after this morning's dead end.**

Earlier today the answer was that journeys between two famous artists can never pass through
anyone obscure, and that no amount of tuning could fix it. That is still true of tuning. But
**you** noticed that the address we use to fetch "artists similar to X" has a settings string
in it, and that only a handful of settings are allowed. That turned out to be the whole thing.

We checked all six permitted settings against 200 artists. **One of them differs from ours by
a single value, and it changes the picture completely:** where our current setting offers
Radiohead essentially nobody outside the most popular tenth of artists, that one offers about
eleven — and some of them are genuinely obscure, not merely less famous. **So the reason
famous journeys stay famous is a setting we picked, not a fact about the data.**

**Two honest caveats, because this is not a free win.**

- **It also seems to offer *fewer* suggestions for artists who are already obscure** — about
  40% as many. That probably means more artists ending up with almost no connections, which is
  the same underlying cause as journeys that have nobody in the middle. We have not measured
  that properly yet, and the next piece of work does.
- **Switching would mean rebuilding the map from scratch**, about four and a quarter hours,
  and it would be a genuinely *different* map rather than a patched one — less than half of
  each famous artist's connections would be the same. Every measurement we have about journey
  quality was taken on the current map. **That is your decision and nothing has been done
  toward it.**

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-29-algorithm-selection-execution-log.md`.*

## N/A — 2026-07-29 — you rewrote what "good" means, and another measurement track ran; the app is untouched

**Nothing to exercise, and nothing is running** — all four ports were checked and are
empty; nothing was started on this machine and nothing was left behind. No routing, no
graph, no weighting, no cost function, and not one line of the app or the website changed.
**A journey you build now is identical to one from yesterday.**

**What happened, in plain terms.** You rewrote the product requirements and they now govern
— including your call that journeys between two famous artists never digging up anyone
obscure is a **defect to fix**, not a limitation to live with. Then the follow-up experiment
you approved ran end to end in a day. Its answer: **even when adding an obscure artist to a
journey costs nothing and every famous artist carries a price, the app still prefers to make
the journey shorter rather than swap famous artists for obscure ones.** That closes the book
on fixing this by tuning the router. The fix now runs through rebuilding the artist map
itself, which is what the next session will plan.

**You also parked two decisions on purpose**, so nobody should relitigate them without you:
whether any of the shorter-but-obscurer journey settings ever ships, and any listening test
on them.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-29-track3b-execution-log.md`.*

## N/A — 2026-07-28 (night, later) — a measurement track ran; nothing you can press changed

**Nothing to exercise, and nothing is running.** All four ports were checked and are empty;
nothing was started on this machine and nothing was left behind. No routing, no graph, no
weighting, no cost function, and not one line of the app or the website changed. **A journey
you build now is identical to one from this afternoon.**

**What happened.** The plan of attack written earlier today was carried out end to end. It
was all measurement — the app was never touched, and nothing has been adopted.

**Two things worth thirty seconds, because they change what is worth trying next.**

- **For journeys between two very famous artists, obscure middles are impossible.** Not
  expensive — absent. Radiohead connects to fifty artists and every one of them is in the
  most popular tenth; the same is true of The Beatles, Metallica, Muse, Coldplay and the
  rest. Every setting tried, including one far stronger than anything anyone would ship,
  delivered **zero** lesser-known artists on those journeys. That half of what you asked for
  cannot be fixed by any setting, only by changing how the map is built.
- **For journeys where at least one end is less famous, a setting was found that works** —
  it roughly doubles the number of genuinely obscure artists you get. **But it also makes
  the journey shorter, about thirteen middle artists down to about seven**, and that is a
  trade only you can judge. It is written up for you and nothing has been decided.

**Nothing is proposed for you to test.** The next real entry here comes when something about
the app itself changes.

**⚠ The redesign entry below is still the live one to run** — the app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing here
supersedes a word of it, and **none of it has been discharged.**

*Detail: `docs/superpowers/2026-07-28-track3-depth-descent-execution-log.md`.*

## N/A — 2026-07-28 (late) — path work resumed; measurements and a plan only; the app is untouched

**Nothing to exercise, and nothing is running** — all ports were checked and are empty.
No routing, no graph, no weighting, no cost function, and not one line of the app or the
website changed. **A journey you build now is identical to one from this afternoon.**

**What happened.** You restarted the path-quality work and set the goal: more obscure
artists in the middle of journeys, fewer very famous ones, especially as you press the
bypass buttons. Today measured where that problem actually lives and wrote the plan of
attack, and both are committed. Two things the measurement settled, in plain terms: on a
journey between two famous artists, the *first* path's famous middles are forced by the
map itself — no setting can change them, and by your own stated preference they are
correct anyway; and **the bypass buttons never actually dig** — after twenty presses the
middle artists are as famous as at the start. That second one is the thing the coming
work tries to fix, with a new rule that makes each press push the journey a little
further off the beaten track. Nothing of that is built yet; nothing you can press has
changed.

**You also decided today:** the handful of artists with missing names get dropped from
any future rebuild rather than repaired. Nothing visible changes until a rebuild happens.

**⚠ The entry below this one is still the live one to run** — the redesigned app on
`https://musicapp.cmiller.io`, including the phone half and the iPhone script. Nothing
here supersedes a word of it.

*Detail: `docs/superpowers/2026-07-28-asc5-path-ascent-execution-log.md`.*

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

## N/A — 2026-07-28 (evening) — the app is being restyled; half of it is done and none of it is live
<!-- "(latest)" stripped 2026-07-28 (night): the redesign is now finished and has its own
     QUEUED entry above, which is the live one. Per the convention below, only that carries
     "(latest)". This entry's "nothing to press yet" is now out of date — the other half landed. -->

**Nothing to exercise, and nothing is running.** No routing, no graph, no weighting, no cost
function — **a journey you build today is the same journey as this morning's.** Nothing was
started on this machine and nothing was left behind; all four ports were checked and are empty.
**The website is completely untouched** — none of this has been published, so the address you
have behaves exactly as it did.

**What this is.** You sent me a design mockup of the app and asked for it to be built. It is
about half built, on a branch, and deliberately stopped halfway at a planned resting point.

**Why there is nothing to press yet.** The half that is done is the front screen and the look of
each artist card. The half that is not done is the new *loading* screen — the one that shows your
two artists with shimmering placeholders between them while it thinks. Until that is wired in,
the app still shows the old plain "Building your path…" line, so **you would be looking at a
half-dressed app and wondering which bits were deliberate.** Better to look once, when it is
whole.

**The one thing worth knowing now, because it is a change in behaviour rather than looks.** When
you press one of the two bypass buttons, the app currently just dims the path while it rebuilds.
It will soon also tell you *what it is doing*, and differently for each button — "Steering around
that sound" for **✕ Not for me**, "Digging for someone newer" for **✓ I know them**. That is the
first time the app will have admitted that the two buttons do different things. There will also
be a short note above each path explaining that either button **rebuilds the whole journey**, not
just the card you pressed — which has always been true and has never been said anywhere.

**The next entry here will be the real one**, when the other half lands: the front screen, the
loading screen, a shared link, and the new explanation, on desktop and on a phone.

**⚠ One thing is still owed from the previous entry and this work does not touch it: the iPhone
script.** Whether a clip plays at all on an iPhone is still genuinely unknown — nobody has ever
opened this app on one — and no test, emulator or Android device can answer it. It is unchanged
and still waiting, immediately below.

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

## N/A — 2026-07-28 — work towards dropping the password; nothing is live yet

**Nothing to exercise, and nothing is running.** No routing, no graph, no weighting, no clips, no
buttons — **not one line of what you'd call the app changed.** A journey you build now is the same
journey as yesterday's, and **the website is exactly as it was, password and all.** Nothing was
started on this machine and nothing was left behind; all four ports were checked and are empty.

**What this was.** The password on the site is quietly doing three jobs, not one. It keeps
strangers out, but it also stops anyone hammering the server, and it stops the app asking the
music service for clips faster than that service will tolerate. **You can't take it off until
something else is doing the second and third jobs**, which is what this work is.

Today did the half that lives inside the app itself:

- **The app can no longer be made to do unlimited work by a single request.** Someone could
  previously send a list of two million artists and the server would read all of it before
  noticing it only wanted two.
- **The check that tells AWS "the app is alive" can no longer be drowned out by traffic.** This
  is the one worth knowing about. Under load that check was waiting in the same queue as
  everyone's journeys and taking 22 seconds against a 5-second deadline — so AWS would conclude
  the app was dead and restart it, moving all the traffic to the second copy, which would then
  fail the same way. **The site wasn't getting slow under heavy use, it was restarting itself in
  a loop.** It now answers immediately. This doesn't make anything faster; it stops busy turning
  into broken.
- **When the music service tells us to back off, the app now hears it.** Before, "you're asking
  too often" and "we don't have that track" looked identical, so being told to slow down made the
  app ask *three times instead of once* — which is how you turn a brief telling-off into a long
  one. It now asks once, and after five refusals it leaves that service alone for a minute and
  uses the other one.

**The one thing you might notice, whenever this does go live:** a card that would have played
something may occasionally stay silent for up to a minute while the app waits out a telling-off.
That's deliberate, and it's the alternative to every card going silent for much longer.

**Nothing is proposed for you to test.** The next entry here will be a real one, and it will be
the big one: **the address with no password on it**, plus a short list for a friend with an
iPhone — because whether clips play at all on an iPhone is still genuinely unknown, and no test,
emulator, or Android phone can answer it.

**One thing is waiting on you before any of that:** a certificate for `musicapp.cmiller.io`. The
commands are in the plan.

*Detail: `docs/superpowers/2026-07-28-password-removal-execution-log.md`. PR #39.*

## N/A — 2026-07-27 (evening, later) — a Gate 3 readiness review ran; the app is untouched

**Nothing to exercise, and nothing is running.** No routing, no graph, no weighting, no clips, no
buttons — **not one line of application code changed.** A journey you build now is the same journey
as this morning's, and the website is untouched. Both ports were checked and are free; nothing was
started.

**What happened.** Four reviewers went over the whole system to answer one question: *what breaks
when the app goes from a handful of people behind a password to anyone on the internet?* They found
real things, but **all of them are decisions and future work, not something to press today.** The
headline: quite a lot is currently kept safe only by the password, and opening the app to the public
is the act of removing it. None of that changes the app you use now.

**Three of the findings are yours to decide, and they are written up for you** (in the review record
below), not queued here because there is nothing to *do* in the app:

- Whether to put a proper web address in front of the site before sharing it widely — cheap now,
  impossible to retrofit for links already sent.
- What the app should record about the strangers who use it, and whether it should say so.
- **Whether to borrow an iPhone for ten minutes.** There is a short, ordered script that would settle
  the one thing no test and no Android phone can: whether music plays at all on an iPhone. The first
  tap answers it.

**Nothing is proposed for you to test.** The next real entry here comes when something about the app
itself changes.

*Detail: `docs/superpowers/findings/2026-07-27-gate2-gate3-team-review.md` (§6 is the decisions
and the borrowed-iPhone script; §7 the live load test). PRs #37, #38.*

## N/A — 2026-07-27 (evening) — the project files moved house; the app did not change
<!-- No "(latest)": per the convention below, only a live QUEUED entry carries it. This is N/A. -->


**Nothing to exercise.** No routing, no graph, no weighting, no clips, no buttons — **not one
line of application code changed.** A journey you build now is the same journey as this morning,
and the website is untouched. This was housekeeping on your machine.

**What happened.** The project now lives at `C:\dev\music-app` instead of inside OneDrive. The
old copy is still there, untouched, as a safety net. Both copies were compared file by file —
all 75,052 of them — and every one matches. The collection of artist data that took four and a
quarter hours to gather, and **cannot be gathered again**, arrived intact.

**⚠ Two things ARE running on this machine, and unusually, they are not mine.** Two copies of
the app's engine have been running quietly since 20 July, on ports **8138** and **8139**. They
are harmless today and nothing uses them. **They matter because they are holding the old copy of
the project open**, and the last step of this job deletes it — which would then half-fail. I
tried to stop them and was blocked from doing so, so it needs you:

```
Stop-Process -Id 71076,59236,60412,97220 -Force
```

**Do not stop anything else.** There is a third thing listening, on port 53342, and it belongs
to your Home Assistant project rather than this one.

**Two things worth thirty seconds of your attention.**

- **Checking the backup found a real problem that had nothing to do with this project.** Several
  files were not being backed up at all. You forced a rescan and it is now uploading over 6 GB
  that had never been included. That was luck in our favour: the last step of this job deletes
  the only other copy of the irreplaceable data, and it would have been deleted into a backup
  that was quietly incomplete.
- **Nothing gets deleted until that backup finishes.** That is deliberate, and it is the gate.

**Nothing is proposed for you to test.** The next real entry here comes when something changes
about the app itself.

*Detail: `docs/superpowers/2026-07-27-onedrive-migration-execution-log.md`.*

## N/A — 2026-07-27 (later) — nothing to press, and one thing I told you that was wrong

**Nothing to exercise, and nothing is running.** No routing, no graph, no weighting, no clips,
no buttons — **not one line of application code changed today**. A journey you build now is the
same journey as this morning's. Nothing was started on this machine and nothing was left
behind; both ports were checked and were already empty.

**The correction, and it is the reason this entry exists.** The last entry told you some
artists' descriptions were mangled, and that The Beatles read `â€œThe Fab Fourâ€` in the
search dropdown. **You said you had never seen that, in the live app or on your machine, and
you were right.** I read the artist map itself and it holds the correct text with correct
quotation marks. The mangling was in the tool *I* used to look at it, not in anything you
have ever been shown. I have struck it from the record.

**Why it is worth thirty seconds of your attention rather than none:** it was quietly becoming
one of the reasons to rebuild the artist map, which is a decision of yours. It is no longer a
reason for anything. **This is the second time this exact mistake has been made here**, so it
is now written into the notes that carry across sessions.

**Your phone run is recorded as passing on every one of the six things it asked for** — the
strongest kind of result this file keeps. Two of them had never been seen working by a person
before, only proved by machine: signing in, and **a link you shared opening correctly for
someone who had never logged in**. That last one is the whole point of putting it on the
internet, and it now works.

**Still not covered, and no Android device can cover it:** anything specific to an iPhone —
how Safari draws the page, the bar at the very bottom, and whether the keyboard alters artist
names as you type them. Whether that matters depends entirely on who you send the link to.

**One thing I found and deliberately did not fix**, so it does not surprise anyone later: the
space the app reserves at the bottom of the screen for a phone's system bar is switched off by
a setting elsewhere, so it has never actually done anything. **It causes no problem today** —
the bar clears fine on its own, which is why your phone run passed — and it would only start
mattering if someone changed that other setting believing the reservation had them covered.

**The other thing today produced is a plan to move the project off OneDrive**, which is
housekeeping on this machine and touches nothing you use.

*Detail: `docs/superpowers/plans/2026-07-27-onedrive-migration.md` and
`docs/superpowers/2026-07-27-HANDOFF-onedrive-migration.md`.*

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

## N/A — 2026-07-27 — three fixes for the first person you send the link to

**Nothing to exercise, and nothing changed about the app on this machine.** No routing, no
graph, no weighting, no clips, no buttons. A journey you build today is the same journey as
yesterday's. Nothing is running on any port — nothing was started and nothing was left behind.

**All three fixes are for the moment you actually send someone the address**, which has not
happened yet. That is why there is nothing to press.

**What was wrong, in plain terms.**

1. **The password box asks for a name as well as a password, and nothing told anyone what the
   name was.** You were only ever going to send the password. Their first go would have been a
   guess. The refusal page now says the name to type. **When you do share the link, send the
   address and the password only** — the page tells them the rest.
2. **Anyone who had visited before would have got a blank white page after any update.** The
   old publishing step deleted the files their browser was still holding on to. Publishing is
   now three steps in a set order that closes that gap. This one you would never have seen
   yourself: it only bites people who visited *before* a change.
3. **If the app fails to arrive for any other reason, it now says so.** Before, every kind of
   failure looked identical — a white screen with nothing on it, which nobody can describe to
   you over a message. It now reads "the app did not load, reload the page". **If you ever see
   that text, that is the message working, not a new fault.**

**One thing was deliberately left unfinished, and it is the honest weak point.** Nothing has
ever checked that the password box actually lets someone *in* — every check so far only proved
it keeps people *out*. The check is now written down but cannot run until the app is actually on
the site. It is the first thing that happens at the next step.

**Still true from the last entry, unchanged:** the thing on the internet is still telling
browsers that a page on your own machine may read from it. It is fixed in the code and reaches
the live site the next time the app is published. You decided today to wait for that rather than
publish twice, which is recorded.

**The phone section further down this file is still waiting.** Its trigger is the app actually
being live, which has not happened yet. Do not run it today — there is still no address a phone
can open.

*Detail: `docs/superpowers/2026-07-27-dep33-remediation-execution-log.md`, "Stage 3".*

## N/A — 2026-07-27 — safety work under the bonnet; nothing to press, and one thing to know

**Nothing to exercise, and nothing changed about the app you use on this machine.** No
routing, no graph, no weighting, no clips, no buttons. A journey you build today is the same
journey as yesterday's. Nothing is running on any port — nothing was started.

**What this was.** Four reviewers went over the new setup last week and found ten things that
mattered. This session fixed most of them. Almost all of it is invisible: tests that were
passing without actually checking anything, and guard rails around the deploy.

**The one worth knowing about, because it is still true right now.** The thing on the
internet is currently telling web browsers that a page running on *your own machine* is
allowed to read from it. It was supposed to have been switched off, and the switch was
written correctly — but the way it was switched off amounts to setting it to *nothing*, and a
setting of nothing simply never arrives. So it has been on since the day it went up.

**How much does that actually matter? Not very much, and I would rather say so than dress it
up.** Almost everything on there refuses to answer anyone who does not come through the front
door. The one thing left readable is a status page that says which version of the artist map
is loaded. Nobody can reach your journeys, your clips, or anything else with it.

**It is fixed, but not yet fixed *out there*.** The correction is written down and tested; it
reaches the live site the next time the app is published, which is the next piece of work
anyway. I checked again after making the fix rather than assuming, and confirmed the live
version still has the old behaviour.

**Two changes you will meet the next time the app is published**, both deliberate:

- **Publishing now refuses to run unless it is told exactly which version it is publishing.**
  It used to quietly fall back to "whatever is newest", which would have silently swapped what
  is running. That was one command away from happening.
- **The command that sets up a brand-new site now refuses** unless you confirm the site really
  is brand new. Run by mistake against the live one, it would have deleted the address itself —
  and an address, once deleted, never comes back. Every link anyone had been sent would have
  died. That was previously prevented only by a sentence in a document.

**Nothing is proposed for you to test.** The next real entry here comes when the app itself is
up and there is something to press — which is the next track.

*Detail: `docs/superpowers/2026-07-27-dep33-remediation-execution-log.md`.*

## N/A — 2026-07-26 — the app is on the internet, but there is nothing to press yet

**Nothing to exercise, and please do not go looking.** The app now has a home on the web
instead of only living on this machine. But **only the engine went up, not the app itself** —
open the address today and you get a password box and then an error page. That is expected
and is the next piece of work, not a fault.

**Nothing about the app on your own machine changed.** No routing, no graph, no weighting.
A journey you build here is the same journey as this morning.

**The address and password are not written down here on purpose.** They are in the deploy
record. **Please don't send either to anyone yet** — two things still need doing first, and
one of them is that *nobody can currently guess the username*, which would just waste their
time. Both are queued as the next session's first work.

**What did get checked, mechanically, so you don't have to:** the thing on the internet is
running exactly the same artist map as your machine — matched on three separate counts. The
password box refuses to let anyone past. And the engine refuses to answer anyone who tries
to reach it directly instead of through the front door.

**What is worth knowing, because it explains the next entry.** Four reviewers went over the
new setup. They found forty-five things, ten of which matter. The most interesting one:
somebody could have accidentally left the whole site open to the public and **not one test
would have failed** — it would have kept working perfectly for you the entire time. That
class of problem is why the next session fixes tests before shipping anything else.

**The next entry here will be a real one** — when the app itself is up, you will get an
address, a password, and a list of things to try on it, including on your phone for the
first time.

*Detail: `docs/superpowers/2026-07-26-gate2-track-b-execution-log.md`.*

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

## N/A — 2026-07-26 — a deploy was designed and reviewed; no code was written

**Nothing to exercise, and nothing is running.** Today produced **documents only** — a design
for putting the app on AWS, a four-person review of it, and an implementation plan. **Not one
line of application code changed.** A journey you generate now is identical to one from this
morning. Nothing is listening on any port.

**What happened, in plain terms.** We settled how the app will be hosted so you can share it
with a handful of people, and we decided to start collecting a record of what the app does
when someone presses the two bypass buttons — because that record is the only thing that can
answer the questions your ear can't, and it's worth having from the first few users rather
than the hundredth.

Then four reviewers went over the whole system, which had not been done in a long time. They
found seven problems **in the plan rather than in the app**, and the most useful one was
embarrassing: the plan claimed a particular kind of broken graph file would load silently and
cause wrong answers. It doesn't — it fails loudly. Worse, the check written to prove the fix
worked **would have passed before anything was fixed.** All of that is corrected now, before
any code was written, which is the cheapest possible moment.

**Two things they found that you would eventually have hit as a user, and both are now
scheduled:** every link you shared would have failed to open for the person you sent it to,
and the app has no phone layout at all — on an iPhone the artist's name gets squeezed to
nothing. Neither was in the original plan.

**Nothing is proposed for you to test.** The next entry here will come when something is
actually built and running.

## N/A — 2026-07-26 (later) — two more measurements ran; the app is untouched

**Nothing to exercise, and nothing is running.** Two measurements ran this afternoon and
**neither changed the app**. No routing, no graph, no setting — a journey you generate now
is identical to one from this morning.

**The servers from earlier today have been stopped**, at your request. Nothing is
listening on either port. If you want the app again, start it the usual way.

**What was learned, in plain terms.** This morning's question was whether the barely-
connected artists we counted are the reason the app never introduces you to them. The
answer, from journeys the app had already produced: it never once put a barely-connected
artist in the middle. That first check was weak on its own, because those journeys all ran
between very famous artists. So a second run built journeys that **start and end** at
barely-connected artists — the best possible chance for others like them to show up in the
middle. They still almost never did.

**What that does and does not mean.** It means being barely connected really is associated
with never being offered to you. It does **not** mean we know why: it could be that the app
weighs them up and passes over them, or simply that an artist with two connections has far
fewer places it could sit between two others. Those point to opposite fixes, and nothing
measured so far tells them apart. That is written down as the first thing to settle if this
is ever picked up.

**Nothing is proposed and nothing was changed.** The next entry here will come when
something is actually adopted into the running app.

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

## N/A — 2026-07-25 — two more experiments ran; the app is untouched

**Nothing to exercise.** Two things ran today and **neither changed the app**. A path you
generate now is identical to one from yesterday, and to one from the day before.

What ran, in plain terms. First, the "charge extra for the motorway" idea from last time was
re-run properly — it had accidentally been tested at half strength. This time it ran at full
strength and well past it, to the point where those hops are priced so high the router avoids
them unless it has no choice. It made journeys somewhat more obscure and somewhat longer, but
nowhere near enough to count, so **nothing was adopted**. Second, a measurement was taken of
the graph itself, reading the raw crawl data. It changed nothing — it only measured.

**The one thing worth knowing, because it explains your complaint.** The app currently takes
about 85% of its steps along connections it treats as "maximally similar". At your best-known
artists — The Beatles, Radiohead, Pink Floyd and eighteen others we test with — **every single
connection is in that category**, and they are all recorded with the identical number. So when
the app is standing on one of those artists, it genuinely cannot tell which neighbour is the
closest match, and falls back on picking someone of similar fame. That is diagnosed, not fixed,
and fixing it would mean rebuilding the graph — which is a decision waiting on you.

**Nothing is queued for you to test**, because there is nothing new to press. The next entry
here will come when something is actually adopted into the running app.

**One question to keep in mind for whenever a change does ship.** The most promising setting
made journeys longer — around 7 stops instead of 5, occasionally 14. Nobody knows where a
journey stops feeling like a journey, and no measurement will find it. That is a
use-the-app question and it is yours to answer when the time comes.

Clips remain known, unrelated, and untouched.

## N/A — 2026-07-24 — Track 2 sweep RAN and returned a null: nothing app-facing changed

**Nothing to exercise, and this time that is the headline rather than a technicality.** The
Track 2 sweep ran to completion and **no configuration beat what the app already does**, so
there is nothing to adopt and nothing changed. The app routes on the same graph as before,
with the same weights. **A path you generate today is identical to one from yesterday.**

Recorded per C1's honesty rule instead of inventing a test. What ran: fifteen candidate
routing configurations, offline, against artists you and I never showed the app. What changed
in the running app: nothing — no routing code, no graph, no setting.

**One builder-side change that cannot affect you yet.** The graph *builder* now refuses to
produce a graph containing artists with no name. It only fires when a graph is rebuilt, and no
rebuild is due until you decide what to do about the 33 nameless artists already in the current
one. Until then the app is untouched.

**What is worth knowing, since it explains something you reported.** Your complaint that
pressing *know them already* repeatedly does not surface more obscure artists now has a
measured cause: the rule that was supposed to make repeated presses dig deeper is firing
constantly and **changing nothing** — tripling its strength moves not a single path. That is
diagnosed, not fixed, and the fix is a decision for you (see the handoff).

Clips (C1/C2) remain known, unrelated, and untouched.

## N/A — 2026-07-24 — Track 2 scorer built: nothing app-facing changed

**Nothing to exercise.** This session built the Stage A arm scorer — offline analysis
tooling in `builder/analysis/2026-07-24-track2-arm-scorer/` that never touches the running
app. **No shipped code, no graph artifact, no config default, and no adoption changed**, and
no experimental arm ran. The app routes on the same `graph-t15-tiebreakfix.bin` as before.

Recorded per closeout C1's honesty rule rather than inventing a test. The next app-facing
queue entry will come when an arm wins and a candidate is **adopted** into
`ApiConfig`/`pathfinding.py` — which has not happened.

Clips (C1/C2) remain known, unrelated, and untouched.

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

## N/A — 2026-07-26 — a second measurement ran; the app is untouched

**Nothing new to exercise, but the app is running and three older entries below are
still waiting on you.**

What ran: a read-only measurement asking *why* certain artists are barely connected,
following on from the census below. **It changed nothing** — no routing, no graph, no
setting. A journey you generate now is identical to one from yesterday.

**Both servers are running and nothing owns them**, so they will outlive this session
and every terminal. Started fresh today, after the latest change:

| what | address | PID |
|---|---|---|
| the app | **http://localhost:5173** | 206500 |
| the service behind it | http://127.0.0.1:8000 | 226716 |

Open the first one in a browser and it works. **If you want them gone**, stop those two
PIDs — nothing else will.

**What was learned, in plain terms, because it explains something you may notice.**
Some artists can never be offered to you in the middle of a journey, and there turned
out to be two quite different reasons. For the ones you'd recognise — Meat Loaf, Elbow,
The Cult, The Streets, Tom Jones — the data is all there: fifty similar artists, all of
them in the app. The rule that builds the map then throws nearly all of it away, because
it insists two artists both name each other, and a famous artist's neighbours are more
listened-to than it is and name someone else. **Those are recoverable.** For the great
majority by headcount, the music service simply never named more than one or two similar
artists in the first place — and that turned out to be because of a cut-off *we* chose
when asking it, not because the data does not exist. Changing that would mean collecting
everything again from scratch.

**Nothing is proposed and nothing was changed.** The next entry here will come when
something is actually adopted into the running app.

**The three entries below are still QUEUED and are the ones worth your time.**

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
