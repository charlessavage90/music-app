# Handoff — `LBD-A4` run and `R10` read, 2026-09-13

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-13-HANDOFF-lbl-listen2-read.md`](2026-09-13-HANDOFF-lbl-listen2-read.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns
it.

**A seam.** `LBD-A4` was run as a full-history pass, `R10` was read against the bar it was
given, the result is written up, and **nothing is in flight**.

**It owns no figures.** `LBD-A4`'s are owned by
[`../../builder/analysis/2026-09-13-lbd-a4/README.md`](../../builder/analysis/2026-09-13-lbd-a4/README.md);
the reasoning is in [`2026-09-13-lbd-a4-execution-log.md`](2026-09-13-lbd-a4-execution-log.md).

---

## What happened, in one line

**`R10` FIRES, on the edge-count half alone** — the pooled `LBD-C1` rate stays far inside its
bar; edge count clears its own several times over. Both figures and both bars are owned by the
analysis README's §§5–7.

## ⚠ The one thing a future reader is most likely to get backwards

**`LBD-X6`'s CONDITION is discharged. `LBD-X6` ITSELF STANDS.**

`LBD-X6` bars generalising the `LBL-` listen-2 result to the cheaper pairing form *"until
`LBD-A4` has run and `R10` has been read"*. Both have now happened — and the answer was that
the pairing form **does** change the map materially. So the bar is **confirmed, not
released**: listen 2's tie holds for ListenBrainz's own pairing semantics and **no sentence
may generalise it to the cheaper form.**

Had neither half fired, the pre-committed other branch would have lifted it. It did not.
**Anyone reading "condition met" as "bar lifted" has inverted the result.**

## Documents now wrong, and in which direction

| document | what is now false | done? |
|---|---|---|
| `NEXT.md` deferral table, `LBD-A4` row | *"Still unrun"* — true when written, **false from 2026-09-13** | **struck in place** with the date and what satisfied it |
| `specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md` | `LBD-X6`'s status; `LBD-AM6-7`'s *"`LBD-A4` was not run here"* is about *that* session and stays true | **status marker added beside**, per §12's own rule — nothing edited |
| `docs/README.md` | had no row for the new analysis directory, log or handoff | **three rows added, one amended** |

## Claims not to revert

- **`LBD-X6` stands.** See the block above. This is the one that will be got wrong.
- **`LBD-C1` is not cited as passed — for `LBD-A0` or for `LBD-A4`.** `LBD-G1` fires on both.
- **`LBD-AM3`'s override enumerates `LBD-A0`–`LBD-A3` and does not name `LBD-A4`.** Do not
  quietly widen it. `R10` was read anyway, and the reasoning is in the analysis README's §5 —
  `R10`'s bar is a *difference between arms*, so a gap common to both cancels.
- **A score ratio nearer 1 is not a fidelity verdict.** The residual is the corpus-date
  lineage gap `LBD-AM3` diagnosed, common to both arms.
- **`R10` says the choice *matters*. It says nothing about which pairing form is *better*.**
  Fewer edges is not worse.
- **`LBD-C2a`, `LBD-C2b` and `LBD-M1` were deliberately not taken on this arm.** Their reads
  were pre-registered for the four `T`-derived arms. Taking one now needs an amendment first.
- **The 128-bucket chunking is not a confound** and must not be "corrected" to match
  `LBD-A0`'s 64. the exactness the pre-registration's §1 establishes holds at any modulus; the change was forced by system
  memory and chosen by measurement.
- **Neither `LBL-` verdict may be re-listened** (`GBL-` §5), and `REQ-41` still bars reading
  either tie as equivalence. Unchanged by this work.

## What I know that is not in the durable record

Three items, now recorded here because they were nowhere else:

1. **The `A4.parquet` manifest records `"arm": "A0"`, and that is correct rather than a bug.**
   `lbd_derive.py`'s `A0` row *is* `(threshold 10, limit 100)` — `LBD-A4`'s own pair — so the
   frozen script was invoked rather than edited to add a label. What identifies the arm is
   `derived_from` naming `T_A4.parquet` with its sha256. Do not "fix" the label: editing that
   script would change the script that produced `LBD-A0`'s own numbers.
2. **A dedicated venv now exists at `C:\unsung-fast\lbd-venv`** (duckdb 1.5.5, matching every
   manifest in the track). It was created because `uv run --with duckdb` faulted at the
   interpreter level. It is outside the repo, gitignored by virtue of living outside it, and
   **a fresh clone will not have it** — recreate with `uv venv` + `uv pip install duckdb` if a
   later session needs to re-run these scripts.
3. **Harness-tracked background jobs get killed on this machine under memory pressure.** Three
   helpers died that way during the pass. Launch multi-hour work detached via `Start-Process`,
   as the `LBD-A0` pass did; the work itself was never at risk.

## Nothing is in flight

No background jobs, no dispatched subagents, no half-written directories. No listeners on
8000 or 5173, and none was started — this session booted no app and needed none. The tree is
clean.

## Artifacts, by checksum — they are gitignored and this is their only identity

| artifact | path | sha256 | rows |
|---|---|---|---|
| `T_A4` (aggregate, `score > 0`) | `C:\unsung-fast\lbd-pairs-a4\aggregate\T_A4.parquet` | `e919bc89425ecb7538fb5092a51ffb5e8a4d507fb2546a40d19a88508202a1e1` | 689,602,719 |
| **`LBD-A4`** (threshold 10, cap 100) | `C:\unsung-fast\lbd-pairs-a4\A4\A4.parquet` | `4ffa4acccc5a950c2d83402cdbb00477e080e8c706b31977c9b69b9d360843d0` | 10,823,170 |
| stage 0 (shared, **unchanged**) | `C:\unsung-fast\lbd-listens.parquet` | `6d77a6819830889d4957a21300eeb84a0db229c3f9084a7a0c30300f07707c08` | 2,647,691,119 |

The 128 bucket partials are at `C:\unsung-fast\lbd-partials-a4\`, each with its own manifest
and sha256. **Their coverage was verified**, not assumed: the residues expanded to the finest
modulus cover every user exactly once, with no duplication.

## Owed, and by whom

**The owner's**, and nothing here is a session's to take:

1. **Merge PR #124.**
2. **Decide whether `LBD-AM3`'s override extends to `LBD-A4`** as a statement about *absolute*
   fidelity. A scope question about his own earlier ruling. **`R10` does not depend on it** and
   nothing is blocked by it.
3. **Decide what follows the `LBD-` track** — the same open question listen 2 left. `LBD-A4`
   was the last arm the pre-registration schedules, and `LBD-D6`'s precondition on `S4` is now
   satisfied. **No session proposes a route.**
4. **The queued use-the-app tests** — `TEST-QUEUE.md`, live since the 2026-09-08 deploy and
   untouched by this work.

Branch `lbd-a4-pairing-delta`, PR **#124** (`gh` says where they are).
