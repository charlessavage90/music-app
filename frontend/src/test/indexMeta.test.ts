import indexHtml from '../../index.html?raw';

// Issue #191. Link-preview crawlers do not run JavaScript, so what they show
// is exactly these static tags. Read from the file that ships (see
// indexFallback.test.tsx for why ?raw rather than node:fs).

const head = new DOMParser().parseFromString(indexHtml, 'text/html').head;

function meta(attr: 'name' | 'property', key: string): string | null {
  return head.querySelector(`meta[${attr}="${key}"]`)?.getAttribute('content') ?? null;
}

test('a shared link previews with a title, a description and an image', () => {
  expect(meta('property', 'og:title')).toBe('Unsung.fm');
  expect(meta('property', 'og:description')).toMatch(/two artists/i);
  expect(meta('name', 'description')).toMatch(/two artists/i);
  expect(meta('property', 'og:url')).toBe('https://unsung.fm/');
  expect(meta('property', 'og:type')).toBe('website');
  expect(meta('name', 'twitter:card')).toBe('summary');
});

test('the preview image is an absolute URL to a file that ships', () => {
  // Crawlers do not resolve relative og:image paths reliably, and the path
  // must be one public/ actually serves.
  const image = meta('property', 'og:image');
  expect(image).toBe('https://unsung.fm/unsung-mark.png');
  expect(head.querySelector('link[rel="icon"]')?.getAttribute('href')).toBe('/unsung-mark.png');
});
