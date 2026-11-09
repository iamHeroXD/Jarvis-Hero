import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },

  // Dev server for Tauri
  server: {
    port: 1420,
    strictPort: true,
    host: '127.0.0.1',
    watch: {
      ignored: ['**/src-tauri/**'],
    },
  },

  // Build output
  build: {
    outDir: 'dist',
    sourcemap: false,
    target: ['es2021', 'chrome110', 'safari13'],
    minify: !process.env.TAURI_DEBUG ? 'esbuild' : false,
  },

  // Vite clears the screen by default
  clearScreen: false,

  // Environment
  envPrefix: ['VITE_', 'TAURI_'],
})
