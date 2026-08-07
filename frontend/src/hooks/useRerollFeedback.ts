import { useEffect, useRef, useState } from 'react';
import type { Artist } from '@/api/types';
import type { RerollReason } from '@/components/RerollNotice';

/**
 * How long the reroll message stays up, even when the answer beat it there.
 *
 * The message is specific per signal (UI-D5) and always has been — but it was
 * bound to the request's lifetime, so a rebuild that answered in 80 ms showed
 * good writing for 80 ms. The owner reported exactly this on 2026-08-02 about
 * the first-load screen ("often too fast to see") and again on 2026-08-07 about
 * the rebuild. This is a floor on READING TIME, not a fake delay: the path
 * underneath has already arrived and is on screen behind it.
 */
export const NOTICE_MIN_MS = 500;

/** How long a newly-arrived artist stays marked once the notice clears. */
export const GLOW_MS = 800;

export interface RerollFeedback {
  /** The signal being acted on, or null. Drives both the notice and the dim. */
  notice: RerollReason | null;
  /** MBIDs on the new path that were not on the previous one. */
  changed: Set<string>;
  /** Call at the moment of the press, before the request is even issued. */
  begin: (reason: RerollReason) => void;
}

const EMPTY: Set<string> = new Set();

/**
 * Confirmation that does not depend on how fast the server answered.
 *
 * Two halves, deliberately on different clocks. The notice is held for a
 * readable minimum; the glow fires afterwards and costs nothing, because by
 * then the path is already rendered. A fast rebuild and a slow one produce the
 * same sequence — which is the point, since the fast one is the broken case.
 */
export function useRerollFeedback(
  status: 'loading' | 'ready' | 'error',
  artists: Artist[],
): RerollFeedback {
  const [notice, setNotice] = useState<RerollReason | null>(null);
  const [changed, setChanged] = useState<Set<string>>(EMPTY);
  const startedAt = useRef(0);
  // null until the FIRST path lands. A first load has nothing to diff against,
  // and marking every artist as new there would be both wrong and a strobe.
  const seen = useRef<Set<string> | null>(null);

  // Computed when the path lands, revealed when the message clears.
  const pending = useRef<Set<string>>(EMPTY);

  const key = artists.map((a) => a.mbid).join('|');

  // WHAT changed. Must be declared before the effect below: both run after the
  // same render when a path lands, in declaration order, and that one reads
  // what this one stores.
  useEffect(() => {
    if (status !== 'ready' || artists.length === 0) return;
    const next = new Set(artists.map((a) => a.mbid));
    const before = seen.current;
    seen.current = next;
    // A first load has nothing to differ from.
    if (!before) return;

    const diff = new Set([...next].filter((m) => !before.has(m)));
    if (diff.size === 0) return;
    // No press behind this one — Back undoing a bypass, say. Nothing is holding
    // a message, so the mark is the whole confirmation and fires at once.
    if (startedAt.current === 0) setChanged(diff);
    else pending.current = diff;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [status, key]);

  // HOW LONG the message stays. Deliberately independent of whether the path
  // changed at all: keying this on the artist list stranded the notice forever
  // when a rebuild returned an identical path, because then nothing it depended
  // on ever changed again.
  useEffect(() => {
    if (notice === null) return;
    if (status === 'error') {
      startedAt.current = 0;
      pending.current = EMPTY;
      setNotice(null);
      return;
    }
    if (status === 'loading') return;

    const wait = Math.max(0, startedAt.current + NOTICE_MIN_MS - Date.now());
    const timer = setTimeout(() => {
      startedAt.current = 0;
      setNotice(null);
      if (pending.current.size > 0) {
        setChanged(pending.current);
        pending.current = EMPTY;
      }
    }, wait);
    return () => clearTimeout(timer);
  }, [status, notice]);

  useEffect(() => {
    if (changed.size === 0) return;
    const timer = setTimeout(() => setChanged(EMPTY), GLOW_MS);
    return () => clearTimeout(timer);
  }, [changed]);

  return {
    notice,
    changed,
    begin: (reason) => {
      startedAt.current = Date.now();
      setNotice(reason);
    },
  };
}
