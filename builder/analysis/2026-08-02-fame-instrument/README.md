# Fame-instrument adoption — working directory

Governing document:
`docs/superpowers/specs/2026-08-02-fame-instrument-adoption-preregistration.md` (`FAM-`).
Execution log: `docs/superpowers/2026-08-02-fame-instrument-execution-log.md`.

Contents:

- `fam-prereg-critique.md` — the `ml-graph-analyst` design critique of the committed
  pre-registration, run **before** the union fetch. Its findings are dispositioned in
  `FAM-AM1` (normative changes) and the execution log §2 (full disposition table).
- `fam_probe.py`, `fam_probe2.py` — the critique's read-only probes over the retained
  2026-07-30 snapshot (`../2026-07-30-fame-proxy-coverage/fp_listenbrainz.json`,
  uncommitted, sha256 `c47fbd22…`) and the two graph artifacts. They write nothing and
  take no CLI arguments. Retained because `FAM-AM1`'s disclosure cites their figures.
- `fi_*.py` (added by execution tasks) — the union fetch and validation scripts.

Snapshot files (`fi_*.json` fetch outputs) are gitignored like all large captures; each
carries a committed manifest sidecar with sha256 and date. Not covered by builder
`testpaths` (frozen-probe convention, owner ruling 2026-08-01).
