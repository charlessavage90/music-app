import type { Artist, Exclusion, Track } from './types';

const BASE = import.meta.env.VITE_API_BASE ?? '/api';

export class ApiError extends Error {
  constructor(public status: number) {
    super(`API error ${status}`);
    this.name = 'ApiError';
  }
}

export async function searchArtists(q: string, signal?: AbortSignal): Promise<Artist[]> {
  const r = await fetch(`${BASE}/artists/search?q=${encodeURIComponent(q)}`, { signal });
  if (!r.ok) throw new ApiError(r.status);
  return (await r.json()) as Artist[];
}

export async function buildPath(
  sources: string[],
  exclude: Exclusion[],
  signal?: AbortSignal,
): Promise<Artist[]> {
  const r = await fetch(`${BASE}/path`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ sources, exclude }),
    signal,
  });
  if (!r.ok) throw new ApiError(r.status);
  const data = (await r.json()) as { artists: Artist[] };
  return data.artists;
}

export async function getTrack(mbid: string, signal?: AbortSignal): Promise<Track | null> {
  const r = await fetch(`${BASE}/artists/${encodeURIComponent(mbid)}/track`, { signal });
  if (r.status === 204) return null;
  if (!r.ok) throw new ApiError(r.status);
  const d = (await r.json()) as { preview_url: string; title: string; cover_url: string };
  return { previewUrl: d.preview_url, title: d.title, coverUrl: d.cover_url };
}
