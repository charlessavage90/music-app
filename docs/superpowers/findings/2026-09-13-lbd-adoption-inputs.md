# `S4` adoption inputs — the owner's three points, and the record beside each

**Role: ACTIVE — an `S4` input; owns no figures.** Every quantity below is cited by section
from the document that owns it and is **never restated here**. This note is written to be
consumed by the `S4` pre-registration if `S4` opens. **It recommends nothing and proposes no
route.**

**What this is.** On **2026-09-13** the owner named three points **in favour of adopting our
own similarity** that **no `LBD-` criterion measures**, and that are **unrelated to connection
counts, dead ends and path quality**. `LBD-C1` measures fidelity, `LBD-C2a` and `LBD-C2b`
supply, `LBD-C3` cost, `LBD-M1` population; the two `LBL-` listens measure what his ear can
tell apart. None of the three points below is in any of those results — which is why they are
recorded here rather than left in a conversation.

**Whose these are.** The three points in §1 are **the owner's**, stated 2026-09-13 and written
as his in substance rather than verbatim. What is set **beside** each — the supporting section,
and the nuance that section attaches — is a session's assembly of the existing record, and is
labelled where the distinction could be missed. **`S4` — the population rule, API sizing, the
fame source and a refresh procedure — remains the owner's decision.**

**Governing documents, unchanged by this note.**
[`../specs/2026-09-06-own-similarity-design.md`](../specs/2026-09-06-own-similarity-design.md)
governs the track (its §9 is the closed list), and
[`../specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md`](../specs/2026-09-07-lbd-fidelity-and-supply-preregistration.md)
owns the criteria, the gates and every amendment. **Where either disagrees with this note, they
govern.** Status is [`../NEXT.md`](../NEXT.md)'s.

---

## 1. The three points FOR adoption, each with its record and its nuance

### 1.1 Artists who emerged since the deployed lists were computed would be in the graph

> **The owner, 2026-09-13:** the lists we serve were computed at some point in the past. An
> artist who has emerged since then cannot be in them, however much they are listened to now.
> If we compute similarity ourselves from a dump we refresh, those artists are in the graph.

**The record that supports it.** The gap between our recomputation and the deployed lists was
diagnosed, and the diagnosis is that the deployed dataset was computed on a fraction of today's
co-listens:
[`builder/analysis/2026-09-08-lbd-similarity/README.md`](../../../builder/analysis/2026-09-08-lbd-similarity/README.md)
**§5b** states the inference and the date it implies, **before** the test that decides it; its
**§5c** reports `C1-DIAG-1`, the single-variable rerun on a corpus rebuilt as it stood at the
inferred date, read against §5b's pre-stated branches. It came out on the first branch: **the
dataset date is the largest term in the gap.** §5a's `created` table is where the corpus's
growth over time is stated. All figures are those sections'.

**The nuance the record attaches.** **`LBD-R8`** (design **§7**) names the mapping bias — listens
that never reach an MBID, concentrated at the obscure end — as a limit on the gain, and as
**inherited from the endpoint rather than introduced by us**. A newly emerged artist reaches our
graph only if their listens map; the artists least likely to map are at the same end of the
distribution as the artists most likely to be new. The design names **`LBD-M1` by fame band** as
what would show the bias's extent. §5c records a second residual honestly: even on the dated
corpus the score ratio did not reach 1, so the deployed dataset saw fewer co-listens still than
that date alone explains, and today's mapping is one of the candidates — **not separable from
this dump.**

**What is not measured, and this is the point of recording it:** *how many* such artists there
are, or who they are. No `LBD-` arm counted them.

### 1.2 Partner artists with no explainable provenance in the deployed lists would be dropped

> **The owner, 2026-09-13:** the deployed lists contain partner artists we cannot explain — we
> can see no route by which the listening data would produce them. Computing similarity
> ourselves drops that class.

**The record that supports it.** The similarity README's **§5a** identifies the class and its
mechanism: archive entries naming artists that exist in MusicBrainz's `artist` table but have
**no `artist_credit_name` row at all** — individual band members, who are never credited on
recordings because the band is. The deployed job therefore attributed listens to them through
**something other than the recording's artist credit, which is the only attribution the pinned
source performs**; §5a states plainly that the mechanism **is not identifiable from that
source**, and gives the class's size and its most frequent members. Its **§5c** shows the class
is **dated-corpus-invariant** — the absent bin did not shrink on the rebuilt corpus, *as it
must not*, since no corpus of ours contains listens attributed to uncredited people. So this is
**structural**: no refresh, and no parameter of ours, brings that class back.

**The nuance.** §5a records the same fact as a **ceiling on fidelity** — the class is part of
why a perfect reimplementation of current source could not reproduce the deployed lists, and
the sections there own that arithmetic. The identical fact reads as a cost under `LBD-C1` and
as a gain under this point, and that is not a contradiction: **`LBD-C1` scores agreement with
the deployed lists, not agreement with what a listener wants.**

⚠ **Whether dropping this class is a gain is the owner's product judgment, and nothing in the
record decides it.** A band's drummer surfacing as a "similar artist" to that band may be
exactly what a listener wants on a card, or exactly what they do not. No `LBD-` criterion, and
neither `LBL-` listen, asked.

### 1.3 The data, the parameters and the refresh schedule would be ours

> **The owner, 2026-09-13:** today the data, the algorithm's parameters and the refresh
> schedule are ListenBrainz's. After adoption they are ours — we choose the corpus, we set the
> knobs, and we decide when it regenerates.

**The record that supports it.** Design **§8** is the list, written from the assessment for
exactly this reader: no live dependency on the Labs endpoint, the bootstrap endpoint, the rate
limit or the six-value enum; refresh becomes a local batch pinned to a dump id and a parameter
string; LB's own regeneration no longer reaches us; the population rule becomes a product
decision; and fame and popularity **could** come from the same pass, each behind its own
decision. Design **§1** is why the knobs matter — the endpoint's threshold, not its cap, is what
`STC-6` established leaves an obscure artist with almost no neighbours, and the remedy was
outside our control.

**The nuance, and it is the sharpest one here.** The thing that would come under our control is
**a reimplementation whose fidelity gate fired**. **`LBD-G1` fired** on the pinned corpus and
was **overridden by owner decision under `LBD-AM3`**, after the §5c diagnosis — the reading
stands at the value the similarity README's §5 records, and the arms were read anyway. ⚠
**`LBD-C1` is never cited as passed**, for any arm. So "our parameters" means parameters of a
job that has not been shown to reproduce the deployed lists to the gate's own floor, and
whose residual gap is a bundle no arm separates (`LBD-X5`). Control is real; **it is control
over that.**

---

## 2. Against, for the same reader

Not a balance exercise, and not an argument. Three costs the same reader needs in view, each
owned elsewhere and cited, **nothing else drawn in**:

- **Served artists that are absent from the recomputed maps altogether.**
  [`builder/analysis/2026-09-10-lbd-served-population/README.md`](../../../builder/analysis/2026-09-10-lbd-served-population/README.md)
  **§3** owns the counts for both maps built over the served population — artists the app serves
  today that have no pair at all in our table, plus those pruned with the largest component. Its
  **§6** records that **who they are was counted and not investigated**, and that whether any of
  them sits in the owner's own journeys is unknown. What to do about them **is** the population
  rule, which is `S4`'s.
- **The operating footprint.** Design **§8**, the same list as §1.3 above and read the other
  way: standing local disk and its annual growth, a full re-download cadence if deletions
  matter, a standing stage of hours in front of the archive replay, and the API's hosting or
  router possibly needing to change with the population.
- **What a refresh actually costs is the similarity stage, not every build.** The archive
  replay — emit, then build — is the cost the pipeline **already** pays today, and its wall
  clocks are owned by
  [`builder/analysis/2026-09-10-lbd-supply/README.md`](../../../builder/analysis/2026-09-10-lbd-supply/README.md)
  **§1** (emit) and **§2** (build). What adoption *adds* per refresh is the pair pass; the
  similarity README's **§5c** owns a measured pass over roughly a third of the corpus, which is
  the closest thing on the record to a refresh-shaped figure. **Read the two together and take
  the units from their own sections** — this note states neither.

---

## 3. What this note does not do

- **It recommends nothing, and proposes no route.** Stopping the `LBD-` track remains a
  complete outcome ([`2026-09-13-lbl-listen2-results.md`](2026-09-13-lbl-listen2-results.md)
  **§6**), and which route follows is the owner's.
- **It is not evidence** about supply, fidelity, path quality or preference, and it reads no
  criterion. Nothing here may be cited as a result.
- **It lifts no bar.** `LBD-X6` stands — listen 2's result holds for ListenBrainz's own pairing
  semantics and may not be generalised to the cheaper form; its condition was discharged and
  `R10` **fired**, which confirmed the bar rather than releasing it. `LBD-X4`, `LBD-X5` and
  `REQ-41` are likewise untouched.
- **It adopts nothing and changes no default.** `S4` owns adoption, and `S4` is its own
  pre-registration and rebuild — in which **every arm records which pairing semantics it uses
  and why** (`LBD-D6`, load-bearing since `R10` fired).
