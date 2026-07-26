# Execution log — why the low-degree artists are low-degree, 2026-07-26

**Role: COMPLETE.** The retained record for the stranding-causes work (PR #25,
commit `59c0ba3`, branch `low-degree-census`). Identifiers namespaced **`STC-`**;
the findings document
[`findings/2026-07-26-stranding-causes.md`](findings/2026-07-26-stranding-causes.md)
owns the interpretation and
`builder/analysis/2026-07-26-stranding-causes/REPORT.md` owns every figure.
**This log restates no figure it does not own.**

Touches no shipped code, no graph, no weight, no config default. Read-only
throughout. The path-quality pause is intact.

---

## 1. What was asked, and the defect in the ask

The task named two causes to separate: **cap-stranded** (a full candidate list,
almost none reciprocating) and **crawl-frontier** (at the edge of the snowball,
so few candidates are in the graph at all).

**`STC-1` is a defect in the task's own framing, not a result within it.** The
second category, measured, is a small fraction of the set. What actually fills
that space is a third cause the ask did not contemplate: the similarity source
named almost no similar artists for those artists **in the first place**. The
two-way split was delivered as specified, in full and with its sensitivity, and
the three-way refinement sits beside it — the ask was answered rather than
replaced.

This is worth recording because the framing was reasonable and the naming still
misleads: "crawl-frontier" invites a remedy (crawl further) that reaches almost
none of the population it appears to name.

## 2. Decisions, with reasoning

**D-1. Reuse the 2026-07-25 candidate model by import, not by copy.** The task
said to reuse `reciprocity.py` and keep its validation gate. Importing it — via
`importlib` with `builder/` as the working directory, because its archive path is
relative and its `KNOWN` set is computed at import time — keeps exactly one
implementation of the builder's cap in the repo and keeps the six-artist gate
guarding it.

**D-2. Correct that model's candidate population, and gate both versions.**
Discovered mid-work: `build_from_archive` computes `known = set(payloads)` and
then `known -= excluded`, dropping MusicBrainz special-purpose placeholders
before any ranking (`pipeline.py:131`–`152`). `reciprocity.py` does not model
that. This mattered here rather than being tidiness — a placeholder can occupy a
top-k slot and displace a real candidate, and it inflates the candidate count,
**which is the quantity the split keys on.** The builder's own
`is_special_purpose` is imported rather than reimplemented, and the six-artist
gate runs **before and after** the correction so neither version is taken on
trust. Recorded as `STC-5`.

**D-3. Add a quantity the ask did not request: how many artists list each one,
regardless of whether it lists them back.** The ask was "how many of its
candidates are in the graph, and how many of those rank it back". Both are
reported. But the stated purpose — *would its low degree persist under any cap
rule* — cannot be answered from those two alone, because a one-directional rule
would keep in-edges the artist itself never named. That column is what produced
`STC-4`, the strongest evidence **against** a cap-rule change, and without it the
report would have implied a larger remedy than exists.

**D-4. Add the source-offered denominator, after the first report was already
written.** The first pass measured only candidates *in the builder's population*.
Reading the generated report surfaced artists with one candidate who were listed
by dozens of others — which "the crawl never reached these" does not describe. The
missing quantity was how many candidates the **source** named at all, before any
in-graph filter. Adding it is what produced `STC-1`. **The first version of the
report was fluent, internally consistent, and wrong in its headline**; what caught
it was reading the output rather than the code.

**D-5. Run the falsifier rather than shipping it as an open question.** The draft
findings document named a check it had not run — whether short candidate lists
are an artifact of fetch-time truncation — and listed it as the cheapest thing
that would strengthen or kill the headline. It was run before commit. It
**half-fired**, and the result is `STC-6`: the length limit provably cannot
produce a short list, so `STC-1` survives it, but the co-occurrence threshold can
and does, and both are parameters **this project chose**
(`BuilderConfig.algorithm`).

**`STC-6` is a correction to a claim this session had already written**: that
nothing in the project's control reaches that population. Wrong — a lower-
threshold re-crawl does. The remedy table in the findings document and the
corresponding passage in the report were both rewritten, and the correction is
recorded rather than quietly applied, because the wrong version is the intuitive
one and will be re-derived.

**D-6. Stop chasing the residual.** Ten artists of 12,088 have a modelled degree
one different from the artifact's. Two candidate causes were investigated and
both are settled by measurement (see §3). The remainder sit at a top-k boundary.
Left alone deliberately, per `memory/stop-refining-instrumental-artifacts.md`:
the split keys on the candidate count, which is verified exactly for every artist
measured, and every degree quoted anywhere is the artifact's own, not the
model's.

## 3. Gate outcomes

Four gates, all printed by `split_causes.py`, all passed or bounded:

1. **Artifact identity** — sha256 asserted before any figure, matching
   `findings/2026-07-23-tiebreak-fix-adoption.md`. Passed.
2. **The 2026-07-25 six-artist gate**, run twice — unmodified, and again after
   `STC-5`'s correction. Passed both times.
3. **Uncapped candidate count consistent with the capped list** — zero
   mismatches across the whole measured population. **This is the gate that
   matters**, because it is the quantity the split keys on. Passed.
4. **Modelled degree equals the artifact's own degree** — passed for all but ten
   artists. Not clean, and not claimed to be; bounded instead, see D-6.

**Two hypotheses about gate 4's residual were eliminated by measurement, not by
argument**, and `verify_residual.py` reproduces both:

- The placeholder exclusion (`STC-5`) accounted for a majority of the original
  discrepancy — reproducible by running the model with and without it.
- A difference in how rows carrying no similarity score are treated **cannot**
  bite, because the archive contains no such row. Counted across every row in
  every archived response.

## 4. Corrections to the prior record

- **`STC-5`** records a limitation in
  `builder/analysis/2026-07-25-mutual-knn-stranding/reciprocity.py`. It does
  **not** invalidate `findings/2026-07-25-mutual-knn-stranding.md`: the
  placeholders are a single-digit count in the whole crawled population, far too
  few to move any distribution that document reports, and none of its six gated
  artists is affected. **Success condition:** any future reuse of that model
  whose result depends on an individual artist's candidate list rather than on a
  distribution must apply the exclusion first. Discharged by that reuse applying
  it, or by the model being retired.
- **`STC-6`** carries the second success condition: **if a re-crawl is ever
  considered for any reason, the co-occurrence threshold is examined at the same
  time**, because the crawl is the only moment it can be changed. Discharged by
  that examination, or by a decision that the current threshold is correct.
- Nothing else in the record is overturned. This work is additive.

## 5. Operational measurements with no other home

- A full archive scan is **several minutes** under OneDrive, and the measurement
  needs two of them plus a per-artist re-read. Budget roughly ten minutes per
  full run of `split_causes.py`, and the same again for `verify_residual.py`.
- `split_causes.py` clears the model's cache every 5,000 artists. Without it the
  parsed top-k for every archived response stays resident and the run is not
  memory-safe.
- `artifact_nodes.json` is **deliberately not committed** — a mechanical re-dump
  of the artifact, regenerated in seconds — via a `.gitignore` **inside** that
  directory. That file is branch-scoped, so a session checking from a branch
  where the directory does not exist cannot see it. This is `CLM-13`'s trap, and
  the directory's `README.md` says so explicitly for that reason.
- Two `builder`/`api` processes are needed because the packages share no code:
  the APG1 reader lives in `api/`, `is_special_purpose` lives in `builder/`, so
  the artifact's node table crosses the gap as data.

## 6. Closeout results

- **A4, default flip:** inapplicable. This work added no config knob and shipped
  no code; unshipped behaviour is not the premise here because there is no
  behaviour.
- **B1, documentation audit:** dispatched, returned **clean — no findings**. Its
  coverage statement notes it did not open the analysis code in full, and its
  `.claude/` half was not evidenced in its coverage list, so that sweep was run
  session-side instead (see B5).
- **B2, reachability:** all four scripts are entry points with documented run
  commands, and the chain resolves — `dump_artifact_nodes.py` produces the node
  table that `split_causes.py` and `verify_residual.py` consume;
  `report_split.py` consumes `causes.json`; `verify_residual.py` imports
  `split_causes`. No orphans. Two throwaway diagnostics written during the work
  were deleted, and the one claim they established that the report cites was
  rebuilt as `verify_residual.py` so it stays checkable.
- **B3, vacuous tests:** inapplicable — this work added no tests. The equivalent
  guard is the four gates in §3, two of which are designed to abort the run.
- **B4, prose versus code:** `pipeline.py:131`–`152` verified to contain both
  `known = set(payloads)` and `known -= excluded` as cited.
- **B5, stale descriptions:** `.claude/agents/ml-graph-analyst.md` re-read
  against this work. It carries **no figures by design** and its
  popularity-versus-degree passage already warns that the two diverge at the top
  of the distribution, which is the direction this work's population sits in. No
  edit needed, and none made.
- **D4, suites:** builder 115 passed; api 153 passed; frontend 64 passed across
  12 files. Run, not recalled.
- **D6, standing context layer: net zero.** `git diff --stat main..HEAD --
  CLAUDE.md .claude/skills/ .claude/agents/` is empty, and `memory/` is
  **469 lines**, unchanged from the figure recorded in the 2026-07-26
  context-layer-maintenance log. `docs/README.md` gained one row, which is a
  routed-around layer rather than a standing one.

## 7. What is NOT established

Recorded here as well as in the findings document, because this is the section a
successor reads:

- **No alternative cap rule was run.** `STC-4` measures the reach of a change
  nobody has proposed. `mutual_knn` won a blind listen and `MKS-5b` binds any
  redesign.
- **The payoff of a lower crawl threshold is unmeasured** (`STC-6`). It is a full
  re-crawl and the new edges rest on weaker evidence by construction.
- **The boundary between the populations is the session's choice**, stated as
  such. Eleven alternatives are printed so it can be overruled by reading a
  different row.
- **Nothing about path quality.** No path was routed, no cost weight read.
