import axios from 'axios'

// 创建 axios 实例
const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 15000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
http.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

// 响应拦截器
http.interceptors.response.use(
  response => {
    const res = response.data
    if (res && res.code !== undefined) {
      if (res.code === 200) {
        return res.data !== undefined ? res.data : res
      } else {
        return Promise.reject(new Error(res.message || '请求失败'))
      }
    }
    return res
  },
  error => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          localStorage.removeItem('token')
          window.location.href = '/login'
          break
        case 403:
          console.error('权限不足:', error.response.data.detail)
          break
        case 429:
          console.error('请求太频繁，被限流')
          break
        default:
          console.error('后端接口报错:', error.response.data.detail || '未知错误')
      }
    }
    return Promise.reject(error)
  }
)

export default http
