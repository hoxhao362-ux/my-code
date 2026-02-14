<script setup>
<<<<<<< HEAD
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
=======
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const showPassword = ref(false)
const isLoading = ref(false)
const error = ref('')

// Background images
const backgroundImages = [
  '/images/24.jpg',
  '/images/26.jpg',
  '/images/wzmc_20140317155634.jpg',
  '/images/wzmc_20140317160144.jpg'
]
const currentImageIndex = ref(0)
const backgroundImage = ref(backgroundImages[0])
let imageInterval = null

onMounted(() => {
  // Start background image rotation
  startImageRotation()
})

onUnmounted(() => {
  // Clear interval when component is unmounted
  if (imageInterval) {
    clearInterval(imageInterval)
  }
})

// Start background image rotation
const startImageRotation = () => {
  imageInterval = setInterval(() => {
    currentImageIndex.value = (currentImageIndex.value + 1) % backgroundImages.length
    backgroundImage.value = backgroundImages[currentImageIndex.value]
  }, 5000) // Change image every 5 seconds
}

const togglePasswordVisibility = () => {
  showPassword.value = !showPassword.value
}

const handleRegister = () => {
  // Reset error
  error.value = ''
  
  // Validation
  if (!username.value || !email.value || !password.value || !confirmPassword.value) {
    error.value = 'Please complete all fields'
    return
  }
  
  if (!email.value.includes('@')) {
    error.value = 'Invalid email format'
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
    return
  }
  
  if (password.value !== confirmPassword.value) {
<<<<<<< HEAD
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
=======
    error.value = 'Passwords do not match'
    return
  }
  
  if (password.value.length < 6) {
    error.value = 'Password must be at least 6 characters'
    return
  }
  
  // Simulate Loading
  isLoading.value = true
  
  // Mock API Call (1.5s delay)
  setTimeout(() => {
    // Create Mock User
    const newUser = {
      username: username.value,
      email: email.value,
      role: 'user', // Force Read-Only role
      id: 'readonly_' + Date.now()
    }
    
    // In a real app, we would send this to backend.
    // For pure frontend simulation, we can optionally save to a mock DB in localStorage if needed for "Login" later.
    // But for this task, the requirement is "Registration successful! Please log in." flow.
    // We can store it in a 'mock_users' list to allow login simulation to check it? 
    // The Login.vue mock logic currently just accepts any non-empty input or specific mocks.
    // To make it consistent, let's just proceed to success.
    
    isLoading.value = false
    router.push('/login?registered=true')
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  }, 1500)
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
<<<<<<< HEAD
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
=======
  <div class="register-container" :style="{ backgroundImage: `url(${backgroundImage})` }">
    <div class="register-overlay">
      <div class="register-card">
      <!-- Header Section -->
      <div class="register-header">
        <h1 class="platform-title">
          Journal <span class="highlight">Submission Platform</span>
        </h1>
        <h2 class="register-subtitle">Register - Read-Only Access</h2>
        <p class="register-desc">
          Create an account to view content<br>
          (For submission/review access, please use the Submit System)
        </p>
      </div>

      <!-- Form Section -->
      <div class="register-form">
        <!-- Username -->
        <div class="form-group">
          <label>Username</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="Choose a username"
          />
        </div>
        
        <!-- Email -->
        <div class="form-group">
          <label>Email</label>
          <input 
            type="email" 
            v-model="email" 
            placeholder="Enter your email"
          />
        </div>

        <!-- Password -->
        <div class="form-group">
          <label>Password</label>
          <div class="password-input-wrapper">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="password" 
              placeholder="Create a password"
            />
            <span class="eye-icon" @click="togglePasswordVisibility">
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </span>
          </div>
        </div>
        
        <!-- Confirm Password -->
        <div class="form-group">
          <label>Confirm Password</label>
          <input 
            :type="showPassword ? 'text' : 'password'" 
            v-model="confirmPassword" 
            placeholder="Confirm your password"
          />
        </div>

        <!-- Error Message -->
        <p v-if="error" class="error-text">{{ error }}</p>

        <!-- Register Button -->
        <button 
          class="submit-btn" 
          @click="handleRegister" 
          :disabled="isLoading"
          :class="{ 'loading': isLoading }"
        >
          {{ isLoading ? 'Creating Account...' : 'Register' }}
        </button>
        
        <!-- Back to Login Link -->
        <div class="login-link-wrapper">
          <span class="login-text-label">Already have an account? </span>
          <a href="#" class="login-link" @click.prevent="goToLogin">Log in here</a>
        </div>
      </div>

      <!-- Footer Section -->
      <div class="register-footer">
        <div class="footer-links">
          <a href="#" target="_blank">Privacy Policy</a>
          <span class="separator">|</span>
          <a href="#" target="_blank">Terms of Use</a>
        </div>
        <p class="copyright">
          &copy; 2026 Journal Submission Platform. All rights reserved.
        </p>
      </div>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
      </div>
    </div>
  </div>
</template>

<style scoped>
<<<<<<< HEAD
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
=======
/* Global Layout */
.register-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #F8F8F8; /* Light Gray Background - Matching Login */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: background-image 1s ease-in-out;
  font-family: Arial, sans-serif;
  position: relative;
}

/* Overlay for better readability */
.register-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 100%;
}

/* Card Container */
.register-card {
  width: 420px; /* Slightly wider for registration form */
  background: #FFFFFF;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* Header Styles */
.register-header {
  text-align: center;
}

.platform-title {
  font-size: 24px; /* Slightly smaller than login to fit */
  font-weight: bold;
  color: #333333;
  margin: 0 0 12px 0;
  line-height: 1.2;
}

.highlight {
  color: #C93737; /* Brand Color */
}

.register-subtitle {
  font-size: 18px;
  font-weight: bold;
  color: #333333;
  margin: 0 0 8px 0;
}

.register-desc {
  font-size: 12px;
  color: #999999;
  line-height: 1.5;
  margin: 0;
}

/* Form Styles */
.register-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333333;
  font-weight: 500;
}

.form-group input {
  padding: 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  outline: none;
  transition: border-color 0.3s;
}

.form-group input::placeholder {
  color: #CCCCCC;
}

.form-group input:focus {
  border-color: #C93737;
}

/* Password Input Wrapper */
.password-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.password-input-wrapper input {
  width: 100%;
  padding-right: 40px; /* Space for eye icon */
}

.eye-icon {
  position: absolute;
  right: 12px;
  cursor: pointer;
  font-size: 16px;
  color: #999;
  user-select: none;
}

/* Error Text */
.error-text {
  font-size: 12px;
  color: #C93737;
  margin: 0;
  text-align: center;
}

/* Submit Button */
.submit-btn {
  width: 100%;
  padding: 12px;
  background-color: #C93737;
  color: white;
  font-size: 16px;
  font-weight: bold;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
  margin-top: 8px;
}

.submit-btn:hover {
  background-color: #B02E2E; /* Darken 10% */
}

.submit-btn.loading {
  background-color: #CCCCCC;
  cursor: not-allowed;
}

/* Login Link Wrapper */
.login-link-wrapper {
  text-align: center;
  margin-top: 12px;
  font-size: 12px;
  color: #333333;
}

.login-link {
  color: #C93737;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.login-link:hover {
  color: #B02E2E;
}

/* Footer Section */
.register-footer {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-top: 1px solid #F0F0F0;
  padding-top: 24px;
}

.footer-links {
  font-size: 11px;
  color: #999999;
}

.footer-links a {
  color: #999999;
  text-decoration: none;
}

.footer-links a:hover {
  color: #666666;
}

.separator {
  margin: 0 8px;
}

.copyright {
  font-size: 11px;
  color: #999999;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .register-card {
    width: 100%;
    max-width: 320px;
    padding: 24px;
    margin: 20px;
  }
  
  .register-desc {
    display: none; /* Hide non-core text on mobile */
  }
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
}
</style>