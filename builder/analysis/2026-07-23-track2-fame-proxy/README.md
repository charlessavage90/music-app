# Fame-proxy validation (P4 / pre-registration §5)

**Owns its figures.** Cite this file by section; do not restate its numbers elsewhere.

Governing document: [`specs/2026-07-23-track2-preregistration.md`](../../../docs/superpowers/specs/2026-07-23-track2-preregistration.md) §5,
as amended by **A10** (§9). Artifact asserted in every script:
`graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`.

**Status (2026-07-24): COMPLETE for Deezer, and Deezer FAILED.** The owner labelled the
29-artist sample blind; `nb_fan` was fetched and scored; **two of the four pre-registered
falsifiers fired** (see §4). The pre-registered response is to re-run the identical protocol
against Wikipedia pageviews, same labels — **not yet built.** Figures owned here and in
`score.json`; the execution log cites them as a gate outcome and does not re-derive.

---

## 1. Two defects in §5's sample definition, found before any label was collected

Both would have been unrecoverable afterwards, which is the same argument that moved A6
earlier: the owner's labels are reusable across *proxies* but not across *samples*.

### 1.1 S1 and S3 overlap by four artists — the sample is 29 distinct, not ~33

§5 defines S3 as "F6's named reaches (Max Richter, Ólafur Arnalds) and the log §2.11
insular-stratum artists (saib., Purrple Cat, idealism, Miami Nights 1984)". **All four of
the latter are already in S1's nine names.** Counted as written, the sample is
9 + 12 + 6 + 6 = 33; distinct, it is **29**.

This is not cosmetic. Every statistic in §5 is reported **per stratum as well as pooled**,
so four artists would have contributed twice to the pooled AUC, the pooled inversion rate
and B_unk, and would have appeared in two strata whose per-stratum readings §5 interprets
differently — S1 as the anchor for the unknown end, S3 as a live test of §2.11's inference.

**Resolved (A10):** the four are **S1 members**, and S3 is the two F6 reaches only. S3's
stated purpose is not lost — it was "directly tests §2.11's inference that these would not
feel famous to the owner", and S1 tests exactly that, with nine artists instead of four.

**Consequences, stated because they change two pre-registered quantities:**

- **S3 is now n = 2.** Per-stratum statistics on it are uninformative and will be reported
  as counts only, not as an AUC. The stratum survives to keep Max Richter and Ólafur
  Arnalds — the two artists the owner actually reached in F6 — individually visible.
- **The match-failure falsifier gets stricter.** "> 20 % of the sample" is 5.8 of 29 rather
  than 6.6 of 33, so the falsifier now fires at **6** failures where it previously fired at
  **7**. Left as a proportion rather than renegotiated, since the proportion is what was
  pre-registered.

### 1.2 §5's claim that S1's labels already exist is false at the granularity §5 needs

§5 says of the nine names: *"Their labels exist; they anchor the 'unknown' end."*
They do not. The record holds exactly one thing —
[`TEST-QUEUE.md`](../../../docs/superpowers/TEST-QUEUE.md), 2026-07-23 entry:
**"No, mostly unknown."** That is a *collective* verdict on nine artists. §5's scoring
needs each artist assigned to one of three buckets (*know well / heard of / never heard
of*), and:

- it gives no per-artist assignment;
- it does not separate *heard of* from *never heard of* at all, and that boundary is where
  B_unk is computed;
- the word **"mostly"** positively implies at least one of the nine was **not** unknown,
  with no record of which one.

**Resolved (A10):** the nine are labelled by the owner alongside everyone else. The cost is
nine extra names on one list, not a second session. **S1 is no longer assumed to anchor the
unknown end** — that becomes something the labels show or fail to show, which is strictly
more informative than assuming it.

The original verdict is **not retracted**. It settled what it was asked — §2.11's inference
that in-graph popularity does not mean fame at the top — and that remains settled. It was
never a three-bucket labelling and should not have been carried as one.

---

## 2. The sample, fixed

Produced by [`fix_sample.py`](fix_sample.py) → [`sample.json`](sample.json). Rerunning it
reproduces the list exactly; it routes no paths and fetches nothing.

**S2's twelve were not hand-picked.** §5 names three exemplars and otherwise says only
"chosen to span the strata the record identifies", which does not pin a set. The rule is
fixed in the script's docstring and applied mechanically: the three named exemplars, then
each judged pair's least / most / median in-graph-popular interior, filled in that order,
skipping artists already selected, ties on lowest MBID.

**In-graph popularity is used only to spread the sample, never to score it.** Selecting on
`pop_raw` is safe precisely because P4 exists to find out whether `pop_raw` means anything
about fame — and the selection is evidence in its own right:

| Judged pair | interiors | least popular | most popular |
|---|---|---|---|
| Miles Davis → Daft Punk | 36 | **Whitney Houston 0.5124** | **Nick Drake 0.7400** |
| The Shins → Wishbone Ash | 47 | **Whitney Houston 0.5124** | AC/DC 0.8056 |
| Metallica → Taylor Swift | 36 | Death Cab for Cutie 0.5428 | Nirvana 0.8824 |

**Whitney Houston is the least in-graph-popular interior of two of the three pairs, and
Nick Drake is the most popular of one** — above Frank Sinatra, Ella Fitzgerald and Elvis
Presley, all of which are interiors of that same pair. Anyone would rank those two the
other way round on fame. This is Phase 1 log §2.11 reproduced inside the sample §5 built
to test it, and it means S2 spans a fame/popularity disagreement rather than merely a
popularity range. Recorded as an observation, not a finding: n is three pairs, and it is
post-hoc with respect to the selection rule, which was fixed before these values were read.

**`blink‐182`** in the judged-listen record is spelled with U+2010 HYPHEN, not ASCII
`-`. It did not reach the final twelve, but it confirms P5's "record's own hyphen trap" is
present in live data and not hypothetical — the normalisation rule must fold Unicode
punctuation before matching, as P5 requires.

---

## 3. Protocol, as executed

1. **Owner labelled all 29 into three buckets, blind** (2026-07-23). Recorded in
   `labels.json` via `record_labels.py`, keyed by `blind_order.json` position so the
   answer→artist→stratum mapping is auditable. No fan count existed on the machine when he
   was asked.
2. **`nb_fan` fetched via Deezer artist search** (`fetch_fame.py`), exact match after P5
   normalisation (unit-tested in `test_p5.py`, including the U+2010 trap). Does **not** reuse
   `clips.py` (§0). `--probe` first confirmed §0's external assumption out-of-sample —
   `nb_fan` present on Radiohead / Portishead / Sault, 27k–4.06M.
3. **Scored** per §5 as amended by A6 (`score.py` → `score.json`).

## 4. Result — Deezer `nb_fan` is UNFIT (§5). Figures owned here.

| §5 test | Result | Pre-registered falsifier | |
|---|---|---|---|
| **Primary — AUC(know-well > heard-of), S4 excluded** | **0.680** (n=5 vs 5) | < 0.70 | **FIRES** |
| **Catastrophic inversions outside S4** | **2** | > 1 | **FIRES** |
| Spearman ρ, pooled (diagnostic, non-gating) | 0.697 | — | — |
| B_unk (band separation) | valid at 199,337 (81.25 % never-heard below) | none exists | clear |
| Match failure | 3.4 % (CROOVE only, an S4 off-platform case) | > 20 % (6 of 29) | clear |

The two inversions: **Paul Simon (244,072 fans)** and **Death Cab for Cutie (199,337)** are
labelled *know well* but sit below **Diana Krall (833,167)**, labelled *never heard of*.
Per-stratum Spearman: S1/S3 single-bucket (undefined), S2 0.416, S4 0.791.

**Mechanism — a Deezer market/genre skew, not noise.** Paul Simon and Death Cab are
under-followed on Deezer relative to their fame; Diana Krall (jazz-pop, older record-buying
audience) is over-followed relative to how known she is. This is popularity ≠ fame (Phase 1
log §2.11) on a third population — after in-graph popularity and the path-level trace
(execution log, step-43).

**The AUC miss (0.68 vs 0.70) was not argued away.** The threshold was committed before the
labels existed precisely so a near-miss cannot be relitigated post-hoc. The inversion
falsifier fired outright. Both mean `nb_fan` is unfit at this granularity.

**Two things the labels themselves confirmed** (both vindicating A10): S1 came back **all
nine "never heard of"** — the earlier collective "mostly unknown" was *fully* unknown at
three-bucket granularity; and **Nick Drake** (most in-graph-popular interior of pair 1) drew
only *heard of* while **Whitney Houston** (least popular of two pairs) drew *know well* — the
popularity/fame inversion the mechanical S2 selection surfaced, confirmed in the owner's own
judgement.

## 5. Next — Wikipedia pageviews (pre-registered §5 fallback), NOT built

Same labels (committed, reusable across proxies), same 29 names, same scoring — `score.py`
is proxy-agnostic and reads any `fan_counts.json`-shaped file. The open work is **name →
article resolution**, which Deezer did not have: English-Wikipedia title lookup with
disambiguation and cross-language cases the sample deliberately contains (林俊傑 → "JJ Lin";
lo-fi acts that may have **no article**, which is a legitimate match failure, not something
to force). Fix and assert the pageviews window before fetching, exactly as Deezer fixed
exact-match-after-P5 first. Match failure > 6 of 29 is still a falsifier.

**If Wikipedia also fails**, the §5 terminal fallback is owner-labelling of every
evaluated-path artist — real owner time, and **his** decision. Not before.
