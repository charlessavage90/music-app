# Documentation audit — full project, 2026-07-27

**Role: COMPLETE.** The record of a one-time full-project documentation audit, run at the
owner's instruction after `doc-auditor` was moved from `haiku` to `sonnet` (`be7db75`,
2026-07-27). Identifiers **`DAF-`**, verified unused across `docs/`, `.claude/`, `api/`,
`builder/`, `frontend/` and `infra/` before allocation, and disjoint from `DEP-`, `TR-`,
`TKA-`, `TKB-`, `TKC-`, `TKD-`, `RMD-`, `FRO-`, `ARC-`, `SEC-`, `QUA-`, `FMS-`, `BYP-`,
`MKS-`, `STC-`, `SYN-`, `CNS-`, `CWD-`, `DRV-`, `BTF-`, `ASC-`, `TF-`, `CLM-`, `DLV-`.

**This document owns no figures.** It records defects, their locations, and what was done
about them. Where it and a document it describes disagree, read the document.

---

## 1. What ran, and why it was split

The corpus is roughly **45,000 lines** across `docs/`, `.claude/`, the four package READMEs
and the `builder/analysis/` directories — about **11× the ~4,000-line budget** at which
`doc-auditor`'s own definition says to stop and ask for a narrower scope. A single broad run
would have skimmed and reported as though it had audited.

It was therefore split into **ten parallel slices**, each within or near budget, each told
that size is the only thing that may narrow scope and that silently dropping a file is
itself a finding:

| Slice | Scope | ~Lines |
|---|---|---|
| A | Entry points and the always-loaded context layer — **owns the cold-start test and existence checklist** | 5,235 |
| B | The handoff chain (18 files) + resume brief — **owns correct-the-corrector** | 2,300 |
| C | Findings, 2026-07-25 → 07-27 | 3,500 |
| D | Findings, 2026-07-19 → 07-24, incl. the scoring adjudication | 3,150 |
| E | All specs and pre-registrations — **owns reads-of-results (check J)** | 4,060 |
| F | Current plans, 2026-07-23 → 07-27 | 7,340 |
| G | Legacy plans, 2026-07-19 → 07-22 — targeted checks only, declared | 10,250 |
| H1 | Phase 1 / Phase 2 era execution logs | 5,380 |
| H2 | Gate 2 era execution logs | 2,900 |
| I | **Cross-cutting**: project-wide identifier census, `builder/analysis/` figure-owner directories, orphan and map-completeness sweep | grep-driven |

Slice I exists because partitioning destroys exactly the two checks that are inherently
global. Every cross-document collision in §3 below was found by a slice that could see
across documents; a purely partitioned audit would have missed most of them.

**Every finding quoted in §2 and §3 was independently re-verified** against the file, the
source, or `git` before being recorded here. Two reported findings did not survive that check
and are recorded as such in §5.

---

## 2. The shape of the result

**`DAF-1` — the content is in good shape; the status layer is not.** Across all ten slices,
almost every HIGH finding is a claim about *what a document is* or *whether it still
applies* — not a substantive error. Measurements reproduce. The one-record rule for figures
holds, with three small exceptions (§4). Code citations mostly resolve, and where they have
drifted it is by a handful of lines from later insertions. What has decayed is documents
saying what they are.

This matters because it is **narrower and more mechanical** than "the documentation has
drifted", and it points at a fix the project already has: `plans/2026-07-26-track-d-frontend.md`
opens with `⚠ EXECUTED 2026-07-26 — do not execute again … where that log and this plan
disagree, the log wins`. That pattern is correct, it works, and as of this audit it had been
applied to **one plan out of twelve**.

**`DAF-2` — the most dangerous instances were plans asserting they had not been run.**
`plans/2026-07-26-track-b-infrastructure.md:7` read `**Role: ACTIVE, not yet executed.**`
while PR #29 was merged and the app was live on CloudFront. It is a thirteen-task plan that
provisions AWS infrastructure and is not idempotent. Four other merged plans read as pending;
four legacy plans carried **no status marker at all** while opening with a live instruction —
`REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development … to implement this plan
task-by-task` — over ~10,000 lines of already-shipped work.

**`DAF-3` — the provenance caveat was attached to the one section it does not cover.**
`DRV-1` records that Phase 1 log **§2.11 and §2.12** were measured on `graph-t15-capfix.bin`,
which the app has not run since 2026-07-23. Inside that 1,230-line log, `DRV-1` appeared
**once**, at line 396 — inside **§2.9**, in a banner whose own text says the caveat does not
cover §2.9's table. §2.11 and §2.12 had nothing. Both `docs/README.md` and `NEXT.md` instruct
readers to *"read §2.12 first"*, so a reader following the project's own instruction landed
precisely where the warning was absent.

**`DAF-4` — a prior `doc-auditor` run certified a claim that was false, and the class is the
one the tool names as its own blind spot.** `2026-07-26-low-degree-census-execution-log.md:167`
records step `B1` as *"Dispatched and CLEAN — zero HIGH, zero MEDIUM … `docs/README.md` entry
complete."* That document is not mentioned anywhere in `docs/README.md`. The run was
2026-07-26, inside the `haiku` window (`e3fbb3e` 2026-07-25 → `be7db75` 2026-07-27). The
auditor definition's own warning reads *"You are weak at **absence**"* — and this is the
absence check failing while reporting clean.

> **Read `DAF-4` at the strength it supports.** One instance is not a controlled comparison,
> and the defect class is genuinely hard rather than obviously careless. What is established:
> a `haiku`-era run returned a false clean bill on a mechanically checkable claim, and the
> `sonnet` run found it. What is **not** established: any general ratio between the two.

**`DAF-5` — the map had drifted from the documents it classifies.** `docs/README.md` states
it classifies *every* document in `docs/`. Three were missing (two reachable only as a mention
inside another row, one absent entirely). It called a handoff "the CURRENT handoff" three
handoffs after it stopped being one, and repeated a stale `F1` status the rest of the record
had already corrected.

---

## 3. Identifier collision register

The project has **eleven collisions already on record** (`A1`–`A7`, `C1`–`C3`, `R1`, per
`CLAUDE.md`'s incident narrative). This audit found **eleven more that were not**. None is
renamed — forward-only, per the standing rule; a frozen document's value is that it is frozen.
They are recorded so the next document that mints identifiers can avoid them.

| # | Token | Meaning A | Meaning B | Found by |
|---|---|---|---|---|
| `DAF-C1` | `C4` | Roadmap's Phase 2 damping criterion (rejected) | Track 2 pre-registration's payload guard | B |
| `DAF-C2` | `P1`–`P4` | Track 2 fame-proxy/harness prerequisites | Track B's owner-run AWS/IAM/billing/secrets prerequisites | B |
| `DAF-C3` | `P1`–`P3` | Track 2 prerequisites | C3 blind-listen's bypass **policies** (all-known / mixed / all-dislike) | E |
| `DAF-C4` | `C5`, `C6` | Track 2's local no-regression guard / withdrawn coverage guard | Phase 1 log §2.13's decision IDs — **cited by the same design document that cites Track 2** | E |
| `DAF-C5` | `D1`–`D7` | `closeout`'s git-finalisation steps | Track 2 protocol review's numbered findings | A |
| `DAF-C6` | `C1` | `closeout`'s "C1. Use the application" step | Gate 1 clip defect **and** Track 2 criterion (three meanings) | A |
| `DAF-C7` | `F1`, `F2` | Shipped minimum-stop feature / a bypass complaint | P8b harness review's local `F1`–`F14` findings | A, I |
| `DAF-C8` | `C1`–`C6` | Phase 1 log §2.13 decision IDs | Phase 1 log §7 clip defects — **same document** | H1 |
| `DAF-C9` | `F6` | Repair-retune log's dogfooding finding ("coherence wobble") | P8b harness finding, same document | H1 |
| `DAF-C10` | `T1` | A Track 1 work item | The expressway-toll arm family — **same document, and that document's own collision self-check at :2095 explicitly declared `T1`/`T1a`/`T1b` clean** | I |
| `DAF-C11` | `A1`–`A5`, `D1`–`D6` | Low-degree census log's own decisions and defects | `closeout`'s standard step letters, in the same log | H2 |

**`DAF-6` — the pattern worth acting on is that three of these are inside a single document,
and two were missed by that document's own collision check.** `DAF-C10` is the sharpest: the
repair-and-retune log ran a dedicated census, listed `T1` among identifiers "checked and not
collisions", and was wrong. `DAF-C8` and `DAF-C9` were missed because the census that ran was
scoped to the *pre-registration*, so it structurally could not see the log's own reuse.
**A collision check scoped to one document cannot clear a second document's tokens**, and
saying it did is worse than not running it.

**`DAF-7` — the namespaced series work.** Every hyphenated series (`DEP-`, `TR-`, `TKA-`,
`TKB-`, `TKD-`, `RMD-`, `MKS-`, `STC-`, `SYN-`, `CNS-`, `CWD-`, `BTF-`, `ASC-`, `TF-`) is
collision-free. Every collision above involves a bare letter-and-digit token. The convention
adopted after the `R1` incident is doing its job; the residue is documents that predate it,
and procedural step letters (`closeout`'s `A`/`B`/`C`/`D` series) that were never treated as
identifiers at all.

---

## 4. Figure duplication (check C)

The one-record rule holds well. Three live exceptions, none currently wrong:

- `plans/2026-07-21-phase2-path-quality.md:379` states a zero-rate of `0.7%`; the adjudication
  §4.3 states `0.73 %`. **This one has already begun to drift** — it is the mechanism the rule
  exists to prevent, caught mid-drift. Two further restatements at `:414` and `:2680`.
- `docs/README.md:161` restates Track 2F's headline figures in the same row that says
  *"a second copy would restate its figures. Cite this directory."*
- `2026-07-27-gate2-track-c-execution-log.md:213` restates the adopted graph's artist and edge
  counts, owned by `findings/2026-07-23-tiebreak-fix-adoption.md`.

Separately, the pre-adoption artifact's node/edge/sha256 triad is stated independently in at
least six documents with no owner designated (H1). They agree today.

**`DAF-8` — a meta-fact about the one-record rule had itself drifted into three copies.**
`CLAUDE.md`, `docs/README.md:31` and `findings/2026-07-21-architecture-review-and-path-baseline.md:9`
all described the adjudication's §6 as tracking **"27 prior claims"**. Direct count: the table
has **45 numbered rows**, having grown by amendment on 2026-07-21 and 2026-07-22. None of the
three copies is the adjudication itself.

---

## 5. Two reported findings that did not survive verification

Recorded because an audit that only lists confirmed hits hides its own error rate.

- **The root `README.md` does not lack a status marker.** An early reading of the chain
  suggested a live never-fixed defect there. It carries `**Status:**` at `:14`, and the
  `Role:` convention is scoped to `docs/`. The real (lesser) defect is that the line
  *duplicates* `NEXT.md`'s gate state — on the same sentence that calls `NEXT.md` the only
  document stating what is done.
- **`docs/README.md`'s role marker was not "there throughout."** Slice C correctly found that
  the 2026-07-26 report's "STILL OPEN" claim is false, but repeated the map's own explanation
  for why. `git` shows the marker was added 2026-07-25 in `8a4450e`, as the fix for the
  2026-07-25 audit's finding. So the 2026-07-26 defect is **carrying a fixed finding forward
  without re-checking it** — a different and more instructive failure than a never-true claim.
  `docs/README.md`'s correction has been corrected in place.

---

## 6. What was changed, and what was left alone

**Changed** (all on branch `doc-audit-full-project`; no source code, no weight, no config,
no graph):

- Status banners added or corrected on **twelve documents**: five current plans, four legacy
  plans, two shipped specs, one execution log — every one of them asserting or implying
  pending work that had shipped.
- `⚠ PROVENANCE` banners added inline at Phase 1 log **§2.11 and §2.12** (`DAF-3`).
- Supersession banner added to `2026-07-24-HANDOFF-track2.md`, the one file in the handoff
  chain that never got one.
- `2026-07-25-HANDOFF-f1-minimum-stop.md`'s "F1 is NOT discharged" **struck in place**, not
  deleted, with the discharge recorded.
- `docs/README.md`: three missing document rows added; the "CURRENT handoff" row corrected;
  the `F1` row corrected; the frontend test count corrected to 78 with a note that counts move;
  the "27 prior claims" count dropped rather than replaced; the dep33-stage3 row's ambiguous
  "Track C log" disambiguated; the role-marker history corrected.
- `api/README.md`: three real `ApiConfig` env vars added that the table omitted.
- `.claude/skills/session-start/SKILL.md`: corrected a claim that three environment traps are
  in `CLAUDE.md` — only one is.
- `plans/2026-07-22-phase2-revised-plan.md`: three bare relative paths that do not resolve
  from `plans/` given `../`.

**Deliberately not changed:**

- **Frozen documents' identifiers.** Nothing renamed anywhere. §3 is a register, not a change.
- **Frozen audit reports and pre-registrations.** The internal severity miscount in
  `2026-07-25-doc-audit-gate1-clips-ux.md` and the subordinate-clause specimen at Track 2
  pre-registration `:227–231` are recorded, not edited. The latter is the actual passage
  `CLAUDE.md`'s incident narrative describes, and its evidential value is that it is frozen.
- **`CLAUDE.md` and anything else in the budgeted standing context layer.** See §7 — that is
  the owner's call, not a session's.

---

## 7. The standing-layer items — decided by the owner, 2026-07-27

The three items below were escalated because they touch the budgeted standing context layer,
which is his call and not a session's. **He authorised all three the same day; they are done.**
The remaining rows are still open.

| Item | Outcome |
|---|---|
| The stale **"27 prior claims"** in `CLAUDE.md` (`DAF-8`) | **DONE — dropped, not replaced with "45".** A count restated outside the table it describes is the drift mechanism itself; replacing one number with another only resets the clock. The row now says to read the count off §6. |
| The **`consultant` agent**'s invisibility from every entry point | **DONE.** Added to `CLAUDE.md`'s orient table and `docs/README.md`'s agent list, carrying the fact a reader most needs: it is **not a subagent**, and a working session must never dispatch it as one, because its value is that its inputs are the owner's rather than another session's paraphrase. |
| `CLAUDE.md` having no `Role:` marker | **DONE.** It was the only document in the role-labelled system without one. |

**Cost of the above, measured from the diff per `closeout` **D6**, in characters because this
layer is written in long single lines that `wc -l` cannot see change in:** `CLAUDE.md`
**37,228 → 38,438** (+1,210 chars, 556 → 559 lines). `memory/` unchanged at 378 lines.
**Nothing was removed to pay for it** — no live passage was compressed to free space, which
the standing rule warns has twice cost the exact clause that made a check usable.

**Two further items were put to him and decided the same day:**

| Item | Outcome |
|---|---|
| The root `README.md`'s status line (§5) | **DONE — reduced to what does not change between gates.** It carried the gate number and date while naming `NEXT.md` as the only document that states them; that line now says "pre-alpha. Not public." and points. |
| The **`builder/README.md` deferral** | **DONE — struck as DISCHARGED in both handoffs that carried it** (`2026-07-24-HANDOFF-track2-complete.md`, `2026-07-25-HANDOFF-track2f-and-headroom.md`). The file was written 2026-07-25 in `0d8b999`, **before Gate 1 closed**, so the condition was met on time and nothing recorded it. Both entries were accurate when written — the file landed about an hour after the later handoff was committed. Struck in place rather than deleted, per this project's convention for handoffs. |

**Still open, and deliberately not acted on:**

| Item | Why it is his, and why it was left |
|---|---|
| Whether **`TEST-QUEUE.md`** (1,134 lines, append-only, grows every closeout) gets archived past some depth | A change to a working ritual's cost, not a defect — nothing in it is wrong. The session's position, which the owner accepted: **leave it** until `session-start` actually feels slow. Archiving early splits the audit trail for a cost not yet paid. |

**`DAF-9` — a deferral with a success condition still needs something that checks it.** The
`builder/README.md` item had a well-formed condition ("written, or explicitly declined, before
Gate 1 closes"), that condition was satisfied **two days** before Gate 1 closed, and it sat
open in two documents for another two days after that. The condition was not the weak part;
**nothing was scheduled to read it.** Worth knowing the next time a deferral is written — and
an argument for `closeout`'s deferral pass explicitly re-testing conditions rather than only
checking that each has one.

### 7a. Role markers, swept to completion

Prompted by the owner asking whether the markers were consistent after §6's fixes. They were
not — a mechanical sweep of the first twelve lines of every document found **eleven** more:

- **Ten handoffs — every one written from 2026-07-26 onward** — had silently dropped the
  `Role:` line the earlier eight all carried. No document decided to stop; the convention
  simply lapsed partway through Gate 2's build tracks. Each now declares its **actual
  supersession state** rather than a generic label, so the chain is readable from any file in
  it without going via the map.
- **`findings/2026-07-25-doc-audit-gate1-clips-ux.md` declared no role at all** — the exact
  defect class it was itself written to check for in other documents. Marker added. Its
  internal severity miscount (§2 of that file claims five HIGH findings; the table has seven
  rows, two HIGH, and the summary sums to six) is recorded in a header caveat and **not
  corrected in place** — the findings stand, only the arithmetic about them is wrong, and a
  frozen report's value is that it is frozen.

**The sweep now returns clean across all 86 documents under `docs/`.** Package READMEs
(`api/`, `builder/`, `frontend/`, `infra/`, `builder/analysis/`) are **deliberately excluded
rather than silently skipped**: the `Role:` convention is scoped to the project record, not to
code documentation, and imposing it there would be inventing a rule rather than enforcing one.

**Not escalated, because they are methodology and therefore mine:** the ten-way split, which
checks each slice ran, what to re-verify, and which fixes were mechanical enough to apply
without asking. All are recorded above so they can be disagreed with.

---

## 8. What this audit did not cover

- **Slice G (legacy plans, ~10,250 lines) ran targeted checks only** — status markers,
  supersession marking, dead references, stale predictions, figure restatement — and says so.
  A defect embedded in the untouched middle of those four large plans would not have been
  found. This was directed, not chosen by the slice.
- **Slice H1 tiered the repair-and-retune log**, reading ~1,990 of its 2,478 lines in full and
  sampling headers across lines 925–1415.
- **No `builder/analysis/` `REPORT.md` was re-derived.** Existence, role declaration and
  reachability were checked for all 24 directories; the arithmetic inside them was not
  re-run, which is `ml-graph-analyst`'s remit and not a doc audit's.
- **`docs/reference/` and `docs/how-we-map-similar-artists.md` were excluded**, per
  `CLAUDE.md`'s standing instruction that neither is project documentation.
- **The three `builder/analysis/` alias scripts** were not executed to confirm the read-only
  aliases still resolve.
