import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArtistSearch } from '@/components/ArtistSearch';
import type { Artist } from '@/api/types';

export function LandingPage() {
  const [from, setFrom] = useState<Artist | null>(null);
  const [to, setTo] = useState<Artist | null>(null);
  const navigate = useNavigate();

  const sameArtist = !!from && !!to && from.mbid === to.mbid;
  const ready = !!from && !!to && !sameArtist;

  return (
    <main className="max-w-xl mx-auto px-4 py-16">
      <h1 className="text-2xl font-semibold mb-6">Artist Path</h1>
      <p className="text-[var(--color-muted)] mb-8">
        Name two artists and hear a smooth path between them.
      </p>
      <div className="space-y-4">
        <ArtistSearch label="From" onSelect={setFrom} />
        <ArtistSearch label="To" onSelect={setTo} />
      </div>
      {sameArtist && (
        <p className="mt-3 text-sm text-[var(--color-away)]">Pick two different artists.</p>
      )}
      <button
        type="button"
        disabled={!ready}
        onClick={() => from && to && navigate(`/path/${from.mbid}/${to.mbid}`)}
        className="mt-6 rounded-lg bg-[var(--color-accent)] px-4 py-2 font-medium disabled:opacity-40"
      >
        Find path
      </button>
    </main>
  );
}
