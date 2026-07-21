import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { usePath } from './usePath';

function Harness() {
  const state = usePath();
  return <div data-testid="state">{state.status}:{state.error ?? ''}:{state.artists.map(a => a.name).join(',')}</div>;
}

function renderAt(url: string) {
  return render(
    <MemoryRouter initialEntries={[url]}>
      <Routes><Route path="/path/:from/:to" element={<Harness />} /></Routes>
    </MemoryRouter>,
  );
}

afterEach(() => vi.restoreAllMocks());

test('resolves and exposes artists', async () => {
  vi.spyOn(client, 'buildPath').mockResolvedValue([
    { mbid: 'a', name: 'Miles', disambiguation: '', popularity: 1 },
  ]);
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('ready::Miles'));
});

test('passes decoded exclusions to buildPath', async () => {
  const spy = vi.spyOn(client, 'buildPath').mockResolvedValue([]);
  renderAt('/path/a/b?dislike=z&known=y');
  await waitFor(() => expect(spy).toHaveBeenCalledWith(
    ['a', 'b'],
    [{ id: 'z', reason: 'dislike' }, { id: 'y', reason: 'known' }],
    expect.any(AbortSignal),
  ));
});

test('maps 409 to nopath', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(409));
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:nopath:'));
});

test('maps 404 to notfound', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.ApiError(404));
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:notfound:'));
});
