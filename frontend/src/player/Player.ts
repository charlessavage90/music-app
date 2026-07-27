export interface Player {
  play(url: string): void;
  pause(): void;
  onEnded(cb: () => void): void;
  /** Fired when the element cannot play the current source — a dead signed URL included. */
  onError(cb: () => void): void;
  dispose(): void;
}

/**
 * Wraps one detached `Audio` element.
 *
 * **Handlers replace, never accumulate, and a disposed player is inert.** Both
 * rules exist because of defects found in use rather than by tests. StrictMode
 * mounts effects twice in dev and passes a fresh closure each time, so the DOM's
 * same-reference de-duplication does not apply and listeners piled up: one track
 * ending ran the advance twice and skipped an artist, because the browser drains
 * microtasks between listener callbacks so the second call saw the first's result.
 * And `dispose()` clearing the source makes the browser fire `error`, which the
 * retry handler read as a dead clip — restarting playback after the page had
 * navigated away. See the gate-1 execution log §18.
 */
export class HtmlAudioPlayer implements Player {
  private audio = new Audio();
  private endedCb?: () => void;
  private errorCb?: () => void;
  private disposed = false;

  play(url: string): void {
    if (this.disposed) return;
    // Only assigning a *different* src is what lets toggle() resume rather than
    // re-seek to zero, which is why the card's pause button used to restart.
    if (this.audio.src !== url) this.audio.src = url;
    // A rejected play() — autoplay policy, a decode failure — is the same event
    // as a dead source from the journey's side: no audio is coming. Route it to
    // the error channel, which already owns the one silent retry, rather than
    // adding a second channel that would need its own policy and put the four
    // player invariants back in play. jsdom returns undefined here, not a
    // promise, which Promise.resolve normalises.
    //
    // Only the handler that was live when THIS play() started may hear about it.
    // Checking `disposed` is not sufficient and neither is dispose() clearing
    // the callback: StrictMode disposes and re-subscribes on the same instance,
    // which revives it and installs a new handler, so a rejection from a
    // superseded play() would reach that handler and buy a retry — restarting
    // playback after the page had navigated away, which is the defect dispose()
    // exists to prevent. Found by closeout B3.
    const handlerAtPlay = this.errorCb;
    void Promise.resolve(this.audio.play()).catch(() => {
      if (!this.disposed && this.errorCb === handlerAtPlay) handlerAtPlay?.();
    });
  }

  pause(): void {
    this.audio.pause();
  }

  // Subscribing is the revival signal. StrictMode mounts, cleans up, and mounts
  // again on the same memoised instance, so `disposed` must not be permanent —
  // treating it as permanent silences the app outright.
  onEnded(cb: () => void): void {
    if (this.endedCb) this.audio.removeEventListener('ended', this.endedCb);
    this.disposed = false;
    this.endedCb = cb;
    this.audio.addEventListener('ended', cb);
  }

  onError(cb: () => void): void {
    if (this.errorCb) this.audio.removeEventListener('error', this.errorCb);
    this.disposed = false;
    this.errorCb = cb;
    this.audio.addEventListener('error', cb);
  }

  dispose(): void {
    this.disposed = true;
    // Detach before clearing the source: assigning '' resolves against the document
    // URL and fires `error`, which must not reach a handler that would retry it.
    if (this.endedCb) this.audio.removeEventListener('ended', this.endedCb);
    if (this.errorCb) this.audio.removeEventListener('error', this.errorCb);
    this.endedCb = undefined;
    this.errorCb = undefined;
    this.audio.pause();
    this.audio.src = '';
  }
}
