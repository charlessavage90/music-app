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

test('buildPath returns artists and the stop rule, and sends sources+exclude', async () => {
  const fetch = mockFetch(200, {
    artists: [{ mbid: 'x', name: 'A', disambiguation: '', popularity: 0.5 }],
    stop_rule: 'forced',
  });
  vi.stubGlobal('fetch', fetch);
  const exclude = [{ id: 'z', reason: 'dislike' as const }];
  const result = await buildPath(['a', 'b'], exclude);
  expect(result.artists).toHaveLength(1);
  expect(result.stopRule).toBe('forced');
  const body = JSON.parse((fetch.mock.calls[0][1] as RequestInit).body as string);
  expect(body).toEqual({ sources: ['a', 'b'], exclude });
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

test('sends a journey id header on both calls', async () => {
  const fetchMock = vi.fn().mockResolvedValue({
    ok: true, status: 200, json: async () => ({ artists: [], stop_rule: 'natural' }),
  });
  vi.stubGlobal('fetch', fetchMock);

  await buildPath(['a', 'b'], []);
  const headers = fetchMock.mock.calls[0][1].headers;
  expect(headers['x-journey-id']).toMatch(/^[A-Za-z0-9-]{8,64}$/);
});
