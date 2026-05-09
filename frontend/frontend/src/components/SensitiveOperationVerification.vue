<script setup>
import { ref, computed, onUnmounted, watch, onMounted } from 'vue'
import { useUserStore } from '../stores/user'
import { useToastStore } from '../stores/toast'
import { captchaApi } from '../utils/api'

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
const platformName = computed(() => userStore.basicConfig?.platformName || 'Peerex Peer')

// State
const verificationCode = ref('')
const captchaImage = ref('')
const captchaReqId = ref('')
const errorMsg = ref('')
const isLoading = ref(false)

// 获取验证码图片
const fetchCaptcha = async () => {
  try {
    const res = await captchaApi.getImage()
    const data = res.data || res
    captchaImage.value = data.image || ''
    captchaReqId.value = data.req_id || ''
    verificationCode.value = ''
    errorMsg.value = ''
  } catch (error) {
    console.error('获取验证码失败:', error)
    toastStore.add({ message: 'Failed to load captcha', type: 'error' })
  }
}

onMounted(() => {
  if (props.visible) {
    fetchCaptcha()
  }
})

watch(() => props.visible, (newVal) => {
  if (newVal) {
    fetchCaptcha()
  }
})

const verifyCode = async () => {
  if (!verificationCode.value) {
    errorMsg.value = 'Please enter the verification code'
    return
  }
  
  if (!captchaReqId.value) {
    errorMsg.value = 'Captcha session expired. Please refresh.'
    await fetchCaptcha()
    return
  }
  
  isLoading.value = true
  try {
    await captchaApi.verify({
      req_id: captchaReqId.value,
      code: verificationCode.value
    })
    
    // 验证成功
    emit('verify-success')
    emit('close')
  } catch (error) {
    const detail = error.response?.data?.detail || error.message || 'Invalid verification code'
    errorMsg.value = detail
    // 验证失败后刷新验证码（一次性消耗）
    await fetchCaptcha()
  } finally {
    isLoading.value = false
  }
}

const close = () => {
  emit('close')
}

onUnmounted(() => {
  // Cleanup if needed
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
          For security, please complete the captcha verification.
        </p>

        <div class="step-container">
          <!-- 验证码图片 -->
          <div class="captcha-container">
            <img 
              v-if="captchaImage" 
              :src="captchaImage" 
              class="captcha-image"
              alt="Captcha"
              @click="fetchCaptcha"
            />
            <div v-else class="captcha-placeholder" @click="fetchCaptcha">
              Click to load captcha
            </div>
            <button class="refresh-btn" @click="fetchCaptcha" :disabled="isLoading">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"></polyline>
                <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"></path>
              </svg>
            </button>
          </div>
          
          <input 
            type="text" 
            v-model="verificationCode" 
            class="code-input" 
            placeholder="Enter captcha code"
            maxlength="6"
            @keyup.enter="verifyCode"
          >
          
          <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

          <div class="btn-group">
            <button class="btn secondary" @click="close">
              Cancel
            </button>
            <button class="btn primary" @click="verifyCode" :disabled="isLoading || !verificationCode">
              {{ isLoading ? 'Verifying...' : 'Verify & Proceed' }}
            </button>
          </div>
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

/* Captcha Styles */
.captcha-container {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  margin-bottom: 1rem;
}

.captcha-image {
  border-radius: 4px;
  border: 1px solid #ddd;
  cursor: pointer;
  max-width: 180px;
  height: 50px;
  object-fit: contain;
}

.captcha-placeholder {
  padding: 0.8rem 1.5rem;
  background: #f5f5f5;
  border: 1px dashed #ddd;
  border-radius: 4px;
  cursor: pointer;
  color: #999;
  font-size: 0.85rem;
}

.refresh-btn {
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #666;
}

.refresh-btn:hover:not(:disabled) {
  background: #f5f5f5;
}

.refresh-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.btn-group {
  display: flex;
  gap: 0.8rem;
}

.btn.secondary {
  background: #f5f5f5;
  color: #666;
  flex: 1;
}

.btn.secondary:hover {
  background: #eee;
}

.btn.primary {
  flex: 2;
}

.code-input {
  margin-bottom: 0.5rem;
}
</style>