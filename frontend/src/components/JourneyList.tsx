import { useEffect, useImperativeHandle, useMemo, useRef, useState, type Ref } from 'react';
import { ArtistCard } from './ArtistCard';
import { PlayerBar } from './PlayerBar';
import { usePlayer } from '@/player/usePlayer';
import { cachedTrack, resolveFreshUrl } from '@/hooks/useClip';
import type { Artist, StopRule } from '@/api/types';

/** What the page can ask of the journey's audio from outside it. */
export interface JourneyControls {
  stop: () => void;
}

interface Props {
  artists: Artist[];
  stopRule: StopRule;
  onBypass: (mbid: string) => void;
  /** MBIDs that were not on the previous path — briefly marked on arrival. */
  changed?: Set<string>;
  ref?: Ref<JourneyControls>;
}

export function JourneyList({ artists, stopRule, onBypass, changed, ref }: Props) {
  // Which artists have a clip — not where it lives. Holding the URL here is what
  // let a tab left open serve a dead signature (C2); the player re-signs on play.
  const [hasClip, setHasClip] = useState<Record<string, boolean>>({});

  const playables = useMemo(
    () => artists.filter((a) => hasClip[a.mbid]).map((a) => ({ mbid: a.mbid })),
    [artists, hasClip],
  );

  // Which clip each card is showing. Per-journey rather than per-card so the
  // player can resolve the SAME track the card is displaying — the card owns
  // the choice, the player owns the audio, and they must not disagree.
  const [clipIndex, setClipIndex] = useState<Record<string, number>>({});

  const player = usePlayer(playables, (mbid) =>
    resolveFreshUrl(mbid, clipIndex[mbid] ?? 0),
  );
  const currentName = artists.find((a) => a.mbid === player.currentMbid)?.name ?? null;
  const currentTrackTitle = player.currentMbid
    ? cachedTrack(player.currentMbid, clipIndex[player.currentMbid] ?? 0)?.title ?? null
    : null;

  function cycleClip(mbid: string, candidateCount: number) {
    // The audio in flight is the OLD track. Restarting it here would race the
    // state update that chooses the new one, so the card falls silent and the
    // user presses play — one press, and unambiguous about what is playing.
    if (player.currentMbid === mbid) player.stop();
    setClipIndex((prev) => ({
      ...prev,
      [mbid]: ((prev[mbid] ?? 0) + 1) % candidateCount,
    }));
  }

  // A cycled index that resolved to nothing must not strand the card: track 1
  // is the one index every card that ever showed "Try another track" has
  // already proven has a clip, so it is always safe to fall back to.
  function resetDeadIndex(mbid: string) {
    setClipIndex((prev) => (prev[mbid] ? { ...prev, [mbid]: 0 } : prev));
  }

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
      {/* The rail spans the full height of the journey, and there is no arrow
          at its foot — both at the owner's request, 2026-07-28. */}
      <ol className="relative flex flex-col gap-3.5 pl-[19px]">
        <span className="absolute left-0 inset-y-0 w-[3px] rounded-full bg-gradient-to-b from-[var(--color-accent)] via-[var(--color-rail-mid)] to-[var(--color-dig)]" />
        {artists.map((artist, i) => (
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              isCurrent={player.currentMbid === artist.mbid}
              // The two artists you chose are the journey's endpoints; the
              // bypass control does not apply to them — there is nothing to
              // reroute for an artist who IS one end of the journey.
              isEndpoint={i === 0 || i === artists.length - 1}
              endpointLabel={
                i === 0 ? 'start' : i === artists.length - 1 ? 'destination' : undefined
              }
              isNew={changed?.has(artist.mbid) ?? false}
              onPlay={player.playFrom}
              onToggle={player.toggle}
              onBypass={onBypass}
              onClipResolved={(mbid, available) =>
                setHasClip((prev) => ({ ...prev, [mbid]: available }))
              }
              clipIndex={clipIndex[artist.mbid] ?? 0}
              onCycleClip={(count) => cycleClip(artist.mbid, count)}
              onDeadIndex={resetDeadIndex}
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
      <PlayerBar
        currentName={currentName}
        trackTitle={currentTrackTitle}
        isPlaying={player.isPlaying}
        position={player.position}
        duration={player.duration}
        stopIndex={artists.findIndex((a) => a.mbid === player.currentMbid)}
        stopCount={artists.length}
        onToggle={player.toggle}
      />
    </>
  );
}
