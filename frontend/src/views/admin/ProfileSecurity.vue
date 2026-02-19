<script setup>
import { ref } from 'vue'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'
import { encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()
const user = ref(userStore.user)

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

// 本地密码验证函数
const validatePassword = (password) => {
  // 验证密码长度和包含字母数字
  return password.length >= 6 && /[a-zA-Z]/.test(password) && /\d/.test(password)
}

// 密码更改数据
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 联系方式更改数据
const contactForm = ref({
  currentPassword: '',
  email: userStore.user?.email || '',
  phone: userStore.user?.phone || ''
})

// 双因素认证数据
const twoFactorAuth = ref({
  enabled: false,
  secret: '',
  verificationCode: ''
})

// 操作消息
const message = ref('')
const messageType = ref('') // 'success' or 'error'

// 显示消息
const showMessage = (type, msg) => {
  messageType.value = type
  message.value = msg
  setTimeout(() => {
    message.value = ''
  }, 3000)
}

// 验证邮箱格式
const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// 验证手机号格式
const validatePhone = (phone) => {
  const phoneRegex = /^1[3-9]\d{9}$/
  return phoneRegex.test(phone)
}

// 更改密码
const changePassword = () => {
  // 验证当前密码
  if (!passwordForm.value.currentPassword) {
    showMessage('error', '请输入当前密码')
    return
  }
  
  // 加密当前密码进行验证
  const encryptedCurrent = encryptPassword(passwordForm.value.currentPassword)
  if (encryptedCurrent !== userStore.user?.password) {
    showMessage('error', '当前密码不正确')
    return
  }
  
  // 验证新密码
  if (!passwordForm.value.newPassword) {
    showMessage('error', '请输入新密码')
    return
  }
  
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showMessage('error', '两次输入的新密码不一致')
    return
  }
  
  if (!validatePassword(passwordForm.value.newPassword)) {
    showMessage('error', '密码必须包含至少6个字符，包含字母和数字')
    return
  }
  
  // 加密新密码
  const encryptedNewPassword = encryptPassword(passwordForm.value.newPassword)
  
  // 更新用户密码
  userStore.updateUser({ password: encryptedNewPassword })
  
  // 重置表单
  passwordForm.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  
  showMessage('success', '密码更改成功')
}

// 更改联系方式
const changeContact = () => {
  // 验证当前密码
  if (!contactForm.value.currentPassword) {
    showMessage('error', '请输入当前密码')
    return
  }
  
  // 加密当前密码进行验证
  const encryptedCurrent = encryptPassword(contactForm.value.currentPassword)
  if (encryptedCurrent !== userStore.user?.password) {
    showMessage('error', '当前密码不正确')
    return
  }
  
  // 验证邮箱格式
  if (contactForm.value.email && !validateEmail(contactForm.value.email)) {
    showMessage('error', '请输入有效的邮箱地址')
    return
  }
  
  // 验证手机号格式
  if (contactForm.value.phone && !validatePhone(contactForm.value.phone)) {
    showMessage('error', '请输入有效的手机号')
    return
  }
  
  // 更新用户联系方式
  userStore.updateUser({
    email: contactForm.value.email,
    phone: contactForm.value.phone
  })
  
  // 重置表单
  contactForm.value = {
    currentPassword: '',
    email: contactForm.value.email,
    phone: contactForm.value.phone
  }
  
  showMessage('success', '联系方式更新成功')
}

// 切换双因素认证
const toggleTwoFactorAuth = () => {
  twoFactorAuth.value.enabled = !twoFactorAuth.value.enabled
  showMessage('success', twoFactorAuth.value.enabled ? '双因素认证已开启' : '双因素认证已关闭')
}

// 生成双因素认证密钥
const generateTwoFactorSecret = () => {
  // 模拟生成密钥
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'
  let secret = ''
  for (let i = 0; i < 16; i++) {
    secret += chars.charAt(Math.floor(Math.random() * chars.length))
  }
  twoFactorAuth.value.secret = secret
  showMessage('success', '双因素认证密钥已生成')
}
</script>

<template>
  <div class="admin-profile-security-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'admin-profile-security'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <!-- 账号安全内容 -->
    <main class="content">
      <div class="header">
        <h1>个人中心 - 账号安全</h1>
        <p class="subtitle">管理您的账号安全设置</p>
      </div>

      <!-- 消息提示 -->
      <div v-if="message" class="message" :class="messageType">
        {{ message }}
      </div>

      <section class="security-section">
        <div class="security-card">
          <!-- 密码更改 -->
          <div class="security-item">
            <h2>密码管理</h2>
            <div class="security-content">
              <form class="password-form" @submit.prevent="changePassword">
                <div class="form-row">
                  <div class="form-group">
                    <label for="currentPassword">当前密码</label>
                    <input 
                      type="password" 
                      id="currentPassword"
                      v-model="passwordForm.currentPassword"
                      class="form-control"
                      placeholder="请输入当前密码"
                      required
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label for="newPassword">新密码</label>
                    <input 
                      type="password" 
                      id="newPassword"
                      v-model="passwordForm.newPassword"
                      class="form-control"
                      placeholder="请输入新密码"
                      required
                    >
                  </div>
                  <div class="form-group">
                    <label for="confirmPassword">确认新密码</label>
                    <input 
                      type="password" 
                      id="confirmPassword"
                      v-model="passwordForm.confirmPassword"
                      class="form-control"
                      placeholder="请确认新密码"
                      required
                    >
                  </div>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-save">保存更改</button>
                </div>
              </form>
              <div class="password-requirements">
                <h3>密码要求：</h3>
                <ul>
                  <li>• 长度至少6个字符</li>
                  <li>• 包含字母和数字</li>
                  <li>• 建议包含大小写字母和特殊字符</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- 联系方式管理 -->
          <div class="security-item">
            <h2>联系方式管理</h2>
            <div class="security-content">
              <form class="contact-form" @submit.prevent="changeContact">
                <div class="form-row">
                  <div class="form-group">
                    <label for="contactCurrentPassword">当前密码</label>
                    <input 
                      type="password" 
                      id="contactCurrentPassword"
                      v-model="contactForm.currentPassword"
                      class="form-control"
                      placeholder="请输入当前密码以验证身份"
                      required
                    >
                  </div>
                </div>
                <div class="form-row">
                  <div class="form-group">
                    <label for="email">邮箱</label>
                    <input 
                      type="email" 
                      id="email"
                      v-model="contactForm.email"
                      class="form-control"
                      placeholder="请输入邮箱地址"
                      required
                    >
                  </div>
                  <div class="form-group">
                    <label for="phone">手机号</label>
                    <input 
                      type="tel" 
                      id="phone"
                      v-model="contactForm.phone"
                      class="form-control"
                      placeholder="请输入手机号"
                      required
                    >
                  </div>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-save">保存更改</button>
                </div>
              </form>
            </div>
          </div>

          <!-- 双因素认证 -->
          <div class="security-item">
            <h2>双因素认证</h2>
            <div class="security-content">
              <div class="two-factor-header">
                <p>双因素认证可以为您的账号提供额外的安全保护</p>
                <div class="toggle-switch-container">
                  <label class="toggle-switch">
                    <input 
                      type="checkbox" 
                      v-model="twoFactorAuth.enabled"
                      @change="toggleTwoFactorAuth"
                    >
                    <span class="toggle-slider"></span>
                  </label>
                  <span class="toggle-label">{{ twoFactorAuth.enabled ? '已开启' : '已关闭' }}</span>
                </div>
              </div>
              <div v-if="twoFactorAuth.enabled" class="two-factor-setup">
                <div class="setup-step">
                  <h3>1. 生成认证密钥</h3>
                  <div class="secret-display">
                    <span v-if="twoFactorAuth.secret" class="secret-text">{{ twoFactorAuth.secret }}</span>
                    <button 
                      class="btn btn-generate" 
                      @click="generateTwoFactorSecret"
                      :disabled="twoFactorAuth.secret"
                    >
                      生成密钥
                    </button>
                  </div>
                </div>
                <div class="setup-step">
                  <h3>2. 扫描二维码</h3>
                  <div class="qr-code-container">
                    <div class="qr-placeholder">二维码将显示在这里</div>
                  </div>
                </div>
                <div class="setup-step">
                  <h3>3. 验证验证码</h3>
                  <div class="verification-code">
                    <input 
                      type="text" 
                      v-model="twoFactorAuth.verificationCode"
                      class="form-control"
                      placeholder="请输入验证码"
                      maxlength="6"
                    >
                    <button class="btn btn-verify">验证</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </main>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 期刊投稿平台. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
/* 主容器样式 */
.admin-profile-security-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.content.embedded-content {
  margin-top: 0;
}

/* 头部样式 */
.header {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.subtitle {
  font-size: 0.95rem;
  color: #7f8c8d;
  margin: 0;
  font-weight: 400;
}

/* 消息提示样式 */
.message {
  padding: 1rem 1.5rem;
  border-radius: 6px;
  margin-bottom: 2rem;
  font-weight: 500;
  font-size: 0.95rem;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

/* 安全设置区域样式 */
.security-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 2rem;
  margin-bottom: 2rem;
}

/* 安全卡片样式 */
.security-card {
  max-width: 800px;
}

/* 安全项目样式 */
.security-item {
  margin-bottom: 2.5rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e9ecef;
}

.security-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.security-item h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-weight: 600;
}

/* 密码表单样式 */
.password-form {
  margin-bottom: 2rem;
}

.form-row {
  display: flex;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.form-group {
  flex: 1;
  min-width: 250px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 0.95rem;
}

.form-control {
  padding: 0.9rem 1.2rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 2rem;
}

/* 按钮样式 */
.btn {
  padding: 0.9rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-width: 120px;
}

.btn-save {
  background-color: #2ecc71;
  color: white;
}

.btn-save:hover {
  background-color: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
}

.btn-generate {
  background-color: #3498db;
  color: white;
}

.btn-generate:hover:not(:disabled) {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-generate:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
  opacity: 0.7;
}

.btn-verify {
  background-color: #f39c12;
  color: white;
}

.btn-verify:hover {
  background-color: #e67e22;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(243, 156, 18, 0.3);
}

/* 密码要求样式 */
.password-requirements {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.password-requirements h3 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 600;
}

.password-requirements ul {
  margin: 0;
  padding-left: 1.5rem;
}

.password-requirements li {
  margin-bottom: 0.5rem;
  color: #6c757d;
  font-size: 0.95rem;
}

.password-requirements li:last-child {
  margin-bottom: 0;
}

/* 双因素认证样式 */
.two-factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.toggle-switch-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* 切换开关样式 */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 34px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #3498db;
}

input:focus + .toggle-slider {
  box-shadow: 0 0 1px #3498db;
}

input:checked + .toggle-slider:before {
  transform: translateX(26px);
}

.toggle-label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 1rem;
}

/* 双因素设置样式 */
.two-factor-setup {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
}

.setup-step {
  margin-bottom: 2rem;
}

.setup-step:last-child {
  margin-bottom: 0;
}

.setup-step h3 {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 600;
}

.secret-display {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.secret-text {
  font-family: 'Courier New', Courier, monospace;
  font-size: 1.2rem;
  font-weight: 600;
  padding: 0.75rem 1.5rem;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  min-width: 200px;
  text-align: center;
  letter-spacing: 2px;
}

.qr-code-container {
  display: flex;
  justify-content: center;
  margin: 1.5rem 0;
}

.qr-placeholder {
  width: 200px;
  height: 200px;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  font-size: 0.95rem;
}

.verification-code {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.verification-code .form-control {
  flex: 1;
  min-width: 200px;
  font-size: 1.1rem;
  text-align: center;
  letter-spacing: 2px;
}

/* 页脚样式 */
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 1rem 0;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  text-align: center;
  font-size: 0.9rem;
}

.footer-content p {
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: 1rem;
    margin-top: 70px;
  }
  
  .header h1 {
    font-size: 1.5rem;
  }
  
  .security-section {
    padding: 1.5rem;
  }
  
  .form-row {
    flex-direction: column;
    gap: 1rem;
  }
  
  .form-group {
    width: 100%;
    min-width: auto;
  }
  
  .form-actions {
    justify-content: stretch;
  }
  
  .btn {
    width: 100%;
  }
  
  .two-factor-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .secret-display {
    flex-direction: column;
    align-items: stretch;
  }
  
  .secret-text {
    text-align: center;
  }
  
  .verification-code {
    flex-direction: column;
    align-items: stretch;
  }
  
  .verification-code .form-control {
    text-align: left;
  }
}
</style>