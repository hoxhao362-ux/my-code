import { defineStore } from 'pinia'
import { authApi, userApi } from '@/utils/api'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
    role: localStorage.getItem('user_role') || ''
  }),
  
  getters: {
    isLoggedIn: (state) => !!state.token,
    currentRole: (state) => state.role
  },
  
  actions: {
    async login(loginForm) {
      try {
        const res = await authApi.login(loginForm)
        const token = res.token || res.access_token
        this.token = token
        localStorage.setItem('token', token)
        await this.fetchUserInfo()
        return true
      } catch (error) {
        console.error('登录失败:', error)
        throw error
      }
    },

    async fetchUserInfo() {
      try {
        const userData = await userApi.getCurrentUser()
        this.userInfo = userData
        this.role = userData.role || 'author'
        localStorage.setItem('userInfo', JSON.stringify(userData))
        localStorage.setItem('user_role', this.role)
      } catch (error) {
        console.error('获取用户信息失败，可能 Token 已过期:', error)
        this.logout()
      }
    },

    async logout() {
      try {
        await authApi.logout()
      } catch (error) {
        console.warn('后端登出接口异常，但前端继续清除本地状态')
      } finally {
        this.token = ''
        this.userInfo = null
        this.role = ''
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        localStorage.removeItem('user_role')
      }
    }
  }
})
