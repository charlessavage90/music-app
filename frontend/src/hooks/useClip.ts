import { useEffect, useState } from 'react';
import { getTrack } from '@/api/client';
import type { Track } from '@/api/types';

type ClipState = { status: 'loading' | 'ready' | 'none'; track: Track | null };

const cache = new Map<string, Track | null>();

export function useClip(mbid: string): ClipState {
  const [state, setState] = useState<ClipState>(() =>
    cache.has(mbid)
      ? { status: cache.get(mbid) ? 'ready' : 'none', track: cache.get(mbid) ?? null }
      : { status: 'loading', track: null },
  );

  useEffect(() => {
    if (cache.has(mbid)) {
      const cached = cache.get(mbid) ?? null;
      setState({ status: cached ? 'ready' : 'none', track: cached });
      return;
    }
    let active = true;
    setState({ status: 'loading', track: null });
    getTrack(mbid)
      .then((track) => {
        cache.set(mbid, track);
        if (active) setState({ status: track ? 'ready' : 'none', track });
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
