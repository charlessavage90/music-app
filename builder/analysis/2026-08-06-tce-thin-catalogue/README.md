# `TCE-` — **VOID.** `TCE-G1` failed and no outcome was computed.

**Role: ACTIVE — results of record, and the result is a gate failure.** Governing document:
`docs/superpowers/specs/2026-08-06-thin-catalogue-edge-preregistration.md` (committed `31166c9`,
`TCE-AM1` at `dfe8a63`, `TCE-AM2` at `b757ea1` — **all three before this run**).

**This directory OWNS its figures.** Raw `tce_result.json`, runner `tce_run.py`. Cite it.

> ## ⛔ THE PROBE IS VOID. There is no `TCE-C1`, no `TCE-C2`, no `TCE-C3`/`C4`/`C5`, and no
> `Δ_R`. The run stopped at phase 3 of 7. **No branch fired and none may be inferred.**

---

## 1. What the gate returned

`TCE-G1` was evaluated **first and alone**, per §3. MBIDs read from the committed
`2026-08-06-laura-lee-closure/ll_closure.json`, per `TCE-AM2`, and the source is recorded in
`tce_result.json`.

| Artist | Required | **Measured (release-groups)** | |
|---|---|---|---|
| Laura Lee (Khruangbin member) | `== 0` | **0** | PASS |
| Laura Lee (soul & gospel, b.1945) | `≥ 20` | **16** | **FAIL** |
| Leon Bridges | `≥ 5` | **37** | PASS |
| Khruangbin | `≥ 5` | **59** | PASS |

**One cell failed, so the probe is void.** §3: *"Any cell failing → the probe is VOID. Not a
weak pass, not a caveat, not 'the instrument is approximate'."* The runner stopped before the
existence pass, before any run-state quantity, and before any `x_R`.

## 2. ⚠ The instrument is CORRECT. The threshold was wrong, and it was mine.

**Checked independently against the live MusicBrainz API after the failure**, which is
diagnosis of the instrument and not an outcome value:

| | dump counter | live MB API |
|---|---|---|
| Laura Lee (soul) | 16 | **16** |
| Leon Bridges | 37 | **37** |

**Exact agreement.** The counter also orders the four subjects correctly (0 < 16 < 37 < 59) and
returns exactly 0 for the motivating case. **Nothing suggests the instrument cannot see
catalogue size.**

**The defect is in how the threshold was set.** `≥ 20` was anchored on a *recording* count of
288 without ever checking what that implies for *release-groups* — 288 recordings across 16
release-groups is about 18 per group, entirely ordinary for a 1960s soul artist whose catalogue
is albums plus compilations. **The gate encoded a guess about the world, not a property of the
instrument**, and it was a bad guess.

> **That does not un-void the probe, and this document will not treat it as doing so.** A gate
> whose threshold is corrected *after seeing the value it failed on* is not a gate. The record
> is that it fired. Recalibrating a bound after a gate fires is a decision with a precedent
> here — `MSW-G3`, where the owner recalibrated deliberately and it was recorded as **his**
> decision, not the session's.

## 3. ⚠ A finding the gate surfaced by accident, and it is NOT about this probe

**MusicBrainz itself carries a same-name mis-credit between the two Laura Lees, and it is
inconsistent between levels.**

- The **recording** *Not Up for Discussion* is credited to `50ef58c4…` — the **Khruangbin
  member**. (Verified in the Laura Lee closure.)
- The **release-group** of the same name is credited to `70a65cf5…` — the **1945 soul &
  gospel singer**, whose disambiguation MusicBrainz returns as "soul & gospel
  singer/songwriter". Credited alongside Niia, who is the modern collaborator.

**Two consequences, and the first is uncomfortable:**

1. **Cell 1 of `TCE-G1` passed partly because of this mis-credit.** Had the release-group been
   credited correctly, the Khruangbin member's count would be `≥ 1` and the `== 0` cell would
   have failed instead. **The instrument is fine; the ground truth it was checked against is
   contaminated.**
2. **This is same-name confusion in the SOURCE data** — MusicBrainz — rather than in
   ListenBrainz's listen mapping. It therefore bears on the **open population question** at
   `docs/superpowers/2026-08-06-cocredit-investigation-execution-log.md` §6 item 1, which the
   Laura Lee closure left explicitly open. **It is not evidence for the thin-catalogue
   mechanism and must not be read as such**, and `n = 1` still licenses no rate.

## 4. Structural facts established before the gate — reportable, and NOT outcomes

| | |
|---|---|
| Arm A reference artists (archived list ≥ 30) | **45,693** of 75,000 |
| Arm B reference artists (degree ≥ 30) | **19,485** of 58,838 |
| Distinct MBIDs needing a catalogue size | **110,268** |
| Release-groups scanned | **4,431,141** |
| Needed MBIDs with ≥ 1 credited release-group | **90,414** |
| **Arm B reference artists with a rank-10 boundary tie** | **3,977 (20.4 %)** |

**⚠ The 90,414 figure is NOT the thin base rate and may not be used as one.** The existence
pass never ran, so MBIDs absent from the release-group dump are an unseparated mixture of
"artist with no releases" and "MBID that no longer exists". Separating them is exactly what
`TCE-G2` was rewritten to do.

**The tie figure is the one worth carrying.** §0.1 named `p99_log_clip`'s non-monotonicity as a
term dormant everywhere except the top of the list. **One arm B reference artist in five has a
score tie spanning the rank-10 boundary** — so the concern was real and correctly sized, and
any future run of this design must resolve those ties explicitly rather than by sort order.

## 5. Barred reads

1. **No outcome exists.** No `TCE-` criterion was computed. Nothing here supports `R1`, `R2`,
   `R3` or `R4`.
2. **"The instrument is fine" is not a pass.** §2 is diagnosis, not adjudication.
3. **The mis-credit in §3 is `n = 1`** and licenses no rate, in either direction.
4. **§4's counts are structural**, not results. In particular the release-group figure is not a
   base rate.

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-08-06-tce-thin-catalogue/tce_run.py
```

~9 min cold (75,000 archive files, then the release-group dump). The dump pass caches to
`rg_counts.json.gz`, which is gitignored as build output; deleting it forces a re-scan.
