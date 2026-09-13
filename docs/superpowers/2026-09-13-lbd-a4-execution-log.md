# Retained execution log — `LBD-A4`, the pairing-delta arm, and the `R10` read, 2026-09-13

**Role: RETAINED EXECUTION LOG for the `LBD-A4` session. ACTIVE.** It records decisions and
reasoning, not narration — git has what each commit did.

**It owns no figures.** `LBD-A4`'s are owned by
[`../../builder/analysis/2026-09-13-lbd-a4/README.md`](../../builder/analysis/2026-09-13-lbd-a4/README.md);
`LBD-A0`–`LBD-A3`'s by
[`../../builder/analysis/2026-09-08-lbd-similarity/README.md`](../../builder/analysis/2026-09-08-lbd-similarity/README.md);
the served map's by [`findings/2026-07-21-scoring-adjudication.md`](findings/2026-07-21-scoring-adjudication.md).
**Cited by section, never restated.** It owns no status — [`NEXT.md`](NEXT.md) does.

**Governed by** [`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
(§0's arm table, §1's run plan, §2, §9's `R10`, and `LBD-AM3`/`LBD-AM6`) and by
[`specs/2026-09-06-own-similarity-design.md`](specs/2026-09-06-own-similarity-design.md)
`LBD-D6` and §7's `LBD-R4`.

---

## 1. The outcome, in one paragraph

`LBD-A4` ran as a full-history pass, `R10` was read against the bar, and **`R10` fires on the
edge-count half alone**: the pooled `LBD-C1` rate stays far inside its bar while edge count
clears its own several times over (analysis README §§5–7 own both). **`LBD-X6`'s condition is discharged
and the bar it protects is confirmed rather than released.** `LBD-R4` is retired as a risk and
confirmed as a fact. No graph was built, no `S4` design begun, nothing adopted.

## 2. Decisions taken, with reasoning

### 2.1 `R10`'s bar transports a `share` onto a `count`, and the resolution was committed first

**The defect is in the pre-registration, not in the run**, and it is the one plan defect this
session found. §9's `R10` row reads *"Material = the `LBD-G2` bar applied to edge count, or 5
pp on the pooled `LBD-C1` rate"*. `LBD-G2` is defined on a **share** (share of added artists
at ≤ 2 partners); edge count is a **count**. The row does not say which reading transports.

**Resolved as a 1 % relative change in rows**, `|A4 − A0| / A0`, and committed in the
analysis README's §3 at `44417b0` **before the pass ran**. Two candidate readings existed and
the more sensitive one was chosen deliberately: a laxer reading is the direction that can
flatter a null, and a bar chosen after seeing the result would have been unfalsifiable either
way. The git timestamp is the evidence, and it is the part that cannot be reconstructed
afterwards.

**Also fixed there before the pass:** the read of *every* possible result, including both
nulls and — the branch that actually fired — the case where the two halves disagree.

### 2.2 The pass is a driver over frozen scripts, never a new implementation

`--pairing distinct` already existed as `T3-D7` in `lbd_similarity.py`, with the fixture
asserting it in **both** the naive and the algebraic form against hand-derived values. So
`a4_run.py` computes nothing: it invokes the frozen scripts once per bucket, combines and
derives. That is what makes §2's held-constant table enforced by construction rather than by
care.

**The fixture was re-run on this machine before the pass** — eight fidelity checks green,
seven mutants red. That is `session-start`'s verify-one-claim discharged against the claim
this whole session rests on, and it is the same evidence class `LBD-AM3` rested on.

### 2.3 Chunking changed from `LBD-A0`'s 64 buckets to 128, and it is not a confound

The first attempt at `LBD-A0`'s own settings (64 buckets, 12 GB) was **killed by the system
under memory pressure** — 12 GB of a 31.7 GB machine with other work live; `LBD-A0`'s pass
had the machine to itself. Rather than retry the same setting or guess a smaller one, **one
bucket was measured** at mod 128 / 8 GB: peak RSS 7.64 GB against 11.9, and a shorter pass in
total.

**The exactness is not a claim about the number 64 — and it is the PRE-REGISTRATION'S §1 that establishes it, from LB's own SQL, not `LBD-D2`, which is the decision to run on DuckDB and names chunking only as the fallback.** Every stage through
`user_contribtion_mbids` partitions by `user_id`; only the final cross-user `SUM` crosses a
boundary, and `T3-D3`'s integer cast is applied by `combine_sql` to the completed sum and
never to a partial. The modulus moves wall clock and peak memory — `LBD-C3` quantities — and
cannot move a figure.

**The six mod-64 partials from the killed attempt were deleted rather than mixed in.** Mixing
would have been exact and the coverage check handles it, but one uniform chunking is a
cleaner record than 18 minutes of saved compute is worth.

### 2.4 `LBD-C2a` was deliberately NOT taken on this arm

It is a single `GROUP BY` over a table that now exists, which is exactly why it needed a
decision rather than a reflex. Its reads — `LBD-G2`, `R4`–`R12` — were pre-registered for the
four `T`-derived arms, **not for this one**, and taking an unregistered read *after* results
exist is what the pre-registration discipline exists to prevent. Same for `LBD-C2b` and
`LBD-M1` on this arm. Anyone who wants them owes an amendment first.

### 2.5 `LBD-G1` fires on `LBD-A4`, and the session answered rather than escalated

`LBD-A4`'s top-band pooled rate is below the 0.60 floor, as `LBD-A0`'s was. **`LBD-AM3`'s
override enumerates `LBD-A0`–`LBD-A3` and does not name `LBD-A4`**, which did not exist when
the owner ruled.

Per `CLAUDE.md` — *"Before escalating anything, answer it yourself and write the answer
down"* — the answer is in the analysis README's §5 and turns on one point: **`R10`'s bar is a
difference between arms, not a level against the archive**, so a lineage gap common to both
arms cancels, and §2 fixed that framing before the pass for exactly this reason. Supporting:
`LBD-A4` scores *higher* than `LBD-A0` in three bands of five; the mutant-detecting fixture
passed here; and the owner's `LBD-D6` ruling of 2026-09-12 **post-dates `LBD-AM3`** and orders
this arm run and `R10` read.

**What was NOT decided, and is flagged as the owner's:** whether `LBD-AM3`'s override extends
to `LBD-A4` as a statement about *absolute* fidelity. `R10` does not depend on it. **`LBD-C1`
is not cited as passed, for either arm.**

### 2.6 The per-artist distribution was taken with the diagnosis script, not the read script

The pre-registration's §2 requires `LBD-C1` **reported two ways, both required**.
`lbd_reads.py`'s quantiles carry the NaN-sort defect the `LBD-A0` README documents, and this
run reproduces the signature (band 0 printing p10 above the median). They are reproduced
nowhere. `lbd_c1_diagnose.py` supplies the corrected distribution, and its decomposition then
supplied something better than agreement — see §3.

## 3. What the record gained beyond the `R10` verdict

Both are owned by the analysis README (§5a, §6) and cited here, not restated.

- **The mechanism is measured, not argued.** Both arms have the *same* comparable pairs in the
  top band, but the ratio of our score to ListenBrainz's drops under the cheaper pairing, and
  its upper tail drops further. That is the quantity that must move for half a million pairs
  to fall below a fixed strength bar while the pair set itself barely changes.
- **The lost edges are our surplus, not ListenBrainz's answer.** The archive's own pairs for
  sampled top-band artists land within 0.1 pp of each other on *every* outcome under both
  arms. Labelled as inference in the README.

**Guarded against explicitly in both places:** a score ratio nearer 1 is **not** evidence that
`LBD-A4` is the more faithful arm — the residual is the corpus-date lineage gap `LBD-AM3`
diagnosed, common to both.

## 4. Corrections to the prior record

**None.** No previously-recorded claim is overturned by this work. Two additions rather than
corrections:

- `NEXT.md`'s `LBD-A4` deferral row said **"Still unrun"**. That is true as written and
  **false from 2026-09-13**; it is struck in place with the date, per A3.
- `LBD-X6` was written as a bar with a discharge condition. The condition is now met **and the
  bar survives it.** Any future reader must not read "condition discharged" as "bar lifted" —
  that inversion is the single most likely misreading of this session's output.

## 5. Gate outcomes

| gate / read | outcome |
|---|---|
| **`R10`** | **FIRES**, on the edge-count half alone. §3's disagreement branch |
| **`LBD-G1`** on `LBD-A4` | **FIRES** (top band below the floor), as on `LBD-A0`. `LBD-AM3`'s override does not name this arm — §2.5 |
| **`LBD-G3`** (cost) | its spill bar was already exceeded on the `LBD-A0` pass; the prescribed response — the chunked form — is what both passes are |
| `LBD-G2`, `LBD-G4` | **not reached.** `LBD-G2` governs supply reads, deliberately not taken (§2.4); `LBD-G4` gates the first full pass and was discharged there |
| **`LBD-R4`** (design §7) | **retired as a risk, confirmed as a fact.** The drift is real and measured; `LBD-D6`'s declaration rule is what manages it |

## 6. Operational measurements with no other home

Timings, memory and spill for all three stages are `LBD-C3` figures and are owned by the
analysis README's §4. Two things that belong here instead, because they are facts about the
*session* rather than about the arm:

- **Two instrument faults, both self-inflicted, neither touching a figure.** A combine that
  failed on a spill cap which was an artefact of an orphaned temp directory left by a
  process this session had killed 15 seconds earlier; and a `PyEval_SaveThread` GIL fault in
  the ephemeral `uv run --with duckdb` environment. The second was resolved by creating a
  dedicated venv at `C:\unsung-fast\lbd-venv` **at duckdb 1.5.5 — the same version every
  manifest in this track records**, so the instrument is unchanged. Both are recorded in the
  README's §4 so a reader comparing logs is not left to infer them.
- **Harness-tracked background jobs are killed under system memory pressure**, which ended
  three helper processes during the pass. The work itself survived because it was launched
  detached via `Start-Process`, which is what the `LBD-A0` pass also did. Worth knowing for
  any future multi-hour pass on this machine.

## 7. `closeout` D6 — the standing context layer

Measured against the memory directory this session's own context names
(`C:\Users\charl\.claude\projects\C--dev-music-app\memory\`):

| layer | unit | value |
|---|---|---|
| unconditional — `~/.claude/CLAUDE.md` + `CLAUDE.md` + `MEMORY.md` + every loading `description:` | characters | **50,977** |
| conditional — `SKILL.md` and agent bodies, `memory/*.md` bodies | lines | **2,726** |

**This session's delta in both: zero.** `git diff --name-only origin/main...HEAD` returns
nothing under `CLAUDE.md`, `.claude/` or `memory/`. Both figures are **identical to the
listen-2 read's**, and this branch is based on the same `main`, so the comparison is like for
like with no other branch's growth folded in.
