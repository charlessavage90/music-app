# Handoff — `LBL-` listen 1 run, read and written up, 2026-09-11

**Role: ⚠ SUPERSEDED ON NEXT ACTIONS 2026-09-12 by
[`2026-09-12-HANDOFF-lbl-listen2-prep.md`](2026-09-12-HANDOFF-lbl-listen2-prep.md)** — the owner
chose a route and listen 2 has since been prepared under `LBD-AM6`. **It remains authoritative for
the listen-1 read and for every claim-not-to-revert below**, none of which `LBD-AM6` touches.
*(Original role:)* **ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-10-HANDOFF-lbd-listen-prep.md`](2026-09-10-HANDOFF-lbd-listen-prep.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**A SEAM handoff.** The listen was run, unblinded, read and written up; nothing is
half-finished and nothing is in flight.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
the `LBD-AM5` block in §10 — **executed**, and still governing every read.
**The read:** [`findings/2026-09-11-lbl-listen1-results.md`](findings/2026-09-11-lbl-listen1-results.md)
— **the figures owner for this listen; cite it by section, never restate a number.**
**Retained log:** [`2026-09-11-lbl-listen1-read-execution-log.md`](2026-09-11-lbl-listen1-read-execution-log.md).
Branch `lbd-listen`, PR #116 (addresses only; `gh` says where they are).

---

## ⛔ The owner has ruled: NO further blind listen for now

Stated 2026-09-11: *"I don't want to do another blind listen immediately. I'll discuss with
another session which route to take."*

**So listen 2 does not start, and no session proposes starting it.** The route is an open
question he is taking to a separate session — most likely a `consultant` session, which
reads **only the committed record**. That is why this handoff and `NEXT.md` set the options
out properly rather than pointing at a conversation: **the record is that session's only
input.** Do not dispatch a consultant from a working session (`CLAUDE.md` forbids it); he
launches it himself.

## What a cold reader most needs

1. **The read is `LBL-R2`, the tie.** *"My ear cannot tell our recomputed lists from
   ListenBrainz's own."* Neither question came near the margin the pre-registration fixed
   before any journey existed — **figures in the findings note's §1.1, restated nowhere,
   including here.** Nothing adopted, no default changed, no shipped code touched.
2. **A tie here is not "the maps are the same".** They are structurally very different
   (served-population README §3, §3a). The finding is that the difference was **inaudible on
   this instrument**, and the instrument's limit was the pair draw — most undecided rows
   were undecided because the owner knew everyone on both sides, which he said himself.
3. **One pair moved, and it moved to our map**: The Litter → Night Moves, every depth on the
   coherence question, plus his only unprompted pair-level preference. Obscure endpoints,
   long journeys. **One pair carries no read** — it is a hint about where to look.
4. **`WHAT-GOOD-LOOKS-LIKE` value 8 gained a corroboration from inside the blind.** Where
   his two answers pointed opposite ways, he wanted the coherent side. Still preference,
   not evidence; no threshold comes off it.

## Claims that must NOT be reverted

- **The verdict may not be re-listened** — `GBL-` §5's run-once rule binds it. A further
  listen is a **new amendment on new pairs**, never a re-run of these.
- **The owner's closing note changed no number**, and the findings note's §1.5 shows the
  arithmetic. Do not let a later reader treat it as having moved the result, and do not
  re-tally on his free-text "slight"/"strong" wording — that coding does not exist and
  inventing it after the fact is barred.
- **`lbl_listen1_owner_notes.md`'s provenance caveat stands**: its commit timestamp is the
  write-up session's, so "written before he read the read" rests on his account, not on git.
  Do not upgrade that sentence.
- **`LBD-X4` and `LBD-X5` travel with every listen-1 sentence** — no attribution to "the
  data" without the 439-artist cap-step term beside it, and none to any single component of
  the data bundle.
- **`V` is an experimental control, not a population rule.** `S4` owns adoption.
- **Three `docs/README.md` rows were corrected** because they said the listen had not run.
  They are right now; do not restore them.

## What is on disk and must not be rebuilt

Identities owned by the served-population README §0–§5; paths only here. All unchanged by
this session — it built nothing.

**Provenance for the two gitignored maps is already durable in two places** (`closeout` D3):
the served-population README §5 records both artifacts' sha256s beside their build records, and
`lbl_listen1_result.json` carries each map's path and sha256 inside the result itself — so a
future reader can tell which artifacts this verdict was drawn from without trusting a path.
**Not restated here.**

| | |
|---|---|
| the two listenable maps | `C:\unsung-fast\lbd-artifacts\LBD-A0V.bin`, `LBD-A5V.bin`, each with its `.bin.json` sidecar |
| archives, `LBD-A5` table | `C:\unsung-fast\lbd-archives\…`, `C:\unsung-fast\lbd-pairs\A5\` |
| the sealed listen-1 mapping | `.superpowers/lbl/` — gitignored, and **already unsealed into the committed result**; nothing depends on it now |
| listen 2's materials | ~~**do not exist.** Its pairs are fixed in `lbl_pairs.json`; its map is built; nothing else is prepared~~ — **TRUE WHEN WRITTEN, FALSE SINCE 2026-09-12.** `LBD-AM6` prepared them and **superseded that pair table**: listen 2's pairs are now `lbl_pairs2.json`. See [`2026-09-12-HANDOFF-lbl-listen2-prep.md`](2026-09-12-HANDOFF-lbl-listen2-prep.md). The map is unchanged and was not rebuilt. |

## What I know that is not in the durable record

- **The four routes in [`NEXT.md`](NEXT.md) were mine to set out, not to rank.** If I had to continue
  I would re-draw pairs before spending another listen — the tie's limiting factor was
  measured to be familiarity, and a listen on the same kind of pairs would return the same
  kind of tie. That is a view, it is in the findings note's §3 as a falsifier, and it is
  **not** a recommendation on which route to take: that is his.
- **The `DLS-T1` probe did not fire for this session**, and the observation is confounded by
  this session's harness mode reading files through Bash rather than the `Read` tool.
  Written up in the retained log §5. **It is not the `DLS-T1` read** and must not be used as
  one.
- **Nothing was measured that is not written down.** The only figures this session produced
  are in the findings note; the hand-recomputed tally matched the committed one exactly.

## In flight

**Nothing.** No server, no listener, no background job — ports 8000, 5173 and 8765 were all
clear at closeout and this session started none. No subagent is running.

## Owed, and by whom

| | |
|---|---|
| **Owner — the open decision** | **which route the `LBD-` track takes.** Four options are set out in [`NEXT.md`](NEXT.md), with what each costs and what each would settle. He has said he will take this to a separate session; **no session starts any of them on its own initiative.** |
| **Owner — still unruled, and it gates one option** | **`LBD-D6`** — `LBD-A4` was to run before any further arm was pre-registered, and `LBD-A5` was registered without it. Listen 1 is unaffected; **listen 2 is entirely about that arm.** |
| **Owner — unrelated and still queued** | the **three use-the-app tests** in [`TEST-QUEUE.md`](TEST-QUEUE.md), live since the 2026-09-08 deploy. Untouched by this work. |
| **Owner** | **merge PR #116.** |
| **A future listen, whichever route** | the **six** instrument items in the findings note's §4 — among them a minimum interior length in the pair gate, selecting for unfamiliar interiors, asking for pick strength on the row with its own pre-registered threshold, and dealing the side shuffle rather than drawing it. |
