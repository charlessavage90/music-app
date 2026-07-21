export type BypassReason = 'dislike' | 'known';

export interface Artist {
  mbid: string;
  name: string;
  disambiguation: string;
  popularity: number;
}

export interface Track {
  previewUrl: string;
  title: string;
  coverUrl: string;
}

export interface Exclusion {
  id: string;
  reason: BypassReason;
}
