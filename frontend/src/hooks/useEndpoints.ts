import { useEffect, useState } from 'react';
import * as client from '@/api/client';
import type { Artist } from '@/api/types';

type Endpoints = { from: Artist | null; to: Artist | null };

/**
 * The two artists the URL names, for the loading screen.
 *
 * UI-7: every failure resolves to null and nothing propagates. `POST /api/path`
 * is the real request; a decorative lookup must not be able to turn a working
 * page into an error page. Pass `skip` once the path itself has supplied names.
 */
export function useEndpoints(fromMbid?: string, toMbid?: string, skip = false): Endpoints {
  const [state, setState] = useState<Endpoints>({ from: null, to: null });

  useEffect(() => {
    if (skip || !fromMbid || !toMbid) return;
    const controller = new AbortController();
    let active = true;
    Promise.all([
      client.getArtist(fromMbid, controller.signal).catch(() => null),
      client.getArtist(toMbid, controller.signal).catch(() => null),
    ]).then(([from, to]) => {
      if (active) setState({ from, to });
    });
    return () => {
      active = false;
      controller.abort();
    };
  }, [fromMbid, toMbid, skip]);

  return state;
}
