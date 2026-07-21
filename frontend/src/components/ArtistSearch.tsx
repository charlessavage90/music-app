import { useEffect, useRef, useState } from 'react';
import { searchArtists } from '@/api/client';
import type { Artist } from '@/api/types';

interface Props {
  label: string;
  onSelect: (artist: Artist) => void;
}

export function ArtistSearch({ label, onSelect }: Props) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Artist[]>([]);
  const [open, setOpen] = useState(false);
  const inputId = useRef(`search-${Math.random().toString(36).slice(2)}`).current;
  const selectedName = useRef<string | null>(null);

  useEffect(() => {
    const q = query.trim();
    if (!q || q === selectedName.current) {
      setResults([]);
      setOpen(false);
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => {
      searchArtists(q, controller.signal)
        .then((r) => {
          setResults(r);
          setOpen(true);
        })
        .catch(() => {
          /* aborted or transient — leave prior results */
        });
    }, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query]);

  function choose(artist: Artist) {
    selectedName.current = artist.name;
    onSelect(artist);
    setQuery(artist.name);
    setOpen(false);
  }

  return (
    <div className="relative">
      <label htmlFor={inputId} className="block text-sm text-[var(--color-muted)] mb-1">
        {label}
      </label>
      <input
        id={inputId}
        className="w-full rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] px-3 py-2 outline-none focus:border-[var(--color-accent)]"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        autoComplete="off"
      />
      {open && results.length > 0 && (
        <ul className="absolute z-10 mt-1 w-full rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] overflow-hidden">
          {results.map((a) => (
            <li key={a.mbid}>
              <button
                type="button"
                className="w-full text-left px-3 py-2 hover:bg-[var(--color-accent)]/20"
                onClick={() => choose(a)}
              >
                {a.name}
                {a.disambiguation && (
                  <span className="text-[var(--color-muted)] text-sm"> — {a.disambiguation}</span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
