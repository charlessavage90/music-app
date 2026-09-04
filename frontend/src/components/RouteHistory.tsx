import type { Artist } from '@/api/types';

/**
 * The artists a bypass has removed from this journey.
 *
 * Before this existed a press made an artist vanish with no trace, which made
 * the press unreviewable — you could not see what you had skipped, or tell a
 * press that worked from one the router ignored (REQ-46).
 *
 * With one bypass signal (LUX-1) every row reads the same way, so this is a
 * LIST OF ARTISTS YOU SKIPPED rather than a route history with two verbs. It is
 * designed as what it is. The caption is the most useful thing a first-time
 * visitor can learn: the whole state is in the URL, so Back is safe.
 *
 * Order note: the URL preserves press order WITHIN a signal. A link shared
 * before LUX-1 can carry both, and its two blocks are then listed one after the
 * other rather than interleaved. That is a cosmetic limit on old links only —
 * no new link can have two blocks.
 *
 * Names arrive with the path response itself (LUX-2b) — the API knows for
 * certain which ids are in the graph, so there is no loading state here and
 * no client-side lookup.
 */
interface Props {
  /** Artists a bypass removed, in press order. */
  bypassed: Artist[];
  /** Exclusion ids the graph does not have (LUX-D2). */
  unresolved: string[];
}

export function RouteHistory({ bypassed, unresolved }: Props) {
  if (bypassed.length === 0 && unresolved.length === 0) return null;
  const recentFirst = [...bypassed].reverse();

  return (
    <section className="mt-7 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4">
      <h2 className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">
        Artists you skipped
      </h2>
      <ol className="mt-2.5 flex flex-col gap-1.5">
        {recentFirst.map((a) => (
          <li key={a.mbid} className="flex items-baseline gap-2 text-[13px]">
            <span aria-hidden className="text-[var(--color-label)]">·</span>
            <span className="text-[var(--color-text)]">{a.name}</span>
          </li>
        ))}
        {unresolved.map((id) => (
          // Not a blank line and not a dropped row: the router ignored this
          // press too, and saying so is the only honest thing here. Listed
          // after the named rows because the URL cannot say where it belonged.
          <li key={id} className="flex items-baseline gap-2 text-[13px]">
            <span aria-hidden className="text-[var(--color-label)]">·</span>
            <span className="text-[var(--color-label)]">An artist no longer in the map</span>
          </li>
        ))}
        <li className="flex items-baseline gap-2 border-t border-[var(--color-border)] pt-2 text-[13px] text-[var(--color-muted)]">
          <span aria-hidden className="text-[var(--color-label)]">·</span>
          Original route
        </li>
      </ol>
      <p className="mt-3 text-[11.5px] text-[var(--color-label)]">
        Back undoes any of these — the whole journey is in the address bar.
      </p>
    </section>
  );
}
