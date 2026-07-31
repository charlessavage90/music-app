# Handoff — tag discrimination probe, Tasks 1–3 of 8, 2026-07-30

**Role: ⚠ SUPERSEDED 2026-07-31 on NEXT ACTIONS ONLY** by
[`2026-07-31-HANDOFF-release-tag-coverage.md`](2026-07-31-HANDOFF-release-tag-coverage.md).
**This document REMAINS AUTHORITATIVE for the `TAS-` track's internals, and `TAS-` Tasks 5–8
are still owed and unrun** — the `REL-` probe was a parallel investigation, not a
continuation, and touched none of them. Supersedes
[`2026-07-30-HANDOFF-coherence-tag-probe.md`](2026-07-30-HANDOFF-coherence-tag-probe.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a SEAM handoff, not mid-flight.** Tasks 1–3 ended with both gate reads resolved
and committed; nothing is in flight, no subagent is running, no background job survives,
all four ports are empty, and the tree is clean. It is an *earlier* seam than the plan
named (Seam A sits after Task 4) and a better one: Task 3 is the decision point, Task 4 is
mid-measurement. The owner asked for the handoff; the degradation tell did not fire.

## What this work is

A pre-registered probe testing the one assumption both candidate architectures rest on:
**does genre agreement discriminate between the candidates an artist already has**, or is it
the similarity score wearing a different hat. Governing document:
[`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md)
(`TAS-`). Plan:
[`plans/2026-07-30-tag-discrimination-probe.md`](plans/2026-07-30-tag-discrimination-probe.md).
Record: [`2026-07-30-tag-discrimination-execution-log.md`](2026-07-30-tag-discrimination-execution-log.md).
Probes: `builder/analysis/2026-07-30-tag-discrimination/`.

**Tasks 1–3 done. Both gates passed. Tasks 4–8 unrun.** Nothing adopted, no criterion fixed,
no weight, default or currency changed, no rebuild performed, and the owner's ear not spent.

## Read §8 of the pre-registration before touching TAS-4

**`TAS-4`'s original bar is WITHDRAWN AS FALSE** (`TAS-AM1`), and the plan's Task 4 was
rewritten to match. The withdrawn plain sentence is deliberately kept in the document,
marked false — **do not tidy it away.** A pre-registration's value is that its errors stay
visible.

`TAS-AM2` fixes the substrate per criterion: **selection-side on the pre-cap capture,
map-side on the adopted artifact, never compared across.**

## What the next session must not revert

- **No arm runs at bound 100.** Ranking is provably never consulted there — the source caps
  candidate lists at 100, so top-100 of a ≤100 list cuts nothing. Track B proved it
  byte-identically (`PS100` ≡ `MK100`, `LBS-3`). A λ sweep at bound 100 is a column of
  identical graphs. The owner initially voted to test both bounds and changed the vote on
  seeing this; do not reinstate it as though it were an oversight.
- **The neutral rule is per-artist and never zero**, and it is the **one dormant term** —
  inert at λ = 0, active in every arm. Pinned by `test_tas_common.py`. **Any change after a
  result exists is a §8 amendment, not an edit**, and every finding must be reported as
  "λ **and** the neutral rule", never as a clean single knob.
- **`ct_wikidata_genres.py` stays frozen.** `tas_wikidata.py` exists precisely so it did not
  have to be edited.
- **A `TAS-5` null is weak evidence about tags specifically.** Three consecutive router
  pricing changes have returned nulls here; that caution is written into the criterion. Do
  not report a `TAS-5` null as "tags do not work" — `TAS-3` and `TAS-4` are what distinguish
  the two.
- **The tag frame is a LATIN-SCRIPT vocabulary.** Non-Latin genre labels normalise to empty
  and are dropped, so those artists read as *unlabelled*. Correct, `COH-2` shares it, and it
  is pinned by test — but `TAS-1`'s coverage must be read as Latin-script coverage.

## The open decision, and what I would do

**The architecture question — build-time selection vs router-side pricing — is deliberately
still open**, and the probe exists to inform it. `TAS-4` and `TAS-5` are the two halves.

**If I were continuing: run Task 4 next, unchanged.** `TAS-3` came back the encouraging way
— the signal is largely independent of similarity and the great majority of candidate lists
are not already in agreement order — so the mechanism that would have made λ inert at every
value is absent. That makes `TAS-4` the highest-information next measurement, and it is
cheap: the capture exists, the reconstruction is verified edge-for-edge, and the arms are
seconds each.

**Two things I would not do.** I would not skip ahead to `TAS-5` because it is architecturally
more attractive — a `TAS-5` null is uninterpretable without `TAS-4` beside it. And I would
not run the red instrument check late: Task 7 carries it, and **`TAS-4`/`TAS-5` results must
not be believed before it has run.**

## Already updated — do not re-edit

`NEXT.md`, `docs/README.md` (two new rows), `TEST-QUEUE.md` (N/A entry), the previous
handoff's role line, the probe directory `README.md`, and the plan's Task 4 (rewritten under
`TAS-AM1`, with the invented accessors replaced).

## What I know that is not otherwise in the durable record

- **The captures live in the session scratchpad, not the repo** —
  `alge_capture.npz` / `algb_capture.npz`, ~20 MB each. That directory is session-specific
  and will not survive. **Regenerate with `td_capture.py` (~2 min) rather than hunting for
  them**; `td_turnover.py --verify` makes a stale capture impossible to use silently.
- **Task 4's plan code calls `load_capture` and `mutual_edge_set` from `td_turnover.py`, and
  those names were written from the analyst's description rather than read off the file.**
  There is a verify step covering it. The likely mismatch is keying: the capture stores
  int-id CSR arrays plus an `mbids` array, while `simulate_top_k` is MBID-keyed, so an
  id-mapping step is probably needed between them.
- **Three of this session's four plan defects were caught by verify-against-source steps
  that the plan itself carried.** If you are tempted to skip one, that is the evidence
  against.
- **`ml-graph-analyst` was dispatched twice and its transcript is warm** (agent
  `ac691b098bba53852`). It holds the mutuality transfer function and the path-carrying
  measurement. If a `TD-` question comes up, resuming it is cheaper than a cold dispatch —
  but note its second dispatch *refuted its own first hypothesis*, so treat its speculation
  as speculation and its measurements as measurements.
- **The owner deferred the `testpaths` question**, so the `TAS-` tests do not run in the
  default builder suite. Run them explicitly; the command is in the probe README.
- **Nothing about tags has been measured against the owner's ear, and cannot be offline.**
  The 11 blind verdicts remain unconsumed; `ct_retrodict.py` remains committed and unrun.
