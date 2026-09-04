import { expect, test } from '@playwright/test';

// TR-16: on a 390px phone the card row's non-shrinkable elements exceed the
// available width and the artist name — the only content that matters — is
// squeezed toward zero. Measured in a real browser because jsdom computes no
// layout: a jsdom test here could only assert class names and would pass before
// the fix (the FMS-P1 / TR-2 vacuous-check pattern).
test.use({ viewport: { width: 390, height: 844 } });

test('a journey is usable at phone width', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('From').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('To').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /discover a path/i }).click();

  await expect(page.locator('ol li').first()).toBeVisible();

  // EVERY assertion below is on an INTERIOR card, and that is the whole test.
  // The first and last cards are the journey's endpoints and carry no bypass
  // buttons — which are exactly the non-shrinkable elements that cause the
  // squeeze. Measuring `.first()` measures the one card that was never broken:
  // it passed against unmodified source, which is the FMS-P1 / TR-2 pattern
  // this spec exists to avoid, caught on its own RED run (TKD-2).
  const interior = page.locator('ol li').nth(1);
  await expect(interior).toBeVisible();

  // 1. The page must not scroll sideways.
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);

  // 2. The artist name must get real width, not a sliver. 160px is well under
  //    what the fixed layout gives it and well over what the broken one does.
  // UI-5: pinned to the element, not to its typography. This was
  // `.locator('.font-semibold')` — a Tailwind class doing test duty, which the
  // 2026-07-28 restyle moves. It would have failed for a reason unrelated to
  // what this spec measures.
  const box = await interior.getByTestId('artist-name').first().boundingBox();
  expect(box).not.toBeNull();
  expect(box!.width).toBeGreaterThan(160);

  // 3. The bypass control stays reachable and legible at phone width. It is no
  //    longer behind a disclosure (LUX-1), so there is no tray to open — but it
  //    now carries two lines of text, which is the new thing only a layout
  //    engine can confirm fits at 390px.
  const bypass = interior.getByRole('button', { name: /dig deeper/i });
  await expect(bypass).toBeVisible();
});
