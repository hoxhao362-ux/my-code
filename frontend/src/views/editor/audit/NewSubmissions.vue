<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { stripHtmlTags, truncateText } from '../../../utils/helpers.js'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Filter for New Submissions
const pendingJournals = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === 'pending_initial_review' || 
    // Legacy support
    journal.status === '待审核' || 
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
  const elem = document.querySelector('.manuscript-viewer')
  if (!document.fullscreenElement) {
    elem.requestFullscreen().catch(err => {
      alert(`Error attempting to enable full-screen mode: ${err.message} (${err.name})`)
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
    alert('Preview Unavailable\n\nThis file type is not supported for preview. Please download to view.')
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
    alert('Download started for all attachments.')
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
  alert('Revision request sent to writer.')
}

const printStatement = () => {
  window.print()
}

const downloadFile = (fileName) => {
  alert(`Downloading ${fileName}...`)
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
      
      assignStatus.value = `Status: Assigned to ${screenForm.value.selectedEditorName}`
      
      // Add Log
      userStore.addSystemLog({
        type: 'operation',
        user: user.value?.username || 'editor',
        action: 'Editor Assigned',
        target: `Manuscript ID: ${updatedJournal.id} assigned to ${screenForm.value.selectedEditorName}`
      })

      // Delay close to show status? User requirement says "Top shows status". 
      // But usually we close the modal after success. 
      // "Click Confirm -> API calls -> Status Update in Modal?" 
      // If we close immediately, user won't see it.
      // Let's assume we show an alert (standard flow) or keep it open briefly?
      // User says: "Submission after data update... Modal top shows status text".
      // This implies the modal might stay open or we show it on the *next* view?
      // Actually "Confirm & Proceed" usually implies moving forward.
      // Let's show an alert and close, or just close. 
      // "Confirm & Proceed" -> Close Modal.
      
    } catch (error) {
      alert('Assignment failed. Please try again.')
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
  alert('Screening confirmed. Manuscript moved to next stage.')
}

// --- Suggest Transfer Logic ---
const transferForm = ref({
  reason: '',
  targetJournal: 'Lancet Digital Health',
  letter: ''
})

const transferJournals = ['Lancet Digital Health', 'Journal of Medical Imaging', 'Lancet Global Health']

const openTransferModal = (journal) => {
  currentJournal.value = journal
  transferForm.value = {
    reason: '',
    targetJournal: 'Lancet Digital Health',
    letter: `Dear ${journal.writer},\n\nWe have reviewed your manuscript "${journal.title}". While it is of high quality, we believe it would be better suited for our sister journal, Lancet Digital Health.\n\nBest regards,\nThe Lancet Editorial Team`
  }
  showTransferModal.value = true
}

const sendTransfer = () => {
  if (!transferForm.value.reason) {
    alert('Please enter a reason for transfer.')
    return
  }

  const updatedJournal = { ...currentJournal.value }
  updatedJournal.status = 'transfer_suggested'
  userStore.updateJournal(updatedJournal)

  showTransferModal.value = false
  alert('Transfer suggestion sent to writer.')
}

// --- Reject Logic ---
const rejectForm = ref({
  reason: '',
  otherReason: '',
  comments: '',
  template: 'Standard Template'
})

const openRejectModal = (journal) => {
  currentJournal.value = journal
  rejectForm.value = {
    reason: '',
    otherReason: '',
    comments: '',
    template: 'Standard Template'
  }
  showRejectModal.value = true
}

const confirmReject = () => {
  if (!rejectForm.value.reason || !rejectForm.value.comments) {
    alert('Please fill in all required fields.')
    return
  }
  
  if (rejectForm.value.reason === 'Other' && !rejectForm.value.otherReason) {
    alert('Please specify the other reason.')
    return
  }

  const updatedJournal = { ...currentJournal.value }
  updatedJournal.status = 'rejected_after_initial_screen'
  userStore.updateJournal(updatedJournal)

  showRejectModal.value = false
  alert('Rejection confirmed. Notification sent to writer.')
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
        <h1>New Submissions</h1>
        <p class="subtitle">Screening & Initial Check</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in pendingJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title" @click="viewDetail(journal.id)">{{ journal.title }}</h3>
            <div class="journal-meta">
              <span><strong>Writer:</strong> {{ journal.writer }}</span>
              <span><strong>Date:</strong> {{ journal.date }}</span>
              <span><strong>Module:</strong> {{ journal.module }}</span>
            </div>
            <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract), 200) }}</p>
            <div class="materials-links">
              <a href="#" @click.prevent="openManuscriptModal(journal)" class="link">View Manuscript</a>
              <a href="#" @click.prevent="openAttachmentsModal(journal)" class="link">View Attachments</a>
              <a href="#" @click.prevent="openEthicsModal(journal)" class="link">Ethics Statement</a>
            </div>
          </div>
          <div class="journal-actions">
            <button class="btn btn-primary" @click="openScreenModal(journal)">Screen & Send</button>
            <button class="btn btn-warning" @click="openTransferModal(journal)">Suggest Transfer</button>
            <button class="btn btn-danger" @click="openRejectModal(journal)">Reject</button>
          </div>
        </div>
        <div v-if="pendingJournals.length === 0" class="no-data">
          No new submissions pending screening.
        </div>
      </div>
    </main>

    <!-- 1. Screen & Send Modal -->
    <div v-if="showScreenModal" class="modal-overlay">
      <div class="modal-content fixed-size-modal screen-modal">
        <div class="modal-header">
          <h2>Screen & Send Confirmation</h2>
        </div>
        
        <div class="modal-body">
          <div class="modal-section info-section">
            <p><strong>Title:</strong> {{ currentJournal?.title }}</p>
            <p><strong>Writer:</strong> {{ currentJournal?.writer }}</p>
            <p><strong>Module:</strong> {{ currentJournal?.module }}</p>
            <p><strong>Submission Date:</strong> {{ currentJournal?.date }}</p>
          </div>

          <div class="modal-section">
            <label class="input-label">Initial Screening Notes (Optional)</label>
            <textarea v-model="screenForm.notes" placeholder="Enter brief screening notes (optional)" class="lancet-input short-textarea"></textarea>
          </div>

          <div class="modal-section">
            <label class="input-label">Assignment Options</label>
            <div class="radio-group">
              <label class="radio-item">
                <input type="radio" v-model="screenForm.assignmentType" value="auto" @change="handleAssignmentTypeChange">
                Auto-assign to Assign Reviewers task pool
              </label>
              <label class="radio-item">
                <input type="radio" v-model="screenForm.assignmentType" value="specific" @change="handleAssignmentTypeChange" :disabled="noEditorsAvailable">
                Assign to specific editor
              </label>
            </div>
            
            <div v-if="noEditorsAvailable" class="warning-text">
              No active editors are available for manual assignment. This manuscript will be auto-assigned to the Assign Reviewers task pool.
            </div>

            <div v-if="screenForm.assignmentType === 'specific'" class="sub-option">
               <div class="custom-dropdown" @click="toggleEditorsDropdown">
                 <div class="dropdown-header" :class="{ 'placeholder': !screenForm.selectedEditorId }">
                   {{ screenForm.selectedEditorName || 'Select Editor' }}
                 </div>
                 <div v-if="isEditorsDropdownOpen" class="dropdown-list">
                   <div v-if="isLoadingEditors" class="dropdown-status">Loading editors...</div>
                   <div v-else-if="editorsList.length === 0" class="dropdown-status">No active editors available</div>
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
          <button class="btn btn-secondary" @click="showScreenModal = false">Cancel</button>
          <button class="btn btn-primary" 
            @click="confirmScreen"
            :class="{ 'disabled-grey': screenForm.assignmentType === 'specific' && !screenForm.selectedEditorId }"
          >Confirm & Proceed</button>
        </div>
      </div>
    </div>

    <!-- Validation Modal -->
    <div v-if="showValidationModal" class="modal-overlay" style="z-index: 2000;">
      <div class="validation-modal-content">
        <h3>Required Selection Missing</h3>
        <p>Please select an editor to assign this manuscript to before proceeding.</p>
        <div class="validation-footer">
          <button class="btn-text-only-bordered" @click="closeValidationModal">OK</button>
        </div>
      </div>
    </div>

    <!-- 2. Suggest Transfer Modal -->
    <div v-if="showTransferModal" class="modal-overlay">
      <div class="modal-content fixed-size-modal transfer-modal">
        <div class="modal-header">
          <h2>Suggest Transfer to Another Journal</h2>
        </div>
        
        <div class="modal-body">
          <div class="modal-section info-section">
            <p><strong>Title:</strong> {{ currentJournal?.title }}</p>
            <p><strong>Writer:</strong> {{ currentJournal?.writer }}</p>
            <p><strong>Module:</strong> {{ currentJournal?.module }}</p>
          </div>

          <div class="modal-section">
            <label class="input-label required">Transfer Reason</label>
            <textarea v-model="transferForm.reason" placeholder="Enter reason for transfer suggestion (required)" class="lancet-input medium-textarea"></textarea>
          </div>

          <div class="modal-section">
            <label class="input-label">Journal Selection</label>
            <select v-model="transferForm.targetJournal" class="lancet-select">
              <option v-for="j in transferJournals" :key="j" :value="j">{{ j }}</option>
            </select>
          </div>

          <div class="modal-section">
            <div class="section-header clickable" @click="toggleTransferPreview = !toggleTransferPreview">
              <label class="input-label">Transfer Letter Preview {{ toggleTransferPreview ? '(-)' : '(+)' }}</label>
            </div>
            <textarea v-if="toggleTransferPreview" v-model="transferForm.letter" class="lancet-input letter-preview"></textarea>
          </div>
        </div>

        <div class="modal-footer fixed-footer">
          <button class="btn btn-secondary" @click="showTransferModal = false">Cancel</button>
          <button class="btn btn-primary" @click="sendTransfer" :disabled="!transferForm.reason">Send Transfer Suggestion</button>
        </div>
      </div>
    </div>

    <!-- 3. Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay">
      <div class="modal-content fixed-size-modal reject-modal">
        <div class="modal-header">
          <h2>Reject Manuscript</h2>
        </div>
        
        <div class="modal-body">
          <div class="modal-section info-section">
            <p><strong>Title:</strong> {{ currentJournal?.title }}</p>
            <p><strong>Writer:</strong> {{ currentJournal?.writer }}</p>
            <p><strong>Submission Date:</strong> {{ currentJournal?.date }}</p>
          </div>

          <div class="modal-section">
            <label class="input-label required">Rejection Reason</label>
            
            <!-- Group: Scope & Novelty -->
            <div class="reason-group">
              <div class="group-header clickable" @click="toggleRejectGroup('Scope & Novelty')">
                <strong>Scope & Novelty</strong> {{ activeRejectGroup === 'Scope & Novelty' ? '(-)' : '(+)' }}
              </div>
              <div v-show="activeRejectGroup === 'Scope & Novelty'" class="group-content">
                <label class="radio-item"><input type="radio" v-model="rejectForm.reason" value="Out of scope"> Out of scope for this journal</label>
                <label class="radio-item"><input type="radio" v-model="rejectForm.reason" value="Insufficient novelty"> Insufficient novelty or originality</label>
              </div>
            </div>

            <!-- Group: Methodology -->
            <div class="reason-group">
              <div class="group-header clickable" @click="toggleRejectGroup('Methodology')">
                <strong>Methodology</strong> {{ activeRejectGroup === 'Methodology' ? '(-)' : '(+)' }}
              </div>
              <div v-show="activeRejectGroup === 'Methodology'" class="group-content">
                <label class="radio-item"><input type="radio" v-model="rejectForm.reason" value="Major methodological flaws"> Major methodological flaws</label>
                <label class="radio-item"><input type="radio" v-model="rejectForm.reason" value="Statistical errors"> Statistical errors</label>
              </div>
            </div>

            <!-- Group: Presentation & Other -->
            <div class="reason-group">
              <div class="group-header clickable" @click="toggleRejectGroup('Presentation')">
                <strong>Presentation & Other</strong> {{ activeRejectGroup === 'Presentation' ? '(-)' : '(+)' }}
              </div>
              <div v-show="activeRejectGroup === 'Presentation'" class="group-content">
                <label class="radio-item"><input type="radio" v-model="rejectForm.reason" value="Poor presentation"> Poor presentation or language quality</label>
                <label class="radio-item"><input type="radio" v-model="rejectForm.reason" value="Other"> Other</label>
                 <div v-if="rejectForm.reason === 'Other'" class="sub-option">
                   <input v-model="rejectForm.otherReason" placeholder="Specify other reason" class="lancet-input" />
                </div>
              </div>
            </div>
          </div>

          <div class="modal-section">
            <label class="input-label required">Detailed Rejection Comments</label>
            <textarea v-model="rejectForm.comments" placeholder="Enter detailed rejection comments (required)" class="lancet-input medium-textarea"></textarea>
          </div>

          <div class="modal-section">
            <label class="input-label">Rejection Letter Template</label>
            <select v-model="rejectForm.template" class="lancet-select">
              <option>Standard Template</option>
              <option>Custom Template</option>
            </select>
          </div>
        </div>

        <div class="modal-footer fixed-footer">
          <button class="btn btn-secondary" @click="showRejectModal = false">Cancel</button>
          <button class="btn btn-primary" @click="confirmReject" :disabled="!rejectForm.reason || !rejectForm.comments">Confirm Rejection</button>
        </div>
      </div>
    </div>

    <!-- 4. View Manuscript Modal -->
    <div v-if="showManuscriptModal" class="modal-overlay">
      <div class="modal-content wide-modal">
        <h2 v-if="!isFullScreen">Manuscript: {{ truncateText(currentJournal?.title, 50) }}</h2>
        
        <div class="modal-top-bar" v-if="!isFullScreen">
          <span><strong>ID:</strong> {{ currentJournal?.id }}</span>
          <span><strong>Writer:</strong> {{ currentJournal?.writer }}</span>
          <span><strong>Date:</strong> {{ currentJournal?.date }}</span>
          <span><strong>Status:</strong> {{ currentJournal?.status }}</span>
        </div>
        
        <div class="viewer-controls" :class="{ 'fullscreen-controls': isFullScreen }">
          <div class="control-group">
            <button class="btn-text" @click="handleZoomIn" :disabled="zoomLevel >= 200" :class="{ disabled: zoomLevel >= 200 }">Zoom In</button>
            <span class="control-label">Zoom: {{ zoomLevel }}%</span>
            <button class="btn-text" @click="handleZoomOut" :disabled="zoomLevel <= 50" :class="{ disabled: zoomLevel <= 50 }">Zoom Out</button>
          </div>
          
          <div class="control-group">
             <button class="btn-text" @click="handlePrevPage" :disabled="currentPage <= 1" :class="{ disabled: currentPage <= 1 }">Previous Page</button>
             <span class="control-label">Page {{ currentPage }} of {{ totalPages }}</span>
             <button class="btn-text" @click="handleNextPage" :disabled="currentPage >= totalPages" :class="{ disabled: currentPage >= totalPages }">Next Page</button>
          </div>

          <div class="control-group">
            <button class="btn-text" @click="toggleFullScreen">{{ isFullScreen ? 'Exit Full Screen' : 'Full Screen' }}</button>
          </div>
        </div>

        <div class="manuscript-viewer" :style="{ transform: `scale(${zoomLevel/100})`, transformOrigin: 'top left' }">
          <!-- Mock PDF Viewer -->
          <div class="pdf-placeholder">
            <p>[PDF Viewer Placeholder - Page {{ currentPage }}]</p>
            <p>Rendering manuscript content for: {{ currentJournal?.title }}</p>
            <div class="abstract-preview">
              <h3>Abstract</h3>
              <p>{{ currentJournal?.abstract }}</p>
              <p v-for="i in 5" :key="i">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            </div>
          </div>
        </div>

        <div class="modal-footer" v-if="!isFullScreen">
          <button class="btn btn-primary" @click="downloadFile('manuscript.pdf')">Download Manuscript</button>
          <button class="btn btn-secondary" @click="showManuscriptModal = false">Close</button>
        </div>
      </div>
    </div>

    <!-- 5. View Attachments Modal -->
    <div v-if="showAttachmentsModal" class="modal-overlay">
      <div class="modal-content wide-modal">
        <h2>Attachments for: {{ truncateText(currentJournal?.title, 50) }}</h2>
        
        <div class="modal-top-bar">
           <button class="btn-text" @click="downloadAllAttachments" :disabled="isPreparingDownload" :class="{ disabled: isPreparingDownload }">
             {{ isPreparingDownload ? 'Preparing Download...' : 'DOWNLOAD ALL ATTACHMENTS' }}
           </button>
           <button class="btn-text" @click="refreshAttachmentList" :disabled="isRefreshingList" :class="{ disabled: isRefreshingList }">
             {{ isRefreshingList ? 'Refreshing...' : 'Refresh List' }}
           </button>
        </div>

        <div v-if="isRefreshingList" class="loading-state">
          Refreshing Attachment List...
        </div>

        <div v-else-if="previewFile" class="attachment-preview-area">
           <div class="preview-header">
             <span>Preview: {{ previewFile.name }}</span>
             <button class="btn-text" @click="closePreview">Close Preview</button>
           </div>
           <div class="preview-content">
             [Preview Content for {{ previewFile.type }}]
             <br>
             (Zoom In / Zoom Out controls would be here for images)
           </div>
        </div>

        <div v-else class="attachments-list">
          <!-- Group: Supplementary Materials -->
          <div class="attachment-group">
            <h3>Supplementary Materials</h3>
            <div class="attachment-item">
              <div class="file-info">
                <span class="file-name">Supplementary_Data_S1.xlsx</span>
                <span class="file-meta">2.4 MB • Uploaded on {{ currentJournal?.date }}</span>
              </div>
              <div class="file-actions">
                 <button class="btn-text" @click="viewAttachment('Supplementary_Data_S1.xlsx', 'xlsx')">View</button>
                 <button class="btn-text" @click="downloadFile('Supplementary_Data_S1.xlsx')">Download</button>
              </div>
            </div>
          </div>

          <!-- Group: Figures -->
          <div class="attachment-group">
            <h3>Figures & Tables</h3>
            <div class="attachment-item">
              <div class="file-info">
                <span class="file-name">Figure_1_HighRes.tiff</span>
                <span class="file-meta">15.2 MB • Uploaded on {{ currentJournal?.date }}</span>
              </div>
              <div class="file-actions">
                 <button class="btn-text" @click="viewAttachment('Figure_1_HighRes.tiff', 'image')">View</button>
                 <button class="btn-text" @click="downloadFile('Figure_1_HighRes.tiff')">Download</button>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAttachmentsModal = false">Close</button>
        </div>
      </div>
    </div>

    <!-- 6. Ethics Statement Modal -->
    <div v-if="showEthicsModal" class="modal-overlay">
      <div class="modal-content wide-modal">
        <h2>Ethics Statement: {{ truncateText(currentJournal?.title, 50) }}</h2>
        
        <div class="ethics-content">
           <div class="ethics-section">
             <h3>IRB Approval</h3>
             <p>This study was approved by the Institutional Review Board of [Hospital Name] (Approval No. IRB-2023-001) on January 15, 2023.</p>
           </div>
           <div class="ethics-section">
             <h3>Informed Consent</h3>
             <p>Written informed consent was obtained from all participants prior to their inclusion in the study.</p>
           </div>
           <div class="ethics-section">
             <h3>Data Sharing</h3>
             <p>De-identified participant data will be made available upon reasonable request to the corresponding writer.</p>
           </div>
        </div>

        <div class="verification-status" :class="{ 
          'verified': ethicsVerified, 
          'pending': !ethicsVerified && currentJournal?.ethicsStatus !== 'Revision Requested',
          'revision': currentJournal?.ethicsStatus === 'Revision Requested'
        }">
          Status: {{ currentJournal?.ethicsStatus || (ethicsVerified ? 'Verified' : 'Pending Verification') }}
        </div>
        
        <!-- Revision Request Modal (Nested) -->
        <div v-if="showRevisionRequest" class="nested-modal">
           <h3>Request Ethics Statement Revision</h3>
           <textarea v-model="revisionComments" placeholder="Add additional comments for the writer (optional)" class="lancet-input"></textarea>
           <div class="nested-actions">
             <button class="btn btn-primary" @click="sendRevisionRequest">SEND REQUEST</button>
             <button class="btn btn-secondary" @click="showRevisionRequest = false">CANCEL</button>
           </div>
        </div>

        <div class="modal-footer" v-if="!showRevisionRequest">
          <button class="btn-text" @click="printStatement">Print Statement</button>
          
          <template v-if="currentJournal?.ethicsStatus !== 'Revision Requested'">
            <button v-if="!ethicsVerified" class="btn btn-primary" @click="verifyEthics">
              {{ isVerifying ? 'Verifying...' : 'VERIFY ETHICS STATEMENT' }}
            </button>
            <button v-else class="btn btn-danger" @click="unverifyEthics">
              {{ isVerifying ? 'Unverifying...' : 'UNVERIFY' }}
            </button>
            
            <button v-if="!ethicsVerified" class="btn btn-warning" @click="openRevisionRequest">REQUEST REVISION</button>
          </template>
          
          <button class="btn btn-secondary" @click="showEthicsModal = false">CLOSE</button>
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
  font-family: 'Times New Roman', Times, serif;
}
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
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
  color: #e30613; /* Lancet Red */
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
  color: #e30613;
  text-decoration: none;
  font-size: 14px;
  border-bottom: 1px solid transparent;
}
.link:hover {
  border-bottom-color: #e30613;
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
  font-family: 'Times New Roman', Times, serif;
  font-size: 14px;
  font-weight: bold;
  transition: all 0.2s;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
.btn-primary { 
  background: #e30613; /* Lancet Red */
  color: white; 
}
.btn-primary:hover { 
  background: #c00410; 
}
.btn-primary:disabled {
  background: #ffcccc;
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
  color: #e30613; 
  border: 1px solid #e30613;
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
  border-bottom: 2px solid #e30613;
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
  color: #e30613;
}
.lancet-input, .lancet-select {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 0;
  font-family: 'Times New Roman', Times, serif;
  font-size: 14px;
  width: 100%;
  box-sizing: border-box;
}
.lancet-input:focus, .lancet-select:focus {
  outline: none;
  border-color: #e30613;
}
textarea.lancet-input {
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
  border-bottom: 2px solid #e30613;
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
  font-family: 'Times New Roman', Times, serif;
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
  font-family: 'Times New Roman', Times, serif;
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
  color: #e30613;
  margin-right: auto;
  font-weight: bold;
  align-self: center;
}
.warning-text {
  color: #e30613;
  font-size: 14px;
  margin-top: 5px;
  padding: 10px;
  background: #fff0f0;
  border: 1px solid #ffcccc;
}
</style>
