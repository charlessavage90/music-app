interface Props {
  /** Whose clip — so eight Retry buttons are eight names (G3-F4). */
  name: string;
  onRetry: () => void;
}

/**
 * Asks again about a clip that failed for a transient reason (G3-F11). Shared
 * by the card and the detail so the two cannot word it differently.
 */
export function ClipRetry({ name, onRetry }: Props) {
  return (
    <button
      type="button"
      onClick={onRetry}
      aria-label={`Retry preview for ${name}`}
      className="flex-none cursor-pointer text-[var(--color-muted)] underline underline-offset-2 hover:text-[var(--color-text)]"
    >
      Retry
    </button>
  );
}
