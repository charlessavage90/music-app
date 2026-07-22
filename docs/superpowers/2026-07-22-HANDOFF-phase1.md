# HANDOFF — Phase 2 is closed; Phase 1 needs planning

**Role: ACTIVE.** Written 2026-07-22 at Phase 2 closeout, for a session with no prior
context. Delete once Phase 1 has a written plan.

---

## 1. Where things stand

**Phase 2 (path quality) is COMPLETE.** The owner ran a blind listening test between two
graph arms and chose **`capfix`**. Adopted config, now the default in
`builder/src/artistpath_builder/config.py`:

| Knob | Value |
|---|---|
| `cap_strategy` | `mutual_knn` |
| `similarity_rescale` | `p99_log_clip` |
| `similarity_damping` | `0.0` |

The losing options (`pre_symmetrise`, `percentile_rank`) are **deleted from the code and
raise**. Damping stays a supported float knob.

Read **execution log §16 (verdict) and §17 (adoption)** before anything else in
`docs/superpowers/`. Where another document disagrees with those two sections, they win.

**Next action: plan Phase 1.** It is unplanned. It leads with **C3**.

---

## 2. Claims that were overturned — do not "correct" them back

A well-meaning editor reading older prose will find confident statements that measurement
has since killed. All three are recorded in the roadmap's Phase 2 section and the
execution log.

- **Damping was the predicted fix. It was tested at 0.25 / 0.5 / 0.75 and REJECTED** — the
  undamped arm won. Older docs (and the roadmap's own C4 line, historically) frame damping
  as the thing Phase 2 would adopt. It is not.
- **Neighbour-set Jaccard was to be the "primary, score-independent objective." It was not
  adopted.** The overlap-family metrics sign-flip between analysis and held-out slices at
  these effect sizes — adjudication §6 claims 41–42. That is a finding about the
  *instrument*, and it would have held identically had it favoured the other arm.
- **The p99 ceiling defect was NOT fixed.** The adopted rescale is still the clip. The rank
  transform that removes the ceiling *lost* the blind test. The defect is real, carried
  forward, and explicitly not closed.

---

## 3. Already updated — do not re-edit

`CLAUDE.md` (orient table, graph-shape section, gitignore paragraph), `docs/README.md`
(current state + document roles), the roadmap (Phase 1 and Phase 2 sections), the Phase 2
spec (status line), `builder/.../config.py`, `api/.../config.py`, and execution log
§§16–17. The blind-test handoff has been deleted per its own instruction.

---

## 4. What Phase 1 has to cover

**C3 leads, and it is a pathfinding defect, not a UX item** (revised plan §6). `w_floor` is
a no-op and `known` degrades to a bare hard exclusion. It is a direct contributor to the
founding complaint — rerolls returning artists at the same popularity band. Filing it under
"bypass" next to button fixes is part of why it sat unscheduled behind sixteen tasks of
graph work.

Then: clips (C1 artist matching, C2 cache identity vs signed URL), then frontend UX. Full
list in the roadmap's Phase 1 section, including the two carried-in items with success
conditions.

---

## 5. What I know that is not obvious from the record

Three things worth having in the room when Phase 1 is planned.

**The channel that decided Phase 2 is one nothing measures.** The owner's verdict rested
almost entirely on **bypass behaviour** — how paths evolve over repeated rerolls. On
first-generated paths with no bypass, he judged the two arms *mostly similar*. The entire
six-arm sweep measured first paths. So the metric suite and the thing that actually decided
the phase are looking at different objects. Any Phase 1 tuning that optimises first-path
metrics is optimising the channel the owner found least informative.

**His stated target for bypass, in his own words** (execution log §16 — he corrected an
earlier paraphrase of mine, and the correction is the point):

> first paths are *expected* to favor hubs more so than bypassed paths. When tuning and
> adjusting, we're not aiming for a result like "first paths should never hit hubs". Part
> of our desired behavior however is that more bypasses (and especially bypasses of hubs)
> should result in fewer and fewer hubs in each iteration.

So the target is a **monotone decline in hub incidence across successive bypasses**, not a
hub-free first path. A tuning run that suppressed hubs in the first path would look like
success and miss the goal entirely. He flagged this as gut instinct rather than data and
explicitly deferred adjudicating it — it is a hypothesis to test, not a settled
requirement.

**A listening test has real coverage limits, and he named them.** Some obscure artists are
absent from the graph (e.g. Bee Caves), and obscure artists he does not personally know
(e.g. Lang Lang) are hard for him to evaluate. So the obscure tail — exactly what bypass is
supposed to reach — is the region a listening test probes worst. If Phase 1 needs evidence
about the tail, it needs an instrument other than the owner's ear.

---

## 6. Traps that are still live

- `UV_LINK_MODE=copy` on every `uv` command (OneDrive breaks hardlinks).
- `PYTHONIOENCODING=utf-8` on anything printing artist names.
- `python -u` / `PYTHONUNBUFFERED=1` for long background jobs, or the log is 0 bytes and the
  job looks dead while running fine.
- **Graph artifacts are gitignored; a checksum is their only identity.** Several graphs sit
  in `builder/scratch/` and they are **not** interchangeable. The adopted one is
  `graph-t15-capfix.bin`, sha256
  `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237`.
- The 500-node test fixtures **are** committed now (they were silently not, until
  2026-07-22 — see execution log §17). The 5k dev graph is not; build it or copy it.
