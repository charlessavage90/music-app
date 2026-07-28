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
