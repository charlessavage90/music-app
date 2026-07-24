# Track 2 Stage A — the C1–C6 arm scorer

**Role: ACTIVE analysis record. Owns its figures.** Nothing here restates a figure from
`docs/superpowers/findings/2026-07-21-scoring-adjudication.md` or from the two fame-proxy
directories; those own theirs.

**No factorial arm has run.** This directory currently holds only the pre-arm checks.

## What lives here

| File | What it is |
|---|---|
| `arms.py` | The 15 arms as data — factor table, isolating baselines, R1 selection eligibility, the package-contrast list. The sweep is **two stages**: 11 factorial/diagnostic runs, then R1 picks W, then 4 attachments. Prints its own factor table. |
| `run_arms.py` | The walker. All-`known`, 20 bypasses, victim = most-popular interior (ties → lowest node id), independent per arm, guard G on everywhere, snapshots at {0,1,2,3,5,7,10,15,20}. Produces **paths only**. Implements **A13** (guard-infeasible cells dropped from all arms uniformly). |
| `fame.py` | Fame resolution under **A11** (F = log10(1+pageviews), unmatched → 0). Imports the canonical resolver; adds the **A15** English-article recall fallback and the A11 d15/d20 notability guard. Disk-cached. |
| `verify_resolver_equivalence.py` | Proves **A15**'s fallback leaves the §5 validation sample's 9/29 split byte-identical — a recall fix, not a proxy change. |
| `score.py` | C1–C4 (gating), C6 (reported, **A12**), the C5/F5/repeat/A14-tracking diagnostics, and **R1**'s selection of W. Deterministic, offline, re-runnable. |
| `band_gap.py` / `band_gap.json` | §2.2's permitted recalibration (does not fire) and the coverage-by-bucket measurement **A12** rests on. |
| `fame_cache.json` | Network-expensive resolved fame, cached by name. Seeded with P's 156 interiors so the full run and the P8b review do not re-fetch them. |

## Harness validated on production P — not an experimental arm

P is production; its paths are already in the record (the A0 gate). Running the full
pipeline on P alone validates the machinery without generating any experimental result, and
the output is a sanity signal in its own right:

- **C3 drop d5→d20 = 0.164**, against a 0.5 threshold — the scorer measures **production
  failing the depth-gradient criterion**, which is F2 stated as a number. A candidate must
  clear 0.5 to pass; production does not.
- **C1 mean ΔF = 0.000** — P against itself, as it must be. Confirms the pairing is correct.
- **C2 = 4/8** — production already reaches below B_unk in exactly the threshold number of
  pairs. **Flagged for P8b:** C2's minimum is met by production itself on this pair set, so
  C2 is close to non-discriminating here and C1/C3 carry the real load. Worth the reviewer's
  eye.
- **Resolver recall (A15) confirmed on real data:** Justice, Rainbow, and Ye (Kanye West)
  were scoring at the fame floor and sitting in P's own scored cells; the fallback recovers
  them (5.303 / 5.708 / 6.587) without disturbing the validated sample.

## Config-figure discipline (closeout B5, checked)

The scorer restates **no** figure from `config.py` — in particular none of the p99
similarity-clamp figures that B5 requires to cite adjudication §5.4. Its only numeric
constants are the pre-registered §2.2 thresholds (`C1_MEAN_MAX = -1.0`, `C3_DROP_MIN = 0.5`,
…), each cited to §2.2 in `score.py`, and B_unk is **read at runtime** from the committed
`../2026-07-24-track2-fame-proxy-wikipedia/score.json`, never hard-coded. The cost weights
live in `mirror.py` (not this directory) and are cited there. So B5's clamp-citation rule
does not bind here — recorded rather than skipped, per the tightened B5.

## Sequence from here

Per the execution log's seam entry: **P8b review of this harness → then the arms.** No
factorial arm has been scored. The next session runs `run_arms.py` (no `--arms` filter) for
the full stage-1 grid, `fame.py`, `score.py`, reads R1's W, then `run_arms.py --arms W …`
plus `stage2(W)` for the attachments.

## §2.2's permitted recalibration — checked, does not fire

The pre-registration allows exactly one threshold adjustment before arms run: if the
owner's *know well* and *never heard of* bands sit closer than **1.0 log10** apart, every
log10 threshold rescales. Two defensible readings, reported because they differ by 5× and
the conservative one is close to the trigger:

| Reading | Band gap | Fires? |
|---|---|---|
| **As scored** (A11's encoding — unmatched artists at F = 0) | **6.161** | no |
| **Matched only** (drops the zeros; separation among artists the proxy can see) | **1.093** | no |

**Neither fires, so every §2.2 threshold stands as written.** The conservative reading is
the one worth carrying forward: at 1.093, **C1's −1.0 log10 threshold is almost exactly one
of the owner's perception bands wide.** So C1 asks, in his units, for the middle artist to
drop about one full step in how well he would know them — which is a more defensible thing
to have pre-registered than a bare number looked like.

## Coverage by label bucket — why C6 could not stay a gate

| Bucket | Matched to an English Wikipedia article |
|---|---|
| *know well* | 7 / 7 |
| *heard of* | 6 / 6 |
| *never heard of* | **7 / 16** |

| Stratum | Matched |
|---|---|
| S1 — the nine anchor unknowns (lo-fi / synthwave) | **1 / 9** |
| S2 — judged-listen interiors | 12 / 12 |
| S3 — the two likely reaches | 2 / 2 |
| S4 — off-platform stress cases | 5 / 6 |

Everything the owner recognises resolves. Only the stratum he does not recognise fails to,
and it fails almost completely. **Under A11 an unmatched artist is scored at the fame floor
rather than dropped, so match failure is now a marker of the obscurity the sweep exists to
reach** — which is what makes C6's ≥ 90 % coverage gate untenable as written. Full argument
and the owner's decision: pre-registration **A12**.

## Determinism

`band_gap.py` reads only committed JSON, asserts that every labelled artist appears in the
pageview fetch, and takes no network calls. Re-running it reproduces `band_gap.json` byte
for byte.
