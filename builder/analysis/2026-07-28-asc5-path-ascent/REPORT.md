# ASC-5 discharge — results. 2026-07-28

**Role: the deliverable of this directory. OWNS its figures.** Decision rules were
committed at `8562d15` before the script first ran; every read below is the
pre-committed branch fired by the measured value, quoted from `README.md` unchanged.
Raw figures: `asc5_path_ascent.json`. Instrument: `asc5_path_ascent.py` (Snyk-clean).

**Gates: all passed.** PLA-G1 reproduced the P8b one-hop figures exactly (null 0.4998,
A0 0.8261, X 0.8687 at 4 dp). PLA-G2 artifact identity held (`4cb84ef9…`, = sidecar =
`paths.json`). PLA-G3 found zero degree-1 interiors across all 11 arms' cells.

**Currency: in-graph popularity percentile / pop_raw throughout, except PLA-R4(a),
which is fame (log10 pageviews) from committed `scores.json`.** Popularity is not fame
at the top (§2.11); nothing below is a fame claim unless marked as one.

---

## PLA-R1 — the climb does NOT survive to the first path; the famous middles there are arithmetic

*(Plain: on journeys between two famous artists, the app's middles are about as famous
as the middles of the shortest possible routes on the map itself — the map forces
famous middles there, whatever the router prefers.)*

**Measured.** `D` = median over 10 included pairs of (delivered interior median pctl −
geodesic interior median pctl) = **+0.0004**. Two pairs excluded (direct edges:
Radiohead → The Beatles, Muse → Coldplay). Per-pair: seven pairs within ±0.005 of
zero, three of those *negative* (the router's middles slightly **less** popular than
the geodesic set's). The geodesic interior sets themselves sit at median pctl
0.938–0.9998 — **the hop-minimal routes between these endpoints already pass almost
exclusively through top-1 % artists.**

**Pre-committed read fired: `D ≤ 0.03` → ASC-3 collapses at path level** — on this
pair set's first paths, the interiors the router delivers are roughly what any short
route forces, and a pricing account of famous first-path interiors does not hold here.

**The one figure cutting against the blanket reading, named:** Nirvana → CROOVE — the
only pair with an obscure endpoint — is **+0.054**, delivered 0.992 vs geodesic 0.938.
Where the structure leaves headroom to route obscure, the router visibly climbed. One
pair; directionally consistent with ASC-1; not separable from noise on n = 1.

## PLA-R2 — context: twenty bypasses never leave the top of the popularity ordering

*(Plain: after twenty presses of "I know them", the typical artist in the middle of
the journey is still inside the top half-percent of the app's popularity ordering, and
the single most obscure artist ever shown across all twelve journeys and every depth
is still inside the top ten percent.)*

| depth | pairs | interiors pooled | median pctl | min pctl |
|---|---|---|---|---|
| 0 | 12 | 35 | 0.9948 | 0.9020 |
| 3 | 12 | 37 | 0.9982 | 0.9020 |
| 7 | 12 | 35 | 0.9960 | 0.9020 |
| 10 | 12 | 49 | 0.9980 | 0.9020 |
| 15 | 12 | 50 | 0.9959 | 0.9020 |
| 20 | 12 | 58 | 0.9979 | 0.9020 |

No decision hangs on this table (README); it is the popularity-currency statement of
the problem the owner named, beside C3's fame-currency one (P fails the depth gradient
at 0.164 vs 0.5, owned by `scores.json`). The depth profile is **flat**: the ladder
replaces famous artists with equally famous artists all the way down.

## PLA-R3 — one-hop X vs A7: ambiguous band, by 0.0003

*(Plain: removing the last of the price on moving between fame levels makes the
cheapest next step climb slightly more often — but the effect is right on the line we
drew in advance between "too small to matter" and "worth attention".)*

**Measured.** ascent(A7) = 0.8484, ascent(X) = 0.8687, **Δ = +0.0203** against bands
|Δ| ≤ 0.02 / Δ ≥ 0.05. **Pre-committed read: ambiguous band**, and it is stated as
such rather than rounded into either neighbour.

What is *not* ambiguous is single-arm and against the null (ASC-1's own class): **X's
cost is the similarity term alone, and it climbs on 86.9 % of nodes against a 50 %
null.** The similarity term by itself reproduces the whole climb; the diluted jump
price modulates it by about two points.

## PLA-R4 — path-level X vs A7: the jump price is immaterial across whole journeys

*(Plain: across full journeys with up to twenty bypasses, the two settings that differ
only in that price delivered middles of essentially identical fame.)*

**Measured.** (a) Fame: **+0.0037 log10** (committed `scores.json` isolating block,
exact per F9) against bands 0.1 / 0.3 — **read: jump price immaterial at path level.**
(b) Popularity: median paired interior-pctl difference at d ≥ 10 = **−0.0019** over 36
paired cells. Both currencies agree.

---

## What I infer (labelled as inference, plain language)

1. **The first path between two famous artists cannot be made less famous by any cost
   function, because the map itself offers no un-famous short routes there.** That is
   not even a defect by the owner's own calibration (WGLL value 9: fame should track
   the endpoints on the first path).
2. **The live failure is the bypass ladder** — it should trade fame for novelty as it
   deepens, and it measurably does not (PLA-R2 here; C3 in fame units). Two repricing
   tracks and the toll already failed to move this, and this measurement says why that
   account is coherent: the climb is carried by the similarity term itself (PLA-R3's
   single-arm figure), which no symmetric repricing of the popularity terms touches,
   and nothing in the cost function becomes *more* obscurity-seeking as bypass depth
   grows — the floor device only ever *permits* diving (and dies by d20, P8b F7); no
   term ever *rewards* it.
3. **For the parked p99 rescale**: scoring its pre-registration on famous-pair
   first-path fame would be structurally doomed (PLA-R1) — any fame criterion must
   live on bypass-depth gradient and/or pairs with non-famous endpoints, where
   movement is possible (Nirvana → CROOVE is the existence proof).

## Weakest link

**The geodesic null is hop-minimal, not cost-agnostic.** "Any short route is famous"
was measured on minimum-hop paths; slightly longer routes (the router's actual
alternatives) may offer less famous interiors that neither the geodesic set nor the
delivered path exposes. If a k-shortest-paths or near-geodesic ensemble showed
plentiful low-pctl interiors within +1–2 hops of minimal, PLA-R1's "arithmetic"
reading would weaken back toward pricing. That re-read is cheap (same instrument class)
and has not been run. Second: ten pairs, famous-skewed by construction (CWD-2's shape)
— PLA-R1's collapse is a statement about *this pair set's first paths*, not about the
graph. I would defend the gates, PLA-R2's table and PLA-R4 cheaply; I would abandon
the blanket "arithmetic, not pricing" reading on one contrary near-geodesic ensemble
measurement.

## What this does not establish

- Nothing about **fame** from any fresh figure (currency notice).
- **It does not reopen §2.12** — "the router prices the stratum exits correctly and
  declines them" is about bypass-depth reachability; PLA-R1 is about first paths.
  PLA-R2 is consistent with §2.12 standing.
- Nothing about the **degree floor** or the low-degree axis (different currency).
- No arm, no adoption, no rebuild, no threshold for any future experiment.
