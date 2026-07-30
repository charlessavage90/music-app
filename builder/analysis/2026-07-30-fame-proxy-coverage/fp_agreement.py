"""Steps 3-4: banded coverage and agreement across three instruments.

THE THREE INSTRUMENTS, IN THEIR OWN CURRENCIES -- NOT INTERCHANGEABLE
  in-graph pop_pctl  score-weighted in-degree, percentile. Computed from the
                     SAME edges the router traverses, so it cannot audit
                     itself. Circular by construction, not by defect.
  LB total_user_count  distinct ListenBrainz listeners. Same corpus as the
                     similarity edges, so population-CONSISTENT but not
                     population-NEUTRAL -- consistency makes bias invisible,
                     not absent.
  Wikipedia sitelinks  how many language Wikipedias carry an article. The only
                     one of the three INDEPENDENT of our corpus, which is the
                     property that makes it worth keeping whatever else is
                     true of it.

WRITTEN BEFORE THE RESULT WAS SEEN
  Already known, not predicted: LB coverage is 99.94% over the artifact
  (74,151/74,193) -- that run is done and its figure is not a forecast.

  Predicted here:
   (a) Wikidata/EN-article coverage falls off a cliff below the median. The
       200-artist stratified probe measured 100/100/78/72/25 percent by band;
       the lower half is ~50% of the artifact, so I expect MORE THAN HALF the
       graph to carry no English article -- i.e. to be a single indistinct
       value to the adopted fame ruler.
   (b) any-language coverage adds LITTLE over English. The same probe found
       22% vs 20% in the bottom band, one artist in forty. If multi-language
       adds more than 5 points anywhere, prediction (b) is wrong and the
       Western-bias argument for multilingual pageviews gets stronger, not
       weaker.
   (c) LB-vs-sitelinks agreement is strong ACROSS bands and weak WITHIN them
       -- the signature of two instruments that agree about who is famous and
       disagree about ordering among peers. Within-band rho < 0.5 expected.

  A caveat that bites (a) and (b) and is stated in advance: this sample is the
  artifact's own population, which is LB-skewed, so non-Western artists are
  under-represented before anything is measured. That biases (b) TOWARD
  confirmation. It is evidence about our graph, not about Wikipedia.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_agreement.py
"""

from __future__ import annotations

import json

from fp_common import BAND_ORDER, HERE, band_of, fame_frame

OUT = HERE / "fp_agreement.json"


def spearman(xs: list[float], ys: list[float]) -> float | None:
    """Rank correlation. Ties averaged; the cost function cares about ORDER."""
    if len(xs) < 8:
        return None

    def rank(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for t in range(i, j + 1):
                out[order[t]] = (i + j) / 2 + 1
            i = j + 1
        return out

    rx, ry = rank(xs), rank(ys)
    n = len(xs)
    mx, my = sum(rx) / n, sum(ry) / n
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return round(num / den, 4) if den else None


def main() -> None:
    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    lb = json.loads((HERE / "fp_listenbrainz.json").read_text(encoding="utf-8"))
    frame = fame_frame()

    rows: dict[str, dict] = {b: {"n": 0, "lb": 0, "wd": 0, "en": 0, "any": 0,
                                 "xs": [], "ys": []} for b in BAND_ORDER}
    for mbid, pctl in frame.items():
        band = band_of(pctl)
        if band is None:
            continue
        r = rows[band]
        r["n"] += 1
        wrec = wikidata.get(mbid)
        lrec = lb.get(mbid)
        if lrec:
            r["lb"] += 1
        if wrec:
            r["wd"] += 1
            if wrec.get("enwiki"):
                r["en"] += 1
            if wrec.get("wikis", 0) > 0:
                r["any"] += 1
        if lrec and wrec and wrec.get("wikis", 0) > 0:
            r["xs"].append(float(lrec["users"]))
            r["ys"].append(float(wrec["wikis"]))

    out = {}
    for band in BAND_ORDER:
        r = rows[band]
        n = max(r["n"], 1)
        out[band] = {
            "artists": r["n"],
            "lb_covered": round(r["lb"] / n, 4),
            "has_wikidata": round(r["wd"] / n, 4),
            "has_en_article": round(r["en"] / n, 4),
            "has_any_language_article": round(r["any"] / n, 4),
            "multilang_gain_points": round((r["any"] - r["en"]) / n * 100, 2),
            "rho_lb_vs_sitelinks_within_band": spearman(r["xs"], r["ys"]),
            "n_both_signals": len(r["xs"]),
        }

    total = sum(r["n"] for r in rows.values())
    at_floor = total - sum(r["en"] for r in rows.values())
    allx = [x for r in rows.values() for x in r["xs"]]
    ally = [y for r in rows.values() for y in r["ys"]]
    out["_whole_artifact"] = {
        "artists": total,
        "lb_covered": round(sum(r["lb"] for r in rows.values()) / total, 4),
        "at_wikipedia_floor": at_floor,
        "at_wikipedia_floor_share": round(at_floor / total, 4),
        "rho_lb_vs_sitelinks_pooled": spearman(allx, ally),
        "duplicate_mbid_to_two_items": sum(
            1 for v in wikidata.values() if v and v.get("duplicate_item")
        ),
    }

    OUT.write_text(json.dumps(out, indent=1), encoding="utf-8")

    print(f"{'band':>12} {'artists':>8} {'LB':>7} {'wikidata':>9} {'EN art':>7} "
          f"{'any-lang':>9} {'+pts':>5} {'rho(LB,wikis)':>14}")
    for band in BAND_ORDER:
        r = out[band]
        rho = r["rho_lb_vs_sitelinks_within_band"]
        print(f"{band:>12} {r['artists']:>8} {r['lb_covered']:>6.1%} "
              f"{r['has_wikidata']:>8.1%} {r['has_en_article']:>6.1%} "
              f"{r['has_any_language_article']:>8.1%} "
              f"{r['multilang_gain_points']:>5.1f} "
              f"{'--' if rho is None else format(rho, '+.3f'):>14}")
    w = out["_whole_artifact"]
    print(f"\nwhole artifact: {w['artists']} artists, "
          f"{w['at_wikipedia_floor']} ({w['at_wikipedia_floor_share']:.1%}) "
          f"at the Wikipedia floor")
    print(f"pooled rho(LB users, language count) = {w['rho_lb_vs_sitelinks_pooled']}")
    print(f"MBIDs mapping to two Wikidata items: {w['duplicate_mbid_to_two_items']}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
