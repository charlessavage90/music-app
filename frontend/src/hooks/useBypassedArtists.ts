import { useEffect, useState } from 'react';
import * as client from '@/api/client';

export interface BypassedArtist {
  mbid: string;
  /** null once we know there is no name to show — a 404 or a failed lookup. */
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
      setNames(Object.fromEntries(mbids.map((m) => [m, cache.get(m) ?? null])));
      return;
    }
    void Promise.all(
      wanted.map(async (mbid) => {
        try {
          const artist = await client.getArtist(mbid);
          cache.set(mbid, artist.name);
        } catch {
          // A 404 is the interesting case and a transport failure is not
          // distinguishable here; both mean the row cannot state a name.
          cache.set(mbid, null);
        }
      }),
    ).then(() => {
      if (!active) return;
      setNames(Object.fromEntries(mbids.map((m) => [m, cache.get(m) ?? null])));
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
