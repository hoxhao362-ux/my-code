<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import Navigation from '../../components/Navigation.vue'
import ReviewForm from '../../components/ReviewForm.vue'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const messageStore = useMessageStore()
const toastStore = useToastStore()
const user = computed(() => userStore.user)

const journalId = route.params.id
const journal = computed(() => userStore.journals.find(j => String(j.id) === String(journalId)))

// Helper to calculate due date (simulated for now, 14 days from submission)
const getDueDate = (date) => {
  if (!date) return ''
  const d = new Date(date)
  if (isNaN(d.getTime())) return ''
  d.setDate(d.getDate() + 14)
  return d.toISOString().split('T')[0]
}

const isOverdue = computed(() => {
  if (!journal.value) return false
  const dueDateStr = getDueDate(journal.value.date)
  if (!dueDateStr) return false
  const dueDate = new Date(dueDateStr)
  if (isNaN(dueDate.getTime())) return false
  const today = new Date()
  return today > dueDate
})

const daysOverdue = computed(() => {
  if (!journal.value) return 0
  const dueDateStr = getDueDate(journal.value.date)
  if (!dueDateStr) return 0
  const dueDate = new Date(dueDateStr)
  if (isNaN(dueDate.getTime())) return 0
  const today = new Date()
  const diffTime = Math.abs(today - dueDate)
  return Math.floor(diffTime / (1000 * 60 * 60 * 24))
})

const isReadonly = computed(() => {
  if (!journal.value || !journal.value.reviewHistory) return false
  // For re-review, only check if user has reviewed in current Re-review stage
  // For normal review, check if user has any review
  if (isRevision.value) {
    return journal.value.reviewHistory.some(r => 
      r.reviewer === user.value.username && 
      (r.stage === 'Re-review' || r.stage === '复审')
    )
  }
  return journal.value.reviewHistory.some(r => r.reviewer === user.value.username)
})

const isCompletedView = computed(() => {
  return route.query.view === 'details'
})

const completedReviewData = computed(() => {
  if (!journal.value || !journal.value.reviewHistory) return []
  return journal.value.reviewHistory.filter(r => r.reviewer === user.value.username)
})

const completedStatus = computed(() => {
  // If user has any completed review, show completed status
  return completedReviewData.value.length > 0 ? 'Completed' : 'Pending'
})

const completedDate = computed(() => {
  if (completedReviewData.value.length === 0) return ''
  // Get the latest completion date
  const sorted = [...completedReviewData.value].sort((a, b) => new Date(b.date) - new Date(a.date))
  return sorted[0].date
})

const initialReviewData = computed(() => {
  if (!journal.value || !journal.value.reviewHistory) return null
  return journal.value.reviewHistory.find(r => r.reviewer === user.value.username && r.type !== 'Re-review')
})

// Check if this is a revision (Re-review)
const isRevision = computed(() => journal.value && (journal.value.reviewStage === '复审' || journal.value.reviewStage === 'Re-review'))

// Blind Review Logic
const isBlindReview = ref(true)

const displayContent = computed(() => {
  if (!journal.value || !journal.value.content) return ''
  let content = journal.value.content
  if (isBlindReview.value) {
    // Simple mock anonymization
    content = content.replace(/Author Name/g, '[Anonymized]')
    content = content.replace(/University of X/g, '[Anonymized Institution]')
  }
  return content
})

const activeTab = ref(route.query.tab || 'overview')

// Update active tab if query param changes
watch(() => route.query.tab, (newTab) => {
  if (newTab && tabs.value.some(t => t.id === newTab)) {
    activeTab.value = newTab
  }
})

const tabs = computed(() => {
  const baseTabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'manuscript', label: 'Manuscript' },
    // Add Revision Details tab if it is a revision
    ...(isRevision.value ? [{ id: 'revision-details', label: 'Revision Details' }] : []),
    { id: 'review-form', label: 'Review Form' },
    { id: 'coi', label: 'Conflict of Interest' },
    { id: 'messages', label: 'Messages' },
    { id: 'history', label: 'History' }
  ]
  return baseTabs
})

// COI State
const coiState = ref({
  hasConflict: 'no',
  declaration: ''
})

// Messages State
const newMessage = ref('')

// Find or create a thread for this manuscript
const currentThread = computed(() => {
  // Find a thread where manuscriptId matches
  // In a real app, we might need a more robust way to find the "Editor-Reviewer" thread for this specific manuscript
  return messageStore.myThreads.find(t => String(t.manuscriptId) === String(journalId))
})

const messages = computed(() => {
  if (!currentThread.value) return []
  return messageStore.messages.filter(m => m.threadId === currentThread.value.id).sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
})

const sendMessage = async () => {
  if (!newMessage.value.trim()) return
  
  try {
    if (currentThread.value) {
      await messageStore.sendMessage({
        threadId: currentThread.value.id,
        recipientId: currentThread.value.participants[0] === user.value.username ? null : 'editor_001', // Simplification
        recipientName: 'Editor', // Default to Editor
        recipientRole: 'editor',
        content: newMessage.value
      })
    } else {
      // Start new thread
      await messageStore.sendMessage({
        recipientId: 'editor_001', // Mock Editor ID
        recipientName: 'Editor',
        recipientRole: 'editor',
        subject: `Question regarding Manuscript #${journalId}`,
        content: newMessage.value,
        manuscriptId: journalId,
        manuscriptTitle: journal.value?.title || 'Unknown Manuscript'
      })
    }
    newMessage.value = ''
  } catch (e) {
    console.error('Failed to send message', e)
    toastStore.add({ message: 'Failed to send message', type: 'error' })
  }
}

const showSubmitModal = ref(false)
const pendingReviewData = ref(null)

// Review Submission
const handleReviewSubmit = (data) => {
  pendingReviewData.value = data
  showSubmitModal.value = true
}

const confirmSubmit = () => {
  if (!journal.value || !pendingReviewData.value) return
  
  const { ratings, comments, confidentialComments, decision, file } = pendingReviewData.value
  const today = new Date().toISOString().split('T')[0]
  const updatedJournal = { ...journal.value }
  
  if (!updatedJournal.reviewHistory) updatedJournal.reviewHistory = []
  
  // Create review record
  const reviewRecord = {
    stage: updatedJournal.reviewStage || 'Review',
    status: 'Completed',
    reviewer: user.value.username,
    date: today,
    comment: comments,
    confidentialComments: confidentialComments,
    ratings: ratings,
    decision: decision,
    type: isRevision.value ? 'Re-review' : 'Review',
    file: file ? file.name : null // Mock file storage
  }

  updatedJournal.reviewHistory.push(reviewRecord)
  
  // Update Global Status logic:
  // Only mark as 'review_completed' when all reviewers have completed their reviews
  // First, determine how many reviewers are assigned to this manuscript
  const uniqueReviewers = [...new Set(updatedJournal.reviewHistory.map(r => r.reviewer))]
  
  // Check if this manuscript has assigned reviewers information
  const totalAssignedReviewers = updatedJournal.assignedReviewers ? updatedJournal.assignedReviewers.length : 1
  
  // If no assigned reviewers information, assume single reviewer setup
  // Mark as review_completed when:
  //1. There are assigned reviewers and all have completed (uniqueReviewers.length >= totalAssignedReviewers)
  //2. No assigned reviewers information and at least one reviewer has completed
  if (updatedJournal.assignedReviewers) {
    if (uniqueReviewers.length >= totalAssignedReviewers) {
      // All assigned reviewers have completed
      updatedJournal.status = MANUSCRIPT_STATUS.REVIEW_COMPLETED
    } else {
      // Still waiting for other reviewers
      updatedJournal.status = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW
    }
  } else {
    // Single reviewer setup or no assigned reviewers info
    // Mark as completed once any reviewer submits
    updatedJournal.status = MANUSCRIPT_STATUS.REVIEW_COMPLETED
  }

  userStore.updateJournal(updatedJournal)
  showSubmitModal.value = false
  
  // Clear any draft
  localStorage.removeItem(`review_draft_${journal.value.id}`)

  router.push('/reviewer/assignments?filter=completed')
}

const submitCOI = () => {
  toastStore.add({ message: 'Conflict of Interest declaration submitted.', type: 'success' })
}

const downloadFile = (file) => {
  const link = document.createElement('a')
  link.href = file.url || '#'
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Mock Author Response for Revision
const authorResponse = ref(`
Thank you for your valuable comments. We have revised the manuscript accordingly.
1. Addressed the concern about sample size by adding 50 more participants.
2. Clarified the methodology section as requested.
3. Updated Figure 3 to show higher resolution data.
`)

</script>

<template>
  <div class="manuscript-detail-container">
    <Navigation :user="user" current-page="reviewer-detail" />
    
    <main class="content" v-if="journal">
      <!-- Completed Review Details View -->
      <div v-if="isCompletedView" class="review-details-view">
        <div class="page-header">
          <h1>Review Details</h1>
        </div>

        <!-- 1. Manuscript Info -->
        <section class="info-card">
          <div class="info-grid compact">
             <div class="info-row">
               <span class="label">Manuscript ID:</span>
               <span class="value">{{ journal.id }}</span>
             </div>
             <div class="info-row">
               <span class="label">Title:</span>
               <span class="value">{{ journal.title }}</span>
             </div>
             <div class="info-row">
               <span class="label">Type:</span>
               <span class="value">{{ journal.module || 'Research Article' }}</span>
             </div>
             <div class="info-row">
               <span class="label">Submission Date:</span>
               <span class="value">{{ journal.submissionDate || journal.date }}</span>
             </div>
             <div class="info-row">
               <span class="label">Due Date:</span>
               <span class="value">{{ getDueDate(journal.date) }}</span>
             </div>
             <div class="info-row">
               <span class="label">Status:</span>
               <span class="status-badge-completed">Completed</span>
             </div>
             <div class="info-row">
               <span class="label">Completed On:</span>
               <span class="value">{{ completedDate }}</span>
             </div>
          </div>
        </section>

        <!-- 2. Original Review -->
        <div v-for="(review, index) in completedReviewData" :key="index">
          <section class="info-card review-card">
            <h3>{{ review.type === 'Re-review' ? `Revision Review (Round ${index})` : 'Original Review' }}</h3>
            
            <div class="scorecard">
               <h4>Scorecard</h4>
               <div v-for="(score, dim) in review.ratings" :key="dim" class="score-row">
                 <span class="dim-label">{{ dim }}</span>
                 <span class="dim-score">{{ score }}</span>
                 <span class="dim-stars">
                   {{ score === 'Excellent' ? '★★★★★' : score === 'Good' ? '★★★★☆' : score === 'Fair' ? '★★★☆☆' : '★★☆☆☆' }}
                 </span>
               </div>
            </div>

            <div class="comments-block">
              <h4>Confidential Comments to Editor</h4>
              <div class="readonly-text">{{ review.confidentialComments || 'No confidential comments provided.' }}</div>
            </div>

            <div class="comments-block">
              <h4>Comments to Author</h4>
              <div class="readonly-text">{{ review.comment || 'No comments provided.' }}</div>
            </div>

            <div class="recommendation-block">
              <span class="rec-label">Recommendation:</span>
              <span class="rec-value">{{ review.decision }}</span>
            </div>
             
             <div class="timestamp-footer">
               Review Completed On: {{ review.date }}
             </div>
          </section>
        </div>

        <!-- 4. Bottom Action -->
        <div class="bottom-actions">
          <button class="btn-back-gray" @click="router.push('/reviewer/assignments?filter=completed')">Back to Completed Reviews</button>
        </div>

      </div>

      <!-- Standard Tab View -->
      <div v-else>
        <div v-if="isOverdue && !isReadonly" class="overdue-alert">
          This {{ isRevision ? 're-review' : 'review' }} is overdue by {{ daysOverdue }} days. Please complete it as soon as possible.
        </div>
        <div class="page-header">
          <button class="back-btn" @click="router.back()">← Back</button>
          <div class="header-info">
            <h1>{{ journal.title }}</h1>
            <span class="manuscript-id">ID: {{ journal.id }}</span>
            <span v-if="isRevision" class="revision-badge">Revision (Re-review)</span>
            <span v-if="isBlindReview" class="blind-badge">Blind Review - Author Information Removed</span>
          </div>
        </div>

        <!-- Tabs -->
        <div class="tabs-header">
          <button 
            v-for="tab in tabs" 
          :key="tab.id" 
          class="tab-btn" 
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content">
        
        <!-- Overview -->
        <div v-if="activeTab === 'overview'" class="tab-pane">
          <section class="info-section">
            <h3>Basic Information</h3>
            <div class="info-grid">
              <!-- Author Hidden for Blind Review -->
              <div class="info-item" v-if="!isBlindReview">
                <label>Author:</label>
                <span>{{ journal.author }}</span>
              </div>
              <div class="info-item">
                <label>Title:</label>
                <span>{{ journal.title }}</span>
              </div>
              <div class="info-item">
                <label>Abstract:</label>
                <p v-if="journal.abstract && journal.abstract.trim()" class="abstract-text content-text">{{ journal.abstract }}</p>
                <p v-else class="abstract-text placeholder-text">Author's abstract will be displayed here once the manuscript is submitted successfully.</p>
              </div>
              <div class="info-item">
                <label>Keywords:</label>
                <span>{{ journal.keywords ? (Array.isArray(journal.keywords) ? journal.keywords.join(', ') : journal.keywords) : '' }}</span>
              </div>
              <div class="info-item">
                <label>Submission Date:</label>
                <span>{{ journal.date }}</span>
              </div>
              <div class="info-item">
                <label>Current Status:</label>
                <span class="status-badge">{{ journal.status }}</span>
              </div>
            </div>
          </section>
        </div>

        <!-- Manuscript -->
        <div v-if="activeTab === 'manuscript'" class="tab-pane">
          <section class="files-section">
            <h3>Manuscript Files</h3>
            <div v-if="journal.attachments && journal.attachments.length">
              <div v-for="file in journal.attachments" :key="file.name" class="file-item">
                <div class="file-info">
                  <span class="file-icon">📄</span>
                  <span class="file-name">{{ file.name }}</span>
                  <span class="file-size">({{ (file.size / 1024).toFixed(1) }} KB)</span>
                </div>
                <div class="file-actions">
                  <button class="btn-primary" @click="downloadFile(file)">Download</button>
                </div>
              </div>
            </div>
            <div v-else class="no-data">
              <!-- Mock File if none exists -->
               <div class="file-item">
                <div class="file-info">
                  <span class="file-icon">📄</span>
                  <span class="file-name">Main_Manuscript.pdf</span>
                  <span class="file-size">(2.5 MB)</span>
                </div>
                <div class="file-actions">
                  <button class="btn-primary">Download</button>
                </div>
              </div>
            </div>
          </section>

          <section class="content-preview">
             <h3>Online Reading</h3>
             <div class="blind-notice" v-if="isBlindReview">
               This is a blind review - author information has been anonymized. Self-citations are marked as 'Author et al.'
             </div>
             <div class="paper-content" v-if="displayContent" v-html="displayContent"></div>
             <div class="paper-content placeholder" v-else>
               <p>PDF Preview is not available for this mock data.</p>
             </div>
          </section>
        </div>

        <!-- Revision Details (Only for Revision) -->
        <div v-if="activeTab === 'revision-details'" class="tab-pane">
          <section class="response-section">
            <h3>Author's Response to Previous Review</h3>
            <div class="response-box">
              <pre>{{ authorResponse }}</pre>
            </div>
          </section>
          
          <section class="diff-section">
            <h3>Changes Highlight (Mock Diff)</h3>
            <div class="diff-view">
              <p>... previous text <span class="removed">sample size was small</span> <span class="added">sample size was increased to 150 participants</span> ...</p>
              <p>... methodology was <span class="added">clarified using the double-blind protocol</span> ...</p>
            </div>
          </section>
        </div>

        <!-- Review Form -->
        <div v-if="activeTab === 'review-form'" class="tab-pane">
          <ReviewForm 
            :journal="journal" 
            :readonly="isReadonly"
            :initialData="initialReviewData"
            :isRevision="isRevision"
            @submit="handleReviewSubmit" 
            @cancel="router.back()" 
          />
        </div>

        <!-- Conflict of Interest -->
        <div v-if="activeTab === 'coi'" class="tab-pane">
          <div class="coi-form">
            <h3>Conflict of Interest Declaration</h3>
            <p class="instruction">Please declare if you have any conflict of interest regarding this manuscript.</p>
            
            <div class="radio-group">
              <label>
                <input type="radio" v-model="coiState.hasConflict" value="no">
                I have no conflict of interest.
              </label>
              <label>
                <input type="radio" v-model="coiState.hasConflict" value="yes">
                I have a conflict of interest (please specify below).
              </label>
            </div>

            <textarea 
              v-if="coiState.hasConflict === 'yes'"
              v-model="coiState.declaration"
              placeholder="Please describe the nature of the conflict..."
              rows="4"
            ></textarea>

            <button class="btn-primary" @click="submitCOI">Submit Declaration</button>
          </div>
        </div>

        <!-- Messages -->
        <div v-if="activeTab === 'messages'" class="tab-pane">
          <div class="messages-container">
            <div class="message-list">
              <div 
                v-for="msg in messages" 
                :key="msg.id" 
                class="message-bubble"
                :class="{ 'sent': msg.senderName === user.username, 'received': msg.senderName !== user.username }"
              >
                <div class="msg-header">
                  <span class="sender">{{ msg.senderName }}</span>
                  <span class="date">{{ new Date(msg.createdAt).toLocaleString() }}</span>
                </div>
                <div class="msg-body" v-html="msg.content"></div>
              </div>
            </div>
            <div class="message-input">
              <textarea v-model="newMessage" placeholder="Type a message to the editor..."></textarea>
              <button class="btn-primary" @click="sendMessage">Send</button>
            </div>
            <div v-if="messages.length === 0" class="no-messages">
              No messages yet. Start a conversation with the editor.
            </div>
          </div>
        </div>

        <!-- History -->
        <div v-if="activeTab === 'history'" class="tab-pane">
          <div class="history-list">
             <div v-if="!journal.reviewHistory || journal.reviewHistory.length === 0" class="no-data">
               No history recorded.
             </div>
             <div v-else v-for="(rec, idx) in journal.reviewHistory" :key="idx" class="history-item">
               <div class="history-date">{{ rec.date }}</div>
               <div class="history-content">
                 <!-- Reviewer Record -->
                 <template v-if="rec.reviewer">
                   <strong>{{ rec.stage }} - {{ rec.status }}</strong>
                   <p v-if="rec.comment" class="history-comment">{{ rec.comment }}</p>
                   <div v-if="rec.decision" class="decision-tag">Decision: {{ rec.decision }}</div>
                   <div v-if="rec.ratings" class="ratings-block">
                     <div v-for="(score, dim) in rec.ratings" :key="dim" class="rating-item">
                       <span class="dim-label">{{ dim }}:</span>
                       <span class="dim-score">{{ score }}</span>
                     </div>
                   </div>
                   <div v-if="rec.file" class="file-tag">📎 {{ rec.file }}</div>
                 </template>
                 <!-- Editor Record -->
                 <template v-else-if="rec.actor">
                   <strong>{{ rec.actor }}</strong>
                   <span class="action-tag">{{ rec.action }}</span>
                   <p v-if="rec.comment" class="history-comment">{{ rec.comment }}</p>
                 </template>
                 <!-- Legacy Record -->
                 <template v-else>
                   <strong>{{ rec.stage || 'Review' }} - {{ rec.status }}</strong>
                   <p v-if="rec.comment" class="history-comment">{{ rec.comment }}</p>
                   <div v-if="rec.decision" class="decision-tag">Decision: {{ rec.decision }}</div>
                 </template>
               </div>
             </div>
          </div>
        </div>

      </div>
      </div>
    </main>

    <div v-else class="loading-state">
      Loading...
    </div>

    <!-- Submit Confirmation Modal -->
    <div v-if="showSubmitModal" class="modal-overlay" @click="showSubmitModal = false">
      <div class="modal-content" @click.stop>
        <h3>Confirm Review Submission</h3>
        <p>Are you sure you want to submit this review? This action cannot be undone.</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showSubmitModal = false">Cancel</button>
          <button class="btn-confirm" @click="confirmSubmit">Confirm Submit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
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
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
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
.manuscript-detail-container {
  min-height: 100vh;
  background: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.content {
  max-width: 1200px;
  margin: 100px auto 0;
  padding: 2rem;
  width: 100%;
}

.overdue-alert {
  background-color: #C93737;
  color: white;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-weight: 500;
  display: flex;
  align-items: center;
}

.overdue-alert::before {
  content: '⚠️';
  margin-right: 0.5rem;
  filter: brightness(0) invert(1); /* Make emoji white */
}

.page-header {
  margin-bottom: 1.5rem;
}

.back-btn {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  font-size: 1rem;
  margin-bottom: 0.5rem;
  padding: 0;
}

.back-btn:hover { text-decoration: underline; }

.header-info h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}

.manuscript-id {
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-right: 10px;
}

.revision-badge {
  background: #e67e22;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  vertical-align: middle;
}

.blind-badge {
  border: 1px solid #C93737;
  color: #C93737;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  vertical-align: middle;
  margin-left: 10px;
  font-weight: 600;
}

.blind-notice {
  background: #fff5f5;
  color: #C93737;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  border: 1px dashed #C93737;
}

/* Tabs */
.tabs-header {
  display: flex;
  border-bottom: 2px solid #ddd;
  margin-bottom: 2rem;
  overflow-x: auto;
}

.tab-btn {
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -2px;
  cursor: pointer;
  font-weight: 500;
  color: #666;
  white-space: nowrap;
}

.tab-btn.active {
  color: #C93737;
  border-bottom-color: #C93737;
}

.tab-btn:hover:not(.active) {
  color: #C93737;
}

/* Tab Content */
.tab-pane {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.info-section h3, .files-section h3, .content-preview h3, .response-section h3, .diff-section h3 {
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.info-grid {
  display: grid;
  gap: 1.5rem;
}

.info-item label {
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
  color: #555;
}

.abstract-text {
  line-height: 1.6;
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

.status-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

/* Files */
.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 0.5rem;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.file-name { font-weight: 500; }
.file-size { color: #999; font-size: 0.9rem; }

.btn-primary {
  background: #C93737;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-primary:hover { background: #a92e2e; }

/* COI */
.coi-form {
  max-width: 600px;
}

.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin: 1rem 0;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.coi-form textarea {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 1rem;
}

/* Messages */
.messages-container {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background: #f9f9f9;
  border-radius: 6px;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.message-bubble {
  max-width: 70%;
  padding: 1rem;
  border-radius: 12px;
}

.message-bubble.sent {
  align-self: flex-end;
  background: #C93737;
  color: white;
}

.message-bubble.received {
  align-self: flex-start;
  background: white;
  border: 1px solid #eee;
}

.msg-header {
  font-size: 0.8rem;
  margin-bottom: 0.25rem;
  opacity: 0.8;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.message-input {
  display: flex;
  gap: 1rem;
}

.message-input textarea {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: none;
  height: 60px;
}

/* History */
.history-item {
  display: flex;
  gap: 2rem;
  padding: 1rem 0;
  border-bottom: 1px solid #eee;
}

.history-date {
  color: #999;
  font-size: 0.9rem;
  width: 100px;
}

.history-content strong {
  display: block;
  margin-bottom: 0.25rem;
}

.decision-tag {
  display: inline-block;
  background: #f1c40f;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.file-tag {
  color: #27ae60;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.action-tag {
  display: inline-block;
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

.history-comment {
  margin: 0.5rem 0;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 4px;
  border-left: 3px solid #3498db;
  white-space: pre-wrap;
  line-height: 1.5;
}

.ratings-block {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f0f8ff;
  border-radius: 4px;
}

.rating-item {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  border-bottom: 1px dashed #ddd;
}

.rating-item:last-child {
  border-bottom: none;
}

.dim-label {
  font-weight: 500;
  color: #666;
}

.dim-score {
  font-weight: 600;
  color: #2c3e50;
}

.no-data {
  color: #999;
  text-align: center;
  padding: 2rem;
}

/* Revision Details */
.response-box {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  border: 1px solid #eee;
  margin-bottom: 2rem;
}

.response-box pre {
  white-space: pre-wrap;
  font-family: inherit;
  color: #333;
}

.diff-view {
  background: white;
  padding: 1rem;
  border: 1px solid #eee;
  border-radius: 6px;
  font-family: monospace;
}

.removed {
  background-color: #ffebee;
  text-decoration: line-through;
  color: #c62828;
}

.added {
  background-color: #e8f5e9;
  color: #2e7d32;
}

/* Review Details View Styles */
.review-details-view {
  max-width: 900px;
  margin: 0 auto;
}

.info-grid.compact {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.info-row {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
}

.label {
  font-weight: 600;
  color: #666;
  min-width: 120px;
}

.value {
  color: #333;
}

.status-badge-completed {
  background: #28A745;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.review-card {
  margin-top: 1.5rem;
}

.scorecard {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.score-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px dashed #eee;
}

.dim-label {
  font-weight: 500;
  flex: 1;
}

.dim-score {
  width: 100px;
  text-align: right;
  font-weight: bold;
}

.dim-stars {
  width: 100px;
  text-align: right;
  color: #f1c40f;
}

.comments-block {
  margin-bottom: 1.5rem;
}

.comments-block h4 {
  margin-bottom: 0.5rem;
  color: #666;
  font-size: 0.95rem;
}

.readonly-text {
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
  border: 1px solid #eee;
  white-space: pre-wrap;
  color: #333;
}

.recommendation-block {
  margin-top: 1rem;
  padding: 1rem;
  background: #e8f5e9;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rec-label {
  font-weight: 600;
  color: #2e7d32;
}

.rec-value {
  font-weight: bold;
  color: #2e7d32;
  font-size: 1.1rem;
}

.timestamp-footer {
  margin-top: 1rem;
  text-align: right;
  color: #999;
  font-size: 0.85rem;
}

.bottom-actions {
  margin-top: 2rem;
  text-align: center;
}

.btn-back-gray {
  background: #999999;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.btn-back-gray:hover {
  background: #808080;
}
</style>