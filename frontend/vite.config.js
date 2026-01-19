import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
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
        },
        chunkFileNames: 'assets/[name]-[hash].js',
        entryFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  },
  // 移除了esbuild的charset配置，因为esbuild默认就是utf-8
})
