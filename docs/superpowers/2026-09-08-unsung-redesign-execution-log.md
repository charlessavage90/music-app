# `UXR-` execution log — the Unsung.fm redesign

**Role: RETAINED EXECUTION LOG for `UXR-T1`–`UXR-T11`. ACTIVE. Owns no figures and no status**
(`NEXT.md` owns status). Appended per task: decisions and reasoning, never narration.
Plan: `plans/2026-09-08-unsung-redesign.md`. Spec: `specs/2026-09-08-unsung-redesign-scope.md`.

Executed inline by the session that wrote the plan (owner's "go", 2026-09-08), warm on every
file it touches; the plan's two handoff seams (after `T5`, after `T8`) are where a fresh
session takes over.

## §1 `UXR-T1` — tokens and faces

- `@fontsource-variable/space-grotesk@5.3.0` installed; both faces self-hosted (`UXR-D11`).
- The `@theme` block replaced wholesale with the role-named palette, plus ten aliases for
  the pre-redesign names (`UXR-D17`). The mechanical check — every `var(--color-*)` referenced
  under `src/` resolves to a definition in `index.css` — printed nothing undefined.
- Two keyframes added (`un-eq`, `un-sheen`) and a `.motion-safe-only` opt-out under
  `prefers-reduced-motion`, so the equaliser and the CTA sheen stop for people who asked them to.
- No behaviour changed; the suite is the check that nothing but colour moved.

## §2 `UXR-T2` — the name

- `Brand` is one accessible object (`role="img"`, `aria-label="Unsung.fm"`) wrapping a
  decorative `<img alt="">` and an `aria-hidden` split wordmark. **The plan's second
  assertion contradicted its own component** (it queried role `img` by name while the
  component carries exactly that role and name); corrected to assert the inner `<img>` is
  decorative and that only one `img` role exists. The plan's intent, not its letter.
- Title, no-JS fallback and favicon link renamed; `public/favicon.svg` (the Vite template's
  bolt) removed. A grep for "Artist Path" under `src/`, `index.html`, `e2e/` is empty; the
  `artistpath:` localStorage key and the package names are identifiers, not the product name.
- **The mark file `frontend/public/unsung-mark.png` did not exist at commit time** — it is
  the owner's export. Every test passes without it; the page shows a broken image until it
  lands.
