import { expect, test } from 'vitest';
import { appleUrl, spotifyUrl } from './dspUrls';

test('an id produces a deep link', () => {
  expect(spotifyUrl('4Z8W4fKeB5YxbusRsdQVPb', 'Radiohead'))
    .toBe('https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb');
  expect(appleUrl('657515', 'Radiohead'))
    .toBe('https://music.apple.com/artist/657515');
});

test('no id falls back to a search link, never to nothing', () => {
  expect(spotifyUrl(null, 'Tipsy'))
    .toBe('https://open.spotify.com/search/Tipsy/artists');
  expect(appleUrl(null, 'Tipsy'))
    .toBe('https://music.apple.com/search?term=Tipsy');
});

test('names are URL-encoded', () => {
  expect(spotifyUrl(null, 'Sigur Rós')).toContain('Sigur%20R%C3%B3s');
  expect(appleUrl(null, 'Sigur Rós')).toContain('Sigur%20R%C3%B3s');
});

// The app routes deliberately toward obscure artists, so a name carrying a
// slash or a hash is not an edge case here — it is the population the search
// fallback exists to serve. An unencoded '#' would truncate the Spotify path
// at the fragment and land the listener on an empty search.
test('a name with URL-significant characters cannot break out of the path', () => {
  expect(spotifyUrl(null, 'AC/DC')).toBe('https://open.spotify.com/search/AC%2FDC/artists');
  expect(spotifyUrl(null, '#1 Dads')).toContain('%231%20Dads');
  // '&' would start a second query parameter and '#' a fragment, either of
  // which silently truncates the search term. Both must be encoded.
  expect(appleUrl(null, 'Above & Beyond')).toBe(
    'https://music.apple.com/search?term=Above%20%26%20Beyond',
  );
  expect(appleUrl(null, '#1 Dads')).toBe('https://music.apple.com/search?term=%231%20Dads');
});

// encodeURIComponent deliberately leaves !'()*-._~ alone and they are safe
// where these two put them. Pinned so a future "let's encode harder" change
// has to be a deliberate one rather than an accident.
test('characters that are safe unencoded are left alone', () => {
  expect(appleUrl(null, 'Sunn O)))')).toBe('https://music.apple.com/search?term=Sunn%20O)))');
});

// "" is what the wire used to be able to carry; the api now normalises it to
// null. Treating it as an id would compose a link to a nonexistent artist page
// rather than to a search — a dead end instead of a useful one.
test('an empty-string id is treated as no id, not as an id', () => {
  expect(spotifyUrl('', 'Tipsy')).toBe('https://open.spotify.com/search/Tipsy/artists');
  expect(appleUrl('', 'Tipsy')).toBe('https://music.apple.com/search?term=Tipsy');
});
