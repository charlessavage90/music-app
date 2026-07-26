interface Props {
  currentName: string | null;
  isPlaying: boolean;
  onToggle: () => void;
}

export function PlayerBar({ currentName, isPlaying, onToggle }: Props) {
  if (!currentName) return null;
  return (
    <div className="fixed bottom-0 inset-x-0 border-t border-[var(--color-border)] bg-[var(--color-surface)] px-4 pt-3 pb-[calc(0.75rem+env(safe-area-inset-bottom))] flex items-center gap-3">
      <button
        type="button"
        aria-label={isPlaying ? 'Pause' : 'Play'}
        onClick={onToggle}
        className="w-9 h-9 rounded-full bg-[var(--color-accent)] text-white flex items-center justify-center"
      >
        {isPlaying ? '❚❚' : '▶'}
      </button>
      <span className="text-sm text-[var(--color-muted)]">{currentName}</span>
    </div>
  );
}
