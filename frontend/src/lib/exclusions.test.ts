import { expect, test } from 'vitest';
import { addExclusion, clearExclusions, decodeExclusions } from './exclusions';

test('decodeExclusions reads both lists, dislikes first', () => {
  const params = new URLSearchParams('dislike=a,b&known=c');
  expect(decodeExclusions(params)).toEqual([
    { id: 'a', reason: 'dislike' },
    { id: 'b', reason: 'dislike' },
    { id: 'c', reason: 'known' },
  ]);
});

test('decodeExclusions returns [] when absent', () => {
  expect(decodeExclusions(new URLSearchParams())).toEqual([]);
});

test('addExclusion appends to the correct list and does not mutate input', () => {
  const input = new URLSearchParams('dislike=a');
  const out = addExclusion(input, 'b', 'dislike');
  expect(out.get('dislike')).toBe('a,b');
  expect(input.get('dislike')).toBe('a'); // unchanged
});

test('addExclusion is idempotent (no duplicates)', () => {
  const out = addExclusion(new URLSearchParams('known=c'), 'c', 'known');
  expect(out.get('known')).toBe('c');
});

test('addExclusion writes known separately from dislike', () => {
  const out = addExclusion(new URLSearchParams('dislike=a'), 'c', 'known');
  expect(out.get('dislike')).toBe('a');
  expect(out.get('known')).toBe('c');
});

test('clearExclusions strips both lists', () => {
  const out = clearExclusions(new URLSearchParams('dislike=a&known=c'));
  expect(out.has('dislike')).toBe(false);
  expect(out.has('known')).toBe(false);
});
