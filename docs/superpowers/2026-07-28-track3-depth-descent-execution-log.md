# Track 3 — the depth-descent device: execution log

**Role: RETAINED EXECUTION LOG for Track 3.** Appended per task, not only at closeout.
Governing document: [`specs/2026-07-28-track3-depth-descent-preregistration.md`](specs/2026-07-28-track3-depth-descent-preregistration.md)
— where this log and it disagree about design, **it wins**; where they disagree about
what was *run*, this log wins.

**Owns no figures that belong elsewhere.** Scoring/path-quality figures live in
`findings/2026-07-21-scoring-adjudication.md`. Track 3's own measurements are owned by
`builder/analysis/2026-07-28-track3-depth-descent/` and cited from here.

Discharge order (prereg §4): **DD-P2 → DD-P1 → DD-P3 → DD-P4**, then arms.

Artifact throughout: `graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`, asserted
by every script (DD-G3). N = 74,193, E = 898,006.

---

## §1 — DD-P2: the pair set. DISCHARGED.

Twelve pairs drawn and frozen in
[`builder/analysis/2026-07-28-track3-depth-descent/pairs.json`](../../builder/analysis/2026-07-28-track3-depth-descent/pairs.json)
by `draw_pairs.py`, seed 20260728, sorted-MBID base ordering. Committed before any arm.

**Band edges, made half-open so the bands are disjoint:** famous = pctl ≥ 0.90 (the same
top decile DD-P1 removes), mid = pctl ∈ [0.50, 0.90). Pool sizes at degree > 1: famous
7,403; mid 29,399.

### Two rules the pre-registration could not fix itself

**DD-D1 — the carry-over count is wrong in the pre-registration.** DD-P2 says "the 4
Track 2 analysis pairs with famous endpoints". Measured on the artifact there are **6**:
Miles Davis→Daft Punk, Metallica→Taylor Swift, Radiohead→The Beatles, Muse→Coldplay,
Madonna→Bob Dylan, Pink Floyd→Aphex Twin. The two Track 2 analysis pairs that miss are
The Shins→Wishbone Ash (0.876) and Nirvana→CROOVE (0.851) — both fail on the *second*
endpoint. This is the CLAUDE.md failure shape "documents asserting things about the world
that aren't true", caught by the pre-execution grep rather than after a run.

The count **4** is load-bearing — it makes 12 pairs, the 8/4 split, and the deliberately
minority all-famous slice. *Which* 4 is not. **Rule adopted: the first 4 both-famous
pairs in the frozen `ANALYSIS_PAIRS` order** (`2026-07-23-track2-sweep/verify_mirror.py`,
committed 2026-07-23). That ordering predates Track 3, so it cannot have been chosen to
suit a Track 3 result — the only property the tie-break needs. Recorded as experimental
bookkeeping (the owner's decision table puts pair selection on the session's side), not
escalated.

**DD-D2 — the held-out composition was unspecified.** "8 analysis / 4 held-out, assigned
by the same seed" does not say how the four are spread, and an unstratified draw can
empty a group. **Rule adopted: stratified — 2 carry-over, 1 famous→mid, 1 mid→mid.** Two
carry-overs go because the all-famous slice is least informative for the owner's goal
(PLA-R1: famous-pair first paths are structurally forced; famous-pair first-path fame is
*barred* as a criterion by prereg §7) and because the pre-registration's own rationale
wants that slice in the minority. Analysis therefore holds 2 all-famous / 3 famous→mid /
3 mid→mid, and every group keeps an anchor in both halves. **No criterion in the
pre-registration reads the held-out set**; it is confirmatory only, which is why this is
low-stakes bookkeeping rather than a design change.

### Exclusions

Degree-1 endpoints excluded from both pools. Guard-compliance tested **directly** — the
mirror at production config with guard G ON, requiring a d0 path with a non-empty
interior — rather than by looking `MKS-6` up in a table. That test subsumes `MKS-6`
exactly: a no-detour pair is precisely one where guard G cannot produce an interior.

**Zero rejections of either kind across the whole draw.** Expected in hindsight and worth
stating: `MKS-6`'s 6,599 no-detour pairs are *adjacent* pairs, and randomly drawn
cross-band endpoints are essentially never adjacent. The exclusion is therefore in force
but was never load-bearing here.

### The set

| group | analysis | held out |
|---|---|---|
| carry-over (all-famous) | Metallica→Taylor Swift; Muse→Coldplay | Miles Davis→Daft Punk; Radiohead→The Beatles |
| famous→mid | The Mills Brothers→Tracey Chattaway; Daniel Avery→Rita Marley; Lykke Li→Nobunny | Megadeth→Mala Rodríguez |
| mid→mid | Verbose→Daniel Herskedal; Menswear→洲崎綾; Natasha Kmeto→Vanbot | t-low→L‐Vis 1990 |

Endpoint percentiles and degrees are in `pairs.json`; not restated here.

---

## §2 — DD-P1: depth headroom. DISCHARGED, after the prescribed re-draw.

**Figures owned by `builder/analysis/2026-07-28-track3-depth-descent/`**
(`headroom.json`, `headroom_v2.json`), cited here, not restated elsewhere.

Instrument: BFS on the induced subgraph (top-decile pctl ≥ 0.90 removed, endpoints
exempt, that cell's exclusion set applied, direct edge masked so the result is always
guard-compliant), against P's delivered hop count + 2. The walk is the committed
`run_arms.walk`; exclusion sequences are reconstructed under the walker's own victim
rule and asserted to lie in the preceding interior.

### First run (`pairs.json`) — trigger fired at 50 %

18 of 36 C1-window cells lacked headroom (37.5 % analysis-only). No infeasible cells.
The failure is **all-or-nothing per pair** — every pair had headroom at all nine
snapshot depths or at none — and perfectly stratified by band: carry-over 0/36 cells,
famous→mid 18/36 (2 of 4 pairs), mid→mid 36/36.

**DD-F1 — the mechanism, measured not inferred.** Every failing pair has an endpoint
with **0 or 1 edges to the bottom 90 %**. Removing the top decile does not lengthen
these journeys, it *disconnects* them: Radiohead, Metallica, Muse, Coldplay, Taylor
Swift, Miles Davis, Madonna, Bob Dylan, Pink Floyd, Aphex Twin and Megadeth each have
degree 29–50 in the graph and **degree 0** in the sub-decile graph. Across the whole
artifact the share of artists with zero sub-decile edges rises **4.5 % → 10.3 % →
20.1 % → 45.1 % → 80.0 %** across the pctl bands [0.900,0.950), [0.950,0.980),
[0.980,0.990), [0.990,0.999), [0.999,1.000). This is the per-pair, all-depths extension
of PLA-R1 and is consistent with §2.10's famous↔obscure edge depletion under mutual
k-NN.

**Band edges are stated in full deliberately.** The series is reproducible only under
these exact edges — DD-P3 had to search six schemes to recover them from an elided
quotation, and two neighbouring schemes give visibly different numbers. Reproduced by
`dd_f1_provenance.py` → `dd_f1_provenance.json`, which also owns the named endpoints'
sub-decile degrees; before it, no committed script computed the quantity the log quoted.

**DD-F2 — the +2 hop slack never bound anything.** All 54 failing cells were
*unreachable*, none "reachable but too long", so the slack constant did no work. Where
an obscure route exists it is **5–8 hops against production's 8–19** — the obscure
route is consistently *shorter* than what production delivers. Production is not
avoiding obscure middles because they are far; `w_hop` is 0.02 against `w_sim` 3.0, so
it is buying similarity with hops. **This is a design input for DD-R2 and it was not
anticipated by the pre-registration.**

### DD-D3 — the branch trigger is unsatisfiable by construction

C1-window = 12 pairs × 3 depths = 36 cells; the carry-over slice is 4 × 3 = 12. **All
six** both-famous carry-over candidates have an endpoint with zero sub-decile edges, so
any permitted choice of 4 contributes 12/36 = **33.3 % lacking headroom against a 30 %
trigger** — the trigger fires for every permitted pair set, with or without headroom
anywhere else. A trigger that cannot be cleared cannot discriminate, and its remedy
cannot change its state.

DD-R3's read ("the graph does not offer obscure middles near these journeys at all")
is **contradicted by the measurement that would trigger it**: headroom was found on 6
of 12 pairs. The trigger conflates *the pair set contains pairs where the question
cannot be asked* with *the question has no answer*. Recorded as a pre-registration
defect of the shape CLAUDE.md names — a gate whose effect size was never checked
against the design feeding it.

### The remedy, executed so it can succeed

The prescribed remedy is "re-draw the pair set once". Executed in `draw_pairs_v2.py`
with **DD-P1 headroom as a draw-time precondition** — the one change that lets a
re-draw move the trigger. Same seed, one draw, no re-seeding. Scored set is now 12
headroom-passing pairs (6 famous→mid, 6 mid→mid), split 8 analysis / 4 held-out, 4/2
per group: every count the pre-registration fixed is preserved.

**The all-famous slice is retained but UNSCORED** — walked for DD-G2 (first-path
identity), excluded from DD-C1/C2/C4/C5. It cannot pass DD-P1 by any choice of pairs,
so it can no longer anchor a fame criterion, and prereg §7 already bars scoring
famous-pair first-path fame.

**Result on the re-drawn set: 108/108 cells with headroom, 0 % lacking, 0 infeasible,
trigger not fired.** Draw-time acceptance at d0 held at all nine depths — expected,
since the walker's victims are the *most popular* interiors, which the sub-decile
subgraph has already removed, so exclusions barely touch it.

**DD-R2's precondition is now satisfied at 100 %** (it needs ≥ 70 %), which is what
makes a Track 3 null interpretable as a mechanism-strength statement rather than an
artefact of a pair set with nowhere to go.

### Weakest link

DD-P1 as written is **conservative**: it demands a path whose interiors are *all*
sub-decile, but the device only rewards descent proportionally and never requires a
fully sub-decile path. So headroom is sufficient for the device to have somewhere to
go, not necessary — pairs it rejected may still admit substantial partial descent. This
matters for how far DD-F1 generalises: it licenses "superstar endpoints cannot be
routed through an all-obscure interior", **not** "superstar journeys cannot be made
more obscure at all". The stronger claim is not measured here and must not be quoted
from this log.

**Consequence to carry forward:** "famous" in the scored set now means *top-decile but
not superstar*. Drawn famous endpoints span pctl 0.9102–0.9966, so the band is not
collapsed to the bottom of the decile — but the pctl ≥ 0.999 band is structurally
incapable of supporting this question at any price.

---

## §3 — DD-P3: analyst protocol review. FIRST HALF DISCHARGED.

Dispatched on the owner's explicit instruction (a session does not dispatch a subagent
here unsolicited). Report: `builder/analysis/2026-07-28-track3-depth-descent/DD-P3-analyst-review.md`;
probes in `dd_p3_review_probes.py`. Derivation only, per its remit — it was not asked
whether the track should proceed and did not say.

**Confirmed clean:** the DD-P1 instrument on all four sub-questions, including a runtime
spy on the exclusion lists actually passed to `find_path_mirror` across 21 depths on 4
pairs (worth having — `obscure_hops` being constant across depths is also the signature
of a silently unapplied exclusion set); DD-D3's unsatisfiability arithmetic, exactly,
with two strengthenings the log had omitted; §2's realised-toll figures; the device's
well-posedness as a Dijkstra node potential.

**Two load-bearing findings re-verified by this session** rather than taken on report,
per the standing rule about building on another agent's conclusions. Both reproduce.

### DD-D4 — DD-A4 and DD-A5 are struck from the run

The floor base is `min(pop_raw)` over the endpoints, measured 0.3081–0.4570 on the
scored set, and it relaxes 0.15 per `known` — so **the floor is dead from k = 3** (k = 4
on one pair). The shallowest depth any criterion reads is d5. Therefore DD-A4's cost
function is **bit-identical to DD-A2's, and DD-A5's to DD-A3's, at every scored depth**:
a third of the planned run cannot move any criterion. The floor axis is answerable only
at d ∈ {0,1,2}, which §5 does not read.

Worse, they would **fail DD-G2**: turning `w_floor` off changes the d0 path on
Miles Davis→Daft Punk (7 hops vs 6). §3 says a gate failure voids the run, and the
correct d0 reference for a floor-off arm is a floor-off zero-ramp arm, which Track 3's
arm list does not contain.

**Struck. The run is P, DD-A1, DD-A2, DD-A3.** Note the causation honestly: §0's
argument for making the floor a live axis was correct against Track 2's famous pairs
(floor alive to k ≤ 4–6) and was **voided by this session's own re-draw**, which moved
the pair set obscure enough that the floor dies almost immediately.

### DD-D5 — the device prices length and obscurity inseparably; §5 cannot attribute

`w · k · Σ_interior pctl` factorises as *(interior count) × (mean interior pctl)*. Over
the 8 analysis pairs at k = 10 the **length share of the toll differential runs
69.6 %–96.1 %, median 80.7 %** — the device is around four-fifths a hop-count penalty.
And the graph forecloses disentangling it after the fact: **on 6 of 12 pairs the
unweighted shortest path is already entirely sub-decile** (independently reproduced this
session — the same six), while production takes 10–17 hops through interiors at pctl
0.94–0.99.

So an arm that moves DD-C1 cannot be shown to have found obscurer artists rather than
simply *shorter paths*. Track 2 had the instrument for this — `score.py`'s C4 payload
guard, written against WGLL value 2 — and **§5 has no equivalent**; DD-C5 does not
cover it, since a count of distinct sub-decile interiors rises with obscurity and does
not fall with shortening. Finding 8 compounds it: pooled-median scoring is mechanically
biased by length, and pure shortening alone moves the DD-C2 statistic 0.026–0.064
downward with **zero** descent.

**Adopted: DD-C6, a length control, fixed now with its plain sentence.** Mean interior
count per arm vs P at the same cell. *(Plain: does the journey still have about as many
artists in it, or did the app just make it shorter?)* An arm whose mean interior count
falls more than **1.0** below P's is flagged in every table it appears in, and **DD-C1
may not be read as descent for a flagged arm**. This is a qualifier on attribution, not
a new success criterion — it cannot make a null into a pass.

### DD-D6 — the currency gap, and the cheapest decisive test left

DD-P1 certifies headroom in **percentile**; DD-C1/DD-C2 score in **fame** (log10
pageviews). "An all-sub-decile route exists" does not entail "a route 1.0 log10 F below
production's" — the §2.12 currency trap, in a new place. The analyst could not bound the
gap (only 239 mbids join Track 2's `fame.json` to pctl, 202 of them at pctl ≥ 0.99).

**This runs before any arm.** Implemented in `dd_d6_gap.py`, and strengthened from what
the analyst proposed: rather than scoring the *shortest* all-obscure route (an existence
witness, not an optimum), it computes the **`w → ∞` ceiling** — the path minimising
Σ pctl over interiors, which is the limit the device converges to as its strength grows.
No arm at any `w` can be more obscure than that. The ceiling is computed directly rather
than through the device, **so a bug in DD-P4's toll can neither flatter nor spoil it**.
If the ceiling's fame gap is well short of −1.0 log10, DD-C1 is unreachable at any
strength and the dose ladder is answering a question whose answer is already fixed.

**DD-G4 correction.** Its first half is **already satisfied by committed code**:
`fame.py` emits a table keyed by mbid (`"keyed_by": "mbid"`, P8b F8), and the name-keyed
*cache* underneath it is deliberate and correct — two nodes sharing a name share a
Wikipedia article. This session initially read the name-keyed cache as the defect DD-G4
names; it is not. What **is** outstanding is DD-G4's second half, the assertion that no
scored interior is blank-named, which `fame.py` does not enforce (it marks nameless nodes
and `score.py` merely excludes them from C2 reach). That assertion is implemented in
`dd_d6_gap.py::score` and must be carried into DD-P4's scorer — the arms that dive aim
exactly where blank names concentrate, which is why the pre-registration made it a gate
rather than a deferral.

### Carried into DD-P4

- **DD-D7** — implement the toll on the **edge-relaxation target** (`cost(u→v) +=`), not
  on node settle; a node-settled implementation silently prices nodes that never appear
  on the returned path.
- Count guard-G activations per arm beside `floor_active` (finding 10: guard G is listed
  constant as a *setting*, but its activation is not, and the device makes the 2-node
  direct path uniquely toll-free).
- The directory needs a `README.md` (2026-07-23 spec §4.2) and no committed script
  computes sub-decile degree, though DD-F1 quotes it.

### DD-D6 result — DD-C1 is reachable, and the mechanism is shortening

Figures owned by `gap_result.json` / `gap_paths.json`. Fame matched 322/366 = 88.0 %
(reported, not gated — A12); 11 unmatched-but-potentially-notable carry the A11 guard.
DD-G4's blank-name assertion passed: no scored interior is blank-named.

**The ceiling clears DD-C1 comfortably.** Mean fame gap against production, C1 window
(d ≥ 10), analysis pairs: **−2.72 log10** (median −3.15, range −4.49 to −0.32), with
**19 of 24 cells** past DD-C1's −1.0. So the track is not chasing an unreachable
threshold, and the dose ladder is worth running.

**But the ceiling reaches it by cutting the journey, not by swapping artists.** Interior
count, C1 window: production median **13**, ceiling median **5** — a median drop of 8.
DD-C6 flags this by a wide margin, so **the ceiling's DD-C1 movement may not be read as
descent**. This is DD-D5 confirmed at the limit rather than argued.

**And the counterweight, which inverts the obvious reading.** Counting sub-decile
interiors in absolute terms — the discovery-payload shape WGLL value 1 defines, an
absolute count and not a rate:

| C1 window, analysis (n = 24) | production | ceiling |
|---|---|---|
| interiors | 13 | 5 |
| of those, below pctl 0.90 | 2 | 5 |

**The ceiling delivers more genuinely obscure artists in 24 of 24 cells — no
exceptions** (48/48 across all cells; mean payload 1.54 → 4.88). Production's long path
is mostly a parade of well-known artists carrying about two obscure ones; the ceiling is
a short path that is almost entirely obscure. So the shortening does **not** cost novelty
in the owner's own metric — it raises both the rate and the absolute count.

**This lands on a genuine tension between two recorded owner values, and resolving it is
his, not a session's.** WGLL **value 1** measures novelty as an absolute count and its
worked example has more artists winning — the ceiling satisfies it. WGLL **value 2** says
bypass should *lengthen* the path **and** increase novelty, "both, or neither counts" —
the ceiling fails its lengthening half while passing its novelty half. His stated Track 3
goal is phrased as *frequency* of obscure artists in interiors, which the ceiling improves
on both readings (2/13 → 5/5).

**Nothing here decides that.** WGLL records preference, not evidence, and a threshold may
never be read off it. The arms are run as pre-registered; DD-C5 (payload) and DD-C6
(length) are both reported beside DD-C1 at DD-R1, and the trade-off is put to the owner in
those terms rather than resolved by a criterion. **No blind listen is scheduled by this
finding** — that remains his call.

---

## §5 — DD-P4 and the arms. RUN COMPLETE; DD-R1 fires.

**Figures owned by `builder/analysis/2026-07-28-track3-depth-descent/REPORT.md` and
`t3_scores.json`.** Not restated here beyond what a read needs.

`mirror.py` gained `w_known_ramp_pctl`, default 0.0, applied to the edge-relaxation
target (DD-D7) with the target endpoint exempt, added only when live so production's
expression is executed unchanged. **DD-G1 re-earned** (byte-identical on 212/212 cells);
**DD-G2/DD-C3 PASS** on all 16 pairs including anchors. Snyk clean on both touched
directories. `run_arms_t3.py` imports the committed walker rather than adding a flag to
it, so no committed Track 2 file changed and every Track 2 figure still reproduces.

**DD-P3 finding 10 did not materialise.** Guard G fired 42 times in *every* arm
including P, and the floor stayed live on 1.11–1.19 % of relaxations across all four.
Neither varies with the knob — so the one term §0 could not certify as constant is
constant in fact. Known because it was counted, not because it was assumed.

**DD-R1 fires — an adoptable candidate exists.** DD-A2 (`w = 0.03`) passes DD-C1 and
DD-C2 with DD-C3 holding, and DD-R1's presupposed run state is satisfied in full;
nothing is owed for this read. **DD-R2 and DD-R3 do not apply.**

**Both qualifiers fire on every arm.** DD-C6: the journey shortens by a mean 5.74
interiors at DD-A2 (~13 → ~7), so **DD-C1 may not be read as descent** — the DD-D5
confound arriving exactly where predicted, which is why DD-C6 was adopted before the run
and not after seeing the table. DD-C4: median per-hop similarity falls 0.980 → 0.736.
DD-C4 gates nothing by design (offline coherence metrics were the worst predictors of the
owner's verdict), but a 0.244 drop is not a rounding error.

**Two findings the pre-registration did not anticipate.** (1) Production **fails DD-C2 in
the negative direction** — its middles get *more* famous as bypasses accumulate. The
owner's original complaint, in fame currency, on this pair set, for the first time. (2)
DD-C2 is **non-monotone in `w`**: at the strong dose the path is near-maximally obscure by
d5, leaving little room to descend by d20, so the gradient compresses against its own
floor. **DD-A3 is not "more of DD-A2"** — it trades depth-gradient for absolute obscurity.

**What is owed to the owner and to nobody else:** whether ~7 mostly-obscure artists beat
~13 mostly-famous ones carrying about 1.5 obscure. It lands on the value tension recorded
in §4. **No blind listen and no adoption are scheduled by this track** (prereg §7).

### Selection effect of the re-draw, bounded

Unconditioned Monte-Carlo (300 draws/group): acceptance 83.3 % famous→mid, 99.3 %
mid→mid. If an excluded pair's true effect lies between zero and the included pairs',
the conditioned DD-C1 estimate overstates the unconditioned mean by **≤ 9.5 % relative**
(≈0.09 log10 against a −1.0 threshold). One slice, n = 300/group, not reproduced —
treat as indicative. The bound breaks only if excluded pairs' effect has the opposite
sign, which DD-D5 makes live rather than free. Relative to journeys a *user* would
actually request the selection is much larger and **unmeasured**; there is no request
log. Composition shifts toward lower percentile, not lower degree — sub-decile degree is
the discriminating variable (median 8 accepted vs 0 rejected), another case where degree
and popularity answer differently.
