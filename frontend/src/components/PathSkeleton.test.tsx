import { render, screen } from '@testing-library/react';
import { expect, test } from 'vitest';
import { PathSkeleton } from './PathSkeleton';

const artist = (name: string) => ({ mbid: name, name, disambiguation: '', popularity: 0 });

test('names both endpoints when they are known', () => {
  render(<PathSkeleton from={artist('Nirvana')} to={artist('Cocteau Twins')} />);
  expect(screen.getByText('Nirvana')).toBeInTheDocument();
  expect(screen.getByText('Cocteau Twins')).toBeInTheDocument();
  expect(screen.getByText(/listening for the steps between them/i)).toBeInTheDocument();
});

// UI-7: the lookup is decorative and may fail. The screen must still render.
test('degrades without endpoint names', () => {
  render(<PathSkeleton from={null} to={null} />);
  expect(screen.getByText(/listening for the steps between them/i)).toBeInTheDocument();
  expect(screen.getByText(/this usually takes a few seconds/i)).toBeInTheDocument();
});

test('offers nothing to press', () => {
  render(<PathSkeleton from={artist('Nirvana')} to={artist('Cocteau Twins')} />);
  expect(screen.queryByRole('button')).not.toBeInTheDocument();
});
