export interface Player {
  play(url: string): void;
  pause(): void;
  onEnded(cb: () => void): void;
  dispose(): void;
}

export class HtmlAudioPlayer implements Player {
  private audio = new Audio();

  play(url: string): void {
    if (this.audio.src !== url) this.audio.src = url;
    void this.audio.play();
  }

  pause(): void {
    this.audio.pause();
  }

  onEnded(cb: () => void): void {
    this.audio.addEventListener('ended', cb);
  }

  dispose(): void {
    this.audio.pause();
    this.audio.src = '';
  }
}
