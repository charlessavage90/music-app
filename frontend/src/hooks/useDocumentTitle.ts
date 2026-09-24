import { useEffect } from 'react';

/** What index.html ships, and what every page without its own title shows. */
export const APP_TITLE = 'Unsung.fm';

/**
 * The tab title for a journey, naming both ends (issue #191).
 *
 * A browser tab, a bookmark, history and the OS share sheet all read
 * document.title, and it was the constant app name on every journey. Link
 * PREVIEWS in chat apps are a different matter: their crawlers do not run
 * JavaScript, so they see only index.html's static tags — naming the artists
 * there would need the page rendered at the edge, which this does not attempt.
 */
export function journeyTitle(from?: string | null, to?: string | null): string {
  return from && to ? `${from} → ${to} · ${APP_TITLE}` : APP_TITLE;
}

/** Sets document.title while mounted, and restores the app name after. */
export function useDocumentTitle(title: string): void {
  useEffect(() => {
    document.title = title;
  }, [title]);
  useEffect(() => () => {
    document.title = APP_TITLE;
  }, []);
}
