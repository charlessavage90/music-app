# `LUX-E1` arm B′ — the live map rebuilds byte-identically. 2026-09-05

**This directory OWNS these figures.** Cite this file; never restate its numbers elsewhere.

- Script: `armb_sha.py` — run from `builder/`, ~40 s, offline
- Governing spec: `docs/superpowers/specs/2026-09-03-launch-ux-scope.md` §5, `LUX-E1`
  as amended by **`LUX-E1-AM1`** (the drop-list arm) and **`LUX-E1-AM2`** (the archive pin).
  Both were committed **before this ran**; the git timestamps are the evidence of ordering.

**Plain sentence, fixed in `AM2` before the result existed:** *if we build the map again from
the archive as it stood before the expansion, using the exact artist-exclusion list the live
map was built with, do we get the live map back byte for byte?*

**Threshold, also fixed before the run:** byte-identical to `43dd82bb…`, or not. No partial
credit.

---

## 1. Result — **BYTE-IDENTICAL. The threshold is met.**

| | rebuilt | live (`graph-msw-tu50.bin`) | |
|---|---|---|---|
| artists | 58,838 | 58,838 | match |
| edges | 1,315,684 | 1,315,684 | match |
| bytes | 17,773,958 | 17,773,958 | match |
| sha256 | `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` | same | **match** |

## 2. Pinned inputs — the two that had drifted

| input | pinned to | why |
|---|---|---|
| unlistenable ALG-B payload | `unlistenable_drop_algb_20260805.json` | `AM1` — HEAD's default is the re-censused 117k list |
| archive | `scratch/grt-archive-algb.pre-cex-snapshot` | `AM2` — the live tree gained 73,877 files after the build |
| algorithm | `CANDIDATE_ALGORITHM` (ALG-B), explicit | `CEX-R5`; matches the live manifest's recorded string |
| `cap_strategy` / `require_fame` | `trimmed_union` / `True` | the values the live manifest records |

## 3. What this establishes

- **The drop-list pointer and the archive were the ONLY build-side drifts.** Both are now
  identified and neither is a mystery. `AM1`'s and `AM2`'s "different" branches do not fire.
- **`LUX-4` is a metadata change as priced, not a graph adoption.** The gate is discharged.
- **Determinism (spec §9) holds** across a month and a reverted expansion.
- **It retro-validates an assumption no manifest records** — that
  `grt-archive-algb.pre-cex-snapshot` is the tree the live map was built from. Inspection could
  not confirm it; the sha does.

## 4. ⚠ A THIRD `CXA-` leftover, found by running this: **acceptance rejects the live map**

`artistpath-build build` **cannot** produce this artifact. `cmd_build` runs `check_acceptance`
*before* `serialise`, and `CXA-` Task 1 (`c4cfbb1`) recalibrated the bounds for the extended
population. A correct rebuild is refused:

```
ArtifactRejected: artifact rejected; not written:
  - artist count 58838 outside bounds [70900, 106400]
```

**The served map's own population is outside the bounds the builder would now admit.** This is
the same failure shape as the other two — the `CXR-` revert moved the map and did not move the
thing calibrated around it — and it is the third instance:

| `CXA-` leftover | moved by the revert? | consequence |
|---|---|---|
| unlistenable drop-list pointer | no | 31 artists newly dropped (`../2026-09-05-lux-e1-drift-source/`) |
| ALG-B archive tree | no | 73,877 extra responses; unpinned rebuild reads the extended crawl |
| **acceptance bounds** | **no** | **a correct rebuild is REJECTED and never serialised** |

**This is a blocker for `LUX-4`**, which must rebuild the artifact to add its fields and will
land on the same population and the same refusal. It is **not** a correctness problem with the
graph: acceptance governs whether a build is *admitted*, never what it *contains*, which is why
bypassing it here cannot change a byte and the comparison above stays valid.

**Bypassing acceptance is right for a probe and wrong for a shipping build.** `check_acceptance`
exists because the artifact is gitignored and a bad one is otherwise caught only by a human
noticing a missing artist. The fix belongs in the `LUX-4` plan and **which fix is the owner's**:
recalibrate the bounds back to the served population, or add the `--criteria` hook the CLI lacks
(`cmd_build` already reads `getattr(args, "criteria", PRODUCTION_ACCEPTANCE)`, so the code half
exists and no argument is wired to it). **A session must not widen a bound to admit a build** —
the archive's standing warning is that this removes the protection with nothing going red.

## 5. What this does NOT establish

- **Nothing about the app's quality, and no path was walked.** This is an identity check on a
  file.
- **Nothing about what a rebuild from HEAD's *defaults* produces.** Arm A was not run and does
  not need to be: its inputs are now both identified, and `AM1` predicted it red on the drop
  list alone.
- **It does not repoint anything.** No default moved. The candidate artifact
  `scratch/graph-luxe1-armb.bin` is byte-identical to the served one and adopts nothing.
- **It does not decide the 31 artists.** Whether to repoint the drop-list default back or
  accept the drop remains the owner's one-line choice, per `AM1`.
