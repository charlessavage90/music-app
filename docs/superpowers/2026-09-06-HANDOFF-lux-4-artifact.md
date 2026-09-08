# Handoff — `LUX-4` through the artifact, 2026-09-06

**⚠ Role: SUPERSEDED ON EVERYTHING by
[`2026-09-08-HANDOFF-lux-4-wire-and-card.md`](2026-09-08-HANDOFF-lux-4-wire-and-card.md),
2026-09-08 — NOT the current handoff.** Its "Start here" is spent: `L4-T8`–`L4-T11` are done
and the plan is finished, so the successor supersedes this on **next actions and status
alike**, not on next actions only. **Everything this note records about `L4-T1`–`L4-T7` still
stands in full**, including its whole must-not-revert list and the artifact's sha — with one
count updated forward: it says the plan was wrong about the repository **four** times, which
was true when written, and a **fifth** was found during `L4-T10`. The successor carries it.

*(Original role:)* **ACTIVE — this is the CURRENT handoff FOR THE `LUX-4` TRACK.** Nothing
supersedes it. Supersedes
[`2026-09-05-HANDOFF-lux-e1-and-lux-4-plan.md`](2026-09-05-HANDOFF-lux-e1-and-lux-4-plan.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

⚠ **A SECOND track went live 2026-09-07 and has its own current handoff** —
[`2026-09-07-HANDOFF-lbd-preregistration.md`](2026-09-07-HANDOFF-lbd-preregistration.md) for
`LBD-`. **Neither supersedes the other** and neither blocks the other. A reader who wants
"the" next action wants [`NEXT.md`](NEXT.md), which sequences both. *(Track qualifier added
2026-09-07: this line read "the CURRENT handoff" unqualified, which was true when written and
became ambiguous the moment a second track opened.)*

**A SEAM handoff, and the seam the plan chose at authoring time** (`L4-T7`, "the artifact
exists, is verified, and its identity is committed"). Everything downstream reads a finished
artifact rather than a live understanding. The degradation tell did not fire — but see
"What I know that is not in the durable record" for an honest note on execution slips.

Branch `lux-4-links-info-card`, **PR #105 (draft)** — both are addresses; `git` and `gh` own
what has landed.

---

## Start here

**`L4-T8`.** The artifact is built and verified; the API does not read its new keys yet.
Continue at [`plans/2026-09-05-lux-4-links-and-info-card.md`](plans/2026-09-05-lux-4-links-and-info-card.md)
task `L4-T8`, then `L4-T9` (the second seam), `L4-T10`, `L4-T11`.

**Nothing is assigned to the owner by this work.** His outstanding items are unchanged and
predate it: deploy `LUX-1..3`, then run the one queued use-the-app test. `NEXT.md` owns that
list.

**⚠ Read the plan's per-task correction blocks before executing any task.** Four of its tasks
were wrong about the repository and each carries a correction block at its head. Assume the
remaining tasks may be too, and grep every function, file and config value before trusting it —
that is what found all four.

## What this session did

`L4-T1`, `L4-T1b` (added), `L4-T2`, `L4-T3`, `L4-T4`, `L4-T5`, `L4-T6`, `L4-T7`. All three
suites green at closeout and Snyk clean, including one new Low fixed rather than accepted —
run them rather than trusting a count written here.

1. **`L4-T1`** — acceptance bounds restored; **the served map's own gate admits it again**, and
   a build through the restored defaults reproduces `43dd82bb` byte-identically.
2. **`L4-T1b`** — the manifest now records **which files** a build applied, logged at build
   start. Discharges a deferral whose condition had already fired once unhonoured.
3. **`L4-T2`–`L4-T4`** — extraction and the three frozen, sha-pinned maps.
4. **`L4-T5`/`L4-T6`** — links and facts carried node-indexed into three additive APG1 keys.
5. **`L4-T7`** — rebuilt, verified two independent ways, `LUX-E5` passed.

**The artifact:** `builder/scratch/graph-lux4.bin`, sha
`fd92a7352afb7321e80f3818262d08169fcfb3af1d6841d7ccfca0f5e5740369`. **Gitignored**, so that
sha and its manifest sidecar are the only identity it has. Counts and sizes:
[`builder/analysis/2026-09-05-lux-4-rebuild/README.md`](../../builder/analysis/2026-09-05-lux-4-rebuild/README.md) §2. ⚠ Take the deploy checksum from the sidecar, never from here
(`DEP-24`).

## Claims an editor must NOT revert

- **The rebuild is the served graph plus exactly three metadata keys.** Proven twice: the
  control arm returns `43dd82bb` byte-identically, and subtracting the three keys from the
  shipping artifact reproduces the served one byte for byte. Do not weaken either to a sha
  comparison — **the sha MUST differ**, keys were added.
- **The plan's `L4-T7` control arm is unusable and was replaced.** `armb_sha.py` calls
  `build_from_archive`, which wires the maps unconditionally since `L4-T5`. Do not restore it
  as the control, and do not add a config knob to make it work — the no-knob decision is
  recorded at the `deezer_ids` call site.
- **`LUX-E5` PASSED**, with headroom. **Nothing is dropped; `area` stays.** Figures: rebuild README §4.
- **`LUX-E3`'s read: Spotify beats Apple in every band**, so the feature is "both services"
  with a search fallback. Figures: lux4-extract README §2.
- **`artist_facts` per-field coverage is NOT a `LUX-E2` read.** `LUX-E2` is stated over
  delivered cards and remains BLOCKED on its damaged `TAS-` sample.
- **The `2026-08-02-dsp-ids/` directory is frozen and was deliberately not touched** — its
  outputs are pinned by `deezer_ids.py`.
- **The dump is the 2026-07-29 export** (its own `TIMESTAMP`), **CC0 1.0** per its own
  `COPYING`. The older "2026-07-28" label was wrong and is corrected forward only.

## Two findings that are work, not notes — both deferred with conditions

- **`ULC-F4`** — the un-listenable keep-check measures the **name** search while the app
  resolves by **identity** first, so both drop lists drop artists the app can play. Figures:
  `builder/analysis/2026-09-05-lux-e1-drift-source/README.md` §6. **Owner's call**; needs a
  re-census, a rebuild and its own pre-registration.
- **The Deezer id gap** — a slice of served artists carry no Deezer id at all, because the
  shipped map was extracted over a population predating the served map. **A session's work, not
  a decision.** Condition: *the first rebuild after `LUX-4` merges.* Counts and the expected
  recovery: `builder/analysis/2026-09-05-lux4-extract/README.md` §4.

## What I know that is not in the durable record

1. **The plan was wrong four times, in four different ways**, and every one was caught by
   checking against the repo rather than by reading carefully: a wrong commit hash for the
   acceptance band (`3aa61f0` is the *retired* map's, rejecting the served one on both
   bounds); a population that does not cover the served map; a wiring location that
   contradicts `build_graph`'s own docstring; and a control arm invalidated by an earlier task
   in the same plan. **Treat the remaining tasks as unverified.**
2. **The `artist_facts` shape is a deliberate trade-off, measured, and it is the thing to
   revisit for `LUX-E6`.** List-of-dicts costs more than parallel arrays would, because it
   repeats key names per artist, and its RSS cost is a large multiple of its JSON size — **that
   multiplier, not the byte count, is what governs `LUX-E6`**, where a genre-tag list per artist
   multiplies the same way against a fixed container ceiling. Measurements: rebuild README §4;
   the shape trade-off is recorded at the contract point in `artifact.py`'s docstring.
3. **Execution slips were more frequent than usual, and all were caught by my own checks**:
   a header-inclusive byte comparison that failed on a correct artifact, a regex that matched
   "i" plus optional "d", a path confined against the wrong root, two wrong working
   directories, and three separate 17 GB re-extractions where one value-distribution survey up
   front would have found all three defects at once. None reached a commit. **The reusable
   lesson is the third one: survey a field's value distribution before writing its first
   consumer.**
4. **Another session was live in a worktree** as of 2026-09-06, writing analysis output on its
   own branch. It has no `builder/scratch/` and no `.venv`; it was told to read artifacts by
   absolute path from the main tree.

## Nothing is in flight

No background jobs, no dispatched subagents, no half-written directories. Ports 8000 and 5173
were not used by this session. The working tree is clean and everything is pushed.
