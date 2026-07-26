import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { LandingPage } from './LandingPage';

afterEach(() => vi.restoreAllMocks());

function setup(url = '/') {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/path/:from/:to" element={<div data-testid="dest">dest</div>} />
      </Routes>
    </MemoryRouter>,
  );
}

test('navigates to the path route once both artists are chosen', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockImplementation(async (q) => [
    { mbid: q.includes('miles') ? 'm' : 'd', name: q, disambiguation: '', popularity: 1 },
  ]);
  setup();
  await user.type(screen.getByLabelText('From'), 'miles');
  await user.click(await screen.findByText('miles'));
  await user.type(screen.getByLabelText('To'), 'daft');
  await user.click(await screen.findByText('daft'));
  await user.click(screen.getByRole('button', { name: /find path/i }));
  expect(screen.getByTestId('dest')).toBeInTheDocument();
});

test('arrives from "new path" with both artists already filled in', async () => {
  const search = vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  expect(screen.getByLabelText('From')).toHaveValue('Miles Davis');
  expect(screen.getByLabelText('To')).toHaveValue('Daft Punk');
  // Prefilled names are already chosen, so they must not re-open a dropdown.
  expect(search).not.toHaveBeenCalled();
});

test('a prefilled pair can be sent straight back off without retyping', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  await user.click(screen.getByRole('button', { name: /find path/i }));
  expect(screen.getByTestId('dest')).toBeInTheDocument();
});

test('typing over a prefilled artist disables "Find path" until one is chosen again', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  const dest = screen.getByLabelText('To');
  await user.clear(dest);
  await user.type(dest, 'wilco');

  // The box and the page must not disagree about who is chosen. Before this
  // fix the button stayed live and routed to Daft Punk — the artist the user
  // had just typed over — with no way to tell why.
  expect(screen.getByRole('button', { name: /find path/i })).toBeDisabled();
});

test('a single edited character is enough to un-choose', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  await user.type(screen.getByLabelText('To'), 'x');

  expect(screen.getByRole('button', { name: /find path/i })).toBeDisabled();
});

test('blocks identical endpoints with a nudge', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'same', name: 'Radiohead', disambiguation: '', popularity: 1 },
  ]);
  setup();
  await user.type(screen.getByLabelText('From'), 'radio');
  await user.click(await screen.findByText('Radiohead'));
  await user.type(screen.getByLabelText('To'), 'radio');
  await user.click((await screen.findAllByText('Radiohead'))[0]);
  expect(screen.getByText(/pick two different artists/i)).toBeInTheDocument();
});
