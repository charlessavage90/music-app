import { useEffect, useState } from 'react';
import * as client from '@/api/client';

/**
 * "58,000 artists mapped by who listens to whom" — live, from /api/meta (UXR-D8).
 *
 * Floored to the nearest thousand: the exact count changes with every rebuild and
 * is a fact about the artifact, not a promise to the visitor. Renders NOTHING on
 * any failure (UI-7): this is decoration, and a decoration must not be able to
 * turn a working landing page into an error.
 */
export function ArtistCountBadge() {
  const [count, setCount] = useState<number | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    client.getMeta(controller.signal)
      .then((m) => setCount(m.artists))
      .catch(() => setCount(null));
    return () => controller.abort();
  }, []);

  if (count === null || count < 1000) return null;
  const floored = Math.floor(count / 1000) * 1000;
  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-[var(--color-border-strong)] bg-[var(--color-surface)] px-3.5 py-1.5 text-[12.5px] text-[var(--color-muted)]">
      <span aria-hidden className="size-1.5 rounded-full bg-[var(--color-start)] [animation:ap-pulse_1.8s_ease-in-out_infinite]" />
      {floored.toLocaleString('en-US')} artists mapped by who listens to whom
    </div>
  );
}
