import type { BypassReason, Exclusion } from '@/api/types';

const KEY: Record<BypassReason, string> = { dislike: 'dislike', known: 'known' };

/**
 * How many exclusions the link was written with (issue #187).
 *
 * A link cut in transit — a chat client's length limit, a half-copied address
 * — that loses WHOLE ids leaves every survivor well-formed, so the server has
 * nothing to object to and the journey is silently a different one. The count
 * is the one thing the cut cannot take with it, because it is written FIRST:
 * truncation removes the tail of a URL, and the ids are the tail.
 *
 * Deliberately first, not last. A trailing marker is removed by the very cut
 * it is meant to detect, and its absence is indistinguishable from a link
 * shared before the marker existed — so it could never flag anything.
 */
export const COUNT_KEY = 'n';

function list(params: URLSearchParams, reason: BypassReason): string[] {
  const raw = params.get(KEY[reason]);
  return raw ? raw.split(',').filter(Boolean) : [];
}

export function decodeExclusions(params: URLSearchParams): Exclusion[] {
  const out: Exclusion[] = [];
  for (const id of list(params, 'dislike')) out.push({ id, reason: 'dislike' });
  for (const id of list(params, 'known')) out.push({ id, reason: 'known' });
  return out;
}

/** The same parameters with the count re-derived and placed first. */
function withCount(params: URLSearchParams): URLSearchParams {
  const n = decodeExclusions(params).length;
  const out = new URLSearchParams();
  if (n > 0) out.set(COUNT_KEY, String(n));
  for (const [k, v] of params) if (k !== COUNT_KEY) out.append(k, v);
  return out;
}

export function addExclusion(
  params: URLSearchParams,
  mbid: string,
  reason: BypassReason,
): URLSearchParams {
  const next = new URLSearchParams(params);
  const ids = list(params, reason);
  if (!ids.includes(mbid)) ids.push(mbid);
  next.set(KEY[reason], ids.join(','));
  return withCount(next);
}

export function clearExclusions(params: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(params);
  next.delete('dislike');
  next.delete('known');
  next.delete(COUNT_KEY);
  return next;
}

/** A link that arrived with fewer exclusions than it was written with. */
export interface LinkDamage {
  /** The count the link was written with; null when the count itself is cut or garbled. */
  expected: number | null;
  /** How many exclusions actually arrived. */
  found: number;
}

/**
 * Whether this link arrived whole, as far as its count can tell.
 *
 * Null means intact OR unverifiable: a link with no count predates it, and is
 * trusted exactly as it was before — flagging it would call every link shared
 * before issue #187 broken. A cut INSIDE the last id is not this function's to
 * catch: the count still matches, and the server reports the fragment as an
 * unknown id (RouteHistory's "An artist no longer in the map").
 */
export function linkIntegrity(params: URLSearchParams): LinkDamage | null {
  const raw = params.get(COUNT_KEY);
  if (raw === null) return null;
  const found = decodeExclusions(params).length;
  if (!/^\d+$/.test(raw)) return { expected: null, found };
  const expected = Number(raw);
  return expected === found ? null : { expected, found };
}
