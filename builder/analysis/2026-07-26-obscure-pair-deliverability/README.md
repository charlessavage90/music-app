# Deliverability on ordinary and obscure pairs — decision rule

**Role: ACTIVE analysis record. Owns its figures.** Cites, never restates,
`../2026-07-26-committed-walk-deliverability/` and the documents named below.

**Not an experimental arm, so not pre-registered as one.** No arm, no rebuild, no config
change, no adoption, no threshold. Production router settings, unchanged, on the adopted
artifact. **But it decides how an existing finding must be read, so its decision rule is
written and committed BEFORE the measurement runs**, in this file — the git history is the
evidence of that order. Modelled on `../2026-07-25-ceiling-ordering-headroom/`.

---

## The question, and why the existing answer is not one

`../2026-07-26-committed-walk-deliverability/` measured which artists the production router
actually delivered as interior cards, and found **none** below ten connections. Its own
report states the test **could fail meaningfully and could not pass meaningfully**: the
pairs were pre-registered for Track 2 with famous endpoints, whose median connection count
is several times the graph's own. Finding no obscure artists in the middle of journeys
between famous artists is close to what any router would do.

**This run supplies the missing arm**: the same instrument, the same production settings,
the same walk, on pairs whose endpoints are *ordinary* and *obscure*. It is the measurement
`CWD-5` named as the falsifier of `CWD-1`'s usefulness.

## Reuse, not new machinery

The instruction was to reuse the existing scorer if it can take a different pair set
cheaply, and to stop and report if it cannot. **It can, and nothing committed is
modified.** `../2026-07-24-track2-arm-scorer/run_arms.py` exposes `walk(store, src, dst,
cfg, ctx, pop, ...)` — a complete all-`known` walk for one pair — and the production arm's
config is `arms.STAGE1`'s `P` ("mirror-and-verify target; user-facing baseline",
`arms.py:87`). This directory imports both and drives them with a different pair set.

**The walk, the depths and the arm are therefore identical to the committed run by
construction, not by transcription.** Snapshots `(0, 1, 2, 3, 5, 7, 10, 15, 20)`, max depth
20 — `arms.py:35-36`. The only thing that differs is which pairs are routed, which is the
whole point.

## How the pairs are selected — no hand-picking

**Sampled from the graph's own connection-count distribution**, by node id, with a fixed
seed. Endpoints are never resolved by name: name lookup is what produced the wrong entity
twice in this project (`MKS-` §5, and `BYP-` §9), and sampling ids sidesteps both the
duplicate-name rule and `CNS-1` entirely.

- **Population.** Every node in the adopted artifact **except** those with an empty name —
  the one known contaminant, per the census. No popularity screen; popularity ranks nothing
  (§2.11) and is not consulted here at any point.
- **Two strata, by the node's own connection count.** The graph's median degree is 9
  (owned by `../2026-07-26-stranding-causes/REPORT.md`).
  - **OBSCURE** — degree in **[1, 5]**, well below the median.
  - **ORDINARY** — degree in **[6, 15]**, bracketing the median.
- **Draw.** `numpy.random.default_rng(20260726)`, 24 distinct nodes per stratum, uniformly
  at random without replacement, paired in draw order (1st with 2nd, 3rd with 4th, …).
- **Result: 12 OBSCURE→OBSCURE pairs and 12 ORDINARY→ORDINARY pairs**, 24 in total. Both
  endpoints of a pair come from the same stratum so the label is unambiguous. Twelve per
  stratum matches the committed run's twelve, so the comparison is like-for-like in size.

The seed, the strata bounds and the draw rule are fixed here **before** the sample is
inspected. Whatever it produces is what is routed.

## The decision rule

**Primary quantity: the share of DISTINCT interior artists whose connection count is below
ten.** Distinct artists, not cards — the same currency `SYN-4` and the committed run used,
so the two are directly comparable.

*(Plain: of all the different artists the app put in the middle of these journeys, what
fraction were barely-connected ones?)*

| outcome | threshold | what it means |
|---|---|---|
| **APPEAR FREELY** | **≥ 20 %** | the famous-pair zero was substantially an artefact of that pair set |
| **INTERMEDIATE** | strictly between | deliverable but under-represented; the reading survives only in weakened form |
| **DO NOT APPEAR** | **≤ 5 %** | the zero survives a pair set chosen to give low-connection artists every chance |

**The reference point is the graph, not zero.** Slightly over half of all nodes hold fewer
than ten connections (owned by `../2026-07-26-committed-walk-deliverability/REPORT.md`), so
a router indifferent to connection count would land near that share. **20 % is therefore
still far below indifference** — it is set where the result would clearly no longer be
attributable to the pair set alone.

### What each outcome does to the reading that connection count limits delivery

That reading is the premise under `SYN-1`–`SYN-3` in
`../../../docs/superpowers/findings/2026-07-26-low-degree-synthesis.md`.

- **APPEAR FREELY →** the premise is **not supported in general**. Low connection count
  does not prevent the router delivering an artist; `CWD-1` then describes famous journeys
  only, and `SYN-1`–`SYN-3` must be restated with that scope or lose most of their force.
- **DO NOT APPEAR →** the premise is **supported**, and materially so, because the pair set
  was built to give low-connection artists their best chance and they still did not appear.
  It remains an association, not a demonstrated cause.
- **INTERMEDIATE →** the premise holds **in weakened form**. I will report which side it
  fell on and by how much rather than rounding to a verdict, and will not re-describe the
  band afterwards.

**Secondary quantities, reported but not deciding:** the same share over interior *cards*
rather than distinct artists; the share at two or fewer connections; the minimum observed;
the full distribution; and the two strata separately.

### Stated in advance, for calibration

**I expect INTERMEDIATE, and I will guess 10–25 %.** The reasoning: `ASC-1` records that
the router climbs toward more popular artists about four times in five where the graph
offers a coin flip, which predicts interiors far better connected than the endpoints even
here — but a walk that *starts* at an artist with one or two connections has to take its
first hop among those few, so some low-connection cards should appear that the famous pairs
structurally could not produce. If the result is **0 %** again, that is a stronger finding
than anything in the committed run, and I have said so before seeing it.

## Gates, each of which aborts or voids

1. **Artifact sha256** asserted against the adopted value
   (`findings/2026-07-23-tiebreak-fix-adoption.md`) before any figure is computed.
2. **Void condition — a degree-1 artist cannot be an interior card** (`DRV-4`; census §1).
   One appearing means the extraction is wrong, and that reading is deliberately not
   available as a finding. *(Endpoints may be degree-1; interiors may not.)*
3. **Representativeness** — if fewer than 20 of the 24 pairs produce any interior card at
   all, the run is reported as unrepresentative and the shares are **not** quoted as a
   verdict. Pairs that yield no interior are **not dropped and not replaced**; dropping
   them would bias the sample toward exactly the pairs that route deeply.

## What this cannot support, stated before the result

- **It cannot separate pricing from arithmetic.** A low-connection artist has fewer chances
  to lie between two others, so part of any shortfall is combinatorial rather than a
  routing decision. This run does not distinguish them and no figure here should be read
  as "the router refuses".
- **It says nothing about famous journeys**, just as the committed run says nothing about
  obscure ones. The two are complementary and neither generalises to the other.
- **Nothing about path quality.** No cost weight is read, no criterion scored, no listening
  judgement implied. Whether these journeys are *good* is not measured.
- **It is one sample under one seed.** The strata bounds are a choice; a different band
  would move the figures.
