# Selectors that encode status, and payloads that cannot say what they cover

**Role: ACTIVE — a problem statement awaiting a maintenance session.** Nothing here is
decided, nothing is specced, and no code has been changed. Written 2026-08-09 by the `CEX-`
Task 11 execution session at the owner's instruction, **deliberately as an input to a
separate session** rather than as work done in flight.

**This document owns the reference counts in `SEL-1` and the module table in `SEL-2`.** Cite
them; do not restate them elsewhere.

**Identifier series `SEL-`** — collision-checked across every ref on 2026-08-09, zero matches.

---

## The problem in one paragraph

Several names and structures in the builder encode a fact that was true once and is not
structural: *which algorithm is in production*, *which crawl a list was censused over*, *how
many artists a crawl should fetch*. Each was accurate when written. Each has since moved, or
is about to. The failure mode is not a crash — it is a lookup that **succeeds** and returns
something subtly wrong, or a name that reads as current and is historical. In plain terms:
**the code says "production" about something that has not been in production for weeks, and
one of the three filters can silently apply a list computed over a smaller set of artists
than the one being built.**

## How this surfaced

The owner raised it after this session made the error directly. Asked what remained in Task
11, the session reported that "the shipped production behaviour is untouched" — reasoning
from `PRODUCTION_ALGORITHM` to *what production serves*. Those are different things, and
`config.py:29-33` says so explicitly. The conclusion happened to survive on an unrelated
argument (a drop list only affects future builds), but the derivation was wrong, and it was
wrong in the way a cold session is most likely to be wrong: **by trusting a constant's name
over its comment.**

Worth recording because the guard already existed. `CEX-R5` raised this exact confusion and
plan Task 7 put the warning into `config.py`. The comment did its job; the session read the
constants first. **A warning adjacent to a misleading name does not neutralise the name.**

---

## Findings

### `SEL-1` — two constants are named for a role, and the role has moved

| Code identifier | Algorithm | What it actually is |
|---|---|---|
| `PRODUCTION_ALGORITHM` | ALG-E (`contribution_5`) | the **original** 2026-07 crawl — superseded, not what production serves |
| `CANDIDATE_ALGORITHM` | ALG-B (`contribution_3`) | the **adopted lineage** — `graph-msw-tu50.bin` was built from it and `ApiConfig.graph_path` serves it |

Documented at `builder/src/artistpath_builder/config.py:29-33`.

**Blast radius, measured 2026-08-09** — this is why the answer is not a rename:

| Where | References |
|---|---|
| shipped code (`builder/src/artistpath_builder/`) | 21 |
| tests | 62 |
| **frozen scripts under `builder/analysis/`** | **23** |
| documents, incl. frozen execution logs and specs | 8 files |

The frozen column is decisive. The 2026-07-23 `hubfrac` → `top1pct_degree_frac` rename is the
worked precedent: shipped code still carries read-only aliases so those frozen probes keep
executing, and they remain deferred for removal. `CLAUDE.md` also records that a rename's
blast radius includes every document that *describes* the quantity, **including by omission**,
which no grep can find.

### `SEL-2` — population identity is implemented in one of three sibling modules

| Module | Keyed by | Carries censused population | Refuses on drift |
|---|---|---|---|
| `unlistenable_drop.py` | algorithm | ✅ count + sha256 + members | ✅ `ULC-F1` |
| `no_release_drop.py` | algorithm alone | ❌ | ❌ |
| `featured_credit_drop.py` | algorithm alone | ❌ | ❌ |

`no_release_drop.py:34-38` states the gap knowingly: *"That identity claim holds only while
one algorithm means one crawl... this module keeps the algorithm-only key deliberately, as a
frozen-era rule."* `featured_credit_drop.py:18-25` mirrors it line-for-line by design.

**The condition that made the algorithm-only key safe has now expired.** ALG-B's archive was
75,000 artists when those lists were censused; it is 117,302 after the `CEX-` extension. The
lookup still succeeds.

### `SEL-3` — what prevents that being a live defect today is data, not code

`pipeline.py:279-284` records that the three drop classes are strict subsets and that applying
all three is identical to applying `unlistenable` alone. So the two unhardened modules can
only ever **under**-apply on new artists, and `unlistenable` catches what they miss.

That property was re-verified over the extended population by the 2026-08-09 census, which
asserts it in code and exits rather than freezing anything if it fails. **So this is a
structural risk, not an open bug** — but the guard is a fact about the current data,
re-established by hand at each census, rather than something the two modules enforce.

### `SEL-4` — the constant-triple pattern does not scale to a third algorithm

Each module hand-maintains, per population: a path constant, a pinned sha256 constant, and a
dict entry. Three modules × two populations is tolerable. **A third algorithm makes it 27
hand-edited constants**, each of which is a place to make a silent mistake, and each of which
a reviewer must check individually.

### `SEL-5` — defaults that record a one-time decision

`BuilderConfig.target_artist_count = 75_000` was a decision about one run. As a default it now
silently no-ops a crawl whose `done` count already exceeds it. **This is already recorded as
`CEX-F1`** (execution log §8, due before the next crawl extension) — named here only because
it is the same class as `SEL-1` and `SEL-2`, not to duplicate it. Its remedies and condition
live there and are not restated.

---

## What is explicitly NOT claimed

- **No live defect is asserted.** `SEL-3` explains why. A maintenance session should verify
  that independently rather than inherit it.
- **No renaming is proposed.** `SEL-1`'s table is the argument against.
- **Nothing here touches the running `CEX-` track.** The Task 11 build's expected rejection is
  on acceptance bounds and is unrelated.

---

## Recommended next steps

Ordered by cost. **Only the first is proposed for near-term action.**

### R1 — add an adopted-lineage pointer (one line, forward-only)

```python
# The algorithm whose archive the ADOPTED map was built from. Status, not
# identity — this line moves when adoption moves; the ALG_* constants never do.
ADOPTED_ALGORITHM = CANDIDATE_ALGORITHM
```

New code reads `ADOPTED_ALGORITHM`; the two role-named constants decay into honest historical
labels. Touches no frozen script, no test, no document. **This is the whole of the cheap fix
for `SEL-1`.**

### R2 — generalise population identity to the other two modules

Port `unlistenable_drop.py`'s payload identity block and refusal to `no_release_drop.py` and
`featured_credit_drop.py`.

> **Trigger:** the first time a build needs either filter applied independently of
> `unlistenable`, **or** the first census where the subset property in `SEL-3` fails. Until
> then this is apparatus ahead of a decision.

### R3 — replace the constant triples with a registry

One manifest mapping population identity → payload, read by all three modules.

> **Trigger:** the arrival of a third algorithm, **or** a second extension of either archive.
> Either one makes `SEL-4`'s arithmetic bite.

### R4 — write the conventions down

Candidate wording, as siblings to the existing *"quantities carry their currency in their
name"*:

1. **Selectors name what they are, never their status.** A constant encoding a role —
   production, candidate, current, adopted — is a time bomb: the role moves and the name does
   not. Name by identity; keep status in exactly one pointer.
2. **A frozen payload is identified by the population it was computed over, not by the
   selector that chose it.** `ULC-F1` generalised.
3. **A default that records a one-time decision is not a default.** It should be required per
   invocation, or the code should refuse when the value contradicts observed state.

> **⚠ Where these live is an owner decision with a standing-layer cost.** `CLAUDE.md` is where
> the sibling convention lives, but it loads into every future session. The cheaper shape is
> the detail in a `specs/` document with a one-line pointer from `CLAUDE.md`. Whichever is
> chosen, the character cost must be reported from the diff and approved, per the budget rule.

---

## Owed at the next closeout

- A row in [`docs/README.md`](../../README.md) classifying this document.
- A mention in [`NEXT.md`](../NEXT.md) so a future session can find it.

Neither was done here: both are maintenance-track edits to documents the `CEX-` track is not
otherwise touching, and doing them in flight is what this document exists to avoid.
