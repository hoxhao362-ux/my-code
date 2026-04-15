<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from '../../../composables/useI18n'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import Navigation from '../../../components/Navigation.vue'
import { truncateText } from '../../../utils/helpers'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'
import RevisionAuditDetail from './RevisionAuditDetail.vue'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Stage 2: Editor receives revision (Journal Platform Editor Norms)
// Auth Filter: Only Editor can access
const authFilter = () => {
  if (user.value?.role !== 'editor' && user.value?.role !== 'admin') {
    router.push('/login') // Or access denied page
    return false
  }
  return true
}

onMounted(() => {
  if (!authFilter()) return
  loadRevisions()
})

/**
 * 临时模拟接口 - 待后端提供 /api/revision/pending 后替换
 * 获取待处理的修订稿列表
 */
const getPendingRevisions = async () => {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500))
  // Return filtered data from store (Frontend Simulation)
  return userStore.journals.filter(journal => 
    [MANUSCRIPT_STATUS.REVISION_SUBMITTED].includes(journal.status)
  ).map(journal => ({
    // Align fields with actual code as per requirement
    ms_id: journal.id,
    title: journal.title,
    author: journal.author,
    submit_time: journal.lastUpdated || journal.date, // Use update time as revision time
    revision_note: journal.revisionNote || 'No response provided.',
    revision_type: journal.revisionType || 'Minor Revision', // Mock revision type
    deadline: journal.deadline || '2026-03-01', // Mock deadline
    status: journal.status,
    version: journal.version || 'R1', // Journal Platform: Version Control
    format_checked: journal.format_checked || false, // Journal Platform: Format Check Status
    raw_data: journal // Keep reference to original object for updates
  }))
}

const revisionList = ref([])
const loading = ref(true)

const loadRevisions = async () => {
  loading.value = true
  try {
    revisionList.value = await getPendingRevisions()
  } catch (e) {
    console.error('Failed to load revisions', e)
  } finally {
    loading.value = false
  }
}

// View Switching Logic
const currentView = ref('list') // 'list' | 'detail'
const detailItem = ref(null)

const openDetailView = (item) => {
  detailItem.value = item
  currentView.value = 'detail'
}

const handleBackToList = () => {
  currentView.value = 'list'
  detailItem.value = null
}

const handleDetailUpdate = async () => {
  currentView.value = 'list'
  detailItem.value = null
  await loadRevisions()
}

// Stage 3: Editor Audits Revision (Legacy logic for other statuses)
// Preview Linkage
const showPreviewModal = ref(false)
const selectedPreviewItem = ref(null)
const activePreviewTab = ref('reviewerComments') // reviewerComments, manuscriptPreview, revisionHistory

const previewRevisionFile = (item) => {
  selectedPreviewItem.value = item
  activePreviewTab.value = 'reviewerComments' // 默认显示审稿人意见
  showPreviewModal.value = true
}

const closePreviewModal = () => {
  showPreviewModal.value = false
  selectedPreviewItem.value = null
}

// 获取模拟的审稿人意见
const getReviewerComments = (item) => {
  // 尝试从稿件数据中获取真实评论
  if (item.raw_data && item.raw_data.reviews && item.raw_data.reviews.length > 0) {
    return item.raw_data.reviews.map((review, index) => ({
      reviewerId: `Reviewer #${index + 1}`,
      realName: review.reviewer, // 保存真实姓名供编辑参考
      comments: typeof review.comments === 'string' ? [review.comments] : 
                typeof review.comment === 'string' ? [review.comment] : 
                review.comments || review.comment || []
    })).filter(reviewer => reviewer.comments && reviewer.comments.length > 0)
  }
  // 尝试从 reviewHistory 中获取评论
  if (item.raw_data && item.raw_data.reviewHistory && item.raw_data.reviewHistory.length > 0) {
    return item.raw_data.reviewHistory.map((review, index) => ({
      reviewerId: `Reviewer #${index + 1}`,
      realName: review.reviewer, // 保存真实姓名供编辑参考
      comments: typeof review.comment === 'string' ? [review.comment] : 
                review.comment || []
    })).filter(reviewer => reviewer.comments && reviewer.comments.length > 0)
  }
  // 模拟数据作为 fallback
  return [
    {
      reviewerId: 'Reviewer #1',
      comments: [
        'The methodology section requires clarification on sample size calculation.',
        'Figure 2 needs to be updated to include the new data points.'
      ]
    },
    {
      reviewerId: 'Reviewer #2',
      comments: [
        'The discussion should be revised to better contextualize the findings.'
      ]
    }
  ]
}

// 获取模拟的稿件内容
const getManuscriptContent = (item) => {
  if (item.raw_data && item.raw_data.content) {
    return item.raw_data.content
  }
  return `[Simulation] This is the manuscript content for MS ID: ${item.ms_id}\n...`
}

// 获取模拟的修订历史
const getRevisionHistory = (item) => {
  if (item.raw_data && item.raw_data.reviewHistory && item.raw_data.reviewHistory.length > 0) {
    return item.raw_data.reviewHistory
  }
  return []
}

// Audit Linkage
const showConfirmModal = ref(false)
const showDoubleConfirm = ref(false) // Double confirm for Approve/Reject
const selectedItem = ref(null)
const actionType = ref('') // 'approve', 'reject', 'revision'
const comment = ref('') 

// Journal Platform: Format Check
const showFormatCheckModal = ref(false)
const formatChecklist = ref([
  { id: 1, label: t('editor.audit.revisionHandling.formatCheck.checklist.wordCount'), checked: false },
  { id: 2, label: t('editor.audit.revisionHandling.formatCheck.checklist.abstract'), checked: false },
  { id: 3, label: t('editor.audit.revisionHandling.formatCheck.checklist.coi'), checked: false },
  { id: 4, label: t('editor.audit.revisionHandling.formatCheck.checklist.figures'), checked: false },
  { id: 5, label: t('editor.audit.revisionHandling.formatCheck.checklist.references'), checked: false }
])

const openFormatCheck = (item) => {
  selectedItem.value = item
  // Reset checklist
  formatChecklist.value.forEach(i => i.checked = false)
  showFormatCheckModal.value = true
}

const confirmFormatCheck = () => {
  const allChecked = formatChecklist.value.every(i => i.checked)
  if (!allChecked) {
    toastStore.add({ message: t('editor.audit.revisionHandling.alerts.allChecksRequired'), type: 'warning' })
    return
  }
  
  if (selectedItem.value) {
    selectedItem.value.format_checked = true
    const journal = selectedItem.value.raw_data
    journal.format_checked = true
    userStore.updateJournal(journal)
  }
  showFormatCheckModal.value = false
  toastStore.add({ message: t('editor.audit.revisionHandling.alerts.formatPassed'), type: 'success' })
}

// Journal Platform: Re-review Coordination
const showReviewerSelectModal = ref(false)
const selectedReviewers = ref([])
const availableReviewers = ref([])

const openAuditModal = (item, action) => {
  selectedItem.value = item
  actionType.value = action
  comment.value = ''
  
  if (action === 'revision') {
    // Open Reviewer Selection for Re-review
    // Load all reviewers from userStore
    availableReviewers.value = userStore.users
      .filter(user => user.role === 'reviewer')
      .map(user => ({
        id: user.id || user.username,
        name: user.username,
        status: 'Available'
      }))
    
    // If no reviewers in store, use mock data as fallback
    if (availableReviewers.value.length === 0) {
      availableReviewers.value = [
        { id: 'r1', name: 'Dr. Smith (Reviewer 1)', status: 'Available' },
        { id: 'r2', name: 'Prof. Johnson (Reviewer 2)', status: 'Available' },
        { id: 'r3', name: 'Dr. Lee (New)', status: 'Available' }
      ]
    }
    
    selectedReviewers.value = availableReviewers.value.slice(0, 2).map(r => r.id) // Default to first two reviewers
    showReviewerSelectModal.value = true
  } else {
    showConfirmModal.value = true
  }
}

const confirmReReview = () => {
  showReviewerSelectModal.value = false
  // Proceed to confirmation with selected reviewers note
  comment.value = t('editor.audit.revisionHandling.alerts.sentToReviewers', { reviewers: selectedReviewers.value.join(', ') })
  showConfirmModal.value = true
}

const isCommentValid = computed(() => {
  return comment.value && comment.value.trim().length > 0 && comment.value !== '<p><br></p>'
})

const getConfirmTooltip = computed(() => {
  if (!isCommentValid.value) return t('editor.audit.decisionMaking.alerts.enterComments')
  return ''
})

const handleConfirmClick = () => {
  if (!isCommentValid.value) return
  showDoubleConfirm.value = true
}

/**
 * 审核修订稿
 */
const auditRevision = async () => {
  if (!selectedItem.value) return

  // Determine new status based on action
  let newStatus = ''
  let historyAction = ''
  let notificationTitle = ''
  let notificationMsg = ''

  if (actionType.value === 'approve') {
    newStatus = MANUSCRIPT_STATUS.REVIEW_COMPLETED 
    historyAction = 'Approved revision'
    notificationTitle = t('editor.audit.revisionHandling.alerts.notification.approvedTitle')
    notificationMsg = t('editor.audit.revisionHandling.alerts.notification.approvedMsg', { id: selectedItem.value.ms_id, comment: comment.value })
  } else if (actionType.value === 'reject') {
    newStatus = MANUSCRIPT_STATUS.REVISION_REQUIRED
    historyAction = 'Returned for revision'
    notificationTitle = t('editor.audit.revisionHandling.alerts.notification.rejectedTitle')
    notificationMsg = t('editor.audit.revisionHandling.alerts.notification.rejectedMsg', { id: selectedItem.value.ms_id, comment: comment.value })
  } else if (actionType.value === 'revision') {
    newStatus = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW // Return to reviewers
    historyAction = 'Sent back to reviewers for re-review'
    notificationTitle = t('editor.audit.revisionHandling.alerts.notification.statusUpdateTitle')
    notificationMsg = t('editor.audit.revisionHandling.alerts.notification.reReviewMsg')
  }

  // Update Status (Frontend Simulation)
  const journal = selectedItem.value.raw_data
  const updatedJournal = { ...journal }
  updatedJournal.status = newStatus
  
  // If sent back to reviewers for re-review, set reviewStage to 'Re-review'
  if (actionType.value === 'revision') {
    updatedJournal.reviewStage = 'Re-review'
    // Assign selected reviewers to the manuscript (store both id and name)
    if (selectedReviewers.value && selectedReviewers.value.length > 0) {
      updatedJournal.assignedReviewers = selectedReviewers.value.map(id => {
        const reviewer = availableReviewers.value.find(r => String(r.id) === String(id))
        return reviewer ? { id: reviewer.id, name: reviewer.name } : { id: id, name: id }
      })
    }
  }
  
  // Add History Entry
  const historyEntry = {
    date: new Date().toISOString().split('T')[0],
    actor: `Editor ${user.value.username}`,
    action: historyAction,
    comment: comment.value
  }
  if (!updatedJournal.reviewHistory) updatedJournal.reviewHistory = []
  updatedJournal.reviewHistory.push(historyEntry)

  // Update Store
  userStore.updateJournal(updatedJournal)

  // Stage 4: Feedback (Notification)
  // Simulate sending notification to author via shared localStorage
  const existingNotifications = JSON.parse(localStorage.getItem('notifications') || '[]')
  
  // Notify Author
  existingNotifications.unshift({
    id: Date.now(),
    title: notificationTitle,
    message: notificationMsg,
    type: actionType.value === 'approve' ? 'success' : actionType.value === 'reject' ? 'error' : 'info',
    createdAt: new Date().toISOString(),
    isRead: false,
    targetUser: selectedItem.value.author // Target user
  })

  // If sent back to reviewers, notify them (Mock)
  if (actionType.value === 'revision') {
     existingNotifications.unshift({
        id: Date.now() + 1,
        title: t('editor.audit.revisionHandling.alerts.notification.reReviewTitle'),
        message: t('editor.audit.revisionHandling.alerts.notification.reviewerMsg', { id: selectedItem.value.ms_id }),
        type: 'warning',
        createdAt: new Date().toISOString(),
        isRead: false,
        targetRole: 'reviewer' 
     })
  }

  localStorage.setItem('notifications', JSON.stringify(existingNotifications))
  
  // Close Modals
  showDoubleConfirm.value = false
  showConfirmModal.value = false
  
  await loadRevisions()
  
  toastStore.add({ message: t('editor.audit.revisionHandling.alerts.auditSuccess', { 
    id: selectedItem.value.ms_id, 
    action: actionType.value === 'approve' ? t('editor.audit.revisionHandling.actions.approve').toLowerCase() : 
            actionType.value === 'reject' ? t('editor.audit.revisionHandling.actions.returnForRevision').toLowerCase() : 
            actionType.value 
  }), type: 'success' })
}
</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-revision-handling" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <template v-if="currentView === 'list'">
        <div class="header">
          <h1>{{ t('editor.audit.revisionHandling.title') }}</h1>
          <p class="subtitle">{{ t('editor.audit.revisionHandling.subtitle') }}</p>
        </div>

        <div class="table-container">
          <table class="revision-table">
            <thead>
              <tr>
                <th>{{ t('editor.audit.revisionHandling.columns.id') }}</th>
                <th>{{ t('editor.audit.revisionHandling.columns.title') }}</th>
                <th>{{ t('editor.audit.revisionHandling.columns.version') }}</th>
                <th>{{ t('editor.audit.revisionHandling.columns.deadline') }}</th>
                <th>{{ t('editor.audit.revisionHandling.columns.status') }}</th>
                <th>{{ t('editor.audit.revisionHandling.columns.formatCheck') }}</th>
                <th>{{ t('editor.audit.revisionHandling.columns.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="7" class="text-center">{{ t('common.loading') }}</td>
              </tr>
              <tr v-else-if="revisionList.length === 0">
                <td colspan="7" class="text-center">{{ t('editor.audit.revisionHandling.noManuscripts') }}</td>
              </tr>
              <tr v-else v-for="item in revisionList" :key="item.ms_id">
                <td>{{ item.ms_id }}</td>
                <td class="title-cell" :title="item.title">{{ truncateText(item.title, 30) }}</td>
                <td><span class="version-tag">{{ item.version }}</span></td>
                <td>
                  <span :class="{'text-danger': new Date(item.deadline) < new Date()}">
                    {{ new Date(item.deadline).toLocaleDateString() }}
                  </span>
                </td>
                <td>
                  <span class="status-tag">{{ item.status.replace('_', ' ').toUpperCase() }}</span>
                </td>
                <td>
                  <span v-if="item.format_checked" class="check-pass">{{ t('editor.audit.revisionHandling.formatCheck.passed') }}</span>
                  <button v-else class="btn btn-sm btn-outline" @click="openFormatCheck(item)">{{ t('editor.audit.revisionHandling.formatCheck.runCheck') }}</button>
                </td>
                <td class="actions-cell">
                  <button class="btn btn-sm btn-info" @click="previewRevisionFile(item)">{{ t('editor.audit.revisionHandling.actions.preview') }}</button>
                  <button class="btn btn-sm btn-success" :disabled="!item.format_checked" @click="openAuditModal(item, 'approve')">{{ t('editor.audit.revisionHandling.actions.approve') }}</button>
                  <button class="btn btn-sm btn-warning" :disabled="!item.format_checked" @click="openAuditModal(item, 'revision')">{{ t('editor.audit.revisionHandling.actions.reReview') }}</button>
                  <button class="btn btn-sm btn-danger" @click="openAuditModal(item, 'reject')">{{ t('editor.audit.revisionHandling.actions.returnForRevision') }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>

      <template v-else>
        <RevisionAuditDetail 
          :manuscript="detailItem" 
          @back="handleBackToList" 
          @update="handleDetailUpdate" 
        />
      </template>
    </main>

    <!-- Format Check Modal -->
    <div v-if="showFormatCheckModal" class="modal-overlay">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.formatCheck.title') }}</h3>
          <button class="close-btn" @click="showFormatCheckModal = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>{{ t('editor.audit.revisionHandling.formatCheck.verifyItems', { version: selectedItem?.version }) }}</p>
          <div class="checklist">
             <div v-for="check in formatChecklist" :key="check.id" class="check-item">
               <label>
                 <input type="checkbox" v-model="check.checked">
                 {{ check.label }}
               </label>
             </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showFormatCheckModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="confirmFormatCheck">{{ t('editor.audit.revisionHandling.formatCheck.passBtn') }}</button>
        </div>
      </div>
    </div>

    <!-- Reviewer Selection Modal -->
    <div v-if="showReviewerSelectModal" class="modal-overlay">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.reReview.title') }}</h3>
          <button class="close-btn" @click="showReviewerSelectModal = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>{{ t('editor.audit.revisionHandling.reReview.selectReviewers') }}</p>
          <div class="reviewer-list">
             <div v-for="r in availableReviewers" :key="r.id" class="reviewer-select-item">
               <label>
                 <input type="checkbox" :value="r.id" v-model="selectedReviewers">
                 {{ r.name }} <span class="badge">{{ r.status }}</span>
               </label>
             </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showReviewerSelectModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="confirmReReview">{{ t('editor.audit.revisionHandling.reReview.sendBtn') }}</button>
        </div>
      </div>
    </div>

    <!-- Confirm Modal (Reuse project style) for Legacy Actions -->
    <div v-if="showConfirmModal" class="modal-overlay">
      <div class="modal-box modal-lg">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.modals.confirmAction', { action: actionType.toUpperCase() }) }}</h3>
          <button class="close-btn" @click="showConfirmModal = false">&times;</button>
        </div>
        <div class="modal-content">
          <p>
            {{ t('editor.audit.revisionHandling.modals.areYouSure', { action: actionType, id: selectedItem?.ms_id }) }}
          </p>

          <div class="form-group">
            <label>{{ actionType === 'approve' || actionType === 'reject' ? t('editor.audit.revisionHandling.modals.editorComment') : t('editor.audit.revisionHandling.modals.editorCommentsOptional') }}</label>
            
            <template v-if="actionType === 'approve' || actionType === 'reject'">
               <div class="editor-tip" v-if="actionType === 'approve'">{{ t('editor.audit.revisionHandling.modals.approveRationale') }}</div>
               <div class="editor-tip warning" v-else-if="actionType === 'reject'">{{ t('editor.audit.revisionHandling.modals.rejectRationale') }}</div>
               
               <textarea v-model="comment" rows="6" class="form-control"></textarea>
            </template>
            <template v-else>
               <textarea v-model="comment" rows="3" :placeholder="t('editor.audit.revisionHandling.modals.commentPlaceholder')" class="form-control"></textarea>
            </template>
          </div>
        </div>
        <div class="modal-footer">
            <button class="btn btn-secondary" @click="showConfirmModal = false">{{ t('common.cancel') }}</button>
            
            <div class="btn-wrapper" :title="getConfirmTooltip">
              <button 
                class="btn" 
                :class="actionType === 'reject' ? 'btn-danger' : actionType === 'approve' ? 'btn-success' : 'btn-primary'" 
                @click="actionType === 'approve' || actionType === 'reject' ? handleConfirmClick() : auditRevision()"
                :disabled="(actionType === 'approve' || actionType === 'reject') && !isCommentValid"
              >
                 {{ t('editor.audit.revisionHandling.modals.confirmBtn', { action: actionType.charAt(0).toUpperCase() + actionType.slice(1) }) }}
              </button>
            </div>
          </div>
      </div>
    </div>

    <!-- Double Confirm Modal for Approve/Reject -->
    <div v-if="showDoubleConfirm" class="modal-overlay" style="z-index: 1100;">
      <div class="modal-box" :class="{ 'warning-box': actionType === 'reject' }" style="width: 450px;">
        <div class="modal-header" :class="{ 'warning-header': actionType === 'reject' }">
          <h3>{{ actionType === 'approve' ? t('editor.audit.revisionHandling.modals.doubleConfirm.approveTitle') : t('editor.audit.revisionHandling.modals.doubleConfirm.rejectTitle') }}</h3>
          <button class="close-btn" @click="showDoubleConfirm = false">&times;</button>
        </div>
        <div class="modal-content">
          <template v-if="actionType === 'approve'">
            <p>{{ t('editor.audit.revisionHandling.modals.doubleConfirm.approveMsg') }}</p>
          </template>
          <template v-else-if="actionType === 'reject'">
            <p style="color: #d32f2f; font-weight: 600;">{{ t('editor.audit.revisionHandling.modals.doubleConfirm.rejectMsg') }}</p>
          </template>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showDoubleConfirm = false">{{ t('common.cancel') }}</button>
          <button class="btn" :class="actionType === 'reject' ? 'btn-danger' : 'btn-success'" @click="auditRevision">{{ t('common.confirm') }}</button>
        </div>
      </div>
    </div>

    <!-- Preview Modal -->
    <div v-if="showPreviewModal" class="modal-overlay" style="z-index: 1050;">
      <div class="modal-box" style="width: 90vw; max-width: 1000px; max-height: 90vh;">
        <div class="modal-header">
          <h3>{{ t('editor.audit.revisionHandling.preview.title', { id: selectedPreviewItem?.ms_id }) }}</h3>
          <button class="close-btn" @click="closePreviewModal">&times;</button>
        </div>
        <div class="modal-content" style="flex: 1; display: flex; flex-direction: column;">
          <!-- Tab Navigation -->
          <div class="tab-navigation">
            <button 
              class="tab-btn" 
              :class="{ 'active': activePreviewTab === 'reviewerComments' }"
              @click="activePreviewTab = 'reviewerComments'"
            >
              {{ t('editor.audit.revisionHandling.preview.tabs.reviewerComments') }}
            </button>
            <button 
              class="tab-btn" 
              :class="{ 'active': activePreviewTab === 'manuscriptPreview' }"
              @click="activePreviewTab = 'manuscriptPreview'"
            >
              {{ t('editor.audit.revisionHandling.preview.tabs.manuscriptPreview') }}
            </button>
            <button 
              class="tab-btn" 
              :class="{ 'active': activePreviewTab === 'revisionHistory' }"
              @click="activePreviewTab = 'revisionHistory'"
            >
              {{ t('editor.audit.revisionHandling.preview.tabs.revisionHistory') }}
            </button>
          </div>
          
          <!-- Tab Content -->
          <div class="tab-content" style="flex: 1; overflow-y: auto;">
            <!-- Reviewer Comments Tab -->
            <div v-if="activePreviewTab === 'reviewerComments'" class="tab-pane">
              <div v-if="selectedPreviewItem">
                <div v-for="(reviewer, index) in getReviewerComments(selectedPreviewItem)" :key="index" class="reviewer-block">
                  <strong>{{ reviewer.reviewerId }}{{ reviewer.realName ? ` (${reviewer.realName})` : '' }}:</strong>
                  <ul>
                    <li v-for="(comment, cIndex) in reviewer.comments" :key="cIndex">
                      {{ comment }}
                    </li>
                  </ul>
                </div>
                <div v-if="getReviewerComments(selectedPreviewItem).length === 0" class="no-content">
                  {{ t('editor.audit.revisionHandling.preview.noContent') }}
                </div>
              </div>
            </div>
            
            <!-- Manuscript Preview Tab -->
            <div v-if="activePreviewTab === 'manuscriptPreview'" class="tab-pane">
              <div v-if="selectedPreviewItem" class="manuscript-content">
                <pre class="content-text">{{ getManuscriptContent(selectedPreviewItem) }}</pre>
              </div>
            </div>
            
            <!-- Revision History Tab -->
            <div v-if="activePreviewTab === 'revisionHistory'" class="tab-pane">
              <div v-if="selectedPreviewItem">
                <div class="history-list">
                  <div v-for="(history, index) in getRevisionHistory(selectedPreviewItem)" :key="index" class="history-item">
                    <div class="history-meta">
                      <span class="history-date">{{ history.date }}</span>
                      <span class="history-actor">{{ history.actor }}</span>
                      <span class="history-action badge">{{ history.action }}</span>
                    </div>
                    <div class="history-comment" v-if="history.comment">
                      {{ history.comment }}
                    </div>
                  </div>
                  <div v-if="getRevisionHistory(selectedPreviewItem).length === 0" class="no-content">
                    {{ t('editor.audit.revisionHandling.preview.noHistory') }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePreviewModal">{{ t('common.close') }}</button>
          <button class="btn btn-primary" @click="openDetailView(selectedPreviewItem); closePreviewModal()">{{ t('editor.audit.revisionHandling.preview.openDetail') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-container {
  padding: 30px;
  background-color: #f9f9f9;
  min-height: 100vh;
  font-family: 'Segoe UI', sans-serif;
  display: flex;
  flex-direction: column;
}

.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.header {
  border-bottom: 2px solid #0056B3;
  margin-bottom: 20px;
  padding-bottom: 10px;
}

.header h1 {
  font-size: 24px;
  color: #333;
  margin: 0;
}

.subtitle {
  font-size: 14px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

.table-container { background: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); overflow: hidden; }
.revision-table { width: 100%; border-collapse: collapse; }
.revision-table th, .revision-table td { padding: 1rem; text-align: left; border-bottom: 1px solid #eee; }
.revision-table th { background: #f8f9fa; font-weight: 600; color: #555; }
.revision-table tr:hover { background: #f1f1f1; }

.version-tag { background: #e0f2f1; color: #00695c; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 0.85rem; }
.status-tag { background: #e2e6ea; color: #495057; padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.8rem; }
.check-pass { color: #28a745; font-weight: bold; }
.text-danger { color: #dc3545; font-weight: bold; }

.actions-cell { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.btn { padding: 0.4rem 0.8rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; color: white; font-size: 0.85rem; transition: 0.2s; }
.btn-sm { font-size: 0.8rem; padding: 0.3rem 0.6rem; }
.btn-info { background: #17a2b8; }
.btn-success { background: #28a745; }
.btn-warning { background: #ffc107; color: #333; }
.btn-danger { background: #dc3545; }
.btn-secondary { background: #6c757d; }
.btn-primary { background: #007bff; }
.btn-outline { background: white; border: 1px solid #007bff; color: #007bff; }
.btn-outline:hover { background: #e3f2fd; }
.btn:hover { opacity: 0.9; }
.btn:disabled { background: #ccc; border-color: #ccc; color: #666; cursor: not-allowed; opacity: 0.7; }

.text-center { text-align: center; color: #999; }

/* Modal Styles */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; }
.modal-box { background: white; width: 500px; max-width: 90%; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); display: flex; flex-direction: column; max-height: 90vh; }
.modal-lg { width: 800px; }
.modal-header { padding: 1rem 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; }
.modal-header h3 { margin: 0; font-size: 1.2rem; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }
.modal-content { padding: 1.5rem; overflow-y: auto; }
.form-group { margin-top: 1rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.form-control { width: 100%; padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; }
.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; }

.checklist { margin-top: 1rem; display: flex; flex-direction: column; gap: 0.8rem; }
.check-item label { display: flex; gap: 0.5rem; align-items: center; cursor: pointer; }
.check-item input[type="checkbox"] { width: 18px; height: 18px; }

.reviewer-select-item { margin-bottom: 0.8rem; padding: 0.5rem; background: #f8f9fa; border-radius: 4px; }
.reviewer-select-item label { display: flex; gap: 0.5rem; align-items: center; cursor: pointer; }
.badge { background: #e3f2fd; color: #0d47a1; font-size: 0.75rem; padding: 2px 6px; border-radius: 4px; margin-left: auto; }

.editor-tip { font-size: 0.85rem; color: #666; background: #e3f2fd; padding: 8px; border-radius: 4px; margin-bottom: 8px; border-left: 3px solid #2196f3; }
.editor-tip.warning { background: #ffebee; border-left-color: #d32f2f; color: #b71c1c; }

.btn-wrapper { display: inline-block; }
.warning-box { border-top: 5px solid #d32f2f; }
.warning-header h3 { color: #d32f2f; }

/* Preview Modal Styles */
.tab-navigation {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 1rem;
  background: #f8f9fa;
}

.tab-btn {
  padding: 0.8rem 1.2rem;
  border: none;
  background: none;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  border-bottom: 3px solid transparent;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #007bff;
  background: #e3f2fd;
}

.tab-btn.active {
  color: #007bff;
  border-bottom-color: #007bff;
  background: white;
}

.tab-content {
  padding: 1rem 0;
}

.tab-pane {
  height: 100%;
}

.reviewer-block {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #007bff;
}

.reviewer-block strong {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 1rem;
  color: #333;
}

.reviewer-block ul {
  margin: 0;
  padding-left: 1.5rem;
}

.reviewer-block li {
  margin-bottom: 0.5rem;
  line-height: 1.5;
  color: #555;
}

.manuscript-content {
  height: 100%;
}

.content-text {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 4px;
  border: 1px solid #ddd;
  white-space: pre-wrap;
  font-family: 'Times New Roman', serif;
  line-height: 1.6;
  color: #333;
  height: 100%;
  min-height: 300px;
}

.history-table {
  width: 100%;
  overflow-x: auto;
}

.history-table table {
  width: 100%;
  border-collapse: collapse;
}

.history-table th,
.history-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.history-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #555;
  white-space: nowrap;
}

.history-table tr:hover {
  background: #f1f1f1;
}

.no-content {
  text-align: center;
  color: #666;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 4px;
  border: 1px solid #ddd;
}

/* Ensure modal content has proper flex layout */
.modal-content {
  display: flex;
  flex-direction: column;
}

.modal-content > .tab-content {
  flex: 1;
  overflow-y: auto;
}
</style>