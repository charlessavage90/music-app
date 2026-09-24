import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { PlayerBar } from './PlayerBar';

const base = { currentName: 'Herbie Hancock', trackTitle: 'Watermelon Man', isPlaying: true, onToggle: vi.fn(), onRetry: vi.fn() };

test('shows elapsed and total time and the stop position in the whole-journey currency', () => {
  // UXR-D10: N of M counts EVERY artist including both endpoints; index is 0-based in.
  render(<PlayerBar {...base} position={11.2} duration={30} stopIndex={1} stopCount={6} />);
  expect(screen.getByText('0:11')).toBeInTheDocument();
  expect(screen.getByText('0:30')).toBeInTheDocument();
  expect(screen.getByText('Stop 2 of 6')).toBeInTheDocument();
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '37');
});

test('the bar play button names what is playing', () => {
  render(<PlayerBar {...base} position={0} duration={30} stopIndex={1} stopCount={6} />);
  expect(screen.getByRole('button', { name: 'Pause Herbie Hancock' })).toBeInTheDocument();
});

// G3-F1: a failed clip keeps the bar, says why, and offers a way back.
test.each([
  ['no-clip', /no preview for this artist right now/i],
  ['unreachable', /couldn.t reach the preview service/i],
  ['wont-play', /this clip wouldn.t play/i],
] as const)('a %s failure is stated with a retry', async (failure, message) => {
  const onRetry = vi.fn();
  render(
    <PlayerBar {...base} isPlaying={false} position={0} duration={0} stopIndex={1} stopCount={6}
      failure={failure} onRetry={onRetry} />,
  );
  expect(screen.getByRole('status')).toHaveTextContent(message);
  expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  await userEvent.setup().click(screen.getByRole('button', { name: 'Retry Herbie Hancock' }));
  expect(onRetry).toHaveBeenCalledTimes(1);
});

test('renders nothing with no current artist', () => {
  const { container } = render(<PlayerBar {...base} currentName={null} position={0} duration={0} stopIndex={-1} stopCount={0} />);
  expect(container).toBeEmptyDOMElement();
});
