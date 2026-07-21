# External reference material — not project documentation

**Role: EXTERNAL.** Nothing in this directory is project documentation, and none of it
should be loaded as context for development work.

These are third-party materials consulted during **early project planning**. They
informed decisions that are now recorded properly in `../superpowers/specs/` and
`../superpowers/findings/`. Those documents are the record; these are the raw inputs.

**Do not:**
- cite anything here as a project decision or a source of truth;
- load these files as context on a routine basis — `similarity.md` alone is ~1,600 lines
  of extracted PDF text and will crowd out documentation that actually applies;
- infer that a technique described here is used in this project. Mostly they are not.

**Do:** read a specific section if a spec or finding explicitly points you here for
background on a decision.

## Contents

| File | What it is |
|---|---|
| `similarity.md` | Korzeniowski, Oramas & Gouyon, *"Artist Similarity for Everyone: A Graph Neural Network Approach"* — an academic paper on GNN-based artist similarity, extracted from PDF. Considered during early planning; **the approach it describes is not what this project implements.** |
| `sample-ai-prompt` | A prompt kept from early planning. Historical. |

For what this project actually does and why, start at `../README.md`.
