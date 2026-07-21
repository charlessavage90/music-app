import { Link } from 'react-router-dom';

interface Props {
  error: 'notfound' | 'nopath' | 'unknown';
  onClearExclusions: () => void;
}

export function PathStatus({ error, onClearExclusions }: Props) {
  if (error === 'nopath') {
    return (
      <div className="rounded-lg border border-[var(--color-away)]/40 p-4">
        <p className="mb-3">No path avoiding those artists.</p>
        <button
          type="button"
          onClick={onClearExclusions}
          className="rounded-lg bg-[var(--color-accent)] px-3 py-1.5 text-sm"
        >
          Clear exclusions
        </button>
      </div>
    );
  }
  const message =
    error === 'notfound' ? "Couldn't find that artist." : 'Something went wrong building the path.';
  return (
    <div className="rounded-lg border border-[var(--color-border)] p-4">
      <p className="mb-3">{message}</p>
      <Link to="/" className="text-[var(--color-accent)]">
        Start over
      </Link>
    </div>
  );
}
