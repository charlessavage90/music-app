import { useEffect, useState } from 'react';
import { useClip } from '@/hooks/useClip';
import { PlayButton } from './PlayButton';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artist: Artist;
  isPlaying: boolean;
  /** This card owns the audio, playing or paused — so its button toggles. */
  isCurrent?: boolean;
  /** One of the two artists you chose. Neither bypass signal applies to them. */
  isEndpoint?: boolean;
  /** Which end, when this is an endpoint. Drives the eyebrow label. */
  endpointLabel?: 'start' | 'destination';
  onPlay: (mbid: string) => void;
  onToggle?: () => void;
  onBypass: (mbid: string, reason: BypassReason) => void;
  /**
   * Reports whether this artist has a clip at all — never its URL. The URL is
   * signed and short-lived, so the player asks for one at the moment of play (C2).
   */
  onClipResolved?: (mbid: string, hasClip: boolean) => void;
}

/**
 * A choice inside the tray. Both rebuild the whole path — the difference is the
 * direction, which is why neither is styled as an accept and neither as a
 * reject. Red-vs-green signalled a conflict that does not exist.
 */
const TRAY_OPTION =
  'flex w-full items-baseline gap-2 rounded-lg border px-3.5 py-2.5 text-left transition-colors sm:flex-1 sm:min-w-0';

export function ArtistCard({
  artist, isPlaying, isCurrent, isEndpoint, endpointLabel,
  onPlay, onToggle, onBypass, onClipResolved,
}: Props) {
  const clip = useClip(artist.mbid);
  const playable = clip.status === 'ready';
  const silent = clip.status === 'none';
  // The tray is per-card and deliberately not lifted: two cards may be open at
  // once, and a press rebuilds the path anyway, which unmounts every card.
  const [trayOpen, setTrayOpen] = useState(false);

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
        isPlaying
          ? 'bg-[var(--color-accent)]/[.13] border-[var(--color-accent)]/[.34]'
          : isEndpoint
            ? 'bg-[var(--color-surface)] border-[var(--color-endpoint)] shadow-[inset_0_1px_0_rgba(231,233,238,.05)]'
            : trayOpen
              ? 'bg-[var(--color-surface)] border-[var(--color-border-hover)]'
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
          <div
            className={`mt-1 text-[12.5px] truncate ${
              silent ? 'text-[var(--color-label)]' : 'text-[var(--color-muted)]'
            }`}
          >
            {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
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
        <div className="-mx-3.5 sm:-mx-4 mt-3 border-t border-[var(--color-strip-border)] bg-[var(--color-strip)]">
          {/* One control in both states, so the tray can be closed again. The
              design drew the expanded tray with no way back — a gap, not a
              decision. Collapsed it is the strip; open it heads the tray. */}
          <button
            type="button"
            onClick={() => setTrayOpen((v) => !v)}
            aria-expanded={trayOpen}
            className={
              trayOpen
                ? 'flex w-full items-center gap-1.5 px-3.5 pt-3 pb-2.5 text-[11px] font-medium uppercase tracking-[.08em] text-[var(--color-label)] sm:px-4'
                : 'flex h-[38px] w-full items-center justify-center gap-1.5 text-[12.5px] text-[var(--color-note)] transition-colors hover:bg-[var(--color-accent)]/[.07] hover:text-[var(--color-accent)]'
            }
          >
            {trayOpen ? 'Which direction?' : 'Rebuild from here'}
            <span aria-hidden className="text-[11px]">{trayOpen ? '▴' : '▾'}</span>
          </button>

          {trayOpen && (
            // Stacked on a phone, side by side from sm up — the captions are
            // what need the width, and two of them do not fit on 390px.
            <div className="flex flex-col gap-2 px-3.5 pb-3.5 sm:flex-row sm:px-4">
              <button
                type="button"
                onClick={() => onBypass(artist.mbid, 'dislike')}
                className={`${TRAY_OPTION} border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-accent)] hover:bg-[var(--color-accent)]/10`}
              >
                <span className="whitespace-nowrap text-[13.5px]">Steer away</span>
                <span className="truncate text-[11.5px] text-[var(--color-note)]">
                  less like this sound
                </span>
              </button>
              <button
                type="button"
                onClick={() => onBypass(artist.mbid, 'known')}
                className={`${TRAY_OPTION} border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-accent)] hover:bg-[var(--color-accent)]/10`}
              >
                <span className="whitespace-nowrap text-[13.5px]">Go deeper</span>
                <span className="truncate text-[11.5px] text-[var(--color-note)]">
                  something more obscure
                </span>
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
