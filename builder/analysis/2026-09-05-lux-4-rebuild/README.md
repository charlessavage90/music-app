# `LUX-4` rebuild — verification and `LUX-E5`, 2026-09-06

**Role: FIGURES OWNER for the `LUX-4` artifact's identity and for `LUX-E5`. ACTIVE.**
**Cited elsewhere, never restated.** Produced by `L4-T7` of
[`plans/2026-09-05-lux-4-links-and-info-card.md`](../../../docs/superpowers/plans/2026-09-05-lux-4-links-and-info-card.md).

**Result: the rebuild is the served graph plus exactly three metadata keys, and `LUX-E5`
passes with roughly 8× headroom.** Nothing is dropped.

## 1. The factor table

The claim under test is *"same graph, plus three metadata keys."* The sha **must** differ —
keys were added — so a sha comparison cannot be the check.

| Arm | LUX-4 maps | archive | drop list | expected | result |
|---|---|---|---|---|---|
| **Control** | **patched to empty** | pre-CEX snapshot | `…algb_20260805.json` | sha == `43dd82bb…` | ✅ **byte-identical** |
| **Shipping** | populated | pre-CEX snapshot | `…algb_20260805.json` | sha differs; everything else identical | ✅ **verified, 16 checks** |

**Held constant, and why the intervention cannot change it:** the archive and drop list are
pinned per invocation (both are the drifted inputs `LUX-E1` identified); `--algorithm`,
`--cap-strategy` and `--require-fame` are passed explicitly. The intervention adds metadata
only — it touches no edge, no score and no node, and the writes happen after the graph is
built. **The control arm is what proves that rather than assuming it.**

⚠ **The plan's control arm could not be used and was replaced.** `L4-T7` step 1 said to reuse
`../2026-09-05-lux-e1-armb/armb_sha.py` and expect byte-identical. That became impossible at
`L4-T5`: it calls `build_from_archive`, which now wires the LUX-4 maps unconditionally, so it
can never reproduce `43dd82bb` again. The plan's table names an arm with *"maps not wired"*,
and once they are wired no such arm exists — there is deliberately no config knob.
`control_empty_maps.py` restores a real control by patching the two loaders, which is the only
remaining way to build pre-LUX-4 output from post-LUX-4 code.

## 2. Identity

| | artifact | bytes | sha256 |
|---|---|---|---|
| served | `graph-msw-tu50.bin` | 17,773,958 | `43dd82bb3771691ed778c1f2a3a079cdad0bd75636b2bedb1c754c8a2be79cc8` |
| **LUX-4** | `graph-lux4.bin` | **23,753,986** | `fd92a7352afb7321…` *(full value in the manifest sidecar)* |

Both builds: **58,838 artists, 1,315,684 edges**. ⚠ **Take the deploy checksum from the
manifest sidecar, never from this table** (`DEP-24`).

## 3. What `verify.py` checks, and why subtraction is the strong one

Two independent checks, both green:

- **Structural** — every deserialised field compared to the served artifact: counts, mbids,
  names, disambiguations, `pop_raw`, `deezer_ids`, `fame_lb_raw`, offsets, neighbours, scores,
  edge types; then the metadata key sets differenced.
- **Subtraction** — strip the three new keys from the new artifact's metadata, re-serialise
  with `artifact.serialise`'s exact json parameters, rebuild the payload, and require it to be
  **byte-identical to the served artifact, sha included.** It is. Where the structural check
  compares *values*, this compares *bytes*, so it also catches a change in JSON key ordering,
  separator choice or unicode escaping — none of which alters a single Python value, and all of
  which would silently break the claim.

**One check went red on the first run and the bug was in the check.** A whole-prefix byte
comparison failed while the subtraction passed — the header's uint64 metadata-length field
legitimately differs, because the new blob is bigger. Two checks of the same claim disagreeing
is what exposed it; a single check would have been believed. The comparison now excludes the
header and asserts the header's other fields separately.

## 4. `LUX-E5` — does it still fit in the memory the service has?

**Plain sentence, fixed in the spec before any result existed:** *does the extra artist
information still fit in the memory the running service actually has?*

**Threshold:** must fit within the deployed container's configured memory with headroom for
the existing working set. Production is **AWS App Runner, 1 vCPU / 2 GB**
(`infra/src/artistpath_infra/stack.py`). If it did not fit, fields would be dropped starting
with tags — already deferred — so the first droppable thing would be `artist_facts`' `area`.

**Measured on this workstation, not in the container.** Treat the absolute numbers as
indicative of the platform and **the delta as the measurement**.

| | served | LUX-4 | delta |
|---|---|---|---|
| artifact on disk | 16.95 MiB | 22.65 MiB | +5.70 |
| metadata blob | 5.4 MiB | 11.1 MiB | +5.7 |
| boot time (`GraphStore.load`) | 0.19 s | 0.40 s | +0.21 |
| RSS after load | 87.9 MiB | 100.0 MiB | +12.1 |
| **RSS holding the three lists** (what `L4-T8` will do) | 92.3 MiB | **158.7 MiB** | **+66.4** |
| peak working set during boot | 127.4 MiB | **261.5 MiB** | +134.1 |
| Python heap (`tracemalloc`, current) | 27.7 MiB | 55.5 MiB | +27.8 |

**Read: `LUX-E5` PASSES with room to spare.** Peak boot is **261 MiB against 2048 MiB — 12.8%**;
steady state is 159 MiB, **7.8%**. Boot time of 0.4 s sits far inside App Runner's health check
(10 s interval, 5 s timeout). Nothing is dropped, and `area` stays.

⚠ **`GraphStore` does not retain these keys until `L4-T8`** — today it parses and discards
them. The "holding the three lists" row simulates exactly what `T8` will keep, because
measuring only the load would have understated the running cost by a factor of five.

**RSS and `tracemalloc` disagree (66.4 vs 27.8 MiB) and both are reported deliberately.**
`tracemalloc` counts Python allocations exactly; RSS also carries allocator retention and the
transient full-file read that `gc.collect()` does not return to the OS. The served-artifact row
shows that transient alone costing 4.5 MB with *nothing* retained. **Compare the RSS figure
against the container limit** — it is the conservative one and it is what the limit measures.

**The finding worth carrying forward: 5.70 MiB of JSON costs ~66 MiB of RSS, roughly 10×.**
That is Python object overhead — 58,838 dicts and their repeated key strings. It is affordable
here and it is the number that should govern `LUX-E6`: a genre-tag list per artist would
multiply the same way, against a 2 GB ceiling. The shape trade-off is recorded at the contract
point in `artifact.py`'s module docstring.

## 5. Reproduce

```bash
cd builder
# control (~10 min): post-LUX-4 code, maps off, must return 43dd82bb
UV_LINK_MODE=copy PYTHONUNBUFFERED=1 uv run python -u \
  analysis/2026-09-05-lux-4-rebuild/control_empty_maps.py
# shipping build (~10 min)
UV_LINK_MODE=copy PYTHONUNBUFFERED=1 PYTHONIOENCODING=utf-8 uv run artistpath-build build \
  --archive-dir scratch/grt-archive-algb.pre-cex-snapshot \
  --algorithm "session_based_days_7500_session_300_contribution_3_threshold_10_limit_100_filter_True_skip_30" \
  --cap-strategy trimmed_union --require-fame \
  --unlistenable-list src/artistpath_builder/data/unlistenable_drop_algb_20260805.json \
  --out scratch/graph-lux4.bin
UV_LINK_MODE=copy uv run python analysis/2026-09-05-lux-4-rebuild/verify.py
cd ../api   # LUX-E5 needs the api's venv, not the builder's
UV_LINK_MODE=copy uv run python ../builder/analysis/2026-09-05-lux-4-rebuild/boot_cost.py \
  ../builder/scratch/graph-lux4.bin
```

**Build cost measured here: 616 s.** Neither the "~40 s" nor the older "~23 min" figure is
usable for planning; both this and the 2026-09-05 rebuild (297 s) exceed the manifest-derived
40 s by an order of magnitude, plausibly filesystem-cache state over an archive of tens of
thousands of small files. **Budget ten minutes.**

⚠ `builder/scratch/` is gitignored, so neither artifact is in the repo. Identity is by the
shas above and by each artifact's manifest sidecar.
