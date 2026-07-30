# What the source algorithm's parameters actually mean — read from ListenBrainz's own code

**Role: AUTHORITATIVE for the semantics of the `algorithm` string's parameters; OWNS ONE
MEASUREMENT SERIES** — the candidate-list-length table, whose figures live in
`../../../builder/analysis/2026-07-30-lb-source-semantics/` and are cited here, not
restated elsewhere. Identifiers **`LBS-`**, collision-checked. Written 2026-07-30, before
the Track B (cap-selection simulation) design, which should cite this document rather
than re-derive any of it.

**What this changes: interpretation only.** No default, no code path, no decision. The
closed enum (`CS-P0e`), `MKS-5b`, and the parked `ALG-B` adoption are all untouched.

## Sources, ranked

1. **`listenbrainz_spark/similarity/artist.py` at `metabrainz/listenbrainz-server`
   master** — the Spark job that generates the similar-artists dataset our crawls
   consume. Fetched 2026-07-30; the parameter docstrings and SQL quoted below are
   verbatim. This is the authoritative source: it is the code that computed every score
   in our archives.
2. **A forum comment by rob (LB staff), 2024-02-07**
   (`https://community.metabrainz.org/t/how-does-similar-artists-work/678642/3`) — the
   mechanism outline that prompted this note. Useful, and **wrong in two particulars
   the source corrects** (`LBS-2`, `LBS-6`). A staff comment eighteen months older than
   the code loses to the code.

## LBS-1 — how a score is built (mechanism, from source)

Per user, listens over the trailing `days` window are split into **sessions**. Within a
session, every pair of listens whose artists differ **and whose artist credits differ**
contributes `s1.similarity × s2.similarity` to that artist pair, where `similarity` is
1 for a main artist and **0.25 for a featured artist** (`FEATURED_ARTIST_WEIGHT`). Each
user's total for a pair is capped at `contribution` (`LEAST(SUM(similarity),
{max_contribution})`), the capped per-user totals are summed across users and cast to
integer, pairs at or below `threshold` are discarded (`HAVING score > {threshold}` —
strictly greater), and each artist's surviving pairs are ranked by score for the
`limit` cut.

Two consequences already in our record are confirmed at the source: the score is
**symmetric by construction** (pairs are stored lexically ordered — there is no
directed score anywhere in the pipeline), which is what `CS-P0f` measured; and
same-credit collaborations never pair, so an artist is never "similar" to its own
credit.

## LBS-2 — the parameter table

Docstring lines quoted verbatim from `main()`; the operative SQL from
`build_sessioned_index()`.

| token | source definition (verbatim) | operative detail |
|---|---|---|
| `session_based_days` | "the number of days of listens to consider for calculating listening sessions" | `from_date = today − days`. Production's 7500 ≈ 20.5 years — effectively all history. |
| `session` | "the max time difference between two listens in a listening session" | **The unit is seconds.** `difference` is computed from epoch-second timestamps minus track duration in seconds, so `session_300` means a session survives gaps of up to **5 minutes** between the end of one listen and the start of the next. rob's comment says "a window of 300 minutes"; the code says otherwise. |
| `contribution` | "the max contribution a user's listens can make to a recording pair's similarity score" | `LEAST(SUM(similarity), {max_contribution})` grouped by **(user, pair) over the whole window** — a per-user cap, applied once per pair across all of that user's sessions. **This is the anti-repeat-listening device**, and it is the single token that separates `ALG-B` (3) from production (5). |
| `threshold` | "the minimum similarity score for two recordings to be considered similar" | `HAVING score > {threshold}` — strict, on the integer-cast cross-user sum. |
| `limit` | "the maximum number of similar recordings to request for a given recording (this limit is instructive only, upto 2x number of recordings may be returned)" | `rank() OVER (PARTITION BY mbid0 ORDER BY score DESC)` then `WHERE rank <= {limit}` — a top-N on the **lexically-first** member of each pair. See `LBS-3` for why "up to 2x" is exactly what we observe. |
| `skip` | "the minimum threshold in seconds to mark a listen as skipped" | A listen is excluded when the next listen starts more than `skip` seconds before this one would have ended (`skip_threshold = −skip`). `skip_30`: tracks abandoned >30 s early contribute nothing. |
| `filter` | **Undefined.** | Current master's own algorithm-string builder emits **no `filter` token at all**, yet five of our six permitted values carry `filter_True` — so the deployed dataset predates master, and the token's meaning is unrecoverable from current source. **Left open deliberately: it cannot bear on the `ALG-B` decision**, because `ALG-B` and `ALG-E` both carry `filter_True` and differ only in `contribution`. |

## LBS-3 — `limit` is the list-length knob, and the "2x" clause reconciles the data

`ALG-C` is the only permitted value with `limit_50`. If `limit` were a hard list-length
cap its lists should stop at 50; if it were a score cap they should look like everyone
else's. Measured over the committed AS raw records (200 artists × 6 arms, no new
requests — script and output in
`../../../builder/analysis/2026-07-30-lb-source-semantics/`):

**`ALG-C`'s lists have median 100 and max 100 — indistinguishable from the `limit_100`
arms.** That looks like evidence that `limit` is not a list cap, and an earlier read in
this session said exactly that. The source's own caveat — "this limit is instructive
only, upto 2x number of recordings may be returned" — is the reconciliation: the top-N
is computed per **lexical partition** (`PARTITION BY mbid0`), so serving "similar to X"
plausibly unions X's own partition (≤ limit rows) with rows where X is the
lexically-second member of pairs ranked in *other* artists' partitions (up to ~limit
more). 2 × 50 = 100, which is precisely `ALG-C`'s ceiling. *The partition explanation
is inference from the quoted SQL; the 2x clause and the measured ceiling are not.*

**Operationally nothing moves:** every arm's observed ceiling is 100, so the k-sweep's
natural ceiling of `k = 100` stands, and `NEXT.md`'s closed item ("do not propose
raising the candidate-list length — not possible") stands with its mechanism intact.
Why the `limit_100` arms never show the 2x slack (max 200) is unexplained — most
plausibly an endpoint-side cap at 100 — and is not worth chasing: no permitted value
could exploit it.

## LBS-4 — why lowering `contribution` thins obscure artists' lists (labelled inference)

*Inference from `LBS-1`/`LBS-2`, for the Track B design to use as orientation — it is
not evidence and must not be cited as a measured result.*

A pair's score is the sum of per-user contributions, each capped at `contribution`. So
lowering the cap from 5 to 3 compresses exactly the pairs sustained by **few devoted
listeners** while barely touching pairs supported by **many casual ones** — the score
shifts from "how much do fans co-listen" toward "how many distinct people co-listen."

In plain terms: under production, two artists stay connected if **three** people ever
listened to both in the same sitting (3 users × cap 5 = 15 > 10); under `ALG-B` it
takes **four** (3 × 3 = 9 fails the strict threshold; 4 × 3 = 12 passes). An obscure
artist's connections are mostly the few-devoted-listeners kind, so raising the
distinct-listener bar is precisely a supply cut at the obscure end — which is the
mechanism-shaped hole in `RC-R1` (stranding measured as supply, cause unexplained).
The derivation assumes non-featured credits (weight 1); featured pairs need more
listeners still.

## LBS-5 — corrections to standing paraphrases, none of them figures

- **The owner's working note read `limit` as the per-session score cap.** Per source
  that job belongs to `contribution` (per **user**, not per session), and `limit` is
  the instructive top-N. The confusion is rob's comment's fault — see `LBS-6`.
- **"Session = 300 minutes" (rob, echoed in the working note) is wrong per source:**
  300 **seconds**. A session is listening with no 5-minute silence, not a 5-hour
  window.
- The algorithm-selection handoff recorded that the forum's `contribution` mapping
  "does not cleanly match the parameter" and left it open. **Resolved here**: the
  forum comment conflated `contribution` with `limit`, and this document supersedes
  every earlier paraphrase of the parameter semantics.

## LBS-6 — where the staff comment and the source disagree

rob's comment says a repeat-heavy session "is capped at 50 counts contributed by this
session." Current master caps at `contribution` (5 or 3 in every permitted value), per
**user over the whole window**, not per session — and no permitted value carries a cap
of 50 anywhere except `limit_50`, which does something else entirely. Either the code
changed between 2024-02 and now, or the comment was loose; unresolvable from outside
and not worth resolving. **Recorded so nobody re-imports the comment's numbers over
the source's.**
