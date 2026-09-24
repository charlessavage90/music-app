/**
 * PathPage behaviour from the Gate 2→3 review's accessibility and sharing
 * findings (issues #185, #187, #188, #191, #193). A separate file from
 * PathPage.test.tsx so each stays about one thing.
 */
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useLocation } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import type { Artist, PathResult } from '@/api/types';
import { PathPage } from './PathPage';

afterEach(() => {
  vi.restoreAllMocks();
  document.title = '';
});

function artist(mbid: string, name: string): Artist {
  return { mbid, name, disambiguation: '', popularity: 0.5, spotifyId: null, appleId: null, facts: null };
}

function path(...artists: Artist[]): PathResult {
  return { artists, stopRule: 'natural', bypassed: [], unresolved: [] };
}

const MILES = artist('m', 'Miles Davis');
const HERBIE = artist('h', 'Herbie Hancock');
const SUNRA = artist('x', 'Sun Ra');
const DAFT = artist('d', 'Daft Punk');

function renderAt(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/" element={<div>landing</div>} />
        <Route path="/path/:from/:to" element={<PathPage />} />
      </Routes>
    </MemoryRouter>,
  );
}

// ---- #185: the cold-start screen, wired end to end.

test('a timed-out first load offers Try again, and pressing it builds the path', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'getArtist').mockRejectedValue(new Error('decorative'));
  const buildPath = vi.spyOn(client, 'buildPath')
    .mockRejectedValueOnce(new client.TimeoutError(20_000))
    .mockResolvedValueOnce(path(MILES, HERBIE, DAFT));

  renderAt('/path/m/d');
  await user.click(await screen.findByRole('button', { name: 'Try again' }));

  expect(await screen.findByText('Herbie Hancock')).toBeInTheDocument();
  expect(buildPath).toHaveBeenCalledTimes(2);
});

// ---- #193: the server's reason reaches the page.

test('a same-artist link shows the server\'s reason, not "Something went wrong"', async () => {
  vi.spyOn(client, 'getArtist').mockRejectedValue(new Error('decorative'));
  vi.spyOn(client, 'buildPath').mockRejectedValue(
    new client.ApiError(422, 'pick two different artists — a journey needs somewhere to go'),
  );
  renderAt('/path/m/m');
  expect(await screen.findByRole('alert')).toHaveTextContent(
    'Pick two different artists — a journey needs somewhere to go',
  );
});

test('the bypass cap says so and offers a clean slate', async () => {
  vi.spyOn(client, 'getArtist').mockRejectedValue(new Error('decorative'));
  vi.spyOn(client, 'buildPath').mockRejectedValue(
    new client.ApiError(422, 'List should have at most 200 items after validation, not 201', {
      kind: 'too_many_exclusions', max: 200,
    }),
  );
  renderAt('/path/m/d?known=a');
  expect(await screen.findByRole('alert')).toHaveTextContent(/more skips than one journey can hold \(200\)/i);
  expect(screen.getByRole('button', { name: /clear exclusions/i })).toBeInTheDocument();
});

// ---- #188: focus after a bypass.

test('after a bypass, focus lands on the journey heading rather than the page body', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce(path(MILES, HERBIE, DAFT))
    .mockResolvedValueOnce(path(MILES, SUNRA, DAFT));

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');
  await user.click(screen.getAllByRole('button', { name: /^About / })[1]);
  await user.click(screen.getAllByRole('button', { name: /dig deeper/i })[0]);
  await screen.findByText('Sun Ra');

  // The notice is held for a readable minimum before the new path is "landed".
  await waitFor(() => expect(screen.getByRole('heading', { level: 1 })).toHaveFocus(), { timeout: 2000 });
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(/Miles Davis.*Daft Punk/);
});

test('"reset path" hands focus to the heading too, since its own button disappears', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce(path(MILES, SUNRA, DAFT))
    .mockResolvedValueOnce(path(MILES, HERBIE, DAFT));

  renderAt('/path/m/d?n=1&known=h');
  await screen.findByText('Sun Ra');
  await user.click(screen.getByRole('button', { name: /reset path/i }));
  await screen.findByText('Herbie Hancock');

  await waitFor(() => expect(screen.getByRole('heading', { level: 1 })).toHaveFocus(), { timeout: 2000 });
});

test('a first load does not steal focus', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue(path(MILES, HERBIE, DAFT));
  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');
  await new Promise((r) => setTimeout(r, 700));
  expect(screen.getByRole('heading', { level: 1 })).not.toHaveFocus();
});

// ---- #191: the tab title names the journey.

test('the page title names both artists once they are known', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue(path(MILES, HERBIE, DAFT));
  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');
  expect(document.title).toBe('Miles Davis → Daft Punk · Unsung.fm');
});

test('the title names the pair while the path is still loading', async () => {
  vi.spyOn(client, 'buildPath').mockImplementation(() => new Promise(() => {}));
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) =>
    mbid === 'm' ? MILES : DAFT,
  );
  renderAt('/path/m/d');
  await waitFor(() => expect(document.title).toBe('Miles Davis → Daft Punk · Unsung.fm'));
});

test('leaving the journey restores the app title', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue(path(MILES, HERBIE, DAFT));
  const { unmount } = renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');
  unmount();
  expect(document.title).toBe('Unsung.fm');
});

// ---- #187: a link cut in transit.

test('a link that lost skipped artists in transit says so', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue(path(MILES, HERBIE, DAFT));
  renderAt('/path/m/d?n=3&known=a%2Cb');
  await screen.findByText('Herbie Hancock');
  expect(screen.getByText(/this link looks cut short/i)).toHaveTextContent(
    /shared with 3 skipped artists, but only 2 arrived/i,
  );
});

test('a whole link, and a link from before the count existed, say nothing', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue(path(MILES, HERBIE, DAFT));
  const { unmount } = renderAt('/path/m/d?n=2&known=a%2Cb');
  await screen.findByText('Herbie Hancock');
  expect(screen.queryByText(/cut short/i)).not.toBeInTheDocument();
  unmount();

  renderAt('/path/m/d?known=a%2Cb');
  await screen.findByText('Herbie Hancock');
  expect(screen.queryByText(/cut short/i)).not.toBeInTheDocument();
});

test('a bypass press writes the count first, so a cut link can be told apart', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce(path(MILES, HERBIE, DAFT))
    .mockResolvedValue(path(MILES, SUNRA, DAFT));
  function Where() {
    return <div data-testid="where">{useLocation().search}</div>;
  }
  render(
    <MemoryRouter initialEntries={['/path/m/d']}>
      <Routes>
        <Route path="/path/:from/:to" element={<><PathPage /><Where /></>} />
      </Routes>
    </MemoryRouter>,
  );
  await screen.findByText('Herbie Hancock');
  await user.click(screen.getAllByRole('button', { name: /^About / })[1]);
  await user.click(screen.getAllByRole('button', { name: /dig deeper/i })[0]);

  await waitFor(() => expect(screen.getByTestId('where')).toHaveTextContent('?n=1&known=h'));
});
