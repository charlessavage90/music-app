# Findings — the label weighting and evidence probe (`WGT-`), 2026-08-01

**Role: ACTIVE — owns the `WGT-` figures.** Raw record and probes:
`builder/analysis/2026-08-01-label-weighting/`. Governing document:
[`../specs/2026-08-01-label-weighting-probe-preregistration.md`](../specs/2026-08-01-label-weighting-probe-preregistration.md),
committed before any figure existed (`d593f18`); its `WGT-AM1` corrected a definitional
gloss before any run. **Diagnostic only: nothing adopted, no `TAS-` criterion, bar,
vocabulary or substrate changed, no rebuild, no blind listen spent.**

## §0 The headline pair — quote them together

1. **Weighting is a live knob everywhere measured.** Rarity weighting alone changes
   5.3–10.8% of map connections depending on frame at the middling setting, and the
   evidence scheme 8.6–14.8% — five to fifteen times the owner's 1% materiality line —
   while individual candidate lists barely reorder. The cap converts shuffles at the cut
   line into map change, exactly as `tas_weighting` first measured on one frame.
2. **And nothing here says any weighted journey sounds better.** No offline number can;
   every road to adoption runs through the cap re-evaluation pre-registration, a rebuild,
   and the owner's ear (`REQ-38`).

**The style verdict (`WGT-2`): NOT REVERSED, both schemes.** *Plain: once rare labels
count for more, do the fine "indie rock"-type labels stop washing the signal out? No.*
Equal weighting was not the reason the Discogs style column hurt; its cost is intrinsic
on this vocabulary.

## §1 The instrument record — everything green before anything was read

| Check | Result |
|---|---|
| `WGT-0d` provenance | capture regenerated **byte-identically** to execution log §14.1's sha (`893609e9…`) |
| `WGT-0b` reproduction | committed `tas_weighting` turnovers reproduced at every λ, **and** the generalized pass produced **bit-identical fields** to the committed implementation on `W0`; all five `tas_frame_split` plain medians reproduced exactly (0.1726 / 0.16 / 0.1565 / 0.1403 / 0.1418) |
| `WGT-0a` identity | unit-weighted path = plain path, bit-identical, every frame, every λ — agreement fields and selections both |
| `WGT-0c` forced identity | λ = 0 turnover exactly 0 in every cell |

## §2 The fame-leak gate (`WGT-1`) — nothing degraded, one near-miss

Votes leak fame at Spearman **0.4345**; release-group support at **0.4983** — both under
the pre-registered 0.50 bar, so both keep their strength claims. **The RG figure missed
the bar by 0.0017.** The rule was fixed before the number existed and it holds; the
proximity is stated here so nobody later reads "passed" as "passed comfortably". The
`FPC-9` caveat rides on both figures: they are computed where fame is measurable, and
blind exactly where a leak would matter most.

## §3 The grid

**`WGT-2` deltas** (within-scheme, the only valid direction of comparison; committed
plain directions from `tas_frame_split.json` as reference):

| Isolation | rarity: spread Δ / redundancy Δ | evidence: spread Δ / redundancy Δ |
|---|---|---|
| styles onto `W1` | −0.0135 / +0.0166 | −0.0133 / +0.0091 |
| styles onto `W4` | −0.0104 / +0.0116 | −0.0114 / +0.0042 |
| genres onto `W1` | −0.0037 / +0.0014 | −0.0035 / +0.0016 |
| genres onto `W5` | −0.0006 / −0.0036 | −0.0016 / −0.0033 |

Eight of eight style signs keep the committed directions: styles cost spread and raise
redundancy under every weighting tried. The coarse genre column stays near-inert to
slightly helpful. **`W4` remains the dominant frame, now on three measurements.** Styles
also still buy zero reach — an analytic property of the carrier sets, restated in the
pre-registration before any run.

**`WGT-3` selection turnover vs plain, λ = 1.0** (full λ grid in `wgt_grid.json`):

| Frame | rarity | evidence |
|---|---|---|
| `W0` | 5.3% | 8.6% |
| `W1` | 8.9% | 12.0% |
| `W4` | 10.8% | 14.8% |
| `W5` | 8.0% | 12.0% |
| `W6` | 8.5% | 12.9% |

Median within-list rank correlations sit at 0.94–1.0 with 25–78% of lists below 0.99 —
the richer frames give weighting more artists with enough labels to act on.

**A caution on the evidence scheme, scale-free and consistent:** adding vote/support
strength raises redundancy with similarity in four of five frames (e.g. `W0` 0.182 →
0.203, `W4` 0.194 → 0.225). *Plain: well-evidenced labels sit on well-documented artists,
and similarity already knows those artists best.* Evidence weighting moves more edges
while adding less information the app did not already have.

**`WGT-6` singleton drag: negligible.** Singleton labels carry 0.2–0.6% of union mass;
excluding them changes no correlation or turnover measurably. The weighting's effect is
not an artifact of one-artist labels.

**`WGT-5`** delivered `STYLE-VOCABULARY.md` — 737 styles (not "~600"), with carrier
counts and rarity weights — and per-source rarity distributions in `wgt_tables.json`.

## §3a Five quality filters later — the style column's cost survives them all

**Owner-directed follow-up, same day, diagnostic, no bars** (`wgt_style_filters.py` /
`wgt_style_filters.json`; plain Jaccard, committed baselines reproduced before reading).
Two rival mechanisms for §3's style verdict were put to measurement: the owner's
vocabulary-quality gradient (recorded in `STYLE-VOCABULARY.md`), and **cross-source
orthographic fragmentation** — MB and Discogs spelling the same genre differently
(`drum n bass`, `rhythm & blues`, three spellings of hip-hop), raised in discussion after
the grid closed.

| Style column variant | spread Δ | redundancy Δ |
|---|---|---|
| committed full column (reference) | −0.0197 | +0.0291 |
| carrier floor ≥ 400 (the owner's "true sub-genres" band) | −0.0161 | **+0.0321** |
| carrier floor ≥ 200 | −0.0175 | +0.0299 |
| MB-vocabulary intersection | −0.0150 | +0.0270 |
| fold-normalised, onto `W1f` | −0.0196 | +0.0309 |
| fold-normalised, onto `W4f` (second isolation) | −0.0153 | +0.0245 |

- **Fragmentation is refuted as the mechanism, and the hypothesis was this session's.**
  The fold merges only 17 Discogs-only styles into MB matches (737 → 736 keys; `W0`
  2015 → 2001) and the deltas barely move (−0.0196 vs the committed −0.0197). The
  spelling variants are real — `drum n bass` alone carries 4,338 artists — but far too
  few to explain anything. Mechanistic predictions about these label sources are now
  0-for-3 in this record.
- **Filtering to the owner's best band does not rescue styles either — it makes the
  redundancy *worse* (+0.0321, the highest measured).** The recognizable sub-genres are
  precisely what similar artists already share, so the similarity score already carries
  them. *Plain: the style labels a person would actually use are the ones the app's
  similarity data already knows; the labels that would add new information are the ones
  the owner's read flagged as unusable. No filter or weighting sits between those two
  facts.*
- **The styles question is closed with a mechanism**: measured under the committed
  vocabulary, two weighting schemes, two carrier floors, a curated-vocabulary
  intersection, and a fold-normalised variant on two isolations — every one keeps both
  adverse directions. Nothing here amends `TAS-` §1; the fold's 17 merges are recorded
  for any future frame amendment, where the normaliser fix rides along for free.

## §4 The release-level question (`WGT-4`) — Branch 3, EXCLUDED

One full pass over the 345 GB (decimal) release dump — 48.7 min, 60,422 graph artists,
1,754,672 single-credit releases. All three readings, then the pre-registered rule:

| Reading | Figure | Bar | Outcome |
|---|---|---|---|
| `WGT-4a` reach | **329** artists gain a first label | ≥ 742 | no reach case |
| `WGT-4b` evidence | **28.0%** of lists reorder below 0.99 | > 25% | material |
| `WGT-4c` reissue confound | Spearman **0.406** (pressings-per-album vs fame) | ≥ 0.37 | **fired** |

**Branch 3: the ordering movement release evidence adds is fame-shaped, so `EV-R` is
excluded and the movement is recorded as a leak finding, not a signal.** *Plain: individual
pressings do change which candidates look coherent — but mostly because famous albums get
pressed more, so counting pressings smuggles fame into a coherence score.* The original
release-group-over-release preference therefore **stands under the weighting lens**, and
for a sharper reason than the coverage argument that first motivated it. The `evidence⁺`
re-run never runs; the pre-`EV-R` grid is the record.

## §5 What this licenses — the device recommendation, and its limits

Per the pre-registration §6, one input to the future cap re-evaluation pre-registration:

> **The candidate device is rarity-weighted agreement over `W4`** (artist-page labels +
> MusicBrainz release groups + Discogs coarse genre; no styles; no evidence strength).
> Rarity beats plain on the owner's stated concern (broad labels over-counted) and moves
> selection well past the materiality line; the evidence scheme adds more movement but
> pays for it in redundancy with similarity, and its strongest ingredient survived its
> gate by 0.0017. Simpler wins until something measured says otherwise.

Limits, fixed here: this is an *input*, not an adoption; a `W4` vocabulary change is a
`TAS-` §8 amendment designed cold, the owner's trigger; and no offline figure in this
probe says the resulting journeys sound better.

## §6 Two standing caveats attached to every Discogs figure, and a data asset

- **Every Discogs-derived figure here and in `TAS-`/`REL-` is a lower bound.** Discogs
  attribution goes through one MusicBrainz-sourced Discogs ID; alias releases (the same
  musician under another name — common for electronic artists) are invisible. The
  undercount sits identically in every cell, so no comparison is threatened. The unused
  `discogs_20260701_artists.xml` is **already on disk** and carries the alias/member
  tables for an exact ID join — no download and no name matching needed if a frame
  amendment is ever triggered.
- **The release pass side-collected record labels, countries and release years** per
  graph artist (`wgt_release_raw.json`; descriptive, no `WGT-` reading consumes it). The
  owner's parked label-affinity and junk-label-clustering ideas start from data now, not
  from a fresh 322 GiB stream.

## §7 Weakest links

The fame frame's blind tail sits under every leak figure in §2 and §4 — defended:
directions and contrasts; abandoned cheaply: absolute magnitudes. The spread statistic is
scale-sensitive; what is defended in §3 is the eight-sign pattern and the scale-free
redundancy reading, never a spread magnitude. And two bars resolved within 0.03 of their
thresholds (`WGT-1` RG at 0.4983 of 0.50; `WGT-4b` at 0.2797 of 0.25) — both rules held
as written, neither with room.

## §8 Operational

Grid ~35 min; release pass 48.7 min at 117 MB/s with a versioned-schema checkpoint
(restarted once, deliberately, to add the side-collection before any output existed).
Snyk over the new scripts: **4 Low findings, all the accepted CLI-path class** —
recorded for the standing `NEXT.md` row, not fixed, extending the acceptance is the
owner's. The no-release tail sample (20 artists, 7 clips resolve) is outside this probe
by its §8. **The owner's manual read is complete and recorded in `TAIL-SAMPLE.md`
beside the draw: 18 of 20 judged not journey-worthy** — contributors, one-track
features and soundtrack credits living on in similarity data — **and the two real
artists found are real precisely where MusicBrainz is blind** (Spotify-only
catalogues, no MB releases), with thin neighbours and no tag data to route them
coherently. Any filter built on "has a release" would cut both. The product
decision this opens is the owner's and is not proposed here.
