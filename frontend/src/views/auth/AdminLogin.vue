<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { encryptPassword } from '../../utils/encryption'
import { useI18n } from '../../composables/useI18n'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const username = ref('')
const password = ref('')
const error = ref('')
// Role selected by context or dropdown
const selectedRole = ref('')
// Remember Me
const rememberMe = ref(false)

// Determine Context and Title
const contextTitle = computed(() => {
  const role = route.query.role
  if (role === 'author') return t('auth.adminLogin.title.author')
  if (role === 'reviewer') return t('auth.adminLogin.title.reviewer')
  if (role === 'admin') return t('auth.adminLogin.title.admin')
  return t('auth.adminLogin.title.default')
})

// Auto-select role based on query
onMounted(() => {
  if (route.query.role === 'author') {
    selectedRole.value = 'author'
  } else if (route.query.role) {
    selectedRole.value = route.query.role
  }

  const savedUsername = localStorage.getItem('adminRememberedUsername')
  const savedPassword = localStorage.getItem('adminRememberedPassword')
  if (savedUsername && savedPassword) {
    username.value = savedUsername
    password.value = savedPassword
    rememberMe.value = true
  }
})

const handleLogin = async () => {
  if (!username.value || !password.value) {
    error.value = t('auth.adminLogin.error.required')
    return
  }
  
  try {
    // Pass plaintext password to userStore.login
    
    // Role Logic: 1. URL Query 2. Dropdown 3. Fallback
    let role = selectedRole.value || (username.value === 'admin' ? 'admin' : 
               username.value === 'reviewer' ? 'reviewer' : 
               username.value === 'author' || username.value.startsWith('author') ? 'author' : 
               'user')
    
    // Check if user is trying to login to wrong portal
    if (route.query.role && role !== route.query.role) {
       // Allow "admin" to login everywhere, but strict for others
       if (role !== 'admin') {
         error.value = t('auth.adminLogin.error.authorized', { role: role.charAt(0).toUpperCase() + role.slice(1) })
         return
       }
    }

    const credentials = {
      username: username.value,
      password: password.value,
      role: role
    }
    
    await userStore.login(credentials)
    
    if (rememberMe.value) {
      localStorage.setItem('adminRememberedUsername', username.value)
      localStorage.setItem('adminRememberedPassword', password.value)
    } else {
      localStorage.removeItem('adminRememberedUsername')
      localStorage.removeItem('adminRememberedPassword')
    }
    
    let redirectPath = '/admin/login'
    if (userStore.currentRole === 'admin') {
      redirectPath = '/editor/dashboard'
    } else if (userStore.currentRole === 'reviewer') {
      redirectPath = '/reviewer/dashboard'
    } else if (userStore.currentRole === 'author') {
      redirectPath = '/admin/author-dashboard'
    } else if (userStore.currentRole === 'editor' || userStore.currentRole === 'associate_editor') {
      redirectPath = '/editor/dashboard'
    }
    
    // If Admin logs into specific portal, redirect there? 
    // Usually Admin goes to Editor Portal.
    
    router.push(redirectPath)
  } catch (err) {
    console.error('Login failed:', err)
    error.value = t('auth.adminLogin.error.failed')
  }
}

const goToRegister = () => {
  router.push('/admin/register')
}
</script>

<template>
  <div class="admin-login-container">
    <div class="admin-login-bg"></div>
    <div class="admin-login-form-wrapper">
      <div class="admin-login-form">
        <!-- 登录标题 -->
        <h2 class="admin-login-title">{{ contextTitle }}</h2>
        
        <div class="admin-form-group">
          <label for="admin-username">{{ t('auth.adminLogin.username') }}</label>
          <input 
            type="text" 
            id="admin-username" 
            v-model="username" 
            :placeholder="t('auth.adminLogin.username')"
          />
        </div>
        <div class="admin-form-group">
          <label for="admin-password">{{ t('auth.adminLogin.password') }}</label>
          <input 
            type="password" 
            id="admin-password" 
            v-model="password" 
            :placeholder="t('auth.adminLogin.password')"
          />
        </div>
        
        <!-- 记住密码 -->
        <div class="admin-form-group admin-remember-me">
          <input 
            type="checkbox" 
            id="admin-rememberMe" 
            v-model="rememberMe" 
          />
          <label for="admin-rememberMe">{{ t('auth.adminLogin.rememberMe') }}</label>
        </div>
        
        <!-- 角色选择 (Hide if fixed in query) -->
        <div class="admin-form-group" v-if="!route.query.role">
          <label for="admin-role">{{ t('auth.adminLogin.role') }}</label>
          <select 
            id="admin-role" 
            v-model="selectedRole"
            class="admin-role-select"
          >
            <option value="">{{ t('auth.adminLogin.selectRole') }}</option>
            <option value="admin">{{ t('auth.adminLogin.roles.admin') }}</option>
            <option value="editor">{{ t('auth.adminLogin.roles.editor') }}</option>
            <option value="reviewer">{{ t('auth.adminLogin.roles.reviewer') }}</option>
            <option value="author">{{ t('auth.adminLogin.roles.author') }}</option>
          </select>
        </div>
        
        <p v-if="error" class="admin-error-message">{{ error }}</p>
        <button class="admin-login-btn" @click="handleLogin">{{ t('auth.adminLogin.loginBtn') }}</button>
        <div class="admin-register-link">
          <span>{{ t('auth.adminLogin.noAccount') }}</span>
          <a href="#" @click.prevent="goToRegister">{{ t('auth.adminLogin.registerNow') }}</a>
        </div>
        <div class="admin-back-link">
          <a href="/" @click.prevent="router.push('/')">{{ t('auth.adminLogin.backToHome') }}</a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 后台登录页面样式 */
.admin-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #e9ecef;
  position: relative;
}

.admin-login-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url('https://picsum.photos/1920/1080');
  background-size: cover;
  background-position: center;
  opacity: 0.3;
  z-index: 0;
}

.admin-login-form-wrapper {
  position: relative;
  z-index: 1;
  background-color: rgba(255, 255, 255, 0.98);
  border-radius: 10px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  padding: 2.5rem;
  width: 100%;
  max-width: 450px;
}

.admin-login-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #343a40;
  font-size: 1.8rem;
}

/* 表单样式 */
.admin-form-group {
  margin-bottom: 1.2rem;
}

.admin-form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-size: 0.95rem;
  font-weight: 500;
}

.admin-form-group input,
.admin-form-group select {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s, box-shadow 0.3s;
  background-color: white;
}

.admin-form-group input:focus,
.admin-form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

/* 记住密码样式 */
.admin-remember-me {
  display: flex;
  align-items: center;
  margin-bottom: 1.2rem;
  gap: 0.5rem;
}

.admin-remember-me input[type="checkbox"] {
  width: auto;
  margin: 0;
  accent-color: #007bff;
}

.admin-remember-me label {
  margin: 0;
  font-size: 0.9rem;
  color: #6c757d;
  cursor: pointer;
}

/* 角色选择样式 */
.admin-role-select {
  background-image: url("data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3E%3Cpath fill='none' stroke='%23495057' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='m2 5 6 6 6-6'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  background-size: 16px;
  padding-right: 2rem;
  appearance: none;
}

/* 错误消息样式 */
.admin-error-message {
  color: #dc3545;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

/* 登录按钮样式 */
.admin-login-btn {
  width: 100%;
  padding: 0.9rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  font-weight: 500;
  transition: background-color 0.3s, transform 0.1s;
  margin-bottom: 1rem;
}

.admin-login-btn:hover {
  background-color: #0056b3;
}

.admin-login-btn:active {
  transform: translateY(1px);
}

/* 注册链接样式 */
.admin-register-link {
  text-align: center;
  font-size: 0.9rem;
  color: #6c757d;
  margin-bottom: 0.8rem;
}

.admin-register-link a {
  color: #007bff;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-register-link a:hover {
  color: #0056b3;
  text-decoration: underline;
}

/* 返回主站链接样式 */
.admin-back-link {
  text-align: center;
  font-size: 0.9rem;
}

.admin-back-link a {
  color: #6c757d;
  text-decoration: none;
  transition: color 0.3s;
}

.admin-back-link a:hover {
  color: #495057;
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .admin-login-form-wrapper {
    padding: 1.8rem;
    margin: 1rem;
  }
  
  .admin-login-title {
    font-size: 1.5rem;
    margin-bottom: 1.5rem;
  }
}
</style>