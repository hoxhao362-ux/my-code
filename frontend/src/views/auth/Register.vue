<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword, validateEmail, validatePhone } from '../../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const email = ref('')
const phone = ref('')
const password = ref('')
const confirmPassword = ref('')
const invitationCode = ref('')
const verificationCode = ref('')
const error = ref('')
const success = ref('')
const countDown = ref(0)
const timer = ref(null)

// 生成验证码（模拟）
const generateVerificationCode = () => {
  return Math.floor(100000 + Math.random() * 900000).toString()
}

// 发送验证码
const sendVerificationCode = () => {
  if (!email.value) {
    error.value = '请先填写邮箱'
    return
  }
  
  if (!validateEmail(email.value)) {
    error.value = '请输入有效的邮箱格式'
    return
  }
  
  // 模拟发送验证码
  const code = generateVerificationCode()
  console.log('验证码已发送：', code)
  alert('验证码已发送到您的邮箱，实际开发中会调用后端接口发送')
  
  // 倒计时
  countDown.value = 60
  if (timer.value) clearInterval(timer.value)
  timer.value = setInterval(() => {
    countDown.value--
    if (countDown.value <= 0) {
      clearInterval(timer.value)
    }
  }, 1000)
}

// 验证邀请码并确定角色
const determineRole = (code) => {
  if (!code) return 'user'
  if (code === userStore.adminCode) return 'admin'
  if (code === userStore.reviewerCode) return 'reviewer'
  if (code === userStore.authorCode) return 'author'
  return 'user'
}

const handleRegister = () => {
  // 表单验证
  if (!username.value || !email.value || !phone.value || !password.value || !confirmPassword.value || !verificationCode.value) {
    error.value = '请填写完整的注册信息'
    return
  }
  
  // 邮箱格式验证
  if (!validateEmail(email.value)) {
    error.value = '请输入有效的邮箱格式'
    return
  }
  
  // 手机号格式验证
  if (!validatePhone(phone.value)) {
    error.value = '请输入有效的手机号格式'
    return
  }
  
  if (password.value !== confirmPassword.value) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  // 模拟验证码验证（实际开发中会调用后端接口验证）
  
  // 加密密码
  const encryptedPassword = encryptPassword(password.value)
  
  // 确定角色
  const role = determineRole(invitationCode.value)
  
  // 模拟注册逻辑
  const userData = {
    id: Date.now().toString(),
    username: username.value,
    email: email.value,
    phone: phone.value,
    password: encryptedPassword,
    role: role
  }
  
  // 添加用户到用户列表
  userStore.users.push(userData)
  localStorage.setItem('users', JSON.stringify(userStore.users))
  
  // 调用状态管理的登录方法（实际应该调用注册方法，这里简化处理）
  userStore.login(userData)
  
  // 显示成功消息并跳转到首页
  success.value = '注册成功！正在跳转到首页...'
  
  setTimeout(() => {
    router.push('/')
  }, 1500)
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-container">
    <div class="register-bg"></div>
    <div class="register-form-wrapper">
      <div class="register-form">
        <h2 class="register-title">用户注册</h2>
        
        <div class="form-group">
          <label for="username">用户名</label>
          <input 
            type="text" 
            id="username" 
            v-model="username" 
            placeholder="请输入用户名"
          />
        </div>
        
        <div class="form-group">
          <label for="email">邮箱</label>
          <input 
            type="email" 
            id="email" 
            v-model="email" 
            placeholder="请输入邮箱"
          />
        </div>
        
        <div class="form-group">
          <label for="phone">手机号</label>
          <input 
            type="tel" 
            id="phone" 
            v-model="phone" 
            placeholder="请输入手机号"
          />
        </div>
        
        <div class="form-group verification-group">
          <div class="verification-input">
            <label for="verificationCode">验证码</label>
            <input 
              type="text" 
              id="verificationCode" 
              v-model="verificationCode" 
              placeholder="请输入验证码"
            />
          </div>
          <button 
            class="send-code-btn" 
            @click="sendVerificationCode" 
            :disabled="countDown > 0"
          >
            {{ countDown > 0 ? `${countDown}秒后重发` : '发送验证码' }}
          </button>
        </div>
        
        <div class="form-group">
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="请输入密码"
          />
        </div>
        
        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <input 
            type="password" 
            id="confirmPassword" 
            v-model="confirmPassword" 
            placeholder="请再次输入密码"
          />
        </div>
        
        <div class="form-group">
          <label for="invitationCode">邀请码（选填）</label>
          <input 
            type="text" 
            id="invitationCode" 
            v-model="invitationCode" 
            placeholder="填写邀请码可获得对应权限"
          />
        </div>
        
        <p v-if="error" class="error-message">{{ error }}</p>
        <p v-if="success" class="success-message">{{ success }}</p>
        
        <button class="register-btn" @click="handleRegister">注册</button>
        <div class="login-link">
          <span>已有账号？</span>
          <a href="#" @click.prevent="goToLogin">立即登录</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 基本样式 */
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  position: relative;
}

.register-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://picsum.photos/1920/1080');
  background-size: cover;
  background-position: center;
  opacity: 0.5;
  z-index: 0;
}

.register-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  padding: 2rem;
  width: 100%;
  max-width: 400px;
}

.register-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #4a90e2;
}

.verification-group {
  display: flex;
  gap: 0.5rem;
  align-items: flex-start;
}

.verification-input {
  flex: 1;
}

.send-code-btn {
  margin-top: 1.5rem;
  padding: 0.75rem 1rem;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.3s;
}

.send-code-btn:hover:not(:disabled) {
  background-color: #357abd;
}

.send-code-btn:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error-message {
  color: #e74c3c;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.success-message {
  color: #27ae60;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.register-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: #27ae60;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.3s;
  margin-bottom: 1rem;
}

.register-btn:hover {
  background-color: #229954;
}

.login-link {
  text-align: center;
  font-size: 0.9rem;
  color: #555;
}

.login-link a {
  color: #4a90e2;
  text-decoration: none;
  transition: color 0.3s;
}

.login-link a:hover {
  color: #357abd;
}
</style>