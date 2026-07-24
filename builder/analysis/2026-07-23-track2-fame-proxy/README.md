# Fame-proxy validation (P4 / pre-registration §5)

**Owns its figures.** Cite this file by section; do not restate its numbers elsewhere.

Governing document: [`specs/2026-07-23-track2-preregistration.md`](../../../docs/superpowers/specs/2026-07-23-track2-preregistration.md) §5,
as amended by **A10** (§9). Artifact asserted in every script:
`graph-t15-tiebreakfix.bin`, sha256 `4cb84ef9…b061dc8`.

**Status: sample fixed, labels not yet collected, nothing fetched.** No fan count exists
on this machine, which is the state §5's protocol requires at the moment the owner is asked.

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

## 3. What happens next, in order

1. **Owner labels all 29 into three buckets, blind** — no fan counts exist yet, and the
   session collecting the labels holds none.
2. **Fetch `nb_fan` via Deezer artist search**, exact match after P5 normalisation
   (NFKC fold + Unicode-punctuation folding). **Must not reuse `api/.../clips.py`**, which
   calls Deezer *track* search first-hit with no name verification (§0) — that is the C1
   wrong-artist failure mode in the code.
3. **Score per §5 as amended by A6:** AUC on *know well* vs *heard of* (S4 excluded) as the
   primary falsifier; tie-corrected Spearman as a non-gating diagnostic; catastrophic
   inversions as a per-stratum rate with S4 read as Attack 3 blind spots; B_unk over the
   full sample including S4.

**That `nb_fan` exists on Deezer artist objects remains an external assumption**, flagged
as such in §0 and verified by nothing in this repo. Step 2 confirms or refutes it, and it
is the cheapest thing in the chain to check — but it is not checked yet, and nothing should
depend on it until it is.
