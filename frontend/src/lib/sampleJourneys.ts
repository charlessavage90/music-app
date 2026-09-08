// The landing page's measured journeys. In their own module because a
// component file that also exports constants defeats fast refresh (oxlint
// react/only-export-components), and because e2e/landing-samples.spec.ts
// imports them without wanting a component.

/**
 * Ready-made pairs, so a first visit does not begin with a blank box. Owner-chosen
 * 2026-08-07. `steps` = artists BETWEEN the two (UXR-D6), measured on the served
 * graph 2026-09-08 by the router itself.
 *
 * ⚠ MBIDs and step counts both depend on the SERVED ARTIFACT. A future artifact can
 * drop an artist or move a count. e2e/landing-samples.spec.ts asks the live router
 * for each pair and fails if a chip disagrees — that test IS the re-check rule.
 */
export const SAMPLE_JOURNEYS = [
  { from: '561d854a-6a28-4aa7-8c99-323e6ce46c2a', fromName: 'Miles Davis',
    to: 'a74b1b7f-71a5-4011-9441-d0b5e4122711', toName: 'Radiohead', steps: 3 },
  { from: '1d543e07-d0d2-4834-a8db-d65c50c2a856', fromName: 'Dolly Parton',
    to: '056e4f3e-d505-4dad-8ec1-d04f521cbb56', toName: 'Daft Punk', steps: 4 },
  { from: '89aa5ecb-59ad-46f5-b3eb-2d424e941f19', fromName: 'Bad Bunny',
    to: '56a55378-f155-48de-80a5-d80104221267', toName: 'Chappell Roan', steps: 6 },
] as const;

/** The desktop hero's illustrative journey (UXR-D14). Same drift rule, same test. */
export const TEASER = {
  from: '561d854a-6a28-4aa7-8c99-323e6ce46c2a',
  to: '056e4f3e-d505-4dad-8ec1-d04f521cbb56',
  names: ['Miles Davis', 'Nina Simone', 'Marvin Gaye', 'Daryl Hall & John Oates', 'Genesis', 'David Gilmour', 'Daft Punk'],
} as const;
