# Where a rebuild from HEAD would drift from the served map — 2026-09-05

**Role: ACTIVE. Owns the figures below; they are cited elsewhere, never restated.**
Prompted by the owner asking whether the `CXR-` revert returned the app to its exact
pre-expansion state, and by another session's observation that **the revert moved the map but
not the drop list.** That observation is correct. This measures what it costs.

**Nothing here is about what the site serves now.** The API reads a prebuilt binary and never
loads a drop list — verified by grep over `api/src/`. Drop lists are applied by
`pipeline.py` at **build** time, so the served artifact carries whatever list was current when
it was built on 2026-08-06, and no later change can reach it. This document is entirely about
**what a rebuild would produce**, which is `LUX-E1`'s question.

Reproduce with `drift_check.py` (read-only, seconds, touches nothing served).

## 1. The one build input that moved

`CXA-` Task 2 (`7404a4c`) shipped a re-censused unlistenable payload and **repointed the
ALG-B default at it**. The revert did not repoint it back. The list the served map was
actually built with is still shipped, correctly marked "superseded as a DEFAULT, not
orphaned".

| | list | drops | censused over |
|---|---|---|---|
| built `graph-msw-tu50.bin` | `unlistenable_drop_algb_20260805.json` | 15,708 | 75,000 |
| **HEAD's default** | `unlistenable_drop_algb_20260809.json` | 27,262 | 117,302 |

**The absolute gap is misleading and must not be quoted on its own:** 11,584 MBIDs appear only
in HEAD's list, but nearly all of them name artists who exist only in the extended 117k
population and are simply absent from the served graph, where dropping them is a no-op.

## 2. What it costs on the population that actually exists

Restricted to the served graph's own 58,838 MBIDs, read from the artifact's metadata blob:

| | count |
|---|---|
| served graph population | 58,838 |
| **in the served graph and newly dropped by HEAD's list** | **31** |
| dropped by the built-with list but not by HEAD's (would return) | **0** |

**So a rebuild that changes only this one input yields a graph 31 nodes smaller — 0.05% —
and strictly a subset.** Nothing returns. Edge and largest-component effects follow from
removing those 31 and are not measured here.

## 3. What this predicts about `LUX-E1`, and what it does not

`LUX-E1`'s threshold is **byte-identical or not**, with no partial credit. A 31-node
difference is a different population, so **`LUX-E1`'s default-arm answer is knowable now and
it is RED** — without spending the rebuild.

**What this does NOT establish, and the distinction is the whole point:** that this is the
**only** drift. It is one input shown to have moved. A rebuild pinned to the 2026-08-05 list
either comes back byte-identical — proving this was the only build-side drift — or does not,
proving something else moved as well. **That second arm is the isolating baseline, and it is
the informative one;** the default arm's redness is now a foregone conclusion and reading it
alone would waste the run. `LUX-E1-AM1` in the scope document adds it.

The builder already supports the pin: `ce47106` (`SEL-`) added a per-invocation unlistenable
payload override, so the second arm needs no new code.

## 4. A second build input also moved, and it is not measured here

`CXA-` Task 1 (`c4cfbb1`) **recalibrated the acceptance bounds** (`acceptance.py`). Acceptance
governs whether a build is *admitted*, not what it *contains*, so it cannot change a sha —
but it means a rebuild is checked against bounds calibrated for the extended population.
Recorded so `LUX-E1` does not read a pass on the guard as evidence the population is
unchanged. The archive's standing warning applies: widening a bound to admit a build removes
the protection with nothing going red.

## 5. Ruled out, by inspection rather than assumption

- **The API never reads a drop list** (`grep -rn 'drop' api/src/` returns one unrelated
  comment), so none of this reaches a running service.
- **No routing weight moved.** Every weight in `ApiConfig` is identical between the
  pre-expansion state and HEAD — checked field by field.
- **The `no_release` and `featured_credit` drop families were not repointed.** `7404a4c`
  touched only the unlistenable family.
