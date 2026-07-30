# Execution log — graph rebuild, Track A (`GR`), 2026-07-29

**Role: ACTIVE** — the retained record of the `GR` track, appended per task rather than
only at closeout. Governing document:
[`plans/2026-07-29-graph-rebuild-track-a.md`](plans/2026-07-29-graph-rebuild-track-a.md).
Branch `graph-rebuild-planning`.

**Owns no path-quality figures.** Scoring and path-quality figures live in
`findings/2026-07-21-scoring-adjudication.md` and are cited by section. The build-shape
figures below are this track's own and are owned here.

**Nothing is adopted. `BuilderConfig.algorithm` still carries `contribution_5`; the API
still boots `graph-t15-tiebreakfix.bin`.**

---

## §1 What ran, and in what order

The plan was written cold from the committed record, then executed inline in the same
session. Entry state: PR #49 merged to `main`, branch cut from the merge.

Order deviation worth recording: **GR-4's baseline step was run first**, before GR-1's
code landed, because it is the only moment the pre-drop refusal can be observed. The plan
anticipated this and named it as an option; it was taken.

## §2 GR-1 — the nameless-artist drop rule

**Baseline, taken before any code changed** (production archive, `cmd_build`):

```
INFO filtered 7 special-purpose entities
INFO largest component: 74193 of 74993 artists
ArtifactRejected: 33 artist(s) carry no name
  (e.g. 06e1ca5b-…, 12df23de-…, 18197573-…) — unsearchable, clipless,
  and renderable only as a blank card
```

The three sample MBIDs match the F8 record
(`builder/analysis/2026-07-24-track2-p8b-harness-review/`) exactly, and the largest
component matches the adopted artifact's 74,193. **The tripwire fired as designed and
nothing was written.**

**Owner evidence that upgraded the decision.** The drop-vs-backfill decision was already
the owner's (2026-07-28). On 2026-07-29 he checked the three most popular nameless MBIDs
against MusicBrainz by hand: **all three return "Artist not found"**. They are deleted or
merged upstream entities that survive in ListenBrainz's similarity data. So backfilling
names by MBID — the declined alternative — was never available at all. Recorded because it
converts a preference into the only implementable option.

Sampled for that check (adopted artifact, sha256 `4cb84ef9…` verified before reading):

| MBID | pop_pctl | degree | neighbourhood |
|---|---|---|---|
| `c9ba47ca-0bd2-4814-966d-ecfb06d032a3` | 0.91 | 11 | Japanese anime/game composers |
| `626d3be1-08a5-4b46-835f-67601919db26` | 0.88 | 14 | indie folk |
| `a55263d7-6ec2-4560-80cb-551bc6c94c9e` | 0.64 | 19 | English folk / Americana |

The blank name is an **upstream data gap, not a parse failure on our side** — the first
artist's neighbours carry CJK names correctly. This is the third time console/encoding
suspicion has been raised about this data and the second time it has been wrong; the
cause here is genuinely absent upstream data.

**Implemented** in `build_from_archive`, beside the special-purpose filter and before the
mass computation, so a dropped artist contributes to no marginal and a neighbour stranded
by the drop falls out at the largest-component prune rather than dangling. No config
knob: `REQ-2` is a Must and zero is the only defensible count, so a switch would be an
escape hatch on the guard.

## §3 GR-2 — algorithm selection

`BuilderConfig` was a frozen dataclass with no way to select the source algorithm and
`cli._config` threaded only `--target`, so **no trial build on a non-default algorithm was
possible** — the gap the RC session recorded and dissolved only because its instrument
constructed the algorithm string itself.

`PRODUCTION_ALGORITHM` and `PERMITTED_ALGORITHMS` now name the closed enum of six values
validated by `CS-P0e`; `--algorithm` is accepted by both `crawl` and `build` (build needs
it because GR-3 keys the archive *read* on it too). An unpermitted value raises
`SystemExit` at the CLI boundary rather than reaching the endpoint for its HTTP 400.

**The default is untouched**, and the test `test_config_default_algorithm_is_production`
pins it: flipping it *is* the re-crawl decision, which is the owner's.

## §4 GR-3 — algorithm-scoped keys (`RC-H3`)

Two hazards, both closed:

- **Archive key.** `similar/listenbrainz/{mbid}.json` did not encode the algorithm, so a
  re-crawl aimed at the existing archive would silently return production data to every
  future build. Production keeps the flat layout — 75,000 irreplaceable responses do not
  get moved, and every existing script finds them there — and every other algorithm gets
  a sub-tree. The flat build skips nested keys, so it cannot sweep a sub-tree in through
  the shared prefix.
- **Checkpoint.** A resumed crawl under a different algorithm would have treated the other
  algorithm's finished artists as done and skipped every one. The checkpoint now carries
  an `algorithm` field and refuses a mismatched resume. A missing field means production,
  so every pre-existing checkpoint still resumes.

## §5 GR-4 — verification rebuild

**Gate `GR-G1` — *"a rebuild of today's map from today's data, with the blank-name artists
dropped, is accepted by the build's own safety checks"* — PASSED.** Binary gate, no
refusal of any kind. The artifact was written, which is itself the evidence:
`check_acceptance` raises before `serialise` is reached.

```
INFO filtered 7 special-purpose entities
INFO dropped 36 nameless artists
INFO largest component: 74157 of 74957 artists
INFO wrote ./scratch/graph-dropnameless-verify.bin: 74157 artists,
     897620 edges (12.1 per artist), 14.7 MB, 29s
```

**Identity** (from the manifest sidecar, never transcribed by hand):
sha256 `73feffa03856f55dda134b84aa5ee40073495ae16f27e8116a4d961b65a69faa`,
built at commit `dd7bbe3`, 28.5 s. **Verification artifact only — not adopted, not
pointed at by anything.** The API still boots `graph-t15-tiebreakfix.bin`.

### Deltas against the adopted artifact (74,193 artists / 898,006 edges — RC log §7)

| Quantity | Adopted | GR-4 | Delta |
|---|---|---|---|
| Artists (largest component) | 74,193 | 74,157 | **−36** |
| Edges | 898,006 | 897,620 | **−386** |
| Pre-prune population | 74,993 | 74,957 | −36 |

### The 36-vs-33 reconciliation, because it looks like a discrepancy and is not

F8 and the baseline refusal both say **33**; the drop rule reports **36**. Both are
correct and they count different populations:

- **33** is blank names in the *emitted* graph — the largest component only, which is all
  `check_acceptance` and F8 ever see.
- **36** is blank names in the *full pre-prune* population, which is where the drop rule
  runs by design (before the mass computation, so a dropped artist perturbs no marginal).

So 3 of the 36 sat outside the largest component already. The arithmetic closes exactly:

```
pre-prune   74,993 − 36 (all blanks)            = 74,957   ✓ observed
component   74,193 − 33 (blanks inside the LCC) = 74,160
observed    74,157  ⇒  3 further nodes left the component
```

**Those 3 are the stranded neighbours the rule was written to catch** — nodes whose only
tie was to a dropped nameless artist, now pruned rather than left dangling as blank-card
dead ends. This is the first direct evidence that the stranding clause does real work on
production data; the unit test proved the mechanism, and here it fires three times.

**Edge delta.** −386, a net decrease. The plan predicted movement in *either* direction,
because removing a nameless artist from a top-50 candidate list promotes the 51st into
the mutual-k-NN cap and can mint new edges. A net loss of 386 against 36 dropped artists
(mean degree ~12, so ~430 edge-ends naively) is consistent with that partial offset. No
figure here needs explaining away.

**Cost, corrected.** The build takes **~29 seconds**, not the "~2 minutes" the RC log §6
records. That figure is not wrong so much as stale/generous; budget from 29 s.

**This discharges the second half of `acceptance.py`'s standing success condition** ("the
drop rule lands in the build and this check then passes on a rebuild"). The tripwire
stays in place, unweakened, as a standing rule for future crawls.

## §6 Test suite

| Point | Result |
|---|---|
| Baseline (AS log §10, recalled then re-run) | 115 passed |
| After GR-1 | 118 passed (+3) |
| After GR-2 | 123 passed (+5) |
| After GR-3 | 128 passed (+5) |

`test_replay.py`'s byte-identical rebuild test passes at every point, which is the
determinism sentinel for the flat production path.

## §7 Owed, and not discharged

- **`snyk_code_scan` has NOT been run** on any of the three code diffs — the Snyk CLI is
  unauthenticated in this environment and authenticating is a browser flow only the owner
  can complete. The global instruction requires it on new first-party code. Owed on
  GR-1/GR-2/GR-3; recorded in each commit message rather than left implicit.
