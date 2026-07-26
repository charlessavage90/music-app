import { useEffect, useRef, useState } from 'react';
import { searchArtists } from '@/api/client';
import type { Artist } from '@/api/types';

interface Props {
  label: string;
  /** Already-chosen artist to open with — set when returning from a path. */
  initial?: Artist | null;
  /** An artist, or null when the box no longer holds a chosen one. */
  onSelect: (artist: Artist | null) => void;
}

export function ArtistSearch({ label, initial, onSelect }: Props) {
  const [query, setQuery] = useState(initial?.name ?? '');
  const [results, setResults] = useState<Artist[]>([]);
  const [open, setOpen] = useState(false);
  // A search that found nothing and a search that failed used to render
  // identically as nothing. After the deploy the second is a real event.
  const [status, setStatus] = useState<'idle' | 'empty' | 'failed'>('idle');
  const inputId = useRef(`search-${Math.random().toString(36).slice(2)}`).current;
  // A prefilled name is already a choice, so it must not fire a search and
  // drop a dropdown over the page the moment you arrive.
  const selectedName = useRef<string | null>(initial?.name ?? null);

  useEffect(() => {
    const q = query.trim();
    if (!q || q === selectedName.current) {
      setResults([]);
      setOpen(false);
      setStatus('idle');
      return;
    }
    const controller = new AbortController();
    const timer = setTimeout(() => {
      searchArtists(q, controller.signal)
        .then((r) => {
          setResults(r);
          setOpen(true);
          setStatus(r.length === 0 ? 'empty' : 'idle');
        })
        .catch((err) => {
          // An abort is this component superseding its own request, not a
          // failure the user should be told about.
          if (controller.signal.aborted || (err as Error)?.name === 'AbortError') return;
          setResults([]);
          setOpen(false);
          setStatus('failed');
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
        onChange={(e) => {
          const next = e.target.value;
          setQuery(next);
          // Typing away from the chosen artist un-chooses them. The text and the
          // selection are separate state, and nothing else reconciles them: left
          // alone, "Find path" stays live and routes to the artist you just typed
          // over. Not a race with the dropdown — only clicking an entry chooses,
          // so waiting for it never helped.
          if (selectedName.current !== null && next !== selectedName.current) {
            selectedName.current = null;
            onSelect(null);
          }
        }}
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
      {status !== 'idle' && (
        <p className="mt-1 text-sm text-[var(--color-muted)]">
          {status === 'empty' ? 'No artists found.' : 'Search is unavailable — try again.'}
        </p>
      )}
    </div>
  );
}
