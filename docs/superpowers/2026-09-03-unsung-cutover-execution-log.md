# Execution log — the `unsung.fm` cutover, 2026-09-03

**Role: ACTIVE, and it owns only this session's work.** Infrastructure and documentation. **No
application code, no graph, no cost function, no artifact** — the bytes served are identical
before and after. It states no project status: [`NEXT.md`](NEXT.md) owns that. It owns no
path-quality figures.

Identifiers: none minted. This session cited `DEP-34`, `DEP-34-FIX`, `ARC-6`, `PW-5`–`PW-7`,
`G3-A5` and `DEP-24`, and introduced no new series.

---

## §1 What happened

The app moved from `musicapp.cmiller.io` to `unsung.fm`. The owner bought the domain
(2026-09-02), pointed the nameservers at Cloudflare, and built the Cloudflare side; this
session did the AWS side and the documentation.

Three names now reach the app, all 301, all path-preserving:

| From | Mechanism |
|---|---|
| `musicapp.cmiller.io` | Cloudflare Redirect Rule on the `cmiller.io` zone |
| `www.unsung.fm` | Cloudflare Redirect Rule on the `unsung.fm` zone |
| the generated CloudFront domain | `viewer_function.js`, unchanged behaviour |

## §2 Decisions, with reasoning

**The cutover is one variable, and `cdk diff` proved it.** The diff before deploy showed
exactly three changes: the viewer function's substituted hostname, the distribution's
`Aliases`, and the viewer certificate. **No App Runner diff at all** — which is the positive
evidence that the deploy did not move the image tag or the graph, not merely an absence of
intent to.

**The old name is redirected at Cloudflare, not kept as a second CloudFront alias.** Flipping
`ARTISTPATH_SITE_HOSTNAME` removes the old name from `Aliases`, so CloudFront refuses its TLS
handshake and old links break (observed: 525). Keeping both would need a SAN certificate *and*
a change to `stack.py`, whose `domain_names` is singular — and the viewer function would then
301 to the canonical name anyway. The redirect achieves the same result one hop earlier and
touches no AWS code. Same reasoning applied to `www`.

**Three live documents got a standing note rather than a find-and-replace.** Every occurrence
of the old host in `NEXT.md`, `TEST-QUEUE.md` and `docs/README.md` sits inside a dated
record — a discharged queue entry saying what was pressed and when, a superseded status block,
or a map row describing a frozen handoff. Replacing them would assert the owner tested a
domain that did not exist on the date beside it. The notes tell a cold reader which address is
live and which entries are historical; the records stay as written.

**Deliberately not decided here:** whether the app is *renamed* to "Unsung". Only the address
moved. Recorded in `NEXT.md` as available and unapproved, with what it touches, so no session
reads `unsung.fm` and assumes the rename landed.

## §3 Defects found — one in this session's own work

**Per-deploy inputs were persisted into `infra/.env.deploy`, and that is `ARC-6`/`DEP-34`
again.** The file set neither `ARTISTPATH_DEPLOY_IMAGE_TAG`, `_GRAPH_KEY` nor `_SIDECAR`, all
three of which `app.py` requires, so the cutover needed them. This session wrote them into
`.env.deploy` — where §5 says the tag is *"per-deploy, never persisted"* and §4 exports the
graph pair the same way.

**Why it is a defect and not untidiness:** `_require()` checks only that a variable is *set*.
A persisted value satisfies the guard while naming last month's graph, which converts
`DEP-34`'s loud failure back into the silent revert `DEP-34-FIX` was written to prevent. Caught
by re-reading §5 while fixing §5. Removed, with a comment in their place; the warning is now in
the `DEP-34` block so the next session does not repeat it.

The deploy itself was unaffected — the values were read off the live service and the `cdk diff`
confirmed they reproduced production rather than moving it.

**A second defect in this session's own work, found by `doc-auditor` at B1.** The standing
note added to `NEXT.md` claimed it *"survives a `closeout` rewrite"* — but that document's
Maintenance rule says it is *"rewritten wholesale at `closeout`"* and carried no exception. The
claim was a **directive wearing the clothes of a description**, and the next closeout could
have deleted the block while following the rules as written. The exception is now stated in the
Maintenance rule itself, which is what makes the claim true. Neither this nor §3 was findable
by grep; both are claims that were wrong beside code and rules that were right.

## §4 Corrections to the prior record

**`DEP-34` in `infra/README.md` was stale by four weeks and said the opposite of the truth.**
It described `ARTISTPATH_DEPLOY_GRAPH_KEY` and `_SIDECAR` as defaulting to the pre-`MSW-`
artifact, and stated that making them required was *"deliberately not done here… the owner's
call"*. `DEP-34-FIX` did it on 2026-08-07 (`2930fac`). The block now records it as closed. The
incident narrative is kept, per `CLAUDE.md`: knowing what the guard is for is what makes it
transfer.

**Do not revert:** the `DEP-34` block's status is CLOSED, and the graph variables are
required. A well-meaning editor reading an older handoff could reinstate the defaults.

## §5 Gate outcomes

| Gate | Result |
|---|---|
| `cdk diff` before deploy (README §5) | **Passed** — three expected resources, nothing else |
| `cdk deploy` | **Passed**, 241 s |
| Live verification, all names | **Passed** — 200 on `/`, on a deep `/path/` route and on `/api`; 301 with path *and* query preserved from both redirects |
| `scripts/docs-lint.sh` hard checks | **Passed**, before and after the documentation edits |
| Reference resolution (D4-mt) | **Passed** — every path, commit and section number the diff names resolves |

**No gate failed and none was skipped.** No suite was run: nothing executable changed, so
D4 was discharged as D4-mt.

## §6 Operational measurements with no other home

- `cdk deploy` for an alias-and-certificate change: **241 s**, plus 6 s synth.
- ACM certificate issuance for `unsung.fm` + `www.unsung.fm` (DNS validation, Cloudflare):
  completed within the session, no retry.
- **`localStorage` does not survive the move**, because it is scoped to an origin. Every
  existing user's bypass-explainer dismissal is gone and the explainer reopens once. Expected,
  harmless, and queued in `TEST-QUEUE.md` as *not* a fault so it is not reported as one.

## §7 Deferrals

| Item | Success condition |
|---|---|
| The `musicapp.cmiller.io` certificate, kept unattached as the rollback path | **The owner says the move is settled** — then delete the certificate *and* its validation CNAME together. Recorded at `infra/README.md` §9 |
| Rename the app to "Unsung" | **Owner approval**, plus his two decisions on the landing copy. Recorded in `NEXT.md` |

`G3-A5` was checked and **does not reopen**: it was closed 2026-07-28 on there being a custom
domain at all, and this changes which one.

## §8 The standing context layer (closeout D6)

Measured against `C:\Users\charl\.claude\projects\C--dev-music-app\memory`, the directory this
session's own context names.

| Layer | Now | Previously recorded | Delta |
|---|---|---|---|
| **Unconditional** | **45,854 characters** | 45,854 | **0** |
| **Conditional** | **2,475 lines** | 2,475 | **0** |

**Zero in both.** Nothing in `CLAUDE.md`, the skill or agent descriptions, the memory index or
any memory body was touched. No owner decision is owed on this layer.

`.claude/` was checked for stale deployment descriptions (B5) and contains none — it holds no
hostname or topology claims at all, only permission entries. `CLAUDE.md` names no hostname
either, by design: it points at `NEXT.md` for status.
