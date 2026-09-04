import { useEffect, useState } from 'react';
import * as client from '@/api/client';
import { ApiError } from '@/api/client';

export interface BypassedArtist {
  mbid: string;
  /** null once we know there is no name to show — a confirmed 404 only. */
  name: string | null;
  loading: boolean;
}

/**
 * Names for artists a bypass removed from the path.
 *
 * A bypassed artist is HARD-EXCLUDED, so they are absent from the path response
 * and there is nowhere else to read their name from. One in-memory lookup per
 * id against GET /api/artists/{mbid} — no pathfinding, no network beyond the
 * API — and it works on a cold load of a shared link, which is the case the
 * panel exists to serve.
 *
 * Only a genuine 404 is cached as "this artist has no name" (LUX-D2: it is a
 * durable fact about the graph). A timeout or any other transport failure is
 * NOT cached — the cache is module-scope and never invalidated, so caching a
 * blip there would permanently mislabel a real, present artist as "no longer
 * in the map" for the rest of the session, for every panel that looks up the
 * same id. Those ids are simply left uncached, so the row stays in `loading`
 * (rendered as "…", never a false claim) and a later mount of this hook for
 * the same id will retry — no cache entry means it lands back in `wanted`.
 *
 * DELIBERATELY TEMPORARY (LUX-2a). LUX-2b puts these artists on the path
 * response itself and this hook is deleted with its round trips. It ships first
 * so the panel lands without an API change to review alongside it.
 */
const cache = new Map<string, string | null>();

export function useBypassedArtists(mbids: string[]): BypassedArtist[] {
  const key = mbids.join('|');
  const [names, setNames] = useState<Record<string, string | null>>({});

  useEffect(() => {
    let active = true;
    const wanted = mbids.filter((m) => !cache.has(m));
    if (wanted.length === 0) {
      setNames(Object.fromEntries(mbids.filter((m) => cache.has(m)).map((m) => [m, cache.get(m) ?? null])));
      return;
    }
    void Promise.all(
      wanted.map(async (mbid) => {
        try {
          const artist = await client.getArtist(mbid);
          cache.set(mbid, artist.name);
        } catch (err) {
          // A 404 means the graph does not have this artist — durable, safe to
          // cache. Anything else (a timeout, a 5xx, a dropped connection) says
          // nothing about whether the artist exists, so leave it uncached and
          // let a later mount retry rather than asserting an absence we don't
          // actually know.
          if (err instanceof ApiError && err.status === 404) {
            cache.set(mbid, null);
          }
        }
      }),
    ).then(() => {
      if (!active) return;
      setNames((prev) => {
        const next = { ...prev };
        for (const m of mbids) {
          if (cache.has(m)) next[m] = cache.get(m) ?? null;
        }
        return next;
      });
    });
    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  return mbids.map((mbid) => ({
    mbid,
    name: names[mbid] ?? null,
    loading: !(mbid in names),
  }));
}
