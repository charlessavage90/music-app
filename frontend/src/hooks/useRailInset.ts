import { useLayoutEffect, useState, type RefObject } from 'react';

/**
 * Where a rail's line starts and stops: the first dot's centre and the last
 * dot's centre, measured rather than assumed (the dots are the list's
 * `[data-rail-dot]` elements — `RailDot` in components/Rail.tsx).
 *
 * It was a fixed 41px inset at both ends until 2026-09-08, and a fixed inset
 * CANNOT be right — on the journey page the two endpoint cards carry an
 * eyebrow the interior cards do not, so they are taller, by an amount that
 * changes with width and with whether the eyebrow wraps. Measured in a
 * browser, 41px overshot by 7.5px at each end at 1280, and at 390 it was
 * lopsided: 3.25px past the top dot and 10.75px past the bottom one.
 *
 * Null until measured, and null wherever nothing can measure (jsdom has no
 * layout, and ResizeObserver may be absent) — the line then spans the list,
 * which is what it did before and is never worse than a wrong inset.
 * Re-measures when `key` changes and on resize: row heights move with width,
 * with wrapping, and with the display face finishing loading — all after the
 * first paint.
 */
export function useRailInset(listRef: RefObject<HTMLElement | null>, key: unknown) {
  const [inset, setInset] = useState<{ top: number; bottom: number } | null>(null);

  useLayoutEffect(() => {
    const ol = listRef.current;
    if (!ol) return;

    function measure() {
      if (!ol) return;
      const dots = ol.querySelectorAll<HTMLElement>('[data-rail-dot]');
      if (dots.length < 2) return setInset(null);
      const box = ol.getBoundingClientRect();
      const first = dots[0].getBoundingClientRect();
      const last = dots[dots.length - 1].getBoundingClientRect();
      // A layout-less environment reports zeros; that is the null case, not an
      // inset of zero, which would draw a full-height line claiming precision.
      if (box.height === 0) return setInset(null);
      const next = {
        top: first.top + first.height / 2 - box.top,
        bottom: box.bottom - (last.top + last.height / 2),
      };
      setInset((prev) => (prev && prev.top === next.top && prev.bottom === next.bottom ? prev : next));
    }

    measure();
    if (typeof ResizeObserver === 'undefined') return;
    const ro = new ResizeObserver(measure);
    ro.observe(ol);
    return () => ro.disconnect();
  }, [listRef, key]);

  return inset;
}
