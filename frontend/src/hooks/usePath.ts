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
  error?: PathError;
  /**
   * What the server said about the failure, when it said something a person can
   * read (issue #193). Shown for `invalid`; the other kinds have fixed wording.
   */
  message?: string;
  /** For `toomany`: the server's cap on exclusions, from its own error. */
  limit?: number;
  /** Rebuilds the same path. The only error state with a useful response. */
  retry: () => void;
}

/**
 * `invalid` is a 422 with a readable reason (two identical artists); `toomany`
 * is the bypass cap, the one 422 a person reaches by pressing buttons. Both
 * were 'unknown' — "Something went wrong" — until issue #193.
 */
export type PathError = 'notfound' | 'nopath' | 'timeout' | 'invalid' | 'toomany' | 'unknown';

type Failure = Pick<PathState, 'error' | 'message' | 'limit'>;

function classify(err: unknown): Failure {
  if (err instanceof TimeoutError) return { error: 'timeout' };
  if (err instanceof ApiError) {
    if (err.status === 404) return { error: 'notfound' };
    if (err.status === 409) return { error: 'nopath' };
    if (err.status === 422) {
      if (err.limit?.kind === 'too_many_exclusions') return { error: 'toomany', limit: err.limit.max };
      if (err.detail) return { error: 'invalid', message: err.detail };
    }
  }
  return { error: 'unknown' };
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
          ...classify(err),
        });
      });
    return () => controller.abort();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return { ...state, retry: () => setAttempt((n) => n + 1) };
}
