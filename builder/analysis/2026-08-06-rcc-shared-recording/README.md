# `RCC-` — is the top similarity edge a SHARED RECORDING credit?

**Date:** 2026-08-06 · **Governing document:**
`docs/superpowers/specs/2026-08-06-shared-recording-preregistration.md` (committed `d478c84`,
amended by **`RCC-AM1`** at `59b7fdf`, **both before any outcome value was observed**).

**This directory OWNS its figures.** Raw `rcc_raw.json`, scored `rcc_result.json`. Cite it.

## Run state

**`RCC-G1` passed: 200/200 answered in both arms, answer rate 1.000.** Under `RCC-AM1` the
sample is 400 usable, 0 skipped — against 15/200 surviving in CONTROL under the original rule.

## Verdict

| Arm | shares a recording with **rank-1** | with the **tail** (80 % depth) | lift |
|---|---|---|---|
| CLASS (central, unlistened) | 7.5 % | 1.0 % | **+6.5** |
| CONTROL-OBSCURE | 17.0 % | 4.0 % | **+13.0** |

- **`RCC-C1` = `null`.** The CLASS lift is 6.5 points, below the pre-registered 10-point floor.
- **`RCC-C2` = `general`**, at **−6.5** — and note the **sign is opposite to the hypothesis's
  prediction**. Ordinary obscure artists show *more* co-credit at rank 1 than the class does.

## ⚠ The instrument was validated this time, which is what makes the null readable

`CCR-` failed because its instrument could not see the mechanism. This one can:

| Query | Result |
|---|---|
| Khruangbin + Leon Bridges | **count = 9** — incl. *Texas Sun*, credit "Khruangbin / Leon Bridges / Austin Jenkins" |
| Laura Lee + Leon Bridges | 0 |
| Laura Lee + Khruangbin | 0 |

**The instrument finds the collaboration that started this investigation.** So a null is a
result about the world, not about the tool.

## What this means, and it is not what the hypothesis predicted

**Co-credit does shape top similarity edges — in both arms, rank 1 is several times likelier
to be a shared credit than an edge 80 % down the same list.** The mechanism is real and
visible. **But it does not explain the class**, and the class shows *less* of it than ordinary
obscure artists do.

Combined with `CCR-`, two independent instruments now decline to attribute the class to
recording collaboration. The depth-exposure census remains the standing explanation — the fame
ramp compounding along the path — and it is untouched by this.

## ⚠ Laura Lee is now an OPEN puzzle, and this is the sharpest thing here

She scores **214** to Leon Bridges — rank 2 on his list — while sharing **zero** artist credits
with him *or with her own band*. So her edge is not a co-credit artefact under the definition
this probe validated. **How she acquires it is unexplained.**

**A name-collision hypothesis was raised and is WEAKENED, not dismissed.** MusicBrainz holds
**six** artists named "Laura Lee", including a 1945-born soul & gospel singer
(`70a65cf5…`) — and if listens resolved to the wrong MBID, a soul singer co-occurring with
Leon Bridges would explain 214 exactly. **Against it:** her archived similar-list reads
Tame Impala, Khruangbin, SAULT, Skinshape, Unknown Mortal Orchestra — a coherent modern
psych-soul cluster, not a 1960s soul one. That is evidence the listens belong to roughly the
right scene.

**This is `BYP-13`'s defect class pointed at a new target.** `BYP-13` is about a wrong
same-named artist reaching a *clip*; this would be a wrong same-named artist reaching the
*graph's edges*. **Not measured, not claimed, and it needs its own pre-registration.**

## Barred reads (from the pre-registration, travelling with every citation)

1. A shared recording credit does not prove the similarity came from it — association, never
   causation. The causal mechanism rests on `LBS-1`.
2. MusicBrainz recording coverage is incomplete, so both cells are **floors**. Only the
   within-artist *difference* is interpretable; the absolute rates are not.
3. **`RCC-C2` compares "top of your list vs bottom of your list" across arms**, not "rank 1 vs
   rank 75" across arms — see `RCC-AM1`.
4. No adoption follows. No default, weight or filter changes on this result.

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-08-06-rcc-shared-recording/rcc_fetch.py
```
Resumes from `rcc_raw.json`. ~50 minutes; MusicBrainz 503s if queried again immediately after.
