# `LBD-S4` adoption at `LBA-A6` — retained execution log

**Role: ACTIVE, retained.** Appended **per task**, not at closeout. Decisions and reasoning, not
narration — this is what makes the session replaceable rather than precious.

**Governing document:** [`specs/2026-09-14-lbd-s4-adoption-preregistration.md`](specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), §11's `LBA-AM1`–`LBA-AM4` read before §3, §4, §5, §7 or §8.
**It owns no figures**; candidate figures are owned by this session's `builder/analysis/` directory
when one exists. **Status is `NEXT.md`'s**, never restated here.

**Scope, from the owner, 2026-09-21.** Task 1 — the `LBA-AM4` amendment. Task 2 — §8 items 1–3, the
candidate build, and nothing else. **Hard bars he set:** generate no journey on either map, design
no listen, do not deploy, do not change `ApiConfig.graph_path`, re-read no `LBD-` or `LBA-`
criterion, both `LBL-` verdicts run-once and final, and the `P` drop payload is
`unlistenable_drop_algb_20260809.json` and no other.

---

## Task 1 — `LBA-AM4`, the unblinded use gate (`LBA-G5`)

**Committed before any build work began**, which is the property the amendment exists to have.

### What was decided, and why

**Identifiers.** `LBA-AM4` and `LBA-G5` were both swept across every local and remote ref before
minting, per `CLAUDE.md`'s collision rule — `git grep -lE` over `refs/remotes refs/heads` limited
to `*.md`, never the working directory. Both silent. `LBA-G5` is minted because `CLAUDE.md`
requires every gate to carry its own effect size under its own identifier; calling the new stage
"the use gate" without one would have made it unciteable.

**§8 is NOT renumbered, deliberately.** The gate sits between items 3 and 4 as a marked insertion
that leaves items 1–4 with their numbers. The alternative — making the listen item 5 — would have
silently falsified every document already written that says *"§8's four items"*, which includes
stage-3 README §9's options B, C and D, all three of them frozen. §11's own rule is that an
amendment is added *beside* the text it qualifies rather than edited into it.

### Two corrections to the owner's brief, both made before writing

Recorded because both were going into a pre-registration, which is the document class whose entire
value is that it was committed before results, and a false premise inside one is not recoverable
later.

**1. The `CXR-` detection latency — the correction was mine and it was WRONG, and the owner's
original brief was right.** Four documents state the revert criterion fired *"after three weeks of
use"*. I read that as time-to-detect and told the owner his "within the first hour" premise was
contradicted by the record. **He corrected it: he noticed within minutes; the three weeks was
availability** — he was away, and as the app's only user he left it until he had time to roll back.
**None of the four documents says which quantity it measures**, which is exactly why the misreading
was available. The correction goes forward into `LBA-AM4` rather than into the four documents, all
of which are COMPLETE or HISTORICAL and are therefore never edited (`docs/README.md`'s rule, and
`session-start` MT1's).

**This changed the amendment's argument, not just a date.** "A short period is the cheapest
detector" is a claim about cost; "detected within minutes, by use, and by no instrument in advance"
is a claim about *sensitivity*, and only the second makes a two-day bound defensible rather than
merely convenient.

**2. `LBA-A3` differs from the candidate in TWO columns, not one.** The brief described the
fallback as differing "in population only". §2.1's own baseline column says `V` → `P` moves
population **and** the drop-list payload (`…20260805` vs `…20260809`), and its boxed warning is
explicit that the column is real even where its effect is zero — the `20260809` payload would drop
31 members of `V`. The fallback is unaffected and remains sound; what changes is what the amendment
is permitted to claim about the comparison, and it now says two columns. Accepted by the owner
without objection.

### The owner's two inputs, recorded verbatim

Given 2026-09-21, **before he had seen a single journey on any `LBA-` map** — no candidate build
existed, and no arm carried `fame_lb` at all. **No draft criteria were offered to him**: the
`CXA-` precedent's value is that the trigger is his words and not a rationalisation, and giving him
wording to react to is the one act that would have contaminated it.

- **Criterion:** *"a noticeably worse product experience on more than half of tested journeys"*,
  meaning **novel artists become more difficult to surface OR novelty is traded for coherence**
  (novel artists surface but the path's coherence suffers as a result).
- **Period:** **2 days of actual app use, maximum.**

⚠ **The second limb is new.** The 2026-08-10 `CXA-` criterion had the novelty limb alone, so a
candidate trading coherence for novelty would have passed it and fires this one. Recorded as his
difference, not as a session's paraphrase of the older criterion.

### Claims verified from source before the amendment cited them

Per `CLAUDE.md`'s rule that every function, file and config value a document names is grepped
before it is relied on:

| claim | verified |
|---|---|
| `graph_store.fame_percentiles` is the ranking device | `api/src/artistpath_api/graph_store.py:141`, called at `:329` |
| a fame-free artifact has **no** ranking, not a degenerate one | `graph_store.py:329` — `fame_lb_pctl=… if fame_lb else None` |
| `require_fame` is the builder knob `LBA-D5` pinned | `builder/…/config.py:132`, consumed `pipeline.py:448` |
| the `P` payload name | `builder/…/unlistenable_drop.py:101`; used in stage 2's `s4_build_A*.json` |
| `LBA-A3` = `LBD-A5V` is built, serialised and fame-carrying | `C:\unsung-fast\lbd-artifacts\LBD-A5V.bin` + sidecar, on disk |
| every relative link in the amendment resolves | checked programmatically, none broken |

### What Task 1 does not do

No build, no journey, no listen design, no default changed, no shipped code touched, no `LBD-` or
`LBA-` criterion re-read. `ApiConfig.graph_path` untouched.
