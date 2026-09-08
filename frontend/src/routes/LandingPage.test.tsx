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

test('offers the three sample journeys, each linking straight at a path', () => {
  setup();
  const links = screen.getAllByRole('link');
  expect(links).toHaveLength(3);
  // Accessible names, not textContent: the chevron is aria-hidden, so this is
  // what a screen reader actually announces.
  expect(links.map((l) => l.getAttribute('aria-label'))).toEqual([
    'Miles Davis to Radiohead, 3 steps',
    'Dolly Parton to Daft Punk, 4 steps',
    'Bad Bunny to Chappell Roan, 6 steps',
  ]);
  // Ordinary links, not buttons that navigate — so they are shareable, open in
  // a new tab, and work with Back like any other journey.
  for (const l of links) expect(l.getAttribute('href')).toMatch(/^\/path\/[0-9a-f-]{36}\/[0-9a-f-]{36}$/);
});

// A sample journey must reach the same route the form does, or it is a
// different feature that happens to look like one.
test('pressing a sample journey lands on the path route', async () => {
  const user = userEvent.setup();
  setup();
  await user.click(screen.getByRole('link', { name: /miles davis/i }));
  expect(screen.getByTestId('dest')).toBeInTheDocument();
});

test('navigates to the path route once both artists are chosen', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockImplementation(async (q) => [
    { mbid: q.includes('miles') ? 'm' : 'd', name: q, disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
  ]);
  setup();
  await user.type(screen.getByLabelText('Start with'), 'miles');
  await user.click(await screen.findByText('miles'));
  await user.type(screen.getByLabelText('End with'), 'daft');
  await user.click(await screen.findByText('daft'));
  await user.click(screen.getByRole('button', { name: /build the path/i }));
  expect(screen.getByTestId('dest')).toBeInTheDocument();
});

test('arrives from "new path" with both artists already filled in', async () => {
  const search = vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  expect(screen.getByLabelText('Start with')).toHaveValue('Miles Davis');
  expect(screen.getByLabelText('End with')).toHaveValue('Daft Punk');
  // Prefilled names are already chosen, so they must not re-open a dropdown.
  expect(search).not.toHaveBeenCalled();
});

test('a prefilled pair can be sent straight back off without retyping', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  await user.click(screen.getByRole('button', { name: /build the path/i }));
  expect(screen.getByTestId('dest')).toBeInTheDocument();
});

test('typing over a prefilled artist disables "Build the path" until one is chosen again', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  const dest = screen.getByLabelText('End with');
  await user.clear(dest);
  await user.type(dest, 'wilco');

  // The box and the page must not disagree about who is chosen. Before this
  // fix the button stayed live and routed to Daft Punk — the artist the user
  // had just typed over — with no way to tell why.
  expect(screen.getByRole('button', { name: /build the path/i })).toBeDisabled();
});

test('a single edited character is enough to un-choose', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  setup('/?from=m&fromName=Miles+Davis&to=d&toName=Daft+Punk');

  await user.type(screen.getByLabelText('End with'), 'x');

  expect(screen.getByRole('button', { name: /build the path/i })).toBeDisabled();
});

test('blocks identical endpoints with a nudge', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'same', name: 'Radiohead', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
  ]);
  setup();
  // By ROLE: the dropdown entries are buttons. A sample chip now renders
  // "Radiohead" as its own text node inside a link, so a text query clicks the
  // chip and navigates away before the second box is ever filled.
  await user.type(screen.getByLabelText('Start with'), 'radio');
  await user.click(await screen.findByRole('button', { name: 'Radiohead' }));
  await user.type(screen.getByLabelText('End with'), 'radio');
  await user.click((await screen.findAllByRole('button', { name: 'Radiohead' }))[0]);
  expect(screen.getByText(/pick two different artists/i)).toBeInTheDocument();
});

// Removed at the owner's request 2026-07-28: the decorative three-dot rail
// stays, the clip-length line under it does not. Asserted as absent rather than
// deleted, so restoring the line is a deliberate act and not an accident.
test('the landing page does not state clip length', () => {
  setup();
  expect(screen.queryByText(/30 seconds/i)).not.toBeInTheDocument();
});

test('each sample journey says how many steps it takes, in the "between" currency', () => {
  setup();
  // UXR-D6/D7: "steps" = artists BETWEEN the two chosen. Measured on the served
  // graph 2026-09-08; e2e/landing-samples.spec.ts pins these against the live
  // router so a rebuild that moves them fails a test instead of lying on a chip.
  expect(screen.getByRole('link', { name: /miles davis.*radiohead/i })).toHaveTextContent('3 steps');
  expect(screen.getByRole('link', { name: /dolly parton.*daft punk/i })).toHaveTextContent('4 steps');
  expect(screen.getByRole('link', { name: /bad bunny.*chappell roan/i })).toHaveTextContent('6 steps');
});

test('the hero carries the approved copy and a three-step "How it works"', () => {
  setup();
  expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent(
    'Hear what lives between two artists you love.',
  );
  expect(screen.getByText(/name two artists/i)).toBeInTheDocument();
  expect(screen.getByText(/listen to the path/i)).toBeInTheDocument();
  expect(screen.getAllByText(/dig deeper/i).length).toBeGreaterThan(0);
});

test('the teaser names the measured Miles Davis to Daft Punk journey, without tags', () => {
  setup();
  for (const name of ['Nina Simone', 'Marvin Gaye', 'Daryl Hall & John Oates', 'Genesis', 'David Gilmour']) {
    expect(screen.getByText(name)).toBeInTheDocument();
  }
  expect(screen.queryByText(/low reach/i)).not.toBeInTheDocument();
});
