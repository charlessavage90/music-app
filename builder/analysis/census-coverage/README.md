# Census coverage store (`ULC-F2`)

**Role: ACTIVE data store — the one directory under `analysis/` that is neither a
frozen record nor a tool.** Censuses **read** it and **write back** what they freshly
learn, so a crawl extension pays dump passes only for genuinely new artists. First
writer: `../2026-08-05-ulf-census/ulf_census.py` (the `ULF-` filter census, rule
document `docs/superpowers/specs/2026-08-05-unlistenable-filter-rule.md`).

**`ulf_coverage.json` is deliberately untracked** (the `REL-` raw-output template:
large, regenerable, derived summaries committed elsewhere). It is **machine-local
state on the machine that has the MB dumps** — the dumps under `builder/scratch/`
are not in git either, so committing the store would buy a fresh clone nothing it
could extend. What IS committed: the census scripts that regenerate it, and the
frozen list payloads derived from it.

**Do not delete it casually.** Regeneration costs about an hour of dump passes over
~50 GiB, which is exactly the cost this store exists to stop re-paying. The project
has nearly lost `analysis/` state to a scratchpad clean once before.

Schema: `{"artists": {mbid: record}}`, where each record's fields each carry their
own provenance (`d2` + `d2_src`, `dsp`/`discogs`/`deezer` + `signals_src`,
`clip_resolves` + `clip_src`). **Absence of a field means UNKNOWN, never false** —
that distinction is what the `ULC-` census's committed output could not express,
and losing it is how an expansion silently under-censuses.
