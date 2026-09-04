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

/** Whether a journey needed a stop forced in, and whether one was possible. */
export type StopRule = 'natural' | 'forced' | 'adjacent_only';

export interface PathResult {
  artists: Artist[];
  stopRule: StopRule;
  /** Artists a bypass removed, in press order. Absent from `artists`. */
  bypassed: Artist[];
  /** Exclusion ids the graph does not have. The router ignored these. */
  unresolved: string[];
}
