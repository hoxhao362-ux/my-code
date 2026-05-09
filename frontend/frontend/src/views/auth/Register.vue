<template>
  <div class="register-container">
    <h2>{{ t('auth.register.title') || 'Create Account' }}</h2>
    <form @submit.prevent="handleRegister">
      <div class="form-item">
        <label>Username</label>
        <input v-model="registerForm.username" type="text" placeholder="Choose a unique username" />
      </div>

      <div class="form-item">
        <label>Email Address</label>
        <input v-model="registerForm.email" type="email" placeholder="example@domain.com" />
      </div>

      <div class="form-item">
        <label>Password</label>
        <input v-model="registerForm.password" type="password" placeholder="Create a strong password" />
      </div>

      <div class="form-item">
        <label>Confirm Password</label>
        <input v-model="registerForm.confirmPassword" type="password" placeholder="Repeat your password" />
      </div>

      <div class="form-item">
        <label>Invitation Code (Optional)</label>
        <input
          v-model="registerForm.invite_code"
          @blur="handleInviteCodeBlur"
          type="text"
          placeholder="Enter code for specialized roles"
        />
        <small :class="['hint', inviteCodeValid ? 'success' : 'error']">
          {{ inviteCodeMessage }}
        </small>
      </div>

      <div v-if="errorMessage" class="error-msg">{{ errorMessage }}</div>

      <button type="submit" :disabled="loading">
        {{ loading ? 'Registering...' : 'Sign Up' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { userApi, adminApi } from '@/utils/api'
import { useUserStore } from '@/stores/user'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  invite_code: ''
})

const loading = ref(false)
const errorMessage = ref('')
const inviteCodeMessage = ref('')
const inviteCodeValid = ref(true)

const handleInviteCodeBlur = async () => {
  if (!registerForm.invite_code) {
    inviteCodeMessage.value = ''
    inviteCodeValid.value = true
    return
  }
  
  try {
    const res = await adminApi.validateInvitationCode(registerForm.invite_code)
    const data = res.data || res
    if (data.valid) {
      inviteCodeMessage.value = `Code valid. Assigned Role: ${data.role}`
      inviteCodeValid.value = true
    } else {
      inviteCodeMessage.value = 'Invalid or expired invitation code.'
      inviteCodeValid.value = false
    }
  } catch (error) {
    inviteCodeMessage.value = 'Failed to verify invitation code.'
    inviteCodeValid.value = false
  }
}

const handleRegister = async () => {
  if (registerForm.password !== registerForm.confirmPassword) {
    errorMessage.value = 'Passwords do not match.'
    return
  }
  if (!inviteCodeValid.value) {
    errorMessage.value = 'Please provide a valid invitation code.'
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const res = await userApi.register({
      username: registerForm.username,
      email: registerForm.email,
      password: registerForm.password,
      invite_code: registerForm.invite_code || undefined
    })
    
    const responseData = res.data || res
    if (responseData.token) {
      userStore.token = responseData.token
      localStorage.setItem('token', responseData.token)
      await userStore.fetchUserInfo()
      
      // ==== 统一分流逻辑 ====
      const role = userStore.currentRole
      if (role === 'admin') {
        router.push('/admin/dashboard')
      } else if (['editor', 'associate_editor', 'ea_ae'].includes(role)) {
        router.push('/editor/dashboard')
      } else if (role === 'reviewer') {
        router.push('/reviewer/dashboard')
      } else {
        router.push('/author/dashboard')
      }
    } else {
      router.push('/login')
    }
  } catch (error) {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    if (status === 400) {
      errorMessage.value = detail || 'Registration failed. Please check your details.'
    } else if (status === 429) {
      errorMessage.value = 'Too many requests. Please try again later.'
    } else {
      errorMessage.value = 'An internal server error occurred.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  max-width: 480px;
  margin: 0 auto;
  padding: 40px 20px;
}

.register-container h2 {
  margin-bottom: 24px;
  text-align: center;
  color: #1a1a1a;
}

form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-item label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #333;
}

.form-item input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
}

.form-item input:focus {
  outline: none;
  border-color: #4a90d9;
  box-shadow: 0 0 0 2px rgba(74, 144, 217, 0.2);
}

.form-item small.hint {
  display: block;
  margin-top: 4px;
  font-size: 12px;
}

.form-item small.hint.success {
  color: #27ae60;
}

.form-item small.hint.error {
  color: #e74c3c;
}

.error-msg {
  color: #e74c3c;
  font-size: 14px;
  text-align: center;
}

button[type="submit"] {
  padding: 12px;
  background-color: #4a90d9;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

button[type="submit"]:hover:not(:disabled) {
  background-color: #357abd;
}

button[type="submit"]:disabled {
  background-color: #a0a0a0;
  cursor: not-allowed;
}
</style>
