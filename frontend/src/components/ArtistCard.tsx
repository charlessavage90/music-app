import { useEffect } from 'react';
import { useClip } from '@/hooks/useClip';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artist: Artist;
  isPlaying: boolean;
  onPlay: (mbid: string) => void;
  onBypass: (mbid: string, reason: BypassReason) => void;
  onClipResolved?: (mbid: string, url: string | null) => void;
}

export function ArtistCard({ artist, isPlaying, onPlay, onBypass, onClipResolved }: Props) {
  const clip = useClip(artist.mbid);
  const playable = clip.status === 'ready';

  useEffect(() => {
    if (clip.status === 'loading') return;
    onClipResolved?.(artist.mbid, clip.track?.previewUrl ?? null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clip.status]);

  return (
    <div
      className={`flex items-center gap-4 rounded-xl px-4 py-3 border border-[var(--color-border)] ${
        isPlaying ? 'bg-[var(--color-accent)]/15' : 'bg-[var(--color-surface)]'
      }`}
    >
      <div
        className="w-14 h-14 rounded-lg flex-none bg-[var(--color-border)] bg-cover"
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
      <button
        type="button"
        onClick={() => onBypass(artist.mbid, 'dislike')}
        className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-away)]/40 text-[var(--color-away)]"
      >
        ✕ Not for me
      </button>
      <button
        type="button"
        onClick={() => onBypass(artist.mbid, 'known')}
        className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-dig)]/40 text-[var(--color-dig)]"
      >
        ✓ I know them
      </button>
      <button
        type="button"
        aria-label={isPlaying ? 'Pause' : 'Play'}
        disabled={!playable}
        onClick={() => onPlay(artist.mbid)}
        className="w-10 h-10 rounded-full flex-none bg-[var(--color-accent)] text-white flex items-center justify-center disabled:opacity-30"
      >
        {isPlaying ? '❚❚' : '▶'}
      </button>
    </div>
  );
}
