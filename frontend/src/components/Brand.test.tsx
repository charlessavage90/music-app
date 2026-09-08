import { render, screen } from '@testing-library/react';
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
