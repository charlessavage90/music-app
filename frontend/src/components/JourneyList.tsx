import { useEffect, useImperativeHandle, useMemo, useRef, useState, type Ref } from 'react';
import { ArtistCard } from './ArtistCard';
import { PlayerBar } from './PlayerBar';
import { usePlayer } from '@/player/usePlayer';
import { resolveFreshUrl } from '@/hooks/useClip';
import type { Artist, BypassReason, StopRule } from '@/api/types';

/** What the page can ask of the journey's audio from outside it. */
export interface JourneyControls {
  stop: () => void;
}

interface Props {
  artists: Artist[];
  stopRule: StopRule;
  onBypass: (mbid: string, reason: BypassReason) => void;
  ref?: Ref<JourneyControls>;
}

export function JourneyList({ artists, stopRule, onBypass, ref }: Props) {
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

  // The controls that leave or rebuild a path live on the page, not on a card, and
  // waiting for the rebuild to silence the audio reads as a lag rather than as a
  // response to the press. So the page can stop it the moment a button is pressed.
  useImperativeHandle(ref, () => ({ stop: () => stopRef.current() }), []);

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
            {/* Some pairs cannot be given a stop: one of the two holds a single
                connection in the graph, and it is to the other. Saying so beats
                a page with two cards and nothing to press. */}
            {stopRule === 'adjacent_only' && i === 0 && (
              <p className="px-1 py-3 text-sm text-[var(--color-muted)]">
                These two are next to each other — there&rsquo;s no artist in between.
              </p>
            )}
          </li>
        ))}
      </ol>
      <PlayerBar currentName={currentName} isPlaying={player.isPlaying} onToggle={player.toggle} />
    </>
  );
}
