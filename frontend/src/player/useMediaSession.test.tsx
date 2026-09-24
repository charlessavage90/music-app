import { renderHook } from '@testing-library/react';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';
import { useMediaSession } from './useMediaSession';

// jsdom has neither navigator.mediaSession nor MediaMetadata, so both are
// stood in for here with the smallest shape the hook touches.
class FakeMetadata {
  init: { title: string; artist: string; artwork: Array<{ src: string }> };
  constructor(init: FakeMetadata['init']) {
    this.init = init;
  }
}

let handlers: Record<string, (() => void) | null>;
let ms: { metadata: FakeMetadata | null; playbackState: string; setActionHandler: (a: string, h: (() => void) | null) => void };

beforeEach(() => {
  handlers = {};
  ms = {
    metadata: null,
    playbackState: 'none',
    setActionHandler: (a, h) => { handlers[a] = h; },
  };
  Object.defineProperty(navigator, 'mediaSession', { value: ms, configurable: true });
  vi.stubGlobal('MediaMetadata', FakeMetadata);
});

afterEach(() => {
  delete (navigator as unknown as Record<string, unknown>).mediaSession;
  vi.unstubAllGlobals();
});

const controls = () => ({ play: vi.fn(), pause: vi.fn(), stop: vi.fn() });

test('names what is playing to the OS, and says whether it is', () => {
  const c = controls();
  const { rerender } = renderHook(
    ({ playing }) => useMediaSession({ artist: 'Herbie Hancock', title: 'Watermelon Man', artwork: 'c.jpg' }, playing, c),
    { initialProps: { playing: true } },
  );
  expect(ms.metadata?.init).toEqual({ title: 'Watermelon Man', artist: 'Herbie Hancock', artwork: [{ src: 'c.jpg' }] });
  expect(ms.playbackState).toBe('playing');
  rerender({ playing: false });
  expect(ms.playbackState).toBe('paused');
});

test('the OS controls drive the player, through the latest handlers', () => {
  const first = controls();
  const latest = controls();
  const { rerender } = renderHook(
    ({ c }) => useMediaSession({ artist: 'A', title: null, artwork: null }, true, c),
    { initialProps: { c: first } },
  );
  rerender({ c: latest });
  handlers.pause?.();
  handlers.play?.();
  handlers.stop?.();
  expect(first.pause).not.toHaveBeenCalled();
  expect(latest.pause).toHaveBeenCalledTimes(1);
  expect(latest.play).toHaveBeenCalledTimes(1);
  expect(latest.stop).toHaveBeenCalledTimes(1);
});

test('nothing current clears the metadata, and unmounting releases the controls', () => {
  const { rerender, unmount } = renderHook(
    ({ now }) => useMediaSession(now, false, controls()),
    { initialProps: { now: { artist: 'A', title: 'T', artwork: null } as { artist: string; title: string | null; artwork: string | null } | null } },
  );
  rerender({ now: null });
  expect(ms.metadata).toBeNull();
  expect(ms.playbackState).toBe('none');
  unmount();
  expect(handlers.play).toBeNull();
  expect(handlers.pause).toBeNull();
});

test('is a no-op where the browser has no media session', () => {
  delete (navigator as unknown as Record<string, unknown>).mediaSession;
  expect(() => renderHook(() => useMediaSession({ artist: 'A', title: null, artwork: null }, true, controls()))).not.toThrow();
});
