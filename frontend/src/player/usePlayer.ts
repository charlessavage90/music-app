import { useEffect, useMemo, useRef, useState } from 'react';
import { HtmlAudioPlayer } from './Player';

interface Playable {
  mbid: string;
}

/** Returns a URL that is signed *now*, or null if the artist has no clip. */
type ResolveUrl = (mbid: string) => Promise<string | null>;

/**
 * Owns playback for a journey.
 *
 * The player is handed a resolver rather than URLs (C2, browser side). A preview
 * signature lasts 15 minutes — measured, see the gate-1 execution log §15 — while a
 * card can stay mounted for hours, so a URL captured when the card was drawn is
 * dead by the time it is pressed. Every start therefore asks for the URL at that
 * moment, and an audio error buys one silent retry with a newly signed one.
 */
export function usePlayer(playables: Playable[], resolveUrl: ResolveUrl) {
  const player = useMemo(() => new HtmlAudioPlayer(), []);
  const [currentMbid, setCurrentMbid] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const listRef = useRef(playables);
  listRef.current = playables;
  const resolveRef = useRef(resolveUrl);
  resolveRef.current = resolveUrl;

  // Playback state the callbacks need synchronously — an `ended` or `error` event
  // arrives outside React's render cycle and cannot wait for state to settle.
  const currentRef = useRef<string | null>(null);
  const loadedUrlRef = useRef<string | null>(null);
  const retriedRef = useRef(false);
  // Guards against a slow resolve landing after the user has moved on.
  const startTokenRef = useRef(0);

  function clear() {
    currentRef.current = null;
    loadedUrlRef.current = null;
    setCurrentMbid(null);
    setIsPlaying(false);
  }

  async function start(mbid: string, { isRetry = false } = {}) {
    const token = ++startTokenRef.current;
    if (!isRetry) retriedRef.current = false;

    const url = await resolveRef.current(mbid);
    if (token !== startTokenRef.current) return; // superseded by a later press
    if (!url) {
      clear();
      return;
    }

    currentRef.current = mbid;
    loadedUrlRef.current = url;
    setCurrentMbid(mbid);
    setIsPlaying(true);
    player.play(url);
  }

  useEffect(() => {
    player.onEnded(() => {
      const list = listRef.current;
      const idx = list.findIndex((p) => p.mbid === currentRef.current);
      const next = idx >= 0 ? list[idx + 1] : undefined;
      if (next) void start(next.mbid);
      else clear();
    });

    player.onError(() => {
      const mbid = currentRef.current;
      if (!mbid || retriedRef.current) {
        clear();
        return;
      }
      retriedRef.current = true;
      void start(mbid, { isRetry: true });
    });

    return () => player.dispose();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [player]);

  function playFrom(mbid: string) {
    if (!listRef.current.some((p) => p.mbid === mbid)) return;
    void start(mbid);
  }

  function stop() {
    startTokenRef.current++; // abandon any resolve still in flight
    player.pause();
    clear();
  }

  function toggle() {
    if (isPlaying) {
      player.pause();
      setIsPlaying(false);
      return;
    }
    // Resume the source already loaded rather than re-resolving: a new URL would
    // reset the element and re-seek to zero. If it has expired while paused the
    // error handler re-signs it, which is why the two halves are complementary.
    const url = loadedUrlRef.current;
    if (currentRef.current && url) {
      player.play(url);
      setIsPlaying(true);
    }
  }

  return { currentMbid, isPlaying, playFrom, toggle, stop };
}
