import { defineConfig } from 'vite'

// Simple Vite dev server proxy so frontend fetch('/api/...') is forwarded
// to the Flask backend running on localhost:5000
export default defineConfig({
  base: '/PokeTools/', // Pour GitHub Pages
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
