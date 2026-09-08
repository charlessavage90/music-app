import type { Artist, ArtistFacts, Exclusion, PathResult, StopRule, Track } from './types';

const BASE = import.meta.env.VITE_API_BASE ?? '/api';

/**
 * One id per page session, so a sequence of bypass presses reads as one walk.
 *
 * Deliberately NOT in the URL: path state is the shareable artifact and the
 * bug-report artifact, and an analytics id has no business in it. Resets on
 * reload, so one human walk can log as two — the full exclusion list is in
 * every event, so walks stay reconstructible regardless.
 */
const JOURNEY_ID = crypto.randomUUID().slice(0, 32);

function withJourney(headers: Record<string, string> = {}): Record<string, string> {
  return { ...headers, 'x-journey-id': JOURNEY_ID };
}

export class ApiError extends Error {
  status: number;
  constructor(status: number) {
    super(`API error ${status}`);
    this.name = 'ApiError';
    this.status = status;
  }
}

/**
 * A request we cut off ourselves, distinct from an abort the caller asked for.
 *
 * The distinction is load-bearing: `usePath` aborts on navigation and returns
 * early when it sees its own signal aborted, so a timeout implemented by
 * aborting the caller's signal would be swallowed and the page would sit on
 * "Building your path…" forever — the exact defect this fixes.
 */
export class TimeoutError extends Error {
  readonly ms: number;
  constructor(ms: number) {
    super(`Request timed out after ${ms}ms`);
    this.name = 'TimeoutError';
    this.ms = ms;
  }
}

/** Chosen, not measured. Path is longest: Dijkstra at depth plus a cold instance. */
const TIMEOUT_MS = { search: 8_000, path: 20_000, track: 10_000, artist: 8_000 } as const;

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  ms: number,
  caller?: AbortSignal,
): Promise<Response> {
  const internal = new AbortController();
  const relay = () => internal.abort();
  if (caller?.aborted) internal.abort();
  else caller?.addEventListener('abort', relay);

  let timedOut = false;
  const timer = setTimeout(() => {
    timedOut = true;
    internal.abort();
  }, ms);

  try {
    return await fetch(url, { ...init, signal: internal.signal });
  } catch (err) {
    if (timedOut) throw new TimeoutError(ms);
    throw err;
  } finally {
    clearTimeout(timer);
    caller?.removeEventListener('abort', relay);
  }
}

/**
 * The wire shape of an artist. snake_case, and every LUX-4 field optional.
 *
 * Optional rather than nullable because the api that serves them may be older
 * than this frontend — a deploy is two images, not one, and the frontend can
 * land first. An absent key and a null one must reach the app identically.
 */
interface ArtistWire {
  mbid: string;
  name: string;
  disambiguation: string;
  popularity: number;
  spotify_id?: string | null;
  apple_id?: string | null;
  facts?: ArtistFacts | null;
}

/**
 * The snake_case → camelCase boundary for artists, mirroring what `getTrack`
 * does for `candidate_count` and `buildPath` for `stop_rule`.
 *
 * Artists were previously cast straight through, which worked only because no
 * field was multi-word. LUX-4 adds the first three, so the cast would have
 * left `spotifyId` undefined on every card with nothing to notice it —
 * silently, since `undefined` renders as a search link exactly like a real
 * absence. Hence a real mapper and a test that a snake_case body maps.
 */
function artistFrom(d: ArtistWire): Artist {
  return {
    mbid: d.mbid,
    name: d.name,
    disambiguation: d.disambiguation,
    popularity: d.popularity,
    // `?? null` so a frontend deployed ahead of the API degrades to search
    // links rather than to `undefined` leaking into the components.
    spotifyId: d.spotify_id ?? null,
    appleId: d.apple_id ?? null,
    facts: d.facts ?? null,
  };
}

export async function searchArtists(q: string, signal?: AbortSignal): Promise<Artist[]> {
  const r = await fetchWithTimeout(
    `${BASE}/artists/search?q=${encodeURIComponent(q)}`, {}, TIMEOUT_MS.search, signal,
  );
  if (!r.ok) throw new ApiError(r.status);
  return ((await r.json()) as ArtistWire[]).map(artistFrom);
}

export async function buildPath(
  sources: string[],
  exclude: Exclusion[],
  signal?: AbortSignal,
): Promise<PathResult> {
  const r = await fetchWithTimeout(
    `${BASE}/path`,
    {
      method: 'POST',
      headers: withJourney({ 'content-type': 'application/json' }),
      body: JSON.stringify({ sources, exclude }),
    },
    TIMEOUT_MS.path,
    signal,
  );
  if (!r.ok) throw new ApiError(r.status);
  const data = (await r.json()) as {
    artists: ArtistWire[];
    stop_rule: StopRule;
    bypassed?: ArtistWire[];
    unresolved?: string[];
  };
  return {
    artists: data.artists.map(artistFrom),
    stopRule: data.stop_rule,
    bypassed: (data.bypassed ?? []).map(artistFrom),
    unresolved: data.unresolved ?? [],
  };
}

/**
 * One artist by MBID. In-memory on the server: no network, no pathfinding.
 *
 * Exists for the loading screen — a shared link carries only MBIDs, so without
 * this the two endpoint cards cannot be named until the path itself returns.
 */
export async function getArtist(mbid: string, signal?: AbortSignal): Promise<Artist> {
  const r = await fetchWithTimeout(
    `${BASE}/artists/${encodeURIComponent(mbid)}`, {}, TIMEOUT_MS.artist, signal,
  );
  if (!r.ok) throw new ApiError(r.status);
  return artistFrom((await r.json()) as ArtistWire);
}

export async function getTrack(
  mbid: string,
  index = 0,
  signal?: AbortSignal,
): Promise<Track | null> {
  // `index` is appended only when it is non-zero, so the overwhelmingly common
  // request stays byte-identical to what it was before LUX-3.
  const qs = index > 0 ? `?index=${index}` : '';
  const r = await fetchWithTimeout(
    `${BASE}/artists/${encodeURIComponent(mbid)}/track${qs}`,
    { headers: withJourney() },
    TIMEOUT_MS.track,
    signal,
  );
  if (r.status === 204) return null;
  if (!r.ok) throw new ApiError(r.status);
  const d = (await r.json()) as {
    preview_url: string;
    title: string;
    cover_url: string;
    candidate_count?: number;
  };
  return {
    previewUrl: d.preview_url,
    title: d.title,
    coverUrl: d.cover_url,
    // `?? 1` so a frontend deployed ahead of the API degrades to "one track,
    // no control" rather than hiding every card's clip.
    candidateCount: d.candidate_count ?? 1,
  };
}
