# Retained execution log — the un-listenable class (`ULC-`), 2026-08-05

**Role: RETAINED EXECUTION LOG** for the session that designed, ran and wrote up `ULC-`.
**Owns no figures and no status.** Figures:
[`findings/2026-08-05-unlistenable-class-results.md`](findings/2026-08-05-unlistenable-class-results.md).
Status: [`NEXT.md`](NEXT.md). Governing document:
[`specs/2026-08-05-unlistenable-class-preregistration.md`](specs/2026-08-05-unlistenable-class-preregistration.md).

Decisions and reasoning only — not what each step did, which git has.

---

## 1. Decisions taken, with reasoning

**1.1 The census sets no bar; only the comparisons carry fixed numbers.** The owner's instinct
was that this is a descriptive test. Adopted, with one carve-out: counting needs no bar, a
*comparison* does — and he already had a directional preference for the rebuilt graph, which is
the condition under which an unfixed threshold gets chosen to fit. So `ULC-C1` is a distribution,
and only `ULC-G1` and `ULC-R1` carry numbers. The precedent is `ctc_census.py` and `fcf_census.py`,
both of which open *"DIAGNOSTIC ONLY … sets no bar."*

**1.2 The predicate is derived from the definition, not fitted to the cases.** The first draft
fitted a cut to the known artists. With a validation set this small that is circular and teaches
nothing. Fixing the predicate in advance means it can **fail**, which converts a thin set from a
weakness into a real test. Recorded because the reflex to fit was strong and the draft that did it
was already written.

**1.3 `ULC-P5` is measured but has no baseline.** The artifact the site serves carries neither
drop flag — it predates the wiring. It cannot be compared with any cell, and it is the only
population a user has ever seen. Reporting it alone, with `ULC-B4` barring its use in a
cross-archive sentence, was the only way to have both facts without one contaminating the other.

**1.4 The unknown-track ambiguity was measured rather than adjudicated.** Two of the owner's own
statements pull opposite ways: his asymmetry ruling favours treating unknown as insubstantial, his
warning about MusicBrainz incompleteness favours the opposite. Rather than pick, both readings
were computed and the affected count reported. **It came out ~0.5 % of nodes and the two readings
differ by nine artists, so the question never needed answering.** Generalisable: when two
principles conflict and the conflict is cheap to size, size it first.

**1.5 Merge, not rebase, when folding in `main`.** This track's integrity rests on commit
timestamps proving each design decision preceded the result it governs. Rebase rewrites commits.
The merge was clean and cost nothing.

**1.6 The statistic was NOT changed after seeing that it could not see the effect.** See §3.

---

## 2. Defects found in the design itself — five, all before the stage they affected

Each became an amendment, committed before the stage ran.

| | What was wrong | Consequence had it stood |
|---|---|---|
| `ULC-AM1` | — (a disclosure, not a defect) | — |
| `ULC-AM2` | §1.1's worked counterexample was no longer clean: the owner re-read Keith Scott's release as one track and moved him toward the class | §2.2a's whole interpretation of a `predicate_wrong` result was wrong, and is superseded there |
| `ULC-AM3` | `ULC-OG3` was unasked: nothing said whether one track counts | The predicate would have been chosen by me on a question that is the owner's |
| **`ULC-AM4`** | **`ULC-V1` contained Four Tet**, whose can't-tell was an identity doubt, not an availability one | **The gate would have been measured against an artist no correct predicate could catch** |
| `ULC-AM5` | `ULC-R1`'s trigger named no depths | Three defensible poolings available *after* seeing results |

**`ULC-AM4` is the one worth carrying forward.** The findings note it derives from says "eight of
the nine can't-tells" without naming which nine — so the target set had to be reconstructed by
reading the owner's notes, and one of the seven was a different kind of can't-tell entirely.
**A count in prose is not a set.** When a later track needs the members rather than the number,
the count cannot supply them and reconstructing is where the error enters.

**On `ULC-AM4`'s bar: the absolute count was held at 5, not rescaled.** Dropping an artist the
predicate could never catch makes its job easier, so keeping the *rate* would have loosened the
bar under cover of a correction. Holding the count moved it from 5-of-7 to 5-of-6.

---

## 3. The design defect that survived to the result, and was not patched

**`ULC-R1`'s statistic is a paired median. The exposure distribution is zero-inflated.** Most rows
are zero on both sides and a handful carry everything, so the median difference is 0.00 pp — it
would have read `no_detectable_difference` for a gap between 0 % and 15 %.

**It was left alone.** Switching to the mean after seeing which statistic gives the interesting
answer is the fishing the whole design exists to prevent, and it would have devalued every other
figure in the track. Recorded in the findings note §1.3c and in the pre-registration as unpatched.

**Two things that make this cheaper than it looks.** The run state was independently unmet
(95/96), so no branch could fire regardless — and a looser reading of §4 that would have rescued
the complete comparison was **declined**, because it would have been adopted after seeing which
comparison it rescued.

**The lesson is not "pick a better statistic."** It is that a pre-registered statistic encodes an
assumption about the *shape* of the effect, and nothing in the design asked what shape was
expected. A one-line "what distribution do we expect, and can this statistic see it?" would have
caught it.

---

## 4. Gate outcomes

| Gate | Outcome |
|---|---|
| **`ULC-G1`** | **`separable`** — both clauses met, with margin on each (figures: results §1.2) |
| **`ULC-R1`** | **NOT TAKEN.** Run state 95/96, and §3's statistic could not have seen the effect. No branch assigned |
| Census determinism | **PASS** — full re-run, every figure identical |
| Artifact checksums | **PASS** — all five verified before reading |
| `ULC-D1 ⊆ ULC-D2` | **PASS** — asserted in code |

**`ULC-S2`'s missing slot:** `B-S0` does not reach depth 20 on Led Zeppelin → Guster. Anticipated
in kind — the eight pairs were approved against `B-S1` and the adopted graph, and three of the four
arms were never checked for reachability.

---

## 5. Corrections to the prior record

**`ULC-AM0` — `findings/2026-08-05-coherence-audit-results.md` §6's "22 of 23" includes the
audit's own 12 planted controls in the denominator.** Correct figures: **10 of 11**. The
conclusion stands at 90.9 % rather than 95.7 %; the evidence base is half the size it appears. **No
`CAU-` criterion is affected** — `cau_score.py:62-68` excludes controls correctly, and the defect
is confined to that one hand-written check. Reproducible via `ulc_validation.py`.

**It is now landed in that note**, as a callout at the head of its §6 with the original text left
standing beneath. **This session first declined to make that edit and was wrong to** — the reason
given was that the `CAU-` note owns its own figures, which is an *authority* argument, and
`closeout` B1 says plainly that authority is never grounds to escalate a finding you have the
facts to fix. The documentation audit caught it, on exactly the right ground: a reader standing in
the `CAU-` note had no way to know the figure was disputed. **The instinct was deference and the
effect was leaving a known-wrong figure reading as settled** — worth recording, because deference
is the disguise that failure wears.

**Two claims of mine, corrected in conversation and recorded so they are not re-derived:**

- I inferred the Discogs exemption was a *solo* release. It is not: the census tests presence in
  `<artists>`, sole or not. The owner's spot check found no solo releases and both are true at
  once — the filter was never asking for solo.
- I claimed Discogs main-artist credit is a poor proxy for having music of one's own *"in either
  direction"*. Only one direction is supported. Max Martin does not demonstrate the other: he has
  no record of his own to play, so flagging him is correct. The claim conflated *creative output*
  with *something to listen to under this name*.

**A claim NOT retracted:** DSP links are unreliable in **both** directions — a missing link does
not mean absence from the platform (the owner's correction), and a present link does not mean
presence (his broken McVie Spotify link). Different signal, both halves demonstrated.

---

## 6. Operational measurements with no other home

| | |
|---|---|
| Census, three dump passes over ~52 GiB | **46.6 min** (release-group 2.3, release 42.1, artist 2.2) |
| Discogs **masters** scan, 2.58 M entries | **36 s** (3.1 GiB) |
| Discogs **releases** scan, 19.19 M entries | **19.2 min** (61.6 GiB) |
| Stage-2 exposure, 672 journeys over 4 arms | **< 2 min** |
| New collision sweep (all refs) vs old working-directory grep | **0.25 s** vs minutes |

**The masters/releases ratio is the reusable fact — 20× smaller, 32× faster.** The owner raised
it and it did answer the question asked.

> **But not as a replacement, and my first write-up of this was wrong.** I recorded it as "the
> default first instrument for any Discogs presence check." **`NEXT.md`'s standing deferral on the
> masters export already warned that masters *lose* tail coverage — "single-version releases often
> have no master" — and my own data confirms it on the worst possible case.** Joey Kramer has **0
> masters and 1 sole-credited release**. A masters-only check reports that he has no sole Discogs
> credit, which is exactly backwards, and it is *his* sole credit — a drum sample library — that
> proves "require sole credit" is an insufficient fix.
>
> **Correct rule: masters first as a cheap screen, releases before any conclusion that turns on an
> artist having nothing.** The coverage loss falls precisely on the tail this class lives in, so
> the instrument is at its weakest exactly where the question is hardest. Recorded because the
> deferral had predicted this and I had to be shown it by my own output.

**A cost paid for a persistence mistake:** the census first wrote only rates, not membership, so
Stage 2's inputs required a **full 46-minute re-run**. It bought the determinism check, so it was
not wasted — but the general rule is to persist the sets, not the summary. `ULC-F2` is the same
mistake one level up, in the shared census.

---

## 7. Killed and declined

- **A second predicate after a `predicate_wrong` result** — barred in the pre-registration before
  running. Not killed by evidence; killed by design, so that a failure produces a finding rather
  than a search.
- **The looser reading of prereg §4** (comparisons fire independently, so `A4`−`A3` is complete) —
  declined, §3.
- **Fitting the reference cut to the calibration set** — replaced by `ULC-D2`, §1.2.
- **`ULC-B3`'s false-positive measurement** — declined by design, not deferred. `ULC-V1` can show
  the predicate catches what it should and never that it spares what it should. Any rule needs its
  own pre-registration.

---

## 8. Standing-layer delta (D6)

| Layer | Unit | Total | Delta this track |
|---|---|---|---|
| Unconditional | characters | **45,333** | **0** |
| Conditional | lines | **2,417** | **0** |

Measured against `C:\Users\charl\.claude\projects\C--dev-music-app\memory\`, the directory this
session's own context names. **This track added nothing to either layer** — no `CLAUDE.md` edit, no
memory file, no skill or agent change. Both totals are inherited from the maintenance session that
landed immediately before this closeout (PR #79) and are recorded here as the new baseline, not as
this track's doing.
