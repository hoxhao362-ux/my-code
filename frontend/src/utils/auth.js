/**
 * Token 管理工具
 * 处理 Token 的持久化与读取
 * 与 http.js 中的 localStorage.getItem('token') 保持一致
 */
import { clearAllAuthData } from './clearLocalStorage'

const TOKEN_KEY = 'token'

/**
 * 设置 Token
 * @param {string} token - JWT Token
 */
export const setToken = (token) => {
  localStorage.setItem(TOKEN_KEY, token)
}

/**
 * 获取 Token
 * @returns {string|null}
 */
export const getToken = () => {
  return localStorage.getItem(TOKEN_KEY)
}

/**
 * 移除 Token
 */
export const removeToken = () => {
  localStorage.removeItem(TOKEN_KEY)
}

/**
 * 登出处理 - 清除 Token 和所有用户信息缓存
 */
export const logout = () => {
  // 修复：调用统一的清理工具，彻底消除该工具未被引用的问题
  clearAllAuthData()
}
