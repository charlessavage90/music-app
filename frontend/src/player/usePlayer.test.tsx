import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StrictMode } from 'react';
import { beforeEach, expect, test, vi } from 'vitest';
import { usePlayer } from './usePlayer';

const played: string[] = [];
const ended: Array<() => void> = [];
const errored: Array<() => void> = [];
const timed: Array<(p: number, d: number) => void> = [];
const playState: Array<(playing: boolean) => void> = [];
const volumes: number[] = [];

vi.mock('./Player', () => ({
  HtmlAudioPlayer: class {
    play(url: string) { played.push(url); }
    pause = vi.fn();
    dispose = vi.fn();
    onEnded(cb: () => void) { ended.push(cb); }
    onError(cb: () => void) { errored.push(cb); }
    onTimeUpdate(cb: (p: number, d: number) => void) { timed.push(cb); }
    onPlayingChange(cb: (playing: boolean) => void) { playState.push(cb); }
    setVolume(v: number) { volumes.push(v); }
  },
}));

beforeEach(() => {
  volumes.length = 0;
  try { sessionStorage.clear(); } catch { /* no storage */ }
  played.length = 0;
  ended.length = 0;
  errored.length = 0;
  timed.length = 0;
  playState.length = 0;
});

function Harness({ resolve }: { resolve: (mbid: string) => Promise<string | null> }) {
  // Miles and Kraftwerk are playable; a middle artist with no clip is absent from the list.
  const p = usePlayer([{ mbid: 'miles' }, { mbid: 'kraftwerk' }], resolve);
  return (
    <div>
      <span data-testid="current">{p.currentMbid ?? 'none'}</span>
      <span data-testid="failure">{p.failure ?? 'ok'}</span>
      <span data-testid="playing">{String(p.isPlaying)}</span>
      <span data-testid="pos">{p.position}/{p.duration}</span>
      <span data-testid="volume">{p.volume}</span>
      <button onClick={() => p.playFrom('miles')}>play</button>
      <button onClick={() => p.setVolume(0.3)}>quieter</button>
      <button onClick={p.retry}>retry</button>
      <button onClick={p.toggle}>toggle</button>
      <button onClick={p.stop}>stop</button>
      <button onClick={p.next}>next</button>
      <button onClick={p.previous}>previous</button>
    </div>
  );
}

test('auto-advance under StrictMode plays the very next artist, not the one after', async () => {
  // Reproduction of the skip found in use. main.tsx renders under StrictMode, and
  // dispose() does not remove listeners, so every handler is registered twice in
  // dev — meaning `ended` fires the advance twice for a single track ending.
  const user = userEvent.setup();
  render(
    <StrictMode>
      <Harness resolve={async (mbid) => `url-for-${mbid}`} />
    </StrictMode>,
  );
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['url-for-miles']));

  await act(async () => { ended.forEach((cb) => cb()); });

  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('kraftwerk'));
  expect(played).toEqual(['url-for-miles', 'url-for-kraftwerk']);
});

test('auto-advances to the next playable on track end', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('miles'));
  await act(async () => { ended.forEach((cb) => cb()); });
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('kraftwerk'));
});

test('signs the URL at the moment of play, not when the card was drawn', async () => {
  // C2, browser side. The old shape took a URL resolved at mount and held it for
  // the life of the card, far longer than a signature lasts (gate-1 execution log
  // §15 owns that figure). The player must ask for the URL when the button is pressed.
  const user = userEvent.setup();
  let issued = 0;
  const resolve = async () => `signed-${++issued}`;

  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['signed-1']));

  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['signed-1', 'signed-2']));
});

test('resolves a fresh URL for the next track on auto-advance too', async () => {
  const user = userEvent.setup();
  const seen: string[] = [];
  const resolve = async (mbid: string) => {
    seen.push(mbid);
    return `url-for-${mbid}`;
  };

  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['url-for-miles']));

  await act(async () => { ended.forEach((cb) => cb()); });
  await waitFor(() => expect(played).toEqual(['url-for-miles', 'url-for-kraftwerk']));
  expect(seen).toEqual(['miles', 'kraftwerk']);
});

// G3-F1: each of the three failure routes used to end in clear() — the bar
// vanished and nothing said why. Each now leaves the artist current, a named
// failure, and a retry.
test('an artist whose clip resolves to nothing stays current with a no-clip failure', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async () => null} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('failure')).toHaveTextContent('no-clip'));
  expect(screen.getByTestId('current')).toHaveTextContent('miles');
  expect(screen.getByTestId('playing')).toHaveTextContent('false');
  expect(played).toEqual([]);
});

test('a lookup that fails is an unreachable failure, and retry plays it', async () => {
  const user = userEvent.setup();
  let fail = true;
  const resolve = async () => {
    if (fail) throw new Error('offline');
    return 'signed';
  };
  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('failure')).toHaveTextContent('unreachable'));
  expect(screen.getByTestId('current')).toHaveTextContent('miles');

  fail = false;
  await user.click(screen.getByText('retry'));
  await waitFor(() => expect(played).toEqual(['signed']));
  expect(screen.getByTestId('failure')).toHaveTextContent('ok');
  expect(screen.getByTestId('playing')).toHaveTextContent('true');
});

test('the play control on a failed clip retries it rather than doing nothing', async () => {
  const user = userEvent.setup();
  let fail = true;
  const resolve = async () => {
    if (fail) throw new Error('offline');
    return 'signed';
  };
  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('failure')).toHaveTextContent('unreachable'));
  fail = false;
  await user.click(screen.getByText('toggle'));
  await waitFor(() => expect(played).toEqual(['signed']));
});

test('a failure that lands after the user moved on is not reported', async () => {
  const user = userEvent.setup();
  let reject!: (e: Error) => void;
  const resolve = (mbid: string) =>
    mbid === 'miles'
      ? new Promise<string | null>((_, r) => { reject = r; })
      : Promise.resolve(`url-for-${mbid}`);
  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await user.click(screen.getByText('stop'));
  await act(async () => { reject(new Error('late')); });
  expect(screen.getByTestId('failure')).toHaveTextContent('ok');
  expect(screen.getByTestId('current')).toHaveTextContent('none');
});

test('stop clears a failure along with everything else', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async () => null} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('failure')).toHaveTextContent('no-clip'));
  await user.click(screen.getByText('stop'));
  expect(screen.getByTestId('failure')).toHaveTextContent('ok');
  expect(screen.getByTestId('current')).toHaveTextContent('none');
});

test('retries once with a newly signed URL when the audio element errors', async () => {
  // The generic safety net: whatever kills a URL mid-life, one silent retry with a
  // fresh signature costs nothing in the common case and covers auto-advance too.
  const user = userEvent.setup();
  let issued = 0;
  const resolve = async () => `signed-${++issued}`;

  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['signed-1']));

  await act(async () => { errored.forEach((cb) => cb()); });
  await waitFor(() => expect(played).toEqual(['signed-1', 'signed-2']));
});

test('gives up after one retry rather than looping on a permanently dead clip', async () => {
  const user = userEvent.setup();
  let issued = 0;
  const resolve = async () => `signed-${++issued}`;

  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['signed-1']));

  await act(async () => { errored.forEach((cb) => cb()); });
  await waitFor(() => expect(played).toHaveLength(2));

  await act(async () => { errored.forEach((cb) => cb()); });
  // G3-F1: giving up is visible — still current, named, and retryable.
  await waitFor(() => expect(screen.getByTestId('failure')).toHaveTextContent('wont-play'));
  expect(screen.getByTestId('current')).toHaveTextContent('miles');
  expect(played).toHaveLength(2);

  // A manual retry is a fresh start, so it gets its own one silent retry too.
  await userEvent.setup().click(screen.getByText('retry'));
  await waitFor(() => expect(played).toHaveLength(3));
  expect(screen.getByTestId('failure')).toHaveTextContent('ok');
});

// G3-F8: an interruption the app did not ask for — a phone call, a Bluetooth
// pause — used to leave the UI saying "playing" over silence.
test('a pause the app did not ask for shows as paused, and a resume as playing', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('playing')).toHaveTextContent('true'));

  act(() => playState.at(-1)?.(false));
  expect(screen.getByTestId('playing')).toHaveTextContent('false');
  expect(screen.getByTestId('current')).toHaveTextContent('miles'); // paused, not gone

  act(() => playState.at(-1)?.(true));
  expect(screen.getByTestId('playing')).toHaveTextContent('true');
});

test('after an external pause, the toggle resumes rather than pausing again', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['url-for-miles']));
  act(() => playState.at(-1)?.(false));
  await user.click(screen.getByText('toggle'));
  expect(played).toEqual(['url-for-miles', 'url-for-miles']);
});

// --- issue #207: volume ------------------------------------------------------

test('a volume change reaches the player without restarting or re-resolving the clip', async () => {
  const user = userEvent.setup();
  const resolve = vi.fn(async (mbid: string) => `url-for-${mbid}`);
  render(<Harness resolve={resolve} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['url-for-miles']));

  await user.click(screen.getByText('quieter'));

  expect(volumes.at(-1)).toBe(0.3);
  expect(screen.getByTestId('volume')).toHaveTextContent('0.3');
  expect(played).toEqual(['url-for-miles']);
  expect(resolve).toHaveBeenCalledTimes(1);
  expect(screen.getByTestId('playing')).toHaveTextContent('true');
});

test('the volume carries to the next clip and survives a remount within the session', async () => {
  const user = userEvent.setup();
  const { unmount } = render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  await user.click(screen.getByText('quieter'));
  unmount();

  volumes.length = 0;
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  expect(screen.getByTestId('volume')).toHaveTextContent('0.3');
  expect(volumes).toContain(0.3); // applied to the new element on mount
});

test('an unreadable stored volume falls back to full', () => {
  sessionStorage.setItem('artistpath.volume', 'loud');
  render(<Harness resolve={async () => null} />);
  expect(screen.getByTestId('volume')).toHaveTextContent('1');
});

test('position and duration follow the audio element and reset when playback stops', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(played).toEqual(['url-for-miles']));
  act(() => timed.at(-1)?.(11.2, 30));
  expect(screen.getByTestId('pos')).toHaveTextContent('11.2/30');
  act(() => ended.at(-1)?.()); // miles ends, kraftwerk starts
  await waitFor(() => expect(played).toHaveLength(2));
  act(() => ended.at(-1)?.()); // kraftwerk ends, nothing next
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('none'));
  expect(screen.getByTestId('pos')).toHaveTextContent('0/0');
});

// #223: the OS "next track" / "previous track" keys.
test('next and previous move between playable cards, and do nothing past either end', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async (mbid) => `url-for-${mbid}`} />);

  await user.click(screen.getByText('next')); // nothing current yet
  expect(played).toEqual([]);

  await user.click(screen.getByText('play'));
  await user.click(screen.getByText('previous')); // already at the first card
  await user.click(screen.getByText('next'));
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('kraftwerk'));

  await user.click(screen.getByText('next')); // already at the last: a skip never stops the player
  expect(screen.getByTestId('current')).toHaveTextContent('kraftwerk');
  expect(screen.getByTestId('playing')).toHaveTextContent('true');

  await user.click(screen.getByText('previous'));
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('miles'));
  expect(played).toEqual(['url-for-miles', 'url-for-kraftwerk', 'url-for-miles']);
});
