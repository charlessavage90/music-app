import { expect, test } from '@playwright/test';

// Requires the API running on :8000, and the dev server (started by webServer).
// (The 5k dev fixture this once named is retired; :8000 boots the adopted graph.)
test('search, path, bypass produces a new path without the bypassed artist', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('From').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('To').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /discover a path/i }).click();

  // The path renders as a list of cards. Wait on the LIST, not on the artist's
  // name: the name was doing duty as the wait for navigation, and that worked
  // only for as long as the landing page never mentioned Miles Davis. It does
  // now — one of the three sample journeys is his — so the old assertion passed
  // instantly against the page we were trying to leave, and the read below then
  // raced an empty list. An implicit wait that depends on text being ABSENT
  // somewhere else is not a wait.
  await expect(page.locator('ol li').first()).toBeVisible();
  const before = await page.locator('ol li').allInnerTexts();
  expect(before.length).toBeGreaterThan(1);
  expect(before[0]).toContain('Miles Davis');

  // Bypass the second artist with "steer away", which now sits behind that
  // card's footer strip — so the walk is open the tray, then choose.
  // UI-13: located by data-testid, not `.font-semibold`. The endpoint eyebrow
  // ("Starting artist") is also font-semibold, so .nth(1) silently became the
  // FIRST card's name — and the assertion below then demanded that the start
  // artist disappear, which it never can. A test hook must not be a style hook.
  const second = page.locator('ol li').nth(1);
  const secondName = await second.getByTestId('artist-name').innerText();
  await second.getByRole('button', { name: /reroute from here/i }).click();
  await second.getByRole('button', { name: /steer away/i }).click();

  // URL now carries the exclusion, and the bypassed artist is gone from the new path.
  await expect(page).toHaveURL(/dislike=/);
  await expect(page.getByText(secondName, { exact: true })).toHaveCount(0);
});
