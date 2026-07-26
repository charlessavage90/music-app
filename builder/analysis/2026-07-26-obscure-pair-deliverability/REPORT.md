# Deliverability on ordinary and obscure pairs — 2026-07-26

**Role: the measurement record for this directory. It owns every figure below;
cite this file, do not restate its numbers.** The decision rule is in
[`README.md`](README.md) and was **committed before this ran** (`8aa6f84`).

Read-only on the artifact. Production router settings, unchanged. **No arm, no
rebuild, no config change, no adoption, no threshold.**

Artifact: `graph-t15-tiebreakfix.bin`, sha256
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted
before any figure was computed.

## The sample the rule produced

Drawn by node id under seed `20260726`, uniformly at random from each stratum,
after excluding the 33 nameless nodes.

| stratum | endpoint degree | pool | pairs |
|---|---|---:|---:|
| OBSCURE | 1–5 | 26,103 | 12 |
| ORDINARY | 6–15 | 26,224 | 12 |

**All 24 pairs produced interior cards**, against a rule requiring at least 20,
so the shares below are a verdict rather than a description of a thin sample.

| quantity | value |
|---|---:|
| scored walks (24 pairs × 9 depths) | **216** |
| interior card instances | **2,982** |
| distinct artists delivered as an interior card | **543** (0.73 % of the artifact) |

## Connection counts of the artists delivered

| quantity | value |
|---|---:|
| **minimum degree observed** | **4** |
| maximum degree observed | 50 |
| median degree, distinct artists | 29 |
| **distinct artists below 10 connections** | **18 (3.31 %)** |
| **distinct artists at ≤ 2 connections** | **0 (0.00 %)** |
| interior cards below 10 connections | **100 of 2,982 (3.35 %)** |

| degree band | distinct artists | share |
|---|---:|---:|
| 1–2 | 0 | 0.00 % |
| 3–9 | 18 | 3.31 % |
| 10–19 | 94 | 17.31 % |
| 20–29 | 172 | 31.68 % |
| 30–39 | 154 | 28.36 % |
| 40–49 | 101 | 18.60 % |
| 50 (the cap) | 4 | 0.74 % |

### By stratum — the obscure endpoints did move it, and not by much

| stratum | distinct | below 10 | share | min degree | cards |
|---|---:|---:|---:|---:|---:|
| OBSCURE | 358 | 17 | **4.75 %** | 4 | 1,596 |
| ORDINARY | 336 | 2 | **0.60 %** | 5 | 1,386 |

Starting a journey at an artist with one to five connections raises the share of
barely-connected artists in the middle by roughly eightfold over ordinary
endpoints — and **still leaves it under the rule's 5 % floor.**

The ten lowest-degree artists delivered, with cards filled:

| degree | artist | cards |
|---:|---|---:|
| 4 | The Dandy Warhols | 4 |
| 4 | Scott Wade | 9 |
| 5 | Dolly Parton | 1 |
| 6 | Slater | 9 |
| 6 | Fetty Wap | 2 |
| 7 | Young Fathers | 9 |
| 7 | Cyan Kicks | 9 |
| 8 | Scar | 9 |
| 8 | M.I.A. | 3 |
| 8 | Phillipa Alexander | 9 |

## Comparison with the famous-pair run

Figures for the famous pairs are owned by
`../2026-07-26-committed-walk-deliverability/REPORT.md` and are **cited, not
restated** — that report holds the counts, the zero, and the endpoint-degree
skew that made it uninterpretable on its own.

Stated as directions rather than as its numbers: moving from famous-to-famous
pairs to ordinary and obscure ones **lowered the minimum connection count
observed**, and **raised the share of low-connection interiors off its floor** —
but only to 3.31 %, against a graph in which slightly over half of all nodes are
below ten connections (that share is also owned by the committed-walk report).

**The direction of the change is what the pair-set objection predicted. The
magnitude is not.**

## The decision rule fired: DO NOT APPEAR

| clause | threshold | observed | fired? |
|---|---|---:|---|
| APPEAR FREELY | ≥ 20 % | 3.31 % | no |
| **DO NOT APPEAR** | **≤ 5 %** | **3.31 %** | **yes** |
| INTERMEDIATE | strictly between | — | no |
| representativeness | ≥ 20 of 24 pairs | 24 | ok |
| void — degree-1 interior | any voids the run | none | run valid |

**Prediction recorded before the run: INTERMEDIATE, 10–25 %. That was wrong** —
the observed share fell below the predicted range and past the opposite
threshold. Recorded rather than quietly dropped; the rule's outcome stands as
written and has not been re-described to accommodate the miss.

## What this still cannot support

- **It cannot separate pricing from arithmetic.** A barely-connected artist has
  fewer chances to lie between two others, so part of this shortfall is
  combinatorial rather than a routing decision. **This is the single largest
  unresolved confound and it was named before the run.** Nothing here licenses
  "the router refuses to deliver them".
- **It does not establish that these artists are undeliverable.** Eighteen
  distinct artists below ten connections *were* delivered, one at four
  connections. The finding is that they are rare, not absent.
- **The ≤ 2 zero is partly structural, not a discovery.** A degree-1 artist
  cannot be an interior card at all (`DRV-4`), so that population could only ever
  have contributed its degree-2 half.
- **One sample, one seed, two chosen bands.** A different stratum boundary would
  move the figures; 24 pairs cannot characterise 74,193 nodes.
- **Nothing about path quality.** No cost weight was read, no criterion scored,
  no listening judgement implied. Whether these journeys are *good* is not
  measured and not guessed at.
- **It says nothing about famous journeys**, which is the complementary
  restriction to the one the committed-walk report carries about obscure ones.
