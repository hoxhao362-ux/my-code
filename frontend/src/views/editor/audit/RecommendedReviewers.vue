<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import ConflictOfInterestCheck from '../../../components/audit/ConflictOfInterestCheck.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

// 筛选条件
const selectedStatus = ref('all')
const selectedField = ref('all')
const selectedRisk = ref('all')
const selectedStage = ref('all')
const searchKeyword = ref('')

// 状态选项
const statusOptions = ['all', 'pending', 'accepted', 'rejected', 'invited', 'completed', 'declined', 'contact_failed', 'withdrawn']
const statusLabels = {
  all: 'All Status',
  pending: 'Pending Review',
  accepted: 'Accepted',
  rejected: 'Rejected',
  invited: 'Invited',
  completed: 'Completed',
  declined: 'Declined Invitation',
  contact_failed: 'Contact Failed',
  withdrawn: 'Withdrawn by Author'
}

// Stage Options
const stageOptions = ['all', 'initial', 'revision']
const stageLabels = {
  all: 'All Stages',
  initial: 'Initial Submission',
  revision: 'Revision'
}

// 风险等级选项
const riskOptions = ['all', 'low', 'medium', 'high']
const riskLabels = {
  all: 'All Risks',
  low: 'Low Risk',
  medium: 'Medium Risk',
  high: 'High Risk'
}

// 专业领域选项
const fieldOptions = ['all', 'Clinical', 'Public Health', 'Global Health', 'Medical Imaging', 'Drug Discovery', 'Bioinformatics']
const fieldLabels = {
  all: 'All Fields',
  Clinical: 'Clinical',
  'Public Health': 'Public Health',
  'Global Health': 'Global Health',
  'Medical Imaging': 'Medical Imaging',
  'Drug Discovery': 'Drug Discovery',
  'Bioinformatics': 'Bioinformatics'
}

// Use Store Data
const recommendedReviewers = computed(() => userStore.recommendedReviewers)

// 筛选后的推荐评审人
const filteredReviewers = computed(() => {
  let result = recommendedReviewers.value
  
  // 按状态筛选
  if (selectedStatus.value !== 'all') {
    result = result.filter(r => r.status === selectedStatus.value)
  }
  
  // 按专业领域筛选
  if (selectedField.value !== 'all') {
    result = result.filter(r => r.reviewerExpertise.includes(selectedField.value))
  }

  // Filter by Stage
  if (selectedStage.value !== 'all') {
    result = result.filter(r => (r.stage || 'initial') === selectedStage.value)
  }

  // 按风险等级筛选
  if (selectedRisk.value !== 'all') {
    result = result.filter(r => r.riskLevel === selectedRisk.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value.trim()) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(r => 
      r.manuscriptTitle.toLowerCase().includes(keyword) ||
      r.reviewerName.toLowerCase().includes(keyword) ||
      r.reviewerAffiliation.toLowerCase().includes(keyword) ||
      r.recommendationReason.toLowerCase().includes(keyword)
    )
  }
  
  return result
})

const MAX_ACTIVE_REVIEWS = 3
const MAX_AUTHOR_RECOMMENDED_PER_MANUSCRIPT = 2

// History: Get all recommendations by current author
const currentAuthorHistory = computed(() => {
  if (!currentReviewer.value) return []
  return recommendedReviewers.value.filter(r => 
    r.authorId === currentReviewer.value.authorId
  ).sort((a, b) => new Date(b.recommendedAt) - new Date(a.recommendedAt))
})

// History: Count how many times this specific reviewer was recommended by this author
const currentReviewerFrequency = computed(() => {
  if (!currentReviewer.value) return 0
  return recommendedReviewers.value.filter(r => 
    r.authorId === currentReviewer.value.authorId && 
    r.reviewerEmail === currentReviewer.value.reviewerEmail
  ).length
})

// History: Flag frequent recommendations (> 2 times)
const isFrequentRecommendation = computed(() => {
  return currentReviewerFrequency.value > 2
})

// Helper: Check for active reviews limit
const checkReviewerLimit = (reviewer) => {
  const activeCount = recommendedReviewers.value.filter(r => 
    r.reviewerEmail === reviewer.reviewerEmail && 
    ['invited', 'accepted'].includes(r.status)
  ).length
  
  return {
    isOverLimit: activeCount >= MAX_ACTIVE_REVIEWS,
    count: activeCount
  }
}

// Helper: Check for Author Recommendation Limit
const checkAuthorRecommendationLimit = (manuscriptId) => {
  const acceptedCount = recommendedReviewers.value.filter(r => 
    String(r.manuscriptId) === String(manuscriptId) && 
    ['accepted', 'invited', 'completed'].includes(r.status)
  ).length
  
  return {
    isOverLimit: acceptedCount >= MAX_AUTHOR_RECOMMENDED_PER_MANUSCRIPT,
    count: acceptedCount
  }
}

// Helper: Check for Conflict of Interest
const checkConflictOfInterest = (reviewer) => {
  const conflicts = []
  
  // 1. Affiliation Check (Mock: Check against author's affiliation if available, or just warn if same as previous authors)
  // In a real app, we would fetch the manuscript author's affiliation.
  // Here we check if the reviewer affiliation contains the author name (just as a dummy heuristic) or if high risk.
  if (reviewer.riskLevel === 'high') {
    conflicts.push('High Risk Reviewer (Frequent recommendations or low quality)')
  }
  
  if (reviewer.submissionCount > 2) {
    conflicts.push(`Frequent Recommended Reviewer (${reviewer.submissionCount} times by this author)`)
  }

  // Integrity Check (Mock)
  if (reviewer.reviewerName.toLowerCase().includes('bad') || reviewer.reviewerEmail.includes('fake')) {
    conflicts.push('Academic Integrity Alert: Name/Email matches flagged list')
  }

  return conflicts
}

// Helper: Add history record to journal
const addToJournalHistory = (manuscriptId, action, reviewerName, reason) => {
  const journal = userStore.journals.find(j => String(j.id) === String(manuscriptId))
  if (!journal) return false

  const newRecord = {
    stage: 'Reviewer Recommendation',
    status: action === 'accepted' ? 'Accepted' : (action === 'declined' ? 'Declined Invitation' : (action === 'contact_failed' ? 'Contact Failed' : 'Rejected')),
    reviewer: user.value?.username || 'admin',
    date: new Date().toISOString().split('T')[0],
    comment: `Editor updated status to ${action} for reviewer: ${reviewerName}. Reason/Note: ${reason || 'N/A'}`,
    type: 'Recommended Reviewer'
  }

  const updatedJournal = {
    ...journal,
    reviewHistory: [...(journal.reviewHistory || []), newRecord]
  }

  // Also add to System Logs (Global Audit)
  userStore.addSystemLog({
    type: 'operation',
    user: user.value?.username || 'admin',
    action: `Reviewer Recommendation: ${action}`,
    target: `Reviewer: ${reviewerName} (Manuscript ID: ${manuscriptId})`,
    ip: '192.168.1.' + Math.floor(Math.random() * 255) // Mock IP
  })

  return userStore.updateJournal(updatedJournal)
}

// 批量操作
const selectedReviewerIds = ref([])
const toggleSelectAll = () => {
  if (selectedReviewerIds.value.length === filteredReviewers.value.length) {
    selectedReviewerIds.value = []
  } else {
    selectedReviewerIds.value = filteredReviewers.value.map(r => r.id)
  }
}

const handleBulkAccept = () => {
  if (selectedReviewerIds.value.length === 0) {
    alert('Please select at least one reviewer to accept.')
    return
  }
  
  // Aggregate Warnings
  let totalWarnings = []
  
  // Check High Risk
  const highRiskCount = recommendedReviewers.value.filter(r => selectedReviewerIds.value.includes(r.id) && r.riskLevel === 'high').length
  if (highRiskCount > 0) totalWarnings.push(`- ${highRiskCount} high-risk reviewers selected.`)

  // Check Limits
  const selectedReviewers = recommendedReviewers.value.filter(r => selectedReviewerIds.value.includes(r.id))
  
  // Group by manuscript to check per-manuscript limit
  const byManuscript = {}
  selectedReviewers.forEach(r => {
    if (!byManuscript[r.manuscriptId]) byManuscript[r.manuscriptId] = 0
    byManuscript[r.manuscriptId]++
  })
  
  Object.keys(byManuscript).forEach(mid => {
    const currentCount = checkAuthorRecommendationLimit(mid).count
    if (currentCount + byManuscript[mid] > MAX_AUTHOR_RECOMMENDED_PER_MANUSCRIPT) {
      totalWarnings.push(`- Manuscript ID ${mid} will exceed the limit of ${MAX_AUTHOR_RECOMMENDED_PER_MANUSCRIPT} author-recommended reviewers.`)
    }
  })

  if (totalWarnings.length > 0) {
    if (!confirm(`Bulk Action Warnings:\n\n${totalWarnings.join('\n')}\n\nDo you want to proceed anyway?`)) {
      return
    }
  }
  
  selectedReviewerIds.value.forEach(id => {
    const reviewer = recommendedReviewers.value.find(r => r.id === id)
    if (reviewer) {
      const updated = { ...reviewer, status: 'accepted', reviewedAt: new Date().toISOString(), reviewedBy: user.value?.username || 'admin' }
      userStore.updateRecommendedReviewer(updated)
      
      // Add to history
      addToJournalHistory(reviewer.manuscriptId, 'accepted', reviewer.reviewerName, 'Bulk acceptance')
    }
  })

  // Notify Authors (Mock)
  alert(`Notifications sent to ${selectedReviewerIds.value.length} authors about accepted reviewers.`)
  
  selectedReviewerIds.value = []
  alert('Selected reviewers have been accepted and recorded in manuscript history.')
}

const handleBulkReject = () => {
  if (selectedReviewerIds.value.length === 0) {
    alert('Please select at least one reviewer to reject.')
    return
  }
  
  selectedReviewerIds.value.forEach(id => {
    const reviewer = recommendedReviewers.value.find(r => r.id === id)
    if (reviewer) {
      const updated = { ...reviewer, status: 'rejected', reviewedAt: new Date().toISOString(), reviewedBy: user.value?.username || 'admin' }
      userStore.updateRecommendedReviewer(updated)
      
      // Add to history
      addToJournalHistory(reviewer.manuscriptId, 'rejected', reviewer.reviewerName, 'Bulk rejection')
    }
  })
  
  selectedReviewerIds.value = []
  alert('Selected reviewers have been rejected and recorded in manuscript history.')
}

// 详情模态框
const showDetailModal = ref(false)
const currentReviewer = ref(null)
const reviewComment = ref('')

const openDetailModal = (reviewer) => {
  currentReviewer.value = { ...reviewer } // Clone to avoid direct mutation of prop if passed, though here it's from store
  reviewComment.value = ''
  showDetailModal.value = true
}

const handleAccept = () => {
  if (currentReviewer.value) {
    // 1. Check Author Recommendation Limit
    const limitCheck = checkAuthorRecommendationLimit(currentReviewer.value.manuscriptId)
    if (limitCheck.isOverLimit) {
      if (!confirm(`Warning: This manuscript already has ${limitCheck.count} author-recommended reviewers accepted/invited. 
      
      Best practice is to limit author recommendations to ${MAX_AUTHOR_RECOMMENDED_PER_MANUSCRIPT} per paper.
      
      Do you still want to proceed?`)) {
        return
      }
    }

    // 2. Check Reviewer Workload Limit
    const workloadCheck = checkReviewerLimit(currentReviewer.value)
    if (workloadCheck.isOverLimit) {
      if (!confirm(`Warning: Reviewer ${currentReviewer.value.reviewerName} already has ${workloadCheck.count} active reviews.
      
      Do you still want to assign more work?`)) {
        return
      }
    }

    // 3. Conflict of Interest Check
    const conflicts = checkConflictOfInterest(currentReviewer.value)
    if (conflicts.length > 0) {
       const conflictMsg = conflicts.map(c => `- ${c}`).join('\n')
       if (!confirm(`Potential Conflict of Interest / Risk Detected:\n\n${conflictMsg}\n\nAre you sure you want to accept?`)) {
         return
       }
    }

    const updated = { ...currentReviewer.value, status: 'accepted', reviewedAt: new Date().toISOString(), reviewedBy: user.value?.username || 'admin' }
    userStore.updateRecommendedReviewer(updated)
    
    // Add to history
    addToJournalHistory(currentReviewer.value.manuscriptId, 'accepted', currentReviewer.value.reviewerName, reviewComment.value)

    // Notify Author
    alert(`Notification sent to author (${currentReviewer.value.authorName}): Your recommended reviewer ${currentReviewer.value.reviewerName} has been accepted.`)

    showDetailModal.value = false
    alert('Reviewer accepted successfully. Record added to manuscript history.')
  }
}

const handleReject = () => {
  if (currentReviewer.value) {
    const updated = { ...currentReviewer.value, status: 'rejected', reviewedAt: new Date().toISOString(), reviewedBy: user.value?.username || 'admin' }
    userStore.updateRecommendedReviewer(updated)
    
    // Notify Author
    const reason = reviewComment.value || 'Editorial decision.'

    // Add to history
    addToJournalHistory(currentReviewer.value.manuscriptId, 'rejected', currentReviewer.value.reviewerName, reason)

    alert(`Notification sent to author (${currentReviewer.value.authorName}): Your recommended reviewer ${currentReviewer.value.reviewerName} was not selected. Reason: ${reason}`)

    showDetailModal.value = false
    alert('Reviewer rejected successfully. Record added to manuscript history.')
  }
}

// Special Case Handlers
const handleMarkDeclined = () => {
  if (currentReviewer.value) {
    if (!confirm('Are you sure you want to mark this reviewer as "Declined Invitation"? This will require selecting an alternative.')) return
    
    const updated = { ...currentReviewer.value, status: 'declined', reviewedAt: new Date().toISOString(), reviewedBy: user.value?.username || 'admin' }
    userStore.updateRecommendedReviewer(updated)
    
    addToJournalHistory(currentReviewer.value.manuscriptId, 'declined', currentReviewer.value.reviewerName, reviewComment.value || 'Reviewer declined invitation.')
    
    showDetailModal.value = false
    alert('Marked as Declined. Please proceed to invite an alternative reviewer.')
  }
}

const handleMarkContactFailed = () => {
  if (currentReviewer.value) {
    if (!confirm('Are you sure you want to mark this reviewer as "Contact Failed"? This implies incorrect contact information.')) return
    
    const updated = { ...currentReviewer.value, status: 'contact_failed', reviewedAt: new Date().toISOString(), reviewedBy: user.value?.username || 'admin' }
    userStore.updateRecommendedReviewer(updated)
    
    addToJournalHistory(currentReviewer.value.manuscriptId, 'contact_failed', currentReviewer.value.reviewerName, reviewComment.value || 'Email bounced/Contact failed.')
    
    showDetailModal.value = false
    alert('Marked as Contact Failed. You may request updated information from the author.')
  }
}

const handleInviteAlternative = (reviewer) => {
  alert(`Redirecting to reviewer search to find alternative for: ${reviewer.manuscriptTitle}`)
  // Logic to redirect to assign reviewer page or show search modal would go here
}

const handleRequestInfoUpdate = (reviewer) => {
  alert(`Notification sent to author ${reviewer.authorName} to update contact info for ${reviewer.reviewerName}.`)
  // Logic to send notification would go here
}

// 邀请模态框
const showInviteModal = ref(false)
const inviteForm = ref({
  subject: '',
  content: ''
})

const openInviteModal = (reviewer) => {
  currentReviewer.value = { ...reviewer }
  
  // Default Template (mocking the one from config)
  // Check if double-blind is enabled (mock setting)
  const isDoubleBlind = true // Mock: get from journal settings
  
  const link = `${window.location.origin}/reviewer-registration?email=${encodeURIComponent(reviewer.reviewerEmail)}&recommendationId=${reviewer.id}&token=${Date.now()}`
  
  // Conditionally hide author name
  const authorReference = isDoubleBlind ? 'an author' : `the author ${reviewer.authorName}`
  
  const stageSuffix = reviewer.stage === 'revision' ? ' (Revision)' : ''
  const stageContext = reviewer.stage === 'revision' ? 'revised ' : ''

  inviteForm.value = {
    subject: `Invitation to Review${stageSuffix}: ${reviewer.manuscriptTitle}`,
    content: `Dear Dr. ${reviewer.reviewerName},

We would like to invite you to review the ${stageContext}manuscript entitled "${reviewer.manuscriptTitle}" (ID: ${reviewer.manuscriptId}) submitted by ${authorReference} for our journal.

Abstract:
(Abstract of the manuscript would go here...)

Please click the link below to accept this invitation and register as a temporary reviewer:
${link}

Sincerely,

The Editorial Office
${userStore.basicConfig?.platformName || 'Journal Platform'}`
  }
  
  showInviteModal.value = true
}

const sendInvitation = () => {
  if (currentReviewer.value) {
    // 1. Check Author Recommendation Limit
    const limitCheck = checkAuthorRecommendationLimit(currentReviewer.value.manuscriptId)
    if (limitCheck.isOverLimit) {
      if (!confirm(`Warning: This manuscript already has ${limitCheck.count} author-recommended reviewers accepted/invited. Proceed with invitation?`)) {
        return
      }
    }
    
    // 2. Conflict Check
    const conflicts = checkConflictOfInterest(currentReviewer.value)
    if (conflicts.length > 0) {
       const conflictMsg = conflicts.map(c => `- ${c}`).join('\n')
       if (!confirm(`Potential Conflict of Interest / Risk Detected:\n\n${conflictMsg}\n\nProceed with invitation?`)) {
         return
       }
    }

    const updated = { 
      ...currentReviewer.value, 
      status: 'invited', 
      reviewedAt: new Date().toISOString(), 
      reviewedBy: user.value?.username || 'admin' 
    }
    userStore.updateRecommendedReviewer(updated)
    
    addToJournalHistory(currentReviewer.value.manuscriptId, 'invited', currentReviewer.value.reviewerName, 'Invitation email sent.')
    
    showInviteModal.value = false
    alert(`Invitation sent to ${currentReviewer.value.reviewerEmail} successfully.`)
  }
}

// 评价模态框 (Quality Evaluation)
const showEvalModal = ref(false)
const evalForm = ref({
  timeliness: 5,
  professionalism: 5,
  standardization: 5,
  objectivity: 5,
  comment: ''
})

const calculatedGrade = computed(() => {
  const avg = (evalForm.value.timeliness + evalForm.value.professionalism + evalForm.value.standardization + evalForm.value.objectivity) / 4
  if (avg >= 4.8) return 'S'
  if (avg >= 4.0) return 'A'
  if (avg >= 3.0) return 'B'
  return 'C'
})

const openEvalModal = (reviewer) => {
  currentReviewer.value = { ...reviewer }
  evalForm.value = { timeliness: 5, professionalism: 5, standardization: 5, objectivity: 5, comment: '' }
  showEvalModal.value = true
}

const submitEvaluation = () => {
  if (evalForm.value.comment.length < 10) {
    alert('Please enter at least 10 characters for comment.')
    return
  }
  
  if (currentReviewer.value) {
    const updated = { 
      ...currentReviewer.value, 
      evalStatus: 'evaluated',
      avgScore: ((evalForm.value.timeliness + evalForm.value.professionalism + evalForm.value.standardization + evalForm.value.objectivity) / 4).toFixed(1)
    }
    
    // Check for low score warning
    if (calculatedGrade.value === 'C') {
       alert(`Warning: Reviewer graded C. System will flag this reviewer as High Risk for future recommendations.`)
       updated.riskLevel = 'high'
    }
    
    // Check for Malicious Recommendation (System Logic)
    // If the reviewer is flagged as High Risk AND the grade is C, we warn the author.
    if (calculatedGrade.value === 'C') {
       // Add a system log for "Malicious Recommendation Warning"
       userStore.addSystemLog({
          type: 'warning',
          user: user.value?.username || 'system',
          action: 'Malicious Recommendation Detected',
          target: `Author: ${currentReviewer.value.authorName} (Reviewer: ${currentReviewer.value.reviewerName})`,
          ip: '127.0.0.1'
       })
       
       // In a real system, this would trigger an email. Here we simulate it.
       alert(`SYSTEM ALERT: Malicious Recommendation Detected.\n\nA warning has been recorded for author ${currentReviewer.value.authorName} regarding the recommendation of ${currentReviewer.value.reviewerName} (Grade: C).\n\nAction: Author flagged for monitoring.`)
    }

    userStore.updateRecommendedReviewer(updated)
  }
  
  showEvalModal.value = false
  alert('Evaluation submitted successfully.')
}

// 状态标签样式
const getStatusClass = (status) => {
  switch (status) {
    case 'pending': return 'status-pending'
    case 'accepted': return 'status-accepted'
    case 'rejected': return 'status-rejected'
    case 'invited': return 'status-invited'
    case 'completed': return 'status-completed'
    case 'declined': return 'status-declined'
    case 'contact_failed': return 'status-failed'
    case 'withdrawn': return 'status-withdrawn'
    default: return ''
  }
}

// 状态显示文本
const getStatusText = (status) => {
  if (status === 'accepted') return 'Accepted (Pool)'
  return statusLabels[status] || status
}

// 风险等级样式
const getRiskClass = (level) => {
  switch (level) {
    case 'high': return 'risk-high'
    case 'medium': return 'risk-medium'
    case 'low': return 'risk-low'
    default: return ''
  }
}
</script>

<template>
  <div class="lancet-container">
    <Navigation 
      v-if="!$attrs.embedded"
      :user="user" 
      current-page="audit-recommended-reviewers" 
      :toggle-directory="()=>{}" 
      :logout="userStore.logout" 
    />

    <main class="content">
      <!-- Header -->
      <div class="page-header">
        <h1 class="main-title">Recommended Reviewers Quality Assurance</h1>
        <p class="warning-text">Review and manage reviewers recommended by authors for {{ PLATFORM_NAME }}. Monitor quality and prevent abuse.</p>
        
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
          <select v-model="selectedRisk">
            <option v-for="risk in riskOptions" :key="risk" :value="risk">
              {{ riskLabels[risk] }}
            </option>
          </select>
          <select v-model="selectedField">
            <option v-for="field in fieldOptions" :key="field" :value="field">
              {{ fieldLabels[field] }}
            </option>
          </select>
          <input 
            type="text" 
            v-model="searchKeyword" 
            placeholder="Search by manuscript title, reviewer name, or affiliation..." 
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
            :checked="selectedReviewerIds.length === filteredReviewers.length && filteredReviewers.length > 0"
          />
          <label for="selectAll">Select All</label>
        </div>
        <button class="btn btn-primary" @click="handleBulkAccept" :disabled="selectedReviewerIds.length === 0">
          Bulk Accept
        </button>
        <button class="btn btn-red" @click="handleBulkReject" :disabled="selectedReviewerIds.length === 0">
          Bulk Reject
        </button>
      </div>

      <!-- Recommended Reviewers List -->
      <table class="lancet-table">
        <thead>
          <tr>
            <th style="width: 50px;"></th>
            <th>Manuscript Title</th>
            <th>Recommended Reviewer</th>
            <th>Stage</th>
            <th>Risk Analysis</th>
            <th>Quality (Avg)</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="reviewer in filteredReviewers" :key="reviewer.id" class="hover-row">
            <td>
              <input 
                type="checkbox" 
                :value="reviewer.id" 
                v-model="selectedReviewerIds"
              />
            </td>
            <td class="bold-text">{{ reviewer.manuscriptTitle }}</td>
            <td>
              <div>{{ reviewer.reviewerName }}</div>
              <div class="affiliation">{{ reviewer.reviewerAffiliation }}</div>
            </td>
            <td>
              <span class="stage-badge" :class="reviewer.stage === 'revision' ? 'stage-revision' : 'stage-initial'">
                {{ reviewer.stage === 'revision' ? 'Revision' : 'Initial' }}
              </span>
            </td>
            <td>
              <div class="risk-badge" :class="getRiskClass(reviewer.riskLevel)">
                {{ reviewer.riskLevel.toUpperCase() }}
              </div>
              <div class="risk-detail" v-if="reviewer.submissionCount > 1">
                <span v-if="reviewer.submissionCount > 2" class="text-danger">
                  🔥 Freq: {{ reviewer.submissionCount }}x
                </span>
                <span v-else>
                  Freq: {{ reviewer.submissionCount }}x
                </span>
              </div>
            </td>
            <td>
              <div class="score-box" :class="{ 'score-low': reviewer.avgScore < 3.0 }">
                 ★ {{ reviewer.avgScore }}
              </div>
            </td>
            <td>
              <span class="status-badge" :class="getStatusClass(reviewer.status)">
                {{ getStatusText(reviewer.status) }}
              </span>
            </td>
            <td class="actions">
              <button class="btn btn-sm btn-primary" @click="openDetailModal(reviewer)">
                Details
              </button>
              
              <button 
                v-if="reviewer.status === 'pending'" 
                class="btn btn-sm btn-success" 
                @click="openInviteModal(reviewer)"
              >
                Invite
              </button>

              <!-- Special Handling Actions -->
              <button 
                v-if="reviewer.status === 'declined'" 
                class="btn btn-sm btn-eval" 
                @click="handleInviteAlternative(reviewer)"
              >
                Alternative
              </button>
              
              <button 
                v-if="reviewer.status === 'contact_failed'" 
                class="btn btn-sm btn-grey" 
                @click="handleRequestInfoUpdate(reviewer)"
              >
                Req. Update
              </button>

              <button 
                class="btn btn-sm btn-eval" 
                v-if="reviewer.status === 'completed' && reviewer.evalStatus === 'unevaluated'"
                @click="openEvalModal(reviewer)"
              >
                Evaluate
              </button>
               <span v-if="reviewer.evalStatus === 'evaluated'" class="eval-done">Evaluated</span>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- No Results -->
      <div v-if="filteredReviewers.length === 0" class="no-data">
        No recommended reviewers found matching the current filters.
      </div>

    </main>

    <!-- Detail Modal -->
    <div v-if="showDetailModal" class="modal-overlay">
      <div class="modal-box large">
        <h3>Recommended Reviewer Details</h3>
        <div class="modal-content">
          <div class="section">
            <h4>Risk Assessment</h4>
            
            <!-- COI Check Component -->
            <ConflictOfInterestCheck 
              v-if="currentReviewer"
              :authorName="currentReviewer.authorName"
              :reviewer="{
                username: currentReviewer.reviewerName,
                affiliation: currentReviewer.reviewerAffiliation
              }"
              style="margin-bottom: 15px;"
            />

            <div class="risk-report">
               <p><strong>Risk Level:</strong> <span :class="'text-' + currentReviewer?.riskLevel">{{ currentReviewer?.riskLevel.toUpperCase() }}</span></p>
               <p><strong>Submission Frequency:</strong> Recommended {{ currentReviewer?.submissionCount }} times by this author.</p>
               <p><strong>Historical Performance:</strong> Average Score {{ currentReviewer?.avgScore }} / 5.0</p>
               
               <!-- Integrity Status -->
               <div style="margin-top: 10px; padding: 5px; border-radius: 4px;" 
                    :class="(currentReviewer?.reviewerName.toLowerCase().includes('bad') || currentReviewer?.reviewerEmail.includes('fake')) ? 'bg-danger-light' : 'bg-success-light'">
                   <strong>Integrity Database Check:</strong> 
                   <span v-if="currentReviewer?.reviewerName.toLowerCase().includes('bad') || currentReviewer?.reviewerEmail.includes('fake')">⚠️ FLAGGED (Potential Record Found)</span>
                   <span v-else>✅ CLEAN (No records found)</span>
               </div>
            </div>
          </div>

          <div class="section">
            <h4>Manuscript Information</h4>
            <p><strong>Title:</strong> {{ currentReviewer?.manuscriptTitle }}</p>
            <p><strong>Author:</strong> {{ currentReviewer?.authorName }}</p>
          </div>
          
          <div class="section">
            <h4>Reviewer Information</h4>
            <p><strong>Name:</strong> {{ currentReviewer?.reviewerName }}</p>
            <p><strong>Email:</strong> {{ currentReviewer?.reviewerEmail }}</p>
            <p><strong>Affiliation:</strong> {{ currentReviewer?.reviewerAffiliation }}</p>
            <p><strong>Expertise:</strong> {{ currentReviewer?.reviewerExpertise.join(', ') }}</p>
          </div>
          
          <div class="section">
            <h4>Recommendation Details</h4>
            <p><strong>Recommendation Reason:</strong> {{ currentReviewer?.recommendationReason }}</p>
            <p><strong>Recommended At:</strong> {{ currentReviewer?.recommendedAt ? new Date(currentReviewer.recommendedAt).toLocaleString() : 'N/A' }}</p>
          </div>
          
          <div class="section">
            <h4>Author Recommendation History</h4>
            
            <!-- Frequency Alert -->
            <div v-if="isFrequentRecommendation" class="alert-box warning">
              <span class="icon">⚠️</span>
              <div style="margin-left: 10px;">
                <strong>Frequent Recommendation:</strong> This author has recommended {{ currentReviewer?.reviewerName }} 
                {{ currentReviewerFrequency }} times.
              </div>
            </div>

            <!-- History Table -->
            <div class="history-table-container">
              <table class="history-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Reviewer</th>
                    <th>Manuscript</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="rec in currentAuthorHistory" :key="rec.id" :class="{'current-row': rec.id === currentReviewer?.id}">
                    <td>{{ new Date(rec.recommendedAt).toLocaleDateString() }}</td>
                    <td>{{ rec.reviewerName }}</td>
                    <td class="truncate" :title="rec.manuscriptTitle">{{ rec.manuscriptTitle }}</td>
                    <td>
                      <span class="status-badge small" :class="getStatusClass(rec.status)" style="font-size: 10px; padding: 2px 6px;">
                        {{ getStatusText(rec.status) }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <div class="section">
            <h4>Review Comments / Notes</h4>
            <textarea 
              v-model="reviewComment" 
              rows="4" 
              placeholder="Enter review comments (optional)..."
              class="comment-input"
            ></textarea>
          </div>
        </div>
        
        <div class="modal-actions">
          <div class="left-actions">
             <button v-if="['pending', 'invited'].includes(currentReviewer?.status)" class="btn btn-warning" @click="handleMarkDeclined">Mark Declined</button>
             <button v-if="['pending', 'invited'].includes(currentReviewer?.status)" class="btn btn-grey" @click="handleMarkContactFailed">Mark Contact Failed</button>
          </div>
          <div class="right-actions">
            <button class="btn btn-grey" @click="showDetailModal = false">Cancel</button>
            <button class="btn btn-red" @click="handleReject">Reject</button>
            <button v-if="['pending'].includes(currentReviewer?.status)" class="btn btn-success" @click="openInviteModal(currentReviewer)">Invite</button>
            <button class="btn btn-primary" @click="handleAccept">Accept</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Invitation Modal -->
    <div v-if="showInviteModal" class="modal-overlay">
      <div class="modal-box large">
        <h3>Send Review Invitation</h3>
        <p class="modal-subtitle">Inviting: {{ currentReviewer?.reviewerName }} ({{ currentReviewer?.reviewerEmail }})</p>
        
        <div class="alert-box warning" v-if="true"> <!-- Mock double-blind check -->
           <span class="icon">🔒</span>
           <div style="margin-left: 10px;">
             <strong>Double-Blind Review:</strong> Author name has been anonymized in the template.
           </div>
        </div>

        <div class="form-group" style="margin-bottom: 15px;">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Email Subject</label>
          <input type="text" v-model="inviteForm.subject" class="search-input" style="width: 100%;">
        </div>
        
        <div class="form-group">
          <label style="display: block; font-weight: bold; margin-bottom: 5px;">Email Content</label>
          <textarea v-model="inviteForm.content" rows="12" class="comment-input"></textarea>
          <p class="hint" style="font-size: 12px; color: #666; margin-top: 5px;">
            Note: This email includes a unique registration link for the reviewer.
          </p>
        </div>
        
        <div class="modal-actions">
          <button class="btn btn-grey" @click="showInviteModal = false">Cancel</button>
          <button class="btn btn-primary" @click="sendInvitation">Send Invitation</button>
        </div>
      </div>
    </div>

    <!-- Evaluation Modal -->
    <div v-if="showEvalModal" class="modal-overlay">
      <div class="modal-box large">
        <h3>Evaluate Recommended Reviewer</h3>
        <p class="modal-subtitle">Reviewer: {{ currentReviewer?.reviewerName }} | Task: {{ currentReviewer?.manuscriptTitle }}</p>
        
        <div class="rating-grid">
          <div class="rating-item">
            <label>Timeliness</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.timeliness = n" :class="{active: n <= evalForm.timeliness}">★</span>
            </div>
            <span class="score-display">{{ evalForm.timeliness }}</span>
          </div>
          <div class="rating-item">
            <label>Professionalism</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.professionalism = n" :class="{active: n <= evalForm.professionalism}">★</span>
            </div>
             <span class="score-display">{{ evalForm.professionalism }}</span>
          </div>
          <div class="rating-item">
            <label>Standardization</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.standardization = n" :class="{active: n <= evalForm.standardization}">★</span>
            </div>
             <span class="score-display">{{ evalForm.standardization }}</span>
          </div>
          <div class="rating-item">
            <label>Objectivity</label>
            <div class="stars">
              <span v-for="n in 5" :key="n" @click="evalForm.objectivity = n" :class="{active: n <= evalForm.objectivity}">★</span>
            </div>
             <span class="score-display">{{ evalForm.objectivity }}</span>
          </div>
        </div>

        <div class="grade-preview">
          Calculated Grade: <span class="grade-badge" :class="calculatedGrade">{{ calculatedGrade }}</span>
        </div>

        <div class="form-group">
          <label>Evaluation Comment (Required, >10 chars)</label>
          <textarea v-model="evalForm.comment" rows="4" placeholder="Detailed feedback on the review quality..."></textarea>
        </div>

        <div class="modal-actions">
          <button class="btn btn-grey" @click="showEvalModal = false">Cancel</button>
          <button class="btn btn-primary" @click="submitEvaluation">Submit Evaluation</button>
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
  vertical-align: middle;
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

.risk-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
  color: white;
}
.risk-high { background: #D1202F; }
.risk-medium { background: #FFC107; color: #333; }
.risk-low { background: #28a745; }

.risk-detail {
  font-size: 11px;
  color: #D1202F;
  margin-top: 4px;
}

.score-box {
  font-weight: bold;
  color: #28a745;
}
.score-low {
  color: #D1202F;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  text-transform: uppercase;
}

.status-pending { background: #fff3cd; color: #856404; }
.status-accepted { background: #d4edda; color: #155724; }
.status-rejected { background: #f8d7da; color: #721c24; }
.status-invited { background: #d1ecf1; color: #0c5460; }
.status-completed { background: #e2e3e5; color: #383d41; }
.status-declined { background: #343a40; color: #fff; }
.status-failed { background: #e0a800; color: #fff; }
.status-withdrawn { background: #6c757d; color: #fff; }

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

.btn-primary { background: #1a365d; color: white; }
.btn-primary:hover { background: #2c5282; }
.btn-primary:disabled { background: #a0aec0; cursor: not-allowed; }

.btn-red { background: #D1202F; color: white; }
.btn-red:hover { background: #b01b27; }

.btn-grey { background: #e2e6ea; color: #333; }
.btn-eval { background: #FFC107; color: #333; }
.btn-eval:hover { background: #e0a800; }

.btn-warning { background: #e0a800; color: white; }
.btn-warning:hover { background: #d39e00; }

.btn-success { background: #28a745; color: white; }
.btn-success:hover { background: #218838; }

.eval-done {
  color: #28a745;
  font-weight: bold;
  font-size: 12px;
}

.btn-sm { padding: 4px 12px; font-size: 11px; }

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal-box.large {
  width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.section {
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}
.section h4 {
  margin-top: 0;
  color: #1a365d;
  font-size: 14px;
  text-transform: uppercase;
  border-left: 3px solid #D1202F;
  padding-left: 8px;
}

.risk-report {
  background: #fff3cd;
  padding: 10px;
  border-radius: 4px;
}
.text-high { color: #D1202F; font-weight: bold; }
.text-medium { color: #856404; font-weight: bold; }
.text-low { color: #28a745; font-weight: bold; }

.rating-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}
.rating-item label { display: block; font-weight: bold; margin-bottom: 5px; }
.stars { color: #CCC; font-size: 20px; cursor: pointer; display: inline-block; }
.stars span.active { color: #FFC107; }
.score-display { margin-left: 10px; font-weight: bold; }

.grade-preview { margin-bottom: 20px; font-weight: bold; }
.grade-badge { padding: 2px 8px; background: #EEE; border-radius: 4px; margin-left: 10px; }

textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #CCC;
  font-family: 'Times New Roman';
  resize: vertical;
}

.modal-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  margin-top: 20px;
}

.right-actions, .left-actions {
  display: flex;
  gap: 10px;
}

.no-data {
  text-align: center;
  padding: 40px;
  color: #777;
  background: #f8f9fa;
  border-radius: 8px;
}

.alert-box {
  padding: 10px 15px;
  border-radius: 6px;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.alert-box.warning {
  background-color: #fff3cd;
  border: 1px solid #ffeeba;
  color: #856404;
}

.history-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9em;
}

.history-table th, .history-table td {
  padding: 8px;
  border-bottom: 1px solid #eee;
  text-align: left;
}

.history-table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.current-row {
  background-color: #e8f4ff; /* Highlight current recommendation */
}

.truncate {
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-danger {
  color: #dc3545;
  font-weight: bold;
}

.bg-danger-light {
  background-color: #f8d7da;
  color: #721c24;
}

.bg-success-light {
  background-color: #d4edda;
  color: #155724;
}
</style>