import { afterEach, expect, test, vi } from 'vitest';
import { ApiError, buildPath, getTrack, searchArtists } from './client';

function mockFetch(status: number, body: unknown) {
  return vi.fn().mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response);
}

afterEach(() => vi.unstubAllGlobals());

test('searchArtists returns artists', async () => {
  vi.stubGlobal('fetch', mockFetch(200, [
    { mbid: 'a', name: 'Radiohead', disambiguation: '', popularity: 1.0 },
  ]));
  const out = await searchArtists('radio');
  expect(out[0].name).toBe('Radiohead');
});

test('buildPath unwraps the artists array and sends sources+exclude', async () => {
  const fetch = mockFetch(200, { artists: [{ mbid: 'x', name: 'A', disambiguation: '', popularity: 0.5 }] });
  vi.stubGlobal('fetch', fetch);
  const out = await buildPath(['a', 'b'], [{ id: 'z', reason: 'dislike' }]);
  expect(out).toHaveLength(1);
  const body = JSON.parse((fetch.mock.calls[0][1] as RequestInit).body as string);
  expect(body).toEqual({ sources: ['a', 'b'], exclude: [{ id: 'z', reason: 'dislike' }] });
});

test('getTrack maps snake_case to camelCase', async () => {
  vi.stubGlobal('fetch', mockFetch(200, { preview_url: 'u', title: 't', cover_url: 'c' }));
  const track = await getTrack('a');
  expect(track).toEqual({ previewUrl: 'u', title: 't', coverUrl: 'c' });
});

test('getTrack returns null on 204', async () => {
  vi.stubGlobal('fetch', mockFetch(204, null));
  expect(await getTrack('a')).toBeNull();
});

test('buildPath throws ApiError with status on 409', async () => {
  vi.stubGlobal('fetch', mockFetch(409, {}));
  await expect(buildPath(['a', 'b'], [])).rejects.toMatchObject({ status: 409 } as Partial<ApiError>);
});
