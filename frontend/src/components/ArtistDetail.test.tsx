import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistDetail } from './ArtistDetail';

// Distinct MBIDs per test, as in ArtistCard.test.tsx: useClip caches by
// `mbid:index` at module scope with a ten-minute TTL and nothing clears it
// between tests, so a shared id would serve the first test's candidateCount
// to every later one.
const air = (mbid: string) => ({
  mbid, name: 'Air', disambiguation: 'French duo', popularity: 0.5,
  spotifyId: '1', appleId: null,
  facts: { type: 'Group', country: 'FR', area: 'Versailles', begin: '1995', end: null, ended: false },
});
const base = (mbid: string) => ({
  artist: air(mbid), index: 2, total: 6, isEndpoint: false, clipIndex: 0,
  isPlaying: false, isCurrent: false,
  onPlay: vi.fn(), onToggle: vi.fn(), onCycleClip: vi.fn(), onBypass: vi.fn(), onClose: vi.fn(),
});
afterEach(() => vi.restoreAllMocks());

test('says which stop this is, shows the facts, and offers both services', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'La Femme', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistDetail {...base('detail-facts')} />);
  // UXR-D10's currency: every artist including the two you chose, 1-based.
  expect(screen.getByText('Stop 3 of 6')).toBeInTheDocument();
  // The facts line is ArtistInfo, unchanged and with its own tests — what is
  // asserted here is only that this component mounts it.
  expect(screen.getByText(/French duo/)).toBeInTheDocument();
  expect(screen.getByText(/Versailles/)).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Air on Spotify' })).toHaveAttribute(
    'href', 'https://open.spotify.com/artist/1',
  );
  expect(screen.getByRole('link', { name: 'Air on Apple Music' })).toHaveAttribute(
    'href', 'https://music.apple.com/search?term=Air',
  );
});

test('one bypass control, on interior artists only, and it fires the known signal', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const onBypass = vi.fn();
  render(<ArtistDetail {...base('detail-bypass')} onBypass={onBypass} />);
  await user.click(screen.getByRole('button', { name: /dig deeper/i }));
  expect(onBypass).toHaveBeenCalledWith('detail-bypass');
});

test('an endpoint gets no bypass control', () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistDetail {...base('detail-endpoint')} isEndpoint />);
  expect(screen.queryByRole('button', { name: /dig deeper/i })).not.toBeInTheDocument();
});

// An endpoint is an artist you chose, so you probably know them — but the links
// still answer "where do I go to hear more", so they render there too. Pinned
// because it is a decision (LUX-4), not an accident, and it moved here with them.
test('an endpoint detail still carries both links', () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistDetail {...base('detail-endpoint-links')} isEndpoint />);
  expect(screen.getByRole('link', { name: 'Air on Spotify' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Air on Apple Music' })).toBeInTheDocument();
});

// REQ-45, moved here from the card with the control: a press routes to a MORE
// OBSCURE similar artist, so a label that reads as rejection is a defect, not a
// wording preference.
test('the bypass control does not read as rejecting the artist', () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistDetail {...base('detail-wording')} />);
  expect(screen.queryByText(/not for me|dislike|reject|no thanks|steer away/i)).not.toBeInTheDocument();
  // The consequence a short label cannot carry, stated where the choice is made.
  expect(screen.getByText(/rebuilds the whole journey/i)).toBeInTheDocument();
  expect(screen.queryByText(/recommended/i)).not.toBeInTheDocument(); // UXR-D16
});

test('"Try another track" appears when there is another track', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 3 });
  const onCycleClip = vi.fn();
  render(<ArtistDetail {...base('detail-cycle')} onCycleClip={onCycleClip} />);
  await user.click(await screen.findByRole('button', { name: /try another track/i }));
  expect(onCycleClip).toHaveBeenCalledWith(3);
});

// Thin catalogues are exactly the artists this app exists to deliver
// (TCE-/TCR-). A control that cannot do anything is worse than no control.
test('offers nothing to cycle to when the artist has one track', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'Only', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistDetail {...base('detail-single')} />);
  expect(await screen.findByText('Only')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /try another track/i })).not.toBeInTheDocument();
});

test('offers nothing to cycle to on a silent artist', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistDetail {...base('detail-silent')} />);
  expect(await screen.findByText(/no preview available/i)).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: /try another track/i })).not.toBeInTheDocument();
});

// The dock has no scrim and no Escape — DetailSheet owns those — so this
// button is the only way to close the detail at lg.
test('the close button reports the close', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const onClose = vi.fn();
  render(<ArtistDetail {...base('detail-close')} onClose={onClose} />);
  await user.click(screen.getByRole('button', { name: /close/i }));
  expect(onClose).toHaveBeenCalledTimes(1);
});

test('the play button on the playing detail pauses instead of restarting', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  const onPlay = vi.fn();
  const onToggle = vi.fn();
  render(<ArtistDetail {...base('detail-toggle')} isCurrent isPlaying onPlay={onPlay} onToggle={onToggle} />);
  await user.click(screen.getByRole('button', { name: /pause/i }));
  expect(onToggle).toHaveBeenCalled();
  expect(onPlay).not.toHaveBeenCalled();
});
