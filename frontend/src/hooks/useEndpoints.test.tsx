import { renderHook, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { useEndpoints } from './useEndpoints';

const artist = (mbid: string, name: string) => ({ mbid, name, disambiguation: '', popularity: 0, spotifyId: null, appleId: null, facts: null });
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
//
// ⚠ Deliberately MIXED — one lookup fails, one succeeds — and that is the whole
// point of the test. The obvious version fails BOTH and asserts both are null,
// and it is vacuous: when Promise.all rejects, .then never runs, so state stays
// at its INITIAL value of null, which is what the assertion reads. It passes
// against code with no error handling at all. Caught by mutation at closeout
// 2026-07-28.
//
// Asserting that the SURVIVING lookup still lands is what cannot be faked: it
// only happens if the failure was swallowed per-promise rather than taking the
// pair down with it.
test('one failed lookup does not take the other down', async () => {
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) => {
    if (mbid === 'b') throw new Error('boom');
    return artist(mbid, 'Nirvana');
  });
  const { result } = renderHook(() => useEndpoints('a', 'b'));
  await waitFor(() => expect(result.current.from?.name).toBe('Nirvana'));
  expect(result.current.to).toBeNull();
});

test('skip prevents the request entirely', async () => {
  const spy = vi.spyOn(client, 'getArtist').mockResolvedValue(artist('a', 'Nirvana'));
  renderHook(() => useEndpoints('a', 'b', true));
  await new Promise((r) => setTimeout(r, 20));
  expect(spy).not.toHaveBeenCalled();
});
