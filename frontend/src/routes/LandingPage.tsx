import { useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { ArtistSearch } from '@/components/ArtistSearch';
import type { Artist } from '@/api/types';

/**
 * The pair carried back by "New path", if we arrived that way.
 *
 * Only the id is used to route; the name is what fills the box. Both must be
 * present to count as a choice, or "Find path" would enable on a half-known
 * artist.
 */
function seedFrom(params: URLSearchParams, idKey: string, nameKey: string): Artist | null {
  const mbid = params.get(idKey);
  const name = params.get(nameKey);
  if (!mbid || !name) return null;
  return { mbid, name, disambiguation: '', popularity: 0 };
}

export function LandingPage() {
  const [params] = useSearchParams();
  const [seedA] = useState(() => seedFrom(params, 'from', 'fromName'));
  const [seedB] = useState(() => seedFrom(params, 'to', 'toName'));
  const [from, setFrom] = useState<Artist | null>(seedA);
  const [to, setTo] = useState<Artist | null>(seedB);
  const navigate = useNavigate();

  const sameArtist = !!from && !!to && from.mbid === to.mbid;
  const ready = !!from && !!to && !sameArtist;

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-[520px] flex-col px-7 pt-11 pb-9 sm:pt-14">
      <h1 className="text-[27px] sm:text-[38px] font-medium tracking-[-.02em] sm:tracking-[-.025em] leading-[1.1] sm:leading-[1.05]">
        Artist Path
      </h1>
      {/* Owner-written 2026-08-07, replacing the single paragraph of 2026-07-28.
          Two lines with split roles, because one sentence was carrying both the
          promise and the mechanism and the promise kept losing: the page never
          said the app is FOR finding music you don't know.

          These are HIS words verbatim, not a session's draft. The earlier
          version explained the mechanism ("someone their listeners share") and
          he cut it — the page now promises the outcome and leaves the how to
          the journey page's explainer. Do not reinstate the mechanism line
          here without asking him. */}
      <p className="mt-3 sm:mt-3.5 max-w-[320px] sm:max-w-[420px] text-[17px] sm:text-[19px] leading-[1.35] tracking-[-.01em] text-[var(--color-text)] text-pretty">
        Find a smooth path between any two artists
      </p>
      <p className="mt-2.5 max-w-[300px] sm:max-w-[400px] text-[13.5px] sm:text-[14.5px] leading-[1.5] text-[var(--color-muted)] text-pretty">
        Discover what lives in between
      </p>

      <div className="mt-11 sm:mt-10 flex flex-col gap-5">
        <ArtistSearch label="From" initial={seedA} onSelect={setFrom} />
        <ArtistSearch label="To" initial={seedB} onSelect={setTo} />
        {sameArtist && (
          <p className="text-sm text-[var(--color-away)]">Pick two different artists.</p>
        )}
        <button
          type="button"
          disabled={!ready}
          onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
          className="mt-1.5 h-[52px] sm:h-[54px] w-full rounded-full bg-[var(--color-accent)] text-[15.5px] sm:text-base font-semibold tracking-[.01em] text-[var(--color-bg)] transition-opacity enabled:hover:bg-[#5b9ce0] disabled:cursor-not-allowed disabled:opacity-30"
        >
          Discover a path
        </button>
      </div>

      {/* A miniature of the journey the app builds: your artist, someone in
          between, their artist. Decorative — the three dots carry the same
          colours as the two bypass signals and the rail. The clip-length line
          that sat under this was removed 2026-07-28 at the owner's request. */}
      <div className="mt-auto flex flex-col items-center pt-10">
        <div className="flex items-center gap-2" aria-hidden>
          <span className="block size-[5px] rounded-full bg-[var(--color-away)]" />
          <span className="block h-px w-[22px] bg-[var(--color-border)]" />
          <span className="block size-[5px] rounded-full bg-[var(--color-muted)]" />
          <span className="block h-px w-[22px] bg-[var(--color-border)]" />
          <span className="block size-[5px] rounded-full bg-[var(--color-dig)]" />
        </div>
      </div>
    </main>
  );
}
