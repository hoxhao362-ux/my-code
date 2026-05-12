import { defineStore } from 'pinia'
import { userApi, adminApi } from '@/utils/api'
import { usePlatformStore } from './platform'
import { useMessageStore } from './messages'

/**
 * 对齐后端的角色层级制度
 * 参考 backend/core/enums.py
 */
const ROLE_LEVELS = {
  'admin': 100,
  'editor': 90,
  'associate_editor': 80, // 替换原 deputy_editor
  'ea_ae': 70,
  'reviewer': 60,
  'author': 50,           // 移除原 writer
  'user': 10              // 移除原 normal
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: null,           // 初始为 null，由 fetchUserInfo 填充
    role: 'user'              // 默认设为基础角色
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    currentRole: (state) => state.role,
    roleLevel: (state) => ROLE_LEVELS[state.role] || 0,
    
    // 编辑部成员权限（管理、分配、决策）
    isEditorial: (state) =>
      ['admin', 'editor', 'associate_editor', 'ea_ae'].includes(state.role),
    
    // 纯审稿人权限
    isReviewer: (state) => state.role === 'reviewer',
    
    // 纯作者权限
    isAuthor: (state) => state.role === 'author',
  },
  
  actions: {
    /**
     * 普通用户登录
     */
    async login(loginForm) {
      try {
        const res = await userApi.login(loginForm)
        // 健壮的数据拆解逻辑
        const loginData = res.data?.data || res.data || res
        const token = loginData.token
        
        if (!token) throw new Error('未获取到有效鉴权凭证(Token)')
        
        this.token = token
        localStorage.setItem('token', token)
        await this.fetchUserInfo()
        return true
      } catch (error) {
        console.error('登录流程异常:', error)
        throw error
      }
    },

    /**
     * 管理员专用登录
     */
    async adminLogin(loginForm) {
      try {
        const res = await adminApi.adminLogin(loginForm)
        const loginData = res.data?.data || res.data || res
        const token = loginData.token
        
        if (!token) throw new Error('未获取到管理员鉴权凭证(Token)')
        
        this.token = token
        localStorage.setItem('token', token)
        await this.fetchUserInfo()
        return true
      } catch (error) {
        console.error('管理员登录流程异常:', error)
        throw error
      }
    },

    /**
     * 从后端同步最新的用户信息
     */
    async fetchUserInfo() {
      try {
        const res = await userApi.getCurrentUser()
        const userData = res.data?.data || res.data || res
        
        this.userInfo = userData
        this.role = userData.role || 'user'
        
        localStorage.setItem('userInfo', JSON.stringify(userData))
        localStorage.setItem('user_role', this.role)
      } catch (error) {
        console.error('获取用户信息失败，状态已重置:', error)
        this.logout()
      }
    },

    /**
     * 登出并清理本地所有认证状态
     */
    async logout() {
      try {
        if (this.token) {
          await userApi.logout()
        }
      } catch (error) {
        console.warn('后端注销接口调用失败，继续清理本地缓存')
      } finally {
        this.token = ''
        this.userInfo = null
        this.role = 'user'
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('user_role')
      }
    },

    /**
     * 刷新期刊数据
     */
    async refreshJournals() {
      try {
        const platformStore = usePlatformStore()
        await platformStore.fetchJournals()
      } catch (error) {
        console.warn('刷新期刊数据失败:', error)
      }
    },

    /**
     * 加载反馈消息
     */
    async loadFeedbackMessages() {
      try {
        const messagesStore = useMessageStore()
        await messagesStore.fetchMessages()
      } catch (error) {
        console.warn('加载反馈消息失败:', error)
      }
    },

    /**
     * 同步用户上下文
     * @param {string} source - 'main' 或 'submission'
     */
    syncUserContext(source) {
      if (source === 'main') {
        const savedUser = sessionStorage.getItem('readonly_user')
        if (savedUser && savedUser !== 'null' && savedUser !== 'undefined') {
          try {
            const parsedUser = JSON.parse(savedUser)
            this.userInfo = parsedUser
            this.role = parsedUser.role || 'user'
          } catch (e) {
            console.warn('解析只读用户数据失败:', e)
          }
        }
      } else if (source === 'submission') {
        const submissionUser = localStorage.getItem('submit_user')
        if (submissionUser) {
          try {
            const parsedUser = JSON.parse(submissionUser)
            this.userInfo = parsedUser
            this.role = parsedUser.role || 'user'
          } catch (e) {
            console.warn('解析提交用户数据失败:', e)
          }
        }
      }
    }
  }
})
