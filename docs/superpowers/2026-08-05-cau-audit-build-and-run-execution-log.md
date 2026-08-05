# `CAU-` audit build and run — execution log, 2026-08-05

**Role: COMPLETE.** The reasoning behind designing, building and running the coherence
audit. **Owns no figures and no status** — figures live in
`findings/2026-08-05-coherence-audit-results.md`, status in `NEXT.md`. Cited, never
restated.

**Written by the session that did the chunk, while it was still alive, and committed before
it read the result.** It has not seen `cau_result.json`, the findings note,
`cau_owner_notes_SEALED.md`, the scoring session's log or handoff, `NEXT.md`'s current top
block, or any commit message after `adafde1`. That bar exists because knowing what a choice
produced reshapes the recollection of why it was made — the sealed-note problem running in
the other direction.

**On the "no figures" rule.** Section 1 below records **build-side population and
instrument measurements** — how many artists were in scope, how the artifact was sampled.
Those are inputs, not results, and the findings note does not own them. **Nothing derived
from `cau_judgements.json`'s verdicts appears anywhere in this document.** Where a count of
judgements is unavoidable it is one already fixed in the pre-registration before any
judgement existed.

**Chunk boundaries.** Begins where `2026-08-04-gbl-writeup-execution-log.md` ends (the
`GBL-` null written up and committed at `c4e0e8f`). Ends at `adafde1`. Ten commits,
`c8e5494` through `adafde1`.

---

## 1. Numbers computed during the build that are written down nowhere

Recorded because a successor would otherwise recompute them, and because two of them were
decision inputs whose provenance would otherwise be invisible.

**Sizing the audit (first pass, before the pre-registration existed):**

- The V0 arm's deep journeys contain **66 distinct interior artists**; the G arm's contain
  54. Only the G figure reached the prereg (§2). **The 66 is barred from any comparative
  sentence** — §6 bars comparison with today's app, and this number exists only because both
  arms were counted in one pass while deciding what the audit's scope should be.
- **6 artists appear as interiors in both arms; 48 are G-only.** Same bar applies.
- V0's deep journey lengths run **3 to 15 cards** against G's 3 to 11. Same bar. Recorded
  only so a successor knows it was measured and deliberately not used.
- **11 of the 54 G interior artists recur across more than one journey**, which is what
  forced the "a slot is (journey, position)" decision in `CAU-AM1` — the same artist can
  genuinely fit in one journey and not another.

**Sizing the rejected carrier-journey design (§2.1 below):**

- The 8 unaudited **d0** G journeys hold **28 interior slots**, distributed
  **[1, 2, 3, 3, 3, 3, 5, 8]** per journey. The 28 reached `CAU-AM3` as the cost of the
  rejected option; **the per-journey distribution did not**, and it is the part that
  mattered — it is why controls could not be concentrated into two or three carriers
  (§2.1).

**The artifact:**

- `B-S1` holds **63,056 nodes**, of which **24,368 carry a MusicBrainz disambiguation**.
  `CAU-AM4` records the percentage; the raw counts are here.

**The built audit:**

- **52 of the 109 cards** on the served page carry a disambiguation. This is in `7fb587c`'s
  commit message only.
- Judgeable cards per journey, **in the order they appear on the page**:
  **[1, 3, 5, 3, 9, 3, 5, 4, 4, 6, 9, 4, 5, 5, 8, 3]**. Computed live when the owner
  reported that the first journey looked like "just the start and end points". Nowhere in
  the record, and worth keeping — see §3.6.

**The owner's sealed note, at the moment it was committed unread (`4009707`):**

- **797 bytes**, decodes as UTF-8, **no BOM**, non-empty. Verified without opening it.
- Source file mtime **2026-08-05T00:54:45**, from `C:\Users\charl\Downloads`. Recorded for
  completeness while noting the argument made at the time: **an mtime is weak evidence** —
  trivially altered, not preserved by git, does not survive a copy. The commit is the
  evidence. The mtime merely corroborates it.

## 2. Decided against, and why

Negative decisions leave no artifact. Listed unfiltered, including options entertained
briefly.

### 2.1 Alternatives for where the red control lives

- **Carrier journeys — put all 12 controls in the 8 unaudited d0 journeys.** Would have kept
  all 65 real slots scored and left the audited journeys pristine. **Rejected by the owner**
  on cost (28 extra judgements of pure camouflage, workload 77 → 105); `CAU-AM3` records
  that it was his call. Recorded here: I would still call it the scientifically cleaner
  design, and if a future audit has more of the listener's time available it is the one to
  build.
- **Concentrating controls into 2–3 large carriers instead of spreading over 8.** Rejected
  before it was ever offered: with the per-journey slot distribution above, a carrier would
  have had to run roughly a third fake, and a journey that is a third nonsense reads as
  obviously broken — it identifies itself as a carrier and the control dies.
- **Using V0 journeys as carriers.** Rejected: it puts the other arm's journeys in front of
  the listener, which muddies "one-arm audit" and creates a comparison the design bars.
- **Whole fake journeys as the control** — 12 journeys with entirely random interiors.
  Rejected: rejecting an obviously random path is a far easier task than spotting one bad
  card among real ones, so `CAU-G1` would pass trivially and prove nothing about the
  instrument's resolution at the difficulty that matters.
- **Mid-path placement plus excluding both flanking slots.** The arithmetic was ~24 slots
  lost, `D_all` ≈ 41. Rejected in favour of endpoint-adjacent placement, which costs 12.
- **Showing the contaminated card without judgement controls.** Rejected: a card with no
  radio buttons is visibly different, so the listener learns that controls sit next to
  exactly those cards. The exclusion had to be silent, which is why he judges all 77 and the
  scorer discards.
- **Reducing the control count below 12 to save workload.** Rejected: the 10-of-12 bar was
  already pre-registered, and lowering the count after the fact is moving a bar.

### 2.2 Alternatives for the instrument

- **A scored per-journey "does this journey hang together" question.** Considered once
  `CAU-AM1` made whole journeys visible, since the owner's `GBL-` complaint was about
  whole-path detours. Rejected as scope creep: it needs its own pre-registered bar, and on
  his own `GBL-` notes it was likely to come back uninformatively positive for this arm.
  Kept as **unscored free text** so the impression has somewhere to land without becoming a
  criterion invented after the fact.
- **Mandating a minimum number of tracks or a listening time floor.** Rejected as
  unenforceable and infantilising; "as long as it takes" is the honest instruction.
- **Asking him to log which tracks he heard.** Rejected as heavy for what it buys.
- **Inferring "had to look them up" from response timing** instead of a checkbox. Rejected:
  needs instrumentation, and timing is meaningless across sittings split over hours.
- **Reordering the page so short journeys come last.** Offered after he hit the one-interior
  journey first; I recommended against it and he agreed it was a false alarm. Reasoning:
  order is not load-bearing for any criterion, so the change would buy only ergonomics while
  costing a regenerated sealed artifact mid-run and the sentence *"the tooling was adjusted
  after the listener saw the first item"* in the record.
- **Prepending a provenance header to the owner's sealed note.** Rejected: it means
  rewriting his file. Provenance went in the commit message instead, and the file is
  byte-identical to what he wrote.

### 2.3 Alternatives on process

- **Scoring the audit myself.** Declined. The run brief said a fresh session scores and
  writes up, and the reason binds hardest on the session that chose the bars and built the
  instrument. Considered the `GBL-` precedent, where the runner ran the mechanical unblind
  and committed the result before handing over — that runner was *blind*, which is what made
  it safe; I was not, so the precedent does not transfer.
- **Reading the owner's note to check it before committing it.** Declined; committed unread.
- **Using `pop_raw` or a degree-derived quantity to match injected artists.** Never
  seriously entertained, but recorded because it is the standing trap: the matching currency
  is `fame_lb_pctl` via `cre_common.Ruler`, the adopted novelty-likelihood proxy. No retired
  currency is touched anywhere in this harness.

## 3. What the owner said that never reached a file

Four amendments came from him. These are the parts of the conversation that did not.

1. **He confirmed, explicitly, that he scored the `GBL-` rows on coherence.** *"Whether I
   meant to or not, that's how I ended up scoring the rows."* The `GBL-` findings note
   records this as **my inference from his written notes** (its §2.2). His confirmation came
   later, in conversation, and **upgrades that inference to a stated fact.** It is nowhere in
   the record. Anyone re-reading `GBL-` should know the inference was checked with the person
   who made the judgements.
2. **He raised the run-once tension himself before I did** — *"I expect you won't like it
   because we're past the blind test."* He was not trying to slip a re-test past the rule; he
   named the objection and asked for a view. Worth recording because the record otherwise
   reads as though a session imposed the constraint on him.
3. **His argument for why fixing clips would not fix the problem** — that there is no way to
   evaluate an artist from a 30-second slice of one song, and that this only started to
   matter once real numbers of novel artists appeared. The prereg §0 captures the substance.
   What it does not capture is that **this was his diagnosis, not mine** — I had recorded
   clip failures as a power problem in the `GBL-` note without seeing that the failure is
   correlated with the treatment.
4. **He declined to set `CAU-C1`'s bar when first asked**, then ratified 75% after being
   shown the `REQ-9` argument. `CAU-AM2` records the ratification and the initial no
   preference. It does not record that I had proposed 85% and 65% as the alternatives, with
   85% flagged as likely to park the audit in the ambiguous band and answer nothing.
5. **He paused the run rather than push through when the presentation confused him** — *"I'm
   pausing briefly because I don't want to wreck the experiment."* Behavioural, and the
   reason the one-interior-journey confusion cost nothing.
6. **The one-interior journey reads as broken to a listener.** He reported seeing "just the
   start and end points" and stopped. It was not a bug — the shuffle put the shortest journey
   first. **A journey with a single interior card looks like a rendering failure**, and any
   future audit built on this harness should either order short journeys away from the front
   or say up front that some journeys have one judgeable card.
7. **He asked whether the next session needs a `session-start`.** Answered yes, full ritual;
   not recorded anywhere, and not mine to write into a session prompt.

## 4. Defects in my own plan and code

The handoff lists five and was written short. Complete list, including the ones fixed
silently.

**In the design (both caught by the owner, both pre-run):**

1. **Isolated triples could not pose the question** where several consecutive artists are
   novel to the listener — `CAU-AM1`.
2. **An inserted control contaminated its two real neighbours** — `CAU-AM3`. Measured on the
   discarded build before it was thrown away.

**In the pre-registration, caught by my own tooling:**

3. **`CAU-CORR1`** — §4 said controls *replace* an artist while `CAU-AM1`'s arithmetic said
   77 = 65 + 12. Found by the build script's self-check 5, not by re-reading.

**In the code and the harness:**

4. **A test that tested nothing.** Reverting `CAU-AM3`'s placement rule left all 29 tests
   green, because nothing drove `pick_injections` — only a downstream guard would have
   caught a regression, and only at run time in front of the owner. Found by mutation
   testing, fixed with two tests that drive the function directly.
5. **`/status` was stricter than the governing document**, requiring all 16 optional journey
   notes before reporting complete. A blank textarea never fires `onblur`, so "complete" was
   **unreachable** for an honest listener. He hit it having judged everything. The scorer
   never had the bug.
6. **The run brief was written in bash** (`VAR=value cmd`), which fails in cmd.exe. Neither
   env var was needed for those commands.
7. **A Snyk MEDIUM false positive** on a dict key literally named `"pass"`. Resolved by
   renaming the `CAU-C1` branches to `meets_bar` / `ambiguous` / `below_bar` — better naming
   regardless, since the middle branch is deliberately neither.

**Method defects, fixed silently, and the more useful half:**

8. **I reported a file edit as done when it had not happened.** A patch script printed
   `"brief fixed"` unconditionally without asserting the substitution occurred; git caught it
   with "nothing to commit". **This happened twice** — the run-brief fix and the branch-name
   rename in the tests — both times because a search string with `\n` failed to match a file
   git had normalised to CRLF. Root cause is not the line endings, it is **printing success
   without asserting it**. Every later patch script asserts.
9. **Heredoc escaping mangled two committed test lines.** A `\` line continuation collapsed,
   leaving assertions with the message run onto one long line in `test_cau_score.py` and
   `test_cau_page.py`. Valid Python, tests pass, purely cosmetic — recorded so it is not
   mistaken for intent.
10. **The first build was generated under the defective placement and discarded**, along
    with its sealed map. `CAU-AM3` says so; recorded here because "a build existed and was
    thrown away" is the kind of fact that later looks like a gap.
11. **Two background-server tasks report `failed, exit code 1` in the task log.** Both are my
    own `taskkill`. Noise, but a successor reading those logs could misread them as harness
    faults.

## 5. Why the audit is shaped this way, beyond what the amendments argue

**Endpoint-adjacent injection placement** — `CAU-AM3` gives the contamination argument. The
second reason is not written anywhere: **endpoints are the owner's own picks and therefore
always familiar to him**, so a control placed beside one can be judged without a lookup, in
context he fully understands. The cost, and it compounds `CAU-AM4`'s: **a control next to a
familiar anchor is probably easier to reject than one buried mid-path**, so `CAU-G1` is
easier to pass than the mid-path version would have been. Both weakenings were taken
deliberately and both point the same way.

**Obscurity banding** — ±0.05 on `fame_lb_pctl`, doubling on failure, **capped at 6
widenings** before falling back to distance-only. The schedule and the cap are
arbitrary-but-bounded; what matters is that **widenings are recorded per injection**, so a
reader can see how hard each control actually was. In the shipped build the schedule never
engaged. A successor reusing this should know the cap exists and that it was never
exercised.

**The `None` band is its own band.** An artist the ruler cannot read must be matched by
another the ruler cannot read — otherwise the injection is detectable by *the absence of a
reading* rather than by the music. This is in a code docstring only.

**Distance 3, not 2 or 4.** Three is the smallest value guaranteeing **no edge and no shared
neighbour**. Two would permit a common neighbour, which is exactly where a coincidentally
plausible artist lives. Four or more shrinks the candidate pool and starts forcing band
widenings, trading control hardness for control detectability.

**No clips on the page, deliberately** — a 30-second preview is the instrument this audit
exists to replace. This is the single most important shape decision and it is stated in the
brief but nowhere as a design rationale.

**Radios save on change, not behind a save button.** The `GBL-` runner had to verify
separately that the page's save button wrote through, because a broken button would have
been invisible to an API-level test. Removing the button removes that failure mode. It also
created the journey-note bug (§4.5), since a textarea's `onblur` is the analogous trap.

**Port 8766, deliberately not `GBL-`'s 8765**, so a stale `GBL-` server cannot be mistaken
for this one.

**Shuffled journey order, no pair or depth labels** — prevents anchoring and stops him
grouping journeys by pair and comparing d10 against d20, which is a comparison the design
does not ask for.

**Seed committed in source** (`cau_build.SEED`) so the draw is reproducible from the repo
alone.

**Two denominators declared before the run** specifically because `D_lookup` is the harder
population and will score worse — declaring only one, or choosing after, is the classic
post-hoc move.

**`CAU-C2` exists because a rate cannot distinguish sprinkled failure from concentrated
failure**, and one wrecked journey in eight is a different product from the same rate spread
thin.

**`CAU-C3` exists to falsify this audit's own premise.** It was put in deliberately so the
design can undermine its own rationale rather than only confirm it.

**The load-bearing design move, which no document states as such:** the tension with `GBL-`'s
run-once rule dissolved once the question was reframed as **one-sided** — *is the new
material junk?* — rather than as a rematch. A one-arm question needs no comparison, no
margin and no blind, which is what made the audit cheap, fast and compatible with the null
standing untouched. Everything else in the design follows from that reframing.

## 6. Gate outcomes

| Gate | Outcome |
|---|---|
| Build self-checks (five, against the real artifacts) | **All passed on first firing.** Material shape, every artist resolving in `B-S1`, one injection per journey and exactly 12, the `CAU-CORR1` slot arithmetic, `CAU-AM3`'s `D_all` arithmetic, and the page-cleanliness scan |
| Band widenings needed | **Zero** — every control matched its target's obscurity band *and* cleared distance 3. The strongest available form of the control |
| Harness test suite | **33 passed** |
| Mutation checks | **7 run, 6 red as intended, 1 green** — the green one exposed §4.4 and was fixed |
| Snyk code scan | 1 MEDIUM, adjudicated a **false positive**, resolved by rename; **rescan clean** |
| Live endpoint exercise | Passed — status, judge, bad-verdict rejection, unknown-slot rejection, restart persistence |
| **Browser render check** | **NEVER REACHED.** The Chrome extension was not connected. Fell back to `node --check` on the script extracted from the served page, plus the live endpoint exercise, and told the owner explicitly to confirm the page rendered before settling in |
| `CAU-G1`, `CAU-C1`, `CAU-C2`, `CAU-C3` | **Never computed by this session, by design** |

**The never-reached gate cost something real, and it is the clearest instrument lesson
here.** A render check is exactly what would have surfaced the one-interior journey looking
like a rendering failure (§3.6). Instead the owner found it mid-run, paused, and asked — which
worked, but only because he stopped rather than pushed on. The `GBL-` run log had already
recorded that a real browser check catches what an API-level test cannot; that lesson was
available and could not be applied.

## 7. Other things not in the durable record

- **The audit is not any of the options the `GBL-` findings note offered.** Its §4 listed
  accept-the-null, open-the-clip-defect-as-a-track, and open-the-detour-question. What the
  owner chose is closest to the second but reframed from **repair** to **measurement** — the
  clip defect is not fixed, it is routed around by changing the instrument. A reader
  comparing §4 to what happened will not otherwise find the mapping.
- **The `GBL-` findings note's §6.4 flagged preview *quality* as an unmeasured defect class
  distinct from `BYP-13`.** The owner's diagnosis (§3.3) is the sharper version of that same
  observation, arrived at independently a few hours later. The two should be read together.
- **This session was the sole occupant of the tree throughout the build and run.** It was
  told another session was live only when asked for this log. Nothing in `c8e5494`–`adafde1`
  needs the concurrent-session caveats.
- **A pattern in the owner's two design catches, and they are the same shape.** Both were
  about *what a card's neighbours mean*: isolated triples stripped the neighbours of meaning
  when they were unfamiliar; an inserted control gave a real card a meaningless neighbour.
  Neither was visible from inside the design, and both were found by imagining the act of
  judging rather than by reading the specification. **A future pre-registration for anything
  presented to a listener should be walked through as a listener before it is committed** —
  that is the cheap check both defects would have failed.
- **`cau_page_data.json` was gitignored deliberately and temporarily**, with the un-ignore
  instruction placed in the brief and the handoff. If a successor finds it still ignored
  after the write-up landed, that is an untidied loose end, not a decision.
- **No question is settled on the way out of this log.** Everything above is the state as it
  stood at `adafde1`. Anything the scoring session found supersedes it.
