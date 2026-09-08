import { useEffect } from 'react';
import { useClip } from '@/hooks/useClip';
import { PlayButton } from './PlayButton';
import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
  /** 0-based position among ALL artists including endpoints; drives the rail dot's colour. */
  index: number;
  total: number;
  isPlaying: boolean;
  /** This card owns the audio, playing or paused — so its button toggles. */
  isCurrent?: boolean;
  /**
   * One of the two artists you chose. Since 2026-09-08 it drives the eyebrow
   * and the card's frame only — the bypass control it used to gate is in
   * ArtistDetail, which decides interior-only for itself.
   */
  isEndpoint?: boolean;
  /** Which end, when this is an endpoint. Drives the eyebrow label. */
  endpointLabel?: 'start' | 'destination';
  /**
   * This artist was not on the previous path. Marked briefly on arrival, which
   * is the confirmation that survives a rebuild answering faster than the eye.
   */
  isNew?: boolean;
  /** Its detail is the open one (UXR-D3). */
  isSelected?: boolean;
  onPlay: (mbid: string) => void;
  onToggle?: () => void;
  /** Open this artist's detail. Selection is JourneyList's, never the URL's. */
  onDetail: () => void;
  /**
   * Reports whether this artist has a clip at all — never its URL. The URL is
   * signed and short-lived, so the player asks for one at the moment of play (C2).
   */
  onClipResolved?: (mbid: string, hasClip: boolean) => void;
  /** Which of this artist's candidate clips to show. Owned by JourneyList. */
  clipIndex?: number;
  /**
   * A CYCLED index (clipIndex > 0) resolved to no clip at all — the candidate
   * the card was showing dropped out from under it (the catalogue briefly
   * refused us, or it lost the track). Without this the card is stranded: no
   * track plays, and with candidateCount now 0 (a 204 carries no body, so the
   * count that would size the control is gone with it) "Try another track"
   * has nothing to render, leaving no way back to track 1 short of a reload.
   * Never fires for a card that simply has no clip at index 0 — that is a
   * normal silent card, not a dead index.
   *
   * The control that cycles moved to ArtistDetail on 2026-09-08; this stayed,
   * because the card is what renders the clip and so what can see it die.
   */
  onDeadIndex?: (mbid: string) => void;
}

/** Cyan at the start, pink at the end, violet-ish between — the rail's own gradient, per stop. */
function dotColour(index: number, total: number): string {
  if (index === 0) return 'var(--color-start)';
  if (index === total - 1) return 'var(--color-end)';
  return 'var(--color-playing)';
}

/**
 * One stop on the journey — the LISTENING surface only (UXR-D2).
 *
 * Cover, name, track, play, and a button to the detail. The facts line, the
 * streaming links, "Try another track" and "Dig deeper" all moved to
 * ArtistDetail on 2026-09-08; the card is what you press to hear, the detail is
 * where you go once you have.
 */
export function ArtistCard({
  artist, index, total, isPlaying, isCurrent, isEndpoint, endpointLabel, isNew, isSelected,
  onPlay, onToggle, onDetail, onClipResolved, clipIndex, onDeadIndex,
}: Props) {
  const clip = useClip(artist.mbid, clipIndex ?? 0);
  const playable = clip.status === 'ready';
  const silent = clip.status === 'none';

  useEffect(() => {
    if (clip.status === 'loading') return;
    onClipResolved?.(artist.mbid, playable);
    if (!playable && (clipIndex ?? 0) > 0) onDeadIndex?.(artist.mbid);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [clip.status]);

  const frame = isSelected
    ? 'border-[1.5px] border-[var(--color-detail)] bg-[#12141d] shadow-[0_0_0_4px_rgba(79,127,224,.1)]'
    : isPlaying
      ? 'border border-[rgba(143,108,245,.45)] bg-[linear-gradient(120deg,rgba(143,108,245,.16),rgba(46,197,238,.07))]'
      : isEndpoint
        ? 'border border-[var(--color-border-hover)] bg-[var(--color-surface-raised)]'
        : 'border border-[var(--color-border)] bg-[var(--color-surface)] hover:border-[var(--color-border-hover)]';

  return (
    <div className="relative">
      {/* The rail dot for this stop, and the anchor JourneyList measures to
          decide where its rail starts and stops (`data-rail-dot`).

          GEOMETRY, and the two halves must stay in sync: the list pads its
          content by 26px, so -29px here puts this dot's centre 3.5px from the
          list's own left edge. The rail is 3px wide at left-2px, which is the
          same 3.5px centre. Changing either number alone leaves the dots
          sitting beside the line — which is what happened, by exactly 3px,
          until it was measured in a browser on 2026-09-08. */}
      <span
        aria-hidden
        data-rail-dot
        className="absolute -left-[29px] top-1/2 size-[13px] -translate-y-1/2 rounded-full border-[3px] bg-[var(--color-bg)]"
        style={{ borderColor: isSelected ? 'var(--color-detail)' : dotColour(index, total) }}
      />
      {/* Fades from an accent ring to nothing over GLOW_MS. The card is not
          re-mounted between paths when the artist survives, so the isNew class
          arriving IS the animation trigger. */}
      <div
        className={`flex items-center gap-3 rounded-2xl px-3.5 py-3 sm:gap-4 sm:px-[18px] sm:py-3.5 ${frame} ${
          isNew ? '[animation:ap-glow_800ms_ease-out]' : ''
        }`}
      >
        <div
          className={`size-12 flex-none rounded-[10px] bg-[var(--color-border)] bg-cover sm:size-[54px] ${
            silent ? 'opacity-75' : ''
          }`}
          style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
          aria-hidden
        />
        <div className="min-w-0 flex-1">
          {endpointLabel && (
            <div
              className="text-[10px] font-bold uppercase tracking-[.16em]"
              style={{ color: endpointLabel === 'start' ? 'var(--color-start)' : 'var(--color-end)' }}
            >
              {endpointLabel === 'start' ? 'You started here' : 'You were heading here'}
            </div>
          )}
          <div className="flex items-center gap-2.5">
            {/* UI-5: data-testid, not a style class — e2e/responsive.spec.ts
                measures this element and must not depend on its typography. */}
            <div
              data-testid="artist-name"
              className="truncate font-display text-[16.5px] font-semibold tracking-[-.02em] sm:text-[19px]"
            >
              {artist.name}
            </div>
            {/* Was the words "▮▮▮ now playing" until 2026-09-08. The equaliser
                says it in the space a truncating name needs back, and keeps the
                accessible name for anything that cannot see it move. */}
            {isPlaying && (
              <span className="flex h-[13px] flex-none items-end gap-0.5" aria-label="now playing" role="img">
                {[0, 0.15, 0.3].map((delay) => (
                  <span
                    key={delay}
                    className="motion-safe-only block h-full w-[3px] origin-bottom rounded-[1px] bg-[var(--color-playing)] [animation:un-eq_.9s_ease-in-out_infinite]"
                    style={{ animationDelay: `${delay}s` }}
                  />
                ))}
              </span>
            )}
          </div>
          {/* The duration sits in its own non-shrinking span so a long title
              truncates and "0:30" survives — the reverse would drop the one
              fact this line was changed to carry. Only shown when there IS
              something to play; "No preview available" must not claim 30
              seconds of it. Bare "0:30" rather than "0:30 sample" at the
              owner's request 2026-08-07: seven characters back for the title,
              which truncates hard at 390px. */}
          <div className="mt-1 flex items-baseline gap-1.5 text-[12.5px] sm:text-[13px]">
            <span
              className={`truncate ${silent ? 'text-[var(--color-label)]' : 'text-[var(--color-muted)]'}`}
            >
              {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
            </span>
            {playable && <span className="flex-none text-[var(--color-label)]">· 0:30</span>}
          </div>
        </div>
        {/* The way to everything this card no longer carries. Present on every
            stop including the two you chose: the links and the facts are worth
            reaching there too (LUX-4), and only "Dig deeper" is interior-only. */}
        <button
          type="button"
          onClick={onDetail}
          aria-label={`About ${artist.name}`}
          aria-expanded={isSelected ?? false}
          className={`flex size-11 flex-none items-center justify-center rounded-full border text-[15px] sm:size-[46px] ${
            isSelected
              ? 'border-[var(--color-detail)] bg-[rgba(79,127,224,.16)] text-[var(--color-text)]'
              : 'border-[var(--color-border-strong)] text-[var(--color-muted)] hover:text-[var(--color-text)]'
          }`}
        >
          <span aria-hidden>›</span>
        </button>
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
