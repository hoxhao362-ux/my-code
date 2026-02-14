// 密码加密工具函数

/**
 * 加密密码
 * @param {string} password - 原始密码
 * @returns {string} 加密后的密码
 */
export function encryptPassword(password) {
  // 使用 Base64 加密（简单实现，实际项目中应使用更安全的加密算法）
  return btoa(password)
}

/**
 * 解密密码
 * @param {string} encryptedPassword - 加密后的密码
 * @returns {string} 解密后的密码
 */
export function decryptPassword(encryptedPassword) {
  // 使用 Base64 解密
  return atob(encryptedPassword)
}

/**
<<<<<<< HEAD
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean} 是否为有效邮箱格式
 */
export function validateEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
=======
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} Is valid email
 */
export function validateEmail(email) {
  // More robust email regex
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  return emailRegex.test(email)
}

/**
<<<<<<< HEAD
 * 验证手机号格式
 * @param {string} phone - 手机号码
 * @returns {boolean} 是否为有效手机号格式
 */
export function validatePhone(phone) {
  const phoneRegex = /^1[3-9]\d{9}$/
=======
 * Validate phone number format (International support)
 * @param {string} phone - Phone number
 * @returns {boolean} Is valid phone number
 */
export function validatePhone(phone) {
  // Allow optional + prefix, 7 to 15 digits
  const phoneRegex = /^\+?[0-9]{7,15}$/
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  return phoneRegex.test(phone)
}
