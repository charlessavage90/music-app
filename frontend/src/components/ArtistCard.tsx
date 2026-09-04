import { useEffect } from 'react';
import { useClip } from '@/hooks/useClip';
import { PlayButton } from './PlayButton';
import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
  isPlaying: boolean;
  /** This card owns the audio, playing or paused — so its button toggles. */
  isCurrent?: boolean;
  /** One of the two artists you chose. Neither bypass signal applies to them. */
  isEndpoint?: boolean;
  /** Which end, when this is an endpoint. Drives the eyebrow label. */
  endpointLabel?: 'start' | 'destination';
  /**
   * This artist was not on the previous path. Marked briefly on arrival, which
   * is the confirmation that survives a rebuild answering faster than the eye.
   */
  isNew?: boolean;
  onPlay: (mbid: string) => void;
  onToggle?: () => void;
  onBypass: (mbid: string) => void;
  /**
   * Reports whether this artist has a clip at all — never its URL. The URL is
   * signed and short-lived, so the player asks for one at the moment of play (C2).
   */
  onClipResolved?: (mbid: string, hasClip: boolean) => void;
}

export function ArtistCard({
  artist, isPlaying, isCurrent, isEndpoint, endpointLabel, isNew,
  onPlay, onToggle, onBypass, onClipResolved,
}: Props) {
  const clip = useClip(artist.mbid);
  const playable = clip.status === 'ready';
  const silent = clip.status === 'none';

  useEffect(() => {
    if (clip.status === 'loading') return;
    onClipResolved?.(artist.mbid, playable);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clip.status]);

  return (
    <div
      className={`rounded-xl border px-3.5 sm:px-4 ${
        // A step card's footer strip bleeds to the card's edges, so the card
        // owns no bottom padding and must clip: the strip supplies both.
        isEndpoint ? 'py-3.5' : 'overflow-hidden pt-3.5 pb-0'
      } ${
        // Fades from an accent ring to nothing over GLOW_MS. The card is not
        // re-mounted between paths when the artist survives, so this class
        // arriving IS the animation trigger.
        isNew ? '[animation:ap-glow_800ms_ease-out]' : ''
      } ${
        isPlaying
          ? 'bg-[var(--color-accent)]/[.13] border-[var(--color-accent)]/[.34]'
          : isEndpoint
            ? 'bg-[var(--color-surface)] border-[var(--color-endpoint)] shadow-[inset_0_1px_0_rgba(231,233,238,.05)]'
            : 'bg-[var(--color-surface)] border-[var(--color-border)] hover:border-[var(--color-border-hover)]'
      }`}
    >
      {endpointLabel && (
        <div className="mb-2.5 text-[9.5px] font-semibold uppercase tracking-[.14em] text-[var(--color-note)]">
          {endpointLabel === 'start' ? 'Starting artist' : 'Destination artist'}
        </div>
      )}
      {/* No longer wraps: the two bypass signals moved out of this row into the
          footer strip below, and they were the non-shrinkable pair that forced
          the artist name toward zero at phone width (TR-16). */}
      <div className="flex items-center gap-3 sm:gap-3.5">
        <div
          className={`flex-none rounded-[9px] bg-[var(--color-border)] bg-cover ${
            isEndpoint ? 'w-14 h-14' : 'w-[52px] h-[52px]'
          } ${silent ? 'opacity-75' : ''}`}
          style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
          aria-hidden
        />
        <div className="flex-1 min-w-0">
          {/* UI-5: data-testid, not a style class — e2e/responsive.spec.ts
              measures this element and must not depend on its typography. */}
          <div
            data-testid="artist-name"
            className="font-semibold text-base sm:text-[16.5px] tracking-[-.01em] truncate"
          >
            {artist.name}
          </div>
          {/* The duration sits in its own non-shrinking span so a long title
              truncates and "0:30" survives — the reverse would drop the one
              fact this line was changed to carry. Only shown when there IS
              something to play; "No preview available" must not claim 30
              seconds of it. Bare "0:30" rather than "0:30 sample" at the
              owner's request 2026-08-07: seven characters back for the title,
              which truncates hard at 390px. */}
          <div className="mt-1 flex items-baseline gap-1.5 text-[12.5px]">
            <span
              className={`truncate ${
                silent ? 'text-[var(--color-label)]' : 'text-[var(--color-muted)]'
              }`}
            >
              {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
            </span>
            {playable && <span className="flex-none text-[var(--color-label)]">· 0:30</span>}
          </div>
          {isPlaying && (
            <div className="mt-1.5 text-[10.5px] font-medium uppercase tracking-[.1em] text-[var(--color-accent)]">
              ▮▮▮ now playing
            </div>
          )}
        </div>
        <PlayButton
          state={isPlaying ? 'pause' : 'play'}
          size="card"
          disabled={!playable}
          // The card that owns the audio toggles it. Calling onPlay here would
          // re-seek to zero, which is why only the bottom bar could pause.
          onClick={() => (isCurrent ? onToggle?.() : onPlay(artist.mbid))}
        />
      </div>

      {!isEndpoint && (
        // The recessed footer strip. Negative margins cancel the card's own
        // horizontal padding so it spans edge to edge; the card clips it.
        //
        // ONE control since LUX-1, so the strip IS the control rather than a
        // disclosure for a pair of them. The tray, its aria-expanded state and
        // its "way back" heading all went with the second option: a tray that
        // reveals a single button is a wasted press (LUX-D1).
        <div className="-mx-3.5 sm:-mx-4 mt-3 border-t border-[var(--color-strip-border)] bg-[var(--color-strip)]">
          <button
            type="button"
            onClick={() => onBypass(artist.mbid)}
            className="flex w-full flex-col items-center gap-0.5 px-3.5 py-2.5 text-center transition-colors hover:bg-[var(--color-accent)]/[.07] sm:px-4"
          >
            <span className="text-[12.5px] text-[var(--color-note)]">
              Dig deeper — same vibe, less familiar
            </span>
            {/* The one thing the label cannot imply, said at the moment of
                choosing rather than only in the explainer above the path,
                which can be dismissed and usually has been. */}
            <span className="text-[11px] text-[var(--color-label)]">
              Rebuilds the whole journey
            </span>
          </button>
        </div>
      )}
    </div>
  );
}
