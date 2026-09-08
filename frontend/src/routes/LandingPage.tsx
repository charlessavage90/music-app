import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ArtistCountBadge } from '@/components/ArtistCountBadge';
import { ArtistSearch } from '@/components/ArtistSearch';
import { Brand } from '@/components/Brand';
import type { Artist } from '@/api/types';
import { SAMPLE_JOURNEYS, TEASER } from '@/lib/sampleJourneys';

const WORDS = ['no', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine'] as const;

/** The mockup's three cards, verbatim (UXR-D13). */
const HOW = [
  { n: '01', tone: 'var(--color-start)', title: 'Name two artists',
    body: 'One you are in the mood for, one you are curious about.' },
  { n: '02', tone: 'var(--color-playing)', title: 'Listen to the path',
    body: 'Every stop gets a 30-second clip, and every step sounds like a sensible move from the last. No jolts.' },
  { n: '03', tone: 'var(--color-end)', title: 'Dig deeper',
    body: 'Know a stop already? Press Dig deeper and the route rebuilds through artists you are far less likely to know.' },
] as const;

/**
 * The pair carried back by "New path", if we arrived that way.
 *
 * Only the id is used to route; the name is what fills the box. Both must be
 * present to count as a choice, or the button would enable on a half-known
 * artist.
 */
function seedFrom(params: URLSearchParams, idKey: string, nameKey: string): Artist | null {
  const mbid = params.get(idKey);
  const name = params.get(nameKey);
  if (!mbid || !name) return null;
  return { mbid, name, disambiguation: '', popularity: 0, spotifyId: null, appleId: null, facts: null };
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
  const teaserSteps = TEASER.names.length - 2;

  return (
    <main className="mx-auto w-full max-w-[1280px] px-6 pb-14 pt-6 sm:px-10">
      <header className="flex items-center justify-between py-2">
        <Brand size="hero" />
        {/* UXR-D13: no nav until the pages behind it exist. */}
      </header>

      <div className="mt-10 grid items-center gap-12 lg:mt-16 lg:grid-cols-[1.08fr_.92fr] lg:gap-16">
        <div>
          <ArtistCountBadge />
          {/* UXR-D12: the mockup's copy, verbatim. If the owner overrules that
              decision, the 2026-08-07 lines return here under the new type:
              "Find a smooth path between any two artists" / "Discover what lives in between". */}
          <h1 className="mt-5 font-display text-[31px] font-medium leading-[1.06] tracking-[-.03em] text-balance sm:text-[44px] lg:text-[60px] lg:leading-[1.02] lg:tracking-[-.035em]">
            Hear what lives between two artists you love.
          </h1>
          <p className="mt-4 max-w-[520px] text-[15px] leading-[1.5] text-[var(--color-muted)] text-pretty sm:text-[18px]">
            Name two. Unsung.fm builds a listenable path between them — every step a small,
            sensible move from the last, with a 30-second clip. Then{' '}
            <span className="text-[var(--color-text)]">dig deeper</span> to swap the obvious
            names for the ones you have never heard.
          </p>

          <div className="mt-8 flex max-w-[600px] flex-col gap-3.5">
            <div className="grid gap-3.5 sm:grid-cols-2">
              <ArtistSearch label="Start with" end="start" initial={seedA} onSelect={setFrom} />
              <ArtistSearch label="End with" end="destination" initial={seedB} onSelect={setTo} />
            </div>
            {sameArtist && (
              <p className="text-sm text-[var(--color-away)]">Pick two different artists.</p>
            )}
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
              <button
                type="button"
                disabled={!ready}
                onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
                className="h-14 rounded-full bg-[linear-gradient(90deg,var(--color-start),var(--color-playing)_55%,var(--color-end))] bg-[length:200%_100%] px-9 text-[16.5px] font-bold tracking-[-.01em] text-[var(--color-bg)] [animation:un-sheen_9s_linear_infinite] motion-safe-only disabled:cursor-not-allowed disabled:opacity-30"
              >
                Build the path
              </button>
              <span className="text-[13.5px] text-[var(--color-label)]">
                Takes about three seconds · no account needed
              </span>
            </div>
          </div>

          {/* The blank-box problem: the form asks you to think of two artists before
              the app has shown you it is worth the effort. These cost one tap and are
              ordinary links, so they are shareable and work with Back like any journey. */}
          <section className="mt-8">
            <h2 className="text-[12.5px] text-[var(--color-label)]">Or start from one of these</h2>
            <ul className="mt-3 flex flex-wrap gap-2.5">
              {SAMPLE_JOURNEYS.map((j) => (
                <li key={j.from}>
                  <Link
                    to={`/path/${j.from}/${j.to}`}
                    aria-label={`${j.fromName} to ${j.toName}, ${j.steps} steps`}
                    className="flex items-center gap-2 rounded-full border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-4 py-2.5 text-[14px] transition-colors hover:border-[var(--color-start)]"
                  >
                    <span>{j.fromName}</span>
                    <span aria-hidden className="text-[var(--color-label)]">→</span>
                    <span>{j.toName}</span>
                    <span className="text-[12px] text-[var(--color-label)]">{j.steps} steps</span>
                  </Link>
                </li>
              ))}
            </ul>
          </section>
        </div>

        {/* The desktop hero's right column: the mark, breathing, and the teaser (UXR-D14).
            Hidden below lg — the mobile artboard shows the mark alone, above the h1. */}
        <div className="hidden flex-col items-center gap-7 lg:flex">
          <div className="relative flex size-[300px] items-center justify-center">
            <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle,rgba(143,108,245,.28),rgba(46,197,238,.12)_45%,transparent_70%)]" aria-hidden />
            <img src="/unsung-mark.png" alt="" width={246} height={246} className="relative" />
          </div>
          <div className="w-full max-w-[420px] rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-5">
            <div className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">
              A path, {WORDS[teaserSteps] ?? teaserSteps} steps
            </div>
            <ol className="relative mt-4 flex flex-col gap-3 pl-5">
              <span aria-hidden className="absolute bottom-1.5 left-[3px] top-1.5 w-0.5 rounded-full bg-gradient-to-b from-[var(--color-start)] via-[var(--color-playing)] to-[var(--color-end)]" />
              {TEASER.names.map((name) => (
                <li key={name} className="relative flex items-center gap-2.5 text-[14.5px]">
                  <span aria-hidden className="absolute -left-[22px] size-2 rounded-full border-2 border-[var(--color-playing)] bg-[var(--color-surface)]" />
                  {name}
                </li>
              ))}
            </ol>
          </div>
        </div>
      </div>

      <section className="mt-14 grid gap-5 border-t border-[var(--color-border)] pt-10 md:grid-cols-3">
        {HOW.map((h) => (
          <div key={h.n} className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] px-6 py-6">
            <div className="flex items-center gap-3">
              <span className="font-display text-[13px] font-bold tracking-[.06em]" style={{ color: h.tone }}>{h.n}</span>
              <span aria-hidden className="h-px flex-1" style={{ background: `linear-gradient(90deg, ${h.tone}, transparent)` }} />
            </div>
            <h3 className="mt-4 font-display text-[21px] font-medium tracking-[-.02em]">{h.title}</h3>
            <p className="mt-2 text-[14.5px] leading-[1.55] text-[var(--color-muted)] text-pretty">{h.body}</p>
          </div>
        ))}
      </section>
    </main>
  );
}
