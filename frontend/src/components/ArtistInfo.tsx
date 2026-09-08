import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
}

/** MusicBrainz stores full dates where it has them; a card wants the year. */
function year(date: string | null): string | null {
  return date ? date.slice(0, 4) : null;
}

/**
 * "1993–2008", "1995–", "–2008", or nothing.
 *
 * An open right-hand side is the point of the trailing dash: an artist still
 * active reads as ongoing rather than as a single-year event, and an end with
 * no beginning reads as an ending rather than as a formation year.
 */
function lifeSpan(begin: string | null, end: string | null): string | null {
  const from = year(begin);
  const to = year(end);
  if (from && to) return `${from}–${to}`;
  if (from) return `${from}–`;
  if (to) return `–${to}`;
  return null;
}

/**
 * One compact line of structured facts about an artist (`LUX-4`).
 *
 * `L4-D3`: RENDER ONLY WHAT IS PRESENT, with no placeholder rows. A missing
 * life span shows nothing, not "Unknown" — the same position `LUX-3` took for
 * an absent control, and it is the empty state `LUX-E2` exists to check. That
 * evaluation is BLOCKED (its sample is damaged on the served map), so this
 * ships the cheapest empty state; if `LUX-E2` later finds a field too sparse
 * in the obscure half, the consequence is a designed empty state HERE, not a
 * rebuild. The artifact carries the data either way.
 *
 * A prose description is dropped, not deferred (spec §4.5): not Wikipedia's,
 * which is the fame floor again, and not generated, which hallucinates hardest
 * on exactly the obscure artists this app exists to deliver.
 *
 * The disambiguation leads because it is human-written and is usually the most
 * useful sentence available about an artist nobody has heard of. It has been
 * on the wire all along and was rendered only in the search dropdown.
 */
export function ArtistInfo({ artist }: Props) {
  const f = artist.facts;
  const parts = [
    artist.disambiguation || null,
    f?.type ?? null,
    // The human-readable area, falling back to the ISO code. Both together is
    // "United Kingdom · GB", which is noise on a one-line card.
    f?.area ?? f?.country ?? null,
    lifeSpan(f?.begin ?? null, f?.end ?? null),
  ].filter((p): p is string => Boolean(p));

  if (parts.length === 0) return null;

  return (
    // Matches the track-title line's typography deliberately: this is the same
    // register of information, not a heading and not a caption.
    //
    // WRAPS, and does not truncate — the one place this differs from the track
    // title above it. Truncating cost the life span on most real cards at
    // 390px ("Person · United States · 1933–2…"), because the dates sit at the
    // end of the natural reading order while the area is the longest and least
    // useful part. The alternatives were reordering the line so truncation ate
    // the area instead, or dropping `type` when a disambiguation is present —
    // both invent a ranking of which facts matter, which is exactly what
    // `L4-D3` declines to do. Wrapping shows all of it and costs one line on
    // the cards that need it. Pinned by e2e/responsive.spec.ts, which measures
    // it in a real layout engine; jsdom computes no layout, so a unit test
    // here could only assert the class name and would pass either way.
    <div className="mt-1 text-[12.5px] text-[var(--color-muted)]">
      {parts.join(' · ')}
    </div>
  );
}
