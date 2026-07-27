# What BoilTheFrog's graph and router actually did

### A reconstruction from the original project's own committed crawl data, 2026-07-27

**This directory owns every figure below.** The interpretation lives in
`docs/superpowers/findings/2026-07-27-boilthefrog-source-review.md`, which owns no figures
and cites this file by section.

**Read-only with respect to artistpath.** No artistpath artifact was opened, no config was
touched, no arm was run, nothing was rebuilt, routed or adopted. The path-quality pause is
intact. This measures a **third-party repository**, not this project's graph.

**Subject.** `github.com/plamere/BoilTheFrog` at `1f2cb60` (2020-06-12, repository HEAD),
21 commits spanning 2014-06-08 → 2020-06-12.

> ### Licence — checked, and it constrains what may be reused
>
> **There is no licence.** No `LICENSE`/`COPYING` file at any path, and no copyright or
> licence header in any source file. A public repository with no licence grant is
> **all-rights-reserved by default**: readable, not reusable.
>
> **What that permits.** Reading it, measuring it, describing it, and quoting short excerpts
> for commentary — all of which this review does. The scripts here are an independent
> reimplementation written to measure, not a port; **no upstream code is vendored, and the
> clone is gitignored** (see `.gitignore` in this directory).
>
> **What it forbids, and it lands on this review's own suggestion.** `BTF-7` points at
> upstream's `de_norm` as an answer to `CNS-1`. **That function may not be copied.** The
> *behaviour* — normalise identically at index and query time, strip a leading "the", fold
> accents and punctuation — is an idea and is free to reimplement; the code expressing it is
> not. Anyone acting on `BTF-7` writes it from the description, not from the file.
>
> *Stated because the parked deferral that requested this review required it explicitly —
> see `docs/superpowers/2026-07-23-repair-and-retune-execution-log.md`, "Parked, with
> triggers". It was missed on the first pass and added at closeout.*

---

## (a) What is being reconstructed, and the one thing that could not be

The repository commits its own crawl output at `new_crawler/g2/`:

| file | lines | content |
|---|---:|---|
| `nodes.js` | 95,059 | one Spotify artist object per line (`id`, `name`, `popularity`, `followers`) |
| `edges.js` | 40,009 | one `{source_uri: [target_uri, …]}` per line — the crawled related-artist lists |

**3 lines in each file are truncated** by unflushed writes. They are skipped, which is
faithful: the original's own loader skips them (`new_crawler/db.py:60`, *"skipped bad line
in db"*; `:71` for edges). Usable: **95,056 artists**, **40,006 expanded sources**.

`build()` in `btf_graph_measure.py` mirrors `new_crawler/artist_graph.py::load_graph`
exactly — `min_popularity = 30`, `max_edges_per_artist = 4`,
`weight = 1 + pop_weight·|Δpop|/100`, selection by `sorted(...)[:4]`, undirected union,
`blacklist.csv` applied (2 artists, 1 edge).

> ### The one omission, stated up front
>
> **`skip_artists_with_no_tracks` cannot be reproduced.** The per-artist track lists lived
> in a RocksDB that is not committed. Every artist here is therefore treated as having
> tracks, so the reconstruction is an **upper bound on node count** and, weakly, on the
> low-degree share. It cannot inflate the degree of a *famous* artist — the artists it
> wrongly admits are obscure ones with no Spotify top tracks — so **§(c)'s fame result is
> unaffected** and **§(b)'s stranding percentages are conservative in the direction that
> weakens my own reading**.

Two further facts about the source data, both measured, both load-bearing later:

- **Raw related-artist lists are at most 20 long** (min 0, median 20, max 20) — Spotify's
  `artist_related_artists` returns 20. This is a property of the *source*, not a choice.
- **55,976 of 95,056 crawled artists (58.89 %) clear `min_popularity = 30`.**

---

## (b) The shipped graph

| quantity | value |
|---|---:|
| nodes | 45,010 |
| edges | 129,333 |
| mean degree | 5.75 |
| degree p50 / p90 / p99 | 5 / 9 / 15 |
| **max degree** | **38** |
| components | 81 |
| largest component | 44,747 (99.42 %) |

Degree distribution:

| degree | count | share | cumulative |
|---:|---:|---:|---:|
| 0 | 39 | 0.09 % | 0.09 % |
| 1 | 3,234 | 7.19 % | 7.28 % |
| 2 | 1,201 | 2.67 % | 9.94 % |
| 3 | 509 | 1.13 % | 11.07 % |
| 4 | 10,812 | 24.02 % | 35.09 % |
| 5 | 8,944 | 19.87 % | 54.96 % |
| 6 | 6,410 | 14.24 % | 69.20 % |

**≥ 4 connections: 40,027 (88.93 %). ≤ 2 connections: 4,474 (9.94 %).**

Out-degree is 4 for 39,701 sources and **0 for 5,127** — sources whose entire
related-artist list fell below `min_popularity`. In-degree: min 0, p50 3, p90 8, p99 14,
max 38.

---

## (c) Degree does not track fame — and the famous are near-leaves

| Spotify popularity | artists | mean deg | median deg | max deg | % deg ≤ 2 | mean in-deg |
|---|---:|---:|---:|---:|---:|---:|
| 30–39 | 13,376 | 4.06 | 4 | 26 | **32.76 %** | 2.41 |
| 40–49 | 17,356 | 6.47 | 6 | 38 | 0.41 % | 4.03 |
| 50–59 | 9,127 | 6.56 | 6 | 28 | 0.15 % | 4.14 |
| 60–69 | 3,650 | 6.33 | 6 | 23 | 0.16 % | 3.87 |
| 70–79 | 1,152 | 6.10 | 6 | 20 | 0.00 % | 3.47 |
| 80–89 | 283 | 5.77 | 5 | 14 | 0.00 % | 3.01 |
| 90–100 | 66 | 5.65 | 5 | 11 | 0.00 % | 2.79 |

The twenty most popular artists in the graph:

| pop | deg | in | out | name |
|---:|---:|---:|---:|---|
| 100 | 4 | 0 | 4 | Ed Sheeran |
| 99 | 4 | 0 | 4 | Post Malone |
| 98 | 4 | 0 | 4 | Drake |
| 98 | 4 | 0 | 4 | Khalid |
| 97 | 5 | 4 | 4 | 21 Savage |
| 97 | 4 | 1 | 4 | Bad Bunny |
| 96 | 5 | 1 | 4 | Justin Bieber |
| 95 | 7 | 3 | 4 | Taylor Swift |
| 95 | 11 | 11 | 4 | Young Thug |
| 94 | 9 | 9 | 4 | Travis Scott |
| 94 | 4 | 0 | 4 | The Weeknd |

**Pearson r(popularity, degree) = +0.2711.** Top 1 % by degree (450 artists): mean
popularity **48.7**, mean degree 17.5 — against a whole-graph mean popularity of **46.4**.
The most-connected artists are mid-popularity (Bernadette Peters 38, EZA 34, Emil Gilels
32); **the most famous artists sit at or below the graph's mean degree.**

**Stranding is confined to the bottom band.** 32.76 % of the 30–39 band holds ≤ 2
connections; every band above 40 is at or under 0.41 %.

---

## (d) Factor table — which knob bounds the degree

No variant applies a reciprocity test.

| var | cap | criterion | nodes | edges | mean | p99 | **max** | % deg ≤ 2 | top-1 % mean pop |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|
| **A** | 4 | popularity proximity *(SHIPPED)* | 45,010 | 129,333 | 5.75 | 15 | **38** | 9.94 % | 49.7 |
| **B** | 4 | similarity rank | 49,730 | 136,130 | 5.47 | 17 | **67** | 13.97 % | 53.2 |
| **C** | 20 | popularity proximity | 55,964 | 566,251 | 20.24 | 61 | **147** | 11.00 % | 56.8 |
| **D** | 20 | similarity rank | 55,964 | 566,251 | 20.24 | 61 | **147** | 11.00 % | 56.8 |

**Held constant, and why the intervention cannot change it.** `min_popularity = 30` decides
membership *before* edge selection, so no variant can admit or exclude a node by its own
action. No variant tests reciprocity. The source's list length is fixed at ≤ 20 by Spotify.

> ### ⚠ C and D are the same graph. That cell is vacuous by construction.
>
> At cap = 20 the criterion only reorders a list that is **never longer than 20**, so both
> variants keep every admissible edge and the two builds are byte-identical — identical node
> count, edge count, max degree and hub list. **"Criterion effect at cap = 20" is not a null
> result; it is not a comparison at all.**
>
> Recorded rather than deleted because this is the project's signature defect
> (`FMS-P1`, `TR-2`, `TKB-4`, and the ten green mutations of the `DEP-33` review) reproduced
> once more, in a table written by someone who had just read the rule requiring an isolating
> baseline per row. It was caught by **running** the comparison and noticing two identical
> columns, not by review.

**The usable reads, therefore, are the cap-4 row pair and the two cap effects:**

- **Criterion, at a fixed cap of 4 (A vs B — differs by exactly one column):** popularity
  proximity **halves max degree, 67 → 38**, and cuts the ≤ 2-connection share from
  **13.97 % → 9.94 %**.
- **Cap, at fixed criterion (A vs C, B vs D):** 38 → 147 and 67 → 147.

**The cap is the dominant bound; the criterion is a real second-order effect at the cap.**

**And the ceiling that limits transfer:** even *fully uncapped*, max degree is only **147**,
because the source hands out at most 20 candidates. BoilTheFrog never faces an unbounded-degree
regime at all.

---

## (e) The bypass ladder

`new_crawler/artist_graph.py::path` — `weight = 10000` if either endpoint is in the skipset,
else the base weight. A **soft, node-local penalty**: no radius, no decay, no popularity
relaxation, one signal. Endpoints are unbypassable in the UI
(`new-web/index.html:536`, `index > 0 && index < list.length - 1`).

12 simulated presses per pair. `known-like` bypasses the most popular interior artist each
press; `random` bypasses a uniformly random one. **This is a simulation of user clicks, not
a use run.**

| pair | mode | cards | interior min pop | interior mean pop | plateau |
|---|---|---|---|---|---|
| Bob Dylan (78) → Metallica (84) | known-like | 9 → 10 | 75 → 68 | 77.0 → 70.8 | **presses 9–12 identical** |
| Bob Dylan → Metallica | random | 9 → 12 | 75 → 66 | 77.0 → 70.7 | — |
| Miley Cyrus (86) → Miles Davis (70) | known-like | 14 → 14 | 68 → 68 | 72.3 → **72.3** | **presses 6–12 identical** |
| Miley Cyrus → Miles Davis | random | 14 → 15 | 68 → 64 | 72.3 → 70.7 | — |
| Weezer (77) → Lady Gaga (86) | known-like | 9 → 10 | 72 → 71 | 77.6 → 74.6 | **presses 7–12 identical** |
| Weezer → Lady Gaga | random | 9 → 12 | 72 → 72 | 77.6 → 75.9 | — |
| Kenny G (70) → Cannibal Corpse (58) | known-like | 11 → 16 | 58 → 49 | 66.4 → 54.5 | — |
| Kenny G → Cannibal Corpse | random | 11 → 20 | 58 → 49 | 66.4 → 52.2 | — |

**Three measured facts:**

1. **The first path's interior popularity tracks the endpoints.** Dylan/Metallica (78, 84)
   → interior mean 77.0. Weezer/Gaga (77, 86) → 77.6. Kenny G/Cannibal Corpse (70, 58) →
   66.4.
2. **`known-like` saturates.** Three of four pairs reach a fixed point and return the
   identical path for every subsequent press. Miley → Miles ends at **exactly** its starting
   interior popularity after 12 presses, having risen to 81.3 at press 5 on the way.
3. **Length does not progressively increase.** 9 → 10, 14 → 14, 9 → 10. Only the pair with
   the two least popular endpoints lengthens materially (11 → 16/20), and that pair is also
   the only one that descends materially.

**Confound, stated:** `known-like` is a heuristic for "artists the user recognises", not a
measurement of it. Both modes show the same saturation and small drift, and the omitted
no-tracks filter means this reconstruction reaches obscurity **more easily** than the real
app did — so the finding is conservative.

---

## (f) Two mechanisms that never ran

**Track-level energy smoothing.** All three shipped front-ends advertise it prominently:
*"we pick a well-known track for each artist that minimizes the difference in energy between
this track, the previous track and the next track"* (`web/index.html:171`,
`new-web/index.html:177`, `new-web/gindex.html:166`), and the author repeats it in both blog
posts.

| file | `minimizeEnergyChange` defined | called |
|---|---|---|
| `web/index.html` (2014) | line 312 | line 501 — **commented out** |
| `new-web/index.html` (2018–20) | line 334 | **no call site** |
| `new-web/gindex.html` | line 307 | **no call site** |

What ships instead is `artist.curTrack = randomIndex(artist.tracks)`
(`new-web/index.html:539`) — a **uniformly random pick** among that artist's ≤ 5 top tracks.

It would have been a no-op regardless in the Spotify era: `data/sp_songs.py:87` sets
`rs['energy'] = .5` for **every** track in `fetch_spotify_tracks`, the function
`crawl_songs` actually calls (`:171`). The function that reads a real
`audio_summary.energy` is `fetch_rdio_tracks` (`:48`), which **nothing calls**. And
`grep -rn energy new_crawler/` returns **zero matches** — the 2018–20 pipeline never
fetched or stored the field at all.

**`simple_edges`.** `artist_graph.py:18` carries a similarity-rank edge-selection branch,
switched off (`self.simple_edges = False`); the cap it feeds is `:19`. That is variant **B**
in §(d).

---

## (g) The cost function, normalised against artistpath's

BoilTheFrog, both generations: `weight = 1 + pop_weight·|Δpop|/100` with `pop_weight = 100`
and Spotify popularity on 0–100 — i.e. **`1 + |Δpop₀₋₁₀₀|`**. Dividing through by 100 to put
the popularity delta on a 0–1 scale gives `0.01 + 1.0·|Δpop₀₋₁|`.

| term | BoilTheFrog (normalised) | artistpath (`api/src/artistpath_api/config.py:44-61`) |
|---|---:|---:|
| popularity jump | 1.0 | `w_jump` = 1.0 |
| per hop | 0.01 | `w_hop` = 0.02 |
| **similarity** | **0** | **`w_sim` = 3.0** |
| obscurity floor | — | `w_floor` = 1.0 |
| avoidance | — | `w_avoid` = 1.0 (`avoid_radius` = 2) |
| degree hub | — | `w_degree_hub` = 0.0 |

Weights cited, not restated as figures of this project's own — `config.py` owns them.

**Similarity is priced at zero in BoilTheFrog.** The similarity data decides only which
edges *exist*; it never prices one. Coherence is a property of graph construction alone.

---

## (h) Search and identity

`new_crawler/search.py::de_norm` ("Dan Ellis normalization") normalises before indexing and
before querying: strips apostrophes and periods, strips accents, lowercases, `&` → `and`,
**strips a leading `the `**, collapses non-word runs to `_`. Prefix match over a sorted
name list via `bisect`; on a local miss it falls back to the live Spotify search API and
caches the result under both the typed and canonical names.

Clips are fetched by **Spotify artist ID** — `spotify.artist_top_tracks(artist['id'])`
(`new_crawler/rdb.py:191`) — the same identifier space the graph is keyed on.

---

## (i) Reproducing this

```bash
git clone https://github.com/plamere/BoilTheFrog.git btf   # pin 1f2cb60
# place btf/ beside these scripts, then:
python btf_graph_measure.py     # (a) (b) and the A-vs-B overlap
python btf_degree_vs_fame.py    # (c)
python btf_factor_table.py      # (d)
python btf_bypass_ladder.py     # (e)
python verify_reconstruction.py # (j) -- run this FIRST; it exits non-zero if the
                                #     build has stopped responding to its inputs
```

`btf/` is **gitignored** and cloned on demand — it carries no licence (see above) and is
~121 MB.

Pure stdlib, no networkx, no artistpath imports. `btf_degree_vs_fame.py`,
`btf_factor_table.py` and `btf_bypass_ladder.py` import `btf_graph_measure` for the loaders.

**Edge-set overlap between variants A and B** (`btf_graph_measure.py`): 129,330 vs 136,129
edges, 38,815 shared — Jaccard **17.13 %**; only **30.01 %** of shipped edges survive under
similarity-rank selection. The two criteria produce substantially different graphs from
identical crawl data.

---

## (j) Positive controls — added at closeout, and they found a defect

`verify_reconstruction.py`, run per closeout **B3**. Every figure above rests on the build
mirroring the original faithfully; a build that silently ignored one of its inputs would
produce a plausible, wrong and entirely green report. So each input is perturbed and the
output must **move**, in a direction predicted before the run.

| | prediction | result |
|---|---|---|
| **C1** | raising `min_popularity` strictly shrinks the graph | ✅ floor 0/30/60 → 45,666 / 45,010 / 5,151 nodes |
| **C2** | raising the per-source cap strictly raises mean degree | ✅ cap 1/4/8 → 1.67 / 5.75 / 10.12 |
| **C3** | at cap 4 the two criteria differ materially | ✅ Jaccard 17.13 %, max degree 38 vs 67 |
| **C4** | at a cap ≥ the longest source list the criterion **cannot** bind, so §(d)'s C and D must be identical | ✅ longest list 20 ≤ cap 20; edge sets and stats identical |
| **C5** | the 3 skipped corrupt lines do not move the result | ✅ 95,056 of 95,059 parsed; build still 45,010 nodes |

**C4 is the one worth having.** It derives §(d)'s vacuous cell from first principles rather
than observing it — the difference between having understood that cell and having noticed it.

> ### The control failed on first run, and the defect was real
>
> `build()` filtered candidates with `popularity.get(e, 0)` but computed the weight with
> `popularity[e]`. The original uses `collections.defaultdict(int)`
> (`new_crawler/artist_graph.py:53`), so an unknown target scores **0** and never raises;
> the plain dict here raises `KeyError`.
>
> **No published figure is affected, and that is proven rather than asserted.** At the
> shipped floor of 30 the filter excludes every unknown target before the weight is
> computed, so the two are behaviourally identical there — the divergence is reachable only
> at a floor ≤ 0, which is why every reported build ran clean. All five figures above
> reproduce byte-identically after the fix.
>
> It is recorded because it is the fourth time in this document's own subject matter that a
> mechanism looked right and was not exercised, and because **it was found by running a
> control, not by reading the code** — which is the same way `TKD-2`, `TKA-1` and §(d)'s
> vacuous cell were found.

---

*Frozen record. Not a tool; not maintained. Figures here are cited by
`docs/superpowers/findings/2026-07-27-boilthefrog-source-review.md` and must not be restated
there.*
