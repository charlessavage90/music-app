import { expect, test } from '@playwright/test';

// Requires the API running on :8000 against the 5k graph, and the dev server (started by webServer).
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

  // Bypass the second artist with "not for me".
  const secondName = (await page.locator('ol li .font-semibold').nth(1).innerText());
  await page.locator('ol li').nth(1).getByRole('button', { name: /not for me/i }).click();

  // URL now carries the exclusion, and the bypassed artist is gone from the new path.
  await expect(page).toHaveURL(/dislike=/);
  await expect(page.getByText(secondName, { exact: true })).toHaveCount(0);
});
