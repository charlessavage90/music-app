# `LBD-AM1` — is the residual set reachable by the `LBD-` track at all?

**Role: FIGURES OWNER for `LBD-AM1`'s reachability read. ACTIVE.** Every figure below is owned
here and is **cited elsewhere, never restated** — including in the amendment that commissioned
it. Raw record: [`lbd_am1_reachability.json`](lbd_am1_reachability.json); harness:
[`lbd_am1_reachability.py`](lbd_am1_reachability.py); log beside them.

**Written 2026-09-07, before any `LBD-` arm had run.**

**Owns no other figures.** Task 1's whole-set supply read is owned by
[`../2026-09-07-lbd-inputs/README.md`](../2026-09-07-lbd-inputs/README.md) §2. The residual
set's construction and every degree figure behind it are owned by
[`../2026-09-07-degree-floor-at-admission/README.md`](../2026-09-07-degree-floor-at-admission/README.md).
Both are cited here and neither is restated.

---

## 1. What this answers, and why it runs now

`LBD-AM1` amends
[`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](../../docs/superpowers/specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
§3 to report `LBD-C2a` **stratified** into the **residual set** — the `CXR`-added artists still
at two or fewer connections when our own degree ceiling does not bind — and its complement.
The residual set is the part of the dead-end problem **raising the degree ceiling cannot
reach**, and so the part `LBD-` addresses.

⚠ **That is narrower than "no rule of ours can reach them."** Both probes held the union
width at `union_top_j = 50` and kept the drop lists; the top-*j* cut deletes a large share of
candidate edges before the degree trim runs at all (figures owned by the ceiling probe's §6).
**No arm has varied the union width**, so whether it would reach this stratum is
**unmeasured** and nothing here rules it out.

That makes one question a **bound on the whole track**: an artist nobody in ListenBrainz's
corpus played can gain no edge at any threshold and any cap, so a null over such artists would
say nothing about either explanation the track contrasts. Task 1 answered this for the added
set as a whole and it is the reason `R6` and `R7` are distinguishable at all. **It has not been
asked of the residual stratum, and asking it at Task 4 would be asking it after the expensive
work.** One join answers it now.

## 2. Inputs, pinned

| input | identity |
|---|---|
| residual list, as produced by the `DFA-` probe | `dfa_residual_mbids.txt`, sha256 `fa8d85cc…b4f43a08` |
| the same list, pinned beside the other fixed sets | `D:\unsung-large-data\lbd-inputs\cxr_residual_mbids.txt`, same sha256 |
| the `DFA-` record it was extracted from | `dfa_benefit_identity.json`, sha256 `f10b3329…e2f26675` |
| Task 1's added set | `cxr_added_mbids.txt`, sha256 `bfed95ef…59a4339` *(cited from Task 1's README §1)* |
| Task 1's per-artist supply output | `cxr_added_dump_supply.parquet`, sha256 `9644d603…2a6b4d6e` |

**Three structural checks run before any figure**, and each raises rather than reports: the
residual list must be a **subset** of the pinned added set (no stray MBIDs), its length must
equal the count the `DFA-` record committed, and the copy written to the pinned directory must
hash equal to its source. All three passed.

**One extraction note, stated because it would otherwise read as a claim the record supports.**
`dfa_benefit_identity.json` as first committed held **counts only, no MBIDs**. The list was
produced by re-running that probe's own committed script with list emission added — the same
code path, the same three builds — and **every pre-existing value in that record reproduced
exactly**, with `mbid_lists` the only new key. That reproduction is the evidence the list is
the same object the counts describe.

---

# MEASURED

## 3. How much of the residual set is in the corpus at all

**The minimum is arithmetic on ListenBrainz's own SQL, not an estimate** — a pair needs at
least **4 distinct listeners** before it can clear `ALG-B`'s threshold at all. That figure and
its derivation are Task 1's, cited here.

| | **residual set** | complement | 
|---|---:|---:|
| artists | **5,967** | 23,925 |
| present in the corpus | 5,959 | 23,889 |
| **absent entirely** | **8 (0.13 %)** | 36 (0.15 %) |
| **≥ 4 distinct listeners** | **5,947 (99.67 %)** | 23,831 (99.61 %) |
| ≥ 10 distinct listeners | 5,894 | 23,706 |
| ≥ 50 distinct listeners | 4,178 | 20,590 |
| distinct listeners over those present — p10 / median / p90 | **26 / 81 / 321** | 41 / 140 / 468 |

## 4. What this establishes

**Absence is not a bound on this track, and the residual set is not the part that is missing.**
99.67 % of the residual artists have at least the four distinct listeners a pair
mathematically requires, which is **marginally higher** than the complement's 99.61 %, and only
8 of them are absent from the corpus entirely. Had the residual set been largely absent, the
track's central read would have been unanswerable for exactly the artists it exists to serve,
and that would have surfaced at Task 4 after the expensive pass. It is not.

**They are, however, listened to less.** The median residual artist has 81 distinct listeners
against the complement's 140, and the gap runs the length of the distribution. That is
directionally what one expects of artists that stayed sparse, it is **not** a reachability
bound, and it is worth carrying into the read: a smaller listener base leaves less room for the
co-occurrence a pair actually needs.

# WHAT IS NOT ESTABLISHED HERE

- **Having enough listeners is necessary, not sufficient, and the gap is the whole of the
  track's second stage.** A pair's score needs listeners who played **both** artists inside one
  session. **Nothing here measures co-occurrence.** This read raises the prior that supply
  exists; it does not establish it, and **it must not be cited as evidence that any arm will
  move `LBD-C2`.** The direction it settles is the negative one: a residual null cannot be
  explained away by absence.
- **The residual set was measured on one population under one cap rule** and inherits every
  caveat of the probe that produced it. It is **a pinned MBID list, not a claim about any other
  build**, and it must not be re-derived per arm or transferred to a different lineage.
- **Task 1's denominator caveat carries over unchanged.** Membership is read from
  `artist_credit_mbids` while ListenBrainz's own job joins `artist_credit_id`; the two were not
  compared, and a small disagreement at the obscure end would move the 0.13 % rather than the
  99.67 %.
- **Nothing here is about any cap rule.** The candidate fix for the *complement* — the artists
  a non-binding ceiling does rescue — sits outside this track entirely. Design §9 keeps the
  cap-rule decision parked and the owner's, and **this read proposes none, runs none and
  depends on none.**
- **No arm has run.** This is an input read, and it adds no gate, no effect size and no
  threshold to anything.
