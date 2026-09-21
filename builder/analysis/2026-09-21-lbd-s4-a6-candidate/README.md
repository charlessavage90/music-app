# `LBA-A6` candidate — §8 items 1–2, built and stopped at acceptance

**Role: ACTIVE. This directory OWNS every figure below.** The execution log
(`docs/superpowers/2026-09-21-lbd-s4-a6-adoption-execution-log.md`) owns the reasoning and
restates none of them; `NEXT.md` owns status and restates none of them either.

**The arm, in the words fixed before any result existed** (`LBA-` §2.2):

> **`LBA-A6`** — *every artist the deeper crawl found, at the two-listener bar.*

Population `P`, threshold 3, ListenBrainz's own pairing (`LBA-D1`), filter `on, inert (20260809)`.
Built on the owner's go/no-go ruling of 2026-09-21.

⚠ **This is the first build in the whole track that is a candidate for serving.** Every build
before it pinned `require_fame=False` and was an experimental control (`LBD-D7`, `LBA-D5`).

⚠ **NOT SERIALISED.** It fails `PRODUCTION_ACCEPTANCE` on three bounds. §8 item 2 reserves
recalibration to the owner. No bound was widened and none is proposed. **§8 item 3 (manifest
pinning) is therefore not reached** — it operates on a serialised artifact and there is none.

Files: `cand_fame.py` / `cand_fame.json` (the fame stage), `cand_build.py` / `cand_build.json`
(the build, the structural proof and the acceptance report).

---

## 1. Inputs, and the proof that nothing pinned was touched

| input | sha256 | state |
|---|---|---|
| `S4-A6` archive `MANIFEST.json` | `950e3ee8…` | verified against stage 2's pin **before and after** both the fetch and the build — **unchanged** |
| `LBA-A6.bin` (stage 2's build) | `199b9e20…` | verified, read-only, used as the structural reference |
| `LBA-A6-bare.bin` (stage 2's bare copy) | `f35cb19d…` | verified, read-only, used as the structural reference |

Stage 2's archive was opened through `ReadOnlyArchive` (`GRT-A1`), so a write would have raised
rather than landed. Fame records were written to a **separate** directory,
`C:\unsung-fast\lbd-archives\S4-A6-fame`, and the build composed the two halves read-only
(`FameOverlayArchive`, `LBD-AM5-4`'s pattern).

**Step 6 of the refresh procedure does not fire at `P`.** The `20260809` payload already censused
`P` with 0 uncovered (`LBD-AM4-3`), which is why stage 2 could build this arm with the filter on
and applicable. `LBA-G3` fired on the *union* of all nine populations, not on `P`.

## 2. The fame stage (§6 step 7)

| | |
|---|---|
| artists fetched | **87,764** (the archive's full artist set — a superset of the built node set by construction) |
| measured null | **3** |
| wall clock | **80 s** |
| `LBA-M5` part 2's estimate for this arm | 88 batches, **58–77 s** |

The estimate was sound and slightly optimistic. A null is a **measured absence** and is never a
floor value (`FAM-AM1.8`).

## 3. The build

| | |
|---|---|
| nodes | **87,394** (largest component, of 87,764) |
| CSR entries | **2,490,728** |
| wall clock | **16.7 min** (14.2 min on the discarded first run — machine variation only) |
| p99 rescale | scale 2,035; 148,038 of 14,793,382 edges saturated (1.001 %) |
| config delta from stage 2's census build | **exactly `{require_fame}`**, asserted field by field |

### 3a. Structural identity — one sha256, and it holds

| | |
|---|---|
| candidate re-serialised with its five additive lists emptied | `f35cb19d935d53a184173d006791334b42b0b64ee9b7593b1c3ab1029b7c8d6d` |
| stage 2's `LBA-A6-bare.bin` | **identical** |
| fields compared against stage 2's `LBA-A6.bin` | **12 checked, 0 differing** |

The twelve are `mbids`, `names`, `disambiguations`, `deezer_ids`, `spotify_ids`, `apple_ids`,
`artist_facts`, `offsets`, `neighbours`, `scores`, `edge_types`, `pop_raw`. **Attaching fame and
the id maps moved nothing**: node order and all four CSR arrays are byte-identical to the map
stages 2 and 3 measured. Every structural figure those stages recorded therefore still describes
this artifact.

### 3b. `LBA-X8`'s go-stage measurement — the metadata overhead, measured not projected

`LBA-X8` said every size figure in the pre-registration is a lower bound and that the exact
overhead would be measured here, on the candidate.

| | bytes |
|---|---:|
| bare (as stages 2 and 3 sized it) | 30,261,096 |
| candidate, all five additive keys | **37,986,239** |
| **overhead** | **7,725,143 — +25.5 %** |

### 3c. Fame coverage

**87,391 of 87,394** nodes carry a measured listener count; **3** are measured nulls.

## 4. Clip and streaming id coverage — the number that bears on the use gate

The three id maps are **frozen snapshots extracted over the adopted artifact's population**, which
is today's served map, not `P` (`deezer_ids.py`'s own docstring; `NEXT.md` carries it as a
deferral whose condition is *"whenever it is next questioned"*).

| map | on the served map | on the candidate | **on the 29,485 artists the candidate ADDS** |
|---|---:|---:|---:|
| `deezer_ids` | 55.22 % | **40.87 %** (35,720) | **11.41 %** |
| `spotify_ids` | 69.07 % | **51.24 %** (44,778) | **15.25 %** |
| `apple_ids` | 50.85 % | **37.49 %** (32,768) | **10.10 %** |
| `artist_facts` | 97.22 % | **73.55 %** (64,274) | **26.99 %** |

The candidate keeps **57,909** of the served map's 58,838 artists and adds **29,485**.

⚠ **This is a coverage gap in a dated snapshot, not a property of the map**, and it is
concentrated almost entirely on the added artists. A missing Deezer id degrades to name search,
which is the `BYP-13` surface — a card playing a different artist of the same name. **It is not a
`LBA-G5` signal**, and a gate reading that attributes it to the candidate has attributed a
property of the id snapshot to the similarity graph.

## 5. Acceptance — `PRODUCTION_ACCEPTANCE`, unmodified

**Seven checks. Four pass, three fail.** No bound widened, none proposed.

| check | kind | measured | floor | ceiling | verdict |
|---|---|---:|---:|---:|---|
| famous median degree | §2.8 **detector** | 49.0 | 25.0 | — | **PASS** |
| famous min degree | §2.8 **detector** | 23 | 8 | — | **PASS** |
| artists with no name | detector | 0 | — | 0 | **PASS** |
| canonical artists absent from LCC | detector | 0 | — | 0 | **PASS** |
| node count | **tripwire** | 87,394 | 47,000 | 71,000 | **FAIL — 16,394 over, 123.1 % of the ceiling** |
| edge count | **tripwire** | 2,490,728 | 1,050,000 | 1,580,000 | **FAIL — 910,728 over, 157.6 % of the ceiling** |
| median degree | **tripwire** | 26.0 | 5.0 | 25.0 | **FAIL — 1 over, 104.0 % of the ceiling** |

The shipped check's own wording, quoted rather than paraphrased:

```
artifact rejected; not written:
  - artist count 87394 outside bounds [47000, 71000]
  - edge count 2490728 outside bounds [1050000, 1580000]
  - median degree 26.0 outside bounds [5.0, 25.0]
```

**The kind column is `acceptance.py`'s own distinction and it is the whole reading.** The two
`famous …` bounds are the §2.8 failure-signature detectors — the Radiohead collapse — and both
pass with margin. The three that fail are **regression tripwires**, which `acceptance.py` states
are deliberately generous and exist to catch *a build that silently loses a large share of the
graph*. This build fails them by being **larger**, which is the direction they were never written
to police.

### 5a. Sensitivity of a recalibrated band — arithmetic only, NOT a recommendation

§8 item 2 requires that a new centre be derived independently of the build that went red, that the
tolerance stay at about ±20 %, and that sensitivity be checked against the four artifacts
`acceptance.py` names. **The 2026-08-06 `MSW-` precedent centred the band on the candidate.** That
arithmetic, applied here, gives nodes 69,915–104,873 and edges 1,992,582–2,988,874:

| artifact | nodes | edges | node bound | edge bound | verdict |
|---|---:|---:|---|---|---|
| served `MSW-` map — **must ACCEPT** | 58,838 | 1,315,684 | OUT | OUT | **reject** ⚠ |
| `JFX-B`, the reverted adoption — must reject | 88,685 | 1,618,164 | in | OUT | reject |
| retired pre-`MSW` mutual-kNN — must reject | 74,193 | 898,006 | in | OUT | reject |
| mutual-kNN of this archive — must reject | 81,749 | 905,558 | in | OUT | reject |
| `LBA-A3` = `LBD-A5V`, the `LBA-G5` fallback | 57,932 | 1,681,254 | OUT | OUT | reject ⚠ |

**Two things this arithmetic shows, and neither decides anything:**

1. **All three "must reject" verdicts survive — but entirely on the edge bound.** The recalibrated
   node band admits every one of them, including `JFX-B`, the artifact the owner's ear rejected in
   August. That is consistent with `acceptance.py`'s own warning that the edge floor is the only
   bound that can see a silent cap-rule revert; here it is the only bound doing any work at all.
2. **It would reject the served map and the fallback.** That is precisely the drift `LUX-E1`
   diagnosed on 2026-09-05, where a *correct* rebuild of the live map was refused before
   `serialise` and never written. It bites only if either map is ever rebuilt — which the `LBA-G5`
   fallback path would require.

## 6. What is barred from being read off this directory

- **No path-quality or routing claim.** Nothing here scores a journey; no journey was generated on
  either map (`LBA-D3`).
- **No `LBD-` or `LBA-` criterion is re-read.** `LBA-M1`–`M5` and `LBA-G1`–`G4` stand exactly as
  stages 1–3 read them.
- **`LBA-AM4`'s four bars on `LBA-G5` apply in full**, in particular that a pass is not evidence of
  quality and does not substitute for the `REQ-38` listen.
- **The id-coverage table in §4 says nothing about whether those artists are playable** — it
  measures snapshot coverage, and `LBA-X2`(b) / `ULC-F4` already record that the un-listenable
  rule's own criterion is the name-search route while the app resolves by identity first.
- **§5a is arithmetic, not a proposal.** No bound is recalibrated here.
