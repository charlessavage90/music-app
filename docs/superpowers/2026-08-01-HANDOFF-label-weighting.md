# Handoff — the label weighting and evidence probe (`WGT-`), 2026-08-01

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-08-01-HANDOFF-tas5-routing.md`](2026-08-01-HANDOFF-tas5-routing.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which
owns it.

**This is a SEAM handoff.** Everything is committed and pushed, nothing is in flight, no
subagent is running, no background job survives, no port is listening, and the tree is
clean. The probe was designed, pre-registered, executed through every reading, extended
twice at the owner's direction, and written up in one session. PR stacks on #58.

## What this work is

Governing document:
[`specs/2026-08-01-label-weighting-probe-preregistration.md`](specs/2026-08-01-label-weighting-probe-preregistration.md)
(committed before any figure; `WGT-AM1` is pre-results and says so). Figures:
[`findings/2026-08-01-label-weighting-probe.md`](findings/2026-08-01-label-weighting-probe.md)
— **read its §0 pair together, always.** Record:
[`2026-08-01-label-weighting-execution-log.md`](2026-08-01-label-weighting-execution-log.md).
Probes: `builder/analysis/2026-08-01-label-weighting/`.

## The five things that must not be reverted

1. **The style column is CLOSED with a mechanism, not just a verdict.** Eleven readings —
   two weighting schemes, two carrier floors, a curated-vocabulary intersection, a
   fold-normalised variant on two isolations — all keep both adverse directions. The
   recognizable styles are the ones similarity already knows (findings §3a). Do not
   re-propose style filtering without new grounds; the grounds tried are enumerated.
2. **`EV-R` (release-level evidence) is EXCLUDED as fame-shaped** — `WGT-4` Branch 3, the
   pre-registered rule firing, not a judgement. The album-level preference stands for a
   sharper reason than the coverage argument that first made it.
3. **The device recommendation is an INPUT, not an adoption**: rarity-weighted agreement
   over `W4`, no styles, no evidence strength. It goes to a future cap re-evaluation
   pre-registration designed cold. A `W4` vocabulary change remains a `TAS-` §8
   amendment, the owner's trigger; the blind listen (`REQ-38`) is unspent.
4. **Two bars resolved within 0.03 of their thresholds and the findings say so** (`WGT-1`
   RG at 0.4983 of 0.50; `WGT-4b` at 0.2797 of 0.25). Both rules held as written. Do not
   tidy the proximity language away, and do not re-argue the bars — no bar may move now
   that results exist.
5. **The owner's two manual records are data, not prose** — his 20 tail verdicts in
   `TAIL-SAMPLE.md` (18 of 20 not journey-worthy; the 2 real ones are MB-blind) and his
   style-vocabulary calibration read in `STYLE-VOCABULARY.md`. Preference records in the
   `WHAT-GOOD-LOOKS-LIKE` sense: no threshold may be read off them; a criterion
   contradicting them is wrong.

## Status of `TAS-` — unchanged by this work

**⚠ CORRECTED 2026-08-01 (latest): `TAS-` Task 8 has since been WRITTEN.** The findings are
[`findings/2026-07-30-tag-discrimination.md`](findings/2026-07-30-tag-discrimination.md), the
owner-facing read is execution log §17, and the `TAS-` probe is complete through all eight
tasks. *(As written at this handoff's seam, and true then:)* **`TAS-` Task 8 (its findings
document) is still owed and still unwritten.** This probe is a successor investigation, not
that document. The `TAS-` handoff below remains authoritative for its track's internals.

## The open decision, and what I would do

**Whether to pull the cap re-evaluation (#4 in the owner's ordering, the mutual-k-NN
re-question) now that its device input exists.** If I were continuing: write that
pre-registration next, cold, naming (`W4`, rarity) as its single fixed device, Track B's
results as its measured input, and the owner's premise about source-data reciprocity as a
stated assumption to verify against the `LBS-` findings from source. What I would not do:
any further label-side measurement first — the device question is as answered as offline
measurement gets, and more sharpening spends time the cap question does not need.

## Already updated — do not re-edit

`NEXT.md` (rewritten at this closeout), `docs/README.md` (rows for the spec, findings,
log and this handoff; the `TAS-` handoff row's supersession), the `REL-` closed-row
correction (dump not deleted), the predecessor handoff's role line, `TEST-QUEUE.md` (new
N/A entry), and the four new Snyk Lows folded into the standing acceptance row.

## What I know that is not otherwise in the durable record

- **The capture lives in a session scratchpad and dies with it** — regenerate via
  `td_capture.py` (~8 min); the sha to expect is in the `TAS-` log §14.1 and
  `wgt_grid.py`. Three consecutive regenerations have been byte-identical.
- **The shell's working directory persists across tool calls here** — three background
  launches failed or misfired on `cd builder` assumptions this session. Launch with
  absolute paths.
- **`wgt_release_raw.json` holds the label/country/year side-collection** nothing
  consumes yet; its checkpoint schema is versioned (`CKPT_SCHEMA = 2`) so a stale
  checkpoint refuses to resume rather than corrupting a restart.
- **The fold rules live in `wgt_style_filters.fold_label` with unit checks inline** — 17
  style merges; if a frame amendment ever lands, the normaliser fix rides along free.
