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
