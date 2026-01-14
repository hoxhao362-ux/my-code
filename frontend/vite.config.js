import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    // 配置API代理，将/api请求转发到后端服务器
    proxy: {
      '/api': {
        target: 'http://localhost:8000', // 后端服务器地址
        changeOrigin: true, // 允许跨域
        secure: false // 不验证SSL证书
      }
    }
  }
})
