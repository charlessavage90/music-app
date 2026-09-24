import { expect, test, type APIRequestContext } from '@playwright/test';
import { SAMPLE_JOURNEYS, TEASER } from '../src/lib/sampleJourneys';

// UXR-T10 / issue #213. The landing page's sample chips and its teaser carry a
// stop count and a list of names MEASURED on the served graph. A rebuild can
// move either, and until this spec existed nothing noticed: the chip lied and
// the suite stayed green. This is the re-check rule as a test — after any
// artifact adoption it fails if a chip or the teaser disagrees with the router.
//
// The count is INCLUSIVE (issue #202, `journeyLength`): every artist on the
// journey, both chosen ones included — so it is compared with the router's
// `artists.length` as-is, never `- 2`.
//
// Requests go through the dev server's `/api` proxy (the same route the app
// takes), so they hit whichever API the proxy points at — :8000 by default,
// `VITE_API_PROXY` otherwise — rather than a hard-coded port that could be a
// different graph than the page under test is using.
//
// If this fails after an adoption: the served graph moved. Update the
// constants in src/lib/sampleJourneys.ts to what the router returned (the
// failure message names it) and say so in the PR — never weaken the test.

async function routerJourney(request: APIRequestContext, from: string, to: string) {
  const r = await request.post('/api/path', { data: { sources: [from, to], exclude: [] } });
  expect(r.ok(), `POST /api/path ${from} -> ${to}: HTTP ${r.status()}`).toBeTruthy();
  const body = (await r.json()) as { artists: { mbid: string; name: string }[] };
  return body.artists;
}

test('every sample chip states the stop count the live router gives', async ({ page, request }) => {
  await page.goto('/');
  for (const j of SAMPLE_JOURNEYS) {
    const artists = await routerJourney(request, j.from, j.to);
    const label = `${j.fromName} -> ${j.toName}: router returned ${artists.length} stops (${artists
      .map((a) => a.name)
      .join(' / ')})`;
    // The endpoints are the ones the chip names — a rebuild that re-assigns an
    // MBID would otherwise pass here with a count for some other artist.
    expect(artists[0].mbid, label).toBe(j.from);
    expect(artists[artists.length - 1].mbid, label).toBe(j.to);
    expect(artists.length, label).toBe(j.stops);
    // And the rendered chip says the router's number, not merely the module's:
    // this is what a visitor reads.
    await expect(
      page.getByRole('link', { name: `${j.fromName} to ${j.toName}, ${artists.length} stops` }),
      label,
    ).toBeVisible();
  }
});

test('the teaser lists exactly the journey the live router builds', async ({ page, request }) => {
  const artists = await routerJourney(request, TEASER.from, TEASER.to);
  expect(artists.map((a) => a.name)).toEqual([...TEASER.names]);

  // The rendered teaser (desktop only — it is hidden below lg, and this spec
  // runs at Playwright's 1280 default) shows those names in that order.
  await page.goto('/');
  const teaser = page.locator('main ol');
  await expect(teaser).toHaveCount(1);
  expect(await teaser.locator('li').allInnerTexts()).toEqual(artists.map((a) => a.name));
});
