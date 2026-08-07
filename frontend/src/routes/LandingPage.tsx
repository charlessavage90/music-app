import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArtistSearch } from '@/components/ArtistSearch';
import type { Artist } from '@/api/types';

/**
 * Ready-made pairs, so a first visit does not begin with a blank box and the
 * demand that you think of two artists. Owner-chosen 2026-08-07.
 *
 * ⚠ The MBIDs are hardcoded and therefore depend on the SERVED ARTIFACT. All
 * six were confirmed present in graph-msw-tu50.bin and all three pairs were
 * confirmed to build a natural path (5, 6 and 8 stops) on 2026-08-07. MBIDs are
 * stable in MusicBrainz, so the risk is not that one changes — it is that a
 * future artifact DROPS an artist, after which that card lands on the
 * "we couldn't find that artist" page. Re-check these three after any graph
 * adoption; there is no test that can, because the test fixtures are 500-node
 * samples that contain none of them.
 */
const SAMPLE_JOURNEYS = [
  {
    from: '561d854a-6a28-4aa7-8c99-323e6ce46c2a', fromName: 'Miles Davis',
    to: 'a74b1b7f-71a5-4011-9441-d0b5e4122711', toName: 'Radiohead',
  },
  {
    from: '1d543e07-d0d2-4834-a8db-d65c50c2a856', fromName: 'Dolly Parton',
    to: '056e4f3e-d505-4dad-8ec1-d04f521cbb56', toName: 'Daft Punk',
  },
  {
    from: '89aa5ecb-59ad-46f5-b3eb-2d424e941f19', fromName: 'Bad Bunny',
    to: '56a55378-f155-48de-80a5-d80104221267', toName: 'Chappell Roan',
  },
] as const;

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
        <ArtistSearch label="From" end="start" initial={seedA} onSelect={setFrom} />
        <ArtistSearch label="To" end="destination" initial={seedB} onSelect={setTo} />
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

      {/* The blank-box problem: the form asks you to think of two artists before
          the app has shown you it is worth the effort. These cost one tap and
          are ordinary links, so they are shareable and work with the back
          button like any other journey. */}
      <section className="mt-11 sm:mt-12">
        <h2 className="text-[12.5px] sm:text-[13px] text-[var(--color-muted)]">
          Not sure where to start? Try one of these.
        </h2>
        <ul className="mt-3.5 flex flex-col gap-2.5">
          {SAMPLE_JOURNEYS.map((j) => (
            <li key={j.from}>
              <Link
                to={`/path/${j.from}/${j.to}`}
                className="group flex items-center gap-3 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-3.5 transition-colors hover:border-[var(--color-accent)] hover:bg-[var(--color-accent)]/[.07]"
              >
                <span className="min-w-0 flex-1 truncate text-[14.5px] sm:text-[15px]">
                  {j.fromName}
                  <span className="mx-2 text-[var(--color-label)]">→</span>
                  {j.toName}
                </span>
                <span
                  aria-hidden
                  className="flex-none text-[var(--color-label)] transition-colors group-hover:text-[var(--color-accent)]"
                >
                  ›
                </span>
              </Link>
            </li>
          ))}
        </ul>
      </section>

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
