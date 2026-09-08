import { useEffect, useImperativeHandle, useLayoutEffect, useMemo, useRef, useState, type Ref } from 'react';
import { ArtistCard } from './ArtistCard';
import { ArtistDetail } from './ArtistDetail';
import { DetailDock } from './DetailDock';
import { DetailSheet } from './DetailSheet';
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

  // Whose detail is open (UXR-D3). Component state, never URL state: the URL is
  // the shareable journey, and which panel was open is not part of one.
  // UXR-T7 renders the detail from this; UXR-T6 only records the press.
  const [selected, setSelected] = useState<string | null>(null);

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
    // The artist whose detail is open may not be on the new path at all
    // (UXR-D3). Closing is the only answer that is right either way.
    setSelected(null);
  }, [pathKey]);

  // Where the rail starts and stops: the first dot's centre and the last
  // dot's centre, measured rather than assumed.
  //
  // It was a fixed 41px inset at both ends until 2026-09-08, and a fixed inset
  // CANNOT be right — the two endpoint cards carry an eyebrow the interior
  // cards do not, so they are taller, by an amount that changes with width and
  // with whether the eyebrow wraps. Measured in a browser, 41px overshot by
  // 7.5px at each end at 1280, and at 390 it was lopsided: 3.25px past the top
  // dot and 10.75px past the bottom one.
  //
  // Null until measured, and null wherever nothing can measure (jsdom has no
  // layout, and ResizeObserver may be absent) — the rail then spans the list,
  // which is what it did before and is never worse than a wrong inset.
  const listRef = useRef<HTMLOListElement>(null);
  const [railInset, setRailInset] = useState<{ top: number; bottom: number } | null>(null);

  useLayoutEffect(() => {
    const ol = listRef.current;
    if (!ol) return;

    function measure() {
      if (!ol) return;
      const dots = ol.querySelectorAll<HTMLElement>('[data-rail-dot]');
      if (dots.length < 2) return setRailInset(null);
      const box = ol.getBoundingClientRect();
      const first = dots[0].getBoundingClientRect();
      const last = dots[dots.length - 1].getBoundingClientRect();
      // A layout-less environment reports zeros; that is the null case, not an
      // inset of zero, which would draw a full-height rail claiming precision.
      if (box.height === 0) return setRailInset(null);
      const next = {
        top: first.top + first.height / 2 - box.top,
        bottom: box.bottom - (last.top + last.height / 2),
      };
      setRailInset((prev) =>
        prev && prev.top === next.top && prev.bottom === next.bottom ? prev : next,
      );
    }

    measure();
    if (typeof ResizeObserver === 'undefined') return;
    // Card heights move with width, with the eyebrow wrapping, and with the
    // display face finishing loading — all after the first paint.
    const ro = new ResizeObserver(measure);
    ro.observe(ol);
    return () => ro.disconnect();
  }, [pathKey]);

  // The controls that leave or rebuild a path live on the page, not on a card, and
  // waiting for the rebuild to silence the audio reads as a lag rather than as a
  // response to the press. So the page can stop it the moment a button is pressed.
  useImperativeHandle(ref, () => ({ stop: () => stopRef.current() }), []);

  // One element, two containers (UXR-D3): the dock at lg, the sheet below it.
  // Built once here so the two cannot drift apart.
  const selectedIndex = artists.findIndex((a) => a.mbid === selected);
  const detail = selectedIndex >= 0 && (
    <ArtistDetail
      artist={artists[selectedIndex]}
      index={selectedIndex}
      total={artists.length}
      isEndpoint={selectedIndex === 0 || selectedIndex === artists.length - 1}
      clipIndex={clipIndex[artists[selectedIndex].mbid] ?? 0}
      isPlaying={player.currentMbid === selected && player.isPlaying}
      isCurrent={player.currentMbid === selected}
      onPlay={player.playFrom}
      onToggle={player.toggle}
      onCycleClip={(count) => cycleClip(artists[selectedIndex].mbid, count)}
      onBypass={onBypass}
      onClose={() => setSelected(null)}
    />
  );

  return (
    <>
      <div className="lg:grid lg:grid-cols-[1fr_400px] lg:items-start lg:gap-10">
      {/* Still no arrow at its foot — the owner's request, 2026-07-28. What
          changed on 2026-09-08 is where it starts and stops: the cards now
          carry a dot each, so the rail runs dot to dot rather than the full
          height of the list, as the approved mockup draws it.
          `left-2px` with `w-3px` centres it 3.5px from this list's left edge —
          the same centre the dots use; see the geometry note in ArtistCard. */}
      <ol ref={listRef} className="relative flex flex-col gap-3.5 pl-[26px]">
        <span
          aria-hidden
          className="absolute left-[2px] w-[3px] rounded-full bg-gradient-to-b from-[var(--color-start)] via-[var(--color-playing)] to-[var(--color-end)]"
          style={railInset ? { top: railInset.top, bottom: railInset.bottom } : { top: 0, bottom: 0 }}
        />
        {artists.map((artist, i) => (
          <li key={artist.mbid}>
            <ArtistCard
              artist={artist}
              // Among ALL artists including the two you chose (UXR-D10's
              // currency, not UXR-D6's "steps"): it colours the rail dot.
              index={i}
              total={artists.length}
              isPlaying={player.currentMbid === artist.mbid && player.isPlaying}
              isCurrent={player.currentMbid === artist.mbid}
              // Drives the eyebrow and the frame. The bypass is still
              // interior-only — there is nothing to reroute for an artist who
              // IS one end of the journey — but that gate moved to the detail
              // below, which computes it from the same two indices.
              isEndpoint={i === 0 || i === artists.length - 1}
              endpointLabel={
                i === 0 ? 'start' : i === artists.length - 1 ? 'destination' : undefined
              }
              isNew={changed?.has(artist.mbid) ?? false}
              isSelected={selected === artist.mbid}
              onPlay={player.playFrom}
              onToggle={player.toggle}
              onDetail={() => setSelected(artist.mbid)}
              onClipResolved={(mbid, available) =>
                setHasClip((prev) => ({ ...prev, [mbid]: available }))
              }
              clipIndex={clipIndex[artist.mbid] ?? 0}
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
        <DetailDock>
          {detail || (
            <p className="px-[18px] py-5 text-[13.5px] text-[var(--color-muted)]">
              Open any artist with &rsaquo; for where to hear more, and to dig deeper from there.
            </p>
          )}
        </DetailDock>
      </div>
      <DetailSheet open={!!detail} onClose={() => setSelected(null)}>{detail}</DetailSheet>
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
