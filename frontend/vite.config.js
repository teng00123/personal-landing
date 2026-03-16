import { defineConfig, splitVendorChunkPlugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  plugins: [
    vue(),
    splitVendorChunkPlugin(),
    AutoImport({ resolvers: [ElementPlusResolver()] }),
    Components({ resolvers: [ElementPlusResolver()] }),
    // PWA / Service Worker
    VitePWA({
      registerType: 'autoUpdate',
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        runtimeCaching: [
          {
            urlPattern: /^\/api\/v1\/articles/,
            handler: 'StaleWhileRevalidate',
            options: {
              cacheName: 'api-articles-cache',
              expiration: { maxEntries: 50, maxAgeSeconds: 60 * 5 }, // 5分钟
            },
          },
          {
            urlPattern: /^\/api\/v1\/profile/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'api-profile-cache',
              expiration: { maxEntries: 10, maxAgeSeconds: 60 * 60 }, // 1小时
            },
          },
          {
            urlPattern: /\/uploads\/.*/,
            handler: 'CacheFirst',
            options: {
              cacheName: 'uploads-cache',
              expiration: { maxEntries: 100, maxAgeSeconds: 60 * 60 * 24 * 7 }, // 7天
            },
          },
        ],
      },
      manifest: {
        name: 'Personal Landing',
        short_name: 'Portfolio',
        theme_color: '#409EFF',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          { src: '/favicon.ico', sizes: '64x64', type: 'image/x-icon' },
        ],
      },
    }),
  ],

  resolve: {
    alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) },
  },

  build: {
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor-vue':    ['vue', 'vue-router', 'pinia'],
          'vendor-ui':     ['element-plus'],
          'vendor-i18n':   ['vue-i18n'],
          'vendor-marked': ['marked', 'highlight.js'],
        },
      },
    },
    // 启用 CSS 代码分割
    cssCodeSplit: true,
    // chunk 大小警告阈值
    chunkSizeWarningLimit: 1000,
    // 生产环境移除 console
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true,
      },
    },
  },

  server: {
    host: true,
    port: 5173,
    proxy: {
      '/api':     { target: 'http://localhost:8000', changeOrigin: true },
      '/uploads': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})
