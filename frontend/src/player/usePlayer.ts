import { useEffect, useMemo, useRef, useState } from 'react';
import { HtmlAudioPlayer } from './Player';

interface Playable {
  mbid: string;
}

/**
 * Returns a URL that is signed *now*, or null if the artist has no clip.
 * Rejects when the lookup itself failed — which is not the same thing (G3-F1).
 */
type ResolveUrl = (mbid: string) => Promise<string | null>;

/**
 * Why the current artist is not playing, when it should be (G3-F1). Each of
 * these used to end in clear(): the bar vanished and nothing said why.
 *
 * - `no-clip`     — asked at the moment of play, the server had no clip.
 * - `unreachable` — the lookup failed: offline, timed out, catalogue busy.
 * - `wont-play`   — we had a URL, the audio element refused it, and the one
 *                   silent retry with a fresh signature failed too.
 */
export type PlaybackFailure = 'no-clip' | 'unreachable' | 'wont-play';

/**
 * The listener's volume, for the rest of the tab's life (#207): sessionStorage,
 * so it survives a new path or a reload but a new visit starts at full. A
 * convenience, never state that must persist — every read and write tolerates
 * storage that is missing, blocked or holding something unreadable.
 */
const VOLUME_KEY = 'artistpath.volume';

function storedVolume(): number {
  try {
    const raw = sessionStorage.getItem(VOLUME_KEY);
    const v = raw === null ? NaN : Number(raw);
    return Number.isFinite(v) && v >= 0 && v <= 1 ? v : 1;
  } catch {
    return 1;
  }
}

function storeVolume(v: number) {
  try {
    sessionStorage.setItem(VOLUME_KEY, String(v));
  } catch {
    /* storage unavailable: the volume still holds for this page */
  }
}

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
  // Seconds, straight from the element's own clock (UXR-D10) — never estimated.
  const [position, setPosition] = useState(0);
  const [duration, setDuration] = useState(0);
  const [failure, setFailure] = useState<PlaybackFailure | null>(null);
  const [volume, setVolumeState] = useState(storedVolume);

  const listRef = useRef(playables);
  listRef.current = playables;
  const resolveRef = useRef(resolveUrl);
  resolveRef.current = resolveUrl;
  const volumeRef = useRef(volume);
  volumeRef.current = volume;

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
    setPosition(0);
    setDuration(0);
    setFailure(null);
  }

  // The failure routes' replacement for clear(): this artist stays current, so
  // the bar stays up and names who failed, and says why with a way to retry.
  // Nothing is loaded, so a toggle cannot resume a dead source — it retries.
  function fail(mbid: string, why: PlaybackFailure) {
    player.pause(); // whatever was playing before this press must not play on under the message
    currentRef.current = mbid;
    loadedUrlRef.current = null;
    setCurrentMbid(mbid);
    setIsPlaying(false);
    setPosition(0);
    setDuration(0);
    setFailure(why);
  }

  async function start(mbid: string, { isRetry = false } = {}) {
    const token = ++startTokenRef.current;
    if (!isRetry) retriedRef.current = false;

    let url: string | null;
    try {
      url = await resolveRef.current(mbid);
    } catch {
      if (token === startTokenRef.current) fail(mbid, 'unreachable');
      return;
    }
    if (token !== startTokenRef.current) return; // superseded by a later press
    if (!url) {
      fail(mbid, 'no-clip');
      return;
    }

    currentRef.current = mbid;
    loadedUrlRef.current = url;
    setCurrentMbid(mbid);
    setFailure(null);
    setIsPlaying(true);
    setPosition(0);
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
      if (!mbid) {
        clear();
        return;
      }
      if (retriedRef.current) {
        fail(mbid, 'wont-play');
        return;
      }
      retriedRef.current = true;
      void start(mbid, { isRetry: true });
    });

    player.onTimeUpdate((p, d) => {
      setPosition(p);
      setDuration(d);
    });

    // G3-F8: the element has the last word on whether it is playing. The app
    // still sets isPlaying on its own presses, so the button answers at once,
    // but anything that pauses or resumes the element without asking — a phone
    // call, a Bluetooth headset, the OS media keys — now shows as it is.
    player.onPlayingChange(setIsPlaying);

    // The element starts at full volume; bring it to the listener's level once.
    // From then on setVolume() keeps the two in step.
    player.setVolume(volumeRef.current);

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

  /** Start the current artist again from a failure — a fresh start, with its own silent retry. */
  function retry() {
    const mbid = currentRef.current;
    if (mbid) void start(mbid);
  }

  function pause() {
    player.pause();
    setIsPlaying(false);
  }

  function resume() {
    if (failure) {
      retry();
      return;
    }
    // Resume the source already loaded rather than re-resolving: a new URL would
    // reset the element and re-seek to zero. If it expired while paused, the error
    // handler re-signs it *if this track still has its one retry* — which is why
    // resolve-on-play and retry-on-error are complementary rather than alternatives.
    const url = loadedUrlRef.current;
    if (currentRef.current && url) {
      player.play(url);
      setIsPlaying(true);
    }
  }

  function toggle() {
    if (isPlaying) pause();
    else resume();
  }

  /** Loudness only (#207): no restart, no re-resolve, playing or not. */
  function setVolume(v: number) {
    const next = Math.min(1, Math.max(0, v));
    player.setVolume(next);
    setVolumeState(next);
    storeVolume(next);
  }

  return {
    currentMbid, isPlaying, position, duration, failure, volume,
    playFrom, toggle, pause, resume, retry, stop, setVolume,
  };
}
