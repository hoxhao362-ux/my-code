import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  // Server Config
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  // Build Config
  build: {
    target: 'esnext',
    assetsDir: 'assets',
    cssCodeSplit: true, // Enable CSS code splitting
    sourcemap: false, // Disable sourcemaps for production
    minify: 'esbuild', // Use esbuild for minification (faster)
    chunkSizeWarningLimit: 1000, // Increase warning limit to 1000kb
    rollupOptions: {
      output: {
        // Manual Chunks Strategy
        manualChunks(id) {
          if (id.includes('node_modules')) {
            // Split Vue core libs
            if (id.includes('vue') || id.includes('pinia') || id.includes('vue-router')) {
              return 'vue-core'
            }
            // Split other large libs if any
            // if (id.includes('lodash')) return 'lodash'
            
            return 'vendor' // Other dependencies
          }
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  }
})
