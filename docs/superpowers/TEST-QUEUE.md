# Use-the-app test queue

**Role: ACTIVE, permanent. A CHECKLIST AND NOTHING ELSE.** The app is at [**https://unsung.fm**](https://unsung.fm).

**How to use it.** Run down the boxes in order, on the device each one names. Report back in one
message: the numbers that failed, what you saw, and a URL for anything broken. Anything you did
not get to is simply still unticked. **A session discharges the items you report and moves them to
[`archive/TEST-QUEUE-discharged.md`](archive/TEST-QUEUE-discharged.md)**, so what is left here is
always what is still to press.

**An empty file is a valid and normal state.** An entry is written only when there is something
you can actually press. Silence never means a session forgot.

**Two rules govern what may be added** — both the owner's, and a session that breaks either has
written the wrong thing:

1. **Only a change he can exercise.** Not "here is what I did this session". That belongs in the
 closeout report and the PR body, which he reads at the time.
2. **Only things that can be found *wrong*** — a defect, a regression, something that does not
 work. **Never "tell me how it feels."** His continuous judgement of the app has no completion
 state, so an entry for it could never be discharged. Where a session genuinely needs his taste,
 that is a designed evaluation with its own pre-registration, not a queue entry.

> **Budget: 70 lines** — a new check past it must displace something. That is the
> pressure working. It reached **255 on 2026-09-12** because sessions appended reasoning instead of
> checks; reasoning belongs in the archive, the PR body or the execution log. Checked at `closeout`
> **B6-budget**. **Never compress a live check to fit** — discharge one, or raise the budget and
> say why.

---

## QUEUED 2026-09-24 — the player sweep (#221–#223)

**Where:** on unsung.fm, after the next deploy.

- [ ] 1. **Clip playing, desktop or phone.** Press the keyboard's / headset's / lock screen's **next
  track**: the next card with a clip starts. **Previous track** goes back one. On the last card, next
  does nothing — the clip keeps playing.

## QUEUED 2026-09-25 — the new map (`LBA-A6`), after the deploy that ships it

**Where:** on unsung.fm, after the next deploy.

- [ ] 2. **Landing page, any device.** The Bad Bunny → Chappell Roan example says **3 stops**. If it
  says 8, the site is still on the old map. Press it: the journey has exactly one artist between.
- [ ] 3. **Start a journey, any device.** Type `Miles Davis` in the first box. The **first**
  suggestion is Miles Davis the trumpeter, not Miles Davis Quintet.
