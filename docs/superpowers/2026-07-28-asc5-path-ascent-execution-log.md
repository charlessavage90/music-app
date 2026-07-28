# Execution log — ASC-5 discharge (path-level ascent re-reads) — 2026-07-28

**Role: ACTIVE execution log.** Appended per task, not only at closeout.

## §0 — Status change: path-quality work is UNPAUSED, owner decision 2026-07-28

The owner unpaused path-quality work in this session, in these words: improve the
frequency of obscure artists (and/or reduce the frequency of very famous artists)
showing up in path interiors, **especially when the bypass buttons are used**. That is
the trigger `NEXT.md` reserves to him, so `NEXT.md`'s pause statement is stale as of
today; per its own rule the fresher record (this log) wins until the next closeout
rewrites it.

**What the unpause does not change:** a blind listening test, a production rebuild
(still hard-blocked by `acceptance.py`'s nameless-artist gate — his decision, unmade),
and any growth of `CLAUDE.md` all still need his explicit go. Track 2 / Track 2F /
the ceiling toll remain closed nulls; loosening the both-ways cap remains rejected.

## §1 — Instrument choice: why ASC-5, not the degree floor and not the rescale prereg

The resume brief (`2026-07-26-RESUME-BRIEF-path-quality.md`) was read in full first,
as it instructs, then its reading order (synthesis, committed-walk deliverability,
docs map), then `router-ascent-gradient` and `WHAT-GOOD-LOOKS-LIKE.md`.

- The owner's goal is stated in **fame/obscurity currency**. The degree-floor question
  (brief §1) is the **degree** axis — related but not the same currency (§2.6, §2.11) —
  and is itself blocked by the brief's §2 arithmetic-vs-pricing confound. Not started.
- On the fame axis, the parked candidate is the **builder-side p99 rescale**, and the
  record (`router-ascent-gradient` §6, echoed in `docs/README.md`) says its
  pre-registration should not carry a fame criterion before **ASC-5** is answered —
  otherwise a third fame-scored null in a row is the likely outcome.
- ASC-5 is two **re-reads of committed runs** — no rebuild, no arm, no owner spend —
  so it is also what cheapest-experiment-first selects.

## §2 — Verification before building (session-start check)

The load-bearing claim — "the X-vs-A7 contrast already exists in the run" — was
verified against the repo before any design: `paths.json` holds all 11 stage-1 arms;
`arms.py` confirms X's isolating baseline is A7, one column apart (`w_jump` 0.3 → 0);
the artifact on disk is the adopted one (sha256 `4cb84ef9…` = sidecar = `paths.json`);
and `scores.json` already carries the isolating contrast block (F9's success
condition), including X-vs-A7 in fame units. The one-hop method to extend to A7 is
`probe_artifact.py` Q5, mirrored exactly (`mirror.py:180-183` mean-matching).

## §3 — Decision rules committed before the run

`builder/analysis/2026-07-28-asc5-path-ascent/README.md`, commit `8562d15`, fixes
PLA-G1/G2/G3 (instrument gates), PLA-R1 (path-level climb vs geodesic null, thresholds
0.10 / 0.03 pctl), PLA-R3 (one-hop X−A7, thresholds ±0.02 / ±0.05, calibrated to the
committed A0→X span), and PLA-R4 (path-level X−A7, thresholds 0.1 / 0.3 log10), each
with its plain-language sentence fixed at definition time. The script was Snyk-scanned
clean before first run.

## §4 — Results: all gates passed; which pre-committed branches fired

Figures are owned by the analysis directory's `REPORT.md`; only the fired branches are
recorded here. One defect between rule-commit and run: the script's first execution
failed at JSON serialization (numpy types) — fixed with no change to any statistic or
threshold, and the fix predates any figure existing (the first run died before writing
output).

- **PLA-G1/G2/G3 all passed** — the instrument reproduces P8b's committed one-hop
  figures exactly, artifact identity holds, no degree-1 interior anywhere.
- **PLA-R1 fired its collapse branch**: on the famous-skewed pair set's first paths,
  delivered interiors are no more popular than the geodesic sets' — the famous middles
  there are *forced by structure*, not chosen by pricing. The single obscure-endpoint
  pair moved the other way, named in the report as the figure cutting against the
  blanket reading.
- **PLA-R2 (context)**: the bypass ladder's popularity profile is flat to d20 — the
  ladder swaps famous for equally famous all the way down. The user-facing statement
  of the owner's problem, in popularity currency.
- **PLA-R3 fired the ambiguous branch by 0.0003** — stated as ambiguous, not rounded.
  The non-ambiguous single-arm fact: the pure-similarity cost climbs at one hop far
  above the null, so the similarity term alone carries the climb (ASC-4 supported in
  its single-arm form).
- **PLA-R4 fired "immaterial"** in both currencies: the jump price does not change
  what whole journeys deliver, X vs A7, exactly per the committed isolating block.

**Design consequences carried forward:** any fame-scored criterion for the parked p99
rescale must not live on famous-pair first paths (structurally doomed per PLA-R1);
the bypass-depth gradient and non-famous-endpoint pairs are where movement is
possible; and no term in the cost function ever *rewards* descent or strengthens with
depth — the floor only permits diving and is dead by d20 (P8b F7) — which is the
mechanism-shaped gap left after two repricing nulls.

## §5 — ASC-5 marked discharged in place

`findings/2026-07-25-router-ascent-gradient.md` §4 annotated with a dated discharge
note pointing at the analysis directory; `docs/README.md` given the directory's
authoritative row.

## §6 — Owner set the ordering; Track 3 pre-registration committed

The owner approved the recommended ordering (depth-directional device first; rescale
parked until it answers; degree-floor axis not started; his spends last) and asked to
proceed. `specs/2026-07-28-track3-depth-descent-preregistration.md` is committed —
identifiers `DD-` (verified unused), device `w_known_ramp_pctl · k · pop_pctl(v)`,
six-arm factor table over dose × floor with per-row isolating baselines, the floor
declared a live interacting term in §0 rather than a constant (the Track 2 §0 lesson
in mirror image), first-path invariance as a verified gate (DD-G2), fame keyed by
MBID as a precondition (P8b F8, live for diving arms), and reads DD-R1/R2/R3 each
naming their run state. No arm may run until all four prerequisites discharge, in the
order DD-P2 (pair set) → DD-P1 (depth headroom, which runs on those pairs) → DD-P3
(analyst review) → DD-P4 (harness + Snyk). The first committed version listed P1
before P2; caught on re-read the same hour and corrected with an explicit
discharge-order sentence rather than a renumber (identifiers are forward-only).
Nothing in the pre-registration schedules a blind listen, a rebuild, or any owner
spend.

## §7 — Owner decision recorded: nameless artists are DROPPED

**2026-07-28, the owner, in this session: the 33 nameless artists are to be dropped,
not backfilled.** Recorded at the tripwire itself (`acceptance.py` docstring), which
stays in force until the drop rule is implemented in `build` — before the
largest-component prune, so stranded neighbours are pruned rather than left dangling.
This is a standing build rule (future crawls can mint new nameless nodes), and it is
**not implemented by this session**: no rebuild is due, Track 3 needs none, and
implementing it belongs to whichever session next touches the builder ahead of a
rebuild. The `acceptance.py` check is the forcing function; do not weaken it.

## §8 — Closeout record (run 2026-07-28, at the seam)

- **A1/A2**: this log is the retained record; handoff
  `2026-07-28-HANDOFF-track3-preregistered.md` written, previous handoff's role line
  edited to point forward. No `.superpowers/sdd/` ledger existed (no subagent-driven
  development this session).
- **A3**: every open deferral re-tested against `NEXT.md`'s table; none newly due. The
  `--prune` pass ripens ~2026-07-29 (not yet). The near-geodesic re-read is absorbed
  into DD-P1 with that stated as its condition. The nameless remediation now carries
  its condition (before the next production rebuild) with `acceptance.py` as the
  forcing function.
- **A4**: no shipped config knob was added — the Track 3 knob exists only in the
  pre-registration, not in code. Not closed *because* nothing shipped; stated rather
  than skipped.
- **A5**: ports 8000, 5173, 8138, 8139 all free; nothing started, nothing owned,
  nothing left running. The queued test-queue entries need no local server (live site).
- **B1**: `docs-lint.sh` — 3 hard failures found (the three new documents unclassified
  in `docs/README.md`), fixed, re-run clean (exit 0). `doc-auditor` dispatched scoped
  to the diff; findings and remediation recorded below when it reports.
- **B2**: `asc5_path_ascent.py` is a self-contained analysis script; nothing imports
  it and nothing should. No shipped module was created.
- **B3**: no tests were added; the instrument's green-goes-red evidence is PLA-G1
  (reproduces committed figures exactly) plus the first run's honest failure.
- **B5**: stale-description sweep found and fixed: `CLAUDE.md`'s orient row (pause
  claim, now false), `memory/roadmap-pointer.md` (same), `memory/MEMORY.md` index line
  (same), and `memory/path-quality.md` restating "27 prior claims" — the exact stale
  count `CLAUDE.md` warns about, converted to a read-the-table instruction.
- **D1**: tree clean at final commit; no gitignored path touched except reading
  committed analysis outputs.
- **D2**: artifact unchanged; fixtures untouched. **D3**: artifact identity asserted
  and recorded in every output (`4cb84ef9…`).
- **D4**: suites run, not asserted — builder **115 passed**, api **217 passed**,
  frontend **107 passed** (18 files).
- **D6**: unconditional **43,692 → 43,773 characters (+81)**; conditional **2,120 →
  2,121 lines (+1)**. The +81 is the `CLAUDE.md` orient-row correction: the false
  "PAUSED" claim replaced by the invariant plus both pause dates and a pointer to
  `NEXT.md`. A pure removal would have been net-negative but would have deleted the
  guard against a stale-copy reversion; the residual cost is flagged as the owner's to
  keep or trim. The +1 line is the memory corrections.
- **C1**: queued — the N/A entry at the top of `TEST-QUEUE.md`; the redesign entry
  below it remains the live one to run.
