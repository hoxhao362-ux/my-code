<script setup>
/**
 * 忘记密码页面 - Peerex Peer
 * 修复严重问题 #6：彻底移除 Mock，对接真实后端 API
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { userApi } from '@/utils/api'
import { encryptPassword } from '@/utils/encryption'
import { useToastStore } from '@/stores/toast'

const router = useRouter()
const toastStore = useToastStore()

// 视图与表单状态
const step = ref(1) // 1: 发送验证码, 2: 验证并设置新密码
const email = ref('')
const code = ref('')
const newPassword = ref('')
const confirmPassword = ref('')

// 防抖与倒计时状态 (修复轻微#1)
const isSending = ref(false)
const isSubmitting = ref(false)
const countdown = ref(0)

// --- 逻辑 1: 请求发送验证码 ---
const handleSendCode = async () => {
  if (isSending.value || countdown.value > 0) return
  if (!email.value) {
    toastStore.add({ message: 'Please enter your academic email.', type: 'warning' })
    return
  }

  isSending.value = true
  try {
    // 调用真实发码 API
    await userApi.sendResetCode({ email: email.value })
    toastStore.add({ message: 'Verification code sent successfully!', type: 'success' })

    // 进入下一步并开启60秒防刷倒计时
    step.value = 2
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) clearInterval(timer)
    }, 1000)
  } catch (error) {
    toastStore.add({
      message: error.response?.data?.message || 'Failed to send verification code.',
      type: 'error'
    })
  } finally {
    isSending.value = false
  }
}

// --- 逻辑 2: 提交重置密码 ---
const handleReset = async () => {
  if (isSubmitting.value) return

  // 基础本地校验
  if (!code.value || !newPassword.value || !confirmPassword.value) {
    toastStore.add({ message: 'Please fill in all required fields.', type: 'warning' })
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    toastStore.add({ message: 'New passwords do not match.', type: 'error' })
    return
  }

  isSubmitting.value = true
  try {
    // 调用加密工具：SHA-256 异步哈希
    const encryptedPw = await encryptPassword(newPassword.value)

    // 调用真实重置 API
    await userApi.resetPasswordWithCode({
      email: email.value,
      code: code.value,
      new_password: encryptedPw
    })

    toastStore.add({ message: 'Password reset successful! Redirecting...', type: 'success' })

    // 延迟 1.5 秒后打回登录页
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (error) {
    toastStore.add({
      message: error.response?.data?.message || 'Reset failed. Please check your verification code.',
      type: 'error'
    })
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>{{ step === 1 ? 'Forgot Password' : 'Set New Password' }}</h2>
        <p class="subtitle">Peerex Peer Academic Submission System</p>
      </div>

      <div v-if="step === 1" class="auth-form">
        <div class="form-group">
          <label>Academic Email Address</label>
          <input
            v-model="email"
            type="email"
            placeholder="Enter your registered email"
            class="form-control"
            @keyup.enter="handleSendCode"
          />
        </div>
        <button class="btn-submit" :disabled="isSending" @click="handleSendCode">
          {{ isSending ? 'Sending...' : 'Send Verification Code' }}
        </button>
      </div>

      <div v-else class="auth-form">
        <div class="form-group">
          <label>Verification Code (Sent to {{ email }})</label>
          <input v-model="code" type="text" class="form-control" placeholder="6-digit code" />
        </div>
        <div class="form-group">
          <label>New Password</label>
          <input v-model="newPassword" type="password" class="form-control" placeholder="At least 8 characters" />
        </div>
        <div class="form-group">
          <label>Confirm New Password</label>
          <input v-model="confirmPassword" type="password" class="form-control" @keyup.enter="handleReset" />
        </div>
        <button class="btn-submit" :disabled="isSubmitting" @click="handleReset">
          {{ isSubmitting ? 'Resetting...' : 'Reset Password' }}
        </button>
        <p class="resend-text" v-if="countdown > 0">Resend code in {{ countdown }}s</p>
        <button v-else class="btn-link" @click="handleSendCode">Resend Code</button>
      </div>

      <div class="auth-footer">
        <router-link to="/login">Back to Login</router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 严格遵循学术风 UI 规范，使用纯净的蓝白配色 */
.auth-container { display: flex; justify-content: center; align-items: center; min-height: 100vh; background-color: #f4f7f9; }
.auth-card { width: 100%; max-width: 420px; background: white; padding: 2.5rem; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.auth-header { text-align: center; margin-bottom: 2rem; }
.auth-header h2 { color: #004d71; margin-bottom: 0.5rem; font-size: 1.5rem; }
.subtitle { color: #666; font-size: 0.85rem; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; font-size: 0.9rem; }
.form-control { width: 100%; padding: 0.75rem; border: 1px solid #d9d9d9; border-radius: 4px; font-size: 0.95rem; box-sizing: border-box; }
.form-control:focus { border-color: #004d71; outline: none; }
.btn-submit { width: 100%; padding: 0.85rem; background-color: #004d71; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 600; transition: opacity 0.2s; font-size: 1rem; }
.btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }
.auth-footer { margin-top: 1.5rem; text-align: center; }
.auth-footer a { color: #004d71; text-decoration: none; font-size: 0.9rem; font-weight: 500; }
.auth-footer a:hover { text-decoration: underline; }
.resend-text { font-size: 0.85rem; color: #999; margin-top: 1rem; text-align: center; }
.btn-link { background: none; border: none; color: #004d71; cursor: pointer; display: block; margin: 1rem auto; font-weight: 500; }
</style>
