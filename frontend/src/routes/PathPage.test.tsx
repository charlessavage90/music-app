import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { PathPage } from './PathPage';

afterEach(() => vi.restoreAllMocks());

function renderAt(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/" element={<h1>Pick two artists</h1>} />
        <Route path="/path/:from/:to" element={<PathPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

test('renders the path, then a bypass triggers a new request carrying the exclusion', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  // Three stops, because bypass is only offered on the interior — the two
  // artists you chose are endpoints and cannot be rerouted away.
  const buildPath = vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce([
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
      { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9 },
      { mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 0.95 },
    ])
    .mockResolvedValueOnce([
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
      { mbid: 'x', name: 'Sun Ra', disambiguation: '', popularity: 0.7 },
      { mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 0.95 },
    ]);

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');

  // The only bypass on offer is Herbie's — the interior of a three-stop path.
  await user.click(screen.getByRole('button', { name: /not for me/i }));

  await waitFor(() =>
    expect(buildPath).toHaveBeenLastCalledWith(
      ['m', 'd'],
      [{ id: 'h', reason: 'dislike' }],
      expect.any(AbortSignal),
    ),
  );
  await screen.findByText('Sun Ra');
});

test('offers a start-over control that goes back to choosing two artists', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue([
    { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
    { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9 },
  ]);

  renderAt('/path/m/d?known=h');
  await screen.findByText('Herbie Hancock');

  await user.click(screen.getByRole('link', { name: /start over/i }));
  expect(await screen.findByText('Pick two artists')).toBeInTheDocument();
});

test('shows the no-path banner with a clear-exclusions action on 409', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(409));
  renderAt('/path/m/d?dislike=z');
  expect(await screen.findByText(/no path avoiding those artists/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /clear exclusions/i })).toBeInTheDocument();
});
