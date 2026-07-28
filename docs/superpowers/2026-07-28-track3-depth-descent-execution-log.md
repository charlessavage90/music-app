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
