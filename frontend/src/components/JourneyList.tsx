import { useMemo, useRef, useState } from 'react';
import { ArtistCard } from './ArtistCard';
import { PlayerBar } from './PlayerBar';
import { usePlayer } from '@/player/usePlayer';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artists: Artist[];
  onBypass: (mbid: string, reason: BypassReason) => void;
}

export function JourneyList({ artists, onBypass }: Props) {
  const [urls, setUrls] = useState<Record<string, string | null>>({});
  const urlsRef = useRef(urls);
  urlsRef.current = urls;

  const playables = useMemo(
    () =>
      artists
        .map((a) => ({ mbid: a.mbid, url: urls[a.mbid] }))
        .filter((p): p is { mbid: string; url: string } => !!p.url),
    [artists, urls],
  );

  const player = usePlayer(playables);
  const currentName = artists.find((a) => a.mbid === player.currentMbid)?.name ?? null;

  return (
    <>
      <ol className="relative flex flex-col gap-2 pl-5">
        <span className="absolute left-1.5 top-3 bottom-3 w-[3px] rounded bg-gradient-to-b from-[var(--color-accent)] to-[var(--color-dig)]" />
        {artists.map((artist) => (
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              onPlay={player.playFrom}
              onBypass={onBypass}
              onClipResolved={(mbid, url) => setUrls((prev) => ({ ...prev, [mbid]: url }))}
            />
          </li>
        ))}
      </ol>
      <PlayerBar currentName={currentName} isPlaying={player.isPlaying} onToggle={player.toggle} />
    </>
  );
}
