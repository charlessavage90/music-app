# `LBA-A6` candidate — §8 items 1–3, built, serialised and pinned

**Role: ACTIVE. This directory OWNS every figure below.** The execution log
(`docs/superpowers/2026-09-21-lbd-s4-a6-adoption-execution-log.md`) owns the reasoning and
restates none of them; `NEXT.md` owns status and restates none of them either.

**The arm, in the words fixed before any result existed** (`LBA-` §2.2):

> **`LBA-A6`** — *every artist the deeper crawl found, at the two-listener bar.*

Population `P`, threshold 3, ListenBrainz's own pairing (`LBA-D1`), filter `on, inert (20260809)`.
Built on the owner's go/no-go ruling of 2026-09-21.

⚠ **This is the first build in the whole track that is a candidate for serving.** Every build
before it pinned `require_fame=False` and was an experimental control (`LBD-D7`, `LBA-D5`).

⛔ **NOT DEPLOYED, and `ApiConfig.graph_path` is UNCHANGED.** The app still serves
`graph-msw-tu50.bin`. This artifact exists to be run locally for `LBA-G5`, the unblinded use
gate (`LBA-AM4`), which is the owner's to run. **No journey has been generated on it and no
listen is designed** (`LBA-D3`).

Files: `cand_fame.py`/`.json` (the fame stage), `cand_ids_extract.py`/`.json` (the id
re-extraction), `cand_build.py`/`.json` (the build, the structural proof, acceptance, and the
serialisation).

---

## 1. The artifact

| | |
|---|---|
| path | `C:\unsung-fast\lbd-artifacts\LBA-A6-candidate.bin` |
| **sha256** | **`28311d81d264b8ee950d855aef4a812c93073263433d131c0ad1a982e5395d5b`** |
| bytes | 39,697,349 |
| sidecar | `LBA-A6-candidate.bin.json`, written by the shipped `build_manifest` / `write_manifest` |
| round trip | reloaded through the shipped api `GraphStore`: 87,394 artists, node order matches the build, fame ranking present |

**`DEP-24` honoured mechanically, not by care.** The checksum above was **read back out of the
written sidecar** and verified against the file on disk; it is never carried from a variable and
never transcribed by hand. Take it from the sidecar, not from this table.

⚠ **Stage 2's `LBA-A6.bin` is untouched.** The candidate has a new name precisely so a pinned
instrument input behind committed stage-2 and stage-3 results cannot be overwritten.

## 2. Inputs, and the proof that nothing pinned was touched

| input | sha256 | state |
|---|---|---|
| `S4-A6` archive `MANIFEST.json` | `950e3ee8…` | verified against stage 2's pin **before and after** every pass — **unchanged** |
| `LBA-A6.bin` (stage 2's build) | `199b9e20…` | verified, read-only, structural reference |
| `LBA-A6-bare.bin` (stage 2's bare copy) | `f35cb19d…` | verified, read-only, structural reference |
| `graph-msw-tu50.bin` (served) | `43dd82bb…` | verified, read-only, id-coverage baseline |

Stage 2's archive was opened through `ReadOnlyArchive` (`GRT-A1`), so a write would have raised
rather than landed. Fame records went to a **separate** directory,
`C:\unsung-fast\lbd-archives\S4-A6-fame`, and the build composed the two halves read-only
(`FameOverlayArchive`, `LBD-AM5-4`'s pattern).

**Step 6 of the refresh procedure does not fire at `P`.** The `20260809` payload already censused
`P` with 0 uncovered (`LBD-AM4-3`). `LBA-G3` fired on the *union* of all nine populations, not on
`P`.

## 3. The fame stage (§6 step 7)

| | |
|---|---|
| artists fetched | **87,764** (the archive's full artist set — a superset of the built node set) |
| measured null | **3** |
| wall clock | **80 s** |
| `LBA-M5` part 2's estimate for this arm | 88 batches, **58–77 s** |

The estimate was sound and slightly optimistic. On the built map, **87,391 of 87,394** nodes carry
a measured listener count.

⚠ **The round-trip figure "87,394 nodes with a fame percentile" is NOT the measured count.**
`graph_store.fame_percentiles` gives a measured null **0.0** — genuine maximal obscurity under the
novelty-likelihood construct — while **excluding** it from the frame, so no NaN survives. Both
numbers are in `cand_build.json` and they answer different questions.

## 4. The build

| | |
|---|---|
| nodes | **87,394** (largest component, of 87,764) |
| CSR entries | **2,490,728** |
| wall clock | **11.3 min** |
| p99 rescale | scale 2,035; 148,038 of 14,793,382 edges saturated (1.001 %) |
| config delta from stage 2's census build | **exactly `{require_fame}`**, asserted field by field |

### 4a. Structural identity — one sha256, and it holds

| | |
|---|---|
| candidate re-serialised with its five additive lists emptied | `f35cb19d935d53a184173d006791334b42b0b64ee9b7593b1c3ab1029b7c8d6d` |
| stage 2's `LBA-A6-bare.bin` | **identical** |
| structural fields compared against stage 2's `LBA-A6.bin` | **8 checked, 0 differing** |

The eight are `mbids` (node order), `names`, `disambiguations`, `offsets`, `neighbours`, `scores`,
`edge_types` and `pop_raw` (popularity). **Neither attaching fame nor re-extracting the id maps
moved the map.** Every structural figure stages 2 and 3 recorded therefore still describes this
artifact.

The four metadata id lists **are** expected to differ, and do — that is §5, not a structural
change. The bare comparison empties all five additive lists before serialising, which is exactly
why it remains the proof.

### 4b. `LBA-X8`'s go-stage measurement — the metadata overhead, measured not projected

| | bytes |
|---|---:|
| bare (as stages 2 and 3 sized it) | 30,261,096 |
| candidate, all five additive keys | **39,697,349** |
| **overhead** | **9,436,253 — +31.2 %** |

⚠ **This supersedes the +25.5 % measured before the id re-extraction.** The maps grew, so the
overhead grew with them; the later figure is the one that describes the shipped artifact.

## 5. Id and fact coverage — before and after the re-extraction

The three maps were frozen snapshots extracted over the **adopted artifact's** population. The
owner ruled on 2026-09-21 to re-extract over the candidate's, because a missing Deezer id sends a
clip down the name-search path — the `BYP-13` surface — and the gap was concentrated on exactly
the artists the use gate will look at hardest.

**The extraction:** offline, 2,945,470 dump rows in **2.2 min**, all **112,855** population
artists matched. Rejected relations: 180 Spotify, 58 Apple, 4 Deezer. **Strictly additive** — the
extractor refuses to write if any MBID the shipped maps held is missing, and it passed.

| map | map size | **served map** | **candidate** | **the 29,485 artists the candidate ADDS** |
|---|---|---|---|---|
| `deezer_ids` | 39,465 → **47,504** | 55.22 → **57.13 %** | 40.87 → **50.04 %** | 11.41 → **34.87 %** |
| `spotify_ids` | 52,421 → **61,636** | 69.07 → 69.07 % | 51.24 → **61.78 %** | 15.25 → **46.50 %** |
| `apple_ids` | 35,888 → **42,074** | 50.85 → 50.85 % | 37.49 → **44.57 %** | 10.10 → **31.08 %** |
| `artist_facts` | 89,090 → **109,147** | 97.22 → 97.22 % | 73.55 → **96.50 %** | 26.99 → **95.02 %** |

On the built artifact, node-indexed: `deezer_ids` 35,720 → **43,730**, `spotify_ids` 44,778 →
**53,993**, `apple_ids` 32,768 → **38,954**, `artist_facts` 64,274 → **84,331**.

**Deezer gained on the SERVED map too, and the asymmetry is informative.** The `LUX-4` maps were
extracted in September over a population that already contained the served map, so they had no gap
to close there. The Deezer map dates from 2026-08-02 and was extracted over the **pre-`MSW`**
adopted population of 74,193, so it was missing ids for served artists as well. That 1.91-point
gain is a real improvement to what is live today, not only to the candidate.

⚠ **Still a coverage gap, not a playability measurement.** A missing id degrades to name search,
which is today's behaviour, never a wrong answer. **It is not an `LBA-G5` signal**: a gate reading
that attributes a wrong-artist clip to the candidate has attributed a property of an id snapshot to
the similarity graph.

## 6. Acceptance — `PRODUCTION_ACCEPTANCE` as recalibrated 2026-09-21

**Seven checks, seven pass.** The bounds were recalibrated on the owner's ruling; the basis, the
sensitivity check and the accepted cost are in `acceptance.py`'s own comment and in the execution
log. **They were recalibrated in `acceptance.py`; the check itself was never bypassed** — the
build script refuses to serialise if `check_acceptance` still rejects, which is a separate guard
from the one asking whether the owner ruled.

| check | kind | measured | floor | ceiling | |
|---|---|---:|---:|---:|---|
| famous median degree | §2.8 **detector** | 49.0 | 25.0 | — | PASS |
| famous min degree | §2.8 **detector** | 23 | 8 | — | PASS |
| artists with no name | detector | 0 | — | 0 | PASS |
| canonical artists absent from LCC | detector | 0 | — | 0 | PASS |
| node count | tripwire | 87,394 | 69,900 | 105,000 | PASS |
| edge count | tripwire | 2,490,728 | 1,990,000 | 2,990,000 | PASS |
| median degree | tripwire | 26.0 | 5.0 | 34.0 | PASS |

⚠ **The accepted cost of that recalibration.** These bounds now **reject the served map**
(58,838 / 1,315,684) and **reject `LBA-A3` = `LBD-A5V`** (57,932 / 1,681,254), the fallback
`LBA-G5` would revert to. `tests/test_acceptance.py` asserts that rejection explicitly, and
`NEXT.md` carries the remedy: restore `acceptance.py`'s `PREVIOUS (MSW- restore 2026-09-05)` line
before rebuilding either map.

## 7. What is barred from being read off this directory

- **No path-quality or routing claim.** Nothing here scores a journey; no journey was generated on
  either map (`LBA-D3`).
- **No `LBD-` or `LBA-` criterion is re-read.** `LBA-M1`–`M5` and `LBA-G1`–`G4` stand exactly as
  stages 1–3 read them.
- **`LBA-AM4`'s four bars on `LBA-G5` apply in full** — in particular that a pass is not evidence
  of quality and does not substitute for the `REQ-38` listen.
- **§5 measures snapshot coverage, not playability.** `LBA-X2`(b) / `ULC-F4` already record that
  the un-listenable rule's own criterion is the name-search route while the app resolves by
  identity first.
- **Acceptance passing says nothing about whether the map is good.** It says the build is not
  malformed and is the shape the bounds were aimed at — which is, since 2026-09-21, this
  candidate.

## 8. Running it locally for `LBA-G5` — the owner's gate

⛔ **Nothing here deploys.** `ApiConfig.graph_path` is unchanged, so without `ARTISTPATH_GRAPH`
the API still boots the served map. This points one local process at the candidate.

⚠ **Do not start these from a Claude session's shell if the session runs in Orca.** When Orca
retires the session it kills the session's whole process tree, and both servers go with it — that
is how the gate's servers died at about 10:14 on 2026-09-24, mid-request and with no shutdown line.
**Start them detached instead:** run `C:\unsung-fast\lbd-artifacts\lba-g5-logs\start-servers.ps1`
from any PowerShell (a session can launch it via WMI `Win32_Process.Create`, which parents it to
the system rather than to the session). It sets the same three variables as below, appends API
stdout to a new `api-partN.log` in that folder, and passes `--host` to Vite so the phone can reach
it. The two terminal recipes below remain correct for a human at a keyboard.

**Terminal 1 — the API.** The checksum is read out of the sidecar by the command itself, never
typed (`DEP-24`):

```powershell
cd C:\dev\music-app\api
$env:ARTISTPATH_GRAPH = "C:\unsung-fast\lbd-artifacts\LBA-A6-candidate.bin"
$env:ARTISTPATH_GRAPH_SHA256 = (Get-Content "$($env:ARTISTPATH_GRAPH).json" -Raw | ConvertFrom-Json).sha256
$env:UV_LINK_MODE = "copy"
uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

**Terminal 2 — the frontend**, which proxies `/api` to port 8000:

```powershell
cd C:\dev\music-app\frontend
npm run dev
```

Then open the URL Vite prints (normally `http://localhost:5173`).

**Confirm you are on the candidate, not the served map**, before judging anything:

```powershell
(Invoke-RestMethod http://localhost:8000/api/meta)
```

`artists` must read **87,394** and `graph_sha256` must start **`28311d81`**. If it says 58,838 you
are on the served map and the environment variable did not take.

**Verified before being written here:** the boot path was exercised with exactly these values —
87,394 artists loaded, the fame ranking present, 43,730 Deezer ids — and a deliberately wrong
checksum was confirmed to refuse the boot, so the guard is real rather than decorative.
