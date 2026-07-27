# Resume brief — path quality

**Role: ACTIVE. A handoff for a cold session**, written 2026-07-26 for someone who will
read it months from now with no memory of any of this. It is meant to be read in full; it
is short on purpose and carries five things only.

**Resuming path-quality work is the owner's trigger, never a session's. This document is
not a resume signal** — it exists so that *if* he resumes it, the next session starts from
the right question instead of re-deriving one. Nothing here is proposed, pre-registered, or
assigned a threshold.

---

## 1. The decision you are being asked to make

> **Should we build a bounded degree floor — restoring a small number of edges to artists
> the both-ways cap leaves at one or two connections, with a quota on the *receiving* side
> so that maximum degree cannot rise?**

Yes or no, with a design and a cost if yes. It is a decision, not a research topic. The
alternative on the table is *do nothing*, and that is a real option.

## 2. Settle this first — it blocks everything else

**Why do barely-connected artists almost never appear as middle cards? Two explanations
survive, and nobody has separated them:**

- **Arithmetic** — an artist with few connections has fewer places to *fit* between two
  other artists. Nothing to do with routing.
- **Pricing** — the router evaluates them and declines them.

**They point to opposite conclusions.** If it is arithmetic, adding edges is exactly the
fix. **If it is pricing, adding edges changes nothing** and the floor is wasted work — the
artists would become eligible and still not be chosen.

**Neither measurement to date touches this**, and both say so explicitly in their own
reports. **Settle it before designing or costing anything.** It needs an instrument neither
run used, and choosing that instrument is the first real task.

## 3. A correction to carry — the intervention is bigger than it sounds

A consulting session sized the degree floor as a **small** change: a few edges per artist,
lifting the stranded ones off one or two connections.

**Today's obscure-pair run shows that would buy nothing.** Nothing at all was delivered
below four connections, and nothing at two — even on journeys that started and ended at
barely-connected artists. So a floor set at two or three lands entirely inside the range
that never gets delivered anyway. **Artists would have to be lifted considerably higher for
the floor to change what anyone sees.**

Two consequences: the intervention is **larger** than previously implied, and the
receiving-side quota is therefore a **real design problem** rather than a formality —
lifting many artists much higher is exactly what pushes back on the degree bound the quota
exists to protect. Figures: `builder/analysis/2026-07-26-obscure-pair-deliverability/REPORT.md`.

## 4. Reading order — three items, then stop

1. **`findings/2026-07-26-low-degree-synthesis.md`** — the interpretive assembly written
   the same day. It is the only document that reads *across* the three measurements, and it
   names its own weakest item.
2. **`findings/2026-07-26-committed-walk-deliverability.md`** — what the router actually
   delivered, both runs, including §7 and the confound in §2 above.
3. **`docs/README.md`** — the map, for anything else you need and for which documents are
   superseded.

**Do not re-derive the measurement chain from the analysis directories.** Three exercises
sit under `builder/analysis/` with full deliverables; they own the figures and you should
cite them, but reading them in sequence to reconstruct the story costs a day and the
findings documents above exist precisely so you do not have to.

**Background, not direction — added 2026-07-27, and deliberately outside the three.**
`findings/2026-07-27-boilthefrog-source-review.md` reads the source of **boilthefrog**, the
product this project's calibration record names as its reference. Read it for **context on
what the reference product does and does not do** — it corrected `WHAT-GOOD-LOOKS-LIKE.md`
in two places. **Do not read it for direction.** It is a study of a *different product with
a different goal*: boilthefrog excludes obscure artists from its graph outright, and its
author built its popularity term to keep listeners *away* from them. **It changes nothing in
§1, §2, §3 or §5 of this brief.** In particular, the option it names is a **graph**
intervention and **§2 blocks it exactly as §2 blocks the degree floor** — the read-this-first
box at the head of that document says so, and is the part to trust if its later sections read
more enthusiastically than that.

## 5. Closed, and what you may not spend

**Closed — do not reopen, and do not re-argue:**

- **Loosening the both-ways cap is rejected.** Dropping the reciprocity test restores
  unbounded degree, and bounded degree is what won a blind listening test. Any targeted
  alternative must answer that coupling by demonstration, not assertion.
- **Track 2 and Track 2F are nulls. Do not re-run either.**
- **The ceiling toll is exhausted at mechanism strength**, with its bound holding.
- **Gate 1 is complete, including F1.** Every journey gets at least one stop, or says why
  it cannot.

**May not be spent without the owner's explicit decision:**

- **A blind listening test.** One-shot, and it is his ear.
- **A production rebuild.** Also currently *blocked* — `builder/src/artistpath_builder/acceptance.py`
  rejects a rebuild while the artifact carries nameless artists, by design, and that
  decision is his and unmade.
- **Any growth of `CLAUDE.md`** or the standing context layer.

**Still parked, so they are not lost:**

- **The builder-side p99 rescale** — the live candidate when path work paused. Measured as
  having real headroom; **not pre-registered.**
- **The re-crawl probe at a lower score cut-off** — the largest lever on how many artists
  are barely connected, and it is a parameter this project chose. Payoff unmeasured. The
  cheap version is a read-only probe of the source for a sample, not a full re-crawl.
