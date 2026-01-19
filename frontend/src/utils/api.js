import { useUserStore } from '../stores/user'

// API基础配置
const API_BASE_URL = '/api'

// 创建请求函数
const request = async (url, options = {}) => {
  const userStore = useUserStore()
  const token = userStore.user?.token
  
  const defaultHeaders = {
    'Content-Type': 'application/json'
  }
  
  if (token) {
    defaultHeaders['Authorization'] = `Bearer ${token}`
  }
  
  const config = {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers
    }
  }
  
  try {
    const response = await fetch(`${API_BASE_URL}${url}`, config)
    
    // 处理非200状态码
    if (!response.ok) {
      console.error('API请求失败:', response.status, response.statusText)
      return null // API请求失败时返回null，而不是抛出错误
    }
    
    // 处理204 No Content
    if (response.status === 204) {
      return null
    }
    
    return await response.json()
  } catch (error) {
    console.error('网络请求错误:', error)
    return null // 网络错误时返回null，而不是抛出错误
  }
}

// 用户相关API
export const userApi = {
  // 用户注册
  register: (userData) => {
    return request('/user/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
  },
  
  // 用户登录
  login: (credentials) => {
    return request('/user/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
  },
  
  // 获取当前用户信息
  getCurrentUser: () => {
    return request('/user/me')
  },
  
  // 用户登出
  logout: () => {
    return request('/user/logout', {
      method: 'POST'
    })
  }
}

// 文献相关API
export const journalApi = {
  // 上传文献
  upload: (formData) => {
    return request('/journal/upload', {
      method: 'POST',
      body: formData,
      headers: {
        // 不需要设置Content-Type，浏览器会自动设置
      }
    })
  },
  
  // 获取我的文献列表
  getMyJournals: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/journal/my?${queryString}`)
  },
  
  // 获取文献详情
  getJournalDetail: (jid) => {
    return request(`/journal/detail/${jid}`)
  },
  
  // 删除文献
  deleteJournal: (jid) => {
    return request(`/journal/${jid}`, {
      method: 'DELETE'
    })
  },
  
  // 获取公开文献列表
  getPublicJournals: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/journal/public?${queryString}`)
  }
}

// 审稿相关API
export const reviewApi = {
  // 获取待审核文献列表
  getPendingJournals: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/review/pending?${queryString}`)
  },
  
  // 审核文献
  reviewJournal: (jid, reviewData) => {
    return request(`/review/review/${jid}`, {
      method: 'POST',
      body: JSON.stringify(reviewData)
    })
  },
  
  // 获取审核历史记录
  getReviewHistory: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/review/history?${queryString}`)
  },
  
  // 获取审核统计信息
  getReviewStatistics: () => {
    return request('/review/statistics')
  },
  
  // 获取被拒绝的文献列表
  getRejectedJournals: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/review/rejected?${queryString}`)
  }
}

// 管理员相关API
export const adminApi = {
  // 获取用户列表
  getUsers: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/admin/users?${queryString}`)
  },
  
  // 修改用户角色
  updateUserRole: (uid, role) => {
    return request(`/admin/users/${uid}/role`, {
      method: 'PUT',
      body: JSON.stringify({ role })
    })
  },
  
  // 删除用户
  deleteUser: (uid) => {
    return request(`/admin/users/${uid}`, {
      method: 'DELETE'
    })
  },
  
  // 获取所有文献列表
  getAllJournals: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/admin/journals/all?${queryString}`)
  },
  
  // 删除文献
  deleteJournal: (jid) => {
    return request(`/admin/journals/${jid}`, {
      method: 'DELETE'
    })
  },
  
  // 获取所有审核记录
  getAllReviewRecords: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/admin/review-records?${queryString}`)
  },
  
  // 获取系统统计信息
  getSystemStatistics: () => {
    return request('/admin/statistics')
  },
  
  // 获取已删除文献列表
  getDeletedJournals: (params = {}) => {
    const queryString = new URLSearchParams(params).toString()
    return request(`/admin/journals/deleted?${queryString}`)
  },
  
  // 彻底删除文献
  permanentlyDeleteJournal: (jid) => {
    return request(`/admin/journals/deleted/${jid}`, {
      method: 'DELETE'
    })
  }
}
