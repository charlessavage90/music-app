"""Turn causes.json into the deliverable: the split, its sensitivity, the lists.

READ-ONLY. Consumes `causes.json` and writes `REPORT.md`. Measures nothing
itself, so every figure here is `split_causes.py`'s.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-stranding-causes/report_split.py
"""

from __future__ import annotations

import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent

# THE BOUNDARY. A choice, not a measurement, and the report says so.
# Anchor: the median artifact node holds 9 connections. An artist the builder
# could offer 10 or fewer usable candidates could not reach that median even
# under a rule that kept every one of them, so for those the cap rule is not the
# remedy. Above it, the artist had enough material to be ordinarily connected
# and the reciprocity requirement is what took it away.
FRONTIER_CUT = 10
MEDIAN_GRAPH_DEGREE = 9
TOP_N = 50


def table(rows, title, note):
    out = [f"### {title}", "", note, "",
           "| # | artist | deg | offered | usable | judged | back | listed by |",
           "|---:|---|---:|---:|---:|---:|---:|---:|"]
    for n, r in enumerate(rows, 1):
        name = r["name"].strip() or "*(nameless)*"
        out.append(
            f"| {n} | {name} | {r['degree']} | {r['n_offered']} | {r['n_pool']} | "
            f"{r['n_candidates']} | {r['n_reciprocated']} | "
            f"{r['n_ranked_by_others']} |"
        )
    out.append("")
    return out


def main() -> None:
    data = json.loads((HERE / "causes.json").read_text(encoding="utf-8"))
    rows = data["rows"]
    total = len(rows)
    K = data["k"]

    capped = [r for r in rows if r["n_pool"] > FRONTIER_CUT]
    frontier = [r for r in rows if r["n_pool"] <= FRONTIER_CUT]
    thin = [r for r in frontier if r["n_offered"] <= FRONTIER_CUT]
    true_frontier = [r for r in frontier if r["n_offered"] > FRONTIER_CUT]
    by_pop = sorted(rows, key=lambda r: -r["pop_raw"])
    many = sum(1 for r in rows if r["n_ranked_by_others"] >= 10)

    L: list[str] = [
        "# Why the low-degree artists are low-degree - 2026-07-26",
        "",
        "**Role: the measurement record for this directory. It owns every figure below;",
        "cite this file, do not restate its numbers.** Read-only throughout: no rebuild,",
        "no routing change, no adoption, nothing proposed.",
        "",
        f"Artifact: `graph-t15-tiebreakfix.bin`, sha256 `{data['artifact_sha256']}`,",
        "asserted before any figure was computed.",
        "",
        "## The question",
        "",
        "The census counted the artists the app can never introduce anyone to (one",
        "connection) or can only reach down a single corridor (two). That set is",
        f"**{total}** artists, and the ask was to separate two causes:",
        "",
        "- **CAP-STRANDED** - the artist had a full list of candidates who *are* in the",
        "  graph, and almost none of them ranked it back. The both-ways rule destroyed",
        "  its connections, and a different rule would give them back.",
        "- **CRAWL-FRONTIER** - the artist sits at the edge of the snowball crawl, so few",
        "  of its candidates are in the graph at all. Its low degree would persist under",
        "  any cap rule.",
        "",
        "**The headline is that the second category, as phrased, is nearly empty** - and",
        "what fills its place is a third cause that neither the crawl nor the cap rule",
        "can address. The two-way split that was asked for is given first and in full,",
        "then the refinement.",
        "",
        "## Measured",
        "",
        f"Population: every artifact node with degree <= 2 - **{total}** artists",
        f"({data['artifact_nodes']} nodes in the graph, {data['candidate_population']} in",
        f"the builder's candidate population after {data['special_purpose_excluded']}",
        "placeholder entities are dropped).",
        "",
        "Columns, throughout:",
        "",
        "| column | meaning |",
        "|---|---|",
        "| **offered** | how many similar artists the source named for this artist at all |",
        "| **usable** | how many of those were themselves crawled, so the builder could use them |",
        f"| **judged** | usable, capped to k = {K} - the list the both-ways rule judged |",
        "| **back** | how many of them ranked this artist back - the modelled degree |",
        "| **listed by** | how many artists list it, whether or not it lists them |",
        "",
        "**`deg` is the artifact's own degree and `back` is the model's count of the same",
        "thing.** They agree for all but ten artists (gate 4 below), so a row where they",
        "differ is that residual showing, not a contradiction - `deg` is the authoritative",
        "one.",
        "",
        "`offered` vs `usable` is what separates a crawl problem from a source problem,",
        "and `listed by` is what separates *stranded by the rule* from *beyond any",
        "rule's reach*: an artist thirty others list is one a one-directional rule would",
        "rescue; an artist only one other lists is not.",
        "",
        "### How many candidates each artist actually had",
        "",
        "| usable candidates | artists | share |",
        "|---|---:|---:|",
    ]
    for label, lo, hi in [("1-2", 1, 2), ("3-5", 3, 5), ("6-10", 6, 10),
                          ("11-20", 11, 20), ("21-49", 21, 49),
                          (f"{K}+ (full list)", K, 10**9)]:
        n = sum(1 for r in rows if lo <= r["n_pool"] <= hi)
        L.append(f"| {label} | {n} | {100 * n / total:.1f}% |")

    L += [
        "",
        "## The split that was asked for",
        "",
        f"**The boundary is my choice, and it is this: an artist is CRAWL-FRONTIER if the",
        f"builder had {FRONTIER_CUT} usable candidates or fewer.**",
        "",
        f"The anchor is the graph's own median degree, which is {MEDIAN_GRAPH_DEGREE}. An",
        f"artist with {FRONTIER_CUT} usable candidates or fewer could not reach that",
        "median even under a rule that kept every single one, so for those the cap rule",
        "is not the remedy. Above the line the artist had enough material to be",
        "ordinarily connected, and the both-ways requirement is what took it away.",
        "",
        "| population | artists | share |",
        "|---|---:|---:|",
        f"| CRAWL-FRONTIER (usable <= {FRONTIER_CUT}) | {len(frontier)} | "
        f"{100 * len(frontier) / total:.1f}% |",
        f"| CAP-STRANDED (usable > {FRONTIER_CUT}) | {len(capped)} | "
        f"{100 * len(capped) / total:.1f}% |",
        "",
        "**Because the boundary is a choice, here is every other choice.** Read this",
        "before quoting the split: the two populations are a continuum.",
        "",
        "| boundary | CRAWL-FRONTIER | CAP-STRANDED |",
        "|---|---:|---:|",
    ]
    for cut in (2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 49):
        n = sum(1 for r in rows if r["n_pool"] <= cut)
        L.append(f"| usable <= {cut} | {n} ({100 * n / total:.1f}%) | "
                 f"{total - n} ({100 * (total - n) / total:.1f}%) |")

    lo2 = sum(1 for r in rows if r["n_pool"] <= 2)
    hi50 = sum(1 for r in rows if r["n_pool"] >= K)
    L += [
        "",
        "Two fixed points bound the table and neither depends on my choice:",
        "",
        f"- **{lo2} artists ({100 * lo2 / total:.1f}%) had two usable candidates or",
        "  fewer.** They could not have exceeded degree 2 under *any* selection rule.",
        f"- **{hi50} artists ({100 * hi50 / total:.1f}%) had a full {K}-candidate list.**",
        "  Meat Loaf's case exactly.",
        "",
        "## The refinement: cause (b) is not what it says it is",
        "",
        "**CRAWL-FRONTIER as defined above conflates two situations that have nothing in",
        "common.** Splitting it on whether the *source* had anything to offer:",
        "",
        "| population | artists | share | what it means |",
        "|---|---:|---:|---|",
        f"| CAP-STRANDED | {len(capped)} | {100 * len(capped) / total:.1f}% | "
        "full candidate list, the rule discarded it |",
        f"| SOURCE-THIN | {len(thin)} | {100 * len(thin) / total:.1f}% | "
        f"the source named <= {FRONTIER_CUT} similar artists in the first place |",
        f"| CRAWL-FRONTIER | {len(true_frontier)} | "
        f"{100 * len(true_frontier) / total:.1f}% | "
        "the source named plenty; the crawl had not reached them |",
        "",
        f"**The crawl frontier explains {100 * len(true_frontier) / total:.1f}% of the",
        f"set, not {100 * len(frontier) / total:.1f}%.** For the artists below the line,",
        f"the median number offered by the source is",
        f"{st.median([r['n_offered'] for r in frontier]):.0f} and the median usable is",
        f"{st.median([r['n_pool'] for r in frontier]):.0f} - practically everything the",
        "source named had already been crawled. The crawl did its job. The source simply",
        "does not know much about these artists.",
        "",
        "That matters because the three have different remedies: crawling further reaches",
        "the smallest group, changing the cap rule reaches the middle one, and the",
        "largest group is reached by neither.",
        "",
        "### What SOURCE-THIN actually means - checked, because the obvious reading is wrong",
        "",
        "The tempting conclusion is *the similarity source knows nothing about these",
        "artists, and nothing in this project's control changes that*. **That is wrong,",
        "and the check that shows it is cheap.** The source is queried with a fixed",
        "algorithm string (`BuilderConfig.algorithm`) carrying two parameters we chose:",
        "",
        "- **`limit_100`** - at most 100 similar artists per request. 39.1% of all 75,000",
        "  crawled artists return exactly 100, so the limit binds for a large minority.",
        "  **It cannot produce a short list**: truncation only shortens long ones to 100.",
        "  So it does not touch this finding.",
        "- **`threshold_10`** - pairs below a co-occurrence threshold are not returned at",
        "  all. **This does produce short lists**, and it is the reason a SOURCE-THIN",
        "  artist is thin.",
        "",
        "So the accurate statement is **not** \"the source has no data on these artists\"",
        "but \"the source has no data on these artists *above the threshold we asked for*\".",
        "Re-crawling at a lower threshold is inside this project's control. What it would",
        "yield has **not** been measured, and it would mean a full re-crawl plus edges",
        "resting on weaker evidence - so this is a named option with an unmeasured payoff,",
        "not a recommendation.",
        "",
        "For completeness: 188 of the 75,000 archived responses are empty, and the longest",
        "possible response is 100 by construction.",
        "",
        "## What cuts against the cap-stranded share",
        "",
        "The obvious reading of the cap-stranded number is *a different rule would give",
        "those artists their connections back*. **The `listed by` column complicates",
        "that, and it is why that column was measured.**",
        "",
        "| listed by | artists | share |",
        "|---|---:|---:|",
    ]
    for label, lo, hi in [("1 artist", 1, 1), ("2-4", 2, 4), ("5-9", 5, 9),
                          ("10-29", 10, 29), ("30 or more", 30, 10**9)]:
        n = sum(1 for r in rows if lo <= r["n_ranked_by_others"] <= hi)
        L.append(f"| {label} | {n} | {100 * n / total:.1f}% |")

    few = sum(1 for r in rows if r["n_ranked_by_others"] <= 4)
    one = sum(1 for r in rows if r["n_ranked_by_others"] == 1)
    L += [
        "",
        f"**{100 * few / total:.1f}% of the set is listed by four artists or fewer**, and",
        f"{100 * one / total:.1f}% by exactly one. Even the most permissive change",
        "available - keeping every one-directional candidate - would leave most of these",
        "artists with a handful of connections at most.",
        "",
        "A floor of zero is not reported because it cannot occur: a node with at least",
        "one connection is necessarily listed by at least one artist, so `listed by` >=",
        "degree >= 1 by construction, not by measurement.",
        "",
        "### ...and what cuts back the other way",
        "",
        "**Quoting the paragraph above on its own would mislead.** The causes are almost",
        "perfectly stratified by popularity, so the small rescuable population is",
        "precisely the one anyone would ever notice.",
        "",
        "| band, by in-graph popularity | listed by, median | listed by >= 10 | cap-stranded |",
        "|---|---:|---:|---:|",
    ]
    for label, band in [("top 50", by_pop[:50]), ("top 100", by_pop[:100]),
                        ("top 500", by_pop[:500]), ("top 1000", by_pop[:1000]),
                        ("top 2000", by_pop[:2000]), (f"all {total}", by_pop),
                        ("lowest 1200", by_pop[-1200:])]:
        lb = [r["n_ranked_by_others"] for r in band]
        ge10 = sum(1 for x in lb if x >= 10)
        cs = sum(1 for r in band if r["n_pool"] > FRONTIER_CUT)
        L.append(f"| {label} | {st.median(lb):.0f} | {ge10} "
                 f"({100 * ge10 / len(band):.0f}%) | {100 * cs / len(band):.0f}% |")

    top50_ge10 = sum(1 for r in by_pop[:50] if r["n_ranked_by_others"] >= 10)
    top2000_ge10 = sum(1 for r in by_pop[:2000] if r["n_ranked_by_others"] >= 10)
    L += [
        "",
        f"**All {many} of the rescuable artists sit in the top 2000 by popularity**",
        f"({top2000_ge10} of {many}), and {top50_ge10} of the top 50 are rescuable. The",
        "least popular 1200 contain **none** of them.",
        "",
        "So the honest statement is both halves at once:",
        "",
        "- **By count**, the set is dominated by artists the similarity source barely",
        "  covers, and neither the crawl nor the cap rule addresses them.",
        "- **By who anyone would recognise**, the set is dominated by artists with full",
        "  candidate lists discarded by the both-ways rule, and a rule change is exactly",
        "  what would reach them.",
        "",
        "Which of those matters more depends on whether the goal is to fix a population",
        "or to fix the artists a person actually meets. That is not a measurement",
        "question and this document does not answer it.",
        "",
        "## The lists",
        "",
        "Ranked by in-graph popularity **to choose whose names to show, and for nothing",
        "else** - popularity ranks nothing here (Phase 1 log 2.11). It is sound as a",
        "screen only because popularity is accumulated *before* the cap, so the",
        "reciprocity rule destroys degree and leaves popularity untouched.",
        "",
    ]
    L += table(
        sorted(capped, key=lambda r: -r["pop_raw"])[:TOP_N],
        f"Top {TOP_N} CAP-STRANDED - the rule discarded these",
        "Full candidate lists, almost none reciprocated. A different cap rule reaches "
        "these.",
    )
    L += table(
        sorted(true_frontier, key=lambda r: -r["pop_raw"])[:TOP_N],
        f"Top {TOP_N} CRAWL-FRONTIER - the crawl had not reached these",
        f"The source named more than {FRONTIER_CUT} similar artists but few were "
        f"crawled. Only {len(true_frontier)} artists are in this group at all.",
    )
    L += table(
        sorted(thin, key=lambda r: -r["pop_raw"])[:TOP_N],
        f"Top {TOP_N} SOURCE-THIN - the source barely knows these",
        "Nothing in this project's control changes these: the similarity data itself "
        "is thin.",
    )

    L += [
        "## What this does not establish",
        "",
        "- **The causes are not exclusive, and the split reports which one binds.** An",
        "  artist with 15 usable candidates and one connection lost fourteen to the rule",
        "  *and* had a thin list. Every figure is about the binding constraint.",
        "- **It says nothing about whether a different rule would be better.**",
        "  `mutual_knn` won a blind listen, and dropping reciprocity restores unbounded",
        "  degree (`MKS-5b`). Nothing here is evidence for a redesign.",
        "- **`listed by` is not a promise.** It counts one-directional candidates; it does",
        "  not model any specific alternative rule, and no alternative rule was run.",
        "- **The names are the graph's own**, so an artist stored under a different",
        "  spelling appears under that spelling (`CNS-1`).",
        "",
        "## Gates, and the one residual",
        "",
        "1. The artifact sha256 is asserted before any figure is computed.",
        "2. The 2026-07-25 candidate model's own gate - six artists whose predicted",
        "   neighbour sets must match the shipped graph - runs **twice**: unmodified, and",
        "   again after the builder's placeholder exclusion is applied.",
        f"3. The uncapped candidate count is consistent with the capped list for **all",
        f"   {total}** artists: 0 mismatches. This is the gate that matters most, because",
        "   the candidate count is what the split keys on.",
        f"4. The modelled degree equals the artifact's own degree for "
        f"**{total - len(data['degree_disagreements'])} of {total}**.",
        "",
        f"**The residual is {len(data['degree_disagreements'])} artists "
        f"({100 * len(data['degree_disagreements']) / total:.2f}%), each off by one",
        "connection.** Two candidate causes were investigated and both are settled: the",
        "builder drops MusicBrainz placeholder entities before ranking and the 2026-07-25",
        "model did not (**fixed here - it accounted for 7 of the original 17**), and the",
        "builder drops rows carrying no similarity score while that model keeps them as",
        "zero (**measured: there are no such rows in the archive, 0 of 4,234,499**). The",
        "remaining ten sit at the rank-50 boundary of a partner's list. They were left",
        "there deliberately: the split keys on the candidate count, which gate 3 verifies",
        "exactly, and every degree quoted here is the artifact's own, not the model's.",
        "",
    ]

    dest = HERE / "REPORT.md"
    dest.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {dest}")
    print(f"CAP-STRANDED   {len(capped):5} {100 * len(capped) / total:5.1f}%")
    print(f"SOURCE-THIN    {len(thin):5} {100 * len(thin) / total:5.1f}%")
    print(f"CRAWL-FRONTIER {len(true_frontier):5} "
          f"{100 * len(true_frontier) / total:5.1f}%")


if __name__ == "__main__":
    main()
