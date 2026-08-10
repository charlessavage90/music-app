# `JFX-` pre-registration critique — figures

**Role: FIGURES OWNER for the famous-to-famous reachability measurement.** Cited by
`specs/2026-08-09-journey-fame-exposure-preregistration.md` `JFX-AM1` and by the forward
correction in `PRODUCT-REQUIREMENTS.md` §8. **Never restate these numbers elsewhere.**

Run 2026-08-09, before any `JFX-` arm ran. Nothing here adopts, deploys or decides.

## Artifact identity

`builder/scratch/graph-msw-tu50.bin`, sha256
`43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` — matched against its
manifest sidecar by the script, which **refuses to run** on a mismatch. 58,838 nodes;
58,746 (99.84%) carry a fame measurement.

Reproduce: `cd builder && UV_LINK_MODE=copy uv run python
analysis/2026-08-09-jfx-prereg-critique/jfx_s1_reachability.py`

## The question

`PRODUCT-REQUIREMENTS.md` §8 recorded, from `DD-F1` (2026-07-28), that *"superstar endpoints
have zero edges below the top popularity decile"*, concluding REQ-37 is *"currently
unachievable on famous-to-famous pairs at any router setting"*. A `JFX-` prereg critique
leaned on that to argue the `S1` famous–famous stratum is a structural zero and should be
removed from the `JFX-G1` gate.

**Three reasons that claim may not transfer**, all raised by the owner:

1. `DD-F1` was measured on the **pre-`MSW-`** artifact. The cap rule changed 2026-08-06 from
   mutual k-NN (edge survives only if **both** endpoints rank the other top-k) to
   `trimmed_union` (**either** suffices). An obscure artist ranks a famous one highly and the
   famous one does not reciprocate — so exactly these edges were the ones mutual k-NN
   destroyed and `trimmed_union` keeps.
2. `DD-F1` is stated in **popularity** currency; `JFX-` scores in **fame** (`fame_lb`).
3. `DD-F1` predates the 2026-08-02 fame redefinition, so its "fame" is the retired worldly
   construct.

So both currencies are measured on the adopted artifact: popularity reproduces `DD-F1`'s own
claim apples-to-apples, fame answers what `JFX-` needs.

## Result — the claim does NOT transfer to fame currency

Share of a top-10% artist's neighbours that sit below the top 10%:

| Currency | mean | p50 | artists with **zero** such neighbours | median count |
|---|---|---|---|---|
| **Fame** (`fame_lb`) | 45.41% | 46.00% | **1.07%** (63 / 5,875) | 15 |
| Popularity (`pop_raw`) | 41.75% | 42.86% | 2.96% (174 / 5,884) | 21 |

At the very top, where "superstar" plausibly meant:

| Currency | Tier | Pool | **Zero** below-decile neighbours | Median count |
|---|---|---|---|---|
| Fame | top 1% | 588 | 1.53% | 6 |
| Fame | top 0.2% | 118 | **0.00%** | 8 |
| Popularity | top 1% | 589 | 15.79% | 4 |
| Popularity | top 0.2% | 118 | **44.07%** | 1 |

Mean degree of the top-10% pool: 39.0 (fame) / 49.1 (popularity), against a graph mean of
22.36 — famous artists sit near the degree ceiling of 50.

Share of a top-10% artist's neighbours below the **median** (the `S3` band) is much thinner:
mean 9.39% in fame, 3.64% in popularity.

## Reading, and the part that must not be collapsed

**`DD-F1` is not refuted in its own currency.** At the top 0.2% by popularity, 44.07% of
artists still have zero edges below the popularity decile, median 1. That finding **survives
where it was measured**.

**It does not transfer to fame, which is what `JFX-` scores on.** The same tier in fame
currency has **zero** boxed-in artists and a median of 8 routes below the decile. Popularity
is score-weighted in-degree computed *from the graph* — a superstar is popular partly because
they are wired to other popular artists, which is circular — whereas fame is an external
listener count. Same artists, opposite answer. This is §2.6/§2.11/§2.12's currency trap, and
the critique walked into it by carrying a claim across currencies unchecked.

**⚠ This measures STRUCTURE (edges available), not ROUTING (paths chosen).** The structural
barrier behind the REQ-37 conflict is gone; whether journeys actually descend is what `JFX-`
measures. Owner-reported use of the live app corroborates it. **Do not cite this as evidence
that journeys descend** — it is evidence that they *can*.

**⚠ The `MSW-` switch addressing this was BY DESIGN, not incidental** — owner statement,
2026-08-09: improving famous-to-famous behaviour was one of his reasons for the switch. The
`MSW-` adoption records do not mention it (swept: execution log, plan, handoff — zero hits),
so the adoption is recorded as resting on narrower grounds than it had. Corrected forward in
`PRODUCT-REQUIREMENTS.md` §8, not by editing the frozen `MSW-` records.

## What this changed in the pre-registration

`JFX-AM1` withdraws the proposal to remove `S1` from the `JFX-G1` gate. All 300 pairs stay.
