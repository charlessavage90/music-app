import { renderHook, waitFor } from '@testing-library/react';
import { expect, test, vi, afterEach } from 'vitest';
import * as client from '@/api/client';
import { ApiError, TimeoutError } from '@/api/client';
import { useBypassedArtists } from './useBypassedArtists';

afterEach(() => vi.restoreAllMocks());

test('resolves each bypassed id to a name, in the order given', async () => {
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) => ({
    mbid, name: mbid === 'a' ? 'Alice Coltrane' : 'Sun Ra', disambiguation: '', popularity: 1,
  }));
  const { result } = renderHook(() => useBypassedArtists(['a', 'b']));
  await waitFor(() => expect(result.current[0].loading).toBe(false));
  expect(result.current.map((x) => x.name)).toEqual(['Alice Coltrane', 'Sun Ra']);
});

// LUX-D2: a shared link can carry an id the graph does not have. The row must
// resolve to a stated absence rather than hanging on "loading" forever.
test('an artist the graph does not have resolves to a null name, not a hang', async () => {
  vi.spyOn(client, 'getArtist').mockRejectedValue(new ApiError(404));
  const { result } = renderHook(() => useBypassedArtists(['gone']));
  await waitFor(() => expect(result.current[0].loading).toBe(false));
  expect(result.current[0].name).toBeNull();
});

// Fix round 1: a 404 is a durable fact about the graph, but a timeout is not.
// Caching a timeout as "no name" would permanently mislabel a real artist —
// the cache is module-scope and never invalidated. A transport failure must
// stay in `loading` (never claim the artist is gone) and must not poison the
// cache, so a later lookup of the same id can still succeed.
test('a timeout does not get cached as an absence, and a later attempt can still resolve the name', async () => {
  const getArtist = vi
    .spyOn(client, 'getArtist')
    .mockRejectedValueOnce(new TimeoutError(8_000))
    .mockResolvedValueOnce({ mbid: 'flaky', name: 'Sun Ra', disambiguation: '', popularity: 1 });

  const { result, unmount } = renderHook(() => useBypassedArtists(['flaky']));
  await waitFor(() => expect(getArtist).toHaveBeenCalledTimes(1));
  // Still unresolved — a timeout is not a claim that the artist is gone, and
  // the row must not render "no longer in the map" on the strength of it.
  expect(result.current[0].loading).toBe(true);
  expect(result.current[0].name).toBeNull();

  // A fresh mount (e.g. navigating back to a shared link) is this hook's only
  // retry path, since the effect does not re-fire for an unchanged id list.
  unmount();
  const { result: retried } = renderHook(() => useBypassedArtists(['flaky']));
  await waitFor(() => expect(retried.current[0].loading).toBe(false));
  expect(getArtist).toHaveBeenCalledTimes(2);
  expect(retried.current[0].name).toBe('Sun Ra');
});
