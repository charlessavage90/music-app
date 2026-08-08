# Retained execution log — the `CEX-` crawl-extension design, 2026-08-07/08

**Role: RETAINED EXECUTION LOG.** Reasoning behind the `CEX-` design and plan. **Owns no
figures** — `builder/analysis/2026-08-07-cex-frontier/` and
`builder/analysis/2026-08-08-cxs-growth/` own them, cited by name and never restated.
Status lives in [`NEXT.md`](NEXT.md).

Governing document: [`specs/2026-08-07-crawl-extension-design.md`](specs/2026-08-07-crawl-extension-design.md).
Operational document: [`plans/2026-08-08-crawl-extension.md`](plans/2026-08-08-crawl-extension.md).
Handoff: [`2026-08-08-HANDOFF-cex-design.md`](2026-08-08-HANDOFF-cex-design.md).

**No shipped code changed.** The diff is three documents, two doc-map rows, and two analysis
directories.

---

## §1 — What the owner asked, and what it turned out to be

He asked to expand the crawl beyond 75,000, for **known missing artists** and **headroom**,
naming two artists: Goose (the Norwalk jam band) and Commander Cody.

**The single highest-value decision in this session was refusing to plan before checking those
two names.** It cost about ten minutes and it dissolved half the stated motivation:

- **Commander Cody was never missing.** Crawled, shipped, 4 inbound references. Unfindable
  because search is literal prefix-or-substring and the map spells him *"& His Lost Planet
  Airmen"* against the queried *"and the Lost Planet Airmen"*. **A search defect (`CEX-R3`),
  and no crawl fixes it.**
- **Goose is genuinely absent, and no crawl fixes that either** (§2).

Had a plan been written first, it would have been a multi-hour crawl that addressed neither
example. This is the `cheapest-experiment-first` rule paying out on its stated terms.

## §2 — Two claims of mine, both falsified, both by measurement

**Recorded prominently because they are the transferable part of this session.**

### `CEX-R1`'s remedy — seeding — was wrong, and the review caught it

The first draft of the spec's §3 argued a seeded Goose would survive because `trimmed_union`
keeps an edge if *either* endpoint ranks the other in its top-`j`. **That is the union step,
and it is not the step that decides.** `trimmed_union_cap` then trims every node to the degree
ceiling, with no floor protecting a node's last edge.

An independent review session (`CEXR-1`) found this from the source and named the exact
measurement that would settle it. **It was right, and it flagged itself as the finding it
would abandon most cheaply — which is what made it worth testing rather than accepting.**

**I then made a second error while verifying it.** Fleet Foxes' degree is 44, under the ceiling
of 50, and I read that as headroom that would save Goose. It is not headroom: **2,792 artists
compete for those slots**, and the 44 is the residue after a wildly oversubscribed node was cut
to 50 and lost a few more to partners' trims. **A single degree number cannot distinguish
"has room" from "was cut to the bone"; the inbound count can.**

Settled by build, not argument: a matched pair differing only in Goose's presence produced
**identical node and edge counts**, and Goose was absent at all three ceilings including the
most permissive selectable one. Figures owned by the `cex-frontier` directory.

### The hub-competition worry was wrong, and it was mine unprompted

I told the owner that more artists would crowd the hubs and squeeze the obscure tail out. He
correctly translated it back and asked whether he had understood. **On re-examination the claim
was an expectation I had stated as a finding, and I withdrew it — then measured it under
`CXS-`.**

**It runs backwards.** The tail gets *better* connected as the crawl grows, monotonically, and
hub saturation *falls*. Figures owned by the `cxs-growth` directory.

**What generalises:** both errors were confident inferences from partial mechanism — half an
algorithm in the first case, one of two opposing mechanisms in the second. Neither was caught
by reasoning harder. Both were caught by building the thing.

## §3 — Decisions taken, with reasoning

- **Seeding removed from the track**, rather than deferred. The question is answered, not open.
- **The cap rule is a separate track.** Track B already priced both sides (exclusion 538 → 34
  at ceiling 100; famous-pair hub transit +75…+152 %). Nothing needed re-measuring; the owner
  asked whether higher caps had ever been tested and the answer was already in the record.
- **The search fix is a separate track.** It shares no code and no artifact with the crawl, and
  bundling it would make a cheap fix wait on an adoption decision it does not need.
- **The archive snapshot is a required step, not a suggestion** — the owner's condition for
  proceeding. It converts the one genuinely irreversible step into a reversible one.
- **Inline execution recommended over subagent fan-out** for the plan: every task is sequential,
  four tasks touch `cli.py`, and each task already carries complete code and tests.

## §4 — Decided against

- **Building the uncapped case** to confirm that only an already-condemned configuration would
  hold Goose. It would not have changed a decision — uncapped is barred from candidacy — so it
  was left as labelled inference. (`stop-refining-instrumental-artifacts`.)
- **Narrowing `CXS-`'s cohort** to rescue `CXS-C2`'s relative threshold. That would have broken
  the frozen-frame control which is the whole design; `CXS-AM1` changed the *read* instead.
- **A `no_release` / `featured_credit` re-census** at plan step 6. `pipeline.py:279-284` states
  all three classes are strict subsets, and the baseline census bears it out.

## §5 — Defects in this session's own documents, found by review

The independent review returned **fourteen findings**, all dispositioned in the spec's §10.
The ones that changed the design rather than the prose:

- **`CEXR-2`** — `--algorithm` is needed at four steps, not one, and there is **no `RC-H3`
  counterpart on the build side**. A defaulted build silently reads ALG-E's tree and lists.
- **`CEXR-4`** — acceptance rejects on **both** bounds. The spec named the node ceiling only,
  which would have handed the owner a narrower decision than the real one.
- **`CEXR-5`** — the refusal **can** misfire across runs; the original argument that it could
  not was wrong. Fixed with a checkpoint `exhausted` flag.
- **`CEXR-7b`** — `refrontier` must **union**, not replace. **`CEX-G1` structurally cannot
  catch this**: the frontier is a set difference, so a replacing rewrite reports the correct
  number while having broken `done ⊆ discovered`. A second assertion was added.

## §5a — What the closeout audit found in this session's own output

**Six HIGH findings, every one of them mine, and none of them findable by the checks I had
already run.** All fixed before the PR. The three worth carrying:

- **I cited "PR #91" in two documents before the PR existed.** The highest PR in the repo was
  #90. This is the project's signature failure — confident prose about a fact nobody checked —
  and it would have sent a cold session hunting for a PR that had never been opened. **A number
  invented for a document is a claim, and it gets checked like one.**
- **Plan Task 8's code would have raised `NameError`.** It told the implementer to append a log
  line reading a variable `rescaled` "at the end of `rescale_scores`" — but that function has no
  such variable and no shared end, returning an inline comprehension from one branch while the
  other raises. **The plan's own promise is that it is prescriptive; a task that cannot be run
  as written breaks exactly that.** Verified against source and rewritten as the small refactor
  it actually requires.
- **`docs/README.md` named two current handoffs at once.** I edited the bypass-tray handoff's
  role line and did not update its row in the map. The map is what a cold session trusts to
  resolve exactly that ambiguity.

**And one defect of absence, which is the class the audit exists for:** the frozen baseline
census README still ended a sentence "— only seeding can", written the day before seeding was
falsified. Nothing in it was false; it simply had no forward pointer, so a reader arriving from
a citation would have come away believing a dead remedy was live. **A grep for wrong content
cannot find a missing sentence.** Fixed with an inline forward pointer that leaves the figures
untouched.

**Two of my documents also restated figures the `builder/analysis/` directories own** — one of
them in a bullet that simultaneously claimed the figure was recorded nowhere else, four lines
below the log's own "owns no figures" role line.

## §6 — Gate outcomes

| | Outcome |
|---|---|
| `CXS-C1` (primary) | **Material and monotonic** — the pre-registered rise branch fired |
| `CXS-C2` | **Null** — below the `CXS-AM1` bar |
| `docs-lint` hard checks | **Passed**, after fixing one failure of my own (the plan had no role marker) |
| `doc-auditor` (closeout B1) | **Six HIGH, all in this session's own output, all fixed — see §5a** |
| `CEXR-1` verification | **Confirmed** — seeding falsified at three ceilings |
| Snyk Code (new analysis script) | **0 issues** |
| `CEX-G1`, `CEX-G2` | **Not reached** — they belong to plan execution |

## §7 — Corrections to the prior record

- **`config.py:17` is stale and is not yet fixed.** It calls ALG-E "the adopted 75k archive's
  algorithm"; the adopted map's lineage is **ALG-B**. Surfaced by the review, recorded as
  `CEX-R5`, remediated by **plan Task 7** — so it is still live in the tree today.
- **`ULC-F3` is reproduced, not merely cited**: `discovered` and `done` are both exactly
  75,000 and the recorded frontier is 0.
- **`ULC-F2`'s extended-population direction has still never fired.** It fires at plan step 6.

## §8 — Operational measurements with no other home

- **The archive size and the free space on the volume are owned by the spec's §4 step 0**,
  where the snapshot precondition is defined — cited here, not restated. The point worth
  recording is the *consequence*: the snapshot turned out to cost a negligible fraction of the
  volume, which is what made it a required step rather than a trade to argue about.
- **File mtimes recover the true crawl order**, spanning 2026-07-29 21:53 to 2026-07-30 06:02.
  **The span and rate are owned by `builder/analysis/2026-08-08-cxs-growth/README.md`'s
  "Provenance of the subsets"** — cited, not restated. *(An earlier version of this bullet
  restated both figures and asserted they were recorded nowhere else. That was false — the
  `cxs-growth` README already had them — and it violated this log's own "owns no figures"
  role line four lines from the top. Found by the closeout audit.)* The exact wall-clock
  timestamps above are additional detail and have no other home.
- **Build times** (`drop_unlistenable=False`, warm cache): ~20 s at 25k, ~40 s at 50 k, ~56–84 s
  at 75 k, ~72–78 s at ceiling 100. The first cold build of the session took **496 s** — an
  8× spread that makes any single timing a poor basis for a timeout.
- **A 10-minute tool timeout killed a probe mid-run and skipped its `finally` block**, leaving
  the archive at 75,001 with a seeded file in it. Caught and reverted; verified back to 75,000.
  **`finally` does not survive SIGTERM.** Both later harnesses were rewritten to use an
  in-memory read-only `RawArchive` overlay so there is no cleanup to skip. **This is the
  reusable lesson: a probe against a shared artifact should not write to it at all.**

## §9 — Standing context layer (D6)

**Unconditional 45,902 characters — delta 0. Conditional 2,465 lines — delta 0.** Neither
`CLAUDE.md`, `MEMORY.md`, nor any skill or agent `description:` was touched. Nothing is owed.
