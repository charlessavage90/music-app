import { render, screen } from '@testing-library/react';
import { expect, test, vi } from 'vitest';
import { PlayerBar } from './PlayerBar';

const base = { currentName: 'Herbie Hancock', trackTitle: 'Watermelon Man', isPlaying: true, onToggle: vi.fn() };

test('shows elapsed and total time and the stop position in the whole-journey currency', () => {
  // UXR-D10: N of M counts EVERY artist including both endpoints; index is 0-based in.
  render(<PlayerBar {...base} position={11.2} duration={30} stopIndex={1} stopCount={6} />);
  expect(screen.getByText('0:11')).toBeInTheDocument();
  expect(screen.getByText('0:30')).toBeInTheDocument();
  expect(screen.getByText('Stop 2 of 6')).toBeInTheDocument();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '37');
});

test('renders nothing with no current artist', () => {
  const { container } = render(<PlayerBar {...base} currentName={null} position={0} duration={0} stopIndex={-1} stopCount={0} />);
  expect(container).toBeEmptyDOMElement();
});
