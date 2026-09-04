import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCard } from './ArtistCard';

// Distinct MBIDs per test: useClip caches by MBID at module scope, so reusing
// one id would bleed a resolved clip into the 204 test.
const artist = (mbid: string) => ({ mbid, name: 'Miles Davis', disambiguation: '', popularity: 1 });
afterEach(() => vi.restoreAllMocks());

test('one bypass control, and it fires the known signal', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  const onBypass = vi.fn();
  render(<ArtistCard artist={artist('bypass')} isPlaying={false} onPlay={vi.fn()} onBypass={onBypass} />);

  // LUX-1: there is no tray to open. The footer strip IS the control.
  await user.click(screen.getByRole('button', { name: /dig deeper/i }));
  expect(onBypass).toHaveBeenCalledTimes(1);
  expect(onBypass).toHaveBeenCalledWith('bypass');
});

// REQ-45: a press routes to a MORE OBSCURE similar artist, so a label that reads
// as rejection is a defect, not a wording preference. This test is the guard.
test('the bypass control does not read as rejecting the artist', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistCard artist={artist('wording')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(screen.queryByRole('button', { name: /steer away/i })).not.toBeInTheDocument();
  expect(screen.queryByText(/not for me|dislike|reject|no thanks/i)).not.toBeInTheDocument();
  // The consequence a short label cannot carry, stated where the choice is made.
  expect(screen.getByText(/rebuilds the whole journey/i)).toBeInTheDocument();
});

test('play disabled and card still present when clip is 204', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={artist('silent')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeDisabled());
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('a card with a clip says how long it is', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
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
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  const onPlay = vi.fn();
  render(<ArtistCard artist={artist('playable')} isPlaying={false} onPlay={onPlay} onBypass={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeEnabled());
  await user.click(screen.getByRole('button', { name: /play/i }));
  expect(onPlay).toHaveBeenCalledWith('playable');
});

test('the button on the playing card pauses it instead of restarting it', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
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
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
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
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={artist('endpoint')} isEndpoint isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.queryByRole('button', { name: /dig deeper/i })).not.toBeInTheDocument();
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('an endpoint card carries its eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={artist('start')} isEndpoint endpointLabel="start" isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByText('Starting artist')).toBeInTheDocument();
});

test('a destination card carries the other eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
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
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistCard artist={artist('hook')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(screen.getByTestId('artist-name')).toHaveTextContent('Miles Davis');
});

test('offers another track when the artist has more than one', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({
    previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 4,
  });
  const onCycleClip = vi.fn();
  render(
    <ArtistCard
      artist={artist('cycle')} isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()} onCycleClip={onCycleClip}
    />,
  );
  await user.click(await screen.findByRole('button', { name: /try another track/i }));
  expect(onCycleClip).toHaveBeenCalledWith(4);
});

// Thin catalogues are exactly the artists this app exists to deliver (TCE-/TCR-).
// A control that cannot do anything is worse than no control.
test('offers nothing to cycle to when the artist has one track', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({
    previewUrl: 'u', title: 'Only', coverUrl: 'c', candidateCount: 1,
  });
  render(
    <ArtistCard
      artist={artist('single')} isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()} onCycleClip={vi.fn()}
    />,
  );
  expect(await screen.findByText('Only')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /try another track/i })).not.toBeInTheDocument();
});

test('offers nothing to cycle to on a silent card', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(
    <ArtistCard
      artist={artist('silent-cycle')} isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()} onCycleClip={vi.fn()}
    />,
  );
  await screen.findByText(/no preview available/i);
  expect(screen.queryByRole('button', { name: /try another track/i })).not.toBeInTheDocument();
});
