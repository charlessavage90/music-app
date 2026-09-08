// Two screenshots per page at the two widths the spec names (UXR spec §6).
// Not a test: run by hand after any visual task. Requires the dev server on
// :5173 and the API on :8000, exactly as `npm run test:e2e` does.
//   node e2e/screenshot.mjs /                      -> landing
//   node e2e/screenshot.mjs /path/<from>/<to>      -> journey
// From Git Bash prefix MSYS_NO_PATHCONV=1, or the shell rewrites "/" into a
// Windows path before node sees it (memory: deploy-environment-traps).
import { chromium } from '@playwright/test';
import { mkdirSync } from 'node:fs';

const arg = process.argv[2] ?? '/';
const route = arg.startsWith('/') ? arg : '/';
const name = route === '/' ? 'landing' : 'journey';
mkdirSync('e2e/screenshots', { recursive: true });
const browser = await chromium.launch();
for (const width of [390, 1280]) {
  const page = await browser.newPage({ viewport: { width, height: width === 390 ? 844 : 900 } });
  await page.goto(`http://localhost:5173${route}`);
  await page.waitForTimeout(2500);
  // Cover art is a background-image from Deezer's CDN and is NOT covered by
  // the timeout above: at 2500ms a journey shot came back with seven empty
  // grey boxes and read as a regression in the card (2026-09-08, UXR-T6).
  // Nothing here is asserted, so a slow CDN must not be able to make a
  // screenshot lie about the app.
  await page.waitForLoadState('networkidle').catch(() => {});
  await page.screenshot({ path: `e2e/screenshots/${name}-${width}.png`, fullPage: true });
  await page.close();
}
await browser.close();
