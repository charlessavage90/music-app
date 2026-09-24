/**
 * How long a journey is, wherever the app names a length: EVERY artist on it,
 * including the two the listener chose. Owner's ruling 2026-09-24 (issue #202):
 * one convention, globally, and it is the inclusive one — a journey from A to B
 * through five other artists is a seven-stop journey.
 *
 * This replaces the redesign's split currencies (UXR-D6 "steps" = artists
 * between; UXR-D10 "Stop N of M" = every artist). "Stops" is the word, because
 * the artist panel and the player bar already said "Stop N of M". Every surface
 * that states a length — landing example card, sample-journey chips, the
 * journey heading's tile, the artist panel, the player bar — takes its number
 * from here, so the `- 2` can never come back on one of them.
 */
export function journeyLength(artists: readonly unknown[]): number {
  return artists.length;
}
