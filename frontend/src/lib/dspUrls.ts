/**
 * Compose streaming URLs from the platform id tails the artifact carries.
 *
 * The artifact stores ids, never URLs (`L4-D2`), so the hostname lives here
 * and a scheme change is a frontend edit rather than a graph rebuild — the
 * alternative bakes a hostname into 58,838 entries and into every artifact
 * built after it, forever.
 *
 * A null id NEVER means "no button". It means a search link: the app routes to
 * obscure artists, so the missing-id case is disproportionately the population
 * this exists to serve, and a card that shows one service while silently
 * dropping the other reads as the artist being absent from that service
 * (spec §4.1, option A).
 *
 * Both take `''` as absent too. The api normalises the artifact's in-band ""
 * to null, so this is defence rather than a live path — but an empty id would
 * compose a link to a nonexistent artist page, which is a worse failure than
 * the search link it replaces.
 */

export function spotifyUrl(id: string | null | undefined, name: string): string {
  return id
    ? `https://open.spotify.com/artist/${id}`
    : `https://open.spotify.com/search/${encodeURIComponent(name)}/artists`;
}

export function appleUrl(id: string | null | undefined, name: string): string {
  return id
    ? `https://music.apple.com/artist/${id}`
    : `https://music.apple.com/search?term=${encodeURIComponent(name)}`;
}
