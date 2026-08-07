import type { BypassReason } from '@/api/types';

export type RerollReason = BypassReason | 'reset';

/**
 * Fixed at design time (spec §7) so wording cannot be reshaped to fit an
 * implementation. No trailing ellipsis — the animated dots supply it.
 *
 * These are accurate to the router, not decorative: `dislike` applies a soft
 * penalty to the disliked artist's NEIGHBOURHOOD, decaying over `avoid_radius`
 * hops; `known` relaxes the obscurity floor more aggressively. If either
 * mechanism changes, these strings are wrong.
 *
 * Reworded 2026-08-07 to echo the tray's own verbs — the buttons now read
 * "Steer away" and "Dig deeper", and a notice that said something else made the
 * press and its response look like two different events. The mechanisms are
 * unchanged, so the accuracy above still holds.
 */
const MESSAGE: Record<RerollReason, string> = {
  dislike: 'Steering away from that sound',
  known: 'Digging deeper for someone newer',
  reset: 'Back to the original path',
};

/**
 * Shown over the previous path while a reroll is in flight (UI-D4). The path
 * underneath stays legible at 60% opacity rather than being replaced, so a run
 * of bypass presses does not strobe.
 */
export function RerollNotice({ reason }: { reason: RerollReason }) {
  return (
    <div className="pointer-events-none absolute inset-0 z-10 flex items-start justify-center pt-24">
      <div
        role="status"
        aria-live="polite"
        className="flex items-center gap-2.5 rounded-full border border-[var(--color-border)] bg-[var(--color-surface)] px-5 py-3 text-[13px] text-[var(--color-text)] shadow-[0_24px_48px_-12px_rgba(0,0,0,.75)]"
      >
        {MESSAGE[reason]}
        <span className="flex items-center gap-1" aria-hidden>
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="block size-1 rounded-full bg-[var(--color-accent)] [animation:ap-pulse_1.2s_ease-in-out_infinite]"
              style={{ animationDelay: `${i * 0.16}s` }}
            />
          ))}
        </span>
      </div>
    </div>
  );
}
