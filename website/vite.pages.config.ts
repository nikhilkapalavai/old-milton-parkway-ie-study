import { fileURLToPath } from 'node:url';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/postcss';
import { defineConfig } from 'vite';

// The simulation and interface run entirely in the browser. GitHub Pages
// needs static assets rather than the original Sites/Cloudflare server build.
export default defineConfig({
  base: '/old-milton-parkway-ie-study/',
  plugins: [react()],
  resolve: {
    alias: { '@': fileURLToPath(new URL('.', import.meta.url)) },
  },
  css: { postcss: { plugins: [tailwindcss()] } },
  build: { outDir: 'dist/pages' },
});
