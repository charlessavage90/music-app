# 2026-07-30 — tag-discrimination probe: swap-rate → edge-turnover transfer function

**Analysis only.** Nothing here builds an artifact, writes to `builder/src`, changes a
default, or adopts anything. The crawl archives are opened through `ReadOnlyArchive`
(`GRT-A1`) inside the Track B helper these scripts reuse.

## What question these answer

`TAS-4` in `docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md`
kills the build-time architecture when "the median artist swaps ≤ 2 of 50". Its own bound
says the *built* consequence of a given swap rate is not derivable from the swap rate,
because mutual k-NN deletes edge (u,v) when **either** endpoint drops it. These scripts
measure that conversion on the real candidate-list and mutuality distribution, so the
threshold can be stated in the quantity it is actually about — and then measure whether
the deleted connections are ones journeys route through.

## Scripts

| script | what it is |
|---|---|
| `td_capture.py` | Runs `_capture_pipeline` from the Track B harness (`cb_run_cells.py:185`) — same code path, same archive, byte-deterministic — and freezes the pre-cap candidate lists + `ranking` values as int-id CSR arrays in an `.npz`. Nothing downstream re-reads the archive. |
| `td_turnover.py` | The transfer function. Reconstructs `mutual_knn_cap`'s top-50 selection over the capture, perturbs the ranking in seven arms (factor table in the module docstring), and reports edge deletions / creations / symmetric-difference turnover against an independent-uniform-drop null built from each arm's own realised drop rates. `--verify` runs the green instrument check. |
| `td_coverage.py` | Holds swap size fixed and varies only the share of artists the reranker touches — the zero-inflated case `TAS-1` expects. Isolates whether the *median* is a safe summary of the quantity `TAS-4` bounds. |
| `td_pathedges.py` | Are the deleted connections the ones journeys use? Routes a pair set with `find_journey` at production `ApiConfig()` weights on the SAME substrate the selection is simulated on, then intersects routed edges with each arm's deleted set. Reports the safety ratio (routed deletion rate ÷ population deletion rate) per regime, per swap size and per pair class, with a split-half stability check and the creation mirror. |

## Instrument check (green)

The reconstructed selection must reproduce a real build **exactly**, not approximately.
It is checked against `builder/scratch/cb-cells/ALG-E-mutual_knn-k50.bin`
(sha256 `73feffa0…a69faa`), edge set for edge set, over that artifact's node set.
`td_turnover.py --verify` runs it; `td_pathedges.py` asserts it before scoring anything.

Both also assert the sha256 of the **adopted** artifact
`builder/scratch/graph-t15-tiebreakfix.bin` (`4cb84ef9…61dc8`) and report how the
substrate differs from it. The adopted artifact predates the nameless-artist drop that
`_assemble` now applies, so the two node sets are not identical; the delta is reported in
the JSON rather than assumed away. `td_pathedges.py` deliberately uses the **one**
substrate for both the selection simulation and the routing, so the intersection is
internally consistent.

## Pair set (td_pathedges only)

Own seed `20260730-tdcal` — **deliberately not** the pre-registered `TAS-5` seed
`20260730-tas`, so this calibration does not consume the pre-registered draw. The three
class definitions mirror spec §3 (`ff` both ≥ 0.99, `fo` one ≥ 0.99 and one < 0.50, `oo`
both < 0.50) over the adopted artifact's percentile fame frame as a fixed reference
population. Fame here is **popularity percentile**, not degree.

## Running

```bash
cd builder
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_capture.py --out <scratch>/alge_capture.npz
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_turnover.py --capture <scratch>/alge_capture.npz --verify
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_coverage.py --capture <scratch>/alge_capture.npz
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-30-tag-discrimination/td_pathedges.py --capture <scratch>/alge_capture.npz --per-class 300
```

`--archive ALG-B` on the capture gives the second slice; the turnover run then needs
`--out …_algb.json` and no `--verify` (the green check is ALG-E's artifact).

Captures are ~2 min (ALG-E) / ~7.5 min (ALG-B) and land in the session scratchpad, not
here — they are large and reproducible. Simulation arms are seconds each; the 900-pair
routing in `td_pathedges.py` is ~10 min.

## Outputs kept here

`td_turnover.json` (ALG-E), `td_turnover_algb.json` (ALG-B second slice),
`td_coverage.json`, `td_pathedges.json`. Figures are read off these, not restated in
this README.

## What these do NOT use

**No tag data.** The tag frame does not exist yet, so the reranking is a synthetic
uniform agreement field with tunable magnitude, deliberately independent of similarity
strength. The arms fix the *size* of the reordering, never its content — so the `MULT-*`
rows say nothing about what λ the real tag signal would need (`TAS-3` names exactly that
hazard). The transfer function itself is a property of the graph's mutuality structure,
which is what makes it reusable whatever the tag frame turns out to look like.

---

# The probe proper (`TAS-`)

**Added after the `TD-` derivations above, which exist to make `TAS-4` measure the right
quantity.** The `TD-` scripts are instrument work on the graph's mutuality structure and
use no tag data; the `tas_*` scripts below are the pre-registered probe and use nothing
else. Both series live here because the second consumes the first — `TAS-4` reuses
`td_turnover.py`'s reconstruction and its green check rather than reimplementing them.

Governing document:
`docs/superpowers/specs/2026-07-30-tag-discrimination-probe-preregistration.md`.
Implementation plan: `docs/superpowers/plans/2026-07-30-tag-discrimination-probe.md`.
**Read all of §8 before touching anything.** `TAS-AM1` withdraws `TAS-4`'s original bar as
false; `TAS-AM2` fixes the substrate per criterion; **`TAS-AM3` withdraws the red instrument
check as unachievable** and replaces it; `TAS-AM4` authorises evaluating a candidate frame.
**`TAS-AM3` and `TAS-AM4` were appended after results existed and say so at their heads.**

| script | what it is |
|---|---|
| `tas_common.py` | Shared loading and **the agreement device** — Jaccard over union-genre labels, plus the neutral rule for unlabelled pairs. The only place either is defined. |
| `tas_tags.py` | Full-graph union-genre tag frame over the LB batched transport (`COH-5`). Resumable. |
| `tas_signal.py` | `TAS-1` (coverage by edge class), `TAS-2` (within-list spread), `TAS-3` (collinearity diagnostic). Carries both gate reads. |
| `tas_select.py` | `TAS-4` — edge turnover under the λ grid, per `TAS-AM1`. |
| `tas_guard.py` | `TAS-6` obscurity guard **(selection half only — the routing half is still owed)**, plus `TAS-AM3a` (liveness and equivalence) and `TAS-AM3b` (null control). **The randomised-label red check it originally carried is WITHDRAWN by `TAS-AM3`**; `randomised_labels` is retained and runnable only because `TAS-AM3` cites its figure. |
| `tas_frame_eval.py` | `TAS-AM4` — evaluates the `REL-` enriched frames as **candidates** beside the committed one. Changes no vocabulary. |
| `tas_frame_split.py` | **Diagnostic, not a criterion.** Decomposes `TAS-AM4`'s `W6` into its two Discogs columns (`W4` = closed 15-value genre, `W5` = ~600-value style), isolating each twice. Reproduces `TAS-AM4`'s committed figures and aborts if it cannot. Figures: `tas_frame_split.json`; reasoning: execution log §15. |
| ⚠ `tas_pairs.py` | **NOT YET BUILT** — Task 5. The §3 pair draw, own seed, classes carried end to end. |
| ⚠ `tas_route.py` | **NOT YET BUILT** — Task 6. `TAS-5` — routing under a harness-local coherence term. |

## The neutral rule is the one dormant term

It is inert at λ = 0 and active in every arm, so a bad choice cannot show up in the
baseline. It is fixed in `tas_common.py`, pinned by `test_tas_common.py`, and **must not
move after any result exists** — a change is a §8 amendment, not an edit.

> **⚠ Those tests do NOT run in the default suite.** `pyproject.toml` sets
> `testpaths = ["tests"]`, so `uv run --extra dev pytest -q` collects 129 tests and none
> of them are these. Run them explicitly:
>
> ```bash
> UV_LINK_MODE=copy uv run --extra dev pytest analysis/2026-07-30-tag-discrimination/ -q
> ```
>
> This is pre-existing — two earlier probes (`2026-07-23-track2-fame-proxy`,
> `2026-07-24-track2-fame-proxy-wikipedia`) carry test files in the same position. Every
> analysis test passes today, so adding `analysis` to `testpaths` would work cleanly; that
> is a shared-config change for the owner to make, not a probe's to take. **Read the count
> off the command above — this file does not own it, and the number here went stale once
> already.** **Until then,
> "pinned by test" means pinned by a test somebody has to remember to run** — so the
> command above belongs in any closeout that touches this directory.

`neutral_for` takes the artist's **own** label set: the neutral value is the median
agreement between the artist and its own labelled candidates. An earlier draft in the
implementation plan measured candidates against each other, which is a different
quantity; the corrected version has exactly one resolution path (`resolved_agreement`)
so the two cannot drift apart again.

## Vocabulary

Union genre = LB genre-whitelisted tags ∪ Wikidata P136, both through the **frozen**
`ct_common.norm_genre`. Same vocabulary as the `COH-` coverage figures, so `TAS-1` is
comparable with them. **Not** the widest tag union (`COH-6` measured that as
near-identical in the tail).

> **⚠ Correction to an earlier line in this file, and to the implementation plan.** Both
> said the P136 half was already on disk and only the LB half needed collecting. **That is
> wrong.** `fp_wikidata.json` holds *item* presence (`qid`, `wikis`, `enwiki`) and no
> genres at all; `ct_wikidata_genres.json` holds genre **counts** (`{"genres": 10}`), not
> labels, because `COH-1` only ever needed presence. **The P136 labels were never
> persisted and are not recoverable from either output.** `tas_wikidata.py` collects them,
> and `ct_wikidata_genres.py` is left frozen rather than edited to serve a later question.
> Verified by inspecting both files rather than trusting the plan.

**The union genre is a LATIN-SCRIPT vocabulary, and that is not a choice made here.**
`norm_genre` ASCII-folds, so a label with no Latin characters normalises to the empty
string and is dropped: `パンク` → `''`, `한국` → `''`. An artist whose only genres are
non-Latin therefore reads as **unlabelled** and takes the neutral value rather than
scoring zero agreement — correct, since overlap across disjoint vocabularies is not
computable, but it means `TAS-1`'s coverage must be read as Latin-script coverage.
Diacritics fold rather than vanish (`Música popular brasileira` survives), so it is a
script limit, not a language limit. `COH-2`'s figures share the property, so the two
records stay comparable. Pinned by
`test_non_latin_only_artists_read_as_UNLABELLED_and_that_is_recorded`.

## Deferred, with a condition

**Adding `analysis` to `testpaths`** — deferred by the owner 2026-07-30. All 34 analysis
tests pass today, so it would work cleanly, but it changes what every `pytest` run in the
builder package collects. **Condition: revisit if any `TAS-` test ever needs to gate a
merge, or at the closeout that retires this probe** — whichever comes first. Until then
the explicit command above is the only thing running these tests.
