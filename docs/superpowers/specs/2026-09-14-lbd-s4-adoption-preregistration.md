# `LBD-S4` adoption — pre-registration (`LBA-`)

**Role: ACTIVE, and GOVERNING for `LBD-S4`'s arms, measurements, gates and reads.**
Committed **before anything runs**: no arm is derived, no archive emitted, no graph built, no
census run and no listen designed. The git commit timestamp is the evidence that it preceded
every result, which is the part that cannot be reconstructed afterwards.

**Where it sits in the chain.**
[`2026-09-06-own-similarity-design.md`](2026-09-06-own-similarity-design.md) governs the
`LBD-` track — its §2 makes `LBD-S4` a stage, its §3 fixes `LBD-D1`–`D8`, its §8 lists what
adoption changes operationally, and **its §9 is the closed list, which this document does not
reopen**. [`2026-09-07-lbd-fidelity-and-supply-preregistration.md`](2026-09-07-lbd-fidelity-and-supply-preregistration.md)
governs the `LBD-` track's own criteria, arms, gates and reads, including every amendment in
its §10 and §12. **This document governs `LBD-S4` and nothing else. Where it disagrees with
either on anything outside `S4`, they govern and this document is wrong.** Status is
[`../NEXT.md`](../NEXT.md)'s, never restated here.

**It owns no figures.** Every quantity below is either a bar this document fixes, a value read
from source with its file and line, or arithmetic over ListenBrainz's own SQL. Measured figures
are **cited by section from the document that owns them and never restated** — principally
[`builder/analysis/2026-09-08-lbd-similarity/README.md`](../../../builder/analysis/2026-09-08-lbd-similarity/README.md)
(the reimplementation, `LBD-C1`, `LBD-C2a`, the threshold curve §6c),
[`builder/analysis/2026-09-10-lbd-supply/README.md`](../../../builder/analysis/2026-09-10-lbd-supply/README.md)
(the fixed-population builds),
[`builder/analysis/2026-09-10-lbd-served-population/README.md`](../../../builder/analysis/2026-09-10-lbd-served-population/README.md)
(the two maps over the served population),
[`builder/analysis/2026-09-13-lbd-a4/README.md`](../../../builder/analysis/2026-09-13-lbd-a4/README.md)
(the pairing delta and `R10`), and
[`../findings/2026-07-27-gate2-gate3-team-review.md`](../findings/2026-07-27-gate2-gate3-team-review.md)
(the hosting and API-size baseline).

**Two inputs this document consumes and does not re-derive.**
[`../findings/2026-09-13-lbd-adoption-inputs.md`](../findings/2026-09-13-lbd-adoption-inputs.md)
— the owner's three points for adoption that no `LBD-` criterion measures, each with its
supporting section and that section's nuance; it recommends nothing, and neither does this
document. And [`../PRODUCT-REQUIREMENTS.md`](../PRODUCT-REQUIREMENTS.md) §9 — `REQ-38` (blind
listening is the **primary** evaluation method and offline metrics must not override listener
judgment) and `REQ-41` (*"no difference"* in unfamiliar territory is **uninformative**, not
evidence of equivalence).

**Identifiers introduced here: the `LBA-` series** — `LBA-A1`–`LBA-A9` (arms), `LBA-D1`–`LBA-D9`
(decisions; `D1`–`D3` are the **owner's**, the rest are this document's), `LBA-M1`–`LBA-M5`
(measurements), `LBA-G1`–`LBA-G4` (gates), `LBA-R0`–`LBA-R9` plus `LBA-R4-V` (reads), `LBA-X1`–`LBA-X8` (named
exposures), and the amendment register's entries `LBA-AM1`, `LBA-AM2` and `LBA-AM3` (§11), with `LBA-AM1-A1`–`A12`, `LBA-AM1-O1`–`O4` and `LBA-AM3-1`–`-3` minted inside them. **Collision-checked across every ref on 2026-09-14** —
`git grep -lE '\bLBA-' $(git for-each-ref --format='%(refname)' refs/remotes refs/heads) -- '*.md'`,
and the same for each sub-pattern `LBA-A[0-9]`, `LBA-R[0-9]`, `LBA-M[0-9]`, `LBA-X[0-9]`,
`LBA-D[0-9]`, `LBA-G[0-9]`: **all free**, with nothing in the working tree either.

⚠ **The series is namespaced deliberately, and a bare token is never used.** §9 of the `LBD-`
pre-registration owns a bare `R1`–`R12`; `LBD-R1`–`LBD-R9` are that track's *risks*, a different
kind of object; Track 2 owns a bare `A0`–`A7` and `C1`–`C3`; the fame-proxy work owns a bare
`S1`–`S4` as **strata**, and `G3-S4` is a security finding. **`S4` alone is not a free token and
is used in this document only as the stage's name.** Forward-only: nothing committed is renamed.

---

## §0 — The question

> **Plain sentence, and it is the whole document: is a map built from our own recomputation of
> ListenBrainz's raw listening data worth shipping — at what population of artists, and at what
> strength bar — given what it costs to run?**

Three quantities, one decision. The stop is the owner's. **This document does not recommend a
route, and no read below concludes one.**

---

## §1 — The owner's three rulings, recorded verbatim and not reopened

Given on **2026-09-14**, before this document was written. They are quoted in substance as his
and are **not a session's inference from any result**.

**`LBA-D1` — the pairing rule, HIS.**

> The pairing rule for every `S4` arm is ListenBrainz's own — once per pair of plays within a
> session — because it is the only form with any listening evidence behind it. The cheaper form
> is barred for `S4` unless it gets its own blind listen.

*Plain: when we count how often two artists are played together, we count every pair of plays,
the way ListenBrainz does — not once per listening session, which is cheaper to compute.*

This discharges `LBD-D6`'s standing requirement in the strongest available form: **every arm
here uses ListenBrainz's own pairing, and the reason is recorded above.** Both listens were run
on maps derived that way, so a listen-based judgment transfers to these arms and to no others.
`LBD-X6` **stands** — `LBD-A4` ran, `R10` fired on the edge-count half, and reading the
discharged condition as a lifted bar inverts the result. Every arm derives from `T`
(sha256 `03d47b05…`), **never from `T_A4`** (sha256 `e919bc89…`), and each arm's manifest
records which.

**`LBA-D2` — the strength threshold is an OPEN FACTOR, HIS.**

> The strength threshold is not a ruling: the arms carry it, and I rule at the go/no-go stop
> with the numbers in front of me.

*Plain: how much listening evidence a connection needs before we believe it is a knob the
experiment varies, not a choice made in advance.* So the threshold is a **column of the factor
table** (§2.1), and **no read below selects a threshold.** §7's table is written so that every
threshold outcome, including "they are indistinguishable", has a read.

**`LBA-D3` — no blind listen before the go/no-go stop, HIS.**

> No blind listen is designed or run before the go/no-go stop. The `REQ-38` listen that adoption
> requires is designed cold, as a later amendment, only if I say go.

*Plain: nobody spends my ear until I have decided the numbers are worth spending it on.* So
**this document designs no listen, fixes no listen protocol, and draws no pairs.** §8 states what
the listen would be *for*; its design is a later amendment written when no result of it exists.
`GBL-` §5's run-once rule binds both existing `LBL-` verdicts regardless, and neither may be
re-listened on any protocol.

---

## §2 — Factor table

### §2.1 The arms — one row per variant, one column per knob that varies

**Two knobs vary and nothing else: the strength threshold, and the population rule.** A full
3 × 3 lattice, so that every cell has a baseline differing from it in exactly one column.

| arm | `threshold` | distinct listeners a pair needs | population rule | **drop filter** | isolating baseline, and how many columns it is actually away |
|---|---:|---:|---|---|---|
| **`LBA-A1`** *control* | **10** | 4 | **`V`** — today's served artists | `on, inert (20260805)` | — (it *is* the control) |
| **`LBA-A2`** | **7** | 3 | `V` | `on, inert (20260805)` | `LBA-A1` — **threshold only** ✓ |
| **`LBA-A3`** | **3** | 2 | `V` | `on, inert (20260805)` | `LBA-A1` — **threshold only** ✓; **and** `LBA-A2` — **threshold only** ✓ |
| **`LBA-A4`** | **10** | 4 | **`P`** — the extended crawl's artists | `on, inert (20260809)` | `LBA-A1` — population **and the drop-list payload** (two columns; see the note) |
| **`LBA-A5`** | **7** | 3 | `P` | `on, inert (20260809)` | `LBA-A4` — **threshold only** ✓; **and** `LBA-A2` — population **and payload** |
| **`LBA-A6`** | **3** | 2 | `P` | `on, inert (20260809)` | `LBA-A4` — **threshold only** ✓; **and** `LBA-A3` — population **and payload** |
| **`LBA-A7`** | **10** | 4 | **`U`** — every artist the table names | **`off, uncensused`** | `LBA-A4` — population **and filter state** (**two columns**, and the second is §2.4's) |
| **`LBA-A8`** | **7** | 3 | `U` | **`off, uncensused`** | `LBA-A7` — threshold, **with the population dependent on it** (`LBA-X6`); **and** `LBA-A5` — population **and filter state** |
| **`LBA-A9`** | **3** | 2 | `U` | **`off, uncensused`** | `LBA-A7` — threshold, **with the population dependent on it** (`LBA-X6`); **and** `LBA-A6` — population **and filter state** |

> ### ⚠ Four of these nine baselines are NOT one column away, and the table says so in the column rather than in a disclaimer
>
> **The drop-filter column was added on 2026-09-14 after the `ml-graph-analyst` critique** (§11,
> `LBA-AM1`, finding `LBA-AM1-A8`). §2.4 already derived the hazard; what it did not do was put it where
> a reader looks, which is the baseline column. `CLAUDE.md`'s own rule is that **a disclaimer
> nothing later reads is not a control**, and the baseline column is what is later read.
>
> - **`V` → `P` also changes the payload.** `unlistenable_drop_algb_20260805.json` and
>   `…20260809.json` are each *measured inert on their own population*, so neither removes anybody
>   from the arms that use it — but they are **not interchangeable**: the `20260809` payload would
>   drop 31 members of `V` (`LBD-AM5-3` owns that count). The column is real even where its effect
>   is zero, and a one-column claim across it is wrong even though no artist moves.
> - **`P` → `U` changes the filter's STATE, not its payload.** Inert-because-applicable becomes
>   absent-because-refused. **This is the term §2.4 names as the dangerous one**, and it is present
>   in exactly the three arms that grow the map most.
>
> **Consequence, a bar:** no read may describe an `LBA-A7`/`A8`/`A9` result as a *population*
> effect without naming the filter state beside it, and no read may describe a `V`→`P` result as a
> *population* effect without naming the payload beside it. `LBA-M4` is what sizes the first.

**Every other token is `LBD-A0`'s** — `days` 7500, `session` 300, `skip` 30, `contribution` 3,
`limit` 100, ListenBrainz's own pairing (`LBA-D1`) — i.e. `CANDIDATE_ALGORITHM` less its
`filter_True` token, which current ListenBrainz source does not emit (`LBS-2`, `LBD-X3`).

**The distinct-listener column is arithmetic, not an estimate.** Each user contributes at most
`contribution` to a pair's score and `HAVING score > threshold` is strict, so a pair needs at
least ⌈(threshold + 1) / contribution⌉ distinct users before it can survive — the
pre-registration's §7 derives it from ListenBrainz's own SQL. At `contribution` 3 that is 4 at
threshold 10, **3 at thresholds 6–8**, 2 at thresholds 3–5, and 1 at 0–2.

#### Why threshold 7, and not some other middle value

**It is the three-listener bar, and no other value on the committed curve is.** The two bars
already on the record are ListenBrainz's own (10, four listeners) and the two-listener bar
`LBD-A5` used (3). Between them, the *only* integer thresholds requiring exactly three distinct
listeners are 6, 7 and 8 — and **7 is the one the committed descriptive curve already carries a
cell for** (`builder/analysis/2026-09-08-lbd-similarity/README.md` §6c, at both `limit` 100 and
no limit, on all four pinned sets; **its figures are owned there and are not restated here**).
So 7 is chosen because it is the middle value in the quantity that actually governs — how many
different people must have played both artists — rather than the middle value in an arbitrary
integer score, and because choosing it spends no new derivation to see where it sits.

⚠ **A middle value in threshold space is NOT a middle value in listener space, and picking one
without checking the arithmetic would have produced a dead arm.** Thresholds 3 and 5 both require
two distinct listeners; an arm at 5 would have differed from `LBA-A3` in score mass alone, not in
the quantity the plain sentence names. Recorded because it is the mistake this section exists to
avoid, and because §6c's shape at thresholds 4 and 5 would have made 5 look like the obvious pick.

#### The three population rules

| rule | definition | how its membership is obtained |
|---|---|---|
| **`V`** — today's served artists only | the node set of `graph-msw-tu50.bin` (`ApiConfig.graph_path`'s default), sha256 `43dd82bb…` verified against its sidecar, read through the shipped `GraphStore` | the pinned file `C:\unsung-fast\lbd-archives\population_msw_mbids.txt`, sha256 `b5e0cb94…`, written by `LBD-AM5-1` and **re-verified, never re-derived** |
| **`P`** — the extended crawl's artists | the node set of `graph-cxa-adopted.bin`, sha256 `bc0431c4…` verified against its sidecar | the pinned file `C:\unsung-fast\lbd-archives\population_cxa_mbids.txt`, sha256 `1bbff8fc…`, written by `LBD-AM4-1`, **re-verified, never re-derived** |
| **`U`** — every artist the table names | every artist appearing as `mbid0` **or** `mbid1` in the arm's own derived table, after the standard drop lists, after the largest-component prune | derived per arm from the arm's table; **it is the only population rule that moves with the threshold**, which is `LBA-X6` |

**`U`'s minimum-degree floor is 1, stated explicitly and held constant across all three `U`
arms.** *Plain: an artist is in the map if the listening data gives them at least one connection
that survives our own cap rule and the prune, and we impose no extra bar on top.* A floor above 1
is a **fourth knob** and is deliberately not turned: it would make every `U` cell
incomparable with its `V` and `P` baselines, which impose no such floor either. **A floor change
is a later amendment**, and §7's `LBA-R8` is the read that would motivate one.

⚠ **`U` is the only rule whose membership depends on the threshold**, because a looser bar admits
pairs naming artists a tighter bar never reaches. That is the rule's substance, not a defect —
but it means an `LBA-A7` → `LBA-A9` comparison moves *two* things at once in the sense that
matters to a reader, and `LBA-X6` states the consequence and the bar.

### §2.2 Each arm's plain sentence, fixed here, before any result exists

Quoted verbatim wherever an arm is named in any later report (`CLAUDE.md`'s rule: the sentence is
fixed beside the value so a report whose wording drifts from it is as visible as a moved number).

- **`LBA-A1`** — *the artists the app serves today, connected by our own recomputation at the
  same strength bar ListenBrainz used.* The control. **This is `LBD-A0V`**, already derived,
  emitted, built and serialised.
- **`LBA-A2`** — *the same artists, but a connection is kept when three different people's
  listening supports it instead of four.*
- **`LBA-A3`** — *the same artists, but two people are enough.* **This is `LBD-A5V`**, already
  built and serialised.
- **`LBA-A4`** — *every artist the deeper crawl found, at ListenBrainz's own bar.*
- **`LBA-A5`** — *every artist the deeper crawl found, at the three-listener bar.*
- **`LBA-A6`** — *every artist the deeper crawl found, at the two-listener bar.*
- **`LBA-A7`** — *every artist anywhere in ListenBrainz's listening data who gets a connection at
  ListenBrainz's own bar — not just the ones our crawl happened to discover.*
- **`LBA-A8`** — *the same, at the three-listener bar.*
- **`LBA-A9`** — *the same, at the two-listener bar.* **This is the corner**, and it is the only
  cell that can say *"there is no bigger map to have inside these rules."*

**`LBA-A9` is why the lattice is full.** With only the `V` and `P` rows, a null on population is
explicable by the crawl having already found everyone worth finding; with only the tight
thresholds, a null is explicable by the bar. **Only the corner can distinguish "the map is as big
as it usefully gets" from "our rules were keeping it small."** This is the shape `CLAUDE.md`
records from Track 2's stage 2, where the four arms a session recommended skipping produced the
only signal in fifteen — and `LBA-D8` below is written so that no cell is dropped for being
uninteresting.

### §2.3 Held constant, and why each is genuinely constant under the intervention

| held constant | why the intervention cannot change it |
|---|---|
| **pairing — ListenBrainz's own** | `LBA-D1`, the owner's ruling. Every arm derives from the same materialised table `T`; no arm re-runs the pass |
| `contribution` = 3 | applied per `(user, pair)` **before** the cross-user aggregation, so it is baked into `T` and no derivation can reach it (`LBD-` pre-registration §1's stage table) |
| `limit` = 100 | applied by the same `rank()` window in `lbd_derive.py`, unedited, for every arm |
| `days`, `session`, `skip` | identical across all nine arms by construction; each fixed at `ALG-B`'s value and baked into `T` |
| the listen corpus and the MusicBrainz side-tables | one pinned dump (`…dump-2647-20260901-000002-full`) and one `mbdump` snapshot (`20260905-002519`), both pinned in Task 1's README; `T` was computed from them once |
| cap strategy `trimmed_union`, `union_top_j` = 50, `union_degree_ceiling` = 50 | applied by `build` **after** the similarity table; identical `BuilderConfig` for every arm, asserted knob-by-knob by the build script (the `lbv_build.py` precedent) |
| similarity rescale `p99_log_clip`, `similarity_damping` = 0.0 | the only strategy `BuilderConfig.__post_init__` permits; and it cannot move a degree read, because the cap ranks on **unclipped** strengths (`pipeline.py`, *"Rank the cap on UNCLIPPED strengths"*) which at damping 0 are monotone in the raw score |
| router weights and the cost function (`ApiConfig`) | nothing in `builder/` writes them, and the **only** routing read taken here is `LBA-M1`'s query-cost half, which runs the shipped `find_journey` under `ApiConfig` defaults on every map through one code path |
| the fame source | `LBD-D4`: the existing `fame` stage over the arm's own population, or the read is not made. **No fame is fetched here** (`LBA-D5`), so the column is constant by being absent from every arm alike |
| the added set, the pre-existing set and the residual stratum | pinned files with committed sha256s (`cxr_added_mbids.txt` `bfed95ef…`, `cxr_preexisting_mbids.txt` `768054b7…`, `cxr_residual_mbids.txt` `fa8d85cc…`), read by every arm and **never re-derived** |
| the fame ruler used for banding | the served artifact's own `fame_lb` records, by MBID, for every arm — a fixed ruler across arms, and `LBA-X7` states what it cannot reach |

### §2.4 Held constant in the configuration, NOT constant in effect — the term the intervention switches on

> **This is the section `CLAUDE.md` requires because a factor table cannot see a dormant term:
> a term inert in the baseline *for a reason the intervention removes* is an uncontrolled
> variable that appears only in the arms that succeed.** There is one here, it is the drop
> lists, and it is exactly the shape of `LBD-A0V`'s own `w_floor` case.

**The un-listenable drop list removes nobody from `V` and nobody from `P` — and it removes nobody
from `U` either, because over `U` it cannot run at all.** Those two zeroes look identical in a
configuration dump and mean opposite things.

- Over `V` and over `P` the list is **measured inert**: the `20260805` payload covers `V` and
  drops none of it, and the `20260809` payload covers `P` and drops none of it. Both measurements
  are the pre-registration's own (`LBD-AM5-3` and `LBD-AM4-3` own those counts). The filter is
  *on*, *applicable*, and *removes nobody*.
- Over `U` the census guard **refuses**: `unlistenable_drop.py` raises `PopulationNotCensused`
  for any archive containing artists the census never evaluated, and every `U` arm's population is
  larger than any censused set by construction. So a `U` arm must set `drop_unlistenable=False`
  (`LBD-X3`'s rule for a table's own population), and the filter is *off*.
- `drop_no_release_tail` and `drop_featured_credit` have **no guard at all**, so over `U` they
  silently under-filter rather than refusing — the failure that makes no noise.

**Why this is the dangerous shape and not merely an inconvenience.** The arms that grow the
population are precisely the arms in which a filter that would remove unplayable artists stops
operating. Left alone, every `U` arm would report a larger, denser map *partly because its quality
filter was disabled*, and the factor table would show the filter as "held constant" in all nine
rows. **`LBA-M4` exists to size that term**, `LBA-G4` fires when it is large enough to discount
`LBA-M3`'s supply gain, and `LBA-X2` carries the bar into every sentence about a `U` arm.

**Two further terms that are active in every arm but whose effect grows with the arms that
succeed** — both carried forward rather than re-derived:

- **The degree ceiling** (`LBD-X1`). An arm that supplies more candidates hands more of them to a
  rule that deletes the weakest edges of over-full artists, **bilaterally**. Its bar is carried as
  `LBA-X3`. Raising the ceiling is **not** a free downstream fix and nothing here proposes one:
  design §9 keeps the cap-rule decision parked and the owner's, and Track B measured a cost on
  famous-pair journeys (figures owned by `../findings/2026-07-30-track-b-cap-selection-results.md`).
- **The largest-component prune.** It removes a small fraction of `V` and of `P` (counts owned by
  the two build READMEs) and its effect over `U` is unmeasured, because `U` has a fringe neither
  smaller population has. It is reported per arm by `LBA-M1` rather than assumed small.

### §2.5 Named exposures

- **`LBA-X1` — the population moves four population-relative quantities.** `pop_raw`
  (score-weighted in-degree), `fame_lb_pctl` (percentile within the artifact,
  `graph_store.fame_percentiles`), `degree_hub_penalty` (top-1 %-by-**degree**) and the p99
  rescale all recompute over each arm's own node set. This is `LBD-X2` and the `CXR-P1` mechanism.
  **Consequence, a bar:** no sentence may attribute a difference between two arms to the strength
  threshold while the population also moved. It is why the lattice is full and why every read
  below names which column its baseline isolates.
- **`LBA-X2` — the un-listenable census is a census over a population, and it over-drops.** Two
  distinct facts, both binding. (a) A payload is valid only for the population it censused, so any
  population larger than today's needs a re-census before the filter can apply — §2.4. (b)
  **`ULC-F4`**: the keep-check's criterion is the **name**-search route, while the app resolves
  **identity first** (`api/…/clips.py` `_search`, shipped 2026-08-02), so the rule can call an
  artist unlistenable whom the app would play on its first attempt. Figures for the size of that
  over-drop on both committed payloads are owned by
  [`builder/analysis/2026-09-05-lux-e1-drift-source/README.md`](../../../builder/analysis/2026-09-05-lux-e1-drift-source/README.md)
  §6.2 and are **not restated here**; that README's §6.3 records that its own read is unlicensed
  and that changing the rule needs its own pre-registration, a re-census and a rebuild. **So every
  `LBA-M4` figure is an over-estimate of what the app genuinely cannot play, by an amount §6.2
  bounds on two populations and nobody has bounded on `U`.**
- **`LBA-X3` — the degree ceiling absorbs supply**, carried verbatim from `LBD-X1`: a **graph-level
  supply null is barred from supporting a "the data is not there" conclusion.** The pair-table
  level is where that conclusion lives, and the `LBD-` track already took it (`R4` fired).
- **`LBA-X4` — the data bundle**, carried from `LBD-X5`. Between ListenBrainz's deployed lists and
  any arm here lie a corpus roughly three times the size, the absent `filter_True` stage, today's
  msid→mbid mapping, the uncredited band-member class and our deterministic tie-break. **No
  sentence may credit or blame any one component of it.** It applies to every comparison with the
  served map, which is every `LBA-M2` figure.
- **`LBA-X5` — the cap-step population term**, carried from `LBD-X4`. Artists took part in the
  served build's cap step that no arm here can include, because the emitter never writes them;
  the count is owned by `LBD-AM5-2`. **No sentence may attribute a served-map comparison to "the
  similarity data" without naming this term beside it.** It does not touch any arm-to-arm
  comparison, where both sides are emitted by the same emitter.
- **`LBA-X6` — `U`'s membership moves with the threshold.** `V` and `P` are pinned MBID files; `U`
  is a consequence of the arm. **Consequence, a bar:** a `U`-row threshold comparison
  (`LBA-A7`↔`LBA-A8`↔`LBA-A9`) is a comparison in which the population is a *dependent variable*,
  and no read may treat it as a one-column comparison in the same sense as the `V` and `P` rows.
  It is still the correct comparison to make, because that dependence is what a `U` population
  rule would actually ship — but it must be stated wherever a `U` threshold effect is reported.
- **`LBA-X7` — the fame ruler cannot reach outside `V`.** Banding uses the served artifact's own
  `fame_lb` records by MBID, which exist only for artists the served map contains. `LBA-M2` is
  *about* served artists, so it is unaffected; **any other by-band reporting is confined to the
  served population and says nothing about the artists an arm adds.** Fetching fame for a larger
  population is a real cost, estimated by `LBA-M5` and spent only at the go stage.
- **`LBA-X8` — every size figure here is a lower bound on the shipped artifact.** Arms build with
  `require_fame=False` and without clip ids (`LBA-D5`), so their serialised bytes and their boot
  memory omit the `fame_lb`, `deezer_ids`, `spotify_ids`, `apple_ids` and `artist_facts` metadata
  a shipped artifact carries. `LBA-G1`'s bar is set with headroom for that (§5), and the exact
  overhead is measured at the go stage on the candidate build, not projected here.

### §2.6 Which cells are built and censused, and what the unrun cells bar

**All nine cells are derived and their populations counted** (`LBA-D8` stage 1) — that costs
filters and `GROUP BY`s over a table that already exists. **Whether every cell is emitted and
built is a resource question, gated by `LBA-G2`, never a judgement.** Whether the census pass is started is likewise a resource question, gated by `LBA-G3` at the same point. The census is **one offline
pass over the union of all nine populations** (`LBA-D6`), so no arm is censused in preference to
another.

**If `LBA-G2` stops a cell**, the report says so in those words — *"unbuilt for a resource
reason"* — and these conclusions are barred for that cell, named now rather than negotiated later:

1. **No map-level read.** `LBA-M1`, `LBA-M2` and `LBA-M3` are graph-level and are simply unread;
   the cell's table-level population and pair counts stand and are reported.
2. **No inference that the rule is unservable.** A build that does not fit this machine says
   nothing about whether a service could hold the map — `build_from_archive` holds neighbour
   objects in a Python dict during its first pass, which is a property of the builder, not of
   `GraphStore`. **"We could not build it here" and "it is too big to serve" are different
   claims and the second needs `LBA-M1`.**
3. **No cross-population comparison at that threshold.** If `LBA-A9` is unbuilt, no sentence
   compares the two-listener bar across population rules at the map level.

---

## §3 — Decisions this document takes

`LBA-D1`–`LBA-D3` are the owner's and are in §1. The rest are this session's, and each is
methodology — the right-hand column of `CLAUDE.md`'s decision table.

**`LBA-D4` — every arm is a derivation of the existing `T`, and nothing re-runs the pass.**
`threshold` and `limit` are the only two tokens applied strictly after the cross-user aggregation
(the `LBD-` pre-registration's §1, verified from ListenBrainz's source), and the pairing form is
fixed by `LBA-D1`, so all nine arms are pure filters and window functions over one materialised
table. `lbd_derive.py` is run **unedited**, as `lbv_derive_a5.py` already runs it. **No
full-history pass is scheduled by this document**, which is why `LBD-C3`'s cost gate (`LBD-G3`) has
nothing to fire on here and why §4's cost measurement is about *refresh*, not about this run.

**`LBA-D5` — every arm builds with `require_fame=False`, and no fame is fetched.**
*Plain: the maps we measure carry no listener counts, because nothing we measure needs them.* All
five measurements are structural or resource measurements; **no journey is scored, no listen is
run** (`LBA-D3`), and `LBD-AM5-4`(iii) measured that a fame-carrying build is **structurally
identical** to its fame-free census build — node order, CSR arrays, scores and popularity. This is
what makes `LBA-M5`'s fame cost an *estimate* rather than a nine-fold fetch, and it is `LBD-D4`
met rather than worked around: no currency is introduced.

> ⚠ **One measurement does run the router, and it is admissible without fame — checked from
> source rather than assumed.** `LBA-M1`'s query-cost half calls the shipped `find_journey` at
> **zero `known` presses**. `pathfinding.py:130-132` computes `ramp_fame = w_known_ramp_fame_pctl
> × n_known`, which at `n_known = 0` is exactly `0.0`, and the file's own comment records that
> `cost += 0.0 * fame` is *numerically identical* to omitting the term — *measured, not assumed*,
> and pinned by `MSW-G2` (no path moves at k = 0). So a d0 query over a fame-free build takes the
> production cost function's exact values. **It follows that `LBA-M1` measures d0 only**, and
> **no deeper depth is measured here**, because the ramp is live there and fame is absent. That
> limit is stated in `LBA-M1` and is not worked around.

**`LBA-D6` — the un-listenable class is measured once, offline, over the union of all nine
populations.** Membership of the class is a property of an artist, not of an arm, so one pass
serves every cell and no arm is preferred. The pass is `ulf_census.py`'s **offline half only** —
its detector is `ULC-D2` applied to local MusicBrainz dumps with no network — run as a **forward
copy**, never in place, following the 2026-08-09 precedent (`docs/superpowers/2026-08-09-cex-task11-execution-log.md`
§2 records why re-running a frozen census script in place is refused). The **network half is not
run**: §4's `LBA-M4` states exactly what it therefore estimates and how.

**`LBA-D7` — arms over a population the committed payloads do not cover build with
`drop_unlistenable=False`, and the fact is reported per arm rather than inferred from the
config.** Over `V` the payload is `unlistenable_drop_algb_20260805.json` and over `P` it is
`unlistenable_drop_algb_20260809.json`, each pinned by `unlistenable_list_path` and each measured
inert on its own population; over `U` the filter is off. **Every arm's row in every results table
carries a `filter` column saying `on, inert` or `off, uncensused`.** §2.4 is why.

**`LBA-D8` — execution is staged, and stage 1 is the cheapest thing that could change the
design.**

- **Stage 1 — derive and count, all nine cells.** Filters and window functions over `T`, plus a
  `GROUP BY` for each cell's distinct-artist count and pair count, **and the count of union members
  absent from the census coverage store**. Minutes to a couple of hours, no emission, no build.
  **This is the only measurement that can rule a cell out on resources before any of it is spent**,
  and **both `LBA-G2` and `LBA-G3` read off it** — the second moved here from stage 3 under
  `LBA-AM1`'s finding `LBA-AM1-A11`, because a gate discovered six hours into a census pass has already cost
  what it exists to save.
- **Stage 2 — emit and build** every cell `LBA-G2` did not stop, in the order `A1`, `A4`, `A7`,
  `A2`, `A5`, `A8`, `A3`, `A6`, `A9` — control first, then each threshold across all three
  population rules, so that a partial run always holds a complete one-column comparison.
- **Stage 3 — the census pass and the five measurements.**

⚠ **Stage 1 may stop a cell only on `LBA-G2`'s stated bar, and on nothing else.** A cell is never
dropped for looking uninteresting, for being "obviously dominated", or for costing time. **The
executing session does not have the authority to reduce the lattice**; changing it is an
amendment, committed before stage 2 runs.

**`LBA-D9` — `LBA-A1` and `LBA-A3` are reused, not rebuilt, and their identity is asserted by
sha256 rather than assumed.** `LBD-A0V` and `LBD-A5V` are exactly these two cells: same table
(`T`), same tokens, same population `V`, same drop-list override, same `BuilderConfig`, built by
`lbv_build.py` under `LBD-AM5-3`. The executing session **re-verifies both artifacts and their
archives against the sha256s the served-population README's §0, §2 and §5 record** and refuses to
proceed on any mismatch. **Reuse is the better control, not only the cheaper one:** rebuilding
them would introduce a build-date column the factor table does not have. *(Their serialised
artifacts carry fame, since they were built for a listen; `LBA-M1` reads the **census** build's
figures, which the same README records separately.)*

---

## §4 — The five measurements

Each carries its plain sentence, fixed here before any result exists, and either a stated effect
size or an explicit *reported descriptively, no threshold*.

### `LBA-M1` — map size and what it costs to serve

> **Plain sentence: how big is the map — how many artists, how many connections, how large a
> file — and can the machine we run on still serve it?**

Per arm, four quantities and one comparison:

| quantity | how |
|---|---|
| **artists** | nodes after the largest-component prune, from the built graph |
| **connections** | reported in **both** units, each labelled: *connections* (degree sum ÷ 2) and *CSR entries* (each connection in both directions, the unit every manifest sidecar's `"edges"` uses). The served-population README's §0 warning records that a build was once refused because a bound was written in one unit and checked in the other |
| **bytes** | **the BARE-ARTIFACT size**, `24 + 4(N+1) + 9·E_csr + len(bare metadata JSON)`, where *bare* is the four mandatory metadata keys only — `mbids`, `names`, `disambiguations`, `popularity` (`artifact.py`'s `serialise`; the other five are additive and omitted when empty). Computed **identically for all nine arms**, by decoding, with **no rebuild** — which is what makes it comparable across the seven arms that are built here and the two that are reused (`LBA-D9`). Reported beside the **shipped projection** = bare + the measured per-node additive cost from the calibration pair below. *(Revised 2026-09-14, `LBA-AM1` finding `LBA-AM1-A12`: the previous definition was "the serialised census build", and no census build of `LBA-A1` or `LBA-A3` was ever serialised — their only artifacts carry all five additive keys, so seven arms would have been compared against two that were ~1.34× larger for a reason that is not the arm.)* |
| **boot memory** | peak RSS of a process that loads the artifact through the shipped `GraphStore` and nothing else, measured three times, median reported — **then scaled to the shipped artifact by the measured calibration below.** The raw census figure is never compared with `LBA-G1`(a)'s bar directly |
| **query cost** | median and p95 wall-clock of the shipped `find_journey` at **d0**, no exclusions, `ApiConfig` defaults, over a fixed pair set drawn once and reused for every arm — the same process, the same machine, the arm's map and the served map measured back to back. `LBA-D5`'s block is why this is the production cost function's exact values, and why **only** d0 is measured |

**The pair set for the query-cost half is fixed before any arm is built**: 200 pairs drawn with
`random.Random(20260914)` from the artists present in **every** built arm and in the served map,
so that no arm is measured on pairs another could not route; the resulting MBID list is written to
a file with its sha256 **before stage 2 begins**. A pair whose endpoints are adjacent in any map
is redrawn, since `find_journey`'s forced-detour branch is a different code path. *(The drawing
rule is fixed now; the set cannot be drawn until stage 2 says which arms exist, which is stated
here so the ordering is not discovered later.)*

**Two calibration measurements, taken ONCE before stage 2 and fixed here as instrument work,
not as results.** *Plain: work out how much bigger a real shipped map is than the stripped-down
ones we measure, and how much memory the web service itself uses, so the size limit is about the
thing we would actually run.*

- **`metadata_ratio`** — median peak RSS of a `GraphStore`-only load of `graph-lux4.bin` ÷ the same
  for `graph-msw-tu50.bin`. The two are **identical in N and in CSR entries** (both sidecars record
  58,838 / 1,315,684, verified against the files 2026-09-14) and differ only in the three `LUX-4`
  additive keys, so the ratio isolates the metadata. **It is a property of the artifacts, not of any
  arm**, and it must be measured rather than assumed: the same pair differs by **1.336×** in
  serialised bytes, and resident cost does not track bytes, because `GraphStore` holds these keys as
  Python `list[str]` and `list[dict]` while the CSR arrays stay as numpy.
- **`framework_rss`** — resident of a booted `build_default_app` process minus the store's own
  contribution, measured once on the served artifact. **This term has never been measured in this
  project**, and `LBA-G1`(a) cannot be evaluated without it.

**What `LBA-M1` can and cannot separate, derived rather than discovered later.** The cap rule
enforces `degree ≤ 50` (`graph.py`'s `trimmed_union_cap`), so for any arm `E_csr ≤ 50·N` and
`N ≤ |population|`. On the `V` row that caps every arm at `|V|` nodes and `50·|V|` CSR entries —
the same arithmetic the served-population README's §5 uses to derive its acceptance ceiling. The
two committed `V`-row endpoints (that README's §3, which owns both figures) already span a small
fraction of that headroom, while the `V`→`P` step at a fixed threshold moves both quantities by
tens of percent. **So `LBA-M1` measures the population column with far more dynamic range than the
threshold column, and `LBA-G1` is in practice a population gate.** It is not degenerate — the
statistic moves — but a reader must not take a `V`-row null on `LBA-M1` as evidence that the
threshold does not affect size. *(Recorded 2026-09-14, `LBA-AM1` finding **`LBA-AM1-O1`**.)*

**Against the hosting baseline.** The service runs on App Runner at **1 vCPU and 2 GB memory**,
`min_size=1`, `max_size=2` (`infra/src/artistpath_infra/stack.py:199-200,268-273`). The Gate 2→3
review found *"memory is not a constraint"* and cold start 0.13 s local — **on the retired 75k
artifact, not the one served today** — and measured the live 1-vCPU container at **2.5–3.5× the
dev laptop's per-request CPU**, with throughput flat under concurrency at roughly 1.5 req/s. All
of those figures are owned by [`../findings/2026-07-27-gate2-gate3-team-review.md`](../findings/2026-07-27-gate2-gate3-team-review.md)
§1, §5 and its live-calibration section, and **none is restated here.** `max_size=2` is the cost
ceiling and the only automatic spend control, and `NEXT.md` places it in *must not be changed*.

**Effect size: `LBA-G1`, §5.** Two halves, either of which fires.

### `LBA-M2` — what happens to the artists the app serves today

> **Plain sentence: of the artists the app can reach today, how many are simply not in this map
> at all — and of the ones that are, for how many have fewer than half the artists we show as
> similar to them survived?**

Both halves are reported **by fame band**: five equal-count bands by the served artifact's own
`fame_lb` (band 0 least-listened, band 4 most), the `LBD-M1` precedent, a fixed ruler across arms
(`LBA-X7`).

- **Absent.** Members of `V` with no node in the arm's map, split into *no pair at all in the
  arm's table* and *pruned with the largest component* — the split the served-population README's
  §3 already reports for two maps, because they are different failures.
- **Materially changed, defined before any build.** For an artist present in **both** the served
  map and the arm's map, let `A` be its neighbour set in the **served** map, `B` its neighbour set
  in the **arm's** map, and `c` the size of their intersection. The gated statistic is
  **retention**:

  > **`R = c / |A| < 0.5`** — *plain: fewer than half the artists we show as similar to them are
  > still there.*

  Reported alongside the share at **`R = 0`** — *plain: none of them is still there.*

> ### ⚠ The statistic was JACCARD until 2026-09-14, and the plain sentence did not match it
>
> **Revised under `LBA-AM1`, findings `LBA-AM1-A1` and `LBA-AM1-A6`, before any arm ran.** The original read *"Jaccard
> overlap below 0.5"* beside the sentence *"fewer than half the artists we show as similar to them
> are the same artists."* **Those are different statistics, and the gap is one line of arithmetic.**
> For two lists of equal length `d`, Jaccard is `c / (2d − c)`, so a Jaccard of 0.5 means
> `c = 2d/3` — the bar fired when **more than a third** of the list changed, not more than half.
> The sentence's own condition, `c < |A|/2`, is a Jaccard of **1/3**. `CLAUDE.md` requires the plain
> sentence to be fixed beside the value *before any result exists* precisely so it cannot be
> reshaped to fit one; here the two disagreed at authoring time, which is the cheapest possible
> moment to find it.
>
> **Retention is adopted rather than simply moving the Jaccard bar to 1/3, and the reason is a
> second defect the same critique derived.** Jaccard is bounded above by the ratio of the two list
> lengths, so a Jaccard of 0.5 or more is **arithmetically impossible** whenever one list is more
> than twice the other. The original text asserted the opposite — *"both neighbour lists are capped
> at 50 by the same cap rule, so the two sets are of comparable size and Jaccard is not distorted by
> a length mismatch"* — and **that does not follow: the ceiling bounds the maximum, not the
> spread.** The served map's median degree and the two committed arms' medians differ by 8 and 10
> (served-population README §3, which owns those figures), so a large share of artists would have
> been flagged with **zero contribution from neighbour identity**. On the *tightest* comparison
> available — the two committed arms against each other, same pinned population, medians two apart
> — the analyst measured **5.42 %** of the common set forced below 0.5 by the length pair alone;
> the served-versus-arm comparison `LBA-M2` actually makes has a wider median gap and therefore a
> larger forced share. Retention has no such bound: its denominator is the served list alone, so an
> arm holding a longer list is not penalised for holding one.

**Four raw quantities are recorded per artist, and five shares per arm** — the controls the
critique named `C-β` and `C-γ`, adopted in full. *Plain: write down enough per artist that three
different reasons a neighbourhood changed can be told apart afterwards.*

Recorded per artist: the served list's length, the arm list's length, the intersection size, and
`b_out` — the number of the arm's neighbours that are **not** artists the app serves today.

| reported per arm | what it is |
|---|---|
| **`R`** | intersection ÷ served list length — **the gated statistic** |
| **`R_avail`** | intersection ÷ the number of served neighbours that are **in the arm's population at all** — *plain: of the artists we show today that this map could have chosen, how many did it keep?* **This is the control that separates "it chose differently" from "it was never available to choose"** |
| **`b_out` share** | `b_out` ÷ the arm list's length — *plain: what fraction of the new neighbours are artists the app does not serve today* |
| **forced share** | the share of the common set whose two list lengths differ by more than 2× — **the null model for a Jaccard-style read**, reported so the retired statistic's bound stays visible and a later reader cannot re-adopt it unknowingly |
| **denominator, both ways** | the changed count as a share of the common set **and** as a share of `V`, so the absent half and the changed half compose additively (`C-γ`). Without this the two halves trade off: an arm that loses more served artists gets a **better**-looking changed share, because the artists whose neighbourhood moved most have been removed from the denominator |

**Why `R_avail` is not optional, derived.** Writing `J` for the Jaccard of the same pair and `J_V`
for the Jaccard with the arm's list restricted to the served population, the identity is
`1/J − 1/J_V = b_out / c`: **the population contribution is exactly additive in inverse-Jaccard
units**, so it can be reported as its own column rather than left bundled into one number. The same
separation in retention terms is `R_avail − R`, which is non-zero exactly when some served
neighbour was outside the arm's population. **Three causes lower any one-scalar overlap measure — a
pure re-ranking, the cap re-selecting from a larger candidate set, and the population changing — and
no single scalar separates them.** Retention sees the second and third; `R_avail` removes the third;
a pure re-ranking is invisible to all of them, which is why the rank companion below exists.

**A rank companion, descriptive and ungated: `overlap@10`** — the share of the served map's ten
strongest neighbours still present in the arm's list. *Plain: of the ten artists we currently think
are closest to them, how many survive?* A pure re-ranking — the same set in a different order —
scores `R = 1.0` and is invisible to every membership statistic, and the top of the list is what a
journey actually walks through. **No threshold attaches to it.**

**An arm-to-arm comparison within each population row**, adopted as the critique's `A7`:
`LBA-A1`↔`A2`↔`A3`, `LBA-A4`↔`A5`↔`A6`, `LBA-A7`↔`A8`↔`A9`, using the same statistics. *Plain:
compare the maps to each other as well as to today's, so the effect of the strength bar can be seen
without everything else moving at the same time.* **Both sides share a population and an emitter, so
the population cause and the `LBA-X4` data bundle are absent by construction — this is the only
`LBA-M2` comparison in the design that isolates the threshold.** ⚠ On the `U` row `LBA-X6` still
applies: the population moves with the threshold there, so that row's arm-to-arm comparison is not
one-column in the sense the other two rows are.

**Effect size: reported descriptively, no threshold.** *Plain: this is what the owner is deciding
about, not something a number can decide for him.* A map that changes a lot is what adoption
*is*; whether that change is acceptable is the left-hand column of `CLAUDE.md`'s decision table —
his, on his product judgment, informed by §8's listen if he says go. **A session must not attach a
bar to this and must not describe a high figure as a failure or a low one as a pass.**

⚠ **`LBA-X4` and `LBA-X5` travel with every `LBA-M2` figure taken against the served map** — the
data column is a bundle no arm separates, and the cap-step population term applies. **Neither
travels with the arm-to-arm comparison**, which is exactly its point.

### `LBA-M3` — the added artists' supply

> **Plain sentence: of the artists the deeper crawl added — the ones that arrived with almost no
> connections — what share are still dead ends in this map?**

The track's own statistic, unchanged: **share at or below 2 connections over the pinned added set,
with an artist absent from the map counted as 0** (`LBD-C2b`'s `share_le_2_or_absent`), with the
pinned pre-existing set as the **within-arm control** and the arm's own table-level figure as the
second control — `LBD-G2`'s two-control condition, carried verbatim. The residual stratum
(`cxr_residual_mbids.txt`) and its complement are reported **descriptively**, the shape `LBD-AM1`
gave `LBD-C2a`.

**Effect size: `LBD-G2`'s bar, carried — ≥ 1 percentage point against the arm's isolating
baseline, admissible only with both controls reported; ≥ 10 points without them.** The bars and
their derivation are the `LBD-` pre-registration's §3 and are not re-derived here.

> ### ⚠ Where this bar is admissible, resolved here rather than left to an executing session
>
> **Revised 2026-09-14 under `LBA-AM1`, findings `LBA-AM1-A4` and `LBA-AM1-A9`.** The original text left two questions
> open that a session running the arms would have had to answer with results in hand, which is the
> one moment a pre-registration exists to take the decision away from.
>
> **On the `V` row the bar is UNFIREABLE, by construction.** The added set is exactly the artists
> the extended crawl has and the served map does not, so no member of it is in `V`; the emitter
> writes a payload only for a member of the arm's population, so no `V` arm can contain one. The
> statistic is therefore **1.0 for `LBA-A1`, `LBA-A2` and `LBA-A3` alike**, and the difference
> between any two of them is **identically zero**. §2.6 already said the value is a construction
> fact; what it did not say is the consequence — **`LBD-G2`'s bar cannot fire on `A1`↔`A2`,
> `A1`↔`A3` or `A2`↔`A3`, so a null there carries no information about the threshold.** This is the
> shape `NEXT.md` records for `CRS-C3`, which was structurally unable to fire on any selectable
> Track B cell and whose null therefore said nothing about concentration. **A null that cannot be
> anything else is not evidence.** See `LBA-R4`, which is amended to match.
>
> **On the `U` row the bar is admissible DESCRIPTIVELY ONLY.** `LBA-M3`'s own rule is that
> `LBD-G2` applies within a population rule and never across one; `LBA-X6` says the `U` population
> is a *dependent* variable that moves with the threshold. Those two clauses conflicted as written.
> **The resolution: the bar may be computed and reported on `A7`↔`A8`↔`A9`, and it may never be
> read as a one-column threshold attribution there.** Every `U`-row sentence naming it carries
> `LBA-X6` beside it.
>
> **So the bar is admissible as a one-column threshold read on exactly two arms** — `LBA-A5` and
> `LBA-A6`, each against `LBA-A4`. Stated as a number rather than left to be counted later, because
> a reader who believes the lattice supports nine such reads will over-weight the evidence by more
> than four times.

**A fourth stratum, added under `LBA-AM1` finding `LBA-AM1-A10` (`C-ε`): `nodes(arm) − V`, per arm,
descriptive.** *Plain: the artists this map has that the app does not serve today — including the
ones no crawl of ours ever found.* The three pinned strata are all subsets of the extended crawl's
population, so **none of them can see the artists a `U` rule adds beyond it** — which is the only
thing `LBA-A7`–`A9` exist to test. This stratum **cannot be pinned** and is derived per arm
(`LBA-X6`), so it is descriptive, carries no bar, and its membership is recorded with the arm's
figures so a later reader can tell which artists it covered.

### `LBA-M4` — playability

> **Plain sentence: of the artists in this map, and of the ones it adds beyond what the app serves
> today, what share would the un-listenable rule throw out — and how confident is that number?**

**Run, not estimated: the class.** The offline census half (`LBA-D6`) applies `ULC-D2` — no
sole-credited substantial release group — over the union population, using the coverage store at
`builder/analysis/census-coverage/ulf_coverage.json` so that only genuinely new artists cost a
dump pass. Each arm reads its own share off that one pass.

> ⚠ **"Exact" is exact only for freshly evaluated artists, and the qualification is now required
> rather than optional** (`LBA-AM1`, finding `C-δ`). The coverage store carries verdicts from
> three earlier censuses, each tagged with its source, and those verdicts were computed against
> **earlier MusicBrainz snapshots than the pinned `20260905-002519` one**. The provenance is
> recoverable per artist, so **every `LBA-M4` class figure is reported split by verdict source** —
> freshly evaluated against this dump, versus each carried census — and the word *exact* is used
> only of the fresh share. The store's own current membership is recorded before and after the
> pass (`LBA-D6`), since the census both reads and writes it.

**Estimated, and here is exactly how: the drop.** Dropping requires the network keep-check —
a commercial-DSP link plus a resolving clip — which `LBA-D6` does not run. So the drop share is
estimated as *class share × the within-class drop rate the two committed censuses measured*, with
**both** committed rates reported as a range rather than averaged, since they were taken on
different populations. Those rates are owned by
`builder/analysis/2026-08-05-ulf-census/ulf_census.json` and
`builder/analysis/2026-08-09-cex-recensus/ulf_census.json` and are **not restated here**. Every
`LBA-M4` drop figure is labelled **estimated** wherever it appears.

**Three bounds on the estimate, all stated now.**

1. **It is an over-estimate of what the app cannot play, by `ULC-F4`'s mechanism** — `LBA-X2`(b).
   The size of the over-drop on the two committed payloads is owned by the LUX-E1 drift-source
   README §6.2; **on `U` it is unbounded, because nobody has measured it there.**
2. **The carried verdicts are un-re-run.** Both committed payloads carry drop verdicts inherited
   from the earlier no-release and featured-credit rules, and those entries hold no clip record.
   The same README bounds that residue; it is unmeasured, not zero.
3. **The within-class drop rate is being extrapolated outside the populations it was measured on**
   (`LBA-AM1`, `C-δ`). Reporting both committed rates as a range is honest about their spread; it
   is **not** a control for applying either to `U`, and no sentence may treat it as one.

**Effect size: `LBA-G4`, §5** — on the *added* half only, because that is the half that discounts
`LBA-M3`. The whole-population share is **reported descriptively, no threshold.**

> ⚠ **`LBA-G4` is `n/a` on the `V` row, not zero** (`LBA-AM1`, finding `LBA-AM1-A5`). Its subject is the
> artists an arm adds beyond `V`, and for a `V` arm that set is empty — a share of nothing, not a
> share of zero. The per-arm table prints **`n/a`**; printing `0` would read as *perfectly
> playable*, which is the opposite of *not measured*.

### `LBA-M5` — what it costs to operate

> **Plain sentence: how long does one refresh take, how much disk does it need, and what exactly
> would somebody have to run?**

**Reported descriptively, no threshold.** Four parts:

1. **The similarity pass** — cited, never re-run and never re-timed here. The `LBD-A0` pass's
   stage timings, spill and the combine are owned by `builder/analysis/2026-09-08-lbd-similarity/README.md`
   §4; the `LBD-A4` pass's by `builder/analysis/2026-09-13-lbd-a4/README.md` §4; the hardware
   context — the dump on a spinning disk and DuckDB's thread-count trap — by §4 of the first.
   **What a refresh adds over today's pipeline at the SERVED population is this pass and nothing
   else**: the archive replay (emit, then build) is a cost the pipeline already pays, and its wall
   clocks are owned by `builder/analysis/2026-09-10-lbd-supply/README.md` §1 and §2. ⚠ **At any
   population above `V` that sentence no longer holds** — §6's steps 6 and 7, the re-census and the
   fame fetch, are additional and are sized by part 2 and by `LBA-G3`. *(Corrected 2026-09-14,
   `LBA-AM1`, finding `LBA-AM1-O3`: as first written this part and §6's ⚠ contradicted each other for
   every arm above `V`.)*
2. **The fame fetch — estimated, and the method is fixed here.** `fetch_fame` posts batches of
   `MAX_PER_REQUEST = 1000` MBIDs (`fame.py:57`, the endpoint's own truncation limit read from
   ListenBrainz source) and pauses `BuilderConfig.request_delay_seconds` = 1 / `requests_per_second`
   between batches, which at the shipped `requests_per_second = 5.0` (`builder/…/config.py:74,289-290` — **the builder's, not the API's**; both packages have a `config.py`) is
   0.2 s. So the estimate is **⌈N / 1000⌉ × (0.2 s + one round trip)**, with N the arm's measured
   artist count from `LBA-M1` and the round trip taken from the one measured fame run on the
   record (owned by `docs/superpowers/2026-08-09-cex-task11-execution-log.md` §6). The stage is
   **resumable**, so a refresh pays only for artists with no record — stated because it is the
   difference between a first build and a recurring cost.
3. **Disk at a stated cadence.** The standing corpus and its annual growth, and the re-download
   cadence a deletions-matter policy implies, are design §8's and are cited from there. The pinned
   dump's own size and file count are owned by Task 1's README §1. **The cadence is a policy
   choice, not a measurement:** the procedure below is written for a **monthly** full refresh,
   and a different cadence changes only step 1's frequency.
4. **The refresh procedure**, §6 — a numbered list, which is the deliverable.

⚠ **`LBA-M5` adds no arm-discriminating information beyond `LBA-M1`'s artist count, and no read may
treat it as independent evidence about an arm** (`LBA-AM1`, finding `LBA-AM1-O2`). Parts 1 and 3 are
identical across all nine arms — one pass over one shared table, one corpus — part 4 is a
deliverable rather than a measurement, and part 2 is a deterministic function of `LBA-M1`'s N. It is
a cost statement about a *candidate*, not a comparison between candidates.

## §5 — Gates, each with its own effect size

**Every gate carries the size of difference that fires it.** A trigger without one cannot tell the
finding it was written for from noise, and it fires the expensive response either way.

> ### ⚠ All four gates were revised on 2026-09-14 under `LBA-AM1`, before any arm ran
>
> The `ml-graph-analyst` critique found that **two of the four were not evaluable as written** —
> `LBA-G1`(a) compared a stripped-down build against a bar protecting a shipped one, and `LBA-G2`
> extrapolated peak memory from a basis that does not exist on the record — and that a third fired
> too late to act on. Each is re-derived below with its inputs named. **No result existed for any of
> them**, so the commit-before-results property is intact and this revision spends none of it.

| gate | plain sentence | fires when | consequence | effect size |
|---|---|---|---|---|
| **`LBA-G1`** hosting | *this map is too big, or too slow, for the machine the app runs on* | **either** half: (a) **projected shipped peak RSS** — the census build's measured median peak × `metadata_ratio`, **plus** `framework_rss` — exceeds **1.6 GB**; **or** (b) the arm's **median d0 query wall-clock exceeds 2× the served map's**, measured back to back in the same process on the same pair set | the arm is reported as **requiring a hosting or router change before it could ship**, and that requirement is named in every sentence about it. **It does not stop the arm being measured** — the other four measurements are taken and reported | 1.6 GB; 2× |
| **`LBA-G2`** build feasibility | *we cannot build this map on this machine* | the arm's projected build peak RSS exceeds **24 GB**, projected from a fit over **every build already instrumented in this stage**, in **archive neighbour rows** | the cell is **not emitted or built**. §2.6's three barred conclusions apply. **Not a finding about anything** — a resource fact, `LBD-G4`'s shape | 24 GB projected peak |
| **`LBA-G3`** census feasibility | *working out which artists are unplayable would take too long* | **at stage 1**, the projected offline census pass exceeds **6 hours**, projected as a fixed scan floor plus (artists in the union population but absent from the coverage store) ÷ the per-artist rate the 2026-08-09 census measured | the pass is **not started**. `LBA-M4`'s class share for the uncovered part is **estimated** from the class rates the committed censuses measured, labelled as such, and the report says which arms carry an estimated class rather than a measured one | 6 h projected |
| **`LBA-G4`** playability discount | *the artists this rule adds are much more often unplayable than the ones it keeps from today's map* | for an arm, **the class share over `nodes(arm) − V` exceeds the class share over `nodes(arm) ∩ V` by ≥ 10 percentage points** — both taken from the **same census pass, the same dump and the same arm** | `LBA-M3`'s supply figure for that arm is **reported twice** — as measured, and with the estimated drop applied — and the report says the gain is discounted. **It stops nothing** | 10 pp |

### Where each bar comes from, and which of its inputs are measured rather than chosen

**`LBA-G1`(a) — 1.6 GB, and the two terms that make it evaluable.** *Plain: the limit is about the
map the app would actually load, not the stripped-down one we measure.* The instance holds 2 GB
(`stack.py:268-273`); 1.6 GB is **80 %**, leaving 20 % for request-time allocation and OS slack.
That margin is **a design choice with no prior calibration and is stated as one.** What is *not*
chosen is the rest of the expression:

- **`metadata_ratio`** is measured (`LBA-M1`'s calibration block), not assumed. **The original bar
  assumed 30 % of the instance would cover the interpreter, the framework, the clip cache *and*
  the metadata a census build omits — one flat number standing in for four terms, three of which
  scale differently.** The critique measured the metadata term alone on a pair of artifacts
  identical in artist count and CSR entries: **it nearly doubles resident cost while adding only
  about a third to serialised bytes**, because `GraphStore` holds those keys as Python lists of
  strings and dicts while the CSR arrays stay as numpy. A flat deduction in the wrong direction by
  that much admits an arm that cannot boot.
- **`framework_rss`** is measured once and **has never been measured in this project**. Until it
  is, `LBA-G1`(a) is **not evaluable**, and an executing session that reaches stage 2 without it
  must take it before reading the gate rather than guessing it.

**`LBA-G1`(b) — 2×, and what its justification does and does not rest on.** The ratio is
self-normalising, which is its strength: it compares an arm with the served map in the same process
on the same pairs, so machine state cancels. The Gate 2→3 review's live calibration found the
container **2.5–3.5× slower per request than the dev laptop** with throughput flat under
concurrency, and its top blocking finding rests on a single uncontended obscure request already
costing about two seconds live — **all owned by that review and not restated.** ⚠ **Converting that
into "a 2× local increase lands past four seconds live" requires the served map's own local median
d0, which no document on the record states.** *(Corrected 2026-09-14, `LBA-AM1`, finding `LBA-AM1-O4`:
the original text asserted the four-second figure as though it followed.)* Two consequences, both
binding: the missing quantity **is measured as part of `LBA-M1` itself**, since the served map's
median d0 is one of the two numbers the ratio is built from — so the gate supplies its own
calibration; and **the cited two-second figure is a tail while the gate reads a median**, so the
report gives **p50 and p95 side by side** and the gate fires on the median alone.

**`LBA-G2` — 24 GB, and the basis it now has.** The machine has 32 GB; 24 GB is the bar `LBD-G4`
used for the same machine and the same reason, and `LBD-AM4-2` barred `LBD-A3` from building on
exactly this ground. ⚠ **The original text projected from "the three builds on the record whose
rows and wall clocks are owned by the two build READMEs" — and that basis does not exist**: there
are **four** such builds, not three, and **none of them records a memory figure at all.** Neither
build README nor any committed JSON beside them carries one (checked 2026-09-14), and wall clock is
not a proxy for peak memory — across those four builds it varies several-fold per neighbour row for
reasons the served-population README itself attributes to OS cache state. So the projection is now
**built rather than assumed**:

- **Peak RSS is instrumented in the stage-2 build wrapper** and recorded per build, beside the
  neighbour-row count already recorded. This is the missing instrument, and it is a few lines in
  `lbv_build.py`'s shape.
- **Stage 2 builds in ascending order of archive neighbour rows**, so every projection is an
  interpolation or a short extrapolation from builds already completed, and the first builds are
  the small safe ones. A cell is stopped when its projection from **all** instrumented builds so
  far exceeds 24 GB.
- ⚠ **The unit is ARCHIVE NEIGHBOUR ROWS — pre-cap, two per pair — and not CSR entries.** Three
  edge units are in play in this track and the served-population README's §0 records a build
  already refused once for confusing two of them. On the committed arms the pre-cap and post-cap
  counts differ by a factor of several; reading one as the other misprojects a build peak by that
  factor.

**`LBA-G3` — 6 h, and it now fires at stage 1 rather than six hours into stage 3.** The bar is a
working-session choice — the longest census pass that still fits between two sessions without
occupying the owner's machine for a working day — and is **stated as a choice**. ⚠ **What changed
is the variable, not the bar** (`LBA-AM1`, finding `LBA-AM1-A11`): the cost driver is the count of union
members **not already in the coverage store**, which stage 1 produces for free, and the one census
at a comparable population on the record (owned by the 2026-08-09 execution log §6) gives both the
scan floor and the per-artist rate. Projecting at stage 1 costs nothing; discovering the overrun in
stage 3 costs six hours and an unmeasured arm.

**`LBA-G4` — 10 pp, and its baseline is now one column away.** ⚠ **The original baseline was the
class rates the committed censuses measured on their own populations** — a different population, a
different MusicBrainz dump, and a *whole-population* share set against an *added-subset* share:
at least two columns, possibly three. *(Corrected 2026-09-14, `LBA-AM1`, finding `LBA-AM1-A5` / `C-δ`.)* The
baseline is now **within the arm**: the class share over the artists it adds beyond `V` against the
class share over the artists it keeps from `V` — **same rule, same dump, same pass, same arm, one
column.** The 10-point size is unchanged and is still calibrated on the spread between the class
rates the censuses on the record produced, which remains the only calibration available for this
quantity; those figures are owned by the two census JSONs named in `LBA-M4`. *(The original
derivation said "three censused populations" while the firing clause said "two committed censuses";
the bar is calibrated on the spread across **all** censused populations on the record, and the
firing clause is the within-arm comparison above.)*

## §6 — The refresh procedure

*Plain: if we adopt this, here is the whole list of what somebody runs to make a new map, and
what gets written down so a later reader can tell exactly which map they have.*

Pinned per `LBD-D5`: **a dump id, a MusicBrainz snapshot, and a parameter string**, all three
recorded in a `MANIFEST.json` at the archive root and carried into the artifact's sidecar by the
shipped `build_manifest` / `write_manifest`. `resolve_build_inputs` and `log_build_inputs`
(`builder/src/artistpath_builder/manifest.py:67,133`) are the builder-side pattern the archive
manifest feeds.

1. **Download the ListenBrainz Spark/parquet dump.** Record its id, `TIMESTAMP`, file count and
   row count. Verify against the published sha256 where the published tar is available; where it
   is not, record the internal-consistency checks instead and say so — Task 1's README §1 carries
   the standing warning that this substitution was necessary once and why.
2. **Download the MusicBrainz `mbdump` snapshot.** Record its directory timestamp and both
   `SCHEMA_SEQUENCE` values; extract `recording`, `artist_credit_name` and `artist` into the three
   parquet frames, each sorted so a rebuild is byte-comparable, each sha256'd.
3. **Run the similarity pass** at the pinned parameter string and **ListenBrainz's own pairing**
   (`LBA-D1`), chunked by `user_id % k` — exact, not an approximation, because every stage up to
   and including the per-user cap partitions by user. Record `T`'s sha256, row count, wall-clock
   and spill.
4. **Derive the adopted arm** at its `threshold` and `limit` by `lbd_derive.py`, unedited. Record
   the table's sha256 and row count.
5. **Emit the archive** over the adopted population rule, by `emit_archive.py`, unedited. The
   `MANIFEST.json` records the dump id, the `mbdump` timestamp, the parameter string, **the
   pairing form and why** (`LBD-D6`), the population rule and the sha256 over its sorted member
   MBIDs.
6. **Re-census the drop lists over the new population** — both halves. The offline half applies
   `ULC-D2` with write-back to the coverage store; the network half runs the keep-check to
   completion, refusing to freeze while any lookup was refused (`ULF-4`). A population the payload
   does not cover makes the build refuse, loudly, which is the design.
7. **Run the `fame` stage** over the new population. Resumable; it costs only what is not already
   recorded.
8. **Attach the clip and streaming ids** — `deezer_ids.py`, `dsp_links.py`, `artist_facts.py`.
9. **Build, acceptance-check, serialise, write the manifest.** Acceptance per §8's rule, never
   widened from `PRODUCTION_ACCEPTANCE`'s intent.
10. **Verify and deploy.** Reload the artifact through the shipped `GraphStore`; take
    `ARTISTPATH_GRAPH_SHA256` **from the sidecar, never transcribed by hand** (`DEP-24`), so a
    wrong artifact refuses to boot.

⚠ **Steps 6 and 7 are the two that do not exist today at this scale.** Step 6's network half is
hours and is the only step that depends on a third-party service answering; step 7's cost scales
with the population, estimated by `LBA-M5`(2). **Neither is run by this pre-registration.**

---

## §7 — The go/no-go read table

**The stop is the owner's.** Every read below is a statement of what the numbers say, not a
recommendation, and **no row concludes a route.** Each names the run state it presupposes.

**Run-state vocabulary.** *derived* = the arm's table exists and its populations are counted
(stage 1). *built* = the arm is emitted and built (stage 2). *censused* = the offline census pass
has run and the arm's class share is measured rather than estimated. *sized* = `LBA-M1`'s boot and
query-cost halves have been taken on that arm. *complete* = every cell either built or stopped by
`LBA-G2` with its bar recorded.

| # | result | the read | run state it presupposes |
|---|---|---|---|
| **`LBA-R0`** | stage 1's counts project a build peak above `LBA-G2`'s bar for one or more cells | those cells are **not built**. *Plain: the biggest maps are too big to assemble on this machine.* **Not a finding about anything** — a resource fact. §2.6's three barred conclusions apply, and the lattice is reported with holes rather than silently reduced | derived |
| **`LBA-R1`** | **no arm fires `LBA-G1`** | *Plain: every map we could build still fits the machine the app runs on, so size is not what decides this.* The decision then rests on `LBA-M2`, `LBA-M3` and `LBA-M4` alone, and the report says so | complete **and** sized |
| **`LBA-R2`** | **`LBA-G1` fires on some arms and not others** | *Plain: some of these maps would need a bigger machine or a faster router before they could ship, and the report names which and on which half.* **The hosting requirement is a cost, not a disqualification** — whether to pay it is the owner's. The arms below the bar are reported unchanged beside them | complete **and** sized |
| **`LBA-R3`** | **`LBA-G1` fires on every arm above `V`** | *Plain: any map bigger than the one we serve today would need the hosting to change.* The population question then **is** a hosting question, and `LBA-M5`'s operating cost is read beside it. This does not say the change is not worth making | complete **and** sized |
| **`LBA-R4`** | **on the `P` row, and on the `U` row with `LBA-X6` beside it**: the three thresholds **do not separate** — neither `LBA-A5` nor `LBA-A6` moves `LBD-G2`'s bar on `LBA-M3` against `LBA-A4`, the absent shares lie within a point of each other, and `LBA-M1` does not fire `LBA-G1` differently across them | *Plain: how much listening evidence we demand barely changes the map, once the population is fixed.* **The threshold is then not the decision** and the report says so plainly. ⚠ **This is not evidence that the thresholds sound alike** — that is `REQ-38`'s question and no listen has been run (`LBA-D3`); `REQ-41` bars reading any absence of difference as equivalence | complete |
| **`LBA-R4-V`** *(added 2026-09-14, `LBA-AM1`, finding `LBA-AM1-A4`)* | **the `V` row is excluded from `LBA-R4` and its outcome is stated here instead**, because two of that read's three clauses are already settled on the committed record and the third cannot fire at all | *Plain: on today's artists, we already know from work that is finished what the strength bar does to the map, and one of the three things `LBA-R4` looks at could never have told us anything.* **(i) The `LBA-M3` clause is UNFIREABLE** — the statistic is 1.0 for all three `V` arms by construction, so every threshold difference on it is identically zero and the null carries no information (`LBA-M3`'s block; the `CRS-C3` shape). **(ii) The absent-share clause is ALREADY RESOLVED and resolved AGAINST the read**: the two committed `V`-row arms' absent counts are owned by the served-population README's §3, and their difference as a share of `V` is **larger than one percentage point**, so `LBA-R4`'s "within a point" condition fails on this row before anything is run. **(iii) Only the `LBA-M1` clause is live**, and §4's block records that it measures the threshold with far less dynamic range than the population. **Consequence: no `LBA-R4`-shaped conclusion may be drawn about the `V` row**, and the `V` row's threshold evidence is the arm-to-arm `LBA-M2` comparison and nothing else | derived — **(ii) is already true on the committed record and is stated here, before stage 1, so that it cannot later be reported as a finding of this design** |
| **`LBA-R5`** | within a population rule, the thresholds **do** separate | *Plain: how much listening evidence we demand visibly changes the map.* The report gives the three cells side by side with their plain sentences and **names no preferred value** — `LBA-D2` reserves that to the owner at the stop | complete |
| **`LBA-R6`** | the population rules separate on `LBA-M3` but **not** on `LBA-M2`'s materially-changed share | *Plain: a bigger population reaches the artists that arrive unconnected without much disturbing the journeys between the artists the app already has.* **`LBA-X6` travels with the first half** — over `V` the added-set figure is 1.0 by construction, so this read is about the `P`-versus-`U` contrast and never about `V` | complete |
| **`LBA-R7`** | the population rules separate on **both** | *Plain: a bigger population reaches the unconnected artists and also substantially rearranges who we show as similar to the artists you already see.* **Both halves are reported by fame band**, because the trade may fall differently at the two ends, and `LBA-X4`/`LBA-X5` travel with the second half | complete |
| **`LBA-R8`** | an arm's map is materially larger than today's **and** a large share of the artists it adds fall in the un-listenable class (`LBA-G4` fires) | *Plain: this rule adds a lot of artists, and a lot of the ones it adds are artists we probably cannot play.* `LBA-M3`'s figure for that arm is reported **twice**, measured and discounted. **`LBA-X2`'s two bounds travel with it**: the census over-drops relative to how the app resolves clips, and the carried verdicts are unmeasured. **A minimum-degree floor above 1, or a re-censused filter, are the two candidate responses and neither is proposed here** — each is its own amendment | complete **and** censused |
| **`LBA-R9`** | **the numbers say no** — for every arm, either `LBA-G1` fires, or the arm changes what the app serves substantially (`LBA-M2`) while adding little the app can play (`LBA-M3` discounted by `LBA-M4`) | *Plain: none of the maps we could build is both servable and clearly better than what we have.* **Stopping the `LBD-` track here is a complete outcome, not an abandonment** — the supply question is answered at the table level, at the map level and at the ear twice, and the listen-2 findings note's §6 says so. **No session proposes what follows** | complete, sized **and** censused |

**Nothing in this table is reachable before its run state**, and a partial run licenses no read.
In particular **`LBA-R4` and `LBA-R5`–`LBA-R9` all presuppose `complete`** (`LBA-R4-V` is the one exception, and it presupposes only `derived`, because two of its three clauses are settled on the committed record and the third cannot fire) — every cell either built or stopped
on `LBA-G2`'s stated bar with the bar recorded. A lattice reduced by judgement rather than by that
gate does not reach `complete`, and none of these reads may be taken on it.

**Every result reaches the owner in `CLAUDE.md`'s four parts, in order:** measured (tables, no
adjectives); what the session infers, labelled as inference and in plain language a person who
does not know what Jaccard measures can disagree with; the weakest link and what would falsify it;
options and consequences. **Each identifier is given with its plain sentence**, never bare.

---

## §8 — What "go" commits to

**Stated now so that "go" is a decision about a known thing, not an opening of an unbounded one.**
None of it runs before the stop.

1. **A candidate build** at the chosen threshold and population rule, with **fame attached** (the
   `fame` stage over that population — `LBD-D4`'s only admissible source, and a real fetch whose
   cost `LBA-M5`(2) estimated) and **clip and streaming ids attached** (`deezer_ids.py`,
   `dsp_links.py`, `artist_facts.py`). This is the first build in the whole track that is a
   candidate for serving; every build before it pinned `require_fame=False` and was an
   experimental control (`LBD-D7`).
2. **Acceptance criteria, never widened from `PRODUCTION_ACCEPTANCE`'s intent.** The intent is
   written in `acceptance.py`'s own comments and is quoted here as the rule, not paraphrased as a
   sentiment: the tolerance stays at about **±20 %**; only the bounds that actually fail are
   moved; the new centre is derived from something known **independently of the build that went
   red**; and sensitivity is checked against the four known artifacts the module names, with the
   **edge floor preserved**, because it is the only bound that can see a silent cap-rule revert.
   ⚠ **Recalibrating a bound so a NEW artifact can be adopted is risk acceptance and is the
   owner's** — his ruling of 2026-09-05, recorded in the `LUX-4` execution log, which also records
   a session getting that distinction wrong in both directions on one day. A candidate at any
   population above `V` will breach the node bound by construction; **that breach is a decision,
   not a bug, and it is his.**
3. **Manifest pinning**, §6 steps 5, 9 and 10 — the archive `MANIFEST.json`, the artifact sidecar
   through `build_manifest`/`write_manifest`, and `ARTISTPATH_GRAPH_SHA256` taken from the sidecar
   so a wrong artifact refuses to boot (`DEP-24`).

> ### ⚠ `LBA-AM4` INSERTS A STAGE HERE — between item 3 and item 4, dated 2026-09-21
>
> **`LBA-G5`, the unblinded use gate.** The owner uses the candidate locally for a bounded period
> against a pass/fail criterion he wrote before seeing a single journey. It is a **stop-gate, not
> a quality bar**, and it is **not** the `REQ-38` listen below and does not replace it. Failing it
> means the candidate is never listened to. Passing it licenses **nothing except proceeding to
> item 4**. Full text, his criterion verbatim, and the four bars: §11 `LBA-AM4`.
>
> **The numbering of items 1–4 is deliberately unchanged**, so that every document written before
> 2026-09-21 that says *"§8's four items"* still resolves. §8 now has **five stages**; item 4 is
> still item 4.

> ### ⚠ `LBA-AM5` REVERSES THE ORDER OF THE TWO STAGES BELOW — dated 2026-09-22
>
> **Item 4, the blind listen, runs FIRST; `LBA-G5`, the use gate, runs SECOND.** Running the gate
> first would have had the listen's one listener using the candidate knowingly for up to two days
> immediately before a run-once blind listen. The box above is `LBA-AM4`'s and is left as written;
> the order it implies is superseded. Reasoning, and the gate's pair log: §11 `LBA-AM5`.
>
> **Item 4's design is `LBA-AM6`** (§11), written cold on 2026-09-22 before any journey existed.
4. **Then the `REQ-38` blind listen: today's map against the candidate, on today's artists** — the
   shape the owner can judge, and the only evidence class this project treats as primary.
   **Designed cold, as a separate amendment to this document, written when no journey exists on
   either map** (`LBA-D3`). What that amendment owes, named now so it cannot be quietly narrowed:
   a pair draw whose rule is committed before it runs; a generation gate; the reads fixed before
   any journey exists; and **`GBL-` §5's run-once rule**, which already binds both existing `LBL-`
   verdicts and will bind that one. **Neither existing verdict may be re-listened, and no verdict
   carries across listens.**

---

## §9 — Barred reads, carried forward

Every one of these is inherited, not invented here, and each is barred **whatever this
pre-registration measures.**

- **No equivalence from either listen tie.** `REQ-41`: *"no difference"* in unfamiliar territory
  is **uninformative**, not evidence of equivalence. Both `LBL-` listens read `LBL-R2`, the tie;
  *"our recomputation passed"* and *"it failed"* are **both** barred, for both listens.
- **No verdict across listens.** Listen 2 says nothing about `LBD-A5V` against the served map.
  `GBL-` §5 makes both verdicts run-once; neither may be re-listened on any protocol.
- **No attribution inside the data bundle** (`LBD-X5` / `LBA-X4`). No sentence credits or blames
  the corpus age, the absent `filter_True` stage, today's mapping, the band-member class or our
  tie-break individually.
- **`LBD-X4` / `LBA-X5` travels with every comparison against today's map.** Artists took part in
  the served build's cap step that no arm here can include.
- **`LBD-X6` stands: nothing generalises to the cheaper pairing form.** Its condition was
  discharged on 2026-09-13 and `R10` **fired**, which confirmed the bar rather than releasing it.
  **Reading the met condition as a lifted bar inverts the result.** `LBA-D1` makes the point moot
  for these arms — all nine use ListenBrainz's own pairing — and it does **not** license a sentence
  about the cheaper form.
- **`LBD-C1` is never cited as passed**, for `LBD-A0` or for `LBD-A4`. `LBD-G1` fired on both;
  `LBD-AM3`'s override enumerates `LBD-A0`–`LBD-A3` and does not name `LBD-A4`, and whether it
  extends to that arm as an **absolute** fidelity statement is the owner's and is open. **Every
  arm here inherits whatever the reimplementation gets wrong that the synthetic sub-check cannot
  see**, and that sentence appears in the results document.
- **Nothing here re-reads any `LBD-` criterion.** `LBD-C1`, `LBD-C2a`, `LBD-C2b`, `LBD-C3`,
  `LBD-M1`, `LBD-G1`–`LBD-G4` and `R1`–`R12` are read exactly as they were read, in the documents
  that own them. `LBA-M3` uses `LBD-C2b`'s **statistic** and `LBD-G2`'s **bar** over a new set of
  arms; that is a new measurement in an old currency, not a re-read.
- **`LBD-C2a`, `LBD-C2b` and `LBD-M1` were deliberately not taken on `LBD-A4`**, and taking one now
  needs an amendment to *that* document first. Nothing here takes one.
- **No routing or path-quality claim beyond `LBA-M1`'s d0 query cost**, which measures *what it
  costs to serve a query*, never *whether the answer is good*. A denser map is not a better journey
  until a listener says so (`REQ-38`), and `LBA-D3` bars designing that listen before the stop.
- **`V` and `P` remain experimental controls in every document that used them as such.** Their
  appearance here as candidate **population rules** is a new use in a new document and changes
  nothing about how `LBD-AM4`, `LBD-AM5` or either listen may be read.

---

## §10 — Claims check

**Every function, file, config value and figures-owning document this pre-registration names,
resolved 2026-09-14 against the working tree at `origin/main` (`1e3a81f`).** Anything not
resolved is marked *not-yet-built* with the dependency stated, or *stale*.

**Shipped code — all RESOLVED.**

| named | where | status |
|---|---|---|
| `find_journey` | `api/src/artistpath_api/pathfinding.py:194` | resolved |
| the fame-ramp guard `ramp_fame` / `ramp_fame_on` | `api/src/artistpath_api/pathfinding.py:130-132`, applied at `:170` | resolved — and it is the claim `LBA-D5`'s block rests on, read from source rather than from any document |
| `ApiConfig.w_known_ramp_fame_pctl` | `api/src/artistpath_api/config.py:108` | resolved |
| `ApiConfig.graph_path`, `ApiConfig.graph_sha256` | `api/src/artistpath_api/config.py:49,56` | resolved |
| `GraphStore`, `GraphStore.fame_percentiles` | `api/src/artistpath_api/graph_store.py` (dataclass; `:141`) | resolved |
| `build_from_archive` | `builder/src/artistpath_builder/pipeline.py:169` | resolved |
| `serialise` | `builder/src/artistpath_builder/artifact.py:87` | resolved |
| `check_acceptance`, `PRODUCTION_ACCEPTANCE`, `AcceptanceCriteria` | `builder/src/artistpath_builder/acceptance.py:259`, `:118`, `:54` | resolved |
| `build_manifest`, `write_manifest`, `resolve_build_inputs`, `log_build_inputs` | `builder/src/artistpath_builder/manifest.py:147,176,67,133` | resolved |
| `PopulationNotCensused`, `load_unlistenable_list` | `builder/src/artistpath_builder/unlistenable_drop.py:132,151` | resolved |
| `fetch_fame`, `load_fame`, `lb_fame_fetcher`, `MAX_PER_REQUEST` | `builder/src/artistpath_builder/fame.py:107,198,226,57` | resolved |
| `BuilderConfig.requests_per_second`, `.request_delay_seconds` | `builder/src/artistpath_builder/config.py:74,289-290` | resolved |
| `cmd_fame` | `builder/src/artistpath_builder/cli.py:196` | resolved |
| `deezer_ids.py`, `dsp_links.py`, `artist_facts.py` | `builder/src/artistpath_builder/` | resolved |
| `trimmed_union_cap` — the rule that enforces `degree ≤ degree_ceiling` | `builder/src/artistpath_builder/graph.py` | resolved — it is what bounds every arm's size and makes `LBA-M1`'s dynamic-range derivation possible |
| `serialise`'s four mandatory metadata keys, and the five additive keys omitted when empty | `builder/src/artistpath_builder/artifact.py` | resolved — `LBA-M1`'s bytes definition rests on this split, and the size expression was checked against three committed artifacts byte-for-byte on 2026-09-14 |
| `graph-lux4.bin` and its sidecar — `LBA-G1`(a)'s `metadata_ratio` calibration pair | `builder/scratch/` (gitignored; identity is its sidecar's sha256 `fd92a735…`) | resolved on this machine — **identical in artist count and CSR entries to `graph-msw-tu50.bin`**, verified against both sidecars 2026-09-14, which is what makes the pair a valid isolation of the metadata term |
| App Runner `min_size=1`, `max_size=2`, `cpu="1 vCPU"`, `memory="2 GB"` | `infra/src/artistpath_infra/stack.py:199-200,268-273` | resolved |
| the drop-list payloads `unlistenable_drop_algb_20260805.json`, `…20260809.json`, `no_release_drop_algb_20260802.json`, `featured_credit_drop_algb_20260803_am1.json` | `builder/src/artistpath_builder/data/` | resolved |

**Research scripts to be run unedited — all RESOLVED.**

| named | where |
|---|---|
| `lbd_derive.py` | `builder/analysis/2026-09-08-lbd-similarity/` |
| `emit_archive.py`, `lbd_build_census.py`, `lbd_c2b_compare.py`, `lbd_population_coverage.py`, `lbd_source.py` | `builder/analysis/2026-09-10-lbd-supply/` |
| `lbv_build.py`, `lbv_emit.py`, `lbv_derive_a5.py`, `lbv_coverage.py` | `builder/analysis/2026-09-10-lbd-served-population/` |
| `ulf_census.py` (offline half), `ulf_clips.py` (network half, **not run here**), `ulf_droplist.py` | `builder/analysis/2026-08-05-ulf-census/`, with the 2026-08-09 forward copies in `builder/analysis/2026-08-09-cex-recensus/` |
| `jfx_route.py`, `cre_ladder.py` | `builder/analysis/2026-08-09-jfx-prereg-critique/`, `builder/analysis/2026-08-03-cap-reevaluation/` — named as the routing-harness precedents only; **neither is run here** |

**Figures-owning documents — all RESOLVED, all cited by section and never restated.**

`builder/analysis/2026-09-08-lbd-similarity/README.md` (§4 cost, §5–5c fidelity and the diagnosis,
§6 `LBD-C2a`, §6c the threshold curve) · `builder/analysis/2026-09-10-lbd-supply/README.md` (§0–§5)
· `builder/analysis/2026-09-10-lbd-served-population/README.md` (§0–§6) ·
`builder/analysis/2026-09-13-lbd-a4/README.md` (§§4–8) · `builder/analysis/2026-09-07-lbd-inputs/README.md`
(§1 the dump and the frames) · `builder/analysis/2026-09-05-lux-e1-drift-source/README.md` (§6.2,
§6.3 — `ULC-F4`) · `builder/analysis/2026-08-05-ulf-census/ulf_census.json` and
`builder/analysis/2026-08-09-cex-recensus/ulf_census.json` (the class and carry counts) ·
`docs/superpowers/2026-08-09-cex-task11-execution-log.md` §6 (the census and fame wall clocks, and
the release dump's real size) · `docs/superpowers/findings/2026-07-27-gate2-gate3-team-review.md`
(§1, §5 and the live-calibration section) ·
`docs/superpowers/findings/2026-07-30-track-b-cap-selection-results.md` §1 (the ceiling's measured
cost) · `docs/superpowers/findings/2026-09-13-lbd-adoption-inputs.md` ·
`docs/superpowers/findings/2026-09-11-lbl-listen1-results.md` and
`…/2026-09-13-lbl-listen2-results.md` (§0 and §5 of each).

**Gitignored artifacts this document pins by sha256 rather than by path — NOT VERIFIABLE FROM
GIT, and verified by the executing session before use.** `T.parquet` `03d47b05…`,
`T_A4.parquet` `e919bc89…` (named only to be excluded), `A0.parquet` `f9bd1f83…`,
`A5.parquet` `f34cd889…`, `LBD-A0V.bin` `494c53d5…`, `LBD-A5V.bin` `2d34746e…`,
`graph-msw-tu50.bin` `43dd82bb…`, `graph-cxa-adopted.bin` `bc0431c4…`,
`population_msw_mbids.txt` `b5e0cb94…`, `population_cxa_mbids.txt` `1bbff8fc…`,
`cxr_added_mbids.txt` `bfed95ef…`, `cxr_preexisting_mbids.txt` `768054b7…`,
`cxr_residual_mbids.txt` `fa8d85cc…`. **Their identity is the checksum; `builder/scratch/` and
`C:\unsung-fast\` are gitignored and a fresh clone has none of them.**

**NOT-YET-BUILT, with the dependency stated.**

- **The `U` populations do not exist as files.** No document on the record states how many artists
  the full pair table names: `LBD-M1` was explicitly **not** taken at the table level (the
  similarity README's §6b says so in those words), and the two build READMEs count only within `P`
  and `V`. **Stage 1 produces them**, and this pre-registration states no figure for them.
- **A threshold-7 derivation does not exist.** It is one filter and window over `T` by
  `lbd_derive.py` unedited; §6c carries a *descriptive* cell at that threshold but no arm.
- **The census coverage store's current membership** is `builder/analysis/census-coverage/ulf_coverage.json`,
  which the census scripts read **and write**; it is active data, not a frozen output, so its state
  at run time is whatever the last census left and stage 3 records it before and after.
- **Peak-RSS instrumentation in the build wrapper does not exist** (`LBA-AM1`, finding `LBA-AM1-A3`). No
  build on the record reports a memory figure — checked across both build READMEs and every
  committed JSON beside them on 2026-09-14 — so **`LBA-G2` cannot be evaluated until stage 2 adds
  it.** A few lines in `lbv_build.py`'s shape; named here rather than discovered at the gate.
- **`framework_rss` has never been measured in this project** (`LBA-AM1`, finding `LBA-AM1-A2`), so
  **`LBA-G1`(a) is not evaluable until it is.** One measurement on the served artifact, before
  stage 2 reads the gate.
- **The served map's local median d0 is on no document.** `LBA-M1`'s query-cost half produces it
  as one of the two numbers its own ratio is built from, so the gate supplies its own calibration
  — but nothing on the record states it today, and `LBA-G1`(b)'s narrative no longer assumes it.
- **The `LBA-M1` query-cost pair set** is drawn in stage 2, after the built arms are known — the
  drawing rule is fixed in `LBA-M1` and the file is sha-pinned before any timing is taken.

**One thing this document deliberately does not assert.** Whether a `U` population is a sensible
thing to ship at all — the corpus names artists no crawl of ours ever discovered, and nothing on
the record says how many of them anyone would want to meet on a card. **`LBA-M4` sizes the
playability half of that question and no measurement here touches the rest of it.** It is a product
judgment, it is the owner's, and §7 gives it to him with the numbers rather than a recommendation.

---

## §11 — Amendments to THIS document, made after it was committed

> ### 📍 STATUS MARKER — added 2026-09-16, and it changes nothing above it
>
> **`LBA-D8` is fully executed.** Stage 1 (derive and count, 2026-09-14), stage 2 (emit, build and
> size, 2026-09-15) and stage 3 (`LBA-M2`–`M5`, the reads, the report, 2026-09-16) have all run.
> Figures are owned by the three stage READMEs under `builder/analysis/`; **this document owns no
> figures and none is added here.**
>
> **Gate outcomes, including the failures:** `LBA-G3` **FIRED** at stage 1 — no census pass was
> started and none is owed. `LBA-G2` **FIRED** on `LBA-A9` at stage 2 — *unbuilt for a resource
> reason*, with §2.6's three barred conclusions attached. `LBA-G1` fired on **nothing**, across the
> **eight sized** arms. `LBA-G4` is **reported unreadable** on every arm where it is evaluable,
> under `LBA-AM3-2`'s disqualifier, and `n/a` on the `V` row.
>
> **Reads taken:** `LBA-R0` and `LBA-R1` (stage 2); `LBA-R5` on the `P` and `U` rows (stage 3).
> `LBA-R4` does not read on either row. `LBA-R4-V` is restated, never reported as a finding.
> **`LBA-R6`/`LBA-R7` are not adjudicable by this design** — they differ only on a half for which
> neither they nor `LBA-M2` carries an effect size, and §4 fixes `LBA-M2` as descriptive on
> purpose. **`LBA-R8` and `LBA-R9` are formally UNREACHABLE** (`LBA-AM3-1`).
>
> **The go/no-go stop is reached and is the owner's.** No arm is selected, no threshold preferred,
> no route recommended; `LBA-D2` stands. **If he says go, §8 is what that commits to**, and the
> `REQ-38` listen is designed cold as a later amendment (`LBA-D3`).
>
> ⚠ **One discrepancy found at the stage-3 closeout and deliberately NOT fixed here.** §5 writes
> `LBA-G2`'s bar as **24 GB**; the instrument implements **24 GiB**. **No cell's disposition
> changes under either reading.** §11's own rule is that a bar's value is never edited, and
> settling this after the results exist would be changing a bar with results in hand. It is filed
> in `NEXT.md`'s deferral registry as the owner's.

**Every entry is dated and numbered, and is added beside the text it qualifies — never as a silent
edit to it.** The commit timestamp is what makes the register worth having, exactly as it is for
the document itself.

**The rule that governs every entry here:** a bar's *value* is never edited. If a later session
finds one inconvenient, the answer is an amendment with its own reasoning and its own date, and it
states plainly whether a result already existed when it was written and which criterion's
commit-before-results property it therefore spends. That property is the whole point of the
document.

---

### `LBA-AM1` — the `ml-graph-analyst` critique, and the twelve changes it produced

**Dated 2026-09-14. NOTHING HAD RUN AT THE TIME THIS WAS WRITTEN** — no arm derived, no archive
emitted, no graph built, no census run, no listen designed. **The document's commit-before-results
property is fully intact and this amendment spends none of it.** That is why the changes below are
made **in place** rather than as notes beside the original text: there is no result any of them
could have been reshaped to fit, and the register entry is what records that. **It is also why the
original wording of each changed clause is quoted here** — the record of *why a definition is what
it is* is the part that matters to a later reader, and it is the part a silent edit destroys.

**Why it was run.** The owner commissioned one derivation-only critique of the measurement design
before the PR merged and before anything was executed, on four questions and no judgement question:
degeneracy and discriminating power; the exact behaviour of the "materially different neighbour
list" statistic under three separate causes; population invariance and whether the stated controls
isolate the arm's effect; and whether the effect sizes are in the statistic's own currency and every
baseline genuinely one column away. The analyst was explicitly barred from being asked which arm
should ship or how the owner should rule, and was not asked.

**What the critique is, and what it is not.** It is a derivation over the committed record and the
shipped code, plus three instrument probes on artifacts that already existed. **It read no arm of
this document** — the analyst records declining to compute `LBA-M2`'s numerator on the two reused
maps, on the grounds that doing so would spend the commit-before-results property for two of nine
cells, and that decision is endorsed here. **Its figures are its own** and are cited, never restated
as this document's.

**Verified before acting, not taken on trust.** Four load-bearing claims were checked independently
against source before any change was made: the two calibration artifacts are identical in artist
count and CSR entries and differ only in the three `LUX-4` keys (both sidecars, and the files);
**neither build README nor any committed JSON beside them records a peak-memory figure**, so
`LBA-G2`'s stated extrapolation basis genuinely did not exist; `w_degree_hub` is `0.0`
(`api/…/config.py:83`), so §2.3's reasoning about the saturation-degenerate top-1 %-by-degree set holds
unchanged; and the APG1 size expression reproduces three committed artifacts byte-for-byte, which is
what makes `LBA-M1`'s new bytes definition computable without a rebuild.

> ### ⚠ The findings were numbered `A1`–`A12` bare, and that was itself a collision
>
> **Caught by `docs-lint` check 5 on 2026-09-14, in this very entry.** The analyst numbered its
> findings `A1`–`A12`; written into this document as bare tokens they collided with **Track 2's
> `A1`–`A7`, which are simultaneously factorial arms and amendment IDs** — the exact collision
> `CLAUDE.md` records as having cost a session the rule that governed it, and which this
> document's own header says it namespaces deliberately to avoid. The lint named seven other
> documents already minting the same bare tokens.
>
> **They are now `LBA-AM1-A1`–`LBA-AM1-A12`, and the observations `LBA-AM1-O1`–`LBA-AM1-O4`**,
> collision-checked across every ref: free. The numbering still matches the critique's own, so a
> reader holding the analyst's report can map each finding one-to-one.
>
> **It is recorded rather than quietly fixed** because of where it happened: inside the register
> entry whose subject is measurement discipline, written by a session that had checked the
> `LBA-` series across every ref a few hours earlier. **Collision discipline does not transfer
> from a series to the identifiers a later section mints inside it**, and a mechanical check is
> what caught it, not a careful reading.

#### The changes, each with the finding that produced it

| # | what changed | the finding |
|---|---|---|
| **`LBA-AM1-A1`** | **`LBA-M2`'s gated statistic: Jaccard < 0.5 → retention `c/|A|` < 0.5.** The plain sentence is unchanged in meaning and now matches the value | *"Jaccard below 0.5"* and *"fewer than half the artists we show are the same"* are **different statistics**: at equal list lengths a Jaccard of 0.5 means a third of the list changed, and the sentence's own condition is a Jaccard of 1/3. They disagreed **at authoring time**, which `CLAUDE.md`'s fix-the-sentence-beside-the-value rule exists to surface |
| **`LBA-AM1-A6`** | **Four raw quantities recorded per artist and five shares reported per arm**, including `R_avail`, the `b_out` share, the **forced share** as a null model, and the denominator both ways | Jaccard is bounded by the ratio of the two list lengths, so the original's *"both lists are capped at 50, so the two sets are of comparable size"* **does not follow — a ceiling bounds the maximum, not the spread.** A large share of artists would have been flagged with zero contribution from neighbour identity, and the rate would have been reported **with no null model** |
| **`LBA-AM1-A7`** | **An arm-to-arm `LBA-M2` comparison within each population row**, plus `overlap@10` as an ungated rank companion | Three causes lower any one-scalar overlap measure and no scalar separates them; the arm-to-arm form removes the population cause and the `LBA-X4` bundle **by construction**, and a pure re-ranking is invisible to every membership statistic |
| **`LBA-AM1-A4`** | **`LBA-R4` is scoped to the `P` and `U` rows; the new `LBA-R4-V` states the `V` row's position instead** | Two of `LBA-R4`'s three clauses were dead on the `V` row: `LBA-M3` is **unfireable** there by construction (the `CRS-C3` shape), and the absent-share clause is **already resolved against the read** by the committed record. A read partly settled before it is written must say so |
| **`LBA-AM1-A9`** | **`LBD-G2`'s bar: admissible as a one-column threshold read on `LBA-A5` and `LBA-A6` only**; on the `U` row it is computed and reported but never read as a one-column attribution | `LBA-M3`'s *"within a population rule"* and `LBA-X6`'s *"the population is a dependent variable"* **conflicted**, and an executing session would have had to resolve it with results in hand |
| **`LBA-AM1-A10`** | **A fourth descriptive stratum, `nodes(arm) − V`**, derived per arm | All three pinned strata are subsets of the extended crawl's population, so **none could see the artists a `U` rule adds beyond it** — the only thing `LBA-A7`–`A9` exist to test |
| **`LBA-AM1-A8`** | **A `drop filter` column in §2.1, and four baselines restated as two columns** | §2.4 derived the hazard but the **baseline column** did not carry it, and the baseline column is what a later reader reads. `CLAUDE.md`: a disclaimer nothing later reads is not a control |
| **`LBA-AM1-A2`** | **`LBA-G1`(a): 1.4 GB of a census build → 1.6 GB of a projected shipped build**, with `metadata_ratio` and `framework_rss` as measured inputs | The original deducted one flat 30 % to cover interpreter, framework, clip cache **and** the metadata a census build omits — four terms that scale differently. The metadata term alone was measured at nearly double the resident cost while adding about a third to bytes, so the bar was loose in the direction that admits an unbootable arm |
| **`LBA-AM1-A3`** | **`LBA-G2`: peak RSS instrumented in the stage-2 build wrapper, builds ordered by ascending neighbour rows, the unit labelled** | **The stated extrapolation basis does not exist** — no build on the record reports memory, wall clock is not a proxy for it, and there are four such builds not three. The unit slip between archive neighbour rows and CSR entries is the one the served-population README records a refused build for |
| **`LBA-AM1-A11`** | **`LBA-G3` moved from a stage-3 wall-clock stop to a stage-1 projection** | The cost driver is the count of union members absent from the coverage store, which stage 1 produces for free. As written the gate was discovered six hours into the pass |
| **`LBA-AM1-A5`** | **`LBA-G4`: baseline moved inside the arm** (added-beyond-`V` against kept-from-`V`, same pass and dump), and **`n/a` rather than `0` on the `V` row** | The original baseline was two or three columns away — different population, different dump, whole-population share against added-subset share. And the gate's subject is empty on a `V` arm, so its value is a share of nothing; printing `0` would read as *perfectly playable* |
| **`LBA-AM1-A12`** | **`LBA-M1`'s bytes: "the serialised census build" → the bare-artifact size**, computed identically for all nine arms by decoding | **No census build of `LBA-A1` or `LBA-A3` was ever serialised.** Their only artifacts carry all five additive keys, so seven arms would have been compared against two that were about a third larger for a reason that is not the arm — and `LBA-D9` forbids rebuilding them |

#### Observations recorded, which changed no value

- **`LBA-AM1-O1` — `LBA-G1` is in practice a population gate.** The cap rule bounds every arm's size by
  its population, so `LBA-M1` measures the population column with far more dynamic range than the
  threshold column. Recorded in `LBA-M1`; the statistic is **not** degenerate and no bar moved.
- **`LBA-AM1-O2` — `LBA-M5` adds no arm-discriminating information beyond `LBA-M1`'s artist count.**
  Three of its four parts are identical across all nine arms. Recorded as a bar on how it may be
  read.
- **`LBA-AM1-O3` — an internal contradiction**, corrected: `LBA-M5`(1)'s *"this pass and nothing else"*
  and §6's ⚠ about steps 6 and 7 could not both be right for any arm above `V`. `LBA-M5`(1) is now
  scoped to the served population.
- **`LBA-AM1-O4` — `LBA-G1`(b)'s narrative overstated what follows.** The four-second live figure
  requires the served map's local median d0, which no document states. The gate's **ratio** is
  unchanged and sound; its justification now says what is measured and what is not, and the missing
  quantity turns out to be one the gate measures itself.
- **§2.3's `w_degree_hub` and rescale reasoning was checked and holds.** `w_degree_hub = 0.0` keeps
  the saturation-degenerate top-1 %-by-degree set out of the router, and the cap's unclipped ranking
  makes degree reads rescale-independent. **One case it does not cover, now named:** `LBA-M1`'s
  query cost is neither a degree read nor a membership read, and the p99 rescale recomputes per map,
  so an arm-to-arm wall-clock difference is not attributable to size alone.
- **The distinct-listener arithmetic in §2.1 was re-derived and is correct**, including the warning
  that an arm at threshold 5 would have been a dead arm.

#### What this amendment does NOT do

- **It changes no arm, no population rule and no threshold.** The 3 × 3 lattice is exactly as it was.
- **It relaxes nothing.** Every bar it moves, it moves toward being harder to satisfy or toward being
  evaluable at all; `LBA-G1`(a) is the only numeric bar to change and it is now applied to a larger
  projected quantity.
- **It does not reopen the owner's three rulings** (`LBA-D1`–`D3`), and the analyst was not asked
  about them.
- **It adopts nothing, changes no default, and touches no shipped code.** The critique named one
  instrument that does not exist — peak-RSS recording in the build wrapper — and that is stage-2
  work, not a change made here.
- **It leaves two quantities explicitly unmeasured**, named so they are not discovered later:
  `framework_rss`, without which `LBA-G1`(a) is not evaluable, and the served map's local median
  d0, which `LBA-M1` now supplies as a by-product of its own comparison.

**Identifier `LBA-AM1`.** Collision-checked across every ref on 2026-09-14 together with the rest of
the `LBA-` series: free.

---

### `LBA-AM2` — how `LBA-G2`'s first projection is obtained, and which stage-2 order governs

**Dated 2026-09-14, written at the stage-1 seam.**

> ### ⚠ What existed when this was written, stated plainly — it is NOT the `LBA-AM1` position
>
> **`LBA-AM1` could say "nothing had run". This amendment cannot, and the difference is
> load-bearing.** `LBA-D8` **stage 1 has been executed**: all nine cells are derived and counted,
> and the author of this amendment **knows every cell's archive-neighbour-row count** — which is
> precisely `LBA-G2`'s x-axis. Figures are owned by
> [`builder/analysis/2026-09-14-lbd-s4-stage1/README.md`](../../../builder/analysis/2026-09-14-lbd-s4-stage1/README.md).
>
> **What does NOT exist is `LBA-G2`'s y-axis.** No cell has been emitted or built, no peak RSS has
> been measured, and the instrument that would measure one is not yet written. **So there is no
> value of the gate's statistic for any arm, and this amendment cannot have been shaped to admit or
> exclude a cell** — nothing has been projected.
>
> **The honest statement of what it spends:** it spends none of `LBA-G2`'s commit-before-results
> property, because no build result exists. It is **not** written in ignorance of the cells' sizes,
> and a reader weighing it should know that the ordering rule it settles was chosen by an author who
> could already see which cells are large. The resolution below is therefore argued from the two
> committed passages and from `LBD-AM5`'s completed builds, **not** from which cells it would be
> convenient to reach — and it **stops no cell and reduces nothing**.

**The conflict.** Three committed passages cannot all be acted on as written.

1. **§3, `LBA-D8` stage 1:** *"This is the only measurement that can rule a cell out on resources
   before any of it is spent, and **both `LBA-G2` and `LBA-G3` read off it**."* And §7's `LBA-R0`
   gives the run state `derived`.
2. **§5, `LBA-G2`'s firing clause:** *"projected from a fit over **every build already instrumented
   in this stage**"* — stage 2 — and its derivation: *"**Stage 2 builds in ascending order of
   archive neighbour rows** ... A cell is stopped when its projection from **all** instrumented
   builds so far exceeds 24 GB."*
3. **§10:** *"**`LBA-G2` cannot be evaluated until stage 2 adds it**"* — the peak-RSS
   instrumentation.

And a second conflict inside the same pair: **§3 `LBA-D8` fixes the stage-2 order as `A1`, `A4`,
`A7`, `A2`, `A5`, `A8`, `A3`, `A6`, `A9`** *("control first, then each threshold across all three
population rules, so that a partial run always holds a complete one-column comparison")*, while
**§5 requires ascending archive-neighbour-row order**. With stage 1's counts in hand these are
**not the same order** and the difference is material: under `LBA-D8`'s order the second cell built
is `LBA-A7`, whose archive is **about twice** the first built cell's, so its projection would be a
2× extrapolation from a **single** instrumented point — which cannot even define a fit with an
intercept. §5's ordering rule exists to prevent exactly that.

#### The resolution

**(a) `LBA-G2` is read progressively during stage 2; stage 1 supplies only the x-axis.** §5 and §10
govern the mechanism, and they are specific where `LBA-D8`'s one clause is loose. `LBA-D8`'s
sentence is read as: stage 1 produces the **input** to both gates. That is true of `LBA-G3`, which
`LBA-AM1-A11` moved to stage 1 outright and which **has now been read there**, and it is true of
`LBA-G2` in the weaker sense that its x-axis — every cell's archive neighbour rows — is a stage-1
product. **§7's `LBA-R0` is correspondingly read as reachable only once stage 2 has begun**, not at
the close of stage 1.

**(b) The first build is not evaluable by `LBA-G2`, and proceeds unconditionally.** With zero
instrumented builds there is no fit, and the gate is silent rather than permissive. **It is not an
unguarded step:** under (c) the first built cell is the smallest, and its archive lies **between the
two archives `LBD-AM5` already built successfully on this machine** (`LBD-A0V`'s and `LBD-A5V`'s —
the served-population README §2 owns both counts). So the first build is an interpolation in
archive size between two completed builds, even though neither recorded a peak RSS. Its measured
peak RSS becomes the first instrumented point.

**(c) Stage 2 builds in ascending archive-neighbour-row order — §5's rule governs the sequence.**
**And this costs `LBA-D8`'s stated rationale nothing; it improves on it.** `LBA-D8`'s order was
written as though the control had to be built. It does not: `LBA-A1` and `LBA-A3` are **reused**
(`LBA-D9`) and both already exist, and both sit on the `V` row. So under ascending order **the
complete `V` row exists after the first build**, and the complete `P` row — which carries the only
two one-column threshold reads `LBA-AM1-A9` admits, `LBA-A5` and `LBA-A6` against `LBA-A4` — is
complete **earlier** than under `LBA-D8`'s order. A partial run therefore holds a complete
one-column comparison sooner, which is what that clause asked for.

**(d) The fit, stated so it is not chosen later.** With **one** instrumented point the only
available projection is proportional (through the origin) and is labelled as such; with **two or
more** it is a least-squares line in archive neighbour rows, intercept free. A cell is stopped when
its projection from **all** instrumented builds so far exceeds **24 GB**. The bar is unchanged.

**(e) The unit is unchanged and is restated because it has caused a refusal here before:**
**archive neighbour rows, pre-cap, two per pair — never CSR entries.**

#### What this amendment does NOT do

- **It changes no arm, no population rule, no threshold and no bar.** The 3 × 3 lattice is exactly
  as it was, and `LBA-D8`'s prohibition stands: a cell is stopped only on `LBA-G2`'s stated bar.
- **It does not make `LBA-G2` readable at the close of stage 1**, and the stage-1 report claims no
  `LBA-G2` result.
- **It does not touch `LBA-G1`, `LBA-G3` or `LBA-G4`**, nor any measurement, read or exposure.

**Identifier `LBA-AM2`.** Collision-checked across every ref on 2026-09-14: free.

---

### `LBA-AM3` — what `LBA-G3`'s firing costs the read table, and how `LBA-G4` is read without a pass

**Dated 2026-09-15, written at the stage-2/stage-3 seam, BEFORE `LBA-M2`, `M3`, `M4` or `M5` was
taken.**

> ### ⚠ What existed when this was written, stated plainly — it is neither `LBA-AM1`'s position nor `LBA-AM2`'s
>
> **Stages 1 and 2 are complete.** `LBA-M1` is taken on eight arms, `LBA-G1` fired on nothing,
> `LBA-G2` stopped `LBA-A9`, `LBA-G3` fired at stage 1. Figures are owned by the two stage
> READMEs.
>
> **What does NOT exist is any result of the four measurements this amendment touches.**
> `LBA-M2`, `LBA-M3`, `LBA-M4` and `LBA-M5` have not been taken for any arm, so **no value of
> `LBA-G4`'s statistic exists** and nothing below can have been shaped to admit or exclude an arm.
>
> **The honest statement of what it spends: none of `LBA-M2`–`M5`'s or `LBA-G4`'s
> commit-before-results property.** It is **not** written in ignorance, and a reader weighing it
> should know exactly what its author could already see: every arm's size, CSR entries, boot
> memory and d0 query cost (stage 2 §3b); every arm's count of population members absent from the
> coverage store (stage 1 §2); and the prune's measured retention on two `U` cells (stage 2 §2e).
> **It could not see any class share, any retention figure, any supply share, or any provenance
> mix** — which is every quantity the rules below govern.

⚠ **`LBA-AM3` and `LBD-AM3` are different objects one character apart, and both are live in this
stage.** `LBD-AM3` is the `LBD-` track's fidelity override, whose extension to `LBD-A4` is an open
question of the owner's; this is `LBD-S4`'s third amendment. Neither is ever written bare as
*"AM3"*. Recorded because `CLAUDE.md`'s collision rule is about what a reader can confuse, and a
one-letter gap between two series that appear in the same paragraph is the case it is weakest
against. **Collision-checked across every ref on 2026-09-15: `LBA-AM3` and `LBA-AM3-1`–`-3` free.**

---

#### `LBA-AM3-1` — `LBA-R8` and `LBA-R9` are formally UNREACHABLE, and the design therefore cannot deliver a licensed "no"

**This is a consequence of `LBA-G3` firing at stage 1, not a new decision.** §7's run-state
vocabulary defines *censused* as *"the offline census pass **has run** and the arm's class share
is **measured rather than estimated**."* `LBA-G3` fired — the pass is not started and none is owed
— so **no arm will ever reach *censused* within `LBD-S4` as designed.** `LBA-R8` presupposes
*complete and censused*; `LBA-R9` presupposes *complete, sized and censused*. §7's closing rule is
firm: *"Nothing in this table is reachable before its run state, and a partial run licenses no
read."*

**The consequence that matters, named because it is easy to miss:** `LBA-R9` is the row that reads
*"the numbers say no"* and that records **stopping the `LBD-` track here as a complete outcome
rather than an abandonment.** It is the owner's own exit read, and the design as executed cannot
hand it to him licensed. §0's claim that every threshold outcome has a read survives; the claim
that every *decision* outcome has one does not.

**The reads stage 3 may take are exactly:** `LBA-R4` (on the `P` row, and on the `U` row with
`LBA-X6` beside it), `LBA-R5`, `LBA-R6` and `LBA-R7`. `LBA-R4-V` is restated as **already settled
on the committed record** and is never reported as a finding of this design. `LBA-R0` and `LBA-R1`
were taken at stage 2 and are not re-read here.

**The owner's instruction, recorded as his and dated 2026-09-15.** Given when he set stage 3's
scope, with the unreachability already stated to him:

> State that `LBA-R8` and `LBA-R9` presuppose censused and are formally unreachable, and give
> beside that statement what the estimated `LBA-M4` would say if it were read as measured,
> labelled so the owner can weigh it.

**What that does and does not do.** It **does not** make either read reachable, does not license a
§7 row, and does not enter the record as a finding. The content is reported as an **explicitly
unlicensed sensitivity**, in its own block, under a heading that says so, carrying `LBA-X2`'s two
bounds and the coverage split of `LBA-AM3-3`. **It is recorded here rather than done silently**
because §11's own rule is that a change of practice against this document arrives as a dated
amendment with its reasoning — and because the owner asking for a sensitivity he can weigh is a
different act from a session taking a barred read, which only the record can distinguish
afterwards.

#### `LBA-AM3-2` — `LBA-G4` is computed with its residual confound MEASURED, and it has its own effect size

**The problem.** §5's firing clause requires both class shares *"taken from the **same census
pass, the same dump and the same arm**."* With no pass run, every verdict is carried from the
2026-08-05 or the 2026-08-09 census, **against earlier MusicBrainz snapshots than the pinned
`20260905-002519` one**. The *same arm* half holds — `LBA-AM1-A5` moved the baseline inside the
arm and that is untouched. The *same pass, same dump* half does not.

**Why "declare it unevaluable" is the wrong answer, and why "compute it quietly" is worse.** The
confound is not that the verdicts are old — both subsets are equally old. It is that the two
subsets may draw from the two censuses in **different proportions**, which would put a dump column
back into a comparison `LBA-AM1-A5` had made one column wide. **That proportion is measurable**,
per artist, from the coverage store's own `d2_src` field.

**The resolution, fixed before any provenance mix has been looked at.**

1. `LBA-G4` is computed within the arm as `LBA-AM1-A5` defines it, and **every figure is labelled
   an estimate** wherever it appears.
2. **The verdict-source mix of both subsets is reported beside it** — the share of each subset
   whose `d2` verdict came from each census.
3. **Effect size for the disqualifier, stated as a number rather than left to judgement:** if the
   two subsets' shares of `cex-recensus-2026-08-09`-sourced verdicts **differ by 10 percentage
   points or more**, `LBA-G4` is **reported unreadable for that arm** and no gate result is given
   for it — only the two class shares, descriptively, with the mix beside them.
4. Below that difference the gate reads as specified, still labelled an estimate.

**Where the 10-point size comes from.** It is `LBA-G4`'s **own bar, in the same units** —
percentage points of a share. The principle: a provenance difference large enough to account for
the gate's own firing threshold is a difference large enough to disqualify the comparison. A looser
disqualifier would admit a gate result the confound could have produced by itself; a tighter one
would refuse comparisons whose residual column is smaller than the effect being measured.
**Stated as a choice, not a measurement**, in §5's own manner.

#### `LBA-AM3-3` — `LBA-M4`'s coverage is UNEVEN across the lattice, and the split is reported per arm

**`LBA-M4`'s ⚠ already requires the split by verdict source and reserves *exact* for the fresh
share. After `LBA-G3`, the fresh share is zero on every arm** — stage 1 §3 says so. What neither
document says is that *"estimated on every arm"* covers **two different situations**, and the
difference falls exactly on the arms the measurement exists to size.

- On `LBA-A1`–`LBA-A6`, stage 1 §2 measured **zero** population members absent from the coverage
  store. Every artist carries a verdict, so the class share is **carried-measured over a complete
  population** and only the *drop* is extrapolated.
- On `LBA-A7` and `LBA-A8`, a large majority of the population is **absent from the store
  entirely** (stage 1 §2 owns the counts). The store's own status string binds here: *"absence of a
  field means UNKNOWN, never false."* So for those arms **both** the class share and the drop are
  extrapolated, over a population most of which no census has ever evaluated.

**Consequence, a bar.** Every `LBA-M4` table carries a **coverage column per arm** — the share of
the arm's built node set holding a `d2` verdict — and **no sentence compares a `U`-row class share
with a `V`- or `P`-row one as though both were measured on the same basis.** The `U` figures are an
extrapolation from the covered minority to the uncovered majority, and the report says so wherever
they appear.

#### What this amendment does NOT do

- **It changes no arm, no population rule, no threshold, and no bar's value.** `LBA-G4`'s 10-point
  bar is untouched; `LBA-AM3-2`'s 10-point disqualifier is a **new and separate** criterion that
  can only ever *withhold* a gate result, never produce one.
- **It does not make `LBA-R8` or `LBA-R9` reachable**, and the stage-3 report claims neither.
- **It does not reopen the owner's three rulings** (`LBA-D1`–`D3`), select an arm, prefer a
  threshold, or recommend a route.
- **It adopts nothing, changes no default, and touches no shipped code.**
- **It does not re-read any `LBD-` criterion**, and `LBD-AM3`'s extension to `LBD-A4` — a different
  object, see the warning above — remains open and the owner's.

**Identifier `LBA-AM3`.** Collision-checked across every ref on 2026-09-15, together with
`LBA-AM3-1`–`LBA-AM3-3`: free.
---

### `LBA-AM4` — the unblinded use gate (`LBA-G5`), inserted between §8 item 3 and §8 item 4

**Dated 2026-09-21, written AFTER the owner's go/no-go ruling and BEFORE any candidate build
exists.**

> ### ⚠ What existed when this was written, stated plainly — it is a later position than `LBA-AM1`, `LBA-AM2` or `LBA-AM3`
>
> **All three stages are complete and reported.** `LBA-M1`–`M5` are taken on the eight sized arms;
> `LBA-G1` fired on nothing, `LBA-G2` stopped `LBA-A9`, `LBA-G3` fired at stage 1, `LBA-G4` is
> reported unreadable under `LBA-AM3-2` wherever it is evaluable. Every read the run state
> licensed has been read. **Figures are owned by the three stage READMEs and none is restated
> here.**
>
> **The owner's go/no-go ruling exists and is GO**, at `LBA-A6` — population `P`, threshold 3,
> ListenBrainz's own pairing (`LBA-D1`). Given 2026-09-21.
>
> **What does NOT exist is anything this amendment governs.** No candidate build exists: no
> artifact of any arm carries `fame_lb`, because every arm built `require_fame=False` (`LBA-D5`).
> **No journey has been generated on any `LBA-` map by anyone**, so no result of `LBA-G5` and no
> result of the `REQ-38` listen can exist, and neither the criterion nor the period below can have
> been shaped to admit or exclude an outcome.
>
> **The honest statement of what it spends: none of `LBA-M1`–`M5`'s or `LBA-G1`–`G4`'s
> commit-before-results property**, all of which were read and reported before it was written. It
> spends the commit-before-results property of **`LBA-G5` itself**, which is intact — its author
> could see every structural and resource figure the three stages produced, and could see **no
> journey, no candidate artifact, and no fame ranking over `P`**, which is every quantity the gate
> below is about.

⚠ **This amendment does not renumber §8.** Items 1–4 keep their numbers so that every document
written before today which says *"§8's four items"* — stage-3 README §9 options B, C and D among
them — still resolves. **§8 now has five stages**, and the gate sits between items 3 and 4.

---

#### `LBA-G5` — the unblinded use gate

**Plain sentence, fixed here before any result exists:** *the owner uses the new map himself for a
short, bounded period, and says whether it made the app worse.*

**His pass/fail criterion, given 2026-09-21, recorded verbatim, written before he had seen a
single journey on any `LBA-` map:**

> a noticeably worse product experience on more than half of tested journeys

**and, in his words, what "noticeably worse" means here — two limbs, either of which fires it:**

> novel artists become more difficult to surface **OR** novelty is traded for coherence (meaning
> novel artists surface but coherence of the path suffers as a result)

**His bounded period, given at the same time:** **2 days of actual app use, maximum.**

**The effect size is his and is in the criterion: *more than half* of tested journeys.** A
minority of worse journeys does not fire this gate. It is recorded as an effect size and not as a
sentiment because `CLAUDE.md`'s rule is that a gate without one cannot tell the finding it was
written for from noise and fires the expensive response either way — and the expensive response
here is discarding a candidate.

⚠ **The second limb is NEW and has no precedent on this project.** The 2026-08-10 `CXA-` criterion
had the novelty limb alone. A candidate that surfaced novel artists *at the cost of the path
hanging together* would have **passed** that criterion and fires this one. Recorded because the
difference is the owner's and is not a session's paraphrase of the older criterion.

#### Why this gate exists — the `CXR-` defect class, and why no `LBA-` arm can see it

**The `CXR-` regression is the case.** Its diagnosis is
[`builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`](../../../builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md),
whose figures are owned there and are **not restated here**. Its `CXR-P1` half is a
**fame-ranking** mechanism: the ramp prices each artist by rank within *the artifact's own measured
population* (`graph_store.fame_percentiles`), so adding artists below the existing population moves
everyone and squeezes the only device that steers a journey toward unfamiliar artists at depth.

**Any `P`-population map carries that mechanism by construction, and no arm in this document
measured it.** Three of this document's own clauses say so and they interlock:

- **`LBA-X1`** names the fame percentile as one of four population-relative quantities that
  recompute over each arm's own node set, and names `CXR-P1` as the mechanism.
- **`LBA-D5`** built every arm with `require_fame=False`. **No arm has a fame ranking at all.**
- **`LBA-X7`** confines the fame ruler to `V`: banding uses the served artifact's own `fame_lb`
  records, which exist only for artists the served map contains.

**So the candidate acquires, at §8 item 1, the exact quantity that produced the August regression,
and it acquires it after every measurement in this document was taken.** Nothing in stages 1–3 is
wrong about it; the design simply never had it in hand.

**Use is the cheapest known detector of this class, and the only demonstrated one.** No instrument
in this project detected the `CXR-` regression in advance; the owner detected it **within minutes
of use**.

> ⚠ **A correction to the record, made here because the documents that carry the figure are
> frozen.** Four documents state that the `CXR-` revert criterion fired *"after three weeks of
> use"* — the `CXA-` adoption handoff, the `CXR-` revert handoff, the `CXR-` diagnosis README and
> `findings/2026-09-16-cxr-revert-and-the-s4-population.md`. **That interval is TIME-TO-REPORT, not
> time-to-detect.** The owner states (2026-09-21) that he noticed the degradation within minutes;
> the delay was availability — he was away, and he is the app's only user, so he left it until he
> had time to roll back. **None of those four documents says which quantity it is measuring**, and
> a session reading them on 2026-09-21 took the three weeks for the detection latency and drew the
> opposite conclusion about how long this gate needs to be. The four documents are COMPLETE or
> HISTORICAL and are **not edited**; per `docs/README.md`'s rule the correction goes forward, and
> this is where it lands.

**Two days is therefore a bounded period chosen against a demonstrated detection latency**, not
merely a cheap one. The `CXA-` plan's separate calibration points the same way: the
`ALG-E → ALG-B` switch was recognised as a clear improvement in under five minutes.

#### The four bars on this gate

1. **It is a STOP-GATE, not a quality bar.** It can only ever *stop* the candidate. It produces no
   score, ranks nothing, and no figure it yields may enter the record as a measurement of path
   quality — that currency belongs to `findings/2026-07-21-scoring-adjudication.md` and this gate
   adds nothing to it.
2. **It is NOT the `REQ-38` listen and does not replace it.** It is unblinded, single-subject, and
   the owner knows which map he is on throughout. `REQ-38` remains owed in full at §8 item 4,
   designed cold as a separate amendment written when no journey exists on either map (`LBA-D3`),
   and `GBL-` §5's run-once rule will bind its verdict. **A pass here is not evidence of quality
   and must never be cited as one.**
3. **Failing it means the candidate is not listened to**, and the fallback is **`LBA-A3`** —
   `LBD-A5V`, already built, serialised and carrying fame, immediately servable. ⚠ **`LBA-A3`
   differs from the candidate in TWO columns, not one: population (`V` vs `P`) and drop-list
   payload (`…20260805.json` vs `…20260809.json`).** §2.1's baseline column and its boxed warning
   own this: the payload column is real even where its effect is zero, and a one-column claim
   across it is wrong even though no artist moves. The fallback is sound; **no comparison between
   `LBA-A3` and the candidate may be reported as a population effect alone.**
4. **Passing it licenses NOTHING except proceeding to §8 item 4.** It adopts nothing, changes no
   default, selects no threshold for any future map, and says nothing about the `U` row, about
   `LBA-A9`, or about any arm not built. `LBA-R9` remains unreachable and a pass here is not a
   substitute certificate.

#### What being unblinded costs, stated rather than glossed

The owner knows he is on the candidate, expects it to differ, and chose the criterion. **That is
exactly the `CXA-` precedent's shape and it worked** — the 2026-08-10 criterion fired on
2026-09-01 and the revert followed. It is admissible here for the same reason: a stop-gate's
failure mode is a *false pass*, and expectation bias on an unblinded subject who wants the
candidate to succeed pushes toward the false pass, which is the direction that costs least —
it forfeits nothing except the chance to stop early, and `REQ-38` still stands behind it.
**The reverse is not true of a quality claim**, which is why bar 1 and bar 2 exist.

#### What this amendment does NOT do

- **It changes no arm, no population rule, no threshold, and no bar's value.** `LBA-G1`–`LBA-G4`
  are untouched; `LBA-G5` is a new and separate criterion that can only ever *stop* a candidate.
- **It does not design, shape, pre-empt or narrow the `REQ-38` listen**, whose amendment is owed
  cold by a separate session (`LBA-D3`). It draws no pair, fixes no protocol and generates no
  journey.
- **It does not reopen the owner's three rulings** (`LBA-D1`–`D3`) or his go/no-go ruling.
- **It re-reads no `LBD-` or `LBA-` criterion**, and both `LBL-` verdicts remain run-once and final.
- **It adopts nothing, changes no default, touches no shipped code, and does not change
  `ApiConfig.graph_path`.**
- **It does not renumber §8.**

**Identifiers `LBA-AM4` and `LBA-G5`.** Both collision-checked across every local and remote ref on
2026-09-21, by `git grep -lE` over `refs/remotes` and `refs/heads` restricted to `*.md`: **both
free.**

---

### `LBA-AM5` — the blind listen runs FIRST and the use gate SECOND: `LBA-AM4`'s sequence corrected

**Dated 2026-09-22. Forward-only: `LBA-AM4`'s text above is not edited**, and neither is any bar's
value. The owner instructed this amendment on 2026-09-22.

> ### What exists when this is written, stated plainly
>
> - **The `LBA-A6` candidate is built, serialised and pinned** (§8 items 1–3), with its four
>   id/fact maps **re-extracted over its own population** on the owner's ruling of 2026-09-21. Its
>   identity is its manifest sidecar beside it in `C:\unsung-fast\lbd-artifacts\`; the checksum is
>   taken from there and never transcribed (`DEP-24`). Figures are owned by
>   [`builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md`](../../../builder/analysis/2026-09-21-lbd-s4-a6-candidate/README.md).
> - **No journey has been generated on the candidate by any session** — that README says so, and
>   no script in its directory calls the router. *Stated precisely rather than more broadly, because
>   `LBA-AM4`'s wording ("no journey has been generated on any `LBA-` map by anyone") is wider than
>   the record: stage 2's `LBA-M1` query-cost half (`s4_query_cost.py`) ran the shipped
>   `find_journey` at d0 over 200 seeded random pairs on the **fame-free stage-2** `LBA-A6` arm and on
>   the served map, for **wall-clock timing only**. It recorded times and hop counts, no artist, and
>   nothing was shown to anyone. No listener has seen, heard or been told a journey on any `LBA-` map.*
> - **The owner has not run the use gate `LBA-G5`.** No result of it exists.
> - **No result of the `REQ-38` listen exists, and none of its design exists either** — it is
>   `LBA-AM6`, written after this amendment is committed.
>
> **What it spends: nothing.** It moves the order of two stages, neither of which has run, and it
> changes no criterion, no bar, no period and no read.

#### The defect

**`LBA-AM4` inserted an unblinded use stage that generates journeys on the candidate immediately
before §8 item 4.** Item 4 is the `REQ-38` blind listen, whose precondition is that it is **designed
when no journey exists** (§8 item 4; `LBA-AM4`'s own bar 2 restates it), and **whose listener is the
same person who runs the use gate** — the owner. Running the gate first means the one listener
arrives at a run-once blind listen having spent up to two days using the candidate knowingly.

**That contamination can be neither measured nor undone.** `GBL-` §5 makes each listen's verdict
run-once and final, so a contaminated verdict cannot be repeated clean; and nothing in the listen
could separate a pick made on the journeys from a pick made on a remembered interior, a
recognised style, or a feel learned during the gate. **This is not hypothetical here:** the `GBL-`
run log §5
([`../2026-08-04-gbl-run-execution-log.md`](../2026-08-04-gbl-run-execution-log.md)) records the
listener volunteering, before he saw the result, that it was *"almost always really easy to tell
which side was the 'new' graph"* — identification by feel, in an earlier listen, **without** two
days of prior use. Two days of knowing use can only make that easier.

`LBA-AM4` did not intend this: it states that it *"does not design, shape, pre-empt or narrow the
`REQ-38` listen"*. The defect is in the sequence, not in the gate.

#### The fix — the order of §8's fourth and fifth stages is reversed

**The `REQ-38` blind listen (§8 item 4) runs FIRST. `LBA-G5`, the use gate, runs SECOND.** §8 items
1–4 keep their numbers, as `LBA-AM4` requires; what changes is only which of the two post-build
stages runs first. So the sequence is now: items 1–3 (done) → **item 4, the blind listen** →
**`LBA-G5`, the use gate** → adoption, which is the owner's.

**Why this order and not the other — an asymmetry, not a preference:**

- **If the candidate FAILS the gate, the listen's verdict is discarded, whichever order they ran
  in.** A failed gate stops the candidate (`LBA-AM4` bar 3), so a verdict about a candidate that
  will not ship is spent either way. Running the listen first costs, at worst, a listen on a
  candidate that is then stopped.
- **If the candidate PASSES the gate, the listen is adoption's primary evidence** (`REQ-38`: offline
  metrics must not override listener judgment), **and it must be uncontaminated.** Running the gate
  first would put the adoption decision on a verdict whose blind had already been spent.

So listen-first loses, at most, the ear on a candidate the gate would have stopped. Gate-first
loses, whenever the candidate is good enough to adopt, the integrity of the only evidence the
adoption rests on. **The cost named in `LBA-AM4` bar 3 — *"failing it means the candidate is not
listened to"* — is thereby given up deliberately**, on the owner's instruction: the listen is now
spent before the cheap gate can stop the candidate.

**The gate is unblinded by design, and running it second does not weaken it.** It never depended on
not knowing which map he was on (`LBA-AM4`, *"What being unblinded costs"*). What protects it from
knowledge of the listen's verdict is **its pre-written criterion**, recorded verbatim in `LBA-AM4`
on 2026-09-21 before any journey or verdict existed: *"a noticeably worse product experience on
more than half of tested journeys"*, with its two limbs. He judges journeys against that sentence,
not against the listen's result, and the sentence cannot be moved now that a verdict will exist
before the gate runs — §11's rule that a bar's value is never edited binds it.

**`LBA-G5`'s outcomes after a verdict exists, fixed now so neither is decided later:**

- **Gate FAILS** — the candidate is stopped exactly as `LBA-AM4` bar 3 says. The listen's verdict is
  recorded and stands as the run-once record of that comparison; it adopts nothing. The fallback,
  and the restoration of `acceptance.py`'s previous bounds before any rebuild, are unchanged —
  `NEXT.md`'s deferral row already keys the restoration on *"the candidate is not adopted"*, which
  covers every route.
- **Gate PASSES** — licenses nothing except proceeding to the owner's adoption decision, with the
  listen's verdict as its primary evidence. `LBA-AM4` bar 4 is otherwise unchanged.

#### One new requirement on the gate: the owner logs the artist pairs he uses

**During `LBA-G5`, the owner records every artist pair he runs a journey on** — the two endpoint
artists, in the order entered, one line per journey. *Plain: write down which two artists each
journey went between, so that anyone reading the gate's result later can see what it was tested
on.* Where the log lives is an operational choice and is `LBA-AM6`'s runner brief's to name. Two
reasons, neither of which reaches the listen, which by then will already have run:

1. **"More than half of tested journeys" needs a denominator.** Without a log, the effect size the
   owner wrote into his own criterion has nothing to be counted against.
2. **It makes the pairs available to any later listen** — as exclusions, because a pair he has used
   knowingly on the candidate carries the memory tell `lbl_pairs.py` step 2 excludes for `GBL-AM1`.

The log records **pairs, not verdicts per journey.** His criterion is his, applied as he wrote it;
the log does not turn it into a scored instrument, and `LBA-AM4` bar 1 — *no figure it yields may
enter the record as a measurement of path quality* — is unchanged.

#### The owner's gate period stands

**"2 days of actual app use, maximum"** is his, given 2026-09-21 and recorded verbatim in `LBA-AM4`.
**This amendment does not shorten, lengthen or otherwise touch it.** Moving the gate after the
listen changes when it starts, not how long it is.

#### What this amendment does NOT do

- **It edits no text of `LBA-AM4`** and moves no bar's value — `LBA-G5`'s criterion, its two limbs,
  its effect size and its period all stand verbatim.
- **It designs no part of the `REQ-38` listen.** That is `LBA-AM6`, written after this is committed.
- **It generates, draws or describes no journey and no pair.**
- **It does not reopen `LBA-D1`–`D3` or the go ruling**, re-reads no `LBD-` or `LBA-` criterion, and
  leaves both `LBL-` verdicts run-once and final.
- **It adopts nothing, changes no default and touches no shipped code.**
- **It does not renumber §8.**

**Identifier `LBA-AM5`.** Collision-checked 2026-09-22 across every local and remote ref, by
`git grep -lE '\bLBA-AM5'` over `refs/remotes` and `refs/heads`: **free.**

---

### `LBA-AM6` — the `REQ-38` blind listen: today's served map against the `LBA-A6` candidate (§8 item 4)

**Dated 2026-09-22. Designed cold**, as `LBA-D3` and §8 item 4 require, after `LBA-AM5` was
committed (`e1cf884`) and on the owner's instruction of the same day.

> ### What exists when this is written, stated plainly
>
> **No journey exists on the candidate** (`LBA-AM5`'s first box, unchanged since). **No pair has been
> drawn, no pre-screen has run, and no harness for this listen exists.** The owner has not run
> `LBA-G5`. **The session that wrote this amendment has generated, viewed and been told no journey
> on either map**: it read no page-data, verdict, result or pre-screen file from either `LBL-`
> listen or from `GBL-`, and it did not open the candidate artifact. It read the protocol documents,
> the two listens' findings notes, and the harness's source.
>
> **What it spends: nothing.** Every read below is fixed before any journey this listen could
> present exists, which is the property `GBL-` §5 and `LBA-D3` need and the commit timestamp
> evidences.

**The plain question, fixed here:** *"Would the app give better journeys if it served the new map
instead of today's?"*

**Identifiers.** Sub-items `LBA-AM6-1`–`LBA-AM6-11`. **This listen's own series is `LAL-`**
(`LAL-Q1`–`LAL-Q4`, `LAL-K`, `LAL-R1`–`LAL-R4`) — deliberately **not** `LBL-`, whose `Q` and `R`
identifiers are bound to listens 1 and 2 and whose `LBL-Q3`/`LBL-Q4` would collide with this
listen's different questions. Two exposures, `LBA-X9` and `LBA-X10`.

#### `LBA-AM6-1` — the comparison, and its factor table

**Incumbent: today's served map**, `graph-msw-tu50.bin` (`ApiConfig.graph_path`'s default),
verified at generation against its sidecar **and** against the deployed `graph-lux4.bin` by the
routing-identity gate `lbl_generate.py` already carries, so that "today's map" is the one the site
actually routes on. **Challenger: the `LBA-A6` candidate**, `LBA-A6-candidate.bin`, verified against
its sidecar. Both shas are read from the sidecars by script into the listen's map pin, never
transcribed.

| map | similarity data | `threshold` | population | un-listenable drop payload | fame records | id / fact maps | router | isolating baseline |
|---|---|---|---|---|---|---|---|---|
| **served** — incumbent | ListenBrainz's deployed lists (`ALG-B` snapshot) | LB's 10 | `V` | `…20260805` | the `fame` stage's records in the served lineage's snapshot | the served lineage's | `ApiConfig` defaults | — |
| **`LBA-A6` candidate** — challenger | our recomputation of ListenBrainz's listening data (`T`, ListenBrainz's own pairing, `LBA-D1`) | **3** | **`P`** | **`…20260809`** | **fetched over `P` at §8 item 1** | **re-extracted over `P`** | same | **none is one column away** |

**No map differs from the candidate in exactly one column, and none can be built for this listen**:
the candidate differs from the served map in at least five columns, and **that bundle is the thing
adoption decides.** So the verdict is about **the candidate as a whole against today's map**, and
it is **barred from attributing any difference to any one column or any subset of them** —
threshold, population, payload, fame date or data source. The nearest built maps are no help:
`LBA-A3` (`LBD-A5V`) is two columns from the candidate (§2.1), and listens 1 and 2 compared other
pairs of maps (`LBA-AM6-9`). The id/fact column is **neutralised for the listen** by `LBA-AM6-6`
(clips are a function of the artist alone), so it cannot reach a verdict.

**Held constant, and why each genuinely is:** the router — the shipped `find_journey` under
`ApiConfig` defaults, one code path for both maps; the press ladder — `cre_ladder.victim_key`,
identical code on both sides; the pairs and depths — one set for both maps by construction; clip
resolution — one rule keyed by MBID for both sides (`LBA-AM6-6`); the page, its questions and the
listener.

**Held constant in configuration, NOT in effect — the terms the intervention switches on.** The
population column moves every population-relative quantity the router reads (`LBA-X1`):
`fame_lb_pctl`, `pop_raw`, `degree_hub_penalty` and the p99 rescale all recompute over `P`. **This
includes the fame-ranking mechanism behind the August `CXR-` regression** (`LBA-AM4`, *"Why this
gate exists"*), which acts through the ramp and so only after presses. It is not an uncontrolled
nuisance here — it is part of what adoption would ship, and it is **why d10 and d20 are in the
listen**. **Consequence, a bar:** no sentence may attribute a d10 or d20 difference to the ramp,
the fame ranking or any single recomputed quantity; the listen hears their joint effect and cannot
separate them.

#### `LBA-AM6-2` — the pair draw: the rule, fixed now, before any journey exists

*Plain: take artists the owner is known to listen to, pair them up, and keep only pairs on which
the two maps give genuinely different journeys — different at every depth, and different in
artists he does not know — without ever looking at which map's journey is longer, more obscure or
better.*

**Who runs it.** A **fresh preparation session**, which commits the pre-screen script with this rule
in its docstring **before first running it** — the `lbl_prescreen2.py` / `855b090` precedent, and
the ordering is the evidence. **Its outputs are map-labelled**, so that session may not run the
listen or write it up (`LBD-AM6`'s precedent), and its outputs go on the runner brief's do-not-read
list.

1. **Pool.** The owner's familiarity-ranked artists, `gbl_pair_candidates.json`'s `usable` list in
   its committed order — so both endpoints are artists he demonstrably knows (`REQ-41`).
2. **Excluded at ARTIST level — every endpoint of every pair on which journeys were presented to him
   in any blind listen.** That is `GBL-AM1`'s eight pairs (`gbl_pairs_approved.json`, sha-pinned),
   listen 1's eight primaries (`lbl_pairs.json`) and listen 2's eight primaries (`lbl_pairs2.json`).
   No substitution fired in either `LBL-` listen (`LBD-AM6-1` D2; listen-2 findings §1.1), so the
   primaries are exactly what was heard. The reason differs per listen, and each is sufficient:
   `GBL-`'s arm is the served map's lineage; listen 1 presented journeys **on the served map**, this
   listen's incumbent; and listen 2's `LBD-A5V` is the candidate's own threshold and pairing over
   `V` (§2.1, `LBA-A3`), so a remembered listen-2 interior could identify the candidate's side.
3. **Excluded as PAIRS, artists kept** — every reserve pair of both `LBL-` listens. None was ever
   generated, so the artists carry no memory (`LBD-AM6-1` D2).
4. **Membership.** Both endpoints are nodes of **both** maps, read from the two artifacts directly.
5. **Pairing.** Greedily in pool order, each artist with the earliest still-unpaired artist to which
   it is **not directly connected in either map** (`lbl_pairs.py` step 4, applied to both maps).
6. **Pre-screen.** For each candidate pair, both maps' journeys are generated exactly as
   `LBA-AM6-3` will generate them, and **three gates** are applied:
   - **Gate L — length** (listen-2 findings §4 item 1's companion, `LBD-AM6-3`): **at least 3
     interior artists** at **every** depth on **both** maps.
   - **Gate D — difference at EVERY depth** (listen-2 findings §4 item 1): the two maps' interior
     artist **sets** differ at **all three** depths, not two. Listen 2's gate of 2 of 3 let five
     identical cells through, four of them at d0, which is in the tally.
   - **Gate N — differential novelty at every depth** (listen-2 findings §4 item 2): at every depth,
     the **symmetric difference** of the two interior sets contains **at least one artist absent
     from the owner's familiarity list**. *Interior-set difference is not novelty difference; this
     is the version of it that can be measured in advance.* **The familiarity list is exactly
     `lbl_prescreen2.py`'s `familiarity_mbids`** — `gbl_pair_candidates.json`'s `usable` plus
     `ambiguous` entries — used here, as there, only to count, never to exclude.
7. **Ranking — magnitude and unfamiliarity, never direction.** Survivors are ordered by (a) the
   **total count, over the three depths, of symmetric-difference artists absent from the familiarity
   list**, most first; then (b) fewest interior artists the list contains, over both maps and all
   depths (`LBD-AM6-1`'s key); then pool rank; then MBID — a total order, so the selection is
   reproducible from the committed output. **Nothing in any gate or key reads which side an artist
   is on, which map is longer, or which is more or less famous.**
8. **Selection.** The first **8** are the primaries and the next **4** are ordered reserves. Fewer
   than 12 survivors: stop and report; the owner supplies pairs, **which must pass the same gates**.
9. **Owner's strike, before anything is shown to him.** The preparation session shows the owner the
   twelve pairs as **endpoint names only** — no interior, no length, no map. **He may strike any
   pair** — for instance one he has run on the live app — and the next reserve fills it. That spends
   nothing: an endpoint name is not a journey. After the page is first served, no pair changes.

> ⚠ **`LBA-X9` — the selection leans toward pairs on which the candidate's added artists appear,
> and that is disclosed rather than corrected.** The artists the candidate adds (count owned by the
> candidate README) are absent from the served map by construction and mostly absent from the
> familiarity list, so a direction-blind count over the symmetric difference will rank highly the
> pairs on which the candidate routes through them. **That is magnitude of difference — the
> difference this listen exists to hear — not a preference for either map**, and no key reads
> which side the artists sit on. **Consequence, a bar:** the verdict holds for **pairs on which the
> two maps differ at every depth in artists he does not know**, and no sentence may generalise it
> to the typical journey. The per-side split of those artists is computed at generation and
> **sealed** (`LBA-AM6-5`).

**Also disclosed, not controllable:** the owner uses the served map daily, and pairs he has run on
the live app are recorded nowhere. Step 9 lets him strike any he recognises; the rest is measured on
the row by `LAL-Q4` (`LBA-AM6-4`).

**The familiarity list is known to under-read what he knows** (listen-2 findings §4 item 3): it
can say an artist is unfamiliar when he knows them. No advance fix exists that does not show him
journeys, so **the defect is measured on the row instead**, by `LAL-K` below, and reported beside
the verdict.

#### `LBA-AM6-3` — what is generated

For each pair, the journeys production `find_journey` returns over each map under `ApiConfig`
defaults, at **d0, d10 and d20** — *the first path, and the path after ten and after twenty presses
of "Dig deeper"* (the `known` signal) — along **the all-`known` ladder**: at each press the pressed artist is
`cre_ladder.victim_key`'s choice over **that map's own** fame percentile, exactly as both `LBL-`
listens routed. **The limitation travels** (`JFX-` `AM1.3`): a real user presses whoever they know,
so the ladder is a fixed stand-in for a user, identical on both sides. **Twenty presses is what
exercises the ramp** — the mechanism `LBA-AM6-1` names.

**Generation gates, in this order and mechanically, before anything is shown to anyone:** a primary
is replaced by its next reserve if (a) an endpoint is not a node of both maps, (b) the endpoints are
directly connected in either map, or (c) Gate L fails. Gates D and N are then **asserted** — they
are deterministic and passed at the pre-screen, so a failure means the maps or the code moved, and
generation stops. Reserves exhausted: stop and report; no read exists until eight pairs are
complete. **Before serving**, the differential check refuses a page serving one map against itself,
and the routing-identity gate (`LBA-AM6-1`) must pass.

#### `LBA-AM6-4` — what the listener sees and answers

**One side-by-side section per pair**, the `GBL-`/`LBL-` format: both maps' journeys at the three
depths, depth order preserved within a side, no labels, no metrics, names with their MusicBrainz
disambiguation. **Sides are DEALT to a balanced 4–4** — four pairs put each map on the left, which
pairs being decided by a system random source (listen-2 findings §4 item 7; `LBD-AM6-6`). **Up to
three clips per artist** (§4 item 6). **A card that resolved no clip says so on the card** — *"no
clip found"* — instead of falling silent (§4 item 8: a silent, one-sided clip gap would cost a row
without anyone noticing it was a resolver problem rather than a map problem).

**Per row (pair × depth), wording frozen here, before any journey exists:**

- **`LAL-Q1` — coherence:** *"At this point, which side holds together better as a journey — each
  step a sensible next listen?"* — **left / right / no preference.** (`LBL-Q1`'s wording, unchanged.)
- **`LAL-Q2` — novelty:** *"At this point, which side gives you more artists that are new to you?"* —
  **left / right / no preference.** (`LBL-Q2`'s wording, unchanged.)
- **`LAL-Q3` — pick strength:** *"if you picked a side, how strong?"* — **slight / strong**, per axis,
  required wherever that axis carries a clear pick and refused where it does not. (`LBL-Q4`'s
  wording and treatment, carried forward as listen-2 findings §4 item 5 records.)
- **`LAL-Q4` — could you tell which side is the new map:** *"On this row, can you tell which side is
  the new map?"* — **no / yes, left / yes, right**, required on every row, **shown only after
  `LAL-Q1` and `LAL-Q2` are answered for that row**, so asking it cannot prime the picks.
- **`LAL-K` — known-everyone box:** *"Every artist that differed between the two sides was already
  known to me"* — a tick box.
- **The clip-problem box**, *"a clip problem stopped me judging this row"*, and notes.

**Per pair, at the end:** *"Did either side collapse into a random walk into obscurity? If so, which
and where?"* (`GBL-Q2`'s clause) and notes.

**Dropped: `LBL-Q3`'s trade-off question** (listen-2 findings §4 item 4: 24 "no"s including the
opposite-picks row). Whether a row traded one axis against the other is **computed from the row** —
it is exactly the rows on which `LAL-Q1` and `LAL-Q2` name opposite sides — and reported
descriptively.

#### `LBA-AM6-5` — the blind, and what is recorded but hidden

**`GBL-` §6 in substance.** The side mapping is written by script to the gitignored
`.superpowers/lal/` before serving and read by nothing until every verdict is on disk. **Three fresh
sessions, none of them this one:** the **preparation** session (`LBA-AM6-2`; it sees map-labelled
pre-screen output and so may do nothing after it), the **runner** — fresh and mechanics-only,
working from a runner brief with no results, no expected outcome and no framing, and saying nothing
to the owner beyond mechanics (`CLAUDE.md`, *"Exception — blind evaluations"*) — and a **further
fresh write-up session**, which alone runs the unblind. **No Spotify, monthly-listener or
ListenBrainz lookups during the listen.** **Nobody computes a running tally during the listen.**

**The blind is imperfect, and three tells are disclosed now:**

1. **`LBA-X10` — membership.** The candidate contains artists the served map lacks (count owned by
   the candidate README). **A row on which the only difference is an artist the served map cannot
   contain may be identifiable by membership alone**, and nothing in the design can hide that
   without hiding the thing being compared. `LAL-Q4` measures it.
2. **Feel.** The `GBL-` run log §5 records the listener identifying the new map *"almost always"*.
3. **Daily use of the served map.** A remembered live-app journey identifies the incumbent's side.

**Recorded at generation, sealed beside the mapping, shown to no one until after the verdict, and
deciding nothing:** per journey, interior fame on the **candidate's own `fame_lb_pctl`** — the only
ruler covering every artist either side can present, since the served map's records cannot reach
the added artists (`LBA-X7`) — and on the served ruler where it is defined; per side, the count of
presented artists outside `V`; per side, the count of symmetric-difference artists absent from the
familiarity list (`LBA-X9`'s split); length; the non-hub interior count and `top1pct_degree_frac`;
and per-side clip coverage.

#### `LBA-AM6-6` — clips: one source, keyed by the artist alone

Every presented artist resolves through the app's own `ClipResolver.resolve(mbid, name,
deezer_artist_id, index)`, with the **name and Deezer id taken from one source for both sides**:
the **candidate artifact's** recorded id where it records one, otherwise the **served artifact's**,
otherwise name search — the same answer for an artist whichever side it appears on. *Plain: an
artist sounds the same whichever map put them on the page.* **Generation refuses if the two
artifacts record different Deezer ids for the same MBID.** The re-extraction was strictly additive,
so they should agree, but that is exactly the kind of assumption this refusal exists to check
rather than trust. An artist only one map can present gets the clip it would get in that map's
app. **The listen judges maps, not id snapshots** — the same line `LBA-AM4` draws for the gate.

#### `LBA-AM6-7` — the reads, `LAL-R1`–`LAL-R4`, fixed before any journey exists

**Per axis, 24 rows** (8 pairs × 3 depths). **d0 is IN the tally**, for `LBD-AM5-5`'s reason: the
intervention is the map, which acts on the very first path. A **clear pick** is left or right; *no
preference* counts for neither. **Margin bar: 8** — `GBL-`'s scaling rule, 3 of 10 per row, rounded
up: 24 × 0.3 = 7.2 → 8. Per axis, the challenger is the candidate and the incumbent is the served
map:

- **candidate better** — margin ≥ 8 toward the candidate;
- **served better** — margin ≥ 8 toward the served map;
- **no detectable difference** — margin < 8;
- **underpowered** — margin < 8 **and** at least 8 of that axis's *no-preference* rows carry the
  clip-problem box (`GBL-` results §6.2). A margin ≥ 8 stands however many rows were lost.

| read | when | *plain sentence* |
|---|---|---|
| **`LAL-R1` PASS** | no axis *served better*; at least one *candidate better* | *"Journeys on the new map are better on [axis], and no worse on the other."* |
| **`LAL-R2` TIE** | both axes *no detectable difference* | *"My ear cannot tell the new map from today's on these pairs."* |
| **`LAL-R3` FAIL** | either axis *served better* — **including a split** where the other axis went to the candidate | *"Today's map gives better journeys on [axis]."* |
| **`LAL-R4` UNDERPOWERED** | no axis *better* either way, and at least one axis *underpowered* | *"Too many rows were lost to clip problems to read this listen."* |

**A split counts as FAIL deliberately**: `WHAT-GOOD-LOOKS-LIKE` value 8 — novelty is delivered
through coherence, not traded against it — and it is the same judgement the owner wrote into
`LBA-G5`'s second limb. A novelty loss beside a coherence gain is reported as FAIL on novelty, in
those words. Two axes with the same bar raise the chance that one crosses by noise; accepted, and
stated.

> **`REQ-41`, beside the tie, because this is where it bites.** *"No difference" in unfamiliar
> territory is uninformative, not evidence of equivalence.* **`LAL-R2` is not "the new map is as
> good as today's"**, not "the new map is safe to ship", and not "the population change is
> inaudible". It says the instrument could not separate them on these eight pairs at this margin.

**What each read licenses** — consequences, not recommendations; adoption stays the owner's:

- **PASS** — the ear evidence `REQ-38` asks for, on these pairs, favours the candidate. `LBA-G5`
  runs next (`LBA-AM5`).
- **TIE** — no ear evidence either way at this instrument's resolution. Nothing here licenses
  adoption or rules it out; whether to run `LBA-G5` and adopt on a tie is the owner's.
- **FAIL** — the ear placed today's map above the candidate on the named axis, and `REQ-38` bars
  offline figures from overriding that. What follows is the owner's.
- **UNDERPOWERED** — no read. **The listen is not repeated on the same pairs**; a further listen on
  new pairs, after the clip defect is addressed, is a new amendment.

**Run state each read presupposes, named per read:**

- **`LAL-R1`–`LAL-R4`** presuppose **all 24 rows answered on both axes, `LAL-Q3` wherever owed,
  `LAL-Q4` on every row, and all eight pair-end entries saved** — and the unblind run by the
  write-up session after all of that is on disk. **No read is reachable before that**: a partial
  run licenses nothing, whatever a partial tally would show. **A listen whose outcome looks settled
  before row 24 still runs to row 24 and to the eighth pair's end entry**, because the run state
  is part of the read, and because nobody may be computing a tally to know it looks settled.
- **The descriptive reads in `LBA-AM6-8`** presuppose the same full run **and** the unblind.
- **The pre-screen and the draw** (`LBA-AM6-2`) presuppose both artifacts passing their sidecar
  checks and nothing else; they read no verdict.

#### `LBA-AM6-8` — descriptive reads that decide nothing, including the identification field

**Reported beside the verdict, marked as deciding nothing, with no threshold and no branch reading
any of them:**

- **`LAL-Q4` — identification.** Per row, what he answered and, after the unblind, whether it was
  right: the counts of *no*, of *yes and right*, and of *yes and wrong*, per depth. **It never enters
  the tally, the margin, the bar or any verdict.** A verdict reached on rows he could identify is
  still the verdict; how much weight that leaves it is for the owner to judge, with the count in
  front of him — **not** for the write-up to discount rows by.
- **`LAL-Q3` — strength**: clear picks by strength and by role, per axis (`LBD-AM6-5`'s treatment).
- **`LAL-K`**: rows ticked, per depth and per axis's *no-preference* rows.
- **Computed trade-off rows**: rows on which `LAL-Q1` and `LAL-Q2` name opposite sides.
- **The sealed metrics** of `LBA-AM6-5`, and whether any tracked his picks.

**The unblind script is tested for invariance**: the verdict must be identical under every
assignment of `LAL-Q3`, `LAL-Q4` and `LAL-K`, as `lbl_unblind.py` is for strength.

#### `LBA-AM6-9` — run-once, and nothing carries across listens

**This verdict is run-once and final under `GBL-` §5.** An unwelcome verdict stands; it may not be
re-listened on any protocol, re-tallied on strength, identification or familiarity, or re-read
after `LBA-G5`. A later listen on new pairs is a new amendment and produces a new verdict, never a
correction of this one.

**No verdict carries across listens.** Listen 1 (served against `LBD-A0V`) and listen 2 (`LBD-A0V`
against `LBD-A5V`) both read the tie; **neither says anything about the candidate**, this listen
says nothing about either of their comparisons, and **no transitive claim may be built across the
three**. This verdict also says nothing about `LBA-A3`, any other threshold, the `U` row, `LBA-A9`,
or any map not built; `LBA-R9` stays unreachable (`LBA-AM3-1`) and this listen is not a substitute
for it.

#### `LBA-AM6-10` — barred reads, whatever the verdict

- **Attribution to any one column or subset** (`LBA-AM6-1`): threshold, population, payload, fame
  date, data source — and, within the data column, any one component of the bundle (`LBA-X4`).
- **A population effect without the payload beside it** (§2.1's bar), and a served-map comparison
  attributed to "the similarity data" without `LBA-X5` beside it.
- **Attribution to the ramp or the fame ranking alone** at d10/d20 (`LBA-AM6-1`).
- **Generalisation to the typical journey** (`LBA-X9`), or to the cheaper pairing form — the
  candidate uses ListenBrainz's own pairing (`LBA-D1`), and `LBD-X6`'s logic applies.
- **"Equivalent" from a tie** (`REQ-41`).
- **Any read of the descriptive or sealed quantities as deciding anything** (`LBA-AM6-8`).
- **Any `LBA-G5` outcome as re-reading this verdict**, or this verdict as evidence about `LBA-G5`'s
  criterion. The gate's pre-written criterion is what keeps the two apart (`LBA-AM5`).

#### `LBA-AM6-11` — where things land, and what does NOT change

**Outputs.** The listen's harness, runner brief, pairs, pre-screen output and (later) verdicts in
`builder/analysis/2026-09-22-lba-a6-blind-listen/`, **adapted by copy** from
`builder/analysis/2026-09-10-lbd-blind-listen/`, whose files stay frozen as the record of listens 1
and 2. The sealed mapping and hidden metrics in `.superpowers/lal/`. The owner's `LBA-G5` pair log
(`LBA-AM5`) at the location the runner brief names. The result in a findings note written by the
write-up session.

**What does not change:** every `LBA-` bar value, `LBA-G1`–`LBA-G5` and their criteria, `LBA-D1`–`D3`,
the go ruling, `LBA-AM5`'s order, `LBA-G5`'s period, both `LBL-` verdicts, and `ApiConfig.graph_path`.
**It adopts nothing, changes no default, touches no shipped code, recommends nothing and selects
nothing.** Nothing in it was written with knowledge of any journey this listen could present.

**Identifiers `LBA-AM6` (sub-items `-1`–`-11`), `LAL-` (`LAL-Q1`–`Q4`, `LAL-K`, `LAL-R1`–`R4`),
`LBA-X9`, `LBA-X10`.** Collision-checked 2026-09-22 across every local and remote ref, by
`git grep -lE` over `refs/remotes` and `refs/heads` for `\bLBA-AM6`, `\bLAL-`, `\bLBA-X9` and
`\bLBA-X1[0-9]`: **all free.**

---

### `LBA-AM7` — `LBA-AM6-2`'s pool rebuilt from the owner's extended history, and vetted by him by name

**Dated 2026-09-23. Written by the preparation session, after its first pre-screen ran and before
any code under this amendment has run.** What that session had seen when writing it: the first
pre-screen's **counts** (pool, eligible, drawn, rejections by gate, survivors) and the **twelve drawn
pairs' endpoint names**. It had not opened any per-pair row, length, interior or novelty figure in
`lal_prescreen.json`/`.md`, and it has generated, viewed and been told no journey. **Nothing in this
amendment reads either map except for name-to-MBID membership**, so it cannot steer toward a side.

**The plain question is unchanged.** Every read, gate, depth, question, bar and exposure of
`LBA-AM6` stands. Only **step 1 (the pool) and the familiarity list** change, and with them the
pairs.

#### `LBA-AM7-1` — the defect

Shown the twelve drawn pairs as endpoint names only (`LBA-AM6-2` step 9), **the owner did not
recognise 11 of the 16 endpoints in the eight pairs they occupy** — *"I think some of these artists
are instances where one song by them is on a playlist that I listen to frequently."* Only four of
twelve pairs had two artists he knows. Striking eight exceeds the four reserves, so under
`LBA-AM6-2` the draw stops.

**Cause, verified in source.** The pool (`gbl_pair_candidates.json`, built by `gbl_pairs.py` for
`GBL-`) is ranked by **total minutes played** from `StreamingHistory_music_0.json` — Spotify's short
account-data export — so one song on a frequently played playlist can rank an artist near the top.
Step 1's premise, *"both endpoints are artists he demonstrably knows (`REQ-41`)"*, was never checked
against him. The same list feeds Gate N and ranking key (b) as the familiarity list, which therefore
**under-reads what he has heard** (no pre-2025 history) as well as over-reading what he knows.

The owner's **extended streaming history**, 2014–2026, is on his machine at
`D:\unsung-large-data\Owner's Spotify Extended Streaming History\` (`Streaming_History_Audio_*.json`).
No script in the repo had read it. **It is personal data and carries IP addresses: nothing raw from
it is committed** — only per-artist derived counts.

#### `LBA-AM7-2` — the new pool, fixed before it is built

*Plain: list the artists he has listened to most widely — many different songs, not one song many
times — show him the names, keep only the ones he says he knows, and draw from those.*

1. **Qualifying stream:** an `Audio` record with a `master_metadata_album_artist_name` and
   `ms_played ≥ 30 000` (Spotify's own count-as-a-play threshold). Podcasts and video are not music
   and are skipped.
2. **Per artist** (the name as recorded): `distinct_tracks` — distinct `spotify_track_uri` with a
   qualifying stream; `plays` — qualifying streams; `years` — distinct calendar years with one;
   `minutes`.
3. **Order:** `distinct_tracks` descending, then `plays` descending, then name. **Breadth of
   listening, not volume**, because the defect is exactly one track played many times.
4. **Resolution:** the name is matched with the app's own `artistpath_api.search.normalise` against
   `names` in **both** maps (`gbl_pairs.py`'s rule). Pool-eligible only if it resolves to exactly
   one node in each and **the same MBID** in both. Also excluded: every endpoint `LBA-AM6-2` step 2
   excludes (the three presented listens), unchanged.
5. **The list shown to him:** the first **150** pool-eligible artists in that order, **names only**,
   numbered. **He names every artist on it he does not know;** every one he does not name is taken
   as known, so he reviews all 150. His answer is committed verbatim, with the list, before the
   pre-screen runs.
6. **Pool:** the known artists, in step 3's order. **Pool rank** (ranking key (c)) is the position in
   that pool.
7. **Too few:** if fewer than 12 survive the pre-screen, the **next 100** eligible artists are listed
   for him the same way and appended in order; then the pre-screen reruns over the enlarged pool. It
   is deterministic, so the first pool's pairs are reproduced as the greedy draw's prefix only where
   pairing allows — the rerun's output is the one that stands.

#### `LBA-AM7-3` — the familiarity list, rebuilt

**Every artist with at least one qualifying stream in the extended history**, resolved by
`normalise` against both maps, **every matching node in either map** (homonyms included, as the old
list included `ambiguous`), **plus** every artist he marked as known. Used only to count, never to
exclude — as before. **Over-reading is the safe direction here:** an artist wrongly counted as
familiar can only make Gate N harder to pass and key (a) smaller; it cannot make a pair look more
novel than it is. `LAL-K` still measures the residual on the row.

#### `LBA-AM7-4` — what runs, and in what order

`lal_pool_am7.py` (steps 1–5 and `-3`) and `lal_prescreen_am7.py` (step 6 onward: `LBA-AM6-2` steps
4–9 **unchanged**, importing `lal_prescreen.py`'s committed gate and ranking functions) are committed
**with this amendment, before either runs**. Then: build the list → he names the unknown → commit →
pre-screen → the twelve pairs by endpoint name → **his strike, exactly `LBA-AM6-2` step 9** → pin →
runner. The first draw (`lal_pairs_drawn.json`, `a76ab8b`) is **superseded, kept as the record**; no
journey on it was shown to anyone.

#### `LBA-AM7-5` — disclosed, and deferred with a success condition

**The same premise was unchecked in all three earlier blind listens** (`GBL-`, `LBL-` 1 and 2), whose
endpoints came from the same short export. Their verdicts are **run-once and stand** (`GBL-` §5); this
amendment re-reads none of them. **Owed:** each of the three findings notes' rows in `docs/README.md`
carries a pointer to this sub-item saying their endpoints' familiarity was not confirmed with the
owner. **Condition:** done when those three rows point here. ✅ **DISCHARGED 2026-09-23** — the three rows carry the pointer (`92a4231`).

#### `LBA-AM7-6` — what does NOT change

Every `LBA-AM6` read, bar, gate (L, D, N), depth, question, blind rule, exposure and barred read;
`MIN_INTERIOR`; the 8 + 4 selection; the strike; the harness downstream of `lal_pairs.json`.
`LBA-X9` still applies. **It adopts nothing and changes no default.**

**Identifier `LBA-AM7` (sub-items `-1`–`-6`).** Collision-checked 2026-09-23 by `git grep -lE
'\bLBA-AM7'` over every local and remote ref: **free.**
