# GBL run — execution log (the blind runner session)

**Session role:** mechanics-only runner for the gentle-arm blind listen, driven entirely
by `builder/analysis/2026-08-04-gentle-arm-blind-listen/RUNNER-BRIEF.md`. This session did
not execute the harness plan and read none of the material the brief barred: no
`docs/superpowers/findings/`, no `NEXT.md`, no spec §1–§2, no execution log — until the
owner instructed it to write this file, after the listen was complete and committed.

**Date:** 2026-08-04. **Branch:** `gentle-arm-blind-listen`.

**What this session produced:** three commits — `f730fb8` (verdicts), `2570e21` (result),
`816689a` (the owner's pre-result notes) — plus this log.

**What it did not produce:** any assessment. The write-up belongs to a further fresh
session, per the harness log §8 and the `CRE-` Stage-3 rule.

---

## 1. Steps run, in order

| Step | Outcome |
|---|---|
| Preflight — `git status`, branch | Clean, on `gentle-arm-blind-listen` |
| Preflight — harness tests | 30 passed, ~4 s |
| `gbl_generate.py` | `8 pairs x 3 depths x 2 arms; sealed mapping written; page data clean` — all five self-checks passed |
| `gbl_clips.py` | 145/152 artists resolved (run four times in total; see §3) |
| `gbl_page.py` smoke test | Passed; detail in §2 |
| The listen | Split across two sittings, ~12:15 and ~17:00 |
| `/status` at the end | `complete: true`, 32/32 rows |
| `gbl_unblind.py` | Ran clean, wrote `gbl_result.json` |

**The fifth self-check did not fire.** The brief flagged it as the one most likely to —
three pairs had been recombined by the owner and nobody had confirmed they reach depth 20
with room to judge. They did. No pair swap was needed and none was requested.

## 2. Smoke test — what was actually confirmed

Beyond the brief's four items, because a failure in any of them would have cost a sitting:

- Page renders in a real browser (not just HTTP 200): opened in Chrome, DOM built, no
  console errors on load.
- A clip plays **in the page**: counter advanced to `0:06 / 0:29` on a real `<audio>`
  element. Separately, 5/5 sampled preview URLs returned `206 audio/mpeg`.
- **The page's own save button writes through** — this is not the same check as posting to
  `/verdict` with a script, and a broken button would have been invisible to the API-level
  test. Verified by clicking a radio and `save row`, then reading the changed pick off disk.
- Saved rows survive a server restart (`/status` held at 30 missing across a restart).
- `/status` returns the missing rows.
- Smoke-test verdicts deleted afterwards; the file's entire contents were read first and
  confirmed to be smoke-test data only. Clean start verified at 32/32 missing.

## 3. Clip TTL — corrected finding

Deezer preview signatures carry `exp=` in the URL. Measured across four batches:

| batch | resolved | expired | lifetime |
|---|---|---|---|
| 1 | ~12:15 | 12:30 | ~15 min |
| 2 | ~12:36 | 12:51 | ~15 min |
| 3 | ~16:58 | 17:13 | ~15 min |
| 4 | ~17:14 | 17:29 | ~15 min |

**The TTL is a consistent ~15 minutes.** `gbl_clips.py`'s docstring — "re-run on listen
day, minutes before serving" — is correct as written.

**Recorded because the mistake is the useful part:** this session first reported batch 3 as
lasting "over four hours, unlike the ~15-minute windows", and wrote that into the owner's
running commentary. It had measured only the expiry timestamp and never the resolution
time, then inferred a lifetime from one endpoint. The four hours were the owner stepping
away for work, not a long-lived signature; he corrected it. **A duration claim needs both
endpoints measured** — the probe script printed `min(exp)` and no clock reading, which made
the wrong inference easy and the right one impossible.

**Operational consequence for the next listen, which is the part that matters:** a ~15
minute window is shorter than a sitting. Four re-runs were needed. Each re-run requires
`gbl_clips.py` **and** a server restart (clips are embedded into the HTML at server start,
so a page refresh alone re-serves the same dead URLs), then a browser refresh by the
listener. Verdicts survive this untouched — the server reloads them from disk. Budget one
re-run per return from a break, and one mid-pair if a pair runs long.

## 4. Observations the owner reported during the run

Recorded verbatim-in-substance, **not characterised** — classifying these is the write-up
session's call, and `TEST-QUEUE.md` entries were deliberately not written by this session.
His full pre-result notes are `gbl_owner_notes.md`, committed at `816689a`.

1. **Missing clips** — many instances. 7 of 152 artists resolved to nothing; silent card
   slots were 4 on one side and 8 on the other out of 315, which this session judged not
   conspicuous under the brief's §3 test and therefore did not report at the time.
2. **Unjudgeable previews** — clips that were song intros or otherwise gave nothing to
   evaluate an artist on.
3. **Suspected wrong-artist clip** — at least one case, possibly more. `BYP-13` is live and
   shared by both sides by construction, per `gbl_clips.py`'s docstring.

He notes in `gbl_owner_notes.md` that (2) and (3) leave him unable to tell an incoherent
*artist* from an incoherent *clip choice*. That bears on how coherence verdicts should be
read, and it is his statement, not this session's inference.

## 5. Blind integrity — what this session saw and did not see

Stated plainly so the write-up session can weigh it rather than assume either way.

- **Never opened** `.superpowers/gbl/` directly, and never saw the sealed mapping.
- **Did read the clips map indirectly**, by extracting the embedded JSON from the served
  page in order to check per-side clip coverage (§3, and the brief's §3 asks for exactly
  that comparison). The page is declared safe to view and the clip map is non-differential
  by construction — resolution is name-based for both arms — so this carries no arm
  identity. Recorded anyway rather than left to be discovered.
- **Did see the unblind script's one-line output**, which names the branch and margin. This
  was unavoidable at step 8. It happened **after** all 32 rows were saved and committed at
  `f730fb8`, so it cannot have reached any verdict. It was disclosed to the owner before he
  dictated his notes, and he chose to proceed; the notes at `816689a` are his words with no
  summarising or reordering.
- **The owner reports the blind did not hold on his side.** In his own words: it was
  "almost always really easy to tell which side was the 'new' graph and which is the one
  we've been using", and he "tried not to think about that". This is the single most
  load-bearing thing in this log for whoever writes up the result. It is his observation,
  volunteered before he read `gbl_result.json`, and this session offers no view on what it
  does to the result's standing.

## 6. Loose ends left deliberately

- **`gbl_page_data.json` is untracked.** Generated by `gbl_generate.py`; this session left
  the commit-or-ignore decision alone rather than deciding it blind.
- **No `TEST-QUEUE.md` entries written**, for the reason in §4.
- **`NEXT.md` not touched**, and no closeout run. Both need to know what this listen was
  *for*, which is precisely the context the blinding removed.
- **A bookkeeping caution:** this session once told the owner a depth-20 row was unsaved,
  having read `gbl_verdicts.json` at a moment that did not reflect his latest save, and
  corrected it a minute later. `/status` is the authority on completeness; a direct file
  read timed against the owner's actions is not.

## 7. What is owed

The write-up of `gbl_result.json`, by a fresh session that did not run the listen. It
should read, in this order: `gbl_verdicts.json` (the result), `gbl_owner_notes.md` (his
pre-result impressions, and §5 above on how they were taken), then `gbl_result.json`.
