# CRE pre-registration critique — frozen record (2026-08-03)

**Role: COMPLETE, frozen.** The committed record of the two pre-run reviews of
`docs/superpowers/specs/2026-08-03-cap-reevaluation-preregistration.md`, dispatched at
the owner's instruction on 2026-08-03, **before any CRE arm was built or run and before
the pre-registration merged**. The prereg's §9 revision record is the consumer; the
reviews' surviving findings were folded into the document while it was still free to
amend.

- `cre-analyst-critique.md` — the `ml-graph-analyst` report. **Owns the figures it
  states** (measured over committed artifacts and committed Track 3 / Track B outputs;
  no Track B cell was re-run, no repo file was modified by the review). Two of its
  measurements are result-bearing for the revised design and are disclosed in the
  prereg's §9: the `CRE-D1` direction measurement (probe 3b) and the incumbent-supply
  pricing prior (probe 9).
- `cre-repo-check.md` — the general-purpose repo-check report ("check the document's
  claims against the repo"). Findings plus its verified-clean coverage list.
- `cre_probe1.py` … `cre_probe10.py` (incl. `cre_probe3b.py`) — the probe scripts the
  analyst report cites, **committed as-executed and frozen**. They are the record of
  what the critique ran, not maintained instruments: hardcoded paths, no tests, not
  collected by any suite (`testpaths` stays `["tests"]` by owner ruling). Do not edit;
  a future measurement wanting one of these starts a new script in a new directory.
- The analyst's probe outputs were not separately captured as JSON; the figures live in
  the report itself, which for this directory is the authoritative statement of them.

**Reading order:** the prereg §9 first (what changed and why), then the two reports.
The prereg governs wherever a report's proposal was adjusted rather than adopted
verbatim — §9 lists each divergence.
