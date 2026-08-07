import { expect, test } from '@playwright/test';

// Requires the API running on :8000, and the dev server (started by webServer).
// (The 5k dev fixture this once named is retired; :8000 boots the adopted graph.)
test('search, path, bypass produces a new path without the bypassed artist', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('From').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('To').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /find path/i }).click();

  // The path renders as a list of cards.
  await expect(page.getByText('Miles Davis')).toBeVisible();
  const before = await page.locator('ol li').allInnerTexts();
  expect(before.length).toBeGreaterThan(1);

  // Bypass the second artist with "steer away", which now sits behind that
  // card's footer strip — so the walk is open the tray, then choose.
  // UI-13: located by data-testid, not `.font-semibold`. The endpoint eyebrow
  // ("Starting artist") is also font-semibold, so .nth(1) silently became the
  // FIRST card's name — and the assertion below then demanded that the start
  // artist disappear, which it never can. A test hook must not be a style hook.
  const second = page.locator('ol li').nth(1);
  const secondName = await second.getByTestId('artist-name').innerText();
  await second.getByRole('button', { name: /rebuild from here/i }).click();
  await second.getByRole('button', { name: /steer away/i }).click();

  // URL now carries the exclusion, and the bypassed artist is gone from the new path.
  await expect(page).toHaveURL(/dislike=/);
  await expect(page.getByText(secondName, { exact: true })).toHaveCount(0);
});
