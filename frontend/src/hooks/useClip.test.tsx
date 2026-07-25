import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { useClip } from './useClip';

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
