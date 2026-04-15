// 密码加密工具函数

/**
 * 使用 SHA-256 算法哈希密码
 * @param {string} password - 原始密码
 * @returns {Promise<string>} 哈希后的十六进制字符串
 */
export async function encryptPassword(password) {
  // 将字符串转为 Buffer
  const msgUint8 = new TextEncoder().encode(password)
  // 计算哈希值
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgUint8)
  // 将 ArrayBuffer 转为十六进制字符串
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  return hashHex
}

// 注意：SHA-256 是单向哈希，不可逆，因此原 decryptPassword 函数应删除或弃用

/**
 * Validate email format
 * @param {string} email - Email address
 * @returns {boolean} Is valid email
 */
export function validateEmail(email) {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
  return emailRegex.test(email)
}

/**
 * Validate phone number format (International support)
 * @param {string} phone - Phone number
 * @returns {boolean} Is valid phone number
 */
export function validatePhone(phone) {
  const phoneRegex = /^\+?[0-9]{7,15}$/
  return phoneRegex.test(phone)
}
