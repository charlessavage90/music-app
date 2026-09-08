import { expect, test } from '@playwright/test';

// Requires the API running on :8000, and the dev server (started by webServer).
// (The 5k dev fixture this once named is retired; :8000 boots the adopted graph.)
test('search, path, bypass produces a new path without the bypassed artist', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('Start with').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('End with').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /build the path/i }).click();

  // Wait for the NAVIGATION first, then for the list.
  //
  // The same defect has now bitten this line twice, from two different
  // directions, and the lesson is the same both times: waiting on anything the
  // page we are LEAVING also has is not a wait. First it was the artist's name
  // (the landing page names Miles Davis in a sample journey). Then UXR-T3 gave
  // the landing page a teaser that is itself an `<ol>` of names, so waiting on
  // `ol li` also passed instantly against the landing page — and `allInnerTexts`
  // then ran mid-navigation and read an empty list, which is a `length` of 0
  // rather than a timeout, so it surfaced as a bewildering assertion failure.
  // And the URL is not enough on its own: it changes before React swaps the
  // page, so `ol li` still matched the landing teaser for an instant after
  // `waitForURL` resolved. `artist-name` is rendered by ArtistCard and by
  // nothing else in the app, so it belongs to the journey and cannot be
  // satisfied by the page we are leaving or by the loading skeleton.
  await page.waitForURL(/\/path\//);
  await expect(page.getByTestId('artist-name').first()).toBeVisible();
  const before = await page.locator('ol li').allInnerTexts();
  expect(before.length).toBeGreaterThan(1);
  expect(before[0]).toContain('Miles Davis');

  // Bypass the second artist. Two presses since UXR-T7 (owner decision 2,
  // 2026-09-08): open that artist's detail, then dig from inside it. The
  // control is interior-only, so this must be a middle card — an endpoint's
  // detail carries no Dig deeper at all.
  // UI-13: located by data-testid, not `.font-semibold`. The endpoint eyebrow
  // ("Starting artist") is also font-semibold, so .nth(1) silently became the
  // FIRST card's name — and the assertion below then demanded that the start
  // artist disappear, which it never can. A test hook must not be a style hook.
  const second = page.locator('ol li').nth(1);
  const secondName = await second.getByTestId('artist-name').innerText();
  await second.getByRole('button', { name: /^About / }).click();
  // One detail component, two containers (UXR-D3) — the dock at lg and up, the
  // sheet below it. BOTH are in the DOM at every width and CSS hides one, so
  // this filters on what is actually shown rather than assuming a viewport.
  // This spec sets none, so it runs at Playwright's 1280 default and sees the
  // dock; `e2e/responsive.spec.ts` pins the sheet at 390.
  const digDeeper = page.getByRole('button', { name: /dig deeper/i }).filter({ visible: true });
  await expect(digDeeper).toHaveCount(1);
  await digDeeper.click();

  // URL now carries the exclusion, and the bypassed artist is gone from the new
  // path — scoped to the journey's own cards (`artist-name`), not the whole
  // page: LUX-2b legitimately names the bypassed artist again, in the "Artists
  // you skipped" panel, so a page-wide text search would now find it there.
  await expect(page).toHaveURL(/known=/);
  await expect(page.getByTestId('artist-name').filter({ hasText: secondName })).toHaveCount(0);

  // LUX-2b: the bypassed artist is not gone without trace — the panel names
  // them. Only a real browser proves the data actually reaches the rendered
  // page through the URL round trip and the path response together.
  await expect(page.getByText('Artists you skipped')).toBeVisible();
  await expect(page.getByText(secondName)).toBeVisible();
});
