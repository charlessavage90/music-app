# Retained execution log — `JFX-AM1`, the pre-registration critique amendment, 2026-08-09

**Role: RETAINED EXECUTION LOG.** Reasoning behind `JFX-AM1`. **Owns no figures** —
`builder/analysis/2026-08-09-jfx-prereg-critique/README.md` owns the reachability
measurement, and the analyst's simulations are recorded in the amendment clauses that rest
on them. Owns the D6 standing-layer numbers, which the closeout rule requires to live here.

**No arm ran.** No artifact built, no pair routed, no fame statistic computed. The only
measurement is a static property of the already-adopted artifact.

Branch `crawl-extension-design`, PR #91.

---

## §1 What this session was for

The owner opened it as the `JFX-` execution session and asked for an `ml-graph-analyst`
review of the pre-registration **first**. That review, two owner corrections, and two
defects found by writing code against the document produced `JFX-AM1` — twelve clauses,
committed before any arm ran.

The session did **not** proceed to run the arms. It recommended a handoff instead (§7).

## §2 Decisions, with reasoning

### The four clauses that change what passes

| Clause | Decision | Why |
|---|---|---|
| `AM1.2` | Fame quantity becomes **log-scaled** | **Owner decision.** Raw counts span four orders of magnitude, so a pooled median over three strata is a rank statistic landing inside `S2`; `S1` and `S3` movement is invisible to it. Log is a fixed monotone transform, so it satisfies §2's currency rule's *reason* exactly as raw does and unlike percentile. |
| `AM1.5` | `G1b` becomes the linear contrast `T = D_B − 0.67·D_A` | The ratio's behaviour is governed by its denominator's signal-to-noise. Simulated, it declares a genuinely equal map broken **up to 42%** of the time when that denominator is weak, with the interval spanning negative values. `T` is algebraically identical for `D_A > 0` and always bounded. |
| `AM1.6` | Three step tests → one **simultaneous band**, plus an effect size | Four correlated tests at nominal coverage gave a **7.5–8.2%** false-stop rate under a truly flat gradient. The max-statistic band restores family-wise 5% from replicates that already exist. |
| `AM1.7` | `C6` and `C7` get effect sizes | Both fire §4 branches on the undefined word *"materially"*, and `C6`'s branch **voids every one-knob reading in the document**. |

**The 67% bar is UNCHANGED, and that was a decision rather than an omission.** Three reasons,
recorded because the reasoning is what a later reader needs: `AM1.2`'s log switch repairs the
arithmetic distortion that made the bar looser than its own press-count translation; it is a
*"the map is broken"* bar, so leniency sends marginal maps to the owner as a judgement call
instead of auto-rejecting them; and adjusting a threshold on a guess about curve shape is not
better than leaving it when the design measures the shape directly. **Added instead: the
report states the realised press-count equivalence beside the ratio**, converting the
assumption the bar rests on into a measured quantity.

### A decision this session REVERSED — its own

`AM1.1` **withdraws a proposal this session made and argued for.** It recommended removing
the famous–famous stratum from the `JFX-G1` gate, on `PRODUCT-REQUIREMENTS.md` §8's record
that superstar endpoints have zero edges below the top popularity decile.

**The owner challenged it from use of the live app** — novel artists appear far more often
than on the old map, including on famous-to-famous journeys — and named the reason the
record might not transfer: it predates the current fame construct.

**Measured, and the proposal was wrong.** Three independent reasons it does not transfer, all
of which the owner had raised or implied: the finding was measured on the **pre-`MSW-`**
artifact under **mutual k-NN**, in **popularity** currency, under the **retired** worldly-fame
construct. Mutual k-NN required *both* endpoints to rank each other, which destroyed exactly
the famous↔obscure edges an obscure artist contributes; `trimmed_union` keeps them.

**⚠ `DD-F1` is NOT overturned, and this is the half most at risk of being collapsed.** It
survives in popularity currency at the very top and fails to transfer to fame. Recording it
as refuted would be the §2.6/§2.11/§2.12 currency error a third time — which is what this
session committed by carrying the claim across currencies without checking.

**⚠ The measurement is STRUCTURE, not ROUTING.** It licenses *"famous endpoints can
descend"*, never *"journeys do"*.

### An owner correction to the write-up

The session described the `MSW-` switch as having remedied this **incidentally**. **It did
not: improving famous-to-famous behaviour was one of his reasons for the switch.** Recorded
as a designed remedy.

**⚠ And that surfaced a gap in the record.** Swept the `MSW-` execution log, plan and
handoff for the concept — **zero hits.** The adoption is written up resting on the coherence
argument and the filter fix, and is silent on a reason the owner actually held. So the
`MSW-` adoption is recorded on **narrower grounds than it had**. Corrected forward in
`PRODUCT-REQUIREMENTS.md` §8; the frozen `MSW-` records were not edited.

**The 2026-07-29 defect ruling is NOT closed.** The structural precondition behind it no
longer holds, which is not the same thing. Closing it is the owner's, and structure is not
routing.

## §3 Defects found in the document itself, not in code

The pre-registration was committed 2026-08-09 and reviewed the same day. Six defects, the
first two of which made parts of it undefined rather than merely imprecise:

1. **The measurement instrument was never named.** No routing function, no press-selection
   rule, no ruler frame. Each unstated choice changes the primary number, and one of them —
   `find_path` vs `find_journey` — would have dropped a *different* pair set in each arm,
   which is selection on the outcome inside a paired design. `AM1.3`.
2. **`G1a`/`G1b` were stated in a pooling §2 does not use.** §2 defines the paired median of
   per-pair differences; §3 stated four pooled levels. `DD-P3H-2` records this project
   already getting a **sign flip** from that exact substitution.
3. **`REQ-37` is misclassified as a Must.** It is under `### Expect`. The gate stands on
   `REQ-13` alone — which is a **trend** claim, and therefore licenses the overall test and
   **not** the per-step monotonicity requirement. The statistically risky half of the gate
   was also the half with no requirement anchor.
4. **`G1b` had no branch for its own denominator being unmeasurable.** The ratio↔contrast
   equivalence holds only for `D_A > 0` and nothing tested it. `AM1.5` adds the viability
   clause and a fixed read for the other case.
5. **§0.1 listed the drop payload as held constant.** The *flag* is constant; the *payload*
   is not, and re-censusing moves artists in and out for reasons unrelated to the crawl. The
   intervention is **four** changes, not three. `AM1.8`.
6. **§1 described a build script in the present tense that had never been written.**
   `AM1.12`. Found by trying to run it.

## §4 A claim this session made and then had to correct — in its own amendment

`AM1.10` originally justified per-statistic seeding by asserting a shared `random.Random`
would *"silently change every later interval"*.

**The test written to demonstrate it refused to go red.** At 10,000 replicates the bootstrap
distribution of a median over n≈40 is discrete enough that forward and reverse call order
produce **identical** intervals. The mechanism is real and reappears at ~50 replicates.

**Corrected in the amendment with the measurement beside it, and in the module docstring** —
the second of which was caught only at closeout B4, having been left live after the spec was
fixed. The seed is kept for reproducibility, not because it repairs a defect. The test
asserts **both** halves and fails if either stops holding.

**This is the session's own instance of the failure class the project names most often:
confident prose about correct code.** The code was always fine.

## §5 Gate outcomes

**No `JFX-` gate ran** — no arm was executed. `JFX-G1`, `C1`–`C7` and `M1'` are all unrun.

Closeout gates that did run: `docs-lint` hard checks **passed**; `doc-auditor` dispatched
(B1); mutation checks on both load-bearing invariants went **red then green** (B3); Snyk
**clean** after one LOW was fixed; builder suite **245 passed**; 20 new tests, each shown
red before being kept.

## §6 Corrections to the prior record

- **`PRODUCT-REQUIREMENTS.md` §8's structural conflict is stale as a present-tense claim.**
  Forward correction added; the sentence is struck in place, not deleted.
- **The `MSW-` adoption's recorded grounds are incomplete** (§2 above). Not editable — those
  records are frozen — so the correction lives in `PRODUCT-REQUIREMENTS.md`.
- **Three restatements introduced by this session's own first commit were converted to
  citations at closeout B1**: a config default (`w_known_ramp_fame_pctl`), another
  document's figures (`DD-P3H-2`'s), and the reachability figures the amendment itself
  declared owned elsewhere. The doc-map row carried the same self-contradiction and was
  fixed with them.

## §7 Why this session stopped short of running the arms

**`CLAUDE.md`: *a material mid-flight amendment is also a seam — there is a new governing
document, and the next session reads it cold, which is the condition the amendment was
written for.*** That is exactly this position.

The session that wrote twelve clauses is the worst available reader of whether those clauses
carry their own reasoning. If the amended document cannot brief a cold session, that is
cheaper to discover now than after 300 pairs have been routed on it.

**Recommended: build the routing harness and run the arms in a fresh session.** The owner was
told this is his call and that pressing on is available.

## §8 Operational notes with no other home

- **`GraphStore` does not retain raw fame.** It computes `fame_lb_pctl` at load and discards
  the values, so the harness must parse the APG1 metadata blob for `fame_lb`. The spec's
  *"in-memory `fame_lb_raw`"* names a **builder** field. `AM1.4`.
- **`BuilderConfig.algorithm` defaults to ALG-E while the adopted lineage is ALG-B**, with no
  guard on the build side. The diagnostic script **requires** `--algorithm` rather than
  defaulting it.
- **PowerShell mangles a commit message containing double quotes** when passed as a native
  argument — carried from the previous handoff and hit again. `git commit -F-` with a
  heredoc from Bash works.
- **`cd builder` inside a Bash heredoc script does not persist** the way the surrounding tool
  call's cwd does; two commands failed on `cd: builder: No such file or directory` after an
  earlier `cd` in the same session. Use absolute paths.

## §9 D6 — the standing context layer

Measured against `C:/Users/charl/.claude/projects/C--dev-music-app/memory`.

| Layer | Now | Delta |
|---|---|---|
| **Unconditional** | **45,880 characters** | **0** |
| **Conditional** | **2,475 lines** | **0** |

Previous figures: 45,880 / 2,475 (`2026-08-09-cex-task11-execution-log.md` §9) — **identical,
compared against the recorded numbers rather than inferred from "nothing was touched".**
This session edited no `CLAUDE.md`, no `.claude/` file and no `memory/` file. **Nothing is
owed to the owner on D6.**
