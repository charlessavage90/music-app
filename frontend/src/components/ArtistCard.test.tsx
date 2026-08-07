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
  // Both signals now sit behind the footer strip, so the tray is opened first.
  await user.click(screen.getByRole('button', { name: /reroute from here/i }));
  await user.click(screen.getByRole('button', { name: /steer away/i }));
  await user.click(screen.getByRole('button', { name: /dig deeper/i }));
  expect(onBypass).toHaveBeenNthCalledWith(1, 'bypass', 'dislike');
  expect(onBypass).toHaveBeenNthCalledWith(2, 'bypass', 'known');
});

test('the tray is shut until the strip is pressed, and shuts again', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(<ArtistCard artist={artist('tray')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);

  const strip = screen.getByRole('button', { name: /reroute from here/i });
  expect(strip).toHaveAttribute('aria-expanded', 'false');
  expect(screen.queryByRole('button', { name: /steer away/i })).not.toBeInTheDocument();

  await user.click(strip);
  expect(screen.getByRole('button', { name: /steer away/i })).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /dig deeper/i })).toBeInTheDocument();
  // The consequence neither label implies, said at the moment of choosing —
  // the explainer above the path can be dismissed and usually has been.
  expect(screen.getByText(/both options rebuild the whole journey/i)).toBeInTheDocument();

  // The design drew no way back out of the open tray. This is that way back:
  // the same control, relabelled — so it must genuinely close.
  const heading = screen.getByRole('button', { name: /how should this change/i });
  expect(heading).toHaveAttribute('aria-expanded', 'true');
  await user.click(heading);
  expect(screen.queryByRole('button', { name: /steer away/i })).not.toBeInTheDocument();
});

test('play disabled and card still present when clip is 204', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={artist('silent')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeDisabled());
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('a card with a clip says how long it is', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(<ArtistCard artist={artist('len')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(await screen.findByText(/0:30/i)).toBeInTheDocument();
});

// The duration is a claim about a clip. A card with nothing to play must not
// make it — that would read as "30 seconds of silence" rather than "nothing".
test('a card with no clip claims no duration', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={artist('nolen')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(await screen.findByText(/no preview available/i)).toBeInTheDocument();
  expect(screen.queryByText(/0:30/i)).not.toBeInTheDocument();
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

test('the button on the playing card pauses it instead of restarting it', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  const onPlay = vi.fn();
  const onToggle = vi.fn();
  render(
    <ArtistCard
      artist={artist('nowplaying')} isCurrent isPlaying
      onPlay={onPlay} onToggle={onToggle} onBypass={vi.fn()}
    />,
  );
  await user.click(screen.getByRole('button', { name: /pause/i }));
  expect(onToggle).toHaveBeenCalled();
  expect(onPlay).not.toHaveBeenCalled();
});

test('the button on a paused card resumes it instead of restarting it', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  const onPlay = vi.fn();
  const onToggle = vi.fn();
  render(
    <ArtistCard
      artist={artist('paused')} isCurrent isPlaying={false}
      onPlay={onPlay} onToggle={onToggle} onBypass={vi.fn()}
    />,
  );
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeEnabled());
  await user.click(screen.getByRole('button', { name: /play/i }));
  expect(onToggle).toHaveBeenCalled();
  expect(onPlay).not.toHaveBeenCalled();
});

test('an endpoint card stays bare — no strip, so no way to reach either signal', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(
    <ArtistCard
      artist={artist('endpoint')} isEndpoint isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.queryByRole('button', { name: /reroute from here/i })).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /steer away/i })).not.toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /dig deeper/i })).not.toBeInTheDocument();
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('an endpoint card carries its eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(
    <ArtistCard
      artist={artist('start')} isEndpoint endpointLabel="start" isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByText('Starting artist')).toBeInTheDocument();
});

test('a destination card carries the other eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(
    <ArtistCard
      artist={artist('dest')} isEndpoint endpointLabel="destination" isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByText('Destination artist')).toBeInTheDocument();
});

// UI-5: the e2e responsive spec used to find this by the Tailwind class
// `.font-semibold`, which this task moves. A test hook must not be a style hook.
test('the artist name carries a stable test hook', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c' });
  render(<ArtistCard artist={artist('hook')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(screen.getByTestId('artist-name')).toHaveTextContent('Miles Davis');
});
