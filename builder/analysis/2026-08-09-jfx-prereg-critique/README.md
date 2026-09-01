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

---

# `JFX-` RESULTS — the arms, run 2026-08-09/10

> **⚠ QUALIFIED, NOT CORRECTED, 2026-09-01 — and this applies to THIS HALF ONLY.**
> Everything below is accurate and nothing in it has been overturned: `JFX-G1` passed
> exactly as recorded, on the artifacts named above. What changed is what a reader should
> **conclude** from it.
>
> **`JFX-B` — the extended map these arms scored — was adopted on 2026-08-10 and REVERTED
> from production on 2026-09-01**, after three weeks of owner use fired the revert criterion
> he had set before adoption. **`JFX-G1b` is a "the map is broken" stop-gate, and passing it
> never meant "no worse"**: the bar it clears explicitly permits the extended map to need
> materially more digging than `JFX-A` to reach the same obscurity, and it used materially
> more. The permitted bound and the realised figure are in the `JFX-G1` section below — read
> them as a floor that was cleared, never as a quality result.
>
> **The barred read below still binds and is the reason this banner exists:** `AM1.3` records
> that `G1a` is mechanically weak in the absolute and is **not** evidence the product works
> for a user. Do not use a `JFX-G1` PASS to argue the extended map was an improvement.
>
> **`graph-cxa-adopted.bin` is the REJECTED artifact, not "the newer one"** — nothing here
> licenses redeploying it. Mechanism:
> [`../2026-09-01-cxr-regression-diagnosis/README.md`](../2026-09-01-cxr-regression-diagnosis/README.md).
> Reasoning: `docs/superpowers/2026-09-01-cxr-revert-execution-log.md`.
>
> **The reachability critique above (through "What this changed in the pre-registration") is
> NOT qualified by any of this.** It was measured on `graph-msw-tu50.bin`, which is the map
> production serves again — the revert restored the artifact that half was run on.

**Role: FIGURES OWNER for the `JFX-` run as well as for the reachability measurement
above.** Everything below is cited, never restated — including in `NEXT.md`, the handoff
and the PR body.

Governing: `specs/2026-08-09-journey-fame-exposure-preregistration.md` as amended by
`JFX-AM1`. **Nothing here adopts, deploys, or changes what any user sees.**

## Artifact identity

| Arm | Artifact | sha256 | Nodes | Edges |
|---|---|---|---|---|
| `JFX-A` | `graph-msw-tu50.bin` (adopted) | `43dd82bb…2be79cc8` | 58,838 | 1,315,684 |
| `JFX-B` | `graph-cex-117k.bin` (diagnostic) | `bc0431c4…8e7ece46` | 88,685 | 1,618,164 |

`JFX-B` was built **twice from identical inputs and produced identical bytes**, direct
evidence for §1's claim that it is byte-identical to what `cmd_build` would emit after a
bounds change. Its manifest records `acceptance.passed = false` and `DO_NOT_DEPLOY =
true` with the rejection verbatim; **the bounds were not widened.**

```
INFO rescale p99 scale=769 | saturated edges 37053 of 3698308 (1.002%)
INFO largest component: 88685 of 90026 artists
INFO wrote graph-cex-117k.bin: 88685 artists, 1618164 edges, 23.4 MB, 541s
     - acceptance REJECTED (recorded, not suppressed)
```

## Coverage: 297 of 300 pairs

S1 100, S2 98, S3 99. Three pairs could not produce a value at all four depths and were
dropped rather than imputed; **no redraw** (§2). The drops split **1 against `JFX-B`, 1
against `JFX-A`, 1 against both** — no systematic disadvantage to either arm.

**§4 presupposes 300.** It got 297. The reads below are taken on 297; this is the
deviation.

## Validity checks — first, because §4 does not license the headline without them

| | d0 | d5 | d10 | d20 | bar |
|---|---|---|---|---|---|
| `C6` floor fires, A to B | 2.36→3.03 % | 0→0 % | 0→0 % | 0→0 % | +5 pp |
| `C7` null share, A to B | 0.04→0.04 % | 0.04→0.09 % | 0.09→0.09 % | 0.18→0.18 % | +2 pp |

**Neither fires.** `C6`'s largest gap is +0.67 pp and only at d0; flat zero from d5 on,
independently corroborating `AM1.9`'s finding that the floor is spent by press five.
`C7`'s null share **rises with depth in BOTH arms**, so per `AM1.7` both gradients are
attenuated — equally, so the between-arm contrast is not distorted.

## `JFX-G1` — GATE — both clauses PASS

```
G1a  steps on JFX-B   d0-d5    -0.0930  simultaneous band [-0.1309, -0.0551]
                      d5-d10   -0.0499  simultaneous band [-0.0880, -0.0118]
                      d10-d20  -0.1329  simultaneous band [-0.1879, -0.0780]
     overall d0-d20 drop       +0.3632  CI [+0.2860, +0.4225]         PASS
G1b  D_A +0.4329 CI [+0.3234, +0.4867]  t_A 10.60  (viability clause satisfied)
     D_B +0.3632      R-hat 0.839
     T = D_B - 0.67*D_A = +0.0732   one-sided 95% lower +0.0175       PASS
```

Every step is negative and every band strictly negative, so no step rises. `AM1.9`'s
**realised** press-count equivalence: **~24 presses** on `JFX-B` to reach where `JFX-A`
gets in 20 (the bar permitted up to 30).

**⚠ `AM1.3`: `G1a` is a WEAK test in the absolute.** `victim_key` deletes the most famous
interior twenty times, so part of the decrease is mechanical. It is **not** evidence the
product works for a user. The force is in `G1b`, where that component sits in both arms.

## `JFX-C1` — gradient, no threshold by design (REQ-42)

| depth | median (B−A) | mean (B−A) | pairs moved |
|---|---|---|---|
| d0 | +0.0000 `[0, 0]` | −0.0022 `[−0.0286, +0.0260]` | 166/297 |
| d5 | +0.0000 `[0, 0]` | −0.0130 `[−0.0525, +0.0257]` | 226/297 |
| d10 | +0.0000 `[0, 0]` | +0.0259 `[−0.0206, +0.0711]` | 231/297 |
| d20 | +0.0000 `[0, +0.0003]` | **+0.0680 `[+0.0155, +0.1214]`** | 249/297 |

**`AM1.11` read 9 FIRES at d20**: the median is null while the mean's interval excludes
zero. Both reported. **The gate stays on the median**; promoting the mean would change
what passes and is the owner's call, not a bookkeeping fix.

`C2`: every stratum's median is 0.0000 at every depth. `C3`: **median journey-length
change is exactly +0.0 in all twelve stratum×depth cells** — journeys do not get longer.
`C4`: +29,892 gained, 45 lost, net +29,847. `C5`: **588/588 = 100.00 %** against a 95 %
bar. `REQ-Q1(a)` matched-only (290/297): `T` +0.0612, one-sided lower +0.0132 — same
conclusion.

**Pre-registered read: §4 read 5** — *"the map got bigger and journeys did not measurably
change… not a failure: `C4`'s coverage gain stands on its own."*

## Two report rows added AFTER the fact, and labelled as such

**Neither is pre-registered.** Both are descriptive decompositions computed because the
owner asked questions the pre-registered set did not answer. They carry no threshold and
license no branch.

**(a) Is `JFX-B`'s gradient actually shallower?** `G1b` tests against the 0.67 bar, never
against parity, so nothing pre-registered answers this.

```
D_B - D_A = -0.0696   95% CI [-0.1407, +0.0250]   -> SPANS ZERO
per stratum   S1 [-0.1927, +0.0292]   S2 [-0.1922, +0.0929]   S3 [-0.2129, +0.1322]
```

**The shallower gradient is NOT established.** The point estimate leans shallower
(R-hat 0.839) but the data cannot distinguish the two maps' depth gradients. Nor does
this establish equality — a real shallowness up to ~0.14 log10 is compatible with n=297.

**(b) Where does the d20 mean drift live?**

| stratum | n | mean (B−A) | 95 % CI | share of overall mean |
|---|---:|---|---|---:|
| S1 famous–famous | 100 | +0.1279 | `[+0.0304, +0.2271]` | 63.3 % |
| S2 mixed | 98 | +0.0534 | `[−0.0405, +0.1495]` | 25.9 % |
| S3 obscure–obscure | 99 | +0.0220 | `[−0.0568, +0.1012]` | 10.8 % |
| **S2+S3, S1 dropped** | 197 | +0.0376 | `[−0.0252, +0.1007]` | — |

Removing S1 removes the effect. **⚠ Post-hoc: three strata, three intervals, one clears
zero — expected about one time in seven under a true null.** §3 gave `C2` no threshold
precisely so the write-up could not decide materiality after the fact. Read as *where to
look*, not an established stratum effect; it needs its own pre-registration to be a claim.

Mechanism, per-pair distribution at d20 (pairs moving beyond ±0.1):

| | more famous | unchanged | less famous | of which **much** less (<−0.5) |
|---|---:|---:|---:|---:|
| S1 | 41 | 39 | 20 | **4** |
| S2 | 35 | 35 | 28 | 10 |
| S3 | 32 | 39 | 28 | 8 |

Large moves *toward* fame are evenly spread (15/15/10). What famous–famous journeys lack
is the **return trip**: they rarely get the large swing toward obscurity the other strata
still get. That asymmetry is the whole effect.

## Instrument provenance

- **`CRE-G1(a)` was re-verified against today's router** before the harness was trusted
  (`AM1.3`'s precondition). The mirror (`f52cc04`, 2026-08-03) **predates** production's
  ramp (`a4ff9c6`, 2026-08-05), and the original gate compared at `excludes=[]` with the
  ramp knob at 0.0 — **doubly inert on the one term whose provenance differs.** The re-run
  compares at every rung to k=20 with the ramp live: **630 rungs, 0 divergences**; both
  red controls fired, the ramp control first at **k=1**, proving the rungs above zero are
  genuinely compared.
- **Routing is production `find_journey` itself.** The equivalence above makes that free.
  `C6` is computed from production's own `effective_floor_raw`. No mirror routing code is
  called.

## Two defects found by running this, both fixed with tests shown red first

- **`manifest.py` could not serialise a `Path`.** `cli.py:108` stores
  `BuilderConfig.unlistenable_list_path` as a `Path`; `build_manifest` fed
  `dataclasses.asdict` straight to `json.dumps`. **Any build using `--unlistenable-list`
  that PASSES acceptance dies at manifest write**, after the full build, artifact already
  on disk, no provenance record. Never fired before: every build using the flag was
  rejected pre-serialise, and every build reaching a manifest used the default `None`.
  **An adoption build off a censused payload is exactly the case that hits it.**
- **`jfx_stats.py` could not import itself.** Its `sys.path` insert used `parents[2]` of
  the FILE (= `builder/`) and pointed at a nonexistent `builder/builder/analysis/…`.
  Invisible because `test_jfx_stats.py` inserts that path itself before importing, and
  nothing else had ever imported the module — "no consumer yet" is precisely why.
