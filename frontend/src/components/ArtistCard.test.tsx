import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCard } from './ArtistCard';

// Distinct MBIDs per test: useClip caches by MBID at module scope, so reusing
// one id would bleed a resolved clip into the 204 test.
const artist = (mbid: string) => ({ mbid, name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null });
afterEach(() => vi.restoreAllMocks());

// UXR-D2. The card is the LISTENING surface; everything you want once the clip
// has done its job lives in the detail. The facts line, both streaming links,
// "Try another track" and "Dig deeper" left this component on 2026-09-08 — each
// is re-asserted on ArtistDetail in UXR-T7, and both moved components keep
// their own test files (ArtistInfo.test.tsx, StreamingLinks.test.tsx).
test('the detail button carries the artist name, and the card carries no links or facts itself', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 3 });
  const onDetail = vi.fn();
  render(
    <ArtistCard
      artist={{ ...artist('detail'), facts: { type: 'Group', country: 'FR', area: 'France', begin: '1995', end: null, ended: false } }}
      index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={onDetail}
    />,
  );
  await user.click(screen.getByRole('button', { name: 'About Miles Davis' }));
  expect(onDetail).toHaveBeenCalledTimes(1);
  // UXR-D2: what a listener needs AFTER listening lives in the detail, not here.
  expect(screen.queryByRole('link', { name: /spotify/i })).not.toBeInTheDocument();
  expect(screen.queryByText(/try another track/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/dig deeper/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/France/)).not.toBeInTheDocument();
});

// The button is a disclosure for the detail beside it (docked) or over it (the
// sheet), so it reports whether that detail is the open one.
test('the detail button reports whether this card is the open one', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  const { rerender } = render(
    <ArtistCard artist={artist('expanded')} index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()} />,
  );
  expect(screen.getByRole('button', { name: 'About Miles Davis' })).toHaveAttribute('aria-expanded', 'false');
  rerender(
    <ArtistCard artist={artist('expanded')} index={1} total={3} isSelected isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()} />,
  );
  expect(screen.getByRole('button', { name: 'About Miles Davis' })).toHaveAttribute('aria-expanded', 'true');
});

// Every artist has a detail, endpoints included: it is where the links and the
// facts live now, and those render for an endpoint exactly as for any other
// stop (LUX-4). Only "Dig deeper" is interior-only, and that is the detail's
// business, not the card's.
test('an endpoint card carries a detail button too', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={artist('endpoint-detail')} index={0} total={3} isEndpoint endpointLabel="start"
      isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()}
    />,
  );
  expect(screen.getByRole('button', { name: 'About Miles Davis' })).toBeInTheDocument();
});

test('play disabled and card still present when clip is 204', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={artist('silent')} index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()} />);
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeDisabled());
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
});

test('a card with a clip says how long it is', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistCard artist={artist('len')} index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()} />);
  expect(await screen.findByText(/0:30/i)).toBeInTheDocument();
});

// The duration is a claim about a clip. A card with nothing to play must not
// make it — that would read as "30 seconds of silence" rather than "nothing".
test('a card with no clip claims no duration', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  render(<ArtistCard artist={artist('nolen')} index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()} />);
  expect(await screen.findByText(/no preview available/i)).toBeInTheDocument();
  expect(screen.queryByText(/0:30/i)).not.toBeInTheDocument();
});

test('play fires onPlay when a clip exists', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  const onPlay = vi.fn();
  render(<ArtistCard artist={artist('playable')} index={1} total={3} isPlaying={false} onPlay={onPlay} onDetail={vi.fn()} />);
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
      artist={artist('nowplaying')} index={1} total={3} isCurrent isPlaying
      onPlay={onPlay} onToggle={onToggle} onDetail={vi.fn()}
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
      artist={artist('paused')} index={1} total={3} isCurrent isPlaying={false}
      onPlay={onPlay} onToggle={onToggle} onDetail={vi.fn()}
    />,
  );
  await waitFor(() => expect(screen.getByRole('button', { name: /play/i })).toBeEnabled());
  await user.click(screen.getByRole('button', { name: /play/i }));
  expect(onToggle).toHaveBeenCalled();
  expect(onPlay).not.toHaveBeenCalled();
});

test('an endpoint card carries its eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={artist('start')} index={0} total={3} isEndpoint endpointLabel="start" isPlaying={false}
      onPlay={vi.fn()} onDetail={vi.fn()}
    />,
  );
  expect(screen.getByText('You started here')).toBeInTheDocument();
});

test('a destination card carries the other eyebrow label', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(
    <ArtistCard
      artist={artist('dest')} index={2} total={3} isEndpoint endpointLabel="destination" isPlaying={false}
      onPlay={vi.fn()} onDetail={vi.fn()}
    />,
  );
  expect(screen.getByText('You were heading here')).toBeInTheDocument();
});

// UI-5: the e2e responsive spec used to find this by the Tailwind class
// `.font-semibold`, which this task moves. A test hook must not be a style hook.
test('the artist name carries a stable test hook', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'So What', coverUrl: 'c', candidateCount: 1 });
  render(<ArtistCard artist={artist('hook')} index={1} total={3} isPlaying={false} onPlay={vi.fn()} onDetail={vi.fn()} />);
  expect(screen.getByTestId('artist-name')).toHaveTextContent('Miles Davis');
});

// A cycled index (clipIndex > 0) that comes back empty must not strand the
// card: candidateCount arrives on the TrackOut body, which a 204 does not
// carry, so the control that could cycle again also vanishes. Without a
// reset there is no way back to track 1 short of a reload. The control that
// does the cycling moved to the detail in UXR-T6; the card still owns the
// clip it displays, so it is still the component that can see this.
test('a dead cycled index reports back so the caller can reset it', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const onDeadIndex = vi.fn();
  render(
    <ArtistCard
      artist={artist('dead-index')} index={1} total={3} isPlaying={false} clipIndex={2}
      onPlay={vi.fn()} onDetail={vi.fn()} onDeadIndex={onDeadIndex}
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
      artist={artist('silent-not-dead')} index={1} total={3} isPlaying={false}
      onPlay={vi.fn()} onDetail={vi.fn()} onDeadIndex={onDeadIndex}
    />,
  );
  await screen.findByText(/no preview available/i);
  expect(onDeadIndex).not.toHaveBeenCalled();
});
