/**
 * Token 管理工具
 * 处理 Token 的持久化与读取
 */

const TOKEN_KEY = 'access_token'

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
