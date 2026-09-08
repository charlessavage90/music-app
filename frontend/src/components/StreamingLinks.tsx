import { appleUrl, spotifyUrl } from '@/lib/dspUrls';
import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
}

/**
 * Two links out to the streaming services, one per service, always both.
 *
 * `LUX-4`. The app's whole job is to hand you an artist you did not know, and
 * a 30-second clip is where that ends unless there is somewhere to go next.
 *
 * BOTH SERVICES ALWAYS RENDER (spec §4.1, option A). Where the artifact has no
 * id the link goes to a search for the artist's name instead of to their page.
 * That is not a degraded state to hide: the app routes toward obscure artists,
 * so missing ids are concentrated in exactly the population this exists to
 * serve, and showing one service while dropping the other reads as the artist
 * being absent from that service rather than as our data being thin.
 *
 * TEXT LABELS ONLY, no logos — a logo pulls in each company's brand
 * guidelines (spec §4.7), which is a licensing question, not a design one.
 */
export function StreamingLinks({ artist }: Props) {
  const links = [
    { label: 'Spotify', href: spotifyUrl(artist.spotifyId, artist.name) },
    { label: 'Apple Music', href: appleUrl(artist.appleId, artist.name) },
  ];

  return (
    <div className="mt-1.5 flex items-center gap-2.5">
      {links.map(({ label, href }) => (
        <a
          key={label}
          href={href}
          target="_blank"
          // noopener so the opened tab cannot reach back through window.opener;
          // noreferrer so we do not hand a DSP the journey URL, which carries
          // the listener's whole path including who they bypassed.
          rel="noopener noreferrer"
          // The accessible name carries the artist, because a screen-reader
          // user hears it out of context and a page of cards is otherwise a
          // list of identical "Spotify" links.
          aria-label={`${artist.name} on ${label}`}
          className="text-[11.5px] text-[var(--color-note)] underline-offset-2 hover:text-[var(--color-accent)] hover:underline"
        >
          {label}
        </a>
      ))}
    </div>
  );
}
