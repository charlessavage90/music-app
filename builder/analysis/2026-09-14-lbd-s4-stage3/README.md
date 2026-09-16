# `LBD-S4` stage 3 — `LBA-M2`–`M5` taken, the reachable reads read, and the go/no-go numbers

**Role: ACTIVE — FIGURES OWNER for `LBA-D8` stage 3.** Every quantity stage 3 measured lives here
and is **cited from elsewhere, never restated.** Stage 1's figures are owned by
[`../2026-09-14-lbd-s4-stage1/README.md`](../2026-09-14-lbd-s4-stage1/README.md) and stage 2's by
[`../2026-09-14-lbd-s4-stage2/README.md`](../2026-09-14-lbd-s4-stage2/README.md); neither is
repeated here. Reasoning is
[`../../../docs/superpowers/2026-09-15-lbd-s4-stage3-execution-log.md`](../../../docs/superpowers/2026-09-15-lbd-s4-stage3-execution-log.md).

**Governing:** [`../../../docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../../../docs/superpowers/specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), including §11's `LBA-AM1`, `LBA-AM2` and `LBA-AM3`.

> ## ⛔ What this stage did NOT do
>
> **No census pass was run** — `LBA-G3` fired at stage 1, which is a resource fact about a pass's
> wall clock and **not a finding about any arm**. **No build, no fame fetch, no listen designed**
> (`LBA-D3`, `LBA-D5`). **No shipped code was touched.** **No arm is selected, no threshold is
> preferred and no route is recommended** — `LBA-D2` reserves the threshold to the owner at the
> go/no-go stop, and §7 of the pre-registration gives him the numbers rather than a
> recommendation.
>
> **`LBA-A9` is a hole in the lattice, not a row in these tables.** `LBA-G2` stopped it at stage 2
> — *unbuilt for a resource reason*. §2.6's three barred conclusions attach to that cell and are
> restated in §0c below, because the second is the one most easily got backwards.

**Structure.** §1–§5 are **measured**: tables, no adjectives. §6 is the reads. §7 is **what this
session infers**, labelled as inference and written so that someone who does not know what
*retention* measures can disagree with it. §8 is the **weakest link**. §9 is **options and their
consequences**. That order is `CLAUDE.md`'s and is not a stylistic choice.

---

## 0. Inputs, pins, and the two things that bound everything below

### 0a. The pins, re-verified by this session

`LBA-D9`. Both instruments re-run rather than inherited from the previous session's task 1 —
a session that reads a conclusion from an artifact it has not itself checked is relying on
another session's memory of a hash.

| instrument | what | result |
|---|---|---|
| `stage1_verify.py` (stage 1's, unedited, `--skip-large`) | the §10 input pins | **13 match**; `T_A4.parquet` **absent from every searched path** (`LBA-D1`) |
| `s3_verify_artifacts.py` | eight bare artifacts, six built artifacts, `LBA-A9`'s stop record | **14 match**; the stop record carries **no artifact** and reads *unbuilt for a resource reason* |

`T.parquet` is deliberately skipped: stage 3 derives nothing and never opens it. Outputs:
`_pins/stage3_verify_inputs.json`, `_pins/stage3_verify_artifacts.json`.

**Every arm is decoded from its BARE artifact through the shipped `GraphStore`**, never through a
local parser. Bare rather than built: a census build carries four of the five additive metadata
keys and the two reused artifacts carry all five, so decoding the built files would read some arms
through metadata others lack. This is stage 2 §3a's choice applied to the structural half; **no
bar moves either way**, since metadata appears in no statistic here.

### 0b. The two facts that make this a stage of estimates

1. **`LBA-G3` fired at stage 1.** No offline census pass was started and none is owed. **Every
   playability figure in §3 is an estimate**, and the split by verdict source shows **zero**
   freshly evaluated artists on every arm.
2. **`LBA-G2` fired on `LBA-A9` at stage 2.** The corner is unbuilt, so it has no map-level
   figures anywhere in this document.

### 0c. `LBA-A9`'s barred conclusions, restated verbatim because they are easy to invert

1. **No map-level read.** `LBA-M1`, `LBA-M2` and `LBA-M3` are simply unread for that cell; its
   table-level population and pair counts stand (stage 1 §1).
2. **No inference that the rule is unservable.** ***"We could not build it here" and "it is too
   big to serve" are different claims, and the second needs `LBA-M1`.*** `build_from_archive`
   holds neighbour objects in a Python dict during its first pass — a property of the **builder**,
   not of `GraphStore`.
3. **No cross-population comparison at the two-listener bar at map level.**

### 0d. The arms, their §2.2 sentences and their filter column

Sentences are quoted **verbatim from §2.2**, fixed before any result existed. The filter column is
`LBA-D7`'s — **said, never inferred from a config dump**, because `on, inert` and `off, uncensused`
look identical in one and mean opposite things (§2.4).

| arm | plain sentence (§2.2) | rule | threshold | listeners | **filter** |
|---|---|---|---:|---:|---|
| **`LBA-A1`** *control* | *the artists the app serves today, connected by our own recomputation at the same strength bar ListenBrainz used* | `V` | 10 | 4 | `on, inert (20260805)` |
| **`LBA-A2`** | *the same artists, but a connection is kept when three different people's listening supports it instead of four* | `V` | 7 | 3 | `on, inert (20260805)` |
| **`LBA-A3`** | *the same artists, but two people are enough* | `V` | 3 | 2 | `on, inert (20260805)` |
| **`LBA-A4`** | *every artist the deeper crawl found, at ListenBrainz's own bar* | `P` | 10 | 4 | `on, inert (20260809)` |
| **`LBA-A5`** | *every artist the deeper crawl found, at the three-listener bar* | `P` | 7 | 3 | `on, inert (20260809)` |
| **`LBA-A6`** | *every artist the deeper crawl found, at the two-listener bar* | `P` | 3 | 2 | `on, inert (20260809)` |
| **`LBA-A7`** | *every artist anywhere in ListenBrainz's listening data who gets a connection at ListenBrainz's own bar — not just the ones our crawl happened to discover* | `U` | 10 | 4 | **`off, uncensused`** |
| **`LBA-A8`** | *the same, at the three-listener bar* | `U` | 7 | 3 | **`off, uncensused`** |
| **`LBA-A9`** | *the same, at the two-listener bar* — **the corner** | `U` | 3 | 2 | **`off, uncensused`** — **UNBUILT (`LBA-G2`)** |

⚠ **The shipped code names the `U` configuration itself.** `pipeline.py:303-318`'s refusal text
calls `drop_unlistenable=False` *"an experimental control and never a shipping configuration."*
**Every `U` arm is built that way**, because no census covers that population and the guard
refuses. `drop_no_release_tail` and `drop_featured_credit` have **no guard at all** and silently
under-filter there.

---

## 1. `LBA-M2` — what happens to the artists the app serves today

> **Plain sentence (§4):** of the artists the app can reach today, how many are simply not in this
> map at all — and of the ones that are, for how many have fewer than half the artists we show as
> similar to them survived?

**The gated statistic is RETENTION, `R = c / |A|`, fired below 0.5** — *fewer than half the
artists we show as similar to them are still there*. `LBA-AM1-A1` and `LBA-AM1-A6` replaced
Jaccard on 2026-09-14, before any arm ran; §1d reports the null model that retirement rests on.

⚠ **`LBA-X4` and `LBA-X5` travel with every figure in §1a–§1b.** Between ListenBrainz's deployed
lists and any arm here lie a corpus roughly three times the size, the absent `filter_True` stage,
today's msid→mbid mapping, the uncredited band-member class and our deterministic tie-break — and
artists took part in the served build's cap step that no arm here can include. **No sentence
credits or blames any one component.** Neither travels with §1c.

**Effect size: none.** §4 fixes `LBA-M2` as *reported descriptively, no threshold*, and bars a
session from attaching one or from calling a high figure a failure or a low one a pass.

### 1a. Against the served map — both halves, per arm

`V` = 58,838 artists (the served map's node set). Absent causes: *no pair* = in the population
with no pair in the arm's own table; *pruned* = in the table, removed with the largest component;
*no id row* = the emitter's no-identity-row skip, separated out because those artists **do** have
pairs and filing them under *no pair* would be false.

| arm | filter | **absent** | share of `V` | no pair | pruned | no id row | **common** | **changed (`R` < 0.5)** | share of common | share of `V` | at `R` = 0 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `LBA-A1` | `on, inert` | 1,696 | 0.0288 | 1,213 | 478 | 5 | 57,142 | 12,821 | **0.2244** | 0.2179 | 0.0443 |
| `LBA-A2` | `on, inert` | 1,372 | 0.0233 | 981 | 386 | 5 | 57,466 | 13,041 | **0.2269** | 0.2216 | 0.0479 |
| `LBA-A3` | `on, inert` | 906 | 0.0154 | 636 | 265 | 5 | 57,932 | 13,446 | **0.2321** | 0.2285 | 0.0535 |
| `LBA-A4` | `on, inert` | 1,680 | 0.0286 | 1,220 | 455 | 5 | 57,158 | 14,094 | **0.2466** | 0.2395 | 0.0475 |
| `LBA-A5` | `on, inert` | 1,381 | 0.0235 | 1,003 | 373 | 5 | 57,457 | 14,307 | **0.2490** | 0.2432 | 0.0507 |
| `LBA-A6` | `on, inert` | 929 | 0.0158 | 665 | 259 | 5 | 57,909 | 14,726 | **0.2543** | 0.2503 | 0.0565 |
| `LBA-A7` | **`off, uncensused`** | 1,444 | 0.0245 | 1,077 | 367 | 0 | 57,394 | 16,666 | **0.2904** | 0.2833 | 0.0586 |
| `LBA-A8` | **`off, uncensused`** | 1,147 | 0.0195 | 856 | 291 | 0 | 57,691 | 16,922 | **0.2933** | 0.2876 | 0.0625 |
| **`LBA-A9`** | **`off, uncensused`** | — | — | — | — | — | — | — | **unbuilt (`LBA-G2`) — unread** | — | — |

**The denominator both ways (`LBA-AM1-A6`'s `C-γ`), so the two halves compose additively.**
Without it an arm that loses more served artists gets a *better*-looking changed share, because
the artists whose neighbourhood moved most have been removed from the denominator. Absent +
changed, as a share of `V`: `LBA-A1` 0.2467 · `LBA-A2` 0.2450 · `LBA-A3` 0.2439 · `LBA-A4` 0.2681
· `LBA-A5` 0.2666 · `LBA-A6` 0.2661 · `LBA-A7` 0.3078 · `LBA-A8` 0.3071.

### 1b. The four raw quantities and the rank companion

Recorded **per artist** in `_raw/s3_m2_raw_<arm>.npz` (served list length, arm list length,
intersection, `b_out`, availability); summarised here.

| arm | `R` median | **`R_avail` median** | `b_out` share (mean) | **forced share** | `overlap@10` (mean) | served list median | arm list median |
|---|---:|---:|---:|---:|---:|---:|---:|
| `LBA-A1` | 0.674 | 0.686 | 0.000 | 0.267 | 0.710 | 18 | 25 |
| `LBA-A2` | 0.673 | 0.682 | 0.000 | 0.295 | 0.708 | 18 | 26 |
| `LBA-A3` | 0.667 | 0.679 | 0.000 | 0.330 | 0.703 | 18 | 27 |
| `LBA-A4` | 0.660 | 0.667 | 0.145 | 0.315 | 0.696 | 18 | 29 |
| `LBA-A5` | 0.660 | 0.667 | 0.155 | 0.346 | 0.694 | 18 | 31 |
| `LBA-A6` | 0.660 | 0.667 | 0.170 | 0.382 | 0.690 | 18 | 33 |
| `LBA-A7` | 0.621 | 0.632 | 0.351 | 0.398 | 0.670 | 18 | 40 |
| `LBA-A8` | 0.620 | 0.625 | 0.385 | 0.442 | 0.667 | 18 | 45 |

- **`R_avail`** — intersection ÷ the served neighbours that are in the arm's map at all. *Of the
  artists we show today that this map could have chosen, how many did it keep?* **The control that
  separates "it chose differently" from "it was never available to choose."** `R_avail − R` is at
  most 0.012 on every arm, so **almost none of the change is availability**.
- **`b_out` share** — the fraction of an arm's neighbour list that is an artist the app does not
  serve today. **0.000 on the `V` row by construction**, which is the table's own sanity check.
- **forced share** — the share of the common set whose two list lengths differ by more than 2×.
  **This is the null model for the retired Jaccard read** and it is why the statistic changed: at
  these length ratios, 26.7 % to 44.2 % of artists would have been flagged with **zero
  contribution from neighbour identity**.
- **`overlap@10`** — the share of the served map's ten strongest neighbours still present.
  Ungated, and **no threshold attaches to it**.

### 1c. Arm to arm, within a population row (`LBA-AM1-A7`)

**Both sides share a population and an emitter, so the population cause and the `LBA-X4` data
bundle are absent BY CONSTRUCTION.** This is the only `LBA-M2` comparison in the design that
isolates the strength threshold.

| baseline → arm | row | common | changed (`R` < 0.5) share | **`R` mean** | `overlap@10` mean | forced share | one column? |
|---|---|---:|---:|---:|---:|---:|---|
| `LBA-A1` → `LBA-A2` | `V` | 57,142 | 0.0000 | **0.99947** | 0.99958 | 0.012 | ✓ |
| `LBA-A1` → `LBA-A3` | `V` | 57,142 | 0.0000 | **0.99873** | 0.99893 | 0.054 | ✓ |
| `LBA-A2` → `LBA-A3` | `V` | 57,466 | 0.00002 | **0.99918** | 0.99929 | 0.024 | ✓ |
| `LBA-A4` → `LBA-A5` | `P` | 86,086 | 0.0000 | **0.99934** | 0.99947 | 0.024 | ✓ |
| `LBA-A4` → `LBA-A6` | `P` | 86,086 | 0.00001 | **0.99841** | 0.99870 | 0.104 | ✓ |
| `LBA-A5` → `LBA-A6` | `P` | 86,649 | 0.0000 | **0.99895** | 0.99912 | 0.044 | ✓ |
| `LBA-A7` → `LBA-A8` | `U` | 311,312 | 0.0001 | **0.99891** | 0.99906 | 0.171 | ✗ — **`LBA-X6`** |

⚠ **`LBA-X6` on the `U` row:** there the population is a **dependent variable** that moves with
the threshold, so that row's arm-to-arm comparison is not one-column in the sense the other two
rows are.

### 1d. By fame band — five equal-count bands on the served artifact's own `fame_lb`

Band 0 is least-listened, band 4 most; the `LBD-M1` precedent, `(fame, mbid)`-sorted so ties are
deterministic; `unknown` = null `fame_lb`. Band sizes: 11,749 / 11,749 / 11,749 / 11,749 / 11,750,
plus 92 unknown. ⚠ **`LBA-X7`: this ruler exists only for artists the served map contains, so no
figure here says anything about the artists an arm adds.**

**Changed (`R` < 0.5) as a share of the band's common set:**

| arm | band 0 | band 1 | band 2 | band 3 | band 4 |
|---|---:|---:|---:|---:|---:|
| `LBA-A1` | 0.2269 | 0.2406 | 0.2204 | 0.2124 | 0.2220 |
| `LBA-A2` | 0.2381 | 0.2419 | 0.2212 | 0.2126 | 0.2219 |
| `LBA-A3` | 0.2601 | 0.2446 | 0.2221 | 0.2131 | 0.2222 |
| `LBA-A4` | 0.2504 | 0.2633 | 0.2455 | 0.2383 | 0.2361 |
| `LBA-A5` | 0.2616 | 0.2633 | 0.2462 | 0.2386 | 0.2365 |
| `LBA-A6` | 0.2829 | 0.2659 | 0.2472 | 0.2393 | 0.2377 |
| `LBA-A7` | 0.3138 | 0.3154 | 0.2941 | 0.2725 | 0.2584 |
| `LBA-A8` | 0.3255 | 0.3169 | 0.2948 | 0.2733 | 0.2586 |

**Absent, counts per band:**

| arm | band 0 | band 1 | band 2 | band 3 | band 4 | unknown |
|---|---:|---:|---:|---:|---:|---:|
| `LBA-A1` | 1,282 | 196 | 68 | 43 | 16 | 91 |
| `LBA-A2` | 1,055 | 133 | 45 | 33 | 15 | 91 |
| `LBA-A3` | 692 | 68 | 24 | 21 | 10 | 91 |
| `LBA-A4` | 1,269 | 186 | 73 | 44 | 17 | 91 |
| `LBA-A5` | 1,048 | 138 | 53 | 34 | 17 | 91 |
| `LBA-A6` | 693 | 77 | 35 | 23 | 10 | 91 |
| `LBA-A7` | 1,106 | 151 | 54 | 30 | 12 | 91 |
| `LBA-A8` | 887 | 101 | 39 | 19 | 10 | 91 |

**91 of the 92 `unknown`-band artists are absent from every arm.** No listens means no listener
count *and* no co-listen pairs — the two absences are the same absence. 0.16 % of `V`; nothing
rests on it.

---

## 2. `LBA-M3` — the added artists' supply

> **Plain sentence (§4):** of the artists the deeper crawl added — the ones that arrived with
> almost no connections — what share are still dead ends in this map?

**Statistic: share at or below 2 connections over the pinned added set (29,892), with an artist
absent from the map counted as 0.** Share-absent is reported separately, because absent and
present-with-degree-1 are different outcomes. **Median degree is reported and NOT gated on** —
`LBD-G2`'s own rule. Unit: **connections**, each counted once; not CSR entries, not archive
neighbour rows.

### 2a. Per arm, with both of `LBD-G2`'s controls

| arm | rule | thr | filter | **added: share ≤ 2 or absent** | share absent | median deg | **pre-existing (control 1)** | **table level (control 2)** | residual | complement |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| `LBA-A1` | `V` | 10 | `on, inert` | **1.0000** | 1.0000 | 0 | 0.0540 | 0.0374 | 1.0000 | 1.0000 |
| `LBA-A2` | `V` | 7 | `on, inert` | **1.0000** | 1.0000 | 0 | 0.0427 | 0.0235 | 1.0000 | 1.0000 |
| `LBA-A3` | `V` | 3 | `on, inert` | **1.0000** | 1.0000 | 0 | 0.0280 | 0.0113 | 1.0000 | 1.0000 |
| `LBA-A4` | `P` | 10 | `on, inert` | **0.0964** | 0.0322 | 13 | 0.0496 | 0.0374 | 0.2673 | 0.0538 |
| `LBA-A5` | `P` | 7 | `on, inert` | **0.0626** | 0.0234 | 16 | 0.0391 | 0.0235 | 0.1639 | 0.0374 |
| `LBA-A6` | `P` | 3 | `on, inert` | **0.0328** | 0.0136 | 19 | 0.0258 | 0.0113 | 0.0657 | 0.0246 |
| `LBA-A7` | `U` | 10 | **`off, uncensused`** | **0.0677** | 0.0286 | 19 | 0.0389 | 0.0374 | 0.1781 | 0.0402 |
| `LBA-A8` | `U` | 7 | **`off, uncensused`** | **0.0395** | 0.0197 | 24 | 0.0290 | 0.0235 | 0.0942 | 0.0259 |
| **`LBA-A9`** | `U` | 3 | **`off, uncensused`** | **unbuilt (`LBA-G2`) — unread** | | | | 0.0113 | | |

**The `V` row's 1.0000 is COMPUTED, not asserted.** §4 argues from construction that no member of
the added set can be in a `V` arm; the script computed it anyway and got 1.0000 on all three. If
the arithmetic had disagreed, the construction argument would have been what was wrong.

**Control 2 is a property of the THRESHOLD ALONE** — all three arms at a threshold derive from one
pair table, so the three population rules share a table-level figure and **it cannot distinguish
them.** Taken by running the frozen `../2026-09-08-lbd-similarity/lbd_reads.py --mode c2a`
**unedited** on each derived table. Its threshold-10 run reproduces that README §6's four
committed shares **exactly** — this instrument's green check, against a record frozen on
2026-09-08.

### 2b. `LBD-G2`'s bar, and exactly where it may be read

**Bar: ≥ 1 percentage point, admissible only with both controls reported** (≥ 10 without). Carried
verbatim; not re-derived here.

| comparison | Δ pp on the added set | admissible as? |
|---|---:|---|
| `LBA-A5` vs `LBA-A4` | **−3.38** | **one-column threshold attribution** (`LBA-AM1-A9`) |
| `LBA-A6` vs `LBA-A4` | **−6.37** | **one-column threshold attribution** (`LBA-AM1-A9`) |
| `LBA-A8` vs `LBA-A7` | −2.82 | computed and reported, **never one-column** — **`LBA-X6`** |
| any `V`-row pair | **identically 0** | **`n/a` — UNFIREABLE by construction**, never a finding |

⚠ **Those two `P`-row cells are the ONLY one-column threshold reads the whole design admits.** A
reader who believes the lattice supports nine of them would over-weight the evidence by more than
four times (`LBA-AM1-A9`, stated as a number there for that reason).

**The within-arm control moves too, and by less.** Pre-existing: 0.0496 → 0.0391 → 0.0258 across
the `P` row, i.e. −1.05 and −2.38 points, against the added set's −3.38 and −6.37. **That ratio is
what the control exists to show.**

### 2c. `LBA-AM1-A10`'s fourth stratum — `nodes(arm) − V`, descriptive, no bar

*The artists this map has that the app does not serve today, including the ones no crawl of ours
ever found.* The three pinned strata are all subsets of the extended crawl's population, so
**none of them can see the artists a `U` rule adds beyond it** — which is the only thing
`LBA-A7`–`A9` exist to test. It cannot be pinned in advance (`LBA-X6`), so its membership is
recorded per arm by count and by sha256 over its sorted MBIDs.

| arm | n | **share ≤ 2 connections** | median deg | membership sha256 |
|---|---:|---:|---:|---|
| `LBA-A1`–`A3` | **0** | — *(empty: a `V` arm's population is `V`, so it adds nobody)* | — | `e3b0c442…` (empty) |
| `LBA-A4` | 28,928 | 0.0663 | 14 | `87b09836…` |
| `LBA-A5` | 29,192 | 0.0401 | 16 | `fa69d009…` |
| `LBA-A6` | 29,485 | 0.0194 | 19 | `5ae92914…` |
| `LBA-A7` | **253,941** | **0.2711** | 6 | `1532efca…` |
| `LBA-A8` | **332,713** | **0.2499** | 7 | `cfdc01f4…` |

Membership files live beside the artifacts at `C:\unsung-fast\lbd-artifacts\s3_stratum4\`; they
are gitignored and the checksum is their identity.

---

## 3. `LBA-M4` — playability. **ESTIMATED on every arm.**

> **Plain sentence (§4):** of the artists in this map, and of the ones it adds beyond what the app
> serves today, what share would the un-listenable rule throw out — and how confident is that
> number?

**Why everything here is an estimate.** `LBA-G3` fired at stage 1, so no census pass ran and none
is owed. **Every verdict is CARRIED**, against an earlier MusicBrainz snapshot than the pinned
`20260905-002519` one. §4 reserves the word *exact* for freshly evaluated artists; after `LBA-G3`
there is **no fresh share at all**, on any arm — computed and reported so the zero is visible
rather than inferred.

**The coverage store was READ AND NOT WRITTEN, and that is evidenced.** sha256
`385f7c04072ddf37…` before **and** after; the script refuses if they differ. It is ACTIVE data
that census scripts read *and write*, so "we did not touch it" needs evidence.

**The within-class drop rates, reported as a RANGE and never averaged** (§4's rule — they were
taken on different populations): **0.8465** (`…20260805` payload, 15,708 of 18,557) and **0.8567**
(`…20260809`, 27,262 of 31,823), read from the payloads rather than transcribed.

### 3a. Per arm, with `LBA-AM3-3`'s coverage column

⚠ **`LBA-AM3-3`: coverage is UNEVEN, and the split falls exactly on the arms this measurement
exists to size.** On `LBA-A1`–`A6` the class share is **carried-measured over a complete
population** and only the drop is extrapolated. On `LBA-A7`/`A8` **both** the class share and the
drop are extrapolated, over a population most of which no census has ever evaluated — the store's
own rule is *"absence of a field means UNKNOWN, never false."* **No sentence may compare a `U`-row
class share with a `V`- or `P`-row one as though both were measured on the same basis.**

| arm | rule | filter | **coverage** | class share of covered | **estimated drop share** | freshly evaluated |
|---|---|---|---:|---:|---:|---:|
| `LBA-A1` | `V` | `on, inert` | **1.0000** | 0.0438 | 0.0371 – 0.0375 | **0** |
| `LBA-A2` | `V` | `on, inert` | **1.0000** | 0.0441 | 0.0374 – 0.0378 | **0** |
| `LBA-A3` | `V` | `on, inert` | **1.0000** | 0.0450 | 0.0381 – 0.0385 | **0** |
| `LBA-A4` | `P` | `on, inert` | **1.0000** | 0.0460 | 0.0390 – 0.0394 | **0** |
| `LBA-A5` | `P` | `on, inert` | **1.0000** | 0.0463 | 0.0392 – 0.0397 | **0** |
| `LBA-A6` | `P` | `on, inert` | **1.0000** | 0.0472 | 0.0400 – 0.0405 | **0** |
| `LBA-A7` | `U` | **`off, uncensused`** | **0.3547** | 0.1918 | 0.1624 – 0.1643 | **0** |
| `LBA-A8` | `U` | **`off, uncensused`** | **0.2861** | 0.1946 | 0.1647 – 0.1667 | **0** |

**Three bounds, on every figure above** (`LBA-X2`, §4):

1. **It is an OVER-estimate of what the app cannot play** — `ULC-F4`: the keep-check uses the
   **name**-search route while the app resolves **identity first**, so the rule can call an artist
   unlistenable whom the app would play on its first attempt. Sized on the two committed payloads
   by the LUX-E1 drift-source README §6.2; **on `U` it is UNBOUNDED, because nobody has measured
   it there.**
2. **The carried verdicts are un-re-run.** Both payloads carry verdicts inherited from the earlier
   no-release and featured-credit rules, holding no clip record. **Unmeasured, not zero.**
3. **The within-class drop rate is extrapolated outside the populations it was measured on.** The
   range is honest about their spread; it is **not** a control for applying either to `U`.

### 3b. `LBA-G4` — and `LBA-AM3-2`'s disqualifier fires on every evaluable arm

**Gate:** class share over `nodes(arm) − V` exceeds class share over `nodes(arm) ∩ V` by **≥ 10
percentage points**, within the arm. **Disqualifier (`LBA-AM3-2`, fixed 2026-09-15 before any
provenance mix was looked at):** if the two subsets' shares of `cex-recensus-2026-08-09`-sourced
verdicts differ by **≥ 10 percentage points**, the gate is **reported unreadable** for that arm.

| arm | added share | kept share | Δ pp vs 10 pp bar | 2026-08-09 share, added | …kept | **skew pp** | **result** |
|---|---:|---:|---:|---:|---:|---:|---|
| `LBA-A1`–`A3` | — | — | — | — | — | — | **`n/a`** — the subject is empty on a `V` arm |
| `LBA-A4` | 0.0515 | 0.0432 | +0.83 | 0.709 | **0.000** | **70.9** | **UNREADABLE** |
| `LBA-A5` | 0.0517 | 0.0436 | +0.81 | 0.711 | **0.000** | **71.1** | **UNREADABLE** |
| `LBA-A6` | 0.0524 | 0.0446 | +0.78 | 0.713 | **0.000** | **71.3** | **UNREADABLE** |
| `LBA-A7` | 0.3515 | 0.0443 | **+30.72** | 0.517 | **0.000** | **51.7** | **UNREADABLE** |
| `LBA-A8` | 0.3548 | 0.0446 | **+31.02** | 0.517 | **0.000** | **51.7** | **UNREADABLE** |

**`n/a` on the `V` row, NOT zero** (`LBA-AM1-A5`): the gate's subject is the artists an arm adds
beyond `V`, and for a `V` arm that set is empty — a share of nothing. Printing `0` would read as
*perfectly playable*.

⚠ **The skew is STRUCTURAL, not an accident of these arms.** Every kept-from-`V` subset draws
**exactly 0.0 %** of its verdicts from the 2026-08-09 recensus, because the 2026-08-05 census
covered the 75,000-artist `ALG-B` population — which contains `V` entirely — and the recensus only
evaluated artists genuinely new to the store. **So under the two censuses that exist, an
added-beyond-`V` subset and a kept-from-`V` subset can NEVER have matching provenance**, and
`LBA-G4` as `LBA-AM1-A5` redefined it is **not readable at all in this stage**. Its root cause is
the one that put `LBA-R8` and `LBA-R9` out of reach: `LBA-G3` fired, so there is no fresh pass to
put both subsets on one footing.

⚠ **What "unreadable" does and does not mean.** The comparison is **disqualified, not wrong** —
and not right either. **Neither *"the artists a `U` rule adds are much less playable"* nor *"they
are fine"* is licensed by this stage.**

---

## 4. `LBA-M5` — what it costs to operate. Descriptive, no threshold.

> ⚠ **`LBA-AM1-O2`: this measurement adds NO arm-discriminating information beyond `LBA-M1`'s
> artist count, and no read may treat it as independent evidence about an arm.** Parts 1 and 3 are
> identical across all eight arms — one pass over one shared table, one corpus. Part 4 is a
> deliverable. Only part 2 varies, and it is a deterministic function of N. **It is a cost
> statement about a candidate, not a comparison between candidates.**

**Part 1 — the similarity pass. CITED, never re-run and never re-timed here.** Owners: the
similarity README §4 (the `LBD-A0` pass's stage timings, spill and combine, and the hardware
context — the dump on a spinning disk and DuckDB's thread-count trap); the `lbd-a4` README §4 (the
`LBD-A4` pass); the supply README §1–§2 (the archive replay wall clocks, a cost the pipeline
already pays). **At the served population a refresh adds this pass and nothing else.** ⚠ **Above
`V` that no longer holds** — §6's steps 6 and 7 are additional (`LBA-AM1-O3`).

**Part 2 — the fame fetch, estimated by §4's fixed method:** `⌈N / 1000⌉ × (0.2 s + one round
trip)`. `MAX_PER_REQUEST = 1000` (`fame.py:57`, the endpoint's own truncation limit);
`request_delay_seconds` = 1 / 5.0 = 0.2 s (the **builder's** `config.py:74,289-290`, not the
API's). ⚠ **The round trip is not exactly recoverable from the record**: the one measured fame run
took 78 s and its log does not name the population it covered, so the per-batch cost is
**bracketed** across the two that session handled — 0.66–0.88 s, giving a round trip of
0.46–0.68 s. Named rather than guessed, as `LBA-AM1` did for `framework_rss`.

| arm | batches | rate-limit floor | **first-build estimate** |
|---|---:|---:|---:|
| `LBA-A1` / `A2` / `A3` | 58 | 11.6 s | **38 – 51 s** |
| `LBA-A4` / `A5` | 87 | 17.4 s | **58 – 76 s** |
| `LBA-A6` | 88 | 17.6 s | **58 – 77 s** |
| `LBA-A7` | 312 | 62.4 s | **206 – 273 s** |
| `LBA-A8` | 391 | 78.2 s | **258 – 343 s** |

**The stage is resumable**, so a refresh pays only for artists with no record — the difference
between a first build and a recurring cost.

**Part 3 — disk at a stated cadence. Cited, not measured here.** The standing corpus, its annual
growth and the re-download cadence a deletions-matter policy implies are the own-similarity
design's §8; the pinned dump's own size and file count are Task 1's README §1. **The cadence is a
policy choice, not a measurement:** §5 below is written for a **monthly** full refresh, and a
different cadence changes only step 1's frequency.

⚠ **The operating cost that actually scales with the population is not in the table above.** It is
§5's step 6, the re-census, whose projection is stage 1 §3's and is what `LBA-G3` fired on.

---

## 5. Part 4 — the refresh procedure (§6's ten steps), the deliverable

*Plain: if we adopt this, here is the whole list of what somebody runs to make a new map, and what
gets written down so a later reader can tell exactly which map they have.*

Pinned per `LBD-D5`: **a dump id, a MusicBrainz snapshot, and a parameter string**, all three in a
`MANIFEST.json` at the archive root and carried into the artifact's sidecar by the shipped
`build_manifest` / `write_manifest`.

1. **Download the ListenBrainz Spark/parquet dump.** Record its id, `TIMESTAMP`, file count and
   row count. Verify against the published sha256 where the published tar is available; where it
   is not, record the internal-consistency checks instead **and say so**.
2. **Download the MusicBrainz `mbdump` snapshot.** Record its directory timestamp and both
   `SCHEMA_SEQUENCE` values; extract `recording`, `artist_credit_name` and `artist` into the three
   parquet frames, each sorted so a rebuild is byte-comparable, each sha256'd.
3. **Run the similarity pass** at the pinned parameter string and **ListenBrainz's own pairing**
   (`LBA-D1`), chunked by `user_id % k`. Record `T`'s sha256, row count, wall clock and spill.
4. **Derive the adopted arm** at its threshold and limit by `lbd_derive.py`, **unedited**. Record
   the table's sha256 and row count.
5. **Emit the archive** over the adopted population rule by `emit_archive.py`, **unedited**. The
   `MANIFEST.json` records the dump id, the `mbdump` timestamp, the parameter string, **the
   pairing form and why** (`LBD-D6`), the population rule, and the sha256 over its sorted member
   MBIDs.
6. **Re-census the drop lists over the new population — both halves.** Offline applies `ULC-D2`
   with write-back to the coverage store; the network half runs the keep-check to completion,
   refusing to freeze while any lookup was refused (`ULF-4`). **A population the payload does not
   cover makes the build refuse, loudly, which is the design.**
7. **Run the `fame` stage** over the new population. Resumable; costs only what is not recorded.
8. **Attach the clip and streaming ids** — `deezer_ids.py`, `dsp_links.py`, `artist_facts.py`.
9. **Build, acceptance-check, serialise, write the manifest.** Acceptance per §8's rule, **never
   widened from `PRODUCTION_ACCEPTANCE`'s intent**.
10. **Verify and deploy.** Reload through the shipped `GraphStore`; take `ARTISTPATH_GRAPH_SHA256`
    **from the sidecar, never transcribed by hand** (`DEP-24`), so a wrong artifact refuses to
    boot.

⚠ **Steps 6 and 7 are the two that do not exist today at this scale.** Step 6's network half is
hours and is the only step depending on a third party answering. **Neither is run by this stage.**

---

## 6. The reads — run state `complete` and `sized`, **NOT `censused`**

- **`complete`** — every cell either built or stopped by `LBA-G2` with its bar recorded (stage 2
  §7). The lattice was **not** reduced by judgement, which §7 says would have put `complete` out
  of reach and barred these reads.
- **`sized`** — `LBA-M1`'s boot and query-cost halves, on the eight sized arms (stage 2 §3b).
- **NOT `censused`** — `LBA-G3` fired at stage 1.

Each read is a **conjunction**, evaluated mechanically in `s3_reads.py` from the committed JSONs,
with the figure that decided each clause recorded. No verdict was reached by looking at one number.

| read | verdict | why |
|---|---|---|
| **`LBA-R4`** (`P` row) — *the three thresholds do not separate* | **DOES NOT READ** | **two of three clauses fail.** Both `P`-row `LBA-M3` deltas clear `LBD-G2`'s 1-point bar (§2b); the absent shares spread by **1.28 points**, past the read's own "within a point". Clause 3 holds — `LBA-G1` fired on nothing across all eight arms (stage 2 §4), so it cannot fire *differently* |
| **`LBA-R4`** (`U` row, **`LBA-X6`** beside it) | **DOES NOT READ** | one of three fails: the `LBA-M3` clause. The population moves with the threshold here, so the arithmetic is reported and the attribution is not |
| **`LBA-R4-V`** | **RESTATED, never a finding** | settled on the committed record **before stage 1**. Clause (i) is unfireable — 1.0 on all three `V` arms, computed here; clause (ii) was already resolved against the read, and this session's independent measurement agrees (spread **1.34 points**), which is an instrument check, **not a result**; clause (iii) is the only live one. **The `V` row's threshold evidence is the arm-to-arm `LBA-M2` comparison (§1c) and nothing else** |
| **`LBA-R5`** (`P` and `U` rows) — *within a population rule, the thresholds do separate* | **READS** | `LBA-R4`'s complement. The cells are given side by side in §2a and §1a with their §2.2 sentences, and **no preferred value is named** — `LBA-D2` |
| **`LBA-R6` / `LBA-R7`** (the `P`-versus-`U` contrast) | **NOT ADJUDICABLE BY THIS DESIGN** | they differ **only** in whether the population rules separate on `LBA-M2`'s materially-changed share — and **neither the read nor `LBA-M2` carries an effect size for that half.** §4 fixes `LBA-M2` as descriptive *by design* and bars attaching a bar to it. Choosing between them here would be **fixing a threshold with results in hand**. Both halves' figures are below; the branch is the owner's |
| **`LBA-R8`, `LBA-R9`** | **FORMALLY UNREACHABLE** (`LBA-AM3-1`) | both presuppose *censused*. `LBA-G3` fired, so no arm will ever reach it within `LBD-S4` as designed |

**`LBA-R6` / `LBA-R7`'s two halves, side by side.** ⚠ **`P` → `U` is NOT one column** — it changes
the population **and the drop filter's state**, from inert-because-applicable to
absent-because-**refused**. And `LBD-G2` applies **within** a population rule and never across one,
so the supply half here is descriptive and carries no bar either.

| at a fixed threshold | supply half — added-set share ≤ 2 | Δ pp | changed-share half | Δ pp |
|---|---|---:|---|---:|
| 10: `LBA-A4` → `LBA-A7` | 0.0964 → 0.0677 | **−2.87** | 0.2466 → 0.2904 | **+4.38** |
| 7: `LBA-A5` → `LBA-A8` | 0.0626 → 0.0395 | **−2.31** | 0.2490 → 0.2933 | **+4.43** |

**`LBA-R9` is the row that reads *the numbers say no*** — and that records **stopping the `LBD-`
track here as a complete outcome rather than an abandonment.** It is the owner's own exit read, and
the design as executed **cannot hand it to him licensed.** §0's claim that every threshold outcome
has a read survives; the claim that every *decision* outcome has one does not.

### 6a. The owner's requested sensitivity — **explicitly unlicensed**

Given on 2026-09-15 with the unreachability already stated to him, and recorded as his in
`LBA-AM3-1`. It lives in its own file, `s3_unlicensed_sensitivity.json`, **makes nothing
reachable, licenses no §7 row, and enters the record as no finding.**

**If the estimated `LBA-M4` were read as measured:** `LBA-G4` **would not fire** on the `P` row
(+0.78 to +0.83 points against a 10-point bar) and **would fire** on the `U` row (+30.72 and
+31.02). Of the artists a `U` arm adds beyond `V`, the estimated drop share would be **0.298–0.301**
(`LBA-A7`) and **0.300–0.304** (`LBA-A8`) — at coverage **0.209** and **0.162** on those subsets.

**Every one of those figures is disqualified by `LBA-AM3-2` at a skew of 51.7 points, is an
over-estimate by `ULC-F4`'s unbounded-on-`U` mechanism, rests on un-re-run carried verdicts, and
is extrapolated from about a sixth of the subset.** That is four independent reasons it is not
evidence, and they are why it is in its own file.

---

## 7. What this session infers — **labelled inference, and you should be able to disagree with it**

Every identifier below carries its plain sentence. Nothing here is a recommendation.

**1. The strength bar — how much listening evidence we demand before we believe two artists are
connected — barely changes *who* you see. It almost only ever *adds*.** Comparing two of our own
maps that differ **only** in that bar, the looser one keeps **99.8 % or more** of the tighter one's
neighbour lists (§1c). *Plain: lowering the bar does not swap anybody out; it puts extra artists
in.* This was not known — the nesting had been proved at the pair-table level, and whether our
degree ceiling of 50 would undo it in the built map was open. It did not, because the typical
artist sits well under that ceiling.

**2. Where the strength bar does matter is the artists who arrived almost unconnected.** Over the
artists the deeper crawl added, the share still at two or fewer connections falls from **9.6 % to
6.3 % to 3.3 %** as the bar loosens (§2a, `P` row). The artists the app already served improve
too, but about a third as much. *Plain: loosening the bar mostly helps the artists who had almost
nothing, which is the group this whole line of work exists to help.*

**3. A bigger population changes what the app shows you noticeably more than the strength bar
does.** Against today's map, the share of served artists who lose more than half their
similar-artist list runs **22.4 %–23.2 %** for maps over today's artists, **24.7 %–25.4 %** over
the deeper crawl's, and **29.0 %–29.3 %** over everyone in the listening data (§1a). *Plain:
whichever of these we shipped, roughly a quarter of the artists you can reach today would have a
substantially different set of neighbours — and going wider pushes that up by several points, not
by a little.*

**4. That change is not because the new map could not find the old neighbours.** `R_avail` — of
the artists we show today that this map **could** have chosen, how many did it keep — is at most
1.2 points above plain retention on every arm (§1b). *Plain: the new maps are mostly choosing
differently, not being forced to.*

**5. The least-listened artists absorb most of the disruption, at both ends.** Band 0 — the fifth
of served artists with the fewest recorded listeners — is both the most likely to vanish from a
map entirely (§1d, absent counts) and the most likely to have its neighbour list rearranged. *Plain:
the artists the app exists to surface are the ones these maps treat least stably.*

**6. Going beyond the deeper crawl's artists reaches a very large number of very thin artists.**
A map over everyone in the listening data adds **254,000–333,000** artists the app does not serve
today, and **about a quarter of them have two or fewer connections** (§2c). *Plain: the widest
option roughly sextuples the map, and a quarter of what it adds are near-dead-ends you would
rarely reach and rarely enjoy arriving at.*

**7. We cannot say how playable those added artists are, and that is a fact about this stage
rather than about them.** The measurement that would say (`LBA-M4` — *what share of these artists
would the un-listenable rule throw out*) is estimated everywhere, and its within-arm comparison is
**disqualified on every arm by a provenance difference of 52 to 71 points** (§3b). *Plain: the only
two censuses we have looked at different sets of artists at different times, so comparing "the
artists a map adds" with "the artists it keeps" compares two different census vintages as much as
two groups of artists.* **That is not a hint that they are bad, and not a hint that they are fine.**

**8. Cost is not what decides this.** The fame fetch is under six minutes on every arm and
resumable (§4); `LBA-G1` — *this map is too big or too slow for the machine the app runs on* —
fired on nothing across the eight sized arms (stage 2 §4). *Plain: the machine can hold any of
these maps, and building one is not the expensive part.* **The expensive part is the re-census**
(§5 step 6), which is what stopped us measuring playability at all.

---

## 8. Weakest link — what this rests on, and what would falsify it

**The load-bearing assumption is that a structural comparison predicts a listening experience. It
is not established, and `REQ-38` says the opposite.** Everything in §1–§3 is *offline metrics*.
`REQ-38` makes the blind listening test the **primary** evaluation method and says offline metrics
must not override listener judgment. **Nothing here has been heard.** Falsified by: a blind listen
at the go stage disagreeing with the direction any figure above points.

**Playability is estimated everywhere, and the two census-dependent reads are gone.** §3's whole
table is carried verdicts; `LBA-R8` and `LBA-R9` are formally unreachable. **The one I would
abandon most cheaply is any statement about the `U` row's added artists' playability** — coverage
there is 16–21 % of the subset, the provenance skew disqualifies the comparison, and `ULC-F4`'s
over-drop is unbounded on that population. Falsified by: one census pass over the union, which
`LBA-G3` priced at multiples of six hours.

**The `U` row's query cost is in the tail, and the gate reads the median.** Stage 2 §3b records
`U`-row p95 at roughly double every `V` and `P` arm's, and stage 2 §4 records how close the
largest sized arm sits to the 2× bar — **that ratio is owned there and is not restated here.**
The gate did not fire — **that is the specified reading, and the tail is
still the number worth looking at.** Worse: the conversion from our laptop to the live container
uses a multiplier measured on the **retired 75k artifact**. Falsified — or confirmed — by: one d0
measurement on the actual container, which is cheap and is already a deferral row.

**Every `U` arm is built in a configuration the shipped code names.** `pipeline.py:303-318` calls
`drop_unlistenable=False` *"an experimental control and never a shipping configuration"*, and the
other two drop stages have **no guard at all** and silently under-filter there. So a `U` row
comparison includes *"its quality filter was off"* as an uncontrolled term — §2.4's named hazard,
and the reason `LBA-M4` exists.

**I would defend:** the arm-to-arm nesting result (§1c), which is one-column by construction and
whose instrument reproduced three frozen figures; the `P`-row supply reads (§2b), which carry both
required controls; and the absent-cause split (§1a), which reproduces stage 1's committed counts
exactly. **I would abandon cheaply:** anything resting on §3's `U`-row figures, and any reading of
§1's served-map comparison that attributes a difference to one component of the data bundle —
`LBA-X4` bars that and this stage cannot separate it.

---

## 9. Options and their consequences — **no arm is preferred and no threshold is named**

`LBA-D2` reserves the threshold to the owner; `LBA-D8` bars this session from reducing anything;
§8 of the pre-registration states what "go" commits to. These are the shapes the numbers leave
open, with what each costs.

**A. Stop here.** The supply question is answered at the pair-table level, at the map level, and
at the ear twice. ⚠ **`LBA-R9` — the read that records this as a *complete outcome* rather than an
abandonment — is formally unreachable**, so stopping would be a decision taken **without** the
design's own licensed exit. That is a defect of the design, not a reason against the decision.

**B. Go at a `V`-row arm** — today's artists, our own recomputation. Commits to §8's four items: a
candidate build with fame and clip ids, acceptance criteria never widened from
`PRODUCTION_ACCEPTANCE`'s intent, manifest pinning, and **then the `REQ-38` blind listen designed
cold**. Consequence: about a quarter of served artists get a substantially different neighbour
list (§1a) for no gain on the added artists — the added-set statistic is 1.0 by construction on
that row. The threshold choice within the row is nearly free structurally (§1c).

**C. Go at a `P`-row arm** — the deeper crawl's artists. Same four commitments, plus a re-census
and a fame fetch over a larger population (§5 steps 6–7). Consequence: the added artists' dead-end
share falls materially and the threshold genuinely matters there (§2b — the only two one-column
reads the design admits); the served map changes a little more than a `V` arm (§1a). Playability
on that row is estimated but over a **fully covered** population.

**D. Go at a `U`-row arm** — everyone in the listening data. Same commitments, plus: a census pass
`LBA-G3` priced at multiples of six hours **before the filter could even be applied**; a map
roughly six times today's; a quarter of what it adds at two or fewer connections (§2c); the
largest sized arm close to the query-cost bar with its cost in the tail (stage 2 §4 owns the
ratio); and **playability that
this stage cannot assess at all** (§3b). ⚠ **`LBA-A9`, the corner — the only cell that could say
"there is no bigger map to have inside these rules" — is unbuilt**, so the `U` row is reported
with a hole in it.

**E. Buy one measurement first.** Two are cheap and both are already deferral rows: **d0 on the
actual container** (replaces a multiplier taken on a retired artifact), and **the census pass over
the union** (turns every figure in §3 from estimated to measured and makes `LBA-R8` and `LBA-R9`
reachable). The second is the one that removes four of §8's weakest links at once.

**Whose call each of these is.** Which map the app should have, what counts as too much change to
what it shows today, and whether an estimated playability figure is good enough to act on are all
his. Methodology, run counts and what to measure next are this session's — and this session has
measured everything the design admits without a census pass.

---

## 10. Files

| file | what |
|---|---|
| `s3_common.py` | arm table, pinned artifact loading through the shipped `GraphStore`, fame bands, archive table membership |
| `s3_verify_artifacts.py`, `_pins/` | task 1/4's pin verification and its outputs |
| `s3_m2.py`, `s3_m2_served.json`, `s3_m2_armtoarm.json`, `_raw/` | `LBA-M2`, both comparisons, and the four per-artist raw quantities |
| `s3_m3.py`, `s3_m3.json` | `LBA-M3`, four strata, both controls |
| `s3_m4.py`, `s3_m4.json` | `LBA-M4` estimated, `LBA-G4` with `LBA-AM3-2`'s disqualifier |
| `s3_m5.py`, `s3_m5.json` | `LBA-M5` |
| `s3_reads.py`, `s3_reads.json` | the §7 reads, clause by clause |
| `s3_unlicensed_sensitivity.py`, `.json` | **the owner's requested sensitivity — unlicensed, not a finding** |

Stratum-4 membership files are gitignored, at `C:\unsung-fast\lbd-artifacts\s3_stratum4\`; their
sha256s are in `s3_m3.json`.
