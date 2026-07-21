/// <reference types="vitest/config" />
import { defineConfig } from 'vite';
import { configDefaults } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
import path from 'node:path';
import os from 'node:os';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Keep Vite's dependency cache OUT of the project tree. This repo lives under
  // OneDrive, which locks files mid-sync and makes Vite fail to clear its cache
  // ("EPERM: operation not permitted, rmdir node_modules/.vite/deps"). A temp
  // dir is outside sync, so the dev server starts reliably whether or not
  // OneDrive syncing is enabled.
  cacheDir: path.join(os.tmpdir(), 'artistpath-vite-cache'),
  resolve: {
    alias: { '@': path.resolve(__dirname, './src') },
  },
  server: {
    proxy: {
      '/api': {
        target: process.env.VITE_API_PROXY ?? 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
    css: true,
    // Playwright specs live in e2e/ and run via `npm run test:e2e`, not Vitest.
    exclude: [...configDefaults.exclude, 'e2e/**'],
  },
});
