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
    <main className="max-w-xl mx-auto px-4 py-10 sm:py-16">
      <h1 className="text-2xl font-semibold mb-6">Artist Path</h1>
      <p className="text-[var(--color-muted)] mb-8">
        Name two artists and hear a smooth path between them.
      </p>
      <div className="space-y-4">
        <ArtistSearch label="From" initial={seedA} onSelect={setFrom} />
        <ArtistSearch label="To" initial={seedB} onSelect={setTo} />
      </div>
      {sameArtist && (
        <p className="mt-3 text-sm text-[var(--color-away)]">Pick two different artists.</p>
      )}
      <button
        type="button"
        disabled={!ready}
        onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
        className="mt-6 w-full sm:w-auto rounded-lg bg-[var(--color-accent)] px-4 py-2 font-medium disabled:opacity-40"
      >
        Find path
      </button>
    </main>
  );
}
