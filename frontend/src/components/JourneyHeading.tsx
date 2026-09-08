interface Props {
  from: string;
  to: string;
  /**
   * Artists BETWEEN the two chosen ones (UXR-D6, UI-D7) — the one count
   * currency the UI states. Not the player bar's "Stop N of M", which counts
   * every artist including both endpoints (UXR-D10).
   */
  steps: number;
}

/** "Your journey" — both names in display type and the steps tile. */
export function JourneyHeading({ from, to, steps }: Props) {
  return (
    <div className="flex items-end justify-between gap-6">
      <div className="min-w-0">
        <div className="text-[11px] font-semibold uppercase tracking-[.12em] text-[var(--color-label)]">
          Your journey
        </div>
        <h1 className="mt-2 flex flex-wrap items-center gap-x-3.5 gap-y-1 font-display text-[23px] font-medium leading-[1.2] tracking-[-.025em] sm:text-[34px] sm:tracking-[-.03em]">
          <span>{from}</span>
          {/* The rail's own gradient, in miniature. Decorative: the heading
              reads as the two names, which is what it is. */}
          <span
            aria-hidden
            className="h-0.5 w-[46px] rounded-full bg-gradient-to-r from-[var(--color-start)] to-[var(--color-end)]"
          />
          <span>{to}</span>
        </h1>
      </div>
      <div className="flex-none rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] px-4 py-2.5 text-center">
        <div className="font-display text-[20px] font-semibold">{steps}</div>
        <div className="text-[11px] uppercase tracking-[.08em] text-[var(--color-label)]">
          {steps === 1 ? 'step' : 'steps'}
        </div>
      </div>
    </div>
  );
}
