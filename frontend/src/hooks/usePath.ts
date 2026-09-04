import { useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import { ApiError, TimeoutError, buildPath } from '@/api/client';
import type { Artist, StopRule } from '@/api/types';
import { decodeExclusions } from '@/lib/exclusions';

export interface PathState {
  status: 'loading' | 'ready' | 'error';
  artists: Artist[];
  stopRule: StopRule;
  bypassed: Artist[];
  unresolved: string[];
  error?: 'notfound' | 'nopath' | 'timeout' | 'unknown';
  /** Rebuilds the same path. The only error state with a useful response. */
  retry: () => void;
}

function classify(err: unknown): PathState['error'] {
  if (err instanceof TimeoutError) return 'timeout';
  if (err instanceof ApiError) {
    if (err.status === 404) return 'notfound';
    if (err.status === 409) return 'nopath';
  }
  return 'unknown';
}

export function usePath(): PathState {
  const { from, to } = useParams();
  const [params] = useSearchParams();
  const [attempt, setAttempt] = useState(0);
  const [state, setState] = useState<Omit<PathState, 'retry'>>({
    status: 'loading', artists: [], stopRule: 'natural', bypassed: [], unresolved: [],
  });

  // The URL is unchanged on a retry, so the attempt counter is what makes the
  // effect run again. Without it "Try again" would do nothing at all.
  const key = `${from}|${to}|${params.toString()}|${attempt}`;

  useEffect(() => {
    if (!from || !to) return;
    const controller = new AbortController();
    setState((prev) => ({
      status: 'loading',
      artists: prev.artists,
      stopRule: prev.stopRule,
      bypassed: prev.bypassed,
      unresolved: prev.unresolved,
    }));
    buildPath([from, to], decodeExclusions(params), controller.signal)
      .then((result) => setState({ status: 'ready', ...result }))
      .catch((err) => {
        if (controller.signal.aborted) return;
        setState({
          status: 'error', artists: [], stopRule: 'natural', bypassed: [], unresolved: [],
          error: classify(err),
        });
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return { ...state, retry: () => setAttempt((n) => n + 1) };
}
