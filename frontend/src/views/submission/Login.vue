<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { useI18n } from '../../composables/useI18n'

const router = useRouter()
const userStore = useUserStore()
const toastStore = useToastStore()
const { t } = useI18n()

const username = ref('')
const password = ref('')
const errorMessage = ref('')

const handleLogin = async (role) => {
  if (!username.value || !password.value) {
    errorMessage.value = t('submission.login.error.required')
    return
  }

  try {
    // Attempt login with specific role for Submission Module
    await userStore.loginSubmission({
      username: username.value,
      password: password.value,
      role: role
    })
    
    // 登录成功后根据角色跳转到对应仪表盘
    if (role === 'author') {
      // Author logs in to submit, go to submission process directly
      router.push('/submission/author/submit')
    } else if (role === 'reviewer') {
      router.push('/admin/audit-dashboard')
    } else if (role === 'editor' || role === 'admin') {
      router.push('/editor/dashboard')
    } else {
      router.push('/submission')
    }
  } catch (error) {
    // Show specific error from store (e.g. password mismatch, lockout)
    errorMessage.value = error.message || t('submission.login.error.failed')
  }
}

const handleOrcidLogin = () => {
  toastStore.add({ message: 'ORCID Login Simulation: Authenticated successfully.', type: 'success' })
}
</script>

<template>
  <div class="submission-login-container">
    <div class="login-box">
      <h2 class="login-title">{{ t('submission.login.title') }}</h2>
      
      <div class="form-group">
        <label>{{ t('submission.login.username') }}</label>
        <input v-model="username" type="text" :placeholder="t('submission.login.placeholder.username')" />
      </div>

      <div class="form-group">
        <label>{{ t('submission.login.password') }}</label>
        <input v-model="password" type="password" :placeholder="t('submission.login.placeholder.password')" />
      </div>

      <p v-if="errorMessage" class="error-msg">{{ errorMessage }}</p>

      <div class="role-buttons">
        <button class="btn-role author" @click="handleLogin('author')">
          {{ t('submission.login.btn.author') }}
        </button>
        <button class="btn-role reviewer" @click="handleLogin('reviewer')">
          {{ t('submission.login.btn.reviewer') }}
        </button>
        <button class="btn-role editor" @click="handleLogin('editor')">
          {{ t('submission.login.btn.editor') }}
        </button>
      </div>

      <div class="orcid-section">
        <p class="orcid-text">{{ t('submission.login.orcid.label') }}</p>
        <button class="btn-orcid" @click="handleOrcidLogin">
          <span class="orcid-icon">ID</span> 
          {{ t('submission.login.orcid.btn') }}
        </button>
        <a href="#" class="orcid-help">{{ t('submission.login.orcid.help') }}</a>
      </div>

      <div class="login-footer">
        <a href="#">{{ t('submission.login.link.sendDetails') }}</a>
        <span class="divider">|</span>
        <a href="#" @click.prevent="$emit('toggle-register')">{{ t('submission.login.link.register') }}</a>
        <span class="divider">|</span>
        <a href="#">{{ t('submission.login.link.help') }}</a>
      </div>
      
      <div class="orcid-info">
        <p>{{ t('submission.login.orcid.info') }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.submission-login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 70px); /* Adjust for header height */
  background-color: #f0f2f5;
  font-family: Arial, sans-serif;
  padding: 2rem;
}

.login-box {
  background: white;
  padding: 2.5rem;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  width: 450px;
  text-align: center;
}

.login-title {
  margin-bottom: 1.5rem;
  color: #333;
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  border-bottom: 2px solid #eee;
  padding-bottom: 1rem;
}

.form-group {
  margin-bottom: 1rem;
  text-align: left;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  font-size: 0.9rem;
  color: #555;
}

.form-group input {
  width: 100%;
  padding: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.error-msg {
  color: #d9534f;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.role-buttons {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin: 1.5rem 0;
}

.btn-role {
  padding: 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.3s;
  color: white;
}

.btn-role.author { background-color: #3498db; }
.btn-role.author:hover { background-color: #2980b9; }

.btn-role.reviewer { background-color: #e67e22; }
.btn-role.reviewer:hover { background-color: #d35400; }

.btn-role.editor { background-color: #2c3e50; }
.btn-role.editor:hover { background-color: #1a252f; }

.orcid-section {
  margin-top: 2rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
}

.orcid-text {
  color: #666;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.btn-orcid {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #a6ce39;
  color: white;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 4px;
  font-weight: bold;
  cursor: pointer;
  text-decoration: none;
}

.orcid-icon {
  background: white;
  color: #a6ce39;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin-right: 8px;
  font-size: 12px;
  font-weight: bold;
}

.orcid-help {
  display: block;
  margin-top: 0.5rem;
  color: #3498db;
  font-size: 0.85rem;
  text-decoration: none;
}

.login-footer {
  margin-top: 2rem;
  font-size: 0.85rem;
}

.login-footer a {
  color: #666;
  text-decoration: none;
}

.login-footer a:hover {
  text-decoration: underline;
}

.divider {
  margin: 0 0.5rem;
  color: #ccc;
}

.orcid-info {
  margin-top: 1rem;
  font-size: 0.8rem;
  color: #999;
  line-height: 1.4;
}
</style>