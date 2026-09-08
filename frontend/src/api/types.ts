export type BypassReason = 'dislike' | 'known';

/**
 * Structured MusicBrainz facts, all optional (LUX-4).
 *
 * A null field means "show nothing", never "Unknown": the card renders only
 * what is present, with no placeholder rows (`L4-D3`).
 */
export interface ArtistFacts {
  type: string | null;
  /** ISO code, e.g. 'GB'. */
  country: string | null;
  /** Human-readable, e.g. 'United Kingdom'. */
  area: string | null;
  /** '1995' or '1995-03-01'. */
  begin: string | null;
  end: string | null;
  ended: boolean | null;
}

export interface Artist {
  mbid: string;
  name: string;
  disambiguation: string;
  popularity: number;
  /**
   * Platform id TAILS, not URLs (`L4-D2`) — `lib/dspUrls` composes the link.
   *
   * null does NOT mean "no button": it means the button goes to a search
   * instead of to an artist page. Null for every artist until the LUX-4
   * artifact is deployed, and permanently null for artists no DSP relation
   * covers.
   */
  spotifyId: string | null;
  appleId: string | null;
  facts: ArtistFacts | null;
}

export interface Track {
  previewUrl: string;
  title: string;
  coverUrl: string;
  /** Playable tracks this artist has. 1 means there is nothing to cycle to. */
  candidateCount: number;
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
