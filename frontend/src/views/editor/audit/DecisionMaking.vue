<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// --- Lancet Style: Tabs for Decision Central ---
const activeTab = ref('consolidation') // consolidation | consensus | appeals

// --- Filter Logic ---
// 1. Consolidation Queue: Manuscripts ready for decision
const decisionJournals = computed(() => {
  if (!user.value) return []
  return userStore.journals.filter(journal => {
    const isStatusReady = journal.status === 'review_completed' || journal.status === 'Reviews Completed'
    const isAssignedToMe = !journal.assignedEditor || journal.assignedEditor === user.value.username
    // Exclude those already in meeting or appeal
    const isInMeeting = journal.decisionStage === 'consensus_meeting'
    const isAppeal = journal.isAppeal
    return isStatusReady && isAssignedToMe && !isInMeeting && !isAppeal
  })
})

// Filter for pending final decision journals (only accessible by editors)
const pendingFinalDecisionJournals = computed(() => {
  if (!user.value || !['editor', 'admin'].includes(user.value.role)) return []
  return userStore.journals.filter(journal => {
    const isPendingFinalDecision = journal.status === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION
    const isAssignedToMe = !journal.assignedEditor || journal.assignedEditor === user.value.username
    return isPendingFinalDecision && isAssignedToMe
  })
})

// Combined list for display
const allDecisionJournals = computed(() => {
  return [...decisionJournals.value, ...pendingFinalDecisionJournals.value]
})

// 2. Consensus Meeting Queue: Manuscripts requiring discussion
const consensusJournals = computed(() => {
  if (!user.value) return []
  // Mock: Filter by a custom property or simulate based on ID
  return userStore.journals.filter(journal => 
    journal.decisionStage === 'consensus_meeting' || 
    (journal.status === 'review_completed' && journal.reviews && journal.reviews.some(r => r.rating < 2) && journal.reviews.some(r => r.rating > 4)) // High variance triggers meeting
  )
})

// 3. Appeals Queue: Rejected manuscripts appealing
const appealJournals = computed(() => {
  if (!user.value) return []
  return userStore.journals.filter(journal => 
    journal.status === 'appeal_submitted' || 
    (journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED && journal.appealRequested)
  )
})

// --- Modal State ---
const showModal = ref(false)
const currentJournal = ref(null)
const decisionType = ref('')
const decisionComments = ref('')

// Lancet: Structured Decision Rationale
const decisionRationale = ref({
  scientificRigor: '',
  novelty: '',
  methodology: '',
  dataIntegrity: '',
  ethicalCompliance: ''
})

// Lancet: Consensus Meeting Data
const meetingAgenda = ref({
  date: new Date().toISOString().slice(0, 16),
  attendees: ['Editor-in-Chief', 'Senior Editor', 'Statistician'],
  notes: ''
})

const openDecisionModal = (journal) => {
  // Permission check: only editor or admin can handle pending final decision manuscripts
  if (journal.status === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION && !['editor', 'admin'].includes(user.value?.role)) {
    alert('Only editors can handle manuscripts pending final decision.')
    return
  }
  
  currentJournal.value = journal
  decisionType.value = 'Minor Revision' // default
  decisionComments.value = ''
  // Reset Rationale
  decisionRationale.value = {
    scientificRigor: 'The study design is robust with appropriate controls.',
    novelty: 'Findings contribute significantly to current understanding.',
    methodology: 'Methods are described in sufficient detail.',
    dataIntegrity: 'Data appears consistent; source data verified.',
    ethicalCompliance: 'IRB approval confirmed.'
  }
  showModal.value = true
}

// --- Auto-Consolidation (Lancet Feature) ---
const autoConsolidateReviews = (journal) => {
  // Simulate AI/System extraction of key points
  const reviews = journal.reviewHistory || journal.reviews || []
  const summary = reviews.map(r => `[${r.reviewer || 'Reviewer'}]: ${r.comment ? r.comment.substring(0, 50) + '...' : 'No comment'}`).join('\n')
  return summary
}

const submitDecision = () => {
  if (!decisionComments.value) {
    alert('Please enter decision comments.')
    return
  }
  
  const journal = { ...currentJournal.value }
  let newStatus = ''
  
  // Standard Decision Types
  if (decisionType.value === 'Accept') {
    // Check current status for special handling
    if (journal.status === 'review_completed' || journal.status === 'Reviews Completed') {
      // If in completed status, move to pending final decision for editor-in-chief
      newStatus = MANUSCRIPT_STATUS.PENDING_FINAL_DECISION
      journal.reviewStage = '待终审'
    } else if (journal.status === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION || journal.status === MANUSCRIPT_STATUS.UNDER_FINAL_DECISION) {
      // If already in final decision stage, move to production process
      newStatus = MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION
      journal.reviewStage = '生产流程'
    } else {
      // Default case: move to production process
      newStatus = MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION
      journal.reviewStage = '生产流程'
    }
  } else if (decisionType.value === 'Reject') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  } else if (decisionType.value === 'Minor Revision' || decisionType.value === 'Major Revision') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REVISION
  } else if (decisionType.value === 'Return to Reviewer') {
    // New Option: Return to Reviewer (Directly restart review process)
    newStatus = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW // or 'under_peer_review'
  } else if (decisionType.value === 'Transfer') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  } else if (decisionType.value === 'Consensus Meeting') {
    // Move to Meeting Queue
    journal.decisionStage = 'consensus_meeting'
    userStore.updateJournal(journal)
    showModal.value = false
    alert('Manuscript moved to Consensus Meeting queue.')
    return
  }
  
  journal.status = newStatus
  
  // Save Structured Decision
  journal.decision = {
    type: decisionType.value,
    comments: decisionComments.value,
    rationale: { ...decisionRationale.value },
    date: new Date().toISOString()
  }
  
  userStore.updateJournal(journal)
  
  // Save Draft
  const draft = {
    manuscriptId: journal.id,
    manuscriptTitle: journal.title,
    content: decisionComments.value,
    templateType: decisionType.value,
    status: 'Draft',
    author: journal.writer || journal.author,
    rationale: decisionRationale.value // Save structured rationale
  }
  userStore.saveDecisionDraft(draft)
  
  showModal.value = false
  
  // Show different messages based on status transition
  if (newStatus === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION) {
    alert(`Decision recorded: ${decisionType.value}. \nManuscript sent to Editor-in-Chief for final decision.`)
  } else if (newStatus === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED) {
    alert(`Decision recorded: ${decisionType.value}. \nDraft letter generated in 'Decisions & Letters' module.`)
  } else {
    alert(`Decision recorded: ${decisionType.value}. \nDraft letter generated in 'Decisions & Letters' module.`)
  }
}

// --- Meeting Functions ---
const scheduleMeeting = (journal) => {
  alert(`Meeting scheduled for ${journal.title}. Notification sent to attendees.`)
}

const finalizeMeetingDecision = (journal) => {
  openDecisionModal(journal) // Open decision modal to finalize
}

// --- Appeal Functions ---
const assignIndependentReviewer = (journal) => {
  alert(`Independent reviewer assigned for appeal of ${journal.title}.`)
  // Logic to change status or assign reviewer
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-decision-making" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>Decision Central</h1>
        <p class="subtitle">Lancet-Style Evidence-Based Decision Making System</p>
      </div>

      <!-- Tab Navigation -->
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'consolidation' }]" 
          @click="activeTab = 'consolidation'"
        >
          Review Consolidation ({{ decisionJournals.length }})
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'consensus' }]" 
          @click="activeTab = 'consensus'"
        >
          Consensus Meetings ({{ consensusJournals.length }})
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'appeals' }]" 
          @click="activeTab = 'appeals'"
        >
          Appeals & Rebuttals ({{ appealJournals.length }})
        </button>
      </div>

      <!-- Tab 1: Review Consolidation -->
      <div v-if="activeTab === 'consolidation'" class="tab-pane">
        <div v-if="allDecisionJournals.length === 0" class="no-data">
          No manuscripts pending consolidation.
        </div>
        <div v-for="journal in allDecisionJournals" :key="journal.id" class="journal-item">
          <div class="journal-header">
             <div class="header-left">
               <h3 class="journal-title">{{ journal.title }}</h3>
               <span class="ms-id">ID: {{ journal.id }}</span>
             </div>
             <span class="status-badge">{{ journal.status }}</span>
          </div>
          
          <div class="consolidation-grid">
            <!-- Left: Reviews -->
            <div class="reviews-column">
              <h4>Reviewer Opinions</h4>
              <div v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
                 <div v-for="(review, idx) in journal.reviewHistory" :key="'h-'+idx" class="review-card">
                   <div class="review-meta">
                     <strong>Reviewer {{ idx + 1 }}</strong>
                     <span :class="['decision-tag', review.decision?.toLowerCase()]">{{ review.decision || 'N/A' }}</span>
                   </div>
                   <p class="review-text">{{ review.comment }}</p>
                   <div class="review-score" v-if="review.score">Score: {{ review.score }}/10</div>
                 </div>
              </div>
              <div v-else class="no-reviews">No reviews data available.</div>
            </div>

            <!-- Right: Editor Consolidation -->
            <div class="editor-column">
              <h4>Editor's Assessment</h4>
              <div class="assessment-box">
                <div class="auto-summary">
                  <span class="ai-badge">System Analysis</span>
                  <p><strong>Consensus Level:</strong> {{ (journal.reviews && journal.reviews.length > 1) ? 'Mixed' : 'High' }}</p>
                  <p><strong>Key Issues:</strong> Methodology, Sample Size (Detected)</p>
                </div>
                <button class="btn btn-outline" @click="openDecisionModal(journal)">Draft Decision & Rationale</button>
                <button class="btn btn-text" @click="decisionType.value = 'Consensus Meeting'; submitDecision()">Request Consensus Meeting</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: Consensus Meetings -->
      <div v-if="activeTab === 'consensus'" class="tab-pane">
        <div class="meeting-toolbar">
           <button class="btn btn-primary">Schedule New Meeting</button>
           <span class="meeting-info">Next Meeting: Tomorrow, 10:00 AM (EST)</span>
        </div>
        
        <div v-if="consensusJournals.length === 0" class="no-data">
          No manuscripts scheduled for consensus meeting.
        </div>
        
        <div v-for="journal in consensusJournals" :key="journal.id" class="journal-item meeting-item">
           <div class="meeting-card">
             <div class="meeting-header">
               <h3>{{ journal.title }}</h3>
               <span class="priority-tag">High Priority</span>
             </div>
             <p class="reason"><strong>Reason for Meeting:</strong> Conflicting reviewer recommendations (Accept vs Reject).</p>
             
             <div class="meeting-actions">
               <button class="btn btn-success" @click="finalizeMeetingDecision(journal)">Finalize Decision</button>
               <button class="btn btn-secondary">View Minutes</button>
             </div>
           </div>
        </div>
      </div>

      <!-- Tab 3: Appeals -->
      <div v-if="activeTab === 'appeals'" class="tab-pane">
        <div v-if="appealJournals.length === 0" class="no-data">
          No active appeals.
        </div>
        <div v-for="journal in appealJournals" :key="journal.id" class="journal-item">
          <h3>{{ journal.title }}</h3>
          <p><strong>Appeal Reason:</strong> Author claims reviewer 2 misunderstood the statistical model.</p>
          <button class="btn btn-primary" @click="assignIndependentReviewer(journal)">Assign Independent Reviewer</button>
        </div>
      </div>

    </main>

    <!-- Detailed Decision Modal (Lancet Style) -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content large-modal">
        <div class="modal-header">
          <h2>Final Decision: {{ currentJournal.title }}</h2>
          <button class="close-btn" @click="showModal = false">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="decision-form">
            <!-- Section 1: Decision Type -->
            <div class="form-section">
              <h3>1. Decision</h3>
              <select v-model="decisionType" class="form-control decision-select">
                <option value="Accept">Accept (Publish without further changes)</option>
                <option value="Minor Revision">Minor Revision (Back to Author - Editor Check Only)</option>
                <option value="Major Revision">Major Revision (Back to Author - Re-review Required)</option>
                <option value="Return to Reviewer">Return to Reviewer (Special Case: Direct Re-review)</option>
                <option value="Reject">Reject (Decline Submission)</option>
                <option value="Transfer">Transfer (Recommend Other Journals)</option>
                <option value="Consensus Meeting">Escalate to Consensus Meeting</option>
              </select>
              <div v-if="decisionType === 'Return to Reviewer'" class="alert-box warning">
                <small><strong>Note:</strong> This option bypasses the author and sends the manuscript directly back to reviewers. Use only for arbitration or internal re-evaluation.</small>
              </div>
            </div>

            <!-- Section 2: Structured Rationale (Lancet Requirement) -->
            <div class="form-section">
              <h3>2. Evidence-Based Rationale</h3>
              <div class="rationale-grid">
                <div class="rationale-item">
                  <label>Scientific Rigor</label>
                  <textarea v-model="decisionRationale.scientificRigor" placeholder="Comment on study design and controls..."></textarea>
                </div>
                <div class="rationale-item">
                  <label>Novelty & Innovation</label>
                  <textarea v-model="decisionRationale.novelty" placeholder="Comment on contribution to the field..."></textarea>
                </div>
                <div class="rationale-item">
                  <label>Methodology</label>
                  <textarea v-model="decisionRationale.methodology" placeholder="Comment on methods..."></textarea>
                </div>
                <div class="rationale-item">
                  <label>Data Integrity</label>
                  <textarea v-model="decisionRationale.dataIntegrity" placeholder="Comment on data quality..."></textarea>
                </div>
              </div>
            </div>

            <!-- Section 3: Decision Letter -->
            <div class="form-section">
              <h3>3. Decision Letter to Author</h3>
              <textarea v-model="decisionComments" rows="6" class="form-control" placeholder="Draft your letter here. The structured rationale above will be attached for internal records."></textarea>
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="submitDecision">Confirm Decision</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-container { min-height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.content { flex: 1; max-width: 1400px; margin: 60px auto 0; padding: 2rem; width: 100%; }
.header { margin-bottom: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem; }
.header h1 { font-size: 2rem; color: #2c3e50; margin: 0; font-family: 'Georgia', serif; }
.subtitle { color: #7f8c8d; margin-top: 0.5rem; font-style: italic; }

/* Tabs */
.tabs { display: flex; gap: 1rem; margin-bottom: 2rem; border-bottom: 2px solid #e0e0e0; }
.tab-btn {
  padding: 1rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 1.1rem;
  color: #666;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s;
}
.tab-btn:hover { color: #3498db; }
.tab-btn.active { color: #3498db; border-bottom-color: #3498db; font-weight: bold; }

/* Journal Item */
.journal-item { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border-left: 5px solid #3498db; }
.journal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1.5rem; border-bottom: 1px solid #eee; padding-bottom: 1rem; }
.journal-title { margin: 0; color: #2c3e50; font-size: 1.3rem; }
.ms-id { font-size: 0.9rem; color: #999; margin-left: 10px; }
.status-badge { background: #e3f2fd; color: #1976d2; padding: 4px 12px; border-radius: 12px; font-size: 0.85rem; font-weight: 600; }

/* Consolidation Grid */
.consolidation-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; }
.reviews-column, .editor-column { background: #f9f9f9; padding: 1.5rem; border-radius: 8px; }
h4 { margin-top: 0; color: #444; border-bottom: 2px solid #ddd; padding-bottom: 0.5rem; margin-bottom: 1rem; }

.review-card { background: white; padding: 1rem; margin-bottom: 1rem; border-radius: 6px; border: 1px solid #eee; }
.review-meta { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem; color: #555; }
.decision-tag { font-weight: bold; text-transform: uppercase; font-size: 0.8rem; }
.decision-tag.accept { color: #27ae60; }
.decision-tag.reject { color: #c0392b; }
.review-text { font-size: 0.95rem; color: #333; line-height: 1.5; margin: 0; }

.assessment-box { display: flex; flex-direction: column; gap: 1rem; }
.auto-summary { background: #e8f4fc; padding: 1rem; border-radius: 6px; border: 1px solid #b3d7ff; }
.ai-badge { background: #3498db; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.7rem; text-transform: uppercase; margin-bottom: 0.5rem; display: inline-block; }

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.6); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; padding: 0; border-radius: 8px; display: flex; flex-direction: column; max-height: 90vh; }
.large-modal { width: 900px; }
.modal-header { padding: 1.5rem; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; background: #f8f9fa; border-radius: 8px 8px 0 0; }
.modal-body { padding: 2rem; overflow-y: auto; }
.modal-footer { padding: 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; background: #f8f9fa; border-radius: 0 0 8px 8px; }

.form-section { margin-bottom: 2rem; }
.form-section h3 { font-size: 1.1rem; color: #2c3e50; margin-bottom: 1rem; border-left: 4px solid #3498db; padding-left: 10px; }

.rationale-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.rationale-item label { display: block; font-weight: 600; color: #555; margin-bottom: 0.5rem; font-size: 0.9rem; }
.rationale-item textarea { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; height: 80px; font-size: 0.9rem; }

.decision-select { font-size: 1rem; padding: 0.8rem; }
.form-control { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; }

.btn { padding: 0.6rem 1.2rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 600; transition: 0.2s; }
.btn-primary { background: #3498db; color: white; }
.btn-primary:hover { background: #2980b9; }
.btn-secondary { background: #95a5a6; color: white; }
.btn-success { background: #27ae60; color: white; }
.btn-outline { background: white; border: 1px solid #3498db; color: #3498db; }
.btn-outline:hover { background: #f0f7fb; }
.btn-text { background: none; color: #7f8c8d; text-decoration: underline; font-size: 0.9rem; }
.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }

.no-data { text-align: center; padding: 4rem; color: #999; font-size: 1.1rem; background: white; border-radius: 8px; }

/* Meeting Styles */
.meeting-card { border-left: 5px solid #e67e22; }
.priority-tag { background: #fce4ec; color: #c2185b; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }

.alert-box { margin-top: 0.5rem; padding: 0.8rem; border-radius: 4px; font-size: 0.9rem; }
.alert-box.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
</style>
