# Round 2 addendum (read after BRIEF-COMMON.md)

Read `exploration/ROUND1.md` first (what died, what showed signal, the shared problems), then the NOTES.md
and best variant file of every round-1 folder your direction builds on. **Reuse their code** (copy into your
folder; don't edit theirs).

What round 2 is for: turn signal into finalists. A finalist
- is visibly less famous by press 3 on famous pairs, and keeps getting less famous to press 10
  (round 1 plateaued at ~78–86: beat that);
- keeps coherence at today's level (~0.66–0.68, bad steps ≤ ~23%) — read the journeys, not just the number;
- does not over-dive on mid-fame pairs (middle artists far below both endpoints at press 1–3 is a defect);
- keeps journeys to a sane length (today 7–8; +3 or so is fine, 18 is not);
- keeps some famous artists (top-10% share not ~0 at press 10);
- replaces the pressed artist with someone similar and less famous as often as possible —
  `exploration/r1-rules/replace_check.py` measures this (today 62%); report it for your best variants;
- routes in under ~3 s per journey (the owner will press it live in a practice room).

Deliverable addition: for each best variant, a **self-contained variant file with its settings baked in as
defaults** (no env vars needed), with the `journey(ctx, s, t, pressed, prev)` interface and a module docstring
whose first line is a one-sentence plain description a listener would understand. The practice room imports
these files directly.

Up to 6 rated runs. The screen's step ratings are cached and shared; rated runs get cheaper as you go.
