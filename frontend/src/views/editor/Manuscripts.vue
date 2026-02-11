<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import InitialReviewModal from '../../components/admin/manuscript/InitialReviewModal.vue'
import AssignReviewersModal from '../../components/admin/manuscript/AssignReviewersModal.vue'
import DraftDecisionModal from '../../components/admin/manuscript/DraftDecisionModal.vue'
import ActionModal from '../../components/admin/manuscript/actions/ActionModal.vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.submissionUser || userStore.user)

// State for Modal
const showInitialReviewModal = ref(false)
const showAssignModal = ref(false)
const showDecisionModal = ref(false)
const showActionModal = ref(false)
const reviewJournal = ref(null)
const assignJournal = ref(null)
const decisionJournal = ref(null)
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
    status: 'Submitted',
    submittedDate: '2026-02-01',
    field: 'Medical Imaging',
    assignedTo: 'editor' // assigned to username 'editor'
  },
  {
    id: 'MS-2026-002',
    title: 'Novel Drug Delivery Systems for Cancer Therapy',
    author: 'Jane Smith',
    status: 'Under Review',
    submittedDate: '2026-01-28',
    field: 'Drug Delivery',
    assignedTo: 'ae_user'
  },
  {
    id: 'MS-2026-003',
    title: 'Clinical Trial Ethics in the AI Era',
    author: 'Alice Johnson',
    status: 'Pending Decision',
    submittedDate: '2026-01-15',
    field: 'Clinical Research',
    assignedTo: 'editor'
  },
  {
    id: 'MS-2026-004',
    title: 'Big Data in Public Health Monitoring',
    author: 'Bob Brown',
    status: 'Revision Requested',
    submittedDate: '2026-01-10',
    field: 'Public Health',
    assignedTo: 'ea_user' // Assistance task
  }
])

const activeTab = ref('all')

const filteredManuscripts = computed(() => {
  let list = manuscripts.value
  
  // Search Filter (Use debounced keyword)
  if (debouncedKeyword.value) {
    const keyword = debouncedKeyword.value.toLowerCase()
    list = list.filter(m => 
      m.id.toLowerCase().includes(keyword) ||
      m.title.toLowerCase().includes(keyword) ||
      m.author.toLowerCase().includes(keyword) ||
      m.field.toLowerCase().includes(keyword)
    )
  }
  
  // Filter based on role scope (Mock logic)
  if (user.value?.role === 'editor') {
     // Editors see assigned + basic list
     if (activeTab.value === 'assigned') {
        return list.filter(m => m.assignedTo === user.value.username)
     }
  } else if (user.value?.role === 'editorial_assistant') {
     // EAs see what they are assisting with
     if (activeTab.value === 'assigned') {
        return list.filter(m => m.assignedTo === user.value.username)
     }
  } else if (user.value?.role === 'associate_editor') {
     // AEs see everything in their field (mocked as all for now)
  }

  // Tab filtering
  if (activeTab.value === 'pending') {
    return list.filter(m => ['Submitted', 'Under Review', 'Pending Decision'].includes(m.status))
  }
  
  return list
})

// Permission Helpers using Store logic
const canInitialReview = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canAssignReviewer = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canMakeDecision = computed(() => userStore.hasRolePermission(user.value?.role, 'associate_editor')) 
const canDraftDecision = computed(() => userStore.hasRolePermission(user.value?.role, 'editor'))
const canFormatCheck = computed(() => userStore.hasRolePermission(user.value?.role, 'editorial_assistant'))
const isReadOnly = computed(() => user.value?.role === 'advisory_editor')

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
  
  // Logic to update local state based on action type
  const index = manuscripts.value.findIndex(m => m.id === actionJournal.value.id)
  if (index !== -1) {
    if (type === 'format_check') {
       // Mock status update
       // manuscripts.value[index].status = 'Format Checked'
       alert('Format Check Completed')
    } else if (type === 'desk_reject') {
       manuscripts.value[index].status = 'Rejected'
       alert('Desk Reject Confirmed')
    } else if (type === 'withdraw') {
       manuscripts.value[index].status = 'Withdrawn'
       alert('Manuscript Withdrawn')
    } else if (type === 'send_to_production') {
       manuscripts.value[index].status = 'In Production'
       alert('Sent to Production')
    } else if (type === 'archive') {
       manuscripts.value[index].status = 'Archived'
       alert('Manuscript Archived')
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
const handleRemindReviewer = (id) => openActionModal(id, 'remind_reviewer')
const handleReplaceReviewer = (id) => openActionModal(id, 'replace_reviewer')
const handleExtendDeadline = (id) => openActionModal(id, 'extend_deadline')
const handleRequestFurtherReview = (id) => openActionModal(id, 'request_further_review')
const handleApproveDecision = (id) => openActionModal(id, 'approve_decision')
const handleGenerateDecisionLetter = (id) => openActionModal(id, 'generate_decision_letter')
const handleSendToProduction = (id) => openActionModal(id, 'send_to_production')
const handleArchive = (id) => openActionModal(id, 'archive')
const handleFormatCheck = (id) => openActionModal(id, 'format_check')

const handleInitialReview = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return

  // Permission check
  if (!canInitialReview.value) {
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

const handleInitialReviewSubmit = (data) => {
  if (!reviewJournal.value) return

  const journalIndex = manuscripts.value.findIndex(m => m.id === reviewJournal.value.id)
  if (journalIndex !== -1) {
     let newStatus = 'Initial Review Completed'
     
     if (data.finalOutcome === 'Reject Directly') {
        newStatus = 'Rejected'
     } else if (data.finalOutcome === 'Suggest Transfer to Sister Journal') {
        newStatus = 'Transferred'
     } else if (data.finalOutcome === 'Forward to Peer Review') {
        newStatus = 'Under Review' // Or ready for peer review
     }
     
     manuscripts.value[journalIndex].status = newStatus
     manuscripts.value[journalIndex].initialReview = data
  }
}

const closeInitialReviewModal = () => {
  showInitialReviewModal.value = false
  reviewJournal.value = null
}

const handleAssignReviewer = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return

  // Permission check
  if (!canAssignReviewer.value) {
     alert("You do not have permission to assign reviewers, please contact the Editor or Associate Editor")
     return
  }

  assignJournal.value = journal
  showAssignModal.value = true
}

const handleAssignConfirm = (data) => {
  if (!assignJournal.value) return

  const journalIndex = manuscripts.value.findIndex(m => m.id === assignJournal.value.id)
  if (journalIndex !== -1) {
    manuscripts.value[journalIndex].status = 'Under Review'
    manuscripts.value[journalIndex].assignedReviewers = data.reviewers
  }
  
  showAssignModal.value = false
  assignJournal.value = null
}

const handleDraftDecision = (id) => {
  const journal = manuscripts.value.find(m => m.id === id)
  if (!journal) return

  // Permission Check
  if (!canDraftDecision.value) {
     alert("You do not have permission to draft decisions, please contact the Editor or Associate Editor")
     return
  }

  // Edge Case: If Editor is processing (Mock check)
  if (user.value.role === 'associate_editor' && journal.isProcessingByEditor) {
    alert("This manuscript is being processed by the Editor-in-Chief, please try again later")
    return
  }

  decisionJournal.value = journal
  showDecisionModal.value = true
}

const handleDecisionSubmit = (data) => {
  if (!decisionJournal.value) return

  const journalIndex = manuscripts.value.findIndex(m => m.id === decisionJournal.value.id)
  if (journalIndex !== -1) {
    if (data.isEICReviewRequired) {
      manuscripts.value[journalIndex].status = 'Under EIC Review'
    } else {
      manuscripts.value[journalIndex].status = data.decision === 'Reject' ? 'Rejected' : 
                                               data.decision === 'Accept' ? 'Accepted' : 
                                               'Revision Requested'
    }
    manuscripts.value[journalIndex].decisionData = data
  }
  
  showDecisionModal.value = false
  decisionJournal.value = null
}

const handleMakeDecision = (id) => {
  if (user.value?.role === 'associate_editor') {
    // Check if it's minor revision (Mock check)
    const decision = prompt("Enter decision (Accept/Minor/Major/Reject):")
    if (decision?.toLowerCase().includes('minor')) {
      alert("Decision Sent: Minor Revision")
    } else {
      alert("Decision Submitted to EIC for Approval")
    }
  } else {
    alert("Opening Decision Interface")
  }
}

</script>

<template>
  <div class="editor-page">
    <div class="page-header">
      <h2>Manuscript Management</h2>
      <div class="role-badge">Current Role: {{ user?.role }}</div>
    </div>

    <div class="tabs">
      <div class="tab-group">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'all' }"
          @click="activeTab = 'all'"
        >
          All Manuscripts
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'assigned' }"
          @click="activeTab = 'assigned'"
        >
          My Assigned
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'pending' }"
          @click="activeTab = 'pending'"
        >
          Pending Action
        </button>
      </div>
      
      <div class="search-container">
        <div class="search-wrapper">
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="Search by Manuscript ID, Title, Author..." 
            class="search-input"
            @focus="showSearchHistory = true"
            @blur="setTimeout(() => showSearchHistory = false, 200)"
          />
          <!-- Search History Dropdown -->
          <div v-if="showSearchHistory && searchHistory.length > 0" class="search-history-dropdown">
            <div class="history-header">
              <span>Search History</span>
              <button @click.stop="clearHistory" class="clear-history-btn">Clear</button>
            </div>
            <div 
              v-for="(item, index) in searchHistory" 
              :key="index" 
              class="history-item"
              @click="selectHistory(item)"
            >
              {{ item }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="manuscript-list">
      <div v-if="filteredManuscripts.length === 0" class="empty-state">
        No matching tasks found
      </div>
      <div v-else v-for="ms in filteredManuscripts" :key="ms.id" class="manuscript-card">
        <div class="ms-header">
          <span class="ms-id">{{ ms.id }}</span>
          <span class="ms-status" :class="ms.status.toLowerCase().replace(' ', '-')">{{ ms.status }}</span>
        </div>
        <h3 class="ms-title">{{ ms.title }}</h3>
        <div class="ms-meta">
          <span>Author: {{ ms.author }}</span>
          <span>Field: {{ ms.field }}</span>
          <span>Date: {{ ms.submittedDate }}</span>
        </div>
        
        <div class="ms-actions" v-if="!isReadOnly">
          
          <!-- State: Submitted -->
          <template v-if="ms.status === 'Submitted'">
            <!-- Row 1: Core Actions (Left) -->
            <div class="action-row left">
              <button 
                v-if="canFormatCheck" 
                class="action-btn"
                :class="ms.formatChecked ? 'gray' : 'blue'"
                :disabled="ms.formatChecked"
                @click="handleFormatCheck(ms.id)"
              >
                Format Check
              </button>
              <button v-if="canFormatCheck" class="action-btn blue" @click="handleDeskReject(ms.id)">Desk Reject</button>
              <button 
                v-if="canInitialReview" 
                class="action-btn"
                :class="ms.formatChecked ? 'blue' : 'gray'"
                :disabled="!ms.formatChecked"
                @click="handleInitialReview(ms.id)"
              >
                Initial Review
              </button>
            </div>
            
            <!-- Row 2: Auxiliary Actions (Left) -->
            <div class="action-row left">
              <button v-if="canAssignReviewer && !ms.assignedTo" class="action-btn blue" @click="handleAssignReviewer(ms.id)">Assign to Editor</button>
              <button 
                v-if="canInitialReview" 
                class="action-btn"
                :class="ms.needsRevision ? 'blue' : 'gray'"
                :disabled="!ms.needsRevision"
                @click="handleRequestRevision(ms.id)"
              >
                Request Revision
              </button>
              <button v-if="user?.role === 'editor'" class="action-btn red" @click="handleWithdraw(ms.id)">Withdraw Manuscript</button>
            </div>
          </template>

          <!-- Row 3: Utility Actions (Right) - Common for all states -->
          <div class="action-row right">
             <button v-if="canInitialReview" class="action-btn gray-small" @click="handleAddNote(ms.id)">Add Note</button>
             <button class="action-btn gray-small" @click="handleViewHistory(ms.id)">View History</button>
          </div>

        </div>
        <div class="read-only-msg" v-else>
          <em>Read Only View (Advisory Editor)</em>
        </div>
      </div>
    </div>

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

    <DraftDecisionModal
      :visible="showDecisionModal"
      :manuscript="decisionJournal"
      :current-user="user"
      @close="showDecisionModal = false"
      @submit="handleDecisionSubmit"
      @save-draft="() => {}"
    />

    <ActionModal
      :visible="showActionModal"
      :manuscript="actionJournal"
      :action-type="currentActionType"
      :current-user="user"
      @close="showActionModal = false"
      @submit="handleActionSubmit"
    />
  </div>
</template>

<style scoped>
.editor-page {
  padding: 2rem;
  max-width: 1200px;
  margin: 60px auto 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.role-badge {
  background: #e0e0e0;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: bold;
  text-transform: uppercase;
  font-size: 0.8rem;
  color: #555;
}

.tabs {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  border-bottom: 1px solid #ddd;
  padding-bottom: 1rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.tab-group {
  display: flex;
  gap: 1rem;
}

.search-container {
  flex-grow: 1;
  max-width: 400px;
}

.search-wrapper {
  position: relative;
  width: 100%;
}

.search-input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.search-history-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  background: white;
  border: 1px solid #ddd;
  border-top: none;
  border-radius: 0 0 4px 4px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 10;
}

.history-header {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 0.8rem;
  color: #888;
  background: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.clear-history-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 0.8rem;
}

.clear-history-btn:hover {
  color: #C93737;
}

.history-item {
  padding: 8px 12px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #333;
}

.history-item:hover {
  background: #f0f0f0;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #888;
  background: #f9f9f9;
  border-radius: 8px;
  font-style: italic;
}

.tab-btn {
  background: none;
  border: none;
  font-size: 1rem;
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: #666;
  border-radius: 5px;
}

.tab-btn.active {
  background: #3498db;
  color: white;
}

.manuscript-card {
  background: white;
  border: 1px solid #eee;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.ms-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.ms-id {
  font-family: monospace;
  color: #888;
}

.ms-status {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.ms-status.submitted { background: #e3f2fd; color: #1976d2; }
.ms-status.under-review { background: #fff3e0; color: #f57c00; }
.ms-status.pending-decision { background: #fce4ec; color: #c2185b; }

.ms-title {
  margin: 0.5rem 0;
  color: #2c3e50;
}

.ms-meta {
  font-size: 0.9rem;
  color: #666;
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
}

.ms-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #f0f0f0;
}

.action-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 8px; /* 8-10px spacing between rows */
}

.action-row.left {
  justify-content: flex-start;
  gap: 8px; /* 6-8px spacing between buttons */
}

.action-row.right {
  justify-content: flex-end;
  gap: 8px;
}

.action-btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

/* Lancet Style Colors */
.action-btn.blue {
  background-color: #165DFF;
  color: white;
}
.action-btn.blue:hover {
  background-color: #134BC0;
}

.action-btn.gray {
  background-color: #E5E7EB;
  color: #6B7280;
  cursor: not-allowed;
}

.action-btn.gray-small {
  background-color: #E5E7EB;
  color: #374151;
  padding: 0.3rem 0.8rem;
  font-size: 0.8rem;
}
.action-btn.gray-small:hover {
  background-color: #D1D5DB;
}

.action-btn.red {
  background-color: #F53F3F;
  color: white;
}
.action-btn.red:hover {
  background-color: #D12D2D;
}

.read-only-msg {
  color: #999;
  font-size: 0.9rem;
  padding-top: 0.5rem;
}
</style>