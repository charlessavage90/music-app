import { Link } from 'react-router-dom';

interface Props {
  error: 'notfound' | 'nopath' | 'timeout' | 'unknown';
  onClearExclusions: () => void;
  onRetry: () => void;
}

export function PathStatus({ error, onClearExclusions, onRetry }: Props) {
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
  // The only error with a useful response, so it is the only one offering an
  // action rather than a way out.
  if (error === 'timeout') {
    return (
      <div className="rounded-lg border border-[var(--color-border)] p-4">
        <p className="mb-3">That took too long. The server may still be waking up.</p>
        <button
          type="button"
          onClick={onRetry}
          className="rounded-lg bg-[var(--color-accent)] px-3 py-1.5 text-sm"
        >
          Try again
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
