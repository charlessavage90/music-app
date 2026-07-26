import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  // Outside the OneDrive-synced tree: the default location fails with
  // EPERM on rmdir, and a manually-run regression gate that errors on its
  // default invocation is a gate people stop running (DEP-30, TR-17).
  outputDir: '../.playwright-results',
  use: { baseURL: 'http://localhost:5173' },
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
