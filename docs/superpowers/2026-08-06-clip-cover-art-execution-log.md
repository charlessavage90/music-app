# Execution log — the clip cover-art defect, and `DEP-34`, 2026-08-06

**Role: RETAINED EXECUTION LOG.** Owns the reasoning for the cover-art fix and the deploy
defect it uncovered. **Owns no status** — `NEXT.md` owns that. **Owns no scoring figures.**
The measurement figures below have no other home (they are properties of a third-party API
and of the shipped artifact's id coverage, not path-quality figures), so they live here and
are cited from elsewhere, never restated.

Branch `clip-cover-art-fix`, **PR #85 MERGED 2026-08-06** at `fee46e2`. Commits `641ced7`
(fix), `9183893` (runbook) and `a3a5217` (closeout).

---

## 1. What was reported, and what it actually was

The owner reported album art loading **inconsistently** on the live site, with clips playing
fine. Both halves of that sentence were accurate and the second is what made it diagnosable:
a clip and its image come from the same response, so "audio yes, image no" localises the fault
to the parse rather than to the fetch.

**Root cause.** `ClipResolver._from_deezer_artist` read the card image from
`row["artist"]["picture_medium"]`. Deezer embeds **a different artist object per endpoint**:

| endpoint | keys on the embedded `artist` object |
|---|---|
| `/search` | `id, name, link, picture, picture_small, picture_medium, picture_big, picture_xl, tracklist, type` |
| `/artist/{id}/top` | `id, name, tracklist, type` |

So the id path always produced `cover_url == ""` and the name path always produced an image.
The card rendered a blank square while the clip played perfectly.

**Why it shipped on 2026-08-06 and not on 2026-08-02**, when the id path was written: the
path only fires for artists carrying a `deezer_id`, and those travel inside the artifact.
`graph-msw-tu50.bin` is the first shipped artifact to carry them. **The defect was authored
in one track and detonated by an unrelated one** — which is why nothing in the `MSW-` work
looked wrong and nothing in the `BYP-13` work was recently touched.

## 2. Measured (against the live catalogues, not fixtures)

| | |
|---|---|
| `picture_medium` present on `/artist/{id}/top` | **0 of 110** sampled artists |
| artists in `graph-msw-tu50.bin` carrying a Deezer id | 32,492 / 58,838 (55.2%) |
| id lookup resolves — 60 random id-carriers | 55 (91.7%) |
| id lookup resolves — 50 popular id-carriers (top decile by `pop_raw`) | 49 (98.0%) |
| steady-state share of **all** artists with no image | ~50.6% |
| steady-state share of **popular** artists with no image | ~88.6% |

**"Steady state" means after the 30-day clip cache drains**, and that distinction is the
whole of why the fault looked intermittent rather than total — see §3.

⚠ **The popular-sample figure uses `pop_raw`, which is score-weighted in-degree** — a proxy
for what routing favours, not a measurement of impressions. Read it as "most well-known
artists", never as a precise impression rate. Sample sizes are 60 and 50 at one seed; the
direction is solid and the second decimal is not.

## 3. Four causes of the intermittency, and only one is the bug

This is the part worth carrying. A user seeing some cards with art and some without is
observing **four** different mechanisms, none visible from the browser:

1. Artists with **no recorded id** (44.8%) take the name path and keep an image.
2. Artists whose recorded id is a **dead or duplicate Deezer page** fall back to the name
   path and keep an image. Radiohead is one: its recorded id `323887691` returns zero
   tracks — the empty-duplicate hazard already recorded in the 2026-08-02 test-queue entry.
3. Artists **cached before the map switch** are served an old identity, image included, for
   up to the 30-day TTL.
4. Everyone else — working id, first resolved since the switch — has **no image**.

**Only (4) is the defect.** (1) and (2) are the fallback working. (3) is a cache doing its
job. The population moves from mostly-(3) to mostly-(4) over 30 days, so the fault was
**getting worse on its own** and would have looked like a slow regression with no commit
behind it.

## 4. The fix, and why the alternative was declined

Read `album.cover_medium`, which is present on **both** Deezer responses.

- **No extra request.** The block is already in the response. An `/artist/{id}` lookup for
  the photograph would double outbound calls on the id path, in a module whose whole design
  is shaped by not amplifying against a rate-limiting service (`G3-A4`).
- **It makes all three paths agree.** iTunes already returned album art (`artworkUrl100`),
  so the resolver had been mixing artist photographs and album covers with nothing saying so.

**Visible consequence, and it is a product change, not a repair:** Deezer-resolved cards now
show an album cover rather than an artist photograph. Raised with the owner as his call
before implementation; he chose it.

## 5. Why 254 passing tests could not see a live defect

**The fixtures invented the response shape.** Both `test_clip_identity.py` and
`test_clips.py` put `picture_medium` on responses Deezer does not send it on. The module's own
docstring had predicted exactly this for exactly these endpoints — *"the tests inject a fake
fetcher, so a wrong field name here would pass every test and produce a silent card"* — and
the prediction was correct and unheeded.

Both fixtures are now transcribed from live responses. The new `test_clip_cover_art.py`
carries **no picture key on its `/top` fixture deliberately**, with a comment saying that
restoring one re-blinds the suite.

**A near-miss worth recording precisely, because the obvious reading of it is wrong.**
`2026-08-04-gbl-harness-execution-log.md` §2 records a fixture/parser divergence over this
exact pair of fields, resolved by moving the fixture to `artist.picture_medium`. That
reconciliation was **correct for that harness**, which calls `_from_deezer` — the search path,
where the key genuinely is present. It was not a missed catch. What nobody did, then or
since, was ask whether the *other* endpoint carried the same key. **The transferable form: a
fixture reconciled against one call site is evidence about that call site only.**

## 6. `DEP-34` — the deploy would have silently reverted the map

**Found by running `cdk diff` before `cdk deploy`, and nothing else would have found it.**

`ARTISTPATH_DEPLOY_GRAPH_KEY` defaults to `graph-t15-tiebreakfix.bin`, the pre-`MSW-`
artifact. `.env.deploy` does not set it, and it is per-deploy rather than per-machine. So an
**API-only deploy that forgets it also rolls the graph back** — reverting an adoption made the
previous day, from a session that had no intention of touching it.

**This is `ARC-6` one variable over.** The image tag had the identical defect (defaulted to
`latest`), was caught the same way on 2026-07-27, and was fixed by making it *required*.
`ARTISTPATH_DEPLOY_GRAPH_KEY` was left defaulted five lines below in the same file.

**Why nothing downstream catches it.** §8's verification compares `/health` against
*whichever sidecar it is handed*. Hand it the sidecar the deploy just used and a wholesale
artifact revert is perfectly self-consistent and **passes**. It detects a partial upload —
what it was written for — and not the wrong artifact. That limit is now stated at the check.

**Fixed at the documentation level only** (§1 warning block, §4 `GRAPH` variable, §5 mandatory
`cdk diff`, §0 and §8 de-hardcoded). **The stronger fix — making both variables required in
`infra/app.py`, as `ARC-6` did — is NOT done**: it changes deploy behaviour and is the owner's
call. Deferred with a condition in §8.

## 7. Decided against

- **A second Deezer request for the artist photograph.** Preserves today's look; doubles
  outbound calls on the id path. Declined on `G3-A4` grounds.
- **Waiting out the 30-day TTL instead of clearing the cache.** Would have left the reported
  symptom in place for a month while the fix sat in production doing almost nothing.
- **Clearing the whole clip table.** The 8 iTunes entries were already correct under both old
  and new code; re-fetching them buys nothing and spends rate limit.
- **Making `ARTISTPATH_DEPLOY_GRAPH_KEY` required in `app.py`** — right fix, wrong session.
  See §6 and §8.

## 8. Deferred, with conditions

| item | condition |
|---|---|
| **`DEP-34-FIX`** — make `ARTISTPATH_DEPLOY_GRAPH_KEY` and `ARTISTPATH_DEPLOY_SIDECAR` required in `infra/app.py`, per `ARC-6` | **Owner's call, and it should be taken before the next artifact adoption.** Until then the runbook is the mitigation and is weaker: it depends on the operator reading a diff. Discharged when `app.py` calls `_require` for both, or when the owner declines and the decision is recorded here. |
| **`CLIP-1`** — a clip can be the right artist and still misrepresent them | Unchanged by this work, still the owner's call. Owned by `2026-08-05-msw-execution-log.md`. **Not** what this track fixed, and the two must not be conflated: `CLIP-1` is about *which track*, this was about *which image*. |

## 9. Operational record

- **Deployed** `artistpath-api:641ced7`, digest `sha256:99fe1bae9db0661247ceba9f7ca0d9df9e490f5b4f3535d0852bd9189572dd12`.
- **Graph unchanged and verified after deploy:** sha256
  `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8`, 58,838 artists,
  1,315,684 edges — all three matched the sidecar mechanically, not by eye (`DEP-24`).
- **Clip cache:** 404 Deezer entries deleted after the image was live, 8 iTunes entries kept.
  Order matters — clearing before the deploy repopulates under the old code.
- **Post-deploy verification on the live site:** Dolly Parton → Aphex Twin and Miles Davis →
  Slipknot, at 0 / 10 / 20 `known` presses. 6 and 8 cards respectively; **every card resolved
  a clip and an image at every depth.**
- Deploy took 169 s. Image build ~40 s.

## 10. Check outcomes (closeout)

- **B3 found a real weakness in this session's own test.**
  `test_both_deezer_paths_agree_on_the_image` survived two mutations, because "both paths
  equally broken" still agrees — which is precisely the production failure. A non-empty
  assertion was added and the mutation now goes red. **Agreement assertions need an absolute
  companion; on their own they are satisfied by uniform breakage.**
- **B5** found three frozen documents describing the old `picture_medium` behaviour
  (`plans/2026-07-20-path-engine-api.md`, `findings/2026-07-23-track2-protocol-analyst-review.md`,
  `2026-08-04-gbl-harness-execution-log.md`). **None edited** — all are COMPLETE or RETAINED
  and accurate as history. The correction lives here.
- **B1:** `docs-lint` hard checks passed; the `CAND` figure lines are the pre-existing
  false-positive class (config weights like `0.01`/`0.10` matching adjudication decimals) and
  none is from this session. The `doc-auditor` returned **one MEDIUM**, fixed here: the
  2026-08-06 `TEST-QUEUE.md` DONE marker still said the two local servers "are still up" in
  the present tense, when they were stopped at `76d3b82`. Struck in place, not deleted.
- **D6: no standing-layer change in either direction.** `CLAUDE.md`, `.claude/` and `memory/`
  were untouched. Totals for the next session to diff against: **unconditional 45,902
  characters**, **conditional 2,465 lines**, measured against
  `~/.claude/projects/C--dev-music-app/memory`.
- Builder 225, api 261, frontend 107 — all green. Snyk: one pre-existing LOW in
  `test_origin_secret.py`, untouched by this work.
