"""Render the degree-1 / degree-2 census into an owner-readable report.

Joins three things:
  - `low_degree.json`  — the full census of all 12,088 low-degree nodes (artifact side)
  - `poll_set.json`    — which of them were polled for fame, and in which role
  - `fame_cache.json`  — the canonical A11/A15 fame rows, keyed by name

**The join is name -> fame, and that is the deliverable's main hazard.** Wikipedia
has no MBID index, so the proxy can only be asked about a name (P8b F8 records the
same constraint for the Track 2 scorer). Two consequences, both surfaced in the
report rather than smoothed over:

  - Two artifact nodes sharing a name necessarily receive the SAME fame figure. At
    most one of them can be the act the article is about.
  - A node sharing a name with a famous act that is NOT in the graph gets that act's
    pageviews. This is undetectable from the artifact, so every row prints the
    **resolved article title** whenever it differs from the artist name: that is what
    was actually measured, and a wrong entity is visible without leaving the page.

Ordering is by pageviews, which is order-identical to A11's F = log10(1 + pageviews)
because log is monotone. Pageviews are printed because the owner can read them.

**Graph popularity (`pop_raw`) selected who to ask, and orders nothing.** Phase 1
log §2.11 established it disagrees with household-name fame at the top, so using it
to rank would reproduce the error the external proxy exists to avoid. Its only job
here is the screen, whose validity the report states from the control sample rather
than assuming.

Run from `builder/`:
    UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 uv run python -u \
      analysis/2026-07-26-low-degree-census/report.py --top 200
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SETS = {"degree_1": "1 connection", "degree_2": "2 connections"}


def load() -> tuple[dict, dict, dict]:
    census = json.loads((HERE / "low_degree.json").read_text(encoding="utf-8"))
    poll = json.loads((HERE / "poll_set.json").read_text(encoding="utf-8"))
    cache: dict = {}
    seed = HERE.parent / "2026-07-24-track2-arm-scorer" / "fame_cache.json"
    if seed.exists():
        cache.update(json.loads(seed.read_text(encoding="utf-8")))
    own = HERE / "fame_cache.json"
    if own.exists():
        cache.update(json.loads(own.read_text(encoding="utf-8")))
    for doc, name in ((census, "low_degree.json"), (poll, "poll_set.json")):
        if doc["artifact_sha256"] != (
            "4cb84ef979f2ef3c127ff59066105b334bae8f7b033e2452749728af6b061dc8"
        ):
            raise SystemExit(f"{name} was not built from the adopted artifact")
    return census, poll, cache


def enrich(rows: list[dict], cache: dict) -> list[dict]:
    """Attach the fame row. An unresolved name is marked, never floored.

    An unresolved name (never reached, or every attempt hit a transient failure) is
    NOT the same thing as an artist with no English article. Conflating them imports
    exactly the silent-obscurity failure `transport.py` exists to prevent, so they
    are counted separately and excluded from the ranked lists.
    """
    out = []
    for r in rows:
        fr = cache.get(r["name"])
        r = dict(r)
        r["resolved"] = fr is not None
        if fr is None:
            r["matched"] = False
            r["fame_pageviews"] = None
        else:
            r["matched"] = bool(fr.get("matched"))
            r["fame_pageviews"] = int(fr["pageviews"]) if fr.get("matched") else 0
            r["F"] = float(fr.get("F", 0.0))
            r["article"] = fr.get("article") or ""
            r["months_present"] = fr.get("months_present")
            r["via"] = fr.get("via") or ""
            g = fr.get("guard") or {}
            r["potentially_notable"] = bool(g.get("potentially_notable"))
            r["non_latin_name"] = bool(g.get("non_latin_name"))
            r["foreign_wikis"] = (g.get("foreign") or {}).get("non_english_wikis") or []
        out.append(r)
    return out


def fmt_row(i: int, r: dict) -> str:
    dis = f" — *{r['disambiguation']}*" if r["disambiguation"] else ""
    notes = []
    if r["name_shared_with"]:
        notes.append(f"⚠ shares this name with {len(r['name_shared_with'])} other "
                     f"node(s) in the graph — the fame figure cannot tell them apart")
    if r.get("article") and r["article"].strip().lower() != r["name"].strip().lower():
        notes.append(f"measured article: *{r['article']}*")
    if r.get("via") == "wikidata_fallback":
        notes.append("recovered by the A15 fallback")
    if r.get("months_present") is not None and r["months_present"] < 12:
        notes.append(f"only {r['months_present']}/12 months of traffic")
    tail = ("  \n    " + "; ".join(notes)) if notes else ""
    return (f"{i:>4}. **{r['name']}**{dis} — "
            f"{r['fame_pageviews']:,} annual pageviews{tail}")


def ranked(rows: list[dict]) -> list[dict]:
    got = [r for r in rows if r["resolved"] and r["matched"]]
    got.sort(key=lambda r: (-r["fame_pageviews"], r["name"].lower()))
    return got


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=200)
    args = ap.parse_args()
    census, poll, cache = load()

    n, crawled = census["artifact_nodes"], census["archived_responses"]
    full = {k: census[k] for k in SETS}
    screen = {k: enrich([r for r in poll["screen"] if r["set"] == k], cache) for k in SETS}
    control = {k: enrich([r for r in poll["control"] if r["set"] == k], cache) for k in SETS}
    polled = [r for k in SETS for r in screen[k] + control[k]]
    unresolved = [r for r in polled if not r["resolved"]]

    L: list[str] = []
    L.append("# Artists the app can never introduce you to\n")
    L.append("### The degree-1 and degree-2 census of the adopted 75k artifact\n")
    L.append(f"Read-only. Artifact `sha256 {census['artifact_sha256'][:16]}…` asserted "
             "before reading, as the existing scripts under `builder/analysis/` do. "
             "**Nothing was rebuilt, routed, adopted or proposed.** No config was "
             "touched, no arm was run.\n")

    # ------------------------------------------------------------------ (a)
    L.append("\n## (a) How many, and out of what\n")
    L.append("| set | nodes | share of artifact nodes | share of crawled artists |")
    L.append("|---|---:|---:|---:|")
    tot = 0
    for k, label in SETS.items():
        c = len(full[k])
        tot += c
        L.append(f"| **{label}** | {c:,} | {100*c/n:.2f} % | {100*c/crawled:.2f} % |")
    L.append(f"| **both** | {tot:,} | {100*tot/n:.2f} % | {100*tot/crawled:.2f} % |")

    L.append(f"\n### Which denominator — `DRV-4`, resolved\n")
    L.append(f"**Both are given, and the answer is that the ambiguity barely matters: "
             f"they differ by 0.17 percentage points.** Artifact nodes = **{n:,}**; "
             f"crawled artists = **{crawled:,}** (archived similarity responses).\n")
    L.append("**They are nested, not alternatives.** `build_from_archive` "
             "(`builder/src/artistpath_builder/pipeline.py:131`) sets "
             "`known = set(payloads)` — the artists holding their *own* archived "
             "similarity response — and keeps a neighbour edge only `if n.mbid in known` "
             "(line 184). **So every artifact node is a crawled artist**; an artist "
             "discovered in someone else's similarity list but never crawled is never a "
             f"node at all. The {crawled - n:,} crawled artists absent from the artifact "
             "were removed by the special-purpose filter, by holding no surviving edge "
             "after the mutual-kNN cap, or by the largest-component prune.\n")

    L.append("### Counted after the largest-component prune — confirmed\n")
    L.append("The artifact is written from `pruned`, built from "
             "`keep = largest_component(...)` (`pipeline.py:231-238`), so every node read "
             "here is already post-prune. The observable consequence, measured: the "
             "**minimum degree anywhere in these sets is 1**, and **0** neighbours have "
             "degree < 1. A pre-prune count would have included degree-0 isolates and "
             "whole disconnected islands.\n")

    L.append("### Non-artist entities — confirmed excluded\n")
    L.append("The build's only type filter is `is_special_purpose`, a case-insensitive "
             "match on the literal `special purpose` in the MusicBrainz disambiguation "
             "(`pipeline.py:42-47`). Nothing else is excluded by type, so this was "
             "checked rather than assumed: **0** placeholder disambiguations survive in "
             "these sets. A deliberately broader scan for container-like names "
             "(`Various Artists`, `[unknown]`, `Soundtrack`, …) flagged only two, and "
             "**both are genuine artists** — `NA` (*NA is Daniel Pineda, aka 1/2 of "
             "Nguzunguzu*) and `Unknown` (*US rapper Richard Patterson*). The one real "
             f"contaminant is the **{census['nameless']} nameless nodes**, excluded from "
             "the lists below and reported in the caveats.\n")

    L.append("### Why these two sets\n")
    L.append("- **1 connection** — a card in the middle of a journey needs a neighbour on "
             "each side, so these artists can *only* ever appear as one of the two "
             "artists you typed in yourself. **The app can never introduce you to them.** "
             "(`DRV-4` states this as structural and unmeasured; this is the measurement.)")
    L.append("- **2 connections** — reachable in the middle, but by exactly one route: in "
             "through one neighbour and out through the other. Deliverable only when the "
             "router happens to price that single detour.\n")

    # ------------------------------------------------- how the lists were built
    L.append("\n## How the fame figures were obtained\n")
    L.append("Fame is **English-Wikipedia annual pageviews** over A11's fixed window "
             "(2025-07 … 2026-06), via the canonical resolver, with an artist that has no "
             "English article scored at the **fame floor**. That is the proxy this project "
             "adopted (pre-registration §5 + amendment **A11**), including A15's recall "
             "fallback — which matters more here than anywhere it has been used, because "
             "a fame-*ranked* list is exactly where a household name wrongly floored "
             "(Justice, Rainbow, Ye) would vanish without trace.\n")
    L.append("**The graph's own popularity was NOT used to rank anything** (Phase 1 log "
             "§2.11: at the top of the distribution it disagrees with household fame). It "
             "was used only to decide *who to ask*, because polling all 12,041 names is "
             "~120,000 API requests and Wikipedia asks for ~1 request/second on one or two "
             "connections. The top **400 by popularity in each set** were polled, plus a "
             "seeded random **200 from below the cut in each set** as a control.\n")
    L.append("**Why popularity is a safe screen here even though it is a bad ranker.** It "
             "is score-weighted in-degree accumulated at `pipeline.py:206-216` — *before* "
             "`mutual_knn_cap` (227), `symmetrise` (230) and `largest_component` (231) — so "
             "it is summed over the **full uncapped neighbour lists**. The reciprocity rule "
             "destroys a stranded artist's degree and leaves its popularity untouched. "
             "Degree and popularity are not merely different currencies (§2.6); they are "
             "read at different stages of the build, and the screen rides on the stage the "
             "defect never reaches.\n")

    # --------------------------------------------- screen validation (control)
    L.append("### Did the screen leak? The control sample\n")
    L.append("**The test is whether a control artist would have made the delivered list** "
             "— not whether it beats the screened set's weakest member. The screened set "
             "is full of low-fame artists by construction (high popularity does not imply "
             "high fame — that is §2.11), so its minimum is near zero and almost any "
             "control artist with an article would clear it. That comparison would fire "
             "on noise and mean nothing. The question that matters is whether polling "
             "everything would have changed the top of the list.\n")
    leak_summary = []
    for k, label in SETS.items():
        rs, rc = ranked(screen[k]), ranked(control[k])
        below = len(full[k]) - len(screen[k])
        # The bar: the fame of the last artist in the delivered list.
        bar = rs[min(args.top, len(rs)) - 1]["fame_pageviews"] if rs else 0
        intruders = [r for r in rc if r["fame_pageviews"] > bar]
        L.append(f"**{label}.** {len(rs)} of the {len(screen[k])} screened have an English "
                 f"article. The delivered list ends at **{bar:,} pageviews** — that is the "
                 f"bar a below-cut artist must clear to belong in it.")
        if not rc:
            L.append(f"    Control ({len(control[k])} random from the {below:,} below the "
                     "cut): **not one has an English Wikipedia article at all** — the "
                     "strongest available form of no-leak.\n")
            leak_summary.append((label, 0, 0.0, below))
            continue
        rate = len(intruders) / len(control[k])
        est = rate * below
        if intruders:
            L.append(f"    Control ({len(control[k])} random from the {below:,} below the "
                     f"cut): **{len(intruders)} would have made the list**, the strongest "
                     f"being **{intruders[0]['name']}** at "
                     f"{intruders[0]['fame_pageviews']:,} pageviews. **The screen leaks.** "
                     f"At {len(intruders)}/{len(control[k])} that implies roughly "
                     f"**{est:.0f}** artists below the cut belong in the list and are "
                     f"missing from it.\n")
        else:
            L.append(f"    Control ({len(control[k])} random from the {below:,} below the "
                     f"cut): {len(rc)} have an article but **none clears the bar** "
                     f"(strongest: {rc[0]['name']}, {rc[0]['fame_pageviews']:,} "
                     f"pageviews). **No leak detected.** A 0/{len(control[k])} sample "
                     f"bounds the missing count at roughly {3 * below / len(control[k]):.0f} "
                     "or fewer (rule of three, 95 %).\n")
        leak_summary.append((label, len(intruders), est, below))

    # ------------------------------------------- crawl coverage, not instrument noise
    # A control artist with real fame and low in-graph popularity is not merely a
    # screen imperfection to be bounded away. Popularity here is score-weighted
    # in-degree over the FULL uncapped lists, so low popularity means few crawled
    # artists named this act as similar at all — which is a statement about what the
    # snowball reached, in the same family as the stranding split itself. Owner's
    # observation, 2026-07-26; recorded because it bears on what the graph can deliver.
    L.append("\n### Famous but barely named by anyone — candidate crawl-coverage gaps\n")
    L.append("**These are not simply screen imperfections, and they should not be filed as "
             "instrument noise.** Popularity here is score-weighted in-degree over the "
             "*full uncapped* neighbour lists, so a low value means **few crawled artists "
             "named this act as similar at all**. When such an artist turns out to be "
             "genuinely famous, that is evidence about what the snowball crawl reached — "
             "the same class of question as the stranding split, and it belongs beside it.\n")
    gaps = []
    for k, label in SETS.items():
        order = sorted([r for r in full[k] if (r["name"] or "").strip()],
                       key=lambda r: (-r["pop_raw"], r["mbid"]))
        rank_of = {r["mbid"]: i for i, r in enumerate(order, 1)}
        for r in ranked(control[k]):
            if r["fame_pageviews"] >= 10_000:
                gaps.append((r, label, rank_of.get(r["mbid"], 0), len(order)))
    gaps.sort(key=lambda t: -t[0]["fame_pageviews"])
    if gaps:
        L.append(f"{len(gaps)} of the {sum(len(control[k]) for k in SETS)} control artists "
                 "clear 10,000 annual pageviews despite sitting below the popularity cut:\n")
        for r, label, rk, tot in gaps:
            art = (f" — measured article *{r['article']}*"
                   if r.get("article") and r["article"].strip().lower()
                   != r["name"].strip().lower() else "")
            share = "; ⚠ name shared in-graph" if r["name_shared_with"] else ""
            L.append(f"- **{r['name']}** — {r['fame_pageviews']:,} annual pageviews, "
                     f"{label}, popularity rank {rk:,} of {tot:,}{art}{share}")
        per_set = {lbl: sum(1 for g in gaps if g[1] == lbl) for lbl in SETS.values()}
        L.append(f"\n**Scaled up**, the control samples 200 of each set's below-cut "
                 "population, so each artist found here implies roughly 30 more in the "
                 "full census: " + "; ".join(
                     f"~{cnt * (len(full[k]) - len(screen[k])) / len(control[k]):.0f} for "
                     f"{lbl}" for (k, lbl), cnt in zip(SETS.items(), per_set.values())) + ".\n")
        L.append("**Before reading these as crawl gaps, two cheaper explanations have to be "
                 "excluded, and this measurement does not exclude them.** (i) The artist is "
                 "famous for something other than music — an actor or presenter with a "
                 "recording credit — so English Wikipedia traffic is real but not musical "
                 "reach, and few artists naming them as *similar* is then correct rather "
                 "than a gap. (ii) The name collides with a more famous act outside the "
                 "graph, inflating the pageview figure; rows carrying an in-graph collision "
                 "are marked, but an out-of-graph collision is undetectable here, which is "
                 "why the measured article title is printed. **The check that would settle "
                 "it is per-artist and manual** — does this act have real listening reach in "
                 "the population the crawl covers — and it is not run here.\n")
    else:
        L.append("**No control artist clears 10,000 annual pageviews.** On this sample the "
                 "below-cut population contains no candidate coverage gap of that size — "
                 "which is also the cleanest available evidence that the screen is not "
                 "hiding a famous artist.\n")

    L.append("**What this does and does not establish.** It tests the screen against "
             "cases nothing selected for fame, which `verify_screen.py`'s ground truth "
             "could not: `MKS-2`'s six artists were found by noticing *recognisable* names "
             "among low-degree ones, so they were already correlated with being "
             "well-connected pre-cap. The control is not selected on anything. What it "
             "still cannot see is the screen's one known failure direction — an artist "
             "famous in a population this snowball crawl under-covers would sit low on "
             "popularity *and* be missed by a 200-node sample. That is the same blind-spot "
             "direction A11 already accepts for Wikipedia-absence, so the two instruments "
             "do not cross-check each other.\n")
    L.append("For scale, `verify_screen.py`'s result: all five `MKS-2` artists present in "
             "this set rank in the **top 11 of 6,396** by popularity — Nada Surf 1st, "
             "The Cult 4th, Meat Loaf 7th, Elbow 8th, The Streets 11th — against a cut at "
             "400. (Pretenders is absent because it holds 6 connections, which is the "
             "finding's own figure and a consistency check passing.)\n")

    # ------------------------------------------------------------------ (b)(c)
    for key, (k, label) in zip("bc", SETS.items()):
        rs = ranked(screen[k])
        L.append(f"\n## ({key}) The {min(args.top, len(rs))} highest-fame artists with "
                 f"only {label}\n")
        L.append(f"Ranked by English-Wikipedia annual pageviews, highest first. Drawn from "
                 f"the {len(screen[k])} highest-popularity nodes of the {len(full[k]):,} "
                 f"with {label}; {len(rs)} of those have an English article.\n")
        for i, r in enumerate(rs[:args.top], 1):
            L.append(fmt_row(i, r))

    # ---------------------------------------------------------------- caveats
    L.append("\n## What would make these lists misleading\n")
    shared = [r for r in polled if r["name_shared_with"]]
    all_shared = census["name_collisions"]
    L.append(f"**1. Shared names — {all_shared:,} of the {tot:,} low-degree nodes share "
             f"their name with another node in the graph ({len(shared)} of the polled "
             "ones), and the fame figure cannot tell them apart.** The proxy resolves by "
             "name, so both nodes receive the same pageview count and at most one of them "
             "is the act the article is about. Affected rows are flagged ⚠ inline. This is "
             "the same hazard class as the live clip defect `BYP-13`, where a card played "
             "a clip by a different artist of the same name.\n")

    unmatched = [r for r in polled if r["resolved"] and not r["matched"]]
    flagged = [r for r in unmatched if r.get("potentially_notable")]
    L.append(f"**2. Absence is scored as obscurity, and {len(flagged)} polled artists look "
             "like possible exceptions.** A11 floors an artist with no English article — "
             "the owner's adopted decision, resting on absence having predicted 'never "
             "heard of' 9/9 on the validation sample. Its accepted residual is a "
             "foreign-language or historically-notable artist, and A11's guard flags "
             f"exactly that: here it fires on {len(flagged)} of the {len(unmatched)} "
             "floored artists. **These are artists who may belong in the lists above and "
             "are absent from them entirely** — an omission, which is the harder error to "
             "notice. Full set: `flagged_unmatched.md`.\n")

    L.append("**3. A name shared with a famous act *outside* the graph inflates fame "
             "silently, and the artifact cannot detect it.** The resolver requires a "
             "musical performer, so it will not return a film or a city, but it cannot "
             "know which *band* of a given name a node means. Mitigation rather than fix: "
             "every row prints the **measured article title** whenever it differs from the "
             "artist name. This is the residual most likely to have put a wrong name high "
             "in a list.\n")

    L.append(f"**4. {census['nameless']} nodes in these sets carry no name at all** and "
             "cannot be looked up, so they would sit at the fame floor for an artifact "
             "defect rather than for obscurity. Excluded from the lists and from the poll. "
             "The builder now rejects them (`acceptance.py`); the adopted artifact still "
             "contains them, and rebuilding is gated behind decisions this measurement "
             "does not make.\n")

    sparse = [r for r in polled if r["matched"] and (r.get("months_present") or 12) < 12]
    L.append(f"**5. {len(sparse)} matched artists have fewer than 12 months of traffic** in "
             "A11's window; a month with no traffic is absent from the API and contributes "
             "zero, so their fame is understated against a full-year artist. Flagged "
             "inline.\n")

    if unresolved:
        L.append(f"**6. {len(unresolved)} polled names never resolved** and are excluded "
                 "from both the ranked lists and the floored counts, rather than being "
                 "silently scored at the floor — an unresolved name and an artist with no "
                 "article are different things.\n")

    leaked = [s for s in leak_summary if s[1] > 0]
    if leaked:
        L.append("**7. The lists are the top of the *screened* set, and the control sample "
                 "says that is not exactly the top of all 12,088.** " + "; ".join(
                     f"for {lbl} roughly **{est:.0f}** of the {below:,} artists below the "
                     f"cut would rank inside the delivered list"
                     for lbl, cnt, est, below in leaked) +
                 ". **The cut was deliberately not deepened** (owner's call, 2026-07-26): "
                 "the ranked list is instrumental — its job was to answer *are recognisable "
                 "artists stranded?*, which the top-11 pile-up of every known `MKS-2` case "
                 "answers emphatically — and a more accurate ordering *below* the reliable "
                 "zone buys a marginally better eyeball sample and nothing else. The "
                 "artists concerned are not discarded: they are reported above as candidate "
                 "crawl-coverage gaps, which is the more useful thing they are evidence "
                 "of.\n")
    else:
        L.append("**7. The lists are the top of the *screened* set, not provably the top of "
                 "all 12,088.** The control sample detected no leak, which bounds but does "
                 "not eliminate the risk. The screen's failure direction is named in "
                 "§'Did the screen leak?': a household name in a population this crawl "
                 "under-covers sits low on popularity and a 200-node sample would likely "
                 "miss it.\n")

    L.append("**8. What is NOT a caveat, because it was caught and fixed.** Three separate "
             "mechanisms in this work would each have made an artist look *maximally "
             "obscure* and drop off the list silently: (i) concurrency provoked Wikidata "
             "throttling, and the canonical resolver's `except Exception: return []` turns "
             "a throttle into a fame-floor score — caught live by "
             "`verify_pool_equivalence.py` (`Compulsion`, 3,801 → 0 pageviews) and fixed "
             "in `transport.py`, which retries transient failures and raises rather than "
             "returning empty; (ii) a bulk-SPARQL shortcut lost 15 of 438 "
             "canonically-matched names including Guns N' Roses and Roxy Music — caught by "
             "`verify_sparql_recall.py` and **abandoned, not patched**; (iii) that same "
             "query reached *Roxy Music (album)* while missing the band entirely. No accept "
             "criterion was changed at any point; the instrument is A11 + A15 unmodified.\n")

    (HERE / "REPORT.md").write_text("\n".join(L), encoding="utf-8")

    fl = ["# Floored but possibly notable — A11's guard, fired\n",
          "These artists have **no English Wikipedia article**, so A11 scores them at the "
          "fame floor and they appear nowhere in the ranked lists. The guard flags them "
          "because a non-Latin name, or an article on a non-English Wikipedia, suggests "
          "the absence may be a gap in English Wikipedia rather than obscurity. Sorted by "
          "how many non-English Wikipedias carry them — the closest thing to a fame signal "
          "available for an artist English Wikipedia does not know.\n"]
    for r in sorted(flagged, key=lambda r: (-len(r["foreign_wikis"]), r["name"].lower())):
        why = []
        if r["non_latin_name"]:
            why.append("non-Latin name")
        if r["foreign_wikis"]:
            why.append(f"{len(r['foreign_wikis'])}+ non-English article(s): "
                       f"{', '.join(w.replace('wiki', '') for w in r['foreign_wikis'][:6])}")
        dis = f" — *{r['disambiguation']}*" if r["disambiguation"] else ""
        n_conn = "1 connection" if r["degree"] == 1 else "2 connections"
        fl.append(f"- **{r['name']}**{dis} — {n_conn} — {'; '.join(why)}")
    (HERE / "flagged_unmatched.md").write_text("\n".join(fl), encoding="utf-8")

    print(f"polled {len(polled)}; resolved {len(polled)-len(unresolved)}; "
          f"matched {sum(1 for r in polled if r['matched'])}; "
          f"floored {len(unmatched)}; guard-flagged {len(flagged)}")
    for k, label in SETS.items():
        print(f"  {label}: {len(ranked(screen[k]))} ranked of {len(screen[k])} screened; "
              f"control {len(ranked(control[k]))} of {len(control[k])} have an article")
    print(f"wrote {HERE/'REPORT.md'} and {HERE/'flagged_unmatched.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
