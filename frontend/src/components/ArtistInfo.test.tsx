import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { ArtistInfo } from './ArtistInfo';
import type { Artist } from '@/api/types';

const base: Artist = {
  mbid: 'a'.repeat(36),
  name: 'Tipsy',
  disambiguation: '',
  popularity: 0.4,
  spotifyId: null,
  appleId: null,
  facts: null,
};

test('renders a compact fact line', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: 'Group', country: 'DE', area: 'Germany',
    begin: '1993', end: '2008', ended: true } }} />);
  expect(screen.getByText(/Germany/)).toBeInTheDocument();
  expect(screen.getByText(/1993–2008/)).toBeInTheDocument();
  expect(screen.getByText(/Group/)).toBeInTheDocument();
});

test('an active artist shows an open-ended span', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: null, country: null, area: null,
    begin: '1995', end: null, ended: false } }} />);
  expect(screen.getByText(/1995–/)).toBeInTheDocument();
});

test('nothing renders when there are no facts', () => {
  const { container } = render(<ArtistInfo artist={{ ...base, facts: null }} />);
  expect(container).toBeEmptyDOMElement();
});

// L4-D3. A missing life span shows NOTHING, not "Unknown". The empty state is
// the absence itself — which is what LUX-E2 exists to check and cannot yet,
// because its sample is damaged on the served map.
test('partial facts render without placeholder rows', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: 'Person', country: null, area: null, begin: null, end: null, ended: null } }} />);
  expect(screen.getByText(/Person/)).toBeInTheDocument();
  expect(screen.queryByText(/unknown/i)).not.toBeInTheDocument();
  expect(screen.queryByText(/n\/a|--|—\s*$/i)).not.toBeInTheDocument();
});

// Already on the wire since before LUX-4 and rendered only in the search
// dropdown, never on a journey card. Surfacing it needs no rebuild, and it is
// often the single most useful line about an unknown artist.
test('the disambiguation is shown on the card', () => {
  render(<ArtistInfo artist={{ ...base, disambiguation: 'US electronic lounge band' }} />);
  expect(screen.getByText(/US electronic lounge band/)).toBeInTheDocument();
});

test('a disambiguation alone renders even with no structured facts', () => {
  const { container } = render(
    <ArtistInfo artist={{ ...base, disambiguation: 'Icelandic post-rock band', facts: null }} />,
  );
  expect(container).not.toBeEmptyDOMElement();
  expect(screen.getByText(/Icelandic post-rock band/)).toBeInTheDocument();
});

// MusicBrainz stores full dates where it has them. A card has one line, and
// the day an artist formed is not what a listener is deciding on.
test('a full date is shown as its year', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: null, country: null, area: null,
    begin: '1995-03-01', end: '2008-11-22', ended: true } }} />);
  expect(screen.getByText(/1995–2008/)).toBeInTheDocument();
  expect(screen.queryByText(/03-01/)).not.toBeInTheDocument();
});

// An artist with an end date but no begin date. Rare, but MusicBrainz has
// them, and "–2008" is honest where "2008" would read as a formation year.
test('an end with no beginning is not shown as a beginning', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: null, country: null, area: null, begin: null, end: '2008', ended: true } }} />);
  expect(screen.getByText(/–2008/)).toBeInTheDocument();
});

// The country code is redundant beside the human-readable area and reads as
// noise on a card. It is carried on the wire for whatever wants it later.
test('the ISO country code is not shown when the area is', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: null, country: 'GB', area: 'United Kingdom', begin: null, end: null, ended: null } }} />);
  expect(screen.getByText(/United Kingdom/)).toBeInTheDocument();
  expect(screen.queryByText(/\bGB\b/)).not.toBeInTheDocument();
});

test('the country code is shown when there is no area', () => {
  render(<ArtistInfo artist={{ ...base, facts: {
    type: null, country: 'IS', area: null, begin: null, end: null, ended: null } }} />);
  expect(screen.getByText(/IS/)).toBeInTheDocument();
});

// An artifact where the extraction reached the artist and found nothing must
// be indistinguishable from one that predates LUX-4 entirely.
test('an all-null facts object renders as nothing', () => {
  const { container } = render(<ArtistInfo artist={{ ...base, facts: {
    type: null, country: null, area: null, begin: null, end: null, ended: null } }} />);
  expect(container).toBeEmptyDOMElement();
});
