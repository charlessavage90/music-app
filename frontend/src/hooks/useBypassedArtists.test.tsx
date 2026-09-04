import { renderHook, waitFor } from '@testing-library/react';
import { expect, test, vi, afterEach } from 'vitest';
import * as client from '@/api/client';
import { ApiError } from '@/api/client';
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
