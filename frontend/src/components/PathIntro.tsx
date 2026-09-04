import { useState } from 'react';
import type { StopRule } from '@/api/types';

const DISMISSED_KEY = 'artistpath:bypass-explainer-dismissed';

function wasDismissed(): boolean {
  try {
    return localStorage.getItem(DISMISSED_KEY) === '1';
  } catch {
    // Private browsing and blocked storage both throw. Showing the explainer
    // is the safe failure — it is help text, not state.
    return false;
  }
}

interface Props {
  /** Artists BETWEEN the two chosen ones — what is visible on screen (UI-D7). */
  count: number;
  stopRule: StopRule;
}

/**
 * The result line and the bypass explainer.
 *
 * The result line is permanent; the explainer is onboarding, so it opens on a
 * first visit and stays closed once dismissed (UI-D6). Both stand down when the
 * two artists are adjacent: there is no count to state, no bypass control to
 * explain, and JourneyList already says the useful thing.
 */
export function PathIntro({ count, stopRule }: Props) {
  const [open, setOpen] = useState(() => !wasDismissed());

  if (stopRule === 'adjacent_only') return null;

  function dismiss() {
    setOpen(false);
    try {
      localStorage.setItem(DISMISSED_KEY, '1');
    } catch {
      // Nothing to do — the explainer simply reopens next time.
    }
  }

  return (
    <div className="mb-5">
      <p className="text-[13.5px] text-[var(--color-muted)]">
        We found a path between these artists in{' '}
        <span className="text-[var(--color-text)]">
          {count} step{count === 1 ? '' : 's'}
        </span>
        .
      </p>

      <button
        type="button"
        onClick={() => (open ? setOpen(false) : setOpen(true))}
        aria-expanded={open}
        className="mt-2 text-[12.5px] text-[var(--color-accent)] hover:underline"
      >
        {open ? '▾' : '▸'} How do I change the path?
      </button>

      {open && (
        <div className="mt-2.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-4 text-[12.5px] leading-[1.55] text-[var(--color-muted)]">
          <p>
            Any artist in the middle has a{' '}
            <span className="text-[var(--color-text)]">Dig deeper</span> control along the
            bottom of their card.
          </p>
          <p className="mt-2">
            Press it and that artist is replaced by someone with a similar sound who is less
            well known — you have already covered the obvious route.
          </p>
          <p className="mt-2 text-[var(--color-text)]">
            It rebuilds the whole journey, so every artist between your two can change — not
            just the one you pressed.
          </p>
          <button
            type="button"
            onClick={dismiss}
            className="mt-3.5 rounded-full border border-[var(--color-border)] px-4 py-1.5 text-[12.5px] text-[var(--color-text)] hover:border-[var(--color-border-hover)]"
          >
            Got it
          </button>
        </div>
      )}
    </div>
  );
}
