import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import type { PathError } from '@/hooks/usePath';

interface Props {
  error: PathError;
  /** The server's own words, for `invalid` (issue #193). */
  message?: string;
  /** The server's cap on exclusions, for `toomany`. */
  limit?: number;
  onClearExclusions: () => void;
  onRetry: () => void;
}

/**
 * Dark text on the accent, as "Find path" does (LandingPage.tsx). The light
 * body text these buttons used to inherit computes to 1.80:1 on #2ec5ee, below
 * WCAG AA's 4.5:1 (issue #189); --color-bg on --color-accent is 9.85:1. A test
 * pins the pairing, because jsdom cannot compute a contrast ratio.
 */
const ACTION =
  'rounded-lg bg-[var(--color-accent)] px-3 py-1.5 text-sm font-semibold text-[var(--color-bg)]';

/**
 * role="alert" so a screen reader hears the failure when it replaces the path
 * (issue #188): this box is mounted fresh on every error, which is the moment
 * an alert is announced, and nothing else on the page changes to signal it.
 */
function Box({ tone = 'neutral', children }: { tone?: 'neutral' | 'away'; children: ReactNode }) {
  const border =
    tone === 'away' ? 'border-[var(--color-away)]/40' : 'border-[var(--color-border)]';
  return (
    <div role="alert" className={`rounded-lg border ${border} p-4`}>
      {children}
    </div>
  );
}

function StartOver() {
  return (
    <Link to="/" className="text-[var(--color-accent)]">
      Start over
    </Link>
  );
}

/** FastAPI's messages are written lower-case, as fragments; this is a sentence. */
function sentence(s: string): string {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

export function PathStatus({ error, message, limit, onClearExclusions, onRetry }: Props) {
  if (error === 'nopath') {
    return (
      <Box tone="away">
        <p className="mb-3">No path avoiding those artists.</p>
        <button type="button" onClick={onClearExclusions} className={ACTION}>
          Clear exclusions
        </button>
      </Box>
    );
  }
  // The 201st skip. Back is the real answer — the 200th is one step behind —
  // so the text says so; the button is for someone who wants a clean slate.
  if (error === 'toomany') {
    return (
      <Box tone="away">
        <p className="mb-3">
          That&rsquo;s more skips than one journey can hold{limit ? ` (${limit})` : ''}. Press
          Back to return to your last path, or clear them and start again.
        </p>
        <button type="button" onClick={onClearExclusions} className={ACTION}>
          Clear exclusions
        </button>
      </Box>
    );
  }
  // The only error with a useful response, so it is the only one offering an
  // action rather than a way out.
  if (error === 'timeout') {
    return (
      <Box>
        <p className="mb-3">That took too long. The server may still be waking up.</p>
        <button type="button" onClick={onRetry} className={ACTION}>
          Try again
        </button>
      </Box>
    );
  }
  const text =
    error === 'notfound'
      ? "Couldn't find that artist."
      : error === 'invalid' && message
        ? sentence(message)
        : 'Something went wrong building the path.';
  return (
    <Box>
      <p className="mb-3">{text}</p>
      <StartOver />
    </Box>
  );
}
