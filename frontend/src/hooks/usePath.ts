import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { ApiError, buildPath } from '@/api/client';
import type { Artist, StopRule } from '@/api/types';
import { decodeExclusions } from '@/lib/exclusions';

export interface PathState {
  status: 'loading' | 'ready' | 'error';
  artists: Artist[];
  stopRule: StopRule;
  error?: 'notfound' | 'nopath' | 'unknown';
}

function classify(err: unknown): PathState['error'] {
  if (err instanceof ApiError) {
    if (err.status === 404) return 'notfound';
    if (err.status === 409) return 'nopath';
  }
  return 'unknown';
}

export function usePath(): PathState {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const [state, setState] = useState<PathState>({
    status: 'loading', artists: [], stopRule: 'natural',
  });

  const key = `${from}|${to}|${params.toString()}`;

  useEffect(() => {
    if (!from || !to) return;
    const controller = new AbortController();
    setState((prev) => ({ status: 'loading', artists: prev.artists, stopRule: prev.stopRule }));
    buildPath([from, to], decodeExclusions(params), controller.signal)
      .then(({ artists, stopRule }) => setState({ status: 'ready', artists, stopRule }))
      .catch((err) => {
        if (controller.signal.aborted) return;
        setState({ status: 'error', artists: [], stopRule: 'natural', error: classify(err) });
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return state;
}
