import { defineConfig } from '@playwright/test';
import os from 'node:os';
import path from 'node:path';

// `reuseExistingServer` means ANY dev server already on the port is the one under
// test — including one from a different worktree, serving different source. So the
// port is overridable: `E2E_PORT=5183 VITE_API_PROXY=http://localhost:8010 npm run
// test:e2e` runs this tree's code against a second API, beside a dev loop that is
// already using 5173 and :8000 (issue #213, where both were taken by another tree).
const port = Number(process.env.E2E_PORT ?? 5173);
const baseURL = `http://localhost:${port}`;

export default defineConfig({
  testDir: './e2e',
  // Outside the OneDrive-synced tree: the default location fails with
  // EPERM on rmdir, and a manually-run regression gate that errors on its
  // default invocation is a gate people stop running (DEP-30, TR-17).
  //
  // The repo ROOT is under OneDrive too, so '../.playwright-results' — the
  // first version of this fix — only moved the problem out of frontend/ and
  // still EPERMs whenever a previous run left artifacts behind. Observed on
  // two consecutive runs, 2026-07-26 (TKD-3). The OS temp dir is genuinely
  // outside sync, which is the same reasoning, and the same remedy, as
  // vite.config.ts's cacheDir.
  outputDir: path.join(os.tmpdir(), 'artistpath-playwright-results'),
  use: { baseURL },
  webServer: {
    command: `npm run dev -- --port ${port} --strictPort`,
    url: baseURL,
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
