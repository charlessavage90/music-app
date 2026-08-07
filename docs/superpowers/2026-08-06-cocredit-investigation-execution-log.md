# Execution log — the co-credit investigation, 2026-08-06

**Role: ACTIVE, retained reasoning record** for the `CCR-` / `RCC-` / B1 work. It states no
project status — [`NEXT.md`](NEXT.md) owns that — and **owns no figures**: those live in
`builder/analysis/2026-08-06-ccr-relationships/`, `…-rcc-shared-recording/` and
`…-rescale-fidelity/`, each of which says so in its own README. Cited here, never restated.

Branch `cocredit-relationship-probe`, **draft PR #87**. No shipped code was touched — nothing
under `api/`, `frontend/` or `builder/src/`.

---

## §0. What prompted this, and what it concluded

The owner, using the newly-live map, noticed that novel artists arriving at depth looked
disproportionately like **solo acts of known bands** (Panda Bear, Andrew VanWyngarden, Steven
Wilson, Zach Condon), and separately that Leon Bridges and Khruangbin drew **identical album
art and title** — which he correctly diagnosed himself as the genuine *Texas Sun*
collaboration rather than a defect.

From that he formed a hypothesis: **ListenBrainz over-weights similarity between artists who
record together**, since a session-based algorithm credits a collaboration's listen to both
participants. His worked case: **Laura Lee**, a Khruangbin member with no solo releases,
sitting at rank 2 (score 214) on Leon Bridges' list.

**Where it ended.** The mechanism is confirmed at the source and is confirmed to *operate* —
but **two independent instruments decline to attribute the observed class to it**, and the
second of those instruments was validated. The standing explanation for the class remains the
one measured first: the `known` fame ramp compounding along the path.

## §1. Decisions taken, with reasoning

- **The drop rules are not the lever.** Ruled out by the owner on 2026-08-06 and independently
  supported: `ULF-` already removes the clearest cases (Laura Lee is dropped and never reaches
  the graph), and he explicitly does *not* want VanWyngarden or Condon dropped. **An option I
  had tabled to widen the drop rule was withdrawn on his reading, before any work went into
  it.**
- **`RCC-` was made a new document rather than an amendment to `CCR-`.** `CCR-`'s null is
  correct *for what it measured*; folding a different test into it would have destroyed the
  record of an instrument failure that is itself worth keeping.
- **`RCC-`'s control was made within-artist.** A session musician is credited on many
  recordings *by construction*, so a between-artist comparison is contaminated, and
  normalising by recording count would divide out the very property under test. Asking one
  artist about two of their own partners holds recording count, coverage, era and prolificacy
  constant by construction.
- **`RCC-` reused the `CCR-` sample verbatim**, so sampling variance could not be offered as
  an explanation for any difference between the two probes.
- **B1 was run without a pre-registration, deliberately.** It reads the behaviour of an
  already-shipped function, like reading a config value. **Anything *comparing* rescales would
  need one**, and its README says so.
- **Considered and not done:** dispatching `ml-graph-analyst`. The questions here were
  arithmetic I had already written down or MusicBrainz lookups, not derivations — and
  `CLAUDE.md` names re-checking one's own arithmetic as explicitly not what that agent is for.

## §2. Defects found in this session's OWN designs

**All three were caught, and two were caught only because the motivating case was re-tested
against the instrument that was supposed to detect it. That check is the transferable lesson.**

1. **`CCR-`'s instrument could not see the hypothesis.** `inc=artist-rels` carries band
   membership, not shared recording credits. **Laura Lee scores `False` on it.** The null is
   therefore about the tool, and is recorded as such rather than as evidence.
2. **`CCR-`'s plain sentence overclaimed** — *"in a band with **or have recorded with**"*
   while §3 fetched only `artist-rels`. Both halves were written by me about an hour apart.
   **Committing the pre-registration early did not help; it fixed the wrong thing in place.**
3. **`RCC-`'s original tail rule was fatal and silent.** Drawing the comparison partner from
   *absolute* ranks 50–100 requires a 100-long list, and list length is itself a property of
   the arm. It left CONTROL at 15 of 200. **The dangerous shape:** the CLASS half would have
   read perfectly fine while the between-arm comparison was quietly worthless. Fixed by
   `RCC-AM1` (relative depth), committed **before any outcome value was observed**; the
   partial data was deleted.

**`CCR-C3` is void and was left uncorrected** — it tallies every relation type held by a
matching artist rather than the matching relation's type. It carries no branch, so no read
depends on it. Recorded rather than adjusted.

## §3. Gate outcomes

| Gate | Outcome |
|---|---|
| `CCR-G1` (documentation density) | **FIRED** at exactly its 2.0 threshold. Selected the conditional outcome as primary, as pre-registered. Did not void anything. |
| `CCR-C1` / `CCR-C2` | **null** |
| `RCC-G1` (query sanity) | **PASSED**, 200/200 answered in both arms |
| `RCC-C1` | **null** |
| `RCC-C2` | **general**, and the **sign is opposite** to the hypothesis's prediction |
| B1 | No gates — descriptive by design |

**Never reached:** nothing. Both probes ran to their pre-registered run state.

## §4. Corrections to the prior record — including three of my own

**Three claims I made in-session were wrong and are corrected here rather than quietly
dropped.** All three were caught within the session; none reached a committed document
uncorrected.

1. **"The live ListenBrainz dataset has drifted from our archive" — FALSE.** It came from
   reading `builder/scratch/graph-archive` (contribution **5**) when the shipped graph is
   built from `grt-archive-algb/…contribution_3…` (contribution **3**). The correct archive
   reproduces the owner's API query exactly. **The archive path is now named explicitly in
   `CCR-`'s §0 so it cannot recur.**
2. **The drop-coverage figure used the wrong lists.** The **ALG-B** variants apply to this
   graph. Corrected, and the original "0 dropped" was **structurally vacuous** anyway —
   dropped artists are not in the graph to be counted.
3. **"The p99 log clip throws most of the signal away" — OVERSTATED.** B1 measured the
   clipped-edge and tied-top-neighbour shares to be small (figures owned by
   `builder/analysis/2026-08-06-rescale-fidelity/README.md`, §"Verdict"); the log is
   monotonic, so ordering survives. The related claim that the ramp "nearly cancels a doubling
   of similarity" is also corrected: it is a **fraction** of one, and that fraction is owned by
   the same README's §"Raw → rescaled" — **read it there, do not carry it in prose.**

**Nothing in the prior record authored by other sessions was overturned.** `LBS-1`, `CAU-`,
`ULF-`, `GBL-` and the `MSW-` adoption are all untouched. The `CAU-` §6 finding that this
class *"was never looked at"* by the filters is **independently reproduced at population
scale**, at a rate consistent with its own corrected figure — see the `CCR-` directory, which
owns both numbers.

## §5. Operational measurements with no other home

- MusicBrainz answered in **~3 s**, not the 1.1 s rate limit, making each ~400-request probe a
  ~50–60 minute run rather than the ~8 minutes budgeted. **It 503s immediately after a full
  run**; the validation queries needed backoff.
- `CCR-` and `RCC-` each completed with **zero fetch errors** at 200 per arm.
- Both probe runners **resume from their raw JSON**, so an interrupted run costs nothing.
- **D6 standing context layer, measured 2026-08-06 against
  `~/.claude/projects/C--dev-music-app/memory`:** unconditional **45,902 characters**,
  conditional **2,465 lines**. **Delta zero in both** — no `CLAUDE.md`, `MEMORY.md`, skill or
  agent `description:` appears in this branch's diff.

## §6. What is open, and what is closed

**Closed, and should not be re-litigated:**

- Widening the drop rule. Owner's ruling plus two nulls.
- That collaboration *can* inflate similarity — settled from source (`LBS-1`), not open.

**Open, in the order I would take them. Each carries a success condition, per `closeout` A3 —
a deferral without one is an unranked backlog, and "accepted, won't fix" is a legitimate
terminal state.**

1. **The Laura Lee puzzle, and it is the sharpest thing here.** She scores 214 to Leon Bridges
   while sharing **zero** artist credits with him *or with Khruangbin*. Her edge is not a
   co-credit artefact under the definition `RCC-` validated. A **name-collision** hypothesis
   is live but weakened: MusicBrainz holds six artists named "Laura Lee" including a 1945-born
   soul singer, which would explain 214 exactly — but her similar-list reads as a coherent
   modern psych-soul cluster. **If it holds it is `BYP-13`'s defect class reaching the graph's
   edges rather than a clip, which is materially worse.** Needs its own pre-registration.
   **Success condition:** a pre-registered probe reports whether same-name MBID collisions
   measurably shape similar-lists, **or** the owner rules it not worth pursuing. **Kill
   signal** (never a count): if ListenBrainz is shown to key similarity on MBIDs that our own
   archive can verify as correctly resolved, the mechanism is unreachable and this closes.

   > **◐ PARTIALLY DISCHARGED 2026-08-06 (night). The WORKED CASE is closed; the POPULATION
   > question is OPEN and must not be recorded as closed.** Results of record:
   > `builder/analysis/2026-08-06-laura-lee-closure/README.md`, which **owns those figures**.
   >
   > **Discharged half — the kill signal fired for Laura Lee.** Both Laura Lees are separately
   > present under distinct MBIDs; their lists are disjoint in character with no bleed either
   > way; the soul singer holds her own catalogue and audience, so nothing leaked away from
   > her. **`BYP-13` is not operating on the graph's edges here**, and the case cannot reach a
   > user anyway — she is in `drop_mbids` of both ALG-B payloads and absent from the adopted
   > artifact.
   >
   > **Open half, and it is why this deferral stays.** One correctly-resolved pair is **not** a
   > demonstration that the matcher always resolves correctly. **No rate was measured and none
   > may be inferred.** Where her 214 comes from also remains unexplained.
   >
   > **⚠ New evidence pointing AT this item, from an unrelated run.** `TCE-G1` surfaced a
   > same-name mis-filing **inside MusicBrainz's own credits**: the *recording* of *Not Up for
   > Discussion* is filed under the Khruangbin Laura Lee, the *release-group* of the same name
   > under the 1945 soul singer. Reproducible check and machine record:
   > `builder/analysis/2026-08-06-tce-thin-catalogue/miscredit_check.py` → `miscredit.json`
   > (`inconsistent: true`). **This is a different level from the closure's** — MusicBrainz's
   > artist credits, not ListenBrainz's listen resolution — and it is why `TCE-G1`'s first cell
   > passed. **`n = 1`; it licenses no rate and is NOT evidence for the thin-catalogue
   > mechanism.**
   >
   > **Owner's ruling 2026-08-06 (night): this item is DEFERRED until after the `TCE-` re-run.**
   > It is not abandoned and not closed. See `NEXT.md`.
2. **B2 — does an alternative rescale change *which artists appear*?** Testable **without a
   rebuild**: `trimmed_union` fixes the topology, so only stored weights vary — a genuine
   one-knob comparison. Needs a pre-registration. **B1 makes this less attractive, not more:
   the router demonstrably still uses the similarity signal, so a rescale change is not
   low-risk.** **Success condition:** run before any future rescale change is adopted, **or**
   explicitly declined as not worth the risk — which on B1's evidence is a defensible outcome.
3. **The duplicate-artwork detector**, still unbuilt and still the only machine-visible
   symptom of `CLIP-1`. **Success condition:** built and reporting a rate, **or** closed with
   `CLIP-1` if the owner rules that defect not worth fixing — it has no independent value.

**Terminal, needing no further work:** `CCR-C3` is **void, accepted, won't fix** — it carries
no branch and adjusting its number would falsify the record of the defect.
