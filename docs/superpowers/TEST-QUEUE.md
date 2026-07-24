# Use-the-app test queue

**Role: ACTIVE, permanent.** The `closeout` skill appends here; `session-start` reads here
and flags anything that has been sitting untested. This is the async counterpart to the
test suites — it catches the defect class that code review and mocked tests structurally
cannot.

**One entry per closeout. Newest first. Mark an entry DONE with the date and what it
found, or DONE — nothing found. Do not delete entries; the record of what was exercised is
the point.**

---

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
