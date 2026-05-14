import axios from 'axios'
import { useToastStore } from '../stores/toast'

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
    
    // 容错解析：FastAPI 直接返回数据（无 code 字段）
    if (!res || typeof res !== 'object') {
      return res
    }
    
    // 标准响应格式：{ code: 200, data: {...}, message: "..." }
    if (res.code !== undefined) {
      if (res.code === 200) {
        return res.data !== undefined ? res.data : res
      } else {
        return Promise.reject(new Error(res.message || res.detail || '请求失败'))
      }
    }
    
    // FastAPI 直接返回数据（无 code 字段）
    if (res.detail) {
      // 可能是错误响应 { detail: "..." }
      return Promise.reject(new Error(res.detail))
    }
    
    // 直接返回完整数据
    return res
  },
  error => {
    if (error.response) {
      const status = error.response.status
      const data = error.response.data || {}
      const detail = data.detail || (Array.isArray(data.detail) ? data.detail.map(d => d.msg).join(', ') : '') || data.message || ''
      
      switch (status) {
        case 401:
          const toastStore = useToastStore()
          toastStore.add({
            message: 'Session Expired: Please login again to continue.',
            type: 'warning'
          })
          
          localStorage.removeItem('token')
          localStorage.removeItem('userInfo')
          localStorage.removeItem('user_role')
          localStorage.removeItem('submit_user')
          
          setTimeout(() => {
            window.location.href = '/login'
          }, 1000)
          break
        case 403:
          console.error('权限不足:', detail)
          break
        case 422:
          // Pydantic 校验错误
          console.error('参数校验错误:', detail)
          break
        case 429:
          console.error('请求太频繁，被限流:', detail)
          break
        case 500:
          console.error('服务器内部错误:', detail)
          break
        default:
          console.error('后端接口报错:', detail || '未知错误')
      }
    } else if (error.request) {
      console.error('网络错误：无法连接到服务器')
    } else {
      console.error('请求配置错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default http
