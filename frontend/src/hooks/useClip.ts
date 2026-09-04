import { useEffect, useState } from 'react';
import * as client from '@/api/client';
import type { Track } from '@/api/types';

type ClipState = { status: 'loading' | 'ready' | 'none'; track: Track | null };

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

async function load(mbid: string, index: number): Promise<Track | null> {
  const track = await client.getTrack(mbid, index);
  cache.set(key(mbid, index), { track, at: Date.now() });
  return track;
}

/**
 * A preview URL signed recently enough to actually play, or null if there is no
 * clip. Called at the moment of play — never at the moment a card is drawn, which
 * is the distinction the whole seam exists for.
 */
export async function resolveFreshUrl(mbid: string, index = 0): Promise<string | null> {
  const entry = fresh(mbid, index, PLAYABLE_URL_MAX_AGE_MS);
  if (entry) return entry.track?.previewUrl ?? null;
  try {
    const track = await load(mbid, index);
    return track?.previewUrl ?? null;
  } catch {
    // A rate-limited or failing catalogue must silence the card, not break play.
    return null;
  }
}

function stateFor(track: Track | null): ClipState {
  return { status: track ? 'ready' : 'none', track };
}

export function useClip(mbid: string, index = 0): ClipState {
  const [state, setState] = useState<ClipState>(() => {
    const entry = fresh(mbid, index);
    return entry ? stateFor(entry.track) : { status: 'loading', track: null };
  });

  useEffect(() => {
    const entry = fresh(mbid, index);
    if (entry) {
      setState(stateFor(entry.track));
      return;
    }
    let active = true;
    setState({ status: 'loading', track: null });
    load(mbid, index)
      .then((track) => {
        if (active) setState(stateFor(track));
      })
      .catch(() => {
        if (active) setState({ status: 'none', track: null });
      });
    return () => {
      active = false;
    };
  }, [mbid, index]);

  return state;
}
