# Execution log — the `TCR-` re-run, 2026-08-06 (night)

**Role: ACTIVE — retained reasoning.** **Owns no figures**
(`builder/analysis/2026-08-06-tcr-thin-catalogue-rerun/` does) and **states no status**
(`NEXT.md` does). Successor in the co-credit chain to
[`2026-08-06-tce-thin-catalogue-execution-log.md`](2026-08-06-tce-thin-catalogue-execution-log.md),
whose §7 (what a re-run must not repeat) this session executed against, item by item.

**No shipped code was touched** — nothing under `api/`, `frontend/` or `builder/src/`.

---

## §1. What this session did, and what it concluded

Re-ran the voided thin-catalogue probe under a **new** pre-registration (`TCR-`), per the
owner's Option A ruling. All gates passed on externally anchored thresholds, both arms
computed, and **nothing anywhere reads enriched — the licensed signals point the opposite
way.** The co-credit investigation closes with three mechanisms tried and none explaining
the owner's observed class. Nothing was adopted; no default changed.

## §2. Decisions taken, with reasoning

- **Gate anchors chosen by measured unambiguity, and live counts fetched before any band
  existed.** Unambiguity = exactly one exact-name match in a live MusicBrainz artist
  search, recorded in the committed `g1_anchors.json` with its fetch timestamp. The order
  (choose → fetch → band → commit → run) is §7 item 1 executed literally.
- **The zero-anchor guess was corrected by the fetch, which is the method proving itself:**
  Andrew VanWyngarden was selected as the zero-detection candidate and the live API
  returned 4 release-groups. Guessed, that number would have rebuilt the exact defect that
  voided `TCE-`. Alana Haim (unambiguous, live 0) took the zero cell; VanWyngarden became
  the small-nonzero cell, giving the gate a 0 / 4 / 37 / 59 / 584 magnitude ladder.
- **Leon Bridges and Khruangbin were kept as regression anchors and labelled as such** —
  their dump counts were already on the committed void-run record, so those cells could
  not surprise; the honest framing is in the prereg rather than discovered by a reader.
- **Tolerance ± max(2, ⌈5 %⌉), zero cell exact.** Eight days of editorial drift moves a
  catalogue by a few entries; a *broken* counter errs by structure (releases vs
  release-groups vs recordings), which is factors. Observed total drift across four orders
  of magnitude: one release-group (Radiohead 584 live / 583 dump).
- **Both Laura Lees demoted to reported run state** — the recorded MusicBrainz mis-filing
  contaminates them as ground truth (§7 item 2). Reported (0 and 16, both matching the
  void run), adjudicating nothing.
- **Ties resolved by exact expectation over a uniformly random ordering of the rank-10
  boundary block** (§7 item 3), in both arms — arm A's raw integer scores tie heavily too
  (17 duplicate scores in one 51-row list was the first file inspected). Chosen over a
  deterministic MBID tie-break because average rank was the committed §0.1 design; the
  expectation form makes it exact for the linear criteria and correctly propagates through
  the mid-p criteria as a mixture.
- **The runner reuses the void run's machinery deliberately** — the counter, existence
  pass, and phase ordering were already exercised; the new-code surface was confined to
  the anchored gate, the Laura Lee demotion, and the tie rule.
- **Adjudication: no pre-registered branch fires as written, and the consequence was taken
  anyway because every adjacent branch shares it.** `TCR-R3` required `C1` and `C3` both
  null; `C3` landed *beyond* null at depleted. `TCR-R4` read the primary; `C1` landed
  null. Rather than stretch a label post hoc, the results README records the gap and shows
  the consequence (closes, nothing adopted) is invariant across the reachable branches —
  with `TCR-C5` below its own null directly excluding the hidden-minority worry that made
  `R3` cautious.

## §3. Defects found in this session's OWN work — two

1. **The runner's first invocation crashed in phase 1** (`len()` on the
   `GraphStore.neighbours_of` generator — the void runner sorted first, which masked it).
   Before any gate value and before any outcome value; fixed with one `list()` call and
   recorded in the results README.
2. **The carried-forward branch table had a gap** — `C1` null with `C3`/`C4` depleted has
   no row — and this session carried it from `TCE-` without examining it, exactly the
   move the carrying was supposed to be safe for. Found by the result landing in it.
   Recorded, not patched post hoc; the next design fixes it at authoring time.

## §4. Gate outcomes

| Gate | Outcome |
|---|---|
| **`TCR-G1`** (anchored instrument validation) | **PASSED 5 of 5**, first and alone. Figures owned by the run directory. |
| **`TCR-G2`** (coverage via artist dump) | **PASSED** (0.99991). |
| **`TCR-G3`** (pinning, per arm) | **FIRED for arm B** — bars its `TCR-C1`/`C2` read, exactly as the carried amendment predicted; a finding about the drop filters, not a fault. Did not fire for arm A. |
| `TCR-C1`–`C5`, both arms | **Computed.** No enrichment anywhere; adjudication in §2. |

**Instrument verification beyond the gate:** the tie machinery was checked against
brute-force enumeration of all tie-block orderings over 200 random lists (0
disagreements), and the runner's band-drift assertion was shown to fire on a wrong band —
the instrument has been seen red, not only green.

## §5. Corrections to the prior record

- **`docs/README.md`'s row for the `TCE-` spec still opened "NOT YET EXECUTED"** — stale
  since the void run, surviving that session's own closeout audit. Corrected to VOID with
  pointers, original text retained struck-in-role.
- **Nothing else was overturned.** The `TCE-` void record stands untouched, as ruled.

## §6. Operational measurements with no other home

- First (crashed) invocation paid a **6.6-minute cold archive scan**; the successful run's
  identical scan took **10 seconds** on the warm OS file cache, and the whole run
  **~4.4 min** including both fresh dump passes. Cold, budget ~11 min.
- **Standing context layer (D6): delta zero on both halves**, evidenced by
  `git diff --name-only 13e54f2..HEAD -- CLAUDE.md .claude/` returning empty and no file
  under `memory/` being written this session.

## §7. What is open

- **The same-name population probe (Option C) is now UNBLOCKED**: the owner deferred it
  "until after the re-run", and the re-run has happened. Whether and when to run it is
  **his**. The eyeball read left the question exactly as open as it found it.
- **B2** (rescale alternatives) and the **duplicate-artwork detector** — untouched,
  conditions not due, still owned by the earlier log's §6.
- **`ULF-3`** re-tested rather than copied: **unchanged, still HALF-DUE** — the era-pinned
  probes still name the old flags and all three flags remain live in `BuilderConfig`
  (checked against `builder/analysis/` and `config.py` this closeout).
