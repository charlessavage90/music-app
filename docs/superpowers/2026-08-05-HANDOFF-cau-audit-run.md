# HANDOFF — the `CAU-` coherence audit is judged and unscored

**Role: ACTIVE — the CURRENT handoff. Nothing supersedes it.** Supersedes
`2026-08-04-HANDOFF-gbl-harness.md` on next actions. **A seam handoff**: the audit is run
to completion, nothing is in flight, tree clean, no server on any port.

**Branch** `gentle-arm-blind-listen`, draft PR #77.

---

## What the next session does

**Score the audit, then write it up.** Both belong to a session that did not build or run
it — this handoff's author designed the audit, chose its bars and built the instrument, and
scoring it would be marking its own work.

From `builder/` (no env prefix — see the brief; `VAR=value cmd` is bash-only and the owner
runs cmd):

```
uv run --extra dev python -u analysis/2026-08-04-coherence-audit/cau_score.py
```

Then, **before writing anything, read in this order and do not skip ahead:**

1. `specs/2026-08-04-coherence-audit-preregistration.md` — governing; four amendments and
   one correction, all committed before any judgement existed.
2. `cau_judgements.json` — the raw verdicts and the owner's per-slot notes.
3. **`cau_owner_notes.md` — the owner's own summary, written after he finished judging and
   **before** anything was scored (committed unread at `4009707`; `cau_result.json` did not
   exist and no criterion was computed at that commit — the commit timestamp is the
   evidence, not the file's mtime).
4. `cau_result.json` — what the scorer wrote.

**Item 3 comes before item 4 deliberately, and this is the `GBL-` ordering.** His
impressions are evidence in their own right; read after the numbers they become
confirmation of whatever the numbers said, and that cannot be unseen. **Do not open
`cau_result.json` until you have read his note.**

His note is also the only place a whole-path impression can legitimately land: §1 bars any
scored whole-path claim, and §7's per-journey free-text boxes are explicitly unscored. If
his summary makes a claim no criterion measures, **report it as his statement and do not
convert it into a finding.**

**After scoring:** remove the `cau_page_data.json` line from `.gitignore` and commit that
file. It is the stimulus as presented and the judgements cannot be interpreted without it.
It was held back only until the run ended, because diffing it against `gbl_page_data.json`
reveals the 12 inserted red-control artists.

## The state, in one paragraph

The `GBL-` blind listen returned its pre-registered null (margin 3 of a required 5;
`findings/2026-08-04-gentle-arm-blind-listen-results.md` owns those figures and **that null
stands, untouched by anything here**). The owner then identified a confound in that listen's
instrument — a 30-second clip of one arbitrary track cannot support a coherence judgement
about an unfamiliar artist, and that failure activates **only in the arm that succeeds at
delivering unfamiliar artists**. `CAU-` is the one-arm follow-up: 16 journeys from the gentle
arm at depths 10 and 20, every interior card judged "does this artist belong on this
journey?", with proper listening (Spotify, several tracks) for any artist the owner could not
place. **77 judgements are complete and committed at `cb11b38`, and nothing has been
scored.**

## What must not be misread

- **`CAU-G1` is evaluated first and alone.** 12 random artists were inserted as a red
  control. **Below 10 rejections the audit is VOID** — reported as void, never as a weak
  pass, and no reading below it survives. The scorer enforces this; do not compute around it.
- **`D_all` is 53, not 65 and not 77.** 65 real slots were presented and judged; the 12
  sitting next to a control are excluded because they were judged beside a fake artist
  (`CAU-AM3`). This is not a session shrinking the audit — it is the fix for a defect the
  owner caught, and the alternative (28 extra camouflage judgements to keep 65) was his call
  to decline.
- **`CAU-C1`'s 75% bar is the OWNER'S**, ratified at `CAU-AM2` after he was shown the
  argument from `REQ-9`. He initially expressed no preference; the bar is his, not a
  session's.
- **`CAU-C1`'s middle branch is deliberately neither a pass nor a fail.** The branch names
  are `meets_bar` / `ambiguous` / `below_bar` for that reason. **The audit names no default
  in the ambiguous band** — do not supply one.
- **`CAU-C3` can falsify this audit's own premise.** A residual can't-tell rate above 15%
  would mean unfamiliarity, not clip length, was the barrier. Report it prominently if it
  fires.
- **§6's barred reads travel with every sentence:** no comparison with today's app, no
  whole-path or "detour" claim, no novelty claim (void by construction — the run sent him to
  Spotify, where monthly listeners are displayed), no adoption on any outcome, no
  single-factor attribution, and **"the coherence question is now settled" is barred even on
  a pass.**
- **`CAU-AM4` weakened the control on purpose.** Cards carry MBID, disambiguation and a
  MusicBrainz link so a lookup lands on the right artist. A disambiguation makes a planted
  artist easier to reject without playing it, so **a `CAU-G1` pass is a weaker demonstration
  of discrimination than it would have been.** Recorded before the run, not discovered after.

## Owed, and by whom

Nothing is owed by this session. Two items remain open and **neither is `CAU-`**: the
owner's 2026-08-04 no-commercialization ruling is in memory but still not in the repo record
(it belongs in `PRODUCT-REQUIREMENTS.md`), and the eight 2026-07-22→27 `TEST-QUEUE.md`
entries remain `QUEUED` and unruled-on — flagged now at five consecutive closeouts.

**No closeout has been run for the `CAU-` build-and-run chunk.** The next session should run
one after the write-up lands.

## Defects found during this chunk, all fixed, all worth knowing

1. **The owner caught two design defects before any judgement existed** — isolated triples
   could not pose the question where several consecutive artists are novel (`CAU-AM1`), and
   an inserted control contaminated its two real neighbours, measured at 20 of 65 slots
   (`CAU-AM3`). Both were pre-run. This is the pre-registration discipline working.
2. **A `CAU-CORR1` internal contradiction** — §4 said controls *replace* an artist while
   `CAU-AM1`'s arithmetic said 77 = 65 + 12. Found by the build script's own self-check.
3. **A test that tested nothing.** Reverting `CAU-AM3`'s placement rule left the whole suite
   green, because nothing drove `pick_injections`. Found by mutation-testing, not by review.
   Five mutations were checked red before the suite was trusted.
4. **`/status` was stricter than the governing document**, requiring all 16 optional journey
   notes before reporting complete. A blank textarea never fires its save event, so
   "complete" was unreachable for an honest listener. The owner hit this having judged
   everything.
5. **The run brief was written in bash** (`VAR=value cmd`), which fails in cmd.exe. Neither
   env var was needed.
