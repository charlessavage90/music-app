import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { resolveFreshUrl, useClip } from './useClip';

afterEach(() => vi.restoreAllMocks());

function Harness({ mbid }: { mbid: string }) {
  const c = useClip(mbid);
  return <div data-testid="c">{c.status}:{c.track?.title ?? ''}</div>;
}

test('loads a clip and exposes the track', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(<Harness mbid="miles" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:So What'));
});

test('204 becomes status none', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<Harness mbid="silent" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('none:'));
});

test('caches by mbid — second mount does not refetch', async () => {
  const spy = vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  const { unmount } = render(<Harness mbid="cached" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:T'));
  unmount();
  render(<Harness mbid="cached" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:T'));
  expect(spy).toHaveBeenCalledTimes(1);
});

test('resolveFreshUrl re-signs a URL held longer than a signature lasts', async () => {
  // The defect this whole seam exists for: a card that stays mounted keeps the URL
  // it was drawn with, and a Deezer signature lasts 15 minutes (execution log §15).
  // Pressing play must not hand the player that URL.
  vi.spyOn(Date, 'now').mockReturnValue(0);
  const spy = vi.spyOn(client, 'getTrack');
  spy.mockResolvedValue({ previewUrl: 'signed-at-zero', title: 'T', coverUrl: 'c' });

  expect(await resolveFreshUrl('mounted')).toBe('signed-at-zero');

  spy.mockResolvedValue({ previewUrl: 'signed-later', title: 'T', coverUrl: 'c' });
  vi.spyOn(Date, 'now').mockReturnValue(20 * 60 * 1000); // 20 minutes on one card

  expect(await resolveFreshUrl('mounted')).toBe('signed-later');
  expect(spy).toHaveBeenCalledTimes(2);
});

test('resolveFreshUrl reuses a URL signed moments ago rather than refetching', async () => {
  // Deezer rate-limits and a path view already fires 8-10 lookups, so pressing play
  // twice in a row must not cost two round trips.
  vi.spyOn(Date, 'now').mockReturnValue(0);
  const spy = vi.spyOn(client, 'getTrack');
  spy.mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });

  expect(await resolveFreshUrl('impatient')).toBe('u');
  vi.spyOn(Date, 'now').mockReturnValue(30 * 1000);
  expect(await resolveFreshUrl('impatient')).toBe('u');

  expect(spy).toHaveBeenCalledTimes(1);
});

test('resolveFreshUrl returns null for an artist with no clip', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  expect(await resolveFreshUrl('silent-resolve')).toBeNull();
});

test('resolveFreshUrl returns null rather than throwing when the lookup fails', async () => {
  vi.spyOn(client, 'getTrack').mockRejectedValue(new Error('rate limited'));
  expect(await resolveFreshUrl('failing-resolve')).toBeNull();
});

test('refetches a clip old enough that its signed URL has expired', async () => {
  // C2, browser side: this cache holds the signed preview URL too, so on a tab
  // left open it serves dead audio exactly like the 30-day server cache did.
  vi.spyOn(Date, 'now').mockReturnValue(0);
  const spy = vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });

  const { unmount } = render(<Harness mbid="longopen" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:T'));
  unmount();

  vi.spyOn(Date, 'now').mockReturnValue(45 * 60 * 1000); // 45 minutes later
  render(<Harness mbid="longopen" />);
  await waitFor(() => expect(screen.getByTestId('c')).toHaveTextContent('ready:T'));
  expect(spy).toHaveBeenCalledTimes(2);
});
