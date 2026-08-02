# Fame-instrument adoption pre-registration — ListenBrainz listener counts as the fame ruler

**Role: GOVERNING pre-registration for the fame-instrument adoption. Identifiers `FAM-`,
collision-checked against the repository 2026-08-02 (no prior `FAM-` exists).** Committed
before any validation figure exists; the git timestamp is the evidence. Amendments, if any,
are appended as `FAM-AM1`… under §8 and never rewrite a committed section.

**What this decides:** whether ListenBrainz listener counts become the fame ruler for all
*future* offline evaluation criteria — in particular the cap re-evaluation
pre-registration, which waits on this. **What it cannot decide:** nothing here touches the
app, the router, telemetry, or any shipped code path; no prior result is re-read (owner
ruling, §0); no cap re-evaluation criterion is fixed here.

---

## §0 Owner rulings recorded (2026-08-02, conversation of record), before any figure

1. **The fame currency becomes ListenBrainz listener counts, MBID-keyed** — option (b) of
   the three presented (MBID-keyed Wikipedia / LB listener counts / hybrid), chosen with
   the caveats presented: weak agreement with Wikipedia, and the shared population blind
   spot. The hybrid was argued against (currency-splicing) and not chosen.
2. **No re-read.** Prior fame-scored results stand as recorded, in the currency they were
   measured in. Cross-era fame comparisons are barred. This was fixed *before* any number
   under the new ruler exists, per the standing rule that the re-read decision precedes any
   recompute.
3. **Sequencing: the instrument is fixed before the graph work.** The cap re-evaluation
   pre-registration is written only after this document's verdict.
4. **Why the ruler changes at all:** the cap re-evaluation's primary outcome is the bypass
   obscurity gradient (`REQ-42` shape — movement with depth, never band-reaching), and the
   incumbent ruler is measured blind on 38.7% of what a successful obscurity push would
   deliver (`FPC-9`). A gradient read on a ruler that saturates at "unknown" flattens
   exactly when an arm is working — measurement failure indistinguishable from arm failure.

## §1 The instrument, exactly

- **Source:** `POST https://api.listenbrainz.org/1/popularity/artist` (1,000 MBIDs per
  request), the endpoint `FPC-4` measured. The quantity read is `total_user_count` —
  **how many distinct ListenBrainz users have ever played the artist.**
- **Quantities and names (currency-in-the-name convention):**
  - `fame_lb_raw` — the integer listener count, per MBID. Never a rank.
  - `fame_lb_pctl` — percentile of `fame_lb_raw` **within the adopted 74,193-artist
    frame**, computed as average rank over ties divided by frame size, stated to be
    tie-stable and byte-reproducible. The frame is the adopted population (Track B
    precedent: band membership everywhere uses the adopted frame); artists outside the
    frame (candidate-only) receive the percentile their raw value would occupy in it.
  - Neither name collides with `pop_raw` / `pop_pctl` (in-graph popularity), which are
    untouched and remain the router's quantities.
- **Population: the union of both graph populations, 93,067 MBIDs** — adopted 74,193 +
  `ALG-B` 68,467 (overlapping), the same union and the same reasoning as the Deezer id
  map: fetched union-wide so the cap re-evaluation cannot trip a coverage condition
  mid-experiment. Union construction is reused from
  `builder/analysis/2026-08-02-dsp-ids/dsp_ids.py`; the `ALG-B` side is the 2026-07-30
  full build (manifest-verified before use).
- **Snapshot discipline:** one fresh fetch, one date, frozen. The output JSON is
  gitignored (size); its **sha256 is recorded in the findings document and a manifest
  sidecar**, the same treatment as graph artifacts. The 2026-07-30 partial snapshot
  (`fp_listenbrainz.json`, adopted population only, on disk uncommitted) is **retained as
  the stability comparator** (`FAM-5`) and never merged into the new snapshot — no
  splicing of two dates.
- **Nulls:** an MBID with no returned value is a visible null — excluded from paired
  reads, counted against `FAM-1`. Nulls are **not** scored at a floor; the incumbent's
  floor semantics do not carry over.

## §2 Held constant, and the hazards carried on the page

- **The shared population blind spot travels with every figure.** ListenBrainz and
  Wikipedia under-represent the same artists (~10× against outside references, one-pair
  measurement, 2026-07-30). Their agreement is a shared blind spot, not corroboration.
  The only validation here with a population outside both is `FAM-4`, which is why it is
  the load-bearing criterion.
- **Non-independence, quoted from the instrument's own header:** listener counts are
  "computed on the same corpus as the similarity edges, so unlike Wikipedia it cannot
  serve as an INDEPENDENT audit of our own popularity"
  (`fp_listenbrainz.py` docstring). For a *gradient* read this is mostly benign — the
  same-corpus bias moves both the graph and the ruler in the same direction — but any
  future claim that the graph "reaches the truly obscure" in some absolute sense cannot
  rest on this ruler alone. Carried, not fixed.
- **The drop rule cannot perturb this work.** Both drop lists remove MBIDs from builds;
  an MBID in the union that a build drops is a no-op for the ruler (same superset
  reasoning as the census and the Deezer map).
- **No dormant term.** The instrument has no weights and no interaction with `ApiConfig`;
  nothing here can switch itself on in a later experiment's successful arms. The one
  latent coupling — `fame_lb_pctl`'s frame — is fixed by name in §1 and any future change
  of frame is an amendment, never a silent recompute.

## §3 Validation criteria — bars fixed before any figure, plain sentence at definition

Each criterion carries its identifier, its bar, and its plain-language sentence, fixed
now. Owner-facing text quotes identifier **and** sentence together.

- **`FAM-1` — coverage.** ≥ 99.0% of the 93,067-MBID union returns a non-null value;
  reported separately for the adopted population and the `ALG-B`-only remainder, so a
  deader candidate tail is visible rather than averaged away. *Plain: the ruler gives a
  real number for essentially every artist either map could deliver.* (`FPC-4` measured
  99.94% on the adopted population; the union is the open half.)
- **`FAM-2` — tail resolution.** Within the adopted frame's lower half by `fame_lb_raw`:
  the largest single tied value holds < 5% of lower-half artists, and the lower half
  contains ≥ 1,000 distinct values. *Plain: in the obscure half — where the old ruler
  went blind — this one must actually tell artists apart, not hand thousands of them the
  same score.* This is the property the gradient measurement depends on.
- **`FAM-3` — top-end sanity.** Every artist on this fixed common-knowledge list sits at
  `fame_lb_pctl ≥ 0.99`: Radiohead, The Beatles, Metallica, Coldplay, Muse, R.E.M.,
  Pixies, PJ Harvey, Pink Floyd. (List fixed here, from names already in the project
  record; deliberately *not* the `acceptance.py` top-N-by-popularity set, which is
  derived from the same corpus and would be circular.) *Plain: the artists everyone has
  heard of all land at the very top of the ruler.*
- **`FAM-4` — hand-read concordance (load-bearing).** From the hand-read Spotify
  monthly-listener table in `findings/2026-07-25-bypass-depth-use-run.md`: take every
  pair of artists whose hand-read counts differ by ≥ 10× and whose identity the record
  does not flag as ambiguous (the `FERG`/A$AP Ferg class is excluded); the ruler must
  agree on the direction of ≥ 90% of those pairs. *Plain: where the owner's own hand
  reads say A is clearly bigger than B, the ruler almost always agrees.* Spotify's
  listener population is outside both ListenBrainz and Wikipedia, which is what makes
  this the criterion that can actually fail informatively.
- **`FAM-5` — snapshot stability.** Spearman ≥ 0.99 between the 2026-07-30 snapshot and
  the new snapshot on their overlapping non-null MBIDs. *Plain: two readings of the same
  instrument a few days apart must nearly agree, or the instrument is too unstable to
  freeze.*

## §4 Read rules, run state, and branches

- **Run state every read presupposes:** the union fetch is complete, its sha256 is
  recorded, and all five criteria are computed from that one frozen snapshot. No read is
  opened earlier; a partial fetch licenses nothing.
- **All five pass →** the instrument is **ADOPTED as the fame ruler for future offline
  evaluation criteria**. Consequences, all of them: the cap re-evaluation
  pre-registration is written in this currency; future fame-currency criteria inherit
  `REQ-Q1`'s conditions (reported all-interiors and matched-only; MBID-keyed frozen
  snapshots); and the `PRODUCT-REQUIREMENTS.md` Definitions edit is **proposed to the
  owner** — the deferral row's condition ("when, and only when, a currency decision is
  made") has fired, and the edit is his layer, drafted for him, never landed unilaterally.
- **Any criterion fails →** **no adoption, and no silent fallback.** The measured failure
  goes to the owner with options; substituting a different ruler (hybrid, Wikipedia,
  multilingual) without a new pre-registration is barred. Partial adoption ("use it only
  where it passed") is barred — that is the hybrid, argued against and not chosen.
- **A pass licenses nothing about coherence, validity, or absolute obscurity** — coverage
  and concordance are not correctness (`FPC-` §4's list carries over verbatim), and the
  §2 hazards travel with every future figure quoted in this currency.

## §5 Execution notes (controller + subagent division, per owner 2026-08-02)

- Controller (this session): this document, the reads, the per-task execution log, all
  owner-facing text. Subagents (Opus): fetch script and run, validation computation,
  tests, Snyk scan on new scripts. `ml-graph-analyst` critiques this design before
  results are acted on (its named trigger: adopting a ranking change).
- Scripts land in `builder/analysis/2026-08-02-fame-instrument/` (`fi_` prefix), reusing
  `fp_common.py` patterns (User-Agent, batching, resumable partials). Environment traps:
  `UV_LINK_MODE=copy`, `PYTHONIOENCODING=utf-8`, `python -u` for anything long-running.
  No archive access is needed, so `GRT-A1`'s read-only condition does not fire.
- Expected cost: ~94 requests for the union at 1,000 MBIDs/request; minutes, resumable.
  The ~3–4 h Wikipedia pageview build (`fp_fame_mbid --build`) is **not** triggered — its
  deferral condition ("if a currency decision adopts the MBID-keyed proxy") did not fire,
  and this document records that so nobody runs it by momentum.

---

## §8 Amendments

### `FAM-AM1` — design-critique corrections, appended 2026-08-02, before the union fetch

**Provenance and disclosure, first.** The `ml-graph-analyst` critiqued the committed
design before any run (its named trigger; critique and probes retained at
`builder/analysis/2026-08-02-fame-instrument/`). During that critique, **`FAM-2`'s
statistics were computed on the retained 2026-07-30 adopted-frame snapshot at the
controller's direction** (largest tie atom 109 artists = 0.147% of the frame, 0.294% of
the lower half; 1,334 distinct lower-half values — both pass the committed bars). No
named-artist value was read, so `FAM-3` and `FAM-4` remain blind; `FAM-1` and `FAM-5`
require the union fetch and remain unknown. **Every re-specification below is made with
`FAM-2`'s adopted-frame values known and says so.** The union fetch had not run when this
amendment was committed; the git timestamp is the evidence.

1. **`FAM-5` re-specified (critique A1 — the committed bar sat in a dead zone).**
   Simulated against the retained snapshot: a single overlap-wide Spearman ≥ 0.99 is
   satisfied even when every value ≤ 100 listeners is re-drawn as uniform noise (0.9991) —
   the tail, which is what the ruler is being adopted for, could be destroyed and the bar
   would pass. Replaced by: **Spearman ≥ 0.99 within each of the five `cb_metrics.BANDS`
   separately, AND 99th percentile of |Δ`fame_lb_pctl`| ≤ 0.01** on overlapping non-null
   MBIDs. *Plain: two readings days apart must nearly agree everywhere — including among
   obscure artists — and almost no artist may move more than one percentile point.*

2. **`FAM-2` re-specified (critique B1/B3 — the distinct-value bar tested the frame's
   median, not resolution, and its direction was perverse: a graph reaching obscurer
   artists would score worse on it with an unchanged ruler).** Replaced by:
   (a) largest `fame_lb_pctl` quantisation step (largest tie atom / non-null count)
   **≤ 0.005 overall and ≤ 0.005 within the bottom decile**; (b) top-5 tie atoms combined
   **≤ 2% of the lower half**; (c) the same statistics computed **on the `ALG-B`-only
   remainder** (critique C4) — the genuinely unknown 18,874 artists, measurable only after
   the union fetch. Adopted-frame values were known at re-specification (bottom-decile
   step 0.00147): the bars carry ~3.4× headroom and this is disclosed rather than hidden.
   *Plain: the ruler must not lump obscure artists into blocks — anywhere, including on
   the candidate data set's own artists.*

3. **`FAM-2`'s effect size (critique B2), resolved without breaking §0.3's sequencing:**
   the measured quantisation step (**0.0015**) is carried forward as a binding floor —
   **the cap re-evaluation's pre-registration must require any claimed gradient to exceed
   10× the ruler's measured quantisation step.** Recorded here so it cannot be quietly
   dropped there.

4. **`FAM-4` procedure and bars (critique A3/A4/A5), and WGLL bound-2 compliance.**
   (a) **Identity confirmation first:** before any ruler value for these artists is read,
   every hand-read artist is resolved to an MBID via the MusicBrainz disambiguation
   procedure (the `BYP-13` guard — the hand reads were Spotify *name* lookups, and the
   record holds a name-search for "Love" returning Sean Combs); unconfirmable rows are
   dropped and disclosed. This is the falsification test WGLL's second bound requires of
   a hand-read instrument inside a pre-registered criterion.
   (b) **Readability floor:** if fewer than 10 qualifying ≥10× pairs remain after
   confirmation, `FAM-4` is **UNREADABLE and adoption is blocked** — below 10 pairs the
   90% bar is arithmetically a 100% bar and cannot be read.
   (c) **Per-artist trace (A4 — 34 pairs from 15 artists is ~15 effective units, not 34):**
   failures are reported per artist beside the pair rate. One pre-committed exception: if
   all failing pairs share a single artist, that artist's hand read is re-verified; if its
   identity cannot be confirmed it is excluded with disclosure, and the remaining set must
   still pass both the 90% bar and the 10-pair floor.
   (d) **Resolution read added (A3 — the ≥10× gate cannot see sub-decade error: a ruler
   wrong by 3.2× on the typical artist passes it 92% of the time, by simulation):**
   **Spearman ≥ 0.8 over all confirmed hand-read artists**, using exactly the pairs the
   ≥10× filter discards — the only ones carrying resolution information. *Plain: beyond
   agreeing on the obvious gaps, the ruler must also broadly rank the full hand-read set
   the way the hand reads do.*

5. **`FAM-3` pass rule (critique B4/B5).** The nine-name list is unchanged (forward-only).
   Pass is now **≥ 8 of 9** at `fame_lb_pctl ≥ 0.99`, any miss reported with its value.
   Disclosed reason: three of the nine (R.E.M., Pixies, PJ Harvey) entered the record as
   reciprocity-collapse tracers — artists whose ListenBrainz candidate data is thin on the
   same corpus this ruler reads — so a single-miss auto-fail would block adoption on
   exactly the artists likeliest to be under-ranked for corpus reasons rather than fame
   reasons. `FAM-3` is also relabelled a **smoke test**: nine Anglophone rock acts are the
   population ListenBrainz over-represents, so no pass of `FAM-3` may ever be cited as
   evidence against the shared-population hazard in §2.

6. **The percentile definition, fixed exactly (critique C1/C2/C3):**
   `fame_lb_pctl(v) = (|{f < v}| + (|{f = v}| + 1)/2) / N_nonnull` — the denominator is
   the **non-null ranked population** (74,151 on the current frame), not the frame size.
   For `v` above the frame maximum, `pctl(v) = pctl(max)`. **"Lower half" means
   `{fame_lb_pctl < 0.5}`**, never a sorted-index split — 14 artists tie at the boundary
   value and membership must not depend on sort stability.

7. **Hazards added to §2, carried not fixed (critique D1/D2/D3/C5):**
   - **Vintage bias**: `total_user_count` is cumulative-lifetime, so at equal current
     popularity an older artist outscores a newer one — a gradient read cannot distinguish
     *less famous* from *newer*. No criterion here touches it.
   - **The ruler IS this snapshot**: the adopted object is the union fetch's dated file
     plus its sha256. Any re-fetch is a new instrument owing its own `FAM-5` and its own
     re-read decision under §0.2's rule.
   - **Scale sensitivity is non-uniform** — a 10× fame drop moves the percentile roughly
     3× more at the frame median than near the top. A **descriptive companion read** (no
     bar, labelled descriptive) is added: `fame_lb_pctl` by bypass depth over the retained
     Track 2 routed paths, to calibrate where production routing sits on this scale.
   - **The frame choice leaves a population-vs-descent confound to the cap
     re-evaluation's factor table**: an `ALG-B` arm's interior percentiles differ partly
     because the populations differ (measured on the adopted side alone: median
     `fame_lb_raw` 2,501 for adopted artists also in `ALG-B` vs 409 for adopted-only —
     6.1×). Named here so that factor table cannot omit it.

8. **Null rule for aggregate reads (critique D5), fixed here rather than downstream:**
   every aggregate in this currency is reported **all-interiors AND matched-only** (the
   `REQ-Q1` shape) with the **null count per depth**. A null is a hole in the denominator,
   not a floor value — and `FAM-1`'s bar permits up to ~931 union nulls, so without this
   rule an arm reaching null-rich territory would be *flattered* by a shrinking
   denominator. The dual report is what makes that visible.

**Not resolved by this amendment, deliberately:** critique A2 — no criterion validates
*ordering* in the obscure region itself (`FAM-4`'s hand reads all sit above 168k monthly
listeners). Whether to add a tail-ordering criterion (≈15 fresh owner hand reads from
`fame_lb_pctl < 0.25`, blind to ruler values, as `FAM-6` via a further amendment) or to
record tail ordering as **assumed, not validated** with its falsifier named, is the
owner's decision — it spends his time — and is put to him in the conversation of record.
