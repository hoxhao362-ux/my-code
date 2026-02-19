<script setup>
import { ref, reactive, computed } from 'vue'
import { PLATFORM_NAME, BRAND_RED } from '../../../constants/emailTemplates'
import ActionModal from '../../../components/admin/manuscript/actions/ActionModal.vue'

const props = defineProps({
  manuscriptId: {
    type: String,
    required: true
  }
})

// --- Mock Data ---

// 1. Author Recommended Reviewers
const recommendedReviewers = ref([
  {
    id: 1,
    serialNo: 1,
    name: 'Dr. John Doe',
    email: 'john.doe@example.com',
    affiliation: 'University of Science',
    reason: 'Expert in the field of deep learning and medical imaging. Has published multiple papers on similar topics.',
    submissionTime: '2026-02-10 14:30',
    type: 'External', // Platform, External
    status: 'Pending', // Pending, Approved, Rejected, Invited
    rejectionReason: ''
  },
  {
    id: 2,
    serialNo: 2,
    name: 'Dr. Alice Smith',
    email: 'alice.smith@example.com',
    affiliation: 'Institute of Technology',
    reason: 'Previous collaborator on related projects, familiar with the methodology.',
    submissionTime: '2026-02-11 09:15',
    type: 'Platform',
    status: 'Approved',
    rejectionReason: ''
  }
])

const recommendedStats = computed(() => {
  const total = recommendedReviewers.value.length
  const pending = recommendedReviewers.value.filter(r => r.status === 'Pending').length
  const approved = recommendedReviewers.value.filter(r => r.status === 'Approved' || r.status === 'Invited' || r.status === 'Invitation Sent').length
  const rejected = recommendedReviewers.value.filter(r => r.status === 'Rejected').length
  return `Total Recommended: ${total} | Pending: ${pending} | Approved: ${approved} | Rejected: ${rejected}`
})

const isAllRecommendedProcessed = computed(() => {
  return recommendedReviewers.value.length > 0 && !recommendedReviewers.value.some(r => r.status === 'Pending')
})

// 2. Author Avoidance Requests
const avoidanceRequests = ref([
  {
    id: 1,
    serialNo: 1,
    name: 'Dr. Robert Evil',
    affiliation: 'Competitor Labs',
    reason: 'Conflict of interest: Currently working on a directly competing project.',
    submissionTime: '2026-02-10 15:00',
    status: 'Pending', // Pending, Approved, Rejected
    rejectionReason: ''
  }
])

const avoidanceStats = computed(() => {
  const total = avoidanceRequests.value.length
  const pending = avoidanceRequests.value.filter(r => r.status === 'Pending').length
  const approved = avoidanceRequests.value.filter(r => r.status === 'Approved').length
  const rejected = avoidanceRequests.value.filter(r => r.status === 'Rejected').length
  return `Total Requests: ${total} | Pending: ${pending} | Approved: ${approved} | Rejected: ${rejected}`
})

// 3. Conflict of Interest Check
const checkStatus = ref('Completed') // Completed, Pending
const conflictResults = ref({
  recommended: [
    {
      reviewerId: 1,
      name: 'Dr. John Doe',
      affiliation: 'University of Science',
      sameAffiliation: false,
      coAuthored: false,
      commonFund: false,
      sameDomain: false,
      linkedAvoidance: false,
      isConflict: false
    },
    {
      reviewerId: 2,
      name: 'Dr. Alice Smith',
      affiliation: 'Institute of Technology',
      sameAffiliation: true, // Conflict!
      coAuthored: true, // Conflict!
      commonFund: false,
      sameDomain: false,
      linkedAvoidance: false,
      isConflict: true // Marked by system or editor
    }
  ],
  excluded: [
    {
      requestId: 1,
      name: 'Dr. Robert Evil',
      affiliation: 'Competitor Labs',
      sameAffiliation: false,
      coAuthored: false,
      commonFund: true,
      sameDomain: false,
      linkedAvoidance: true,
      avoidanceReason: 'Conflict of interest: Currently working on a directly competing project.'
    }
  ]
})

// History Logs
const historyLogs = ref([
  { time: '2026-02-10 14:00', editor: 'System', content: 'Initial conflict check completed.', type: 'conflict' }
])

// Filtered Logs
const recommendedLogs = computed(() => historyLogs.value.filter(l => l.type === 'recommended'))
const avoidanceLogs = computed(() => historyLogs.value.filter(l => l.type === 'avoidance'))
const conflictLogs = computed(() => historyLogs.value.filter(l => l.type === 'conflict'))

// --- Modal State ---
const showActionModal = ref(false)
const showExcludedModal = ref(false)
const currentActionType = ref('')
const currentTarget = ref(null)

// --- Methods: Recommended Reviewers ---

const approveRecommendation = (reviewer) => {
  if (confirm('Are you sure to approve this recommended reviewer?')) {
    reviewer.status = 'Approved'
    addLog(`Approved recommended reviewer ${reviewer.name}`, 'recommended')
  }
}

const rejectRecommendation = (reviewer) => {
  const reason = prompt('Please enter the reason for rejection (e.g., conflict of interest, irrelevant expertise):')
  if (reason) {
    if (reason.trim().length === 0) {
      alert('Reason cannot be empty.')
      return
    }
    reviewer.status = 'Rejected'
    reviewer.rejectionReason = reason
    addLog(`Rejected recommended reviewer ${reviewer.name}. Reason: ${reason}`, 'recommended')
  }
}

const openInviteModal = (reviewer) => {
  if (reviewer.status !== 'Approved' && reviewer.status !== 'Invitation Sent' && reviewer.status !== 'Invited') {
    return
  }
  currentTarget.value = reviewer
  currentActionType.value = 'invite_reviewer'
  showActionModal.value = true
}

const handleInviteSubmit = (payload) => {
  if (currentTarget.value) {
    currentTarget.value.status = 'Invitation Sent'
    currentTarget.value.invitationTime = new Date().toLocaleString()
    addLog(`Sent invitation to recommended reviewer ${currentTarget.value.name}`, 'recommended')
    alert('Invitation sent successfully!')
  }
}

const openNotifyWriterModal = () => {
  currentActionType.value = 'notify_writer_recommendation'
  showActionModal.value = true
}

const handleNotifyWriterSubmit = (payload) => {
  addLog('Notified writer about reviewer recommendation results', 'recommended')
  alert('Notification sent successfully!')
}

const handleActionSubmit = (payload) => {
  if (payload.type === 'invite_reviewer') {
    handleInviteSubmit(payload)
  } else if (payload.type === 'notify_writer_recommendation') {
    handleNotifyWriterSubmit(payload)
  }
}

const cancelInvite = (reviewer) => {
  if (confirm('Are you sure to cancel the invitation? The status will revert to Approved.')) {
    reviewer.status = 'Approved'
    addLog(`Canceled invitation for ${reviewer.name}`, 'recommended')
  }
}

const viewRejectionReason = (reason) => {
  alert(`Rejection Reason:\n${reason}`)
}

const viewReasonPopup = (reason) => {
  alert(`Full Reason:\n${reason}`)
}

// --- Methods: Avoidance Requests ---

const approveAvoidance = (request) => {
  if (confirm('Are you sure to approve this avoidance request? The reviewer will be excluded from the assignment process.')) {
    request.status = 'Approved'
    // Add to excluded list in conflict check (Mock)
    conflictResults.value.excluded.push({
      requestId: request.id,
      name: request.name,
      affiliation: request.affiliation,
      sameAffiliation: false,
      coAuthored: false,
      commonFund: false,
      sameDomain: false,
      linkedAvoidance: true,
      avoidanceReason: request.reason
    })
    addLog(`Approved avoidance request for ${request.name}`, 'avoidance')
  }
}

const rejectAvoidance = (request) => {
  const reason = prompt('Please enter the reason for rejecting the avoidance request (e.g., no valid conflict of interest):')
  if (reason) {
    if (reason.trim().length === 0) {
      alert('Reason cannot be empty.')
      return
    }
    request.status = 'Rejected'
    request.rejectionReason = reason
    addLog(`Rejected avoidance request for ${request.name}. Reason: ${reason}`, 'avoidance')
  }
}

const viewAvoidanceDetails = (request) => {
  alert(`Avoidance Request Details:\nReviewer: ${request.name}\nReason: ${request.reason}\nStatus: ${request.status}`)
}

const reReviewAvoidance = (request) => {
  if (confirm('Revert status to Pending for re-review?')) {
    request.status = 'Pending'
    request.rejectionReason = ''
    addLog(`Reverted avoidance request for ${request.name} to Pending`, 'avoidance')
  }
}

// --- Methods: Conflict Check ---

const markConflict = (item, isConflict) => {
  item.isConflict = isConflict
  addLog(`Marked ${item.name} as ${isConflict ? 'Conflict' : 'Safe'}`, 'conflict')
}

const reCheckSingle = (item) => {
  // Mock re-check
  alert(`Re-checking conflict status for ${item.name}...`)
  setTimeout(() => {
    alert('Check completed. No changes found.')
  }, 1000)
}

const reCheckAll = () => {
  checkStatus.value = 'Pending'
  setTimeout(() => {
    checkStatus.value = 'Completed'
    addLog('Re-ran full conflict of interest check.', 'conflict')
  }, 1500)
}

const downloadReport = () => {
  alert('Report downloaded successfully')
  addLog('Downloaded conflict check report', 'conflict')
}

// --- Helper ---

const addLog = (content, type = 'general') => {
  const now = new Date()
  const timeStr = `${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')} ${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  historyLogs.value.unshift({
    time: timeStr,
    editor: 'Editor Li', // Mock current user as Editor Li
    content: content,
    type: type
  })
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text).then(() => {
    alert('Copied to clipboard')
  })
}

</script>

<template>
  <div class="reviewer-management-module">
    
    <!-- 1. Author Recommended Reviewers -->
    <section class="module-section">
      <div class="module-header">
        <h2 class="module-title">Writer Recommended Reviewers</h2>
        <div class="header-actions">
           <button 
             v-if="isAllRecommendedProcessed" 
             class="btn-action btn-red" 
             @click="openNotifyWriterModal"
             title="Notify Writer of Results"
           >
             Notify Writer of Results
           </button>
        </div>
      </div>
      <div class="module-stats">{{ recommendedStats }}</div>
      <p class="module-desc">Review and manage reviewers recommended by the writers. Approved reviewers can be invited to participate in the peer review process.</p>
      
      <div class="table-container">
        <table class="lancet-table">
          <thead>
            <tr>
              <th width="60" class="text-center">Serial No.</th>
              <th>Reviewer Name</th>
              <th>Type</th>
              <th>Email Address</th>
              <th>Affiliation</th>
              <th>Recommendation Reason</th>
              <th class="text-center">Submission Time</th>
              <th>Review Status</th>
              <th>Editorial Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="r in recommendedReviewers" :key="r.id">
              <td class="text-center">{{ r.serialNo }}</td>
              <td :title="r.name">{{ r.name }}</td>
              <td>
                <span class="status-badge" :class="r.type === 'Platform' ? 'platform-tag' : 'external-tag'">{{ r.type }}</span>
              </td>
              <td>
                {{ r.email }}
                <span class="copy-icon" @click="copyToClipboard(r.email)" title="Copy Email">📋</span>
              </td>
              <td>{{ r.affiliation || 'N/A' }}</td>
              <td>
                <span class="reason-text" :title="r.reason" @click="viewReasonPopup(r.reason)">
                  {{ r.reason.length > 50 ? r.reason.substring(0, 50) + '...' : r.reason }}
                </span>
              </td>
              <td class="text-center">{{ r.submissionTime }}</td>
              <td>
                <span class="status-badge" :class="r.status.toLowerCase().replace(/\s+/g, '-')">{{ r.status }}</span>
              </td>
              <td>
                <!-- Pending Actions -->
                <div v-if="r.status === 'Pending'" class="action-buttons">
                  <button class="btn-action btn-red" @click="approveRecommendation(r)">Approve</button>
                  <button class="btn-action btn-gray" @click="rejectRecommendation(r)">Reject</button>
                </div>
                <!-- Approved Actions -->
                <div v-else-if="r.status === 'Approved'" class="action-buttons">
                  <button class="btn-action btn-red" @click="openInviteModal(r)">Send Invite</button>
                </div>
                <!-- Rejected Actions -->
                <div v-else-if="r.status === 'Rejected'" class="action-buttons">
                  <button class="btn-text" @click="viewRejectionReason(r.rejectionReason)">View Reason</button>
                </div>
                <!-- Invited Actions -->
                <div v-else-if="r.status === 'Invited' || r.status === 'Invitation Sent'" class="action-buttons">
                  <button class="btn-action btn-red" @click="openInviteModal(r)">Resend Invite</button>
                  <button class="btn-action btn-gray" @click="cancelInvite(r)">Cancel Invite</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- History -->
      <div class="history-section">
        <h3 class="history-title">Review History</h3>
        <div class="history-list">
          <div v-for="(log, idx) in recommendedLogs" :key="idx" class="history-item">
            {{ log.time }} | {{ log.editor }} | {{ log.content }}
          </div>
          <div v-if="recommendedLogs.length === 0" class="history-item">No records found.</div>
        </div>
      </div>
    </section>

    <div class="divider"></div>

    <!-- 2. Author Avoidance Requests -->
    <section class="module-section">
      <div class="module-header">
        <h2 class="module-title">Writer Avoidance Requests</h2>
        <div class="module-stats">{{ avoidanceStats }}</div>
      </div>
      <p class="module-desc">Review and evaluate requests from writers to avoid specific reviewers. Approved requests will exclude reviewers from the assignment process.</p>
      
      <div class="table-container">
        <table class="lancet-table">
          <thead>
            <tr>
              <th width="60" class="text-center">Serial No.</th>
              <th>Reviewer Name</th>
              <th>Affiliation</th>
              <th>Avoidance Reason</th>
              <th class="text-center">Submission Time</th>
              <th>Review Status</th>
              <th>Editorial Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in avoidanceRequests" :key="req.id">
              <td class="text-center">{{ req.serialNo }}</td>
              <td>{{ req.name }}</td>
              <td>{{ req.affiliation || 'N/A' }}</td>
              <td>
                <div class="full-reason">{{ req.reason }}</div>
              </td>
              <td class="text-center">{{ req.submissionTime }}</td>
              <td>
                <span class="status-badge" :class="req.status.toLowerCase()">{{ req.status }}</span>
              </td>
              <td>
                <!-- Pending -->
                <div v-if="req.status === 'Pending'" class="action-buttons">
                  <button class="btn-action btn-red" @click="approveAvoidance(req)">Adopt (Shield)</button>
                  <button class="btn-action btn-gray" @click="rejectAvoidance(req)">Reject</button>
                </div>
                <!-- Approved -->
                <div v-else-if="req.status === 'Approved'" class="action-buttons">
                  <button class="btn-text" @click="viewAvoidanceDetails(req)">View Details</button>
                  <span class="check-mark">Shielded ✅</span>
                </div>
                <!-- Rejected -->
                <div v-else-if="req.status === 'Rejected'" class="action-buttons">
                  <button class="btn-text" @click="viewRejectionReason(req.rejectionReason)">View Reason</button>
                  <button class="btn-action btn-red" @click="reReviewAvoidance(req)">Re-review</button>
                  <span class="cross-mark">❌</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Excluded List Link -->
      <div class="excluded-link">
        Excluded Reviewers: {{ conflictResults.excluded.length }} 
        <button class="btn-text" @click="showExcludedModal = true">View List</button>
      </div>
      
      <!-- History -->
      <div class="history-section">
        <h3 class="history-title">Review History</h3>
        <div class="history-list">
          <div v-for="(log, idx) in avoidanceLogs" :key="idx" class="history-item">
            {{ log.time }} | {{ log.editor }} | {{ log.content }}
          </div>
          <div v-if="avoidanceLogs.length === 0" class="history-item">No records found.</div>
        </div>
      </div>
    </section>

    <div class="divider"></div>

    <!-- 3. Conflict of Interest Check -->
    <section class="module-section">
      <div class="module-header">
        <h2 class="module-title">Conflict of Interest Check</h2>
        <div class="module-status">
          Check Status: {{ checkStatus }}
          <button class="btn-action btn-gray btn-sm" @click="reCheckAll" style="margin-left: 10px;">One-click Re-check</button>
        </div>
      </div>
      <p class="module-desc">Automatically check for potential conflicts of interest between writers and reviewers. Editors can manually confirm and mark conflict status.</p>
      
      <div class="coi-container">
        
        <!-- Sub 1: Recommended -->
        <div class="coi-block">
          <h3 class="coi-subtitle">Writer vs Recommended Reviewers</h3>
          <div v-for="item in conflictResults.recommended" :key="item.reviewerId" class="coi-card">
            <div class="coi-card-header">
              Reviewer: {{ item.name }} ({{ item.affiliation }})
            </div>
            <ul class="coi-list">
              <li>
                • Same Affiliation: <span :class="item.sameAffiliation ? 'text-red' : 'text-green'">{{ item.sameAffiliation ? 'Yes' : 'No' }}</span>
              </li>
              <li>
                • Co-authored Papers (Past 5 Years): <span :class="item.coAuthored ? 'text-red' : 'text-green'">{{ item.coAuthored ? 'Yes' : 'No' }}</span>
              </li>
              <li>
                • Common Fund Projects: <span :class="item.commonFund ? 'text-red' : 'text-green'">{{ item.commonFund ? 'Yes' : 'No' }}</span>
              </li>
              <li>
                • Same Email Domain: <span :class="item.sameDomain ? 'text-red' : 'text-green'">{{ item.sameDomain ? 'Yes' : 'No' }}</span>
              </li>
              <li>
                • Linked to Avoidance Request: <span :class="item.linkedAvoidance ? 'text-blue' : 'text-green'">{{ item.linkedAvoidance ? 'Yes' : 'No' }}</span>
              </li>
            </ul>
            <div class="coi-actions">
              <button v-if="item.isConflict || item.sameAffiliation || item.coAuthored" class="btn-action btn-green" @click="markConflict(item, false)">Mark as Safe</button>
              <button v-else class="btn-action btn-red" @click="markConflict(item, true)">Mark as Conflict</button>
              <button class="btn-action btn-gray" @click="reCheckSingle(item)">Re-check</button>
            </div>
          </div>
        </div>

        <!-- Sub 2: Excluded -->
        <div class="coi-block">
          <h3 class="coi-subtitle">Writer vs Excluded Reviewers</h3>
          <div v-for="item in conflictResults.excluded" :key="item.requestId" class="coi-card">
             <div class="coi-card-header">
              Excluded Reviewer: {{ item.name }} ({{ item.affiliation }})
            </div>
            <ul class="coi-list">
              <li>
                 • Avoidance Reason: <span class="text-gray">{{ item.avoidanceReason }}</span>
              </li>
              <!-- Reuse other checks -->
              <li>• Same Affiliation: <span :class="item.sameAffiliation ? 'text-red' : 'text-green'">{{ item.sameAffiliation ? 'Yes' : 'No' }}</span></li>
            </ul>
             <div class="coi-actions">
               <button class="btn-text" @click="viewAvoidanceDetails(item)">View Details</button>
             </div>
          </div>
        </div>

      </div>

      <div class="report-section">
        <h3 class="history-title">Conflict Check Report</h3>
        <div class="report-actions">
          <button class="btn-action btn-red" @click="downloadReport">Download Report</button>
        </div>
        <p class="report-desc">The check report will be retained in the manuscript file for academic traceability.</p>
      </div>

    </section>

    <!-- Action Modal Reuse -->
    <ActionModal
      v-if="showActionModal"
      :visible="showActionModal"
      :actionType="currentActionType"
      :reviewer="currentTarget"
      :reviewers="recommendedReviewers"
      :manuscript="{ id: manuscriptId, title: 'Manuscript Title Mock' }" 
      @close="showActionModal = false"
      @submit="handleActionSubmit"
    />
    
    <!-- Excluded Reviewers Modal (Simple Mock) -->
    <div v-if="showExcludedModal" class="modal-overlay" @click.self="showExcludedModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>Excluded Reviewers List</h3>
          <button class="btn-close" @click="showExcludedModal = false">×</button>
        </div>
        <div class="modal-body">
          <table class="lancet-table">
            <thead>
              <tr>
                <th>Reviewer Name</th>
                <th>Affiliation</th>
                <th>Avoidance Reason</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ex, idx) in conflictResults.excluded" :key="idx">
                <td>{{ ex.name }}</td>
                <td>{{ ex.affiliation }}</td>
                <td>{{ ex.avoidanceReason }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.reviewer-management-module {
  padding: 1rem 0;
}
/* ... existing styles ... */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 600px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.modal-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 { margin: 0; font-size: 1.1rem; }

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.modal-body {
  padding: 1rem;
}

.btn-sm {
  font-size: 12px;
  padding: 2px 8px;
}

.module-section {
  margin-bottom: 2rem;
}

.divider {
  height: 1px;
  background-color: #eee;
  margin: 2rem 0;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.module-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.module-desc {
  font-size: 12px;
  color: #999;
  margin: 0 0 1rem 0;
}

.module-stats, .module-status {
  font-size: 14px;
  color: #333;
}

/* Table Styles */
.table-container {
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.lancet-table {
  width: 100%;
  border-collapse: collapse;
}

.lancet-table th {
  background-color: #fff;
  color: #333;
  font-weight: bold;
  font-size: 14px;
  padding: 12px;
  border-bottom: 2px solid #333;
  text-align: left;
}

.lancet-table td {
  padding: 12px;
  border-bottom: 1px solid #eee;
  color: #333;
  font-size: 14px;
  vertical-align: middle;
}

.lancet-table tr:hover {
  background-color: #f5f5f5;
}

.text-center { text-align: center; }

.copy-icon { cursor: pointer; margin-left: 5px; font-size: 12px; }
.reason-text { cursor: pointer; color: #666; border-bottom: 1px dashed #999; }
.full-reason { white-space: pre-wrap; color: #666; }

/* Status Badges */
.status-badge {
  font-weight: bold;
}
.status-badge.pending { color: #4A90E2; }
.status-badge.approved { color: #28A745; }
.status-badge.rejected { color: #C93737; }
.status-badge.invited, .status-badge.invitation-sent { color: #333; }

.platform-tag { color: #28A745; background: #e8f5e9; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.external-tag { color: #4A90E2; background: #e3f2fd; padding: 2px 6px; border-radius: 4px; font-size: 12px; }

.header-actions {
  display: flex;
  gap: 10px;
}

/* Buttons */
.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-action {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 14px;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-red { background-color: #C93737; color: white; }
.btn-red:hover { background-color: #B02E2E; }

.btn-gray { background-color: #E0E0E0; color: #333; }
.btn-gray:hover { background-color: #D0D0D0; }

.btn-green { background-color: #28A745; color: white; }
.btn-green:hover { background-color: #218838; }

.btn-text {
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
}
.btn-text:hover { text-decoration: underline; color: #666; }

.check-mark { color: #28A745; margin-left: 5px; }
.cross-mark { color: #C93737; margin-left: 5px; }

/* History */
.history-section { margin-top: 1rem; }
.history-title { font-size: 16px; font-weight: bold; color: #333; margin-bottom: 0.5rem; }
.history-list { max-height: 100px; overflow-y: auto; }
.history-item { font-size: 12px; color: #666; margin-bottom: 4px; }

/* COI Styles */
.coi-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 1rem;
}

.coi-block {
  /* background: #f9f9f9; padding: 1rem; border-radius: 8px; */
}

.coi-subtitle {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 12px;
}

.coi-card {
  background: white;
  border: 1px solid #eee;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.coi-card-header {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.coi-list {
  list-style: none;
  padding: 0;
  margin: 0 0 12px 0;
}

.coi-list li {
  font-size: 14px;
  margin-bottom: 8px;
  color: #333;
}

.text-red { color: #C93737; font-weight: bold; }
.text-green { color: #28A745; font-weight: bold; }
.text-blue { color: #4A90E2; font-weight: bold; }
.text-gray { color: #666; }

.coi-actions {
  display: flex;
  gap: 8px;
}

.report-section {
  margin-top: 1rem;
}
.report-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 5px;
}
.report-desc {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.excluded-link {
  text-align: center;
  margin: 1rem 0;
  font-size: 14px;
  color: #333;
}

</style>
