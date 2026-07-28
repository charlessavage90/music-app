import { PlayButton } from './PlayButton';

interface Props {
  currentName: string | null;
  isPlaying: boolean;
  onToggle: () => void;
}

export function PlayerBar({ currentName, isPlaying, onToggle }: Props) {
  if (!currentName) return null;
  return (
    <div className="fixed bottom-0 inset-x-0 border-t border-[var(--color-border)] bg-[var(--color-surface)] px-5 pt-3.5 pb-[calc(1.875rem+env(safe-area-inset-bottom))]">
      <div className="mx-auto flex w-full max-w-[620px] items-center gap-3.5">
        <PlayButton
          state={isPlaying ? 'pause' : 'play'}
          size="bar"
          onClick={onToggle}
        />
        <span className="min-w-0 truncate text-[13px] sm:text-[13.5px] text-[var(--color-muted)]">
          {currentName}
        </span>
      </div>
    </div>
  );
}
