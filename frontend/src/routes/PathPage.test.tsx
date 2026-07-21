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
      <Routes><Route path="/path/:from/:to" element={<PathPage />} /></Routes>
    </MemoryRouter>,
  );
}

test('renders the path, then a bypass triggers a new request carrying the exclusion', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const buildPath = vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce([
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
      { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9 },
    ])
    .mockResolvedValueOnce([
      { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1 },
      { mbid: 'x', name: 'Sun Ra', disambiguation: '', popularity: 0.7 },
    ]);

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');

  const dislikeButtons = screen.getAllByRole('button', { name: /not for me/i });
  await user.click(dislikeButtons[1]); // bypass Herbie

  await waitFor(() =>
    expect(buildPath).toHaveBeenLastCalledWith(
      ['m', 'd'],
      [{ id: 'h', reason: 'dislike' }],
      expect.any(AbortSignal),
    ),
  );
  await screen.findByText('Sun Ra');
});

test('shows the no-path banner with a clear-exclusions action on 409', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(409));
  renderAt('/path/m/d?dislike=z');
  expect(await screen.findByText(/no path avoiding those artists/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /clear exclusions/i })).toBeInTheDocument();
});
