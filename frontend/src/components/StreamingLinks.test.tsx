import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { StreamingLinks } from './StreamingLinks';
import type { Artist } from '@/api/types';

const base: Artist = {
  mbid: 'a'.repeat(36),
  name: 'Radiohead',
  disambiguation: '',
  popularity: 0.9,
  spotifyId: '4Z8W4fKeB5YxbusRsdQVPb',
  appleId: '657515',
  facts: null,
};

test('both services always render, id or not', () => {
  render(<StreamingLinks artist={{ ...base, spotifyId: null, appleId: 'x' }} />);
  expect(screen.getByRole('link', { name: /spotify/i })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: /apple/i })).toBeInTheDocument();
});

test('an id produces a deep link', () => {
  render(<StreamingLinks artist={base} />);
  expect(screen.getByRole('link', { name: /spotify/i })).toHaveAttribute(
    'href',
    'https://open.spotify.com/artist/4Z8W4fKeB5YxbusRsdQVPb',
  );
  expect(screen.getByRole('link', { name: /apple/i })).toHaveAttribute(
    'href',
    'https://music.apple.com/artist/657515',
  );
});

// The whole point of the fallback. Until the LUX-4 artifact deploys EVERY
// artist is in this state, so a card that rendered nothing here would render
// nothing at all in production.
test('no ids at all still renders two working links', () => {
  render(<StreamingLinks artist={{ ...base, spotifyId: null, appleId: null }} />);
  expect(screen.getByRole('link', { name: /spotify/i })).toHaveAttribute(
    'href',
    'https://open.spotify.com/search/Radiohead/artists',
  );
  expect(screen.getByRole('link', { name: /apple/i })).toHaveAttribute(
    'href',
    'https://music.apple.com/search?term=Radiohead',
  );
});

test('links open in a new tab without leaking the referrer', () => {
  render(<StreamingLinks artist={base} />);
  for (const name of [/spotify/i, /apple/i]) {
    const link = screen.getByRole('link', { name });
    expect(link).toHaveAttribute('target', '_blank');
    expect(link).toHaveAttribute('rel', expect.stringContaining('noopener'));
    expect(link).toHaveAttribute('rel', expect.stringContaining('noreferrer'));
  }
});

// Text labels only. Using either company's logo pulls in their brand
// guidelines (spec §4.7), which is a licensing question and not a design one.
test('no service logos are used', () => {
  const { container } = render(<StreamingLinks artist={base} />);
  expect(container.querySelector('img')).toBeNull();
  expect(container.querySelector('svg')).toBeNull();
});

// A screen-reader user hears the accessible name out of context, so "Spotify"
// alone on every card is ambiguous once there are twelve of them.
test('each link names the artist it belongs to', () => {
  render(<StreamingLinks artist={base} />);
  expect(screen.getAllByRole('link', { name: /radiohead/i })).toHaveLength(2);
  expect(screen.getByRole('link', { name: 'Radiohead on Spotify' })).toBeInTheDocument();
  expect(screen.getByRole('link', { name: 'Radiohead on Apple Music' })).toBeInTheDocument();
});
