# Featured-credit filter census (2026-08-03)

The detector census for the featured-credit filter track — the owner-triggered
extension of the adopted no-release drop rule to artists that exist in the graph only
through shared release-group credits (fame-instrument execution log §5a).

**Figures live in the committed JSONs here and are cited, never restated.** Reasoning:
`docs/superpowers/2026-08-03-featured-credit-filter-execution-log.md`. The rule
document (written cold, before any clip result) governs what is adopted; nothing in
this directory adopts anything.

Scripts, in run order (from `builder/`, `UV_LINK_MODE=copy PYTHONIOENCODING=utf-8
uv run python -u …`; no CLI arguments by design):

- `fcf_census.py` — the credit split (total / sole / first-listed) over the MB
  release-group dump for the union of both censused populations; class membership;
  DSP-link and Discogs-id columns; worked-instance checks. → `fcf_census.json`
- `fcf_discogs.py` — resolves the class members' Discogs ids the REL- census never
  saw (57 GB XML pass), so the rule document can fix whether Discogs presence exempts
  from the class. → `fcf_discogs.json`
- `fcf_clips.py` — the keep-check's network half (FCF-2), run only after the rule
  document was committed. Resolver imported from `tail_clips`, never restated;
  resumable; refuses to summarise while any refusal remains (FCF-3).
  → `fcf_clips.json`
- `fcf_droplist.py` — applies the committed rule to the committed captures, verifies
  the FCF-5 worked-instance outcomes, and freezes one list per population.
  → `fcf_droplist.json` (adopted), `fcf_droplist_algb.json` (candidate) — the files
  the builder wiring copies verbatim into package data.

- `fcf_discogs_split.py` — owner-prompted: splits the Discogs exemptions into
  sole-credit vs shared-credit-only, after his spot checks found the shared-credit
  shape. → `fcf_discogs_split.json`. Its result is what prompted `FCF-AM1`.
- `fcf_clips_am1.py` — the amendment's incremental keep-check over the
  shared-credit-only members, run only after `FCF-AM1` was committed.
  → `fcf_clips_am1.json`
- `fcf_droplist_am1.py` — re-applies the amended rule whole, asserts no
  pre-amendment verdict flips, and freezes the superseding lists.
  → `fcf_droplist_am1.json`, `fcf_droplist_algb_am1.json` — what the package data
  now carries. The pre-amendment freezes stay here as the record.

The rule document governing all of it:
`docs/superpowers/specs/2026-08-03-featured-credit-filter-rule.md` (`FCF-`,
amended by `FCF-AM1` with post-result disclosure).

Reuse is by import, never restatement: populations and dump passes come from
`ctc_census` (2026-08-02-candidate-tail-census), the adopted artifact identity from
`cb_metrics` (2026-07-30-track-b-cap-selection).
