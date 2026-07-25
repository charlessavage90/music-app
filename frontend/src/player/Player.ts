export interface Player {
  play(url: string): void;
  pause(): void;
  onEnded(cb: () => void): void;
  /** Fired when the element cannot play the current source — a dead signed URL included. */
  onError(cb: () => void): void;
  dispose(): void;
}

export class HtmlAudioPlayer implements Player {
  private audio = new Audio();

  play(url: string): void {
    // Only assigning a *different* src is what lets toggle() resume rather than
    // re-seek to zero, which is why the card's pause button used to restart.
    if (this.audio.src !== url) this.audio.src = url;
    void this.audio.play();
  }

  pause(): void {
    this.audio.pause();
  }

  onEnded(cb: () => void): void {
    this.audio.addEventListener('ended', cb);
  }

  onError(cb: () => void): void {
    this.audio.addEventListener('error', cb);
  }

  dispose(): void {
    this.audio.pause();
    this.audio.src = '';
  }
}
