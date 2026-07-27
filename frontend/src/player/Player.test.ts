import { expect, test, vi } from 'vitest';
import { HtmlAudioPlayer } from './Player';

// These cover the seam that produced two symptoms in real use and neither in the
// test suite: handlers accumulated because dispose() never detached them, and
// StrictMode mounts every effect twice in dev.

function audioOf(player: HtmlAudioPlayer): HTMLAudioElement {
  return (player as unknown as { audio: HTMLAudioElement }).audio;
}

test('a second ended handler replaces the first rather than joining it', () => {
  // The auto-advance skip. StrictMode runs the effect twice and it passes a NEW
  // closure each time, so the DOM's same-reference de-duplication does not apply —
  // two listeners accumulate. One track ending then ran the advance twice, and
  // because the browser drains microtasks between listener callbacks the second
  // advance saw the first one's result and moved on again, skipping an artist.
  const player = new HtmlAudioPlayer();
  const first = vi.fn();
  const second = vi.fn();
  player.onEnded(first);
  player.onEnded(second);

  audioOf(player).dispatchEvent(new Event('ended'));

  expect(second).toHaveBeenCalledTimes(1);
  expect(first).not.toHaveBeenCalled();
});

test('a second error handler replaces the first rather than joining it', () => {
  const player = new HtmlAudioPlayer();
  const first = vi.fn();
  const second = vi.fn();
  player.onError(first);
  player.onError(second);

  audioOf(player).dispatchEvent(new Event('error'));

  expect(second).toHaveBeenCalledTimes(1);
  expect(first).not.toHaveBeenCalled();
});

test('a disposed player delivers no further events', () => {
  // Clearing the source makes the browser fire `error`, which the retry handler
  // read as a dead clip — so navigating away re-fetched a URL and started playing
  // again, after the page had gone.
  const player = new HtmlAudioPlayer();
  const onEnded = vi.fn();
  const onError = vi.fn();
  player.onEnded(onEnded);
  player.onError(onError);
  const el = audioOf(player);

  player.dispose();
  el.dispatchEvent(new Event('ended'));
  el.dispatchEvent(new Event('error'));

  expect(onEnded).not.toHaveBeenCalled();
  expect(onError).not.toHaveBeenCalled();
});

test('re-subscribing after a dispose revives the player (the StrictMode remount)', () => {
  // StrictMode mounts, cleans up, and mounts again on the SAME memoised player, so
  // dispose() must mean "detached and stopped", never "permanently poisoned".
  // Getting this wrong silences the app completely rather than subtly.
  const player = new HtmlAudioPlayer();
  player.onEnded(vi.fn());
  player.dispose();

  const advance = vi.fn();
  player.onEnded(advance);
  const el = audioOf(player);
  el.dispatchEvent(new Event('ended'));

  expect(advance).toHaveBeenCalledTimes(1);
  player.play('https://example.test/clip.mp3');
  expect(el.src).toContain('clip.mp3');
});

test('a rejected play() reaches the error handler', async () => {
  // Autoplay policy, a decode failure, or a source the element refuses: the
  // promise rejects and nothing on the page hears about it, so the card sits
  // there claiming to play over silence.
  const player = new HtmlAudioPlayer();
  const onError = vi.fn();
  player.onError(onError);
  vi.spyOn(audioOf(player), 'play').mockRejectedValue(
    new DOMException('play() failed', 'NotAllowedError'),
  );

  player.play('https://example.test/clip.mp3');
  await vi.waitFor(() => expect(onError).toHaveBeenCalledTimes(1));
});

test('a rejected play() on a disposed player reaches nobody', async () => {
  const player = new HtmlAudioPlayer();
  const onError = vi.fn();
  player.onError(onError);
  const el = audioOf(player);
  vi.spyOn(el, 'play').mockRejectedValue(new DOMException('x', 'AbortError'));

  player.play('https://example.test/clip.mp3');
  player.dispose();
  await new Promise((r) => setTimeout(r, 0));

  expect(onError).not.toHaveBeenCalled();
});

test('a rejected play() cannot reach a handler that replaced it after a dispose', async () => {
  // Found by closeout B3: the test above passes because dispose() clears the
  // callback, NOT because of the `disposed` flag it appears to be testing — so
  // it survived that flag's removal. This covers the case neither mechanism
  // catches. StrictMode disposes and re-subscribes on the SAME instance, which
  // revives it and installs a new handler; a rejection from the superseded
  // play() would then reach that handler and buy a retry, restarting playback
  // after the page had navigated away. That is the defect dispose() exists to
  // prevent (see the class docstring), reached by a different route.
  const player = new HtmlAudioPlayer();
  player.onError(vi.fn());
  let reject!: (e: unknown) => void;
  vi.spyOn(audioOf(player), 'play').mockReturnValue(
    new Promise<void>((_resolve, rj) => {
      reject = rj;
    }),
  );

  player.play('https://example.test/clip.mp3');
  player.dispose();

  const revived = vi.fn();
  player.onError(revived); // the StrictMode remount
  reject(new DOMException('play() failed', 'NotAllowedError'));
  await new Promise((r) => setTimeout(r, 0));

  expect(revived).not.toHaveBeenCalled();
});

test('a disposed player refuses to start playing again', () => {
  // Note: clearing src leaves the element pointing at the document URL, not at ''.
  // What matters is that the clip is never loaded and playback is never started.
  const player = new HtmlAudioPlayer();
  const el = audioOf(player);
  const started = vi.spyOn(el, 'play').mockResolvedValue(undefined);
  player.dispose();

  player.play('https://example.test/clip.mp3');

  expect(el.src).not.toContain('clip.mp3');
  expect(started).not.toHaveBeenCalled();
});
