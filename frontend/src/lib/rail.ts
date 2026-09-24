/**
 * The rail's non-component half — the list class and the per-stop colour.
 * The line and the dot are components/Rail.tsx, which also carries the
 * geometry note that binds this padding to their offsets; the measuring hook
 * is hooks/useRailInset.ts. Split three ways only because a component file
 * may export nothing but components (oxlint react/only-export-components).
 */

/**
 * The list a rail is drawn in. 26px of left padding is what RailDot's -29px
 * and RailLine's left-2px are computed against — change one, change all
 * three (see the geometry note in components/Rail.tsx).
 */
export const RAIL_LIST_CLASS = 'relative flex flex-col pl-[26px]';

/** Cyan at the start, pink at the end, violet between — the rail's own gradient, per stop. */
export function dotColour(index: number, total: number): string {
  if (index === 0) return 'var(--color-start)';
  if (index === total - 1) return 'var(--color-end)';
  return 'var(--color-playing)';
}
