# Track 3b pre-registration — the thresholded toll

**Role: ACTIVE pre-registration. No experimental arm runs until this document is
committed, and its commit timestamp is the evidence of ordering.** Identifiers are
namespaced **`TB-`** — verified unused across the repository before allocation
(2026-07-29), disjoint from `DD-`, `TF-`, `PLA-`, `ASC-`, `MKS-`, `CNS-`, `STC-`,
`SYN-`, `CWD-`, `REQ-`, `PW-`, `MIG-`, `UI-`, `TK*-`, `BTF-`, `BYP-`. Forward-only;
nothing committed is renamed.

**Commissioned** by the owner 2026-07-29, following the ruling that scored as
follows: Track 3's DD-R1 produced a candidate whose mechanism is UNRESOLVED because
DD-C6 flagged every arm (the fame movement is substantially shortening, not descent).
This track runs the named successor from the Track 3 execution log §7 — the device
that is length-neutral exactly where that confound lives. It is **not a tweak to
Track 3**: the device changes, so it gets its own design, gates and reads, per that
log's own instruction.

**The first governing requirements document is
[`PRODUCT-REQUIREMENTS.md`](../PRODUCT-REQUIREMENTS.md)** — the first track designed
against it. The requirements it serves: REQ-13 *(repeated bypasses must dig up less
famous artists)*, REQ-14 *(no bypass mechanism may treat length as its objective —
which this device satisfies by construction, unlike Track 3's)*, REQ-9 *(novelty
through coherence — untestable offline; TB-C4 is a tripwire only)*. Payload currency
follows the REQ-Q1 ruling (fame, dual-reported, A11 guard read, mbid-keyed frozen
snapshots).

**Scope guards.** No shipped code changes: everything runs in the committed mirror
harness (`builder/analysis/2026-07-23-track2-sweep/mirror.py`), behind a config field
defaulting to 0.0 that **stays** 0.0. No rebuild (`acceptance.py`'s nameless-artist
gate not in play). No blind listen is scheduled by this document — the sequencing
decision of 2026-07-29 defers any listen to the full stack (graph + device), and
surfacing one earlier is the owner's decision alone. Thresholds reuse Track 2's
committed calibration (band gap 1.093 ≈ one owner perception band) — reused, not
re-derived. **No figure here is comparable to Track 3's own except where the pair set
and statistic are identical and the comparison says so.**

---

## §0 — Held constant, and why each is genuinely constant under the intervention

Enumerated per the CLAUDE.md rule. The entry that matters most is the floor, because
Track 3 made it an axis and this track does not — the reason must be measured, not
assumed.

| term | held at | why it stays constant under this intervention |
|---|---|---|
| `w_sim = 3.0`, similarity scores | production | the device adds a node toll; it never touches the sim term. Realised hop similarity is an outcome (TB-C4), not a knob. |
| `w_jump = 1.0`, raw currency | production | untouched; licensed constant by PLA-R4 (jump price immaterial at path level in both currencies). |
| `w_degree_hub = 0.0` | production | degree appears nowhere in the device. |
| `w_hop = 0.02` | production | the unit all magnitudes below are stated in. |
| **the raw floor (`w_floor`)** | **production RAW — constant, NOT an axis, and here is why that is safe** | the floor term depends only on the endpoints' min `pop_raw` and on k (relaxing 0.15 per `known`), never on path content — so no device can wake it. On **this** pair set it is dead from k = 3 (k = 4 on one pair): floor bases 0.3081–0.4570, measured at DD-D4. The shallowest scored depth is d5. A floor axis here would reproduce Track 3's struck arms (DD-A4/DD-A5, bit-identical at every scored depth) — **and re-adding them is barred by `NEXT.md`'s closed list.** The floor axis is answerable only at d ∈ {0,1,2}, which nothing scores. |
| guard G (min one intermediary) | ON everywhere incl. P | as Track 2 §1.2. Activations are **counted per arm** (Track 3's carried item): no scored pair is adjacent, so expected exposure is zero on scored pairs — an activation on a scored pair is an anomaly to investigate, not data. |
| the knee, **0.90** | fixed, not an axis | 0.90 is the boundary the whole instrument chain is calibrated at: DD-P1 headroom certifies sub-decile routes, DD-C5/TB-C5 count sub-decile interiors, DD-F1's structural finding is stated at it. Varying the knee is a second factor column and doubles the run for a question (knee placement) that only matters if the mechanism works at all. **Pre-committed follow-up, not smuggled in:** a knee axis may be proposed only after TB-R1, in its own amendment. |
| victim rule, all-`known` walk, snapshots {0,1,2,3,5,7,10,15,20}, max depth 20 | Track 2's exactly | imported from committed `run_arms.py` lineage (`run_arms_t3.py` precedent: import, never reimplement). The `dislike` ramp is out of scope — REQ-30/REQ-31 make it a different mechanism; noted, not smuggled in. |
| pair set | `pairs_v2.json`, frozen | inherited unchanged (§3). The device cannot alter a frozen file; re-drawing would break comparability with Track 3 for no design reason. |
| fame instrument | A11 exactly (`builder/analysis/2026-07-24-track2-arm-scorer/fame.py`), extended not modified | new interiors need fame fetches (TB-P2), appended to a frozen mbid-keyed snapshot. The encoding (unmatched → floor) is the owner's adopted decision and is not revisited here; its exposure is handled at TB-C1's robustness conditions instead. |

## §1 — The device

One added toll in **percentile currency**, applied on the edge-relaxation target
(DD-D7's rule — a node-settled implementation silently prices nodes that never appear
on the returned path):

> `cost(u→v) += w_known_thresh_pctl · k · max(0, pop_pctl(v) − 0.90)`
> for every relaxed target `v` except the destination endpoint,
> where `k` = number of `known` bypasses so far.

- **At k = 0 the term is exactly zero** — the first path is production's by
  construction (REQ-34 preserved structurally; TB-G2 verifies rather than assumes).
- **On any sub-decile interior the term is exactly zero at every `w` and every k.**
  This is the design property the track exists to test: Track 3's device charged for
  *every* interior, so ~80 % of its price was a hop-count penalty (DD-D5) and
  shortening was rewarded as a side effect. Here, adding an obscure artist is free —
  **length-neutral exactly where DD-D5's confound lives.**
- What the device does **not** remove: shortening still saves toll by *dropping*
  famous interiors without replacement. The device makes descent free, not shortening
  expensive. Whether the router then descends or still shortens is precisely the open
  mechanism question, and TB-C6 is the criterion that reads it.
- Additive and non-negative, so Dijkstra remains valid. Linear in k, no saturation
  knob (one device, one magnitude knob). `pop_pctl` is `MirrorContext.pctl` (average
  rank, deterministic) — a percentile of `pop_raw`, never a fame claim (§2.11).
- Named per the currency rule: `w_known_thresh_pctl`, knee constant
  `KNOWN_THRESH_PCTL_KNEE = 0.90` beside it.

## §2 — Factor table

One axis. Every variant's isolating baseline differs by exactly one column.

| arm | `w_known_thresh_pctl` | baseline | reading | realised toll at k=10 per production-typical interior (in `w_hop`) |
|---|---|---|---|---|
| **P** | 0 (off) | — | user-facing baseline | 0 |
| **TB-A1** | 0.10 | P | does a small thresholded toll move anything | 5× |
| **TB-A2** | 0.30 | TB-A1 | dose | 15× |
| **TB-A3** | 1.00 | TB-A2 | dose; at k=20 the toll on one typical famous interior (≈2.0) is commensurate with the whole sim term (≤3.0) | 50× |

**Dose derivation, so the ladder is comparable to Track 3's in the currency that
matters.** The toll binds only above the knee, so Track 3's `w` values do not
transfer (`pctl − 0.90 ≤ 0.10` against `pctl ≤ 1.0` — execution log §7). The
comparable quantity is the **realised toll per production-typical famous interior**:
production's d ≥ 10 interiors sit at median pctl ≈ 0.998 (PLA-R2), so per interior
the toll is `w · k · 0.098 ≈ w·k/10`, and at k = 10 the realised toll per such
interior is ≈ `w`. Setting `w ∈ {0.10, 0.30, 1.00}` therefore reproduces Track 3's
realised ladder of 5× / 15× / 50× `w_hop` per famous interior at k = 10 — the span
across which Track 3's device produced its (confounded) movement. **Magnitude
escalation beyond TB-A3 is barred in advance**, by the same argument as DD-R2's: at
k = 20 its per-interior toll already rivals the entire similarity term, so "not
strong enough" is not an available reading of a null.

## §3 — The pair set: inherited, not redrawn

**`builder/analysis/2026-07-28-track3-depth-descent/pairs_v2.json`, frozen and
committed** — the DD-P1 remedy set: 12 headroom-passing pairs (6 famous→mid, 6
mid→mid), split 8 analysis / 4 held-out (4/2 per group), drawn with DD-P1 headroom as
a draw-time precondition, seed 20260728. Inheriting it keeps three things Track 3
already paid for: **100 % certified headroom** (108/108 C1-window cells — so a null
here is a mechanism statement, not a pair-set artefact), the frozen fame table
(`t3_fame.json`, extended not rebuilt), and direct comparability of every TB
criterion against Track 3's committed figures on identical cells.

- **The held-out 4 pairs gate nothing** and are scored in a supplementary table only
  (`NEXT.md` closed list: never promoted to a gate).
- **The 4 all-famous anchors are walked, not scored** (TB-G2 runs on them; the
  descriptive anchor table is reported). **Pre-committed expectation:** DD-F1 and
  Track 3's anchor table (payload 0.00 in every arm at every strength) predict this
  device also delivers nothing there — it inherits DD-F1 unchanged (execution log
  §7). A nonzero anchor payload would be a surprise worth its own sentence in the
  log; it feeds no criterion either way.
- Degree-1 endpoints and no-detour pairs remain excluded (MKS-6, inherited from the
  draw).

## §4 — Instrument gates (failure voids the run; not findings)

- **TB-G1** — mirror byte-identity vs `pathfinding.find_path` with
  `w_known_thresh_pctl = 0.0`, re-run on this harness before any arm (the mirror
  gains a term, so the Track 2 gate is re-earned, as DD-G1 was; Track 3's pass does
  not carry).
- **TB-G2** — every arm's d0 path byte-identical to P's on every pair, anchors
  included. *(Plain: the first journey you see is untouched — verified, not
  assumed.)* **Non-vacuity check attached** (Track 3 closeout B3's lesson): d1 paths
  must differ from P on at least one pair per arm; a gate that nothing adjacent can
  trip is not a gate. If d1 differs nowhere at TB-A3, the device is not reaching the
  walk and the harness is broken — stop, fix, re-earn TB-G1.
- **TB-G3** — artifact sha256 `4cb84ef9…b061dc8` asserted in every script; all
  outputs record it.
- **TB-G4** — fame keyed by MBID; assertion that **no scored interior is
  blank-named** (the arms that dive aim exactly where blank names concentrate); and —
  new in this track, per the REQ-Q1 ruling and the standing deferral it discharges —
  **the scorer must read A11's `potentially_notable_unmatched` flag** and report the
  flagged count per arm. `score_t3.py` never read it (`NEXT.md` deferral: "before any
  further fame-scored arm on mid-band pairs" — this is that arm, so the deferral is
  due and this gate is its discharge).

## §5 — Prerequisites, in discharge order

**Order: TB-P1 → TB-P2 → TB-P3 → TB-P4 → arms → TB-P5 → read.** The order applies
Track 3's closeout lesson in advance: its analyst review ran third, and nearly
everything it found (DD-D4, DD-D5, DD-D6) was derivable from the document plus the
artifact with no measurements at all. Here the review runs **first**.

- **TB-P1 — `ml-graph-analyst` protocol review of this document, before anything is
  built.** Derivation only, per its remit; it is not asked whether the track is worth
  running. Dispatch is the owner's word (Track 3 precedent: a session does not
  dispatch it unsolicited). Specific questions it must answer beside the general
  check: (a) is the §2 dose derivation sound, including the pctl ≈ 0.998 typical-
  interior premise; (b) does the §6 ceiling construction (TB-P3) correctly
  characterise the `w → ∞` limit of this device; (c) is TB-C2's pre-committed pooling
  well-defined on this pair set given the known A13-drop asymmetry (DD-P3H-2).
- **TB-P2 — fame extension.** Fetch fame for interiors newly delivered by the ceiling
  probe and the arms, mbid-keyed, appended to the frozen snapshot; A11's two
  detectors unchanged; blank-name assertion at fetch time. The fetch precedes any
  criterion evaluation (DD-G4 discipline).
- **TB-P3 — the ceiling probe, a go/no-go gate with its own effect size.** The
  `w → ∞` limit of this device routes toll-free, and DD-P1 certifies a toll-free
  (all-sub-decile-interior) route exists for every scored cell — so the limit is
  computable directly and cheaply: **Dijkstra with production costs on the induced
  sub-decile subgraph** (top-decile nodes removed, endpoints exempt, that cell's
  exclusion set applied), per C1-window cell. Computed directly rather than through
  the device, so a device bug can neither flatter nor spoil it (the DD-D6 principle).
  Two measurements:
  - **(a) GATE.** Mean fame gap vs P over C1-window analysis cells. **If it fails to
    clear −1.0 log10, the arms are not run** (TB-R3): no dose can beat the `w → ∞`
    limit, so TB-C1 would be unreachable and the ladder would be answering a question
    whose answer is already fixed. *(Plain: first check that even a perfect version
    of this rule could make the journeys one full step less famous — if it can't, we
    don't spend the run.)*
  - **(b) FORECAST, gates nothing.** The ceiling's mean interior count vs P. Track
    3's (unthresholded) ceiling shortened 13 → 5; if **this** ceiling preserves
    length, the mechanism has structural room and the ladder tests whether finite
    doses find it; if it also shortens, TB-R2 is the likely outcome and the run
    proceeds knowing that. Recorded before arms so the forecast cannot be reshaped
    to fit them.
- **TB-P4 — harness.** `mirror.py` gains the thresholded term behind a config field
  defaulting to 0.0, on the edge-relaxation target (DD-D7), destination exempt;
  runner and scorer are **new modules importing committed code**, never edits to
  committed Track 2/3 files (so every prior figure still reproduces). Snyk scan on
  changed code before first run. Guard-G activation counter per arm.
- **TB-P5 — `ml-graph-analyst` harness review after the arms land, BEFORE the
  verdict is read.** Non-optional and explicitly ordered: Track 3's DD-R1 was first
  read with this gate open, caught by the owner's consultant review. The verdict in
  §7 is provisional until the execution log records TB-P5 discharged, and any
  earlier statement of it must say so in its own sentence.

## §6 — Criteria, each with its plain sentence fixed now

Fame is the committed A11 instrument (F = log10(1+pageviews), unmatched → floor),
mbid-keyed, frozen. Cell = pair × depth. C1 window = d ∈ {10, 15, 20}, analysis
pairs.

- **TB-C1 (primary).** Paired ΔF vs P per cell, **cell statistic = median interior F
  difference** (Track 2's calibrated form — chosen over Track 3's cell mean because
  the median is the less floor-exposed of the two, DD-D8), mean over the 24 C1-window
  cells ≤ **−1.0** log10, with ≥ **75 %** of cells negative. *(Plain: after ten or
  more presses of "I know them", the typical artist in the middle is about one full
  step less known than today's app gives you, and this holds across most journeys
  rather than being bought by a few.)*
  **Reported twice, always: all interiors, and matched-only** (REQ-Q1(a), the DD-D8
  shape). The primary is all-interiors — the encoding is the owner's adopted decision
  and an unmatched artist genuinely is reach. Two robustness conditions pre-committed:
  - **(i)** the A11-guard counterfactual must hold — reclassifying every
    `potentially_notable_unmatched` interior as a production-typical famous artist
    (F = P's C1-window median), the arm still passes. An arm that fails this
    counterfactual is **not a pass**.
  - **(ii)** if matched-only misses −1.0 while the primary passes, every statement of
    the pass carries this fixed wording: *"the pass is carried substantially by
    artists with no English Wikipedia article."*
- **TB-C2 (depth gradient).** Interior fame drop d5 → d20 ≥ **0.5** log10. *(Plain:
  the journey measurably keeps getting more obscure as you keep pressing.)*
  **Pooling pre-committed** (DD-P3H-2's lesson — Track 3's production figure
  sign-flipped across poolings): per pair present at both depths,
  Δ = median F(d5 interiors) − median F(d20 interiors); statistic = **median of Δ
  over pairs**; any A13 drop removes that pair from **both** depths. The pooled
  variant Track 3 scored is reported beside it, labelled secondary.
- **TB-C3 (gate, not criterion).** TB-G2 holds. *(Plain: the first journey is
  untouched.)*
- **TB-C4 (coherence tripwire — reported, gates nothing).** Median per-hop similarity
  over **interior hops** (both ends interiors — the definition Track 3's §5 stated
  and its code did not implement; fixed here explicitly, DD-P3H's disclosed variant
  resolved in favour of the stated design) at d ≥ 10, per arm vs P. Drop > **0.10**
  absolute flags the arm in every table. It cannot gate: offline coherence metrics
  were the worst predictors of the owner's verdict (Phase 1 log §3.8); REQ-9 is
  adjudicated by ear or not at all. *(Plain: if the steps stop sounding like
  neighbours, this number won't prove it — but a big drop is a warning worth a
  flag.)*
- **TB-C5 (deliverability, reported).** Distinct interior artists below pctl 0.90 at
  d ≥ 10 per arm (continuity with DD-C5), **plus** the fame distribution of delivered
  interiors (REQ-Q1: fame is the requirement currency; the pctl count is the
  artifact-currency diagnostic). *(Plain: how many genuinely less-known artists
  actually appeared on screen, and how obscure they really are.)*
- **TB-C6 (length criterion — promoted from Track 3's qualifier, and this is the §7
  question the Track 3 log left to this document).** Mean interior count per arm vs P
  over C1-window cells; an arm falling more than **1.0** below P is flagged in every
  table. **Promoted because the device's entire design claim is length-neutral
  descent: TB-R1 requires the passing arm to be unflagged.** A flagged pass is not
  discarded — it is TB-R2, and under REQ-14 shortening is not a product defect — but
  it may not be called descent. *(Plain: did the app find less-famous artists to fill
  the journey, or did it just make the journey shorter?)*

## §7 — Reads. Each names the run state it presupposes.

- **TB-R3 — the ceiling gate fails.** Presupposes: TB-P1–TB-P3 only; **arms not
  run.** If TB-P3(a) fails to clear −1.0: no dose of this device can reach TB-C1, and
  the number itself is the finding — the pctl-headroom → fame-delivery currency gap
  (DD-D6's trap) measured at this device's limit. The record states it with the
  ceiling figures and the track stops. Successor: none scheduled by this document;
  the cap-selection simulation (separately agreed 2026-07-29) proceeds regardless.
- **TB-R1 — mechanism confirmed.** Presupposes: all 4 walks scored, TB-P1–TB-P5 all
  discharged, uniform A13 drop applied. If ≥ 1 arm passes TB-C1 (with both robustness
  conditions) **and** TB-C2, with TB-C3 holding **and TB-C6 unflagged**: the
  thresholded toll produces genuine, length-preserving descent — the mechanism Track
  3 could not attribute. The device becomes the **router-side candidate for the
  stack** (graph work + device, per the 2026-07-29 sequencing), presented with an
  exposure map (one row per criterion × the knob), the TB-C4/TB-C5 tables, realised
  tolls, and both TB-C1 reports. **No blind listen, no adoption, no shipped-code
  change is scheduled — all the owner's.**
- **TB-R2 — shortening still dominates.** Presupposes: same full run state as TB-R1.
  If arms pass TB-C1 but **every** passing arm is TB-C6-flagged: even with obscure
  interiors toll-free, the router prefers dropping famous interiors to replacing
  them. Fixed reading, pre-committed: **the toll family cannot produce
  length-preserving descent on this graph** — this device was its best case, so no
  further toll-shaped term may claim descent without an explicit length-preserving
  constraint, and any such constraint is a new device needing its own
  pre-registration. The candidate pool for the owner's product decision is then
  DD-A2 and the best TB arm, judged on REQ terms (where shortening is priced by him,
  not by a criterion) — that judgement is his and is not scheduled here.
- **TB-R0 — null with headroom.** Presupposes: same full run state; headroom is
  already certified at 100 %. If no arm moves TB-C1 past **−0.3** (a third of the
  primary effect — clearly visible but insufficient, DD-R2's calibration): the
  router declines obscurity that is **free while famous alternatives are priced at up
  to 50× `w_hop` each**. Combined with Track 3 (which moved fame but confounded), the
  pre-committed reading: depth-graduated *routing* devices are exhausted as the
  primary lever on this graph, and the goal is graph-side — the cap-selection
  simulation inherits this figure as a design input. **Magnitude escalation is
  barred** (§2).
- **Partial states:** any read taken before its presupposed state must say so in the
  execution log **in its own sentence**, naming what is still owed — including the
  TB-P5 ordering, which Track 3 got wrong.

## §8 — Closed questions this document may not reopen

Loosening the both-ways cap (`MKS-5b`); re-running Track 2, 2F, the ceiling toll, or
**Track 3's own arms** (its results are closed; DD-A4/DD-A5 stay struck); scoring
anything on famous-pair first-path fame (PLA-R1); promoting the held-out set to a
gate; varying the knee in this track (§0); growing `CLAUDE.md`; spending a blind
listen or a rebuild — both the owner's, the rebuild additionally behind the
nameless-artist drop rule implementation. The all-famous pair class is out of scope
by structure (DD-F1, ruled a defect 2026-07-29 with a graph-side remedy path — a
different track).
