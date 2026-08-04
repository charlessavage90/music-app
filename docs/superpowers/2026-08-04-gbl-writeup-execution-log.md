# GBL write-up — execution log

**Session role:** the further fresh session that reads `gbl_result.json` and writes it up —
the `CRE-` Stage-3 rule (the reader of results did not run them), named as a seam in the
harness log §8 and the runner log §7. **This session did not run the listen and had not seen
any journey, verdict or figure before it opened.**

**Date:** 2026-08-04 (night). **Branch:** `gentle-arm-blind-listen`. **Owns no figures** —
they live in `findings/2026-08-04-gentle-arm-blind-listen-results.md` and the raw JSONs.

---

## 1. What the session found on arrival

`NEXT.md`'s top block was **stale in a way that inverted the state**: it said "The listen has
NOT been run; no journey exists on either arm," while four commits on the branch carried the
verdicts, the result, the owner's pre-result notes and the runner's log. `NEXT.md`'s own
maintenance rule resolves this — the fresher of {handoff, execution log} wins and `NEXT.md` is
then stale, to be fixed rather than worked around. It was fixed here.

This was **not a defect of the runner session**. It left `NEXT.md`, `TEST-QUEUE.md` and the
`gbl_page_data.json` commit-or-ignore call alone deliberately (runner log §6), because all
three need to know what the listen was *for* — precisely the context the blinding removed.
The gap is structural: **a blind runner cannot close out its own work**, so the state is
guaranteed to be stale between the listen and the write-up. Worth carrying into any future
blind protocol.

Also on arrival: **four commits unpushed**. The listen's entire output — a one-shot,
unrepeatable resource — existed only in this working tree. Pushed before any other work.

## 2. Two findings that came from reading the verdicts, not the result

Both came out of the prescribed reading order (verdicts → owner notes → result), and neither
is visible in `gbl_result.json` alone.

**2.1 The primary read tallied an unlabelled pick.** The sixteen deep rows that decide the
outcome were presented as bare left/right/no-preference radios under a heading giving only the
number of presses. **Neither spec §4 nor `gbl_page.html` attaches a question to them** — the
two frozen questions (`GBL-Q1` novelty, `GBL-Q2` coherence) are asked once per pair, at the
end. Reading the owner's per-row notes, he answered the rows almost entirely on coherence
("I think R is the more coherent journey", "L strongly more coherent", "I have to choose L on
coherence"). So the outcome the experiment was built to detect — novelty — was captured only
by the question carrying no threshold, while the read with the threshold measured the other
axis. Recorded in the findings note §2.2 and §6.1 as an inference from the notes, labelled as
such, because the design does not state it.

**2.2 The undecided rows were mostly clip-blocked, not indifferent.** Five of the seven
no-preference deep rows name a clip defect as the reason in the owner's own words at the time;
only two record genuine indifference, both on the pair he flagged himself as badly chosen.
The spec's rule — "ignore clip failures unless they differ by arm" — protects the *direction*
of the comparison and not its *power*. A symmetric defect is unbiased, not harmless. Findings
note §1.3, §2.3, §6.2.

**2.3 Verification, per `session-start`.** The tally was re-derived independently from
`gbl_verdicts.json` against the unsealed mapping before the result was opened: deep rows 6–3
(margin 3), d0 anchor 6–0, `GBL-Q1` 8–0, `GBL-Q2` 3–1–4. Agrees with `gbl_unblind.py` in
every cell. The runner's "32 of 32 rows" claim was also checked against `gbl_page.py:39-47`:
a slot is pair×depth *plus* one claims slot, so 8 × (3 + 1) = 32, and the file holds exactly
24 depth picks and 8 claims entries. Complete.

## 3. Decisions taken, with reasoning

1. **`gbl_page_data.json` is committed.** It carries no arm identity and no metrics — only
   pair keys, endpoint names, depth and the L/R artist lists; checked before deciding. It is
   the only record of the stimulus as presented, the verdicts are uninterpretable without it,
   and the findings note quotes artist names from it. The sealed mapping stays where it is,
   under the gitignored `.superpowers/`.
2. **No bar is proposed for `GBL-Q1`.** The 8–0 novelty sweep is the cleanest signal in the
   listen and it is reported prominently — but spec §5 fixed a threshold only for the deep-row
   tally. Choosing one now, knowing the result, is the thing pre-registration exists to
   prevent. The findings note states this as the reason its §4 option D is unavailable, rather
   than omitting the option.
3. **The null is reported as the result, not softened.** §2.2 and §2.3 explain *why* the
   instrument returned a null, and the note says plainly that this does not change the null:
   §5's run-once rule binds, and the reasoning is offered as input to what to do next rather
   than as a challenge to the verdict.
4. **The d0 anchor is reported and kept out of the read.** §5 excludes it and its clause is
   written one-directionally (it anticipates a strong *V0* d0 preference); the observed 6–0 ran
   the other way. By the same sentence it neither vetoes nor rescues, so it is reported as the
   most interesting *unspent* observation and explicitly not counted.
5. **No single-factor attribution anywhere.** Spec §2 bars it. The one exception taken is the
   one the spec grants itself: at d0 the ramp is inert by construction, so the anchor speaks to
   the graph swap **as a whole** — never data set versus supply rule separately.

## 4. Bookkeeping discharged

What the blind runner correctly declined, closed here: `NEXT.md`'s top block rewritten (with
the superseded block's "the listen is unspent" struck in place rather than edited away); a
`TEST-QUEUE.md` entry written in plain language; three doc-map rows added and the spec's row
updated to EXECUTED; `gbl_page_data.json` committed.

**Not discharged, and still open — neither is `GBL-`:** the owner's 2026-08-04
no-commercialization ruling remains in memory only and belongs in `PRODUCT-REQUIREMENTS.md`;
and the eight 2026-07-22→27 `TEST-QUEUE.md` entries remain `QUEUED` and unruled-on, flagged
now at four consecutive closeouts. Both are the owner's, and folding either into a `GBL-`
commit would bury it.
