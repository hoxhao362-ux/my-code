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
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const toastStore = useToastStore()
const user = computed(() => userStore.user)
const router = useRouter()

// Get status from store, but also allow local override for debug if needed
const status = computed(() => userStore.reviewerApplicationStatus)
const submissionDate = ref('2023-10-27') // Mock date
const showWithdrawModal = ref(false)

const form = reactive({
  name: '',
  email: '',
  orcid: '',
  areas: ''
})

const statusDisplay = computed(() => {
  if (status.value === 'pending_review') return 'Pending Review'
  if (status.value === 'rejected') return 'Rejected'
  if (status.value === 'withdrawn') return 'Withdrawn'
  if (status.value === 'approved') return 'Active Reviewer'
  return 'Unknown'
})

const statusDescription = computed(() => {
  if (status.value === 'pending_review') return 'Your application is being reviewed by the editorial office.'
  if (status.value === 'rejected') return 'Thank you for your interest. Unfortunately, your application was not approved at this time. Please see the email sent to you for more details.'
  if (status.value === 'withdrawn') return 'You have withdrawn your application.'
  if (status.value === 'approved') return 'Congratulations! You have been approved as a reviewer. You can now access the Reviewer Dashboard.'
  return ''
})

const confirmWithdraw = () => {
  userStore.withdrawReviewerApplication()
  showWithdrawModal.value = false
  toastStore.info('Application withdrawn.')
}

const reapply = () => {
  userStore.reapplyReviewer()
  router.push('/resources/reviewer/become')
}

const debugApprove = () => {
  // Check if user ID exists (Strict check for null/undefined/empty string)
  const userId = user.value?.id
  const hasValidId = userId !== null && userId !== undefined && userId !== ''

  if (hasValidId) {
    // Directly update user role to demonstrate the fix
    userStore.updateUserRole(userId, 'reviewer')
    toastStore.success('Application Approved! You are now a reviewer.')
  } else {
    // Fallback for virtual accounts without ID
    console.warn('Virtual account detected (ID missing). Executing debug role update locally.')
    toastStore.warning('Virtual Account: Role updated in session only (ID missing).')
  }

  // Force update current user object in store to reflect role change immediately
  // This ensures the flow continues regardless of ID presence
  if (userStore.user) {
    userStore.user.role = 'reviewer'
    sessionStorage.setItem('readonly_user', JSON.stringify(userStore.user))
  }
  
  // Status should automatically update because it's computed from store.reviewerApplicationStatus which checks role
  // But we need to ensure local status is also updated if store getter relies on it
  userStore.reviewerApplication.status = 'approved'
  localStorage.setItem('reviewer_application_status', 'approved')
}

onMounted(() => {
  // Load data
  const data = userStore.reviewerApplication.data
  if (data) {
    Object.assign(form, data)
  } else if (user.value) {
    // If approved via role but no application data (e.g. created by admin), prefill from user profile
    form.name = user.value.username || ''
    form.email = user.value.email || ''
    form.orcid = user.value.orcid || '' // Assuming user object might have orcid
    form.areas = user.value.expertise ? user.value.expertise.join(', ') : ''
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
  background-color: #f9f9f9;
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
  font-family: 'Georgia', serif;
}

.status-badge {
  display: inline-block;
  padding: 8px 18px;
  border-radius: 2px;
  color: white;
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 24px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-orange {
  background-color: #E67E22;
}

.badge-red {
  background-color: #C93737;
}

.badge-grey {
  background-color: #7f8c8d;
}

.badge-green {
  background-color: #27AE60;
}

.status-details p {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
}

.description {
  font-size: 15px;
  color: #555;
  line-height: 1.6;
  margin-top: 24px;
  margin-bottom: 24px;
}

.link-brand {
  color: #005696;
  text-decoration: none;
  font-weight: 600;
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
  font-size: 14px;
  font-weight: 600;
  color: #777; /* Label grey for read-only */
  margin-bottom: 8px;
}

.read-only-field {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd; /* Read only border */
  border-radius: 2px;
  font-size: 15px;
  background-color: #f9f9f9;
  color: #333;
}

.actions {
  margin-top: 40px;
  display: flex;
  align-items: center;
}

.btn-withdraw {
  padding: 10px 24px;
  background-color: #f0f0f0; /* Grey button */
  color: #333;
  border: 1px solid #ccc;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-withdraw:hover {
  background-color: #e0e0e0;
}

.btn-reapply {
  padding: 10px 24px;
  background-color: #005696; /* Brand button */
  color: white;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 600;
  transition: background-color 0.2s;
}

.btn-reapply:hover {
  background-color: #00447a;
}

.btn-debug {
  padding: 10px 24px;
  background-color: #333;
  color: white;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 600;
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
  padding: 40px;
  border-radius: 4px;
  width: 450px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.modal-content h3 {
  font-size: 20px;
  font-weight: 600;
  color: #333;
  margin-top: 0;
  margin-bottom: 16px;
}

.modal-content p {
  color: #666;
  margin-bottom: 30px;
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
}

.btn-cancel {
  padding: 10px 20px;
  background-color: white;
  border: 1px solid #ccc;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 500;
}

.btn-confirm-withdraw {
  padding: 10px 20px;
  background-color: #C93737;
  color: white;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-weight: 500;
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
