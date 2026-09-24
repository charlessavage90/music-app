import { dotColour } from '@/lib/rail';

/**
 * The rail: a vertical gradient line running dot to dot down a list of stops,
 * cyan at the start, violet between, pink at the end. Drawn by the journey page
 * since 2026-09-08 and, since issue #201, by the landing page's example card
 * with these same pieces — its own arithmetic had the line ~2px off its dots.
 *
 * GEOMETRY, and the three parts must stay in sync: the list pads its content
 * by 26px (RAIL_LIST_CLASS, lib/rail.ts), so -29px on a 13px dot puts the
 * dot's centre 3.5px from the list's own left edge, and the 3px line at
 * left-2px has that same centre. Changing any one number alone leaves the
 * dots sitting beside the line — which is what happened, by exactly 3px,
 * until it was measured in a browser on 2026-09-08. Where the line starts and
 * stops is measured, not assumed: hooks/useRailInset.ts.
 */

/** The line itself. Place it first inside a RAIL_LIST_CLASS list. */
export function RailLine({ inset }: { inset: { top: number; bottom: number } | null }) {
  return (
    <span
      aria-hidden
      data-rail-line
      className="absolute left-[2px] w-[3px] rounded-full bg-gradient-to-b from-[var(--color-start)] via-[var(--color-playing)] to-[var(--color-end)]"
      style={inset ? { top: inset.top, bottom: inset.bottom } : { top: 0, bottom: 0 }}
    />
  );
}

interface DotProps {
  index: number;
  total: number;
  /** Overrides the positional colour — the journey page's selected card. */
  colour?: string;
}

/**
 * One stop's dot, and the anchor `useRailInset` measures. Place it inside a
 * `relative` row of a RAIL_LIST_CLASS list.
 */
export function RailDot({ index, total, colour }: DotProps) {
  return (
    <span
      aria-hidden
      data-rail-dot
      className="absolute -left-[29px] top-1/2 size-[13px] -translate-y-1/2 rounded-full border-[3px] bg-[var(--color-bg)]"
      style={{ borderColor: colour ?? dotColour(index, total) }}
    />
  );
}
