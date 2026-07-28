# ASC-5 discharge — path-level ascent, and the X-vs-A7 isolating contrast

**Role: ACTIVE analysis record. Owns its figures.** Decision rules in this file are
committed **before** the measurement script runs, per the precedent of
`2026-07-25-ceiling-ordering-headroom/` (rule committed at `0e39522`) and
`2026-07-26-obscure-pair-deliverability/` (rule committed at `8aa6f84`). The git history
of this README against its outputs is the evidence of ordering.

**Commissioned by the owner unpausing path-quality work on 2026-07-28**, with the goal:
more obscure / fewer very-famous artists in path interiors, especially under bypass.
This measurement is the cheapest decisive step named in the record —
`findings/2026-07-25-router-ascent-gradient.md` **ASC-5** — and it gates how the parked
builder-side p99 rescale may be pre-registered (that document's §6: a fame-scored
criterion without this answer risks "the third fame-scored null in a row").

**What decision this changes.** Two, both design decisions for the next intervention:
(a) whether the rescale's pre-registration may carry a fame-scored primary criterion,
and (b) whether the next designed intervention is jump-term-directional or
similarity-side. If neither read below would change those, this directory should not
exist.

**Nothing runs an experimental arm.** Inputs are the committed Track 2 stage-1 walks
(`../2026-07-24-track2-arm-scorer/paths.json`, all 11 arms), the committed scores
(`scores.json`, same directory), and the adopted artifact
(`graph-t15-tiebreakfix.bin`, sha256 asserted `4cb84ef9…`). The only new computation is
(1) one-hop local-preference arithmetic in the exact shape of the P8b review's Q5, and
(2) breadth-first-search geodesics used as a **structural null**, the same class of
null as Q5's edge base rate. No fame is fetched; fame figures are read from the
committed `scores.json` only. No adoption, no rebuild, no blind listen.

**Currency notice.** All fresh figures here are in **in-graph popularity percentile**
(`pctl`, average-rank per P6) or **pop_raw** — never fame. Phase 1 log §2.11: at the
top of the distribution popularity is not fame. The one fame-currency figure here
(PLA-R4a) is a subtraction over the committed fame-scored `scores.json` and is exact
per P8b F9 (the P term cancels cell-wise).

Identifiers are namespaced **`PLA-n`** (path-level ascent) — verified unused across the
repository before allocation.

---

## Instrument gates — failure voids the run, and is not a finding

- **PLA-G1 (reproduction).** The one-hop recompute must reproduce the P8b review's
  committed A0 and X ascent fractions (0.8261, 0.8687) and the null (0.4998) to four
  decimal places. If it does not, the instrument differs from the one the record
  trusts, and no other figure from this directory may be read.
- **PLA-G2 (identity).** Artifact sha256 must equal
  `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` and must equal
  `paths.json`'s recorded `artifact_sha256`. Asserted in-script.
- **PLA-G3 (interior sanity).** No delivered interior may have degree 1 at the cell it
  is read from (`DRV-4`: structurally impossible). Any occurrence means extraction is
  wrong; the run is void.

## The measurements and their pre-committed reads

### PLA-R1 — does the climb survive to the journey?

*(Plain: does the journey the app builds pass through more popular artists than the
map itself forces any short route to pass through?)*

**Measured:** for arm P at depth 0, per pair: median popularity percentile of the
delivered path's interiors. Null, per pair: the median percentile over **all interior
nodes lying on any minimum-hop path** between the same endpoints (dist_A(v) +
dist_B(v) == dist(A,B), endpoints excluded). Pairs with geodesic distance < 2 are
excluded from this read (no geodesic interior exists); the exclusion is reported.

**Statistic:** `D` = median over included pairs of (delivered interior median pctl −
geodesic interior median pctl).

**Read — thresholds fixed now:**
- **D ≥ 0.10** (ten percentile points): the climb is a *routing choice* visible at
  path level. ASC-1 reaches the journey; a pricing account of famous interiors stands.
- **D ≤ 0.03**: ASC-3 **collapses at path level** — the interiors the router delivers
  are roughly what any short route between these endpoints forces, and the famous
  middles on first paths are arithmetic, not pricing. A fame-scored criterion on the
  rescale would then need a mechanism argument that does not rest on ASC-1.
- **0.03 < D < 0.10**: ambiguous band, read as *weakened, not settled*, and said so.

Rationale for the sizes: 0.10 is ten percentile points — smaller than the stratum
gaps the Phase 1 log describes, large enough that a user browsing interiors would meet
a different artist population; 0.03 is within what tie-breaking and path-length
differences plausibly produce with no preference at all.

### PLA-R2 — context figure, not a gate: where the bypass ladder lives

*(Plain: after twenty presses of "I know them", how deep into the popularity ordering
has the journey's middle actually gone?)*

**Measured:** for arm P, interior median and minimum pctl per snapshot depth
d ∈ {0,1,2,3,5,7,10,15,20}, pooled over pairs with cells at that depth. Reported as a
table. **No decision hangs on this alone** — it is the user-facing restatement of the
problem the owner named, in this directory's own units, and it calibrates what "moved"
would look like for any future arm. (The fame-currency depth gradient is already owned
by `scores.json` — C3, production fails at 0.164 against 0.5 — this is the popularity
half, measured fresh here.)

### PLA-R3 — the one-hop isolating contrast: X vs A7

*(Plain: two settings differ only in whether moving between fame levels costs anything
at all; does removing that last price change how often the cheapest next step climbs?)*

**Measured:** one-hop cheapest-neighbour ascent fraction, Q5's exact method (ties →
lowest CSR index; floor term dropped as in Q5; documented there), for: the null, A0,
**A7** (`1.5·(1−s) + 0.3·jump_scale_pctl·|Δpctl|`, mirror.py:180-183's mean-matching),
and **X** (`1.5·(1−s)`, jump unpriced). X's isolating baseline is A7 — one column
(`w_jump` 0.3 → 0.0), per `arms.py`.

**Statistic:** `Δ` = ascent(X) − ascent(A7).

**Read — thresholds fixed now, calibrated to the committed A0→X span (+0.0426):**
- **|Δ| ≤ 0.02**: the jump price at A7's dilution is not a material brake on the
  climb. Combined with X being the pure-similarity cost, the climb is carried by the
  **similarity term** — ASC-4 supported at one-hop; the repricing axis is closed at
  the local level and the next intervention is similarity-side.
- **Δ ≥ +0.05**: the jump term is a real brake even at 0.3× diluted; a *directional*
  jump price (never tested — every arm's jump term was symmetric) is a live candidate.
- **Δ ≤ −0.05**: the jump price *promotes* climbing; mechanism check required before
  any design uses this.
- Otherwise: ambiguous band, stated as such.

### PLA-R4 — the path-level X-vs-A7 contrast, from committed data only

*(Plain: across whole journeys with up to twenty bypasses, did those same two settings
deliver middles of different fame?)*

**(a) Fame currency, exact, no fetch:** from committed `scores.json`,
`C1_mean(X vs P) − C1_mean(A7 vs P)` — the paired X−A7 contrast (exact per F9).
**(b) Popularity currency, fresh:** interior median pctl at C1 depths (d ≥ 10) for X
and A7 from `paths.json`, paired over shared cells.

**Read — thresholds fixed now:**
- **|X−A7| ≤ 0.1 log10** on (a): the jump price is immaterial at path level as well —
  with PLA-R3's first branch, the repricing family is closed at both levels for this
  goal, and the intervention space narrows to similarity-side (builder rescale, or a
  directional device priced on something other than |Δpop|).
- **|X−A7| ≥ 0.3 log10**: the jump term matters at path depth even though the sweep's
  symmetric repricing returned nulls; direction-of-sign decides which way.
- Between: ambiguous, stated.

**Run state presupposed:** every read above presupposes only the committed stage-1
data, which exists in full (11 arms, verified 2026-07-28). Nothing is owed after this
run for these reads to be readable. Stage-2 arms are not touched and not needed.

## What this directory cannot conclude, fixed in advance

- Nothing about **fame** from any fresh figure here (currency notice above).
- Nothing about whether the rescale **works** — only how its pre-registration may be
  scored and where the next design should aim.
- Nothing about the **degree-floor** question (`2026-07-26-RESUME-BRIEF` §1–§2): that
  is the low-*degree* axis; this is the fame/popularity axis. Degree ≠ popularity ≠
  fame (§2.6, §2.11, §2.12).
- A one-hop statistic is local preference, not a path property (ASC-5's own caveat);
  that is exactly why PLA-R1/R4 exist alongside PLA-R3.

## Outputs

`asc5_path_ascent.py` → `asc5_path_ascent.json` (all figures) and `REPORT.md` (the
deliverable). Run from `api/`:

    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        ../builder/analysis/2026-07-28-asc5-path-ascent/asc5_path_ascent.py
