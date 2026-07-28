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
      {/* UI-3: the text stays "From"/"To" and is uppercased in CSS.
          getByLabelText is an exact match and four test files depend on it. */}
      <label
        htmlFor={inputId}
        className="block mb-[9px] text-[11px] font-medium uppercase tracking-[.09em] text-[var(--color-label)]"
      >
        {label}
      </label>
      <input
        id={inputId}
        className="w-full h-[52px] sm:h-[54px] rounded-lg bg-[var(--color-surface)] border border-[var(--color-border)] px-4 sm:px-[18px] text-[19px] sm:text-[20px] tracking-[-.01em] outline-none transition-shadow hover:border-[var(--color-border-hover)] focus:border-[var(--color-accent)] focus:shadow-[0_0_0_3px_rgba(74,144,217,.14)]"
        placeholder="Search an artist"
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
        // Artist names are proper nouns the keyboard does not know — "Sigur Rós",
        // "MF DOOM", "!!!" — and iOS rewrites and auto-capitalises them mid-typing,
        // so the query sent was not the query typed and a present artist came back
        // empty.
        autoCorrect="off"
        autoCapitalize="off"
        spellCheck={false}
      />
      {open && results.length > 0 && (
        <ul className="absolute z-10 left-0 right-0 top-[calc(100%+8px)] rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] p-1.5 shadow-[0_24px_48px_-12px_rgba(0,0,0,.75),0_2px_6px_rgba(0,0,0,.4)]">
          {results.map((a) => (
            <li key={a.mbid}>
              <button
                type="button"
                className="flex w-full items-baseline gap-[7px] rounded-lg px-3 py-3 text-left hover:bg-[var(--color-accent)]/10"
                onClick={() => choose(a)}
              >
                <span className="text-[15px] tracking-[-.005em] whitespace-nowrap">{a.name}</span>
                {a.disambiguation && (
                  <span className="text-[12.5px] text-[var(--color-note)] truncate">
                    — {a.disambiguation}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      )}
      {status !== 'idle' && (
        <p className="mt-2 text-sm text-[var(--color-muted)]">
          {status === 'empty' ? 'No artists found.' : 'Search is unavailable — try again.'}
        </p>
      )}
    </div>
  );
}
