# Track 3 — the depth-descent device: measurements

**Role: ACTIVE analysis record. Owns its figures.** Every figure Track 3 produces lives
here and is cited elsewhere, never restated. Scoring/path-quality figures that predate
this track belong to `findings/2026-07-21-scoring-adjudication.md`.

**Governing document:** `docs/superpowers/specs/2026-07-28-track3-depth-descent-preregistration.md`.
Decision rules, criteria and thresholds are fixed **there**, committed before any arm —
this README does not restate them and must not be read as a second source. Amendments
made during execution are recorded in
`docs/superpowers/2026-07-28-track3-depth-descent-execution-log.md`, with the reasoning
and the git timestamp as the evidence of ordering.

**Commissioned** by the owner unpausing path-quality work on 2026-07-28, goal: more
obscure / fewer very-famous artists in path interiors, **especially under bypass**.

**Artifact throughout:** `graph-t15-tiebreakfix.bin`, sha256
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted in every
script (DD-G3). It is gitignored, so the assertion is the only identity check.

**Currency notice.** `pctl` here is a percentile **of `pop_raw`**, average-rank per P6 —
never a fame claim (§2.11), and never interchangeable with `pop_raw` itself (§2.12).
Fame is the committed A11 instrument (`F = log10(1 + annual en.wikipedia pageviews)`,
unmatched → floor) and is resolved only by the committed `../2026-07-24-track2-arm-scorer/fame.py`.
**DD-D6 exists precisely because DD-P1 certifies headroom in percentile while DD-C1
scores in fame**; do not read one as the other anywhere in this directory.

---

## Scripts, in the order they were run

| script | what it does | output |
|---|---|---|
| `recon_bands.py` | band sizes and the Track 2 carry-over candidates' percentiles — reconnaissance for DD-P2, decides nothing | *(stdout)* |
| `draw_pairs.py` | **DD-P2**: the first twelve-pair draw, seed 20260728 | `pairs.json` |
| `dd_p1_headroom.py` | **DD-P1**: does a guard-compliant all-sub-decile route exist within +2 hops, per pair × depth | `headroom.json`, `headroom_v2.json` |
| `draw_pairs_v2.py` | the DD-P1 re-draw, with headroom as a **draw-time precondition** | `pairs_v2.json` |
| `dd_p3_review_probes.py` | **DD-P3**: the analyst's probes (written by the review, not by the executing session) | *(stdout)* |
| `dd_f1_provenance.py` | reproduces DD-F1's band series and named sub-decile degrees | `dd_f1_provenance.json` |
| `dd_d6_gap.py` | **DD-D6**: the ceiling probe — is DD-C1 reachable at *any* strength | `gap_paths.json`, `gap_result.json` |
| `run_arms_t3.py` | **DD-P4**: walks P, DD-A1, DD-A2, DD-A3 over 12 scored pairs + 4 unscored anchors | `t3_paths.json` |
| `score_t3.py` | the pre-registered scorer, DD-C1–DD-C6, analysis set | `t3_scores.json` |
| `score_t3_supplementary.py` | held-out confirmation and the descriptive anchor table — **neither is a criterion** | `t3_supplementary.json` |
| `dd_p3_harness_probes.py`, `dd_p3_harness_probes2.py` | **DD-P3 second half**: the harness review's probes (written by the review) | *(stdout)* |

`DD-P3-analyst-review.md` (protocol) and `DD-P3-harness-review.md` (harness) are the two halves of DD-P3. `gap_fame.json` is fame resolved by
the committed `fame.py`; `fame_run.log` is its network run.

All scripts are run from `api/` (the mirror imports `artistpath_api`):

    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u <script>

`PYTHONIOENCODING=utf-8` is not optional here — several drawn endpoints carry non-Latin
names, and reading any JSON in this directory without an explicit `encoding="utf-8"`
dies on cp1252.

## What is imported, not reimplemented

- the walk — `../2026-07-24-track2-arm-scorer/run_arms.py::walk`
- the cost mirror and `pctl` — `../2026-07-23-track2-sweep/mirror.py`
- fame resolution — `../2026-07-24-track2-arm-scorer/fame.py` (A11's encoding, and its
  name-keyed **cache** with an mbid-keyed **join**, which is P8b F8's rule, not a defect)

The one deliberate exception is `dd_d6_gap.py`'s `min_pctl_path`, which computes the
`w → ∞` limit directly rather than through the device. That is the point: the ceiling it
measures must not depend on DD-P4's implementation, so a bug in the toll can neither
flatter nor spoil it.

## What this directory cannot conclude

- **Nothing about superstar journeys being unimprovable.** DD-F1 shows superstar
  endpoints have no edges below the top decile, which licenses *"cannot be routed through
  an all-obscure interior"* and **not** *"cannot be made more obscure at all"*. The
  second is unmeasured.
- **Nothing comparable to Track 2's figures.** The pair set differs by design and, after
  the DD-P1 re-draw, differs a great deal more. What transfers from Track 2 is the
  threshold; what does not is the prior probability of reaching it.
- **Nothing about what a user would actually experience in aggregate.** The selection
  effect is bounded against a uniform draw from the popularity bands, not against
  journeys anyone requests — there is no request log.
- **Nothing about coherence.** DD-C4 is a reported tripwire; the record says offline
  coherence metrics were the worst predictors of the owner's verdict, so the blind listen
  remains the only coherence instrument this project trusts.
