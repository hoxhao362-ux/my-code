<script setup>
import { ref, onMounted, onUnmounted, reactive, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
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
  localStorage.setItem('reviewer_application_draft', JSON.stringify(form))
  // showToast('Draft saved successfully.') // Assuming toast component exists or reused
}

const submitApplication = () => {
  // 1. Frontend Validation
  validateField('name')
  validateField('email')
  validateField('orcid')
  validateField('areas')

  if (errors.name || errors.email || errors.orcid || errors.areas) {
    return
  }

  // 2. Mock Backend Validation
  // Simulate backend check: if ORCID is '0000-0000-0000-0000', fail it.
  if (form.orcid === '0000-0000-0000-0000') {
    topError.value = 'This ORCID ID is already associated with another reviewer account'
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  topError.value = ''
  isLoading.value = true

  // Simulate API Call
  setTimeout(() => {
    isLoading.value = false
    
    // Save application data
    localStorage.removeItem('reviewer_application_draft')
    
    // Update user status to 'pending_review' in store
    // We assume user is logged in. If not, we might need to create one or store in session.
    // For this demo, we assume the current user applies.
    if (user.value) {
       // Add 'reviewer_application' to user object or store separate state
       // Updating status to a specific application state
       // But 'status' usually means account status. 
       // Let's use a specific flag in localStorage to track application state for the frontend demo.
       localStorage.setItem('reviewer_application_status', 'pending_review')
       localStorage.setItem('reviewer_application_data', JSON.stringify(form))
    }
    
    showSuccessModal.value = true
  }, 1000)
}

const handleSuccessConfirm = () => {
  showSuccessModal.value = false
  router.push('/reviewer/application-status')
}

onMounted(() => {
  const draft = localStorage.getItem('reviewer_application_draft')
  if (draft) {
    const data = JSON.parse(draft)
    Object.assign(form, data)
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
      <p>Reviewing for The Lancet is a prestigious role that allows you to contribute to the scientific community. As a reviewer, you will:</p>
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
}

.sidebar-info h1 {
  font-size: 20px;
  font-weight: bold;
  color: #333;
  margin-bottom: 24px;
}

.sidebar-info p, .sidebar-info li {
  font-size: 14px;
  color: #333;
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
  padding: 48px;
  background-color: white;
}

.form-container {
  max-width: 600px;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
}

.form-group input:focus {
  border-color: #333; /* Default focus */
}

/* Error Styles */
.error-border {
  border-color: #C93737 !important;
}

.error-text {
  color: #C93737;
  font-size: 12px;
  margin-top: 4px;
}

.actions {
  display: flex;
  gap: 16px;
  margin-top: 32px;
}

.btn-save {
  padding: 10px 24px;
  background-color: #E5E5E5;
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-submit {
  padding: 10px 24px;
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-submit:hover {
  background-color: #A02C2C;
}

.btn-submit:disabled {
  background-color: #fab1b1;
  cursor: not-allowed;
}

.privacy-note {
  font-size: 12px;
  color: #999;
  margin-top: 16px;
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
  padding: 32px;
  border-radius: 8px;
  width: 450px;
  border: 1px solid #E5E5E5;
  text-align: center;
}

.modal-content h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  margin-top: 0;
}

.modal-content p {
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.modal-actions-center {
  display: flex;
  justify-content: center;
}

.btn-confirm {
  background: #C93737;
  color: white;
  border: none;
  padding: 10px 32px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
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
  }
  .form-area {
    margin-left: 0;
    width: 100%;
  }
}
</style>
