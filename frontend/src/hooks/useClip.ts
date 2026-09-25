import { useCallback, useSyncExternalStore } from 'react';
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
/**
 * Each automatic wait is stretched by up to this fraction of itself, at random
 * (#222). A path view's cards fail together when the catalogue is busy, and on
 * one fixed schedule they would all ask again in the same instant. Only ever
 * added, so no card asks sooner than the schedule — or the server — said.
 * Chosen, not measured.
 */
export const RETRY_JITTER = 0.5;

function jittered(ms: number): number {
  return ms * (1 + RETRY_JITTER * Math.random());
}

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

const LOADING: ClipState = { status: 'loading', track: null };

/**
 * One clip's live state, shared by everything showing it (#221). A card and its
 * open detail used to hold a lookup each, so a Retry pressed on one left the
 * other showing the failure. Now both subscribe to this, which also makes them
 * one fetch and one retry schedule rather than two.
 *
 * `cache` above still holds only answers; this holds the transient states too,
 * which is why it is separate — and why nothing here outlives its subscribers'
 * interest: the last one leaving cancels any scheduled retry, and the next first
 * subscriber asks afresh unless the cache can answer.
 */
type Live = {
  state: ClipState;
  listeners: Set<() => void>;
  inflight: boolean;
  timer: ReturnType<typeof setTimeout> | undefined;
  // Automatic retries spent. Reset by a first subscriber and by a manual retry,
  // so pressing Retry buys the bounded schedule again.
  autoRetries: number;
};

const live = new Map<string, Live>();

function liveEntry(mbid: string, index: number): Live {
  const k = key(mbid, index);
  let entry = live.get(k);
  if (!entry) {
    const cached = fresh(mbid, index);
    entry = {
      state: cached ? stateFor(cached.track) : LOADING,
      listeners: new Set(),
      inflight: false,
      timer: undefined,
      autoRetries: 0,
    };
    live.set(k, entry);
  }
  return entry;
}

function publish(entry: Live, state: ClipState) {
  entry.state = state;
  for (const listener of entry.listeners) listener();
}

function fetchInto(entry: Live, mbid: string, index: number) {
  entry.inflight = true;
  publish(entry, LOADING);
  load(mbid, index)
    .then((track) => {
      entry.inflight = false;
      publish(entry, stateFor(track));
    })
    .catch((err: unknown) => {
      entry.inflight = false;
      publish(entry, { status: failureStatus(err), track: null });
      if (entry.listeners.size === 0) return; // nobody is looking; the next subscriber asks
      const step = entry.autoRetries;
      if (step >= AUTO_RETRY_DELAYS_MS.length) return;
      const asked = err instanceof client.ApiError ? err.retryAfterMs : undefined;
      const wait = Math.min(jittered(asked ?? AUTO_RETRY_DELAYS_MS[step]), MAX_RETRY_WAIT_MS);
      entry.timer = setTimeout(() => {
        entry.timer = undefined;
        entry.autoRetries = step + 1;
        fetchInto(entry, mbid, index);
      }, wait);
    });
}

function subscribe(mbid: string, index: number, listener: () => void): () => void {
  const entry = liveEntry(mbid, index);
  const first = entry.listeners.size === 0;
  entry.listeners.add(listener);
  if (first && !entry.inflight) {
    const cached = fresh(mbid, index);
    if (cached) {
      publish(entry, stateFor(cached.track));
    } else {
      entry.autoRetries = 0;
      fetchInto(entry, mbid, index);
    }
  }
  return () => {
    entry.listeners.delete(listener);
    if (entry.listeners.size === 0) {
      clearTimeout(entry.timer);
      entry.timer = undefined;
    }
  };
}

function retryNow(mbid: string, index: number) {
  const entry = liveEntry(mbid, index);
  if (entry.inflight) return; // already asking; its answer reaches every subscriber
  clearTimeout(entry.timer);
  entry.timer = undefined;
  entry.autoRetries = 0;
  fetchInto(entry, mbid, index);
}

export function useClip(mbid: string, index = 0): ClipState & { retry: () => void } {
  const state = useSyncExternalStore(
    useCallback((listener: () => void) => subscribe(mbid, index, listener), [mbid, index]),
    () => liveEntry(mbid, index).state,
  );
  const retry = useCallback(() => retryNow(mbid, index), [mbid, index]);
  return { ...state, retry };
}
