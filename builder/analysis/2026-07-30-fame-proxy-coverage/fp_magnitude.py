"""Step 5: does multilingual pageview data change MAGNITUDE, not just coverage?

THE DISTINCTION THIS PROBE EXISTS FOR
  Coverage and magnitude are different questions and the 200-artist probe
  already separated them. Multi-language Wikipedia does NOT extend coverage
  into the obscure tail -- an artist with no article in English almost never
  has one elsewhere, because the binding constraint is encyclopedic
  notability, not language. But among artists who DO have articles, English
  pageviews may badly understate non-Anglophone acts, and that is a live and
  separate defect.

  The worked case that motivated it: Golshifteh Farahani sits in the
  artifact's BOTTOM band with 327 ListenBrainz listeners and 46 language
  Wikipedias. Most of her readership will not be on en.wikipedia. If English
  pageviews rank her near the floor while summed pageviews rank her far above
  it, the adopted proxy is not merely coarse in the tail -- it is wrong about
  a whole class of artist, in a direction that correlates with region.

WRITTEN BEFORE THE RESULT WAS SEEN
  Prediction: median English share of total pageviews is HIGH (> 0.6) for the
  artifact's typical artist, and LOW (< 0.35) for a minority whose language
  set skews non-Anglophone -- so the aggregate rank correlation between EN and
  all-language pageviews is high (> 0.9) while a materially misranked tail
  exists underneath it. A high pooled correlation is therefore NOT evidence
  the question is closed, and I commit now to reading the misranked tail
  separately rather than letting the pooled figure stand for it.

  Decision-relevant threshold, fixed now: if >= 10% of sampled artists move by
  >= 20 rank percentiles between the two rankings, multilingual pageviews are
  a materially different instrument and any Wikipedia arm of a future
  criterion must say which one it means. Below 5%, English is an adequate
  stand-in and the simpler instrument wins.

  WINDOW MATCHED DELIBERATELY to the adopted proxy's: 2025-07 .. 2026-06, the
  window asserted in ../2026-07-24-track2-fame-proxy-wikipedia/
  fetch_pageviews.py. A different window would confound instrument with
  period.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
        analysis/2026-07-30-fame-proxy-coverage/fp_magnitude.py --per-band 40
"""

from __future__ import annotations

import argparse
import json
import random
import time
import urllib.error
import urllib.parse
import urllib.request

from fp_agreement import spearman
from fp_common import BAND_ORDER, HERE, USER_AGENT, band_of, fame_frame

OUT = HERE / "fp_magnitude.json"
SEED = 20260730
WINDOW = ("2025070100", "2026063000")

WD_API = "https://www.wikidata.org/w/api.php"
PV = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article"
      "/{proj}/all-access/user/{title}/monthly/{start}/{end}")


def get_json(url: str, *, attempts: int = 4, timeout: int = 60):
    delay = 1.5
    for _ in range(attempts):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            # 404 from the pageviews API means "no data for this article in
            # this window" -- a real zero, not a failure to be retried.
            if exc.code == 404:
                return None
            if exc.code not in (429, 500, 502, 503, 504):
                raise
            time.sleep(delay)
            delay *= 2
        except (urllib.error.URLError, TimeoutError):
            time.sleep(delay)
            delay *= 2
    return None


def sitelinks_for(qids: list[str]) -> dict[str, dict[str, str]]:
    """QID -> {wiki-project: article title}. 50 per call is the API's limit."""
    out: dict[str, dict[str, str]] = {}
    for i in range(0, len(qids), 50):
        chunk = qids[i : i + 50]
        url = WD_API + "?" + urllib.parse.urlencode({
            "action": "wbgetentities", "ids": "|".join(chunk),
            "props": "sitelinks", "format": "json",
        })
        payload = get_json(url)
        for qid, ent in (payload or {}).get("entities", {}).items():
            out[qid] = {
                site: link["title"]
                for site, link in ent.get("sitelinks", {}).items()
                if site.endswith("wiki") and site not in ("commonswiki", "specieswiki")
            }
        time.sleep(0.3)
    return out


def pageviews(project: str, title: str) -> int:
    url = PV.format(
        proj=project,
        title=urllib.parse.quote(title.replace(" ", "_"), safe=""),
        start=WINDOW[0], end=WINDOW[1],
    )
    payload = get_json(url)
    if not payload or "items" not in payload:
        return 0
    return sum(item["views"] for item in payload["items"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-band", type=int, default=40)
    ap.add_argument("--pause", type=float, default=0.12)
    args = ap.parse_args()

    wikidata = json.loads((HERE / "fp_wikidata.json").read_text(encoding="utf-8"))
    frame = fame_frame()

    # Sample only artists that HAVE an English article: this probe compares two
    # magnitudes, and an artist with neither is a coverage question already
    # answered by fp_agreement.
    by_band: dict[str, list[str]] = {b: [] for b in BAND_ORDER}
    for mbid, pctl in sorted(frame.items()):
        rec = wikidata.get(mbid)
        band = band_of(pctl)
        if band and rec and rec.get("enwiki") and rec.get("qid"):
            by_band[band].append(mbid)

    rng = random.Random(SEED)
    sample: list[str] = []
    for band in BAND_ORDER:
        pool = by_band[band]
        rng.shuffle(pool)
        sample.extend(pool[: args.per_band])
    print(f"sampled {len(sample)} artists with English articles "
          f"({ {b: min(len(by_band[b]), args.per_band) for b in BAND_ORDER} })",
          flush=True)

    links = sitelinks_for([wikidata[m]["qid"] for m in sample])
    rows = []
    for n, mbid in enumerate(sample, 1):
        qid = wikidata[mbid]["qid"]
        sites = links.get(qid, {})
        totals: dict[str, int] = {}
        for site, title in sites.items():
            project = site[:-4].replace("_", "-") + ".wikipedia"
            views = pageviews(project, title)
            if views:
                totals[site] = views
            time.sleep(args.pause)
        en = totals.get("enwiki", 0)
        allv = sum(totals.values())
        rows.append({
            "mbid": mbid, "qid": qid, "band": band_of(frame[mbid]),
            "languages_with_views": len(totals),
            "en_views": en, "all_views": allv,
            "en_share": round(en / allv, 4) if allv else None,
        })
        if n % 20 == 0:
            print(f"  {n}/{len(sample)}", flush=True)

    scored = [r for r in rows if r["all_views"]]
    en_rank = {r["mbid"]: i for i, r in enumerate(
        sorted(scored, key=lambda r: r["en_views"]))}
    all_rank = {r["mbid"]: i for i, r in enumerate(
        sorted(scored, key=lambda r: r["all_views"]))}
    n = len(scored)
    moved = []
    for r in scored:
        shift = abs(en_rank[r["mbid"]] - all_rank[r["mbid"]]) / n
        r["rank_shift_pctl"] = round(shift * 100, 2)
        if shift >= 0.20:
            moved.append(r)

    rho = spearman([float(r["en_views"]) for r in scored],
                   [float(r["all_views"]) for r in scored])
    shares = sorted(r["en_share"] for r in scored if r["en_share"] is not None)
    summary = {
        "window": WINDOW, "seed": SEED, "sampled": len(rows), "scored": n,
        "rho_en_vs_all": rho,
        "median_en_share": shares[len(shares) // 2] if shares else None,
        "share_below_0.35_en": round(
            sum(1 for s in shares if s < 0.35) / len(shares), 4) if shares else None,
        "materially_misranked_share": round(len(moved) / n, 4) if n else None,
        "rows": rows,
    }
    OUT.write_text(json.dumps(summary, indent=1), encoding="utf-8")

    print(f"\nrho(EN views, all-language views) = {rho}")
    print(f"median English share of total views = {summary['median_en_share']}")
    print(f"artists with EN share < 0.35        = {summary['share_below_0.35_en']:.1%}")
    print(f"moved >= 20 rank percentiles        = "
          f"{summary['materially_misranked_share']:.1%}  "
          f"(>=10% material, <5% English is adequate)")
    print("\nlargest movers:")
    for r in sorted(moved, key=lambda r: -r["rank_shift_pctl"])[:8]:
        print(f"  {r['qid']:>10} {r['band']:>11} en_share={r['en_share']} "
              f"shift={r['rank_shift_pctl']}pctl langs={r['languages_with_views']}")
    print(f"\n-> {OUT.name}")


if __name__ == "__main__":
    main()
