# Retained execution log — tag discrimination probe (`TAS-`), 2026-07-30

**Role: RETAINED EXECUTION LOG. Owns no figures.** Criteria figures belong to
`builder/analysis/2026-07-30-tag-discrimination/` and the findings document written when
the probe completes; scoring and path-quality figures stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited here, never restated.

Governing document: [`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md).
Plan: [`plans/2026-07-30-tag-discrimination-probe.md`](plans/2026-07-30-tag-discrimination-probe.md).
Handoff: [`2026-07-30-HANDOFF-tag-discrimination.md`](2026-07-30-HANDOFF-tag-discrimination.md).

**Scope reached: Tasks 1–7 of 8, across three sessions. Only Task 8 (the findings document
and the owner-facing read) is unrun.** Each session's work is appended rather than folded in,
so the three stay separable: **§1–§8** are the first, **§9–§14** the second (Task 4, Task 7's
selection halves, `TAS-AM3`, `TAS-AM4`, closeout), **§15–§16** the third (the Discogs
attribution correction, the rarity-weighting diagnostic, and `TAS-R1`–`TAS-R4` on the routing
side).

**The routing-side plan is a separate document** —
[`plans/2026-07-31-tas5-routing-execution-plan.md`](plans/2026-07-31-tas5-routing-execution-plan.md)
supersedes the original plan's Tasks 5, 6 and Task 7's routing halves; see §16.1 for why.

---

## §1 What the owner asked for, and how the question changed under it

He asked to continue investigating tag-aware neighbour **selection at build time** — the
third coherence strand parked in `NEXT.md`. Three of his interventions changed the design
materially, and each is recorded because the reasoning does not survive in the diff.

**§1.1 The goal is coherence, not obscurity.** Chosen explicitly. This is what makes the
whole track evidence-poor: the two metrics ever built to judge flow were the worst
predictors of his verdicts (Phase 1 §3.8), the tag instrument that might have replaced them
was killed the previous night (`COH-2`), and spending tags on *construction* spends them as
an *evaluator*. **There is no offline scoreboard for this track and cannot be one.** Every
other track here ends in a recommendation; this one ends at a listening test or nowhere.

**§1.2 "Will this run on the full 100 or the 50 cap?"** The literal answer is that ranking
already spans the full pre-cap list (`graph.py:106–110` sorts every candidate, then takes
50), and that this is the *only* reason the device can do anything: reordering within the
surviving 50 is a no-op, since the resulting *set* becomes the edges. All effect comes from
candidates crossing the 50 line.

His deeper argument — the cap was itself a coherence device, so tags might let it loosen —
was **half right, and the half that is right favours him**: the blind listen that adopted
`capfix` fixed the *rule* (mutual k-NN, p99 clip, damping 0), **not the bound of 50**, which
was inherited from the config default. Less stands behind that number than "the cap was
blind-listened" implies.

**§1.3 Why no arm runs at bound 100, decided against his initial vote.** He voted to test
both bounds. Ranking is **provably never consulted** at k = 100: the source caps candidate
lists at 100 (`CS-P0e`), so top-100 of a ≤100 list cuts nothing and the sort result is
discarded. Track B proved this byte-identically without setting out to — `PS100` ≡ `MK100`
on both archives (`LBS-3`), two *different ranking rules* producing one graph. A λ sweep at
bound 100 would be a column of identical graphs. He accepted this and the vote changed.

**What survives of his argument, and it strengthens:** at a loose bound the only thing still
pruning is the **mutual requirement** — the mechanism he has been questioning. Track B's
`R1a` isolated reciprocity at k = 100 and returned **null on both archives**. Parked as a
separate experiment at his instruction (spec §7), explicitly not ruled out.

**§1.4 "Can the router favour higher-ranked neighbours instead?"** A better idea than the
build-time design on cost — no rebuild, reversible, context-aware, and it does not retire
every existing path-quality figure. Against it: **this router has ignored three consecutive
pricing changes** (Track 2's repricing family, Track 3b's toll, Track B's `R2` quota edges
present-and-declined), while structural changes have moved things. That asymmetry is now a
standing caution inside `TAS-5` so a null there cannot be misreported as "tags do not work".

Resolved by **not choosing**: the architecture question is left open for the probe to inform,
which is why the probe measures both selection (`TAS-4`) and routing (`TAS-5`).

---

## §2 Defects found in the plan itself

Four, all in documents this session wrote, all found by the plan's own
verify-against-source steps. **None would have raised an error.** Each is the project's
characteristic failure — confident prose about correct code — and the tally is the argument
for keeping those steps as checkboxes rather than assumptions.

| # | The plan said | What was true |
|---|---|---|
| 1 | `neutral_for` medians each candidate against the first candidate | Must be against the **artist**. A different quantity, and not the one §1 defines. Its test only asserted non-`None`, so it would have passed. |
| 2 | The Wikidata half of the vocabulary is already on disk | **Wrong twice.** `fp_wikidata.json` holds item presence (`qid`, `wikis`, `enwiki`) and *no genres*; `ct_wikidata_genres.json` holds genre **counts**, not labels, because `COH-1` only needed presence. **P136 labels were never persisted.** Unfixed, `label_sets()` would have silently returned half-labelled data for the whole graph. |
| 3 | `graph.neighbours_of_index` / `neighbours_with_scores` | Neither exists. `artifact.deserialise` returns raw CSR arrays with no per-node accessor. |
| 4 | The P136 guard need only check the file **exists** | A partial frame reads as "these artists have no genres" — silent and wrong. Now checks coverage of every graph node. |

Defect 3's fix improved the design rather than merely repairing it: `TAS-1/2/3` and `TAS-5`
now read the graph through the API's `GraphStore`, one code path, so a disagreement between
the coverage measurement and the routing measurement is structurally impossible.

---

## §3 Decisions taken, with reasoning

**§3.1 Keep P136 rather than drop it to save an hour.** Tempting argument against: its
coverage is concentrated in the obscure tail, where the actuator is silent anyway. Wrong in
the case that matters — agreement needs labels at **both** ends, and the candidates a
binding (famous, long-listed) artist chooses between include obscure ones. P136 labels there
are what make a famous→obscure pair *resolvable* rather than neutral, which is the
population `TAS-6` guards.

**§3.2 A new collector rather than editing a frozen probe.** `ct_wikidata_genres.py` is
committed `COH-` work; editing it to serve a later question is how a record stops
reproducing what it claims to have measured. `tas_wikidata.py` is new.

**§3.3 The neutral rule is per-artist, and it is the one dormant term.** Median agreement
between the artist and its **own** labelled candidates, never zero — zero is a positive
claim of dissimilarity, and applying it to missing data would demote unlabelled candidates,
which are disproportionately obscure. Per-artist rather than a global constant because
agreement levels vary by artist. It is **inert at λ = 0 and active in every arm**, the same
shape as `w_floor` in the Track 2 pre-registration's §0, so it is pinned by test and any
finding must be reported as "λ **and** the neutral rule".

**§3.4 Escalated one question to `ml-graph-analyst`, and declined to escalate two.** The
cheap filter closed the other two: bound-100 inertness was already derived with an
independent witness, and the per-artist median's rank-neutrality was worked out and held.
The one dispatched — the conversion from per-artist swaps to built-map change — was not
arithmetic already written down, and its answer changed a committed gate. **See §4.**

**§3.5 Did not change `testpaths`.** All 34 analysis tests pass, so adding `analysis` would
work, but it changes what every builder `pytest` run collects and is beyond the task.
Deferred by the owner with a condition (§6).

---

## §4 Corrections to the record made by this session

**§4.1 `TAS-4`'s original bar was withdrawn as false, before it ran** (`TAS-AM1`). Three
independent findings from the `TD-` derivations, each sufficient on its own:

- Mutual selection does **not** amplify deletions as suspected (≈1.07×) — but every swap
  also *promotes* a neighbour, and per-artist swap counting never saw the creations. The
  conversion is ≈2.11×, linear over the observable range, stable across placement and
  endpoint-correlation regimes and two archives. The old bar admitted ~8.4% of the map
  differing as a "kill".
- The **median** reads 0 while 6.3% of the map moves, because the device is inert wherever
  labels are missing — the zero-inflated case `TAS-1` exists to expect, not a corner case.
- The defence for a permissive bar was **refuted with the sign reversed**. Journeys route
  through connections sitting *deeper* in both endpoints' lists than average, so they are
  deleted at 1.09–1.26× the population rate, never below 1.0. The analyst proposed that
  hypothesis and then killed it.

The withdrawn plain sentence is **kept in the document, marked false**. A
pre-registration's value is that its errors stay visible.

**§4.2 `TAS-AM2` fixes a substrate ambiguity `TAS-AM1` left open.** `TAS-2` asks about an
artist's *candidates*; the artifact holds only the ≤50 survivors. Measuring there would
have answered a different question on an already-similarity-selected population and biased
toward a kill. Rule now stated per criterion: selection-side on the pre-cap capture,
map-side on the adopted artifact, never compared across.

**§4.3 Nothing in the prior record is overturned by this session's measurements.** `COH-`,
`FPC-`, Track B and the adjudication are untouched. `COH-2` is *corroborated*: this
session's independently-collected frame agrees with its banded figures to within half a
point when weighted by band size.

---

## §5 Gate outcomes

| Gate | Outcome |
|---|---|
| `TAS-1` — labels at both ends of famous–famous connections | **PASSED**, far above bar |
| `TAS-2` — does agreement vary between candidates | **PASSED**, well clear of both the kill and the weak-signal flag |
| `TAS-3` — diagnostic, no bar | Signal largely **independent** of similarity; the great majority of candidate lists are not already in agreement order — the opposite of the failure mode it was written to catch |
| `TAS-4` — would it change which neighbours survive selection | **PASSED (does not kill)**, by a wide margin at every λ, in the amended `TAS-AM1` currency of edge turnover. Added §9. |
| `TAS-5`, `TAS-6` | **NOT REACHED.** Unrun, not null. |

Figures: `builder/analysis/2026-07-30-tag-discrimination/tas_signal.json`,
`tas_tags.json` and `tas_select.json`.

**Instrument checks:** the `TD-` reconstruction reproduces `ALG-E-mutual_knn-k50.bin`
edge-for-edge (`td_turnover.py --verify`), and this session's three edge classes sum to
exactly the adopted artifact's independently-measured edge count. Re-run at Task 4 on a
regenerated capture and still exact; see §9.1. The randomised-label **red** check belongs to
Task 7 and has **not** run — **`TAS-4`'s result must not be believed before it does**, and
that now applies to a result that exists rather than to a hypothetical one.

---

## §6 Deferrals opened by this session, each with a condition

| Deferral | Condition |
|---|---|
| **Adding `analysis` to `testpaths`** | Deferred by the owner 2026-07-30. All 34 analysis tests pass, so it would work cleanly. **Revisit if any `TAS-` test needs to gate a merge, or at the closeout that retires this probe** — whichever first. Until then the `TAS-` tests run only when invoked explicitly, so "pinned by test" means pinned by a test someone must remember to run. |
| **`TAS-3`'s pooled correlation mixes within-list and between-artist variation** | **Accepted, won't chase** unless a `TAS-4`/`TAS-5` null needs adjudicating. The per-list already-ordered share answers the operational question directly and points the same way; a third statistic would change no decision. |
| **Replacing mutual k-NN with a tag-based degree limiter** | Owner-raised, parked as a **separate experiment** (spec §7). Not ruled out — ruled separate. Needs its own pre-registration designed cold. Track B's `R1a` corroborates its premise. |
| **The path-carrying measurement cannot say whether a rerouted journey *reads* differently** | **Structural, not chaseable offline** — it is the blind listen's (`REQ-38`). Recorded so no future session mistakes the journey-touch figure for a disruption figure; it is a **ceiling**. |

---

## §7 Operational measurements with no other home

- **ListenBrainz batched metadata sustained ~37–40 artists/s** over the full artifact,
  above `COH-5`'s measured 26/s. Whole-graph collection took well under the 47 minutes
  `COH-5` projected. 50-MBID batches, no throttling observed.
- **Wikidata P136 label collection** over the full artifact completed in the same window at
  250-MBID batches — smaller than `COH-1`'s 600 because a label query returns one row per
  (artist, genre) rather than one per artist.
- **The label collector recovers what the count collector found**: artists with ≥1
  English-labelled P136 genre differ from the earlier count-based total by **one artist**,
  so the English-label filter loses essentially nothing.
- **`norm_genre` ASCII-folds, so the union genre is a LATIN-SCRIPT vocabulary.** Non-Latin
  labels normalise to the empty string and are dropped; an artist whose only genres are
  Japanese or Korean reads as **unlabelled** and takes the neutral value. Correct — overlap
  across disjoint vocabularies is not computable — but it means `TAS-1`'s coverage must be
  read as Latin-script coverage. Diacritics fold rather than vanish, so it is a script
  limit, not a language limit. `COH-2` shares the property, so the two records stay
  comparable. Pinned by test.
- **Captures live in the session scratchpad, not the repo** (~20 MB each), regenerable in
  ~2 min via `td_capture.py`. `td_turnover.py --verify` makes a stale one impossible to use
  silently.

### Artifact provenance (D3) — recomputed at closeout, not transcribed

Both are gitignored, so a checksum is the only identity they will ever have. Verified with
`sha256sum` during this closeout and matching what §8's amendments assert:

| sha256 | file | used for |
|---|---|---|
| `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` | `builder/scratch/graph-t15-tiebreakfix.bin` | the **adopted** artifact — `TAS-1`, and `TAS-5` when it runs (map-side, `TAS-AM2`) |
| `73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa` | `builder/scratch/cb-cells/ALG-E-mutual_knn-k50.bin` | Track B cell — the green check for the pre-cap capture used by `TAS-2`/`TAS-3`, and by `TAS-4` when it runs (selection-side) |

**These two are NOT interchangeable** and differ by 36 artists / 193 edges. Which one a
figure came from is the difference between a valid read and an invalid one — hence
`TAS-AM2`'s standing rule that no read compares across them.

---

## §8 Standing context layer (D6)

Unconditional layer: **44,183 characters**. Conditional layer: **2,154 lines**.
Measured with the D6 commands; the memory-directory slug was confirmed to resolve first.

**Both unchanged by this session — delta zero on each**, verified from the diff rather than
asserted: `git diff --stat 1d34d81..HEAD -- CLAUDE.md .claude/` is empty, and every
`memory/*.md` predates this session. No `CLAUDE.md` row, memory file, skill description or
agent definition was added, removed or reworded. The two amendments and the substrate rule
live in the pre-registration, which is conditional `docs/` and costs a session nothing
unless it reads it.

> **Recorded because it is the exact failure this project keeps having.** The first draft
> of this section stated both figures **without running the commands** — they were plausible,
> internally consistent, and wrong by 39% and 92% respectively. Caught before commit only
> because D6 names the commands and running them is cheap. A retained log is precisely where
> a fabricated figure would have become the baseline every future closeout diffed against.

---

## §9 Task 4 — `TAS-4`, executed by a second session, 2026-07-30

Appended rather than merged into §1–§8 above: those record the first session's work, and a
reader needs to be able to tell which session measured what. **Figures live in
`tas_select.json`**, per this document's role line; nothing below restates one.

### §9.1 The three instrument checks, all run before any arm was read

The order matters and is the reason this section leads with it: `TAS-4` is a gate, and a
gate read on an unverified harness is worth nothing.

1. **Green, asserted in `main()` rather than assumed.** λ = 0 must reproduce the baseline
   selection bit for bit. It is an `assert`, so the run cannot produce a number if it fails.
2. **`td_turnover.py --verify`.** The reconstruction reproduces `ALG-E-mutual_knn-k50.bin`
   edge for edge on a freshly regenerated capture — the sha matches what §8's amendment
   asserts, and `exact_match` is true.
3. **The regenerated capture reproduces the committed `TD-2` record exactly** — all 37 arms,
   every field. This was not in the plan. It is nearly free once the capture is rebuilt, and
   it closes the one gap the handoff flagged: the captures live in a session scratchpad and
   do not survive, so **every `TD-` figure in the record was resting on a file no later
   session could see.** It is now known to be regenerable, not merely assumed to be.

**The red check is still owed and still Task 7's.** Nothing in §9 is believable until it
runs. This is the deferral `NEXT.md` carries as an ordering constraint, and it now guards a
result that exists.

### §9.2 The plan's Task 4 did not describe the code it was written against

The handoff predicted a keying mismatch in `load_capture` / `mutual_edge_set`. It is a
**data-model** mismatch, and larger than predicted: neither name exists, and `td_turnover.py`
expresses a selection as a **boolean mask over one flattened candidate array**, computing
turnover by numpy set operations on packed `u * n + v` edge keys. The plan's
`simulate_top_k(...) -> set[str]` over MBID-keyed dicts is a different shape, not a different
spelling.

Resolved by keeping the plan's **pinned properties** and rewriting them against the real
interface — λ = 0 exactness, a genre match promoted past a stronger mismatch at the cap
boundary, an unlabelled candidate not demoted. The plan's Step 5 existed precisely to catch
this, which makes **four** plan defects found by verify-against-source steps the plan itself
carried. That is now the strongest single argument in this record for not skipping one.

### §9.3 Decisions taken, with reasoning

**The neutral rule is called, never inlined.** An inline median would roughly halve the
agreement field's runtime. It would also be a second copy of the pre-registration's **one
dormant term** — inert at λ = 0, active in every arm — free to drift from the routing arm's
copy in Task 6 while both documents claimed they shared one rule. `tas_common` exists to make
that impossible; buying speed by defeating it would be a poor trade.

**Nodes absent from the fixed fame frame are counted `unframed`, not defaulted to percentile
zero.** `tas_signal` uses `frame.get(mbid, 0.0)`, which is safe there because it runs on the
artifact the frame is built from, so the default never fires. On the capture side it fires,
and percentile 0 would silently class those connections obscure–obscure — moving a per-class
figure with no trace. Pinned by test, and the measured count matches the largest-component
prune's edge count exactly, which is the arithmetic that confirms the classification is
right rather than merely defensible.

**The median is reported and labelled retired.** `TAS-AM1` retires it as the statistic. It is
still emitted under an explicit `_RETIRED_STATISTIC` name so `TD-3`'s zero-inflation is
visible in this record rather than taken on trust from another one.

**Maximum reuse of `td_turnover.py`, zero edits to it.** `Capture`, `mutual_undirected` and
`swaps_per_node` are imported. The only new machinery is the ranking field, which supplies
real tag agreement where `TD-2` supplied a synthetic uniform one. The frozen probe was not
touched, and its committed output was protected during re-running by pointing `--out` at
scratch.

### §9.4 What the comparison against `TD-2` bought, and what it cost nothing to get

`TD-2`'s `MULT-IND` / `MULT-SYM` arms use **the same functional form, the same substrate and
the same λ values** as `TAS-4`, differing in exactly one column: the field is a synthetic
uniform draw rather than real tag agreement. That is an isolating baseline in the factor
table's sense, and it was already committed — so `TAS-4` acquired a one-knob control for
free, and one nobody designed for it.

Two things it shows, both recorded here as **reasoning**, with the numbers in
`tas_select.json` and `td_turnover.json`:

- **The real tag signal reorders considerably *less* than a uniform random field at the same
  λ.** Expected, and worth stating because it means the λ grid's numbers are not a generic
  property of the functional form — they are a property of tags.
- **Tag-aware selection makes the map denser: creations exceed deletions at every λ, and by a
  wider margin than even the *symmetric* synthetic arm.** Jaccard is symmetric, so two
  artists sharing genres promote each other, and genre agreement is clustered in a way a
  random symmetric field is not. **This is a structural consequence nothing in the
  pre-registration anticipated**, and it is not a `TAS-4` finding — `TAS-4` asks whether
  selection would change, and the answer does not depend on it. It is flagged in §9.5 as
  something a rebuild pre-registration must handle.

### §9.5 Deferrals opened by Task 4

| Deferral | Condition |
|---|---|
| **Tag-aware selection increases total edge count** | **Before any rebuild pre-registration is written.** Mutual k-NN bounds each artist's own list, not the count of *mutual* pairs, so a symmetric ranking signal raises mean degree. Track B's cap work, `w_degree_hub` (dormant, and dormant *because of the current graph's top-degree set*), and `CRS-C4`'s hub cost all sit downstream of degree. A rebuild arm must measure it, and the `§0` held-constant row asserting `w_degree_hub` stays dormant is scoped to *this* probe, which rebuilds nothing — **it does not transfer to a rebuild.** |
| **797 capture nodes carry no labels because the tag frame's population is the adopted artifact, not the capture** | **Accepted, won't chase.** They are the nodes the largest-component prune removes, they carry 18 baseline edges between them, and they are treated exactly as genuinely unlabelled artists are. A second-order effect survives — such a node can still occupy a top-50 slot in an in-component artist's candidate list — and is not measured. Reopen only if a rebuild arm's turnover needs attributing to the node. |
| **One new Snyk Low finding: a CLI `--out` path flows into `pathlib.Path` (`tas_select.py`)** | **Recorded, not fixed, and the acceptance is the owner's to extend.** It is the same class as the four pre-existing findings in this directory's frozen `td_*` probes and the 13 already accepted under `builder/analysis/`. It cannot be meaningfully sanitised: captures deliberately live *outside* the repo, so confining the path would break the intended usage. Flagged rather than absorbed silently, because a session should not widen an accepted-risk set on its own authority. |

---

## §10 The two selection-side checks, brought forward from Task 7

Run immediately after §9, not at Task 7. Reordering is a methodology call: the red check is
what makes `TAS-4` believable at all, both selection-side halves need only `tas_select.py`,
and carrying an uncertified gate result through two more tasks is the risk the deferral was
written to prevent. **The routing halves of both remain Task 7's** — they need `tas_route.py`.
Figures in `tas_guard.json`.

### §10.1 `TAS-6` is ADVERSE — and this bars an adoption recommendation

*Plain sentence, quoted from the spec: "does this make the app worse at reaching unknown
artists — the thing you called a defect rather than a limitation?"*

**It does.** Famous→obscure connections fall at **every** λ, crossing the 10% adverse bar at
the top two. Per §5's read — "`TAS-6` adverse, anything else positive → no adoption
recommendation, whatever else holds" — this stands regardless of `TAS-4` having survived, and
regardless of anything `TAS-5` may later show.

The mechanism is the one `TAS-6` was written to catch, and it is the **neutral rule's**, which
is why every finding here is reported as "λ **and** the neutral rule". Unlabelled candidates
take a per-artist median; labelled genre-matching candidates are boosted *above* that median;
unlabelled candidates are disproportionately obscure. The neutral rule stops them being sent
to the bottom, which was its job, but it cannot stop them being squeezed out at the margin.

**The criterion's denominator is thin, and that is information rather than a defence.** The
baseline population is small enough that the reader must see it before judging materiality —
it is in `tas_guard.json`. **No bar is being revisited after seeing a result**, and the
thinness cuts both ways: it is also a statement about how few direct famous→obscure
connections this graph has at all, which is `DD-F1` measured from a new angle.

### §10.2 The red check did not fire, and the check is what is wrong

The pre-registered red check (§4) feeds the harness a randomised tag frame and requires large
turnover. It did not clear the liveness line. **That line was this session's, not
pre-registered** — §4 fixes no number — and `tas_guard.json` carries a field saying so.

**Measured rather than asserted, because the alternative reading is that the harness is
broken:** shuffling labels does not *randomise* overlap, it **destroys** it. On a 4,000-node
sample, agreement is exactly zero on the great majority of labelled pairs under the shuffled
frame against roughly a third under the real one, and both-ends-labelled slots more than
halve — real labelling is correlated with having a long candidate list, and shuffling breaks
that. A near-constant multiplier cannot reorder anything.

**So a Jaccard-overlap device cannot produce large turnover on a shuffled frame by
construction.** §4's red check was written generically and does not fit an overlap-based
device. This is a defect in the instrument check, not in the instrument.

**That claim is doing a lot of work, so here is what would falsify it** and what supports it:
the green check passes for the shuffled frame too (λ = 0 reproduces the baseline whatever the
field says, asserted in code); `td_turnover.py --verify` is exact; all 37 `TD-2` arms
reproduce; and the harness demonstrably reports large turnover on the real frame. A harness
that could not report large change would have failed the last of those.

**The plan's Task 7 Step 5 says to stop on this branch, and this session stopped.** Tasks 5–8
were not started.

### §10.3 What is owed before the probe continues

A replacement control that preserves agreement *strength* while destroying *which candidate
carries it* — permuting the agreement field within each artist's candidate list is the
obvious candidate, since it holds each artist's own distribution exactly fixed.

**It is a `TAS-AM3` and it must be committed before it runs.** The git timestamp is the only
evidence that a control's design preceded its result, and this one is being designed *after*
seeing a result, which is precisely when that evidence matters most. Not written yet.

**This is also a seam.** A material mid-flight amendment means the next session has a new
governing document and should read it cold.

---

## §11 `TAS-AM3` written, committed, and run

Written after §10's stop, committed **before** it ran (`ffc1029`), then run. The amendment
itself discloses that it is the first one appended *after* results existed and names the
hazard that creates. Figures in `tas_guard.json`.

### §11.1 `TAS-AM3a` passes on both conditions, at every λ

*Plain: prove the measuring device can register a big change, by giving it a big change we
already know the answer to.*

The selection masks are **bit-identical** to `td_turnover.mask_multiplicative`, and turnover
reproduces the committed `TD-2` `MULT-SYM` figures **to five decimals at every λ**.

Two things follow, and the second is what the withdrawn check was reaching for. The new
ranking path **is** the already-verified one rather than resembling it — a stronger claim than
the original check could have made. And the harness demonstrably reports very large turnover
when a large signal exists, shown against a **fixed external reference** rather than a
threshold a session picked, which is exactly the weakness that made the withdrawn check's
non-firing ambiguous.

**The red check is DISCHARGED for the selection side, and `TAS-4`'s figures are believable.**
The routing side still owes its own; `TAS-AM3` specifies the same pair for it.

### §11.2 `TAS-AM3b` corrected the withdrawn check's reading, against tags

*Plain: check that the change we measured comes from genres sitting where they actually sit,
rather than from any label-shaped nudge at all.*

The ratio of null turnover to real turnover sits just under a quarter and is strikingly flat
across the whole λ grid — below the 0.50 line fixed in the amendment before the control ran,
so attribution is not unsafe.

**But the withdrawn shuffle had implied a ratio less than half that size.** Holding fixed
*which* artists are labelled — the one knob the naive version also moved — roughly doubles the
null. The naive shuffle halved the number of pairs where the device acts, which suppressed the
null and **overstated how much of `TAS-4`'s turnover was attributable to genre structure.**

**The correction runs against the idea, not for it**, and it is the second time in this probe
that a check has moved a number in the unflattering direction (the first was `TAS-AM1`). It is
also the direct answer to the owner's stated reason for doing this work — that it might catch
another error. It did.

Per `TAS-AM3b`'s pre-registered read, below the threshold the ratio is **reported and nothing
more**: no claim about tags is licensed by this control, and reading it as one would need its
own pre-registration designed cold.

### §11.3 What is retained rather than deleted, and why

`randomised_labels` stays runnable and its output stays in `tas_guard.json` under
`withdrawn_naive_shuffle` with its reason. `TAS-AM3` cites that figure as the evidence that the
direction was known **before** the amendment was written, so deleting the function that
produced it would break the only check a reader has on the amendment's own good faith.

---

## §12 Owner input during this session, recorded because it does not survive in the diff

### §12.1 An architecture instinct, explicitly **NOT** a directive

The owner stated, and labelled as instinct rather than fact or instruction, that **the routing
side looks like the better home for genre discrimination** — and that if genres are to
influence the graph side, it only makes sense **as part of addressing mutual k-NN**.

**Recorded so a later session does not mistake it for a ruling.** He asked to be challenged,
and was. The challenge, and what survived it:

- **Against the routing half of his instinct:** this router has shrugged off **three
  consecutive** pricing changes (Track 2's repricing family, Track 3b's toll, Track B's `R2`
  quota edges present-and-declined). The selection side has just demonstrated it can move
  16–40% of the map. His instinct favours the architecture with the worse record here.
- **For it, on better grounds than he gave:** all three of those changes **re-priced
  quantities the router already had**. `TAS-3` measured genre agreement as only weakly related
  to similarity, so it is new information rather than a re-pricing of old. The three nulls may
  not transfer. Held loosely — "this time is different" is always available — and `TAS-5` is
  what would settle it.
- **His second instinct has mechanical support and is the stronger one.** Tag-aware selection
  raises density *by raising mutuality*, so the genre signal acts directly on the mechanism
  mutual k-NN implements; and `TAS-6`'s adverse result looks like a mutuality artifact, since
  famous→obscure links die at a boundary that must be cleared at both ends while the obscure
  end is usually unlabelled. Track B's `R1a` already found reciprocity at k = 100 doing
  nothing measurable.
- **Refinement offered:** §7 rules those two **separate** because mixing a ranking change with
  a structural one makes every attribution ambiguous. The defensible form is **sequence, not
  combine** — settle mutual k-NN, then re-ask the genre question against whatever replaces it.

He also directed that `TAS-AM3` be done regardless, on the grounds that it was cheap and might
catch something. **It did** — see §11.2, and the correction ran against the idea.

### §12.2 A parallel investigation into richer tag sources — read-only, another session

The owner is having a second session investigate **Discogs** and **MusicBrainz release tags**,
aggregated across an artist's releases, as potentially richer sources than the frame this probe
uses. Explicitly nothing to act on here. Four things that bear on it, recorded so this session's
knowledge reaches it:

1. **The vocabulary is pinned by §1 and a change is a §8 amendment, not an improvement.**
   Swapping the frame breaks comparability with the `COH-` coverage figures, which is the
   reason §1 fixed it in the first place.
2. **The decision-relevant question is narrower than "are there more tags".** It is
   **specifically whether coverage rises in the OBSCURE TAIL** — `TAS-6`'s adverse result is
   driven by unlabelled candidates, which are disproportionately obscure, being squeezed out.
   A richer frame that only thickens labels on artists who already had them changes nothing
   here. One that lifts the bottom half could plausibly flip `TAS-6`.
3. **⚠ CORRECTED — `COH-5` and `COH-6` do NOT bound this question, and this session first said
   they did.** The original wording called `COH-6` "the base rate to beat" and said MusicBrainz
   genres were "already in hand" via `COH-5`. **Both were wrong against the question actually
   being asked**, and the error is recorded rather than silently fixed because it is the shape
   this project keeps hitting — treating a source as one undifferentiated thing.

   - **`COH-5` is a claim about a TRANSPORT, not about what data exists.** It measured
     ListenBrainz against MusicBrainz-direct on **artist-level** genre sets (871/872 identical)
     and concluded LB delivers MB's artist tags ~29× faster. **Release and release-group tags
     live in different tables that no probe here has ever touched.**
   - **`COH-6`'s widest union is entirely artist-level** — any MB tag ∪ any LB tag ∪ any MB
     genre ∪ any P136 statement. Its conclusion is scoped by its own words: unseen artists
     carry no tags of any kind *"in any source measured here"*. **Release-level data was not
     among them, so `COH-6` is silent on aggregation, not evidence against it.**

   **What `COH-6` does give this question is the size of the prize:** widening the
   artist-level vocabulary bought only +3.4 points in the lower half (35.3% → 38.7%), so
   **roughly 61% of lower-half artists carry no artist-level tag from any source**. That is the
   target population, and it is large.

   **Two mechanisms, both plausible, which is what makes it worth measuring rather than
   arguing.** For it: MusicBrainz tagging effort attaches to the thing a person just added,
   usually a *release*, so an obscure artist with one album can have the album tagged while the
   artist entity stays bare. Against it: the indifference that left the artist untagged
   plausibly left the releases untagged too.
4. **Discogs is a genuinely independent source**, unlike anything in the current frame, and so
   does not inherit MusicBrainz's blind spot. It carries the **population-mismatch** trap
   instead — the one that killed every external popularity source — plus a Discogs-ID ↔ MBID
   mapping problem whose coverage must be measured before any tag figure derived through it
   means anything. Discogs has no artist-level tags at all, so it needs the **same**
   release-aggregation method, not a different one.
5. **Three design constraints that are cheap to state and expensive to discover.** (a) Draw the
   sample from artists **unlabelled today**, not from obscure artists generally, or the
   headline is diluted by artists who already have labels; band it as `COH-2` did so the two
   are comparable. (b) **Aggregation introduces a validity failure that coverage cannot show** —
   various-artists compilations and splits attribute other people's genres, and a prolific
   cross-genre artist aggregates to a muddy union, so coverage can rise while labels get worse.
   Decide which release types count *before* running. (c) A high tag rate among the artists that
   resolve to a Discogs ID is **not** a gain of that size if resolution itself is partial.

**Practical note for that session:** the adopted artifact and the archive are **gitignored**,
so they do not appear in a `git worktree`. Any coverage measurement against the real population
must point at `builder/scratch/` in the main tree explicitly.

---

## §13 `TAS-AM4` — the `REL-` frame evaluated as a candidate

Amendment committed before it ran (`17716dc`), then run. **§1's vocabulary is unchanged and
every committed `TAS-` figure still stands on it.** Figures in `tas_frame_eval.json`.

### §13.1 The reads, in the order `TAS-AM4` fixed them

1. **No candidate is killed.** Both enriched frames clear `TAS-2`'s kill bar and its
   weak-signal flag with room, using **`TAS-2`'s existing bars unchanged** — the main thing
   keeping an after-the-fact amendment honest.
2. **The spread fall is the headline, per the read that pre-committed it to being one.** The
   within-list spread falls under both candidates, and by more than twice as much when Discogs
   is added on top of MusicBrainz. The flattening `TAS-AM4` predicted is present.
3. **`TAS-3`, diagnostic and unbarred:** rank correlation with similarity **rises** under both
   candidates — the same failure showing up in the second place it could. The already-ordered
   share falls, but see §13.3 before reading that as headroom.
4. **Reach — the share of candidate slots where the rule acts at all — rises substantially**,
   and this is the quantity that would drive any `TAS-6` improvement.

### §13.2 The comparison was confounded, and the control did not rescue it

`_tas2_tas3` scores every artist it *can*, and enrichment makes far more artists scorable. So
the first pass moved **the frame and the population together** — and the artists that became
scorable are precisely the obscure ones `REL-` reached, whose spread there was every reason to
expect to differ. **Composition and real degradation have opposite implications**, and
`TAS-AM4`'s read 2 presupposes the like-for-like one.

`signal_on()` re-measures every frame on `W0`'s scorable set. That is valid as a one-knob
control because labels only ever **accumulate**, so `W0`'s scorable set is scorable under every
candidate.

**The control changed almost nothing — the degradation is real, on the same artists.**
Recorded because a control that is only reported when it helps is not a control, and this one
was run expecting it might overturn the result.

### §13.3 One confound the control does **not** remove

Fixing the population fixes **which artists** are scored, not **how many of each artist's
candidates** are. Under an enriched frame the same artist has more scorable candidates, and a
longer list is less likely to be *coincidentally* in agreement order. **So the fall in the
already-ordered share must not be read as "more reordering headroom"** — it is at least partly
a list-length artifact. The rank correlation is the cleaner of the two `TAS-3` readings here,
and it moves the other way.

### §13.4 What this does and does not license

**It licenses a recommendation and nothing else** — `TAS-AM4` read 5, fixed before the run.
No `TAS-4`/`TAS-6` re-run, no adoption, no rebuild. **`TAS-6`'s adverse verdict on the
committed frame stands and is not retroactively softened by a better frame existing.**

**The session's position, argued rather than asserted:** if a re-run happens, it should use
**`W1` (MusicBrainz release groups only), not `W6`.** The Discogs increment buys the smaller
share of the remaining reach for roughly as much spread again — the trade is clearly
diminishing, and `W1` keeps the signal closest to the one every committed figure was measured
on. Which cells to run is methodology and therefore the session's; **whether to spend on a
re-run at all is the owner's**, since a `§1` vocabulary change is an amendment to a frozen
document and any adoption downstream spends his ear (`REQ-38`).

### §13.5 Operational

`np.load` on an `.npz` returns a **lazy** `NpzFile`: each `z["key"]` access decompresses the
whole array. The first draft of `signal_on` indexed `z["rank"]` **inside** the inner loop,
decompressing a 4-million-element array once per candidate slot. It ran for over an hour of CPU
before being killed, having produced nothing — and it looked merely slow rather than wrong,
because the invocation also piped through `tail`, which buffered all progress output away.
**Two lessons, both cheap:** materialise every array from an `.npz` once, as the committed
`_tas2_tas3` already did; and do not pipe a long unattended run through `tail`.

---

## §14 Closeout

### §14.1 Artifact provenance (D3) — recomputed, not transcribed

| sha256 | file | used for |
|---|---|---|
| `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` | `builder/scratch/graph-t15-tiebreakfix.bin` | the **adopted** artifact — the fixed fame frame for `TAS-6` and `TAS-AM4`, and `TAS-1`/`TAS-5`'s map-side substrate |
| `73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa` | `builder/scratch/cb-cells/ALG-E-mutual_knn-k50.bin` | the green check's target — the pre-cap capture reproduces it **edge for edge** |
| `893609e97fb31f2a679a5e8005f7488d771414658d671a9eee979a757b550d90` | `alge_capture.npz` (session scratchpad, **not** the repo) | the selection-side substrate for `TAS-2`/`TAS-3`/`TAS-4`/`TAS-6`/`TAS-AM3`/`TAS-AM4` |

**The capture will not survive this session** and is regenerable from committed code via
`td_capture.py` in ~6.5 min cold. Its sha is recorded anyway, so a future regeneration that
does *not* match is detectable rather than silent — and it reproduced the committed `TD-2`
record's 37 arms exactly, which is the stronger check.

**The first two are NOT interchangeable** and differ by 36 artists / 193 edges. `TAS-AM2`'s
standing rule holds: no read compares a capture-side figure against an artifact-side one.

### §14.2 Standing context layer (D6)

Unconditional layer: **44,183 characters.** Conditional layer: **2,154 lines.**

**Delta zero on both, verified from the diff rather than asserted.**
`git diff --stat 3049fcd..HEAD -- CLAUDE.md .claude/` is empty, and every `memory/*.md`
predates this session. No `CLAUDE.md` row, memory file, skill description or agent definition
was added, removed or reworded — including across the `REL-` merge. Two amendments, a new
handoff and five log sections all live in conditional `docs/`, which costs a session nothing
unless it reads them.

### §14.3 Closeout outcomes

- **A4 default-flip: inapplicable, and said rather than skipped.** This work added no config
  knob. `BuilderConfig` and `ApiConfig` are untouched; `w_coh` still does not exist and this
  probe does not propose it.
- **A5:** no listener on 8000/5173/4173/3000. This session started no server and left none
  running. Nothing was queued that needs one.
- **B1:** `docs-lint.sh` hard checks passed; `doc-auditor` returned **no findings**. **But
  three defects in the probe directory's `README.md` were found outside the audit** by
  checking whether the files it lists exist — two scripts listed that do not (`tas_pairs.py`,
  `tas_route.py`, Tasks 5 and 6), and a description of the randomised-label red check that
  `TAS-AM3` had withdrawn. **Recorded as a limitation of "audit clean", not as a criticism of
  it:** file existence is not a class that reading prose detects.
- **B2:** `tas_select` and `tas_guard` have inbound imports. `tas_frame_eval` has none and is
  **not an orphan** — it is a command-line entry point, the same shape as `tas_signal` and
  `td_turnover`. Asked rather than assumed, per B2's own framing.
- **B3:** four deliberate mutations — an off-by-one in the top-*k* mask, the neutral rule
  returning zero, turnover ignoring creations, and unframed nodes classed as obscure — **all
  went red**, then restored green with a clean tree. The tests are not vacuous.
- **B4/B5:** every docstring reuse claim verified against the imports. `ml-graph-analyst.md`
  carries all six cost-function terms and is current — checked because it is the file that
  once described that function with a term missing. Neither `NEXT.md` nor this log restates a
  criterion figure; both cite.
- **D4:** builder 129, api 217, frontend 107 across 18 files. All pass. The probe's own 42
  tests run only when invoked explicitly — `testpaths` is still `["tests"]` by the owner's
  deferral, whose condition is **not** due, since it fires at the closeout that *retires* this
  probe and Tasks 5–8 are unrun.
- **Snyk:** 7 findings in the probe directory, all **Low**, all one class (a CLI `--out` path
  reaching `pathlib.Path`). Three are this session's. Same class as the 13 already accepted
  under `builder/analysis/`; it cannot be meaningfully sanitised, because captures
  deliberately live outside the repo. **Recorded in `NEXT.md`'s deferral table rather than
  absorbed** — widening an accepted-risk set is the owner's call.

---

## §15 The Discogs increment decomposed — an attribution correction

**A new session, 2026-08-01, continuing from the `TAS-AM3`/`TAS-AM4` seam handoff.** Owner-raised,
diagnostic only. **No `TAS-` criterion, bar, weight, default, currency, vocabulary or substrate
changes, nothing is adopted, and `TAS-AM4`'s committed figures are reproduced rather than
replaced** — `tas_frame_eval.json` stays their record. Figures: `tas_frame_split.json`;
producer: `tas_frame_split.py`.

### §15.1 What prompted it

The owner asked why the probe does not use every available tag source, and separately noted
that **Discogs ships two label columns**: a closed 15-value genre list and a ~600-value style
list. `rel_discogs.py` records that distinction at its head and warns that "merging Discogs
genre into any agreement statistic would inflate it badly" — **and `TAS-AM4`'s `W6` merged both
anyway.** So the arm that produced "the enriched frame blunts discrimination" moved two knobs,
and the fall was attributed to neither.

`NEXT.md`'s deferred row had asked for precisely this read — "a cheap read on whether coarse
agreement suffices for what `TAS-` does, answerable against the committed `TAS-` harness with no
rebuild". It is now answered.

### §15.2 Provenance, checked before anything was read

Three checks, all passed, none of them planned as findings:

- **The capture regenerated byte-identically.** Its sha256 matches §14.1's recorded value
  exactly. That section recorded the sha specifically so a divergent regeneration would be
  detectable rather than silent; the check has now run and the pipeline is deterministic
  across sessions from committed code.
- **The green check passed** — the capture reproduces `ALG-E-mutual_knn-k50.bin` edge for edge.
- **`TAS-AM4`'s three committed spread figures reproduce exactly**, on the same fixed
  population of lists. The probe aborts rather than reporting if they do not.

### §15.3 The decomposition, and it inverts the expected attribution

Two new frames, each isolating one Discogs column against a baseline differing by exactly that
column: `W4` adds the closed genre list to `W1`, `W5` adds the style list. With `W6` those give
**two independent isolations of each source**, and all four agree.

**The closed 15-value genre list is not the problem. The ~600-value style list is.** Adding the
coarse list barely moves the spread — in one isolation it slightly *improves* it — and it
**lowers** redundancy with the similarity score in both isolations, meaning it carries
information similarity did not already have. Adding styles costs roughly a tenth of the spread
in both isolations and **raises** redundancy in both.

**The sharpest figure is that styles add no reach whatever on top of the genre list.** Every
artist Discogs styles reach, Discogs genres already reach — which follows from `REL-`'s own
measurement that Discogs releases always carry a genre and only sometimes a style. On this
evidence the style column costs discrimination and buys nothing.

**A better frame than `W6` existed and was never evaluated.** `W4` dominates `W6` on every
measured axis: identical reach, higher spread, lower redundancy. The record's conclusion that
adding Discogs is diminishing is **true as stated and wrongly attributed**, and it pointed at
the worse of two available combinations.

### §15.4 What this does and does not license

**It licenses a correction to the record and nothing else.** No re-run, no adoption, no
rebuild, no vocabulary change. §1 stays pinned to the `COH-2` union genre and every committed
`TAS-` figure still stands on it. **`TAS-6`'s adverse selection-side verdict is untouched** and
still bars an adoption recommendation per §5. Nothing here says `W4` is good enough to adopt —
only that it beats the frame that was measured.

**The spread statistic is scale-sensitive and its magnitude should not be defended.** Adding any
source gives artists more labels, which compresses a Jaccard somewhat regardless of quality. What
survives that objection is the **direction and the contrast**, because the redundancy reading is a
rank correlation, is therefore scale-free, and separates the two columns the same way. Two
statistics, two isolations each, four agreements.

### §15.5 A predictive failure worth recording, because it is the second in one session

**Both the session's and the owner's predictions were wrong, in the same direction.** The
expectation — stated in advance by both, and supported by `rel_discogs.py`'s own warning — was
that the coarse 15-value list would make unrelated artists look alike, and that the finer style
list would be the valuable half. The measurement reversed both.

Earlier the same session predicted that famous artists' long tails of stray tags would suppress
their agreement through the Jaccard denominator **strongly enough to make the device partly a
fame measurement**. Label count is indeed strongly fame-linked, but the effect on agreement is
weak, and **the strong form of that prediction was retracted.**

**A correction to how that retraction was first stated, kept because it is the same substrate
error this log keeps warning about.** The session first reported the effect as "approximately
zero". That figure was measured over the **adopted artifact's surviving edges**; on the
**pre-cap candidate slots** — the selection-side substrate, and the one that actually governs
this device — it is roughly six times larger, though still weak. `TAS-AM2` forbids reading one
against the other, and the gap is informative rather than contradictory: surviving edges are the
strong pairs, where agreement is high whatever the label count, so the denominator effect has
less room to show among them. **The retraction stands; "approximately zero" overstated it.**
Both figures are in `tas_weighting.json`, each labelled with its substrate.

**Two confident mechanistic predictions, both falsified by cheap measurement in one session.**
Recorded as a standing caution: intuitions about what these label sources *do* are not reliable
here, which is an argument for decomposing a frame question rather than reasoning about it — and
for treating "the enriched frame blunts the signal" as exactly the kind of summary that needed
this decomposition before it entered the record.

---

## §16 The routing side, `TAS-R1`–`TAS-R4` — the instrument works and the result is a null

**2026-08-01, same session as §15.** Governing plan:
[`plans/2026-07-31-tas5-routing-execution-plan.md`](plans/2026-07-31-tas5-routing-execution-plan.md),
which supersedes the original plan's Tasks 5, 6 and Task 7's routing halves. Figures:
`tas_route.json`, `tas_route_guard.json`. **Tasks 1–7 of the probe are now complete; Task 8
(findings and the owner-facing read) is deliberately unrun.**

### §16.1 Why a new plan rather than executing the old Tasks 5–7

Five things in the inherited tasks no longer described the code, and **one was a trap rather
than merely stale**: Task 7 Step 5 still instructed the executor to make the randomised-label
red check fire and *stop* if it did not — the check `TAS-AM3` **withdrew as unachievable**. A
fresh executor following the plan would have "fixed" the harness until a shuffle fired, which
is precisely what the handoff forbids. The others: `tas_guard.py` already existed where the
plan said *Create*; `tas_select.simulate_top_k` never existed at all; `neutral_for` was called
without being imported; and the baseline was recomputed once per weight.

**The trap is the finding, not the staleness.** A plan that is merely out of date gets
corrected on contact. A plan that instructs the executor to defeat a withdrawn check reads as
authoritative and would have been followed.

### §16.2 `TAS-AM5` — an amendment written before any routing figure existed

**`TAS-AM3`'s scope clause does not transfer to the routing side, and `TAS-AM2` is why.**
`TAS-AM3a` passes on bit-identity against `td_turnover.mask_multiplicative` and on reproducing
`TD-2` — both on the pre-cap capture — while `TAS-AM2` puts `TAS-5` on the adopted artifact and
forbids reading one against the other. There is no artifact-side reference to be identical to,
and `td_pathedges.json` is not one: it is measured on `ALG-E` too.

What transfers is the *property*: a fixed external reference rather than a judgement call.
`TAS-AM5b` supplies one by **computing the reference independently** — a plain Dijkstra whose
only cost is `(1 − agreement)` — and requiring the forked router at a dominating weight to
reach that optimum exactly. Totals rather than node sequences, so ties are not read as defects.

**This is the first amendment on this probe written before its results existed**, and it says
so at its head. `TAS-AM3` and `TAS-AM4` both had to disclose the opposite. The git commit
timestamp is the evidence, which is the half that cannot be reconstructed afterwards.

### §16.3 Outcomes

- **`TAS-AM5a` (equivalence): PASSED, 0 mismatches on the full draw.** The fork returns
  production's paths exactly at zero weight. This is what licenses the fork omitting the
  bypass machinery — proved, not argued.
- **`TAS-AM5b` (liveness): PASSED, 0 failures.** The term reaches the cost function and can
  fully redirect a journey to the coherence-optimal route.
- **`TAS-5`: does not kill.** Journeys change at every non-zero weight, in every class.
- **⚠ `TAS-AM5c` (null control): FIRES.** Permuting labels among labelled artists reproduces
  nearly all of the real change rate, far above the pre-registered clause. **`TAS-5`'s change
  is NOT attributable to genre structure**, and every `TAS-5` figure carries that caveat.
- **⚠ `TAS-6`'s routing half is VACUOUS.** The baseline count of sub-decile interior artists is
  **zero** — production routing delivers no bottom-decile artist mid-journey on any drawn pair
  — so a 10% reduction cannot be measured and the adverse test returns false by construction.
  **"Not adverse" here is a division-by-zero artifact, not a safety finding.** The zero is
  itself a corroboration of `DD-F1`.

**So neither architecture has an adoption case.** The build-time side is barred by `TAS-6`'s
adverse *selection* half; the router side survives its kill bar but on a change the null
control says is not about genre. **This is the fourth router intervention on this project to
fail to demonstrate a real effect — and the first that looked like a success until the control
ran.**

### §16.4 Two deflations recorded before the null control ran

Both were committed in `TAS-R3`'s message *before* `TAS-AM5c` existed, and both anticipated
its shape. Recorded because a caveat written after a result is worth much less:

1. **The gentlest weight is not gentle.** At `0.25 × w_sim` the added term is comparable in
   size to the similarity term beside it. No cell in the grid is a light touch.
2. **One substitution makes a whole journey "changed".** Journeys average roughly six hops
   between famous artists and twelve between obscure ones, so near-total path-level change is
   close to arithmetically forced. The class ordering in the results matches what path length
   alone predicts, which is the tell.

### §16.5 Defects found in this session's own output

- **A test that was green for the wrong reason, caught by closeout B3.** With both routes
  identical on every production term, a tie-break on lowest node id produced the expected path,
  so `test_a_dominating_weight_routes_through_the_agreeing_neighbour` **passed with the
  coherence term zeroed out**. Fixed by expecting the higher-id route. Four other mutations went
  red as they should; this one did not, and only mutation testing could have found it.
- **A substrate error in this session's own reporting, corrected in §15.5.** "Approximately
  zero" was measured on the artifact and quoted as though it governed the selection side.
- **`docs/README.md` did not classify the new plan** — caught by `docs-lint.sh`, fixed.

### §16.6 Closeout, 2026-08-01

**Artifact provenance (D3) — recomputed, not transcribed.** Unchanged from §14.1: the adopted
artifact and the `ALG-E` reference cell carry the same sha256s, and **the regenerated
`alge_capture.npz` matches §14.1's recorded value byte for byte**. That check existed only
because §14.1 wrote the sha down against a future regeneration; it has now fired and passed.
**No artifact was built, adopted or modified by this work.**

**Standing context layer (D6).** Unconditional layer: **44,183 characters.** Conditional layer:
**2,154 lines.** **Delta zero on both, verified from the diff rather than asserted** —
`git diff --stat 5d66118..HEAD -- CLAUDE.md .claude/` is empty and every `memory/*.md` predates
this session. Two new probe modules, a new plan, a new handoff, an amendment and two log
sections all live in conditional `docs/` and `builder/analysis/`, which cost a session nothing
unless it reads them.

**Closeout outcomes:**

- **A4 default-flip: inapplicable, and said rather than skipped.** This work added no config
  knob. `w_coh` still does not exist in `ApiConfig`, deliberately — it is harness-local, and
  shipping it would be an adoption this probe does not license.
- **A5:** no listener on 8000/5173/4173/3000. This session started no server and left none
  running. The queued test needs none.
- **B1:** `docs-lint.sh` **failed one hard check** — the new plan was not classified in
  `docs/README.md` — fixed, then clean. The `doc-auditor` then found **seven live HIGH
  defects, all staleness in `NEXT.md`, the probe `README.md` and the superseded handoff**,
  every one of which would have told a cold reader that Tasks 5–8 were unrun and pointed it at
  the trap. All fixed. **One of its findings was stale on arrival** — it audited a snapshot
  taken before §16 was appended and reported the section missing; its `LOW` finding (that path
  *cost* might be compared) was checked against source and is clean, since `tas_route.py:206`
  compares path lists. **Checking each finding against current state, rather than accepting or
  dismissing the report wholesale, is the lesson.**
- **B2:** `tas_pairs`, `tas_route` and `tas_route_guard` all have inbound imports.
  `tas_frame_split` and `tas_weighting` have none and are **not orphans** — both are
  command-line entry points with `main()` and a `__main__` guard, the same shape as
  `tas_signal` and `tas_frame_eval`. Asked rather than assumed.
- **B3: this found a real defect, and only mutation testing could have.** Five deliberate
  mutations — counting path endpoints, defaulting an unframed artist to obscure, the neutral
  rule returning zero, the coherence term zeroed, and similarity leaking into the
  agreement-only reference. Four went red immediately. **The fifth did not: with two routes
  identical on every production term, a tie-break on lowest node id produced the expected
  path, so `test_a_dominating_weight_routes_through_the_agreeing_neighbour` passed with the
  coherence term switched off.** Fixed by expecting the higher-id route; re-mutated and now
  red. **Standing lesson: when a fixture offers two symmetric routes, assert the one a
  tie-break would not pick.**
- **B4/B5:** docstring claims checked against the imports beside them. `.claude/` swept for
  stale shape claims and references to this work — **no reference to `TAS-5`, the routing side
  or `tas_route` exists there**, so nothing in the auto-loaded layer went stale.
- **D4:** builder 129, analysis 106, api 217, frontend 107 across 18 files. All pass. The
  probe's own tests still run only when invoked explicitly — `testpaths` is unchanged by the
  owner's deferral, whose condition is **not yet due**: it fires at the closeout that
  *retires* this probe, and Task 8 is unrun.
- **Snyk:** 11 findings in the probe directory, all **Low**, all one class (a CLI path
  reaching `pathlib.Path` or `json.dump`). **Four are this session's.** Same class as the 13
  already accepted under `builder/analysis/`; it cannot be meaningfully sanitised, because
  captures deliberately live outside the repo. **Recorded in `NEXT.md`'s deferral table rather
  than absorbed** — widening an accepted-risk set is the owner's call.

---

## §17 Task 8 — the findings and the owner-facing read

**2026-08-01 (later), a fresh session at the seam the `TAS-R1`–`TAS-R4` handoff named.** No
measurement was run and no probe was re-executed: §5 licenses the outcome read now that the
full grid and both instrument checks are in hand, and Task 8 is that read. **Nothing is
adopted, no criterion, bar, weight, default, currency, vocabulary or substrate changes, and
no blind listen is spent.** Findings:
[`findings/2026-07-30-tag-discrimination.md`](findings/2026-07-30-tag-discrimination.md),
which now **owns the `TAS-` figures**; this log continues to own none.

### §17.1 The read applied, and why two bullets fire rather than one

**Not invented — located.** §5's `TAS-4`/`TAS-5` kill bars are both cleared, so the **"Both
survive"** bullet fires; `TAS-6`'s selection half is adverse, so the **"`TAS-6` adverse,
anything else positive"** bullet fires simultaneously. They are not in conflict, because they
read different things: one the kill bars, one the guard.

**What is inference, and it is labelled as such in the findings rather than presented as a §5
read:** the "Both survive" bullet anticipates *"a real decision with numbers on both sides"*,
and after the two null controls neither side supplies them. The build-time side is barred by
its own guard. The router side clears its bar on a change `TAS-AM5c` says is not attributable
to genre. **So the architecture question is closed rather than open.** The distinction between
the located read and the inference drawn from it is kept visible on the page, because a session
concluding that a pre-registered "this is now the owner's live choice" is in fact moot is
exactly the move that should be checkable.

### §17.2 One verification before building on the handoff

Per `session-start`'s third check, one load-bearing claim was checked against source rather
than accepted from the handoff's prose: that `TAS-6`'s routing half is **vacuous by
construction**. `tas_guard.py:111` returns `False` outright when the baseline is zero, before
any arithmetic — so every `adverse: false` in `tas_route_guard.json`'s routing table is a
hard-coded early return, not a measurement. **Confirmed; the handoff's claim is exact.**

### §17.3 What the findings carry that no earlier document did

- **The two `TAS-6` halves are put side by side with their asymmetry stated** — one adverse on
  a 93-edge denominator, one unmeasurable on a zero baseline — where previously each lived in
  its own session's section.
- **The broader sub-decile-touching count is reported beside `TAS-6`'s narrow one** (10,017 →
  9,658, a 3.6% fall against the narrow measure's 15.05%), explicitly *reported rather than
  substituted for it*. The pre-registered quantity governs; the reader gets to see the other.
- **The two sub-decile interiors the routing guard found at the top two weights are surfaced as
  an unscored observation** rather than dropped. No criterion scores them, n = 2 of 120, and
  the null grid returns zero everywhere — so it is the one place the real frame differs from a
  permuted one. **It licenses nothing**, and saying so is the point: it is the most
  encouraging-looking number in the routing record and it is the one with the least behind it.
- **`W4` is named as dominating `W6`** in the findings' own vocabulary table, so a future
  amendment cannot pick up `W6` from this record.

### §17.4 A defect in this task's own first draft — two reach deltas in different currencies

**Caught by re-deriving every transcribed figure from the JSON rather than trusting the
transcription.** The first draft of the findings reported the `TAS-AM4` reach gain as "+27.7
points for `W1`, +36.3 for `W6`". Those are `tas_frame_eval.json`'s
`acting_slot_change_vs_W0`, which is a **relative** change (0.1824 / 0.658 = 0.2772). In
points the gain is **+18.2** and **+23.9**.

**What makes it worth a section rather than a silent fix: the same document holds a second
reach delta in the *other* currency.** `tas_frame_split.json`'s `reach_change_pts` is
genuinely percentage points, and it feeds the isolation table two paragraphs below the
error. So the draft had two adjacent reach figures in different units with nothing marking
the difference — the exact shape of the confusion `CLAUDE.md`'s orient table opens with, in
a quantity nobody had thought to name a currency for.

**Fixed by stating both units explicitly** rather than by converting one to the other, since
both JSON fields keep their own units and a future reader will meet them directly. The
findings carry a currency note at that table.

**No other figure moved.** Every number in the findings was re-derived from its JSON; this
was the only disagreement.

### §17.5 The three owner-facing checks, run rather than claimed

Run over §17.6's summary before it was written into this log.

- **(a) Bare letter-number tokens.** Scanned; the summary below contains **none**. Every
  criterion is named by what it asks, not by its identifier.
- **(b) Substitution re-read.** Each identifier's plain sentence was substituted and the claim
  re-read for drift. One caught and fixed: a draft sentence read *"the safety check could not
  fire"*, which is broader than the criterion — the guard **did** run and returned a value; what
  could not happen is a *measurable reduction*, because the baseline was zero. Corrected to say
  so.
- **(c) Could the owner disagree?** Yes, and the two places he most plausibly would are named
  in the summary: whether 93 connections is enough to call a guard's verdict material, and
  whether "not about genre" is the right reading of a control that permutes labels rather than
  removing them.

### §17.6 The owner-facing summary (four parts, in order)

**Queued to `TEST-QUEUE.md` at closeout; reproduced here because this log is the durable
record and the queue is rewritten.**

#### Measured

- Genre labels are present at both ends of **99.96%** of connections between two well-known
  artists, **55.03%** where one is obscure, **17.12%** where both are.
- Among the artists similar to a given artist, genre overlap varies: median spread **0.1726**
  against a **0.02** floor below which the idea was to be abandoned.
- Genre overlap and the similarity score agree weakly — rank correlation **0.1857**; the two
  orderings coincide on **3.07%** of candidate lists.
- Using genre to pick connections when the map is built changes **16.4%** of all connections at
  the gentlest setting and **40.4%** at the strongest, against a **1%** line for "changes
  nothing worth caring about". Connections created outnumber those deleted at every setting; the
  map ends **11.7%** larger at the strongest.
- Direct connections from a well-known artist to an obscure one fall from **93** to **87 / 85 /
  83 / 79** across the four settings — past the pre-set 10% line at the top two.
- Using genre to price each step as a journey is built changes **90–100%** of journeys at every
  setting.
- Scrambling which artist owns which labels reproduces **98.2–99.1%** of that journey change.
- Across all 120 test journeys, the app currently delivers **zero** artists from the
  least-famous tenth in the middle of a journey.
- Every measuring-instrument check passed: the experiment's copy of the route-builder returns
  the app's own answer on all 120 journeys with the genre setting off, and goes exactly where
  genre alone dictates when genre is turned up to dominate.

#### What I infer from it — labelled as inference

**The idea was sound and it still does not work, and those are two different findings.**

Genre labels genuinely tell an artist's similar artists apart, and they are not just repeating
what the similarity data already knows. That was the assumption everything rested on and it
held. Had it failed, the whole thread would have died cheaply and correctly.

**Building the map with genre would make the app worse at the thing you called a defect.**
Direct connections from a famous artist down to an obscure one drop at every setting and cross
the line you set at the top two. The reason is mechanical: artists with no genre label are
disproportionately the obscure ones, and while the rule is careful not to punish them, it
cannot stop them being edged out when labelled artists get promoted past them. **A rule written
before any of this ran says an adverse result here blocks a recommendation whatever else looks
good, and I am applying it rather than arguing around it.**

**The journey-pricing side looked like a success and the control took it away.** Turning genre
on changed almost every journey. Then we scrambled which artist owns which labels — keeping
exactly the same artists labelled — and almost exactly the same journeys changed. **So what we
measured was not genre. It is what happens when you add any new per-step cost to a long
journey**, where one substitution anywhere makes the whole thing count as changed. This is the
fourth attempt to change routing by changing prices that has come back empty, and the first
that looked like it worked until the control ran.

**One thing found by accident is worth more than the experiment's own result.** On all 120
journeys tested, the app puts **nobody** from the least-famous tenth in the middle of a journey.
Not few — none. That is your defect measured more sharply than anything else we have, and it
also meant the safety check written for this experiment had nothing it could measure: you cannot
measure a fall from zero.

#### Weakest link

**The treatment of artists with no genre label is doing the most work, and it is the thing to
attack.** Where an artist has no labels we score it at that artist's own typical agreement
rather than at zero — deliberately, because zero would be a claim that they are *dissimilar*,
and that would push obscure artists down exactly where the app needs them up. It was fixed in
writing before anything ran and never adjusted. But it is inert until the feature is switched
on, so the baseline run cannot reveal a bad choice of it, and **a different rule here could
move the obscurity result in either direction.**

**Two places you could reasonably disagree with me.** First, the guard's verdict rests on
**93** connections out of nearly half a million — a thin denominator, which cuts both ways: it
is also a statement about how few famous-to-obscure connections this map has at all. The bar
fired as written and no bar may move now, but you may judge the absolute effect small. Second,
you may think permuting labels is too harsh a control — it keeps the same artists labelled but
gives them each other's genres, and one could argue that destroys something real rather than
isolating it.

#### Options and their consequences

**None of these is a recommendation dressed as a finding, and the choice is yours because each
spends your time or your ear rather than being methodology.**

1. **Retire the thread here.** The question the probe was commissioned to answer — which of the
   two architectures — has an answer: neither, on this evidence. Costs nothing; leaves the
   coherence idea's structural half parked and the 11 blind listening verdicts unspent.
2. **Re-ask it after a richer set of labels.** The parallel investigation more than doubled how
   many obscure artists we know a genre for, which attacks the exact cause of the adverse
   result. **Nothing measured says it would flip** — that needs a rebuilt map, and the rebuild
   is the expensive part.
3. **Take the accidental finding instead.** The zero obscure artists mid-journey is the sharpest
   measurement of your defect on record, and it points at the map-building re-question rather
   than at genre.

**What I am not offering:** any adoption, any weight change, any rebuild, or a listening test.
All four are barred by the document this probe was run under, and none of the evidence here is
the kind that could license one.

### §17.7 Deferrals — one closed, none opened

**Closed by this task:** *"Task 8 — the `TAS-` findings document is unwritten"*, whose condition
was **before the probe is retired**. Both of its clauses are honoured and checkable on the page:
`TAS-AM5c`'s caveat is carried on `TAS-5`'s section head and repeated at its figures, and
`TAS-6`'s routing half is marked **VACUOUS** with its mechanism (`tas_guard.py:111`) rather than
read as a pass.

**No new deferral is opened.** Every other `TAS-` row in `NEXT.md`'s table stands unchanged,
including the two that a findings document might have looked like it discharged: the
**edge-count growth** row still binds any rebuild pre-registration, and the **`TAS-6` routing
half is unmeasurable** row still fires only if an obscure-endpoint draw is ever made for routing.
**The `testpaths` row's condition is now due** — it fires "at the closeout that retires the
`TAS-` probe", and this is that closeout — and it is the owner's deferral to resolve, not a
session's; it is flagged, not actioned.
