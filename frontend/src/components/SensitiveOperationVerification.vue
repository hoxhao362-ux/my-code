<script setup>
import { ref, computed, onUnmounted, watch } from 'vue'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  actionType: {
    type: String,
    default: 'Sensitive Operation'
  },
  target: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'verify-success'])

const userStore = useUserStore()
const toastStore = useToastStore()
<<<<<<< HEAD
const platformName = computed(() => userStore.basicConfig?.platformName || 'Journal Platform')
=======
const platformName = computed(() => userStore.basicConfig?.platformName || 'Peerex Peer')
>>>>>>> e47b4028170e280d7071481fe2e065479b0866ea

// State
const step = ref(1) // 1: Send Code, 2: Verify
const verificationCode = ref('')
const countdown = ref(0)
const errorMsg = ref('')
const isLoading = ref(false)
const verificationMethod = ref('sms') // 'sms' or 'email'

let timer = null

// Reset state when visibility changes
watch(() => props.visible, (newVal) => {
  if (newVal) {
    step.value = 1
    verificationCode.value = ''
    errorMsg.value = ''
    isLoading.value = false
    // Don't auto-send, let user choose method
  }
})

const startCountdown = () => {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

const sendCode = () => {
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
    step.value = 2
    startCountdown()
    toastStore.add({ message: `Verification code sent for ${platformName.value}: 123456`, type: 'info' })
  }, 1000)
}

const verifyCode = () => {
  if (!verificationCode.value) {
    errorMsg.value = 'Please enter the verification code'
    return
  }
  
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
    if (verificationCode.value === '123456') {
      emit('verify-success')
      emit('close')
    } else {
      errorMsg.value = 'Invalid verification code'
    }
  }, 800)
}

const close = () => {
  emit('close')
}

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<template>
  <div v-if="visible" class="verification-overlay">
    <div class="verification-modal">
      <div class="modal-header">
        <h3>Security Verification</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-content">
        <div class="security-icon">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#3498db" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
        </div>
        
        <p class="action-desc">
          You are performing a sensitive operation: 
          <strong>{{ actionType }}</strong>
          <span v-if="target"> on <strong>{{ target }}</strong></span>.
        </p>
        
        <p class="instruction">
          For security, please complete the secondary verification.
        </p>

        <div v-if="step === 1" class="step-container">
          <div class="method-selector">
            <label class="radio-label">
              <input type="radio" v-model="verificationMethod" value="sms">
              <span class="radio-custom"></span>
              SMS Verification ({{ userStore.user?.phone?.slice(-4) ? '***' + userStore.user.phone.slice(-4) : 'Linked Phone' }})
            </label>
            <label class="radio-label">
              <input type="radio" v-model="verificationMethod" value="email">
              <span class="radio-custom"></span>
              Email Verification ({{ userStore.user?.email ? userStore.user.email.split('@')[0].slice(0, 2) + '***@' + userStore.user.email.split('@')[1] : 'Linked Email' }})
            </label>
          </div>
          
          <button class="btn primary full-width" @click="sendCode" :disabled="isLoading">
            {{ isLoading ? 'Sending...' : 'Send Verification Code' }}
          </button>
        </div>

        <div v-if="step === 2" class="step-container">
          <div class="code-input-container">
            <input 
              type="text" 
              v-model="verificationCode" 
              class="code-input" 
              placeholder="Enter 6-digit code"
              maxlength="6"
              @keyup.enter="verifyCode"
            >
          </div>
          
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
          
          <div class="resend-container">
            <span v-if="countdown > 0" class="countdown">Resend in {{ countdown }}s</span>
            <button v-else class="btn-link" @click="sendCode">Resend Code</button>
          </div>

          <button class="btn primary full-width" @click="verifyCode" :disabled="isLoading">
            {{ isLoading ? 'Verifying...' : 'Verify & Proceed' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.verification-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000; /* Higher than normal modals */
  backdrop-filter: blur(2px);
}

.verification-modal {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  animation: slideUp 0.3s ease;
  overflow: hidden;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
  background-color: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.modal-content {
  padding: 2rem 1.5rem;
  text-align: center;
}

.security-icon {
  margin-bottom: 1.5rem;
  display: inline-flex;
  padding: 1rem;
  background-color: #ebf5fb;
  border-radius: 50%;
}

.action-desc {
  font-size: 1rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.instruction {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.method-selector {
  text-align: left;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.95rem;
  color: #555;
}

.radio-label input {
  margin-right: 0.5rem;
}

.step-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.code-input-container {
  margin-bottom: 0.5rem;
}

.code-input {
  width: 100%;
  padding: 0.8rem;
  font-size: 1.2rem;
  text-align: center;
  letter-spacing: 4px;
  border: 1px solid #ddd;
  border-radius: 4px;
  transition: border-color 0.3s;
}

.code-input:focus {
  border-color: #3498db;
  outline: none;
}

.error-msg {
  color: #e74c3c;
  font-size: 0.85rem;
  margin: -0.5rem 0 0.5rem;
}

.resend-container {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 0.5rem;
}

.btn-link {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}

.btn {
  padding: 0.8rem;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.btn.primary {
  background-color: #3498db;
  color: white;
}

.btn.primary:hover {
  background-color: #2980b9;
}

.btn.primary:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}

.full-width {
  width: 100%;
}

.countdown {
  color: #999;
}
</style>