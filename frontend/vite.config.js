import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined,
        entryFileNames: '[name].[hash].js',
        chunkFileNames: '[name].[hash].js',
        assetFileNames: '[name].[hash].[ext]'
      }
    }
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://119.29.37.117:8000',
        changeOrigin: true,
      },
      '/token': {
        target: 'http://119.29.37.117:8000',
        changeOrigin: true,
      },
      '/register': {
        target: 'http://119.29.37.117:8000',
        changeOrigin: true,
      },
      '/projects': {
        target: 'http://119.29.37.117:8000',
        changeOrigin: true,
      }
    }
  }
})
