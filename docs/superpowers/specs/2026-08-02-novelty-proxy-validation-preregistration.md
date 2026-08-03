# Novelty-proxy validation — the owner's known/unknown marks against `fame_lb_pctl`

**Role: GOVERNING mini-pre-registration. Identifiers `NOV-`, collision-checked
2026-08-02 (no prior `NOV-` exists).** Committed before the owner's marks exist; the git
timestamp is the evidence.

**What this decides.** The Definitions ruling of 2026-08-02 redefined obscurity as
**novelty-likelihood** (user-relative) and named `fame_lb_pctl` as its proxy **pending
one validation** — this one. A pass adopts the proxy for offline evaluation and unblocks
the cap re-evaluation pre-registration in this currency. A fail or unreadable returns to
the owner. Nothing else is licensed.

## §1 Design

- **Truth side:** the owner marks each of the committed 30-artist corpus's artists
  **KNOWN or UNKNOWN**, where KNOWN means *he knew the artist before this project's work
  surfaced them to him* — encountering an artist through the app's journeys, the July
  bypass runs, or today's hand-read work does **not** count as knowing them. His marks
  are recorded verbatim before any comparison is computed (WGLL bound three).
- **Checklist blindness:** the sheet (`fi_novelty_checklist.md`) lists the 30 names in a
  deterministic shuffled order (seed 20260802), with **no region labels and no values**,
  so the sheet cannot rank itself.
- **`NOV-1` — separation.** AUC — the probability that a uniformly drawn KNOWN artist
  carries higher `fame_lb_pctl` than a uniformly drawn UNKNOWN artist — **≥ 0.90**, with
  **every inversion pair reported by name**. *Plain: the artists he already knew should
  essentially all sit above the artists he didn't, on the ruler that claims to predict
  exactly that.*
- **Readability floor:** at least **5 artists in each class**, else UNREADABLE — a
  near-unanimous marking gives AUC nothing to measure, and unreadable is not a pass.

## §2 Disclosures at design time

- **The corpus is bimodally drawn** (top-band artists from the July runs; tail artists
  from the obscure quarter), which makes separation easier than a uniform draw would.
  Disclosed rather than hidden: the check's teeth are the **inversions** — any artist he
  knows that the ruler calls obscure, or doesn't know that it calls famous — and the
  inversion list is a first-class output, not a footnote.
- **Ruler values for the 15 famous-band rows were previously reported to the owner** in
  the conversation of record (the `FAM-4` read). The mark "did I know this artist before
  the project" is a fact about him that a seen number cannot plausibly move; disclosed
  anyway. The 15 tail rows' values have never been surfaced to him.
- The LB reference concordances against *worldly fame* (0.4915 / 0.4552) are known and
  are **not** this criterion's construct; no figure here reads against them.

## §3 Consequences, fixed now

- **Pass →** `fame_lb_pctl` is ADOPTED as the novelty-likelihood proxy for offline
  evaluation. The Definitions entry's "pending" clause is struck; the cap re-evaluation
  pre-registration is written in this currency, inheriting the `FAM-` machinery
  (percentile formula, null rules, quantisation floor, snapshot identity) and the
  `REQ-Q1` conditions. The known-press telemetry check remains the long-run validator
  and is not waited on.
- **Fail →** the proxy is not adopted; the failure (with its inversion list) returns to
  the owner. No silent substitute; the Definitions "pending" clause stands.
- **Unreadable →** returns to the owner with the class counts; a redraw or corpus
  extension is a new amendment designed cold.
- A pass licenses **nothing about coherence** and nothing about worldly fame (barred by
  the Definitions ruling until an instrument exists).
