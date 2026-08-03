# Handoff — the featured-credit filter track, 2026-08-03

**Role: ⚠ SUPERSEDED 2026-08-03 (later) on next actions by
[`2026-08-03-HANDOFF-cap-reeval-prereg.md`](2026-08-03-HANDOFF-cap-reeval-prereg.md)** —
the cap re-evaluation pre-registration it named as next has been written, reviewed,
frozen and amended once. Remains authoritative for the featured-credit filter track's
internals. *(Original role:)* **ACTIVE — the CURRENT handoff.** Nothing supersedes it.
Supersedes
[`2026-08-02-HANDOFF-fame-instrument.md`](2026-08-02-HANDOFF-fame-instrument.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff.** The track completed: rule fixed cold, amended once at the
owner's ruling, lists frozen per population, wired, verified, **adoption ruled by the
owner (2026-08-03, without the calibration hand-review) and enacted by merging PR #67.**
Nothing is in flight, no port is listening, the tree is clean and pushed. Reasoning:
[`2026-08-03-featured-credit-filter-execution-log.md`](2026-08-03-featured-credit-filter-execution-log.md)
(§1–§8). Governing document:
[`specs/2026-08-03-featured-credit-filter-rule.md`](specs/2026-08-03-featured-credit-filter-rule.md)
(`FCF-`, amended by `FCF-AM1`).

## The claims that must not be reverted

1. **TJ Brown's drop is a named-in-advance false positive, fixed in FCF-5 before any
   lookup ran.** A future reader finding a real artist on the drop list has found the
   residual the rule document already names, not a defect. No post-hoc keep-list; the
   no-second-mechanism closure argument from the adopted no-release rule applies here
   too.
2. **The calibration hand-review was DECLINED by the owner at adoption (2026-08-03).**
   It was flagged as his spend, priced twice (once at first freeze, again when `FCF-AM1`
   enlarged the no-lookup drop population), and he ruled adoption without it. Do not
   re-propose it absent new grounds; the drop-side false-positive rate is *accepted as
   unmeasured*.
3. **`FCF-AM1` is a post-result amendment and says so on the page** — its evidence is
   the owner's spot checks plus the committed split measurement, never the clip results.
   Its disclosure must not be tidied away, and the pre-amendment lists
   (`fcf_droplist.json`, `fcf_droplist_algb.json`) stay in the probe directory as the
   record — the shipped lists are the `_am1` pair, strict supersets, asserted at
   re-freeze.
4. **The two drop rules are disjoint by construction** (this class requires ≥ 1
   release-group credit; the no-release tail requires zero), census-verified with an
   abort check. Their application order cannot matter; both run before the mass
   computation, which the ordering tests pin.
5. **The three pipeline mirrors were deliberately NOT given either drop stage** — read
   every graph they built as predating both. The two era-pinned callers pin both flags
   off. Same recorded decision as 2026-08-02, extended.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (three new rows; the
fame-instrument handoff's role line), `TEST-QUEUE.md` (new N/A entry), the rule document
(FCF-6 adoption note), `builder/analysis/README.md` (era section), the probe README, and
the execution log through §8.

## What I know that is not in the durable record

Checked deliberately; the log was written per task. Three residuals, folded here:

- **The keep rate is measurably higher among Discogs-exempt-adjacent members.** The
  original class (no Discogs presence at all) kept 394/913 DSP-linked (43%); the
  `FCF-AM1` increment (shared-credit-only) kept 367/1,011 (36%) — but the increment's
  wrong-artist rate was half the original's (≈1/20 vs ≈1/9, `byp13_wrong_artist` in the
  two capture JSONs). Consistent with the increment being realer on average, as the
  amendment's cost paragraph predicted. Nothing consumed this; it is context for any
  future read of the keep lists.
- **The clip-stage pricing figure held**: ~45 min per 1,400 lookups (tail_clips'
  measurement) predicted both runs within a few minutes. Safe to reuse for any future
  keep-check census.
- **The cap re-evaluation prereg author should know the cleanup now has two components
  per population** — a build with `drop_no_release_tail` and `drop_featured_credit` both
  on (the defaults) is "the cleaned substrate"; holding cleanup constant across cells
  means holding *both* flags, and the factor table should carry them as one row or two
  deliberately, not by omission.
