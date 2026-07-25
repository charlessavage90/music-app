# Frozen analysis scripts — and the 2026-07-23 rename

Every directory here is a **record of what was executed**: hardcoded paths, no
maintenance, kept so a result can be re-derived and audited. They are not tools
and are not updated when shipped code changes. The project nearly lost them
once to a scratchpad clean (Phase 1 log §2, closing note).

**One exception, and it is live:** `2026-07-24-track2-arm-scorer/` is the **active
Stage A scoring harness** — the C1–C6 scorer the next Track 2 session runs. It is a
*tool*, not yet a frozen record; it owns its figures in its own README. A reader
arriving from `docs/` reaches it via the current handoff
(`docs/superpowers/2026-07-24-HANDOFF-track2-scorer.md`) and pre-registration
amendments A12–A19. Noted here because a `docs/`-first reader would not otherwise
find it, and because it is the one directory this file's "frozen, not a tool"
framing does not yet describe.

**Its review is frozen, and it is the authority for its own measurements:**
`2026-07-24-track2-p8b-harness-review/` is the **P8b** `ml-graph-analyst` review of that
harness — the pre-registration §7 prerequisite that gated the arms. Fourteen findings
(two HIGH), the verdict "fit to run stage 1, not fit to run stage 2 as it then stood",
and the probe scripts behind each. It owns the blank-name and duplicate-name figures,
the floor-lifetime depths, and the X-bound measurement that **pre-registration A17
turns into bounds on what a result licenses** — cite it from there rather than
restating. There is deliberately **no `findings/` document** for it: a second copy
would duplicate figures, which is the one rule `docs/README.md` puts above the others.
Its F2/F3/F8/F9 fixes landed in the harness next door; F1 and F4–F11 are recorded as
amendments **A17–A19**.

## Why this file exists

On 2026-07-23 the shipped quantities were renamed so that **every popularity-
and degree-derived identifier carries its basis in its name** (the convention is
in `CLAUDE.md`). Three separate wrong conclusions in this project came from
reading one currency as another: degree as fame (log §2.6), popularity as fame
(log §2.11), and raw popularity as percentile (log §2.12).

**Nothing in this directory was renamed.** A rename here would either break the
scripts or — worse — leave them running while silently meaning something
different from the same-named quantity in shipped code.

Instead, shipped code keeps **read-only aliases** under the old names, so these
scripts keep executing unchanged. If you are comparing an old probe's output
against new code, this table says which quantities are the same quantity.

## Mapping

| Old name (still readable here) | New name in shipped code | What it actually is |
|---|---|---|
| `GraphStore.popularity` | `GraphStore.pop_raw` | log-scaled score-weighted in-degree, 0–1. **A value, not a percentile.** |
| `Graph.popularity` (builder) | `Graph.pop_raw` | same, builder side |
| `GraphStore.hub_penalty` | `GraphStore.degree_hub_penalty` | derived from **degree**, not popularity and not fame |
| `ApiConfig.w_hub` | `ApiConfig.w_degree_hub` | weight on the degree-based term above |
| `PathMetrics.hubfrac` | `PathMetrics.top1pct_degree_frac` | fraction of interior nodes in the frozen **top-1%-by-degree** set |
| `PathMetrics.mean_interior_pop` | `PathMetrics.mean_interior_pop_raw` | mean **raw** popularity of interior nodes |
| `PathMetrics.max_interior_pop` | `PathMetrics.max_interior_pop_raw` | max raw popularity of interior nodes |
| `evaluation.hub_node_set` | `evaluation.top_degree_node_set` | module-level **alias**, kept: four scripts here import it by name |
| `pathfinding.effective_floor` | `pathfinding.effective_floor_raw` | **no alias** — nothing here imports it (verified at rename time) |
| `ArtistStats.user_count` | `ArtistStats.pop_indegree_scaled` | **no alias** — builder-internal, never reached these scripts |

**Where an alias was not added, it was because nothing here needs it** —
verified by grep at rename time, not assumed. If a future reader resurrects a
script that does need one, the mapping above is the fix.

**The trap:** `summarise()` and `dataclasses.asdict(PathMetrics)` emit the
**new** keys. Result JSON written before 2026-07-23 — including
`api/eval/results-*.json` and `2026-07-22-c3-bypass-mechanisms/listen_secret.json`
— carries `"hubfrac"` and `"mean_interior_pop"`. Aliases are Python attributes
and do not appear in serialised output, so a script comparing an old JSON file
against a fresh run must map the keys itself.

**What did not change:** the two wire formats. The APG1 metadata key and the
API's JSON response field are both still `popularity`, because renaming either
would invalidate every existing artifact or break the frontend. Only in-memory
identifiers carry the currency.
