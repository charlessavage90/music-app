# What good looks like — calibration for the blind listening test

**Role: ACTIVE, standing.** Update it whenever the owner articulates something new about
what a good path is — usually a blind test, but direct articulation counts too (values 8
and 9 came that way).

The blind listening test is this project's strongest evidence class. It decided the graph
twice, where the offline metrics decided it zero times, and it works because it converts a
question the owner cannot audit (graph structure) into one he can (does this feel right).

**This file is that instrument's calibration record.** Without it, every session
interpreting a verdict re-derives what the owner meant from scratch, and gets it slightly
differently each time.

**It records preference, not evidence.** These are things the owner values, some of them
explicitly flagged by him as gut instinct. They are not criteria, and a change does not
"pass" by matching them. Use them to *interpret a verdict*, never to predict one.

No figures here — they live in `findings/2026-07-21-scoring-adjudication.md`.

---

## What the owner values

**1. Hubs are slots that failed to deliver, not costs that accumulate.**
The product delivers artists the listener does not already know. A hub is not a penalty —
it is a step that delivered nothing. So a longer path carrying more hubs can still be
clearly better, if it carries more novel artists — **bounded by 8: the comparison is
between paths that are both coherent, and this value is not a licence to buy novelty with
incoherence.** The owner's worked case: an 11-artist
path with 4 hubs beats a 4-artist path with 3 hubs, because it delivers 7 novel artists
against 1. This is why the bypass metric is **discovery payload** (absolute count of
non-hub interior artists), with `top1pct_degree_frac` (named `hubfrac` before the
2026-07-23 currency rename; see `builder/analysis/README.md`) as a scale-invariant
companion — see the roadmap's Phase 1 carry-ins.
*Firm. Owner-stated and reasoned, 2026-07-22.*

**2. Bypass should progressively lengthen the path AND increase novelty — both, or
neither counts.**
The first path is expected to route through well-known artists; that is not the failure.
The failure is a bypass that swaps one well-known artist for another without lengthening
or surfacing anything new. Length alone is not the goal — a path that lengthens while
carrying the same or more hubs is a worse result, not a better one. Reference product:
boilthefrog.
*Firm as intent. The owner flagged it himself as gut instinct rather than data-driven
(execution log §16). Bypass telemetry is what would test it.*

**3. Path length has a ceiling set by attention, not by graph structure.**
At some point a journey stops feeling like a journey. No offline metric will find that
boundary, and it is not currently known.
*Unquantified. Discover by use; belongs in `TEST-QUEUE.md`.*

**4. Perceived hub-ness is taste-relative and will not match degree.**
The owner called Vulfpeck a hub; it is almost certainly outside the top 1 % by degree,
which is how `top1pct_degree_frac` defines one. Offline measurement can only ever have the structural
proxy. This is one reason metrics and ear disagreed throughout Phase 2 — they were not
measuring the same object.
*Observation, one instance. Telemetry measures the real thing.*

**5. `known` should route to an artist highly similar to K but *more obscure*.**
"I know The Beatles, give me a Beatles-like act I haven't heard." The load-bearing word
is *more obscure*: an occasional 1:1 swap on `known` is an acceptable outcome **only when
the substitute is less famous than the artist bypassed.** A famous-for-famous swap
(the owner's observed case: Bowie → Pink Floyd → Beatles) is not. This is not an
endorsement of 1:1 swapping as the `known` mechanism — it is a bound on when the swap
outcome is tolerable.
*Owner-stated, 2026-07-23, from live use. The `known` semantic itself is his firm
specification (Phase 1 log §3.4); the less-famous bound is the calibration for judging it.*

**6. `dislike` should 1:1-swap much less often than `known`.**
The two signals are meant to behave differently — `dislike` steers around a stylistic
neighbourhood, `known` seeks a more-obscure cousin — so a bare one-for-one substitution
is a stronger sign of failure on `dislike` than on `known`, where it is occasionally fine
(see 5).
*Owner-stated, 2026-07-23. Preference, not a threshold.*

**7. On a long path, a local bypass deviation is correct; sustained confinement is the
defect.**
When a path is long (>~9), a single bypass sometimes changes only a few nodes near the
bypass point. That is the *expected* behaviour — the path deviates locally to accommodate
one rejection. It becomes a defect only if **several bypasses in a row** keep the changes
confined to the same group of nodes. One or two local deviations are not "swapping."
*Owner-stated, 2026-07-23, and gut-checked against use: he saw the acceptable form this
session and did not see the defect form — local deviations resolved into larger changes
within a further bypass or two.*

**8. Novelty is delivered *through* coherence, not traded against it.**
The unknown artists are the deliverable, but they have to arrive in a way that feels
natural to the listener. The owner's worked case: a 10-artist path that routes cleanly
from A to B with one very well-known artist in the middle is a good path, and it beats 8
obscure artists that do not transition into one another or fit the endpoints. So value 1
compares *coherent* paths; stated without that bound it is an overstatement. The record
agrees: coherence decided nearly every selection in the blind listens, and the two offline
metrics built to guard it (AA, overlap coefficient) were the **worst** predictors of the
owner's verdict — Phase 1 log §3.8, restated in its §4. His §3.9 verbatim verdict notes
are the only description anywhere of what he means by coherent; start there, not from a
metric.
*Owner-stated, 2026-07-24, correcting a restatement of value 1 that had dropped the bound.*

**9. Reducing famous artists is the live problem; eliminating them would be an
over-correction.**
Much of development targets how often well-known artists appear and still does. What is
*not* wanted is a router where they never appear. Part of why the reference product
(boilthefrog) felt good is that **fame tracked the endpoints**: two very popular artists
gave a mostly popular first path, two obscure ones a mostly obscure path. The mechanism
that is meant to carry obscurity is the **bypass** — the more bypasses, the more obscure
the path becomes *while staying coherent*, and the ideal router does that reliably for any
artist pair. Extends value 2, which covers only the famous-endpoint first path, and bounds
it in the other direction.
*Owner-stated, 2026-07-24. His characterisation of boilthefrog; not independently verified
against the article.*

---

## How to run the test, calibrated

- **Exercise bypass, not just first paths.** In the Phase 2 adoption test the arms looked
  similar on three no-bypass comparisons, and bypass is what discriminated them. A blind
  test that only compares first paths may find nothing when a real difference exists.
- **Known limit: the owner can only judge regions of music he knows.** He said so directly
  — obscure artists he does not know are hard to evaluate, and some he does know are
  missing from the graph entirely. Treat "no difference" in unfamiliar territory as
  *uninformative*, not as evidence of equivalence.
- **Where that limit bites there is a cheap second opinion: Spotify monthly listeners, read
  by hand.** The owner has premium access. For a handful of artists at a time — usually "is
  this `known` substitute really *less famous* than the artist it replaced" (value 5) — it
  separates **obscure** from **famous-but-not-to-him**, a distinction neither he nor in-graph
  popularity can make (Phase 1 log §2.11: at the top, a lo-fi producer and a Beatle score
  alike). It **complements rather than duplicates** the adopted fame proxy — English-Wikipedia
  pageviews, with an artist who has no English article scored at the fame floor
  (`specs/2026-07-23-track2-preregistration.md` §5 and A11) — which is blind to the
  modern-obscure tail, exactly where streaming activity is strongest. The two fail in opposite
  directions, which is what makes the second look informative rather than merely noisier.
  - **This is not the eliminated external-popularity source** of
    `findings/2026-07-19-listenbrainz-probe.md` §6d–6f. That elimination is about attaching an
    outside catalogue's figures to graph nodes wholesale and silently; at two artists by hand
    you *see* a miss instead of absorbing it. Monthly listeners is also **not in the Spotify
    Web API** — it is a figure shown in the client only — so hand-reading is the only route,
    and the practice cannot scale into a proxy by accident.
  - **Three bounds.** **Never during a blind listen** — it is an information channel the
    protocol excludes, and the record already carries one path comparison voided for less
    (`2026-07-25-HANDOFF-track2f-and-headroom.md` §7). **Never inside a scored criterion or a
    pre-registered read** without its own falsification test, which is a proxy change through
    the back door. And **write down any check that changed your mind** — an informal look that
    later moves a decision and left no trace is unauditable.
  - *Instrument, not preference. It settles a fact; it never says what good looks like.
    Capability noted 2026-07-25.*
- **Ask a specific claim, do not ask an open question.** The articulation above came from
  the owner correcting concrete wrong claims, not from being asked what he wanted.
  Proposing a specific answer and letting him push on it works; "what makes a path good?"
  produces generic answers.
