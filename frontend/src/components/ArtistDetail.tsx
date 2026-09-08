import { useClip } from '@/hooks/useClip';
import { ArtistInfo } from './ArtistInfo';
import { PlayButton } from './PlayButton';
import { StreamingLinks } from './StreamingLinks';
import type { Artist } from '@/api/types';

interface Props {
  artist: Artist;
  /** 0-based among ALL artists including endpoints; shown 1-based (UXR-D10 currency). */
  index: number;
  total: number;
  isEndpoint: boolean;
  clipIndex: number;
  isPlaying: boolean;
  isCurrent: boolean;
  onPlay: (mbid: string) => void;
  onToggle: () => void;
  onCycleClip: (candidateCount: number) => void;
  onBypass: (mbid: string) => void;
  onClose: () => void;
}

/**
 * Everything about a stop that is not the clip (UXR-D2). Rendered by DetailDock
 * at lg and by DetailSheet below it — one component, two containers (UXR-D3).
 *
 * The facts line (ArtistInfo) and the two links (StreamingLinks) are the LUX-4
 * components unchanged; only their home moved. "Dig deeper" lives here so it
 * cannot be hit by accident on the card (owner decision 2, 2026-09-08).
 */
export function ArtistDetail({
  artist, index, total, isEndpoint, clipIndex, isPlaying, isCurrent,
  onPlay, onToggle, onCycleClip, onBypass, onClose,
}: Props) {
  const clip = useClip(artist.mbid, clipIndex);
  const playable = clip.status === 'ready';
  const candidates = clip.track?.candidateCount ?? 0;

  return (
    <div className="flex flex-col">
      <div className="flex items-center justify-between border-b border-[var(--color-detail-hairline)] px-[18px] py-3.5">
        <span className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-detail-fg)]">
          Stop {index + 1} of {total}
        </span>
        <button
          type="button"
          onClick={onClose}
          aria-label="Close"
          className="flex size-9 items-center justify-center rounded-full border border-[var(--color-detail-border)] text-[14px] text-[var(--color-muted)]"
        >
          <span aria-hidden>✕</span>
        </button>
      </div>

      <div className="flex flex-col gap-[18px] px-[18px] pb-[22px] pt-5">
        <div className="flex items-center gap-3.5">
          <div
            className="size-[86px] flex-none rounded-[14px] bg-[var(--color-border)] bg-cover"
            style={clip.track ? { backgroundImage: `url(${clip.track.coverUrl})` } : undefined}
            aria-hidden
          />
          <div className="min-w-0">
            <div className="font-display text-[26px] font-semibold tracking-[-.03em]">{artist.name}</div>
            {/* L4-D3: renders only what is present, and nothing at all when
                there is nothing to say. The facts line WRAPS and must never
                truncate — it was cut on most real artists at 390px when it did
                (L4-T11). The detail has more width than the card did, which
                makes that easier to honour, not optional. */}
            <ArtistInfo artist={artist} />
          </div>
        </div>

        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-3">
            <PlayButton
              state={isPlaying ? 'pause' : 'play'}
              size="card"
              disabled={!playable}
              // As on the card: the surface that owns the audio toggles it,
              // because onPlay would re-seek to zero.
              onClick={() => (isCurrent ? onToggle() : onPlay(artist.mbid))}
            />
            <span className="min-w-0 truncate text-[13.5px] text-[var(--color-muted)]">
              {clip.status === 'loading' ? '…' : clip.track?.title ?? 'No preview available'}
              {playable && <span className="text-[var(--color-label)]"> · 0:30</span>}
            </span>
          </div>
          {/* LUX-3. One 30-second clip decides whether an unknown artist is
              worth anything to you; if it is unrepresentative the artist is
              rejected and nobody finds out. Absent when there is nothing to
              cycle to — the endpoint states the count and the UI never guesses
              it. Deezer's /top is popularity-ranked, so each press is a
              genuinely less-known track, which reads as "try another" rather
              than as a deep well. */}
          {playable && candidates > 1 && (
            <button
              type="button"
              onClick={() => onCycleClip(candidates)}
              className="self-start text-[12.5px] text-[var(--color-label)] underline-offset-2 hover:text-[var(--color-text)] hover:underline"
            >
              Try another track
            </button>
          )}
        </div>

        {/* Both services always render — a missing id becomes a search link,
            never a missing button (LUX-4 spec §4.1 option A), and that holds
            for an endpoint's detail too. */}
        <StreamingLinks artist={artist} />

        {!isEndpoint && (
          <>
            <div className="h-px bg-[var(--color-detail-hairline)]" />
            <div className="flex flex-col gap-2">
              <div className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">
                Reroute from here
              </div>
              {/* REQ-45: this routes to a MORE OBSCURE similar artist, so no
                  wording here may read as rejecting the artist. No
                  "recommended" either — there is one option, and recommending
                  it against nothing is noise (UXR-D16). */}
              <button
                type="button"
                onClick={() => onBypass(artist.mbid)}
                className="rounded-xl border border-[rgba(245,71,155,.45)] bg-[linear-gradient(130deg,rgba(245,71,155,.14),rgba(143,108,245,.06))] px-4 py-3.5 text-left"
              >
                <span className="block text-[15.5px] font-semibold">Dig deeper</span>
                <span className="mt-1 block text-[13px] leading-[1.45] text-[var(--color-muted)]">
                  Same vibe, less familiar. Rebuilds the whole journey from this point on.
                </span>
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
