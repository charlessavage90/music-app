import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { RerollNotice } from './RerollNotice';

test('names what the dislike signal does', () => {
  render(<RerollNotice reason="dislike" />);
  expect(screen.getByText(/steering around that sound/i)).toBeInTheDocument();
});

test('names what the known signal does', () => {
  render(<RerollNotice reason="known" />);
  expect(screen.getByText(/digging for someone newer/i)).toBeInTheDocument();
});

test('names what a reset does', () => {
  render(<RerollNotice reason="reset" />);
  expect(screen.getByText(/back to the original path/i)).toBeInTheDocument();
});

// The bypass buttons stay pressable underneath: they work today, and usePath
// aborts a superseded request safely.
test('does not intercept pointer events', () => {
  const { container } = render(<RerollNotice reason="dislike" />);
  expect(container.firstElementChild?.className).toContain('pointer-events-none');
});
