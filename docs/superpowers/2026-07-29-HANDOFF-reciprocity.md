# Handoff — reciprocity sampling measured, 2026-07-29

**Role: ⚠ SUPERSEDED 2026-07-29 (latest) on next actions** by
[`2026-07-29-HANDOFF-graph-rebuild-track-a.md`](2026-07-29-HANDOFF-graph-rebuild-track-a.md)
— the plan this handoff asked for was written **and executed to its last task**, so **its
named next action is spent**. One claim below is now **corrected, not merely superseded**:
it states that `RC-P2` predicts an `ALG-B` artifact would be refused by the build. A real
trial build shows **no refusal** — the degree collapse is confirmed and larger than
sampled, but the guard cannot see it (`GRT-P2`). Everything else here remains accurate.

*(Original role: ACTIVE, the CURRENT handoff.)* Supersedes
[`2026-07-29-HANDOFF-algorithm-selection.md`](2026-07-29-HANDOFF-algorithm-selection.md) on
next actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a seam handoff, not mid-flight.** The measurement ran to completion and was read
against a pre-registration committed before it. Nothing is in flight, no subagent is running,
no server is up on any of the four ports, the tree is clean.

## What the next session does

**Write the graph rebuild plan, cold, from the committed record** — the same task the
previous handoff named, now with the number it was waiting for. Everything needed is in
[`2026-07-29-reciprocity-execution-log.md`](2026-07-29-reciprocity-execution-log.md) and its
pre-registration.

**The four strands and their order are unchanged.** Algorithm selection (done) → `AS-H2`'s
stranding question (**now answered — see below**) → cap selection under `MKS-5b` → the
nameless-artist drop rule. Do not restore the pre-2026-07-29 order.

**Two things the plan must now schedule that it would not have before:**

1. **The nameless-artist drop rule is the plan's first build blocker, not a late item.**
   `check_acceptance`'s blank-name check refuses **any** rebuild by design until it lands —
   trial builds included. `NEXT.md` lists it as due inside the plan; it gates the plan's own
   first build.
2. **The cap-selection simulation and any algorithm change interact** and cannot be designed
   independently. `RC-A2`'s rank finding is the evidence. This is not a licence to touch the
   cap: `MKS-5b` stands.

## What changed about the instrument, and why it matters to a reader of the old plan

**The `--target`-capped trial crawl is retired for this question.** It was the agreed next
experiment in `NEXT.md` and in the previous handoff. It cannot answer `AS-H2`: a capped
crawl's readable core is structurally famous, because BFS closes the famous core first and
obscure artists are permanently on the frontier. Measured before any pre-registration existed
— `builder/analysis/2026-07-29-trial-crawl-calibration/`.

**Retired as an instrument for `AS-H2`, not for all questions.** A capped crawl remains the
only way to see component membership, which is exactly what the replacement cannot reach
(`RC-H1`).

## Overturned or corrected claims a well-meaning editor must not revert

- **`ALG-B` strands obscure artists, and this is now measured rather than suspected.**
  `AS-H2`'s 58% candidate-supply drop **does** translate into lost connections. Do not
  restore any wording that treats stranding as an open question on the connection-count axis.
- **But `ALG-B` must not be summarised as "worse" either.** It does what `AS-C1` said it
  does, and `RC-C3` — the median famous-artist degree against the build's own floor — passes.
  Both halves, or neither.
- **The cause is candidate supply, not reciprocation.** For obscure artists the count halves
  while the share pointing back *rises*. Any summary attributing the loss to edges failing to
  reciprocate is backwards.
- **`RC-P3`: the mechanism this session proposed is not supported by its own data.**
  Candidate obscurity does not predict reciprocation (the two sides are indistinguishable).
  Do not re-label this toward the tidier story; it was proposed before it was tested. Same
  shape as `AS-H1` and `TB-P5H-7`.
- **`RC-P1`: the pre-registered scorer had a denominator defect that biased toward the null**,
  and the corrected figure roughly doubles the effect. **Both readings are reported together
  and neither replaces the other** — the pre-registered read is what the committed design
  produced, and `rc_scores.json` is deliberately left unedited to show that.
- **`RC-P2`: an `ALG-B` artifact is predicted to fail `check_acceptance`** on two clauses the
  pre-registration never named — the top-25 minimum degree floor, and the canonical-names
  requirement, since **R.E.M.** reciprocates nothing. Predicted from sampling, not observed
  from a build; a build is what would confirm it, and a build needs item 1 above.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (three new rows), `TEST-QUEUE.md`
(N/A entry), the previous handoff's role line, the pre-registration's §8 (`RC-A1` pre-run and
`RC-A2` post-run, both appended, nothing above them edited). PR #49 body carries the summary.

## What this session knows that is not otherwise in the durable record

- **Nothing was written to any archive, deliberately**, and a real re-crawl still cannot
  select an algorithm: `BuilderConfig` is a frozen dataclass, `_config()` in `cli.py` threads
  only `--target`, and there is no env override. Changing the default *is* the re-crawl
  decision per `NEXT.md`, so a trial build needs either a flag or that decision. The archive
  key does not encode the algorithm either (`RC-H3`), so the two problems compound: a
  re-crawl aimed at the existing archive would silently return production data.
- **The raw records are committed** (`rc_raw_records.json`, 19.0 MB) with full candidate
  lists, not just top-50, so a successor can re-score at a different `k` — which is the
  natural question after `RC-A2`'s rank finding — **without re-hitting the service.** That
  was the reason for storing full lists.
- **`rc_posthoc.py` re-derives degree independently of `rc_score.py`.** If they ever
  disagree, the pre-registered one is the record of what the design produced and the post-hoc
  one is the corrected estimate; neither is a bug in the other.
- **The four collapsed famous artists were diagnosed by hand** (seed rank inside its own
  candidates' lists: 50–97, or absent). That diagnosis is in `RC-A2` but the per-candidate
  rank listing was printed, not saved — it is re-derivable from `rc_raw_records.json` in a
  few lines.
- **An earlier reading of `crawl.py`'s stopping rule was wrong** and was corrected against
  the production checkpoint: `done == discovered == target`, not `done ≈ target/50`. Anyone
  re-deriving trial-crawl cost from the source alone can make the same mistake.
- **Nothing the owner said in conversation is missing from a file.** His agreement to the
  approach, and to switching instruments after being shown the calibration, is reflected in
  the pre-registration and this log; no figure or instruction of his is uncaptured.
