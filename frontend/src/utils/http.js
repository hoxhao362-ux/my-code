import axios from 'axios'

// 创建 axios 实例
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    // 从 localStorage 获取 token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    // 兼容后端返回的 ApiResponse { code, message, data, meta }
    if (response.data && response.data.code !== undefined) {
      if (response.data.code === 200) {
        // 如果后端有 meta 分页信息，可以将其附加到 data 上或者按需处理
        // 为了兼容前端已有代码，默认返回 data
        return response.data.data !== undefined ? response.data.data : response.data
      } else {
        return Promise.reject(new Error(response.data.message || '请求失败'))
      }
    }
    return response.data
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，清除 token 并跳转登录页
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          // 权限不足
          console.error('Permission denied')
          break
        case 500:
          // 服务器错误
          console.error('Server error')
          break
        default:
          console.error('Network error')
      }
    }
    return Promise.reject(error)
  }
)

export default http
