# `CXR-` execution log — the extended map was reverted, 2026-09-01

**Role: RETAINED REASONING for the revert and the diagnosis that followed.** What was
decided, why, and what was checked rather than assumed. **It owns no status** (`NEXT.md`)
and **no figures** — those live in
[`builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md`](../../builder/analysis/2026-09-01-cxr-regression-diagnosis/README.md),
cited by name, never restated.

Branch `crawl-extension-design`, **PR #91** — the same PR that carries the adoption, so one
PR tells the whole story: crawled, measured, adopted, deployed, **reverted**, diagnosed.

---

## §1 What the owner decided, and it was his own criterion coming back

He reported the extended map *"noticeably worse than the old version — it's much harder to
find unknown artists."* Asked where it goes wrong, he answered that comparing single first
journeys is weak evidence — **"there's only one data point per artist pair, and
'unfamiliarity' is not a precise measurement"** — that he thinks it is **worse on both**, and
that **the digging is where it is noticeable**.

That is the revert criterion he set on 2026-08-10, before adoption, quoted in
`TEST-QUEUE.md`: *"a noticeably worse product experience on more than half of tested
journeys, where 'noticeably worse' means how hard it is to find novel artists."*

**He was given the options and chose: revert now, diagnose after.** The revert is his call
because adoption is — the left column of `CLAUDE.md`'s table. **The diagnosis, its method
and its scope were mine and were not put to him.**

## §2 The revert, and what was verified rather than assumed

Graph-only. **No image rebuild**, because the frontend and API code were not implicated and
rebuilding would have made the map not the only variable.

- **`cdk diff` read before deploying, per `DEP-34`.** It showed **exactly three** things:
  `ARTISTPATH_GRAPH`, `ARTISTPATH_GRAPH_SHA256`, and the IAM object-read statement following
  the key. **`.ImageIdentifier` did not appear**, which is the evidence that only the map
  moved.
- **`--require-approval never` was passed deliberately**, and this is the second time it is
  worth flagging rather than treating as routine: the IAM statement is scoped to the object
  key, so **every graph swap moves IAM and every graph swap will therefore prompt**. stdin is
  null here and the prompt would hang. The delta was displayed to the owner in full before
  the deploy. It is a key swap, not a widening of privilege.
- **The sha came from the sidecar via `_sidecar_sha256()`, not from a human** (`DEP-24`).
- **Verified live from outside, not inferred:** `/health` on the App Runner origin reports
  the previous map's node and edge counts and sha; a journey built through the public address
  returns Radiohead → U2 → Nine Inch Nails. `DEP-34`'s warning applies — the `/health` check
  compares the service against whichever sidecar it is handed, so a wholesale revert is
  self-consistent and would pass either way. **What makes this check real is that the counts
  are the OLD map's**, and they are not a value this session supplied to anything.

**Deploy time 185 s.** The clip cache was **not** cleared: clips resolve per artist and the
old map's artists are a subset of the new one's, so every cached entry is still correct for
the artist it names.

## §3 Where the record was, and the thing a reader must not trip on

**PR #91 was never merged.** The extended map ran in production for three weeks off an image
built from an **unmerged branch**, while `main` still described — and still defaulted to —
the old map. So `main` was accidentally *correct* about what is live from 2026-09-01, and
was wrong about it for the three weeks before.

**This is why the revert went onto the adoption's own branch rather than a fresh one off
`main`.** A branch off `main` would have had to describe a revert of something `main` has no
record of. Merging PR #91 now lands both halves together and leaves the trunk consistent with
production.

**⚠ It also means the "adopted" state was never on `main` to go stale.** A future session
should not read that as a design: it was a gap. Production ran unmerged code for three weeks.

## §4 The diagnosis, and the prediction I got backwards

**`PREDICTIONS.md` was committed before any figure existed** (`09a5656`), naming the
threshold that would decide each prediction and what each result would rule out. Two of three
fired; **the one I expected to refute is the one that fired hardest**, and recording that is
the point of committing predictions at all.

- **`CXR-P2` — confirmed, as expected.** The added artists are structurally peripheral.
- **`CXR-P1` — confirmed, and I predicted it REFUTED.** I expected the newly crawled artists
  to have no ListenBrainz listener counts, which would have made the fame ruler immovable.
  **They have them at 99.89 %.** The ruler moved for essentially everyone.
- **`CXR-P3` — did not fire**, and it is the one that would have explained the half of his
  report about the *first* journey. **That half is unexplained and is recorded as
  unexplained** in the figures README, in `NEXT.md` and in the discharged queue entry. It
  would have been easy to let `P1` and `P2` stand in for the whole complaint.

**The generalisable finding, and it is a trap set for every future map switch:** the fame
ruler is framed on **the served artifact's own population** — deliberately, and the docstring
argues the case well. The consequence nobody had drawn is that **growing the map reprices
every artist already in it**, and does so unevenly, because artists near the top of the scale
have nowhere to rise. A map switch is therefore never a "more artists, same routing" change,
whatever the node-set arithmetic says.

## §5 What was NOT done, and deliberately

- **No fix.** Three candidates are visible from the figures and **each needs its own
  pre-registration**. Resuming path-quality work is the owner's trigger.
- **No re-crawl, no rebuild, no bounds change.** The acceptance bounds are untouched: they
  did their job. `graph-cxa-adopted.bin` passed them, and **the bounds were never a quality
  test** — they separate a healthy build from a broken one.
- **`w_known_ramp_fame_pctl` untouched**, in either direction. Moving it in the same release
  as the revert would confound the confirmation test.
- **The `CEX-` crawl extension is not reverted.** The archive, the re-censused payload and
  the fourth acceptance artifact all stand. What was rejected is building the served map from
  that archive **as it stands** — which is a statement about mutual k-NN over a thin crawl,
  not about the crawl being wasted.
- **The routing harness was not re-run.** Establishing that the extended map routes to its own
  new artists less often costs ~2.6 h and would not have changed today's decision, which was
  already taken.

## §6 An observation about this file's siblings, offered not acted on

**`NEXT.md` is 166 KB and `TEST-QUEUE.md` is 109 KB.** `NEXT.md` says of itself that it is
"short by design" and "rewritten wholesale, not appended to", and it now carries roughly
thirty superseded blocks in a stack. That is a real drift between what the document says it
is and what it is, and it is the kind of thing that makes a cold read expensive.

**Not fixed here**, because it is unrelated to the revert and compressing a live status
document is exactly the operation `CLAUDE.md` warns costs the clause that made a check usable.
Named so it is on the board.

## §7 Verification

- **`api` 261 passed, `infra` 66 passed, `builder` 246 passed.** The `api` run includes the
  updated default-artifact pin, which now asserts `graph-msw-tu50.bin`.
- **The pin was not merely edited to match.** It is the guard added after `MSW-` found nothing
  to update, and it is the reason a reverted default cannot silently disagree with production.
  Its comment now warns the next editor that this slot has moved **backwards** once, so
  "update the pin to the newer artifact" is not automatically right.
- **Frontend untouched**, so its suite was not run: no frontend file is in this change.

## §8 Security

No first-party source was added beyond two analysis scripts that read local files and print
numbers (`cxr_census.py`, `cxr_compression.py`). No dependency, lockfile, endpoint or
credential path was touched. **One credential did pass through this session's tooling** — the
App Runner environment listing includes `ARTISTPATH_ORIGIN_SECRET`, and the deploy sources
`infra/.env.deploy`. Neither value was printed into any document, commit or report; the
runbook's §5 warning about credentials in deploy output is the standing rule and it held.
