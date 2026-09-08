import { expect, test } from '@playwright/test';

/**
 * The owner reported this on 2026-08-08: typing in the FIRST artist box opens
 * the matching-artist list over the SECOND box, and the second box's coloured
 * dot showed THROUGH the list instead of being covered by it.
 *
 * Cause: the list and the dot were both absolutely positioned at z-10, and the
 * two boxes are plain flex siblings with nothing between them creating a
 * stacking context. At equal z-index the tie breaks on document order, and the
 * second box's dot comes later in the document than the first box's list — so
 * the dot won.
 *
 * WHY THIS SAMPLES A PIXEL. The obvious instrument, elementFromPoint, is
 * useless here and silently so: the dot carries `pointer-events-none`, and
 * hit-testing skips such elements, so elementFromPoint can never return the
 * dot however it is painted. Written that way this test passed against the
 * BROKEN code. Reading the rendered pixel is the only check that observes what
 * the owner actually saw. The unit test in ArtistSearch.test.tsx covers the
 * ordering invariant; this covers the rendering.
 *
 * Needs the API on :8000, like every spec here.
 */

// src/index.css — the dot's green, and the dropdown's near-black surface.
const DOT_GREEN = [160, 217, 180];
const SURFACE = [24, 26, 31];

const distance = (a: number[], b: number[]) =>
  Math.sqrt(a.reduce((sum, v, i) => sum + (v - b[i]) ** 2, 0));

// The two fields have to be STACKED for one's dropdown to reach the other's
// dot, and since UXR-T3 they are stacked only below `sm` — the landing page
// puts them side by side at 640px and up (`grid gap-3.5 sm:grid-cols-2`). At
// the default viewport the dropdown now opens beside the second field instead
// of over it, so this spec's own precondition stopped holding and it failed
// there rather than on the stacking it exists to check. Pinning the width is
// what keeps it measuring the thing it was written for.
test.use({ viewport: { width: 390, height: 844 } });

test('the open dropdown covers the next field\'s dot', async ({ page }) => {
  await page.goto('/');

  await page.locator('input').first().fill('beat');

  // Wait on a RESULT, not on `ul`: the landing page also renders a
  // ready-made-journeys <ul> that is visible from the start, so waiting for
  // "a ul" passes instantly and measures the wrong element.
  await expect(page.getByText('Beatsteaks')).toBeVisible();

  const geometry = await page.evaluate(() => {
    const boxes = Array.from(document.querySelectorAll('input'));
    const dot = boxes[1].parentElement!.querySelector('span[aria-hidden]')!;
    // Scoped to the FIRST field's own wrapper, and deliberately not selected
    // on z-index — a selector naming the fix cannot witness the fix.
    const list = boxes[0].parentElement!.parentElement!.querySelector('ul')!;
    const d = dot.getBoundingClientRect();
    const l = list.getBoundingClientRect();
    return {
      dot: { x: d.left, y: d.top, width: d.width, height: d.height },
      // Precondition: the dot must actually lie under the open list, or this
      // test proves nothing about stacking.
      dotLiesUnderTheList:
        d.left + d.width / 2 > l.left &&
        d.left + d.width / 2 < l.right &&
        d.top + d.height / 2 > l.top &&
        d.top + d.height / 2 < l.bottom,
    };
  });

  expect(geometry.dotLiesUnderTheList).toBe(true);

  // Read what is actually painted where the dot is. Playwright hands back a
  // PNG buffer and node here has no decoder, so the browser decodes its own
  // screenshot through a canvas.
  const shot = (await page.screenshot({ clip: geometry.dot })).toString('base64');
  const pixel = await page.evaluate(async (b64) => {
    const img = new Image();
    img.src = `data:image/png;base64,${b64}`;
    await img.decode();
    const canvas = document.createElement('canvas');
    canvas.width = img.width;
    canvas.height = img.height;
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(img, 0, 0);
    const { data } = ctx.getImageData(
      Math.floor(img.width / 2),
      Math.floor(img.height / 2),
      1,
      1,
    );
    return [data[0], data[1], data[2]];
  }, shot);

  // The dot's own colour at its own centre means it painted over the list.
  expect(distance(pixel, DOT_GREEN)).toBeGreaterThan(distance(pixel, SURFACE));
});
