<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'
import { stripHtmlTags, truncateText } from '../../../utils/helpers.js'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'
import { useI18n } from '../../../composables/useI18n'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Filter for New Submissions
const pendingJournals = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW || 
    // Legacy support
    journal.status === 'Submitted' || 
    journal.status === 'Pending Screening'
  )
})

// --- Modals State ---
const currentJournal = ref(null)
const showScreenModal = ref(false)
const showTransferModal = ref(false)
const showRejectModal = ref(false)

// --- View Details State ---
const showManuscriptModal = ref(false)
const showAttachmentsModal = ref(false)
const showEthicsModal = ref(false)
const ethicsVerified = ref(false)

// --- View Manuscript State ---
const zoomLevel = ref(100)
const currentPage = ref(1)
const totalPages = ref(10) // Mock total pages
const isFullScreen = ref(false)

const openManuscriptModal = (journal) => {
  currentJournal.value = journal
  showManuscriptModal.value = true
  // Reset state
  zoomLevel.value = 100
  currentPage.value = 1
  isFullScreen.value = false
}

const handleZoomIn = () => {
  if (zoomLevel.value < 200) zoomLevel.value += 10
}

const handleZoomOut = () => {
  if (zoomLevel.value > 50) zoomLevel.value -= 10
}

const handleNextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const handlePrevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const toggleFullScreen = () => {
  const elem = document.querySelector('.modal-content')
  if (!document.fullscreenElement) {
    elem.requestFullscreen().catch(err => {
      toastStore.add({ message: `Error attempting to enable full-screen mode: ${err.message}`, type: 'error' })
    })
    isFullScreen.value = true
  } else {
    document.exitFullscreen()
    isFullScreen.value = false
  }
}

// --- View Attachments State ---
const previewFile = ref(null)
const isRefreshingList = ref(false)
const isPreparingDownload = ref(false)

const openAttachmentsModal = (journal) => {
  currentJournal.value = journal
  showAttachmentsModal.value = true
  previewFile.value = null
  isRefreshingList.value = false
}

const viewAttachment = (fileName, type) => {
  if (type === 'image' || type === 'pdf') {
    previewFile.value = { name: fileName, type }
  } else {
    toastStore.add({ message: t('editor.audit.newSubmissions.alerts.previewUnavailable'), type: 'warning' })
  }
}

const closePreview = () => {
  previewFile.value = null
}

const downloadAllAttachments = () => {
  if (isPreparingDownload.value) return
  isPreparingDownload.value = true
  setTimeout(() => {
    isPreparingDownload.value = false
    toastStore.add({ message: t('editor.audit.newSubmissions.alerts.downloadStarted'), type: 'success' })
  }, 1500)
}

const refreshAttachmentList = () => {
  if (isRefreshingList.value) return
  isRefreshingList.value = true
  setTimeout(() => {
    isRefreshingList.value = false
  }, 1500)
}

// --- Ethics Statement State ---
const isVerifying = ref(false)
const showRevisionRequest = ref(false)
const revisionComments = ref('')

const openEthicsModal = (journal) => {
  currentJournal.value = journal
  ethicsVerified.value = journal.ethicsVerified || false
  showEthicsModal.value = true
  showRevisionRequest.value = false
}

const verifyEthics = () => {
  isVerifying.value = true
  setTimeout(() => {
    const updatedJournal = { ...currentJournal.value }
    updatedJournal.ethicsVerified = true
    updatedJournal.ethicsStatus = 'Verified'
    userStore.updateJournal(updatedJournal)
    ethicsVerified.value = true
    isVerifying.value = false
  }, 1000)
}

const unverifyEthics = () => {
  isVerifying.value = true
  setTimeout(() => {
    const updatedJournal = { ...currentJournal.value }
    updatedJournal.ethicsVerified = false
    updatedJournal.ethicsStatus = 'Pending Verification'
    userStore.updateJournal(updatedJournal)
    ethicsVerified.value = false
    isVerifying.value = false
  }, 1000)
}

const openRevisionRequest = () => {
  showRevisionRequest.value = true
}

const sendRevisionRequest = () => {
  const updatedJournal = { ...currentJournal.value }
  updatedJournal.ethicsStatus = 'Revision Requested'
  userStore.updateJournal(updatedJournal)
  showRevisionRequest.value = false
  toastStore.add({ message: t('editor.audit.newSubmissions.alerts.revisionSent'), type: 'success' })
}

const printStatement = () => {
  window.print()
}

const downloadFile = (fileName) => {
  toastStore.add({ message: t('editor.audit.newSubmissions.alerts.downloading', { name: fileName }), type: 'info' })
}

const toggleTransferPreview = ref(false)
const rejectReasonGroup = ref({
  'Scope & Novelty': false,
  'Methodology': false,
  'Presentation': false
})
const activeRejectGroup = ref('')

const toggleRejectGroup = (group) => {
  activeRejectGroup.value = activeRejectGroup.value === group ? '' : group
}
// --- Screen & Send Logic ---
const screenForm = ref({
  notes: '',
  assignmentType: 'auto', // 'auto' | 'specific'
  selectedEditorId: null,
  selectedEditorName: ''
})

const editorsList = ref([])
const isLoadingEditors = ref(false)
const isEditorsDropdownOpen = ref(false)
const showValidationModal = ref(false)
const assignStatus = ref('')
const noEditorsAvailable = ref(false)

// Watch assignment type to fetch editors
const handleAssignmentTypeChange = async () => {
  if (screenForm.value.assignmentType === 'specific') {
    if (editorsList.value.length === 0) {
      isLoadingEditors.value = true
      noEditorsAvailable.value = false
      try {
        const list = await userStore.fetchEditorsList()
        editorsList.value = list
        
        if (list.length === 0) {
          noEditorsAvailable.value = true
          screenForm.value.assignmentType = 'auto' // Auto-switch back
        }
      } catch (e) {
        console.error(e)
        editorsList.value = []
        noEditorsAvailable.value = true
        screenForm.value.assignmentType = 'auto' // Auto-switch back
      } finally {
        isLoadingEditors.value = false
      }
    } else {
      // List already loaded, but check if empty (shouldn't happen if logic works)
      if (editorsList.value.length === 0) {
         noEditorsAvailable.value = true
         screenForm.value.assignmentType = 'auto'
      }
    }
  } else {
    // Reset selection if switching back to auto
    screenForm.value.selectedEditorId = null
    screenForm.value.selectedEditorName = ''
    assignStatus.value = ''
    noEditorsAvailable.value = false
  }
}

const toggleEditorsDropdown = () => {
  // Always toggle to allow showing "Loading..." or "No active editors" messages
  isEditorsDropdownOpen.value = !isEditorsDropdownOpen.value
}

const selectEditor = (editor) => {
  screenForm.value.selectedEditorId = editor.id
  screenForm.value.selectedEditorName = editor.name
  isEditorsDropdownOpen.value = false
  assignStatus.value = '' // Reset status until confirmed
}

const clearEditorSelection = (e) => {
  e.stopPropagation()
  screenForm.value.selectedEditorId = null
  screenForm.value.selectedEditorName = ''
  isEditorsDropdownOpen.value = true // Keep open to allow re-selection
}

const openScreenModal = (journal) => {
  currentJournal.value = journal
  screenForm.value = { notes: '', assignmentType: 'auto', selectedEditorId: null, selectedEditorName: '' }
  assignStatus.value = ''
  showScreenModal.value = true
}

const closeValidationModal = () => {
  showValidationModal.value = false
}

const confirmScreen = async () => {
  // Validation for specific assignment
  if (screenForm.value.assignmentType === 'specific' && !screenForm.value.selectedEditorId) {
    showValidationModal.value = true
    return
  }

  const updatedJournal = { ...currentJournal.value }
  
  if (screenForm.value.notes) {
    updatedJournal.screeningNotes = screenForm.value.notes
  }
  
  // Logic for assignment
  if (screenForm.value.assignmentType === 'specific') {
    try {
      // 1. Assign Editor
      await userStore.assignEditorToManuscript(updatedJournal.id, screenForm.value.selectedEditorId)
      
      // 2. Sync Task
      await userStore.assignTaskToEditor(screenForm.value.selectedEditorId, {
        taskName: `Assign Reviewers - ${updatedJournal.title}`,
        status: 'Pending',
        manuscriptId: updatedJournal.id
      })
      
      assignStatus.value = `${t('common.status')}: Assigned to ${screenForm.value.selectedEditorName}`
      
      // Add Log
      userStore.addSystemLog({
        type: 'operation',
        user: user.value?.username || 'editor',
        action: 'Editor Assigned',
        target: `Manuscript ID: ${updatedJournal.id} assigned to ${screenForm.value.selectedEditorName}`
      })
      
    } catch (error) {
      toastStore.add({ message: t('editor.audit.newSubmissions.alerts.assignmentFailed'), type: 'error' })
      return
    }
  } else {
    updatedJournal.status = 'reviewer_assignment_pending'
    updatedJournal.assignedEditor = null 
    userStore.updateJournal(updatedJournal)
    
    userStore.addSystemLog({
      type: 'operation',
      user: user.value?.username || 'editor',
      action: 'Initial Review Passed',
      target: `Manuscript ID: ${updatedJournal.id} (Auto-assigned to Pool)`
    })
  }

  showScreenModal.value = false
  toastStore.add({ message: t('editor.audit.newSubmissions.alerts.screenConfirmed'), type: 'success' })
}

// --- Suggest Transfer Logic ---
const transferForm = reactive({
  reason: '',
  targetJournal: 'Journal of Medical Science',
  letter: ''
})

const transferJournals = ['Journal of Medical Science', 'Journal of Medical Imaging', 'Global Health Journal']

const openTransferModal = (journal) => {
  currentJournal.value = journal
  Object.assign(transferForm, {
    reason: '',
    targetJournal: 'Journal of Medical Science',
    letter: t('editor.audit.newSubmissions.modals.transfer.letterTemplate', {
      author: journal.author,
      title: journal.title,
      targetJournal: 'Journal of Medical Science',
      journalName: t('common.journalName')
    })
  })
  showTransferModal.value = true
}

const sendTransfer = () => {
  if (!transferForm.reason) {
    toastStore.add({ message: t('editor.audit.newSubmissions.alerts.transferReasonRequired'), type: 'warning' })
    return
  }

  const updatedJournal = { ...currentJournal.value }
  updatedJournal.status = 'transfer_suggested'
  userStore.updateJournal(updatedJournal)

  showTransferModal.value = false
  toastStore.add({ message: t('editor.audit.newSubmissions.alerts.transferSent'), type: 'success' })
}

// --- Reject Logic ---
const rejectForm = ref({
  reasons: [],
  otherReason: '',
  comments: '',
  template: 'Standard Template'
})

const openRejectModal = (journal) => {
  currentJournal.value = journal
  rejectForm.value = {
    reasons: [],
    otherReason: '',
    comments: '',
    template: 'Standard Template'
  }
  showRejectModal.value = true
}

const confirmReject = () => {
  if (rejectForm.value.reasons.length === 0 || !rejectForm.value.comments) {
    toastStore.add({ message: t('editor.audit.newSubmissions.alerts.fieldsRequired'), type: 'warning' })
    return
  }
  
  if (rejectForm.value.reasons.includes('Other') && !rejectForm.value.otherReason) {
    toastStore.add({ message: t('editor.audit.newSubmissions.alerts.specifyOther'), type: 'warning' })
    return
  }

  const updatedJournal = { ...currentJournal.value }
  updatedJournal.status = MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED
  
  updatedJournal.screeningNotes = `[Initial Screening Rejection]\nReasons: ${rejectForm.value.reasons.join(', ')}\nComments: ${rejectForm.value.comments}`
  
  userStore.updateJournal(updatedJournal)

  showRejectModal.value = false
  toastStore.add({ message: t('editor.audit.newSubmissions.alerts.rejectConfirmed'), type: 'success' })
}

const viewDetail = (id) => {
  router.push(`/admin/journal/${id}`)
}
</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-new-submissions" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>{{ t('editor.audit.newSubmissions.title') }}</h1>
        <p class="subtitle">{{ t('editor.audit.newSubmissions.subtitle') }}</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in pendingJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title" @click="viewDetail(journal.id)">{{ journal.title }}</h3>
            <div class="journal-meta">
              <span><strong>{{ t('editor.audit.newSubmissions.columns.author') }}:</strong> {{ journal.author }}</span>
              <span><strong>{{ t('editor.audit.newSubmissions.columns.date') }}:</strong> {{ journal.date }}</span>
              <span><strong>{{ t('editor.audit.newSubmissions.columns.module') }}:</strong> {{ journal.module }}</span>
            </div>
            <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract), 200) }}</p>
            <div class="materials-links">
              <a href="#" @click.prevent="openManuscriptModal(journal)" class="link">{{ t('editor.audit.newSubmissions.links.viewManuscript') }}</a>
              <a href="#" @click.prevent="openAttachmentsModal(journal)" class="link">{{ t('editor.audit.newSubmissions.links.viewAttachments') }}</a>
              <a href="#" @click.prevent="openEthicsModal(journal)" class="link">{{ t('editor.audit.newSubmissions.links.ethicsStatement') }}</a>
            </div>
          </div>
          <div class="journal-actions">
            <button class="btn btn-primary" @click="openScreenModal(journal)">{{ t('editor.audit.newSubmissions.actions.screen') }}</button>
            <button class="btn btn-warning" @click="openTransferModal(journal)">{{ t('editor.audit.newSubmissions.actions.transfer') }}</button>
            <button class="btn btn-danger" @click="openRejectModal(journal)">{{ t('editor.audit.newSubmissions.actions.reject') }}</button>
          </div>
        </div>
        <div v-if="pendingJournals.length === 0" class="no-data">
          {{ t('editor.audit.newSubmissions.noData') }}
        </div>
      </div>
    </main>

    <!-- 1. Screen & Send Modal -->
    <div v-if="showScreenModal" class="modal-overlay">
      <div class="modal-content fixed-size-modal screen-modal">
        <div class="modal-header">
          <h2>{{ t('editor.audit.newSubmissions.modals.screen.title') }}</h2>
        </div>
        
        <div class="modal-body">
          <div class="modal-section info-section">
            <p><strong>{{ t('common.title') }}:</strong> {{ currentJournal?.title }}</p>
            <p><strong>{{ t('common.author') }}:</strong> {{ currentJournal?.author }}</p>
            <p><strong>{{ t('common.module') }}:</strong> {{ currentJournal?.module }}</p>
            <p><strong>{{ t('editor.audit.newSubmissions.columns.date') }}:</strong> {{ currentJournal?.date }}</p>
          </div>

          <div class="modal-section">
            <label class="input-label">{{ t('editor.audit.newSubmissions.modals.screen.notesLabel') }}</label>
            <textarea v-model="screenForm.notes" :placeholder="t('editor.audit.newSubmissions.modals.screen.notesPlaceholder')" class="jp-input short-textarea"></textarea>
          </div>

          <div class="modal-section">
            <label class="input-label">{{ t('editor.audit.newSubmissions.modals.screen.assignmentLabel') }}</label>
            <div class="radio-group">
              <label class="radio-item">
                <input type="radio" v-model="screenForm.assignmentType" value="auto" @change="handleAssignmentTypeChange">
                {{ t('editor.audit.newSubmissions.modals.screen.autoAssign') }}
              </label>
              <label class="radio-item">
                <input type="radio" v-model="screenForm.assignmentType" value="specific" @change="handleAssignmentTypeChange" :disabled="noEditorsAvailable">
                {{ t('editor.audit.newSubmissions.modals.screen.specificAssign') }}
              </label>
            </div>
            
            <div v-if="noEditorsAvailable" class="warning-text">
              {{ t('editor.audit.newSubmissions.modals.screen.noEditors') }}
            </div>

            <div v-if="screenForm.assignmentType === 'specific'" class="sub-option">
               <div class="custom-dropdown" @click="toggleEditorsDropdown">
                 <div class="dropdown-header" :class="{ 'placeholder': !screenForm.selectedEditorId }">
                   {{ screenForm.selectedEditorName || t('editor.audit.newSubmissions.modals.screen.selectEditor') }}
                 </div>
                 <div v-if="isEditorsDropdownOpen" class="dropdown-list">
                   <div v-if="isLoadingEditors" class="dropdown-status">{{ t('editor.audit.newSubmissions.modals.screen.loadingEditors') }}</div>
                   <div v-else-if="editorsList.length === 0" class="dropdown-status">{{ t('editor.audit.newSubmissions.modals.screen.noActiveEditors') }}</div>
                   <template v-else>
                     <div 
                       v-for="editor in editorsList" 
                       :key="editor.id" 
                       class="dropdown-item" 
                       :class="{ 'selected': screenForm.selectedEditorId === editor.id }"
                       @click.stop="selectEditor(editor)"
                     >
                       {{ editor.name }} ({{ editor.email }})
                     </div>
                   </template>
                 </div>
               </div>
            </div>
          </div>
        </div>

        <div class="modal-footer fixed-footer">
          <div v-if="assignStatus" class="status-text">{{ assignStatus }}</div>
          <button class="btn btn-secondary" @click="showScreenModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" 
            @click="confirmScreen"
            :class="{ 'disabled-grey': screenForm.assignmentType === 'specific' && !screenForm.selectedEditorId }"
          >{{ t('editor.audit.newSubmissions.modals.screen.confirmBtn') }}</button>
        </div>
      </div>
    </div>

    <!-- Validation Modal -->
    <div v-if="showValidationModal" class="modal-overlay" style="z-index: 2000;">
      <div class="validation-modal-content">
        <h3>{{ t('editor.audit.newSubmissions.modals.validation.title') }}</h3>
        <p>{{ t('editor.audit.newSubmissions.modals.validation.message') }}</p>
        <div class="validation-footer">
          <button class="btn-text-only-bordered" @click="closeValidationModal">{{ t('common.ok') }}</button>
        </div>
      </div>
    </div>

    <!-- 2. Suggest Transfer Modal -->
    <div v-if="showTransferModal" class="modal-overlay">
      <div class="modal-content fixed-size-modal transfer-modal">
        <div class="modal-header">
          <h2>{{ t('editor.audit.newSubmissions.modals.transfer.title') }}</h2>
        </div>
        
        <div class="modal-body">
          <div class="modal-section info-section">
            <p><strong>{{ t('common.title') }}:</strong> {{ currentJournal?.title }}</p>
            <p><strong>{{ t('common.author') }}:</strong> {{ currentJournal?.author }}</p>
            <p><strong>{{ t('common.module') }}:</strong> {{ currentJournal?.module }}</p>
          </div>

          <div class="modal-section">
            <label class="input-label required">{{ t('editor.audit.newSubmissions.modals.transfer.reasonLabel') }}</label>
            <textarea v-model="transferForm.reason" :placeholder="t('editor.audit.newSubmissions.modals.transfer.reasonPlaceholder')" class="jp-input medium-textarea"></textarea>
          </div>

          <div class="modal-section">
            <label class="input-label">{{ t('editor.audit.newSubmissions.modals.transfer.journalLabel') }}</label>
            <select v-model="transferForm.targetJournal" class="jp-select">
              <option v-for="j in transferJournals" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>

          <div class="modal-section">
            <div class="section-header clickable" @click="toggleTransferPreview = !toggleTransferPreview">
              <label class="input-label">{{ t('editor.audit.newSubmissions.modals.transfer.previewLabel') }} {{ toggleTransferPreview ? '(-)' : '(+)' }}</label>
            </div>
            <textarea v-if="toggleTransferPreview" v-model="transferForm.letter" class="jp-input letter-preview"></textarea>
          </div>
        </div>

        <div class="modal-footer fixed-footer">
          <button class="btn btn-secondary" @click="showTransferModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="sendTransfer" :disabled="!transferForm.reason">{{ t('editor.audit.newSubmissions.modals.transfer.sendBtn') }}</button>
        </div>
      </div>
    </div>

    <!-- 3. Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay">
      <div class="modal-content fixed-size-modal reject-modal">
        <div class="modal-header">
          <h2>{{ t('editor.audit.newSubmissions.modals.reject.title') }}</h2>
        </div>
        
        <div class="modal-body">
          <div class="modal-section info-section">
            <p><strong>{{ t('common.title') }}:</strong> {{ currentJournal?.title }}</p>
            <p><strong>{{ t('common.author') }}:</strong> {{ currentJournal?.author }}</p>
            <p><strong>{{ t('editor.audit.newSubmissions.columns.date') }}:</strong> {{ currentJournal?.date }}</p>
          </div>

          <div class="modal-section">
            <label class="input-label required">{{ t('editor.audit.newSubmissions.modals.reject.reasonLabel') }}</label>
            
            <!-- Group: Scope & Novelty -->
            <div class="reason-group">
              <div class="group-header clickable" @click="toggleRejectGroup('Scope & Novelty')">
                <strong>{{ t('editor.audit.newSubmissions.modals.reject.categories.scope') }}</strong> {{ activeRejectGroup === 'Scope & Novelty' ? '(-)' : '(+)' }}
              </div>
              <div v-show="activeRejectGroup === 'Scope & Novelty'" class="group-content">
                <label class="radio-item"><input type="checkbox" v-model="rejectForm.reasons" :value="t('editor.audit.newSubmissions.modals.reject.reasons.outOfScope')"> {{ t('editor.audit.newSubmissions.modals.reject.reasons.outOfScope') }}</label>
                <label class="radio-item"><input type="checkbox" v-model="rejectForm.reasons" :value="t('editor.audit.newSubmissions.modals.reject.reasons.insufficientNovelty')"> {{ t('editor.audit.newSubmissions.modals.reject.reasons.insufficientNovelty') }}</label>
              </div>
            </div>

            <!-- Group: Methodology -->
            <div class="reason-group">
              <div class="group-header clickable" @click="toggleRejectGroup('Methodology')">
                <strong>{{ t('editor.audit.newSubmissions.modals.reject.categories.methodology') }}</strong> {{ activeRejectGroup === 'Methodology' ? '(-)' : '(+)' }}
              </div>
              <div v-show="activeRejectGroup === 'Methodology'" class="group-content">
                <label class="radio-item"><input type="checkbox" v-model="rejectForm.reasons" :value="t('editor.audit.newSubmissions.modals.reject.reasons.methodologicalFlaws')"> {{ t('editor.audit.newSubmissions.modals.reject.reasons.methodologicalFlaws') }}</label>
                <label class="radio-item"><input type="checkbox" v-model="rejectForm.reasons" :value="t('editor.audit.newSubmissions.modals.reject.reasons.statisticalErrors')"> {{ t('editor.audit.newSubmissions.modals.reject.reasons.statisticalErrors') }}</label>
              </div>
            </div>

            <!-- Group: Presentation & Other -->
            <div class="reason-group">
              <div class="group-header clickable" @click="toggleRejectGroup('Presentation')">
                <strong>{{ t('editor.audit.newSubmissions.modals.reject.categories.presentation') }}</strong> {{ activeRejectGroup === 'Presentation' ? '(-)' : '(+)' }}
              </div>
              <div v-show="activeRejectGroup === 'Presentation'" class="group-content">
                <label class="radio-item"><input type="checkbox" v-model="rejectForm.reasons" :value="t('editor.audit.newSubmissions.modals.reject.reasons.poorPresentation')"> {{ t('editor.audit.newSubmissions.modals.reject.reasons.poorPresentation') }}</label>
                <label class="radio-item"><input type="checkbox" v-model="rejectForm.reasons" value="Other"> {{ t('editor.audit.newSubmissions.modals.reject.otherLabel') }}</label>
                 <div v-if="rejectForm.reasons.includes('Other')" class="sub-option">
                   <input v-model="rejectForm.otherReason" :placeholder="t('editor.audit.newSubmissions.modals.reject.otherLabel')" class="jp-input" />
                </div>
              </div>
            </div>
          </div>

          <div class="modal-section">
            <label class="input-label required">{{ t('editor.audit.newSubmissions.modals.reject.commentsLabel') }}</label>
            <textarea v-model="rejectForm.comments" :placeholder="t('editor.audit.newSubmissions.modals.reject.commentsPlaceholder')" class="jp-input medium-textarea"></textarea>
          </div>

          <div class="modal-section">
            <label class="input-label">{{ t('editor.audit.newSubmissions.modals.reject.templateLabel') }}</label>
            <select v-model="rejectForm.template" class="jp-select">
              <option :value="t('editor.audit.newSubmissions.modals.reject.templates.standard')">{{ t('editor.audit.newSubmissions.modals.reject.templates.standard') }}</option>
              <option :value="t('editor.audit.newSubmissions.modals.reject.templates.custom')">{{ t('editor.audit.newSubmissions.modals.reject.templates.custom') }}</option>
            </select>
          </div>
        </div>

        <div class="modal-footer fixed-footer">
          <button class="btn btn-secondary" @click="showRejectModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="confirmReject" :disabled="rejectForm.reasons.length === 0 || !rejectForm.comments">{{ t('editor.audit.newSubmissions.modals.reject.confirmBtn') }}</button>
        </div>
      </div>
    </div>

    <!-- 4. View Manuscript Modal -->
    <div v-if="showManuscriptModal" class="modal-overlay">
      <div class="modal-content wide-modal">
        <h2 v-if="!isFullScreen">{{ t('editor.audit.newSubmissions.modals.manuscript.title') }}: {{ truncateText(currentJournal?.title, 50) }}</h2>
        
        <div class="modal-top-bar" v-if="!isFullScreen">
          <span><strong>{{ t('common.id') }}:</strong> {{ currentJournal?.id }}</span>
          <span><strong>{{ t('common.author') }}:</strong> {{ currentJournal?.author }}</span>
          <span><strong>{{ t('common.date') }}:</strong> {{ currentJournal?.date }}</span>
          <span><strong>{{ t('common.status') }}:</strong> {{ currentJournal?.status }}</span>
        </div>
        
        <div class="viewer-controls" :class="{ 'fullscreen-controls': isFullScreen }">
          <div class="control-group">
            <button class="btn-text" @click="handleZoomIn" :disabled="zoomLevel >= 200" :class="{ disabled: zoomLevel >= 200 }">{{ t('editor.audit.newSubmissions.modals.manuscript.zoomIn') }}</button>
            <span class="control-label">Zoom: {{ zoomLevel }}%</span>
            <button class="btn-text" @click="handleZoomOut" :disabled="zoomLevel <= 50" :class="{ disabled: zoomLevel <= 50 }">{{ t('editor.audit.newSubmissions.modals.manuscript.zoomOut') }}</button>
          </div>
          
          <div class="control-group">
             <button class="btn-text" @click="handlePrevPage" :disabled="currentPage <= 1" :class="{ disabled: currentPage <= 1 }">{{ t('editor.audit.newSubmissions.modals.manuscript.prevPage') }}</button>
             <span class="control-label">Page {{ currentPage }} of {{ totalPages }}</span>
             <button class="btn-text" @click="handleNextPage" :disabled="currentPage >= totalPages" :class="{ disabled: currentPage >= totalPages }">{{ t('editor.audit.newSubmissions.modals.manuscript.nextPage') }}</button>
          </div>

          <div class="control-group">
            <button class="btn-text" @click="toggleFullScreen">{{ isFullScreen ? t('editor.audit.newSubmissions.modals.manuscript.exitFullScreen') : t('editor.audit.newSubmissions.modals.manuscript.fullScreen') }}</button>
          </div>
        </div>

        <div class="manuscript-viewer" :style="{ transform: `scale(${zoomLevel/100})`, transformOrigin: 'top left' }">
          <!-- Mock PDF Viewer -->
          <div class="pdf-placeholder">
            <p>[PDF Viewer Placeholder - Page {{ currentPage }}]</p>
            <p>Rendering manuscript content for: {{ currentJournal?.title }}</p>
            <div class="abstract-preview">
              <h3>{{ t('common.abstract') }}</h3>
              <p v-if="currentJournal?.abstract && currentJournal.abstract.trim()" class="content-text">{{ currentJournal.abstract }}</p>
              <p v-else class="placeholder-text">{{ t('common.noData') }}</p>
              
              <h3>{{ t('common.content') }}</h3>
              <p v-if="currentJournal?.content && currentJournal.content.trim()" class="content-text">{{ currentJournal.content }}</p>
              <p v-else class="placeholder-text">{{ t('common.noData') }}</p>
              
              <h3>{{ t('common.references') }}</h3>
              <p v-if="currentJournal?.references && currentJournal.references.trim()" class="content-text">{{ currentJournal.references }}</p>
              <p v-else class="placeholder-text">{{ t('common.noData') }}</p>
            </div>
          </div>
        </div>

        <div class="modal-footer" v-if="!isFullScreen">
          <button class="btn btn-primary" @click="downloadFile('manuscript.pdf')">{{ t('editor.audit.newSubmissions.modals.attachments.download') }} {{ t('common.manuscript') }}</button>
          <button class="btn btn-secondary" @click="showManuscriptModal = false">{{ t('common.close') }}</button>
        </div>
      </div>
    </div>

    <!-- 5. View Attachments Modal -->
    <div v-if="showAttachmentsModal" class="modal-overlay">
      <div class="modal-content wide-modal">
        <h2>{{ t('editor.audit.newSubmissions.modals.attachments.title') }}: {{ truncateText(currentJournal?.title, 50) }}</h2>
        
        <div class="modal-top-bar">
           <button class="btn-text" @click="downloadAllAttachments" :disabled="isPreparingDownload" :class="{ disabled: isPreparingDownload }">
             {{ isPreparingDownload ? t('common.loading') : t('editor.audit.newSubmissions.modals.attachments.downloadAll') }}
           </button>
           <button class="btn-text" @click="refreshAttachmentList" :disabled="isRefreshingList" :class="{ disabled: isRefreshingList }">
             {{ isRefreshingList ? t('common.loading') : t('editor.audit.newSubmissions.modals.attachments.refresh') }}
           </button>
        </div>

        <div v-if="isRefreshingList" class="loading-state">
          {{ t('common.loading') }}
        </div>

        <div v-else-if="previewFile" class="attachment-preview-area">
           <div class="preview-header">
             <span>{{ t('editor.audit.newSubmissions.modals.attachments.preview') }}: {{ previewFile.name }}</span>
             <button class="btn-text" @click="closePreview">{{ t('common.close') }} {{ t('editor.audit.newSubmissions.modals.attachments.preview') }}</button>
           </div>
           <div class="preview-content">
             [{{ t('editor.audit.newSubmissions.modals.attachments.preview') }} {{ t('common.content') }} {{ t('common.for') }} {{ previewFile.type }}]
             <br>
             (Zoom In / Zoom Out controls would be here for images)
           </div>
        </div>

        <div v-else class="attachments-list">
          <!-- Group: Supplementary Materials -->
          <div class="attachment-group">
            <h3>{{ t('editor.audit.newSubmissions.modals.attachments.groups.supplementary') }}</h3>
            <div class="attachment-item">
              <div class="file-info">
                <span class="file-name">Supplementary_Data_S1.xlsx</span>
                <span class="file-meta">2.4 MB • {{ t('common.uploadedOn') }} {{ currentJournal?.date }}</span>
              </div>
              <div class="file-actions">
                 <button class="btn-text" @click="viewAttachment('Supplementary_Data_S1.xlsx', 'xlsx')">{{ t('editor.audit.newSubmissions.modals.attachments.preview') }}</button>
                 <button class="btn-text" @click="downloadFile('Supplementary_Data_S1.xlsx')">{{ t('editor.audit.newSubmissions.modals.attachments.download') }}</button>
              </div>
            </div>
          </div>

          <!-- Group: Figures -->
          <div class="attachment-group">
            <h3>{{ t('editor.audit.newSubmissions.modals.attachments.groups.figures') }}</h3>
            <div class="attachment-item">
              <div class="file-info">
                <span class="file-name">Figure_1_HighRes.tiff</span>
                <span class="file-meta">15.2 MB • {{ t('common.uploadedOn') }} {{ currentJournal?.date }}</span>
              </div>
              <div class="file-actions">
                 <button class="btn-text" @click="viewAttachment('Figure_1_HighRes.tiff', 'image')">{{ t('editor.audit.newSubmissions.modals.attachments.preview') }}</button>
                 <button class="btn-text" @click="downloadFile('Figure_1_HighRes.tiff')">{{ t('editor.audit.newSubmissions.modals.attachments.download') }}</button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAttachmentsModal = false">{{ t('common.close') }}</button>
        </div>
      </div>
    </div>

    <!-- 6. Ethics Statement Modal -->
    <div v-if="showEthicsModal" class="modal-overlay">
      <div class="modal-content wide-modal">
        <h2>{{ t('editor.audit.newSubmissions.modals.ethics.title') }}: {{ truncateText(currentJournal?.title, 50) }}</h2>
        
        <div class="ethics-content">
           <div class="ethics-section">
             <h3>{{ t('editor.audit.newSubmissions.modals.ethics.sections.irb') }}</h3>
             <p>{{ t('editor.audit.newSubmissions.modals.ethics.mockData.irb') }}</p>
           </div>
           <div class="ethics-section">
             <h3>{{ t('editor.audit.newSubmissions.modals.ethics.sections.consent') }}</h3>
             <p>{{ t('editor.audit.newSubmissions.modals.ethics.mockData.consent') }}</p>
           </div>
           <div class="ethics-section">
             <h3>{{ t('editor.audit.newSubmissions.modals.ethics.sections.data') }}</h3>
             <p>{{ t('editor.audit.newSubmissions.modals.ethics.mockData.data') }}</p>
           </div>
        </div>

        <div class="verification-status" :class="{ 
          'verified': ethicsVerified, 
          'pending': !ethicsVerified && currentJournal?.ethicsStatus !== 'Revision Requested',
          'revision': currentJournal?.ethicsStatus === 'Revision Requested'
        }">
          {{ t('common.status') }}: {{ currentJournal?.ethicsStatus || (ethicsVerified ? t('editor.audit.newSubmissions.modals.ethics.verified') : t('editor.audit.newSubmissions.modals.ethics.pending')) }}
        </div>
        
        <!-- Revision Request Modal (Nested) -->
        <div v-if="showRevisionRequest" class="nested-modal">
           <h3>{{ t('editor.audit.newSubmissions.modals.ethics.requestRevision') }}</h3>
           <textarea v-model="revisionComments" :placeholder="t('editor.audit.newSubmissions.alerts.revisionSent')" class="jp-input"></textarea>
           <div class="nested-actions">
             <button class="btn btn-primary" @click="sendRevisionRequest">{{ t('common.submit') }}</button>
             <button class="btn btn-secondary" @click="showRevisionRequest = false">{{ t('common.cancel') }}</button>
           </div>
        </div>

        <div class="modal-footer" v-if="!showRevisionRequest">
          <button class="btn-text" @click="printStatement">{{ t('editor.audit.newSubmissions.modals.ethics.print') }}</button>
          
          <template v-if="currentJournal?.ethicsStatus !== 'Revision Requested'">
            <button v-if="!ethicsVerified" class="btn btn-primary" @click="verifyEthics">
              {{ isVerifying ? t('common.loading') : t('editor.audit.newSubmissions.modals.ethics.verifyBtn') }}
            </button>
            <button v-else class="btn btn-danger" @click="unverifyEthics">
              {{ isVerifying ? t('common.loading') : t('editor.audit.newSubmissions.modals.ethics.unverifyBtn') }}
            </button>
            
            <button v-if="!ethicsVerified" class="btn btn-warning" @click="openRevisionRequest">{{ t('editor.audit.newSubmissions.modals.ethics.requestRevision') }}</button>
          </template>
          
          <button class="btn btn-secondary" @click="showEthicsModal = false">{{ t('common.close') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}
.content {
  flex: 1;
  max-width: 1200px;
  margin: 60px auto 0;
  padding: 2rem;
  width: 100%;
}
.header {
  margin-bottom: 2rem;
  border-bottom: 2px solid #333;
  padding-bottom: 1rem;
}
.header h1 {
  font-size: 24px;
  color: #333;
  margin: 0;
  font-weight: bold;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.subtitle {
  color: #666;
  margin-top: 0.5rem;
  font-size: 14px;
  font-style: italic;
}
.journal-item {
  background: white;
  padding: 1.5rem;
  border: 1px solid #ddd;
  margin-bottom: 1rem;
  display: flex;
  gap: 2rem;
}
.journal-info {
  flex: 1;
}
.journal-title {
  color: #333;
  font-size: 18px;
  cursor: pointer;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
.journal-title:hover {
  color: #0056B3;
}
.journal-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 14px;
  color: #666;
  margin-bottom: 1rem;
}
.journal-abstract {
  color: #333;
  line-height: 1.4;
  margin-bottom: 1rem;
  font-size: 14px;
}
.materials-links {
  display: flex;
  gap: 1rem;
}
.link {
  color: #0056B3;
  text-decoration: none;
  font-size: 14px;
  border-bottom: 1px solid transparent;
}
.link:hover {
  border-bottom-color: #0056B3;
}
.journal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  min-width: 160px;
}
.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 2px;
  cursor: pointer;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.btn-primary { 
  background: #0056B3;
  color: white; 
}
.btn-primary:hover { 
  background: #004494; 
}
.btn-primary:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}
.btn-warning { 
  background: #f0f0f0; 
  color: #333; 
  border: 1px solid #ccc;
}
.btn-warning:hover { 
  background: #e0e0e0; 
}
.btn-danger { 
  background: white; 
  color: #dc3545; 
  border: 1px solid #dc3545;
}
.btn-danger:hover { 
  background: #fff0f0; 
}
.btn-secondary { 
  background: #767676; 
  color: white; 
}
.btn-secondary:hover { 
  background: #5a5a5a; 
}
.no-data {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border: 1px solid #ddd;
}

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  width: 600px;
  padding: 30px;
  border-radius: 0; /* Sharp corners */
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.modal-content h2 {
  font-size: 20px;
  color: #333;
  margin: 0;
  border-bottom: 2px solid #dc3545;
  padding-bottom: 10px;
  text-transform: uppercase;
}
.modal-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.info-section {
  background: #f9f9f9;
  padding: 15px;
  border: 1px solid #eee;
  font-size: 14px;
  line-height: 1.5;
}
.info-section p {
  margin: 0 0 5px 0;
  color: #444;
}
.input-label {
  font-weight: bold;
  font-size: 14px;
  color: #333;
}
.input-label.required::after {
  content: " *";
  color: #dc3545;
}
.jp-input, .jp-select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 0;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}
.jp-input:focus, .jp-select:focus {
  outline: none;
  border-color: #0056B3;
}
textarea.jp-input {
  min-height: 80px;
  resize: vertical;
}
.letter-preview {
  min-height: 120px;
  background: #fafafa;
  font-size: 13px;
}
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.radio-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  cursor: pointer;
}
.sub-option {
  margin-left: 24px;
  margin-top: 5px;
}
.modal-content.fixed-size-modal {
  display: flex;
  flex-direction: column;
  padding: 0;
  border-radius: 0;
  max-height: 90vh; /* Safety limit */
  width: 600px;
}
.screen-modal { height: 500px; }
.transfer-modal { height: 550px; }
.reject-modal { height: 600px; }

.modal-header {
  padding: 20px 30px;
  border-bottom: 2px solid #dc3545;
  background: white;
  flex-shrink: 0;
}
.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
  text-transform: uppercase;
}
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 20px 30px;
}
/* Scrollbar styling for modal body */
.modal-body::-webkit-scrollbar {
  width: 6px;
}
.modal-body::-webkit-scrollbar-track {
  background: transparent;
}
.modal-body::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 0;
}
.fixed-footer {
  padding: 20px 30px;
  border-top: 1px solid #eee;
  background: white;
  flex-shrink: 0;
  margin-top: 0; /* Override default */
}
.short-textarea {
  min-height: 60px;
  height: 80px;
}
.medium-textarea {
  min-height: 80px;
  height: 100px;
}
.clickable {
  cursor: pointer;
  user-select: none;
}
.section-header {
  margin-bottom: 5px;
  color: #333;
  font-weight: bold;
}
.reason-group {
  margin-bottom: 10px;
  border: 1px solid #eee;
  padding: 10px;
  background: #fafafa;
}
.group-header {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}
.group-content {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
@media (max-width: 600px) {
  .modal-content.fixed-size-modal {
    width: 90%;
    height: 80vh;
  }
}
.modal-content.wide-modal {
  width: 800px;
}
.modal-top-bar {
  display: flex;
  gap: 20px;
  background: #f5f5f5;
  padding: 10px 15px;
  font-size: 14px;
  color: #555;
  border-bottom: 1px solid #ddd;
}
.manuscript-viewer {
  background: #eee;
  height: 400px;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid #ccc;
}
.pdf-placeholder {
  background: white;
  min-height: 500px;
  padding: 40px;
  box-shadow: 0 0 10px rgba(0,0,0,0.1);
  text-align: center;
  color: #999;
}
.abstract-preview {
  margin-top: 30px;
  text-align: left;
  color: #333;
}

.placeholder-text {
  color: #666;
  font-style: italic;
}

.content-text {
  color: #000;
  font-style: normal;
}
.attachments-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.attachment-group h3 {
  font-size: 16px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 5px;
  margin-bottom: 10px;
}
.attachment-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background: #f9f9f9;
  border: 1px solid #eee;
}
.file-info {
  display: flex;
  flex-direction: column;
}
.file-name {
  font-weight: bold;
  color: #333;
}
.file-meta {
  font-size: 12px;
  color: #888;
}
.btn-text {
  background: none;
  border: none;
  color: #e30613;
  cursor: pointer;
  font-weight: bold;
  text-decoration: underline;
  margin-left: 10px;
}
.btn-text:hover {
  color: #c00410;
}
.ethics-content {
  background: #fcfcfc;
  padding: 20px;
  border: 1px solid #eee;
  max-height: 400px;
  overflow-y: auto;
}
.ethics-section {
  margin-bottom: 20px;
}
.ethics-section h3 {
  font-size: 16px;
  color: #444;
  margin-bottom: 5px;
}
.verification-status {
  padding: 10px;
  text-align: center;
  font-weight: bold;
  margin-top: 10px;
}
.verification-status.pending {
  background: #fff3cd;
  color: #856404;
}
.verification-status.verified {
  background: #d4edda;
  color: #155724;
}
.btn-text.disabled {
  color: #ccc;
  cursor: not-allowed;
  text-decoration: none;
}
.viewer-controls {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #fff;
  border-bottom: 1px solid #ddd;
}
.fullscreen-controls {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  z-index: 2000;
  background: rgba(255, 255, 255, 0.9);
}
.control-group {
  display: flex;
  gap: 15px;
  align-items: center;
}
.control-label {
  font-size: 13px;
  color: #666;
}
.loading-state {
  padding: 40px;
  text-align: center;
  color: #666;
  font-style: italic;
}
.attachment-preview-area {
  background: #eee;
  padding: 20px;
  min-height: 300px;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-weight: bold;
}
.preview-content {
  background: white;
  padding: 40px;
  text-align: center;
  border: 1px solid #ccc;
}
.verification-status.revision {
  background: #fff3cd; /* Orange-ish */
  color: #856404;
  border: 1px solid #ffeeba;
}
.nested-modal {
  background: #f9f9f9;
  padding: 20px;
  border: 1px solid #ddd;
  margin-top: 20px;
}
.nested-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  margin-top: 10px;
  border-top: 1px solid #eee;
  padding-top: 20px;
}
.custom-dropdown {
  position: relative;
  width: 100%;
  cursor: pointer;
  margin-top: 5px;
}
.dropdown-header {
  padding: 10px;
  border: 1px solid #ccc;
  background: white;
  min-height: 40px;
  display: flex;
  align-items: center;
  font-size: 14px;
  color: #333;
  box-sizing: border-box;
}
.dropdown-header.placeholder {
  color: #666;
}
.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  border: 1px solid #ccc;
  border-top: none;
  background: white;
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.dropdown-list::-webkit-scrollbar {
  display: none;
}
.dropdown-item {
  padding: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}
.dropdown-item:last-child {
  border-bottom: none;
}
.dropdown-item:hover {
  background: #f5f5f5;
}
.dropdown-item.selected {
  color: #e30613;
  background: #fff;
  font-weight: bold;
}
.dropdown-status {
  padding: 15px;
  color: #666;
  font-style: italic;
  text-align: center;
}
.validation-modal-content {
  background: white;
  width: 300px;
  height: 150px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 15px;
  border: 1px solid #999;
  box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}
.validation-modal-content h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: bold;
}
.validation-modal-content p {
  font-size: 14px;
  color: #333;
  margin: 0;
  line-height: 1.4;
}
.validation-footer {
  display: flex;
  justify-content: flex-end;
}
.btn-text-only-bordered {
  background: white;
  border: 1px solid #ccc;
  color: #333;
  padding: 5px 20px;
  cursor: pointer;
  font-size: 14px;
}
.btn-text-only-bordered:hover {
  background: #f0f0f0;
}
.disabled-grey {
  background: #e0e0e0 !important;
  color: #888 !important;
  cursor: not-allowed;
  border-color: #ccc !important;
}
.status-text {
  font-size: 14px;
  color: #0056B3;
  margin-right: auto;
  font-weight: bold;
  align-self: center;
}
.warning-text {
  color: #dc3545;
  font-size: 14px;
  margin-top: 5px;
  padding: 10px;
  background: #fff0f0;
  border: 1px solid #ffcccc;
}
</style>
