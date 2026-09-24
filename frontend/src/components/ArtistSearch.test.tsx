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

// ---- Issue #190: the dropdown must be dismissible. It hangs over the "To"
// field, so a list that never closes is one you can pick a rejected artist from.

const MILES = { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 0.8, spotifyId: null, appleId: null, facts: null };

async function openList(user: ReturnType<typeof userEvent.setup>) {
  vi.spyOn(client, 'searchArtists').mockResolvedValue([MILES]);
  await user.type(screen.getByLabelText('From'), 'miles');
  await screen.findByRole('button', { name: /miles davis/i });
}

test('Escape closes the dropdown and keeps focus in the field', async () => {
  const user = userEvent.setup();
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);
  await openList(user);

  await user.keyboard('{Escape}');

  expect(screen.queryByRole('button', { name: /miles davis/i })).not.toBeInTheDocument();
  expect(screen.getByLabelText('From')).toHaveFocus();
});

test('Escape from inside the list closes it and returns focus to the field', async () => {
  const user = userEvent.setup();
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);
  await openList(user);

  await user.tab();
  expect(screen.getByRole('button', { name: /miles davis/i })).toHaveFocus();
  await user.keyboard('{Escape}');

  expect(screen.queryByRole('button', { name: /miles davis/i })).not.toBeInTheDocument();
  expect(screen.getByLabelText('From')).toHaveFocus();
});

test('moving focus to another field closes the dropdown', async () => {
  const user = userEvent.setup();
  render(
    <>
      <ArtistSearch label="From" end="start" onSelect={vi.fn()} />
      <input aria-label="elsewhere" />
    </>,
  );
  await openList(user);

  await user.click(screen.getByLabelText('elsewhere'));

  expect(screen.queryByRole('button', { name: /miles davis/i })).not.toBeInTheDocument();
});

test('a click outside, on nothing focusable, closes the dropdown', async () => {
  const user = userEvent.setup();
  render(
    <>
      <ArtistSearch label="From" end="start" onSelect={vi.fn()} />
      <p>somewhere else on the page</p>
    </>,
  );
  await openList(user);

  await user.click(screen.getByText('somewhere else on the page'));

  expect(screen.queryByRole('button', { name: /miles davis/i })).not.toBeInTheDocument();
});

test('tabbing from the field into the list does not close it, and Enter chooses', async () => {
  // The blur that closes the list must not fire on the way INTO it — that is
  // the keyboard path to choosing an artist.
  const user = userEvent.setup();
  const onSelect = vi.fn();
  render(<ArtistSearch label="From" end="start" onSelect={onSelect} />);
  await openList(user);

  await user.tab();
  await user.keyboard('{Enter}');

  expect(onSelect).toHaveBeenCalledWith(expect.objectContaining({ mbid: 'm' }));
  // Not dropped to <body> with the entry that unmounted.
  expect(screen.getByLabelText('From')).toHaveFocus();
  expect(screen.queryByRole('button', { name: /miles davis/i })).not.toBeInTheDocument();
});

test('pressing an entry does not blur the field first, so the click still lands', async () => {
  // Safari does not focus a button on click, so the field's blur would carry
  // no relatedTarget and close the list before the click arrived. Holding
  // focus in the field on mousedown is what makes click-to-choose reliable.
  const user = userEvent.setup();
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);
  await openList(user);

  const option = screen.getByRole('button', { name: /miles davis/i });
  const down = new MouseEvent('mousedown', { bubbles: true, cancelable: true });
  option.dispatchEvent(down);

  expect(down.defaultPrevented).toBe(true);
});

test('refocusing the field reopens results it was dismissed from', async () => {
  const user = userEvent.setup();
  render(
    <>
      <ArtistSearch label="From" end="start" onSelect={vi.fn()} />
      <input aria-label="elsewhere" />
    </>,
  );
  await openList(user);
  await user.click(screen.getByLabelText('elsewhere'));
  expect(screen.queryByRole('button', { name: /miles davis/i })).not.toBeInTheDocument();

  await user.click(screen.getByLabelText('From'));

  expect(screen.getByRole('button', { name: /miles davis/i })).toBeInTheDocument();
});

// ---- Issue #188: results and errors were never announced.

test('the result count is announced in a live region', async () => {
  const user = userEvent.setup();
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);
  await openList(user);

  expect(screen.getByRole('status')).toHaveTextContent('1 artist found');
});

test('an empty search and a failed search are announced', async () => {
  const user = userEvent.setup();
  const spy = vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  render(<ArtistSearch label="From" end="start" onSelect={vi.fn()} />);

  // The live region must exist BEFORE its text changes, or it is not read.
  const region = screen.getByRole('status');
  await user.type(screen.getByLabelText('From'), 'zzzz');
  await screen.findByText(/no artists found/i);
  expect(region).toHaveTextContent(/no artists found/i);

  spy.mockRejectedValue(new Error('network'));
  await user.type(screen.getByLabelText('From'), 'q');
  await screen.findByText(/search is unavailable/i);
  expect(region).toHaveTextContent(/search is unavailable/i);
});
