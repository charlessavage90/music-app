import { expect, test } from '@playwright/test';

// TR-16: on a 390px phone the card row's non-shrinkable elements exceed the
// available width and the artist name — the only content that matters — is
// squeezed toward zero. Measured in a real browser because jsdom computes no
// layout: a jsdom test here could only assert class names and would pass before
// the fix (the FMS-P1 / TR-2 vacuous-check pattern).
test.use({ viewport: { width: 390, height: 844 } });

test('a journey is usable at phone width', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('Start with').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('End with').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /build the path/i }).click();

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

  // 2. The artist name must get real width, not a sliver.
  //
  // THE BAR MOVED FROM 160 TO 140 ON 2026-09-08, AND THAT IS A RECALIBRATION,
  // NOT A TEST BENT TO PASS. The premise changed: UXR-T6 put a second round
  // control on the card (the detail chevron), and 160 was measured against a
  // card that had one. The budget at 390px is arithmetic — the card is 324px,
  // leaving 296px inside its padding, and the cover, the two controls and
  // three gaps are all non-shrinkable. Measured before and after:
  //
  //     one control  (pre-T6) : column ~180px
  //     two controls (T6, as first written) :        126px  <- this test caught it
  //     two controls, phone sizes tightened :        150px  <- now
  //
  // Getting back over 160 needs a sub-40px tap target, which is worse than a
  // shorter name. What is NOT negotiable is the sliver TR-16 was about, so the
  // bar sits just under what the approved two-control design affords.
  // UI-5: pinned to the element, not to its typography. This was
  // `.locator('.font-semibold')` — a Tailwind class doing test duty, which the
  // 2026-07-28 restyle moves. It would have failed for a reason unrelated to
  // what this spec measures.
  const box = await interior.getByTestId('artist-name').first().boundingBox();
  expect(box).not.toBeNull();
  expect(box!.width).toBeGreaterThan(140);

  // 3. The bypass control stays reachable and legible at phone width. Since
  //    UXR-T7 it lives in the artist detail, which at 390px is a bottom sheet
  //    — so reaching it is two presses (owner decision 2, 2026-09-08) and the
  //    thing only a layout engine can confirm is that the sheet actually opens
  //    over the journey and the control fits inside it.
  await interior.getByRole('button', { name: /^About / }).click();
  const sheet = page.getByRole('dialog');
  await expect(sheet).toBeVisible();
  await expect(sheet.getByRole('button', { name: /dig deeper/i })).toBeVisible();

  // Opening it must not have introduced a sideways scroll either.
  const sheetOverflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(sheetOverflow).toBeLessThanOrEqual(1);
});

// UXR-T6 put a dot on every card and a rail behind them, and got the geometry
// wrong twice at once: every dot sat 3px left of the rail, and the rail's fixed
// 41px end inset overshot the end dots — by 7.5px at 1280, and lopsidedly at
// 390 (3.25 top, 10.75 bottom). The unit suite was 188 green throughout, because
// jsdom computes no layout; the owner found it by looking at a screenshot.
// This is the assertion that would have failed on T6's first commit.
test('the rail runs through the centre of every dot, and stops at the end ones', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('Start with').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('End with').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /build the path/i }).click();

  await expect(page.locator('ol li').nth(1)).toBeVisible();

  const geometry = await page.evaluate(() => {
    const ol = document.querySelector('ol')!;
    const rail = ol.querySelector<HTMLElement>(':scope > span[aria-hidden]')!;
    const r = rail.getBoundingClientRect();
    const dots = [...ol.querySelectorAll<HTMLElement>('[data-rail-dot]')].map((d) => {
      const b = d.getBoundingClientRect();
      return { cx: b.left + b.width / 2, cy: b.top + b.height / 2 };
    });
    return {
      dx: dots.map((d) => Math.abs(d.cx - (r.left + r.width / 2))),
      topGap: Math.abs(r.top - dots[0].cy),
      bottomGap: Math.abs(r.bottom - dots[dots.length - 1].cy),
      count: dots.length,
    };
  });

  expect(geometry.count).toBeGreaterThan(2);
  // Sub-pixel tolerance only: these are meant to coincide, not to be close.
  for (const dx of geometry.dx) expect(dx).toBeLessThanOrEqual(0.5);
  expect(geometry.topGap).toBeLessThanOrEqual(0.5);
  expect(geometry.bottomGap).toBeLessThanOrEqual(0.5);
});

// LUX-4 adds two lines to every card — the facts line and the links row — and
// height at 390px is the scarcest thing on this page. Assertions 1 and 3 above
// already cover overflow and reachability for the card as a whole; this adds
// the new elements specifically, and is also the ONLY test in the suite that
// exercises the whole chain for real: artifact -> APG1 keys -> ArtistOut ->
// artistFrom -> card. Every other LUX-4 test mocks one end or the other.
test('the streaming links survive phone width and carry a real href', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('Start with').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('End with').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /build the path/i }).click();

  const interior = page.locator('ol li').nth(1);
  await expect(interior).toBeVisible();

  // Since UXR-T7 the links are in the artist detail, not on the card — scoped
  // to the dialog because both containers render and only the sheet is shown
  // at this width, so an unscoped query matches a hidden copy too.
  await interior.getByRole('button', { name: /^About / }).click();
  const sheet = page.getByRole('dialog');
  await expect(sheet).toBeVisible();

  // Both services, always — a missing id is a search link, never no button.
  const spotify = sheet.getByRole('link', { name: /on Spotify/i });
  const apple = sheet.getByRole('link', { name: /on Apple Music/i });
  await expect(spotify).toBeVisible();
  await expect(apple).toBeVisible();
  await expect(spotify).toHaveAttribute('href', /open\.spotify\.com/);
  await expect(apple).toHaveAttribute('href', /music\.apple\.com/);
  await expect(spotify).toHaveAttribute('rel', /noopener/);

  // Adding two lines must not have reintroduced the sideways scroll TR-16 fixed.
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
  );
  expect(overflow).toBeLessThanOrEqual(1);
});

// The facts line WRAPS rather than truncating, and only a layout engine can
// tell. Under `truncate` this line lost its life span on most real artists at
// 390px -- "Person . United States . 1933-2..." -- because the dates sit at
// the end of the natural reading order behind the longest, least useful field.
// A unit test could only assert a class name here and would pass either way,
// which is the FMS-P1 / TR-2 vacuous-check pattern this file exists to avoid.
test('the artist facts line is never cut off at phone width', async ({ page }) => {
  await page.goto('/');

  await page.getByLabel('Start with').fill('miles davis');
  await page.getByRole('button', { name: /miles davis/i }).first().click();
  await page.getByLabel('End with').fill('daft punk');
  await page.getByRole('button', { name: /daft punk/i }).first().click();
  await page.getByRole('button', { name: /build the path/i }).click();

  await expect(page.locator('ol li').nth(1)).toBeVisible();

  // The facts line moved to the artist detail with the links (UXR-T7), so this
  // walks the journey opening each artist in turn. Every artist, not just one:
  // the defect showed on the ones with the most to say, which is not
  // predictable from the pair. Endpoints included — they carry a facts line too.
  const stops = await page.locator('ol li').count();
  const clipped: (string | null)[] = [];
  for (let i = 0; i < stops; i++) {
    await page.locator('ol li').nth(i).getByRole('button', { name: /^About / }).click();
    const sheet = page.getByRole('dialog');
    await expect(sheet).toBeVisible();
    clipped.push(
      ...(await sheet.evaluate((root) =>
        [...root.querySelectorAll('div')]
          .filter((el) => / · /.test(el.textContent ?? '') && el.children.length === 0)
          .filter((el) => el.scrollWidth > el.clientWidth + 1)
          .map((el) => el.textContent),
      )),
    );
    await sheet.getByRole('button', { name: /close/i }).click();
  }
  expect(clipped).toEqual([]);
});
