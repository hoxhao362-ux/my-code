<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { stripHtmlTags, truncateText } from '../../../utils/helpers.js'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import InitialReviewModal from '../../../components/admin/manuscript/InitialReviewModal.vue'
import AssignReviewersModal from '../../../components/admin/manuscript/AssignReviewersModal.vue'
import { useI18n } from '../../../composables/useI18n'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'

const { t } = useI18n()
const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Permissions
const canInitialReview = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canAssignReviewers = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canReject = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))

// State
const showAssignModal = ref(false)
const showInitialReviewModal = ref(false)
const currentJournal = ref(null)
const reviewJournal = ref(null)
const assignJournal = ref(null)
const selectedReviewers = ref([])
const availableReviewers = computed(() => userStore.users.filter(u => u.role === 'reviewer'))

// Actions
const openAssignModal = (journal) => {
  // Permission Check
  if (!canAssignReviewers.value) {
     alert("You do not have permission to assign reviewers, please contact the Editor or Associate Editor")
     return
  }
  
  // For Associate Editor, check if they are assigned to this journal's field (Mock check)
  if (user.value.role === 'associate_editor') {
     // In a real app, we'd check journal.module === user.field
     // For now, we assume they can only see what they can edit
  }

  assignJournal.value = journal
  showAssignModal.value = true
}

const handleAssignConfirm = (data) => {
  if (!assignJournal.value) return
  
  const updatedJournal = { ...assignJournal.value }
  updatedJournal.status = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
  updatedJournal.reviewStage = 'Peer Review'
  updatedJournal.reviewers = data.reviewers.map(r => ({
    id: r.id,
    name: r.name,
    status: 'invited',
    invitedAt: new Date().toISOString(),
    deadline: data.invitation.deadline
  }))
  
  // Logic: If Associate Editor, send copy to Editor (Mock log)
  if (user.value.role === 'associate_editor') {
    console.log('Copy of invitation sent to Editor')
  }

  userStore.updateJournal(updatedJournal)
  
  // Close modal
  showAssignModal.value = false
  assignJournal.value = null
}

const openInitialReview = (journal) => {
  // Permission Check
  if (!canInitialReview.value) {
    // Show temporary alert
    const alertDiv = document.createElement('div')
    alertDiv.style.cssText = `
      position: fixed;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      background: #e74c3c;
      color: white;
      padding: 10px 20px;
      border-radius: 4px;
      z-index: 9999;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `
    alertDiv.textContent = "No permission for initial review"
    document.body.appendChild(alertDiv)
    setTimeout(() => {
      document.body.removeChild(alertDiv)
    }, 5000)
    return
  }

  reviewJournal.value = journal
  showInitialReviewModal.value = true
}

const closeInitialReviewModal = () => {
  showInitialReviewModal.value = false
  reviewJournal.value = null
}

const handleInitialReviewSubmit = (data) => {
  if (!reviewJournal.value) return

  const updatedJournal = { ...reviewJournal.value }
  
  // Update status based on outcome
  updatedJournal.initialReview = data
  
  if (data.finalOutcome === 'Reject Directly') {
    updatedJournal.status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
    updatedJournal.reviewResult = 'Rejected'
  } else if (data.finalOutcome === 'Suggest Transfer to Sister Journal') {
    updatedJournal.status = 'transferred'
    updatedJournal.transferReason = data.detailedReason
  } else if (data.finalOutcome === 'Forward to Peer Review') {
    updatedJournal.status = MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED
    updatedJournal.readyForPeerReview = true
  }

  userStore.updateJournal(updatedJournal)
}

const handleAssignSubmit = () => {
  if (selectedReviewers.value.length === 0) {
    alert(t('screening.errors.selectReviewer'))
    return
  }
  
  const journal = { ...currentJournal.value }
  journal.status = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
  journal.reviewStage = 'Peer Review'
  journal.reviewers = selectedReviewers.value.map(id => {
    const r = availableReviewers.value.find(u => u.id === id)
    return {
      id: r.id,
      name: r.username,
      status: 'invited',
      assignedAt: new Date().toISOString()
    }
  })
  
  userStore.updateJournal(journal)
  showAssignModal.value = false
  currentJournal.value = null
  alert(t('screening.success.assigned'))
}

const handleReject = (journal) => {
  if (confirm(t('screening.confirmReject'))) {
    const updatedJournal = { ...journal }
    updatedJournal.status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
    updatedJournal.reviewResult = 'Rejected'
    userStore.updateJournal(updatedJournal)
  }
}

const pendingJournals = computed(() => {
  let journals = userStore.journals.filter(journal => 
    journal.status === MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW || 
    journal.status === 'Submitted' ||
    journal.status === 'submitted'
  )
  
  if (selectedModule.value !== 'all') {
    journals = journals.filter(j => j.module === selectedModule.value)
  }
  
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    journals = journals.filter(j => 
      j.title.toLowerCase().includes(q) || 
      j.writer.toLowerCase().includes(q) ||
      stripHtmlTags(j.abstract).toLowerCase().includes(q)
    )
  }
  
  return journals
})

const modules = computed(() => userStore.modules)

const viewJournalDetail = (id) => {
  router.push(`/admin/journal/${id}`)
}
</script>

<template>
  <div class="screening-container">
    <Navigation 
      :user="user"
      :current-page="'manuscript-screening'"
      :toggle-directory="() => {}"
      :navigate-to="() => {}"
      :logout="userStore.logout"
    />

    <main class="content">
      <div class="header">
        <h1>{{ t('screening.title') }}</h1>
      </div>

      <div class="filter-section">
        <input v-model="searchQuery" :placeholder="t('screening.searchPlaceholder')" class="search-input" />
        <select v-model="selectedModule" class="filter-select">
          <option value="all">{{ t('screening.allModules') }}</option>
          <option v-for="m in modules" :key="m" :value="m">{{ m }}</option>
        </select>
      </div>

      <div class="journals-list">
        <div v-for="journal in pendingJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title" @click="viewJournalDetail(journal.id)">{{ journal.title }}</h3>
            <p class="journal-meta">{{ journal.writer }} | {{ journal.date }} | {{ journal.module }}</p>
            <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract), 150) }}</p>
          </div>
          <div class="journal-actions">
            <button 
              v-if="canInitialReview"
              class="btn btn-review" 
              @click="openInitialReview(journal)"
            >
              Initial Review
            </button>
            <button 
              v-if="canAssignReviewers"
              class="btn btn-primary" 
              @click="openAssignModal(journal)"
            >
              {{ t('screening.actions.assign') }}
            </button>
            <button v-if="canReject" class="btn btn-reject" @click="handleReject(journal)">{{ t('screening.actions.reject') }}</button>
          </div>
        </div>
        <div v-if="pendingJournals.length === 0" class="no-journals">
          <p>{{ t('screening.noJournals') }}</p>
        </div>
      </div>
    </main>

    <InitialReviewModal 
      :visible="showInitialReviewModal"
      :manuscript="reviewJournal"
      :current-user="user"
      @close="closeInitialReviewModal"
      @submit="handleInitialReviewSubmit"
    />

    <AssignReviewersModal
      :visible="showAssignModal"
      :manuscript="assignJournal"
      :current-user="user"
      @close="showAssignModal = false"
      @send-invitations="handleAssignConfirm"
      @save-draft="() => {}"
    />

    <!-- Old Assign Modal (Removed/Replaced) -->
    
    <footer class="footer">
        <div class="footer-content">
            <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
        </div>
    </footer>
  </div>
</template>

<style scoped>
.screening-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}

.content {
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  width: 100%;
  margin-top: 80px;
}

.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.filter-section {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

.search-input, .filter-select {
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
}

.journal-info {
  flex: 1;
}

.journal-title {
  color: #3498db;
  cursor: pointer;
}

.journal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-left: 1rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  color: white;
}

.btn-primary { background: #3498db; }
.btn-review { background: #27ae60; }
.btn-reject { background: #e74c3c; }
.btn-cancel { background: #95a5a6; }

.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
}

.reviewer-list {
  max-height: 300px;
  overflow-y: auto;
  margin: 1rem 0;
  border: 1px solid #eee;
  padding: 0.5rem;
}

.reviewer-item {
  padding: 0.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.footer {
  background: #2c3e50;
  color: white;
  padding: 1rem 0;
  text-align: center;
  margin-top: auto;
}
</style>
