# Retained execution log — `LBL-` listen 2 prepared under `LBD-AM6`, 2026-09-12

**Role: RETAINED EXECUTION LOG. ACTIVE. Owns no figures and no status.** Figures for the
pre-screen belong to `../../builder/analysis/2026-09-10-lbd-blind-listen/lbl_prescreen2.md`;
listen 1's belong to `findings/2026-09-11-lbl-listen1-results.md`; status belongs to
[`NEXT.md`](NEXT.md). Governing document:
[`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
the **`LBD-AM6`** block at the end of §10.

**Branch `lbl-listen2-prep`, PR #122** (addresses only; `gh` says where they are). Written from a
worktree at `C:\Users\charl\worktrees\music-app-lbl`, taken before orienting because another session
was live on `dls-item1-invocation-repair` in the main tree.

> ⚠ **This session ran the pre-screen and has seen 46 candidate pairs' journeys labelled by map. It
> may not run listen 2 and may not write it up.** `LBD-AM6`'s preamble states the same thing, which
> is where it binds; this is the record of why it was needed.

---

## 0. What the owner decided, and what was left to the session

He chose the route himself and stated it as a constraint, not a question: listen 2 keeps its
**registered comparison** (`LBD-A0V` against `LBD-A5V`, the threshold question, reads `LBL-R1`–`R4`
unchanged) and gets **new pairs and the six instrument fixes**, by amendment, before any journey
exists. He also fixed the sequence — pre-screen first, amendment second, materials third — and the
stop condition: fewer than twelve survivors means commit the counts and report, without writing the
amendment.

Everything below that line was the session's: the pool departures, the screen's two thresholds, the
ranking's tie-breaks, `LBL-Q4`'s treatment, and where the map-labelled output is allowed to live.

## 1. `LBD-D6` — asked before anything was written, as instructed

The exposure was worked out before asking, so the question was not "what should we do" but "here is
what it does and does not touch, and it is your call because it is your rule and the cost is yours".
**The answer corrected the framing in a way worth recording:** the session's note had described the
pairing form's uneven effect as an exposure bearing on the comparison; the owner pointed out that
both arms use ListenBrainz's own pairing semantics — the faithful form — so nothing `LBD-A4` can
return changes either map or listen 2's read. The exposure is real but it is about **generalisation**,
not internal validity, and it is written up in that narrower shape as `LBD-X6`.

The ruling is quoted verbatim in `LBD-AM6-7`, and `NEXT.md`'s `LBD-A4` deferral row was narrowed as
he instructed, with the old condition struck in place rather than deleted.

## 2. The pre-screen — why these gates and not others

**The design problem.** Listen 1 tied, and its §3 measured the limiting factor rather than inferring
it. Two failure modes cost rows: journeys too short to have a shape, and interiors the owner already
knew. Both are properties of the **pair**, so both are fixable at selection time. A third — the two
maps simply agreeing — costs a row silently, and listen 1 had no screen for it at all.

**Gate 1, at least 3 interior artists at every depth on both maps.** `LBD-AM5-5`'s gate (c) asked
for *an* interior artist, which is a depth being reachable rather than a journey being judgeable.
Three is the smallest number that leaves a shape to compare: two consecutive steps to hear.

**Gate 2, the interiors differ at 2 of 3 depths.** One differing depth out of three is thin evidence
that the maps disagree anywhere it matters; requiring all three would have been a much harder screen
whose only benefit is over a bar nothing reads. **This gate is the one that needed care**: it selects
on the *magnitude* of the difference, and it must never see its *direction*. A screen that preferred
pairs where one map's journeys were longer, or more obscure, would have hand-picked the pairs that
map wins on, and the listen would be worthless without anyone being able to see why.

**Ranking on fewest familiar interiors.** §4.2's defect, turned into an ordering rather than a gate —
a gate would have needed a threshold nobody has evidence for, and familiarity is a property that
degrades gracefully.

**Three departures from `lbl_pairs.py`'s pool rule**, recorded as `D1`–`D3` in the output and in the
amendment. `D1` and `D2` are worth separating: listen 1's **primary** endpoints are excluded at
artist level because he heard `LBD-A0V` journeys between them and `LBD-A0V` is listen 2's incumbent,
so a remembered interior identifies a side; its **reserve** pairs are banned only as pairs, because
no substitution fired and none was ever heard, so those artists carry no memory. Excluding reserves
at artist level would have cost sixteen artists from a pool of 125 for no blind benefit at all.

**What the screen does NOT do:** it does not exclude the previously dealt listen-2 pairs. No journey
was ever generated on them and no verdict exists, so re-drawing one spends nothing — and two of them
did in fact come back into the candidate draw and were rejected on their merits.

## 3. The output is map-labelled, and that was the one real hazard in this work

`lbl_prescreen2.json` records each map's journey length per pair and depth. A blind runner who read
it could match a length against the served page and know which side was which. Two options were
available: keep the per-map detail out of the committed record, or commit it and forbid it. **The
second was chosen** — the owner asked for those figures to be recorded, the forbid-list mechanism
already exists and is how `lbl_maps.json` is handled, and a screen whose evidence is not committed
cannot be audited afterwards. The three `lbl_prescreen2.*` files are named explicitly in the runner
brief, with the reason, rather than folded into an existing line.

`lbl_pairs2.json` was deliberately kept free of per-map detail so the runner may read it.

## 4. `LBL-Q4`'s treatment — where the design pressure actually was

The owner's instruction allowed either a pick-strength question with its own pre-registered
treatment **or** an explicit statement that rows are counted and strength is not. It also said
`LBL-R1`–`R4` are unchanged. **Those two together settle it:** any treatment that lets strength
reach the tally *is* a change to the reads, whatever it is called. So strength is asked on the row
and in advance, and the tally does not read it; it gets a descriptive read with no threshold and no
branch. `lbl_unblind.py` is tested for the invariance directly, because a claim that the reads are
unchanged is exactly the kind that is true when written and quietly false two commits later.

The reason to ask at all is §4.5's: the tally weighs a landslide row like a hairline one, and
inventing a strength coding afterwards from his notes is barred. Asking in advance is what makes the
same quantity admissible later.

## 5. Everything is keyed per listen, and listen 1's record is load-bearing

`MIN_INTERIOR_BY_LISTEN`, `SIDE_ASSIGNMENT_BY_LISTEN`, `ROW_EXTRAS_BY_LISTEN`, `PAIRS_BY_LISTEN`.
The temptation was to change the constants outright, since listen 1 will never be generated again.
**It would have been wrong**: `lbl_unblind.py` still reads `lbl_listen1_verdicts.json`, and a
completeness rule that demanded `LBL-Q3` would have made the finished listen retroactively
incomplete. There is a test asserting the committed listen-1 verdicts still read as complete, over
the real file rather than a fixture.

`check_pair`'s `min_interior` defaults to 1 for the same reason — an un-parameterised call gets
listen 1's frozen behaviour, not listen 2's.

## 6. The differential check, as the owner asked it to be verified

G5 existed but was inline in `main()`, which is untestable without two real artifacts. It was
extracted as `assert_differential` and given three tests: a page serving one map against itself is
refused; one differing row anywhere passes; and the check looks across every pair rather than
stopping at the first. The extraction changed no behaviour.

## 7. What was verified rather than assumed

- **Both maps' sha256s match `../../builder/analysis/2026-09-10-lbd-served-population/README.md` §5
  exactly**, hashed from disk at session start and again by `load_map` on every run.
- **No shipped code is touched.** Nothing outside `builder/analysis/2026-09-10-lbd-blind-listen/`
  and `docs/` changed; `api/` and `frontend/` are untouched.
- **121 tests pass** in the harness suite (`uv run --extra dev --with duckdb pytest
  analysis/2026-09-10-lbd-blind-listen -q`).
- **The claim that listen 1 touched no shipped code** — carried in its handoff — was checked against
  the merged PR's file list before being relied on. It holds.

## 8. What is NOT done, deliberately

- **No journey exists for listen 2.** `lbl_generate.py --listen 2` has never been run. The
  pre-screen's journeys are the pre-screen's own and are not the listen's stimulus.
- **No page is generated and no server is running.** Ports 8000, 5173 and 8765 were untouched.
- **`LBD-A4` was not run**, per the ruling's last sentence.
- **`NEXT.md`'s top status block is not rewritten here** — that is `closeout` `A2-next`, and another
  session is live in the main tree with `NEXT.md` among the files it touches.

## 9. One thing a successor should not have to rediscover

The greedy pair draw is **order-dependent**, so the candidate set is a function of the pool order and
of which artists were excluded. That is the committed rule's determinism and it is a feature — but it
means the survivor list cannot be reproduced by re-running the screen against a *different* exclusion
set and expecting the same pairs to appear. If any exclusion changes, the whole draw changes, and the
ranking with it.
