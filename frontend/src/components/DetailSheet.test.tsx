import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { DetailSheet } from './DetailSheet';

test('is a dialog that closes on Escape and on the scrim, and renders nothing when closed', async () => {
  const user = userEvent.setup();
  const onClose = vi.fn();
  const { rerender } = render(<DetailSheet open onClose={onClose}><p>content</p></DetailSheet>);
  expect(screen.getByRole('dialog')).toBeInTheDocument();
  await user.keyboard('{Escape}');
  expect(onClose).toHaveBeenCalledTimes(1);
  await user.click(screen.getByTestId('scrim'));
  expect(onClose).toHaveBeenCalledTimes(2);
  rerender(<DetailSheet open={false} onClose={onClose}><p>content</p></DetailSheet>);
  expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
});

// The listener is on the document, so a sheet that has been closed and left
// mounted must not keep answering Escape for the page behind it.
test('a closed sheet stops listening for Escape', async () => {
  const user = userEvent.setup();
  const onClose = vi.fn();
  const { rerender } = render(<DetailSheet open onClose={onClose}><p>content</p></DetailSheet>);
  rerender(<DetailSheet open={false} onClose={onClose}><p>content</p></DetailSheet>);
  await user.keyboard('{Escape}');
  expect(onClose).not.toHaveBeenCalled();
});
