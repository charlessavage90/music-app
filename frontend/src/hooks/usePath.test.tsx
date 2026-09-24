import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { afterEach, expect, test, vi } from 'vitest';
import * as client from '@/api/client';
import { usePath } from './usePath';

function Harness() {
  const state = usePath();
  return (
    <>
      <div data-testid="state">{state.status}:{state.error ?? ''}:{state.artists.map(a => a.name).join(',')}</div>
      <div data-testid="stop-rule">{state.stopRule}</div>
      <div data-testid="message">{state.message ?? ''}</div>
      <div data-testid="limit">{state.limit ?? ''}</div>
      <button type="button" onClick={state.retry}>retry</button>
    </>
  );
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
  vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: [{ mbid: 'a', name: 'Miles', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null }],
    stopRule: 'natural',
    bypassed: [],
    unresolved: [],
  });
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('ready::Miles'));
});

test('passes decoded exclusions to buildPath', async () => {
  const spy = vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: [], stopRule: 'natural', bypassed: [], unresolved: [],
  });
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

test('classifies a timeout distinctly from an unknown failure', async () => {
  // A cold instance that never answers must not read as a generic failure:
  // it is the one error state with a useful response (wait and retry).
  vi.spyOn(client, 'buildPath').mockRejectedValue(new client.TimeoutError(20_000));
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:timeout:'));
});

test('maps a 422 with a readable reason to invalid, carrying the message', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(
    new client.ApiError(422, 'pick two different artists — a journey needs somewhere to go'),
  );
  renderAt('/path/a/a');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:invalid:'));
  expect(screen.getByTestId('message')).toHaveTextContent('pick two different artists');
});

test('maps the bypass cap to toomany, carrying the server\'s limit', async () => {
  vi.spyOn(client, 'buildPath').mockRejectedValue(
    new client.ApiError(422, 'List should have at most 200 items after validation, not 201', {
      kind: 'too_many_exclusions', max: 200,
    }),
  );
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:toomany:'));
  expect(screen.getByTestId('limit')).toHaveTextContent('200');
});

// Issue #185. The URL does not change on a retry, so the attempt counter is the
// only thing that re-runs the request. Deleting it leaves "Try again" inert,
// and this is the test that notices.
test('retry() rebuilds the same path, so a timed-out request can recover', async () => {
  const user = userEvent.setup();
  const spy = vi.spyOn(client, 'buildPath')
    .mockRejectedValueOnce(new client.TimeoutError(20_000))
    .mockResolvedValueOnce({
      artists: [{ mbid: 'a', name: 'Miles', disambiguation: '', popularity: 1, spotifyId: null, appleId: null, facts: null }],
      stopRule: 'natural', bypassed: [], unresolved: [],
    });
  renderAt('/path/a/b?known=z');
  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('error:timeout:'));

  await user.click(screen.getByRole('button', { name: 'retry' }));

  await waitFor(() => expect(screen.getByTestId('state')).toHaveTextContent('ready::Miles'));
  expect(spy).toHaveBeenCalledTimes(2);
  // The same request, not a fresh one: same endpoints, same exclusions.
  expect(spy.mock.calls[1][0]).toEqual(spy.mock.calls[0][0]);
  expect(spy.mock.calls[1][1]).toEqual(spy.mock.calls[0][1]);
});

test('exposes the stop rule from the response', async () => {
  vi.spyOn(client, 'buildPath').mockResolvedValue({
    artists: [{ mbid: 'a', name: 'A', disambiguation: '', popularity: 0.5, spotifyId: null, appleId: null, facts: null }],
    stopRule: 'adjacent_only',
    bypassed: [],
    unresolved: [],
  });
  renderAt('/path/a/b');
  await waitFor(() => expect(screen.getByTestId('stop-rule')).toHaveTextContent('adjacent_only'));
});
