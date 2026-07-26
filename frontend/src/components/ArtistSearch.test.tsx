import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistSearch } from './ArtistSearch';

afterEach(() => vi.restoreAllMocks());

test('debounces, shows results, and selects one', async () => {
  const user = userEvent.setup();
  vi.spyOn(client, 'searchArtists').mockResolvedValue([
    { mbid: 'm', name: 'Miles Davis', disambiguation: '', popularity: 0.8 },
  ]);
  const onSelect = vi.fn();
  render(<ArtistSearch label="From" onSelect={onSelect} />);

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
      initial={{ mbid: 'd', name: 'Daft Punk', disambiguation: '', popularity: 1 }}
      onSelect={onSelect}
    />,
  );

  // Arriving prefilled is not an edit and must not report anything.
  expect(onSelect).not.toHaveBeenCalled();

  await user.type(screen.getByLabelText('To'), '!');

  expect(onSelect).toHaveBeenCalledWith(null);
});

test('does not query for empty input', async () => {
  const spy = vi.spyOn(client, 'searchArtists').mockResolvedValue([]);
  render(<ArtistSearch label="From" onSelect={vi.fn()} />);
  await new Promise((r) => setTimeout(r, 300));
  expect(spy).not.toHaveBeenCalled();
});
