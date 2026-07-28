import type { Artist } from '@/api/types';

interface Props {
  from: Artist | null;
  to: Artist | null;
}

const SHIMMER =
  'bg-[linear-gradient(90deg,var(--color-inert)_0%,#282c34_40%,var(--color-inert)_80%)] bg-[length:260px_100%] [animation:ap-shimmer_1.6s_linear_infinite]';

/** Four rows of decreasing opacity, as the mockup draws them. */
const ROWS = [
  { w1: '62%', w2: '44%', opacity: 1 },
  { w1: '48%', w2: '56%', opacity: 0.82 },
  { w1: '70%', w2: '38%', opacity: 0.62 },
  { w1: '54%', w2: '48%', opacity: 0.42 },
];

function EndpointCard({ artist }: { artist: Artist | null }) {
  return (
    <div className="flex items-center gap-3.5 rounded-xl border border-[var(--color-endpoint)] bg-[var(--color-surface)] px-3.5 py-4">
      <div className="w-14 h-14 flex-none rounded-[9px] bg-[var(--color-border)]" aria-hidden />
      <div className="min-w-0 flex-1">
        {artist ? (
          <div className="truncate text-base font-semibold tracking-[-.01em]">{artist.name}</div>
        ) : (
          <div className={`h-3 w-[58%] rounded-full ${SHIMMER}`} aria-hidden />
        )}
      </div>
    </div>
  );
}

/**
 * The building-path screen. Shown only when there is nothing on screen yet —
 * a first load or a shared link. A bypass press holds the old path instead
 * (UI-D4), which is `RerollNotice`.
 *
 * Both endpoints come from `useEndpoints`, which may legitimately return nulls
 * (UI-7); the cards shimmer in that case rather than the screen failing.
 */
export function PathSkeleton({ from, to }: Props) {
  return (
    <div className="flex min-h-[60vh] flex-col">
      {from && to && (
        <div className="text-[17px] font-medium tracking-[-.01em]">
          {from.name} <span className="font-normal text-[var(--color-label)]">→</span> {to.name}
        </div>
      )}
      <div
        className="mt-2 text-[13px] text-[var(--color-muted)] [animation:ap-pulse_1.8s_ease-in-out_infinite]"
        aria-live="polite"
      >
        Listening for the steps between them…
      </div>

      <div className="relative mt-7 flex flex-col gap-3.5 pl-[19px]">
        <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] origin-top rounded-full bg-gradient-to-b from-[var(--color-accent)] via-[var(--color-rail-mid)] to-[var(--color-dig)] [animation:ap-grow_2.4s_cubic-bezier(.32,.72,.28,1)_infinite]" />

        <EndpointCard artist={from} />

        {ROWS.map((row, i) => (
          <div
            key={i}
            className="flex items-center gap-3.5 rounded-xl border border-[var(--color-border)] bg-[var(--color-surface)] p-3.5"
            style={{ opacity: row.opacity }}
            aria-hidden
          >
            <div className={`w-[52px] h-[52px] flex-none rounded-[9px] ${SHIMMER}`} />
            <div className="flex min-w-0 flex-1 flex-col gap-2">
              <div className={`h-3 rounded-full ${SHIMMER}`} style={{ width: row.w1 }} />
              <div className="h-[9px] rounded-full bg-[#1d2027]" style={{ width: row.w2 }} />
            </div>
            <div className="w-10 h-10 flex-none rounded-full bg-[var(--color-inert)]" />
          </div>
        ))}

        <div className="px-0 py-1 text-base tracking-[.35em] text-[var(--color-inert-fg)]" aria-hidden>
          ···
        </div>

        <EndpointCard artist={to} />
      </div>

      <p className="mt-auto pt-8 text-center text-[11.5px] tracking-[.02em] text-[var(--color-label)]">
        This usually takes a few seconds
      </p>
    </div>
  );
}
