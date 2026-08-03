# Ruler-candidate shootout — scoring two fame-ruler candidates against the hand-read corpus

**Role: GOVERNING mini-pre-registration. Identifiers `RCS-`, collision-checked 2026-08-02
(no prior `RCS-` exists).** Committed before any candidate value is fetched; the git
timestamp is the evidence. Amendments append as `RCS-AM1`… and never rewrite committed
sections.

**Context and what this decides.** The `FAM-` pre-registration concluded **NO ADOPTION**:
ListenBrainz listener counts failed both hand-read concordance criteria (famous band
0.4915 vs ≥ 0.80; tail 0.4552 vs ≥ 0.70 — cited from `fi_read34.json` / `fi_read6.json`,
the reference rows for everything below). The owner chose (conversation of record,
2026-08-02) to score the two surviving candidates against the existing corpus **before
building anything**. This probe licenses at most the *writing of a full adoption
pre-registration* for a candidate. **It adopts nothing, changes no currency, and its
failure branches all return to the owner.**

## §1 The corpus (the truth side — already committed, no new owner time)

`fi_corpus.json` — 30 rows assembled by derivation from committed sources, no new
measurement: 15 **famous-band** artists (2026-07-25 hand reads, identity-confirmed in
`fi_fam4_identity.json`, FERG excluded, NOFX once) and 15 **tail** artists (the owner's
2026-08-02 checklist reads, committed `d318089`, identities fixed at draw time). Hand
values are Spotify monthly listeners and are the arbiter, per the corpus's own governing
documents. Three tail rows have hand value 0 (confirmed pages, zero listeners): they
enter rank correlations, and are excluded from ratio pairs only.

## §2 The candidates, exactly

- **`W` — MBID-keyed English Wikipedia pageviews.** Resolution MBID → Wikidata (`P434`)
  → EN article → pageviews over the **same trailing window as the adopted proxy**
  (mirror `fp_fame_mbid.py`'s window; read it, do not re-derive). No article → **null**
  (visible; there is no floor score in this probe). WDQS batch for all 30; per-artist raw
  responses committed.
- **`D` — Deezer fan counts (`nb_fan`)** via `GET https://api.deezer.com/artist/{id}`.
  Two identity tiers, pre-committed: **tier 1** — the id recorded in MusicBrainz
  (`dsp_ids.json`; identity guaranteed by the id path). **Tier 2** — name-resolved by
  Deezer search, accepted only with corroborating evidence against the MusicBrainz
  identity (discography or release-title match; era; country), every acceptance
  documented with its evidence, unresolvable → **null**. Tier is recorded per row and
  every figure is reported both pooled and tier-1-only. A page with `nb_fan` 0 is a
  value, not a null.

## §3 Disclosures at design time (known before any candidate value exists)

- The LB reference figures above are known and committed.
- The hand corpus is committed and public in the repo; it is the arbiter, not a result.
- **Deezer tier-1 coverage of the corpus is known: famous 15/15, tail 4/15.** Without
  tier 2, `D`'s tail read would be unreadable before it starts — that is why tier 2
  exists and why its acceptance procedure is fixed here rather than improvised later.
- Wikipedia's tail coverage of the corpus is **not** known per-artist, but the graph-wide
  expectation is low (`FPC-3`: 27.4% EN-article coverage in the lower half), so a
  tail-unreadable outcome for `W` is anticipated as likely and its reading is
  pre-committed below rather than decided after.
- No candidate value for any corpus artist has been looked up by anyone on this project.

## §4 Reads — bars fixed now, one read per candidate per region

Per candidate, per region (famous / tail, 15 corpus rows each):

- **Readability floor: ≥ 12 non-null scored rows in the region**, else that region is
  **UNREADABLE** for that candidate — reported with its null count, never as a pass or
  fail. *(Same floor logic as `FAM-4`/`FAM-6`, for comparability.)*
- **`RCS-1` (famous): Spearman ≥ 0.80** against hand reads — the bar LB failed at 0.4915.
  *Plain: where the owner's July reads say who is bigger, the candidate must broadly
  agree, at least as well as we demanded of the ruler that just failed.*
- **`RCS-2` (tail): Spearman ≥ 0.70** against hand reads — the bar LB failed at 0.4552.
  *Plain: same test, in the obscure quarter the whole exercise exists for.*
- **Descriptive companion, no bar:** direction agreement on ≥ 10× hand-value pairs
  (rows with hand 0 excluded from pairs only), reported per region beside the LB
  reference values.

**Decision rules, all fixed now:**

1. A candidate **readable and passing both regions** → licenses writing a full `FAM-`-style
   adoption pre-registration for it (graph-wide coverage, tail resolution, snapshot
   discipline, null rules — all of which this probe deliberately does not test). Nothing
   more.
2. A candidate **passing famous with tail UNREADABLE** → licenses a famous-band-validity
   claim only; the tail question returns to the owner carrying the measured null counts.
   No full pre-registration is licensed on famous-band evidence alone.
3. A candidate **failing a readable region** → dead for that region's ordering claim; any
   future proposal for it must bring new grounds, not a re-run.
4. **Both candidates tail-unreadable or tail-failing** → the pre-committed reading is
   "no measured candidate orders the tail", and the instrument question returns to the
   owner with that sentence — the two-currency design his `FAM-` conversation set aside
   becomes a live option only by his choice, never by a session's.
5. Ties are broken by nothing: if both candidates pass everything, **both** results go to
   the owner; choosing between them is a construct decision (written-about-ness vs
   streaming-public attention), which is his column.

## §5 Execution notes

Scripts in `builder/analysis/2026-08-02-fame-instrument/` (`rcs_` prefix), no CLI path
arguments, raw responses committed (30-row scale), Snyk scan after. Deezer API is
unauthenticated and rate-limited: be gentle (≤ 1 req/s), and it serves `nb_fan` on the
artist object. WDQS: batch query, standard user agent. Environment traps as ever:
`UV_LINK_MODE=copy`, `PYTHONIOENCODING=utf-8`, `python -u`. The controller reads results
against the bars; the executor reports figures without verdicts.

## §6 Amendments

### `RCS-AM1` — recording-title corroboration for the five blocked rows, appended 2026-08-02 AFTER results existed

**Post-result, and the hazard is stated plainly and permanently:** when this amendment
was decided, `D`'s figures were known (famous 0.7560 failed; tail unreadable at 10/15),
the five rows' candidate `nb_fan` values were visible in the retained search responses,
and widening moves `D`'s tail count across the readability floor in the known-helpful
direction. The executor refused to widen mid-run for exactly this reason; **the owner
ruled to widen** (conversation of record), the `FAM-AM2` class of decision.

**Why the widening is principled rather than convenient:** §2's tier-2 corroboration
required a MusicBrainz *release*-title match, and the five rows (Muelas de Gallo, Jess
Okoro, Acer, DTX, Dorona Alberti — this list is closed) have **zero releases**; each is a
recordings-only artist, so the committed check's truth side is structurally empty. The
check failed for a reason unrelated to what it exists to test. Recording titles are the
same evidence class — works the artist is actually credited on.

**Procedure, fixed before any match is computed:** for each of the five, browse the
artist's MusicBrainz **recordings** (the truth side that exists); Deezer candidates are
the **exact-normalised-name** matches already present in the retained search responses
(no new search); fetch each candidate's track titles (top tracks and album tracks);
normalise (casefold, strip punctuation and whitespace); **accept iff ≥ 1 exact
normalised recording-title match**. Multiple matching candidates → the one with the most
matches; a tie → reject as ambiguous. No match anywhere → the row stays null, reason
recorded, final — there is no third widening. Every acceptance carries its matched
titles as evidence.

**Re-read:** `RCS-2`'s bar and floor are unchanged (Spearman ≥ 0.70, ≥ 12 non-null). The
AM1 tail read is reported **beside** the as-committed one, both permanent; the
as-committed unreadable result is not erased. The famous-region result is untouched by
this amendment and its FAIL at 0.7560 stands.
