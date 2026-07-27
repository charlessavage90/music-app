import indexHtml from '../../index.html?raw';
import { act } from 'react';
import { createRoot } from 'react-dom/client';
import { MemoryRouter } from 'react-router-dom';
import App from '../App';

// FRO-7 / RMD-12. Every failure that stops the JavaScript arriving renders the
// same thing today: a white screen with no text. The reviewer verified the
// commonest cause live — an object synced by the runbook carries no
// Cache-Control, so a browser holds index.html on heuristic freshness, and the
// next deploy's `--delete` removes the hashed asset that stale copy points at.
// The other half of the fix is the runbook's two-pass sync (infra/README.md §6);
// this half is what a visitor sees when it fails anyway.
//
// index.html is read from disk rather than restated here, so the file this
// asserts about is the file that ships. Imported with Vite's ?raw rather than
// node:fs on purpose: tsconfig.app.json gives src/ no node types, and adding
// them to make one test compile would let any app module import node builtins
// and still typecheck. `vite/client` already declares ?raw.

function parsedIndex(): Document {
  return new DOMParser().parseFromString(indexHtml, 'text/html');
}

function normalise(text: string | null): string {
  return (text ?? '').replace(/\s+/g, ' ').trim();
}

test('a browser that gets the page but never runs the JS sees words, not a blank screen', () => {
  const root = parsedIndex().querySelector('#root');
  expect(root).not.toBeNull();
  expect(normalise(root!.textContent).length).toBeGreaterThan(0);
});

test('the app replaces the fallback instead of rendering underneath it', async () => {
  // The fallback is only safe if React owns it. Placed as a SIBLING of #root it
  // would be correct on the way in and then sit under the app forever, so this
  // mounts into the real document structure rather than into a bare div.
  const parsed = parsedIndex();
  const fallbackText = normalise(parsed.querySelector('#root')!.textContent);
  expect(fallbackText.length).toBeGreaterThan(0);

  document.body.innerHTML = parsed.body.innerHTML;
  const root = document.getElementById('root')!;

  await act(async () => {
    createRoot(root).render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>,
    );
  });

  expect(normalise(document.body.textContent)).not.toContain(fallbackText);
});
