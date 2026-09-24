import { expect, test } from 'vitest';
import { COUNT_KEY, addExclusion, clearExclusions, decodeExclusions, linkIntegrity } from './exclusions';

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

// ---- Issue #187: a link cut in transit must not silently become a different
// journey. The count goes FIRST, so any cut that drops ids leaves it behind.

test('addExclusion writes the exclusion count as the first parameter', () => {
  const once = addExclusion(new URLSearchParams(), 'a', 'known');
  const twice = addExclusion(once, 'b', 'known');
  expect(twice.toString()).toBe('n=2&known=a%2Cb');
  expect([...twice.keys()][0]).toBe(COUNT_KEY);
});

test('the count covers a legacy dislike list extended by a new press', () => {
  const out = addExclusion(new URLSearchParams('dislike=a,b'), 'c', 'known');
  expect(out.get(COUNT_KEY)).toBe('3');
  expect(linkIntegrity(out)).toBeNull();
});

test('clearExclusions drops the count with the lists', () => {
  const out = clearExclusions(new URLSearchParams('n=1&known=c'));
  expect(out.toString()).toBe('');
});

test('a whole link is intact', () => {
  expect(linkIntegrity(new URLSearchParams('n=3&known=a,b,c'))).toBeNull();
});

test('a link cut at an id boundary is detected', () => {
  // The case the issue names: whole ids dropped, every survivor well-formed,
  // so the server has nothing to complain about.
  const full = addExclusion(addExclusion(addExclusion(new URLSearchParams(), 'a', 'known'), 'b', 'known'), 'c', 'known').toString();
  const cut = full.slice(0, full.indexOf('%2Cc'));
  expect(linkIntegrity(new URLSearchParams(cut))).toEqual({ expected: 3, found: 2 });
});

test('a link cut before the list starts is detected', () => {
  expect(linkIntegrity(new URLSearchParams('n=3'))).toEqual({ expected: 3, found: 0 });
  expect(linkIntegrity(new URLSearchParams('n=3&kno'))).toEqual({ expected: 3, found: 0 });
});

test('a count that is itself cut or garbled is reported with no expectation', () => {
  expect(linkIntegrity(new URLSearchParams('n='))).toEqual({ expected: null, found: 0 });
  expect(linkIntegrity(new URLSearchParams('n=x&known=a'))).toEqual({ expected: null, found: 1 });
});

test('a link from before the count existed is not flagged', () => {
  // Every link shared before issue #187 has no count. It cannot be checked,
  // and flagging it would call every old link broken.
  expect(linkIntegrity(new URLSearchParams('known=a,b'))).toBeNull();
  expect(linkIntegrity(new URLSearchParams('dislike=a&known=b'))).toBeNull();
  expect(linkIntegrity(new URLSearchParams())).toBeNull();
});
