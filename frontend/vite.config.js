import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/static/wechat-pay-qr.png': { target: 'http://127.0.0.1:8080', changeOrigin: true },
      '/static/bgm': { target: 'http://127.0.0.1:8080', changeOrigin: true },
    },
  },
  build: {
    outDir: '../backend/static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/xlsx')) return 'vendor-xlsx'
          if (id.includes('node_modules/html2canvas')) return 'vendor-html2canvas'
          if (id.includes('node_modules/wordcloud')) return 'vendor-wordcloud'
          if (id.includes('node_modules/vue') || id.includes('node_modules/vue-router')) return 'vendor-vue'
        },
      },
    },
  },
})
