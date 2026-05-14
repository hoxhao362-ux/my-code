/**
 * 统一的本地缓存清理工具
 * 修复：更新为系统实际使用的鉴权 key，并导出供其他组件使用
 */
export const clearAllAuthData = () => {
  const keysToRemove = [
    'token',
    'userInfo',
    'user_role',
    'submit_user'
  ]
  
  keysToRemove.forEach(key => {
    localStorage.removeItem(key)
  })
  
  // 注意：不再盲目清除 'adminRememberedUsername' 等登录页记住密码的偏好设置
}