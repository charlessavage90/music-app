import { render, screen, waitFor } from '@testing-library/react';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { ArtistCountBadge } from './ArtistCountBadge';

afterEach(() => vi.restoreAllMocks());

test('floors the count to the nearest thousand and says what the map is', async () => {
  vi.spyOn(client, 'getMeta').mockResolvedValue({ artists: 58838, graphSha256: 'x' });
  render(<ArtistCountBadge />);
  expect(await screen.findByText('58,000 artists mapped by who listens to whom')).toBeInTheDocument();
});

test('renders nothing at all when the request fails — a decoration cannot break the page (UI-7)', async () => {
  vi.spyOn(client, 'getMeta').mockRejectedValue(new Error('down'));
  const { container } = render(<ArtistCountBadge />);
  await waitFor(() => expect(client.getMeta).toHaveBeenCalled());
  expect(container).toBeEmptyDOMElement();
});
