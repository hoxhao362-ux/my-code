<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useI18n } from '../../composables/useI18n'
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
const route = useRoute()
const userStore = useUserStore()
const { t } = useI18n()
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

// Simulated Manuscript Data (Replaced with Store Data)
const manuscripts = ref([])

// Sync from Store
const syncFromStore = () => {
  manuscripts.value = userStore.journals.map(j => ({
    ...j,
    author: j.writer, // Alias
    submittedDate: j.date || j.submissionDate || '2026-01-01',
    field: j.module || 'General',
    assignedTo: j.assignedEditor || j.assignedTo
  }))
}

// Watch Store Changes
watch(() => userStore.journals, syncFromStore, { deep: true })

// Helper to update store
const updateManuscript = (journal) => {
  userStore.updateJournal(journal)
}

onMounted(() => {
    syncFromStore()
    // Load history
    const history = localStorage.getItem('manuscript_search_history')
    if (history) {
      searchHistory.value = JSON.parse(history)
    }
    
    // Check query param for status filter
    if (route.query.status) {
      selectedStatus.value = route.query.status
    }
  })

const activeTab = ref('all')

// --- Filter State ---
const selectedStatus = ref('all')
const selectedDateRange = ref('custom') // custom, today, this_week, this_month, this_year
const dateRange = ref({ start: '', end: '' })
const showAdvancedFilters = ref(false)
const advancedFilters = ref({ writer: '', field: '' })

// Date range options
const dateRangeOptions = computed(() => [
  { label: t('editor.manuscripts.dateRanges.custom'), value: 'custom' },
  { label: t('editor.manuscripts.dateRanges.today'), value: 'today' },
  { label: t('editor.manuscripts.dateRanges.thisWeek'), value: 'this_week' },
  { label: t('editor.manuscripts.dateRanges.thisMonth'), value: 'this_month' },
  { label: t('editor.manuscripts.dateRanges.thisYear'), value: 'this_year' }
])

// Calculate date range based on selected option
const calculateDateRange = () => {
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  
  switch (selectedDateRange.value) {
    case 'today':
      dateRange.value.start = today.toISOString().split('T')[0]
      dateRange.value.end = today.toISOString().split('T')[0]
      break
    case 'this_week':
      const startOfWeek = new Date(today)
      startOfWeek.setDate(today.getDate() - today.getDay())
      dateRange.value.start = startOfWeek.toISOString().split('T')[0]
      dateRange.value.end = today.toISOString().split('T')[0]
      break
    case 'this_month':
      const startOfMonth = new Date(today.getFullYear(), today.getMonth(), 1)
      dateRange.value.start = startOfMonth.toISOString().split('T')[0]
      dateRange.value.end = today.toISOString().split('T')[0]
      break
    case 'this_year':
      const startOfYear = new Date(today.getFullYear(), 0, 1)
      dateRange.value.start = startOfYear.toISOString().split('T')[0]
      dateRange.value.end = today.toISOString().split('T')[0]
      break
    default:
      // Custom range - keep current values
      break
  }
}

// Watch for date range option changes
watch(selectedDateRange, calculateDateRange)

// Watch for route query changes to update status filter
watch(() => route.query.status, (newStatus) => {
  if (newStatus) {
    selectedStatus.value = newStatus
  }
})

const statusOptions = computed(() => [
  { label: t('statusFilter.all'), value: 'all' },
  { label: t('statusFilter.pendingScreening'), value: 'pending_screening' },
  { label: t('statusFilter.underReview'), value: 'under_review' },
  { label: t('statusFilter.decisionPending'), value: 'decision_pending' },
  { label: t('statusFilter.accepted'), value: 'accepted' },
  { label: t('statusFilter.rejected'), value: 'rejected' },
  { label: t('statusFilter.inProduction'), value: 'in_production' }
])

const fieldOptions = ['Medical Imaging', 'Drug Delivery', 'Clinical Research', 'Public Health', 'Genetics', 'Cardiology']

const resetFilters = () => {
  selectedStatus.value = 'all'
  selectedDateRange.value = 'custom'
  dateRange.value = { start: '', end: '' }
  advancedFilters.value = { writer: '', field: '' }
  searchKeyword.value = ''
}

const filteredManuscripts = computed(() => {
  let list = manuscripts.value
  
  // 1. Keyword Search (Existing)
  if (debouncedKeyword.value) {
    const keyword = debouncedKeyword.value.toLowerCase()
    list = list.filter(m => 
      m.id.toLowerCase().includes(keyword) ||
      m.title.toLowerCase().includes(keyword) ||
      (m.writer || m.author).toLowerCase().includes(keyword) ||
      m.field.toLowerCase().includes(keyword)
    )
  }
  
  // 2. Role Scope (Existing)
  if (user.value?.role === 'editor') {
     if (activeTab.value === 'assigned') {
        list = list.filter(m => m.assignedTo === user.value.username)
     }
  } else if (user.value?.role === 'editorial_assistant') {
     if (activeTab.value === 'assigned') {
        list = list.filter(m => m.assignedTo === user.value.username)
     }
  }

  // 3. Tab filtering (Existing)
  if (activeTab.value === 'pending') {
    list = list.filter(m => [
      MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW, 
      MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW, 
      MANUSCRIPT_STATUS.UNDER_PEER_REVIEW, 
      MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
      MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
    ].includes(m.status))
  }
  
  // 4. Status Filter (New)
  if (selectedStatus.value !== 'all') {
    list = list.filter(m => {
      switch (selectedStatus.value) {
        case 'pending_screening':
          return [MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW, MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW].includes(m.status)
        case 'under_review':
          return [
            MANUSCRIPT_STATUS.PENDING_PEER_REVIEW,
            MANUSCRIPT_STATUS.UNDER_PEER_REVIEW,
            MANUSCRIPT_STATUS.REVIEW_COMPLETED,
            MANUSCRIPT_STATUS.REVISION_REQUIRED,
            MANUSCRIPT_STATUS.REVISION_SUBMITTED
          ].includes(m.status)
        case 'decision_pending':
          return [MANUSCRIPT_STATUS.PENDING_FINAL_DECISION, MANUSCRIPT_STATUS.UNDER_FINAL_DECISION, MANUSCRIPT_STATUS.FINAL_DECISION_REVISION].includes(m.status)
        case 'accepted':
          return m.status === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
        case 'rejected':
          return [MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED, MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED].includes(m.status)
        case 'in_production':
          return [
            MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION, 
            MANUSCRIPT_STATUS.PENDING_COPYRIGHT, 
            MANUSCRIPT_STATUS.PENDING_PROOF, 
            MANUSCRIPT_STATUS.PENDING_PUBLICATION,
            MANUSCRIPT_STATUS.PUBLISHED
          ].includes(m.status)
        default:
          return true
      }
    })
  }

  // 5. Date Range Filter (New)
  if (dateRange.value.start) {
    list = list.filter(m => new Date(m.submittedDate) >= new Date(dateRange.value.start))
  }
  if (dateRange.value.end) {
    list = list.filter(m => new Date(m.submittedDate) <= new Date(dateRange.value.end))
  }

  // 6. Advanced Filters (New)
  if (advancedFilters.value.writer) {
    const writerKey = advancedFilters.value.writer.toLowerCase()
    list = list.filter(m => (m.writer || m.author || '').toLowerCase().includes(writerKey))
  }
  if (advancedFilters.value.field) {
    list = list.filter(m => m.field === advancedFilters.value.field)
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
const getStatusLabel = (s) => t(`status.${s}`) || s
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
  
  // Navigate to publication process page
  router.push({ name: 'editor-publication-process', params: { id } })
}

</script>

<template>
  <div class="editor-page">
    
    <!-- Full Screen Overlay for Heavy Tasks -->
    <div v-if="showChecklist || showFinalDecision || showReviewSummary || showAuditLog || showRevisionCheck" class="fullscreen-overlay">
      <div class="overlay-header">
        <button class="btn-back" @click="showChecklist = false; showFinalDecision = false; showReviewSummary = false; showAuditLog = false; showRevisionCheck = false">← {{ t('editor.manuscripts.back') }}</button>
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
        <h2>{{ t('editor.manuscripts.title') }}</h2>
        <div class="role-badge">{{ t('editor.manuscripts.currentRole') }}: {{ user?.role }}</div>
      </div>

      <div class="tabs">
        <div class="tab-group">
          <button class="tab-btn" :class="{ active: activeTab === 'all' }" @click="activeTab = 'all'">{{ t('editor.manuscripts.tabs.all') }}</button>
          <button class="tab-btn" :class="{ active: activeTab === 'assigned' }" @click="activeTab = 'assigned'">{{ t('editor.manuscripts.tabs.assigned') }}</button>
          <button class="tab-btn" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">{{ t('editor.manuscripts.tabs.pending') }}</button>
        </div>
        
        <div class="search-container">
          <div class="search-wrapper">
            <input type="text" v-model="searchKeyword" :placeholder="t('editor.manuscripts.search.placeholder')" class="search-input" @focus="showSearchHistory = true" @blur="setTimeout(() => showSearchHistory = false, 200)" />
          </div>
        </div>
      </div>

      <!-- Filters Bar (New) -->
      <div class="filters-bar">
        <!-- Row 1: Status, Date, Advanced Toggle, Reset -->
        <div class="filter-row">
           <div class="filter-group">
              <label>{{ t('editor.manuscripts.filter.status') }}</label>
              <select v-model="selectedStatus" class="filter-select">
                <option v-for="opt in statusOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
              </select>
           </div>
           <div class="filter-group">
              <label>{{ t('editor.manuscripts.filter.dateRange') }}</label>
              <select v-model="selectedDateRange" class="filter-select date-range-select">
                <option v-for="option in dateRangeOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
           </div>
           <div class="filter-actions">
              <button class="btn-text filter-toggle" @click="showAdvancedFilters = !showAdvancedFilters">
                {{ showAdvancedFilters ? t('editor.manuscripts.filter.hideAdvanced') : t('editor.manuscripts.filter.advanced') }}
                <span class="toggle-icon">{{ showAdvancedFilters ? '▲' : '▼' }}</span>
              </button>
              <button class="btn-text reset-btn" @click="resetFilters">{{ t('editor.manuscripts.filter.reset') }}</button>
           </div>
        </div>
        
        <!-- Row 2: Advanced Panel -->
        <transition name="slide-fade">
          <div v-if="showAdvancedFilters" class="advanced-panel">
             <div class="filter-group">
                <label>{{ t('editor.manuscripts.filter.writer') }}</label>
                <input type="text" v-model="advancedFilters.writer" :placeholder="t('editor.manuscripts.filter.writer')" class="filter-input">
             </div>
             <div class="filter-group">
                <label>{{ t('editor.manuscripts.filter.field') }}</label>
                <select v-model="advancedFilters.field" class="filter-select">
                   <option value="">{{ t('editor.manuscripts.filter.allFields') }}</option>
                   <option v-for="f in fieldOptions" :key="f" :value="f">{{ f }}</option>
                </select>
             </div>
          </div>
        </transition>
      </div>

      <div class="manuscript-list">
        <div v-if="filteredManuscripts.length === 0" class="empty-state">
          <p>{{ t('editor.manuscripts.noManuscripts') }}</p>
          <button class="btn-text" @click="resetFilters">{{ t('editor.manuscripts.filter.reset') }}</button>
        </div>
        <div v-else v-for="ms in filteredManuscripts" :key="ms.id" class="manuscript-card">
          <div class="ms-header">
            <span class="ms-id">{{ ms.id }}</span>
            <span class="ms-status-badge" :style="{ backgroundColor: getStatusColor(ms.status), color: 'white' }">{{ getStatusLabel(ms.status) }}</span>
          </div>
          <h3 class="ms-title clickable-title" @click="router.push({ name: 'admin-journal-detail', params: { id: ms.id } })">
            {{ ms.title }}
          </h3>
          <div class="ms-meta">
            <span>{{ t('editor.manuscripts.columns.writer') }}: {{ ms.writer || ms.author }}</span>
            <span>{{ t('editor.manuscripts.columns.field') }}: {{ ms.field }}</span>
            <span>{{ t('editor.manuscripts.columns.date') }}: {{ ms.submittedDate }}</span>
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
                 <button class="action-btn red" @click="handleStartPublication(ms.id)">Start Publication Process</button>
               </div>
            </template>

            <!-- 8. Publication Phase (New) -->
            <template v-if="[
                MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION, 
                MANUSCRIPT_STATUS.PENDING_COPYRIGHT, 
                MANUSCRIPT_STATUS.PENDING_PROOF, 
                MANUSCRIPT_STATUS.PENDING_PUBLICATION,
                MANUSCRIPT_STATUS.PUBLISHED
              ].includes(ms.status)">
               <div class="action-row left">
                 <button class="action-btn red" @click="handleStartPublication(ms.id)">
                   {{ ms.status === MANUSCRIPT_STATUS.PUBLISHED ? 'View Publication Details' : 'Continue Publication Process' }}
                 </button>
                 <span class="hint-text">Current Stage: {{ getStatusLabel(ms.status) }}</span>
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
.tabs { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem; flex-wrap: wrap; gap: 1rem; }
.tab-group { display: flex; gap: 1rem; }
.search-container { flex-grow: 1; max-width: 400px; }
.search-input { width: 100%; padding: 0.5rem 1rem; border: 1px solid #ddd; border-radius: 4px; }

/* Filters Bar */
.filters-bar {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.filter-row {
  display: flex;
  gap: 2rem;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #555;
}

.filter-select, .filter-input {
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 180px;
  font-size: 0.95rem;
  color: #333;
}

.filter-input.date {
  min-width: 140px;
}

.date-range-select {
  min-width: 180px;
}

.filter-actions {
  margin-left: auto;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.filter-toggle {
  color: #3498db;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-icon {
  font-size: 0.8rem;
}

.reset-btn {
  color: #999;
}

.reset-btn:hover {
  color: #666;
  text-decoration: underline;
}

.advanced-panel {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px dashed #eee;
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

/* Transitions */
.slide-fade-enter-active {
  transition: all 0.3s ease-out;
}

.slide-fade-leave-active {
  transition: all 0.2s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}

.tab-btn { background: none; border: none; font-size: 1rem; padding: 0.5rem 1rem; cursor: pointer; color: #666; border-radius: 5px; }
.tab-btn.active { background: #3498db; color: white; }

.manuscript-card { background: white; border: 1px solid #eee; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.ms-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
.ms-id { font-family: monospace; color: #888; }
.ms-status-badge { padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
.ms-title { margin: 0.5rem 0; color: #2c3e50; }
.clickable-title { cursor: pointer; transition: color 0.2s; }
.clickable-title:hover { color: #C93737; text-decoration: underline; }
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
