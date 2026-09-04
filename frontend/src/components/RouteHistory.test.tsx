import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { RouteHistory } from './RouteHistory';

const ok = (mbid: string, name: string) => ({ mbid, name, loading: false });

test('nothing is rendered when no artist has been skipped', () => {
  const { container } = render(<RouteHistory bypassed={[]} />);
  expect(container).toBeEmptyDOMElement();
});

// The URL lists presses oldest-first; the panel shows the most recent at the
// top, which is the order the owner's mockup draws.
test('the most recent press is at the top and the original route at the bottom', () => {
  render(<RouteHistory bypassed={[ok('a', 'Alice Coltrane'), ok('b', 'Sun Ra')]} />);
  const rows = screen.getAllByRole('listitem').map((li) => li.textContent);
  expect(rows[0]).toContain('Sun Ra');
  expect(rows[1]).toContain('Alice Coltrane');
  expect(rows[2]).toContain('Original route');
});

test('the caption says Back undoes a press', () => {
  render(<RouteHistory bypassed={[ok('a', 'Alice Coltrane')]} />);
  expect(screen.getByText(/back undoes/i)).toBeInTheDocument();
});

// LUX-D2: a row that cannot name its artist says so. It must neither vanish
// (losing a press the router also ignored) nor render a blank line.
test('an unresolvable artist gets a stated row rather than a blank one', () => {
  render(<RouteHistory bypassed={[{ mbid: 'gone', name: null, loading: false }]} />);
  expect(screen.getByText(/no longer in the map/i)).toBeInTheDocument();
});
