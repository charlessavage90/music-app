# Product requirements — Must / Should / Expect

**Role: AUTHORITATIVE for product requirements.** What the app is required to do (Must),
what it should do (Should), and what typical behaviour looks like (Expect). Drafted by the
owner 2026-07-29 and restated with a session the same day; the draft exists because a
value had been conflated in documentation along the way (§10).

**Relationship to [`WHAT-GOOD-LOOKS-LIKE.md`](WHAT-GOOD-LOOKS-LIKE.md) (WGLL).** That
file remains the calibration record: provenance and firmness of each value, the worked
cases, the boilthefrog delineation, and the blind-test protocol with its instrument
bounds all live there and are not restated here. This document is the requirements layer
above it. **Where the two disagree, this document governs**, and every known
disagreement is listed in §10 — a disagreement discovered later gets added there, never
resolved silently.

**No figures here.** Scoring and path-quality figures live in
`findings/2026-07-21-scoring-adjudication.md`; anything quantitative below is cited, and
the few qualitative calibrations ("a handful, not dozens") are deliberately not numbers.

**Identifiers are `REQ-N`**, assigned once in document order, never renumbered, never
reused — including when a statement later changes category. WGLL's value numbers are that
document's identifiers and are cited here as "value N". Open questions carry `REQ-Q`
identifiers so they cannot be mistaken for requirements.

> **Numeric order is a property of the original draft, not a live invariant.** A requirement
> added later takes the **next free number** and sits where it belongs **topically**.
> `REQ-42`, in §8, is the first such addition and the only identifier out of sequence.
> Restoring the run would put a famous-artists clarification under "Testing and evaluation",
> away from the `REQ-35`/`REQ-37` statements it clarifies and the `DD-F1` note it annotates —
> and renumbering to avoid *that* is exactly what "never renumbered" forbids.
> *Added 2026-08-01 after a documentation audit read the rule the other way and called the
> placement a defect. The rule's own category-change clause already rules that reading out:
> a statement that changes category moves while keeping its number, which breaks the run by
> design. The ambiguity was real enough to mislead a careful cold reader, so it is closed
> here rather than left to recur.*

---

## How to read Must / Should / Expect

- **Must** — a requirement. A violation is a defect wherever it appears, regardless of
  the path's other qualities. Criteria and gates may be built on Musts — with their own
  pre-registered thresholds, because this document still sets none.
- **Should** — a preference with force. A violation is a finding to weigh, not
  automatically a defect; a design that routinely violates a Should owes a reason.
- **Expect** — calibration. Descriptions of typical behaviour, used to interpret
  results. **Never optimization targets, never gates, never thresholds.** An Expect
  turning out wrong is information about the world or about our understanding — not, by
  itself, a defect.

Preferences evolve. The update trigger is the same as WGLL's — the owner articulating
something new — and edits here are forward-only, like everything else committed.

## Definitions — the currencies

Reading one of these quantities as another has produced three separate wrong conclusions
on this project (`CLAUDE.md` orient table; Phase 1 log §2.6, §2.11, §2.12). Every
statement in this document is written in exactly one of them, by name.

- **Novelty** — unknown *to the listener*. Per-user and taste-relative, so not directly
  measurable: the only per-user ground truth the app ever receives is a `known` press,
  which is evidence of *non*-novelty for that user.
- **Obscurity / fame** — how widely known an artist is in the world. The adopted proxy
  is English-Wikipedia pageviews, with no-article artists scored at the fame floor
  (`specs/2026-07-23-track2-preregistration.md` §5 and A11). The proxy is blind in the
  modern-obscure tail; the bounded hand-read second opinion (Spotify monthly listeners)
  and its three usage bounds live in WGLL's "How to run the test".
- **Popularity (in-graph)** — `pop_raw`: score-weighted in-degree from the archive,
  log-scaled. **Not fame at the top of the distribution** (Phase 1 log §2.11 — a lo-fi
  producer and a Beatle score alike), and never a percentile (`pop_pctl` is reserved for
  that, §2.12).
- **Hub (structural)** — top-1 %-by-degree (`top1pct_degree_frac`). Degree ≠ fame
  (§2.6). Perceived hub-ness is taste-relative and will not match degree (value 4).
- **Coherence** — each adjacent pair of artists sounds like a plausible next listen, and
  the whole path reads as one journey that fits its endpoints; no step feels like it
  belongs to a different journey. That sentence is a summary: **the governing record of
  what the owner means is his verbatim verdict notes, Phase 1 log §3.9** — start there,
  not from a metric. The two offline metrics built to guard coherence were the worst
  predictors of his verdicts (§3.8); do not proxy coherence with one.

**The operational chain (owner-stated, 2026-07-29): novelty is reached through
obscurity.** The app cannot know which artists are novel to a specific user — the only
per-user signal is the `known` press — so every requirement on novelty below is carried,
operationally, in the **fame currency**: deliver obscure artists, because obscure implies
probably-novel. The chain is one-way: famous does *not* imply known-to-this-listener, so
a famous interior artist can still be a novelty win for a given user — the proxy just
cannot see it, and no requirement counts on it. The coherence Musts are what stop
obscurity being bought by incoherence, the failure mode the owner's own use run measured
(`findings/2026-07-25-bypass-depth-use-run.md` `BYP-11`: genre departure preceding
obscurity).

✅ **REQ-Q1 (RESOLVED 2026-07-29, owner ruling): discovery payload is scored in
fame.** Value 1's degree-based count (non-hub interiors) is retained as a **secondary
diagnostic only** — never a criterion — because it catches the one failure fame cannot
see: an obscure structural connector the router over-uses. Conditions on any
fame-currency payload criterion, fixed with the ruling: (a) always reported twice — all
interiors and matched-only, the DD-D8 shape, so the fame-floor mass is visible rather
than absorbed; (b) the A11 notability guard must be read by the scorer; (c) mbid-keyed,
frozen snapshots only. **Offline scoring and live telemetry deliberately use different
currencies:** telemetry stays in artifact currencies (popularity/degree), because the
pageview proxy is too weak at the obscure end to commit production monitoring to —
revisit only if a fame source with genuine per-mbid coverage appears. The offline↔live
currency gap is accepted and remains unmeasured (DD-D6).

---

## 1. Core path properties

### Must
- **REQ-1** — Every path is **coherent** end-to-end, per the definition above.
- **REQ-2** — Every card is a real, named artist. No invalid or non-artist nodes (the
  nameless-node drop decision in `NEXT.md` is the live instance of this requirement).
- **REQ-3** — The start and end artists are **fixed anchors**: never bypassed, never
  excluded.
- **REQ-4** — A "no path" result may only ever arise from the user's own exclusions,
  never from missing graph structure. (Implementation: the largest-connected-component
  prune, `CLAUDE.md` "Graph shape".)

### Should
- **REQ-5** — Paths maintain **local smoothness**: each step feels similar to the
  previous one.
- **REQ-6** — Paths avoid repeated reliance on the same structural role — e.g. routing
  through hub after hub.

### Expect
- **REQ-7** — First paths often include well-known artists, especially between popular
  endpoints. This is correct behaviour, not a failure (§8).
- **REQ-8** — Some hubs appear naturally; a hub is not inherently a failure (§5).

## 2. Discovery and novelty

### Must
- **REQ-9** — Novelty is delivered **through** coherence, never at its expense. An
  incoherent path is always worse, however novel (value 8; its worked case — a coherent
  10-artist path with one famous middle beating 8 obscure artists that do not transition
  — lives there).

### Should
- **REQ-10** — Stronger paths deliver **more obscure interior artists**; delivered
  discovery is the key signal for judging bypass behaviour. (Currency: fame — but see
  REQ-Q1 before building any scored criterion on this.)

### Expect
- **REQ-11** — A longer path can beat a shorter one if it delivers more discovery
  (value 1; its worked case lives there).
- **REQ-12** — Occasional well-known artists are acceptable inside otherwise strong
  paths.

## 3. Bypass behaviour

### Must
- **REQ-13** — Repeated bypasses **must increase delivered novelty** (fame currency:
  interiors trend more obscure). A press that swaps one famous artist for another
  equally famous one has delivered nothing.
- **REQ-14** — Lengthening is **not a goal** of bypass, and no bypass mechanism may
  treat added length as its objective. Length changes are side-effects of holding
  coherence while obscurity increases (REQ-19). **Supersedes value 2's "both, or
  neither counts" — see §10.**
- **REQ-15** — On long paths, **sustained confinement** is a defect: several
  consecutive presses whose changes stay inside the same group of nodes. One or two
  local deviations are not "swapping" and are correct behaviour (value 7, including its
  long-path qualifier — this applies to long paths, where local accommodation is
  possible at all).

### Should
- **REQ-16** — Changes begin locally and propagate as presses continue (long paths;
  value 7).
- **REQ-17** — Default behaviour is tuned for typical interaction depths. Long bypass
  sequences — dozens of presses — are test instruments and stress cases, not use cases,
  and should not shape defaults.

### Expect
- **REQ-18** — Novelty emerges within **a handful of presses, not dozens**, under
  typical conditions. Calibration, never a target: nothing may optimize toward a press
  count. Popular endpoints take more presses to reach it; lesser-known endpoints fewer.
- **REQ-19** — Paths tend to **lengthen over repeated bypasses as a side-effect** of
  holding coherence at increasing obscurity — expected, not required, and not a goal.

## 4. Path length and attention

### Should
- **REQ-20** — Paths stay within a **practical attention limit**: at some point a
  journey stops feeling like a journey. The ceiling is real but **unquantified and
  user-dependent** — discover it by use (`TEST-QUEUE.md`), and build no guard or
  criterion on it until it is known (value 3).
- **REQ-21** — Length increases buy something: more discovery, while staying coherent.

### Expect
- **REQ-22** — Lengthening under bypass is gradual. A path roughly doubling over a
  session of presses is unremarkable; runaway growth — an order of magnitude — would be
  a problem, but nothing close has ever been observed, and no guard is required.
- **REQ-23** — Paths composed of highly obscure artists are likely **longer on
  average** than paths between highly popular artists, to maintain coherence.
  *Suspicion, owner-stated 2026-07-29 — gut instinct, not a statement of fact, and
  untested.*

## 5. Hubs

### Should
- **REQ-24** — Evaluation treats a hub as **a slot that delivered nothing** — a missed
  discovery opportunity, never an accumulating penalty. A longer path carrying more
  hubs can still be clearly better if it delivers more novel artists — bounded by
  REQ-9: the comparison is between coherent paths (value 1; its worked case lives
  there).
- **REQ-25** — Structural tracking uses the degree proxy (`top1pct_degree_frac`),
  while remembering it is a proxy.

### Expect
- **REQ-26** — Perceived hub-ness will not align with graph degree, and is
  taste-dependent (value 4 — the Vulfpeck case lives there).

## 6. The `known` signal

### Must
- **REQ-27** — `known` routes to an artist that is **highly similar** to the bypassed
  artist **and more obscure** than it. A famous-for-famous substitution is a defect
  (value 5's observed case lives there). *Promoted from value 5's calibration bound to
  a requirement — owner confirmed 2026-07-29; see §10.*

### Should
- **REQ-28** — Direct 1:1 substitution is an occasional outcome, not the mechanism.
  When it happens, REQ-27's more-obscure bound still applies.

### Expect
- **REQ-29** — Occasional direct substitutions will occur, and are tolerable within
  REQ-27's bound.

## 7. The `dislike` signal

### Must
- **REQ-30** — `dislike` steers **away from the stylistic neighbourhood** of the
  disliked artist — it must not merely substitute a near-identical act.

### Should
- **REQ-31** — 1:1 swaps on `dislike` are rare — materially rarer than on `known`,
  where they are occasionally fine (value 6).

### Expect
- **REQ-32** — `dislike` and `known` produce observably different behaviour; the two
  signals are different mechanisms, not two buttons on one reroll.

## 8. Famous artists

### Must
- **REQ-33** — The system must **not eliminate famous artists**. Reducing their
  frequency is the live problem; a router where they never appear is an over-correction
  (value 9).

### Should
- **REQ-34** — On the **first path**, fame tracks the endpoints: two popular artists
  give a mostly popular first path, two obscure ones a mostly obscure path (value 9,
  endpoint-tracking clause — verified against the reference product, `BTF-2`).
- **REQ-35** — Obscurity is carried by **bypass depth**, not by initial routing.

### Expect
- **REQ-36** — First paths between popular endpoints skew popular.
- **REQ-37** — Repeated bypasses produce progressively more obscure paths **while
  staying coherent**, for any artist pair.

### Should
- **REQ-42** — **The obscurity requirement is a GRADIENT and sets no absolute floor.**
  Owner clarification, 2026-08-01. The goal is artists that are **novel to the user**;
  novelty is not measurable per-user (see Definitions), so obscurity is the **best
  available proxy** — and a proxy for *whether the user is likely to know them*, not a
  target depth. **"We need to deliver the bottom 10% of the graph" is not the
  requirement and never was.** What is required is that **obscurity increases as the
  bypass count increases, and that generally any two starting endpoints can achieve
  that.** Consistent with REQ-13, REQ-35 and REQ-37, all of which are trend statements;
  this entry exists because the trend was repeatedly operationalised as a floor
  downstream, and a citable statement is what stops that recurring.

  **Consequence, not resolved here:** any read that scored obscurity by *reaching a
  fixed band* — rather than by movement with bypass depth — is affected, whatever its
  own bars said. Two live instances at the time of writing: the `DD-F1` framing
  annotated immediately below, and the `TAS-` probe's routing guard, whose "zero
  bottom-decile artists mid-journey" was written up on 2026-08-01 as the sharpest
  corroboration of the defect. Under this entry that reading **overstates it** — the
  absence of a band is not itself a failure if the trend holds. Re-reading either is
  the owner's call, not automatic.

⚠ **Known structural conflict, recorded 2026-07-29:** on the current artifact,
superstar endpoints have zero edges below the top popularity decile
(`2026-07-28-track3-depth-descent-execution-log.md` `DD-F1` — figures owned there), so
REQ-37 is currently **unachievable on famous-to-famous pairs at any router setting**.

> **⚠ Read the decile in that sentence as an OPERATIONALISATION, not the requirement
> (REQ-42, 2026-08-01).** The requirement is the trend; "below the top popularity decile"
> is one way a session made it measurable, and it hardened into the goal itself in
> documents downstream. **The defect ruling below is unaffected and stands** — what a
> famous-to-famous pair cannot do is move *at all*, and a gradient of zero fails REQ-13
> and REQ-37 without any reference to a band. The decile is how the zero was found, not
> what makes it a defect.
Resolving that is a graph-construction question and an owner decision; this document
states the requirement, not the remedy.
**Ruled 2026-07-29: this is a defect, not an accepted limitation.** Most user-entered
endpoints are at the famous end, so this pair class carries the app's implied promise —
corroborated by early friends-and-family feedback ("I must choose bands that have a lot
of listeners in common because most of the pathways have been bands I know"). The remedy
is graph-side by necessity; its design and cost are unstarted and separately decided.

## 9. Testing and evaluation

### Must
- **REQ-38** — Blind listening is the **primary evaluation method**, and offline
  metrics must not override listener judgment (Phase 1 log §3.8 is the standing
  evidence for why).

### Should
- **REQ-39** — Tests exercise **bypass interactions**, not just first paths — bypass is
  what discriminated the arms when first paths looked alike.
- **REQ-40** — Evaluations are framed as **specific claims** the owner can push on,
  never open-ended questions.

### Expect
- **REQ-41** — Results vary with listener familiarity. "No difference" in unfamiliar
  territory is **uninformative**, not evidence of equivalence.

Protocol detail — the blind-test rules, the Spotify monthly-listeners instrument and
its three bounds, and the specific-claim rationale — lives in WGLL's "How to run the
test" and is not restated here.

## 10. Where this document supersedes WGLL

Listed exhaustively; anything not listed is consistent, and WGLL remains governing for
provenance, worked cases, and protocol.

1. **Value 2's "lengthen AND increase novelty — both, or neither counts" is
   superseded** by REQ-13 / REQ-14 / REQ-19. The owner states (2026-07-29) that the
   both-or-neither framing was a conflation introduced during documentation: the
   requirement is that bypass increases novelty; lengthening is an expected
   side-effect of holding coherence at increasing obscurity, never a goal. The rest of
   value 2 — a bypass that swaps famous-for-famous without surfacing anything new is
   the failure — stands as REQ-13.
   **Consequence, not resolved here:** any read that treated failure-to-lengthen as a
   failed half of value 2 is affected. The live instance is Track 3's verdict
   (`NEXT.md`), whose fixed wording rests the trade on value 2's lengthening half.
   Re-reading that verdict under this document is the owner's call, not automatic.
2. **Value 5 is promoted from calibration bound to requirement** (REQ-27) — owner
   confirmed 2026-07-29. The famous-for-famous defect reading is unchanged; what
   changes is its force: it may now back criteria and gates.
