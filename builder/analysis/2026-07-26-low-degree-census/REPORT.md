# Artists the app can never introduce you to

### The degree-1 and degree-2 census of the adopted 75k artifact

Read-only. Artifact `sha256 4cb84ef979f2ef3c…` asserted before reading, as the existing scripts under `builder/analysis/` do. **Nothing was rebuilt, routed, adopted or proposed.** No config was touched, no arm was run.


## (a) How many, and out of what

| set | nodes | share of artifact nodes | share of crawled artists |
|---|---:|---:|---:|
| **1 connection** | 6,396 | 8.62 % | 8.53 % |
| **2 connections** | 5,692 | 7.67 % | 7.59 % |
| **both** | 12,088 | 16.29 % | 16.12 % |

### Which denominator — `DRV-4`, resolved

**Both are given, and the answer is that the ambiguity barely matters: they differ by 0.17 percentage points.** Artifact nodes = **74,193**; crawled artists = **75,000** (archived similarity responses).

**They are nested, not alternatives.** `build_from_archive` (`builder/src/artistpath_builder/pipeline.py:131`) sets `known = set(payloads)` — the artists holding their *own* archived similarity response — and keeps a neighbour edge only `if n.mbid in known` (line 184). **So every artifact node is a crawled artist**; an artist discovered in someone else's similarity list but never crawled is never a node at all. The 807 crawled artists absent from the artifact were removed by the special-purpose filter, by holding no surviving edge after the mutual-kNN cap, or by the largest-component prune.

### Counted after the largest-component prune — confirmed

The artifact is written from `pruned`, built from `keep = largest_component(...)` (`pipeline.py:231-238`), so every node read here is already post-prune. The observable consequence, measured: the **minimum degree anywhere in these sets is 1**, and **0** neighbours have degree < 1. A pre-prune count would have included degree-0 isolates and whole disconnected islands.

### Non-artist entities — confirmed excluded

The build's only type filter is `is_special_purpose`, a case-insensitive match on the literal `special purpose` in the MusicBrainz disambiguation (`pipeline.py:42-47`). Nothing else is excluded by type, so this was checked rather than assumed: **0** placeholder disambiguations survive in these sets. A deliberately broader scan for container-like names (`Various Artists`, `[unknown]`, `Soundtrack`, …) flagged only two, and **both are genuine artists** — `NA` (*NA is Daniel Pineda, aka 1/2 of Nguzunguzu*) and `Unknown` (*US rapper Richard Patterson*). The one real contaminant is the **12 nameless nodes**, excluded from the lists below and reported in the caveats.

### Why these two sets

- **1 connection** — a card in the middle of a journey needs a neighbour on each side, so these artists can *only* ever appear as one of the two artists you typed in yourself. **The app can never introduce you to them.** (`DRV-4` states this as structural and unmeasured; this is the measurement.)
- **2 connections** — reachable in the middle, but by exactly one route: in through one neighbour and out through the other. Deliverable only when the router happens to price that single detour.


## How the fame figures were obtained

Fame is **English-Wikipedia annual pageviews** over A11's fixed window (2025-07 … 2026-06), via the canonical resolver, with an artist that has no English article scored at the **fame floor**. That is the proxy this project adopted (pre-registration §5 + amendment **A11**), including A15's recall fallback — which matters more here than anywhere it has been used, because a fame-*ranked* list is exactly where a household name wrongly floored (Justice, Rainbow, Ye) would vanish without trace.

**The graph's own popularity was NOT used to rank anything** (Phase 1 log §2.11: at the top of the distribution it disagrees with household fame). It was used only to decide *who to ask*, because polling all 12,041 names is ~120,000 API requests and Wikipedia asks for ~1 request/second on one or two connections. The top **400 by popularity in each set** were polled, plus a seeded random **200 from below the cut in each set** as a control.

**Why popularity is a safe screen here even though it is a bad ranker.** It is score-weighted in-degree accumulated at `pipeline.py:206-216` — *before* `mutual_knn_cap` (227), `symmetrise` (230) and `largest_component` (231) — so it is summed over the **full uncapped neighbour lists**. The reciprocity rule destroys a stranded artist's degree and leaves its popularity untouched. Degree and popularity are not merely different currencies (§2.6); they are read at different stages of the build, and the screen rides on the stage the defect never reaches.

### Did the screen leak? The control sample

**The test is whether a control artist would have made the delivered list** — not whether it beats the screened set's weakest member. The screened set is full of low-fame artists by construction (high popularity does not imply high fame — that is §2.11), so its minimum is near zero and almost any control artist with an article would clear it. That comparison would fire on noise and mean nothing. The question that matters is whether polling everything would have changed the top of the list.

**1 connection.** 338 of the 400 screened have an English article. The delivered list ends at **19,616 pageviews** — that is the bar a below-cut artist must clear to belong in it.
    Control (200 random from the 5,996 below the cut): **36 would have made the list**, the strongest being **Kny** at 2,270,316 pageviews. **The screen leaks.** At 36/200 that implies roughly **1079** artists below the cut belong in the list and are missing from it.

**2 connections.** 345 of the 400 screened have an English article. The delivered list ends at **29,663 pageviews** — that is the bar a below-cut artist must clear to belong in it.
    Control (200 random from the 5,292 below the cut): **19 would have made the list**, the strongest being **Gosling** at 4,734,038 pageviews. **The screen leaks.** At 19/200 that implies roughly **503** artists below the cut belong in the list and are missing from it.


### ⚠ Those leak figures are WITHDRAWN — the fame proxy misidentifies artists at this end of the graph

**The leak estimates above are not interpretable, and the coverage-gap reading they were about to support is withdrawn.** Inspecting the highest-fame control artists shows the proxy is not measuring the artist the graph means. The two strongest supposed leaks are **Gosling → the article *Ryan Gosling*** and **Kny → the article *Demon Slayer: Kimetsu no Yaiba***. Neither is an obscure stranded musician who turned out to be famous; both are a name-only lookup landing on a different subject.

**Why the proxy does this here specifically, and why A11's validation did not see it.** The resolver matches on a Wikidata label or alias and then requires the entity to be a musical performer. It never consults the **disambiguation the graph already holds**. At this end of the artifact the names are short and generic — *War*, *Sparks*, *Shining*, *Proof*, *Psycho*, *Ariel*, *God*, *Meth* — so a collision is likely, and when it happens the *more famous* entity wins the pageview count by construction. A11 was validated on a purposively-chosen sample of mostly-recognisable acts, where this barely bites. **This is a scope limit on the adopted fame proxy, not a defect in this census's use of it**, and it is not in the record.

**The graph's own disambiguation contradicts the match in most of the clear cases** — which is what makes them identifiable at all, and names the cheapest possible fix:

| graph name | the graph's disambiguation | article the proxy measured |
|---|---|---|
| War | *US funk/rock band* | **Axl Rose** |
| WATERS | *2010s US-Norwegian band* | **Roger Waters** |
| Cassidy | *US rapper Barry Reese* | **David Cassidy** |
| Sparks | *US rock and pop duo, The Mael brothers* | **Jordin Sparks** |
| Shining | *Norwegian jazz/metal/rock* | **The Shining (novel)** |
| Meth | *UK drum & bass artist* | **Method Man** |
| MZ | *French rap group* | **Yusaku Maezawa** |
| God | *Viking Metal band from Romania* | **G.o.d** |
| Divinity | *Finland/ambient project* | **Divinity (series)** |
| Psycho | *US rapper* | **Psycho (novel)** |

**delivered lists:** of 683 matched artists, 115 (17 %) measured an article that is the same name plus a Wikipedia parenthetical — **usually** right — and **57 (8 %) measured a differently-named subject**, which is where most misidentification lives.
**control sample:** of 152 matched artists, 43 (28 %) measured an article that is the same name plus a Wikipedia parenthetical — **usually** right — and **30 (20 %) measured a differently-named subject**, which is where most misidentification lives.

**The parenthetical class is not reliably safe either, so it is not a clean bill of health.** Checked against the graph's disambiguation, the great majority are right (*Elbow* → *Elbow (band)*, graph says *UK rock band*), but there are real errors hiding in it: *Friends* → *Friends (Swedish band)* where the graph says *Brooklyn based group, formed 2010*, and *Proof* → *Proof (rapper)* — the US rapper of D12 — where the graph says *UK grime MC*. A parenthetical means Wikipedia had to separate same-named topics, which is exactly when picking the wrong one is possible.

**`different_title` is an upper bound on that class's error, not the error rate.** The resolver accepts any Wikidata label or alias, so a real name resolving to a stage name (*Marcus Füreder* → *Parov Stelar*) or a non-Latin name resolving to its romanisation (*裸のラリーズ* → *Les Rallizes Dénudés*, *威神V* → *WayV*) lands in this class **correctly**. By hand, roughly half to two-thirds of them are genuine errors. Every one is flagged **⚠ IDENTITY UNVERIFIED** inline, so the judgement is the reader's rather than a rate they have to trust.

**Where the damage concentrates is the worst possible place: the top.** A misidentified row inherits the *more famous* entity's pageviews, so it sorts upward. The first twenty rows of each list — the part actually meant to be eyeballed — carry a higher error density than the body.

**What survives this, and it is the question that was asked.** The census was run to find out whether recognisable artists are stranded where the app can never introduce them. The correctly-identified rows answer that on their own: Meat Loaf, Ringo Starr, Eddie Vedder, Aaron Carter, Paula Abdul, DJ Khaled and Charlotte Gainsbourg at one connection; Marilyn Monroe, Jermaine Jackson, Stevie Nicks, Barbra Streisand, Nick Jonas, Kid Rock, John Fogerty, Milli Vanilli, Joe Cocker and Todd Rundgren at two. **The ordering is contaminated; the finding is not.**

**The obvious fix — give the resolver the disambiguation the graph already holds — reaches less than half the problem, and misses the worst of it.** Only **337 of 835 (40 %)** matched rows carry a disambiguation at all; the other 498 cannot be adjudicated this way even in principle. **And the two most extreme errors are in that blind half** — *Gosling* → *Ryan Gosling* and *Kny* → *Demon Slayer* both have an **empty** disambiguation, so the check would pass them through untouched. It would catch the *War* / *WATERS* / *Cassidy* / *Sparks* class and stop there.

**So it is named as the cheapest *first* check, not as a fix**, and it is not run here. Any change to the resolver is a change to **A11's adopted, validated instrument** — not this measurement's to make, and re-scoring Track 2's figures against a modified resolver is a separate decision needing its own pre-registration.

**What the control sample does and does not establish.** It tests the screen cases nothing selected for fame, which `verify_screen.py`'s ground truth could not: `MKS-2`'s six artists were found by noticing *recognisable* names among low-degree ones, so they were already correlated with being well-connected pre-cap. The control is not selected on anything. What it still cannot see is the screen's one known failure direction — an artist famous in a population this snowball crawl under-covers would sit low on popularity *and* be missed by a 200-node sample. That is the same blind-spot direction A11 already accepts for Wikipedia-absence, so the two instruments do not cross-check each other.

For scale, `verify_screen.py`'s result: all five `MKS-2` artists present in this set rank in the **top 11 of 6,396** by popularity — Nada Surf 1st, The Cult 4th, Meat Loaf 7th, Elbow 8th, The Streets 11th — against a cut at 400. (Pretenders is absent because it holds 6 connections, which is the finding's own figure and a consistency check passing.)


## (b) The 200 highest-fame artists with only 1 connection

Ranked by English-Wikipedia annual pageviews, highest first. Drawn from the 400 highest-popularity nodes of the 6,396 with 1 connection; 338 of those have an English article.

   1. **Marky Mark** — 3,206,402 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Mark Wahlberg*, a differently-named subject
   2. **Ringo Starr** — *The Beatles* — 2,517,109 annual pageviews
   3. **Aaron Carter** — *US teen pop vocalist* — 1,414,162 annual pageviews
   4. **Christina Grimmie** — 1,389,048 annual pageviews
   5. **Meat Loaf** — 1,318,338 annual pageviews
   6. **Eddie Vedder** — 1,279,056 annual pageviews
   7. **WATERS** — *2010s US‐Norwegian band, led by Van Pierszalowski* — 1,131,984 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Roger Waters*, a differently-named subject, while the graph says *2010s US‐Norwegian band, led by Van Pierszalowski*
   8. **Paula Abdul** — *American singer* — 1,083,635 annual pageviews
   9. **DJ Khaled** — *American hip hop DJ & producer* — 1,044,658 annual pageviews
  10. **Cassidy** — *US rapper Barry Reese* — 993,155 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *David Cassidy*, a differently-named subject, while the graph says *US rapper Barry Reese*
  11. **t.A.T.u.** — *Russian duo* — 900,392 annual pageviews
  12. **Charlotte Gainsbourg** — 872,078 annual pageviews
  13. **Engelbert Humperdinck** — *British pop singer* — 841,291 annual pageviews  
    measured article: *Engelbert Humperdinck (singer)*
  14. **Katharine McPhee** — 798,268 annual pageviews
  15. **Nancy Wilson** — *guitarist/singer of “Heart”* — 702,867 annual pageviews  
    measured article: *Nancy Wilson (rock musician)*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart
  16. **Spın̈al Tap** — 581,165 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Spinal Tap (band)*, a differently-named subject
  17. **Donald Fagen** — 570,756 annual pageviews
  18. **GWAR** — 559,071 annual pageviews
  19. **Tenacious D** — *American comedy rock duo* — 485,060 annual pageviews
  20. **Lauren Jauregui** — 476,963 annual pageviews
  21. **k.d. lang** — 450,620 annual pageviews
  22. **Aaron Lewis** — *lead vocalist for Staind* — 449,929 annual pageviews
  23. **Soulja Boy** — *US rapper fka Soulja Boy Tell ’Em* — 438,588 annual pageviews
  24. **Alexander Ebert** — *singer in Edward Sharpe and the Magnetic Zeros* — 435,006 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Alex Ebert*, a differently-named subject, while the graph says *singer in Edward Sharpe and the Magnetic Zeros*
  25. **The Cult** — *British rock band* — 428,848 annual pageviews
  26. **Midge Ure** — 427,469 annual pageviews
  27. **Billy Ocean** — 404,158 annual pageviews
  28. **LP** — *pop/rock artist LP Pergolizzi* — 378,048 annual pageviews  
    measured article: *LP (singer)*
  29. **Scissor Sisters** — 374,598 annual pageviews
  30. **Craig David** — 351,079 annual pageviews
  31. **Velvet Revolver** — 343,552 annual pageviews
  32. **Wheatus** — 304,848 annual pageviews
  33. **The Waterboys** — *folk-rock* — 295,401 annual pageviews
  34. **Bobbie Gentry** — *Roberta Lee Streeter - American singer-songwriter* — 289,765 annual pageviews
  35. **Iggy and The Stooges** — 282,064 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *The Stooges*, a differently-named subject
  36. **Andrew Gold** — 240,671 annual pageviews
  37. **Ronnie Dunn** — *American country music singer-songwriter and record producer* — 240,369 annual pageviews
  38. **Rocko** — *Atlanta, US rapper* — 237,871 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Rocko's Modern Life*, a differently-named subject, while the graph says *Atlanta, US rapper*
  39. **Bobby McFerrin** — 235,276 annual pageviews
  40. **Tremonti** — *band fronted by Mark Tremonti* — 227,087 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Mark Tremonti*, a differently-named subject, while the graph says *band fronted by Mark Tremonti*
  41. **Jessica** — *American/South Korean singer* — 220,271 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Jessica Jung*, a differently-named subject, while the graph says *American/South Korean singer*; recovered by the A15 fallback
  42. **El DeBarge** — 212,378 annual pageviews
  43. **Mountain** — *US hard rock band* — 210,876 annual pageviews  
    measured article: *Mountain (band)*; recovered by the A15 fallback
  44. **Johnny Rivers** — *Singer, songwriter, and guitarist* — 203,984 annual pageviews
  45. **The Communards** — 195,871 annual pageviews
  46. **Rag’n’Bone Man** — 193,146 annual pageviews
  47. **The Streets** — *Mike Skinner* — 191,784 annual pageviews
  48. **Will Young** — *British singer-songwriter and actor* — 187,108 annual pageviews
  49. **Rachel Platten** — 184,771 annual pageviews
  50. **Fountains of Wayne** — 184,440 annual pageviews
  51. **Screamin’ Jay Hawkins** — 178,530 annual pageviews
  52. **James Gang** — *US rock group* — 177,467 annual pageviews
  53. **The Sugarhill Gang** — 176,313 annual pageviews
  54. **Pure Prairie League** — *American country band* — 176,234 annual pageviews
  55. **Mike Bloomfield** — *guitarist, songwriter* — 172,358 annual pageviews
  56. **The Boomtown Rats** — 172,298 annual pageviews
  57. **Manfred Mann’s Earth Band** — 169,952 annual pageviews
  58. **Jonathan Richman** — 162,446 annual pageviews
  59. **Hum** — *US alternative rock band* — 159,797 annual pageviews  
    measured article: *Hum (band)*; recovered by the A15 fallback
  60. **Chanté Moore** — 157,761 annual pageviews
  61. **A★Teens** — 157,618 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *A-Teens*, a differently-named subject; recovered by the A15 fallback
  62. **Budgie** — *hard rock band from Cardiff, South Glamorgan, Wales* — 153,345 annual pageviews  
    measured article: *Budgie (band)*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart
  63. **Prophets of Rage** — *Rage Against the Machine, Chuck D & B‐Real supergroup* — 152,802 annual pageviews
  64. **Confidence Man** — *Australian electropop band* — 149,830 annual pageviews  
    measured article: *Confidence Man (band)*
  65. **Mike WiLL Made‐It** — 148,515 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Mike Will Made It*, a differently-named subject
  66. **Saint Etienne** — 146,621 annual pageviews  
    measured article: *Saint Etienne (band)*
  67. **Johnny Nash** — *US reggae/pop singer-songwriter* — 142,559 annual pageviews
  68. **Sheck Wes** — *rapper, on Cactus Jack Records and G.O.O.D. Music* — 140,002 annual pageviews
  69. **Neil Cicierega** — 139,543 annual pageviews
  70. **Katrina and the Waves** — *British‐American rock band* — 135,037 annual pageviews
  71. **Crazy Horse** — *American rock band often working with Neil Young* — 133,148 annual pageviews  
    measured article: *Crazy Horse (band)*
  72. **Elbow** — *UK rock band* — 131,019 annual pageviews  
    measured article: *Elbow (band)*
  73. **Electric Six** — *Detroit, USA rock, previously The Wildbunch* — 130,765 annual pageviews
  74. **The Walker Brothers** — *60s/70s pop band* — 129,947 annual pageviews
  75. **JEON SOYEON** — 127,390 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Soyeon*, a differently-named subject
  76. **Ella Henderson** — 125,774 annual pageviews
  77. **Mark Snow** — *American score composer* — 125,214 annual pageviews
  78. **The Tokens** — 121,857 annual pageviews
  79. **Kenny Lattimore** — 120,802 annual pageviews
  80. **Fleur East** — 120,624 annual pageviews
  81. **Deborah Cox** — 118,146 annual pageviews
  82. **Barry McGuire** — 115,250 annual pageviews
  83. **Echosmith** — 110,232 annual pageviews
  84. **The Fabulous Thunderbirds** — 106,035 annual pageviews
  85. **Les Rythmes Digitales** — 104,425 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Stuart Price*, a differently-named subject
  86. **Kelly Price** — 104,158 annual pageviews
  87. **The Cat Empire** — 101,806 annual pageviews
  88. **Des’ree** — 98,933 annual pageviews
  89. **Lipps, Inc.** — 98,886 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Lipps Inc.*, a differently-named subject
  90. **Ailee** — 98,612 annual pageviews
  91. **Eddie Hazel** — 94,757 annual pageviews
  92. **Pilot** — *70s Scottish band* — 94,583 annual pageviews  
    measured article: *Pilot (Scottish band)*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart; recovered by the A15 fallback
  93. **Airbourne** — *Australian hard rock band* — 92,709 annual pageviews  
    measured article: *Airbourne (band)*
  94. **Cornershop** — 91,540 annual pageviews
  95. **Deadsy** — *Californian undercore band* — 88,041 annual pageviews
  96. **Womack & Womack** — 86,864 annual pageviews
  97. **Sigue Sigue Sputnik** — 85,873 annual pageviews
  98. **Ezra Furman** — *US musician/songwriter* — 84,856 annual pageviews
  99. **Prong** — *US metal band* — 80,668 annual pageviews  
    measured article: *Prong (band)*
 100. **The Polyphonic Spree** — 76,982 annual pageviews
 101. **Sloan** — *Canadian power pop band* — 74,532 annual pageviews  
    measured article: *Sloan (band)*
 102. **The Blow Monkeys** — 73,761 annual pageviews
 103. **Guster** — 72,919 annual pageviews
 104. **Álvaro Soler** — 72,434 annual pageviews
 105. **Stereo MC’s** — 72,247 annual pageviews
 106. **Rooney** — *US band* — 71,010 annual pageviews  
    measured article: *Rooney (band)*; recovered by the A15 fallback
 107. **The New Basement Tapes** — 70,932 annual pageviews
 108. **Half Man Half Biscuit** — 69,776 annual pageviews
 109. **Heatmiser** — 68,261 annual pageviews
 110. **The Click Five** — 66,788 annual pageviews
 111. **Tantric** — 65,923 annual pageviews  
    measured article: *Tantric (band)*
 112. **Living in a Box** — 65,455 annual pageviews
 113. **Lady Sovereign** — 64,855 annual pageviews
 114. **Agnes** — *Swedish singer Agnes Carlsson* — 63,414 annual pageviews  
    measured article: *Agnes (singer)*; recovered by the A15 fallback
 115. **Hot Chelle Rae** — 62,578 annual pageviews
 116. **Greyson Chance** — 62,193 annual pageviews
 117. **Gabriella Cilmi** — 61,921 annual pageviews
 118. **Badly Drawn Boy** — 61,713 annual pageviews
 119. **DeJ Loaf** — *Detroit rapper* — 61,288 annual pageviews
 120. **Wall of Voodoo** — *US rock band from L.A.* — 59,751 annual pageviews
 121. **Mary Lou Williams** — *American jazz pianist and composer* — 59,554 annual pageviews
 122. **Therapy?** — *Irish alternative metal band* — 58,869 annual pageviews
 123. **Timber Timbre** — 56,157 annual pageviews
 124. **Gossip** — *USA alt rock band* — 56,095 annual pageviews  
    measured article: *Gossip (band)*; recovered by the A15 fallback
 125. **Jai Paul** — 55,651 annual pageviews
 126. **Lissie** — 55,238 annual pageviews
 127. **Nada Surf** — *US alternative rock band* — 54,513 annual pageviews
 128. **Erika de Casier** — *Portugal-born Danish singer, songwriter, and producer* — 53,533 annual pageviews
 129. **Ron Sexsmith** — 52,877 annual pageviews
 130. **Tracy Bonham** — 52,335 annual pageviews
 131. **Bill Nelson** — *English experimental musician* — 52,299 annual pageviews  
    measured article: *Bill Nelson (musician)*
 132. **Steve Harley & Cockney Rebel** — 51,987 annual pageviews
 133. **Parmalee** — 51,553 annual pageviews
 134. **Kaoma** — *French-Brazilian pop group* — 51,299 annual pageviews
 135. **Fairground Attraction** — 48,613 annual pageviews
 136. **The Airborne Toxic Event** — *American indie band* — 48,403 annual pageviews
 137. **MEDUZA** — *Italian production trio* — 47,927 annual pageviews  
    measured article: *Meduza (producers)*
 138. **Saigon Kick** — 46,062 annual pageviews
 139. **BETWEEN FRIENDS** — *indie pop-rock duo* — 45,975 annual pageviews  
    measured article: *Between Friends (duo)*
 140. **Kasey Chambers** — *Australian country singer‐songwriter* — 45,847 annual pageviews
 141. **Calexico** — 44,680 annual pageviews  
    measured article: *Calexico (band)*
 142. **I Set My Friends on Fire** — 44,081 annual pageviews
 143. **Dustin Kensrue** — 42,706 annual pageviews
 144. **Eighteen Visions** — *Californian metalcore band* — 42,196 annual pageviews
 145. **All About Eve** — 41,536 annual pageviews  
    measured article: *All About Eve (band)*
 146. **Rachelle Ferrell** — 39,030 annual pageviews
 147. **Dario G** — 37,924 annual pageviews
 148. **Todd Terry** — *US house DJ, producer and remixer* — 37,733 annual pageviews
 149. **Rob Scallon** — 37,434 annual pageviews
 150. **The Sleepy Jackson** — 36,842 annual pageviews
 151. **Jens Lekman** — 36,703 annual pageviews
 152. **Edge of Sanity** — *Swedish progressive death metal band* — 35,927 annual pageviews
 153. **Charlie Clouser** — 35,749 annual pageviews
 154. **K.Will** — 34,829 annual pageviews
 155. **DARKSIDE** — *US electronic band from NYC* — 34,572 annual pageviews  
    measured article: *Darkside (band)*
 156. **David Usher** — 34,543 annual pageviews
 157. **Owen Pallett** — *Canadian composer, violinist, keyboardist & vocalist* — 34,508 annual pageviews
 158. **The Magic Numbers** — 34,292 annual pageviews
 159. **Natural Snow Buildings** — 34,187 annual pageviews
 160. **Black Kids** — *US indie rock band from Florida* — 33,924 annual pageviews
 161. **The Wreckers** — 33,759 annual pageviews
 162. **Drake White** — *country singer-songwriter* — 32,729 annual pageviews
 163. **Paul & Paula** — *1960s US pop duo* — 32,472 annual pageviews
 164. **Cloud Cult** — 32,276 annual pageviews
 165. **Rotary Connection** — 32,208 annual pageviews
 166. **Half Japanese** — 31,066 annual pageviews
 167. **Ace** — *1970s UK rock band* — 30,810 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *A.C.E (South Korean band)*, a differently-named subject, while the graph says *1970s UK rock band*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart; recovered by the A15 fallback
 168. **The Von Bondies** — 30,706 annual pageviews
 169. **Lolo Zouaï** — 30,150 annual pageviews
 170. **Belouis Some** — 29,731 annual pageviews
 171. **Superorganism** — *London-based indie pop band* — 29,563 annual pageviews  
    measured article: *Superorganism (band)*
 172. **The Pierces** — 29,521 annual pageviews
 173. **MadeinTYO** — 29,117 annual pageviews
 174. **Last Dinosaurs** — 29,005 annual pageviews
 175. **The Big Pink** — *London based electro duo* — 28,972 annual pageviews
 176. **Dead by April** — 28,182 annual pageviews
 177. **Money Man** — 28,075 annual pageviews
 178. **AronChupa** — 27,522 annual pageviews
 179. **Will Haven** — 26,517 annual pageviews
 180. **White Denim** — *US rock band* — 26,453 annual pageviews
 181. **I Am Kloot** — *English rock band* — 25,795 annual pageviews
 182. **Afro Celt Sound System** — 25,787 annual pageviews
 183. **These New Puritans** — 25,413 annual pageviews
 184. **Glasvegas** — 24,519 annual pageviews
 185. **Tove Styrke** — 23,874 annual pageviews
 186. **Willy William** — *French DJ, producer & singer* — 23,716 annual pageviews
 187. **Sacramentum** — *Swedish melodic black/death metal* — 23,340 annual pageviews  
    measured article: *Sacramentum (band)*
 188. **Mohombi** — 22,865 annual pageviews
 189. **Reamonn** — *German pop rock band* — 22,657 annual pageviews
 190. **Bob Lind** — 22,409 annual pageviews
 191. **The Veils** — *English/New Zealand rock band* — 22,020 annual pageviews
 192. **Stina Nordenstam** — 21,704 annual pageviews
 193. **Motorpsycho** — *Norwegian psychedelic rock band* — 21,543 annual pageviews  
    measured article: *Motorpsycho (band)*
 194. **Blacktop Mojo** — 20,079 annual pageviews
 195. **The American Analog Set** — 20,030 annual pageviews
 196. **Adept** — *Swedish metalcore* — 19,866 annual pageviews  
    measured article: *Adept (band)*
 197. **Dirty Vegas** — 19,840 annual pageviews
 198. **Dot Allison** — 19,834 annual pageviews
 199. **Grace Potter & the Nocturnals** — 19,667 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Grace Potter and the Nocturnals*, a differently-named subject
 200. **Girls' Generation-TTS** — *Girls' Generation subgroup* — 19,616 annual pageviews

## (c) The 200 highest-fame artists with only 2 connections

Ranked by English-Wikipedia annual pageviews, highest first. Drawn from the 400 highest-popularity nodes of the 5,692 with 2 connections; 345 of those have an English article.

   1. **Marilyn Monroe** — *US actress, model & singer* — 4,048,318 annual pageviews
   2. **Jermaine Jackson** — *soul/pop singer, of Jackson 5* — 3,967,741 annual pageviews
   3. **Stevie Nicks** — 2,896,697 annual pageviews
   4. **Barbra Streisand** — 2,795,094 annual pageviews
   5. **Nick Jonas** — 2,302,725 annual pageviews
   6. **Kid Rock** — *American singer/rapper* — 2,189,257 annual pageviews
   7. **Tom Jones** — *Welsh pop singer* — 1,340,931 annual pageviews  
    measured article: *Tom Jones (singer)*
   8. **War** — *US funk/rock band* — 1,283,813 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Axl Rose*, a differently-named subject, while the graph says *US funk/rock band*; recovered by the A15 fallback
   9. **John Fogerty** — 1,172,872 annual pageviews
  10. **Milli Vanilli** — 1,050,196 annual pageviews
  11. **Monty Python** — *British surreal comedy group* — 901,956 annual pageviews
  12. **Joe Cocker** — 821,710 annual pageviews
  13. **Todd Rundgren** — 815,778 annual pageviews
  14. **The Divine Comedy** — 810,685 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Divine Comedy*, a differently-named subject
  15. **Sebastian Bach** — *Canadian metal singer* — 810,257 annual pageviews
  16. **Israel Kamakawiwoʻole** — 787,921 annual pageviews
  17. **Emma Bunton** — 770,656 annual pageviews
  18. **Corey Taylor** — 753,164 annual pageviews
  19. **Vanilla Ice** — 716,683 annual pageviews
  20. **The B‐52s** — 642,433 annual pageviews
  21. **Peter Frampton** — 635,608 annual pageviews
  22. **Richard Ashcroft** — 635,187 annual pageviews
  23. **Tracey Ullman** — 631,907 annual pageviews
  24. **Christian Lee Hutson** — 599,323 annual pageviews
  25. **Siouxsie Sioux** — 583,654 annual pageviews
  26. **Swizz Beatz** — *US hip hop producer* — 501,527 annual pageviews
  27. **Bonnie Raitt** — 496,144 annual pageviews
  28. **Gotye** — 488,533 annual pageviews
  29. **Alesha Dixon** — *English singer, rapper, dancer and author* — 486,008 annual pageviews
  30. **The Chipmunks** — 480,787 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Alvin and the Chipmunks*, a differently-named subject
  31. **The Guess Who** — *Canadian rock band* — 478,232 annual pageviews
  32. **Nate Ruess** — 475,887 annual pageviews
  33. **Levon Helm** — 473,790 annual pageviews
  34. **Badfinger** — 458,320 annual pageviews
  35. **Eve** — *US rapper/singer* — 453,289 annual pageviews  
    measured article: *Eve (rapper)*; ⚠ shares this name with 3 other node(s) in the graph — the fame figure cannot tell them apart; recovered by the A15 fallback
  36. **Jarvis Cocker** — 442,827 annual pageviews
  37. **Alison Moyet** — 426,389 annual pageviews
  38. **Tinashe** — *American R&B singer* — 423,866 annual pageviews
  39. **Grace VanderWaal** — 422,645 annual pageviews
  40. **Jordin Sparks** — 422,293 annual pageviews
  41. **Sparks** — *US rock and pop duo, The Mael Brothers* — 422,293 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Jordin Sparks*, a differently-named subject, while the graph says *US rock and pop duo, The Mael Brothers*
  42. **Shining** — *Norwegian jazz/metal/rock group* — 412,458 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *The Shining (novel)*, a differently-named subject, while the graph says *Norwegian jazz/metal/rock group*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart
  43. **Crowded House** — *Australian rock group* — 400,728 annual pageviews
  44. **Daniel Johnston** — *US singer‐songwriter* — 390,734 annual pageviews
  45. **Leo Sayer** — 382,501 annual pageviews
  46. **Faces** — *successor of “Small Faces”, members Rod Stewart, Ron Wood* — 382,139 annual pageviews  
    measured article: *Faces (band)*
  47. **Extreme** — *US rock band* — 372,418 annual pageviews  
    measured article: *Extreme (band)*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart; recovered by the A15 fallback
  48. **Karen Elson** — *English model and singer-songwriter* — 367,262 annual pageviews
  49. **Dr. Hook** — *aka “Dr. Hook & the Medicine Show”* — 358,383 annual pageviews
  50. **Gipsy Kings** — 344,848 annual pageviews
  51. **Ian Brown** — *UK singer, member of Stone Roses* — 316,856 annual pageviews
  52. **Blind Faith** — *English rock supergroup* — 316,233 annual pageviews
  53. **Grand Funk Railroad** — 315,782 annual pageviews
  54. **Ben Lee** — *Australian singer/songwriter* — 310,209 annual pageviews
  55. **Dexys Midnight Runners** — 299,941 annual pageviews
  56. **Mike + the Mechanics** — 277,297 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Mike and the Mechanics*, a differently-named subject
  57. **Billy Bragg** — 252,841 annual pageviews
  58. **Alabama Shakes** — 250,482 annual pageviews
  59. **Aaron Neville** — 243,128 annual pageviews
  60. **Big Country** — 240,749 annual pageviews
  61. **Vince Guaraldi** — *pianist* — 238,788 annual pageviews
  62. **Paolo Nutini** — 237,734 annual pageviews
  63. **N*E*R*D** — 234,299 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *N.E.R.D.*, a differently-named subject
  64. **Manu Chao** — *French singer‐songwriter* — 227,178 annual pageviews
  65. **3OH!3** — 225,047 annual pageviews
  66. **Paul Di’Anno** — 224,501 annual pageviews
  67. **Darren Hayes** — 220,209 annual pageviews
  68. **Cher Lloyd** — 217,127 annual pageviews
  69. **Chet Atkins** — 209,019 annual pageviews
  70. **Christopher Williams** — *R&B singer* — 208,957 annual pageviews  
    measured article: *Christopher Williams (singer)*
  71. **Iron Butterfly** — 208,428 annual pageviews
  72. **Foghat** — 208,094 annual pageviews
  73. **Jon Bellion** — 206,817 annual pageviews
  74. **Rickie Lee Jones** — 197,447 annual pageviews
  75. **The Archies** — 195,482 annual pageviews
  76. **Smokie** — *English rock band, aka Smokey* — 194,278 annual pageviews  
    measured article: *Smokie (band)*
  77. **Stray Cats** — 184,626 annual pageviews
  78. **Brett Anderson** — *Suede* — 183,648 annual pageviews
  79. **HENRY** — *Henry Lau, Super Junior-M ex-member* — 181,012 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Henry Lau*, a differently-named subject, while the graph says *Henry Lau, Super Junior-M ex-member*; recovered by the A15 fallback
  80. **Aloe Blacc** — 177,301 annual pageviews
  81. **The Caretaker** — *electronic artist James Kirby* — 163,206 annual pageviews  
    measured article: *The Caretaker (musician)*
  82. **Archy Marshall** — *King Krule real name* — 162,041 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *King Krule*, a differently-named subject, while the graph says *King Krule real name*
  83. **Beth Hart** — *US singer-songwriter* — 159,518 annual pageviews
  84. **Big Star** — 157,535 annual pageviews
  85. **Michael Learns to Rock** — 152,499 annual pageviews
  86. **The Sugarcubes** — *Icelandic alternative/post-punk rock band* — 149,564 annual pageviews
  87. **Candi Staton** — 148,294 annual pageviews
  88. **Leslie Grace** — 147,398 annual pageviews
  89. **Blu Cantrell** — 147,310 annual pageviews
  90. **Roger Whittaker** — 145,728 annual pageviews
  91. **Marc Cohn** — 142,632 annual pageviews
  92. **Triumph** — *Canadian rock band* — 138,160 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Triumph the Insult Comic Dog*, a differently-named subject, while the graph says *Canadian rock band*
  93. **D:Ream** — *Northern Irish pop rock & dance group* — 137,000 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *D Ream*, a differently-named subject, while the graph says *Northern Irish pop rock & dance group*
  94. **박진영** — *South Korean singer and producer J.Y. Park* — 135,703 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *J.Y. Park*, a differently-named subject, while the graph says *South Korean singer and producer J.Y. Park*
  95. **Fishbone** — *US rock band* — 132,706 annual pageviews
  96. **Matt Berninger** — 131,759 annual pageviews
  97. **Them** — *Northern Irish group originally feat. Van Morrison* — 130,718 annual pageviews  
    measured article: *Them (band)*; recovered by the A15 fallback
  98. **O.A.R.** — 126,822 annual pageviews
  99. **Scott McKenzie** — 126,501 annual pageviews
 100. **The Calling** — *US rock band* — 125,332 annual pageviews  
    measured article: *The Calling (band)*
 101. **김예림** — *Lim Kim* — 124,669 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Yeri (singer)*, a differently-named subject, while the graph says *Lim Kim*; recovered by the A15 fallback
 102. **DAWN** — *South Korean singer and rapper* — 122,906 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Tony Orlando and Dawn*, a differently-named subject, while the graph says *South Korean singer and rapper*; recovered by the A15 fallback
 103. **Plies** — 118,157 annual pageviews  
    measured article: *Plies (rapper)*
 104. **Beady Eye** — 117,428 annual pageviews
 105. **Tina Arena** — 116,022 annual pageviews
 106. **Akira Yamaoka** — 115,242 annual pageviews
 107. **Pete Shelley** — *Buzzcocks lead singer* — 110,351 annual pageviews
 108. **Karmin** — 103,685 annual pageviews
 109. **Cavalera Conspiracy** — 99,684 annual pageviews
 110. **Big Head Todd and the Monsters** — 99,090 annual pageviews
 111. **Brujería** — 97,683 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Brujeria (band)*, a differently-named subject
 112. **Harvey Danger** — 97,593 annual pageviews
 113. **The Voidz** — *American rock band* — 96,763 annual pageviews
 114. **Stacie Orrico** — 96,672 annual pageviews
 115. **The Beta Band** — 96,170 annual pageviews
 116. **Army of Lovers** — 94,904 annual pageviews
 117. **Infectious Grooves** — 94,765 annual pageviews
 118. **Lindisfarne** — *UK folk & progressive rock band* — 93,498 annual pageviews  
    measured article: *Lindisfarne (band)*
 119. **Jennifer Paige** — 91,264 annual pageviews
 120. **Anna von Hausswolff** — *Swedish singer-songwriter* — 89,886 annual pageviews
 121. **The Real Thing** — *British soul group formed in the 1970s* — 88,941 annual pageviews  
    measured article: *The Real Thing (British band)*
 122. **Atoms for Peace** — 88,363 annual pageviews  
    measured article: *Atoms for Peace (band)*
 123. **Asaf Avidan** — 88,315 annual pageviews
 124. **The Afghan Whigs** — 86,802 annual pageviews
 125. **White Town** — 84,688 annual pageviews
 126. **Spacemen 3** — 83,403 annual pageviews
 127. **Kool Moe Dee** — 83,282 annual pageviews
 128. **Aldo Nova** — *Canadian rock musician* — 82,599 annual pageviews
 129. **Levellers** — 78,575 annual pageviews  
    measured article: *Levellers (band)*
 130. **Quality Control** — *Hip-hop group* — 78,547 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Quality Control Music*, a differently-named subject, while the graph says *Hip-hop group*
 131. **ANOHNI and the Johnsons** — 78,097 annual pageviews
 132. **BLACKSWAN** — *South Korean girl group fka RANIA* — 77,775 annual pageviews
 133. **Altered Images** — *80s Scottish new wave / post-punk band* — 76,580 annual pageviews
 134. **Tobias Jesso Jr.** — 73,956 annual pageviews
 135. **Hyolyn** — 73,103 annual pageviews
 136. **Guano Apes** — 72,918 annual pageviews
 137. **The Angels** — *60’s girl group, best known for “My Boyfriend’s Back”* — 70,999 annual pageviews  
    measured article: *The Angels (Australian band)*
 138. **Soul Coughing** — 69,252 annual pageviews
 139. **Seven Mary Three** — 69,064 annual pageviews
 140. **Lou Barlow** — 68,904 annual pageviews
 141. **Animotion** — 67,258 annual pageviews
 142. **Shai Hulud** — *American metalcore band* — 67,128 annual pageviews
 143. **Cam** — *US country singer Camaron Ochs* — 66,952 annual pageviews  
    measured article: *Cam (singer)*; ⚠ shares this name with 2 other node(s) in the graph — the fame figure cannot tell them apart; recovered by the A15 fallback
 144. **The Wailers Band** — 65,647 annual pageviews
 145. **Fastway** — *1980s UK hard rock band* — 63,407 annual pageviews  
    measured article: *Fastway (band)*
 146. **BloodPop®** — 62,980 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *BloodPop*, a differently-named subject
 147. **The Mekons** — 62,554 annual pageviews
 148. **Man Man** — *US experimental rock band* — 62,538 annual pageviews
 149. **Everything Everything** — 62,286 annual pageviews
 150. **Cock Robin** — 61,575 annual pageviews
 151. **Colosseum** — *progressive rock band* — 61,480 annual pageviews  
    measured article: *Colosseum (band)*
 152. **London Symphony Orchestra** — 60,977 annual pageviews
 153. **Penguin Cafe Orchestra** — 60,151 annual pageviews
 154. **Calboy** — *aka 147CalBoy; American rapper, singer-songwriter* — 59,759 annual pageviews
 155. **Michel Petrucciani** — *FR | jazz* — 58,986 annual pageviews
 156. **SAINt JHN** — 58,075 annual pageviews
 157. **Never Shout Never** — 57,648 annual pageviews
 158. **Arab Strap** — *Scottish indie rock band* — 57,508 annual pageviews
 159. **Caron Wheeler** — *English singer, songwriter, and record producer* — 56,587 annual pageviews
 160. **Flobots** — 56,012 annual pageviews
 161. **Jon Foreman** — 55,233 annual pageviews
 162. **Shontelle** — 54,606 annual pageviews
 163. **Reef** — *English rock band* — 54,543 annual pageviews  
    measured article: *Reef (band)*
 164. **James Hype** — *GB | electronic* — 53,706 annual pageviews
 165. **Son Lux** — *American experimental band* — 53,670 annual pageviews
 166. **Leaders of the New School** — 52,878 annual pageviews
 167. **Lost Boyz** — *US rap group* — 51,637 annual pageviews
 168. **Brooke Candy** — *pop singer/rapper* — 51,427 annual pageviews
 169. **SECRET NUMBER** — 50,976 annual pageviews
 170. **Steve Wariner** — *American country music singer* — 48,657 annual pageviews
 171. **Blood for Blood** — 48,471 annual pageviews
 172. **Pinback** — *US indie rock band* — 48,432 annual pageviews
 173. **DAVICHI** — 47,174 annual pageviews
 174. **Roadrunner United** — 46,818 annual pageviews
 175. **Bunbury** — 46,227 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *Enrique Bunbury*, a differently-named subject
 176. **DeVotchKa** — 44,006 annual pageviews
 177. **Royal Republic** — 41,906 annual pageviews
 178. **Matt Martians** — *American producer, Odd Future member* — 41,308 annual pageviews
 179. **PRETTYMUCH** — 40,441 annual pageviews
 180. **Eisley** — 39,075 annual pageviews
 181. **Joel Adams** — *Australian pop/soul singer-songwriter and producer* — 38,078 annual pageviews  
    measured article: *Joel Adams (singer)*
 182. **Chuck Prophet** — 36,298 annual pageviews
 183. **Jade Bird** — 36,277 annual pageviews
 184. **Juliette and the Licks** — 35,069 annual pageviews
 185. **Savages** — *UK all‐female band led by Jehnny Beth* — 34,853 annual pageviews  
    measured article: *Savages (band)*; ⚠ shares this name with 1 other node(s) in the graph — the fame figure cannot tell them apart
 186. **Fucked Up** — *Canadian hardcore punk band* — 34,599 annual pageviews
 187. **Shriekback** — 34,285 annual pageviews
 188. **Michel Teló** — 32,352 annual pageviews
 189. **J.J. Johnson** — *jazz/bop trombonist/session leader* — 32,274 annual pageviews  
    ⚠ **IDENTITY UNVERIFIED** — measured *J. J. Johnson*, a differently-named subject, while the graph says *jazz/bop trombonist/session leader*
 190. **Sanctuary** — *US heavy metal band* — 32,152 annual pageviews  
    measured article: *Sanctuary (Iron Maiden song)*; recovered by the A15 fallback
 191. **Bury Your Dead** — 31,551 annual pageviews
 192. **Soilent Green** — *American extreme metal band* — 30,954 annual pageviews
 193. **Safri Duo** — *Danish electronic percussion duo* — 30,813 annual pageviews
 194. **The Sounds** — *Swedish indie rock group* — 30,784 annual pageviews
 195. **3 Inches of Blood** — 30,783 annual pageviews
 196. **Cheat Codes** — 30,573 annual pageviews  
    measured article: *Cheat Codes (DJs)*
 197. **Electric Guest** — *United States indie pop band* — 30,355 annual pageviews
 198. **Buffalo Tom** — *US alternative rock band* — 30,070 annual pageviews
 199. **R. Dean Taylor** — *Canadian singer, songwriter and record producer* — 29,710 annual pageviews
 200. **Lindsay Ell** — 29,663 annual pageviews

## What would make these lists misleading

**1. Shared names — 548 of the 12,088 low-degree nodes share their name with another node in the graph (50 of the polled ones), and the fame figure cannot tell them apart.** The proxy resolves by name, so both nodes receive the same pageview count and at most one of them is the act the article is about. Affected rows are flagged ⚠ inline. This is the same hazard class as the live clip defect `BYP-13`, where a card played a clip by a different artist of the same name.

**2. Absence is scored as obscurity, and 58 polled artists look like possible exceptions.** A11 floors an artist with no English article — the owner's adopted decision, resting on absence having predicted 'never heard of' 9/9 on the validation sample. Its accepted residual is a foreign-language or historically-notable artist, and A11's guard flags exactly that: here it fires on 58 of the 365 floored artists. **These are artists who may belong in the lists above and are absent from them entirely** — an omission, which is the harder error to notice. Full set: `flagged_unmatched.md`.

**3. A name shared with a famous act *outside* the graph inflates fame silently, and the artifact cannot detect it.** The resolver requires a musical performer, so it will not return a film or a city, but it cannot know which *band* of a given name a node means. Mitigation rather than fix: every row prints the **measured article title** whenever it differs from the artist name. This is the residual most likely to have put a wrong name high in a list.

**4. 12 nodes in these sets carry no name at all** and cannot be looked up, so they would sit at the fame floor for an artifact defect rather than for obscurity. Excluded from the lists and from the poll. The builder now rejects them (`acceptance.py`); the adopted artifact still contains them, and rebuilding is gated behind decisions this measurement does not make.

**5. 1 matched artists have fewer than 12 months of traffic** in A11's window; a month with no traffic is absent from the API and contributes zero, so their fame is understated against a full-year artist. Flagged inline.

**7. Whether the screen leaks is UNRESOLVED, because the instrument that would measure it is unreliable at this end of the graph.** The control sample's apparent leaks are dominated by misidentified rows (§'Those leak figures are WITHDRAWN'), so the estimates are not evidence of anything and are not restated here. **This does not reopen the cut**, which was deliberately not deepened (owner's call, 2026-07-26): the ranked list is instrumental, its question is answered by the correctly-identified rows, and a deeper cut measured with the same instrument would inherit the same contamination. **What it does mean is that the candidate crawl-coverage-gap reading is withdrawn rather than merely caveated** — it cannot be separated from misidentification without the disambiguation check.

**8. What is NOT a caveat, because it was caught and fixed.** Three separate mechanisms in this work would each have made an artist look *maximally obscure* and drop off the list silently: (i) concurrency provoked Wikidata throttling, and the canonical resolver's `except Exception: return []` turns a throttle into a fame-floor score — caught live by `verify_pool_equivalence.py` (`Compulsion`, 3,801 → 0 pageviews) and fixed in `transport.py`, which retries transient failures and raises rather than returning empty; (ii) a bulk-SPARQL shortcut lost 15 of 438 canonically-matched names including Guns N' Roses and Roxy Music — caught by `verify_sparql_recall.py` and **abandoned, not patched**; (iii) that same query reached *Roxy Music (album)* while missing the band entirely. No accept criterion was changed at any point; the instrument is A11 + A15 unmodified.
