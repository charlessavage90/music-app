import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { JourneyList } from './JourneyList';

const artists = [
  { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
  { mbid: 'k', name: 'Kraftwerk', disambiguation: '', popularity: 0.8, spotifyId: null, appleId: null, facts: null },
];
afterEach(() => vi.restoreAllMocks());

test('renders every artist as a card', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  render(<JourneyList artists={artists} stopRule="natural" onBypass={vi.fn()} />);
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
  expect(screen.getByText('Kraftwerk')).toBeInTheDocument();
});

test('clicking play marks that card now-playing', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  render(<JourneyList artists={artists} stopRule="natural" onBypass={vi.fn()} />);
  const firstPlay = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(firstPlay).toBeEnabled());
  await user.click(firstPlay);
  expect(screen.getByText(/now playing/i)).toBeInTheDocument();
});

test('bypass is offered on the artists in the middle, never on the two you chose', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  const threeStop = [
    artists[0],
    { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9, spotifyId: null, appleId: null, facts: null },
    artists[1],
  ];
  render(<JourneyList artists={threeStop} stopRule="natural" onBypass={vi.fn()} />);

  // One footer strip, on the interior card only — the endpoints stay bare, so
  // there is no route to the signal on them at all.
  expect(screen.getAllByRole('button', { name: /dig deeper/i })).toHaveLength(1);
  // and all three artists are still shown
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
  expect(screen.getByText('Kraftwerk')).toBeInTheDocument();
});

test('a card left mounted past the signature lifetime re-signs before playing', async () => {
  // The span nothing asserted before (execution log §15): the old browser test
  // advanced time and then *remounted*, which re-ran the effect and hid the bug.
  // A real tab stays mounted, so the effect never re-runs and the URL rots in place.
  const user = userEvent.setup();
  vi.spyOn(Date, 'now').mockReturnValue(0);
  const spy = vi.spyOn(client, 'getTrack');
  spy.mockResolvedValue({ previewUrl: 'signed-at-zero', title: 'T', coverUrl: 'c', candidateCount: 1 });

  const stale = [
    { mbid: 'stale-a', name: 'Alice Coltrane', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
    { mbid: 'stale-b', name: 'Sun Ra', disambiguation: '', popularity: 0.8, spotifyId: null, appleId: null, facts: null },
  ];
  render(<JourneyList artists={stale} stopRule="natural" onBypass={vi.fn()} />);
  const firstPlay = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(firstPlay).toBeEnabled());
  const afterDraw = spy.mock.calls.length;

  // The tab sits open for twenty minutes. Nothing unmounts, nothing navigates.
  vi.spyOn(Date, 'now').mockReturnValue(20 * 60 * 1000);
  spy.mockResolvedValue({ previewUrl: 'signed-later', title: 'T', coverUrl: 'c', candidateCount: 1 });

  await user.click(firstPlay);

  await waitFor(() => expect(spy.mock.calls.length).toBeGreaterThan(afterDraw));
});

test('audio stops when the path is recomputed', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  const { rerender } = render(<JourneyList artists={artists} stopRule="natural" onBypass={vi.fn()} />);
  const firstPlay = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(firstPlay).toBeEnabled());
  await user.click(firstPlay);
  expect(screen.getByText(/now playing/i)).toBeInTheDocument();

  const rerouted = [artists[0], { mbid: 'x', name: 'Sun Ra', disambiguation: '', popularity: 0.7, spotifyId: null, appleId: null, facts: null }];
  rerender(<JourneyList artists={rerouted} stopRule="natural" onBypass={vi.fn()} />);

  await waitFor(() => expect(screen.queryByText(/now playing/i)).not.toBeInTheDocument());
});

test('explains itself when the two artists have nobody between them', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  render(<JourneyList artists={artists} stopRule="adjacent_only" onBypass={vi.fn()} />);
  expect(screen.getByText(/next to each other/i)).toBeInTheDocument();
});

test('says nothing on an ordinary journey', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  render(<JourneyList artists={artists} stopRule="natural" onBypass={vi.fn()} />);
  expect(screen.queryByText(/next to each other/i)).not.toBeInTheDocument();
});

test('says nothing when a stop was forced in', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  render(<JourneyList artists={artists} stopRule="forced" onBypass={vi.fn()} />);
  expect(screen.queryByText(/next to each other/i)).not.toBeInTheDocument();
});
