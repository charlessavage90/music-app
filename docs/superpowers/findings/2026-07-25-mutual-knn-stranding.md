# Mutual k-NN strands recognisable artists at one connection — 2026-07-25

**Role: AUTHORITATIVE for its own measurements. Not a decision, not a proposal.**
Owns every figure below; cite this document by section rather than restating them.
Measurements: `builder/analysis/2026-07-25-mutual-knn-stranding/` (two scripts, both
read-only, both self-gating — see §5).

**Nothing was adopted, rebuilt, or changed.** Path-quality work is paused by owner
decision and this finding does not resume it. It is recorded so it cannot be lost,
which is the specific failure that befell F1's deferral condition
(`../2026-07-25-gate1-clips-and-ux-execution-log.md` §16).

Identifiers are namespaced `MKS-n` — disjoint from the `C`, `F`, `A`, `R`, `T3-`
and `TF-` series already in use.

---

## 1. What was found

**MKS-1.** An edge survives the builder's `mutual_knn` cap only if **each artist
ranks the other in its own top 50**. That rule systematically disconnects one class
of artist: **those whose nearest musical neighbours are all substantially more
listened-to than they are.** Their own list points upward; the artists it points at
have fifty better-known candidates ahead of them; every one of those edges dies in
both directions.

**MKS-2.** The result is recognisable artists reduced to a single connection, and
that surviving connection is frequently not their strongest musical relationship —
it is whichever candidate happened to have a small enough catalogue to reciprocate.

| artist | own top-50 | reciprocate | survives | dropped from the head of its own list |
|---|---|---|---|---|
| Meat Loaf | 50 | **1** | Tim Curry | Guns N' Roses, Elton John, Journey, Fleetwood Mac, R.E.M., Van Halen |
| Elbow | 50 | **1** | Doves | Radiohead, Coldplay, Arcade Fire, Muse, Arctic Monkeys, Blur |
| The Cult | 50 | **1** | The Sisters of Mercy | Guns N' Roses, R.E.M., U2, The Rolling Stones, The Clash, Van Halen |
| The Streets | 50 | **1** | Dizzee Rascal | Radiohead, Arctic Monkeys, The Beatles, Gorillaz, The Strokes, Beastie Boys |
| Nada Surf | 50 | **1** | Rogue Wave | The Smashing Pumpkins, Pixies, Modest Mouse, Coldplay, The Strokes, EELS |
| Pretenders | 50 | **6** | The Cars, Blondie, Roxy Music, Crowded House, Paul McCartney, The Bangles | Fleetwood Mac, The Police, The Rolling Stones, R.E.M., U2, Elton John |

Meat Loaf is the clearest case. His sole relationship in the shipped graph is his
Rocky Horror co-star, because Tim Curry's catalogue is small enough to carry him and
no rock act's is.

**MKS-3.** Across a random sample of 150 crawled artists: a typical artist keeps
**43.7 % (mean) / 40.0 % (median)** of its own top-50; resulting degree median **8**,
mean **11.7**; **9.3 %** of artists are left with one connection or none, **18.0 %**
with two or fewer.

**MKS-4.** In aggregate the graph looks healthy, which is why this was not visible
before. Degree rises monotonically with popularity and the stranded artists are
outliers against their own band, not a shifted distribution:

| popularity decile | median degree | mean | % with ≤2 edges |
|---|---|---|---|
| 0–10 | 1 | 1.4 | 96.6 % |
| 40–50 | 10 | 9.3 | 5.1 % |
| 80–90 | 22 | 22.4 | 1.2 % |
| 90–100 | 26 | 26.4 | 0.5 % |

Elbow, The Cult and The Streets all sit above the 92nd popularity percentile, where
the median artist holds ~26 connections and 0.5 % hold two or fewer.

**MKS-5 — this is not the defect the tie-break fix repaired.** That fix
(`2026-07-23-tiebreak-fix-adoption.md`) addressed saturated scores letting an MBID
tie-break decide which neighbours the *most* famous artists kept, and it worked:
Radiohead, The Beatles and Coldplay all hold the full 50. MKS-1 is the band
immediately below — artists popular enough to be searched for, not popular enough to
be reciprocated. Nothing in the record covers them.

## 2. Consequence already observed

**MKS-6.** This is the mechanism behind **F1**, the zero-intermediary path. An
adjacent pair can be given an intermediary only if some third artist connects to
both; where one endpoint holds a single edge, no such artist exists. Measured on the
adopted artifact: **6,599 pairs (1.47 % of 449,003) have no possible detour** —
6,396 because one artist has a single connection, **203** where both have two or
more. Fifteen of those have both endpoints in the top 10 % by popularity, including
`Doves ↔ Elbow`, `Pretenders ↔ Crowded House`, `The Sisters of Mercy ↔ The Cult` and
`Serge Gainsbourg ↔ Charlotte Gainsbourg`. Seven were confirmed through the running
router; all return exactly two cards.

The F1 requirement (every journey needs at least one stop) is therefore
**unsatisfiable for those pairs on this artifact**, whatever the API does. That is a
graph fact, not a routing choice.

## 3. What this does and does not license

**Does:** it establishes the mechanism, names the affected artists, and gives the
size of the class. It is sufficient to justify *investigating* a rule change.

**Does not:** it is **not evidence that the graph would be better under a looser
rule.** `mutual_knn` was adopted deliberately and won a blind listening test against
the alternative (`2026-07-22-phase2-sweep-results.md`); discarding weak one-way links
is its purpose, and this finding measures exactly that purpose operating. **No
adoption, no rebuild, and no rule change is proposed here.** Any such change is
path-quality work, is behind the owner's pause, and would need its own
pre-registration.

**Unmeasured, and deliberately so:** how much this degrades real paths. Stranded
artists are also nearly unreachable *as* intermediaries, so the plausible harm is
wider than the endpoint case — but that is a claim about path quality and is not
measured here.

## 4. Recorded in passing, not investigated

**MKS-7.** **1,283 artist names appear more than once** in the graph, covering 2,838
artists (3.83 %). Two entities named *Nirvana* exist — the US grunge band (degree 50,
popularity 0.998 percentile) and a 1960s UK band (degree 4, 38.8th percentile).
Whether search can serve the wrong one is **not examined here**; search ranks on
popularity, which would favour the intended entity in that example, but no check was
run and the general case is untested. Same family as the C1 wrong-artist clip defect.

## 5. Method, and two errors it survived

Both scripts refuse to report figures they cannot stand behind:

- `degree_and_bridges.py` asserts the artifact's **sha256** against the adopted value
  before reading it. Several graphs exist in `builder/scratch/` and are not
  interchangeable.
- `reciprocity.py` models the builder's cap over the raw archive, then **validates
  its predictions against the shipped graph** for six artists and exits if any
  disagree. It reproduces all six neighbour sets exactly, including Pretenders' six
  and Doves' seven.

That validation gate exists because the first attempt was wrong twice, and both
errors produced confident, plausible output:

1. **k was taken as 15**, read off the `t15` in the artifact filename. The cap is
   `BuilderConfig.max_neighbours_per_artist = 50`; `t15` is a run tag.
2. **The candidate list was not filtered to crawled artists.** The builder filters to
   `known` before ranking; without it, entries the builder never considers displace
   real neighbours inside the window.

Together they reported *Pretenders: 0 mutual* — contradicted by the shipped graph,
which gives it six. **The contradiction against ground truth is what exposed both
errors; re-reading the script would not have.** Hence the gate: a model of the
builder that is not checked against the builder's output is not evidence.

A third error, upstream of the analysis, is worth the same note: **Nirvana was
initially reported as a stranded famous artist.** It is not — a name lookup returned
the wrong one of two entities. Corrected before it reached any conclusion, and the
direct cause of §4 being measured at all.
