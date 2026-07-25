import { expect, test } from '@playwright/test';

// Requires the API on :8000 and the dev server (started by webServer).
//
// These two defects reached the owner's ears while the unit suite stayed green,
// and neither is reproducible in jsdom or in bundled Chromium:
//
//  - Real Chrome is required because Playwright's Chromium ships without the MP3
//    codec, so a clip never plays and never ends naturally.
//  - A *natural* `ended` is required because the browser drains microtasks between
//    listener callbacks, which a JS-dispatched event does not. That difference is
//    exactly what hid the auto-advance skip.
//
// See the gate-1 execution log §18.
test.use({ channel: 'chrome' });

const MILES = '561d854a-6a28-4aa7-8c99-323e6ce46c2a';
const DAFT = '056e4f3e-d505-4dad-8ec1-d04f521cbb56';

/** Exposes every `Audio` the app constructs; `new Audio()` is never in the DOM. */
async function trackAudioElements(page: import('@playwright/test').Page) {
  await page.addInitScript(() => {
    const w = window as unknown as Record<string, unknown>;
    w.__audios = [] as HTMLAudioElement[];
    const Orig = window.Audio;
    class Tracked extends Orig {
      constructor(...args: unknown[]) {
        // @ts-expect-error passthrough
        super(...args);
        (w.__audios as HTMLAudioElement[]).push(this);
      }
    }
    // @ts-expect-error replacing the constructor
    window.Audio = Tracked;
  });
}

/** Seeks the playing clip to just before its end and waits for a real `ended`. */
async function playToEnd(page: import('@playwright/test').Page) {
  await page.evaluate(async () => {
    const audios = (window as never as { __audios: HTMLAudioElement[] }).__audios;
    const a = audios.find((x) => x.src && !x.paused) ?? audios.find((x) => x.src);
    if (!a) throw new Error('no audio element is playing');
    if (!Number.isFinite(a.duration) || a.duration === 0) {
      await new Promise((r) => a.addEventListener('loadedmetadata', r, { once: true }));
    }
    a.currentTime = Math.max(0, a.duration - 0.4);
  });
  await page.waitForTimeout(3000);
}

async function playingCardIndex(page: import('@playwright/test').Page, cards: number) {
  for (let i = 0; i < cards; i++) {
    if ((await page.locator('ol li').nth(i).innerText()).match(/now playing/i)) return i;
  }
  return -1;
}

test('a finished clip advances to the very next artist, never skipping one', async ({ page }) => {
  await trackAudioElements(page);
  await page.goto(`/path/${MILES}/${DAFT}`);
  await page.waitForSelector('ol li');
  const cards = await page.locator('ol li').count();

  const firstPlay = page.locator('ol li').nth(0).getByRole('button', { name: /play|pause/i });
  await expect(firstPlay).toBeEnabled({ timeout: 15000 });

  // Only meaningful while consecutive cards actually have clips: a silent card is
  // skipped by design, which would look identical to the defect.
  for (let i = 0; i < 3; i++) {
    await expect(page.locator('ol li').nth(i).getByRole('button', { name: /play|pause/i })).toBeEnabled();
  }

  await firstPlay.click();
  await expect.poll(() => playingCardIndex(page, cards)).toBe(0);

  await playToEnd(page);
  expect(await playingCardIndex(page, cards)).toBe(1);

  await playToEnd(page);
  expect(await playingCardIndex(page, cards)).toBe(2);
});

test('leaving for a new path silences the clip', async ({ page }) => {
  await trackAudioElements(page);
  await page.goto(`/path/${MILES}/${DAFT}`);
  await page.waitForSelector('ol li');

  const firstPlay = page.locator('ol li').nth(0).getByRole('button', { name: /play|pause/i });
  await expect(firstPlay).toBeEnabled({ timeout: 15000 });
  await firstPlay.click();

  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as never as { __audios: HTMLAudioElement[] }).__audios.some((a) => a.src && !a.paused),
      ),
    )
    .toBe(true);

  await page.getByRole('link', { name: /new path/i }).click();

  await expect
    .poll(async () =>
      page.evaluate(() =>
        (window as never as { __audios: HTMLAudioElement[] }).__audios.some((a) => !a.paused),
      ),
    )
    .toBe(false);
});
