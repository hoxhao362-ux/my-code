<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const toastStore = useToastStore()

const PLATFORM_NAME = computed(() => userStore.basicConfig.platformName || 'Peerex Peer')
const BRAND_RED = '#C93737'

// State
const isLoading = ref(false)
const isSubmitted = ref(false)
const isExpired = ref(false)

// Form Data
const form = reactive({
  name: '',
  title: '',
  affiliation: '',
  email: '',
  field: '',
  bio: '',
  qualificationFile: null, // New: Proof of qualification
  hasConflict: null, // boolean
  conflictDetail: '',
  agreed: false
})

// Mock Data
const fields = [
  'Medicine', 'Biology', 'Public Health', 'Clinical Medicine', 
  'Oncology', 'Cardiology', 'Neurology', 'Immunology'
]

const titles = ['Dr.', 'Prof.', 'Mr.', 'Ms.']

// Init
onMounted(() => {
  // Simulate checking token validity
  const token = route.query.token
  if (!token) {
    // For demo purposes, we allow without token or show error
    // isExpired.value = true
  }
  
  // Pre-fill email from query or mock
  form.email = route.query.email || ''
})

const handleFileUpload = (e) => {
  const file = e.target.files[0]
  if (file) {
    if (file.size > 5 * 1024 * 1024) {
      toastStore.add({ message: 'File size exceeds 5MB limit.', type: 'warning' })
      return
    }
    form.qualificationFile = file
  }
}

const handleSubmit = async () => {
  if (!form.agreed) return
  if (form.hasConflict && !form.conflictDetail) {
    toastStore.add({ message: 'Please provide details for the conflict of interest.', type: 'warning' })
    return
  }
  
  if (!form.qualificationFile) {
    toastStore.add({ message: 'Please upload proof of qualification.', type: 'warning' })
    return
  }

  isLoading.value = true
  
  // Register User
  const newUser = {
    username: form.email.split('@')[0].replace(/[^a-zA-Z0-9]/g, ''),
    email: form.email,
    name: `${form.title} ${form.name}`,
    role: 'reviewer',
    affiliation: form.affiliation,
    field: form.field,
    bio: form.bio,
    status: 'active',
    qualificationProof: form.qualificationFile ? 'file_uploaded' : null
  }
  
  const registeredUser = userStore.addUser(newUser)
  
  // Update Recommendation Status
  const recommendationId = route.query.recommendationId
  if (recommendationId) {
    const reviewer = userStore.recommendedReviewers.find(r => r.id == recommendationId)
    if (reviewer) {
       userStore.updateRecommendedReviewer({
         ...reviewer,
         status: 'accepted',
         userId: registeredUser.id,
         reviewerName: newUser.name, // Update name if they changed it
         reviewedAt: new Date().toISOString(),
         reviewedBy: 'system (registration)'
       })
    }
  }
  
  // Simulate API call delay
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  isLoading.value = false
  isSubmitted.value = true
  
  // Auto redirect to mock review page after 3 seconds
  setTimeout(() => {
    // Log them in automatically for demo
    userStore.loginSubmission({ username: newUser.username, role: 'reviewer' })
    router.push('/reviewer/dashboard') 
  }, 3000)
}

</script>

<template>
  <div class="registration-container">
    <div class="registration-card">
      
      <!-- Header -->
      <header class="header">
        <h1 class="platform-name">
          <span class="brand-red">{{ PLATFORM_NAME.charAt(0) }}</span>{{ PLATFORM_NAME.slice(1) }}
        </h1>
        <p class="subtitle">Temporary Reviewer Registration</p>
      </header>
      
      <!-- Expired State -->
      <div v-if="isExpired" class="expired-state">
        <div class="icon">⚠️</div>
        <h2>Invitation Expired</h2>
        <p>This invitation link has expired (valid for 7 days). Please contact the editorial office if you wish to proceed.</p>
      </div>
      
      <!-- Success State -->
      <div v-else-if="isSubmitted" class="success-state">
        <div class="icon">✅</div>
        <h2>Registration Successful</h2>
        <p>You have successfully registered as a temporary reviewer.</p>
        <p class="redirect-text">Redirecting to the review page...</p>
      </div>

      <!-- Registration Form -->
      <form v-else @submit.prevent="handleSubmit" class="registration-form">
        
        <div class="form-group">
          <label class="required">Full Name (Academic)</label>
          <div class="name-input-group">
            <select v-model="form.title" class="select-input title-select" required>
              <option value="" disabled>Title</option>
              <option v-for="t in titles" :key="t" :value="t">{{ t }}</option>
            </select>
            <input v-model="form.name" type="text" class="input-text name-input" placeholder="e.g. John Doe" required>
          </div>
        </div>

        <div class="form-group">
          <label class="required">Affiliation</label>
          <input v-model="form.affiliation" type="text" class="input-text" placeholder="University / Research Institute / Hospital" required>
        </div>

        <div class="form-group">
          <label class="required">Email Address</label>
          <input v-model="form.email" type="email" class="input-text disabled" readonly required>
          <p class="hint">Email is pre-filled from the invitation and cannot be changed.</p>
        </div>

        <div class="form-group">
          <label class="required">Research Field</label>
          <select v-model="form.field" class="select-input" required>
            <option value="" disabled>Select Research Field</option>
            <option v-for="f in fields" :key="f" :value="f">{{ f }}</option>
          </select>
        </div>

        <div class="form-group">
          <label class="required">Brief Biography / Research Direction</label>
          <textarea v-model="form.bio" rows="3" class="textarea-input" placeholder="Please describe your research direction and expertise related to this manuscript..." required></textarea>
        </div>

        <!-- Qualification Verification (New Feature) -->
        <div class="form-group highlight-box">
          <label class="required">Reviewer Qualification Verification</label>
          <p class="hint-text">To ensure the integrity of our peer review process, please upload a proof of your professional title or institutional affiliation (e.g., ID card, faculty profile screenshot, or official letter).</p>
          
          <div class="file-upload-container">
            <input type="file" id="qualificationFile" @change="handleFileUpload" accept=".pdf,.jpg,.png,.jpeg" class="file-input" required>
            <label for="qualificationFile" class="file-label">
              <span v-if="form.qualificationFile">📄 {{ form.qualificationFile.name }}</span>
              <span v-else>📁 Click to Upload Proof Document (PDF/Image)</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label class="required">Conflict of Interest Declaration</label>
          <div class="radio-group">
            <label class="radio-label">
              <input type="radio" v-model="form.hasConflict" :value="false" required>
              No, I declare no conflict of interest with this manuscript.
            </label>
            <label class="radio-label">
              <input type="radio" v-model="form.hasConflict" :value="true">
              Yes, I have a potential conflict of interest.
            </label>
          </div>
        </div>

        <div v-if="form.hasConflict" class="form-group indent">
          <label class="required">Conflict Details</label>
          <textarea v-model="form.conflictDetail" rows="3" class="textarea-input" placeholder="Please describe the nature of the conflict..." required></textarea>
        </div>

        <div class="form-group checkbox-group">
          <label class="checkbox-label">
            <input type="checkbox" v-model="form.agreed" required>
            I have read and agree to the <a href="#" class="link">Peer Review Guidelines</a> and <a href="#" class="link">Privacy Policy</a>.
          </label>
        </div>

        <div class="form-actions">
          <button type="submit" class="submit-btn" :disabled="isLoading">
            <span v-if="isLoading">Registering...</span>
            <span v-else>Complete Registration & Start Review</span>
          </button>
        </div>

        <div class="footer-note">
          <p>This account is temporary and restricted to this specific manuscript review only. Access will expire after the review is completed.</p>
        </div>

      </form>
    </div>
  </div>
</template>

<style scoped>
.registration-container {
  min-height: 100vh;
  background-color: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  font-family: Arial, Helvetica, sans-serif;
}

.registration-card {
  background: white;
  width: 100%;
  max-width: 600px;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.header {
  text-align: center;
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

.platform-name {
  font-size: 24px;
  color: #333;
  margin: 0 0 5px 0;
}

.brand-red {
  color: #C93737;
}

.subtitle {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

/* File Upload Styles */
.highlight-box {
  background-color: #f9f9f9;
  border: 1px solid #e0e0e0;
  padding: 15px;
  border-radius: 4px;
}

.hint-text {
  font-size: 12px;
  color: #666;
  margin-bottom: 10px;
}

.file-upload-container {
  display: flex;
  align-items: center;
}

.file-input {
  display: none;
}

.file-label {
  display: inline-block;
  padding: 10px 15px;
  background-color: #fff;
  border: 1px dashed #C93737;
  border-radius: 4px;
  cursor: pointer;
  color: #C93737;
  font-size: 14px;
  width: 100%;
  text-align: center;
  transition: all 0.2s;
}

.file-label:hover {
  background-color: #fff0f0;
}

.form-group label.required::after {
  content: " *";
  color: #C93737;
}

.input-text, .select-input, .textarea-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.input-text:focus, .select-input:focus, .textarea-input:focus {
  border-color: #C93737;
  outline: none;
}

.input-text.disabled {
  background-color: #f9f9f9;
  color: #666;
  cursor: not-allowed;
}

.name-input-group {
  display: flex;
  gap: 10px;
}

.title-select {
  width: 80px;
}

.name-input {
  flex: 1;
}

.hint {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: normal;
  cursor: pointer;
}

.indent {
  margin-left: 20px;
  padding-left: 10px;
  border-left: 2px solid #eee;
}

.checkbox-group {
  margin-top: 30px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: normal;
  cursor: pointer;
  font-size: 14px;
}

.link {
  color: #C93737;
  text-decoration: none;
}

.link:hover {
  text-decoration: underline;
}

.submit-btn {
  width: 100%;
  padding: 14px;
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.2s;
}

.submit-btn:hover {
  background-color: #B02E2E;
}

.submit-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.footer-note {
  margin-top: 20px;
  text-align: center;
  font-size: 12px;
  color: #999;
  padding-top: 15px;
  border-top: 1px dashed #eee;
}

/* States */
.expired-state, .success-state {
  text-align: center;
  padding: 40px 20px;
}

.icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.redirect-text {
  color: #999;
  font-size: 14px;
  margin-top: 10px;
}
</style>
