import { useEffect } from 'react';
import { useClip } from '@/hooks/useClip';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artist: Artist;
  isPlaying: boolean;
  /** This card owns the audio, playing or paused — so its button toggles. */
  isCurrent?: boolean;
  /** One of the two artists you chose. Neither bypass signal applies to them. */
  isEndpoint?: boolean;
  onPlay: (mbid: string) => void;
  onToggle?: () => void;
  onBypass: (mbid: string, reason: BypassReason) => void;
  /**
   * Reports whether this artist has a clip at all — never its URL. The URL is
   * signed and short-lived, so the player asks for one at the moment of play (C2).
   */
  onClipResolved?: (mbid: string, hasClip: boolean) => void;
}

export function ArtistCard({
  artist, isPlaying, isCurrent, isEndpoint,
  onPlay, onToggle, onBypass, onClipResolved,
}: Props) {
  const clip = useClip(artist.mbid);
  const playable = clip.status === 'ready';

  useEffect(() => {
    if (clip.status === 'loading') return;
    onClipResolved?.(artist.mbid, playable);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clip.status]);

  return (
    <div
      className={`flex flex-wrap items-center gap-x-3 gap-y-0 sm:gap-x-4 rounded-xl px-3 py-3 sm:px-4 border border-[var(--color-border)] ${
        isPlaying ? 'bg-[var(--color-accent)]/15' : 'bg-[var(--color-surface)]'
      }`}
    >
      <div
        className="w-12 h-12 sm:w-14 sm:h-14 rounded-lg flex-none bg-[var(--color-border)] bg-cover"
        style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
        aria-hidden
      />
      <div className="flex-1 min-w-0">
        <div className="font-semibold truncate">{artist.name}</div>
        <div className="text-sm text-[var(--color-muted)] truncate">
          {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
        </div>
        {isPlaying && <div className="text-xs text-[var(--color-accent)] mt-0.5">▮▮▮ now playing</div>}
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
            className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-full border border-[var(--color-away)]/40 text-[var(--color-away)]"
          >
            ✕ Not for me
          </button>
          <button
            type="button"
            onClick={() => onBypass(artist.mbid, 'known')}
            className="flex-1 sm:flex-none text-xs px-3 py-1.5 rounded-full border border-[var(--color-dig)]/40 text-[var(--color-dig)]"
          >
            ✓ I know them
          </button>
        </div>
      )}
      <button
        type="button"
        aria-label={isPlaying ? 'Pause' : 'Play'}
        disabled={!playable}
        // The card that owns the audio toggles it. Calling onPlay here would
        // re-seek to zero, which is why only the bottom bar could pause.
        onClick={() => (isCurrent ? onToggle?.() : onPlay(artist.mbid))}
        className="w-10 h-10 rounded-full flex-none bg-[var(--color-accent)] text-white flex items-center justify-center disabled:opacity-30"
      >
        {isPlaying ? '❚❚' : '▶'}
      </button>
    </div>
  );
}
