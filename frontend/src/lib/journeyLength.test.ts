import { expect, test } from 'vitest';
import { journeyLength } from './journeyLength';

// Issue #202, the owner's ruling 2026-09-24: a journey's length is every artist
// on it INCLUDING the two chosen. A journey from A to B through five others is
// seven stops wherever the app names a length. This is the one place that
// convention is written down; every surface that states a length calls it.
test('a journey through five artists between two endpoints is seven stops', () => {
  const artists = ['A', 'v', 'w', 'x', 'y', 'z', 'B'];
  expect(journeyLength(artists)).toBe(7);
});

test('the shortest journey the app offers, two adjacent artists, is two stops', () => {
  expect(journeyLength(['A', 'B'])).toBe(2);
});
