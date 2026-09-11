# Handoff — `LBD-` Tasks 6–7 complete, the build-stage stop reached, 2026-09-10

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-10-HANDOFF-lbd-task4-owner-stop.md`](2026-09-10-HANDOFF-lbd-task4-owner-stop.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**A SEAM handoff.** The build stage the owner authorised at the Task 4 stop is finished: both
arms named by `LBD-AM4` are emitted and built over the fixed population, every pre-registered
read is taken, the threshold curve is recorded, and the figures owner is written. **Nothing
further starts on a session's initiative** — a blind listen spends the owner's ear, a threshold
change is a fresh amendment, and adoption is `S4`.

**Governing:** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
with **`LBD-AM4`** (§10 block, §12 row) beside `LBD-AM1`–`AM3`. Design and plan unedited.
**Retained log:** [`2026-09-10-lbd-task67-execution-log.md`](2026-09-10-lbd-task67-execution-log.md).
**Figures:** [`builder/analysis/2026-09-10-lbd-supply/README.md`](../../builder/analysis/2026-09-10-lbd-supply/README.md)
§1–§5 and the Task 4 README's **§6c** (the curve), nowhere else.

---

## What a cold reader most needs

1. **`LBD-G2` clears at graph level for `LBD-A2`, with both controls reported; `R8` and `R9`
   do not fire; the residual stratum moves most** (figures owner §3). *Plain: in a map we
   could ship, dropping ListenBrainz's strength bar takes the added artists from about one in
   ten dead ends to about one in eighty, and the artists our own ceiling could never rescue
   improve most.*
2. **The population was fixed to the extended map's own 88,685 artists (`LBD-AM4-1`)**, so each
   arm differs from the ceiling probe's §4 bridge control in the data alone. That is an
   experimental control, **not a population rule** — `S4` is untouched. It also made the
   population confound visible as a number: restricted to that set, `A2` is 1.6× `A0`, not 7×.
3. **The `A0`-vs-served-map difference is a bundle, not a finding about the reimplementation**
   (figures owner §4's warning): corpus age, the absent `filter_True` stage, today's mapping,
   the band-member class and our tie-break, none separated.
4. **The curve says "threshold 0" means one listener, one session** — score 1 is nearly absent
   from `T`, score 2 is the floor in practice — and most of the dead-end reduction arrives by a
   bar of 3 (Task 4 README §6c). Descriptive; it decides nothing.

## Claims that must NOT be reverted

- **`drop_unlistenable=True` via the `20260809` override is correct for the fixed population
  and supersedes `LBD-X3`'s `False` for that population ONLY** (`LBD-AM4-3`, measured: the
  census covers all 88,685; all three lists remove nobody; both builds logged zero drops).
  `LBD-X3` stays right for any arm over the table's own population. Do not "fix" either.
- **`LBD-A3` is barred from building** (`LBD-AM4-2`) — not "deferred". `LBD-A1` is not built
  and not barred. `LBD-A4` remains unrun.
- **The population restriction is applied to the derived arm after its rank cut, never by
  re-ranking inside the fixed set** — re-ranking would make "`A0`" a different object from the
  one `LBD-C2a` was read on.
- **`LBD-C1` is still "fired and overridden" (`LBD-AM3`)**, never "passed"; these arms inherit
  it.
- **The plan's Task 6 pin of `unlistenable_drop_algb_20260805.json` is wrong for this stage**
  (it censuses 75,000 and would refuse over the fixed population); the plan is deliberately
  unedited and the amendment says which file is used.

## What is on disk and must not be rebuilt

| | |
|---|---|
| `A0` archive | `C:\unsung-fast\lbd-archives\A0\` — 86,854 payloads, digest over payloads `c13c2250…` (identical across three emissions), `MANIFEST.json` `d6f79076…` |
| `A2` archive | `…\lbd-archives\A2\` — 88,285 payloads, `MANIFEST.json` `78c31d29…` |
| population file | `…\lbd-archives\population_cxa_mbids.txt`, `1bbff8fc…` |
| ranked intermediate for the curve | `C:\unsung-fast\lbd-pairs\curve\ranked_P.parquet`, 21.8 GB, `ce48ca44…` — reusable with `--reuse-ranked`; deletable |
| first `A0` build record | `…\lbd-archives\lbd_build_A0.first.json` — identical to the committed one apart from manifest identity |
| everything from Task 4 | unchanged; see the previous handoff's table |

Committed: every results JSON beside the figures owner, including the per-artist degree files
(~3.9 MB each) so the paired read reproduces without a rebuild.

## Already updated — do not redo

`docs/README.md` (rows for this handoff, the previous one, the new log, the new figures owner,
and the Task 4 README's §6c qualifier); the pre-registration (`LBD-AM4` and two pointer notes);
`NEXT.md` (top block rewritten, outgoing block demoted, registries updated); the Task 4 README
(§6c); the two READMEs' "what is NOT established".

## What I know that is not in the durable record

- **Nothing computed is unrecorded.** Every figure is in the two READMEs or the committed JSON.
- **Decided against:** re-ranking inside the fixed population (changes the arm's meaning);
  aggregating neighbour lists inside DuckDB (ran out of memory beside the curve — the sorted
  stream replaced it); building `A1` (bounded above by its pair-level null); reusing the
  crashed curve's intermediate (no footer).
- **The session's own view, offered and not decided:** if a listen is next, amend for a bar of
  2 or 3 before building the arm that gets listened to — the curve says the single-session
  mass buys little on dead ends and costs a lot in list length. The owner has not chosen.
- **A trap, in the log and the script:** two DuckDB processes side by side on this machine,
  one at its own memory limit, ended in an access violation inside DuckDB's native module,
  silently. Run the heavy ones alone.
- **Not investigated, counted only:** 256 added artists with fewer connections under `A2`
  than `A0`; 126 artists the `CXA` build recorded no fame for, nearly all absent from both
  arms; 10 MBIDs with no MusicBrainz identity row, absent from both arms.

## In flight — nothing is running

No process, no listener, no dev server; ports 8000 and 5173 are clear. Every background job
this session started has ended.

## Owed, and by whom

| | |
|---|---|
| **Owner** | merge PR #115; the three live `TEST-QUEUE.md` entries from the 2026-09-08 deploy (untouched by this work); **the decision at the build-stage stop** — blind-listen `A2` at threshold 0, pre-register an intermediate threshold and build that, or stop with the supply question answered at both levels |
| **Successor, only if he proceeds to a listen** | a blind-listen design under `REQ-38` and `WHAT-GOOD-LOOKS-LIKE`; routing needs fame over the arm's population through the existing `fame` stage (plan Task 8, described and NOT scheduled; `LBD-D4`); `LBD-A4` before any further arm is pre-registered (`LBD-D6`) |
