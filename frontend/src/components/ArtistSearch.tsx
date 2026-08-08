import { useEffect, useRef, useState } from 'react';
import { searchArtists } from '@/api/client';
import type { Artist } from '@/api/types';

interface Props {
  label: string;
  /**
   * Which end of the journey this box is. Drives only the dot's colour, which
   * carries the same two colours as the journey rail's gradient — deliberately
   * not derived from `label`, so the dot survives a wording change.
   */
  end: 'start' | 'destination';
  /** Already-chosen artist to open with — set when returning from a path. */
  initial?: Artist | null;
  /** An artist, or null when the box no longer holds a chosen one. */
  onSelect: (artist: Artist | null) => void;
}

export function ArtistSearch({ label, end, initial, onSelect }: Props) {
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
      {/* Its own positioning context, so the dot centres on the INPUT rather
          than on the label-plus-input block. The dropdown below still hangs off
          the outer wrapper, which is what puts it under the whole field. */}
      <div className="relative">
      {/* The mockup's dot, never ported. Purely decorative — it colour-codes the
          two ends against the journey rail — so it is hidden from assistive
          tech, and the input carries its own left padding to clear it. */}
      <span
        aria-hidden
        className={`pointer-events-none absolute left-4 sm:left-[18px] top-1/2 z-10 block size-[7px] -translate-y-1/2 rounded-full ${
          end === 'start' ? 'bg-[var(--color-accent)]' : 'bg-[var(--color-dig)]'
        }`}
      />
      <input
        id={inputId}
        className="w-full h-[52px] sm:h-[54px] rounded-lg bg-[var(--color-field)] border-[1.5px] border-[var(--color-field-border)] pl-9 pr-4 sm:pl-[35px] sm:pr-[18px] text-[19px] sm:text-[20px] tracking-[-.01em] outline-none shadow-[0_1px_0_rgba(231,233,238,.045)_inset,0_6px_18px_-10px_rgba(0,0,0,.9)] transition-colors hover:border-[var(--color-accent)] hover:bg-[var(--color-field-hover)] focus:border-[var(--color-accent)] focus:bg-[var(--color-field-hover)] focus:shadow-[0_0_0_4px_rgba(74,144,217,.13),0_1px_0_rgba(231,233,238,.045)_inset]"
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
      </div>
      {open && results.length > 0 && (
        // z-20, NOT z-10, and the gap is the fix. This list hangs over the
        // NEXT field, whose coloured dot is also absolutely positioned. Both
        // boxes are plain flex siblings with no transform, filter or opacity
        // between them, so nothing creates an intervening stacking context and
        // every z-index here resolves against the same one. At EQUAL z-index
        // the tie breaks on DOM order — and the next field's dot comes later
        // in the document than this list, so it painted on top of the open
        // dropdown. The invariant is that an open dropdown outranks every
        // field decoration; matching the dot's z-10 is what broke it.
        <ul className="absolute z-20 left-0 right-0 top-[calc(100%+8px)] rounded-xl bg-[var(--color-surface)] border border-[var(--color-border)] p-1.5 shadow-[0_24px_48px_-12px_rgba(0,0,0,.75),0_2px_6px_rgba(0,0,0,.4)]">
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
