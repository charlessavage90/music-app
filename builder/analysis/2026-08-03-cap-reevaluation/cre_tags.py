"""`CRE-T6` -- the `S2` agreement tables: real, label-scramble, vote-scramble.

The measure is `wav_read`'s **`evidence_rel`**, verbatim:

    a(u,v) = Σ idf·min(r_u, r_v) over (labels_u ∩ labels_v)
           ÷ Σ idf·max(r_u, r_v) over (labels_u ∪ labels_v)

where `r` is the within-artist relative vote weight `e_rel` (`rel_table` /
`rel_for`). `WAV-0d`'s degeneracy proof is what guarantees the dark-tail rule:
where votes are absent or unusable (`s_max <= 1`) every `r` is 1.0 and the measure
**reduces exactly to rarity-weighted agreement**, so an artist with no vote
evidence is scored by rarity alone rather than penalised.

`a(u,v)` is `None` where either endpoint carries no `W4` label. The neutral rule
that fills those in lives at the point of use (`cap_tag_limited`), not here, so
the table stays a measurement and the device stays a device.

**One table per kind, built ONCE and applied by MBID in every cell** -- the
factor-table discipline: the agreement a pair carries must not vary with the cell
it is measured in.

- **`real`** -- `W4` from `five_frames()`, idf over `W4` at the adopted node
  count, `e_rel` from `wav_read.masses()`.
- **`label_scramble`** -- `TAS-AM3b`'s stronger null: permute label SETS among
  **labelled** artists only, so exactly which artists are labelled is held fixed
  and only the semantics move.
- **`vote_scramble`** (`CRE-AM1`) -- per artist, permute the label→strength
  assignment among **its own** labels before the `e_rel` normalisation. Preserves
  each artist's vote-distribution shape exactly; destroys which tag each vote
  attaches to. This is the attribution companion `CRE-AM1` requires before any
  conclusion credits the votes.
"""
from __future__ import annotations

import math
import random

from cre_common import use_frozen

use_frozen("tag_disc", "rel", "wgt", "wav", "track_b")

from tas_common import GLOBAL_NEUTRAL_FALLBACK  # noqa: E402,F401
from tas_frame_split import five_frames  # noqa: E402
from tas_guard import permuted_labels_among_labelled  # noqa: E402
from tas_weighting import idf_table  # noqa: E402
from wav_read import masses, rel_for, rel_table, strength_of  # noqa: E402

SEED = 20260803
KINDS = ("real", "label_scramble", "vote_scramble")


def _rel_table_vote_scrambled(per: dict, seed: int = SEED):
    """`wav_read.rel_table` with ONE change: within each artist, the combined
    per-label strengths are permuted among that artist's own labels before the
    log1p normalisation.

    Mirrored rather than called because the permutation has to happen at the
    combined-strength level -- `strength_of` sums the four sources, so permuting
    any single source would change the joint distribution instead of preserving
    it. The multiset of strengths per artist is preserved exactly, which is the
    property `test_cre_tags` pins.

    `random.Random(f"{seed}:{mbid}")` is per-artist so the result is independent
    of dict iteration order (determinism, spec §9).
    """
    rel: dict[str, dict[str, float]] = {}
    smax: dict[str, float] = {}
    for m, src in per.items():
        labs = set().union(*(src[k].keys() for k in src)) if src else set()
        s_by: dict[str, float] = {}
        for lab in labs:
            s = strength_of(src, lab)
            s_by[lab] = 1.0 if s <= 0 else s

        # --- the one change -------------------------------------------------
        keys = sorted(s_by)
        vals = [s_by[k] for k in keys]
        random.Random(f"{seed}:{m}").shuffle(vals)
        s_by = dict(zip(keys, vals))
        # --------------------------------------------------------------------

        mx = max(s_by.values(), default=0.0)
        smax[m] = mx
        if mx <= 1.0:
            rel[m] = {lab: 1.0 for lab in s_by}
        else:
            n = math.log1p(mx)
            rel[m] = {lab: min(1.0, math.log1p(s) / n) for lab, s in s_by.items()}
    return rel, smax


class EdgeAgreement:
    """`evidence_rel` over a fixed label frame and vote table."""

    def __init__(self, kind: str, labels: dict[str, set[str]],
                 idf: dict[str, float], rel: dict, smax: dict) -> None:
        self.kind = kind
        self._idf = idf
        self._labels = labels
        # Materialise each artist's frame-filtered rel once; `.a` is called
        # O(edges) times inside the ceiling loop.
        self._r = {m: rel_for(rel, smax, m, labs)
                   for m, labs in labels.items() if labs}

    def labelled(self, mbid: str) -> bool:
        return bool(self._labels.get(mbid))

    def a(self, u: str, v: str) -> float | None:
        lu = self._labels.get(u)
        lv = self._labels.get(v)
        if not lu or not lv:
            return None
        ru, rv = self._r[u], self._r[v]
        idf = self._idf
        inter = lu & lv
        union = lu | lv
        un = sum(idf.get(x, 0.0) * max(ru.get(x, 0.0), rv.get(x, 0.0))
                 for x in union)
        if un <= 0:
            return None
        inn = sum(idf.get(x, 0.0) * min(ru[x], rv[x]) for x in inter)
        return inn / un


# Keyed on (kind, n_artists), NOT on kind alone. `idf` below is computed AT
# n_artists, so a table built at one value is the wrong table at another -- and a
# kind-only key returns before n_artists is ever consulted, so a second caller
# passing a different value would silently receive the first caller's table. Every
# caller today passes the same value, which is precisely why the defect would have
# surfaced as a wrong figure rather than as an error.
_CACHE: dict[tuple[str, int | None], EdgeAgreement] = {}


def agreement_table(kind: str, n_artists: int | None = None) -> EdgeAgreement:
    if kind not in KINDS:
        raise ValueError(f"unknown agreement kind {kind!r}; expected {KINDS}")
    key = (kind, n_artists)
    if key in _CACHE:
        return _CACHE[key]

    w4 = five_frames()["W4"]
    if n_artists is None:
        n_artists = len(w4)
    per = masses()

    if kind == "real":
        labels = w4
        rel, smax = rel_table(per)
    elif kind == "label_scramble":
        labels = permuted_labels_among_labelled(w4, seed=SEED)
        rel, smax = rel_table(per)
    else:  # vote_scramble
        labels = w4
        rel, smax = _rel_table_vote_scrambled(per, seed=SEED)

    # idf is computed over the REAL W4 in every kind: the scrambles are controls
    # on the device, not on the rarity frame, and re-deriving idf per kind would
    # move a second knob.
    idf, _df = idf_table(w4, n_artists=n_artists)
    table = EdgeAgreement(kind, labels, idf, rel, smax)
    _CACHE[key] = table
    return table


class AllNone:
    """The degeneracy table (`WAV-0d` pattern): `a` is undefined everywhere, so
    every `a_eff` collapses to one constant and `cap_tag_limited` must reproduce
    `cap_trimmed_union(trim="weakest_first")` EXACTLY."""

    kind = "all_none"

    def labelled(self, mbid: str) -> bool:
        return False

    def a(self, u: str, v: str) -> float | None:
        return None
