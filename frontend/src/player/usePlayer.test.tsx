import { act, render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { StrictMode } from 'react';
import { beforeEach, expect, test, vi } from 'vitest';
import { usePlayer } from './usePlayer';

const played: string[] = [];
const ended: Array<() => void> = [];
const errored: Array<() => void> = [];
const timed: Array<(p: number, d: number) => void> = [];

vi.mock('./Player', () => ({
  HtmlAudioPlayer: class {
    play(url: string) { played.push(url); }
    pause = vi.fn();
    dispose = vi.fn();
    onEnded(cb: () => void) { ended.push(cb); }
    onError(cb: () => void) { errored.push(cb); }
    onTimeUpdate(cb: (p: number, d: number) => void) { timed.push(cb); }
  },
}));

beforeEach(() => {
  played.length = 0;
  ended.length = 0;
  errored.length = 0;
  timed.length = 0;
});

function Harness({ resolve }: { resolve: (mbid: string) => Promise<string | null> }) {
  // Miles and Kraftwerk are playable; a middle artist with no clip is absent from the list.
  const p = usePlayer([{ mbid: 'miles' }, { mbid: 'kraftwerk' }], resolve);
  return (
    <div>
      <span data-testid="current">{p.currentMbid ?? 'none'}</span>
      <span data-testid="pos">{p.position}/{p.duration}</span>
      <button onClick={() => p.playFrom('miles')}>play</button>
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

test('does not play an artist whose clip cannot be resolved', async () => {
  const user = userEvent.setup();
  render(<Harness resolve={async () => null} />);
  await user.click(screen.getByText('play'));
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('none'));
  expect(played).toEqual([]);
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
  await waitFor(() => expect(screen.getByTestId('current')).toHaveTextContent('none'));
  expect(played).toHaveLength(2);
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
