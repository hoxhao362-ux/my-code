import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { splitVendorChunkPlugin } from 'vite'

// https://vite.dev/config/
export default defineConfig({
<<<<<<< HEAD
  plugins: [vue()],
  // 配置服务器
  server: {
    // 配置API代理，将/api请求转发到后端服务器
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 后端服务器地址
        changeOrigin: true, // 允许跨域
        secure: false // 不验证SSL证书
      }
    }
  },
  // 配置构建输出，确保正确的内容类型
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia']
=======
  plugins: [vue(), splitVendorChunkPlugin()],
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
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
<<<<<<< HEAD
  },
  // 移除了esbuild的charset配置，因为esbuild默认就是utf-8
=======
  }
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
})
