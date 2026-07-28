# The router climbs — a re-reading of A17(c), 2026-07-25

**Role: ACTIVE.** A re-reading of a measurement already in the record, **not a new one.**
Nothing was run, rebuilt, measured or adopted to produce this document.

**It owns no figures.** Every number it discusses is owned by
`../../../builder/analysis/2026-07-24-track2-p8b-harness-review/` and is quoted in the Track 2
pre-registration's **A17(c)** (`../specs/2026-07-23-track2-preregistration.md`). Cite those.
This document exists because that measurement is currently reachable only as a footnote
bounding an arm nobody adopted, and it says something larger than the use it was put to.

**Path-quality work is paused by owner decision, 2026-07-25. This is not a resume signal**
and proposes no arm, no rebuild and no threshold. It raises one hypothesis and names the
cheapest thing that would kill it.

Identifiers are namespaced `ASC-n` — disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-` and
`MKS-`. Each carries its plain-language sentence, fixed here.

---

## 1. What the measurement says

A17(c) was written to bound how the corner arm `X` may be read. To do that, the P8b harness
review measured, one hop out from every node in the adopted artifact, **how often the
cheapest available hop moves toward a more popular artist** — for the production-like arm
`A0`, for `X`, and against the share of the graph's own directed edges that point upward.

**`ASC-1` — the router climbs about four times in five, where the graph itself offers a coin
flip.** *(Plain: from any artist, the cheapest next step is usually toward someone more
famous — far more often than the map of connections would produce on its own.)*

This is the clean result and the one everything else rests on. It is a **single-arm
measurement against a structural null**: no arm-to-arm contrast, therefore no confound. The
gap between the production-like arm's ascent rate and chance is large, and it is a property
of the cost function, not of the graph's wiring. Figures: A17(c).

**`ASC-2` — the sweep's most aggressive dive-cheapening corner does not descend more. It
ascends more.** *(Plain: the setting built to make heading toward obscure artists as cheap as
possible still headed toward famous ones, slightly harder than the normal setting did.)*

**This contrast is confounded and must not be attributed to any single knob.** `X` differs
from `A0` in **three** columns of §1.4's factor table — jump currency, jump weight, and the
similarity weight. Its isolating baseline is `A7`, and that contrast was not measured. So
`ASC-2` supports "the corner arm does not dive" and **nothing about why**. A17(c) uses it
correctly, for exactly that.

## 2. What I infer from it, labelled as inference

**`ASC-3` — the upward pull probably does not originate in the popularity terms, because it
survives the full span of the sweep's repricing.** *(Plain: fifteen attempts at changing what
the app charges for moving between famous and obscure artists never removed the pull toward
famous ones, which suggests the pull is coming from somewhere those attempts never touched.)*

The reasoning, so it can be disagreed with:

- Track 2 varied the jump term's **currency** and **magnitude**, the similarity **weight**,
  the floor, and a ceiling toll (§1.3, §1.4). Track 2F varied the toll's magnitude over eight
  points to 7,500 × `w_hop`.
- None of these is **directional**. The jump term is `w_jump·|Δpop_raw|` — an absolute value,
  stated as symmetric in A17(c). The toll binds on a property of the edge. The floor arms are
  one-sided on *level*, not on direction of travel, and offer no discount on a return climb.
- So no arm in either track could have removed a directional bias, whatever its size.
- With the popularity terms unpriced in `X`, the remaining live terms are the similarity
  term, the per-hop constant (neutral by construction), and the degree-hub penalty (which
  pushes *away* from high-degree, hence away from fame). **The similarity term is the leading
  candidate.**

**`ASC-4` — a plausible mechanism, and the reason it would be structural rather than a
tuning error.** *(Plain: the app measures "similar" and "famous" from the same underlying
data, so picking the most similar artist may be quietly picking a more famous one.)*

Popularity in this graph is **score-weighted in-degree** — there is no separate popularity
source (CLAUDE.md, "Popularity = score-weighted in-degree"). The same co-listening volume
that makes an artist score as popular also makes the edges pointing at it carry high
similarity scores. If that is what is happening, minimising `w_sim·(1 − similarity)` is
partly minimising *toward fame*, and no amount of repricing the popularity terms can undo it.

**This is a hypothesis. It has not been measured, and this document does not measure it.**

## 3. What this does and does not license

**Does:** it establishes that the router has a large upward gradient at the one-hop level
(`ASC-1`), and it gives a coherent account of why two repricing tracks returned nulls that
does not require either to have been badly designed.

**Does not — three ways, and each matters:**

1. **It is not evidence that `w_sim` is the cause.** `ASC-3` and `ASC-4` are inference from
   arm definitions plus one confounded contrast. The isolating contrast (`X` vs `A7`) exists
   in the run and was not reported; reading it would sharpen this considerably.
2. **It is a one-hop *local* measurement, not a path-level one.** A17(c) describes it as
   local preference. A router minimising total cost can climb locally and still descend over
   a complete path, so this is strong evidence about the cost function's gradient and weaker
   evidence about what a user sees.
3. **It does not reopen §2.12.** That section's conclusion — the router prices stratum exits
   correctly and declines them — is untouched. If anything `ASC-1` sits underneath it: this
   describes the gradient, §2.12 describes the toll, and both can hold.

**No adoption, no rebuild, no rule change and no arm is proposed here.** Any of those is
path-quality work, is behind the pause, and would need its own pre-registration.

## 4. The cheapest thing that would settle it

Stated so it cannot drift, and **not scheduled** — it is path-quality work and the trigger is
the owner's:

> **`ASC-5` — read the ascent measurement at path level, and read the `X`-vs-`A7` contrast
> that already exists in the Track 2 run.** *(Plain: check whether the climb the app shows on
> a single step is still there across a whole journey, and compare the two settings that
> differ by only one thing instead of three.)*
>
> **Both are re-reads of committed runs. Neither needs a rebuild, a new arm, or the graph to
> change.** If the path-level gradient is near chance, `ASC-3` collapses and this document is
> a curiosity. If it holds, the next intervention is directional or builder-side, and is
> **not** another repricing sweep.

> **✅ DISCHARGED 2026-07-28 — both re-reads have run**, after the owner unpaused
> path-quality work. Results, gates and pre-committed reads:
> `builder/analysis/2026-07-28-asc5-path-ascent/` (`PLA-` series), which owns every
> figure. In outline, without restating numbers: the path-level gradient is **absent on
> famous-pair first paths** — the hop-minimal routes there are as famous as the delivered
> ones, so `ASC-3` collapses *for that slice* — while the one obscure-endpoint pair moved
> the other way; the `X`-vs-`A7` isolating contrast is **immaterial at path level in both
> currencies**; and the pure-similarity cost climbs at one hop far above the null, which
> is `ASC-4`'s mechanism in single-arm form. §6's caution is upheld: a fame criterion on
> famous-pair first paths would be structurally unable to move.

## 5. Why this was not visible before — a process note, not a criticism

The measurement was commissioned to answer a narrow question: *may `R0`'s null be read as
"no arm in this family can move the outcome"?* It answered it correctly — no — and the answer
was recorded as **a bound on one arm's interpretability**, inside an amendment, inside a
pre-registration for a track that returned a null.

Everything about that placement is right for its purpose. The consequence is that the
strongest single-number statement of the fame problem in this record sits where nobody
re-reads it, because the document it lives in is closed and its result was negative.

**Related, and the same shape:** `2026-07-25-mutual-knn-stranding.md` was written for the
same reason — a mechanism the record already half-held, recorded so it could not be lost.
`MKS-5a` is that document's admission that it initially overstated its own novelty; this one
states its dependence up front for the same reason.

## 6. What this document changes about the parked candidate

The current handoff (`../2026-07-25-HANDOFF-track2f-and-headroom.md` §0) parks a builder-side
p99 rescale as the live candidate, and parks **open question 1** — which direction restored
edge ordering would move routes — as unanswered and load-bearing.

**`ASC-1` is directly relevant to that question and points one way.** If the cheapest hop
already climbs four times in five, restoring similarity ordering sharpens a preference that
is itself upward-tilted. That is an argument for expecting the rescale to produce *better
chosen famous artists* rather than *more obscure ones* — the same conclusion §2.11's
saturated-slot finding reaches by a different route.

**Not a recommendation against the rescale**, which is not this document's to make. It is a
reason the rescale's pre-registration should not be scored on a fame criterion without
answering `ASC-5` first — the third fame-scored null in a row would cost a cycle and teach
nothing.
