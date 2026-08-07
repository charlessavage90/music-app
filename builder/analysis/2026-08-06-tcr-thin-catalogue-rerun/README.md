# `TCR-` — COMPUTED. No enrichment in either arm; arm A's supplements read depleted.

**Role: ACTIVE — results of record for the `TCR-` probe.** Governing document:
`docs/superpowers/specs/2026-08-06-thin-catalogue-rerun-preregistration.md`, committed
`4918eea` **with its anchors and this runner, before the dump counter ran against any gate
anchor and before any outcome value existed.** Predecessor: the VOID `TCE-` run
(`../2026-08-06-tce-thin-catalogue/`), whose record stands untouched and from which **no
outcome value was inherited — none existed there to inherit.**

**This directory OWNS its figures.** Raw `tcr_result.json`, run state `tcr_runstate.json`,
contributor dump `tcr_eyeball_top20.json`, runner `tcr_run.py`, anchors `g1_anchors.json`.
Cite it; never restate.

---

## 1. Gates — all passed, and the anchored design did its job

**`TCR-G1` (does the catalogue counter return the externally checked answer for five
unambiguous artists?): 5 of 5 cells PASS**, evaluated first and alone, bands fixed from
live MusicBrainz values fetched before the pre-registration was committed:

| Cell | Artist | Live (2026-08-06) | Required band | **Dump (2026-07-29)** | |
|---|---|---|---|---|---|
| zero-detection | Alana Haim | 0 | == 0 | **0** | PASS |
| small nonzero | Andrew VanWyngarden | 4 | 2–6 | **4** | PASS |
| moderate | Leon Bridges | 37 | 35–39 | **37** | PASS |
| moderate | Khruangbin | 59 | 56–62 | **59** | PASS |
| large | Radiohead | 584 | 554–614 | **583** | PASS |

Total observed live↔dump drift across five artists spanning four orders of magnitude: **one
release-group** (Radiohead). The anchor-choice lesson is on the record in the prereg:
Andrew VanWyngarden was *chosen as a zero candidate* and the live fetch returned 4 — the
guessed-threshold defect class, caught by measuring before banding.

**Both Laura Lees, reported as run state, adjudicating nothing** (demoted per prereg §3, a
known MusicBrainz mis-filing contaminating them as ground truth): Khruangbin member **0**,
soul singer **16** — both identical to the void run's measurements.

**`TCR-G2` (do the dump and the archive describe the same population?): PASS** — coverage
**0.99991** over 3,819,306 arm-A neighbour slots (basis: presence in the artist dump);
4 of 45,693 arm-A reference artists fell below the 30-entry floor after excluding
unresolved neighbours.

## 2. Run state, per arm — computed and written to disk before any placement was read

| | Arm A (raw archive) | Arm B (adopted graph) |
|---|---|---|
| Reference artists | 45,689 | 19,485 |
| Thin base rate | 0.0790 | 0.00564 |
| `T_R = 0` share (`TCR-G3`) | 0.0841 | **0.8541 → BARS the `TCR-C1` read** |
| Attainable ceiling `C` | 0.5000 | 0.0000 (also `no_resolution`) |
| `TCR-C5` exact null | 0.0356 | 0.0016 |
| Median list length | 100 | 48 |
| Rank-10 boundary ties (post-exclusion) | 11,650 (25.5 %) | 3,977 (**20.4 %** — matches the void run's structural figure exactly) |

**`TCR-G3` fired for arm B exactly as the carried-forward amendment predicted**: 85 % of
arm B reference artists have no thin neighbour anywhere in their list, so the census median
there is a mathematical constant and no `TCR-C1`/`TCR-C2` read is licensed — **reported as
`no_read_licensed`, never as `null`. This is a finding about the drop filters, not a broken
probe**: the shipped map's thin base rate is 14× lower than the raw feed's (0.56 % vs
7.9 %), because the filters remove artists with nothing of their own to play.

All boundary ties were resolved by the §0.1 exact average-rank rule (expectation over a
uniformly random ordering of the tie block), in both arms — one list in four/five has one,
so this was load-bearing, not decoration.

## 3. Outcomes

| | Arm A | Arm B |
|---|---|---|
| **`TCR-C1`** (median `Δ_R`; do thin artists crowd the top ten of the same artist's list?) | **−0.0333 → `null`** (band ±0.125 = ±0.25·C) | `no_read_licensed` (`TCR-G3`) |
| **`TCR-C3`** (mean mid-p vs own-list reshuffle; null exactly 0.500) | **0.4185 → `depleted`** (≤ 0.48) | **0.4896 → `null`** |
| **`TCR-C4`** (thin in top-ten slots vs chance; null exactly 1.000) | **0.716 → `depleted`** (< 0.8) | **0.567 → `depleted`** |
| **`TCR-C5`** (share with top tens too crowded to be luck, vs computed null) | 0.0217 vs null 0.0356 → **ratio 0.61, not concentrated** | 0.0011 vs null 0.0016 → **ratio 0.67, not concentrated** |
| `Δ_R` distribution | mean −0.026, p10 −0.114, p90 +0.078, 21.8 % positive | mean −0.003, 85.6 % exactly zero |
| Descriptive gradient (no read) | medians −0.044 / −0.054 / −0.078 / −0.100 at thin ≤ 1/2/5/10 | 0.000 / −0.025 / −0.075 / −0.150 |

**Every signal that is licensed points the same direction: thin artists sit *lower* in
similar-lists than that same list's own composition predicts, not higher.** Nothing in
either arm reads enriched, and `TCR-C5` sits *below* its own null in both arms — there is
no hidden minority of crowded top-tens; there are *fewer* than chance would give.

## 4. Adjudication — which pre-registered branch fires

- **`TCR-R1` / `TCR-R2`** (enrichment branches): **do not fire.** Nothing is enriched
  anywhere.
- **`TCR-R3`** (null in arm A; closes the investigation): **does not fire as written.** It
  requires `TCR-C1` AND `TCR-C3` both null in arm A, and `TCR-C3` landed *beyond* null, at
  `depleted`.
- **`TCR-R4`** (depleted in arm A): **does not fire as written** either — carried from
  `TCE-`, it reads the primary outcome, and `TCR-C1` landed `null`, not `depleted`.

**So the branch table has a gap this run exposed — `C1` null with `C3`/`C4` depleted — and
that is a defect of the carried-forward branch table, recorded here rather than patched
after the result.** What remains licensed without any post-hoc assignment: **the two
branches adjacent to the measured result (`TCR-R3`, `TCR-R4`) carry the identical
consequence** — the investigation closes and nothing is adopted — and the condition that
made `TCR-R3` cautious (a null median hiding a concentrated minority effect) is directly
excluded by `TCR-C5` reading *below* its null. The consequence is therefore licensed even
though no single label is: **the thin-catalogue hypothesis is unsupported, the measured
direction is the opposite one (as the prereg's §0 confound predicted), and no evidence here
says users meet artificially strong thin-artist links.** The label gap changes no decision;
it is recorded for the next design to fix at authoring time.

**Three mechanisms have now been tried against the owner's observed class — band membership
(`CCR-`, null and instrument-limited), shared recording credits (`RCC-`, null and
instrument-validated), thin catalogues (`TCR-`, unsupported with the direction opposite) —
and none explains it.** The honest statement remains: we do not know what produces the
class he saw.

## 5. The eyeball read (mitigation 2) — and the pre-registered condition did NOT obtain

The top-20 `TCR-C3` contributors in each arm (`tcr_eyeball_top20.json`) were read by hand.
**Same-name and mis-merged MBIDs do NOT dominate.** The dominant thin class at the top of
these lists is **correctly resolved credited personnel**: band members whose releases are
credited to the band (Royal Blood's Mike Kerr, Metallica's Lars Ulrich, Rammstein's
Christoph Schneider, Beirut's own horn and accordion players on Beirut's list), session
musicians, guest vocalists (Yoko Kanno's singers), producers, and remix-community artists
with no formal releases. This is the same class the `CAU-` audit surfaced ("nothing of
their own to listen to") — real people, correctly resolved, genuinely release-group-thin.

**Isolated common-name candidates exist and are named, licensing no rate:** a zero-catalogue
"Simon Green" at rank 1 of a jazz list (Bonobo's civil name), "Mike Davis", "Patrick
Wilson", and alias-split identities ("Gabriela Robin", Yoko Kanno's pseudonym, held as a
separate zero-catalogue MBID). Per prereg §4.4's pre-registered read, these would surface
the **open same-name population question** only if they *dominated* — they do not, so that
question (`2026-08-06-cocredit-investigation-execution-log.md` §6 item 1) **stays open and
is untouched in either direction by this run.**

## 6. Barred reads — carried from the prereg, travelling with every citation

1. **No adoption follows from any branch.** Nothing here changes a default, weight, filter
   or threshold.
2. **This does not reopen widening the drop rule** (owner, 2026-08-06).
3. **Release-group count is a proxy**, looser than the drop rule's criterion.
4. **Top-of-list enrichment ≠ "appears in journeys"** — no journeys were run, and the same
   holds for depletion.
5. **A→B differences are not attributable to the drop filters alone** (two columns differ);
   the 14× base-rate drop in §2 is *consistent with* the filters and not attributed.
6. **The §5 personnel observation is descriptive.** The eyeball read exists to sanity-check
   `TCR-C3`'s inputs, and no branch reads it.

## 7. Run notes

- **One runner defect, found and fixed before any gate was evaluated:** the first
  invocation crashed in phase 1 (`len()` on the `GraphStore.neighbours_of` generator)
  before reaching phase 3; no gate value and no outcome value existed at the fix. The fix
  is one `list()` call, committed with the results.
- The run enforced the §6 ordering structurally: run state written to disk in phase 5 and
  reloaded from disk before phase 6 computed any outcome.
- Runtime ~4.5 min with fresh caches (fast disk cache warm from the void run's scans of the
  same dumps).

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-08-06-tcr-thin-catalogue-rerun/tcr_run.py
```

Dump passes cache to `rg_counts.json.gz` / `artist_exists.json.gz` (gitignored); deleting
them forces a re-scan.
