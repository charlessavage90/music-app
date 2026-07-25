# Use-the-app test queue

**Role: ACTIVE, permanent.** The `closeout` skill appends here; `session-start` reads here
and flags anything that has been sitting untested. This is the async counterpart to the
test suites — it catches the defect class that code review and mocked tests structurally
cannot.

**One entry per closeout. Newest first. Mark an entry DONE with the date and what it
found, or DONE — nothing found. Do not delete entries; the record of what was exercised is
the point.**

---

## ⛔ BLOCKED — 2026-07-25 — do not run question 2 yet; it cannot pass

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

## QUEUED (question 1 only) — 2026-07-25 — clips should play the right artist, and still work an hour later

**This one is app-facing, and it is the first entry in a while that is.** Two clip defects
and four interface annoyances are fixed. Nothing about *which artists* you get changed —
no routing, no cost function, no graph. The journey between any two artists is the same
journey as yesterday; only the audio and the buttons are different.

**The two questions this entry exists to answer**, and they need you rather than a test:

1. **Does the clip play the artist on the card?** Previously the app searched the catalogue
   and took the first result — but that search matches *song titles* as well as artist
   names, so searching for the band The Format returned a song *called* "The Format" by a
   rapper, and played that. Now the app checks the returned track actually belongs to the
   artist named on the card.
2. **Does a clip still play about an hour after you opened the page?** The audio links the
   catalogue hands out are signed and expire within the hour, and we were storing them for
   thirty days — so every play after the first hour was silent. The app now remembers
   *which track* to play rather than the link to it, and fetches a fresh link each time.

**One thing that changed after this entry was first written.** A clip that fails to load
now leaves the card silent instead of returning an error. That matters for *this* test
rather than in general: the music catalogue limits how often we may ask it, and the fix to
question 2 roughly doubles how often we ask. Without this, hitting that limit during your
hour would have produced dead cards that looked exactly like question 2 failing — so a
result you could not have trusted. Detail: the execution log's §12.

**A deliberate trade you should know about before it looks like a bug.** When no track in
the catalogue matches the artist, the card is now **silent instead of playing a stranger**.
So you will see some cards with no audio that previously played something — that is the fix
working, not a regression. Worth reporting only if it happens to artists you would expect
any streaming service to have.

**What to exercise:**

1. **Any path, and press play on several cards.** The one thing to watch is whether the
   voice you hear plausibly belongs to the name on the card. Obscure artists are where this
   was worst, so a path that digs is more informative than a famous one.
2. **Leave the tab open, go and do something else for an hour, come back and press play.**
   This is the whole of question 2 and there is no faster way to ask it. A clip that played
   before you left must still play when you return.
3. **The pause button on a card.** It only ever worked on the bar at the bottom of the
   screen; pressing it on the card itself used to restart the track from the beginning. It
   should now pause, and pressing again should resume from where it stopped.
4. **Press a bypass button and listen.** Audio from the old path should stop when the new
   one arrives, rather than playing over it.
5. **Look at the first and last cards.** The two artists you chose no longer offer "not for
   me" or "I know them" — rejecting them never made sense, since the whole journey is
   defined by them.
6. **The two controls at the top of a path.** "← New path" takes you back to picking two
   artists, **with the pair you were just on already filled into the boxes** — so swapping
   one end for a new artist does not mean retyping both. "↺ Reset path" throws away every
   bypass you have pressed and puts you back on the original path between the same two
   artists; it only appears once you have pressed something. Before this, the only way off
   a path page was the browser's Back button.

**What "wrong" would look like:** a clip that plays an obviously different artist (question
1 failed); silence after an hour on a card that played earlier (question 2 failed); a card
whose pause button still restarts the track; audio from a bypassed path continuing to play;
a bypass button on the first or last card; "New path" arriving at empty boxes, or with a
dropdown of search results already covering the page. Also worth a mention: **a path with only your two
artists and nothing in between now offers no bypass buttons at all** — that is expected
given the change, but it leaves you with nothing to press, and it is the known
zero-intermediary case (F1) rather than a new defect.

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
