import { act, renderHook } from '@testing-library/react';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import { GLOW_MS, NOTICE_MIN_MS, useRerollFeedback } from './useRerollFeedback';
import type { Artist } from '@/api/types';

const a = (mbid: string): Artist => ({ mbid, name: mbid, disambiguation: '', popularity: 0 });
const FIRST = [a('start'), a('mid1'), a('end')];
const SECOND = [a('start'), a('mid2'), a('end')];

beforeEach(() => vi.useFakeTimers());
afterEach(() => vi.useRealTimers());

interface HookProps {
  status: 'loading' | 'ready' | 'error';
  artists: Artist[];
}

/** Drives the hook the way PathPage does: loading, then ready with a path. */
function setup() {
  const initialProps: HookProps = { status: 'loading', artists: [] };
  return renderHook(
    ({ status, artists }: HookProps) => useRerollFeedback(status, artists),
    { initialProps },
  );
}

test('a first load marks nothing — there is no previous path to differ from', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });
  expect(result.current.changed.size).toBe(0);
  expect(result.current.notice).toBeNull();
});

// The whole point of the change. Before this, `notice` was cleared the moment
// the path landed, so an 80ms rebuild showed its message for 80ms.
test('the message outlives a rebuild that answered faster than it can be read', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });

  act(() => result.current.begin('known'));
  expect(result.current.notice).toBe('known');

  // The server answers almost at once.
  act(() => void vi.advanceTimersByTime(80));
  rerender({ status: 'ready', artists: SECOND });
  expect(result.current.notice).toBe('known');

  // Still up just before the floor.
  act(() => void vi.advanceTimersByTime(NOTICE_MIN_MS - 120));
  expect(result.current.notice).toBe('known');

  act(() => void vi.advanceTimersByTime(200));
  expect(result.current.notice).toBeNull();
});

test('a slow rebuild is not padded — the floor is a minimum, not a delay', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });

  act(() => result.current.begin('dislike'));
  act(() => void vi.advanceTimersByTime(NOTICE_MIN_MS * 3));
  rerender({ status: 'ready', artists: SECOND });

  // The floor is already spent, so the notice clears on the next tick rather
  // than serving another NOTICE_MIN_MS.
  act(() => void vi.advanceTimersByTime(1));
  expect(result.current.notice).toBeNull();
});

test('only the artists that actually changed are marked, and only after the notice', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });

  act(() => result.current.begin('known'));
  rerender({ status: 'ready', artists: SECOND });

  // Nothing is marked while the message is still up — the path is dimmed
  // underneath it, and a glow under a dim is invisible anyway.
  expect(result.current.changed.size).toBe(0);

  act(() => void vi.advanceTimersByTime(NOTICE_MIN_MS + 10));
  expect([...result.current.changed]).toEqual(['mid2']);
  // The two endpoints survived, so neither is marked.
  expect(result.current.changed.has('start')).toBe(false);
  expect(result.current.changed.has('end')).toBe(false);
});

test('the mark clears itself', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });
  act(() => result.current.begin('known'));
  rerender({ status: 'ready', artists: SECOND });
  act(() => void vi.advanceTimersByTime(NOTICE_MIN_MS + 10));
  expect(result.current.changed.size).toBe(1);

  act(() => void vi.advanceTimersByTime(GLOW_MS + 10));
  expect(result.current.changed.size).toBe(0);
});

// Browser Back undoing a bypass changes the path with no press behind it. There
// is no message owed, so the mark is the whole confirmation and must not wait
// on a floor that nothing started.
test('a path change nobody pressed marks immediately and shows no message', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });

  rerender({ status: 'ready', artists: SECOND });
  expect(result.current.notice).toBeNull();
  expect([...result.current.changed]).toEqual(['mid2']);
});

// Regression: the notice used to be cleared by an effect keyed on the artist
// list, so a rebuild returning an IDENTICAL path left nothing to change, the
// effect never re-ran, and the message sat on screen over a dimmed path
// forever. Reachable by pressing "Reset path" on an already-original path.
test('a rebuild that changes nothing marks nothing', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });
  act(() => result.current.begin('reset'));
  rerender({ status: 'ready', artists: FIRST });
  act(() => void vi.advanceTimersByTime(NOTICE_MIN_MS + 10));
  expect(result.current.changed.size).toBe(0);
  expect(result.current.notice).toBeNull();
});

test('an error drops the message rather than stranding it on screen', () => {
  const { result, rerender } = setup();
  rerender({ status: 'ready', artists: FIRST });
  act(() => result.current.begin('dislike'));
  rerender({ status: 'error', artists: [] });
  expect(result.current.notice).toBeNull();
});
