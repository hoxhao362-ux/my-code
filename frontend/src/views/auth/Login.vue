<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
<<<<<<< HEAD
import { encryptPassword } from '../../utils/encryption'

const userStore = useUserStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
// 记住密码
const rememberMe = ref(false)

// 背景图片轮播
=======

const router = useRouter()
const userStore = useUserStore()

const username = ref('')
const password = ref('')
const rememberMe = ref(false)
const showPassword = ref(false)
const isLoading = ref(false)
const usernameError = ref('')
const passwordError = ref('')
const loginError = ref('')

// Background images
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
const backgroundImages = [
  '/images/24.jpg',
  '/images/26.jpg',
  '/images/wzmc_20140317155634.jpg',
  '/images/wzmc_20140317160144.jpg'
]
const currentImageIndex = ref(0)
<<<<<<< HEAD
let imageInterval = null

// 从localStorage加载记住的密码
onMounted(() => {
  const savedUsername = localStorage.getItem('rememberedUsername')
  const savedPassword = localStorage.getItem('rememberedPassword')
  if (savedUsername && savedPassword) {
    username.value = savedUsername
    password.value = savedPassword
    rememberMe.value = true
  }
  
  // 启动背景图片轮播，每5秒切换一次
  imageInterval = setInterval(() => {
    currentImageIndex.value = (currentImageIndex.value + 1) % backgroundImages.length
  }, 5000)
})

// 组件卸载时清除定时器
onUnmounted(() => {
=======
const backgroundImage = ref(backgroundImages[0])
let imageInterval = null

// Load remembered user
onMounted(() => {
  const savedUser = localStorage.getItem('readOnlyUser')
  if (savedUser) {
    const userData = JSON.parse(savedUser)
    username.value = userData.username || ''
    rememberMe.value = true
  }
  
  // Start background image rotation
  startImageRotation()
})

onUnmounted(() => {
  // Clear interval when component is unmounted
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  if (imageInterval) {
    clearInterval(imageInterval)
  }
})

<<<<<<< HEAD
const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = '请输入用户名和密码'
    return
  }
  
  try {
    // 加密密码
    const encryptedPassword = encryptPassword(password.value)
    
    // 准备登录凭证
    const credentials = {
      username: username.value,
      password: encryptedPassword
    }
    
    // 调用状态管理的登录方法
    await userStore.login(credentials)
    
    // 记住密码功能
    if (rememberMe.value) {
      localStorage.setItem('rememberedUsername', username.value)
      localStorage.setItem('rememberedPassword', password.value)
    } else {
      localStorage.removeItem('rememberedUsername')
      localStorage.removeItem('rememberedPassword')
    }
    
    // 跳转到首页
    router.push('/home')
  } catch (err) {
    console.error('登录失败:', err)
    // 如果API调用失败，使用模拟登录逻辑
    // 根据用户名自动识别角色
    let role = username.value === 'admin' ? 'admin' : 
               username.value === 'reviewer' ? 'reviewer' : 
               username.value === 'user' ? 'user' : 'author'
    
    // 创建用户数据
    const userData = {
      username: username.value,
      role: role,
      email: '',
      phone: '',
      avatar: ''
    }
    
    // 直接设置用户状态
    userStore.user = userData
    localStorage.setItem('user', JSON.stringify(userData))
    
    // 跳转到首页
    router.push('/home')
  }
=======
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

const handleLogin = () => {
  // Reset errors
  usernameError.value = ''
  passwordError.value = ''
  loginError.value = ''
  
  // Frontend Validation
  let hasError = false
  if (!username.value) {
    usernameError.value = 'Please enter your email/username'
    hasError = true
  }
  if (!password.value) {
    passwordError.value = 'Please enter your password'
    hasError = true
  }
  
  if (hasError) return

  // Loading State
  isLoading.value = true
  
  // Mock Login Delay (1.5s)
  setTimeout(() => {
    // Mock Success (Pure Frontend)
    // Create mock user data for Main Site Read-Only context
    const mockUser = {
      username: username.value,
      role: 'user', // Basic user role for read-only
      email: username.value.includes('@') ? username.value : `${username.value}@example.com`,
      id: 'readonly_' + Date.now()
    }
    
    // Update Store (Client-side only)
    userStore.user = mockUser
    // We do NOT save to the main 'user' localStorage to avoid conflict with Submit system if possible,
    // BUT Navigation.vue checks localStorage('user') or store.
    // The requirement says: "Remember me... store in localStorage... not cross with submit login".
    // "Login success... jump to main site static home... no backend interface call".
    
    // To satisfy "Remember Me" requirement:
    if (rememberMe.value) {
      localStorage.setItem('readOnlyUser', JSON.stringify({ username: username.value }))
    } else {
      localStorage.removeItem('readOnlyUser')
    }
    
    // For session persistence (Read-Only Session), we might need to set 'user' in store.
    // Since we can't touch backend, we just set the store state.
    // If the app reloads, state is lost unless we save to localStorage.
    // Standard 'user' key is used by main site. Submit system uses 'submissionUser'.
    // So it is safe to use 'user' key for Main Site Read-Only session as long as it doesn't overwrite 'submissionUser'.
    sessionStorage.setItem('readonly_user', JSON.stringify(mockUser))
    sessionStorage.setItem('readonly_isLogin', 'true')
    
    isLoading.value = false
    router.push('/home')
  }, 1500)
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
}

const goToRegister = () => {
  router.push('/register')
}
<<<<<<< HEAD
</script>

<template>
  <div class="login-container">
    <div class="login-bg" :style="{ backgroundImage: `url(${backgroundImages[currentImageIndex]})` }"></div>
    <div class="login-form-wrapper">
      <div class="login-form">
        <!-- 登录标题 -->
        <h2 class="login-title">期刊投稿平台</h2>
        
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
          <label for="password">密码</label>
          <input 
            type="password" 
            id="password" 
            v-model="password" 
            placeholder="请输入密码"
          />
        </div>
        
        <!-- 记住密码 -->
        <div class="form-group remember-me">
          <input 
            type="checkbox" 
            id="rememberMe" 
            v-model="rememberMe" 
          />
          <label for="rememberMe">记住密码</label>
        </div>
        
        <p v-if="error" class="error-message">{{ error }}</p>
        <button class="login-btn" @click="handleLogin">登录</button>
        <div class="register-link">
          <span>还没有账号？</span>
          <a href="#" @click.prevent="goToRegister">立即注册</a>
        </div>
      </div>
=======

const goToForgotPassword = () => {
  // Static mock page or just alert as placeholder if no route exists yet, 
  // but spec says "jump to frontend static forgot password page". 
  // Assuming we might need to create one or just link to a placeholder.
  // For now, I'll point to a query param to simulate.
  router.push('/login?view=forgot-password') 
}
</script>

<template>
  <div class="login-container" :style="{ backgroundImage: `url(${backgroundImage})` }">
    <div class="login-overlay">
      <div class="login-card">
      <!-- Header Section -->
      <div class="login-header">
        <!-- Success Message Toast (Pure Frontend) -->
        <div v-if="successMessage" class="success-toast">
          {{ successMessage }}
        </div>

        <h1 class="platform-title">
          Journal <span class="highlight">Submission Platform</span>
        </h1>
        <h2 class="login-subtitle">Login - Read-Only Access</h2>
        <p class="login-desc">
          Access to view content only - no editing/submission permissions<br>
          Separate from submit login system (second-tier access)
        </p>
      </div>

      <!-- Form Section -->
      <div class="login-form">
        <!-- Username -->
        <div class="form-group" :class="{ 'has-error': usernameError }">
          <label>Username / Email</label>
          <input 
            type="text" 
            v-model="username" 
            placeholder="Enter your registered email/username"
            :class="{ 'error-border': usernameError }"
          />
          <p v-if="usernameError" class="error-text">{{ usernameError }}</p>
        </div>

        <!-- Password -->
        <div class="form-group" :class="{ 'has-error': passwordError }">
          <label>Password</label>
          <div class="password-input-wrapper">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="password" 
              placeholder="Enter your password"
              :class="{ 'error-border': passwordError }"
            />
            <span class="eye-icon" @click="togglePasswordVisibility">
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </span>
          </div>
          <p v-if="passwordError" class="error-text">{{ passwordError }}</p>
        </div>

        <!-- Actions -->
        <div class="form-actions">
          <label class="remember-me">
            <input type="checkbox" v-model="rememberMe">
            <span>Remember me for 30 days</span>
          </label>
          <a href="#" class="forgot-password" @click.prevent="goToForgotPassword">Forgot Password?</a>
        </div>

        <!-- Login Error -->
        <p v-if="loginError" class="login-error-text">{{ loginError }}</p>

        <!-- Submit Button -->
        <button 
          class="submit-btn" 
          @click="handleLogin" 
          :disabled="isLoading"
          :class="{ 'loading': isLoading }"
        >
          {{ isLoading ? 'Logging in...' : 'Login' }}
        </button>

        <!-- Register Link (Read-Only) -->
        <div class="register-link-wrapper">
          <span class="register-text-label">Don’t have an account? </span>
          <a href="#" class="register-link" @click.prevent="goToRegister">Register for Read-Only Access</a>
        </div>
      </div>

      <!-- Footer Section -->
      <div class="login-footer">
        <div class="footer-links">
          <a href="#" target="_blank">Privacy Policy</a>
          <span class="separator">|</span>
          <a href="#" target="_blank">Terms of Use</a>
        </div>
        <p class="copyright">
          &copy; 2026 Journal Submission Platform. All rights reserved.
        </p>
      </div>
      </div>
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
    </div>
  </div>
</template>

<style scoped>
<<<<<<< HEAD
/* 登录页面样式 */
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 0;
  transition: background-image 1s ease-in-out;
  animation: backgroundAnimation 30s ease-in-out infinite;
}

/* 背景动态效果 */
@keyframes backgroundAnimation {
  0% {
    transform: scale(1) translateX(0);
  }
  50% {
    transform: scale(1.1) translateX(-5%);
  }
  100% {
    transform: scale(1) translateX(0);
  }
}

.login-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 5px 25px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
  backdrop-filter: blur(10px);
  animation: fadeIn 0.5s ease-out;
}

/* 表单淡入效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #2c3e50;
  font-size: 2rem;
  font-weight: bold;
}

/* 表单样式 */
.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.95rem;
=======
/* Global Layout */
.login-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #F8F8F8; /* Light Gray Background */
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  transition: background-image 1s ease-in-out;
  font-family: Arial, sans-serif;
  position: relative;
}

/* Overlay for better readability */
.login-overlay {
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
.login-card {
  width: 380px; /* Fixed Width for PC */
  background: #FFFFFF;
  border: 1px solid #E5E5E5;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 32px;
  position: relative;
}

/* Success Toast */
.success-toast {
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #e8f5e9;
  color: #2e7d32;
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translate(-50%, -10px); }
  to { opacity: 1; transform: translate(-50%, 0); }
}

/* Header Styles */
.login-header {
  text-align: center;
}

.platform-title {
  font-size: 28px;
  font-weight: bold;
  color: #333333;
  margin: 0 0 12px 0;
  line-height: 1.2;
}

.highlight {
  color: #C93737; /* Brand Color */
}

.login-subtitle {
  font-size: 18px;
  font-weight: bold;
  color: #333333;
  margin: 0 0 8px 0;
}

.login-desc {
  font-size: 12px;
  color: #999999;
  line-height: 1.5;
  margin: 0;
}

/* Form Styles */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  color: #333333;
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  font-weight: 500;
}

.form-group input {
<<<<<<< HEAD
  width: 100%;
  padding: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: all 0.3s ease;
  background-color: rgba(255, 255, 255, 0.9);
}

.form-group input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  background-color: white;
}

/* 记住密码样式 */
.remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 0.75rem;
}

.remember-me input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin: 0;
  accent-color: #3498db;
}

.remember-me label {
  margin: 0;
  font-size: 0.95rem;
  color: #666;
  cursor: pointer;
  transition: color 0.3s ease;
}

.remember-me label:hover {
  color: #3498db;
}

/* 错误消息样式 */
.error-message {
  color: #e74c3c;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  text-align: center;
  padding: 0.75rem;
  background-color: rgba(231, 76, 60, 0.1);
  border-radius: 4px;
  border: 1px solid rgba(231, 76, 60, 0.2);
}

/* 登录按钮样式 */
.login-btn {
  width: 100%;
  padding: 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

.login-btn:hover {
  background-color: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.login-btn:active {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(52, 152, 219, 0.3);
}

/* 注册链接样式 */
.register-link {
  text-align: center;
  font-size: 0.95rem;
  color: #666;
}

.register-link a {
  color: #3498db;
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.register-link a:hover {
  color: #2980b9;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-form-wrapper {
    padding: 1.5rem;
    margin: 1rem;
  }
  
  .login-title {
    font-size: 1.6rem;
=======
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

.error-border {
  border-color: #C93737 !important;
}

.error-text {
  font-size: 12px;
  color: #C93737;
  margin: 4px 0 0 0;
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

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: -4px;
}

.remember-me {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.remember-me input[type="checkbox"] {
  accent-color: #C93737;
  width: 14px;
  height: 14px;
}

.remember-me span {
  font-size: 12px;
  color: #333333;
}

.forgot-password {
  font-size: 12px;
  color: #C93737;
  text-decoration: none;
}

.forgot-password:hover {
  text-decoration: underline;
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

.login-error-text {
  font-size: 12px;
  color: #C93737;
  text-align: center;
  margin: 0;
}

/* Register Link Wrapper */
.register-link-wrapper {
  text-align: center;
  margin-top: 12px;
  font-size: 12px;
  color: #333333;
}

.register-link {
  color: #C93737;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}

.register-link:hover {
  color: #B02E2E;
}

/* Footer Section */
.login-footer {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-top: 1px solid #F0F0F0;
  padding-top: 24px;
}

.register-text {
  font-size: 12px;
  color: #333333;
  margin: 0;
}

.register-text a {
  color: #C93737;
  text-decoration: none;
  font-weight: 500;
}

.register-text a:hover {
  text-decoration: underline;
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
  .login-card {
    width: 100%;
    max-width: 320px;
    padding: 24px;
    margin: 20px;
  }
  
  .login-desc {
    display: none; /* Hide non-core text on mobile */
>>>>>>> e5fb48ccf9d841fc1e38217dce4c36103c37bd05
  }
}
</style>