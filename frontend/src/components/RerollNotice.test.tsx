import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { RerollNotice } from './RerollNotice';

// The message echoes the footer strip's own verb — "Dig deeper". That match is
// the point: the notice is the response to the press, and it read as an
// unrelated event when the words diverged.
test('names what the known signal does', () => {
  render(<RerollNotice reason="known" />);
  expect(screen.getByText(/digging deeper for someone newer/i)).toBeInTheDocument();
});

test('names what a reset does', () => {
  render(<RerollNotice reason="reset" />);
  expect(screen.getByText(/back to the original path/i)).toBeInTheDocument();
});

// The bypass control stays pressable underneath: it works today, and usePath
// aborts a superseded request safely.
test('does not intercept pointer events', () => {
  const { container } = render(<RerollNotice reason="known" />);
  expect(container.firstElementChild?.className).toContain('pointer-events-none');
});
