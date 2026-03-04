<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import SubmissionNavigation from '../submission/components/SubmissionNavigation.vue'
import FlowCheckPanel from './FlowCheckPanel.vue'
import ViewSubmissionModal from './ViewSubmissionModal.vue'
import HistoryModal from './HistoryModal.vue'
import ReviewerStatusModal from './ReviewerStatusModal.vue'
import SubmitRevisionModal from './SubmitRevisionModal.vue'
import { MANUSCRIPT_STATUS, AUTHOR_STATUS_MAP } from '../../constants/manuscriptStatus'

const router = useRouter()
const toastStore = useToastStore()
const flowCheckPanelRef = ref(null)

const handleRunCheck = () => {
  if (flowCheckPanelRef.value) {
    flowCheckPanelRef.value.runCheck(userJournals.value)
  }
}
const userStore = useUserStore()
const user = computed(() => userStore.submissionUser)

// Author submission data
const userJournals = computed(() => {
  // Use submissionUser if available (Author Dashboard Context), fallback to user
  const currentUser = userStore.submissionUser || userStore.user
  if (!currentUser) return []
  return userStore.journals.filter(j => {
    // Robust matching for author field (handle case sensitivity and potential format differences)
    if (!j.author) return false
    return j.author === currentUser.username || 
           j.author.toLowerCase() === currentUser.username.toLowerCase()
  })
})

// Helper to check status groups
const isProcessing = (status) => [
  MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
  MANUSCRIPT_STATUS.UNDER_INITIAL_REVIEW,
  MANUSCRIPT_STATUS.INITIAL_REVIEW_PASSED,
  MANUSCRIPT_STATUS.PENDING_FINAL_DECISION,
  MANUSCRIPT_STATUS.UNDER_FINAL_DECISION
].includes(status)

const isUnderReview = (status) => [
  MANUSCRIPT_STATUS.PENDING_PEER_REVIEW,
  MANUSCRIPT_STATUS.UNDER_PEER_REVIEW,
  MANUSCRIPT_STATUS.REVIEW_COMPLETED
].includes(status)

const isWaitingApproval = (status) => [
  MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION,
  MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
].includes(status)

const isNeedingRevision = (status) => [
  MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION,
  MANUSCRIPT_STATUS.FINAL_DECISION_REVISION,
  MANUSCRIPT_STATUS.REVISION_REQUIRED
].includes(status)

const isRevisionProcessing = (status) => [
  MANUSCRIPT_STATUS.REVISION_SUBMITTED
].includes(status)

const isDecisionMade = (status) => {
  if (!status) return false
  return [
    MANUSCRIPT_STATUS.INITIAL_REVIEW_REJECTED,
    MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  ].includes(status)
}

const isInProduction = (status) => [
  MANUSCRIPT_STATUS.PENDING_COPYRIGHT,
  MANUSCRIPT_STATUS.PENDING_PROOF,
  MANUSCRIPT_STATUS.PENDING_PUBLICATION,
  MANUSCRIPT_STATUS.PUBLISHED
].includes(status)

const isWithdrawn = (status) => [
  MANUSCRIPT_STATUS.WITHDRAWN
].includes(status)

// Menu Groups Configuration
const menuGroups = computed(() => {
  const count = (filterFn) => userJournals.value.filter(filterFn).length
  
  return [
    {
      title: 'New Submissions',
      items: [
        { label: 'Submit New Manuscript', count: null, action: 'submit' },
        { label: 'Submissions Being Processed', count: count(j => isProcessing(j.status)), key: 'processing' },
        { label: 'Submissions Waiting for Author\'s Approval', count: count(j => isWaitingApproval(j.status)), key: 'waiting_approval' },
        { label: 'Under Review', count: count(j => isUnderReview(j.status)), key: 'under_review' }
      ]
    },
    {
      title: 'Revisions',
      items: [
        { label: 'Submissions Needing Revision', count: count(j => isNeedingRevision(j.status)), key: 'needing_revision' },
        { label: 'Revisions Being Processed', count: count(j => isRevisionProcessing(j.status)), key: 'revision_processing' }
      ]
    },
    {
      title: 'Completed',
      items: [
        { label: 'Submissions with a Decision', count: count(j => isDecisionMade(j.status)), key: 'decision_made' },
        { label: 'In Production', count: count(j => isInProduction(j.status)), key: 'in_production' },
        { label: 'Withdrawn', count: count(j => isWithdrawn(j.status)), key: 'withdrawn' }
      ]
    }
  ]
})

// Active selection state
const selectedItemKey = ref(null)

// Handle item click
const handleItemClick = (item) => {
  if (item.action === 'submit') {
    router.push('/submission/author/submit')
    return
  }
  
  // Allow clicking even if count is 0, or strictly following "no correspond status, count 0, do not hide"
  // User says "Prioritize reuse existing...". Existing had `if (item.count > 0)`.
  // But user implies we should be able to see empty lists? "No correspond status... count 0, do not hide".
  // Existing logic prevents clicking if count is 0.
  // I will update this to allow clicking if the user wants to see "Empty" list, 
  // but usually dashboard items with 0 are not clickable if there is nothing to show.
  // However, for "Submissions Being Processed" with 0, clicking shows empty list.
  // The user didn't explicitly say "allow clicking 0 items", just "display 0".
  // I will stick to existing behavior for now (clickable if count > 0) to avoid breaking UX unless necessary.
  if (item.count > 0) {
    selectedItemKey.value = item.key
  }
}

// Get filtered manuscripts for selected item
const selectedManuscripts = computed(() => {
  if (!selectedItemKey.value) return []
  
  switch (selectedItemKey.value) {
    case 'processing': return userJournals.value.filter(j => isProcessing(j.status))
    case 'waiting_approval': return userJournals.value.filter(j => isWaitingApproval(j.status))
    case 'under_review': return userJournals.value.filter(j => isUnderReview(j.status))
    case 'needing_revision': return userJournals.value.filter(j => isNeedingRevision(j.status))
    case 'revision_processing': return userJournals.value.filter(j => isRevisionProcessing(j.status))
    case 'decision_made': return userJournals.value.filter(j => isDecisionMade(j.status))
    case 'in_production': return userJournals.value.filter(j => isInProduction(j.status))
    case 'withdrawn': return userJournals.value.filter(j => isWithdrawn(j.status))
    default: return []
  }
})

// Selected Item Label for header
const selectedItemLabel = computed(() => {
  for (const group of menuGroups.value) {
    const item = group.items.find(i => i.key === selectedItemKey.value)
    if (item) return item.label
  }
  return ''
})

const getAuthorStatusLabel = (manuscript) => {
  // Journal Platform Standard: Submitted status includes ID
  if (manuscript.status === MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW) {
    return `Submitted (Manuscript ID: ${manuscript.id})`
  }
  return AUTHOR_STATUS_MAP[manuscript.status] || manuscript.status
}

// Reviewer Management Logic
const recommendedReviewers = computed(() => userStore.recommendedReviewers)
const showReviewerModal = ref(false)
const showViewSubmissionModal = ref(false)
const showHistoryModal = ref(false)
const showReviewerStatusModal = ref(false)
const showSubmitRevisionModal = ref(false)
const selectedManuscriptForModal = ref(null)

// Action Handlers
const handleSubmitRevision = (manuscript) => {
  selectedManuscriptForModal.value = manuscript
  showSubmitRevisionModal.value = true
}

const handleViewSubmission = (manuscript) => {
  selectedManuscriptForModal.value = manuscript
  showViewSubmissionModal.value = true
}

const handleHistory = (manuscript) => {
  selectedManuscriptForModal.value = manuscript
  showHistoryModal.value = true
}

const handleViewPublicationStatus = (manuscript) => {
  router.push({ name: 'author-publication-status', params: { id: manuscript.id } })
}

const handleReviewers = (manuscript) => {
  if (!isUnderReview(manuscript.status) && !isDecisionMade(manuscript.status)) {
    toastStore.add({ message: 'Manuscript not yet in review process. Please wait for the initial screening to complete.', type: 'warning' })
    return
  }
  
  selectedManuscriptForModal.value = manuscript
  showReviewerStatusModal.value = true
}

const selectedManuscriptForReviewers = ref(null)

const currentManuscriptReviewers = computed(() => {
  if (!selectedManuscriptForReviewers.value) return []
  return recommendedReviewers.value.filter(r => String(r.manuscriptId) === String(selectedManuscriptForReviewers.value.id))
})

const openReviewerModal = (manuscript) => {
  selectedManuscriptForReviewers.value = manuscript
  showReviewerModal.value = true
}

const handleWithdrawRecommendation = (reviewer) => {
  if (!confirm('Are you sure you want to withdraw this recommendation?')) return
  
  const updated = { ...reviewer, status: 'withdrawn', reviewedAt: new Date().toISOString(), reviewedBy: 'author' }
  userStore.updateRecommendedReviewer(updated)
  toastStore.add({ message: 'Recommendation withdrawn successfully.', type: 'success' })
}

</script>

<template>
  <div class="author-dashboard-container">
    <!-- 替换为投稿专用导航 -->
    <SubmissionNavigation />

    <!-- 作者后台内容 -->
    <main class="dashboard-content">
      <div class="dashboard-header-actions">
        <h2 class="dashboard-title">My Manuscripts</h2>
        <button class="btn-flow-check" @click="handleRunCheck">Run Flow Check</button>
      </div>

      <!-- 主内容区域 -->
      <div class="main-lists">
          <div v-for="group in menuGroups" :key="group.title" class="menu-group">
            <h3 class="group-title">{{ group.title }}</h3>
            <ul class="group-list">
              <li v-for="(item, index) in group.items" :key="index" class="list-item">
                <!-- Submit New Manuscript Link -->
                <a 
                  v-if="item.action === 'submit'" 
                  href="#" 
                  class="action-link"
                  @click.prevent="handleItemClick(item)"
                >
                  {{ item.label }}
                </a>
                
                <!-- Status Links -->
                <a 
                  v-else 
                  href="#" 
                  class="status-link"
                  :class="{ 
                    'active': selectedItemKey === item.key, 
                    'disabled': item.count === 0,
                    'clickable': item.count > 0
                  }"
                  @click.prevent="handleItemClick(item)"
                >
                  {{ item.label }} 
                  <span class="count">({{ item.count }})</span>
                </a>
              </li>
            </ul>
          </div>

          <!-- 稿件详情列表区域 (当选中某一项时显示) -->
          <transition name="fade">
            <div v-if="selectedItemKey && selectedManuscripts.length > 0" class="manuscript-details-section">
              <h3 class="details-title">{{ selectedItemLabel }} - Details</h3>
              
              <!-- 列表模板 -->
              <div class="manuscript-list">
                <div v-for="manuscript in selectedManuscripts" :key="manuscript.id" class="manuscript-card">
                   <div class="card-header">
                     <span class="ms-id">#{{ manuscript.id }}</span>
                     <span class="ms-status-badge">{{ getAuthorStatusLabel(manuscript) }}</span>
                   </div>
                   <h4 class="ms-title">{{ manuscript.title }}</h4>
                   <div class="ms-meta">
                     <span>Submitted: {{ manuscript.submittedDate }}</span>
                     <span>Field: {{ manuscript.field }}</span>
                   </div>
                   <div class="card-actions">
                     <button class="action-btn" @click="handleViewSubmission(manuscript)">View Submission</button>
                     <button class="action-btn" @click="handleHistory(manuscript)">History</button>
                     
                     <!-- New Publication Status Button -->
                     <button 
                       v-if="isInProduction(manuscript.status)"
                       class="action-btn btn-primary"
                       @click="handleViewPublicationStatus(manuscript)"
                     >
                       Check Publication Status
                     </button>

                     <button 
                       class="action-btn" 
                       :class="{ 'disabled': !isUnderReview(manuscript.status) && !isDecisionMade(manuscript.status) }"
                       @click="handleReviewers(manuscript)"
                     >
                       Reviewers
                     </button>
                     <button 
                       v-if="isNeedingRevision(manuscript.status)"
                       class="action-btn btn-primary" 
                       @click="handleSubmitRevision(manuscript)"
                     >
                       Submit Revision
                     </button>
                     <!-- Legacy Recommend Reviewers (if needed, otherwise hide or rename) -->
                     <!-- <button class="action-btn" @click="openReviewerModal(manuscript)">Recommend Reviewers</button> -->
                   </div>
                </div>
              </div>
            </div>
          </transition>
      </div>
    </main>

    <FlowCheckPanel ref="flowCheckPanelRef" :manuscripts="userJournals" />

    <!-- Action Modals -->
    <ViewSubmissionModal 
      :visible="showViewSubmissionModal" 
      :manuscript="selectedManuscriptForModal" 
      @close="showViewSubmissionModal = false" 
    />
    
    <HistoryModal 
      :visible="showHistoryModal" 
      :manuscript="selectedManuscriptForModal" 
      @close="showHistoryModal = false" 
    />
    
    <ReviewerStatusModal 
      :visible="showReviewerStatusModal" 
      :manuscript="selectedManuscriptForModal" 
      @close="showReviewerStatusModal = false" 
    />

    <SubmitRevisionModal 
      :visible="showSubmitRevisionModal" 
      :manuscript="selectedManuscriptForModal" 
      @close="showSubmitRevisionModal = false" 
      @submitted="showSubmitRevisionModal = false"
    />

    <!-- Reviewer Management Modal (Legacy/Recommend) -->
    <div v-if="showReviewerModal" class="modal-overlay">
      <div class="modal-box">
        <h3>Recommended Reviewers</h3>
        <p class="modal-subtitle">Manuscript: {{ selectedManuscriptForReviewers?.title }}</p>
        
        <div v-if="currentManuscriptReviewers.length === 0" class="no-data">
          No reviewers recommended for this manuscript.
        </div>

        <ul v-else class="reviewer-list">
          <li v-for="reviewer in currentManuscriptReviewers" :key="reviewer.id" class="reviewer-item">
            <div class="reviewer-info">
              <strong>{{ reviewer.reviewerName }}</strong>
              <span class="affiliation">{{ reviewer.reviewerAffiliation }}</span>
              <span class="status-tag" :class="reviewer.status">{{ reviewer.status }}</span>
            </div>
            <div class="reviewer-actions">
              <button 
                v-if="reviewer.status === 'pending'" 
                class="btn-withdraw" 
                @click="handleWithdrawRecommendation(reviewer)"
              >
                Withdraw
              </button>
            </div>
          </li>
        </ul>

        <div class="modal-footer">
          <button class="btn-close" @click="showReviewerModal = false">Close</button>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="footer">
      <div class="footer-content">
        <p>&copy; 2026 Journal Submission Platform. All rights reserved.</p>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.author-dashboard-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: #fff; /* White background as per screenshot */
  font-family: Arial, sans-serif;
}

.dashboard-content {
  flex: 1;
  width: 100%;
  max-width: 1400px; /* Wider layout */
  margin: 0 auto;
  padding: 2rem 1rem;
}

.dashboard-header-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.dashboard-title {
  font-size: 1.5rem;
  color: #333;
  margin: 0;
}

.btn-flow-check {
  background-color: #0056b3;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.btn-flow-check:hover {
  background-color: #004494;
}

.main-lists {
  width: 100%;
}

.menu-group {
  margin-bottom: 2.5rem;
}

.group-title {
  font-size: 1.2rem;
  font-weight: normal;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.group-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.list-item {
  margin-bottom: 0.5rem;
}

.action-link {
  color: #C93737;
  font-weight: bold;
  text-decoration: none;
  font-size: 0.95rem;
}

.action-link:hover {
  text-decoration: underline;
}

.status-link {
  text-decoration: none;
  font-size: 0.95rem;
  transition: all 0.2s;
  display: inline-block;
  color: #333;
}

.status-link.disabled {
  color: #999;
  cursor: default;
  pointer-events: none; /* Make unclickable */
}

.status-link.clickable {
  color: #0056b3;
  cursor: pointer;
}

.status-link.clickable:hover {
  text-decoration: underline;
}

.status-link.active {
  background-color: #fce4ec; /* Light pink/red for active */
  color: #C93737;
  padding: 2px 5px;
  border-radius: 3px;
  font-weight: bold;
}

/* Manuscript Details Section */
.manuscript-details-section {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 2px solid #C93737;
}

.details-title {
  font-size: 1.2rem;
  color: #333;
  margin-bottom: 1rem;
}

.manuscript-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manuscript-card {
  background: #f9f9f9;
  border: 1px solid #ddd;
  padding: 1rem;
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
  font-size: 0.85rem;
  color: #666;
}

.ms-status-badge {
  font-weight: bold;
  color: #C93737;
}

.ms-title {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 1.1rem;
  font-weight: bold;
}

.ms-meta {
  font-size: 0.85rem;
  color: #555;
  margin-bottom: 1rem;
  display: flex;
  gap: 1rem;
}

.card-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.3rem 0.8rem;
  font-size: 0.85rem;
  background: #eee;
  border: 1px solid #ccc;
  border-radius: 3px;
  cursor: pointer;
}

.action-btn.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #f5f5f5;
  color: #999;
}

.action-btn.btn-primary {
  background: #3498db;
  color: white;
  border: 1px solid #2980b9;
}

.action-btn.btn-primary:hover {
  background: #2980b9;
}

.action-btn:hover:not(.disabled) {
  background: #ddd;
}

/* Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.footer {
  background: #f8f9fa;
  color: #666;
  padding: 1rem;
  text-align: center;
  border-top: 1px solid #eee;
  margin-top: auto;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-subtitle {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.reviewer-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.reviewer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid #eee;
}

.reviewer-info {
  display: flex;
  flex-direction: column;
}

.reviewer-info strong {
  font-size: 1rem;
  color: #333;
}

.affiliation {
  font-size: 0.8rem;
  color: #666;
}

.status-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  margin-top: 4px;
  font-weight: bold;
  text-transform: uppercase;
  width: fit-content;
}

.status-tag.pending { background: #fff3cd; color: #856404; }
.status-tag.accepted { background: #d4edda; color: #155724; }
.status-tag.rejected { background: #f8d7da; color: #721c24; }
.status-tag.invited { background: #d1ecf1; color: #0c5460; }
.status-tag.completed { background: #e2e3e5; color: #383d41; }
.status-tag.declined { background: #343a40; color: #fff; }
.status-tag.contact_failed { background: #e0a800; color: #fff; }
.status-tag.withdrawn { background: #6c757d; color: #fff; }

.btn-withdraw {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-withdraw:hover {
  background: #c82333;
}

.modal-footer {
  margin-top: 1.5rem;
  text-align: right;
}

.btn-close {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-close:hover {
  background: #5a6268;
}
</style>
