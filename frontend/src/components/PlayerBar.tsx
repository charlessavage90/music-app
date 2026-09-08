import { PlayButton } from './PlayButton';

interface Props {
  currentName: string | null;
  trackTitle: string | null;
  isPlaying: boolean;
  /** Seconds, from the audio element's own clock — never estimated. */
  position: number;
  duration: number;
  /** 0-based position among ALL artists including endpoints (UXR-D10). -1 when none. */
  stopIndex: number;
  stopCount: number;
  onToggle: () => void;
}

function mmss(s: number): string {
  const whole = Math.max(0, Math.floor(s));
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, '0')}`;
}

/**
 * The bottom bar: what is playing, how far through, and which stop it is.
 *
 * "Stop N of M" is the WHOLE-JOURNEY currency — every artist including both
 * endpoints — which is not the "steps" the heading counts (artists between).
 * Named here because reading one count as another is a defect class this
 * project has met three times.
 */
export function PlayerBar({ currentName, trackTitle, isPlaying, position, duration, stopIndex, stopCount, onToggle }: Props) {
  if (!currentName) return null;
  const pct = duration > 0 ? Math.min(100, Math.round((position / duration) * 100)) : 0;
  return (
    <div className="fixed inset-x-0 bottom-0 border-t border-[var(--color-bar-border)] bg-[var(--color-bar)] px-5 pt-3.5 pb-[calc(1.25rem+env(safe-area-inset-bottom))]">
      <div className="mx-auto flex w-full max-w-[1200px] items-center gap-4">
        <PlayButton state={isPlaying ? 'pause' : 'play'} size="bar" onClick={onToggle} />
        <div className="min-w-0 flex-1">
          <div className="truncate text-[14px] font-semibold">
            {currentName}
            {trackTitle && <span className="font-normal text-[var(--color-label)]"> — {trackTitle}</span>}
          </div>
          <div className="mt-2 flex items-center gap-2.5">
            <span className="text-[11.5px] text-[var(--color-label)]">{mmss(position)}</span>
            <div
              role="progressbar"
              aria-label="Clip progress"
              aria-valuemin={0}
              aria-valuemax={100}
              aria-valuenow={pct}
              className="relative h-[3px] flex-1 rounded-full bg-[var(--color-border)]"
            >
              <span
                className="absolute inset-y-0 left-0 rounded-full bg-gradient-to-r from-[var(--color-start)] to-[var(--color-playing)]"
                style={{ width: `${pct}%` }}
              />
            </div>
            <span className="text-[11.5px] text-[var(--color-label)]">{mmss(duration)}</span>
          </div>
        </div>
        {stopIndex >= 0 && (
          <span className="hidden flex-none rounded-full border border-[var(--color-border-strong)] px-3.5 py-2 text-[12.5px] text-[var(--color-muted)] sm:inline">
            Stop {stopIndex + 1} of {stopCount}
          </span>
        )}
      </div>
    </div>
  );
}
