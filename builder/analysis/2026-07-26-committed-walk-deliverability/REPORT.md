# Who did the router actually deliver? — committed-walk deliverability, 2026-07-26

**Role: the measurement record for this directory. It owns every figure below;
cite this file, do not restate its numbers.**

Read-only re-read of committed experimental runs. **No routing was run, no
rebuild, no arm, no adoption, no config touched** — the same class as `ASC-5`.

Artifact: `graph-t15-tiebreakfix.bin`, sha256
`4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8`, asserted
before any figure was computed.

## The question

`SYN-1`–`SYN-3` all presuppose that a low connection count is what keeps an
artist off the screen. `SYN-4` fixed the falsifier **before this ran**
(committed `c13f9a6`): if artists with few connections routinely appear as
interior cards, connection count is not what limits delivery.

Scope: the **production-like arm `P` only** — `arms.py:87`, "mirror-and-verify
target; user-facing baseline".

## What the runs contain, and one thing they do not

Interior artists **are** recoverable. Each run stores every walk as artifact
node ids plus a name map, so an interior card is `walk[1:-1]`.

**But the three runs are not three samples.** Track 2 stage 1, Track 2 stage 2
and Track 2F each contain a `P` arm, and all three are **byte-identical** —
same 12 pairs, same 9 depths, same 108 walks, same node ids throughout. `P` is
the deterministic baseline, so this is a **reproducibility** result, not extra
evidence. Every figure below is computed over **one** copy; counting three
would have inflated every instance count threefold.

| quantity | value |
|---|---|
| scored walks (12 pairs × 9 depths) | **108** |
| interior card instances | **384** |
| **distinct artists ever delivered as an interior card** | **156** |
| as a share of the artifact | **0.21 %** of 74,193 nodes |

## Connection counts of the artists delivered

| quantity | value |
|---|---:|
| **minimum degree observed** | **11** |
| maximum degree observed | 50 |
| median degree, distinct artists | 36 |
| median degree, weighted by cards shown | 39 |
| **distinct artists below 10 connections** | **0 (0.00 %)** |
| distinct artists at ≤ 2 connections | 0 (0.00 %) |
| interior cards below 10 connections | **0 of 384 (0.00 %)** |

| degree band | distinct artists | share |
|---|---:|---:|
| 1–2 | 0 | 0.00 % |
| 3–9 | 0 | 0.00 % |
| 10–19 | 12 | 7.69 % |
| 20–29 | 33 | 21.15 % |
| 30–39 | 51 | 32.69 % |
| 40–49 | 47 | 30.13 % |
| 50 (the cap) | 13 | 8.33 % |

**The structural null: 39,334 of the 74,193 nodes (53.02 %) hold fewer than 10
connections.** A degree-blind selection would put about half of interior cards
there. The observed share is zero, over 384 cards.

The ten lowest-degree artists ever delivered, with how many cards each filled:

| degree | artist | cards |
|---:|---|---:|
| 11 | Uriah Heep | 8 |
| 12 | No Doubt | 5 |
| 13 | Tom Waits | 2 |
| 16 | John Legend | 1 |
| 16 | Yes | 1 |
| 17 | Keane | 1 |
| 17 | The Cranberries | 5 |
| 17 | ABBA | 1 |
| 17 | PJ Harvey | 3 |
| 18 | The Raconteurs | 1 |

## `SYN-4`: the falsifier did NOT fire

| clause | threshold | observed | fired? |
|---|---|---:|---|
| distinct interiors below 10 connections | fires at ≥ 25 % | **0.00 %** | no |
| distinct interiors at ≤ 2 connections | fires at ≥ 5 % | **0.00 %** | no |
| expectation stated in advance | under 10 % | 0.00 % | met |
| instrument void — any degree-1 interior | voids the run | none | run valid |

## What this cannot support, stated as strongly as the result

**A low share was the expected outcome, and it is weak confirmation of
nothing.** `SYN-4` said so before the run and the pair set proves it: the 24
endpoints have a **median degree of 47** against the graph's median of 9,
**none** below 10 connections, and the pairs are Radiohead → The Beatles,
Madonna → Bob Dylan, Michael Jackson → Gorillaz and similar. That set was
pre-registered for a different experiment and skews hard toward famous
endpoints. **This test could fail meaningfully; it could not pass
meaningfully.**

So specifically:

- **156 distinct artists is a LOWER BOUND on what the app could deliver, not a
  measure of it.** 12 pairs cannot exercise 74,193 nodes. The figure bounds
  what *these* walks reached; it says nothing about the reachable set.
- **The 0.00 % does not show the router is incapable of delivering a
  low-degree artist.** It shows it did not, on a pair set chosen to be famous.
  Distinguishing *cannot* from *did not here* needs a pair set that asks.
- **Nothing here is about path quality**, and no cost weight was read.
- **The zero is not independent of the graph.** A low-degree artist has fewer
  chances to sit between two others; some of this is arithmetic, not routing.

## Gates

1. **Artifact sha256** asserted against the adopted value before any figure.
2. **Each run's own recorded `artifact_sha256`** matched it, so paths and
   degrees describe the same graph.
3. **Id-space gate** — every referenced node id's committed name equals the
   artifact's own name at that index, for all ids in all three runs. Without
   this, every degree here would be a lookup of an unrelated artist.
4. **Byte-identity across the three runs**, which converted a would-be
   threefold overcount into a reproducibility check.
5. **Void condition** — a degree-1 artist cannot be an interior card
   (`DRV-4`). None appeared; had one, the extraction would be wrong and the
   run void.
