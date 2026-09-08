# Handoff — `LBD-` Tasks 1 and 2 done, 2026-09-07

**Role: SUPERSEDED on next actions, 2026-09-08.** [`2026-09-08-HANDOFF-lbd-task4-midflight.md`](2026-09-08-HANDOFF-lbd-task4-midflight.md) is the current handoff for the `LBD-` track and supersedes this one **on next actions**; this document's account of Tasks 1–2 and of what must not be reverted still stands. *(Was: the current handoff for the `LBD-` track.)* It does **not** supersede
[`2026-09-06-HANDOFF-lux-4-artifact.md`](2026-09-06-HANDOFF-lux-4-artifact.md), which remains
current for `LUX-4`: the two tracks are independent, neither blocks the other, and each has its
own next task. It states no project status — [`NEXT.md`](NEXT.md) owns that.

**A SEAM handoff, and a deliberately chosen one.** The pre-registration is a **material
mid-flight amendment to two committed governing documents**, which `CLAUDE.md` names as a seam
in its own right: there is a new governing document, and the next session reads it cold, which
is the condition the amendment was written for. The degradation tell did not fire.

Branch `lb-dump-exploration`, **PR #109 (draft)** — both are addresses; `git` and `gh` own what
has landed.

---

## Start here

**Task 3** — `lbd_similarity.py`, ListenBrainz's job reimplemented in DuckDB. Continue at
[`plans/2026-09-06-lb-dump-exploration.md`](plans/2026-09-06-lb-dump-exploration.md) Task 3,
**read through**
[`specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md),
which governs and whose §10 lists what it amends in the plan and the design. Neither of those
two is edited; do not "fix" them in place.

**Nothing is assigned to the owner by this work.** His outstanding items are unchanged and
predate it. One thing that is his and is **not** a blocker: the plan review found most of
today's sparsity is attributable to our own degree ceiling rather than to missing listening
data, so whether `LBD-` is still where to spend is his call. Nothing waits on it.

## What this session did

Tasks 1 and 2, from a worktree at `C:\Users\charl\worktrees\music-app-lbd`, reading
`builder/scratch/` by absolute path and writing only under `D:\unsung-large-data\`.

1. **Task 1** — inputs verified and pinned; three descriptive reads added. Figures are owned by
   [`builder/analysis/2026-09-07-lbd-inputs/README.md`](../../builder/analysis/2026-09-07-lbd-inputs/README.md),
   cited never restated.
2. **Task 2** — the pre-registration, **committed before anything ran on real data**. The git
   timestamp is the evidence that cannot be reconstructed afterwards.

## The one thing that changes the run plan

**Verified from ListenBrainz's own source, re-fetched from master by URL** (sha256
`7a8516be7fb0c25b99ef63f3210029c348cf69c987a3ce540f325262e4b90de3`) rather than read from the
plan's prose — a review had found the plan's prose contradicts the SQL it quotes.

`threshold` and `limit` are the **only** two tokens applied after the cross-user aggregation,
and neither enters the `score` expression. So the first four arms are **filters over one
materialised pair table**, not four full-history runs. `contribution`, `session`, `skip`,
`days` and the pairing semantics all change `score` and are **not** derivable.

The chunking fallback is **exact**: every stage up to and including the per-user cap partitions
by `user_id`, so only the final cross-user `SUM` needs re-summing after a union of chunks.

## Claims an editor must NOT revert

- **The pre-registration was committed before results existed.** If a later session finds a
  criterion inconvenient, the answer is a dated amendment with its own reasoning, **never an
  edit to the values.** That property is the whole point of the document.
- **`LBD-C2a` (pair-table level) is the primary supply statistic and `LBD-C2b` (graph level) is
  secondary.** This is not a preference. Our own degree ceiling absorbs supply, so a
  graph-level null is **barred** from supporting `LBD-R1`.
- **`LBD-A3`, the both-relaxed corner, is not optional.** With only the two single-knob arms,
  each null is explicable by the other rule still binding. Do not drop it to save a run — and
  under the restructure above it costs almost nothing anyway.
- **The full dump's published `.tar` is not on disk**, so its checksum was never verified. Do
  not write or imply that it was. The substitute and its limits are in the README's §1 warning.
- **The degree ceiling is a named exposure, not a held constant** — and a strong pair-table
  result does **not** imply an easy ceiling change downstream. Track B measured the cost of
  raising it and the bound-100 set fired the hub-transit bar; both sweeps predate the crawl
  extension, so the ceiling's effect on the added set is unmeasured. **Neither fact discharges
  the other.**
- **`drop_unlistenable=False` on every arm including the baseline.** The drop lists are then no
  longer the served map's filtering, which is recorded rather than worked around.

## What I know that is not in the durable record

1. **Two verification failures, both caught by the rules rather than by care.** The
   `mbdump.tar.bz2` download failed sha256 because `curl -C -` resumed onto a partial file left
   by a killed job and appended 269 MB of duplicate bytes; and the LB dump's tar turned out to
   be absent entirely, so its published checksum could not be checked at all. **The reusable
   lesson is the second one: an input can fail verification by being unverifiable, and that
   reads as success to any check that only compares two hashes when both are present.**
2. **A background command using `nohup … &` inside the Bash tool's own background mode is
   killed** when the wrapper exits — it looks like a failure of the command. Run the command in
   the foreground *of* the background task instead.
3. **The two long jobs saturated `D:` and starved each other**, one to about 1 second of CPU
   in twenty minutes. If a scan looks hung here, check disk throughput before suspecting the
   query.
4. **`unnest` over the whole dump appears not to get column projection pushdown** — the read
   behaved as though far more than the three named columns were being fetched. Task 3's
   aggregation should be written to avoid relying on it, and its cost estimated from a slice
   (`LBD-G4`) rather than from column sizes.
5. **The plan's Task 4 points at "the `LUX-E1` README" and there are two.** The snapshot is
   pinned in `2026-09-05-lux-e1-armb/README.md` §2, not in `-drift-source`. Recorded in the
   inputs README §6.
6. **Two MusicBrainz schema traps, and the second is the reusable one.** `SCHEMA_SEQUENCE` and
   `TIMESTAMP` are at the **archive root**, not under `mbdump/` as the plan implies — harmless,
   and they are the first members so they cost seconds. The one that matters: **`artist` has
   nineteen columns, not seventeen.** Its DDL puts an inline `CHECK` constraint after `ended`
   and then continues with `begin_area` and `end_area`, so a reader who stops at the first
   constraint undercounts. This session did, and said so in the README rather than quietly
   fixing it. **The parser caught it because the column count was declared; it would have been
   silent under `ignore_errors` or `null_padding`,** which are exactly what the error message
   suggests trying. Do not take that suggestion on a positional dump.
7. **`ACTIVE_SCHEMA_SEQUENCE` on MusicBrainz master is 31 and the dump is 31**, so
   `CreateTables.sql` at master is this dump's schema. If a later session takes a newer dump,
   **re-check that pairing before reusing these column lists** — a tagged schema may be needed.
6. **Another session was live in the main tree** throughout. This session took a worktree, used
   pathspec commits, and touched `docs/README.md` with two inserted rows and two appended
   clauses rather than any rewrite, so it reconciles in either merge order.

## ⚠ One adjacency the next session must check before relying on `LBD-X1`

**Another session was working on the degree ceiling while this one ran**, on branch
`dcf-degree-ceiling-falsifier` under its own `DCF-` identifier series. As of this handoff that
work is **not on `main`** and this session **deliberately did not read it** — a second opinion
that has absorbed another session's working notes is not independent, and `LBD-X1` was written
from the committed record only.

**Why it matters here.** `LBD-X1` states that the ceiling's effect on the `CXR` added set is
**genuinely unmeasured**, because both Track B sweeps predate the crawl extension. That is true
of the committed record as of 2026-09-07. **If `DCF-` lands and measures that set, the claim
goes stale**, and the pre-registration would be citing an absence that no longer exists.

**The check, and it is cheap:** before executing Task 3, `git log origin/main` for `DCF-`. If it
has landed, read what it establishes about the added set's degree and **record whether `LBD-X1`
needs an amendment** — dated, with its reasoning, never an edit to the values. Nothing else in
this pre-registration depends on it: `LBD-X1`'s operative consequence is the **bar** on reading
a graph-level null as supporting the track's central risk, and that bar rests on the ceiling
being an active term, which no measurement of its size would remove.

**Do not treat this as a reason to pause.** The two tracks are independent by design §9, which
puts any cap-rule or ceiling change outside `LBD-` entirely.

## Deferred, with conditions

| item | condition |
|---|---|
| `LBDR-F4` — `recording_gid_redirect` is omitted, so a share of listens will not join the recording-length frame and will fall back to the 180-second default | **Discharged at Task 3**, which already owes the unmatched share. Measuring it in Task 1 would need the join Task 3 builds |
| `LBDR-F6` — Tasks 6/7 have no scale budget, and `build_from_archive` holds every payload in memory (`pipeline.py:181`, `payloads: dict[str, bytes]`, verified 2026-09-07) | **Discharged when `LBD-M1` produces an arm's artist and neighbour counts** |
| The dump tar's checksum | **Discharged if a session re-downloads the published tar and verifies it.** Until then no claim may rest on byte-identity to the published dump |
| `LBD-C3`'s revisit threshold resting on no measurement | **Discharged at the full pass**, which produces the first real figure. `LBD-G3`'s 12 h bound is a working-session choice and is labelled as one |
| **The Snyk scan did not run on the three new scripts** — credentials are expired (`401`, and the stored config holds an OAuth entry with no API token) | **Discharged when the owner runs `snyk auth`** and a session re-scans `builder/analysis/2026-09-07-lbd-inputs/`. **His hands, not a decision** — it opens a browser. Reviewed by hand meanwhile and reported honestly rather than as clean: read-only analysis scripts, no runtime network calls, no `eval`, `subprocess.run` with a fixed argument list and no shell, and the only externally-sourced values (the pinned MBID list) go in through `executemany` parameters rather than string interpolation. That is a hand review, **not** a substitute for the scan |

## Closeout record

Maintenance tier plus the code checks that applied. **Evidence, not assertions:**

| check | outcome |
|---|---|
| `scripts/docs-lint.sh` | **1 hard failure, fixed, then `hard checks passed`.** The failure was this session's own: the new handoff had no row in `docs/README.md`. 150 restated-figure *candidates* remain, all pre-existing in older pre-registrations and none from this diff |
| `doc-auditor`, scoped to the diff | **One LOW finding, fixed.** The `LUX-4` handoff's role line claimed "the CURRENT handoff" unqualified while a second track had opened. Its §10 amendment-register check came back clean on all ten claimed amendments, and the figures-ownership check clean |
| builder suite | **286 passed.** `testpaths = ["tests"]`, so `builder/analysis/` is not collected and these scripts cannot affect it |
| api suite | **275 passed** (one pre-existing Starlette deprecation warning) |
| frontend suite | **not run — nothing under `frontend/` changed**, and design §10 puts it out of scope |
| reachability | the three scripts are standalone frozen harnesses run directly, the `builder/analysis/` precedent; nothing in `builder/src`, `api/src` or `frontend/src` imports them, and each is named in the inputs README |
| prose-versus-code | the minimum-listener constant computes to 4 as its comment claims, and the checksum guard does raise before `GraphStore.load`. One docstring was **wrong and was corrected**: it described `artist` as 17 columns |
| `.claude/` sweep | says nothing about this track; no description went stale |
| **D6 unconditional layer** | **51,694 characters — delta ZERO.** `CLAUDE.md`, `~/.claude/CLAUDE.md`, `MEMORY.md` and every skill/agent `description:` are untouched by this branch |
| **D6 conditional layer** | **2,551 lines — delta ZERO.** No skill body, agent body or memory file changed |
| ports 8000 / 5173 | **no listener on either.** Nothing was started, nothing left running, and nothing queued needs one |

**Inapplicable, stated rather than skipped silently:** no config knob was added, so there is
no default to flip; no test was added, so there is no vacuous-test check — the scripts'
positive control is that the added set reproduces `CXR-P2`'s split exactly, and the inputs
README says a failure to reproduce means a broken environment rather than a finding. No
artifact changed, so the committed fixtures are unaffected. Provenance for what cannot be
committed is in the inputs README: every produced parquet and pinned MBID list carries a
sha256, and both graph artifacts were verified against their manifest sidecars before reading.

**Nothing was queued in `TEST-QUEUE.md`, deliberately.** This session changed nothing the owner
can press. Its one live entry is unchanged and still waits on a deploy.

**One pre-existing map defect found and NOT fixed, reported instead.** Four August handoff rows
in `docs/README.md` still read "ACTIVE — the CURRENT handoff": `2026-08-05-HANDOFF-ulf-filter-fix`,
`2026-08-06-HANDOFF-clip-cover-art`, `2026-08-06-HANDOFF-cocredit-investigation` and
`2026-08-05-HANDOFF-cau-scoring`. **Want of evidence, not of authority** — none of those files
carries a successor pointer in its own role line, so correcting each needs a chain trace across
a month of handoffs, which is outside this diff's scope and is a judgement call per row.

## Nothing is in flight

No background jobs left running, no dispatched subagents, no half-written directories. Ports
8000 and 5173 were not used. The worktree is clean and everything is pushed. The worktree
itself is left in place at `C:\Users\charl\worktrees\music-app-lbd` for the next session;
remove it with `git worktree remove` when the track is done.
