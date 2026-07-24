# HANDOFF — Track 2, at the fame-proxy/sweep seam, 2026-07-24

**Role: ACTIVE, short-lived by design.** Written at a **clean seam** (the fame-proxy track
concluded; pre-registration amendment A11 committed), for a session picking up the **sweep**
cold. Records only what is not already in the record. Read the execution log first:

> **[`2026-07-23-repair-and-retune-execution-log.md`](2026-07-23-repair-and-retune-execution-log.md)**,
> the "Track 2" section — in particular the last three entries: the **attractor analyst
> run**, **"P4 CLOSED — owner adopts Option C"**, and everything above them for P4's arc.
> Then **pre-registration [§5 inline + "A11 in full"]** — A11 is governing.
> `docs/README.md` classifies every document.

**First action for the cold session: run `closeout` B1 — dispatch the `doc-auditor`.** Docs
changed materially this session (A11 across the pre-registration; the execution log; the doc
map; two new `builder/analysis/` dirs). B1 is the fresh-session step and its own rule is that
the strongest predictor it finds something is a session concluding it needn't run.

---

## 1. State in three lines

- **P4 (fame proxy) is CLOSED.** Both automated proxies fired §5 (Deezer misranks mid-fame;
  Wikipedia is blind to the modern-obscure tail). **Owner adopted Option C** (A11): the fame
  proxy is **English-Wikipedia pageviews with an unmatched interior scored at the fame floor
  (0)**, replacing §5's owner-labelling fallback. Residual risk accepted, **guarded at
  d15/d20**. Figures owned by `builder/analysis/2026-07-24-track2-fame-proxy-wikipedia/`.
- **The "is the obscure tail a cross-genre attractor?" question is answered: NO, not
  graph-limited** (`builder/analysis/2026-07-24-obscure-tail-attractor/`, verdict
  independently spot-checked). **Carry its caveat:** it was measured in raw-popularity
  currency; the sweep's **fame-currency floor is the untested lever** — watch for lo-fi
  surfacing on downtempo-adjacent paths in the blind listen.
- **No factorial/sweep arm has run.** Artifact untouched, sha256 `4cb84ef9…b061dc8`.

## 2. The open work — the sweep (this is the whole next unit)

Per pre-registration §1.4 + §9's still-open table. Enumerated so it is not re-derived:

- **P6 — percentile machinery** (tie-handling rule; §7/§0 note it is not built). `pop_pctl`
  is reserved and unused for exactly this.
- **The C1–C6 harness**, implementing the **A11 encoding**: score interiors on Wikipedia
  pageviews, **absent = 0 (fame floor)**, plus the **d15/d20 guard** (surface *potentially
  notable* unmatched interiors — non-Latin-script name, or an article exists in a **non**-
  English Wikipedia — for a one-glance owner check before counting them as obscure-reach).
  This is the D4 residual. `score.py` in the Deezer dir is proxy-agnostic (`--value-key`) but
  it validates the *proxy*; the *arm* scorer (C1–C6 over routed paths) does not exist yet.
- **The D4/D6/D7 + C3-depth-anchor amendment** (§9 open table). D4 is now partly discharged
  by A11 — write the one line making the C3 anchor explicit at 5 bypasses when this lands.
- **PR-A (A0 vs P) already ran** — the floor stays off across the factorial (A8); do not
  re-run it. Then the arms (§1.4), then the blind listen (the coherence arbiter).

## 3. Considered and decided this session (do not re-argue)

- **B vs C:** owner first said B, then corrected to **C** on sunk-time reasoning (B's
  labelling premium exceeds the exposure; C is reversible and cannot ship a defect — the
  blind listen gates adoption). Recorded in the execution log and A11.
- **Inventing a third fame proxy:** out of scope — the pre-registration's tree was Deezer →
  Wikipedia → fallback; C resolves the fallback.
- **Running the attractor analyst was worth it** and answered the graph-limited worry; the
  residual is the currency caveat above, carried into A11, not a reason to re-run.

## 4. Numbers computed and not written down

None. All figures are committed: the fame-proxy README + `score.json`; the exploration in
`explore_absence.py` output; the attractor dir's README (owns its figures); CROOVE's identity
(Korean rhythm-game producer, pop_raw 0.457/85th pctl) in the execution log.

## 5. Things the owner said, now in a file

- **Adopts Option C; accepts its residual risk** (A11, execution log).
- Corrected an earlier mis-stated preference for B → C. His reasoning (sunk time) is recorded.

## 6. In flight / git

- **Nothing running.** No subagents live, no background jobs, no stashes. Tree clean.
- **Branch `track2-prereg-amendments`, PR #9 (draft, OPEN).** This branch is now a **coherent
  unit** (pre-registration amendments A1–A11 + P4 closure + supporting analysis). **It is
  ready to merge, and the sweep should branch fresh off `main` after it lands** — a clean
  boundary, and merging is the owner's call. If the sweep continues on this branch instead,
  it will grow large.
- **One committer = the session.** No consultant is live now (the prior one finished).
- **D6 standing-layer delta THIS session: 0** (only `docs/` and `builder/analysis/` touched).
  The branch's +256 on `CLAUDE.md`/`.claude` is the consultant's earlier work, already
  accounted; its two offsetting doc relocations remain due at **Track 2 adoption**.

## 7. Deferred findings — none came due at this seam

Open, with conditions (details: execution log + pre-registration §9):

- **P6, C1–C6 harness, D4 (partly discharged by A11), D6, D7, PR-B** — the sweep.
- **F1 zero-intermediary guard** — due before the sweep's success criterion is finalised.
- **Consultant's two doc deferrals** (relocate the plan-review block; supersede Phase 1 log
  §2) — due at **Track 2 adoption**, which has NOT happened (P4 closing ≠ adoption).
