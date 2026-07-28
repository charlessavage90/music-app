import { useEffect } from 'react';
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

const BYPASS =
  'flex-1 sm:flex-none h-[34px] sm:h-8 px-3.5 rounded-full border text-[12.5px] flex items-center justify-center whitespace-nowrap transition-colors';

export function ArtistCard({
  artist, isPlaying, isCurrent, isEndpoint, endpointLabel,
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
      className={`rounded-xl border px-3.5 py-3.5 sm:px-4 ${
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
      <div className="flex flex-wrap items-center gap-x-3 gap-y-0 sm:gap-x-3.5">
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
        {!isEndpoint && (
          // On a phone this wrapper is full width and ordered last, so it takes a
          // row of its own beneath the artist and the two signals stay labelled.
          // From sm up it collapses back to an ordinary inline pair and the desktop
          // row is exactly what it was. One copy of the markup, deliberately: the
          // e2e specs resolve these by role and Playwright strict mode fails on two.
          <div className="order-last w-full mt-3 flex gap-2 sm:order-none sm:w-auto sm:mt-0">
            <button
              type="button"
              onClick={() => onBypass(artist.mbid, 'dislike')}
              className={`${BYPASS} border-[var(--color-away)]/[.38] text-[var(--color-away)] hover:bg-[var(--color-away)]/10 hover:border-[var(--color-away)]/60`}
            >
              ✕ Not for me
            </button>
            <button
              type="button"
              onClick={() => onBypass(artist.mbid, 'known')}
              className={`${BYPASS} border-[var(--color-dig)]/[.38] text-[var(--color-dig)] hover:bg-[var(--color-dig)]/10 hover:border-[var(--color-dig)]/60`}
            >
              ✓ I know them
            </button>
          </div>
        )}
        <PlayButton
          state={isPlaying ? 'pause' : 'play'}
          size="card"
          disabled={!playable}
          // The card that owns the audio toggles it. Calling onPlay here would
          // re-seek to zero, which is why only the bottom bar could pause.
          onClick={() => (isCurrent ? onToggle?.() : onPlay(artist.mbid))}
        />
      </div>
    </div>
  );
}
