import { useCallback, useEffect, useRef, useState } from 'react';
import * as client from '@/api/client';
import type { Track } from '@/api/types';

/**
 * What a card knows about its clip. Three different things used to read as
 * one "No preview available" (G3-F11), and only the first of them is true:
 *
 * - `none`   — the server looked and this artist has no clip (a 204).
 * - `busy`   — the catalogue refused us (a 503): throttled or down, so the
 *              artist may well have a clip. Transient.
 * - `failed` — we never got an answer: offline, timed out, a server error.
 *              Transient.
 *
 * The two transient ones are never cached, retry on their own a bounded number
 * of times, and can always be retried by hand.
 */
export type ClipStatus = 'loading' | 'ready' | 'none' | 'busy' | 'failed';
type ClipState = { status: ClipStatus; track: Track | null };

/** Whether a status is worth asking again about. */
export function isTransient(status: ClipStatus): boolean {
  return status === 'busy' || status === 'failed';
}

/** The words a card shows for a clip it cannot play. One copy, card and detail alike. */
export function silentLabel(status: ClipStatus): string {
  if (status === 'busy') return 'Preview service busy';
  if (status === 'failed') return 'Couldn’t load preview';
  return 'No preview available';
}

/**
 * How long to wait before each automatic retry of a transient failure. Two,
 * then stop: a path view is 8–10 cards, and a card that keeps asking a service
 * that is refusing us is the amplification G3-A4 removed on the server. A
 * `Retry-After` from the server replaces the step it lands on. Chosen, not
 * measured.
 */
export const AUTO_RETRY_DELAYS_MS = [5_000, 30_000] as const;
/** A ceiling on any server-requested wait, so a card never sits for longer. */
const MAX_RETRY_WAIT_MS = 2 * 60 * 1000;

function failureStatus(err: unknown): 'busy' | 'failed' {
  return err instanceof client.ApiError && (err.status === 503 || err.status === 429)
    ? 'busy'
    : 'failed';
}

/**
 * How long a resolved track may be reused for *display* — title and cover art,
 * which do not expire. Governs what the card shows, not what the player is given.
 */
const CLIP_TTL_MS = 10 * 60 * 1000;

/**
 * How long a signed preview URL may be reused for *playback* (C2).
 *
 * A Deezer signature lasts 15 minutes, measured against wall clock rather than
 * assumed — see the gate-1 execution log §15, which owns that figure. This window
 * is deliberately well inside it: the clip itself runs 30 seconds, so five minutes
 * leaves margin for a card that sits paused. It is not a tuned number, and it
 * trades against a service that rate-limits, so shortening it is not free.
 */
const PLAYABLE_URL_MAX_AGE_MS = 5 * 60 * 1000;

const cache = new Map<string, { track: Track | null; at: number }>();

/** Cache key. The index is part of the identity: two indices are two tracks. */
function key(mbid: string, index: number) {
  return `${mbid}:${index}`;
}

function fresh(mbid: string, index: number, maxAgeMs = CLIP_TTL_MS) {
  const entry = cache.get(key(mbid, index));
  if (!entry || Date.now() - entry.at > maxAgeMs) return undefined;
  return entry;
}

/**
 * Only an ANSWER is cached — a clip, or a 204's "none". A failure throws past
 * the cache, so nothing transient is remembered for CLIP_TTL_MS (G3-F11).
 */
async function load(mbid: string, index: number): Promise<Track | null> {
  const track = await client.getTrack(mbid, index);
  cache.set(key(mbid, index), { track, at: Date.now() });
  return track;
}

/**
 * A preview URL signed recently enough to actually play, or null if there is no
 * clip. Called at the moment of play — never at the moment a card is drawn, which
 * is the distinction the whole seam exists for.
 *
 * REJECTS when the lookup fails. It used to swallow that into null, which the
 * player could not tell from "no clip" and answered by removing itself without a
 * word (G3-F1). The player owns what to say about it.
 */
export async function resolveFreshUrl(mbid: string, index = 0): Promise<string | null> {
  const entry = fresh(mbid, index, PLAYABLE_URL_MAX_AGE_MS);
  if (entry) return entry.track?.previewUrl ?? null;
  const track = await load(mbid, index);
  return track?.previewUrl ?? null;
}

/**
 * What the cache already knows about a track, for a DISPLAY that is not the
 * card (the player bar's title). Never fetches: the card that owns the clip
 * has already resolved it by the time anything plays.
 */
export function cachedTrack(mbid: string, index = 0): Track | null {
  return fresh(mbid, index)?.track ?? null;
}

function stateFor(track: Track | null): ClipState {
  return { status: track ? 'ready' : 'none', track };
}

export function useClip(mbid: string, index = 0): ClipState & { retry: () => void } {
  const [state, setState] = useState<ClipState>(() => {
    const entry = fresh(mbid, index);
    return entry ? stateFor(entry.track) : { status: 'loading', track: null };
  });
  // Bumped to ask again. Part of the fetch effect's key, so a retry is the same
  // code path as the first load, cancellation included.
  const [attempt, setAttempt] = useState(0);
  // Automatic retries spent on THIS clip. Reset by a new clip and by a manual
  // retry, so pressing Retry buys the bounded schedule again.
  const autoRetries = useRef(0);

  useEffect(() => {
    autoRetries.current = 0;
  }, [mbid, index]);

  useEffect(() => {
    const entry = fresh(mbid, index);
    if (entry) {
      setState(stateFor(entry.track));
      return;
    }
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    setState({ status: 'loading', track: null });
    load(mbid, index)
      .then((track) => {
        if (active) setState(stateFor(track));
      })
      .catch((err: unknown) => {
        if (!active) return;
        setState({ status: failureStatus(err), track: null });
        const step = autoRetries.current;
        if (step >= AUTO_RETRY_DELAYS_MS.length) return;
        const asked = err instanceof client.ApiError ? err.retryAfterMs : undefined;
        const wait = Math.min(asked ?? AUTO_RETRY_DELAYS_MS[step], MAX_RETRY_WAIT_MS);
        timer = setTimeout(() => {
          autoRetries.current = step + 1;
          setAttempt((a) => a + 1);
        }, wait);
      });
    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [mbid, index, attempt]);

  const retry = useCallback(() => {
    autoRetries.current = 0;
    setAttempt((a) => a + 1);
  }, []);

  return { ...state, retry };
}
