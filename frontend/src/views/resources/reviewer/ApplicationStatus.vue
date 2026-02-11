<template>
  <div class="page-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-reviewer-status'"
      :logout="userStore.logout"
    />
    
    <div class="sidebar-info">
      <h1>Application Status</h1>
      
      <div class="status-badge" :class="statusClass">
        {{ statusDisplay }}
      </div>

      <div class="status-details">
        <p><strong>Submitted on:</strong> {{ submissionDate }}</p>
        <p><strong>Estimated Review Time:</strong> 7-10 Business Days</p>
      </div>

      <p class="description">
        {{ statusDescription }}
      </p>

      <p>
        <router-link to="/resources/reviewer/guidelines" class="link-brand">View Reviewer Guidelines</router-link>
      </p>
    </div>

    <div class="form-area">
      <div class="form-container">
        <!-- Read-only Form -->
        <div class="form-group">
          <label>Full Name</label>
          <div class="read-only-field">{{ form.name }}</div>
        </div>
        <div class="form-group">
          <label>Email Address</label>
          <div class="read-only-field">{{ form.email }}</div>
        </div>
        <div class="form-group">
          <label>ORCID ID</label>
          <div class="read-only-field">{{ form.orcid }}</div>
        </div>
        <div class="form-group">
          <label>Research Areas / Keywords</label>
          <div class="read-only-field">{{ form.areas }}</div>
        </div>
        
        <div class="actions">
          <button v-if="status === 'pending_review'" class="btn-withdraw" @click="showWithdrawModal = true">Withdraw Application</button>
          <button v-if="status === 'rejected' || status === 'withdrawn'" class="btn-reapply" @click="reapply">Reapply</button>
          
          <!-- Debug Button -->
          <button v-if="status === 'pending_review'" class="btn-debug" @click="debugApprove">Debug: Approve</button>
        </div>
      </div>
    </div>

    <!-- Withdraw Confirmation Modal -->
    <div v-if="showWithdrawModal" class="modal-overlay">
      <div class="modal-content">
        <h3>Withdraw Application</h3>
        <p>Are you sure you want to withdraw your reviewer application? You can reapply later if you change your mind.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showWithdrawModal = false">Cancel</button>
          <button class="btn-confirm-withdraw" @click="confirmWithdraw">Withdraw</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)
const router = useRouter()

const status = ref('pending_review') // pending_review, rejected, withdrawn, approved
const submissionDate = ref('2023-10-27') // Mock date
const showWithdrawModal = ref(false)

const form = reactive({
  name: '',
  email: '',
  orcid: '',
  areas: ''
})

const statusDisplay = computed(() => {
  if (status.value === 'pending_review') return 'Under Review'
  if (status.value === 'rejected') return 'Rejected'
  if (status.value === 'withdrawn') return 'Withdrawn'
  return 'Unknown'
})

const statusClass = computed(() => {
  if (status.value === 'pending_review') return 'badge-orange'
  if (status.value === 'rejected') return 'badge-red'
  if (status.value === 'withdrawn') return 'badge-grey'
  return ''
})

const statusDescription = computed(() => {
  if (status.value === 'pending_review') return 'Your application is currently being reviewed by our editorial team. We will notify you via email once a decision has been made.'
  if (status.value === 'rejected') return 'Thank you for your interest. Unfortunately, your application was not approved at this time. Please see the email sent to you for more details.'
  if (status.value === 'withdrawn') return 'You have withdrawn your application.'
  return ''
})

const confirmWithdraw = () => {
  status.value = 'withdrawn'
  localStorage.setItem('reviewer_application_status', 'withdrawn')
  showWithdrawModal.value = false
}

const reapply = () => {
  // Redirect to Become Reviewer page (it will load draft/existing data if we set it back to draft mode or just populate)
  // We should put the data back into draft storage so BecomeReviewer can pick it up
  localStorage.setItem('reviewer_application_draft', JSON.stringify(form))
  router.push('/resources/reviewer/become')
}

const debugApprove = () => {
  localStorage.setItem('reviewer_application_status', 'approved')
  // Update user role to reviewer
  userStore.updateUserRole(user.value.id, 'reviewer')
  userStore.user.role = 'reviewer'
  userStore.user.status = 'active'
  localStorage.setItem('user', JSON.stringify(userStore.user))
  
  alert('Application Approved! You are now a reviewer.')
  router.push('/reviewer/dashboard')
}

onMounted(() => {
  // Load status and data
  const storedStatus = localStorage.getItem('reviewer_application_status')
  if (storedStatus) {
    status.value = storedStatus
  }
  
  const storedData = localStorage.getItem('reviewer_application_data')
  if (storedData) {
    const data = JSON.parse(storedData)
    Object.assign(form, data)
  }
  
  // Set submission date to today if not stored (mock)
  const d = new Date()
  submissionDate.value = d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
})
</script>

<style scoped>
.page-container {
  display: flex;
  min-height: 100vh;
  padding-top: 0;
  margin-top: 80px;
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

.status-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 4px;
  color: white;
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 24px;
}

.badge-orange {
  background-color: #FFA500;
}

.badge-red {
  background-color: #C93737;
}

.badge-grey {
  background-color: #999;
}

.status-details p {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin-top: 24px;
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
  color: #999; /* Label grey for read-only */
  margin-bottom: 8px;
}

.read-only-field {
  width: 100%;
  padding: 10px;
  border: 1px solid #E5E5E5; /* Read only border */
  border-radius: 4px;
  font-size: 14px;
  background-color: #FAFAFA;
  color: #333;
}

.actions {
  margin-top: 32px;
}

.btn-withdraw {
  padding: 10px 24px;
  background-color: #E5E5E5; /* Grey button */
  color: #333;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-withdraw:hover {
  background-color: #D5D5D5;
}

.btn-reapply {
  padding: 10px 24px;
  background-color: #C93737; /* Brand button */
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-reapply:hover {
  background-color: #A02C2C;
}

.btn-debug {
  padding: 10px 24px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  margin-left: 10px;
}

/* Modal */
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
}

.modal-content h3 {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-top: 0;
  margin-bottom: 16px;
}

.modal-content p {
  color: #666;
  margin-bottom: 24px;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.btn-cancel {
  padding: 8px 16px;
  background-color: #F5F5F5;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.btn-confirm-withdraw {
  padding: 8px 16px;
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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