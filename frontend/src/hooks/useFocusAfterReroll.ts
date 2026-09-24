import { useEffect, useRef, type RefObject } from 'react';

/**
 * Put focus somewhere sensible once a rebuilt path has landed (issue #188).
 *
 * A bypass press unmounts the control that was pressed — "Dig deeper" goes
 * with the artist it removed, "Reset path" with the last bypass — and focus
 * falls to <body>. A keyboard user is then back at the top of the document
 * and a screen reader user is told nothing about the new path.
 *
 * Fires when the reroll message clears, which is the moment the new path is
 * both on screen and no longer dimmed (useRerollFeedback). Only when focus
 * was actually lost: someone who has already moved on — tabbed into a card
 * while the notice was up — is not pulled back.
 */
export function useFocusAfterReroll(
  notice: unknown,
  status: 'loading' | 'ready' | 'error',
  target: RefObject<HTMLElement | null>,
): void {
  const wasActive = useRef(false);
  useEffect(() => {
    if (notice !== null) {
      wasActive.current = true;
      return;
    }
    if (!wasActive.current) return;
    wasActive.current = false;
    // An error replaces the path with PathStatus, whose role="alert" speaks
    // for itself; there is no heading to land on.
    if (status !== 'ready') return;
    const active = document.activeElement;
    if (active && active !== document.body && active.isConnected) return;
    target.current?.focus();
  }, [notice, status, target]);
}
