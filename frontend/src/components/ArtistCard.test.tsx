import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCard } from './ArtistCard';

// Distinct MBIDs per test: useClip caches by MBID at module scope, so reusing
// one id would bleed a resolved clip into the 204 test.
const artist = (mbid: string) => ({ mbid, name: 'Miles Davis', disambiguation: '', popularity: 1 });
afterEach(() => vi.restoreAllMocks());

test('fires the two bypass signals with the right reason', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  const onBypass = vi.fn();
  render(<ArtistCard artist={artist('bypass')} isPlaying={false} onPlay={vi.fn()} onBypass={onBypass} />);
  await user.click(screen.getByRole('button', { name: /not for me/i }));
  await user.click(screen.getByRole('button', { name: /know them/i }));
  expect(onBypass).toHaveBeenNthCalledWith(1, 'bypass', 'dislike');
  expect(onBypass).toHaveBeenNthCalledWith(2, 'bypass', 'known');
});

test('play disabled and card still present when clip is 204', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={artist('silent')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeDisabled());
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('play fires onPlay when a clip exists', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  const onPlay = vi.fn();
  render(<ArtistCard artist={artist('playable')} isPlaying={false} onPlay={onPlay} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeEnabled());
  await user.click(screen.getByRole('button', { name: /play/i }));
  expect(onPlay).toHaveBeenCalledWith('playable');
});
