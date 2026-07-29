# Track 3b — the thresholded toll: analysis directory

Governing document:
`docs/superpowers/specs/2026-07-29-track3b-thresholded-toll-preregistration.md`.

Artifact for everything here: `builder/scratch/graph-t15-tiebreakfix.bin`, sha256
`4cb84ef9…b061dc8` — asserted by every script (TB-G3). N = 74,193, E = 898,006
directed CSR entries.

**Currency notice.** Every figure these scripts produce is in in-graph popularity
percentile (`MirrorContext.pctl`, average rank over `pop_raw`) or in cost units, except
where a committed fame table is joined and the join is labelled. `pctl` is never a fame
claim (Phase 1 log §2.11).

## Scripts

| script | what it computes | reads | writes |
|---|---|---|---|
| `tb_p1_probe_dose.py` | TB-P1(a): the knee's set identity at pctl 0.90; the pctl distribution of production's scored C1-window interiors on `pairs_v2.json`; realised toll per interior and per path at each ladder dose and at Track 3's, in `w_hop` units; DD-D4's floor bases recomputed; adjacency of every pair; TB-C2's surviving-pair arithmetic | artifact, `2026-07-28-track3-depth-descent/{t3_paths,pairs_v2}.json`, `2026-07-24-track2-arm-scorer/paths.json` | stdout only |
| `tb_p1_probe_ceiling.py` | TB-P1(b): TB-P3's ceiling (base-cost-minimal path in the induced sub-decile subgraph, endpoints exempt, P's exclusion sets applied) per C1-window cell; a self-check that the probe's own production cost reproduces P's delivered path; `w*` per cell; the static finite-dose optima at the ladder's three doses; comparison against DD-D6's committed LIMIT path | artifact, `2026-07-28-track3-depth-descent/{pairs_v2,t3_paths,gap_paths,gap_fame}.json` | `tb_p1_ceiling.json` |
| `tb_p1_probe_dormant.py` | TB-P1 general check: whether production's victims are ever sub-decile (the §0 dormant-term question); LIMIT vs ceiling in pctl currency; TB-P2 fetch sizing; TB-C1 / TB-C4 cell arithmetic | artifact, `2026-07-28-track3-depth-descent/{pairs_v2,t3_paths,gap_paths,t3_fame,gap_fame}.json` | stdout only |

All three are read-only with respect to committed Track 2 / Track 3 artefacts: they
import `mirror.py` and `run_arms.walk` and edit nothing.

## How to run

```bash
cd builder
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-29-track3b-thresholded-toll/tb_p1_probe_dose.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-29-track3b-thresholded-toll/tb_p1_probe_ceiling.py
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
    analysis/2026-07-29-track3b-thresholded-toll/tb_p1_probe_dormant.py
```

`tb_p1_probe_ceiling.py` re-walks production for all 12 scored pairs and asserts its own
cost implementation reproduces P's delivered path on every C1-window cell before any
other figure is printed. If that assertion fails, nothing else in its output may be read.
