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
