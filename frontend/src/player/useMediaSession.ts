import { useEffect, useRef } from 'react';

interface NowPlaying {
  artist: string;
  title: string | null;
  artwork: string | null;
}

interface Controls {
  play: () => void;
  pause: () => void;
  stop: () => void;
}

function session(): MediaSession | null {
  return typeof navigator !== 'undefined' && 'mediaSession' in navigator ? navigator.mediaSession : null;
}

/**
 * Tells the OS what is playing and lets its controls drive the player (G3-F8):
 * the lock screen, a headset's button, the media keys. Without it the phone
 * shows nothing, and a hardware pause is the one route to the player the app
 * had no way to hear about.
 *
 * The handlers go through a ref and are registered once, so a re-render never
 * re-registers them — the same reason the player's own handlers replace rather
 * than accumulate. Everything is a no-op where the API is absent.
 */
export function useMediaSession(now: NowPlaying | null, isPlaying: boolean, controls: Controls) {
  const controlsRef = useRef(controls);
  controlsRef.current = controls;

  useEffect(() => {
    const ms = session();
    if (!ms) return;
    const actions: Array<[MediaSessionAction, () => void]> = [
      ['play', () => controlsRef.current.play()],
      ['pause', () => controlsRef.current.pause()],
      ['stop', () => controlsRef.current.stop()],
    ];
    for (const [action, handler] of actions) {
      // An action a browser does not support throws rather than being ignored.
      try { ms.setActionHandler(action, handler); } catch { /* unsupported action */ }
    }
    return () => {
      for (const [action] of actions) {
        try { ms.setActionHandler(action, null); } catch { /* unsupported action */ }
      }
      ms.metadata = null;
      ms.playbackState = 'none';
    };
  }, []);

  const artist = now?.artist ?? null;
  const title = now?.title ?? null;
  const artwork = now?.artwork ?? null;
  useEffect(() => {
    const ms = session();
    if (!ms) return;
    if (!artist || typeof MediaMetadata === 'undefined') {
      ms.metadata = null;
      return;
    }
    ms.metadata = new MediaMetadata({
      title: title ?? artist,
      artist,
      artwork: artwork ? [{ src: artwork }] : [],
    });
  }, [artist, title, artwork]);

  useEffect(() => {
    const ms = session();
    if (!ms) return;
    ms.playbackState = artist ? (isPlaying ? 'playing' : 'paused') : 'none';
  }, [artist, isPlaying]);
}
