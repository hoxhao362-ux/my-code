<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 筛选条件
const selectedStatus = ref('all')
const selectedStage = ref('all')
const searchKeyword = ref('')

// 状态选项
const statusOptions = ['all', 'pending', 'accepted', 'rejected']
const statusLabels = {
  all: 'All Status',
  pending: 'Pending Review',
  accepted: 'Accepted (Excluded)',
  rejected: 'Rejected (Allowed)'
}

// Stage Options
const stageOptions = ['all', 'initial', 'revision']
const stageLabels = {
  all: 'All Stages',
  initial: 'Initial Submission',
  revision: 'Revision'
}

// Use Store Data
const opposedReviewers = computed(() => userStore.opposedReviewers)

// 筛选后的数据
const filteredOpposed = computed(() => {
  let result = opposedReviewers.value
  
  // 按状态筛选
  if (selectedStatus.value !== 'all') {
    result = result.filter(r => r.status === selectedStatus.value)
  }

  // Filter by Stage
  if (selectedStage.value !== 'all') {
    result = result.filter(r => (r.stage || 'initial') === selectedStage.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r => 
      r.manuscriptTitle.toLowerCase().includes(keyword) ||
      r.opposedReviewerName.toLowerCase().includes(keyword) ||
      r.opposedReviewerAffiliation.toLowerCase().includes(keyword) ||
      r.opposedReason.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

// Helper: Add history record to journal
const addToJournalHistory = (manuscriptId, action, reviewerName, comment) => {
  const journal = userStore.journals.find(j => String(j.id) === String(manuscriptId))
  if (!journal) return false

  const statusText = action === 'accepted' ? 'Accepted (Excluded)' : 'Rejected (Allowed)'
  const actionText = action === 'accepted' ? 'accepted opposition request' : 'rejected opposition request'

  const newRecord = {
    stage: 'Reviewer Opposition',
    status: statusText,
    reviewer: user.value?.username || 'admin',
    date: new Date().toISOString().split('T')[0],
    comment: `Editor ${actionText} for reviewer: ${reviewerName}. Note: ${comment || 'N/A'}`,
    type: 'Opposed Reviewer'
  }

  const updatedJournal = {
    ...journal,
    reviewHistory: [...(journal.reviewHistory || []), newRecord]
  }

  return userStore.updateJournal(updatedJournal)
}

// 批量操作
const selectedIds = ref([])
const toggleSelectAll = () => {
  if (selectedIds.value.length === filteredOpposed.value.length) {
    selectedIds.value = []
  } else {
    selectedIds.value = filteredOpposed.value.map(r => r.id)
  }
}

const handleBulkAccept = () => {
  if (selectedIds.value.length === 0) {
    alert('Please select at least one request to accept.')
    return
  }
  
  selectedIds.value.forEach(id => {
    const item = opposedReviewers.value.find(r => r.id === id)
    if (item) {
      const updated = { ...item, status: 'accepted', handledAt: new Date().toISOString(), handledBy: user.value?.username || 'admin' }
      userStore.updateOpposedReviewer(updated)
      
      // Add to history
      addToJournalHistory(item.manuscriptId, 'accepted', item.opposedReviewerName, 'Bulk acceptance')
    }
  })
  
  selectedIds.value = []
  alert('Selected requests have been accepted (Reviewers excluded) and recorded in manuscript history.')
}

const handleBulkReject = () => {
  if (selectedIds.value.length === 0) {
    alert('Please select at least one request to reject.')
    return
  }
  
  selectedIds.value.forEach(id => {
    const item = opposedReviewers.value.find(r => r.id === id)
    if (item) {
      const updated = { ...item, status: 'rejected', handledAt: new Date().toISOString(), handledBy: user.value?.username || 'admin' }
      userStore.updateOpposedReviewer(updated)
      
      // Add to history
      addToJournalHistory(item.manuscriptId, 'rejected', item.opposedReviewerName, 'Bulk rejection')
    }
  })
  
  selectedIds.value = []
  alert('Selected requests have been rejected (Reviewers allowed) and recorded in manuscript history.')
}

// 详情模态框
const showDetailModal = ref(false)
const currentItem = ref(null)
const handleComment = ref('')

// Reason Validation State
const reasonChecks = ref({
  isProfessional: false,
  hasConflict: false,
  isSpecific: false
})

const openDetailModal = (item) => {
  currentItem.value = { ...item }
  handleComment.value = ''
  
  // Reset checks
  reasonChecks.value = {
    isProfessional: false,
    hasConflict: false,
    isSpecific: false
  }
  
  showDetailModal.value = true
}

const handleAccept = () => {
  // Validate Checks
  if (!reasonChecks.value.isProfessional || !reasonChecks.value.hasConflict) {
    alert("You must verify that the reason is Professional and states a Clear Conflict before accepting.")
    return
  }

  if (currentItem.value) {
    const updated = { ...currentItem.value, status: 'accepted', handledAt: new Date().toISOString(), handledBy: user.value?.username || 'admin' }
    userStore.updateOpposedReviewer(updated)
    
    // Add to history
    addToJournalHistory(currentItem.value.manuscriptId, 'accepted', currentItem.value.opposedReviewerName, handleComment.value)

    showDetailModal.value = false
    alert('Request accepted. The reviewer has been excluded and recorded in manuscript history.')
  }
}

const handleReject = () => {
  if (currentItem.value) {
    const updated = { ...currentItem.value, status: 'rejected', handledAt: new Date().toISOString(), handledBy: user.value?.username || 'admin' }
    userStore.updateOpposedReviewer(updated)
    
    // Add to history
    addToJournalHistory(currentItem.value.manuscriptId, 'rejected', currentItem.value.opposedReviewerName, handleComment.value)

    showDetailModal.value = false
    alert('Request rejected. The reviewer is allowed to review and recorded in manuscript history.')
  }
}

// 状态标签样式
const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'accepted': return 'status-accepted'
    case 'rejected': return 'status-rejected'
    default: return ''
  }
}

// 状态显示文本
const getStatusText = (status) => {
  switch (status) {
    case 'pending': return 'Pending'
    case 'accepted': return 'Accepted (Excluded)'
    case 'rejected': return 'Rejected (Allowed)'
    default: return status
  }
}
</script>

<template>
  <div class="lancet-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user" 
      current-page="audit-opposed-reviewers" 
      :toggle-directory="()=>{}" 
      :logout="userStore.logout" 
    />

    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <h1 class="main-title">Opposed Reviewers Management</h1>
        <p class="warning-text">Review and manage reviewers opposed by writers for {{ PLATFORM_NAME }}. Evaluate the reasons carefully.</p>
        
        <div class="filter-bar">
          <select v-model="selectedStatus">
            <option v-for="status in statusOptions" :key="status" :value="status">
              {{ statusLabels[status] }}
            </option>
          </select>
          <select v-model="selectedStage">
            <option v-for="stage in stageOptions" :key="stage" :value="stage">
              {{ stageLabels[stage] }}
            </option>
          </select>
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="Search by manuscript, reviewer name, or reason..." 
            class="search-input"
          />
        </div>
      </div>

      <!-- Bulk Actions -->
      <div class="bulk-actions">
        <div class="select-all">
          <input 
            type="checkbox" 
            id="selectAll" 
            @change="toggleSelectAll"
            :checked="selectedIds.length === filteredOpposed.length && filteredOpposed.length > 0"
          />
          <label for="selectAll">Select All</label>
        </div>
        <button class="btn btn-primary" @click="handleBulkAccept" :disabled="selectedIds.length === 0">
          Bulk Accept (Exclude)
        </button>
        <button class="btn btn-red" @click="handleBulkReject" :disabled="selectedIds.length === 0">
          Bulk Reject (Allow)
        </button>
      </div>

      <!-- Opposed Reviewers List -->
      <table class="lancet-table">
        <thead>
          <tr>
            <th style="width: 50px;"></th>
            <th>Manuscript Title</th>
            <th>Stage</th>
            <th>Opposed Reviewer</th>
            <th>Category</th>
            <th>Reason Summary</th>
            <th>Status</th>
            <th>Requested At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredOpposed" :key="item.id" class="hover-row">
            <td>
              <input 
                type="checkbox" 
                :value="item.id" 
                v-model="selectedIds"
              />
            </td>
            <td class="bold-text">{{ item.manuscriptTitle }}</td>
            <td>
              <span class="stage-badge" :class="item.stage === 'revision' ? 'stage-revision' : 'stage-initial'">
                {{ item.stage === 'revision' ? 'Revision' : 'Initial' }}
              </span>
            </td>
            <td>
              <div>{{ item.opposedReviewerName }}</div>
              <div class="affiliation">{{ item.opposedReviewerAffiliation }}</div>
            </td>
            <td>
              <span class="category-badge">{{ item.reasonType || 'General' }}</span>
            </td>
            <td class="reason-cell" :title="item.opposedReason">
              {{ item.opposedReason.length > 50 ? item.opposedReason.substring(0, 50) + '...' : item.opposedReason }}
            </td>
            <td>
              <span class="status-badge" :class="getStatusClass(item.status)">
                {{ getStatusText(item.status) }}
              </span>
            </td>
            <td>{{ new Date(item.requestedAt).toLocaleDateString() }}</td>
            <td class="actions">
              <button class="btn btn-sm btn-primary" @click="openDetailModal(item)">
                Review
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- No Results -->
      <div v-if="filteredOpposed.length === 0" class="no-data">
        No opposed reviewer requests found matching the current filters.
      </div>

    </main>

    <!-- Detail Modal -->
    <div v-if="showDetailModal" class="modal-overlay">
      <div class="modal-box large">
        <h3>Opposed Reviewer Request Details</h3>
        <div class="modal-content">
          <div class="section">
            <h4>Manuscript Information</h4>
            <p><strong>Title:</strong> {{ currentItem?.manuscriptTitle }}</p>
            <p><strong>Writer:</strong> {{ currentItem?.writerName }}</p>
          </div>
          
          <div class="section">
            <h4>Opposed Reviewer Information</h4>
            <p><strong>Name:</strong> {{ currentItem?.opposedReviewerName }}</p>
            <p><strong>Affiliation:</strong> {{ currentItem?.opposedReviewerAffiliation }}</p>
          </div>
          
          <div class="section">
            <h4>Opposition Details</h4>
            <p><strong>Category:</strong> {{ currentItem?.reasonType || 'Not Specified' }}</p>
            <p class="full-reason"><strong>Reason:</strong> {{ currentItem?.opposedReason }}</p>
            
            <!-- Reason Validation Checklist -->
            <div class="validation-checklist">
               <p class="checklist-title">Reason Validity Check:</p>
               <label class="checkbox-label">
                 <input type="checkbox" v-model="reasonChecks.isProfessional">
                 Reason is professional and academic (not personal)
               </label>
               <label class="checkbox-label">
                 <input type="checkbox" v-model="reasonChecks.hasConflict">
                 Clear conflict of interest stated
               </label>
               <label class="checkbox-label">
                 <input type="checkbox" v-model="reasonChecks.isSpecific">
                 Reason is specific and verifiable
               </label>
            </div>

            <p><strong>Requested At:</strong> {{ currentItem?.requestedAt ? new Date(currentItem.requestedAt).toLocaleString() : 'N/A' }}</p>
            <p><strong>Handled At:</strong> {{ currentItem?.handledAt ? new Date(currentItem.handledAt).toLocaleString() : 'N/A' }}</p>
            <p><strong>Handled By:</strong> {{ currentItem?.handledBy || 'N/A' }}</p>
          </div>
          
          <div class="section">
            <h4>Handling Comments</h4>
            <textarea 
              v-model="handleComment" 
              rows="3" 
              placeholder="Enter internal comments regarding this decision (optional)..."
              class="comment-input"
            ></textarea>
          </div>
        </div>
        
        <div class="modal-actions">
          <button class="btn btn-grey" @click="showDetailModal = false">Cancel</button>
          <button class="btn btn-red" @click="handleReject">Reject (Allow Review)</button>
          <button class="btn btn-primary" @click="handleAccept">Accept (Exclude Reviewer)</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.lancet-container {
  font-family: 'Times New Roman', Times, serif;
  background-color: #FFFFFF;
  min-height: 100vh;
  color: #333333;
}

.content {
  padding: 40px;
  max-width: 1200px;
  margin: 0 auto;
}

/* Header */
.page-header {
  text-align: center;
  margin-bottom: 40px;
}

.main-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  text-transform: uppercase;
}

.warning-text {
  font-size: 12px;
  color: #D1202F;
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  justify-content: center;
  gap: 20px;
  flex-wrap: wrap;
  margin-top: 20px;
}

.filter-bar select,
.search-input {
  padding: 6px 12px;
  border: 1px solid #CCC;
  font-family: 'Times New Roman';
  min-width: 150px;
  border-radius: 4px;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

/* Bulk Actions */
.bulk-actions {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.select-all {
  display: flex;
  align-items: center;
  gap: 5px;
}

/* Table */
.lancet-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  margin-bottom: 30px;
}

.lancet-table th {
  text-align: left;
  padding: 12px 10px;
  border-bottom: 2px solid #CCC;
  font-weight: bold;
  color: #555;
  background: #f8f9fa;
}

.lancet-table td {
  padding: 15px 10px;
  border-bottom: 1px solid #EEE;
  vertical-align: top;
}

.hover-row:hover {
  background: #f8f9fa;
}

.bold-text {
  font-weight: bold;
}

.affiliation {
  font-size: 12px;
  color: #777;
  margin-top: 3px;
}

.reason-cell {
  max-width: 300px;
  color: #555;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
  white-space: nowrap;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-accepted {
  background: #d1ecf1; /* Light Blue for Excluded */
  color: #0c5460;
}

.status-rejected {
  background: #e2e3e5; /* Grey for Allowed (Rejected request) */
  color: #383d41;
}

.stage-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  text-transform: uppercase;
}

.stage-initial {
  background-color: #e2e8f0;
  color: #4a5568;
}

.stage-revision {
  background-color: #ebf8ff;
  color: #3182ce;
  border: 1px solid #bee3f8;
}

.category-badge {
  display: inline-block;
  padding: 2px 8px;
  background-color: #f3f3f3;
  color: #333;
  border-radius: 4px;
  font-size: 11px;
  border: 1px solid #ccc;
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 8px;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 12px;
  transition: background-color 0.3s;
}

.btn-primary {
  background: #1a365d;
  color: white;
}

.btn-primary:hover {
  background: #2c5282;
}

.btn-primary:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.btn-red {
  background: #D1202F;
  color: white;
}

.btn-red:hover {
  background: #b01b27;
}

.btn-grey {
  background: #e2e6ea;
  color: #333;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 11px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box.large {
  width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-content {
  margin-bottom: 20px;
}

.section {
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.section:last-child {
  border-bottom: none;
}

.section h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #1a365d;
  font-size: 14px;
  text-transform: uppercase;
  border-left: 3px solid #D1202F;
  padding-left: 8px;
}

.section p {
  margin: 5px 0;
  font-size: 14px;
  line-height: 1.5;
}

.full-reason {
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  font-style: italic;
  color: #555;
}

.comment-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #CCC;
  font-family: 'Times New Roman';
  resize: vertical;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #777;
  font-style: italic;
  background: #f8f9fa;
  border-radius: 8px;
}
/* Validation Checklist */
.validation-checklist {
  background: #fdfdfd;
  border: 1px solid #e0e0e0;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}

.checklist-title {
  font-weight: bold;
  font-size: 13px;
  margin-bottom: 8px;
  color: #333;
}

.checkbox-label {
  display: block;
  margin-bottom: 5px;
  font-size: 13px;
  cursor: pointer;
}

.checkbox-label input {
  margin-right: 8px;
}
</style>