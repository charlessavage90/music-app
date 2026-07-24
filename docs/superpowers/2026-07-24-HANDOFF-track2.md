# HANDOFF — Track 2, mid-track, 2026-07-24

**Role: ACTIVE, short-lived by design.** Written at a mid-flight retirement, for a session
picking up cold. Records **only what is not already in the record.** Read the execution log
first, then this:

> **[`2026-07-23-repair-and-retune-execution-log.md`](2026-07-23-repair-and-retune-execution-log.md)**,
> the "Track 2 — cost-function retune" section — in particular the last three entries:
> "P4 resolved — Deezer … FAILS", "Next unit — the Wikipedia pageviews proxy", and the
> "Consulting-pass deferrals". `docs/README.md` classifies every document.

**Do not re-derive from this file.** It is a list of loose ends, not a summary. Where this
disagrees with the execution log, the log wins. Supersedes the 2026-07-23 handoff (now
HISTORICAL — its loose ends are closed or folded in below).

**First action for the cold session: run `closeout` B1 — dispatch the `doc-auditor`.** It
was deferred from this mid-flight closeout to the fresh session that has the note in hand
(Part B is a fresh-session step). The closeout skill's own rule: *the strongest predictor
the audit finds something is a session concluding it doesn't need one.* Docs changed a lot
this session (A10, claim 23, the P4 result, four B5 fixes), which is exactly when
descriptions elsewhere go stale.

---

## 1. State in three lines

- **P4 (fame proxy) is half-resolved: Deezer `nb_fan` FAILED §5** — two pre-registered
  falsifiers fired. Recorded, committed, figures owned by
  `builder/analysis/2026-07-23-track2-fame-proxy/` (README §4 + `score.json`).
- **The pre-registered next step is the Wikipedia-pageviews re-run** — same committed
  labels, `score.py` already proxy-agnostic. **Not built.** This is the whole of the next
  unit of work.
- **No sweep arm has been scored. No arm has run.** Everything downstream of a fit proxy
  (P6 percentile machinery, the C1–C6 harness, the D4/D6/D7 + C3-anchor amendment) still
  waits. Adopted artifact untouched, sha256 `4cb84ef9…b061dc8`.

## 2. The one open piece of work — the Wikipedia proxy

Not a decision; the pre-registration already chose it when Deezer failed. What it needs,
enumerated so it is not re-derived:

- **Reuse, do not rebuild:** `labels.json`, `blind_order.json`, `sample.json` are fixed —
  **do not re-collect or re-shuffle labels.** `score.py` reads any `fan_counts.json`-shaped
  file (`{"rows":[{"query","nb_fan","matched",…}], "match_failure_rate":…}`) and applies the
  four §5 falsifiers unchanged. Point it at Wikipedia counts.
- **The hard part is name → article resolution**, which Deezer did not have. English
  Wikipedia (right for an English-speaking owner — state the choice). Disambiguation and
  cross-language cases the sample deliberately holds: **林俊傑 → "JJ Lin"**, and lo-fi/synth
  acts (saib., idealism, Purrple Cat, Toonorth, Leavv) that **may have no article at all —
  a no-article is a legitimate match failure, not something to hand-resolve.**
- **Fix and assert the pageviews window before fetching** (Wikimedia REST pageviews API,
  monthly, summed or averaged over a stated span), exactly as Deezer fixed
  exact-match-after-P5 first. Match failure > 6 of 29 is still a live falsifier.
- **A model to copy:** `fetch_fame.py` has a `--probe` mode that checks the external
  assumption out-of-sample before touching the sample. Do the same for the pageviews API.
- **If Wikipedia also fails:** §5's terminal fallback is owner-labelling of every
  evaluated-path artist. Real owner time, **his** decision — put it to him, do not enter it.

## 3. Considered and decided against this session (so it is not re-argued)

- **Fetch-then-label** (the previous handoff's order). Reversed to **label-then-fetch**:
  match failure is a *measured* falsifier, so fetching first and quietly dropping an
  unresolvable name would corrupt what C6 measures; §5 numbers labelling as step 1 for that
  reason. Recorded in the execution log.
- **Lowering the 0.70 AUC threshold because the miss was marginal (0.68).** Explicitly
  refused — the threshold was pre-registered before labels existed precisely so a near-miss
  cannot be relitigated post-hoc. The *inversion* falsifier fired outright anyway.
- **Building P6 / the scoring harness speculatively before the proxy verdict.** Declined:
  P6 plugs into a harness that does not exist, and building it first is coding against an
  absent interface. It travels to the successor.
- **Pushing into the Wikipedia proxy in this session.** Declined for a fresh session —
  article-matching is materially harder than Deezer's and deserves fresh attention, and this
  was a clean seam.
- **Re-editing the committed execution-log P4 table to cite-not-restate** the figures now
  owned by the fame-proxy README. Left as-is: both tables were written from the same
  `score.json` and agree exactly, so there is nothing to reconcile — noted only so the
  successor does not read the duplication as an oversight.

## 4. Numbers computed and not written down

Almost none — this session persisted its figures as it went. The only ones:

- **The `--probe` values** (out-of-sample assumption check): Radiohead 4,063,651 /
  Portishead 577,927 / Sault 26,709. Reproducible by `python fetch_fame.py --probe`; not
  persisted to a file. Low value; they only established that `nb_fan` exists and has range.

Everything else is committed: all 29 fan counts in `fan_counts.json`, the four scores and
per-stratum Spearman in `score.json` and README §4, the labels in `labels.json`.

## 5. Things the owner said, now in a file

- **"One committer, and it will be you."** The session commits; a parallel **consultant
  session** (scope: meta-files, rules, skills) does not commit its own work. Its edits —
  `CLAUDE.md`, both `SKILL.md`, and a "Consulting-pass deferrals" section it added to the
  execution log — were committed this session under explicit consultant attribution on the
  owner's instruction. **The consultant is now finished; no more edits expected.** Recorded
  in memory (`roadmap-pointer`) and the commit messages.
- The owner's **29 blind verdicts** are in `labels.json` (via `record_labels.py`).

## 6. In flight / git

- **Nothing running.** No subagents dispatched this session, no background jobs, no stashes.
- **Tree is clean** — unusual for a mid-flight handoff, but this session committed at a
  clean seam and everything is pushed. Nothing untracked to explain (D1-mid: satisfied by a
  clean tree rather than by an inventory).
- **Branch `track2-prereg-amendments`, PR #9 (draft, OPEN)** — body rewritten this session
  to cover the whole branch and updated for the P4 result. Not on `main`.
- **D6 (standing-layer delta vs `main`): +247 net** (256 insertions − 9 deletions), *all*
  the consultant's; this session added nothing to the standing layer. Knowingly
  net-positive — the consultant's two deferred findings (relocate the ~107-line "Writing and
  reviewing plans here" block; supersede Phase 1 log §2) are the scheduled offsets, both due
  at **Track 2 adoption**, not at a worker handoff.

## 7. Deferred findings and whether any came due

None came due at this handoff. Open, with conditions (details in the execution log and
pre-registration §9):

- **P6 percentile machinery, C1–C6 harness, D4/D6/D7 + C3-anchor amendment** — all wait on
  a fit proxy.
- **F1 zero-intermediary guard** — due before the sweep's success criterion is finalised.
- **Consultant's two doc deferrals** — due at Track 2 **adoption** (a worker handoff does
  not satisfy this; verified).
- **C3 depth anchor (old handoff 1b):** the exposure map settles it at 5 bypasses by
  implication; write the one line making it explicit when the D4/D6/D7 amendment lands.
