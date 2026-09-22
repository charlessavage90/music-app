# Handoff — `LBA-AM5` (listen before the use gate) and `LBA-AM6` (the listen, designed cold), 2026-09-22

**Role: ACTIVE — this is the CURRENT handoff.** Nothing supersedes it. Supersedes
[`2026-09-21-HANDOFF-lbd-s4-a6-candidate.md`](2026-09-21-HANDOFF-lbd-s4-a6-candidate.md) on next
actions. It does **not** state project status: for that read [`NEXT.md`](NEXT.md), which owns it.

**A seam.** Both amendments are committed on `lbd-s4-listen-amendments` (PR #132, stacked on
#131). Nothing is in flight: no background job, no subagent, no dev server, no half-written
directory. **It owns no figures**, and neither amendment adds one.

## What happened

1. **`LBA-AM5`** — §8's last two stages swapped. **The blind listen runs first and `LBA-G5`, the
   use gate, second.** The defect: the gate had its only listener using the candidate knowingly
   immediately before a run-once blind listen. The reasoning is an asymmetry, recorded in the
   amendment. It adds the owner's **pair log** during the gate and leaves his two-day period as it
   was. `LBA-AM4`'s text is not edited.
2. **`LBA-AM6`** — the `REQ-38` listen, written cold: the served map against the candidate. It fixes
   the draw, the gates, the depths, the questions, the reads including the tie, and the run-once
   rule. It is modelled on `LBD-AM5-5`/`LBD-AM6` and takes every instrument fix from listen 2's §4.
   The new series is **`LAL-`**.

## ⚠ Easy to get backwards

- **This session generated, viewed and was told no journey on either map.** It opened no page-data,
  verdict, result or pre-screen file, and not the candidate. So it holds no knowledge that would
  disqualify it from the listen. But it **designed** the listen, and the `GBL-` §6 precedent keeps
  the designing session off running it and off the write-up anyway.
- **The listen's sessions do generate journeys**: the pre-screen (preparation session) and the
  generation step (runner). That is by design, and it is why three fresh sessions exist. **None of
  them is this one.**
- **`LAL-Q4`, the "can you tell which side is the new map" field, never enters the read.** Nor do
  strength, `LAL-K` or the sealed metrics. The unblind script must be tested for invariance to all
  three.
- **`LBA-AM5`'s first box corrects `LBA-AM4`'s "no journey on any `LBA-` map by anyone" to what the
  record supports.** Stage 2's timing script ran `find_journey` on the fame-free `LBA-A6` arm for
  wall-clock time only. Do not "restore" the broader wording.
- **Ids for the listen are a function of the artist, not the side** (`LBA-AM6-6`). Generation
  refuses if the two artifacts record different Deezer ids for one MBID. That refusal is a check,
  not a formality.

## What I know that is not in the durable record

**One thing, and it is now recorded:** the owner's original instruction said to branch off
`origin/main`. #131 was unmerged, so `main` had no `LBA-AM4`. Asked, he let me choose. I stacked on
#131's branch because merging #131 alone would have put a `NEXT.md` naming "run `LBA-G5`" on `main`.

## Owed, and by whom

**The owner:** run the queued use-the-app tests; merge #131, then #132. After that, `NEXT.md`'s
sequence applies: preparation session → runner session → the listen → write-up session → `LBA-G5`
→ adoption.

**The next session is the PREPARATION session** (`LBA-AM6-2`, `-11`). Its first act is to commit
the pre-screen script with `LBA-AM6-2`'s rule in its docstring **before running it**.
