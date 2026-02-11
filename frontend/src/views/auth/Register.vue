<script setup>
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
    return
  }
  
  if (password.value !== confirmPassword.value) {
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
  }, 1500)
}

const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
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
      </div>
    </div>
  </div>
</template>

<style scoped>
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
}
</style>