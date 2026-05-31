import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { VitePWA } from '@vite-pwa/sveltekit';

export default defineConfig({
  plugins: [
    svelte(),
    VitePWA({
      registerType: 'prompt',
      strategies: 'injectManifest',
      includeAssets: ['favicon.svg', 'favicon.ico', 'robots.txt', 'apple-touch-icon.png'],
      manifest: {
        name: 'Hyphen',
        short_name: 'Hyphen',
        description: 'A haiku-based social platform',
        theme_color: '#0F0E0D',
        background_color: '#F7F5F0',
        display: 'standalone',
        scope: '/',
        start_url: '/',
        icons: [
          {
            src: '/favicon.svg',
            sizes: '192x192',
            type: 'image/svg+xml'
          }
        ]
      },
      workbox: {
        globPatterns: ['client/**/*.{js,css,html,svg,png,ico,webp,woff,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^http:\/\/localhost:8000\/api\/feed/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'hyphen-feed-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60
              }
            }
          }
        ]
      }
    })
  ],
  server: {
    fs: {
      allow: ['..']
    }
  }
});
