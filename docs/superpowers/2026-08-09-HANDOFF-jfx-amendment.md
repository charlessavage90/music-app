# Handoff — `JFX-AM1` committed, arms not run, 2026-08-09

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-09-HANDOFF-cex-task11.md`](2026-08-09-HANDOFF-cex-task11.md) on next actions. It
does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A SEAM handoff, and a deliberate one.** The governing document was materially amended and
the successor is meant to read it cold — which `CLAUDE.md` names as a seam in its own right.
The degradation tell did **not** fire; this session stopped because the amendment is the
seam, not because it was faltering.

Reasoning: [`2026-08-09-jfx-prereg-amendment-execution-log.md`](2026-08-09-jfx-prereg-amendment-execution-log.md).
Figures: `builder/analysis/2026-08-09-jfx-prereg-critique/README.md` — cited, never restated.
Branch `crawl-extension-design`, **PR #91**, commits `7c58af6` and the closeout commit above it.

---

## Start here

1. **Read [`specs/2026-08-09-journey-fame-exposure-preregistration.md`](specs/2026-08-09-journey-fame-exposure-preregistration.md)
   — `JFX-AM1` FIRST, then §0.1, then §2/§3/§4.** The amendment changes all three of those
   and governs where they disagree.
2. **No arm has run.** Nothing is half-executed and nothing is blocked.
3. **The next piece of work is the routing harness**, which does not exist. `jfx_stats.py`
   supplies the statistical primitives and is tested; nothing consumes it yet.

## What is done

`JFX-AM1`, twelve clauses, committed before any arm ran. The reachability measurement that
settles `AM1.1`. The §1 build script, which had never been written. The statistics module and
20 tests. A forward correction in `PRODUCT-REQUIREMENTS.md` §8. Two doc-map rows.

**Nothing adopted, no default flipped, no artifact built, no pair routed. The live site is
untouched and was never in scope.**

## Documents that are now wrong, and in which direction

- **Anything reading `PRODUCT-REQUIREMENTS.md` §8's "unachievable on famous-to-famous pairs"
  as a present-tense fact.** The structural precondition no longer holds; the forward
  correction is inline beneath it.
- **Anything treating the `JFX-` spec's §2/§3/§4 as authoritative without `JFX-AM1`.**
- **Anything describing the `MSW-` adoption's grounds from the `MSW-` records alone** — they
  omit a reason the owner actually held. Those records are frozen and were not edited.

## Claims that must NOT be reverted by a well-meaning editor

- **`DD-F1` is NOT overturned.** It survives in **popularity** currency at the very top and
  fails to transfer to **fame**. Both halves travel together; collapsing either direction is
  the currency error that caused this in the first place.
- **The famous-to-famous measurement is STRUCTURE, not ROUTING.** It licenses "famous
  endpoints *can* descend", never "journeys *do*".
- **The 2026-07-29 defect ruling is OPEN.** The precondition changing is not the ruling
  closing. That is the owner's.
- **The `MSW-` switch addressing famous-to-famous was BY DESIGN**, owner statement — not
  incidental. An earlier draft of this said incidental and he corrected it.
- **`JFX-G1b` stays at 67%.** Unchanged deliberately; `AM1.2` and `AM1.9` record why, and
  `AM1.9` measures the front-loading that makes it slightly lenient.
- **`JFX-C2` still has no threshold**, and `AM1.7` did **not** give it one — the effect sizes
  added there are for `C6` and `C7`, which fire branches. `C2` fires none.
- **`AM1.10`'s negligibility finding.** A shared RNG does **not** materially change intervals
  at 10,000 replicates. The clause corrects an overstatement this session made; do not
  restore the stronger claim.
- **Everything on the previous handoff's "must not be reverted" list still stands in full.**

## Already updated — do not redo

The spec (amended), `PRODUCT-REQUIREMENTS.md` §8, `docs/README.md` (JFX spec row rewritten,
new row for the critique directory), the previous handoff's role line, and this log.
**`TEST-QUEUE.md` was deliberately not written to** — nothing changed that the owner can
press.

## What I know that is not in the durable record

**Nothing of substance.** Everything went into the execution log, including the two shell
traps in its §8 and the self-correction in its §4.

One thing worth repeating because it will bite the successor: **`GraphStore` throws away raw
fame values at load.** The harness must read `fame_lb` from the APG1 metadata blob.
`jfx_s1_reachability.py` has a working parser for it.

## Anything in flight

**Nothing.** No background jobs, no subagents beyond this closeout's `doc-auditor`, **no
listeners: ports 8000, 5173 and 5174 swept and free.** No dev server was started this session
and none was left behind — nothing queued needs one.

## What I would do if I were continuing

1. **Build the routing harness**, to `AM1.3`'s named instrument: `find_journey` semantics,
   `cre_ladder.victim_key` press selection, the production ruler frame. **Re-verify
   `CRE-G1(a)`'s byte-identity against today's `pathfinding.py` first** — the mirror was
   verified 2026-08-03 and the seventh cost term landed 2026-08-05.
2. **Build the diagnostic artifact** (~17 min) with
   `jfx_build_diagnostic.py`, passing `--algorithm alg-b` explicitly.
3. **Materialise the pair set** — first 100 per stratum from the committed candidates, in
   committed order, surviving the intersection. **Report the skipped count**; a non-trivial
   number means the extension *removed* artists.
4. **Report `JFX-G1` first**, then `C6` and `C7`, then the gradients. §4's reads are not
   licensed until both validity checks exist.
5. **Fold `CEX-M1`'s fix into the same artifact** — post-cap saturation, where it is not
   vacuous.

## Open, and not this session's

- **`CEX-F1`**, **`CEXR-6`'s `load_deezer_ids` half**, **`CEX-R3`** (search), **`CLIP-1`**,
  **`FE-SNYK-1`** — unchanged, conditions in the `CEX-` Task 11 log §8.
- **`SEL-R1`–`R4`** — still deferred to a dedicated maintenance session, owner's instruction.
- **The 2026-07-29 famous-to-famous defect ruling** — now has changed evidence under it and
  is the owner's to close or keep.
- **PR #92 is MERGED**; the landing-dot fix is on `main` but **not deployed**.
