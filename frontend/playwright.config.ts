import { defineConfig } from '@playwright/test';
import os from 'node:os';
import path from 'node:path';

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
  use: { baseURL: 'http://localhost:5173' },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
