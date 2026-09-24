import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { expect, test } from 'vitest';
import { Brand } from './Brand';

test('the brand reads as one name to assistive tech, not as "unsung" and ".fm"', () => {
  const { container } = render(<Brand size="nav" />);
  // One accessible name. The mark is decorative (alt=""), the split wordmark is
  // aria-hidden, and a single label on the whole thing carries the product name.
  expect(screen.getByRole('img', { name: 'Unsung.fm' })).toBeInTheDocument();
  expect(container.querySelector('img')?.getAttribute('alt')).toBe('');
  expect(screen.queryByText('unsung')).not.toBeNull(); // visible, but aria-hidden
  expect(screen.getAllByRole('img')).toHaveLength(1);
});

test('the hero size is larger than the nav size', () => {
  const { container: nav } = render(<Brand size="nav" />);
  const { container: hero } = render(<Brand size="hero" />);
  expect(nav.querySelector('img')?.getAttribute('width')).toBe('30');
  expect(hero.querySelector('img')?.getAttribute('width')).toBe('38');
});

// Issue #203: on the journey page the mark is the way home, as a site logo
// conventionally is. The landing page passes no href and keeps the plain mark.
test('given an href, the brand is a link home whose name says so', () => {
  render(
    <MemoryRouter>
      <Brand size="nav" href="/" />
    </MemoryRouter>,
  );
  const link = screen.getByRole('link', { name: /unsung\.fm.*home/i });
  expect(link).toHaveAttribute('href', '/');
  // Still one name: nothing inside the link announces separately.
  expect(screen.queryByRole('img', { name: 'Unsung.fm' })).not.toBeInTheDocument();
});
