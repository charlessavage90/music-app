# HANDOFF — Track 2, mid-track, 2026-07-23

**Role: ACTIVE, and short-lived by design.** Written at retirement, for a session picking
up cold. It records **only what is not already in the record.** Everything about what was
done and why is in the execution log — read that first, then this:

> **[`2026-07-23-repair-and-retune-execution-log.md`](2026-07-23-repair-and-retune-execution-log.md)**,
> the "Track 2 — cost-function retune" section. Governing design and pre-registration are
> named there. `docs/README.md` classifies every document.

**Do not re-derive from this file.** It is a list of loose ends, not a summary. Where this
disagrees with the execution log, the log wins.

---

## 1. Open decisions, and what I would do

Nothing here is blocking except P4, which is the owner's.

| # | Open | Options | What I would do, if continuing |
|---|---|---|---|
| **1a** | **The adjudication's §6 claim table has not been updated for claim 23.** The analyst review settled the exact wording; nobody applied it. | Apply now / defer to sweep completion | **Apply now.** The wording is settled, and `findings/2026-07-21-scoring-adjudication.md` is the single figures record — leaving a claim in it that this session's own work has qualified is exactly the drift the figures rule exists to stop. Wording is in the execution log's "What should enter the adjudication's claim table"; the review owns the reasoning. |
| **1b** | **The C3 depth anchor was settled by implication, never explicitly.** The exposure map shows C3 does not cross the floor change, so the anchor stays at 5 bypasses — but no line anywhere says "decided". | Leave at 5 / move to 7 (arithmetically clean, but the −0.5 threshold was pre-registered against a 5→20 span) | **Leave at 5 and write one line saying so.** Moving it changes the threshold's strictness by an unmeasured amount, which trades a settled question for an open one. |
| **1c** | **Build order for the remaining harness.** | Fame-proxy fetcher first / scoring machinery first | **Fetcher first.** P4 is owner-blocked and is the long pole; the fetcher plus the fixed 33-name list is what makes his ten minutes spendable. Scoring can be built while the labels are outstanding. |
| **1d** | **Analyst items D4, D6, D7 remain open** with success conditions in pre-registration §9's closing table. D7 did not fire in 1,512 walks, so it is empirically quiet but not closed. | — | Land D4 and D6 as a single dated amendment before scoring; leave D7 as a one-line pre-registration of the drop-uniformly rule. |
| **1e** | **PR #9's title and body describe only the first commit's scope** (the D1–D3 amendments). Eight commits are on the branch. It is still a draft. | — | Rewrite the body before anyone reviews it. Not done here because it was outside the handoff instruction. |

**Concrete next actions, in order:** (1) PR body + adjudication claim table — both cheap
bookkeeping. (2) Build the Deezer **artist**-search fetcher with exact-name matching and P5
normalisation — it must **not** reuse `clips.py`, which is first-hit with no name
verification (pre-registration §0). (3) Put the 33 names to the owner blind (P4). (4) While
waiting: percentile machinery per P6, fame scoring, C1–C6 computation, and the D4/D6/D7
amendment. (5) Then the 15 arms.

## 2. In flight

**Nothing is running.** One subagent was dispatched this session — `ml-graph-analyst`, to
review the A0 gate. **It completed**, its findings doc and scripts are committed, and I did
**not** resume it. The harness note says a resumed agent can re-notify under the same task
id; if a notification arrives for it, it is not new work.

**No stashes. Everything this session produced is committed and pushed.**

**But the tree is not clean:** three files carry **the owner's own in-flight edits**, made
while this handoff was being written and deliberately **not** committed here —
`CLAUDE.md`, `.claude/skills/closeout/SKILL.md`, `.claude/skills/session-start/SKILL.md`.
(An earlier round of his `CLAUDE.md` rules *was* committed, at `d2aab59`, on his
instruction; these are further edits on top.) **Do not sweep them into a commit of your
own** — `git add -A` is how another session's work gets absorbed, and this repo has had
two sessions live in one tree before. Ask before committing them.

**The one half-built thing:** `builder/analysis/2026-07-23-track2-sweep/` holds the mirror
(`mirror.py`), its gate (`verify_mirror.py`) and the A0 runner (`run_a0.py`). It has **no
scoring code, no fame proxy, and no runner for any arm other than P and A0.** The mirror
carries every sweep knob and is verified; what is missing is everything downstream of it.

## 3. Numbers computed this session that are written down nowhere

Enumerated without judging relevance, as instructed. All are reproducible by re-running the
committed scripts against the asserted artifact.

**From `run_a0.py` — per-pair floor-term firing rate.** Only the pooled 2.94 % reached a
document. Per pair: Miles Davis → Daft Punk **1.66 %**; The Shins → Wishbone Ash **0.73 %**;
Metallica → Taylor Swift **2.12 %**; Radiohead → The Beatles **0.84 %**; Muse → Coldplay
**3.54 %**; Madonna → Bob Dylan **1.24 %**; Pink Floyd → Aphex Twin **3.33 %**;
Nirvana → CROOVE **3.38 %**; Arctic Monkeys → Johnny Cash **1.10 %**; Michael Jackson →
Gorillaz **1.81 %**; System of a Down → R.E.M. **1.23 %**; The Rolling Stones → Linkin Park
**1.50 %**.

**Node ids of the one divergent cell** (names are recorded; ids are not):
P = `[24679, 24238, 27124, 21079, 41293, 33852, 6329, 1598]`;
A0 = `[24679, 24238, 27875, 51550, 33852, 6329, 1598]`.

**Raw popularity of that cell's members**, beyond the two already recorded (Dean Martin
0.6668, Michael Bublé 0.6563): Miles Davis 0.7103, Ella Fitzgerald 0.7094, Mariah Carey
0.6987, Alicia Keys 0.7076, John Legend 0.7036, Ye 0.7206, Daft Punk 0.6726, Meghan Trainor
0.7059.

**Pair 1's own floor-death point is 5 `known` bypasses** (`ceil(0.6726 / 0.15)`). The record
carries the *universal* bound of 7 and the analyst's per-pair work; this pair-specific
figure, which is where the original "dead from d5" wording came from, is not stated anywhere.

**Verification walk depths, per pair:** 21 for ten pairs; **0** for Radiohead → The Beatles
and Muse → Coldplay. Recorded qualitatively ("ten pairs walked the full 21 depths"), not as
per-pair figures.

**`jump_scale_pctl` was never printed.** `MirrorContext.build` computes it at run time and
no run displayed it, so the mean-matching ratio's actual value on this artifact is not
written down by me. (The analyst review's M2 owns the underlying means.)

**`floor_relax_dislike_pctl` = 0.0266…** (`0.05 × 0.08 / 0.15`). Its derivation is commented
in code; the decimal is nowhere in prose. It is **not pre-registered** and is unreachable
under Stage A's all-`known` protocol.

**Per-artist percentiles for all 42 bypassed artists** exist only in script output. Only the
minimum (The Hives, 0.9773) and a partial name list reached the README.

## 4. Considered and dropped — including things dropped within a minute

- **Reconstructing the dislike/known interleaving of the owner's 43-bypass walk.** I proposed
  it, the owner pushed back on distraction, and it failed the "what decision would this
  change" filter: the intermediate states carry no owner verdict, and a mixed-signal walk
  with a human victim choice is not comparable to the scripted policy anyway. **The method is
  worth keeping even though the task was dropped:** at each step the next bypassed artist
  *must appear in the then-current path*, which is a hard constraint that would very likely
  pin the interleaving uniquely by search. Nothing else records this.
- **Normalising the percentile jump term over top-decile-incident edges** instead of
  graph-wide. Rejected: that ratio is ≈ 1.018, so the normalisation would be a near no-op and
  would not remove the scale confound A3 exists to remove. Only the choice is recorded, not
  the rejected alternative.
- **A pair-adaptive floor relax** (`base_floor / 20`, so every pair's floor dies exactly at
  20 bypasses) in place of the fixed 0.05. Rejected because it puts pair-dependence inside an
  arm's definition. Not recorded anywhere.
- **Masking both directions of the direct edge** in guard G. Chose source→target only; a
  shortest path to the target cannot use the reverse direction because the search stops when
  the target is popped. Reasoning survives as a code comment in `mirror.py`.
- **A team review.** Never seriously — the worry was nameable, which per CLAUDE.md makes it a
  targeted single-agent question.
- **Editing the adjudication** (see 1a) — deliberately flagged rather than done, because that
  document owns its claims.
- **Analyst reporting items O1, O2, O9, O10** (fame-driven victim sensitivity arm; stratified
  reporting with and without the two direct-edge pairs; a pooled-artist variant of C1; one
  sentence saying C1 estimates a total effect under the scripted policy). All are
  harness-time items, none implemented.

## 5. Things the owner said that are not yet in any file

- **The pair-8 substitution is CONFIRMED, not provisional.** He said "keep the substitution"
  after being shown that it was an interpretation of a pre-registered rule rather than an
  execution of one. Pre-registration §2.3 and §9 A7 still describe it as reversible at no
  cost before any arm runs — accurate as written, but it understates its status. **Do not
  re-open it as an open question.**
- **He authorised step 2 directly** ("go ahead and build the mirror"), which is why the
  mirror was built before the floor question was settled.
- **A scope steer:** "I didn't want to distract from the main body of work." Speculative
  side-analyses are unwelcome even when cheap. This is what killed §4's first item.
- **His prior mental model was that the historical URLs cannot yield paths** — only the
  bypassed artists. He raised it as a knowledge check. The correction is recorded in the
  trace capture README §3, but the fact that this was a live misconception is worth knowing
  when presenting anything derived from those URLs.
- **He wrote the three new CLAUDE.md rules himself** (commit `d2aab59`) after observing this
  session. They are his words, not distilled from a conversation, and all three name the
  incident they came from.
- **His stated process for this handoff:** he will verify it with a cold read before work
  continues.

## 6. Git

| | |
|---|---|
| Branch | `track2-prereg-amendments`, off `main` at `fa520c6` |
| Pushed | **Yes**, tracking `origin/track2-prereg-amendments` |
| Working tree | **Not clean** — three files carry the *owner's* uncommitted in-flight edits (`CLAUDE.md`, `.claude/skills/closeout/SKILL.md`, `.claude/skills/session-start/SKILL.md`). Nothing of this session's is uncommitted. See §2 — do not sweep them into a commit. |
| HEAD | `d2aab59` |
| PR | **#9, OPEN, DRAFT.** Title and body cover only the first commit's scope and are stale — see 1e |

Eight commits, oldest first: `0aafa01` (D1–D3 amendments) · `84165cb` (P7/P8 status) ·
`0171953` (A6 + execution order) · `0deb613` (P1 capture, A7 substitution) · `2dedefd`
(mirror + gate) · `cf59665` (A0 gate fired) · `2d85559` (A8/A9 resolution) · `d2aab59` (the
owner's CLAUDE.md rules).

**No artifact was rebuilt.** The adopted graph is untouched at sha256
`4cb84ef9…b061dc8`, asserted in every script written this session.
