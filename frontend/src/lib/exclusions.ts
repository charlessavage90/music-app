import type { BypassReason, Exclusion } from '@/api/types';

const KEY: Record<BypassReason, string> = { dislike: 'dislike', known: 'known' };

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

export function addExclusion(
  params: URLSearchParams,
  mbid: string,
  reason: BypassReason,
): URLSearchParams {
  const next = new URLSearchParams(params);
  const ids = list(params, reason);
  if (!ids.includes(mbid)) ids.push(mbid);
  next.set(KEY[reason], ids.join(','));
  return next;
}

export function clearExclusions(params: URLSearchParams): URLSearchParams {
  const next = new URLSearchParams(params);
  next.delete('dislike');
  next.delete('known');
  return next;
}
