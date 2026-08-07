# Laura Lee closure — does a same-name MBID collision explain her edge?

**Role: ACTIVE — results of record.** Discharges the success condition at
`docs/superpowers/2026-08-06-cocredit-investigation-execution-log.md` §6 item 1.

**This directory OWNS its figures.** Raw `ll_closure.json`, script `ll_closure.py`. Cite it;
never restate the numbers elsewhere.

**⚠ This is DIAGNOSIS of one named case, and it carries no pre-registration BY DESIGN.** It
reads facts about four artists. **Do not retro-fit criteria to it**, and do not read `n=1` as a
population result. What it leaves open is stated in §4, which is the part that must travel with
every citation.

---

## 1. The case

The owner observed novel artists arriving at depth that looked disproportionately like solo
members of known bands, and offered a worked case: **Laura Lee, a Khruangbin member with no
solo releases, at rank 2 on Leon Bridges' list.** Two probes then declined to attribute the
class to recording collaboration — `CCR-` (`null`, instrument-limited) and `RCC-` (`null`,
instrument validated). `RCC-` left her edge unexplained and raised a **same-name MBID
collision** as the live hypothesis: MusicBrainz holds six artists called "Laura Lee", including
a 1945-born soul & gospel singer, and if listens were resolving to the wrong MBID a soul singer
co-occurring with Leon Bridges would explain the edge exactly.

**That hypothesis mattered more than its subject.** It would have been `BYP-13`'s defect class
— a wrong same-named artist — reaching **the graph's edges** rather than a clip, which is
materially worse than anything else open.

## 2. Measured

**Instrument note:** catalogue size counts recordings on which the MBID appears in
`artist-credit`. That is deliberately the measure a **listen** can key to — a play of a track
credited to somebody else does not accrue to a sideman credited only by relationship.

| | Laura Lee, Khruangbin (`50ef58c4…`) | Laura Lee, soul (`70a65cf5…`) | Leon Bridges | Khruangbin |
|---|---|---|---|---|
| Recordings credited | **2** | **288** | 177 | 310 |
| Archived list length | 100 | 100 | 100 | 100 |
| Top / median / min score | 214 / 90 / 74 | 65 / 26 / 21 | 437 / 86 / 65 | 579 / 216 / 179 |
| In adopted graph `43dd82bb…` | **absent** | present, degree 34 | present, degree 43 | present, degree 46 |

**Her two recordings are guest credits on other artists' tracks:** *Not Up for Discussion*
(credited "Niia / Laura Lee") and *Always on Time* ("Meshell Ndegeocello / Laura Lee").
**Neither involves Leon Bridges or Khruangbin.**

**Positions.** Laura Lee (Khruangbin) sits at **rank 2, score 214** on Leon Bridges' own list,
behind only Khruangbin at 437 — the owner's observation confirmed in the direction he met it.
She is **absent from Khruangbin's list**, and that is a **truncation artefact, not an
asymmetry**: Khruangbin's list is dense (median 216) and capped at 100 entries, so her 133 edge
to them falls off the end. Her list carries Khruangbin at rank 3.

**Drop status.** She is in `drop_mbids` — not `keep_mbids` — of **both**
`unlistenable_drop_algb_20260805.json` and `no_release_drop_algb_20260802.json`.

## 3. What this KILLS

**The same-name MBID collision hypothesis is dead for this case.** Four independent reads, and
the second is the decisive one:

1. **Both Laura Lees are separately present in the archive** as reference artists under
   distinct MBIDs, and the ListenBrainz responses are MBID-keyed on both sides
   (`artist_mbid`, `reference_mbid`).
2. **Their lists are disjoint in character with no bleed in either direction.** Hers is 2010s
   psychedelic soul (Leon Bridges, Tame Impala, Khruangbin, SAULT, Skinshape, Unknown Mortal
   Orchestra). The soul singer's is 1960s Southern soul (Wilson Pickett, Otis Redding, Etta
   James, Joe Tex, Muddy Waters). **No soul artist appears in the bassist's top 20 and no
   modern artist in the singer's** — which is exactly what contamination would produce.
3. **The soul singer is not missing her listens.** She holds a 288-recording catalogue and a
   coherent audience of her own. Nothing leaked away from her.
4. **The collision would have had to invent a coherent scene.** Wrongly-attributed listens
   would make the bassist's list look like the singer's. It looks nothing like it.

**So `BYP-13` is NOT operating on the graph's edges in this case**, and the worst reading that
was on the table is removed.

**Also worth recording: the case cannot reach a user today.** She is absent from the adopted
artifact, dropped by the rules that remove artists with nothing of their own to play. Whatever
produced her edge, no journey on the live map can route through her.

## 4. ⚠ What this does NOT settle — and both halves travel together

**(a) The population question is untouched.** The success condition's kill signal reads: *"if
ListenBrainz is shown to key similarity on MBIDs that our own archive can verify as correctly
resolved, the mechanism is unreachable and this closes."* **That is demonstrated for exactly
one pair.** One correctly-resolved pair is not a demonstration that the mapper always resolves
correctly — a collision remains possible for other same-named artists, and plausibly likelier
where both are obscure and the mapper has less to work with. **Nothing here measures a rate,
and no rate may be inferred from this document.**

> **Adjudication, stated plainly because the success condition demands it:** the hypothesis is
> **killed for Laura Lee** and **not settled as a class**. The `§6` item is therefore
> **discharged for its worked case and OPEN as a population question.** It should not be
> recorded as closed.

**(b) Where her 214 actually comes from is still unexplained.** The available explanation is
that her two guest credits are enough — listeners playing those two modern soul tracks also
play Leon Bridges, and session-based similarity credits her for the co-occurrence (`LBS-1`).
**That is consistent with every figure above and is not demonstrated by any of them.** It is a
hypothesis. Specifically unshown: that two tracks can generate an edge of 214, roughly half the
437 that Leon Bridges' actual nine-recording collaborator earns.

**(c) This is not evidence for `TCE-`.** The thin-catalogue pattern that `TCE-` pre-registers
was *suggested* by this case, and a single case cannot support it. `TCE-` tests it at
population scale, within-list and by rank, precisely because the cross-artist score comparison
that makes this case look striking — 2 recordings scoring 214 against 288 scoring 65 — **is
barred** (`TCE-` §0).

## 5. Barred reads

1. **`n=1`.** No rate, share or frequency may be inferred from this document.
2. **This does not reopen widening the drop rule** — closed by the owner 2026-08-06.
3. **No adoption follows.** No default, weight or filter changes on any of it.
4. **Catalogue size here is "recordings credited to the MBID"** — not listen volume, not
   catalogue quality, and looser than the adopted drop rule's sole-credited-and-substantial
   criterion.
5. **The absent-from-Khruangbin's-list fact is a truncation artefact** (§2) and must not be
   cited as an asymmetry finding.

## Reproduce (from `api/`)

```
UV_LINK_MODE=copy PYTHONIOENCODING=utf-8 PYTHONUNBUFFERED=1 uv run python -u \
  ../builder/analysis/2026-08-06-laura-lee-closure/ll_closure.py
```

The MusicBrainz half is cached in `ll_closure.json`; re-runs are offline unless it is deleted.
