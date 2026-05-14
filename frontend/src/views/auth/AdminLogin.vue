<template>
  <div class="admin-login-wrapper">
    <div class="login-card">
      <h2>{{ t('auth.adminLogin.title') || 'Administrative Portal' }}</h2>
      <p class="subtitle">Secure access for Editors and Administrators</p>
      
      <form @submit.prevent="handleAdminLogin">
        <div class="form-group">
          <label>Admin Username</label>
          <input v-model="form.username" type="text" placeholder="Enter administrator ID" required />
        </div>
        
        <div class="form-group">
          <label>Security Password</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required />
        </div>

        <div class="form-options">
          <label class="checkbox-container">
            <input type="checkbox" v-model="form.is_remember" />
            <span class="checkmark"></span>
            {{ t('auth.login.rememberMe') || 'Keep me logged in' }}
          </label>
        </div>

        <div v-if="error" class="error-alert">
          <i class="icon-warning"></i> {{ error }}
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          {{ loading ? 'Verifying Credentials...' : 'Access Dashboard' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useI18n } from 'vue-i18n'
import { encryptPassword } from '@/utils/encryption'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const error = ref('')
const form = reactive({
  username: '',
  password: '',
  is_remember: false
})

const handleAdminLogin = async () => {
  loading.value = true
  error.value = ''

  try {
    const hashedPassword = await encryptPassword(form.password)
    
    await userStore.adminLogin({
      username: form.username,
      password: hashedPassword,
      is_remember: form.is_remember
    })

    // 成功后跳转管理员控制台
    router.push('/admin/dashboard')
  } catch (err) {
    const status = err.response?.status
    const detail = err.response?.data?.detail

    if (status === 403) {
      error.value = detail || 'Access Denied: This account does not have administrative privileges.'
    } else if (status === 404) {
      error.value = detail || 'Account not found. Please check your username.'
    } else if (status === 401) {
      error.value = 'Invalid password. Please try again.'
    } else {
      error.value = 'A connection error occurred. Please verify your network.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.admin-login-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 420px;
  padding: 40px;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
}

.login-card h2 {
  margin: 0 0 8px;
  font-size: 1.75rem;
  color: #1a1a2e;
  text-align: center;
}

.subtitle {
  margin: 0 0 32px;
  font-size: 0.9rem;
  color: #6b7280;
  text-align: center;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  font-size: 0.9rem;
  color: #374151;
}

.form-group input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.form-group input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.form-options {
  margin-bottom: 24px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  color: #4b5563;
  cursor: pointer;
}

.checkbox-container input[type="checkbox"] {
  width: 16px;
  height: 16px;
  accent-color: #6366f1;
}

.error-alert {
  padding: 12px 16px;
  margin-bottom: 20px;
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
  font-size: 0.9rem;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background-color: #6366f1;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background-color: #4f46e5;
}

.btn-primary:disabled {
  background-color: #a5b4fc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .login-card {
    padding: 24px;
    margin: 16px;
  }
}
</style>
