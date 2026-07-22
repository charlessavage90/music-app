# HANDOFF — run the `d025` vs `capfix` blind listening test

**Role: ACTIVE.** Written 2026-07-22 for a session with **zero prior context**. Delete this
file once the verdict is recorded and Task 16 is done.

You do not need to understand Phase 2 to execute this. You need to serve two files on two
ports, hand the owner two URLs, and record what he says. **Read §5 before you speak to him
— the framing matters more than the mechanics.**

---

## 1. What you are doing

Two graph artifacts are built and verified. The owner will use both in the running app,
blind, and say which is better. That verdict decides which one the project adopts.

**You must not tell him which is which, and must not summarise any metric, hypothesis or
expectation.** He gets two bare URLs. Everything else biases the one measurement this test
exists to take.

The pre-registered readings — what each possible verdict means and what to do about it —
are committed at **`docs/superpowers/2026-07-21-phase2-execution-log.md` §15**. Read it.
**That committed version governs. Do not restate or reinterpret it here or anywhere else.**

---

## 2. The two artifacts

Artifacts are gitignored, so the checksum is their only identity. **Verify both before
serving** — a wrong file silently invalidates the test.

| Arm | Path | sha256 |
|---|---|---|
| **`d025`** | `builder/scratch/graph-t15-d025.bin` | `2811e87d1c900e4ec233317c05143ccaec5a3f0e1fb3c531c04455594bb27e65` |
| **`capfix`** | `builder/scratch/graph-t15-capfix.bin` | `c8af6eaccc08de0a85db7f12b2fed101dc3acc720eda1781a6f3a945f50cf237` |

Verified against their manifest sidecars on 2026-07-22. Each has a `<file>.json` manifest
recording config, git commit (`f7583b8`), elapsed time and sha256.

```bash
cd builder/scratch
sha256sum graph-t15-d025.bin graph-t15-capfix.bin
python -c "import json;print(json.load(open('graph-t15-d025.bin.json'))['sha256'])"
python -c "import json;print(json.load(open('graph-t15-capfix.bin.json'))['sha256'])"
```

If either file is missing, rebuild it — do not substitute another artifact. The build
recipe and configs are in `findings/2026-07-22-phase2-sweep-results.md` §1 and §9; a warm
build takes about 30 seconds.

---

## 3. Serve recipe

This is the recipe used successfully in Task 0 (execution log §12), with the gaps that
entry leaves filled in.

**First, randomise and record the mapping — before serving anything.**

```bash
cd "<repo root>"
python -c "
import random, json, pathlib
arms = ['d025', 'capfix']; random.shuffle(arms)
pathlib.Path('.superpowers/BLIND-MAPPING.json').write_text(
    json.dumps({'8000': arms[0], '8001': arms[1]}, indent=2), encoding='utf-8')
print('mapping written')
"
```

`.superpowers/` is gitignored, so the mapping stays local. **Do not print it.**

**Two API processes**, each reading the mapping itself so you never echo it:

```bash
cd api
ART=$(python -c "import json,pathlib;print(json.loads(pathlib.Path('../.superpowers/BLIND-MAPPING.json').read_text())['8000'])")
ARTISTPATH_GRAPH="../builder/scratch/graph-t15-$ART.bin" PYTHONIOENCODING=utf-8 UV_LINK_MODE=copy \
  uv run uvicorn artistpath_api.app:build_default_app --factory --port 8000
```

Repeat for port `8001` with the `['8001']` key. Run each in the background.

**Two frontends**, pointed at those APIs via `VITE_API_PROXY` (read by `vite.config.ts`):

```bash
cd frontend
VITE_API_PROXY=http://localhost:8000 npm run dev -- --port 5175 --strictPort
VITE_API_PROXY=http://localhost:8001 npm run dev -- --port 5174 --strictPort
```

**Gotchas, all hit in Task 0:**

- **Port 5173 may already be occupied** by a stale dev server. Use 5174/5175 as above.
- **Do not start these with a `while read` loop** — it consumes stdin and the servers die
  silently with no log.
- **Python buffers stdout when redirected here.** For any long-running command use
  `python -u` or `PYTHONUNBUFFERED=1` and poll the log, or it looks dead while running fine.
- Prefix **every** `uv` command with `UV_LINK_MODE=copy` — the repo is on OneDrive and
  hardlinking fails without it.

**Verify both stacks serve *different* artifacts before handing over.** If the proxy wiring
is wrong you would be comparing one artifact against itself:

```bash
MB=$(curl -s "http://localhost:8000/api/artists/search?q=miles%20davis" | python -c "import sys,json;print(json.load(sys.stdin)[0]['mbid'])")
DP=$(curl -s "http://localhost:8000/api/artists/search?q=daft%20punk"  | python -c "import sys,json;print(json.load(sys.stdin)[0]['mbid'])")
for p in 5174 5175; do
  curl -s -X POST "http://localhost:$p/api/path" -H "Content-Type: application/json" \
    -d "{\"sources\":[\"$MB\",\"$DP\"]}" | python -c "
import sys,json; a=json.load(sys.stdin)['artists']
print(len(a), ' -> '.join(x['name'] for x in a))"
done
```

The two must differ. **Do not show the owner these paths** — their character is a hint.

---

## 4. Health check

```
GET  http://localhost:800X/api/artists/search?q=<query>   -> 200
POST http://localhost:800X/api/path  {"sources": ["<mbid>", "<mbid>"]}
```

Both frontends should return 200 on `/`.

---

## 5. What you say to the owner

Give him **exactly** the two URLs and the question. No metric summary, no hypothesis, no
"one of these fixes X", no hint of which is which, no framing.

Say this much and no more:

> Two instances, blind: http://localhost:5175 and http://localhost:5174.
> Which, if either, produces better paths?
> "No detectable difference" is a valid answer.
> Judge the artist sequences, not the clips — the clip bugs are live in both and unrelated.

**Known limitation, tell him up front:** the arms differ in edge structure, so a determined
search could distinguish them. This is acceptable and is recorded in advance. If he notices
mid-session, record it as a note; it does not invalidate the judgement.

**Run once.** If the result is disliked it stands. A second listening test is forbidden.

---

## 6. After the verdict

1. **Unblind** — read `.superpowers/BLIND-MAPPING.json`.
2. **Record in the execution log** as a new section: the mapping, the owner's verdict
   **verbatim**, both sha256s, and the date.
3. **Apply the pre-registered reading** from execution log §15. Do not reinterpret it. If
   the reading adopts `d025`, §15 requires you to show the working — that criterion 6 failed
   on a channel independently shown to be unstable — not to bury it.
4. **Task 16 — adopt.** Set the winning config as the default in
   `builder/src/artistpath_builder/config.py`; regenerate the 5k dev fixture and the
   committed 500-node test fixture from the adopted graph; run all three suites; update the
   docs. **C-4: the losing option must be *deleted* from each config knob and raise on use,
   not left as a supported mode.** Full steps: `plans/2026-07-21-phase2-path-quality.md`
   Task 16.
5. **Run the `closeout` skill.** Mechanical post-execution hygiene, about half an hour.
6. **Delete this file.**

---

## 7. Everything else you need is committed

Nothing material is held only in the authoring session's context. Specifically:

| What | Where |
|---|---|
| Every measured figure from the six-arm sweep | `findings/2026-07-22-phase2-sweep-results.md` |
| What those figures mean for future work (claims 41–45) | `findings/2026-07-21-scoring-adjudication.md` §6 |
| The pre-registered readings for this test | execution log §15 |
| How `capfix` won its own blind test, and the serve setup | execution log §12 |
| Decisions, plan defects, gates, open items, environment traps | execution log §§1–14 |
| The governing plan and its amendments | `plans/2026-07-22-phase2-revised-plan.md` |
| Which documents to trust | `docs/README.md` |

**Read `docs/README.md` first if you are new to the repo.** All scoring figures live in one
document by rule; everything else cites it by section.
