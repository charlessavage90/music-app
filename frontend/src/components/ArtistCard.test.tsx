import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCard } from './ArtistCard';

// Distinct MBIDs per test: useClip caches by MBID at module scope, so reusing
// one id would bleed a resolved clip into the 204 test.
const artist = (mbid: string) => ({ mbid, name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null });
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

test('an endpoint card stays bare — no strip, so no way to reach the bypass control', async () => {
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

// A cycled index (clipIndex > 0) that comes back empty must not strand the
// card: candidateCount arrives on the TrackOut body, which a 204 does not
// carry, so the control that could cycle again also vanishes. Without a
// reset there is no way back to track 1 short of a reload.
test('a dead cycled index reports back so the caller can reset it', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const onDeadIndex = vi.fn();
  render(
    <ArtistCard
      artist={artist('dead-index')} isPlaying={false} clipIndex={2}
      onPlay={vi.fn()} onBypass={vi.fn()} onCycleClip={vi.fn()} onDeadIndex={onDeadIndex}
    />,
  );
  await screen.findByText(/no preview available/i);
  expect(onDeadIndex).toHaveBeenCalledWith('dead-index');
});

// The ordinary silent card above (index 0, no clip at all) must NOT be read
// as a dead index -- that would reset an index that was never cycled and is
// not a defect to recover from.
test('an ordinary silent card at index 0 does not report a dead index', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const onDeadIndex = vi.fn();
  render(
    <ArtistCard
      artist={artist('silent-not-dead')} isPlaying={false}
      onPlay={vi.fn()} onBypass={vi.fn()} onCycleClip={vi.fn()} onDeadIndex={onDeadIndex}
    />,
  );
  await screen.findByText(/no preview available/i);
  expect(onDeadIndex).not.toHaveBeenCalled();
});

// --- LUX-4 ------------------------------------------------------------------

test('a card carries links out to both streaming services', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={{ ...artist('links'), spotifyId: 'sp', appleId: null }}
      isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByRole('link', { name: /on Spotify/i })).toHaveAttribute(
    'href', 'https://open.spotify.com/artist/sp',
  );
  // No apple id: a SEARCH link, never a missing button.
  expect(screen.getByRole('link', { name: /on Apple Music/i })).toHaveAttribute(
    'href', 'https://music.apple.com/search?term=Miles%20Davis',
  );
});

// An endpoint card is an artist you chose, so you probably know them — but the
// links cost a line and still answer "where do I go to hear more", so they
// render there too. Pinned because it is a decision, not an accident.
test('endpoint cards carry the links too', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={artist('endpoint-links')} isPlaying={false} isEndpoint
      endpointLabel="start" onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getAllByRole('link')).toHaveLength(2);
});

// A silent card is one whose clip never resolved. The links are the ONLY way
// left to hear the artist at all, so they must not be tied to playability.
test('a card with no clip still carries the links', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(
    <ArtistCard artist={artist('silent-links')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />,
  );
  await waitFor(() => expect(screen.getByText('No preview available')).toBeInTheDocument());
  expect(screen.getAllByRole('link')).toHaveLength(2);
});

test('a card shows the artist facts line', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={{
        ...artist('facts'), disambiguation: 'US jazz trumpeter',
        facts: { type: 'Person', country: 'US', area: 'United States',
                 begin: '1926', end: '1991', ended: true },
      }}
      isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()}
    />,
  );
  expect(screen.getByText(/US jazz trumpeter/)).toBeInTheDocument();
  expect(screen.getByText(/1926–1991/)).toBeInTheDocument();
});

// The state production is in until the LUX-4 artifact deploys: the api serves
// nulls for everything. The card must be exactly what it was before.
test('a card with no facts at all is unchanged', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistCard artist={artist('no-facts')} isPlaying={false} onPlay={vi.fn()} onBypass={vi.fn()} />);
  expect(screen.getByTestId('artist-name')).toHaveTextContent('Miles Davis');
  expect(screen.queryByText(/unknown/i)).not.toBeInTheDocument();
  expect(screen.queryByText(' · ')).not.toBeInTheDocument();
});
