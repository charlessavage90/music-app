# Execution log — the degree-1 / degree-2 census, 2026-07-26

**Role: ACTIVE — the audit trail for this work.** Decisions and reasoning, defects found in
the *approach* rather than in code, gate outcomes including failures, corrections to the
prior record, and operational measurements with no other home.

**Owns no figures.** Interpretation:
[`findings/2026-07-26-low-degree-census.md`](findings/2026-07-26-low-degree-census.md).
Every quantity: [`../../builder/analysis/2026-07-26-low-degree-census/`](../../builder/analysis/2026-07-26-low-degree-census/).

Branch `low-degree-census`, PR #25. Identifiers `CNS-` (see the findings document on why one
series, and on per-item attribution).

---

## 1. Scope, and what it did not touch

Read-only measurement of the adopted 75k artifact (`graph-t15-tiebreakfix.bin`, sha256
asserted before any read, per `findings/2026-07-23-tiebreak-fix-adoption.md`). **No rebuild,
no routing, no arm, no config change, no adoption, no proposal, no threshold touched.**
Path-quality work remains paused by owner decision; this census does not resume it.

## 2. Decisions, with reasoning

**D1 — the fame proxy is imported, never reimplemented.** A11's canonical resolver and A15's
recall fallback are called unchanged from the Track 2 modules. A15 matters more here than
anywhere it has been used: the deliverable is a fame-*ranked* list, so a household name
wrongly floored would **vanish** from it rather than be misplaced.

**D2 — in-graph popularity screens, and ranks nothing.** Owner's methodology call. Polling
all 12,041 names is ~120,000 requests against a service asking ~1 req/s on one or two
connections. Popularity is accumulated *before* `mutual_knn_cap`, so the reciprocity rule
destroys a stranded artist's degree and leaves its popularity untouched — the screen rides
on the build stage the defect never reaches. §2.11 forbids using it to *rank*, and it is not.

**D3 — the cut was deliberately not deepened.** Owner's call. The ranked list is
instrumental: its question was *are recognisable artists stranded?*, answered emphatically
by the known cases landing at the very top. A better ordering *below* the reliable zone buys
a marginally better eyeball sample and nothing else.

**D4 — the bulk-SPARQL shortcut was abandoned, not patched.** It failed its recall gate.
Two of three miss-causes were plainly fixable; the third was never explained, and the deeper
reason not to persist is that the canonical resolver's **precision comes largely from
opensearch's ranking**. Any bulk replacement must invent a disambiguation rule, at which
point A11's §5 validation stops describing the instrument producing the figures. Retained in
the tree as the record of a rejected approach, imported by nothing.

**D5 — two readings were withdrawn rather than caveated.** The screen-leak estimates and the
crawl-coverage-gap reading built on them. Under `CNS-2` leak and misidentification are
inseparable with this instrument, so a warning label would have left an uninterpretable
number in the record looking like evidence.

**D6 — Track 2's exposure was bounded, not re-scored.** Measured with this census's own
classifier over Track 2's *already-committed* fame tables. The one residual is named and
explicitly unchecked: whether a misidentified interior is pivotal to a specific cell, which
could only be settled by re-reading per-cell paths — that is re-scoring.

## 3. Defects found in the approach, not in code

Three mechanisms, each of which makes an artist look **maximally obscure** and disappear
from a ranked list without trace. None was found by careful reading; each was found by a
check that compared two things.

**A1 — throttling becomes obscurity.** `fame._wikidata_search` and `_entity_with_sitelinks`
end in `except Exception: return []`, so a 429 is indistinguishable from "no such entity",
and A11 floors an unresolvable artist. Caught **live** by `verify_pool_equivalence.py`.
Fixed by `transport.py`: retries transient failures and **raises** rather than returning
empty; 404 re-raised immediately, since `pageviews_sum` relies on it meaning "no data". No
accept criterion touched.

**A2 — the bulk filter lost real matches.** `verify_sparql_recall.py` failed it on
canonically-matched names. Causes: punctuation folding A11's `normalise` does and SPARQL
does not; cross-language aliases missed by the `@en` tag; and a third, unexplained.

**A3 — the same query reached an album while missing the band.** See D4.

**A4 — avoided by design:** a name left unresolved by network failure is neither cached nor
floored. Passes repeat until one resolves nothing new; survivors are reported as
**unresolved**, which is a different thing from having no English article. The final run
left **none**.

**A5 — `CNS-2`, the proxy's scope limit.** Found while *reading results*, which is the one
place in this list a check did not catch it — the tell was a supposedly-obscure stranded
artist with implausibly high fame. Recorded in the findings document with its bound.

## 4. Corrections to this session's own claims

Three, all made after checking rather than left standing. Recorded because a session's
self-corrections are the part a successor cannot reconstruct.

1. **The leak test was wrong as first written.** It compared the control's best against the
   screened set's *weakest*. The screened set is full of low-fame artists by construction, so
   its minimum is near zero and almost any control artist would clear it — the test would
   have fired on noise. Corrected to: would a control artist have made the *delivered list*.
2. **"Transient failure" was an assumption, not a diagnosis.** The retry wrapper caught and
   retried without ever logging the HTTP status, and the failures were reported as transient
   for roughly an hour on that basis. `transport.py` now names the real cause.
3. **The parenthetical identity class is not reliably benign.** A first draft said it was.
   Most are right, but *Friends* → *Friends (Swedish band)* where the graph says *Brooklyn
   based group*, and *Proof* → *Proof (rapper)* where the graph says *UK grime MC*, are
   wrong. A parenthetical means Wikipedia had to separate same-named topics, which is exactly
   when the wrong one can be picked.

**And one correction to a proposed fix:** giving the resolver the graph's disambiguation
reaches under half the matched rows, and **both worst errors have an empty disambiguation**,
so it would pass them straight through. It is named as a cheapest *first check*, not a fix.

## 5. Gate outcomes, including failures

| gate | outcome |
|---|---|
| Artifact identity (sha256 asserted before reading) | **PASS** — and re-checked from both JSON intermediates by `report.py` |
| `verify_pool_equivalence.py` — thread pool is neutral | **FAILED, then PASS after `transport.py`.** The failure is the finding (A1) |
| `verify_sparql_recall.py` — bulk filter loses no canonical match | **FAILED. Approach abandoned** (D4), not patched |
| `verify_screen.py` `S1` — known stranded artists inside the cut | **PASS**, with wide margin |
| `verify_screen.py` `S2` — no `pop_raw` saturation at the cut | **PASS** — clean cut, not tie-decided |
| `verify_screen.py` `S3` — non-artist entities excluded | **PASS** — no surviving placeholders; the nameless nodes are the one contaminant |
| Post-largest-component-prune confirmation | **PASS** — confirmed observationally from the artifact, not argued from code |
| Fame poll completeness | **PASS** — 4 passes, zero names left unresolved |
| Screen-leak test | **UNRESOLVED, and withdrawn** — the instrument cannot separate leak from misidentification (D5) |

## 6. Corrections to the prior record

**`DRV-4`'s open denominator question is closed.** The two candidate populations are
**nested, not alternatives**: `build_from_archive` sets `known = set(payloads)`
(`builder/src/artistpath_builder/pipeline.py:131`) and keeps a neighbour edge only
`if n.mbid in known` (line 184), so **every artifact node is a crawled artist**. `DRV-4`
asked which population `MKS-3`'s share was against; the answer is that the choice is
immaterial. **`DRV-4`'s structural claim is upheld and now measured.**

**A11 gains a scope note, and nothing else.** Three placements in
`specs/2026-07-23-track2-preregistration.md` — beside "What A11 does NOT change", in the §5
inline blockquote, and in the amendment-index row. **Not an amendment**: the A-series still
runs A1–A19 and no identifier was renamed or renumbered.

## 7. Operational measurements with no other home

Recorded here because nothing else will hold them, and the next session's cost estimate
depends on them.

- **Fame poll wall time: 76.5 minutes** for 1,171 names at 2 workers, 4 passes.
- **Per-name serial cost**, measured on a 12-name sample before committing to the approach:
  a matched name is fast; a floored name is roughly seven times slower, because it pays A15's
  multi-language Wikidata fan-out and then the A11 guard.
- **Attrition ~15–23 % per pass at 2 workers**, rising within a long pass and recovering
  between them — consistent with cumulative rather than per-request throttling. At 4 workers
  it degrades badly. A burst of 4 concurrent requests succeeds; sustained load does not.
- **`Wikipedia:Database_download`** asks for "at least a second delay between requests" and
  "no more than one or two simultaneous HTTP connections". Any future poll should budget from
  that, not from observed burst speed.
- **Re-resolving does not require re-running the poll.** The cache is keyed by name and
  persists, so correctly-matched pageviews are already paid for; only rejected rows need
  re-walking.

## 8. Closeout outcomes, 2026-07-26

Completion closeout at a clean seam — not the mid-flight scaling. Full ritual, because the
work introduced a **new identifier series**, which is the case that caught collisions in each
of the last two closeouts.

| item | outcome |
|---|---|
| **A1** distil execution log | This document. |
| **A2** handoff note | [`2026-07-26-HANDOFF-low-degree-census.md`](2026-07-26-HANDOFF-low-degree-census.md). "What I know that is not in the durable record" came back **non-empty with three items**, all folded in rather than left in the note. |
| **A3** deferrals have success conditions | **PASS** — three open items, each with one: the Track 2 per-cell exposure residual; the open question in findings §4 (terminal state named); `CNS-1`'s alias check. |
| **A4** default-flip | **INAPPLICABLE, stated rather than skipped** — this work added no config knob and changed no default. It is read-only by construction. |
| **B1** doc-auditor | **Dispatched and CLEAN** — zero HIGH, zero MEDIUM. Confirmed `CNS-` collision-free against all sixteen named series; the three A11 SCOPE NOTE placements mutually consistent and non-contradictory; the owns-no-figures claim verified; `docs/README.md` entry complete. Check **J inapplicable** (no pre-registered experiment ran) and said so rather than forced. It left one prior finding **UNVERIFIED** — whether the roadmap still called F1 deferred — **now closed: it correctly says BUILT and NOT discharged.** |
| **B2** reachability | **PASS** — the only modules nothing imports are the four CLI entry points and the **deliberately abandoned** SPARQL pair, documented as such in three places so a successor cannot mistake abandoned for unfinished. |
| **B3** vacuous-test spot check | **Found a real defect in this session's own work.** `verify_screen.py` printed `FAILS` and **exited 0** — a broken screen would have been a line of output inside a passing run, which is exactly the shape B3 exists to catch. Now gates, and was verified to *both* pass on the real data and raise when the condition is violated. Separately, the artifact checksum gate was tested against the wrong artifact and correctly **exits 1**, and 0 on the adopted one — the `DRV-1` defect class, confirmed caught rather than assumed. The other two verifiers are proven non-vacuous **by observation**: each actually failed during this session. |
| **B4** prose-versus-code | **PASS** — with one correction already recorded at §4 item 3 (the parenthetical class was described as benign and is not). |
| **B5** stale-description sweep, incl. `.claude/` | **PASS on figures** — no census figure is restated anywhere outside the analysis directory, verified in both directions. **One observation actioned:** `.claude/agents/ml-graph-analyst.md` carries the same four-field APG1 blob description as `CLAUDE.md`, so `CNS-1`'s alias check has a **two-file** blast radius, both wrong **by omission** if aliases exist. Folded into `CNS-1`. |
| **C1** use the application | **QUEUED** — `TEST-QUEUE.md`, written for someone holding a mouse: no identifiers in the steps, and it says which of the two lists to prefer and why rather than leaving the reader a choice they cannot make. |
| **D1** clean tree | **PASS.** Ignored deliberately: `__pycache__/`, and `resolve.log` (a transcript, not a result). **`fame_cache.json` is committed on purpose** — it is what makes any future re-resolution cheap. |
| **D2** regenerate fixtures | **INAPPLICABLE** — no artifact changed; this work only ever read one. |
| **D3** provenance | **PASS** — the adopted sha256 is asserted in the scripts and cited to `findings/2026-07-23-tiebreak-fix-adoption.md`. No artifact was created or adopted, so there is no new checksum to record. |
| **D4** suites | **PASS, run not remembered** — builder 115 passed, api 153 passed (1 warning), frontend 64 passed across 12 files. |
| **D5** PR | #25, updated at closeout. |
| **D6** standing context layer | §9 below. |

## 9. Standing context layer (closeout D6)

`git diff --stat` over `CLAUDE.md`, `.claude/skills/`, `.claude/agents/`: **no change** —
this session added nothing to the standing layer inside the repo.

`memory/` **grew by one file** (`stop-refining-instrumental-artifacts.md`) plus one index
line, taking the directory to **469 lines total** — the figure the next closeout compares
against, and the reason it is recorded here rather than only in a commit message: this log is
the only place the two halves of the layer can be added together. It was **not** bought by
compressing anything. It records two owner corrections that generalise past this task — stop
refining a measurement past the decision it changes, and ask what a screen's leak is evidence
*of* — and **the addition is the owner's to keep or drop**, per `CLAUDE.md`'s budget rule; it
is flagged rather than presented as settled.
