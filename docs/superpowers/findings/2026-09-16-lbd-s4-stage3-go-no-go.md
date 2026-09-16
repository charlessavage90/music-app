# `LBD-S4` — the go/no-go stop, and what the numbers do and do not settle

**Role: ACTIVE — the owner-facing note for the `LBD-S4` adoption stop.** It **owns no figures**:
every quantity is owned by
[`builder/analysis/2026-09-14-lbd-s4-stage3/README.md`](../../../builder/analysis/2026-09-14-lbd-s4-stage3/README.md)
and is **cited by section, never restated**. Stage 1's and stage 2's figures are their own READMEs'.
Reasoning is [`../2026-09-15-lbd-s4-stage3-execution-log.md`](../2026-09-15-lbd-s4-stage3-execution-log.md).

**Governing:** [`../specs/2026-09-14-lbd-s4-adoption-preregistration.md`](../specs/2026-09-14-lbd-s4-adoption-preregistration.md)
(`LBA-`), including §11's `LBA-AM1`, `LBA-AM2` and `LBA-AM3`. Where this note and it disagree, **it
governs and this note is wrong.**

> **The stop is the owner's. Nothing here recommends a route, selects an arm or prefers a strength
> threshold** — `LBA-D2` reserves that to him with the numbers in front of him, and `LBA-D3` bars
> designing any listen before he rules.

---

## 1. The question, and where it now stands

> **Is a map built from our own recomputation of ListenBrainz's raw listening data worth shipping
> — at what population of artists, and at what strength bar — given what it costs to run?**

Three quantities, one decision. **All three have now been measured as far as the design admits**,
and one of them — playability — could not be measured at all, for a reason that is a fact about
the census rather than about any map.

**Stage 2 already removed cost from the decision.** `LBA-G1` (*this map is too big, or too slow,
for the machine the app runs on*) fired on nothing across the eight sized arms, which is
`LBA-R1`, read there. Stage 3 confirms the operating side: the fame fetch is small and resumable on
every arm (stage-3 README §4). **What the decision actually rests on is §1–§3 of that README.**

---

## 2. What the numbers say, in plain terms

Each claim below is **inference**, labelled as such, and each points at the section that owns its
figures. **They are written so that they can be argued with without knowing what any statistic
measures.**

**The strength bar almost only ever adds.** Comparing two of our own maps that differ *only* in how
much listening evidence a connection needs, the looser one keeps essentially all of the tighter
one's similar-artist lists and puts extra artists in — it does not swap anybody out. §1c. This was
genuinely open before: the nesting was known at the pair-table level, and whether our degree ceiling
would undo it in the built map had never been measured.

**Where the bar does matter is the artists who arrived almost unconnected** — the group this whole
line of work exists to help. Their dead-end share falls substantially as the bar loosens, and about
three times faster than it does for the artists the app already served. §2a, §2b.

**A wider population changes what the app shows you more than the bar does.** Roughly a quarter of
the artists the app can reach today would have a substantially different set of similar artists
under *any* of these maps, and going wider pushes that up by several points rather than a little.
§1a. And **it is not that the wider maps could not find the old neighbours** — they are choosing
differently, not being forced to. §1b.

**The least-listened artists absorb most of the disruption, at both ends.** They are both the most
likely to disappear from a map entirely and the most likely to have their neighbour list
rearranged. §1d.

**The widest option reaches an enormous number of very thin artists**, about a quarter of whom have
two or fewer connections. §2c.

**We cannot say how playable the artists a wider map adds would be.** That is §3, and §4 of this
note is about why.

---

## 3. The three things that cut against the above, stated here rather than in a footnote

**None of this has been heard.** `REQ-38` makes the blind listening test the **primary** evaluation
method and says offline metrics must not override listener judgment. Everything in §2 is an offline
metric. `REQ-41` additionally bars reading any *absence* of difference as equivalence.

**Playability is estimated on every arm, and its gate is disqualified on every arm where it could
have been read.** `LBA-G3` (*working out which artists are unplayable would take too long*) fired at
stage 1, so no census pass ran. Stage 3 then found that the disqualifier `LBA-AM3-2` fixed — before
any provenance mix had been looked at — fires everywhere, at many times its bar, and that **the
cause is structural**: under the two censuses that exist, the artists a map *adds* and the artists
it *keeps* can never have been evaluated at the same time. Stage-3 README §3b.

**This is the clearest return the pre-registration discipline has paid in this track.** Without
`LBA-AM3-2`, the numbers as they stand would have been read as the playability gate **firing
decisively** on the widest population — and a provenance difference alone could have produced that.
**Neither "the artists a wider map adds are much less playable" nor "they are fine" is licensed.**

**Two of the design's own reads are formally unreachable, and one of them is the owner's exit.**
`LBA-R8` and `LBA-R9` presuppose a census that did not run (`LBA-AM3-1`). **`LBA-R9` is the row that
reads *the numbers say no* and that records stopping the track here as a complete outcome rather
than an abandonment.** The design as executed cannot hand it over licensed. **Stopping remains a
perfectly good decision; what is missing is the design's own certificate for it.**

---

## 4. One branch this design cannot decide, and it is not a result — it is a gap

**`LBA-R6` and `LBA-R7` differ only in whether a wider population changes what the app shows
substantially. Neither read carries an effect size for that half, and `LBA-M2` carries none by
design** — §4 of the pre-registration fixes it as descriptive precisely because *what counts as too
much change* is a product judgment.

**So a session choosing between those two reads would be fixing a threshold with results in hand**,
which is the one thing a pre-registration exists to prevent. Both halves' figures are reported side
by side in stage-3 README §6 and **the branch is the owner's**. It always was; the design simply
did not say so.

`CLAUDE.md`'s rule names this shape directly — *every gate and branch trigger needs its own effect
size* — and this is a branch with none. **Recorded as a defect in the design, not in the result**,
and it failed in the safe direction.

---

## 5. The options, and what each commits to

They are laid out with their consequences in stage-3 README §9 and are not duplicated here. In
shape: **stop**; **go over today's artists**; **go over the deeper crawl's artists**; **go over
everyone in the listening data** (whose corner cell is unbuilt for a resource reason, so that row is
reported with a hole in it); or **buy one more measurement first**, of which two are cheap and both
are already deferral rows in `NEXT.md`.

**What "go" commits to is already fixed and is not reopened here**: §8 of the pre-registration —
a candidate build with fame and clip ids, acceptance criteria never widened from
`PRODUCTION_ACCEPTANCE`'s intent, manifest pinning, **and then the `REQ-38` blind listen, designed
cold as a separate amendment written when no journey exists on either map.**

⚠ **A candidate at any population above today's will breach the node acceptance bound by
construction. That breach is a decision, not a bug, and it is the owner's** — his ruling of
2026-09-05.

---

## 6. Barred reads, carried forward

Every one of these is inherited and binds whatever stage 3 measured.

- **No equivalence from either blind listen.** Both `LBL-` listens read the tie; `REQ-41` makes
  *"no difference"* in unfamiliar territory **uninformative**, not evidence of equivalence. Both
  verdicts are **run-once and final** and neither may be re-listened on any protocol.
- **`LBD-X6` stands.** Its condition was discharged on 2026-09-13 and `R10` **fired**, which
  **confirmed** the bar rather than lifting it. Reading the met condition as a lifted bar inverts
  the result.
- **No attribution inside the data bundle** (`LBA-X4`) and **`LBA-X5` travels with every comparison
  against today's map.**
- **`LBD-C1` is never cited as passed**, for `LBD-A0` or `LBD-A4`; whether `LBD-AM3`'s override
  extends to `LBD-A4` is open and the owner's. **Every arm here inherits whatever the
  reimplementation gets wrong that the synthetic sub-check cannot see.**
- **No routing or path-quality claim** beyond the query cost stage 2 measured. A denser map is not a
  better journey until a listener says so.
- **`LBA-A9`'s three barred conclusions** (stage-3 README §0c) — in particular, ***"we could not
  build it here" and "it is too big to serve" are different claims.***
- **The unlicensed sensitivity in stage-3 README §6a makes nothing reachable** and is not a finding.
