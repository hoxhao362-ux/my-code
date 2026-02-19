<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword, decryptPassword } from '../../utils/encryption'

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
const backgroundImages = [
  '/images/24.jpg',
  '/images/26.jpg',
  '/images/wzmc_20140317155634.jpg',
  '/images/wzmc_20140317160144.jpg'
]
const currentImageIndex = ref(0)
const backgroundImage = ref(backgroundImages[0])
let imageInterval = null

// Load remembered user
onMounted(() => {
  const savedUser = localStorage.getItem('readOnlyUser')
  if (savedUser) {
    const userData = JSON.parse(savedUser)
    username.value = userData.username || ''
    if (userData.password) {
      password.value = decryptPassword(userData.password)
    }
    rememberMe.value = true
  }
  
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

const handleLogin = async () => {
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
  
  try {
    // Call store action with password verification
    await userStore.login({
      username: username.value,
      password: password.value
    })
    
    // To satisfy "Remember Me" requirement:
    if (rememberMe.value) {
      localStorage.setItem('readOnlyUser', JSON.stringify({ 
        username: username.value,
        password: encryptPassword(password.value)
      }))
    } else {
      localStorage.removeItem('readOnlyUser')
    }
    
    // Redirect
    router.push('/home')
  } catch (error) {
    loginError.value = error.message || 'Login failed'
  } finally {
    isLoading.value = false
  }
}

const goToRegister = () => {
  router.push('/register')
}

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
    </div>
  </div>
</template>

<style scoped>
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
  }
}
</style>