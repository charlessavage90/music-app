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
artifact the share of artists with zero sub-decile edges rises 4.5 % → 10.3 % → 20.1 %
→ 45.1 % → **80.0 %** across pctl bands [0.90,0.95) … [0.999,1.0]. This is the
per-pair, all-depths extension of PLA-R1 and is consistent with §2.10's famous↔obscure
edge depletion under mutual k-NN.

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
