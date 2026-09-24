import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { expect, test, vi } from 'vitest';
import { PlayButton } from './PlayButton';

test('is labelled Play when it will start playback', () => {
  render(<PlayButton state="play" size="card" onClick={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Play' })).toBeInTheDocument();
});

test('is labelled Pause when it will stop playback', () => {
  render(<PlayButton state="pause" size="card" onClick={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Pause' })).toBeInTheDocument();
});

// G3-F4 (issue #188): a journey is eight of these, and a screen reader's
// button list read "Play, Play, Play…" with nothing to tell them apart.
test('names the artist it plays when given one', () => {
  const { rerender } = render(<PlayButton state="play" size="card" name="Miles Davis" onClick={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Play Miles Davis' })).toBeInTheDocument();
  rerender(<PlayButton state="pause" size="card" name="Miles Davis" onClick={vi.fn()} />);
  expect(screen.getByRole('button', { name: 'Pause Miles Davis' })).toBeInTheDocument();
});

test('does not fire when disabled', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();
  render(<PlayButton state="play" size="card" disabled onClick={onClick} />);
  const button = screen.getByRole('button', { name: 'Play' });
  expect(button).toBeDisabled();
  await user.click(button);
  expect(onClick).not.toHaveBeenCalled();
});

test('fires when enabled', async () => {
  const user = userEvent.setup();
  const onClick = vi.fn();
  render(<PlayButton state="play" size="card" onClick={onClick} />);
  await user.click(screen.getByRole('button', { name: 'Play' }));
  expect(onClick).toHaveBeenCalled();
});
