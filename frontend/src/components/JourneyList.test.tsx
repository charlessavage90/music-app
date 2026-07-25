import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { JourneyList } from './JourneyList';

const artists = [
  { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
  { mbid: 'k', name: 'Kraftwerk', disambiguation: '', popularity: 0.8 },
];
afterEach(() => vi.restoreAllMocks());

test('renders every artist as a card', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} onBypass={vi.fn()} />);
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
  expect(screen.getByText('Kraftwerk')).toBeInTheDocument();
});

test('clicking play marks that card now-playing', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  render(<JourneyList artists={artists} onBypass={vi.fn()} />);
  const firstPlay = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(firstPlay).toBeEnabled());
  await user.click(firstPlay);
  expect(screen.getByText(/now playing/i)).toBeInTheDocument();
});

test('bypass is offered on the artists in the middle, never on the two you chose', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  const threeStop = [
    artists[0],
    { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9 },
    artists[1],
  ];
  render(<JourneyList artists={threeStop} onBypass={vi.fn()} />);

  expect(screen.getAllByRole('button', { name: /not for me/i })).toHaveLength(1);
  expect(screen.getAllByRole('button', { name: /know them/i })).toHaveLength(1);
  // and all three artists are still shown
  expect(screen.getByText('Miles Davis')).toBeInTheDocument();
  expect(screen.getByText('Kraftwerk')).toBeInTheDocument();
});

test('audio stops when the path is recomputed', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c' });
  const { rerender } = render(<JourneyList artists={artists} onBypass={vi.fn()} />);
  const firstPlay = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(firstPlay).toBeEnabled());
  await user.click(firstPlay);
  expect(screen.getByText(/now playing/i)).toBeInTheDocument();

  const rerouted = [artists[0], { mbid: 'x', name: 'Sun Ra', disambiguation: '', popularity: 0.7 }];
  rerender(<JourneyList artists={rerouted} onBypass={vi.fn()} />);

  await waitFor(() => expect(screen.queryByText(/now playing/i)).not.toBeInTheDocument());
});
