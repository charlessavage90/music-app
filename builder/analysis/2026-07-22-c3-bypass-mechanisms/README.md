# C3 bypass mechanisms — the scripts behind §3 of the Phase 1 log

These produced every figure in **§3.2, §3.6, §3.8, §3.9 and §3.10** of
`docs/superpowers/2026-07-22-phase1-execution-log-and-graph-defect.md` — the Stage 0
binding gate, the two redesigned `known` mechanisms, the rejected route-aware waypoint,
and the blind listening test.

Committed because prose plus a checksum is not enough to re-run an experiment, and these
were about to be lost with a scratchpad directory. **Cite figures from the log, not from
here** — the document owns them. The run parameters are recorded in **§3.10**, not in this
README, for the same reason.

> ⛔ **Read the log's §2 first.** Phase 1 is paused on a graph-structure defect, and the
> hub/payload figures these scripts emit are **degree-based and do not mean "famous."**
> Do not resume mechanism work on the strength of these outputs alone.

## What each one does

| Script | Answers |
|---|---|
| `reconstruct.py` | Replays the owner's real bypass trace (URLs on stdin) against the full graph — the motivating evidence in §3.2. Also answers the Smiths/Shins adjacency question. |
| `stage0.py` | **The binding gate.** Is the proposed multiplicative `known` discount inert? Mirrors production `find_path`, self-checks that the mirror reproduces it exactly with the mechanism off, then layers only the discount. Also measures interior-below-floor for the factor-table confound. |
| `stage0b.py` | Both **redesigned** shapes — additive node reward (cap allowing edge cost → 0) and hard waypoint — with the coherence read via the shipped `path_metrics` (AA, overlap coefficient, `mean_common_neighbours`). |
| `stage0c.py` | The **rejected** route-aware waypoint selection. Kept as the record of a negative result: minimising detour cost selects hub-adjacent cousins, because the free ceiling hops are the cheapest routes. |
| `listen_gen.py` | Generates the blind listen set: walks the hub-targeted all-`known` policy per arm, emits a **public** file (tokens + names only) and a **secret** file (token→arm mapping + hidden metrics). |
| `listen.html` | The blind listening page. Served from a directory containing only itself and the public file, so the secret file 404s. |
| `unblind.py` | Un-blinds the recorded verdicts and computes which hidden metric tracked the owner's ear. |

`listen_public.json` and `listen_secret.json` are the exact set the owner judged — the
36 paths, the sealed mapping, and the hidden per-path metrics. The blind test is over and
un-blinded, so the secret file is no longer sensitive.

## The method worth reusing

`stage0.py`'s structure is the point, not its result: **mirror `find_path`, assert the
mirror reproduces production exactly with the mechanism disabled, only then layer the
mechanism.** That is what makes "the mechanism is inert" a trustworthy claim rather than a
possible reimplementation artifact. Its known limitation — the self-check exercises the
mechanism-*off* path only — is recorded in §3.10.

## Before you re-run them

- **Paths are hardcoded** and several scripts read trace URLs on **stdin**. That is
  deliberate: these are a record of what was executed, not a maintained tool. Adjust the
  constants at the top.
- `stage0.py` and `listen_gen.py` **assert the artifact sha256 before doing anything.**
  Keep that. Several graphs exist in `builder/scratch/` and they are not interchangeable;
  a conclusion drawn from the wrong one looks exactly like a correct one.
- Artifacts are gitignored. These need `graph-t15-capfix.bin` (and `compare_graphs.py` in
  the sibling `2026-07-22-graph-defect-discovery/` needs the control and original too).
- `listen.html` fetches clips from a running API on `:8000`. Serve the page from its own
  directory and widen `ARTISTPATH_CORS_ORIGINS` by **environment variable** — no shipped
  code needs to change.
- Use `python -u`; a buffered job writes a 0-byte log and looks hung.

## Note for a reachability sweep

Nothing imports these, and that is correct. They are **research tooling invoked manually**,
the same category as `nulls.py`, `stats.py` and the sibling `cap-ranking-replay/` scripts —
see Phase 2 execution log §18's B2 check. They produced findings that are in the record,
which is the test that matters.
