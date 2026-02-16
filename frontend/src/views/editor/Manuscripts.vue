<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import InitialReviewModal from '../../components/admin/manuscript/InitialReviewModal.vue'
import AssignReviewersModal from '../../components/admin/manuscript/AssignReviewersModal.vue'
import DraftDecisionModal from '../../components/admin/manuscript/DraftDecisionModal.vue'
import ActionModal from '../../components/admin/manuscript/actions/ActionModal.vue'
import InitialReviewChecklist from '../../components/admin/manuscript/InitialReviewChecklist.vue'
import FinalDecision from '../../views/admin/manuscript/FinalDecision.vue'
import ReviewSummary from '../../components/admin/manuscript/ReviewSummary.vue'
import AuditLog from '../../components/admin/manuscript/AuditLog.vue'
import RevisionCheck from '../../components/admin/manuscript/RevisionCheck.vue'
import { MANUSCRIPT_STATUS, STATUS_LABELS, STATUS_COLORS } from '../../constants/manuscriptStatus'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.submissionUser || userStore.user)

// State for Modal
const showInitialReviewModal = ref(false) // Deprecated, keeping for safety but not used
const showChecklist = ref(false) // New Checklist
const showFinalDecision = ref(false) // New Final Decision
const showReviewSummary = ref(false) // New Review Summary
const showAuditLog = ref(false) // New Audit Log
const showRevisionCheck = ref(false) // New Revision Check
const showAssignModal = ref(false)
const showDecisionModal = ref(false)
const showActionModal = ref(false)
const reviewJournal = ref(null)
const assignJournal = ref(null)
const decisionJournal = ref(null)
const summaryJournal = ref(null)
const revisionJournal = ref(null)
const logJournal = ref(null)
const actionJournal = ref(null)
const currentActionType = ref('')

// Search & History State
const searchKeyword = ref('')
const debouncedKeyword = ref('')
const showSearchHistory = ref(false)
const searchHistory = ref([])
let debounceTimer = null

// Load History
onMounted(() => {
  const history = localStorage.getItem('manuscript_search_history')
  if (history) {
    searchHistory.value = JSON.parse(history)
  }
})

// Debounce Search
watch(searchKeyword, (newVal) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    debouncedKeyword.value = newVal
    if (newVal && !searchHistory.value.includes(newVal)) {
      // Add to history (max 5 items)
      searchHistory.value = [newVal, ...searchHistory.value].slice(0, 5)
      localStorage.setItem('manuscript_search_history', JSON.stringify(searchHistory.value))
    }
  }, 300) // 300ms debounce
})

const selectHistory = (keyword) => {
  searchKeyword.value = keyword
  showSearchHistory.value = false
}

const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem('manuscript_search_history')
}

// Simulated Manuscript Data
const manuscripts = ref([
  {
    id: 'MS-2026-001',
    title: 'Deep Learning in Medical Imaging: A Comprehensive Review',
    author: 'John Doe',
    status: MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
    submittedDate: '2026-02-01',
    field: 'Medical Imaging',
    assignedTo: 'editor' 
  },
  {
    id: 'MS-2026-002',
    title: 'Novel Drug Delivery Systems for Cancer Therapy',
    author: 'Jane Smith',
    status: MANUSCRIPT_STATUS.UNDER_PEER_REVIEW,
    submittedDate: '2026-01-28',
    field: 'Drug Delivery',
    assignedTo: 'ae_user'
  },
  {
    id: 'MS-2026-003',
    title: 'Clinical Trial Ethics in the AI Era',
    author: 'Alice Johnson',
    status: MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
    submittedDate: '2026-01-15',
    field: 'Clinical Research',
    assignedTo: 'editor'
  },
  {
    id: 'MS-2026-004',
    title: 'Big Data in Public Health Monitoring',
    author: 'Bob Brown',
    status: MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION,
    submittedDate: '2026-01-10',
    field: 'Public Health',
    assignedTo: 'ea_user'
  },
  {
    id: 'MS-2026-005',
    title: 'CRISPR Gene Editing Advances',
    author: 'Charlie Green',
    status: MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED,
    submittedDate: '2026-02-05',
    field: 'Genetics',
    assignedTo: 'editor'
  },
  {
    id: 'MS-2026-006',
    title: 'Global Pandemic Response Strategies',
    author: 'Diana White',
    status: MANUSCRIPT_STATUS.UNDER_FINAL_DECISION,
    submittedDate: '2026-01-05',
    field: 'Public Health',
    assignedTo: 'associate_editor'
  },
  {
    id: 'MS-2026-007',
    title: 'AI in Cardiology Diagnosis',
    author: 'Eve Black',
    status: MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED,
    submittedDate: '2025-12-20',
    field: 'Cardiology',
    assignedTo: 'editor'
  }
])

const activeTab = ref('all')

const filteredManuscripts = computed(() => {
  let list = manuscripts.value
  
  // Search Filter
  if (debouncedKeyword.value) {
    const keyword = debouncedKeyword.value.toLowerCase()
    list = list.filter(m => 
      m.id.toLowerCase().includes(keyword) ||
      m.title.toLowerCase().includes(keyword) ||
      m.author.toLowerCase().includes(keyword) ||
      m.field.toLowerCase().includes(keyword)
    )
  }
  
  // Role Scope
  if (user.value?.role === 'editor') {
     if (activeTab.value === 'assigned') {
        return list.filter(m => m.assignedTo === user.value.username)
     }
  } else if (user.value?.role === 'editorial_assistant') {
     if (activeTab.value === 'assigned') {
        return list.filter(m => m.assignedTo === user.value.username)
     }
  }

  // Tab filtering
  if (activeTab.value === 'pending') {
    return list.filter(m => [
      MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW, 
      MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW, 
      MANUSCRIPT_STATUS.UNDER_PEER_REVIEW, 
      MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
      MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
    ].includes(m.status))
  }
  
  return list
})

// Permissions
const canInitialReview = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canAssignReviewer = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canMakeDecision = computed(() => userStore.hasRolePermission(user.value?.role, 'associate_editor') || userStore.hasRolePermission(user.value?.role, 'editor')) 
const canDraftDecision = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canFormatCheck = computed(() => userStore.hasRolePermission(user.value?.role, 'editorial_assistant'))
const isReadOnly = computed(() => user.value?.role === 'advisory_editor')

// Helper
const getStatusLabel = (s) => STATUS_LABELS[s] || s
const getStatusColor = (s) => STATUS_COLORS[s] || '#999'

// Generic Action Handler
const openActionModal = (id, type) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  
  actionJournal.value = journal
  currentActionType.value = type
  showActionModal.value = true
}

const handleActionSubmit = ({ type, data }) => {
  console.log('Action Submitted:', type, data)
  
  const index = manuscripts.value.findIndex(m => m.id === actionJournal.value.id)
  if (index !== -1) {
    if (type === 'format_check') {
       alert('Format Check Completed')
    } else if (type === 'desk_reject') {
       manuscripts.value[index].status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
       alert('Desk Reject Confirmed')
    } else if (type === 'withdraw') {
       manuscripts.value[index].status = MANUSCRIPT_STATUS.WITHDRAWN
       alert('Manuscript Withdrawn')
    } else if (type === 'send_to_production') {
       manuscripts.value[index].status = MANUSCRIPT_STATUS.PENDING_PUBLICATION
       alert('Sent to Production')
    } else if (type === 'archive') {
       manuscripts.value[index].status = 'Archived'
       alert('Manuscript Archived')
    } else if (type === 'invite_reviewer') {
        manuscripts.value[index].status = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
    } else {
       alert(`${type.replace('_', ' ')} Action Completed`)
    }
  }
}

// Action Handlers
const handleDeskReject = (id) => openActionModal(id, 'desk_reject')
const handleRequestRevision = (id) => openActionModal(id, 'request_revision')
const handleWithdraw = (id) => openActionModal(id, 'withdraw')
const handleAddNote = (id) => openActionModal(id, 'add_note')
const handleViewHistory = (id) => openActionModal(id, 'view_history')
const handleGenerateDecisionLetter = (id) => openActionModal(id, 'generate_decision_letter')
const handleSendToProduction = (id) => openActionModal(id, 'send_to_production')
const handleArchive = (id) => openActionModal(id, 'archive')
const handleFormatCheck = (id) => openActionModal(id, 'format_check')

// --- Initial Review (New Checklist) ---
const handleInitialReview = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return

  if (!canInitialReview.value) {
     alert("No permission for initial review")
     return
  }
  
  // Set internal state to 'Under Initial Review' if pending
  if (journal.status === MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW) {
    journal.status = MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW
  }

  reviewJournal.value = journal
  showChecklist.value = true
}

const handleChecklistSubmit = (data) => {
  if (!reviewJournal.value) return
  const index = manuscripts.value.findIndex(m => m.id === reviewJournal.value.id)
  if (index !== -1) {
    manuscripts.value[index].status = data.newStatus
    manuscripts.value[index].initialReviewData = data
  }
  showChecklist.value = false
  reviewJournal.value = null
  alert(`Initial Review Completed: ${data.decision.toUpperCase()}`)
}

const handleChecklistSave = (data) => {
   // Mock save
}

// --- Assign Reviewers ---
const handleAssignReviewer = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  if (!canAssignReviewer.value) {
     alert("Permission denied")
     return
  }
  assignJournal.value = journal
  showAssignModal.value = true
}

const handleAssignConfirm = (data) => {
  if (!assignJournal.value) return
  const index = manuscripts.value.findIndex(m => m.id === assignJournal.value.id)
  if (index !== -1) {
    manuscripts.value[index].status = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
    manuscripts.value[index].assignedReviewers = data.reviewers
  }
  showAssignModal.value = false
  assignJournal.value = null
}

// --- Review Summary (New) ---
const handleReviewSummary = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  
  if (!canDraftDecision.value) {
    alert("Permission denied")
    return
  }
  
  summaryJournal.value = journal
  showReviewSummary.value = true
}

const handleReviewSummarySubmit = (data) => {
  if (!summaryJournal.value) return
  const index = manuscripts.value.findIndex(m => m.id === summaryJournal.value.id)
  if (index !== -1) {
    manuscripts.value[index].status = MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
    alert('Review Summary Report Generated & Submitted to EiC')
  }
  showReviewSummary.value = false
  summaryJournal.value = null
}

// --- Final Decision (New Full View) ---
const handleFinalDecision = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  
  if (!canDraftDecision.value && !canMakeDecision.value) {
    alert("Permission denied")
    return
  }
  
  decisionJournal.value = journal
  showFinalDecision.value = true
}

const handleFinalDecisionSubmit = (payload) => {
  if (!decisionJournal.value) return
  const index = manuscripts.value.findIndex(m => m.id === decisionJournal.value.id)
  
  if (index !== -1) {
    if (payload.role === 'editor') {
      manuscripts.value[index].status = MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
      alert("Materials submitted to Editor-in-Chief")
    } else {
      manuscripts.value[index].status = payload.nextStatus
      alert(`Final Decision Submitted: ${payload.data.decision.toUpperCase()}`)
    }
  }
  
  showFinalDecision.value = false
  decisionJournal.value = null
}

// --- Revision Check (New) ---
const handleRevisionCheck = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  
  if (!canInitialReview.value) {
    alert("Permission denied")
    return
  }
  
  revisionJournal.value = journal
  showRevisionCheck.value = true
}

const handleRevisionSubmit = (data) => {
  if (!revisionJournal.value) return
  const index = manuscripts.value.findIndex(m => m.id === revisionJournal.value.id)
  
  if (index !== -1) {
    if (data.decision === 'pass') {
      // Logic depends on stage. Assuming initial review for now.
      manuscripts.value[index].status = MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED
      alert("Revision Passed")
    } else if (data.decision === 'retry') {
      manuscripts.value[index].status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION
      alert("Returned for Revision")
    } else if (data.decision === 'reject') {
      manuscripts.value[index].status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
      alert("Revision Rejected")
    }
  }
  
  showRevisionCheck.value = false
  revisionJournal.value = null
}

// --- Audit Log (New) ---
const handleAuditLog = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  
  logJournal.value = journal
  showAuditLog.value = true
}

// --- Publication ---
const handleStartPublication = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return
  
  // Logic: Send Notice -> Pending Acceptance Confirmation
  // Mocking transition
  const index = manuscripts.value.findIndex(m => m.id === id)
  manuscripts.value[index].status = MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION
  alert("Acceptance Notice Sent. Waiting for Author Confirmation.")
}

</script>

<template>
  <div class="editor-page">
    
    <!-- Full Screen Overlay for Heavy Tasks -->
    <div v-if="showChecklist || showFinalDecision || showReviewSummary || showAuditLog || showRevisionCheck" class="fullscreen-overlay">
      <div class="overlay-header">
        <button class="btn-back" @click="showChecklist = false; showFinalDecision = false; showReviewSummary = false; showAuditLog = false; showRevisionCheck = false">← Back to Dashboard</button>
      </div>
      
      <div v-if="showChecklist" class="overlay-content">
        <InitialReviewChecklist 
          :manuscript="reviewJournal"
          :current-user="user"
          @close="showChecklist = false"
          @submit="handleChecklistSubmit"
          @save-draft="handleChecklistSave"
        />
      </div>

      <div v-if="showFinalDecision" class="overlay-content">
        <FinalDecision 
          :manuscript="decisionJournal"
          :current-user="user"
          :reviews="[
            { recommendation: 'Accept', summary: 'Excellent work.' }, 
            { recommendation: 'Revise', summary: 'Needs minor changes.' }
          ]"
          @submit="handleFinalDecisionSubmit"
          @save-draft="() => {}"
          @return-materials="() => { showFinalDecision = false; alert('Returned for materials'); }"
        />
      </div>

      <div v-if="showReviewSummary" class="overlay-content">
        <ReviewSummary 
          :manuscript="summaryJournal"
          @submit="handleReviewSummarySubmit"
          @save-draft="() => {}"
        />
      </div>

      <div v-if="showRevisionCheck" class="overlay-content">
        <RevisionCheck 
          :manuscript="revisionJournal"
          @submit="handleRevisionSubmit"
          @save-draft="() => {}"
        />
      </div>

      <div v-if="showAuditLog" class="overlay-content">
        <AuditLog 
          :manuscript="logJournal"
        />
      </div>
    </div>

    <!-- Main Dashboard List (Hidden when overlay active) -->
    <div v-else>
      <div class="page-header">
        <h2>Manuscript Management</h2>
        <div class="role-badge">Current Role: {{ user?.role }}</div>
      </div>

      <div class="tabs">
        <div class="tab-group">
          <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">All Manuscripts</button>
          <button class="tab-btn" :class="{ active: activeTab === 'assigned' }" @click="activeTab = 'assigned'">My Assigned</button>
          <button class="tab-btn" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">Pending Action</button>
        </div>
        
        <div class="search-container">
          <div class="search-wrapper">
            <input type="text" v-model="searchKeyword" placeholder="Search..." class="search-input" @focus="showSearchHistory = true" @blur="setTimeout(() => showSearchHistory = false, 200)" />
          </div>
        </div>
      </div>

      <div class="manuscript-list">
        <div v-if="filteredManuscripts.length === 0" class="empty-state">No matching tasks found</div>
        <div v-else v-for="ms in filteredManuscripts" :key="ms.id" class="manuscript-card">
          <div class="ms-header">
            <span class="ms-id">{{ ms.id }}</span>
            <span class="ms-status-badge" :style="{ backgroundColor: getStatusColor(ms.status), color: 'white' }">{{ getStatusLabel(ms.status) }}</span>
          </div>
          <h3 class="ms-title">{{ ms.title }}</h3>
          <div class="ms-meta">
            <span>Author: {{ ms.author }}</span>
            <span>Field: {{ ms.field }}</span>
            <span>Date: {{ ms.submittedDate }}</span>
          </div>
          
          <div class="ms-actions" v-if="!isReadOnly">
            
            <!-- 1. Pending Initial Review -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW || ms.status === MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW">
              <div class="action-row left">
                <button v-if="canInitialReview" class="action-btn red" @click="handleInitialReview(ms.id)">
                  {{ ms.status === MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW ? 'Continue Initial Review' : 'Start Initial Review' }}
                </button>
              </div>
            </template>

            <!-- 2. Initial Review Passed -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED">
              <div class="action-row left">
                <button v-if="canAssignReviewer" class="action-btn red" @click="handleAssignReviewer(ms.id)">Assign Reviewers</button>
              </div>
              <div class="hint-text">Please assign reviewers to proceed to Peer Review.</div>
            </template>

            <!-- 3. Initial Review Revision (Now Re-Review) -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION">
              <div class="action-row left">
                 <button class="action-btn red" @click="handleRevisionCheck(ms.id)">Start Revision Check</button>
                 <span class="hint-text">Author has submitted revision.</span>
              </div>
            </template>

            <!-- 4. Under Peer Review -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.UNDER_PEER_REVIEW">
               <div class="action-row left">
                 <button class="action-btn gray">Check Review Status</button>
                 <span class="hint-text">Review in progress...</span>
               </div>
            </template>

            <!-- 5. Pending Final Decision (Review Summary -> Final Decision) -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION">
               <div class="action-row left">
                 <button v-if="canDraftDecision" class="action-btn red" @click="handleReviewSummary(ms.id)">Create Review Summary</button>
                 <button v-if="canDraftDecision" class="action-btn gray" @click="handleFinalDecision(ms.id)">Direct Final Decision (Legacy)</button>
               </div>
            </template>

            <!-- 6. Under Final Decision (EiC Reviewing) -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.UNDER_FINAL_DECISION">
               <div class="action-row left">
                 <button v-if="user.role === 'editor_in_chief' || user.role === 'associate_editor'" class="action-btn red" @click="handleFinalDecision(ms.id)">Make Final Decision</button>
                 <button v-else class="action-btn gray">View Decision Progress</button>
               </div>
            </template>

            <!-- 7. Final Decision Passed (Accepted) -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED">
               <div class="action-row left">
                 <button class="action-btn red" @click="handleStartPublication(ms.id)">Send Acceptance Notice</button>
               </div>
            </template>

             <!-- 8. Pending Acceptance Confirmation -->
            <template v-if="ms.status === MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION">
               <div class="action-row left">
                 <button class="action-btn gray">Check Notification Status</button>
                 <button class="action-btn red" @click="handleStartPublication(ms.id)">Resend Notice</button>
               </div>
            </template>

            <!-- Common Utility Actions -->
            <div class="action-row right">
               <button class="action-btn gray-small" @click="handleAuditLog(ms.id)">Audit Log</button>
               <button class="action-btn gray-small" @click="handleAddNote(ms.id)">Add Note</button>
               <button class="action-btn gray-small" @click="handleViewHistory(ms.id)">View History</button>
            </div>

          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <AssignReviewersModal :visible="showAssignModal" :manuscript="assignJournal" :current-user="user" @close="showAssignModal = false" @send-invitations="handleAssignConfirm" />
    <ActionModal :visible="showActionModal" :manuscript="actionJournal" :action-type="currentActionType" :current-user="user" @close="showActionModal = false" @submit="handleActionSubmit" />

  </div>
</template>

<style scoped>
.editor-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 60px auto 0;
}

/* Fullscreen Overlay */
.fullscreen-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: #f5f5f5;
  z-index: 2000;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.overlay-header {
  background: white;
  padding: 10px 20px;
  border-bottom: 1px solid #ddd;
  position: sticky;
  top: 0;
  z-index: 10;
}

.btn-back {
  background: none;
  border: none;
  color: #333;
  font-size: 16px;
  cursor: pointer;
  font-weight: bold;
}

.overlay-content {
  flex: 1;
  padding: 20px;
}

/* Page Styles */
.page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; }
.role-badge { background: #e0e0e0; padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold; font-size: 0.8rem; color: #555; }
.tabs { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem; flex-wrap: wrap; gap: 1rem; }
.tab-group { display: flex; gap: 1rem; }
.search-container { flex-grow: 1; max-width: 400px; }
.search-input { width: 100%; padding: 0.5rem 1rem; border: 1px solid #ddd; border-radius: 4px; }

.tab-btn { background: none; border: none; font-size: 1rem; padding: 0.5rem 1rem; cursor: pointer; color: #666; border-radius: 5px; }
.tab-btn.active { background: #3498db; color: white; }

.manuscript-card { background: white; border: 1px solid #eee; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.ms-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.ms-id { font-family: monospace; color: #888; }
.ms-status-badge { padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
.ms-title { margin: 0.5rem 0; color: #2c3e50; }
.ms-meta { font-size: 0.9rem; color: #666; display: flex; gap: 2rem; margin-bottom: 1.5rem; }
.ms-actions { display: flex; flex-direction: column; gap: 1rem; padding-top: 1rem; border-top: 1px solid #f0f0f0; }

.action-row { display: flex; flex-wrap: wrap; align-items: center; margin-bottom: 8px; }
.action-row.left { justify-content: flex-start; gap: 8px; }
.action-row.right { justify-content: flex-end; gap: 8px; }

.action-btn { padding: 0.5rem 1rem; border-radius: 4px; border: none; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }
.action-btn.blue { background-color: #165DFF; color: white; }
.action-btn.blue:hover { background-color: #134BC0; }
.action-btn.red { background-color: #C93737; color: white; }
.action-btn.red:hover { background-color: #B02E2E; }
.action-btn.gray { background-color: #E5E7EB; color: #6B7280; }
.action-btn.gray-small { background-color: #E5E7EB; color: #374151; padding: 0.3rem 0.8rem; font-size: 0.8rem; }
.action-btn.gray-small:hover { background-color: #D1D5DB; }

.hint-text { font-size: 12px; color: #999; margin-left: 10px; font-style: italic; }

.empty-state { text-align: center; padding: 3rem; color: #888; background: #f9f9f9; border-radius: 8px; }
</style>
