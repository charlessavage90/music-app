# Derivations from the 2026-07-25 consulting session — one verified, six open (one since resolved)

**Role: AUTHORITATIVE for `DRV-1` only** (a verification this session performed). **Everything
else is a labelled hypothesis with a named check, and none of it is a finding.**

It exists because a session was asked what it knew that was not written down, and the answer
was "several things." Reasoning that lives only in a transcript is the failure mode this
project has been bitten by repeatedly — F1's lapsed deferral, `builder/README.md`'s rewritten
trigger. This is that reasoning, recorded at the strength it actually has.

**Path-quality work is paused. Nothing here is a resume signal, an arm, or a proposal.**
`DRV-1` was established from checksums and commit timestamps; no graph was loaded, no path
routed, no rebuild.

Identifiers are namespaced `DRV-n` — disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-`, `MKS-`,
`ASC-` and `BYP-`.

---

## 1. Verified — the graph the diagnosis was measured on is not the graph we run

> **⚠ NARROWED 2026-07-26 — `DRV-1`'s range was over-broad. The exposed sections are §2.11
> and §2.12, not §2.9–§2.12.** The narrowing was established from committed documents plus
> the two manifest sidecars; **nothing was re-run, re-measured or rebuilt.**
>
> - **§2.10 is not exposed, and its reciprocity attribution applies to the adopted
>   artifact.** Its "§2.8's tie-break is not this" table measures the adopted artifact's own
>   topology, under its own name: the adoption record
>   (`2026-07-23-tiebreak-fix-adoption.md`) states the fix's topology is that of **§2.8 Arm 2
>   = `rankfix`'s**; Phase 1 log **§2.13 C2** records Arm 2 and `rankfix` as topologically
>   identical and gives that as the reason a second artifact was never built; and the
>   manifest sidecars for `graph-t15-tiebreakfix.bin` and `graph-t15-rankfix.bin` carry the
>   **same `artists` and `edges` values**, differing only in `similarity_rescale`. §2.10's
>   figures are computed against a **fixed pre-cap in-degree popularity reference** — that is
>   its own circularity correction — so they are score-independent and do not turn on which
>   rescale an artifact emits. The row therefore *is* a measurement of the graph in use.
> - **§2.9 was never supported by the evidence below either.** The three scripts in the
>   evidence table are §2.11's, §2.12's and `coherence_probe.py`; none is §2.9's or §2.10's.
>   §2.9 needs no provenance caveat regardless: **§2.10 supersedes its figures and §2.12
>   retracts its central claim**, so it is already barred from quotation on its own terms.
> - **What is unchanged:** everything below about §2.11 and §2.12, including the concrete
>   Beatles tell, `DRV-2`'s direction-of-error argument, and the recommended re-run. The two
>   scripts that would settle it are still `known_viability.py` and `exits_by_band.py`.

**`DRV-1` — ~~every table in Phase 1 log §2.9–§2.12~~ §2.11's and §2.12's tables were computed
on `graph-t15-capfix.bin`. The app has run `graph-t15-tiebreakfix.bin` since 2026-07-23, and
neither has been recomputed on it.** *(Plain: the measurements behind the project's central
diagnosis were taken on an older version of the graph, six hours before the version we
actually use was adopted.)*

**Evidence, all of it mechanical:**

| | |
|---|---|
| `known_viability.py` (§2.12's table) | asserts `graph-t15-capfix.bin`, sha256 `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237` |
| `exits_by_band.py` (§2.11's table) | asserts the same artifact and checksum |
| `coherence_probe.py` | same |
| Adopted artifact | `graph-t15-tiebreakfix.bin` — **different checksum**, owned by `2026-07-23-tiebreak-fix-adoption.md`; not restated here |
| `known_viability.py` first committed | `af04922`, **2026-07-23 04:13:26 −0400** — the same commit as §2.12 |
| Tie-break artifact adopted | `7bd4e8e`, **2026-07-23 10:21:06 −0400** — **six hours later** |

**The concrete tell, and it is visible in the prose without any of the above:** §2.12's worked
example is *"The Beatles have 7 of 7 neighbours admissible"*, and §2.11 lists the Beatles at
degree 7 as a tie-break victim. `2026-07-25-mutual-knn-stranding.md` `MKS-5` records that on the
adopted artifact **the Beatles hold the full 50**. The document's headline example is false
about the running app.

**`DRV-2` — the likely direction of the error, and it is not alarming. INFERENCE.** *(Plain:
re-measuring would probably strengthen §2.12's conclusion rather than overturn it.)*

§2.12 concludes *"cost-function problem, not graph problem"* on three legs. Only two are
exposed:

- **The pricing arithmetic is artifact-independent** — a raw-popularity delta against a
  per-hop weight. Untouched.
- **The availability table is exposed**, and the tie-break fix *adds* neighbours to exactly the
  famous artists in its top rows (Beatles 7 → 50). More neighbours means more admissible
  substitutes, so its conclusion "`known` is satisfiable, most of all for famous artists" gets
  **stronger**.
- **The hop-distance table is exposed** and moves the same way — more edges cannot lengthen
  shortest paths.

**So `DRV-1` is a provenance defect, not a refutation.** What it does invalidate is **any
specific figure from ~~§2.9–§2.12~~ §2.11 or §2.12 quoted as a fact about the current app** —
and the doc map's Current State did quote them as settled *(the doc map was corrected, and the
range narrowed, 2026-07-26 — see the notice above)*.

**What would settle it:** re-run `known_viability.py` and `exits_by_band.py` against the
adopted artifact. Both are committed, both are read-only, neither needs a rebuild. The scripts
already gate on a checksum, so the assertion is the only line that changes.

## 2. Open derivations — hypotheses, each with its check

None of these has been measured. Each is stated so it can be killed cheaply.

**`DRV-3` — the descent is a round trip, and §2.12 priced it one-way.** *(Plain: to show you a
less famous artist in the middle of a journey, the app has to pay to go down there **and** pay
again to climb back to your destination — the record only ever counted the trip down.)*

§2.12 prices Beatles → Paul Simon at a raw-popularity delta it calls twenty-four hops' worth of
`w_hop`. But an artist in the *interior* is entered and left, so the real ratio is roughly
**double**. If it holds it accounts for three things at once: why `w_floor` is inert, why there
is no cheap *partial* dive, and why fifteen repricing arms plus a full-strength toll all failed
to move the outcome.

**Check:** compute the summed `w_jump` cost of a descend-and-return against a flat route, on the
adopted artifact. **Weakest link, stated plainly:** this session never read `pathfinding.py` —
only CLAUDE.md's transcription of the cost function. If that transcription is stale the
arithmetic is worthless.

**`DRV-4` — a degree-1 artist can never be an interior card, in any path.** *(Plain: an artist
with only one connection can only ever be shown as one of the two artists you typed in — the
app can never introduce you to them.)* An interior card needs a neighbour on each side; a
degree-1 node has one neighbour total. `MKS-6` states this for *endpoint* pairs; the general
form is stronger and is not in the record. Combined with `MKS-3`'s 9.3 %, it bounds how much of
the catalogue is undeliverable as a discovery.

**Check:** none needed for the structural claim — it is a graph fact. What needs checking is
`MKS-3`'s population (crawled artists only, or all artifact nodes), which decides the size.

> **✅ RESOLVED 2026-07-26 by `2026-07-26-low-degree-census.md`** — the one item in §2 that is
> no longer open. The structural claim stands and is no longer only structural: the census
> **measures** the population `DRV-4` described, and it closes the check named above — the two
> candidate populations are **nested, not alternatives** (every artifact node is a crawled
> artist, from the pipeline's own ordering), and the resulting fractions differ immaterially.
> **Figures belong to `builder/analysis/2026-07-26-low-degree-census/`; none is restated
> here.** Two later runs bear on the same question from the delivery side rather than the
> structural one — `findings/2026-07-26-committed-walk-deliverability.md` and its §7 — and
> neither is required by `DRV-4`. **This resolves `DRV-4` only; `DRV-3` and `DRV-5`–`DRV-7`
> remain open at hypothesis strength**, and §4's warning that `DRV-5` is among the likeliest
> to fail is untouched.

**`DRV-5` — §2.12's admissible-substitute counts may be inflated by leaves.** *(Plain: the
record counted how many less-famous neighbours a famous artist has, but never asked whether
those neighbours lead anywhere — and one that doesn't can never actually be used.)* That table
gates on a popularity drop and a similarity threshold. It does not test onward connectivity, and
by `DRV-4` a degree-1 substitute cannot serve mid-path however well it scores.

**Check:** re-run the same script with a degree ≥ 2 filter and compare. Compounds with `DRV-1`,
since both bear on the same table.

**`DRV-6` — the staircase model.** *(Plain: the both-ways rule didn't cut obscure artists off —
it removed the direct shortcuts to them, leaving a stepladder you have to walk down one rung at
a time.)* Mutual k-NN does not sever fame tiers; it removes *shortcuts between distant* tiers
while leaving the short steps between adjacent ones, because comparable-fame artists reciprocate
easily. This is the model that generated `2026-07-25-bypass-depth-use-run.md` `BYP-11`
(descent happens across genres, because within-genre rungs are the stranded ones) and it
reconciles §2.11's zero-obscure-neighbours with §2.12's obscure-region-is-2–3-hops.

**Check:** for a set of famous artists, measure the popularity distribution of neighbours at
hop 1, 2 and 3. A staircase predicts a smooth descent; a wall predicts a cliff.

**`DRV-7` — three discriminating signals go flat at exactly the famous endpoints, leaving
popularity alone to choose.** *(Plain: at the two artists you picked, everything the app uses to
tell good next-steps from bad stops working, except fame.)* Similarity is saturated by the p99
clip; the degree-hub penalty applies **uniformly** when every available neighbour is a hub and
therefore changes no choice; avoidance is empty on a fresh walk. The handoff's §2 reaches the
same place for two of the three — **the hub-penalty-uniformity step is this session's and is
otherwise unrecorded.**

**Check:** at the pre-registered endpoints, count how many of the 50 neighbours are in the
top 1 % by degree. If it is all of them, the term is provably inert there.

## 3. This session's opinions, labelled as opinions

Recorded because withholding them is its own kind of framing, and separated from §1–§2 so they
cannot be mistaken for findings.

- **`BYP-11` is the most consequential thing these two runs produced** — more so than
  `2026-07-25-router-ascent-gradient.md`. "The app can only reach unfamiliar artists by going
  somewhere musically unrelated" is a product statement that can be acted on, and it points at
  the graph rather than the pricing.
- **This session would advise against resuming path work with the builder-side p99 rescale.**
  The ascent finding's §6 deliberately stops short of saying so; a findings document that
  pre-empts the owner's decision is a recommendation wearing a finding's clothes. It is his
  call, and this is a session's view, not an input he asked for.

## 4. Calibration — how much to trust §2

**This session made three confident wrong claims, and the owner caught all three:** that
repeated bypassing never surfaces an unfamiliar artist; that path length oscillates without
progressing; and that the artist card displays the MusicBrainz disambiguation.

**All three share a cause: reasoning over a summary when the underlying data was available.**
The oscillation call was made on a selectively-logged sample; the obscurity floor rested on an
unverified artist identity; the card claim was an assumption about code that was never read.

**Applied to §2 above:** `DRV-3` and `DRV-5` are the two most likely to fail the same way —
`DRV-3` because the cost function was never read at source, `DRV-5` because §2.12's script was
never opened. `DRV-4` and `DRV-7` are structural and cheap to confirm — **and `DRV-4` since has
been, which is the one item in §2 that has been closed rather than merely restated.** `DRV-1`
is the only item here that was verified *at the time of writing*, which is why it is the only
one marked authoritative.

**The pattern is also the argument for the checks above being run before any of this is
built on.**
