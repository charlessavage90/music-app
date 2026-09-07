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

---

## 6. Why the 31 flipped — and the larger defect underneath it

*Added 2026-09-05 during `L4-T1`, prompted by the owner asking **why** clip resolution
differed between the two censuses. §2's count is unchanged; this explains its cause and
should be read before treating either drop list as authoritative.*

### 6.1 The proximate cause: the keep-check searches by NAME, and that search is unstable

All 31 were in the Aug-5 rule class and **all 31 were KEPT** by it — none was dropped, and
none passed the MusicBrainz release half. So both censuses agree they fail the release half;
what flipped is the second clause, *"unless a DSP link exists AND a clip resolves"*.

Worked example, `Foster Cazz` (MB-recorded Deezer id `52228272`):

| | Aug-5 census | Aug-9 re-census |
|---|---|---|
| `name_path.resolves` | **true** — matched `52228272`, track *"ACT III (THE DEATH)"* | **false** — no match |
| `id_path.resolves` | true — *"ACT III (THE DEATH)"* | **true** — *"ACT III (THE DEATH)"* |

Nothing about the artist changed; the same track was reachable by id on both days. The
**name search** did not find him the second time. `refused: []` on both, so this is not a
`ULF-4` refusal that would have been retried — Deezer answered normally and returned
different results.

**The reversals are symmetric, which is the signature of run-to-run churn rather than of a
rule or data change.** On the identical shared 75,000 population, under the identical rule:

| | count | rate |
|---|---|---|
| kept Aug-5 → dropped Aug-9 | **32** | 1.1% of Aug-5 keeps |
| dropped Aug-5 → kept Aug-9 | **30** | 0.2% of Aug-5 drops |

⚠ **This corrects a natural misreading of §2.** That section's *"strictly a subset; nothing
returns"* is correct **as scoped** — 0 return *to the served graph* — but 0 by construction,
since the 30 that would return were already removed at build time and cannot appear in a
served-graph intersection. On equal footing it is 32 out, 30 in. **Neither list is the more
accurate census; they are differently sampled.**

### 6.2 The root cause: the criterion measures the route the app tries SECOND

`api/…/clips.py` `_search` is explicit — *"Identity before name. When MusicBrainz records a
Deezer artist id we ask that artist directly, which involves no name matching and so cannot
return a different artist of the same name (`BYP-13`)."* That shipped **2026-08-02** at
`aff8fb5`, **three days before the Aug-5 census ran**.

The keep-check's criterion is `name_path.resolves` alone. So **the rule can call an artist
unlistenable while the app would play them on its first attempt:**

| census | dropped at the clip stage | of those, `id_path` resolves |
|---|---|---|
| Aug-9 list | 1,507 | **373 (24.8%)** |
| **Aug-5 list — built the SERVED map** | 740 | **220 (29.7%)** |

**So roughly 220 artists are absent from the live map whose clips the app's primary route
resolves.** Bounded claim: it is not established how many would have survived the
largest-connected-component prune, and the ~11.5k `drop_carried` entries from the older rules
carry no clip record in this payload and are unmeasured.

### 6.3 The spec is in tension with itself, and this read is not licensed by it

`ULF-2` states the rule as *"the app's own Deezer→iTunes resolution resolves a clip,
imported, never restated"* — and the app's own resolution is id-first. The next paragraph
calls the id-vs-name split *"instrument data only, never a criterion"* with **"no read of it
is licensed here"**, deferring it to `ULC-F4`. The implementation followed the second
sentence.

What suggests it went the wrong way is the *reason* given: *"a session drummer whose name
matches someone playable is exactly who this rule exists to remove."* That is an argument
that **name matching is too permissive** — and `_from_deezer_artist` does no name matching at
all. The excluded route is the more trustworthy one.

**§6.2's figures are the unlicensed `ULC-F4` read.** They are recorded here as grounds for
opening that track, and are **not** sufficient to change a rule: doing so needs its own
pre-registration, a re-census and a rebuild.

### 6.4 What was and was not done about it

- **Done (`L4-T1`, revert cleanup):** the ALG-B default was repointed back to
  `unlistenable_drop_algb_20260805.json`, the list the served map was built with. This stops
  the churn and restores the LOUD failure — the 75k census refuses against the extended
  archive rather than under-filtering it silently.
- **NOT done, and deliberately:** the criterion was not touched. Changing it alters the
  population, which would turn `LUX-4` from a metadata change into a **graph adoption** —
  acceptance gates and the owner's ear, the operation reverted on 2026-09-01. `ULC-F4` is
  its own track, after `LUX-4`, and the decision is the owner's.

## 7. Verification that the leftovers are cleared (2026-09-05, `L4-T1`)

A full build from the pinned archive with **no `--unlistenable-list` override** — i.e.
through the restored defaults — passed acceptance and produced
`43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`, **byte-identical to the
served artifact**, at 58,838 artists / 1,315,684 edges. This is stronger than `LUX-E1` arm
B′, which had to pin the drop list per invocation: the default path now reproduces
production, which is the build-side exit check §RCA of the handoff says a rollback owes.

⚠ **Build cost, measured rather than carried: 297 s wall clock, and the manifest's
`elapsed_seconds` recorded 297.3 — the timer does span the whole build.** The live map's
manifest records 39.2 s for the same archive, so **the "~40 s" figure is not a reliable
planning number**; the spread is roughly 7×, plausibly filesystem-cache state over an archive
of tens of thousands of small files. Budget minutes, not seconds. *(The earlier "~23 min"
remains struck; this does not restore it.)*
