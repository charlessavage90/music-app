# What the router actually delivered — committed-walk deliverability, 2026-07-26

**Role: AUTHORITATIVE for its own interpretation; OWNS NO FIGURES.** Every quantity
belongs to [`builder/analysis/2026-07-26-committed-walk-deliverability/`](../../../builder/analysis/2026-07-26-committed-walk-deliverability/),
whose `REPORT.md` is the deliverable. **Cite that directory for any number.**

Read-only re-read of committed experimental runs — **no routing was run, no rebuild, no
arm, no adoption, no config touched.** Same class as `ASC-5`. The path-quality pause is
intact and this document does not touch it.

Identifiers are namespaced **`CWD-n`** — verified unused across the repository. It
**resolves `SYN-4`** in [`2026-07-26-low-degree-synthesis.md`](2026-07-26-low-degree-synthesis.md)
and extends no other series.

---

## 1. `CWD-1` — `SYN-4`'s falsifier did not fire, and it did not fire emphatically

*(Plain: across every journey the app's normal settings produced in the recorded
experiments, it never once put a barely-connected artist in the middle — not a single card
out of 384.)*

Both clauses came back at zero, against a graph where **more than half** of all artists
hold fewer than ten connections. The lowest-connection artist ever delivered as an interior
card was Uriah Heep. Counts, thresholds and the degree distribution: the report.

`SYN-1`–`SYN-3` therefore keep their motivation. Connection count is not ruled out as what
keeps an artist off the screen.

## 2. `CWD-2` — but the test could not have passed meaningfully, and this was fixed in advance

*(Plain: the journeys on record nearly all start and end at very famous artists, so finding
no obscure artists in the middle is roughly what you would expect however the app works.)*

`SYN-4` stated before the run that a low share was the expected result and weak
confirmation of nothing. The pair set proves it rather than merely asserting it: the
endpoints' median connection count is several times the graph's own, none is below ten, and
the pairs are Radiohead → The Beatles, Madonna → Bob Dylan and similar. Figures: the report.

**So the honest reading is asymmetric, and it is the whole value of having pre-registered
the clause.** The result removes a way `SYN-1`–`SYN-3` could have been wrong. It supplies
no positive evidence that they are right. **A reader who quotes `CWD-1` without `CWD-2` has
the finding backwards** — this is `STC-3`'s shape again, and deliberately so.

## 3. `CWD-3` — the three committed runs are one sample, not three

*(Plain: three separate experiments each recorded the app's normal settings, and all three
produced exactly the same journeys — so they are one result checked three times, not three
results.)*

Track 2 stage 1, Track 2 stage 2 and Track 2F each carry a `P` arm, and all three are
**byte-identical**. `P` is the deterministic baseline, so this is reproducibility rather
than evidence, and it is recorded because **the first version of this measurement counted
all three and reported three times the true number of interior cards.** The corrected count
is in the report; the gate that now enforces it is the analysis directory's `README.md`
gate 4.

Worth keeping for a reason beyond the arithmetic: the inflated figure was self-consistent
and looked entirely reasonable. What exposed it was noticing that three supposedly
independent runs had returned *identical* totals.

## 4. What this does not establish

- **It does not show the router is incapable of delivering a low-degree artist.** It shows
  it did not, on a pair set chosen to be famous. Separating *cannot* from *did not here*
  needs a pair set that asks the question, and none has been run.
- **The distinct-artist count is a lower bound**, never a measure of what the app could
  deliver. Twelve pairs cannot exercise the artifact.
- **Nothing about path quality.** No cost weight was read and no path was scored.
- **The zero is not purely a routing fact.** A low-degree artist has fewer opportunities to
  sit between two others, so some of the effect is arithmetic rather than pricing. This
  measurement cannot separate the two, and does not try.
- **It does not reopen §2.12**, which concerns whether obscure artists are *reachable*.
  This concerns whether low-*degree* artists were *delivered* — degree is not popularity
  and neither is fame (§2.6, §2.11).

## 5. Weakest link

**The inference from "did not appear" to "connection count gates delivery" is the load-
bearing one, and this measurement supports only the weaker half of it.** What would falsify
`CWD-1`'s usefulness: a re-read over pairs with ordinary or obscure endpoints showing
low-degree interiors appearing freely — which would mean the zero here was an artefact of
the pair set alone. **That measurement has not been run, is cheap, and is not proposed
here**; path-quality work is paused and this document does not resume it.

What I would defend cheaply: `CWD-3`, and the gate results — all mechanical. What I would
abandon on one contrary measurement: any reading of `CWD-1` stronger than "the falsifier
did not fire".

## 6. Nothing is proposed

No rule change, no arm, no threshold, no rebuild, no adoption. `SYN-4` is resolved and
closed; `SYN-1`–`SYN-3` stand exactly as committed, neither strengthened into a
recommendation nor withdrawn.
