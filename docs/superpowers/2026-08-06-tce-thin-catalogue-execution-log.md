# Execution log — the Laura Lee closure and the `TCE-` void run, 2026-08-06 (night)

**Role: ACTIVE — retained reasoning.** **Owns no figures** (the three
`builder/analysis/2026-08-06-{laura-lee-closure,tce-c1-statistic-behaviour,tce-thin-catalogue}/`
directories do) and **states no status** (`NEXT.md` does). Successor in the co-credit chain to
[`2026-08-06-cocredit-investigation-execution-log.md`](2026-08-06-cocredit-investigation-execution-log.md),
whose §6 item 1 this session partially discharged in place.

**No shipped code was touched** — nothing under `api/`, `frontend/` or `builder/src/`.

---

## §0. What this session did, and what it concluded

Picked up the open Laura Lee puzzle on the owner's instruction. **Closed it for its worked
case, left its population half open, pre-registered a third mechanism (`TCE-`), amended that
pre-registration twice before running it, ran it, and it VOIDED on its own instrument-validation
gate.** Nothing was adopted; no default changed.

## §1. Decisions taken, with reasoning

- **Investigated the motivating case before designing anything.** Two free archive reads and
  two MusicBrainz queries settled a hypothesis that had been "live but weakened" for a day.
  The cheapest decisive test was already sitting in the archive.
- **Rewrote `TCE-`'s core comparison to be within-list and rank-based.** The observation that
  motivated the probe (2 recordings scoring 214 against 288 scoring 65) is a **cross-artist
  score comparison**, which nothing licenses. `RCC-AM1` had already paid for this lesson;
  applying it cost the probe its most striking evidence and was still right.
- **Rewrote `§4.1`'s plain sentence rather than restricting the population by fame**
  (`TCE-AM2` era, recorded in `TCE-AM1`). Deciding fact: **arm A's archive carries no fame
  figure**, so a fame criterion is not computable in the isolating baseline and would add a
  third differing column. Naming fame as the concentrating variable would also pre-empt what
  `TCE-C5` exists to measure.
- **Kept `TCE-C1` when the derivation condemned it.** Re-banded and still reported. Removing a
  criterion after an inconvenient result — even a pre-outcome one — is what the discipline
  exists to prevent.
- **Did not correct `TCE-G1`'s threshold after it fired.** A bar moved after seeing the value
  that failed it is not a bar. Escalated to the owner on `MSW-G3`'s precedent.

## §2. Defects found in this session's OWN designs — four, all before any outcome

1. **The effect-size justification used the wrong base rate.** `+0.10` was argued from the
   census's 24.7 % class share. That class is "no *sole-credited substantial* release group";
   `TCE-`'s `thin` is stricter, so its population is a **subset** and 24.7 % is only an upper
   bound. Fixed before commit; the base rate became run state.
2. **`TCE-C1` could be a mathematical CONSTANT** (`TCE-AM1`). Below a base rate of roughly
   0.007–0.023 the census median is exactly 0 at every effect size including a total one.
3. **`TCE-C1` was blind to a concentrated effect** (`TCE-AM1`) — `ULC-R1`'s recorded defect
   reproducing inside a document whose `§4.3` asserted it was *deliberately not repeated*.
   Writing the sentence did not make it true: recording a distribution helps nothing when no
   branch reads it. **This is the most important defect of the four**, because `R3` closes the
   whole investigation and a real effect in a fifth of the census reads as `null`.
4. **`TCE-G2` was unsatisfiable as written.** It required neighbours to "resolve to a count" in
   the release-group dump — but an artist with zero release-groups is **absent** from that
   dump, so it cannot separate "no releases" from "MBID no longer exists". Not hypothetical:
   this archive carries deleted MBIDs. Reimplemented against the **artist** dump before the
   run. That pass never executed, the gate having fired first.

**Defect 3 was found by a dispatched derivation and then re-derived independently before the
amendment was written.** Both the pinning threshold and the blindness reproduce exactly.

## §3. Gate outcomes

| Gate | Outcome |
|---|---|
| **`TCE-G1`** (instrument validation) | **FAILED** — 1 of 4 cells. Probe VOID. Figures owned by `2026-08-06-tce-thin-catalogue/`. |
| `TCE-G2` (coverage) | **Never reached.** |
| `TCE-G3` (pinning, per arm) | **Never reached.** |
| `TCE-C1`–`C5`, both arms | **Never computed.** No branch fired; none may be inferred. |

**The gate did its job.** It stopped the run at phase 3 of 7, before any run-state quantity and
before any `x_R`. **The instrument was subsequently shown correct** — the dump counter agrees
exactly with the live MusicBrainz API — so the failure was a threshold set by reasoning from a
*recording* count without checking what it implies for *release-groups*.

## §4. Corrections to the prior record

- **`§6` item 1 of the previous log is PARTIALLY discharged**, struck in place there rather
  than here: worked case closed, population question open. **It must not be recorded as
  closed.**
- **One truncation artefact corrected:** Laura Lee's absence from Khruangbin's list is the
  100-entry cap (their list's median score exceeds her edge), not an asymmetry. Recorded as a
  barred read in the closure so it is not cited as a finding.
- **Nothing authored by another session was overturned.**

## §5. Operational measurements with no other home

- **Full parse of the 18 GB release-group dump: ~2.2 min** (4,431,141 records). The 17 GB
  artist dump is comparable. **No optimisation was needed** and none should be added — a
  benchmark preceded the decision.
- **Scanning the 75,000-file archive took ~7 min**, dominating the run. It is the cost to
  beat if this is re-run often.
- **Standing context layer (D6), measured this session:** unconditional **45,902 characters**,
  conditional **2,465 lines**. **Delta zero on both**, verified from
  `git diff --name-only 8d2d76f..HEAD -- CLAUDE.md .claude/`, which is empty — no `CLAUDE.md`,
  `MEMORY.md`, skill description or agent description was touched.

  > **⚠ Both numbers were WRITTEN BEFORE THEY WERE MEASURED and both were wrong** (21,458 and
  > 4,286). Caught in the same closeout that produced them, by running the commands. Recorded
  > rather than quietly fixed, because it is this project's named failure class — confident
  > prose beside correct work — occurring in the log whose purpose is to be trusted later. **The
  > zero-delta claim was independently true and is now evidenced by the diff rather than by
  > assertion.**

## §6. What is open

**Open items and their success conditions are owned by the previous log's §6**, as amended in
place. This session changed the state of item 1 only. **B2** and the **duplicate-artwork
detector** are untouched.

**New and carried by `NEXT.md`:** the owner's ruling that `TCE-` be re-run under a **new**
pre-registration with externally anchored gate thresholds, by a fresh session, and that the
same-name population probe waits until after it.

## §7. What a re-run must not repeat

Recorded here because it is the reasoning, not the status:

1. **Anchor gate thresholds on measured values, not inferred ones.** Three of four `TCE-G1`
   cells were loose enough to pass almost anything (`≥ 5`); the fourth was tight and
   unanchored. That distribution of strictness is the defect, not the one number.
2. **Do not anchor a gate on artists with a known same-name problem.** Cell 1 passed *because*
   of a MusicBrainz mis-filing — the ground truth was contaminated.
3. **Resolve rank-10 boundary ties explicitly.** `20.4 %` of arm B reference artists have one
   (figure owned by `2026-08-06-tce-thin-catalogue/`), so sort order silently decides a fifth
   of the arm B top-tens. `§0.1` predicted this and the run confirmed the size.
4. **`TCE-AM1`'s three mitigations remain owed** and were never reached — including the eyeball
   read of the top contributors, which is what distinguishes a real effect from junk MBIDs
   inflating a mean.
