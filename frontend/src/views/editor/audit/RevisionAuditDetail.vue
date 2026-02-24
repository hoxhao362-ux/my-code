<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from '../../../composables/useI18n'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'
import { useUserStore } from '../../../stores/user'

const props = defineProps({
  manuscript: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back', 'update'])

const { t } = useI18n()
const userStore = useUserStore()
const activeTab = ref('preview') // 'preview' | 'response'
const isPreviewed = ref(false) // Check if revision is previewed

// Mock Data Generators
const generateMockReviewerComments = (msId) => {
  return [
    {
      reviewerId: 'Reviewer 1',
      comments: [
        'The methodology section requires clarification on sample size calculation.',
        'Figure 2 needs to be updated to include the new data points.'
      ]
    },
    {
      reviewerId: 'Reviewer 2',
      comments: [
        'The discussion should be revised to better contextualize the findings.'
      ]
    }
  ]
}

const reviewerComments = ref([])
onMounted(() => {
  reviewerComments.value = generateMockReviewerComments(props.manuscript.ms_id)
})

// --- APPROVE LOGIC ---
const showApproveModal = ref(false)

const handleApproveClick = () => {
  if (!isPreviewed.value) {
    alert(t('editor.audit.revisionHandling.detail.modals.approve.reviewRequired'))
    return
  }
  showApproveModal.value = true
}

const confirmApprove = () => {
  // Update status
  const updatedJournal = { ...props.manuscript.raw_data }
  updatedJournal.status = MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
  
  // Add history
  if (!updatedJournal.reviewHistory) updatedJournal.reviewHistory = []
  updatedJournal.reviewHistory.push({
    date: new Date().toISOString().split('T')[0],
    actor: 'Editor',
    action: 'Approved revision',
    comment: 'Revision approved. Proceeding to final acceptance.'
  })

  // Update store
  userStore.updateJournal(updatedJournal)

  // Notify author
  const existingNotifications = JSON.parse(localStorage.getItem('notifications') || '[]')
  existingNotifications.unshift({
    id: Date.now(),
    title: t('editor.audit.revisionHandling.alerts.notification.approvedTitle'),
    message: t('editor.audit.revisionHandling.alerts.notification.approvedMsg', { id: props.manuscript.ms_id, comment: 'Revision approved. Proceeding to final acceptance.' }),
    type: 'success',
    createdAt: new Date().toISOString(),
    isRead: false,
    targetUser: props.manuscript.writer
  })
  localStorage.setItem('notifications', JSON.stringify(existingNotifications))

  showApproveModal.value = false
  emit('update')
}

// --- SEND REQUEST LOGIC ---
const showSendRequestModal = ref(false)
const showSendRequestDoubleConfirm = ref(false)
const revisionType = ref(t('editor.audit.revisionHandling.detail.modals.sendRequest.types.minor'))
const revisionDeadline = ref('')
const sendRequestComment = ref('')
const isReviewerCommentsCollapsed = ref(false)
const editorialDeclarations = ref({
  reviewedComments: false,
  deadlineGuidelines: false,
  scopePolicy: false
})

const openSendRequestModal = () => {
  // Reset state
  revisionType.value = t('editor.audit.revisionHandling.detail.modals.sendRequest.types.minor')
  const date = new Date()
  date.setDate(date.getDate() + 14)
  revisionDeadline.value = date.toISOString().split('T')[0]
  sendRequestComment.value = ''
  editorialDeclarations.value = {
    reviewedComments: false,
    deadlineGuidelines: false,
    scopePolicy: false
  }
  isReviewerCommentsCollapsed.value = false
  showSendRequestModal.value = true
}

const isSendRequestValid = computed(() => {
  const isCommentValid = sendRequestComment.value && sendRequestComment.value.trim().length > 0 && sendRequestComment.value !== '<p><br></p>'
  const areDeclarationsValid = Object.values(editorialDeclarations.value).every(val => val === true)
  return isCommentValid && areDeclarationsValid && revisionDeadline.value
})

const getSendRequestTooltip = computed(() => {
  const isCommentValid = sendRequestComment.value && sendRequestComment.value.trim().length > 0 && sendRequestComment.value !== '<p><br></p>'
  if (!isCommentValid) return t('editor.audit.revisionHandling.detail.modals.sendRequest.tooltips.provideComments')
  
  const areDeclarationsValid = Object.values(editorialDeclarations.value).every(val => val === true)
  if (!areDeclarationsValid) return t('editor.audit.revisionHandling.detail.modals.sendRequest.tooltips.confirmDeclarations')
  
  return ''
})

const handleSendRequestClick = () => {
  if (!isSendRequestValid.value) return
  showSendRequestDoubleConfirm.value = true
}

const confirmSendRequest = () => {
  // Update status
  const updatedJournal = { ...props.manuscript.raw_data }
  updatedJournal.status = MANUSCRIPT_STATUS.REVISION_REQUIRED
  updatedJournal.revisionType = revisionType.value
  updatedJournal.deadline = revisionDeadline.value
  
  // Add history
  if (!updatedJournal.reviewHistory) updatedJournal.reviewHistory = []
  updatedJournal.reviewHistory.push({
    date: new Date().toISOString().split('T')[0],
    actor: 'Editor',
    action: 'Revision Request Sent',
    comment: sendRequestComment.value
  })

  // Update store
  userStore.updateJournal(updatedJournal)

  // Notify author
  const existingNotifications = JSON.parse(localStorage.getItem('notifications') || '[]')
  existingNotifications.unshift({
    id: Date.now(),
    title: t('editor.audit.revisionHandling.alerts.notification.rejectedTitle'),
    message: t('editor.audit.revisionHandling.alerts.notification.rejectedMsg', { id: props.manuscript.ms_id, comment: sendRequestComment.value }),
    type: 'warning',
    createdAt: new Date().toISOString(),
    isRead: false,
    targetUser: props.manuscript.writer
  })
  localStorage.setItem('notifications', JSON.stringify(existingNotifications))

  showSendRequestDoubleConfirm.value = false
  showSendRequestModal.value = false
  emit('update')
}

// --- REJECT LOGIC ---
const showRejectModal = ref(false)
const showRejectDoubleConfirm = ref(false)
const rejectReason = ref('')

const openRejectModal = () => {
  rejectReason.value = ''
  showRejectModal.value = true
}

const handleRejectClick = () => {
  const isReasonValid = rejectReason.value && rejectReason.value.trim().length > 0 && rejectReason.value !== '<p><br></p>'
  if (!isReasonValid) {
    // Rely on tooltip/disabled state, but double check here
    return
  }
  showRejectDoubleConfirm.value = true
}

const isRejectValid = computed(() => {
  return rejectReason.value && rejectReason.value.trim().length > 0 && rejectReason.value !== '<p><br></p>'
})

const confirmReject = () => {
  // Update status
  const updatedJournal = { ...props.manuscript.raw_data }
  updatedJournal.status = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  
  // Add history
  if (!updatedJournal.reviewHistory) updatedJournal.reviewHistory = []
  updatedJournal.reviewHistory.push({
    date: new Date().toISOString().split('T')[0],
    actor: 'Editor',
    action: 'Rejected revision',
    comment: rejectReason.value
  })

  // Update store
  userStore.updateJournal(updatedJournal)

  // Notify author
  const existingNotifications = JSON.parse(localStorage.getItem('notifications') || '[]')
  existingNotifications.unshift({
    id: Date.now(),
    title: t('editor.audit.revisionHandling.alerts.notification.rejectedTitle'),
    message: t('editor.audit.revisionHandling.alerts.notification.rejectedMsg', { id: props.manuscript.ms_id, comment: rejectReason.value }),
    type: 'error',
    createdAt: new Date().toISOString(),
    isRead: false,
    targetUser: props.manuscript.writer
  })
  localStorage.setItem('notifications', JSON.stringify(existingNotifications))

  showRejectDoubleConfirm.value = false
  showRejectModal.value = false
  emit('update')
}

</script>

<template>
  <div class="detail-container">
    <!-- Header -->
    <div class="detail-header">
      <button class="back-btn" @click="$emit('back')">{{ t('editor.audit.revisionHandling.detail.backToList') }}</button>
      <div class="meta-info">
        <h2>{{ manuscript.title }}</h2>
        <div class="meta-row">
          <span class="meta-item"><strong>{{ t('editor.audit.revisionHandling.detail.id') }}</strong> {{ manuscript.ms_id }}</span>
          <span class="meta-item"><strong>{{ t('editor.audit.revisionHandling.detail.status') }}</strong> <span class="status-tag">{{ manuscript.status.replace('_', ' ').toUpperCase() }}</span></span>
          <span class="meta-item"><strong>{{ t('editor.audit.revisionHandling.detail.submitted') }}</strong> {{ manuscript.submit_time }}</span>
        </div>
      </div>
    </div>

    <!-- Content Area -->
    <div class="content-area">
      <div class="tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'preview' }" 
          @click="activeTab = 'preview'"
        >
          {{ t('editor.audit.revisionHandling.detail.tabs.preview') }}
        </button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'response' }" 
          @click="activeTab = 'response'"
        >
          {{ t('editor.audit.revisionHandling.detail.tabs.response') }}
        </button>
      </div>

      <div class="tab-content">
        <!-- Preview Tab -->
        <div v-show="activeTab === 'preview'" class="preview-panel">
          <div class="preview-mock">
            <p class="preview-note">{{ t('editor.audit.revisionHandling.detail.preview.simulationNote') }}</p>
            <div class="document-page">
              <h3>{{ t('editor.audit.revisionHandling.detail.preview.introduction') }}</h3>
              <p v-html="t('editor.audit.revisionHandling.detail.preview.trackChanges', { old: '<del style=\'color:red;background:#ffe6e6;\'>old</del>', new: '<ins style=\'color:green;background:#e6ffec;\'>new</ins>' })"></p>
              <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
              <br><br>
              <p>... (More content) ...</p>
            </div>
          </div>
          <div class="preview-confirmation">
            <label>
              <input type="checkbox" v-model="isPreviewed"> {{ t('editor.audit.revisionHandling.detail.preview.reviewedLabel') }}
            </label>
          </div>
        </div>

        <!-- Response Tab -->
        <div v-show="activeTab === 'response'" class="response-panel">
          <!-- Reviewer Comments Summary (Collapsible in Response Tab too for reference) -->
          <div class="reviewer-comments-section">
            <div class="collapse-header" @click="isReviewerCommentsCollapsed = !isReviewerCommentsCollapsed">
              <span>{{ t('editor.audit.revisionHandling.detail.response.originalComments') }}</span>
              <span class="arrow" :class="{ 'collapsed': isReviewerCommentsCollapsed }">▼</span>
            </div>
            <div class="collapse-content" v-show="!isReviewerCommentsCollapsed">
              <div v-for="(reviewer, index) in reviewerComments" :key="index" class="reviewer-block">
                <strong>{{ reviewer.reviewerId }}:</strong>
                <ul>
                  <li v-for="(comment, cIndex) in reviewer.comments" :key="cIndex">Comment {{ cIndex + 1 }}: {{ comment }}</li>
                </ul>
              </div>
            </div>
          </div>

          <div class="author-response">
            <h3>{{ t('editor.audit.revisionHandling.detail.response.authorResponse') }}</h3>
            <div class="response-item" v-for="(reviewer, index) in reviewerComments" :key="index">
              <h4>{{ t('editor.audit.revisionHandling.detail.response.responseTo', { reviewer: reviewer.reviewerId }) }}</h4>
              <div class="response-box">
                <p><strong>{{ t('editor.audit.revisionHandling.detail.response.authorLabel') }}</strong> {{ t('editor.audit.revisionHandling.detail.response.thankYou') }}</p>
                <div class="quote-box">
                  <em>"{{ reviewer.comments[0] }}"</em>
                </div>
                <p>{{ t('editor.audit.revisionHandling.detail.response.updatedFigure') }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Actions Footer -->
    <div class="actions-footer">
      <button class="btn btn-danger" @click="openRejectModal">{{ t('editor.audit.revisionHandling.detail.actions.reject') }}</button>
      <div class="right-actions">
        <button class="btn btn-warning" @click="openSendRequestModal">{{ t('editor.audit.revisionHandling.detail.actions.requestFurther') }}</button>
        <button class="btn btn-success" @click="handleApproveClick">{{ t('editor.audit.revisionHandling.detail.actions.approve') }}</button>
      </div>
    </div>

    <!-- MODALS -->

    <!-- 1. Approve Confirm Modal -->
    <div v-if="showApproveModal" class="modal-overlay">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.detail.modals.approve.title') }}</h3>
          <button class="close-btn" @click="showApproveModal = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>{{ t('editor.audit.revisionHandling.detail.modals.approve.msg') }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showApproveModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-success" @click="confirmApprove">{{ t('editor.audit.revisionHandling.detail.actions.approve') }}</button>
        </div>
      </div>
    </div>

    <!-- 2. Send Request Modal (Reused) -->
    <div v-if="showSendRequestModal" class="modal-overlay">
      <div class="modal-box modal-lg">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.title') }}</h3>
          <button class="close-btn" @click="showSendRequestModal = false">&times;</button>
        </div>
        <div class="modal-content">
          <p class="mb-4">{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.draftMsg', { id: manuscript.ms_id }) }}</p>

          <!-- Reviewer Comments Summary -->
          <div class="reviewer-comments-section">
            <div class="collapse-header" @click="isReviewerCommentsCollapsed = !isReviewerCommentsCollapsed">
              <span>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.commentsSummary') }}</span>
              <span class="arrow" :class="{ 'collapsed': isReviewerCommentsCollapsed }">▼</span>
            </div>
            <div class="collapse-content" v-show="!isReviewerCommentsCollapsed">
              <div v-for="(reviewer, index) in reviewerComments" :key="index" class="reviewer-block">
                <strong>{{ reviewer.reviewerId }}:</strong>
                <ul>
                  <li v-for="(comment, cIndex) in reviewer.comments" :key="cIndex">Comment {{ cIndex + 1 }}: {{ comment }}</li>
                </ul>
              </div>
            </div>
          </div>

          <!-- Revision Requirements -->
          <div class="form-group">
             <div class="row">
               <div class="col">
                 <label>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.revisionType') }}</label>
                 <select v-model="revisionType" class="form-control">
                   <option>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.types.minor') }}</option>
                   <option>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.types.major') }}</option>
                 </select>
               </div>
               <div class="col">
                 <label>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.deadline') }}</label>
                 <input type="date" v-model="revisionDeadline" class="form-control">
               </div>
             </div>
          </div>

          <div class="form-group">
            <label>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.requirementsLabel') }}</label>
            <div class="editor-tip">{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.requirementsTip') }}</div>
            <div class="quill-wrapper">
              <QuillEditor theme="snow" v-model:content="sendRequestComment" contentType="html" toolbar="essential" style="height: 200px;" />
            </div>
          </div>

          <!-- Editorial Declaration -->
          <div class="editorial-declaration">
            <h4>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.declaration.title') }}</h4>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" v-model="editorialDeclarations.reviewedComments">
                <span>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.declaration.reviewedComments') }}</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="editorialDeclarations.deadlineGuidelines">
                <span>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.declaration.deadlineGuidelines') }}</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="editorialDeclarations.scopePolicy">
                <span>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.declaration.scopePolicy') }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showSendRequestModal = false">{{ t('common.cancel') }}</button>
          <div class="btn-wrapper" :title="getSendRequestTooltip">
            <button 
              class="btn btn-primary" 
              @click="handleSendRequestClick"
              :disabled="!isSendRequestValid"
            >
               {{ t('common.submit') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Send Request Double Confirm -->
    <div v-if="showSendRequestDoubleConfirm" class="modal-overlay" style="z-index: 1100;">
      <div class="modal-box" style="width: 400px;">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.doubleConfirm.title') }}</h3>
          <button class="close-btn" @click="showSendRequestDoubleConfirm = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>{{ t('editor.audit.revisionHandling.detail.modals.sendRequest.doubleConfirm.msg') }}</p>
          <p class="text-muted" style="font-size: 0.9rem; margin-top: 10px;">
            {{ t('editor.audit.revisionHandling.detail.modals.sendRequest.doubleConfirm.note') }}
          </p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showSendRequestDoubleConfirm = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="confirmSendRequest">{{ t('common.confirm') }}</button>
        </div>
      </div>
    </div>

    <!-- 3. Reject Modal -->
    <div v-if="showRejectModal" class="modal-overlay">
      <div class="modal-box modal-lg">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.detail.modals.reject.title') }}</h3>
          <button class="close-btn" @click="showRejectModal = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>{{ t('editor.audit.revisionHandling.detail.modals.reject.areYouSure', { id: manuscript.ms_id }) }}</p>
          
          <div class="form-group">
            <label>{{ t('editor.audit.revisionHandling.detail.modals.reject.reasonLabel') }}</label>
            <div class="editor-tip warning">{{ t('editor.audit.revisionHandling.detail.modals.reject.reasonTip') }}</div>
            <div class="quill-wrapper">
              <QuillEditor theme="snow" v-model:content="rejectReason" contentType="html" toolbar="essential" style="height: 200px;" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRejectModal = false">{{ t('common.cancel') }}</button>
          <div class="btn-wrapper" :title="!isRejectValid ? t('editor.audit.revisionHandling.detail.modals.reject.reasonRequiredTooltip') : ''">
             <button class="btn btn-danger" @click="handleRejectClick" :disabled="!isRejectValid">{{ t('editor.audit.revisionHandling.detail.actions.reject') }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reject Double Confirm (High Risk) -->
    <div v-if="showRejectDoubleConfirm" class="modal-overlay" style="z-index: 1100;">
      <div class="modal-box warning-box" style="width: 450px;">
        <div class="modal-header warning-header">
          <h3>{{ t('editor.audit.revisionHandling.detail.modals.reject.doubleConfirm.title') }}</h3>
          <button class="close-btn" @click="showRejectDoubleConfirm = false">&times;</button>
        </div>
        <div class="modal-content">
          <p style="color: #d32f2f; font-weight: 600;">{{ t('editor.audit.revisionHandling.detail.modals.reject.doubleConfirm.msg') }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showRejectDoubleConfirm = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-danger" @click="confirmReject">{{ t('editor.audit.revisionHandling.detail.modals.reject.doubleConfirm.confirmBtn') }}</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.detail-container { background: #fff; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); display: flex; flex-direction: column; min-height: 80vh; }
.detail-header { padding: 1.5rem; border-bottom: 1px solid #eee; background: #f8f9fa; }
.back-btn { background: none; border: none; color: #666; cursor: pointer; margin-bottom: 1rem; padding: 0; font-size: 0.9rem; }
.back-btn:hover { color: #007bff; text-decoration: underline; }
.meta-info h2 { margin: 0 0 0.5rem 0; font-size: 1.4rem; color: #333; }
.meta-row { display: flex; gap: 2rem; color: #555; font-size: 0.9rem; }
.status-tag { background: #e2e6ea; color: #495057; padding: 0.2rem 0.5rem; border-radius: 4px; font-weight: 500; font-size: 0.8rem; }

.content-area { flex: 1; padding: 1.5rem; display: flex; flex-direction: column; }
.tabs { display: flex; gap: 0.5rem; border-bottom: 1px solid #ddd; margin-bottom: 1.5rem; }
.tab-btn { padding: 0.8rem 1.5rem; background: none; border: none; border-bottom: 3px solid transparent; cursor: pointer; font-weight: 500; color: #666; }
.tab-btn.active { color: #007bff; border-bottom-color: #007bff; }
.tab-btn:hover:not(.active) { background: #f1f1f1; }

.preview-panel, .response-panel { flex: 1; display: flex; flex-direction: column; }
.preview-mock { border: 1px solid #eee; background: #fafafa; padding: 2rem; border-radius: 4px; min-height: 400px; margin-bottom: 1rem; overflow-y: auto; max-height: 500px; }
.preview-note { color: #999; text-align: center; margin-bottom: 2rem; font-style: italic; }
.document-page { background: white; padding: 2rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); max-width: 800px; margin: 0 auto; line-height: 1.6; }
.preview-confirmation { padding: 1rem; background: #e8f5e9; border: 1px solid #c8e6c9; border-radius: 4px; }

.reviewer-comments-section { border: 1px solid #ddd; border-radius: 4px; margin-bottom: 1.5rem; overflow: hidden; }
.collapse-header { background: #f8f9fa; padding: 10px 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; font-weight: 600; user-select: none; }
.collapse-header:hover { background: #e9ecef; }
.arrow { transition: transform 0.3s; font-size: 0.8rem; }
.arrow.collapsed { transform: rotate(-90deg); }
.collapse-content { padding: 15px; border-top: 1px solid #ddd; background: #fff; max-height: 300px; overflow-y: auto; }
.reviewer-block { margin-bottom: 10px; }
.reviewer-block strong { display: block; margin-bottom: 5px; color: #555; }
.reviewer-block ul { margin: 0; padding-left: 20px; color: #666; font-size: 0.9rem; }
.reviewer-block li { margin-bottom: 4px; }

.author-response { margin-top: 1rem; }
.author-response h3 { font-size: 1.2rem; border-bottom: 2px solid #007bff; padding-bottom: 0.5rem; margin-bottom: 1rem; }
.response-item { margin-bottom: 1.5rem; }
.response-item h4 { font-size: 1rem; margin-bottom: 0.5rem; color: #444; }
.response-box { background: #f9f9f9; padding: 1.5rem; border-radius: 4px; border-left: 4px solid #007bff; }
.quote-box { background: #e9ecef; padding: 0.5rem 1rem; margin: 0.5rem 0; border-radius: 4px; color: #555; font-size: 0.9rem; }

.actions-footer { padding: 1.5rem; border-top: 1px solid #eee; background: #fff; display: flex; justify-content: space-between; align-items: center; position: sticky; bottom: 0; }
.right-actions { display: flex; gap: 1rem; }

/* Reuse styles from RevisionHandling */
.btn { padding: 0.5rem 1rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; color: white; font-size: 0.9rem; transition: 0.2s; }
.btn-success { background: #28a745; }
.btn-warning { background: #ffc107; color: #333; }
.btn-danger { background: #dc3545; }
.btn-secondary { background: #6c757d; }
.btn-primary { background: #007bff; }
.btn:hover { opacity: 0.9; }
.btn:disabled { background: #ccc; cursor: not-allowed; opacity: 0.7; }

.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-box { background: white; width: 500px; max-width: 90%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; max-height: 90vh; }
.modal-lg { width: 800px; }
.modal-header { padding: 1rem 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.2rem; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }
.modal-content { padding: 1.5rem; overflow-y: auto; }
.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; }

.form-group { margin-top: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-control { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; }
.row { display: flex; gap: 1rem; }
.col { flex: 1; }
.mb-4 { margin-bottom: 1.5rem; }

.editor-tip { font-size: 0.85rem; color: #666; background: #e3f2fd; padding: 8px; border-radius: 4px; margin-bottom: 8px; border-left: 3px solid #2196f3; }
.editor-tip.warning { background: #ffebee; border-left-color: #d32f2f; color: #b71c1c; }
.quill-wrapper { background: #fff; }
.editorial-declaration { margin-top: 2rem; background: #f9f9f9; padding: 15px; border-radius: 4px; border: 1px solid #eee; }
.editorial-declaration h4 { margin: 0 0 10px 0; font-size: 1rem; color: #333; }
.checkbox-group { display: flex; flex-direction: column; gap: 8px; }
.checkbox-item { display: flex; align-items: flex-start; gap: 8px; cursor: pointer; font-size: 0.9rem; color: #555; }
.checkbox-item input { margin-top: 3px; }

.warning-box { border-top: 5px solid #d32f2f; }
.warning-header h3 { color: #d32f2f; }
</style>
