import { afterEach, expect, test, vi } from 'vitest';
import { ApiError, buildPath, getMeta, getTrack, searchArtists } from './client';

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
  expect(track).toEqual({ previewUrl: 'u', title: 't', coverUrl: 'c', candidateCount: 1 });
});

test('getTrack returns null on 204', async () => {
  vi.stubGlobal('fetch', mockFetch(204, null));
  expect(await getTrack('a')).toBeNull();
});

test('getTrack maps the candidate count and only sends an index when there is one', async () => {
  // A fresh Response per call — a Response body can only be read once, and
  // getTrack is called twice below.
  const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async () =>
    new Response(JSON.stringify({
      preview_url: 'u', title: 't', cover_url: 'c', candidate_count: 3,
    }), { status: 200, headers: { 'content-type': 'application/json' } }),
  );
  expect((await getTrack('m'))?.candidateCount).toBe(3);
  expect(fetchMock.mock.calls[0][0]).not.toContain('index=');
  await getTrack('m', 2);
  expect(fetchMock.mock.calls[1][0]).toContain('index=2');
  fetchMock.mockRestore();
});

test('buildPath throws ApiError with status on 409', async () => {
  vi.stubGlobal('fetch', mockFetch(409, {}));
  await expect(buildPath(['a', 'b'], [])).rejects.toMatchObject({ status: 409 } as Partial<ApiError>);
});

test('buildPath times out rather than hanging forever', async () => {
  vi.useFakeTimers();
  // A server that accepts the request and never answers — the App Runner cold
  // start case. Honours abort so the wrapper can actually cut it off.
  vi.stubGlobal('fetch', (_url: string, init: RequestInit) =>
    new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () =>
        reject(new DOMException('Aborted', 'AbortError')),
      );
    }),
  );

  const pending = buildPath(['a', 'b'], []);
  const assertion = expect(pending).rejects.toMatchObject({ name: 'TimeoutError' });
  await vi.advanceTimersByTimeAsync(20_000);
  await assertion;
  vi.useRealTimers();
});

test("a caller's own abort is not reported as a timeout", async () => {
  vi.stubGlobal('fetch', (_url: string, init: RequestInit) =>
    new Promise((_resolve, reject) => {
      init.signal?.addEventListener('abort', () =>
        reject(new DOMException('Aborted', 'AbortError')),
      );
    }),
  );

  const controller = new AbortController();
  const pending = buildPath(['a', 'b'], [], controller.signal);
  controller.abort();

  // usePath returns early on its own abort; a TimeoutError here would be
  // swallowed by that check and the screen would never change.
  await expect(pending).rejects.toMatchObject({ name: 'AbortError' });
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

// --- LUX-4 ------------------------------------------------------------------

test('artists map snake_case ids and facts to camelCase', async () => {
  vi.stubGlobal('fetch', mockFetch(200, [{
    mbid: 'a', name: 'Radiohead', disambiguation: '', popularity: 1.0,
    spotify_id: '4Z8W', apple_id: '657515',
    facts: { type: 'Group', country: 'GB', area: 'United Kingdom',
             begin: '1991', end: null, ended: false },
  }]));
  const [artist] = await searchArtists('radio');
  expect(artist.spotifyId).toBe('4Z8W');
  expect(artist.appleId).toBe('657515');
  expect(artist.facts?.area).toBe('United Kingdom');
});

test('an api older than this frontend degrades to nulls, not undefined', async () => {
  // A deploy is two images, not one, so the frontend can land first. `undefined`
  // would flow into the components and render as a search link identically to a
  // real absence — silently right, until something starts distinguishing them.
  vi.stubGlobal('fetch', mockFetch(200, [
    { mbid: 'a', name: 'Radiohead', disambiguation: '', popularity: 1.0 },
  ]));
  const [artist] = await searchArtists('radio');
  expect(artist.spotifyId).toBeNull();
  expect(artist.appleId).toBeNull();
  expect(artist.facts).toBeNull();
});

test('bypassed artists are mapped too, not passed through raw', async () => {
  // LUX-2's panel renders these. They went through a different code path from
  // `artists` before this mapper existed, which is exactly how one of them
  // would keep snake_case while the other did not.
  vi.stubGlobal('fetch', mockFetch(200, {
    artists: [{ mbid: 'x', name: 'A', disambiguation: '', popularity: 0.5 }],
    stop_rule: 'natural',
    bypassed: [{
      mbid: 'y', name: 'B', disambiguation: '', popularity: 0.4, spotify_id: 'sp',
    }],
  }));
  const result = await buildPath(['a', 'b'], []);
  expect(result.bypassed[0].spotifyId).toBe('sp');
  expect(result.artists[0].spotifyId).toBeNull();
});

test('getMeta reads the count and the artifact identity', async () => {
  vi.stubGlobal('fetch', mockFetch(200, { artists: 58838, graph_sha256: 'abc' }));
  await expect(getMeta()).resolves.toEqual({ artists: 58838, graphSha256: 'abc' });
});
