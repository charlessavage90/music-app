# Execution log — the bypass tray, the landing page, and `DEP-34-FIX`, 2026-08-07

**Role: COMPLETE.** The reasoning behind the `2026-08-07` UX track. Figures are cited,
never restated. Handoff: [`2026-08-07-HANDOFF-bypass-tray-ux.md`](2026-08-07-HANDOFF-bypass-tray-ux.md).

**This track shipped to production.** Frontend only, plus one infrastructure guard. No
graph, no artifact, no cost function, no router. Branch `bypass-tray-ux`, **PR #89 MERGED**
at `a7a8b9a`; deployed the same day.

---

## §1 — What this was

The owner supplied a Claude Design project ("Artist Path landing screen", three files) and
chose its **2c variant — "footer bar into a tray"** for the journey cards. The design export
is committed at `frontend/design/2026-08-07-bypass-tray/` per `UI-1`. Two of its three files
(`browser-window.jsx`, `support.js`) are canvas scaffolding — a mock Chrome frame and the
`x-dc` template runtime — and are **not implementable**; only `Artist Path.dc.html` carries
design content.

The work then grew by four owner requests, each after pressing the previous build: a copy
pass, clip-length and rebuild feedback, the landing fields and sample journeys, and finally
`DEP-34-FIX` plus the deploy.

## §2 — Decisions taken, with reasoning

### §2.1 — The trigger wording departs from the design, and the design argued the case

The design drew the strip as **"Not this step"**. The owner flagged it. Reading the export
confirmed the objection and supplied the reason: the design's **own 1b variant** is annotated
*"the strongest cure for the swap misread"* — for the phrase **"Rebuild from here"** — and
its Turn 1 header states that both actions rebuild the whole path, which is why red-vs-green
was dropped. *"Not **this step**"* is singular and rejecting, i.e. the precise misread the
redesign exists to cure. That reasoning never travelled into the chosen 2c variant.

Shipped after the owner's copy pass as **"Reroute from here"**, tray heading **"How should
this change?"**.

### §2.2 — The design left three gaps; none was a wording choice

1. **The expanded tray had no way out.** Both the 2c card and the journey mockup draw an
   open tray with no close affordance. Resolved as one control that relabels — strip when
   shut, tray heading when open — so `aria-expanded` is truthful and the tray closes.
2. **The landing page never said the app is for finding unfamiliar music.** Owner-raised.
3. **The design re-added the clip-length footer line**, which `LandingPage.tsx` records the
   owner having removed on 2026-07-28. **Asked rather than reverted; he confirmed it stays
   out.** A design canvas is not authority over a decision the repo already records.

### §2.3 — Rebuild feedback is on two clocks, and the message was never the defect

The owner reported that a fast rebuild showed no confirmation. **The initial diagnosis
offered to him was wrong and he corrected it**: the reroll message has been specific per
signal since `UI-D5` and always was. The defect was that it was bound to the *request's*
lifetime — `PathPage` cleared it the moment a path landed — so an 80 ms rebuild displayed
good writing for 80 ms. Same shape as the 2026-08-02 report about the first-load screen
("often too fast to see").

`useRerollFeedback` splits it: the notice is held a minimum (`NOTICE_MIN_MS`), and the
artists **not on the previous path** are ringed afterwards (`GLOW_MS`). The hold is a floor
on *reading time*, not a delay — the path underneath has already arrived — and a slow
rebuild is not padded. The glow costs no latency because it fires after render.

### §2.4 — The landing fields were built from the wrong token family

They used `--color-surface` on `--color-border`: the tokens for a **recessed** surface. The
one control the landing page exists to get a user into was styled to sit *in* the page. The
mockup had specified otherwise and the 2026-07-28 port did not carry it across. Three new
tokens take the mockup's own values; the coloured dot per field is likewise a port of
something drawn and never built.

### §2.5 — The sample journeys are hardcoded MBIDs, and that is a standing liability

Owner-chosen pairs. All six artists were confirmed present in the served artifact and all
three pairs confirmed to build a natural path **before** the code was written.

> **⚠ This depends on the SERVED ARTIFACT and no test can protect it.** MBIDs are stable in
> MusicBrainz, so the risk is not that one changes — it is that a future artifact **drops**
> an artist, after which that card lands on the not-found page. The committed fixtures are
> 500-node samples containing none of the six. **Re-check after any graph adoption.**
> Recorded at the call site in `LandingPage.tsx`; success condition in §5.

### §2.6 — `DEP-34-FIX` required fixing both variables, not one

`ARTISTPATH_DEPLOY_GRAPH_KEY` **and** `ARTISTPATH_DEPLOY_SIDECAR` both defaulted to the
pre-`MSW-` artifact. What made it lethal rather than loud is that **the two defaults agree
with each other**: the key names the old artifact and the sidecar carries the old artifact's
checksum, so a reverted service boots, matches its own sidecar, and passes every downstream
check. Requiring only the key would have relocated the silent revert into the checksum.

`QUA-10` recorded that `infra/app.py` had no test at all. It has three now. The third is a
grep asserting the retired artifact's name appears in no live code — **the shape that would
actually have caught this, because a default is invisible to every test that supplies the
variable.**

## §3 — Defects found in this session's own work

Recorded because they are the transferable part.

### §3.1 — A stranded notice, found by writing the test rather than the code

Clearing the notice was first keyed on the artist list. A rebuild returning an **identical
path** therefore changed nothing the effect depended on, it never re-ran, and the message
would sit over a dimmed path **forever**. Reachable in the app by pressing *Reset path* on an
already-original path. Fixed by separating the two concerns into two effects; the notice's
lifetime now depends on request status only. Pinned by a named regression test.

### §3.2 — An e2e spec whose wait depended on text being absent elsewhere

`path.spec.ts` used `getByText('Miles Davis')` as its wait for navigation off the landing
page. That worked only while the landing page never mentioned him — which a sample journey
now does. The assertion began passing **instantly against the page the spec was trying to
leave**, and the next line raced an empty list. *An implicit wait that depends on text being
absent somewhere else is not a wait.*

### §3.3 — The same defect class, reintroduced hours later, in a throwaway script

**This is the one worth carrying.** Having fixed §3.2 and written a comment naming the
pattern, the session then used a fixed `waitForTimeout(2500)` in a *disposable* live-site
check, read the DOM before the re-render landed, and **reported a false claim about the
product to the owner** — that a single `known` press had left the path unchanged.

It then compounded it: it supplied a plausible *mechanism* (the depth-graduated fame ramp),
which is real but irrelevant, because `pathfinding.py`'s hard exclusion settles the outcome
before the ramp is consulted. **A plausible explanation attached to a bad measurement is what
makes a wrong claim durable.** The owner's disbelief is what caught it.

Resolved by two independent checks against production — the API directly, and the UI waiting
on the outcome rather than a stopwatch. **The app was correct throughout; only the report was
wrong.** Lesson: a discarded verification script got less rigour than a committed one, and
its output was handed over with equal confidence.

### §3.4 — A browser claim asserted without testing

A CSS comment asserted that "a keyframe cannot resolve a custom property through a colour-mix
at every step in Safari 17". **Never tested.** Caught at closeout B4 and rewritten to state
what is actually known — the token is opaque hex, these stops need alpha, and the literal
sidesteps the question rather than answering it.

## §4 — Gate outcomes

| Gate | Outcome |
|---|---|
| Four mandatory suites (`infra/README.md` §7) | **Passed**, run twice — on the branch and again on `main` before deploying |
| `docs-lint.sh` hard checks | **Passed** |
| Snyk Code, `frontend/src` | **Clean, 0 issues** |
| Snyk Code, `infra` | 3 LOW, **all pre-existing** — verified by scanning `main`'s own `app.py` and getting the identical three |
| `npx snyk test` (frontend deps) | **DID NOT RUN** — org monthly limit reached. Not a pass. See §5. |
| `cdk diff` before deploy | **Not applicable** — frontend-only deploy runs `infra/README.md` §6, no CloudFormation change |
| Drift detection | **DRIFTED, 6 rows. Five are the documented non-drift; the sixth is real.** See §5. |
| Deploy verification (§8) | **Passed** — including a before/after `/health` comparison, which is stronger than the sidecar check the runbook itself flags as weak |

**B3 mutation testing:** two invariants deliberately broken (`NOTICE_MIN_MS` → 0; the tray's
`trayOpen` guard removed) and each produced exactly the targeted failure. The three
`DEP-34-FIX` tests were likewise shown red against the reinstated defaults **before being
kept**.

## §5 — Deferred, each with a success condition

| Item | Condition |
|---|---|
| **`SNS-1` — the billing alarm has no subscriber.** `AlarmTopic` reports **zero** subscriptions; the CDK-created email subscription is gone, almost certainly never confirmed and expired. If the billing alarm fires, nobody is told. Pre-existing; **not caused by this deploy**, which touched no CloudFormation. | **Owner's call, and it is his because it needs his inbox.** Discharged when a subscription exists and is confirmed. `DEP-17` records App Runner billing as unmeasured, so this alarm is the only thing watching cost. |
| **`SMP-1` — the three sample-journey MBID pairs.** §2.5. | **Re-check after any graph adoption**, before that artifact serves. Discharged per adoption, not once. No test can cover it. |
| **`FE-SNYK-1` — the frontend dependency scan did not run.** | Discharged by a successful `npx snyk test` once the org's quota resets. **Mitigation, not a pass:** no dependency manifest changed on this branch — `package-lock.json` and every Python lockfile are byte-identical to `main` — so the last passing scan covers exactly this dependency set. |

**Conditions re-tested this closeout, not copied forward:** `ULF-3` remains **HALF-DUE**
(era-pinned probes still name the old flags; all three flags still live in `BuilderConfig`) —
unchanged by this track, which touched no builder code. `CLIP-1` remains open and untouched.

## §6 — Operational measurements with no other home

- **Deploy shape:** frontend-only, `infra/README.md` §6. No image build, no `cdk deploy`.
  `--prune` deliberately off (`FRO-1`).
- **Bundle identity:** production moved from `index-BLZUsNpG.js` to **`index-Bh6px0BI.js`**,
  captured before and after rather than inferred.
- **Graph identity across the deploy:** `/health` **byte-identical** before and after. This
  is stronger evidence than §8's sidecar check, which the runbook itself notes compares
  against whichever sidecar you hand it and so cannot see a wholesale revert.
- **Live browser verification:** zero console errors; a sample journey and the tray both
  exercised on production.
- **Drift rows:** 6. The env-var row was confirmed to be `ARTISTPATH_CORS_ORIGINS` **by
  name**, not by index — the runbook warns the index moves, and it has moved to 5.

## §7 — Corrections to the prior record

- **`DEP-34-FIX` is CLOSED.** `NEXT.md` and the previous handoff carried it as open and as
  the owner's. It is done, tested, and on `main`.
- **Both live `TEST-QUEUE.md` entries are DISCHARGED**, and the queue is empty. The owner
  reported the `MSW-` map fully exercised on desktop and mobile with no defects or
  regressions, and the artwork fix confirmed. **This is the first evidence of any kind that
  the `MSW-` map holds up in real use by a person** — and it does **not** retrospectively
  license the `GBL-` null, which that adoption overrode knowingly.
- **A new standing rule in `TEST-QUEUE.md`, from an owner ruling:** the queue is for defects
  and functionality only, **never** for long-run judgement of how the app feels. Such an
  entry has no completion state, so it could never be discharged.

## §8 — Closeout record, 2026-08-07

**Tier: full ritual.** A multi-commit track with a production deploy and an infrastructure
change is not a small self-contained one.

**D6 — standing context layer**, measured against
`~/.claude/projects/C--dev-music-app/memory`:

| Layer | Value | Delta |
|---|---|---|
| Unconditional | **45,902 characters** | **0** — `CLAUDE.md` untouched, no skill or agent `description:` line changed |
| Conditional | **2,465 lines** | **0** — one line replaced by one line in `.claude/skills/closeout/SKILL.md` |

That single skill edit is a **correction, not growth**: its worked example told a future
session to write *"press know them already"* into a test-queue entry, naming a button this
track removed. D6's table puts a false-about-the-world correction at net-zero size in the
session's hands, which is what this was.

> **A near-miss worth recording.** The first D6 measurement used `git diff main...HEAD`, which
> reported the `.claude/` change as **empty** — because the closeout's own edits were still
> uncommitted. Taken at face value it would have recorded a false "nothing touched". The
> unconditional number was unaffected (that command reads the working tree directly), but the
> conditional one would have been wrong. **Measure the working tree, or measure after
> committing — not `main...HEAD` mid-closeout.**

**D2 — committed fixtures:** not applicable and stated rather than omitted. This track changed
no graph and no artifact, so `tests/fixtures/*.bin` in both packages are untouched and
un-stale.

**D3 — provenance for what cannot be committed:** no artifact was adopted, built or compared.
The two identities that matter for this track and exist nowhere in git are recorded in §6 —
the production bundle hash before and after, and the live graph `sha256` captured **before and
after the deploy** to prove it did not move.

**B3 — mutation testing outcomes:** `NOTICE_MIN_MS` → 0 failed exactly *"the message outlives
a rebuild that answered faster than it can be read"*; removing the tray's `trayOpen` guard
failed exactly *"the tray is shut until the strip is pressed"*. Neither test is vacuous.

**B1 — audit outcome:** hard lint checks passed; the `doc-auditor` returned **no high-severity
defects in scope** and one MEDIUM outside it — `frontend/README.md` describing the bypass
controls by their old labels. It correctly declined to guess whether that file documents UI or
wire contract. Adjudicated from the record and fixed in both places, differently:
`frontend/README.md` describes the **UI** and now describes the strip and tray;
`api/README.md` documents the **wire codes**, which never changed, and now says so explicitly
so the next relabelling does not drag the codes with it.

> **B5 gap, found by the auditor rather than by me.** My own B5 sweep covered `docs/` and
> `.claude/` — the two the check names — and missed the **package READMEs**, which are exactly
> the "descriptions elsewhere" the check exists for. The sweep was run to the letter and still
> had a hole.
