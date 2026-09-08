import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistSearch } from './ArtistSearch';

afterEach(() => vi.restoreAllMocks());

test('debounces, shows results, and selects one', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 0.8, spotifyId: null, appleId: null, facts: null },
  ]);
  const onSelect = vi.fn();
  render(<ArtistSearch label="From" end="start" onSelect={onSelect} />);

  await user.type(screen.getByLabelText('From'), 'miles');
  const option = await screen.findByText('Miles Davis');
  await user.click(option);

  expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ mbid: 'm' }));
});

test('reports null once the text no longer matches the chosen artist', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  const onSelect = vi.fn();
  render(
    <ArtistSearch
      label="To"
      end="destination"
      initial={{ mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null }}
      onSelect={onSelect}
    />,
  );

  // Arriving prefilled is not an edit and must not report anything.
  expect(onSelect).not.toHaveBeenCalled();

  await user.type(screen.getByLabelText('To'), '!');

  expect(onSelect).toHaveBeenCalledWith(null);
});

test('says so when the catalogue has no match', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);

  await user.type(screen.getByLabelText('From'), 'zzzz');

  expect(await screen.findByText(/no artists found/i)).toBeInTheDocument();
});

test('distinguishes a failed search from an empty one', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockRejectedValue(new Error('network'));
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);

  await user.type(screen.getByLabelText('From'), 'miles');

  expect(await screen.findByText(/search is unavailable/i)).toBeInTheDocument();
  expect(screen.queryByText(/no artists found/i)).not.toBeInTheDocument();
});

test('opts out of the iOS keyboard rewriting artist names', () => {
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);
  const input = screen.getByLabelText('From');

  // Artist names are proper nouns autocorrect does not know, and iOS rewrites
  // them mid-typing, so the query sent is not the query typed.
  expect(input).toHaveAttribute('autocorrect', 'off');
  expect(input).toHaveAttribute('autocapitalize', 'off');
  expect(input).toHaveAttribute('spellcheck', 'false');
});

test('does not query for empty input', async () => {
  const spy = vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);
  await new Promise((r) => setTimeout(r, 300));
  expect(spy).not.toHaveBeenCalled();
});

// The landing page renders two of these as flex siblings, and the first one's
// open dropdown hangs over the second one's field. Both the dropdown and the
// dot are absolutely positioned in the SAME stacking context (nothing between
// them creates one), so at equal z-index the tie breaks on DOM order — and the
// second field's dot comes later in the document than the first field's list.
// That is the defect the owner found: the green dot sat on top of the open
// dropdown. jsdom has no layout and cannot check paint order, so this asserts
// the ordering invariant that governs it: a dropdown outranks a field dot.
function zRank(el: Element | null | undefined): number {
  const match = (el?.getAttribute('class') ?? '').match(/(?:^|\s)z-(\d+)(?:\s|$)/);
  return match ? Number(match[1]) : 0;
}

test('an open dropdown outranks the next field\'s dot', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 0.8, spotifyId: null, appleId: null, facts: null },
  ]);
  const { container } = render(
    <>
      <ArtistSearch label="From" end="start" onSelect={vi.fn()} />
      <ArtistSearch label="To" end="destination" onSelect={vi.fn()} />
    </>,
  );

  await user.type(screen.getByLabelText('From'), 'miles');
  await screen.findByText('Miles Davis');

  const dropdown = container.querySelector('ul');
  const dots = container.querySelectorAll('span[aria-hidden]');
  expect(dropdown).not.toBeNull();
  expect(dots).toHaveLength(2);

  // Strictly greater, not >=: equality IS the bug, because DOM order then
  // decides and it decides against the dropdown.
  expect(zRank(dropdown)).toBeGreaterThan(zRank(dots[1]));
});
