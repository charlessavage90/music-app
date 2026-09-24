import type { LinkDamage } from '@/lib/exclusions';

/**
 * Said when a shared link arrived with fewer skipped artists than it was
 * written with (issue #187). The journey below is still shown — it is a real
 * path between the same two artists — but it is not the one that was sent,
 * and before this nothing on the page could tell you so.
 *
 * Goes away by itself: the next press rewrites the link with a fresh count,
 * and "Reset path" removes it.
 */
export function LinkDamageNotice({ damage }: { damage: LinkDamage }) {
  const detail =
    damage.expected === null
      ? 'Some of the artists skipped in it may be missing'
      : `It was shared with ${damage.expected} skipped ${damage.expected === 1 ? 'artist' : 'artists'}, but only ${damage.found} arrived`;
  return (
    <div
      role="status"
      className="mb-6 rounded-lg border border-[var(--color-away)]/40 p-4 text-[13.5px] text-[var(--color-text)]"
    >
      <p>
        This link looks cut short. {detail}, so the journey below may not be the one you were
        sent. Ask for the whole link to see it.
      </p>
    </div>
  );
}
