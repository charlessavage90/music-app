# Execution log — per-archive drop lists, identity-based clip resolution, and a cleanup pass, 2026-08-02

**Role: COMPLETE.** The retained reasoning for the session named
`drop-list-per-archive-builder`. It owns **no status** — that is [`NEXT.md`](NEXT.md) — and
**no figures**: the Deezer coverage and link-quality numbers live in
`builder/analysis/2026-08-02-dsp-ids/` (`dsp_ids.json`, `delivered_coverage.json`,
`id_quality.json`) and are cited here, never restated.

Five commits, one merged PR (#64) and one open (#65).

---

## §1 What the session was asked to do, and what it actually did

It opened to close one small blocking item and ended up doing five things. The owner
directed each turn; nothing below was self-assigned.

1. **The one-list-any-archive hazard** — closed, merged as part of PR #64.
2. **`BYP-13`, clip resolution by artist identity** — built, PR #65, open.
3. **The test queue** — discharged by the owner, and it falsified a Gate 3 blocker.
4. **`REQ-38`** — converted from an open question to a deferral with a condition.
5. **The `--prune` publish pass and the unaccounted Snyk MEDIUM** — both closed.

---

## §2 The drop-list selector, and why no config field was added

The builder applied the 2026-08-01 production list to whichever archive it was handed. The
fix selects by `config.algorithm`.

**The reasoning that mattered: a build's algorithm already IS its archive identity.**
`build_from_archive` uses `config.algorithm` to choose which archive sub-tree to read, so no
new `BuilderConfig` field was needed. That was not merely tidy — a new field would have
tripped PR #63's mirrors guard and forced a per-mirror review for a distinction the pipeline
already draws.

**Refuse rather than borrow, and the refusal is conditional on the flag.** Four of the six
permitted algorithms have never been censused. `NoDropListForAlgorithm` is fatal, but only
when `drop_no_release_tail` is on — which is what keeps `grt_score.py` and `calibrate.py`
working, since they build uncensused populations with the flag off deliberately. That case
is now pinned by a test rather than left to luck.

**The row understated the defect.** `NEXT.md` said the production list "covers only ~a third
of the candidate population". Measured: the lists share 2,712 MBIDs, so applying today's to
an `ALG-B` build would have dropped 4,323 artists the rule keeps *and* missed 6,789 it
drops. Corrected in place.

**Landed on PR #64 rather than a fresh branch, deliberately.** The fix consumes the census
output that existed only on that branch, and merging them together means `main` never has a
state where the candidate list exists but the builder half-applies it.

---

## §3 `BYP-13` — the decision to build it, and the shape it took

**The owner proposed it and was right that it was cheap.** The id path was not new:
`tail_clips.py:137` `id_path()` already asked Deezer for a specific artist's top track with
no name matching. This session promoted its input into the artifact.

**The measurement that justified it, and the reframe that made it convincing.** Population
coverage is unimpressive; coverage over *card impressions the app actually delivers* is not,
because routing skews famous. Figures: `dsp_ids.json` and `delivered_coverage.json`.

> **The uncomfortable corollary, recorded because it will matter later:** the fix works this
> well *because* of `DD-F1` — the defect the project is trying to fix elsewhere. If journeys
> are ever pushed more obscure, this coverage decays exactly as it becomes more necessary.
> Same shape as `FPC-9`, and it should be treated as the same class rather than a coincidence.

**Delivery mechanism was the owner's call: the APG1 metadata blob, not a sidecar.** His
sequencing argument, and it is the right one — a rebuild is needed for the cap re-evaluation
regardless, and doing the format change *now* keeps it out of that pre-registration's factor
table as a mid-flight amendment. **That window closes when the pre-registration is
committed.**

I raised one argument against it and he overruled it after considering it: option 2 couples
the fix to a rebuild that is inevitable but unscheduled, so the live defect persists until
then. Recorded because a successor should not re-open it as though it were unexamined.

### §3.1 Two constraints that shaped the implementation

Both are invisible when broken, which is why they are here rather than only in comments.

- **`FORMAT_VERSION` is NOT bumped, and `serialise` omits the key when empty.** Both parsers
  check the version for strict equality, so bumping stops every existing artifact loading —
  starting with the one the app serves. Omission additionally keeps frozen-mirror artifacts
  byte-identical, whose shas Track B's identity gate pins. **This is the divergence class PR
  #63 closed, arriving from the other direction**, and it is the reason the key is
  conditional rather than always written.
- **`build_graph` gained a keyword-optional parameter only.** `cb_build_variants.py:479` and
  `measure_headroom.py:151` are frozen and call it with three positional arguments. `ALG-B`
  also stays at `PERMITTED_ALGORITHMS[1]`, which every frozen probe indexes.

### §3.2 Deezer only, and one map for any archive

**Apple ids are measured and not shipped.** They add little over Deezer alone on delivered
impressions, and the Apple-id-to-iTunes path has never been run here. Shipping unproven data
nothing consumes taxes every build and every boot.

**One map for any archive is correct here, and it is NOT the drop-list mistake repeated.** A
drop list encodes a *decision about a population*; a Deezer id is a *property of an artist*.
The failure modes differ in the way that matters: a missing id degrades to name search, a
wrong drop list silently removes the wrong artists. **This fails safe; that failed silent.**
Recorded because the surface similarity is high and a successor will notice it.

---

## §4 Corrections to the prior record

**Four, and the first is mine.**

- **"Strictly better than today by construction" is WITHDRAWN.** I told the owner that before
  measuring. The id path substitutes MusicBrainz's link accuracy for Deezer's search ranking,
  and MusicBrainz sometimes links a duplicate page. Evidence and the two hand-checked cases:
  `id_quality.json`. The net remains clearly positive; the claim of guaranteed direction does
  not survive.
- **`NEXT.md`'s `w_degree_hub` claim was misleading and is corrected.** The row said the term
  "is dormant *because of the current graph's top-degree set*", which reads as the `w_floor`
  dormant-term confound about to repeat. Checked from source: the weight is `0.0` and the
  term is a plain multiplication with no env override, so **it cannot self-activate**. What
  survives is a *decision* a rebuild pre-registration should take deliberately, not a control
  it must design. This one matters because it would have caused a successor to build
  machinery against a confound that cannot occur.
- **`REQ-38` was misread as a debt.** Read from source it says blind listening is the
  *primary evaluation method* — a rule about how a judgment is made when one is being made,
  not an obligation every graph change incurs. See §6.
- **The one-list row understated the magnitude.** §2.

---

## §5 Defects found, and how each was caught

Recorded because the *mechanism* of catching generalises, not the defects.

- **My own extraction missed the `www.` strip** that the reference implementation
  (`tail_signals.py`) has, so Deezer coverage came back as **exactly zero**. Caught by the
  number being implausible, not by any test. A zero that looked merely disappointing rather
  than impossible would have killed the idea.
- **Four recorded Deezer links end in a name slug, not a numeric id.** Deezer's artist
  endpoint would 404 on them. Caught by a test asserting every shipped id is numeric,
  **written before the data was frozen**. Discarding them also let two artists' second,
  numeric link through.
- **The endpoint could pass the wrong node's id and every test still passed.** Found by
  mutation, not by review. That is precisely where an off-by-one would hand one artist's card
  another artist's clip — this feature's own failure mode by a different route. `test_app.py`
  gained the case that kills it.
- **My first `CatalogueUnavailable` test was wrong about the code.** A generic exception is
  treated as "no answer" and correctly falls through to name search; only a real refusal
  skips Deezer. Fixing the test surfaced a case worth having: a **stale id 404s and degrades
  to name search**, which is the "fails safe" claim in `deezer_ids.py` now pinned by a test.

**Defect in this closeout's own inputs:** two figures cited in four places
(`NEXT.md`, PR #65, a module docstring, a test docstring) had **no committed home** — they
lived only in a scratchpad. Found by A1 asking for measurements with no other home. Both are
now committed under `builder/analysis/2026-08-02-dsp-ids/`.

---

## §6 `REQ-38` — the owner's argument, and why it stands

He argued the isolating blind listen is not worth running. **His decisive point: every
outcome leads to the same place** — a pass adopts, a failure would still not revert to
delivering release-less artists, only change the exclusion mechanism. A test whose branches
share a direction is not informing a decision.

**Corroborating evidence he did not cite:** `TAS-` measured zero bottom-decile interior
artists across 120 journeys, and the release-less tail sits overwhelmingly in that region, so
the dropped artists were largely never delivered. The audible effect is second-order.

**The one real cost, named rather than dismissed:** if the cap re-evaluation yields a
rebuild, the drop is permanently confounded with the cap change and only the combined result
is ever heard. That is why the option is *preserved* rather than closed — and the instrument
already is preserved, because `drop_no_release_tail` exists as an experimental control.
Deferring costs no future capability.

---

## §7 Gate outcomes

- **`G3-F2` is FALSIFIED.** HIGH, "blocking if confirmed" in the Gate 2→3 review, which named
  the deciding test. The owner ran it: clips play on a real iPhone.
- **⚠ What it does not license, and this is the part that will be misread.** The code was not
  changed to achieve it — `usePlayer.ts:49` still awaits the URL before `player.play(url)` at
  line 60, exactly the pattern the review flagged. The finding's *description* was accurate;
  only its *consequence* is removed. This is evidence about iOS's current tolerance, not
  proof the play path is correct by construction.
- **The rest of the blocking set is untouched.** Gate 3 stays NOT OPEN.
- **No gate failed and none was worked around.** Nothing in this session was gated.

---

## §8 The Snyk MEDIUM splits in two, and Snyk reports it as one

Its message names both hazards ("vulnerable to XXE and DDOS") and they do not have the same
answer. **Tested on the actual interpreter rather than argued from the rule's title:**

- **XXE — not applicable.** An external entity pointing at a local file is refused outright
  (`ParseError: undefined entity`). The cited **CWE-611 is unreachable**, consistent with the
  rule's own "Python < 3.11" scope against this project's `>= 3.12`.
- **Entity expansion — reachable.** An 11-level billion-laughs shape expanded, so the DoS
  half is real in principle.

**Deliberately not fixed.** The remedy is a new dependency, and editing a frozen probe would
fire the "13 pre-existing findings" row's own reopen condition. Residual exposure is the same
argument the Lows were accepted on. **Accepting it is the owner's**, and it is recorded as
such rather than assumed.

**Generalises:** a finding's *title* is not its scope. Two hazards under one rule id needed
two separate answers, and reading only the title would have closed the row wrongly in the
permissive direction.

---

## §9 Operational, with no other home

- **Full graph build with the drop rule live: 433 s**, 67,039 artists, 824,610 edges, 13.9 MB.
  (Earlier logs record ~30 s and ~78 s builds; those predate the drop step and a slower disk
  state. Recorded so nobody treats 433 s as a regression without checking what changed.)
- **MB artist dump scan: ~2 min** over 16 GB / 2,945,470 rows, offline. Three runs this
  session; adopted-population figures reproduced exactly across the last two, which is the
  consistency check that adding the candidate population perturbed nothing.
- **`--prune` pre-flight that made it safe, and a successor must repeat it:** `--skip-build`
  publishes `frontend/dist` *as it stands*, so a stale `dist/` would prune the assets the
  **live** page names — `FRO-1` with the safety off, and the flag's help text does not say so.
  Verified `dist/index.html` referenced exactly the live page's two hashed assets, then dry-ran
  the delete. Two orphans removed; bucket now 7 objects.
### Artifact provenance (D3) — these are gitignored, so a checksum is their only identity

| Artifact | sha256 | Role here |
|---|---|---|
| `graph-t15-tiebreakfix.bin` | `4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8` | The **adopted** graph. Population for the id map; substrate for the delivered-coverage routing. Verified at every probe entry. |
| `graph-algb-full.bin` | `d008a2b5e0c23cf31b3f12357fa1fccff55d209ec18f54c872cdae9bf4a0757f` | The `ALG-B` candidate, 68,467 artists, built 2026-07-30, **pre-drop** — hence a superset of any final `ALG-B` build, which is what makes it safe for an id map. Manifest-verified before use and now pinned in `dsp_ids.py`. |
| `graph-deezerid-verify.bin` | *not recorded — built, verified, deleted* | A throwaway post-drop build used once to prove the ids survive a real build end to end (67,039 artists, 52.0% carrying an id). **Deliberately not kept**: it is not adopted, nothing points at it, and leaving an unowned `.bin` in `scratch/` is how the "several graphs, not interchangeable" hazard grows. `id_quality.py` needs it, which is why that script's dependency is called out in the handoff. |

### The standing context layer (D6)

**Unconditional 44,183 → 44,245 characters (+62).** Two false-by-omission statements
corrected in `CLAUDE.md`: the APG1 metadata enumeration omitted `deezer_ids`, and the clip
section omitted the id-before-name order. Per D6's table these are corrections, not growth —
a true statement replacing a false one, no new rule or narrative. **A first attempt came in at
+271 and was trimmed**: it carried an explanatory `BYP-13` clause, which is new narrative and
therefore the owner's call, not a session's.

**Conditional 2,154 → 2,154 lines (0).** `ml-graph-analyst.md` carried the same incomplete
APG1 enumeration and was corrected in place at no net cost.

---

## §10 What a successor must not undo

1. **`FORMAT_VERSION` stays at 1 and the key stays conditional.** Both have reasons that are
   invisible from the code alone; §3.1.
2. **`build_graph`'s new parameter stays keyword-optional.** Two frozen probes.
3. **The probe mirrors still must not gain the drop step**, and they did not gain the id step
   either — they never call either.
4. **"Strictly better by construction" must not reappear.** §4.
5. **The `w_degree_hub` correction must not be reverted** to the confound framing. §4.
6. **`REQ-38` must not be restored as a debt.** §6.
