# `RCC-` — is the top similarity edge a SHARED RECORDING credit?

**Role: ACTIVE, governing for the `RCC-` probe.** Committed **before any recording data was
fetched**. Successor to `CCR-`, and **not an amendment to it**: `CCR-`'s null stands for what
it measured (`artist-rels`, i.e. band membership) and is not amendable into a different test.

**Why this exists.** `CCR-` returned `null` because its instrument could not see the
hypothesis. MusicBrainz `artist-rels` carries band membership, not shared recording credits.
**Laura Lee — the motivating case — scored `False` on it**: her one documented relation is
Khruangbin, while her top similarity edge is Leon Bridges, from a shared recording
(*Texas Sun*) that `artist-rels` does not carry. This probe asks the question `CCR-` meant to.

**Still not in question, and this probe neither strengthens nor weakens it:** that collaboration
inflates similarity is established from source (`LBS-1`). What is open is whether it explains
the class the owner sees at depth.

---

## 0. The confound that killed the naive design, and how this avoids it

**A session musician is credited on many recordings by construction.** So "does this artist
share a recording with their top partner?" is contaminated: the class would score higher simply
by being on more records, with no bearing on similarity at all. **Normalising by recording
count would be worse** — it would divide out the very property the hypothesis is about.

**The fix is a within-artist control.** For each artist we ask the same question twice, of the
same artist, against two partners drawn from that artist's *own* similar-list:

- their **rank-1** partner (the top similarity edge), and
- a **tail** partner, drawn from **ranks 50–100** of the same list.

Both queries concern one artist, so the artist's recording count, MusicBrainz coverage, era,
genre and prolificacy are **identical across the comparison by construction**. Anything that
differs between rank-1 and tail is a property of *similarity rank*, which is the only thing
under test.

## `RCC-AM1` — the tail partner is defined by RELATIVE position, not absolute rank

**Committed 2026-08-06, before any outcome value was observed.** A first run was started under
the original §0 definition (tail drawn from **absolute** ranks 50–100), stopped after 20
artists, and its partial data **deleted**. Only sampling diagnostics — archived list lengths —
were inspected; **no `rank1_shared` or `tail_shared` value was read**, so nothing below is
shaped by a result.

**What broke.** Requiring an absolute rank-50–100 partner requires a list of ≥ 100 entries.
Archived list length is **itself a property of the arm**:

| Arm | Median archived list length | Usable under the original rule |
|---|---|---|
| CLASS | 100 | 183 / 200 (91.5 %) |
| CONTROL-OBSCURE | 18 | **15 / 200 (7.5 %)** |

**Selecting on list length selected the control arm away**, and the 15 survivors are atypical
of it by construction. `RCC-C2` would have compared 183 artists against 15 unrepresentative
ones, and `RCC-C1`'s CLASS reading would have been fine while the between-arm reading was
quietly worthless.

**The corrected rule.** The tail partner is the neighbour at index
`floor(0.8 × (L − 1))` of the artist's **own** list of length `L`, requiring `L ≥ 10` so that
rank 1 and the tail are meaningfully separated. Artists with `L < 10` are skipped and counted.

**The trade-off, stated rather than hidden.** Under this rule the tail sits at a different
**absolute** rank in each arm (≈ 80 for CLASS, ≈ 14 for CONTROL) while sitting at the same
**relative** depth. That is the correct choice *because* list length is an arm property:
matching absolute rank is precisely what destroyed the control. **`RCC-C2` therefore compares
"top of your list vs bottom of your list" across arms, not "rank 1 vs rank 75" across arms**,
and every citation of `RCC-C2` carries that sentence.

**`RCC-C1` is unaffected in kind** — it was within-artist before and remains within-artist.

## 1. Sample — reused from `CCR-` deliberately

**The same 400 artists, same arms, same seed (`20260806`)**, read from
`builder/analysis/2026-08-06-ccr-relationships/ccr_raw.json`.

| Arm | `fame_lb_pctl` | `pop_raw_pctl` |
|---|---|---|
| CLASS | < 0.20 | > 0.80 |
| CONTROL-OBSCURE | < 0.20 | < 0.40 |

Reused so that sampling variance cannot be offered as an explanation for any difference
between `CCR-`'s result and this one. Artists whose archived list is shorter than 100 entries
are skipped (no tail partner exists) and the skip count is reported.

## 2. What is fetched

Two requests per artist, both against the same endpoint:

```
/ws/2/recording?query=arid:{artist}%20AND%20arid:{partner}&fmt=json&limit=1
```

read as **`count > 0` ⇒ the two share at least one recording credit**. Rate-limited, one run,
**both arms and both rank positions interleaved** so any mid-run change at MusicBrainz cannot
land on one cell only.

## 3. Gate

**`RCC-G1` (query sanity).** The rank-1 and tail queries must both return a well-formed
`count` for ≥ 90 % of attempted artists in each arm.

> **Plain sentence:** *did the search actually answer, for both partners, for most artists?*

Below 90 % in either arm the run is **incomplete and is reported, not read** — including the
null, since the class is the sparser population and would thin first under systematic failure.

## 4. Outcomes

Let **lift** = P(shares a recording | rank-1 partner) − P(shares a recording | tail partner),
computed **within an arm**.

**`RCC-C1` — the within-artist lift, in CLASS.** Primary.

> **Plain sentence, fixed here and quoted thereafter:** *is the artist the app rates as most
> similar more likely to be someone they are credited on a recording with, than an artist
> further down that same list?*

| `RCC-C1` lift | Branch | Read |
|---|---|---|
| **≥ +20 points** | `supported` | Top similarity edges are co-credit edges. The owner's mechanism is operating on this class. |
| **+10 to +20** | `equivocal` | **Neither supported nor null. No default is named and none may be supplied later.** |
| **< +10 points** | `null` | The top edge is no more a co-credit than an edge fifty places down it. |

**`RCC-C2` — is it specific to the class?** CLASS lift − CONTROL lift.

> **Plain sentence:** *does this happen more to the central-but-unlistened artists than to
> ordinary obscure ones?*

- **≥ +15 points** → `class_specific`.
- **< +15 points** → `general`. **This is a real and reportable outcome, not a failure**: it
  would mean co-credit shapes top similarity edges across the graph, and the class is where it
  becomes *visible* rather than where it happens.

**`RCC-C1` and `RCC-C2` are read independently.** `RCC-C1` may be `supported` while `RCC-C2` is
`general`; that combination is meaningful and must not be collapsed into either label alone.

## 5. The read of every result, including the null

- **`supported` + `class_specific`** — the mechanism explains the class. Licenses **no remedy**:
  dropping artists is already ruled out by the owner, and the edge-level response is `B`
  (the `p99_log_clip` rescale), which is independent of this probe and proceeds regardless.
- **`supported` + `general`** — the mechanism is real but graph-wide. **Raises the value of `B`
  specifically**, because a general distortion is exactly what a rescale can act on and a
  filter cannot.
- **`equivocal`** — no action, and **no second threshold may be reached for**.
- **`null`** — the top similarity edge is not a co-credit artefact. The class remains real and
  measured (the depth census is untouched by this), and **the Laura Lee instance survives**: one
  proven case was never the population claim. `B` proceeds unchanged.

**Barred reads, travelling with every citation:**

1. **A shared recording credit does not prove the similarity score came from it.** This measures
   association, never causation. The causal claim rests on `LBS-1`, not on this.
2. **MusicBrainz recording coverage is incomplete**, so both cells are **floors**. The
   within-artist design makes the *difference* interpretable; the absolute rates are not.
3. **No adoption follows from any branch.** No default, weight or filter changes on this result.
4. **This says nothing about whether these artists are good recommendations.**

## 6. Run state a read presupposes

Both cells (rank-1 and tail), both arms, at the achieved n reported alongside the skip count.
**A partial run supports no branch.**
