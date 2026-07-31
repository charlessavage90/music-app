# Retained execution log — tag discrimination probe (`TAS-`), 2026-07-30

**Role: RETAINED EXECUTION LOG. Owns no figures.** Criteria figures belong to
`builder/analysis/2026-07-30-tag-discrimination/` and the findings document written when
the probe completes; scoring and path-quality figures stay in
`findings/2026-07-21-scoring-adjudication.md`. Cited here, never restated.

Governing document: [`specs/2026-07-30-tag-discrimination-probe-preregistration.md`](specs/2026-07-30-tag-discrimination-probe-preregistration.md).
Plan: [`plans/2026-07-30-tag-discrimination-probe.md`](plans/2026-07-30-tag-discrimination-probe.md).
Handoff: [`2026-07-30-HANDOFF-tag-discrimination.md`](2026-07-30-HANDOFF-tag-discrimination.md).

**Scope reached: Tasks 1–4 of 8.** Three gate reads resolved and passed. Tasks 5–8 unrun.
Task 4 was executed by a second session on 2026-07-30 and is recorded in **§9**, appended
rather than folded into the sections above so the two sessions' work stays separable.

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
3. **`COH-6` is the closest prior result and should be read before spending.** It measured the
   widest-vocabulary variant as near-identical *in the tail*, which is prior evidence that
   widening the vocabulary does not help where it matters. It does **not** settle the question
   — release tags aggregated over a discography are genuinely different from artist-level wide
   tags — but it is the relevant base rate. `COH-5` separately measured ListenBrainz as a
   99.9%-faithful transport for MusicBrainz *genres*, so MB genres are already in hand.
4. **Discogs is a genuinely independent source**, unlike anything in the current frame, and so
   does not inherit MusicBrainz's blind spot. It carries the **population-mismatch** trap
   instead — the one that killed every external popularity source — plus a Discogs-ID ↔ MBID
   mapping problem whose coverage must be measured before any tag figure derived through it
   means anything.

**Practical note for that session:** the adopted artifact and the archive are **gitignored**,
so they do not appear in a `git worktree`. Any coverage measurement against the real population
must point at `builder/scratch/` in the main tree explicitly.
