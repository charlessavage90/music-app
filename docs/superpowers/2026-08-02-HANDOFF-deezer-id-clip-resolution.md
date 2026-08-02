# Handoff — per-archive drop lists, identity-based clip resolution, and a cleanup pass, 2026-08-02

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-02-HANDOFF-tail-drop-and-candidate-census.md`](2026-08-02-HANDOFF-tail-drop-and-candidate-census.md)
on next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md),
which owns it.

**This is a SEAM handoff, not mid-flight.** Everything is committed and pushed, nothing is in
flight, no subagent is running, no background job survives, no port is listening, the tree is
clean. **One thing is deliberately unfinished and it is the owner's: PR #65 is open and
unmerged** — see below.

Reasoning: [`2026-08-02-deezer-id-clip-resolution-execution-log.md`](2026-08-02-deezer-id-clip-resolution-execution-log.md).

## The state in one paragraph

PR #64 merged (per-archive drop lists). **PR #65 is open with 5 commits and is complete work,
not a work-in-progress** — it carries identity-based clip resolution end to end plus this
session's documentation. It was left unmerged deliberately because it changes the
builder/api APG1 contract and the owner should see it before it lands. The owner also ran the
test queue and the iPhone script, which discharged both and falsified a Gate 3 blocker.

## The six claims that must not be reverted

1. **`FORMAT_VERSION` stays at 1, and `serialise` omits `deezer_ids` when empty.** Both
   parsers check the version for strict equality — bumping stops every existing artifact
   loading, including the one the app serves. Omission also keeps frozen-mirror artifacts
   byte-identical, whose shas Track B's identity gate pins. A successor "tidying" this into an
   unconditional write breaks the gate silently.
2. **`build_graph`'s `deezer_ids` parameter stays KEYWORD-optional**, and `ALG-B` stays at
   `PERMITTED_ALGORITHMS[1]`. `cb_build_variants.py:479` and `measure_headroom.py:151` are
   frozen and call positionally / index by position.
3. **"Strictly better by construction" is withdrawn and must not reappear.** The id path
   inherits MusicBrainz's link accuracy; duplicates exist. Net clearly positive, individual
   direction not guaranteed. `id_quality.json`.
4. **The `w_degree_hub` correction stands.** The term is dormant by *weight* (`0.0`), not by
   the graph's top-degree set, so it **cannot** self-activate in a rebuild's winning arms. Do
   not restore the confound framing; it would cause a pre-registration to build a control
   against something that cannot happen.
5. **`REQ-38` is a deferral with a condition, not a debt.** Read from source it governs *how*
   a judgment is made, not that every graph change owes one. Owner's decision 2026-08-02.
6. **One map for any archive is correct for Deezer ids** and is *not* the drop-list mistake
   repeated — a drop list is a decision about a population, an id is a property of an artist,
   and a missing id fails safe where a wrong drop list fails silent.

## Already updated — do not re-edit

`NEXT.md` (deferral rows struck and added, `BYP-13` status, Gate 3 row, owner-owed list,
`w_degree_hub` correction, `REQ-38`, `--prune` and Snyk rows), `TEST-QUEUE.md` (both QUEUED
entries marked DONE, newest N/A entry's stale "still live to run" corrected), the previous
handoff's role line, and the execution log. **PR #65's body carries the full context** and is
current as of the last commit.

## What I know that is not otherwise in the durable record

- **The `--prune` flag's help text does not warn that `--skip-build` publishes `dist/` as it
  stands.** Getting that wrong deletes the assets the live page names. The pre-flight is now
  in `NEXT.md`'s struck row and the execution log §9, but *the script itself still does not
  say it*. A successor reading only `--help` would not know.
- **`id_quality.py`'s result is transcribed into `id_quality.json` rather than written by the
  script**, and the script needs a post-drop verification build that is gitignored and was
  deleted. Re-running costs ~7 min of rebuild plus 120 live Deezer calls. The sample seed is
  fixed, so a rerun draws the same 60 artists.
- **The 433 s build time is not a regression** — earlier logs record ~30 s and ~78 s, and
  those predate the drop step. Nobody should chase it without checking what changed.
- **Deezer's `nb_fan` does not separate "duplicate page" from "genuinely obscure artist" on
  its own.** It needs reading against independently-known fame. That is why the proposed
  mitigation is scoped to the top popularity decile, where the expected count is high.

## The open decision, and what I would do

**Only one, and it is genuinely the owner's: merge PR #65.** It is complete and verified; I
left it unmerged because it changes a contract between two packages that share no code and
are kept in lockstep by hand. If I were continuing I would merge it — the window for the
format change closes when the cap re-evaluation pre-registration is committed, and landing it
after that turns it into a mid-flight amendment forcing every built cell to be rebuilt.

**The next substantial work is unchanged: the cap re-evaluation pre-registration**, written
cold. It still needs the owner's half — how much better a connection rule must be to justify
a rebuild, and whether the data-set switch is inside its scope. Both are "what counts as
better", which is his.

Two things a successor writing that pre-registration should read first: execution log §4 (the
`w_degree_hub` correction — it changes what controls are needed) and `NEXT.md`'s `REL-3` row
(a bar expressed as a multiple of a null was degenerate; do not reuse that form).
