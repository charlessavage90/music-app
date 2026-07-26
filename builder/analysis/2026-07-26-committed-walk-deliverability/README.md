# Committed-walk deliverability — method, 2026-07-26

Tests `SYN-4`, the falsifier in
`docs/superpowers/findings/2026-07-26-low-degree-synthesis.md`, which was
**committed before this ran** (`c13f9a6`) so its numeric expectation could not
be shaped by the result.

**The deliverable is [`REPORT.md`](REPORT.md), which owns every figure.** Cite
it; do not restate its numbers.

| script | run from | reads | writes |
|---|---|---|---|
| `walk_deliverability.py` | `api/` | the adopted APG1 artifact + three committed `paths.json` | `deliverability.json`, stdout |

```bash
# from api/
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
  ../builder/analysis/2026-07-26-committed-walk-deliverability/walk_deliverability.py
```

Runs in seconds — it reads one binary and three JSON files, and touches neither
the crawl archive nor the network.

## Why it runs from `api/`

The APG1 reader lives in `api/` and `builder/` shares no code with it by design.
This script needs degrees, so it goes where the reader is. Same reasoning as
`2026-07-26-stranding-causes/dump_artifact_nodes.py`.

## What it does

Reads the `P` arm — the user-facing baseline (`arms.py:87`) — out of Track 2
stage 1, Track 2 stage 2 and Track 2F. Each walk is stored as artifact node
ids, so an interior card is `walk[1:-1]`. Degrees come from the artifact's CSR
offsets.

## Five gates, and what each is for

Written as aborts, because a plausible-looking wrong answer is the failure mode
this project keeps hitting:

1. **Artifact sha256** — several graphs sit in `builder/scratch/` and are not
   interchangeable.
2. **Each run's recorded `artifact_sha256`** — the walks and the degrees must
   describe the same graph, or every figure is a cross-artifact join.
3. **Id-space gate** — the committed `node_names` must agree with the
   artifact's own names at those indices. If the ids were anything other than
   artifact node indices, every degree would silently be someone else's. This
   is the gate that would have caught the class of error `MKS-` §5 describes.
4. **Byte-identity across the three runs** — `P` is deterministic, so the three
   copies must agree. They do, which makes them **one** sample rather than
   three. The first version of this script counted all three and reported 1,152
   interior cards where there are 384; the gate now enforces the correction.
5. **Void condition** — a degree-1 artist cannot be an interior card
   (`DRV-4`). One appearing would mean the extraction is wrong, and that
   reading is deliberately not available as a finding.

## Scope, stated here as well as in the report

The pair set was pre-registered for Track 2 and skews hard toward famous
endpoints, so a low share of low-degree interiors is the **expected** result.
The measurement can falsify `SYN-4`; it cannot confirm it. The distinct-artist
count is a **lower bound** on what the app could deliver, never a measure of it.

**Nothing was adopted, proposed, rebuilt or reconfigured.**
