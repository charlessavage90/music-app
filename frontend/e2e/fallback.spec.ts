import { expect, test } from '@playwright/test';

// FRO-7 / RMD-12. index.html carries static markup inside #root so that a
// visitor who gets the page but never gets the JavaScript sees words instead of
// a white screen. The whole design depends on React clearing the container it
// owns — so the failure mode is not "the fallback is missing", it is "the
// fallback is still there, under the app, forever".
//
// The unit test asserts this in jsdom. It is repeated here because every other
// e2e spec would pass with the fallback sitting on the page: they look for app
// elements, and leftover text does not stop those existing.

test('the loading fallback is gone once the app has mounted', async ({ page }) => {
  await page.goto('/');

  // This assertion first, deliberately. The fallback and the landing page share
  // a heading, so checking the heading first fails on a strict-mode violation —
  // a real detection, but one whose message says nothing about what broke.
  await expect(page.getByText(/the app did not load/i)).toHaveCount(0);
  await expect(page.getByRole('img', { name: 'Unsung.fm' })).toBeVisible();
});
