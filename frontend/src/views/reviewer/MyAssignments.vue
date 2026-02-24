<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()
const route = useRoute()
const user = computed(() => userStore.user)

// Filter State from Route Query or Default
const currentFilter = ref(route.query.filter || 'pending')

// Update filter when route changes
watch(() => route.query.filter, (newFilter) => {
  if (newFilter) {
    currentFilter.value = newFilter
  }
})

// Search & Sort
const searchQuery = ref('')
const sortField = ref('dueDate')
const sortOrder = ref('asc')

// Tab Navigation
const tabs = [
  { id: 'invitations', label: 'My Invitations' },
  { id: 'pending', label: 'Pending Reviews' },
  { id: 're-reviews', label: 'Pending Re-reviews' },
  { id: 'completed', label: 'Completed Reviews' },
  { id: 'overdue', label: 'Overdue Reviews' }
]

// Tab Counts
const tabCounts = computed(() => {
  const counts = {
    invitations: mockInvitations.value.filter(i => i.status === 'Invited').length,
    pending: 0,
    're-reviews': 0,
    completed: 0,
    overdue: 0
  }

  if (userStore.journals) {
    userStore.journals.forEach(j => {
      const status = j.status
      const stage = j.reviewStage
      const overdue = isOverdue(j.date)
      const isUnderReview = status === 'under_peer_review' || status === '审稿中' || status === 'Under Review'
      const isRevisionStage = stage === '复审' || stage === 'Re-review'
      
      // Check if current user is assigned to this manuscript
      const isAssigned = !j.assignedReviewers || j.assignedReviewers.length === 0 || 
                         j.assignedReviewers.some(r => {
                           // Support both old string format and new object format
                           if (typeof r === 'string') {
                             return r === user.value.username || r.includes(user.value.username)
                           } else if (typeof r === 'object' && r !== null) {
                             return r.name === user.value.username || 
                                    r.id === user.value.username ||
                                    String(r.id) === String(user.value.id)
                           }
                           return false
                         })
      
      // Check if user has reviewed in current stage (for pending/re-reviews filter)
      const reviews = j.reviewHistory || j.reviews || []
      const hasReviewedCurrentStage = isRevisionStage 
        ? reviews.some(r => r.reviewer === user.value.username && (r.stage === 'Re-review' || r.stage === '复审'))
        : reviews.some(r => r.reviewer === user.value.username)
      
      // Check if user has ANY review history (for completed filter)
      const hasAnyReviewHistory = reviews.some(r => r.reviewer === user.value.username)

      // Pending: Under Review, not Re-review, not overdue, not reviewed yet in current stage, assigned to user
      if (isUnderReview && !isRevisionStage && !overdue && !hasReviewedCurrentStage && isAssigned) counts.pending++
      // Re-reviews: Under Review, Re-review stage, not overdue, not reviewed yet in current stage, assigned to user
      if (isUnderReview && isRevisionStage && !overdue && !hasReviewedCurrentStage && isAssigned) counts['re-reviews']++
      // Completed: User has ANY review history (show all historical reviews)
      if (hasAnyReviewHistory) counts.completed++
      // Overdue: Under Review and overdue, not reviewed yet in current stage, assigned to user
      if (isUnderReview && overdue && !hasReviewedCurrentStage && isAssigned) counts.overdue++
    })
  }

  return counts
})

const setFilter = (filter) => {
  currentFilter.value = filter
  router.push({ query: { ...route.query, filter } })
}

// Helper to calculate due date (simulated for now, 14 days from submission)
const getDueDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  d.setDate(d.getDate() + 14)
  return d.toISOString().split('T')[0]
}

const isOverdue = (date) => {
  const dueDateStr = getDueDate(date)
  if (!dueDateStr) return false
  const dueDate = new Date(dueDateStr)
  if (isNaN(dueDate.getTime())) return false
  const today = new Date()
  return today > dueDate
}

const isNearDue = (date) => {
  const dueDateStr = getDueDate(date)
  if (!dueDateStr) return false
  const dueDate = new Date(dueDateStr)
  if (isNaN(dueDate.getTime())) return false
  const today = new Date()
  const diffTime = dueDate - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays <= 3 && diffDays >= 0
}

// Mock Invitations Data (Linked to Store)
const mockInvitations = computed(() => userStore.invitations)

// Table Headers
const tableHeaders = computed(() => {
  if (currentFilter.value === 'invitations') {
    return ['Manuscript ID', 'Title', 'Type', 'Invitation Date', 'Status', 'Actions']
  } else if (currentFilter.value === 're-reviews') {
    return ['Manuscript ID', 'Title', 'Type', 'Submission Date', 'Due Date', 'Status', 'Actions']
  } else {
    // pending, completed, overdue
    return ['Manuscript ID', 'Title', 'Type', 'Submission Date', 'Due Date', 'Status', 'Actions']
  }
})

// Filtered Assignments
const assignments = computed(() => {
  let list = []

  // 1. Initial Data Source
  if (currentFilter.value === 'invitations') {
    // Show all invitations (Invited, Accepted, Declined) for history purpose, 
    // or typically just Invited.
    // Spec says for Decline: "Status label changes... Stay on My Invitations list... Manuscript kept as history".
    // Spec says for Accept: "Status label changes... Auto jump".
    // So we should show all.
    list = [...mockInvitations.value]
  } else {
    list = userStore.journals.filter(j => {
      const status = j.status
      const stage = j.reviewStage
      const overdue = isOverdue(j.date)
      const isUnderReview = status === 'under_peer_review' || status === '审稿中' || status === 'Under Review'
      const isRevisionStage = stage === '复审' || stage === 'Re-review'
      
      // Check if current user is assigned to this manuscript
      const isAssigned = !j.assignedReviewers || j.assignedReviewers.length === 0 || 
                         j.assignedReviewers.some(r => {
                           // Support both old string format and new object format
                           if (typeof r === 'string') {
                             return r === user.value.username || r.includes(user.value.username)
                           } else if (typeof r === 'object' && r !== null) {
                             return r.name === user.value.username || 
                                    r.id === user.value.username ||
                                    String(r.id) === String(user.value.id)
                           }
                           return false
                         })
      
      // Check if user has reviewed in current stage (for pending/re-reviews/overdue filter)
      const reviews = j.reviewHistory || j.reviews || []
      const hasReviewedCurrentStage = isRevisionStage 
        ? reviews.some(r => r.reviewer === user.value.username && (r.stage === 'Re-review' || r.stage === '复审'))
        : reviews.some(r => r.reviewer === user.value.username)
      
      // Check if user has ANY review history (for completed filter)
      const hasAnyReviewHistory = reviews.some(r => r.reviewer === user.value.username)
      
      if (currentFilter.value === 'pending') {
        return isUnderReview && !isRevisionStage && !overdue && !hasReviewedCurrentStage && isAssigned
      }
      
      if (currentFilter.value === 're-reviews') {
         return isUnderReview && isRevisionStage && !overdue && !hasReviewedCurrentStage && isAssigned
      }
      
      if (currentFilter.value === 'completed') {
        // Show all manuscripts that user has reviewed (any stage)
        return hasAnyReviewHistory
      }
      
      if (currentFilter.value === 'overdue') {
         return isUnderReview && overdue && !hasReviewedCurrentStage && isAssigned
      }
      
      return false
    })
  }

  // 2. Search
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(j => 
      j.title.toLowerCase().includes(q) || 
      String(j.id).includes(q) ||
      (j.module && j.module.toLowerCase().includes(q)) ||
      (j.date && j.date.includes(q))
    )
  }

  // 3. Sort
  list.sort((a, b) => {
    let valA = a[sortField.value]
    let valB = b[sortField.value]
    
    if (sortField.value === 'dueDate') {
       valA = getDueDate(a.date)
       valB = getDueDate(b.date)
    }

    if (valA < valB) return sortOrder.value === 'asc' ? -1 : 1
    if (valA > valB) return sortOrder.value === 'asc' ? 1 : -1
    return 0
  })

  return list
})

// Actions
const showDeclineModal = ref(false)
const showAcceptModal = ref(false)
const declineReason = ref('')
const declineOption = ref('') // New for Radio Selection
const currentActionId = ref(null)
const currentActionItem = ref(null)

const openAcceptModal = (item) => {
  currentActionItem.value = item
  showAcceptModal.value = true
}

const confirmAccept = () => {
  if (currentActionItem.value) {
    acceptInvitation(currentActionItem.value)
  }
  showAcceptModal.value = false
  currentActionItem.value = null
}

const openDeclineModal = (item) => {
  currentActionId.value = item.id
  declineReason.value = ''
  declineOption.value = ''
  showDeclineModal.value = true
}

const acceptInvitation = (item) => {
  // Update Invitation Status
  const updatedItem = { ...item, status: 'Accepted' }
  userStore.updateInvitation(updatedItem)
  
  // Create a new journal entry in the store to represent this accepted assignment
  const newAssignment = {
    id: item.id,
    title: item.title,
    module: item.module,
    date: new Date().toISOString().split('T')[0], // Reset due date start
    submissionDate: item.date,
    status: 'under_peer_review',
    reviewStage: '初审',
    writer: 'writer_unknown', // Mock
    abstract: 'This is a mock abstract for the newly accepted invitation.',
    keywords: 'Mock, Keywords',
    attachments: [],
    reviewHistory: []
  }
  
  // Check if it already exists (to avoid duplicates if re-running demo)
  const existing = userStore.journals.find(j => j.id === item.id)
  if (!existing) {
    userStore.addJournal(newAssignment)
  }

  // Auto Jump after small delay to show status change (optional, but good UX)
  setTimeout(() => {
    router.push({ query: { ...route.query, filter: 'pending' } })
    currentFilter.value = 'pending'
  }, 500)
}

const submitDecline = () => {
  if (!declineOption.value) {
    alert('Please select a reason.')
    return
  }
  if (declineOption.value === 'Other' && !declineReason.value) {
    alert('Please enter a reason.')
    return
  }
  
  // Update Invitation Status
  const updatedItem = { ...mockInvitations.value.find(i => i.id === currentActionId.value), status: 'Declined' }
  userStore.updateInvitation(updatedItem)
  
  showDeclineModal.value = false
}

const getStatusDisplay = (status, stage) => {
  if (status === 'under_peer_review' || status === '审稿中' || status === 'Under Review') {
    if (stage === '复审' || stage === 'Re-review') return 'Revision Pending'
    return 'Under Review'
  }
  if (status === 'Invited') return 'Invited'
  if (status === 'Accepted') return 'Accepted'
  if (status === 'Declined') return 'Declined'
  if (status === 'review_completed' || status === '已审核') return 'Completed'
  return status
}

// Draft Detection
const drafts = ref({})

const checkDrafts = () => {
  if (!userStore.journals) return
  userStore.journals.forEach(j => {
    const key = `review_draft_${j.id}`
    if (localStorage.getItem(key)) {
      drafts.value[j.id] = true
    } else {
      drafts.value[j.id] = false
    }
  })
}

onMounted(() => {
  checkDrafts()
  // Re-check periodically in case draft was deleted or added
  setInterval(checkDrafts, 5000)
})

const viewAssignment = (id) => {
  if (currentFilter.value === 'completed') {
    router.push({ path: `/reviewer/manuscript/${id}`, query: { view: 'details' } })
    return
  }

  if (drafts.value[id]) {
    // If draft exists, go directly to review form
    router.push({ path: `/reviewer/manuscript/${id}`, query: { tab: 'review-form' } })
  } else {
    router.push(`/reviewer/manuscript/${id}`)
  }
}
</script>

<template>
  <div class="my-assignments-container">
    <Navigation 
      :user="user"
      current-page="reviewer-assignments" 
    />

    <main class="content">
      <div class="page-header">
        <h1>My Assignments</h1>
      </div>

      <!-- Filters & Actions -->
      <div class="controls-section">
        <div class="tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.id"
            class="tab-btn"
            :class="{ active: currentFilter === tab.id }"
            @click="setFilter(tab.id)"
          >
            {{ tab.label }} <span class="tab-count">({{ tabCounts[tab.id] }})</span>
          </button>
        </div>

        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="Search by Manuscript ID, Title, Writer..."
            class="search-input"
          />
          <span v-if="searchQuery" class="clear-icon" @click="searchQuery = ''">×</span>
        </div>
      </div>

      <!-- Assignments List -->
      <div class="assignments-table-container">
        <table class="assignments-table">
          <thead>
            <tr>
              <th v-for="header in tableHeaders" :key="header">{{ header }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in assignments" :key="item.id">
              <td>{{ item.id }}</td>
              <td class="title-cell" :title="item.title">
                <span @click="viewAssignment(item.id)">{{ item.title }}</span>
              </td>
              <td>{{ item.module || 'Research Article' }}</td>
              <td>{{ item.date }}</td>
              <td v-if="currentFilter !== 'invitations'" :class="{ 
                'text-danger': isOverdue(item.date),
                'text-warning': isNearDue(item.date) && !isOverdue(item.date)
              }">
                {{ getDueDate(item.date) }}
                <span v-if="isOverdue(item.date)" class="overdue-text">
                  (Overdue by {{ Math.floor((new Date() - new Date(getDueDate(item.date))) / (1000 * 60 * 60 * 24)) }} days)
                </span>
                <span v-if="isNearDue(item.date) && !isOverdue(item.date)" class="neardue-text">
                  (Due soon)
                </span>
              </td>
              <td>
                <span class="status-badge" :class="{
                  'status-pending': (item.status === 'under_peer_review' || item.status === '审稿中') && item.reviewStage !== '复审' && item.reviewStage !== 'Re-review',
                  'status-revision': (item.status === 'under_peer_review' || item.status === '审稿中') && (item.reviewStage === '复审' || item.reviewStage === 'Re-review'),
                  'status-invited': item.status === 'Invited',
                  'status-accepted': item.status === 'Accepted',
                  'status-declined': item.status === 'Declined',
                  'status-completed': item.status === 'review_completed' || item.status === '已审核',
                  'status-overdue': isOverdue(item.date) && (item.status === 'under_peer_review' || item.status === '审稿中')
                }">
                  {{ isOverdue(item.date) && (item.status === 'under_peer_review' || item.status === '审稿中') ? 'Overdue' : getStatusDisplay(item.status, item.reviewStage) }}
                </span>
              </td>
              <td class="actions-cell">
                
                <!-- 1. Pending / Overdue -->
                <template v-if="['pending', 'overdue'].includes(currentFilter)">
                  <template v-if="item.reviewStage !== '复审' && item.reviewStage !== 'Re-review'">
                     <button class="action-btn btn-primary" @click="viewAssignment(item.id)">
                      {{ drafts[item.id] ? 'Continue Review' : 'Start Review' }}
                    </button>
                  </template>
                  <template v-else>
                     <button class="action-btn btn-primary" @click="viewAssignment(item.id)">
                      {{ drafts[item.id] ? 'Continue Review' : 'Review Revision' }}
                    </button>
                  </template>
                </template>

                <!-- 2. Re-reviews -->
                <template v-else-if="currentFilter === 're-reviews'">
                  <button class="action-btn btn-primary" @click="viewAssignment(item.id)">
                    {{ drafts[item.id] ? 'Continue Review' : 'Review Revision' }}
                  </button>
                </template>

                <!-- 3. Invitations -->
                <template v-else-if="currentFilter === 'invitations'">
                  <template v-if="item.status === 'Invited'">
                    <button class="action-btn btn-primary" @click="openAcceptModal(item)">
                      Accept
                    </button>
                    <button class="action-btn btn-secondary" @click="openDeclineModal(item)">
                      Decline
                    </button>
                  </template>
                  <template v-else>
                    <!-- No actions for Accepted/Declined items in this list -->
                  </template>
                </template>

                <!-- 4. Completed -->
                <template v-else>
                   <button class="action-btn btn-view" @click="viewAssignment(item.id)">View Details</button>
                </template>

              </td>
            </tr>
            <tr v-if="assignments.length === 0">
              <td :colspan="tableHeaders.length" class="empty-state">
                <span v-if="currentFilter === 'invitations'">No pending review invitations</span>
                <span v-else-if="currentFilter === 'pending'">No pending review tasks</span>
                <span v-else-if="currentFilter === 're-reviews'">No pending re-review tasks</span>
                <span v-else-if="currentFilter === 'completed'">
                  <div class="empty-title">No completed review history</div>
                  <div class="empty-subtitle">You will see your completed review history here once you submit reviews or re-reviews.</div>
                </span>
                <span v-else-if="currentFilter === 'overdue'">
                  <div class="empty-title">No overdue review tasks</div>
                  <div class="empty-subtitle">You will see overdue review tasks here if you miss the due date for any review or re-review.</div>
                </span>
                <span v-else>No matching tasks</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </main>

    <!-- Accept Modal -->
    <div v-if="showAcceptModal" class="modal-overlay" @click="showAcceptModal = false">
      <div class="modal-content" @click.stop>
        <h3>Confirm Accept Invitation</h3>
        <p>Are you sure you want to accept this review invitation for manuscript "{{ currentActionItem?.title }}"?</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showAcceptModal = false">Cancel</button>
          <button class="btn-confirm" @click="confirmAccept">Confirm</button>
        </div>
      </div>
    </div>

    <!-- Decline Modal -->
    <div v-if="showDeclineModal" class="modal-overlay" @click="showDeclineModal = false">
      <div class="modal-content" @click.stop>
        <h3>Decline Review Invitation</h3>
        <p>Please select or enter a reason for declining this invitation:</p>
        
        <div class="radio-group">
          <label><input type="radio" v-model="declineOption" value="Conflict of interest"> Conflict of interest</label>
          <label><input type="radio" v-model="declineOption" value="Insufficient expertise in the field"> Insufficient expertise in the field</label>
          <label><input type="radio" v-model="declineOption" value="Time constraints"> Time constraints</label>
          <label><input type="radio" v-model="declineOption" value="Other"> Other</label>
        </div>

        <textarea 
          v-if="declineOption === 'Other'"
          v-model="declineReason" 
          placeholder="Enter reason..." 
          class="modal-textarea"
        ></textarea>
        
        <div class="modal-actions">
          <button class="btn-cancel" @click="showDeclineModal = false">Cancel</button>
          <button class="btn-confirm" @click="submitDecline">Submit</button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
.my-assignments-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.content {
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}

.page-header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.controls-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.tabs {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 5px;
}

.tab-btn {
  padding: 0.6rem 1.2rem;
  background: white;
  border: 1px solid #ddd;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  transition: all 0.3s;
  white-space: nowrap;
}

.tab-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.tab-btn:hover:not(.active) {
  background: #f1f1f1;
}

.search-box {
  position: relative;
}

.search-input {
  padding: 0.6rem 1rem;
  padding-right: 2.5rem; /* Space for clear icon */
  border: 1px solid #ddd;
  border-radius: 5px;
  width: 300px; /* Wider for English placeholder */
  outline: none;
}

.search-input:focus {
  border-color: #3498db;
}

.clear-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  color: #999;
  font-size: 18px;
}

.clear-icon:hover {
  color: #666;
}

.tab-count {
  color: #C93737;
  font-weight: bold;
  font-size: 14px;
  margin-left: 4px;
}

.assignments-table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow-x: auto;
}

.assignments-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 800px;
}

.assignments-table th,
.assignments-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.assignments-table tbody tr {
  background-color: #FFFFFF;
  transition: background-color 0.2s;
}

.assignments-table tbody tr:hover {
  background-color: #F5F5F5;
}

.assignments-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #2c3e50;
}

.title-cell {
  max-width: 300px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #2c3e50;
  font-weight: 500;
}

.title-cell span {
  cursor: pointer;
  transition: color 0.2s;
  display: inline-block;
  width: 100%;
}

.title-cell span:hover {
  color: #C93737;
  text-decoration: underline;
}

.overdue-text {
  color: #C93737;
  font-weight: bold;
  display: block; /* New line */
  font-size: 12px;
  margin-top: 4px;
}

.neardue-text {
  color: #e67e22;
  font-weight: bold;
  display: block;
  font-size: 12px;
  margin-top: 4px;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.status-pending {
  background: #e3f2fd;
  color: #1976d2;
}

.status-revision {
  background: #fff3e0;
  color: #e67e22;
}

.status-completed {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-invited {
  background: #fff3e0;
  color: #ef6c00;
}

.status-accepted {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-declined {
  background: #f5f5f5;
  color: #999;
}

.status-overdue {
  background: #fcebeb;
  color: #C93737;
}

.text-danger {
  color: #C93737; /* Brand Red */
  font-weight: bold;
}

.text-warning {
  color: #e67e22; /* Orange */
  font-weight: bold;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: opacity 0.3s;
}

.action-btn:hover {
  opacity: 0.9;
}

/* Primary Button (Start Review, Review Revision, Accept) */
.btn-primary {
  background: #C93737; /* Brand Red */
  color: white;
}

/* Secondary Button (Decline) */
.btn-secondary {
  background: #999999; /* Grey */
  color: #333333; /* Dark Grey Text */
}

.btn-view {
  background: #999999;
  color: #333333;
  border-radius: 4px;
  font-size: 14px;
  padding: 6px 12px;
}

.btn-view:hover {
  background: #808080;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #999;
}

.empty-title {
  font-size: 14px;
  color: #999;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 12px;
  color: #999;
}

/* Modal Styles */
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
  z-index: 2000;
}
.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 400px;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}
.modal-textarea {
  width: 100%;
  height: 100px;
  margin: 1rem 0;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.btn-cancel {
  background: #f1f1f1;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
}
.btn-confirm {
  background: #C93737;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
</style>
