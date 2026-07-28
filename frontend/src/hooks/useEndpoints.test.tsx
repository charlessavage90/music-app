import { renderHook, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { useEndpoints } from './useEndpoints';

const artist = (mbid: string, name: string) => ({ mbid, name, disambiguation: '', popularity: 0 });
afterEach(() => vi.restoreAllMocks());

test('resolves both endpoint artists', async () => {
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) =>
    artist(mbid, mbid === 'a' ? 'Nirvana' : 'Cocteau Twins'),
  );
  const { result } = renderHook(() => useEndpoints('a', 'b'));
  await waitFor(() => expect(result.current.from?.name).toBe('Nirvana'));
  expect(result.current.to?.name).toBe('Cocteau Twins');
});

// UI-7: a decorative lookup must never be able to turn a working page into an
// error page. The path request is the real one.
test('a failed lookup yields nulls and never throws', async () => {
  vi.spyOn(client, 'getArtist').mockRejectedValue(new Error('boom'));
  const { result } = renderHook(() => useEndpoints('a', 'b'));
  await waitFor(() => expect(client.getArtist).toHaveBeenCalled());
  expect(result.current.from).toBeNull();
  expect(result.current.to).toBeNull();
});

test('skip prevents the request entirely', async () => {
  const spy = vi.spyOn(client, 'getArtist').mockResolvedValue(artist('a', 'Nirvana'));
  renderHook(() => useEndpoints('a', 'b', true));
  await new Promise((r) => setTimeout(r, 20));
  expect(spy).not.toHaveBeenCalled();
});
