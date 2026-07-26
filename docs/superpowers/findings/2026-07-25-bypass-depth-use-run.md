# 100 bypasses on one pair — what the app actually delivered, 2026-07-25

**Role: AUTHORITATIVE for its own measurements.** The owner's own use of the shipped app,
recorded. Owns every figure below; cite by section rather than restating.

**This is dogfooding, not an experiment.** One pair, one user, one sitting, no arms, no
control, nothing scored, nothing pre-registered. It is recorded because use has twice
surfaced defect classes that code review and offline metrics missed
(`../plans/2026-07-21-alpha-rollout-roadmap.md`, meta-lesson), and because this run is
currently the only evidence anywhere on how deep repeated bypassing actually goes.

**The path-quality pause is intact.** Using the shipped app and writing down what appeared
is not path-quality work and resumes nothing. No arm ran, no weight moved, no rebuild.

Identifiers are namespaced `BYP-n` — disjoint from `C`, `F`, `A`, `R`, `T3-`, `TF-`, `MKS-`
and `ASC-`.

---

## 1. Protocol as actually run, including its defects

Pair **Bob Dylan → Metallica** on the adopted artifact, shipped app, **100 bypass presses**
in one sitting. Buttons pressed as they felt natural rather than to a script: **74 "know them
already", 26 "not for me"** — counted from the final URL's exclusion parameters, all unique,
summing exactly to 100.

Outcome measure: **did a card appear whose artist the owner did not recognise** — then, for
each such artist, **Spotify monthly listeners read by hand** to separate genuinely obscure
from famous-but-not-to-him.

**Three defects in the protocol, stated because they bound every reading below:**

1. **The buttons are mixed, so the two mechanisms are confounded.** Nothing here attributes
   anything to `known` versus `dislike`. That was a deliberate instruction — a use test that
   makes the user behave unnaturally stops being a use test — but it is a cost, and the
   `dislike`-only run is what would pay it back.
2. **A first attempt was abandoned on Radiohead → Bad Bunny**, because the interior fell
   entirely outside the owner's listening knowledge and "unfamiliar" therefore measured
   nothing. This is the limit `../WHAT-GOOD-LOOKS-LIKE.md` already records — treat *no
   difference* in unfamiliar territory as uninformative. The pair was suggested by a session
   optimising for path length and was a design error.
3. **Path length was noted only where it changed sharply.** Intermediate presses moved it too;
   the table below is a set of observations, not a complete series. **A successor run should
   record length on every press** — `BYP-4` and `BYP-6` are both claims about the shape of
   that series, and a range is worth a fraction of a series.

## 2. What appeared

**`BYP-1` — seven artists the owner did not recognise, in 100 presses.** *(Plain: across a
hundred presses of the bypass buttons, seven cards showed an artist he had never heard of.)*

| press | artist | Spotify monthly listeners |
|---|---|---|
| 29 | Lykke Li | 15M |
| 35 | The Human League | 6M |
| 37 | NOFX | 1M |
| 59 | Porcupine Tree | 500k |
| 83 | Television | **372k** |
| 84 | Boards of Canada | 1M |
| 98 | Beach House | 14.8M |

Listener figures are **point-in-time, read by hand on 2026-07-25**, and will drift.

**`BYP-2` — the first one took 29 presses.** *(Plain: the app showed nothing he didn't already
know until the twenty-ninth press.)*

**`BYP-3` — nothing genuinely obscure ever appeared. The floor across all 100 presses is
372k monthly listeners.** *(Plain: it showed him seven artists he didn't know, and not one
artist that isn't well known to somebody.)* In a catalogue of ~74,000 artists the median sits
far below 372k, so the app never left the broadly-famous band at any depth reached here.

## 3. Path length, and the pattern in it

**`BYP-4` — length oscillates; it does not progress.** *(Plain: the journey sometimes gets
long and winding, then snaps back to short, over and over.)*

| press | 0 | 1–27 | 27 | 33 | 36 | 42 | 50 | 83 | 100 |
|---|---|---|---|---|---|---|---|---|---|
| cards | 3 | 3–5 | **12** | 5 | **13** | 5 | 4 | **11** | 6 |

**`BYP-5` — after 100 accumulated exclusions the output is qualitatively where it started:
6 cards, all famous, against 3 cards, all famous, at the beginning.** *(Plain: a hundred
presses later the journey looks much like the one he was given before he pressed anything.)*

This is measured against a stated requirement. `../WHAT-GOOD-LOOKS-LIKE.md` value 2 asks that
bypass **progressively** lengthen the path *and* increase novelty, both or neither. What this
run shows is oscillation around a fixed point, in both quantities.

**`BYP-6` — novelty co-occurs with the length spikes. INFERENCE, not established.** *(Plain:
the new artists tended to show up on the long winding journeys, not the short ones.)*
Three of the seven land on or within two presses of a spike: Lykke Li at 29 after the spike at
27; NOFX at 37 after the spike at 36; Television at 83, on the spike itself. Three
co-occurrences out of seven is suggestive and no more. **Falsified if novelty turns out to
appear at short lengths as often as long** — checkable in Track 2's existing walk data.

## 4. A mechanism for the collapse, and a hypothesis it raises

**`BYP-7` — why a path can get *shorter* as exclusions accumulate. INFERENCE.** Exclusions
only ever accumulate, so the option set only shrinks — yet hop count falls repeatedly. Hop
count is not monotone under exclusion: removing one artist can break a long chain of cheap
small steps, forcing a shorter route that pays larger popularity jumps instead. Total cost
rises, as it must; cards fall.

So the router appears to flip between two regimes — **many small steps with gradual fame
change**, which is the staircase actually being walked and where the discoveries came from,
and **few steps with big jumps across the famous stratum.** The descent is reachable but
**not stable**: it is a transient the router falls out of, not a state it settles into.
Consistent with the descent being paid for twice, on the way down and on the climb back.

**`BYP-8` — a candidate variance source in Track 2 and Track 2F, raised as a hypothesis and
nothing more.** *(Plain: those experiments measured the app at three fixed numbers of presses;
if what they measured swings up and down every several presses, they may have been sampling a
moving target.)* Track 2 scored its primary outcome at depths 10, 15 and 20. If length and
novelty oscillate on a period of roughly six to fifteen presses, those snapshots sample at
essentially arbitrary phase.

**This does not bias a paired arm comparison** — all arms would oscillate — but it could
inflate variance enough to bury an effect across eight pairs. **It is not offered as an
explanation of `R0`.** The check is cheap, read-only and needs no rebuild: plot path length
against depth in the walks that already exist.

## 5. What this does and does not license

**Does:** it establishes, from use, that repeated bypassing *does* eventually surface
unfamiliar artists (`BYP-1`), how long that takes (`BYP-2`), where it tops out (`BYP-3`), and
that neither length nor novelty progresses with depth (`BYP-4`, `BYP-5`).

**Does not — four ways:**

1. **It does not refute §2.9.** That finding is in **graph-popularity percentile** currency;
   this run's instrument is **Spotify monthly listeners**. Television is commercially small
   and plausibly co-listened heavily among rock listeners, so it could sit high in the graph's
   popularity while reading as a discovery. Both can hold. Reading one as the other is the
   error the Phase 1 log warns about in §2.6, §2.11 and §2.12.
2. **One pair, one listener, one sitting.** Bob Dylan → Metallica is a famous-to-famous
   cross-genre pair, which is the hard case by design — it is not a sample.
3. **The buttons are confounded** (§1), so nothing here says which mechanism delivered what.
4. **It proposes no change.** No arm, no weight, no rebuild, no threshold.

## 6. Method note — the second-opinion instrument, and that it changed the read

`../WHAT-GOOD-LOOKS-LIKE.md` licenses hand-read Spotify monthly listeners for exactly this
question, under three bounds. All three are met: **this was not a blind listen** (no arms, no
selection), **no scored criterion used it**, and the third bound — *write down any check that
changed your mind* — is discharged here:

> **Two of the seven would have been logged as discoveries without it.** Lykke Li (15M) and
> Beach House (14.8M) are famous artists outside this listener's geography, not obscure ones.
> The naive measure "did I recognise the name" produced **five of seven** readings that the
> second opinion revised downward in significance.

That is the instrument earning its place on first use, and it is the reason `BYP-3` can be
stated at all.

## 7. Reproducible states

These URLs encode the **full exclusion set** and therefore reproduce the exact path on the
adopted artifact. The host is a local dev server; the path and query are the durable part.

**The exclusion counts corroborate the press labels exactly** — 25+2 = 27, 30+3 = 33,
44+6 = 50, 74+26 = 100, with no duplicates in any list. That is why the press numbers in
`BYP-1` and `BYP-4` can be trusted rather than treated as recollection.

**Press 27 — 12 cards** (25 `known`, 2 `dislike`). The first large length spike.

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58
```

**Press 33 — 5 cards** (30 `known`, 3 `dislike`). Six presses after the spike, collapsed.

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2Cf467181e-d5e0-4285-b47e-e853dcc89ee7%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2C7e5a2a59-6d9f-4a17-b7c2-e1eedb7bd222%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2Ccd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C8dc08b1f-e393-4f85-a5dd-300f7693a8b8
```

**Press 50 — 4 cards** (44 `known`, 6 `dislike`).

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2Cf467181e-d5e0-4285-b47e-e853dcc89ee7%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2C7e5a2a59-6d9f-4a17-b7c2-e1eedb7bd222%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2Ccd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8%2C94b0fb9d-a066-4823-b2ec-af1d324bcfcf%2C9e53f84d-ef44-4c16-9677-5fd4d78cbd7d%2C4b585938-f271-45e2-b19a-91c634b5e396%2C331ce348-1b08-40b9-8ed7-0763b92bd003%2C52074ba6-e495-4ef3-9bb4-0703888a9f68%2C84eac621-1c5a-49a1-9500-555099c6e184%2C34cf95c7-4be9-4efd-a48a-c2ea4a0bb114%2C05517043-ff78-4988-9c22-88c68588ebb9%2C109958eb-a335-4c5e-907e-597ff4c6af46%2C5cbef01b-cc35-4f52-af7b-d0df0c4f61b9%2C39c2a93d-9afa-4a22-9bba-c087ab056e1c%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2C64b94289-9474-4d43-8c93-918ccc1920d1%2Caab5c954-cabe-432e-899e-1c4f99757327&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C8dc08b1f-e393-4f85-a5dd-300f7693a8b8%2C611700cf-27f0-4dc9-ae80-c513a767853e%2Cdcaa4f81-bfb7-44eb-8594-4e74f004b6e4%2C2eada8f8-056a-4093-bbc2-004909ce743b
```

**Press 100 — 6 cards, all famous** (74 `known`, 26 `dislike`). **This is the state that
matters most**: it is the direct evidence for `BYP-5`, and reloading it confirms that a
hundred presses ends qualitatively where it began.

```
http://localhost:5173/path/72c536dc-7137-4477-a521-567eeb840fa8/65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab?known=678d88b2-87b0-403b-b63d-5da7465aecc3%2C9efff43b-3b29-4082-824e-bc82f646f93d%2C9fdaa16b-a6c4-4831-b87c-bc9ca8ce7eaa%2C69ee3720-a7cb-4402-b48d-a02c366f2bcf%2C8f92558c-2baa-4758-8c38-615519e9deda%2C5441c29d-3602-4898-b1a1-b77fa23b8e50%2C66c662b6-6e2f-4930-8610-912e24c63ed1%2Ca3cb23fc-acd3-4ce0-8f36-1e5aa6a18432%2Cbd13909f-1c29-4c27-a874-d4aaf27c5b1a%2C83d91898-7763-47d7-b03b-b92132375c47%2Cc3aeb863-7b26-4388-94e8-5a240f2be21b%2C309c62ba-7a22-4277-9f67-4a162526d18a%2Cb071f9fa-14b0-4217-8e97-eb41da73f598%2Cd43d12a1-2dc9-4257-a2fd-0a3bb1081b86%2C3d2b98e5-556f-4451-a3ff-c50ea18d57cb%2Cb10bbbfc-cf9e-42e0-be17-e2c3e1d2600d%2Cf46bd570-5768-462e-b84c-c7c993bbf47e%2C0383dadf-2a4e-4d10-a46a-e9e041da8eb3%2C618b6900-0618-4f1e-b835-bccb17f84294%2C70248960-cb53-4ea4-943a-edb18f7d336f%2C614e3804-7d34-41ba-857f-811bad7c2b7a%2C5d02f264-e225-41ff-83f7-d9b1f0b1874a%2Ca41ac10f-0a56-4672-9161-b83f9b223559%2Cb83bc61f-8451-4a5d-8b8e-7e9ed295e822%2Cebfc1398-8d96-47e3-82c3-f782abcdb13d%2Cf467181e-d5e0-4285-b47e-e853dcc89ee7%2Ce5c7b94f-e264-473c-bb0f-37c85d4d5c70%2C7e5a2a59-6d9f-4a17-b7c2-e1eedb7bd222%2Ca506f761-2c22-4b2f-8a94-bd748c2c8f75%2Ccd8c5019-5d75-4d5c-bc28-e1e26a7dd5c8%2C94b0fb9d-a066-4823-b2ec-af1d324bcfcf%2C9e53f84d-ef44-4c16-9677-5fd4d78cbd7d%2C4b585938-f271-45e2-b19a-91c634b5e396%2C331ce348-1b08-40b9-8ed7-0763b92bd003%2C52074ba6-e495-4ef3-9bb4-0703888a9f68%2C84eac621-1c5a-49a1-9500-555099c6e184%2C34cf95c7-4be9-4efd-a48a-c2ea4a0bb114%2C05517043-ff78-4988-9c22-88c68588ebb9%2C109958eb-a335-4c5e-907e-597ff4c6af46%2C5cbef01b-cc35-4f52-af7b-d0df0c4f61b9%2C39c2a93d-9afa-4a22-9bba-c087ab056e1c%2Cabd506e1-6f2b-4d6f-b937-92c267f6f88b%2C64b94289-9474-4d43-8c93-918ccc1920d1%2Caab5c954-cabe-432e-899e-1c4f99757327%2C06fb1c8b-566e-4cb2-985b-b467c90781d4%2C04cd0cfd-bfd1-4c36-bc38-95c35e2c045f%2C160629ab-ec18-4931-8c95-02cb92d06186%2C2819834e-4e08-47b0-a2c4-b7672318e8f0%2C092b603f-eb4c-4958-b10e-02420de5885b%2Cf37b3f31-b1f8-4b88-8cb5-b34f709b17d7%2Ca94a7155-c79d-4409-9fcf-220cb0e4dc3a%2C72359492-22be-4ed9-aaa0-efa434fb2b01%2C0c502791-4ee9-4c5f-9696-0602b721ff3b%2Cf93dbc64-6f08-4033-bcc7-8a0bb4689849%2C9a58fda3-f4ed-4080-a3a5-f457aac9fcdd%2Cfa97dd36-1b82-43d7-a6e4-2adeafd59cef%2C9e0e2b01-41db-4008-bd8b-988977d6019a%2Cdebabff3-2559-46e5-862d-ef2a906d7010%2C78f797e3-4913-4026-aad0-1cd858bd735b%2Cf27ec8db-af05-4f36-916e-3d57f91ecf5e%2C03ad1736-b7c9-412a-b442-82536d63a5c4%2Cd8e41375-bd8d-4e39-9da7-f0c171e97086%2Cc3f28da8-662d-4f09-bdc7-3084bf685930%2C33b3c323-77c2-417c-a5b4-af7e6a111cc9%2C1f43d76f-8edf-44f6-aaf1-b65f05ad9402%2C01d3c51b-9b98-418a-8d8e-37f6fab59d8c%2Cb6b2bb8d-54a9-491f-9607-7b546023b433%2Ce01c3376-15fa-40d7-b747-5f219bdefdd7%2C59a7fbcb-ff74-494d-abd0-9c82359040c9%2C7808accb-6395-4b25-858c-678bbb73896b%2C6a726ac6-019e-455c-8bbb-571a77bed52e%2C17b53d9f-5c63-4a09-a593-dde4608e0db9%2C664c3e0e-42d8-48c1-b209-1efca19c0325%2C0af78501-5647-4c18-9a0d-66ac8789e13b&dislike=5182c1d9-c7d2-4dad-afa0-ccfeada921a8%2Cea4dfa26-f633-4da6-a52a-f49ea4897b58%2C8dc08b1f-e393-4f85-a5dd-300f7693a8b8%2C611700cf-27f0-4dc9-ae80-c513a767853e%2Cdcaa4f81-bfb7-44eb-8594-4e74f004b6e4%2C2eada8f8-056a-4093-bbc2-004909ce743b%2Cc0b2500e-0cef-4130-869d-732b23ed9df5%2Cbdc70372-7e8a-4cb9-8d33-f036b3b7cdc1%2C169c4c28-858e-497b-81a4-8bc15e0026ea%2Cece57992-dc2e-4f67-a269-fa43626c1a3d%2C22dc19af-d085-4c9b-adfb-22ec256251f1%2C2f9ecbed-27be-40e6-abca-6de49d50299e%2C2fddb92d-24b2-46a5-bf28-3aed46f4684c%2C3414d446-735a-443c-931f-10634f57e5b9%2Cd2ff6b6b-fc30-48dc-8952-06f9d8fc64f8%2C149e6720-4e4a-41a4-afca-6d29083fc091%2C01809552-4f87-45b0-afff-2c6f0730a3be%2Cd8661c02-f423-4d72-8044-40ff05daf7a1%2C69158f97-4c07-4c4e-baf8-4e4ab1ed666e%2C5dfdca28-9ddc-4853-933c-8bc97d87beec%2C985c709c-7771-4de3-9024-7bda29ebe3f9%2C494e8d09-f85b-4543-892f-a5096aed1cd4%2Ccc2c9c3c-b7bc-4b8b-84d8-4fbd8779e493%2C7bd9e20e-74b9-446a-a2ed-a223f82a36e7%2Cd5cc67b8-1cc4-453b-96e8-44487acdebea%2C77c167d2-4965-4421-830a-9815e4956475
```

The two endpoint MBIDs are `72c536dc-…` (Bob Dylan) and `65f4f0c5-…` (Metallica).

## 8. What this run makes worth doing next

Named, **not scheduled** — the trigger is the owner's:

- **The same pair, `dislike` only.** Pays back §1's confound. The record's expectation is that
  the button *designed* to carry obscurity (`known`) is the weaker of the two, because the
  floor device is never pivotal while the avoidance term is live. Stated before that run,
  so it cannot be fitted afterwards.
- **The length-oscillation check** against Track 2's committed walk data (`BYP-8`). Read-only.

**`BYP-9` — early signal from the start of that run. It points *against* the prediction
directly above it, and it is a named defect shape on the mechanism least expected to show
one.** *(Plain: pressing only "not for me" kept the journey at three cards — start, one artist
in the middle, end — for nine presses running.)*

Nine consecutive `dislike` presses held the path at **3 cards**; the first move to 4 came at
press 10. The run was then abandoned and restarted on a newer build, so this is ten presses,
one pair, and preliminary.

**Why it is more than a length observation.** A 3-card path has exactly **one** interior card,
and bypass is hidden on the endpoints — so the user has exactly one thing to press, and the
app's answer is necessarily **one artist substituted for another**. Nine 3-card paths in a row
is therefore **nine consecutive 1:1 swaps**. Against `../WHAT-GOOD-LOOKS-LIKE.md`:

- **value 6** states `dislike` should 1:1-swap **much less often** than `known`. Here it swapped
  1:1 on every press for nine presses.
- **value 7** names **sustained confinement** — several bypasses in a row keeping the change in
  the same small region — as the defect form, explicitly distinguishing it from single local
  deviations, which are expected and fine. Nine in a row is the defect form.

**A session challenged this as a possible artifact of finer logging** — run 1's early phase was
recorded as a range, not a series (§1 defect 3), so it is not known when run 1 first reached 4
cards. **The challenge is answered by run 1's own notation:** presses 1–27 were recorded as
**"3–5"**, which is a statement of variation. A window containing nine consecutive 3s would not
have been written that way. The owner also states directly that a run of that many 3-card paths
would have been salient enough to report at the time.

**Mechanism, labelled inference:** `dislike` penalises a *neighbourhood* that decays over
several hops, so a long wandering route pays that penalty repeatedly while a short one clears it
in a hop or two. If that is what is happening, `dislike` **suppresses** length — and combined
with `BYP-6` it would be the **weaker** novelty mechanism, not the stronger. That is the
opposite of this section's prediction, which is why the prediction was written down first.
