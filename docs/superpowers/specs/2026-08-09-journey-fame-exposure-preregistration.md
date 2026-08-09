# `JFX-` — does the extended map put less famous artists into journeys?

**Role: PRE-REGISTRATION.** The git commit timestamp is the evidence that this preceded the
result; that is the part that cannot be reconstructed afterwards. **No arm runs before this
document and its pair set are committed.**

**Thresholds are SET, by the owner, 2026-08-09 — before any arm ran.** `JFX-G1b` is 67%
(§3). The draft's second placeholder was **withdrawn rather than filled**: `JFX-C2` gates
nothing, so a threshold on it would have decided in advance which differences the write-up
calls material, which is framing dressed as rigour. It is a report row, on the `MSW-V2`
precedent.

Governing: [`PRODUCT-REQUIREMENTS.md`](../PRODUCT-REQUIREMENTS.md) — every criterion here
is anchored on a `REQ-`, none invented. Operational context: plan Task 11 is complete and
stopped at its owner stop; this does not resume it.

**Identifier series `JFX-`** — collision-checked across every ref, zero matches.

---

## §0 Factor table

| Arm | Artifact | Archive | Nodes | p99 scale | Isolating baseline |
|---|---|---|---|---|---|
| **`JFX-A`** | `graph-msw-tu50.bin` (adopted) | ALG-B @ 75,000 | 58,838 | 850 | — (reference) |
| **`JFX-B`** | `graph-cex-117k.bin` (to build) | ALG-B @ 117,302 | 88,685 | 769 | `JFX-A` |

**`JFX-B`'s baseline differs by more than one column, and that is deliberate and stated
rather than hidden.** The intervention is *the extended crawl*, which is inseparably three
changes: ~30k new artists available as waypoints, new edges attaching to existing artists,
and every similarity reweighted by the p99 shift. **No arm here isolates them.**

**This is the right design for the question asked** — *what does a person get now* — and the
wrong design for *what did adding artists cause*. A third arm isolating the reweighting
(old archive, p99 forced to 769) would be needed for the second question and **is not run
here**. No read below may attribute an effect to "adding artists" specifically.

## §0.1 Held constant, and why each is genuinely constant under the intervention

| Held | Why the intervention cannot change it |
|---|---|
| Every `ApiConfig` cost weight | Read from config, not from the artifact; both arms served by the same code |
| Cap rule (`trimmed_union`, j=50, ceiling=50) | Set in `BuilderConfig`, identical in both builds |
| All three drop flags | `True` in both; `JFX-B` uses its own censused payload via `--unlistenable-list` |
| The pair set | Fixed and committed before either arm runs (§2) |
| Bypass semantics | Frontend/router behaviour, untouched by either artifact |

### ⚠ Two things are NOT constant, and one of them undermines a naive read of Q3

**(a) The fame ruler changes between arms, and the depth mechanism is priced on it.**
`w_known_ramp_fame_pctl` is priced in **fame percentile**, and percentile is ranked against
**the served artifact's own population**. The two arms have different populations, so *the
same artist has a different percentile in each*. The `known` ramp is the depth mechanism —
so depth behaviour differs between arms partly because the ruler moved, not because the
map got bigger.

This **cannot be removed without departing from what the API actually does**, so it is
accepted and named. Consequence, binding on §4: **`JFX-G1` measures whether the extended
map delivers a depth gradient, never whether adding artists caused a change in it.**

**(b) `w_floor` is dormant in `JFX-A` for a reason `JFX-B` may remove.** The floor term
fires when a path dips below the obscurity floor; `w_jump` normally prevents that. The
extended map makes many more obscure artists available to dip *to*. This is the Track 2
dormant-term pattern exactly: a term inert in the baseline for a reason the intervention
removes is not a constant.

**So it is measured, not assumed.** Both arms report the share of paths where the floor
term is non-zero (`JFX-C6`). If it fires materially more in `JFX-B`, every one-knob reading
below is void and must say so.

## §1 The artifact

`JFX-B` needs `graph-cex-117k.bin`, which does not exist: acceptance rejected before
serialising (artists 88,685 against [47,000, 71,000]; edges 1,618,164 against
[1,050,000, 1,580,000]).

**It is built by a script that runs `check_acceptance`, CATCHES the rejection, records it
verbatim in the manifest, and serialises anyway.** The gate is not modified and the bounds
are not widened.

**The artifact is byte-identical to one `cmd_build` would emit after a bounds change** —
the build is deterministic (spec §9), demonstrated 2026-08-09 when the snapshot rebuild
reproduced the adopted artifact exactly. **So if these results support adoption, this
artifact is the one that ships; no rebuild is required.** Adoption remains a separate
owner decision about the bounds.

## §2 The pair set — fixed before any arm runs

- **Analysed population:** the **intersection** of both artifacts' node sets. A pair with an
  endpoint missing from either arm is not comparable and is excluded.
- **300 pairs analysed, 100 per stratum**, stratified on endpoint fame measured in `JFX-A`
  (a fixed ruler chosen before results exist, per §0.1(a)):
  - **`S1` famous–famous** — both endpoints in the top 10% by `fame_lb`
  - **`S2` mixed** — one in the top 10%, one in the bottom 50%
  - **`S3` obscure–obscure** — both in the bottom 50%

**⚠ The intersection cannot be computed yet, because `JFX-B` does not exist — so selection
is fixed in two stages, and neither stage leaves any discretion.**

1. **Now, before the artifact is built:** draw **150 candidate pairs per stratum** from
   `JFX-A`'s node set with seed **20260809**, sorted by MBID before sampling so the draw does
   not depend on dict ordering. **This list is committed alongside this document** as
   `jfx_candidate_pairs.json`.
2. **After `JFX-B` is built:** walk the committed list **in its committed order** and take
   the **first 100 per stratum whose endpoints are present in both artifacts.** Report how
   many candidates were skipped — a non-trivial number is itself a finding, since it means
   the extension *removed* artists the adopted map has.

**Over-selection exists so a shortfall cannot become a reason to draw more.** Topping up a
stratum after seeing which pairs survived would be selection on the outcome. If any stratum
cannot reach 100 from its 150 candidates, **the shortfall is reported and the stratum runs
short** — no redraw.
- **Depths:** `known` = **0, 5, 10, 20**. `d5` is included because REQ-18 requires novelty
  within a handful of presses, not dozens.

**Currency rule, binding:** the primary statistic uses **raw fame** (the wire key `fame_lb`;
in-memory `fame_lb_raw`), never `fame_lb_pctl`. Percentile is population-relative and
comparing it across two populations compares two different rulers — the error `CLAUDE.md`
records as having caused three wrong conclusions here.

**Null rule, binding, and it carries a known bias direction.** A null fame value is a
**measured absence, never a floor** (`FAM-AM1.8`) and must not be coerced to 0 — doing so
would file every unmeasured artist as maximally obscure. So:

- Artists without a measurement are **excluded from the endpoint pool** (they cannot be
  placed in a fame stratum) and **excluded from the interior fame statistic**.
- **The null share among interior artists is reported per arm and per depth (`JFX-C7`).**

**The two arms are expected to differ here, and the direction is stated in advance so it
cannot be spun afterwards.** The adopted map carries 0.16% nulls (92 of 58,838), while the
`CEX-` fame fetch returned nulls for 6.3% of newly fetched artists — though most of those
are also un-listenable-filter candidates and may not survive into `JFX-B`. Unmeasured
artists are disproportionately obscure, so **excluding them pulls the median fame UPWARD in
whichever arm has more of them.** If `JFX-B`'s null share is the higher, the bias runs
**against** the extension: a `C1` result showing interior fame going *down* would be
strengthened by it, and one showing fame going *up* is partly attributable to it and must
say so.

**Statistic:** paired by pair, both arms. Median interior fame per journey, then the paired
median difference with a bootstrap CI, importing `paired_median_ci` from the frozen `ULC-`
script rather than retyping it. **Interior** = the path minus its two endpoints.

**`ULC-R1`'s known statistic defect is inherited deliberately:** where a class is
concentrated in a minority of journeys, the paired median can read zero while the mean
moves. **Both are reported at every depth**, and a divergence between them is a finding,
not a discrepancy to reconcile.

## §3 Criteria

Each carries its plain-language sentence, fixed here, before any result exists. Owner-facing
text must quote the sentence beside the identifier.

| ID | Plain sentence | Type | REQ |
|---|---|---|---|
| **`JFX-G1`** | *Does pressing "dig deeper" still keep making the middle of the journey less famous, press after press?* | **GATE** | REQ-13, REQ-37 |
| `JFX-C1` | *On the bigger map, is the typical artist in the middle of a journey more famous or less famous than before?* | gradient | REQ-10, REQ-42 |
| `JFX-C2` | *Does that answer differ depending on whether you picked two famous artists or two obscure ones?* | gradient | REQ-34 |
| `JFX-C3` | *Do journeys get longer — and if they do, do they buy more discovery for it?* | gradient | REQ-11, REQ-21, REQ-23 |
| `JFX-C4` | *How many more artists can now appear in a journey at all, or be found in search?* | report | — |
| `JFX-C5` | *Have famous artists been pushed out?* | **FLOOR** | REQ-33 |
| `JFX-C6` | *Did the obscurity-floor rule start firing on the bigger map when it never used to?* | validity check | §0.1(b) |
| `JFX-C7` | *How many artists in the middle have no listener measurement at all, and does that differ between the two maps?* | validity check | §2 null rule |
| `JFX-M1'` | *How often is a hop chosen by a tie-break rather than by how similar two artists actually are?* | report | — |

### `JFX-G1` — the only pass/fail, and its effect sizes

REQ-13 and REQ-37 are **Musts**, not gradients: repeated bypasses must increase delivered
novelty. If the extended map breaks the depth gradient, that is a stop **regardless of how
many artists it adds** — the gradient is the product.

- **`G1a` (absolute).** On `JFX-B`, median interior fame must be **non-increasing** across
  d0 → d5 → d10 → d20, and fame(d20) must be below fame(d0) with the bootstrap CI excluding
  zero. **Fails if any step rises with its CI excluding zero.**
- **`G1b` (relative).** `JFX-B`'s total d0→d20 fame decrease must be at least **67%** of
  `JFX-A`'s. **Fires below that.**

  **Owner-set, 2026-08-09, on this translation** — recorded because the reasoning is what a
  later reader needs, not the number. The bar is equivalent to asking *how many presses may
  it take on the new map to reach the distance twenty presses reaches today*: 67% ≈ **no more
  than 50% more presses** (20 → 30). It is anchored on **REQ-18** (novelty within a handful
  of presses, not dozens): at 67% a 10-press journey becomes 15 and stays a handful, whereas
  the draft's 50% would make it 20 and put it in the dozens REQ-18 rules out. **The session
  proposed 50%, then argued against its own number** on that REQ-18 reading; the owner set
  67%, conditional on the measurement being taken at 20 presses, which it is (§2).

  **This is a "the map is broken" bar, not a "the map is worse" bar** — it stops adoption.
  Disappointing-but-not-stopping is what the reported gradients are for.

  *Caveat on the translation, not on the test: press-count equivalence assumes the gradient
  is roughly even across presses, and it may be steep early and flat later. The test is on
  the total d0→d20 drop. The press framing exists to make the bar intuitive, not to redefine
  it.*

### The gradients — thresholds deliberately absent, and why that is not a gap

**REQ-42 states the obscurity requirement is a gradient that sets no absolute floor.** So
`JFX-C1`, `C2` and `C3` carry **no bar**, by design and by requirement.

**What is pre-registered instead is the measurement and the reservation:** the statistic,
the depths, the strata, the direction that counts as better, and — stated here in advance —
that **the trade between coverage gained (`C4`) and any interior-fame cost (`C1`) is the
owner's judgement at read time.** Declaring the reservation in advance is what makes this a
pre-registration rather than a gap that gets filled once the numbers are in.

**`JFX-C2` carries NO materiality threshold, deliberately.** The draft proposed one (a sign
flip, or a 2× magnitude difference) and it was **withdrawn before commit** on the owner's
agreement. `C2` gates nothing and fires no branch, so a threshold could only decide in
advance which differences the write-up would call material — framing dressed as rigour.
Precedent: `MSW-V2` is recorded as *"a report row, not a gate — no threshold was
pre-registered and none was supplied."*

**Instead: all three strata are reported side by side with their confidence intervals**, and
the reader draws the comparison from the numbers. This is a deliberate narrowing of what
the document decides in advance, not an omission.

**`JFX-C3` read, fixed here per REQ-11/REQ-21:** a length increase is acceptable **only**
where the same stratum also shows an interior-fame decrease. Longer *and* more famous is a
loss on both counts and needs no threshold to read as one.

**`JFX-C5` floor**, per REQ-33: at least **95%** of `JFX-A`'s top-1%-by-fame artists must
still be present in `JFX-B`. Below that, the system is eliminating famous artists.

## §4 The read of every result, including the null

Each read names the run state it presupposes.

**Presupposes: all 300 pairs routed in both arms at all four depths, with `JFX-C6` and
`JFX-C7` both reported.** A read taken before either validity check is available is not
licensed by this document, however clean the headline numbers look.

1. **`G1a` fails** → **stop.** The extended map breaks a Must. Nothing else in this document
   can license adoption, and `C1`/`C4` gains do not offset it.
2. **`G1a` passes, `G1b` fires** → the gradient survives but is materially shallower. **Owner
   decision**, and the exposure map for it is `C1` × `C2` — is the shallowness everywhere, or
   confined to one stratum?
3. **`G1a` and `G1b` both pass, `C1` shows interior fame DOWN** → the extension delivers the
   product goal and adds artists. The trade is not in tension; adoption is a straightforward
   owner call.
4. **Both pass, `C1` shows interior fame UP** → the tension he anticipated: more artists
   available, but journeys skew more famous. **No threshold decides this** (REQ-42); it is
   reported with `C4` beside it and the trade is his.
5. **Both pass, `C1` null** → the map got bigger and journeys did not measurably change. This
   is a real and likely outcome, and it is **not** a failure: `C4`'s coverage gain stands on
   its own, and search coverage is unaffected by routing at all.
6. **`C5` fails** → stop, independent of everything above. REQ-33 is not tradeable.
7. **`C6` shows the floor firing materially more in `JFX-B`** → **every reading above is
   void as a one-knob attribution** and the report must say so in those words.
8. **`C7` shows a materially higher null share in `JFX-B`** → the fame comparison carries a
   known upward bias in `JFX-B` (§2). Reads 3 and 5 survive it and are strengthened by it;
   **read 4 must state that some of the apparent fame increase is the bias, not the map.**

## §5 What this design cannot support

- **Any claim that *adding artists* caused an effect.** §0 — the arms differ by three things.
- **Any claim about coherence or whether journeys sound good.** No listening is involved. A
  fame improvement is not a quality improvement; REQ-9 puts novelty behind coherence, and
  nothing here measures coherence.
- **Any cross-arm comparison in percentile currency.** §2.
- **Anything about `JFX-A` vs the pre-`MSW-` world.** Out of scope.

## §6 Reserved to the owner

- ~~Both `⚠ OWNER` thresholds above, before this is committed.~~ **DONE 2026-08-09:**
  `G1b` set to 67%; `C2`'s threshold withdrawn as inappropriate to a report row.
- The `C1`/`C4` trade at read time (declared in advance, per §3).
- Whether to widen the acceptance bounds, which is what adoption requires. `MSW-G3` is the
  precedent and there too it was his.
- Whether to build the artifact at all (§1).
