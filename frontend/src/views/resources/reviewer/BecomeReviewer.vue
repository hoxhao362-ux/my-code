<script setup>
import { ref, onMounted, onUnmounted, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const toastStore = useToastStore()
const user = computed(() => userStore.user)

const router = useRouter()
const form = reactive({
  name: '',
  email: '',
  orcid: '',
  areas: ''
})
const errors = reactive({
  name: '',
  email: '',
  orcid: '',
  areas: ''
})
const topError = ref('')
const showSuccessModal = ref(false)
const isLoading = ref(false)

const validateField = (field) => {
  errors[field] = ''
  const val = form[field] ? form[field].trim() : ''

  if (field === 'name') {
    if (!val) {
      errors.name = 'Full Name is required'
    } else if (val.length < 2 || val.length > 50) {
      errors.name = 'Full Name must be 2-50 characters'
    } else if (!/^[\u4e00-\u9fa5a-zA-Z\s\.]+$/.test(val)) {
      errors.name = 'Full Name can only contain letters, spaces, and dots'
    }
  }

  if (field === 'email') {
    if (!val) {
      errors.email = 'Email Address is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)) {
      errors.email = 'Email Address format is invalid'
    }
  }

  if (field === 'orcid') {
    if (!val) {
      errors.orcid = 'ORCID ID is required'
    } else if (!/^\d{4}-\d{4}-\d{4}-(\d{3}X|\d{4})$/.test(val)) {
      errors.orcid = 'ORCID ID format is invalid (e.g., 0000-0000-0000-0000)'
    }
  }

  if (field === 'areas') {
    if (!val) {
      errors.areas = 'Research Areas are required'
    }
  }
}

const saveDraft = () => {
  userStore.saveReviewerApplicationDraft(form)
  toastStore.success('Draft saved successfully.')
}

const submitApplication = async () => {
  // 1. Frontend Validation
  validateField('name')
  validateField('email')
  validateField('orcid')
  validateField('areas')

  if (errors.name || errors.email || errors.orcid || errors.areas) {
    toastStore.error('Please fix the errors in the form.')
    return
  }

  // 2. Mock Backend Validation
  // Simulate backend check: if ORCID is '0000-0000-0000-0000', fail it.
  if (form.orcid === '0000-0000-0000-0000') {
    topError.value = 'This ORCID ID is already associated with another reviewer account'
    toastStore.error(topError.value)
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  topError.value = ''
  isLoading.value = true

  try {
    await userStore.submitReviewerApplication(form)
    isLoading.value = false
    showSuccessModal.value = true
  } catch (error) {
    isLoading.value = false
    toastStore.error('Submission failed. Please try again.')
    console.error(error)
  }
}

const handleSuccessConfirm = () => {
  showSuccessModal.value = false
  // 提交成功后：
  // 按钮变为不可点击状态，文字改为已提交。
  // 页面显示清晰提示：Your reviewer application has been submitted and is under review.
  // 实际上跳转到 Application Status 页面是更好的体验，因为那里有完整状态展示。
  // 根据需求文档： "保留查看申请、刷新状态功能，页面保持正常交互，不冻结。" -> ApplicationStatus 页面符合要求。
  router.push('/reviewer/application-status')
}

  onMounted(() => {
    // Check if already approved or pending
    const status = userStore.reviewerApplicationStatus
    if (status === 'approved' || status === 'pending_review') {
      // If user is reviewer or already applied, redirect to status page
      if (status === 'approved') {
        toastStore.info('You are already a reviewer.')
        router.push('/reviewer/application-status')
        return
      }
      if (status === 'pending_review') {
        router.push('/reviewer/application-status')
        return
      }
    }
    
    // Virtual Account Check: If user role is already reviewer, skip application
    if (userStore.user?.role === 'reviewer') {
       toastStore.info('You are already a reviewer.')
       router.push('/reviewer/application-status')
       return
    }

    // Load draft
    const draft = userStore.reviewerApplication.draft
    if (draft) {
      Object.assign(form, draft)
      toastStore.info('Draft loaded.')
    }
  })
</script>

<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-reviewer-become'"
      :logout="userStore.logout"
    />
    
    <!-- Top Error Banner -->
    <div v-if="topError" class="top-error-banner">
      {{ topError }}
    </div>

    <div class="sidebar-info">
      <h1>Become a Reviewer</h1>
      <p>Reviewing for the Journal Submission Platform is a prestigious role that allows you to contribute to the scientific community. As a reviewer, you will:</p>
      <ul>
        <li>Stay updated with the latest research in your field.</li>
        <li>Gain recognition for your service (Publons/Web of Science).</li>
        <li>Influence the quality of published research.</li>
      </ul>
      <p>
        <router-link to="/resources/reviewer/guidelines" class="link-brand">View Reviewer Guidelines</router-link>
      </p>
    </div>

    <div class="form-area">
      <div class="form-container">
        <div class="form-group">
          <label>Full Name</label>
          <input 
            type="text" 
            v-model="form.name" 
            :class="{ 'error-border': errors.name }"
            @blur="validateField('name')"
          />
          <div v-if="errors.name" class="error-text">{{ errors.name }}</div>
        </div>
        <div class="form-group">
          <label>Email Address</label>
          <input 
            type="email" 
            v-model="form.email" 
            :class="{ 'error-border': errors.email }"
             @blur="validateField('email')"
          />
          <div v-if="errors.email" class="error-text">{{ errors.email }}</div>
        </div>
        <div class="form-group">
          <label>ORCID ID</label>
          <input 
            type="text" 
            v-model="form.orcid" 
            placeholder="0000-0000-0000-0000" 
            :class="{ 'error-border': errors.orcid }"
             @blur="validateField('orcid')"
          />
          <div v-if="errors.orcid" class="error-text">{{ errors.orcid }}</div>
        </div>
        <div class="form-group">
          <label>Research Areas / Keywords</label>
          <input 
            type="text" 
            v-model="form.areas" 
            placeholder="e.g., Cardiology, Public Health, Epidemiology" 
            :class="{ 'error-border': errors.areas }"
             @blur="validateField('areas')"
          />
          <div v-if="errors.areas" class="error-text">{{ errors.areas }}</div>
        </div>
        
        <div class="actions">
          <button class="btn-save" @click="saveDraft">Save Draft</button>
          <button class="btn-submit" @click="submitApplication" :disabled="isLoading">
            <span v-if="isLoading" class="spinner"></span>
            <span v-if="isLoading">Submitting...</span>
            <span v-else>Submit Application</span>
          </button>
        </div>
        <p class="privacy-note">Your data will be processed in accordance with our Privacy Policy.</p>
      </div>
    </div>

    <!-- Success Modal -->
    <div v-if="showSuccessModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Application Submitted</h3>
        <p>Thank you for your application. The review process typically takes 7-10 business days. You will be notified via email once a decision has been made.</p>
        <div class="modal-actions-center">
          <button class="btn-confirm" @click="handleSuccessConfirm">OK</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Reuse existing styles plus new error styles */
.page-container {
  display: flex;
  min-height: 100vh;
  padding-top: 0;
  margin-top: 80px;
  position: relative;
  background-color: #f9f9f9;
}

.top-error-banner {
  position: fixed;
  top: 80px; /* Below nav */
  left: 0;
  right: 0;
  background-color: #FDEDED;
  color: #C93737;
  padding: 12px 24px;
  text-align: center;
  border-bottom: 1px solid #C93737;
  z-index: 999;
}

.sidebar-info {
  width: 30%;
  background-color: #F5F5F5;
  padding: 48px 32px;
  position: fixed;
  height: calc(100vh - 80px);
  top: 80px;
  left: 0;
  border-right: 1px solid #e0e0e0;
}

.sidebar-info h1 {
  font-size: 24px;
  font-weight: 600;
  color: #333;
  margin-bottom: 24px;
  font-family: 'Segoe UI', sans-serif; /* Journal Platform style font preference */
}

.sidebar-info p, .sidebar-info li {
  font-size: 15px;
  color: #4a4a4a;
  line-height: 1.6;
  margin-bottom: 12px;
}

.sidebar-info ul {
  padding-left: 20px;
  margin-bottom: 24px;
}

.link-brand {
  color: #C93737;
  text-decoration: none;
  font-weight: bold;
}

.form-area {
  margin-left: 30%;
  width: 70%;
  padding: 60px 80px;
  background-color: white;
}

.form-container {
  max-width: 700px;
}

.form-group {
  margin-bottom: 28px;
}

.form-group label {
  display: block;
  font-size: 15px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px; /* Standard corners like Journal Platform */
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #0056B3; /* Journal Platform Blue */
}

/* Error Styles */
.error-border {
  border-color: #C93737 !important;
}

.error-text {
  color: #C93737;
  font-size: 13px;
  margin-top: 6px;
}

.actions {
  display: flex;
  gap: 16px;
  margin-top: 40px;
  align-items: center;
}

.btn-save {
  padding: 12px 28px;
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #ccc;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  transition: background-color 0.2s;
}

.btn-save:hover {
  background-color: #e0e0e0;
}

.btn-submit {
  padding: 12px 28px;
  background-color: #0056B3; /* Journal Platform Blue */
  color: white;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.btn-submit:hover {
  background-color: #00447a;
}

.btn-submit:disabled {
  background-color: #8ab6d6;
  cursor: not-allowed;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: #fff;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.privacy-note {
  font-size: 13px;
  color: #777;
  margin-top: 24px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  padding: 40px;
  border-radius: 4px;
  width: 500px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
  text-align: center;
}

.modal-content h3 {
  font-size: 22px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  margin-top: 0;
}

.modal-content p {
  color: #555;
  margin-bottom: 30px;
  line-height: 1.6;
  font-size: 15px;
}

.modal-actions-center {
  display: flex;
  justify-content: center;
}

.btn-confirm {
  background: #005696;
  color: white;
  border: none;
  padding: 12px 36px;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 600;
  font-size: 15px;
}

@media (max-width: 768px) {
  .page-container {
    flex-direction: column;
  }
  .sidebar-info {
    width: 100%;
    position: relative;
    height: auto;
    top: 0;
    border-right: none;
    border-bottom: 1px solid #e0e0e0;
  }
  .form-area {
    margin-left: 0;
    width: 100%;
    padding: 32px;
  }
}
</style>
