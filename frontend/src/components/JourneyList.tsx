import { useEffect, useMemo, useRef, useState } from 'react';
import { ArtistCard } from './ArtistCard';
import { PlayerBar } from './PlayerBar';
import { usePlayer } from '@/player/usePlayer';
import { resolveFreshUrl } from '@/hooks/useClip';
import type { Artist, BypassReason } from '@/api/types';

interface Props {
  artists: Artist[];
  onBypass: (mbid: string, reason: BypassReason) => void;
}

export function JourneyList({ artists, onBypass }: Props) {
  // Which artists have a clip — not where it lives. Holding the URL here is what
  // let a tab left open serve a dead signature (C2); the player re-signs on play.
  const [hasClip, setHasClip] = useState<Record<string, boolean>>({});

  const playables = useMemo(
    () => artists.filter((a) => hasClip[a.mbid]).map((a) => ({ mbid: a.mbid })),
    [artists, hasClip],
  );

  const player = usePlayer(playables, resolveFreshUrl);
  const currentName = artists.find((a) => a.mbid === player.currentMbid)?.name ?? null;

  // Silence the previous path the moment a new one arrives — otherwise a clip
  // from an artist who is no longer on the journey keeps playing over it.
  const pathKey = artists.map((a) => a.mbid).join('|');
  const stopRef = useRef(player.stop);
  stopRef.current = player.stop;
  useEffect(() => {
    stopRef.current();
  }, [pathKey]);

  return (
    <>
      <ol className="relative flex flex-col gap-2 pl-5">
        <span className="absolute left-1.5 top-3 bottom-3 w-[3px] rounded bg-gradient-to-b from-[var(--color-accent)] to-[var(--color-dig)]" />
        {artists.map((artist, i) => (
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              isCurrent={player.currentMbid === artist.mbid}
              // The two artists you chose are the journey's endpoints; there is
              // nothing to reroute if you reject them.
              isEndpoint={i === 0 || i === artists.length - 1}
              onPlay={player.playFrom}
              onToggle={player.toggle}
              onBypass={onBypass}
              onClipResolved={(mbid, available) =>
                setHasClip((prev) => ({ ...prev, [mbid]: available }))
              }
            />
          </li>
        ))}
      </ol>
      <PlayerBar currentName={currentName} isPlaying={player.isPlaying} onToggle={player.toggle} />
    </>
  );
}
