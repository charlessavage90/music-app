import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { expect, test, vi } from 'vitest';
import type { PathError } from '@/hooks/usePath';
import { PathStatus } from './PathStatus';

function renderStatus(error: PathError, extra: { message?: string; limit?: number } = {}) {
  const onRetry = vi.fn();
  const onClearExclusions = vi.fn();
  render(
    <MemoryRouter>
      <PathStatus error={error} {...extra} onRetry={onRetry} onClearExclusions={onClearExclusions} />
    </MemoryRouter>,
  );
  return { onRetry, onClearExclusions };
}

// Issue #185: the cold-start screen is what the first stranger of the day sees
// on a sleeping instance. Deleting it must fail a test.
test('a timeout says the server may be waking up and offers to try again', async () => {
  const user = userEvent.setup();
  const { onRetry } = renderStatus('timeout');

  expect(screen.getByText(/server may still be waking up/i)).toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: 'Try again' }));
  expect(onRetry).toHaveBeenCalledTimes(1);
});

// Issue #193: the server's own reason, not "Something went wrong".
test('a 422 with a readable reason shows the server\'s message', () => {
  renderStatus('invalid', { message: 'pick two different artists — a journey needs somewhere to go' });
  expect(
    screen.getByText('Pick two different artists — a journey needs somewhere to go'),
  ).toBeInTheDocument();
  expect(screen.queryByText(/something went wrong/i)).not.toBeInTheDocument();
});

test('the bypass cap says what happened, names the limit, and offers a way out', async () => {
  const user = userEvent.setup();
  const { onClearExclusions } = renderStatus('toomany', { limit: 200 });

  expect(screen.getByText(/more skips than one journey can hold \(200\)/i)).toBeInTheDocument();
  expect(screen.getByText(/press back/i)).toBeInTheDocument();
  await user.click(screen.getByRole('button', { name: /clear exclusions/i }));
  expect(onClearExclusions).toHaveBeenCalledTimes(1);
});

test('an unknown failure still falls back to the generic message', () => {
  renderStatus('unknown');
  expect(screen.getByText(/something went wrong building the path/i)).toBeInTheDocument();
});

// Issue #188: a failure replaces the path silently unless it is announced.
test.each<PathError>(['nopath', 'toomany', 'timeout', 'invalid', 'notfound', 'unknown'])(
  'the %s state is announced as an alert',
  (error) => {
    renderStatus(error, { message: 'x', limit: 200 });
    expect(screen.getByRole('alert')).toBeInTheDocument();
  },
);

// Issue #189. jsdom has no layout or colour engine, so this pins the PAIRING
// whose ratio was measured in a real browser (PR notes): dark page colour on the
// accent, 9.85:1. The defect was the buttons inheriting the light body text,
// 1.80:1 — i.e. having no text colour of their own at all.
test.each<[PathError, string]>([
  ['timeout', 'Try again'],
  ['nopath', 'Clear exclusions'],
  ['toomany', 'Clear exclusions'],
])('the %s action "%s" is dark text on the accent', (error, name) => {
  renderStatus(error);
  const cls = screen.getByRole('button', { name }).className.split(/\s+/);
  expect(cls).toContain('bg-[var(--color-accent)]');
  expect(cls).toContain('text-[var(--color-bg)]');
});
