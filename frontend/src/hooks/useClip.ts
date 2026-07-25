import { useEffect, useState } from 'react';
import { getTrack } from '@/api/client';
import type { Track } from '@/api/types';

type ClipState = { status: 'loading' | 'ready' | 'none'; track: Track | null };

/**
 * How long a resolved track may be reused before we ask the API again (C2).
 *
 * A track's preview URL is signed and short-lived — one was measured dead
 * within 31 minutes — and this cache holds that URL, so on a tab left open it
 * would serve expired audio however correct the server is. Ten minutes is
 * comfortably inside the observed lifetime, and the re-fetch is cheap: the
 * server keeps the track identity and only re-signs the URL.
 */
const CLIP_TTL_MS = 10 * 60 * 1000;

const cache = new Map<string, { track: Track | null; at: number }>();

function fresh(mbid: string) {
  const entry = cache.get(mbid);
  if (!entry || Date.now() - entry.at > CLIP_TTL_MS) return undefined;
  return entry;
}

function stateFor(track: Track | null): ClipState {
  return { status: track ? 'ready' : 'none', track };
}

export function useClip(mbid: string): ClipState {
  const [state, setState] = useState<ClipState>(() => {
    const entry = fresh(mbid);
    return entry ? stateFor(entry.track) : { status: 'loading', track: null };
  });

  useEffect(() => {
    const entry = fresh(mbid);
    if (entry) {
      setState(stateFor(entry.track));
      return;
    }
    let active = true;
    setState({ status: 'loading', track: null });
    getTrack(mbid)
      .then((track) => {
        cache.set(mbid, { track, at: Date.now() });
        if (active) setState(stateFor(track));
      })
      .catch(() => {
        if (active) setState({ status: 'none', track: null });
      });
    return () => {
      active = false;
    };
  }, [mbid]);

  return state;
}
