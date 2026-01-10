<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Navigation from '../components/Navigation.vue'
import { useUserStore } from '../stores/user'
import { validateEmail, validatePhone, encryptPassword } from '../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

// 检查用户是否登录
const user = computed(() => userStore.user)
if (!user.value) {
  router.push('/login')
}

// 消息提示
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

// 密码更改数据
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 联系方式更改数据
const contactForm = ref({
  currentPassword: '',
  email: user.value?.email || '',
  phone: user.value?.phone || ''
})

// 验证密码长度和包含字母数字
const validatePassword = (password) => {
  return password.length >= 6 && /[a-zA-Z]/.test(password) && /\d/.test(password)
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
  if (encryptedCurrent !== user.value?.password) {
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
  if (encryptedCurrent !== user.value?.password) {
    showMessage('error', '当前密码不正确')
    return
  }
  
  // 验证邮箱格式
  if (!validateEmail(contactForm.value.email)) {
    showMessage('error', '请输入有效的邮箱地址')
    return
  }
  
  // 验证手机号格式
  if (!validatePhone(contactForm.value.phone)) {
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
</script>

<template>
  <div class="main-account-security-container">
    <!-- 导航栏 -->
    <Navigation 
      :user="user"
      :current-page="'account-security'"
      :toggle-directory="() => {}"
      :logout="userStore.logout"
    />

    <!-- 账号安全内容 -->
    <main class="content">
      <div class="header">
        <h1>账号安全</h1>
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
                <div class="password-requirements">
                  <h3>密码要求：</h3>
                  <ul>
                    <li>• 长度至少6个字符</li>
                    <li>• 包含字母和数字</li>
                    <li>• 建议包含大小写字母和特殊字符</li>
                  </ul>
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-save">保存更改</button>
                </div>
              </form>
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
.main-account-security-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

/* 内容区域样式 */
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
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
  color: #7f8c8d;
  font-size: 1rem;
  margin: 0;
}

/* 消息提示样式 */
.message {
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-weight: 500;
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

/* 安全区域样式 */
.security-section {
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
}

.security-card {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.security-item {
  border-bottom: 1px solid #eee;
  padding-bottom: 2rem;
}

.security-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.security-item h2 {
  font-size: 1.3rem;
  color: #2c3e50;
  margin: 0 0 1.5rem 0;
  font-weight: 600;
}

/* 表单样式 */
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
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
}

.form-control:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

/* 密码要求样式 */
.password-requirements {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  margin: 1rem 0 1.5rem 0;
}

.password-requirements h3 {
  font-size: 1rem;
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
}

.password-requirements ul {
  margin: 0;
  padding-left: 1.5rem;
}

.password-requirements li {
  color: #6c757d;
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

/* 按钮样式 */
.form-actions {
  display: flex;
  justify-content: flex-start;
}

.btn {
  padding: 0.8rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-save {
  background: #2ecc71;
  color: white;
}

.btn-save:hover {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
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
  }
  
  .form-group {
    width: 100%;
  }
  
  .form-actions {
    justify-content: stretch;
  }
  
  .btn {
    width: 100%;
  }
}
</style>