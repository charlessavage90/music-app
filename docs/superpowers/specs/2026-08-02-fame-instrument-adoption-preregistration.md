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
