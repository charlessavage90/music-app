import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes, useSearchParams } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { PathPage } from './PathPage';

afterEach(() => vi.restoreAllMocks());

/** Stands in for the landing page, reporting what the link handed it. */
function LandingProbe() {
  const [params] = useSearchParams();
  const shown = ['from', 'fromName', 'to', 'toName']
    .map((k) => `${k}=${params.get(k) ?? ''}`)
    .join(' ');
  return <div data-testid="landing">{shown}</div>;
}

async function pressBypass(user: ReturnType<typeof userEvent.setup>) {
  await user.click(screen.getByRole('button', { name: /dig deeper/i }));
}

function renderAt(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes>
        <Route path="/" element={<LandingProbe />} />
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
    .mockResolvedValueOnce({
      artists: [
        { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
        { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9, spotifyId: null, appleId: null, facts: null },
        { mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 0.95, spotifyId: null, appleId: null, facts: null },
      ],
      stopRule: 'natural',
      bypassed: [],
      unresolved: [],
    })
    .mockResolvedValueOnce({
      artists: [
        { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
        { mbid: 'x', name: 'Sun Ra', disambiguation: '', popularity: 0.7, spotifyId: null, appleId: null, facts: null },
        { mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 0.95, spotifyId: null, appleId: null, facts: null },
      ],
      stopRule: 'natural',
      bypassed: [],
      unresolved: [],
    });

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');

  // The only bypass on offer is Herbie's — the interior of a three-stop path.
  await pressBypass(user);

  await waitFor(() =>
    expect(buildPath).toHaveBeenLastCalledWith(
      ['m', 'd'],
      [{ id: 'h', reason: 'known' }],
      expect.any(AbortSignal),
    ),
  );
  await screen.findByText('Sun Ra');
});

const THREE_STOP = [
  { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
  { mbid: 'h', name: 'Herbie Hancock', disambiguation: '', popularity: 0.9, spotifyId: null, appleId: null, facts: null },
  { mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 0.95, spotifyId: null, appleId: null, facts: null },
];

test('"new path" goes back to choosing artists, carrying this pair with it', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue({ artists: THREE_STOP, stopRule: 'natural', bypassed: [], unresolved: [] });

  renderAt('/path/m/d?known=h');
  await screen.findByText('Herbie Hancock');

  await user.click(screen.getByRole('link', { name: /new path/i }));

  const landing = await screen.findByTestId('landing');
  // The pair travels with the link so the boxes arrive prefilled.
  expect(landing).toHaveTextContent('from=m');
  expect(landing).toHaveTextContent('fromName=Miles Davis');
  expect(landing).toHaveTextContent('to=d');
  expect(landing).toHaveTextContent('toName=Daft Punk');
});

test('"reset path" drops every bypass and keeps the same two artists', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  const buildPath = vi.spyOn(client, 'buildPath').mockResolvedValue({ artists: THREE_STOP, stopRule: 'natural', bypassed: [], unresolved: [] });

  renderAt('/path/m/d?known=h&dislike=z');
  await screen.findByText('Herbie Hancock');

  await user.click(screen.getByRole('button', { name: /reset path/i }));

  await waitFor(() =>
    expect(buildPath).toHaveBeenLastCalledWith(['m', 'd'], [], expect.any(AbortSignal)),
  );
});

// Distinct mbids: the clip cache is module-level and lives for the whole file, so
// reusing ids the other tests resolved to "no clip" leaves the play button disabled.
const AUDIBLE_THREE_STOP = [
  { mbid: 'aud-m', name: 'Alice Coltrane', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null },
  { mbid: 'aud-h', name: 'Pharoah Sanders', disambiguation: '', popularity: 0.9, spotifyId: null, appleId: null, facts: null },
  { mbid: 'aud-d', name: 'Sun Ra', disambiguation: '', popularity: 0.95, spotifyId: null, appleId: null, facts: null },
];

/** Renders a path whose cards have clips, and starts one playing. */
async function renderPlaying(user: ReturnType<typeof userEvent.setup>, url: string) {
  vi.spyOn(client, 'getTrack').mockResolvedValue({ previewUrl: 'u', title: 'T', coverUrl: 'c', candidateCount: 1 });
  vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce({ artists: AUDIBLE_THREE_STOP, stopRule: 'natural', bypassed: [], unresolved: [] })
    // The rebuild never arrives, so anything that stops only on rebuild stays playing.
    .mockReturnValueOnce(new Promise(() => {}));

  renderAt(url);
  await screen.findByText('Pharoah Sanders');
  const play = (await screen.findAllByRole('button', { name: /play/i }))[0];
  await waitFor(() => expect(play).toBeEnabled());
  await user.click(play);
  await waitFor(() => expect(screen.getByRole('img', { name: /now playing/i })).toBeInTheDocument());
}

test('pressing reset path stops the audio at once, not when the new path arrives', async () => {
  const user = userEvent.setup();
  await renderPlaying(user, '/path/m/d?known=h&dislike=z');

  await user.click(screen.getByRole('button', { name: /reset path/i }));

  await waitFor(() => expect(screen.queryByRole('img', { name: /now playing/i })).not.toBeInTheDocument());
});

test('pressing a bypass stops the audio at once, not when the new path arrives', async () => {
  const user = userEvent.setup();
  await renderPlaying(user, '/path/m/d');

  await pressBypass(user);

  await waitFor(() => expect(screen.queryByRole('img', { name: /now playing/i })).not.toBeInTheDocument());
});

test('there is nothing to reset before any bypass is pressed', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue({ artists: THREE_STOP, stopRule: 'natural', bypassed: [], unresolved: [] });

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');

  expect(screen.queryByRole('button', { name: /reset path/i })).not.toBeInTheDocument();
  expect(screen.getByRole('link', { name: /new path/i })).toBeInTheDocument();
});

test('shows the no-path banner with a clear-exclusions action on 409', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(409));
  renderAt('/path/m/d?dislike=z');
  expect(await screen.findByText(/no path avoiding those artists/i)).toBeInTheDocument();
  expect(screen.getByRole('button', { name: /clear exclusions/i })).toBeInTheDocument();
});

test('a first load shows the skeleton, not the old text line', async () => {
  // The path never lands, so the skeleton is what is on screen throughout.
  vi.spyOn(client, 'buildPath').mockImplementation(() => new Promise(() => {}));
  vi.spyOn(client, 'getArtist').mockImplementation(async (mbid: string) => ({
    mbid,
    name: mbid === 'm' ? 'Miles Davis' : 'Daft Punk',
    disambiguation: '',
    popularity: 0,
    spotifyId: null,
    appleId: null,
    facts: null,
  }));

  renderAt('/path/m/d');

  // Named from the decorative lookup, since no path has arrived to name them.
  expect(await screen.findByText('Miles Davis')).toBeInTheDocument();
  expect(screen.getByText('Daft Punk')).toBeInTheDocument();
  expect(screen.getByText(/listening for the steps between them/i)).toBeInTheDocument();
  expect(screen.queryByText(/building your path/i)).not.toBeInTheDocument();
});

test('a bypass press holds the old path and names what it is doing', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath')
    .mockResolvedValueOnce({ artists: THREE_STOP, stopRule: 'natural', bypassed: [], unresolved: [] })
    // The rebuild never lands, so the held path stays on screen to be asserted.
    .mockReturnValueOnce(new Promise(() => {}));

  renderAt('/path/m/d');
  await screen.findByText('Herbie Hancock');

  await pressBypass(user);

  // UI-D4: the previous path is held and dimmed, never replaced by the skeleton.
  expect(await screen.findByText(/digging deeper for someone newer/i)).toBeInTheDocument();
  expect(screen.getByText('Herbie Hancock')).toBeInTheDocument();
  expect(screen.queryByText(/listening for the steps between them/i)).not.toBeInTheDocument();
});

// UI-D7: what the line counts is the artists BETWEEN the two chosen, which is
// what is visible on screen — not hops. THREE_STOP has exactly one.
test('the result line counts the artists in between', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue({ artists: THREE_STOP, stopRule: 'natural', bypassed: [], unresolved: [] });

  renderAt('/path/m/d');

  expect(await screen.findByText(/we found a path/i)).toHaveTextContent(/in 1 step\./i);
});

// This is the wiring between path state and the panel — no other PathPage test
// supplies a non-empty bypassed/unresolved, so without this the two had never
// been exercised together at any level.
test('a bypassed artist from the path response is named in the route-history panel', async () => {
  vi.spyOn(client, 'getTrack').mockResolvedValue(null);
  vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: THREE_STOP,
    stopRule: 'natural',
    bypassed: [{ mbid: 'z', name: 'Sun Ra', disambiguation: '', popularity: 0.2, spotifyId: null, appleId: null, facts: null }],
    unresolved: [],
  });

  renderAt('/path/m/d?known=z');

  await screen.findByText('Herbie Hancock');
  expect(await screen.findByText('Sun Ra')).toBeInTheDocument();
});
