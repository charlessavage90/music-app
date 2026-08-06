# `CCR-` — do the class's top similarity edges point at people they RECORD with?

**Role: ACTIVE, governing for the `CCR-` probe.** Committed **before any MusicBrainz
relationship data was fetched**. The commit timestamp is the evidence that every read below
preceded the result.

**Owner's hypothesis, in his words (2026-08-06):** ListenBrainz is *"overweighting similarity
of artists that record together"* — when two artists collaborate on a track, especially a
popular one, the session algorithm boosts their similarity. Worked case: **Laura Lee**, a
member of Khruangbin with no solo releases, sits at **rank 2 (score 214)** in Leon Bridges'
crawled similar-artist list.

**What is already established and is NOT what this measures.** The mechanism is confirmed from
source (`findings/2026-07-30-lb-algorithm-semantics.md` `LBS-1`): within a session, listens
whose artists *and* credits differ contribute `s1 × s2`, weight 1 for a main artist and 0.25
for a featured one. **That collaboration can inflate similarity is a fact about the algorithm,
not a question.** This probe asks a different and narrower thing: **does that mechanism explain
the class the owner is actually seeing in the app?**

---

## 0. Held constant, and why the intervention cannot change it

| Held | Why it is genuinely constant here |
|---|---|
| Artifact | `graph-msw-tu50.bin`, sha `43dd82bb…`, verified against its sidecar before each run. Arm membership is read off it; nothing writes it. |
| Archive | `grt-archive-algb/…/session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30/` — **contribution_3**, the crawl this graph was built from. *(An earlier exploratory pass read `graph-archive`, the contribution_5 crawl, and was wrong. Naming the path here so it cannot recur.)* |
| Top partner | Always rank 1 of the artist's archived list. Rank is fixed in the archive and no arm can move it. |
| MB endpoint and `inc=` | One endpoint, one parameter set, both arms, one run. |

## 1. The two quantities, and they are different currencies

- **`fame_lb_pctl`** — rank of the artist's ListenBrainz listener count within this artifact.
  An **audience** measure.
- **`pop_raw_pctl`** — rank of score-weighted in-degree. A **similarity-centrality** measure,
  computed from the archive. **Not** popularity in any external sense, and **not** fame.

The class of interest is **high centrality with low audience** — central to the similarity data,
almost nobody listens to them.

## 2. Arms — factor table

| Arm | `fame_lb_pctl` | `pop_raw_pctl` | Differs from CLASS by |
|---|---|---|---|
| **CLASS** | < 0.20 | > 0.80 | — (the arm under test) |
| **CONTROL-OBSCURE** | < 0.20 | < 0.40 | **centrality only** (audience held low) |

**CONTROL-OBSCURE is the isolating baseline and the primary comparison.** It holds audience low
and varies only centrality, which is the single knob the hypothesis is about. A control at
mid-fame would have varied both and could not support any attribution.

**n = 200 per arm**, sampled without replacement, seed `20260806`. Artists absent from the
archive or with fewer than 10 archived neighbours are skipped and replaced, and the skip count
is reported.

## 3. What is fetched

`https://musicbrainz.org/ws/2/artist/{mbid}?inc=artist-rels&fmt=json`, one request per sampled
artist, rate-limited to 1/second per MusicBrainz's terms, with the project's existing
`artistpath-research/1.0` user agent. **Both arms in a single run**, interleaved, so a
mid-run change at MusicBrainz cannot land on one arm only.

An artist's **related set** is every artist MBID appearing in any `artist-rels` entry —
band membership in either direction, collaboration, and any other artist-artist relation.

## 4. Gate — run first, and alone

**`CCR-G1` (documentation density).** Median count of `artist-rels` entries per artist, per arm.

**Plain sentence, fixed here:** *does MusicBrainz simply know more about one group of artists
than the other?*

This is the probe's main threat. CLASS artists are, by construction, adjacent to famous
artists, and their MusicBrainz pages may be better maintained than a genuinely obscure
artist's. **If so, a positive result could be documentation bias rather than a real difference
in relationships.**

- **If the two arms' median relation counts differ by a factor of 2 or more**, the raw
  comparison in `CCR-C1` is **reported as confounded** and the conditional form (`CCR-C2`)
  becomes the primary outcome, with the confound named in every citation.
- Below 2×, both are reported and `CCR-C1` stands as primary.

**`CCR-G1` never voids the probe** — it selects which outcome is primary. It is evaluated and
reported before either outcome is computed.

## 5. Outcomes

**`CCR-C1` — raw rate.** Proportion of artists in an arm whose **top similarity partner is in
their MusicBrainz related set**.

> **Plain sentence, fixed here:** *how often is the artist the app thinks you are most similar
> to, actually someone you are in a band with or have recorded with?*

**`CCR-C2` — conditional rate.** The same proportion, computed **only over artists with at
least one documented artist-artist relation**. Partially controls documentation density.

> **Plain sentence, fixed here:** *among artists MusicBrainz knows anything about
> relationship-wise, how often is their top match a bandmate or collaborator?*

**Effect size, fixed before any data exists.** Let Δ = CLASS − CONTROL-OBSCURE on whichever of
`CCR-C1`/`CCR-C2` `CCR-G1` selects as primary.

| Δ | Branch | Read |
|---|---|---|
| **≥ +20 points** | `supported` | The owner's mechanism explains the class. Co-credit relationships are what put these artists in the middle of journeys. |
| **+10 to +20** | `equivocal` | **Deliberately neither supported nor null. No default is named here and none may be supplied later.** |
| **< +10 points** | `null` | The class is **not** explained by documented recording/membership relations. |

**`CCR-C3` — relation-type breakdown.** Among CLASS artists whose top partner is related, the
distribution of relation types. **Descriptive, no threshold, and no branch attaches to it.**

## 6. The read of every result, including the null

- **`supported`.** The mechanism is confirmed as the class's cause. This does **not** license
  any specific remedy: dropping artists is already ruled out by the owner (2026-08-06, and
  `ULF-` shows the clearest cases are caught anyway). It makes edge-level work the candidate,
  and **`B` (the `p99_log_clip` rescale) is where that would land** — but `B` is independent of
  this result and proceeds either way.
- **`equivocal`.** No action. Do not re-run with a different threshold to resolve it; the
  threshold is fixed above and reaching for a second one is how a null becomes a finding.
- **`null`.** The class is real and measured — that is not in question, it is in the depth
  census — but its cause is **not** documented co-credit relationships. **The Laura Lee case
  survives a null untouched**: it is a single proven instance, and one instance was never the
  claim under test. `B` proceeds unchanged.

**Barred reads, and they travel with every citation of this document:**

1. **This cannot establish that collaboration inflates similarity.** That is settled from
   source (`LBS-1`) and this probe neither strengthens nor weakens it.
2. **Absence of a MusicBrainz relation is not absence of a relationship.** Both arms are
   floors. Only the *difference* is interpretable, and only subject to `CCR-G1`.
3. **This says nothing about whether these artists are good recommendations.** Coherence is
   `CAU-`'s question and was answered for a different graph.
4. **No adoption follows from any branch.** This probe changes no default, no weight and no
   filter.

## 7. Run state a read presupposes

Every read above presupposes **both arms complete** at n = 200, or the achieved n reported
alongside with the skip count. **A partial run supports no branch** — not even the null, since
the class is the rarer population and would thin first under any systematic fetch failure.

If MusicBrainz rate-limits or errors on more than 10% of either arm, the run is **incomplete**
and is reported as such rather than read.
