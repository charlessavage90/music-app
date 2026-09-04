export type RerollReason = 'known' | 'reset';

/**
 * Fixed at design time (spec §7) so wording cannot be reshaped to fit an
 * implementation. No trailing ellipsis — the animated dots supply it.
 *
 * These are accurate to the router, not decorative: `known` relaxes the
 * obscurity floor harder than `dislike` did and is the only signal carrying the
 * fame ramp. If that mechanism changes, this string is wrong.
 *
 * The `dislike` message went with its button (LUX-1). The signal, its router
 * behaviour and its URL parameter all remain — nothing in the UI can now
 * produce it, which is why this type no longer admits it. `BypassReason` in
 * api/types.ts stays two-valued: that one is the wire contract.
 */
const MESSAGE: Record<RerollReason, string> = {
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
    // Offset measured from the top of the PATH (PathPage owns that positioning
    // context). It was pt-24 against a container that also held the explainer,
    // which is how it came to sit on top of it. Over the first card is the
    // right place: the notice describes the thing underneath it.
    <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex justify-center pt-9">
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
