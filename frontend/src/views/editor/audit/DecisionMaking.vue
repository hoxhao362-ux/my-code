<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import { usePlatformStore } from '../../../stores/platform'
import Navigation from '../../../components/Navigation.vue'
import RichTextEditor from '../../../components/RichTextEditor.vue'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'
import { useI18n } from '../../../composables/useI18n'

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const router = useRouter()
const user = computed(() => userStore.user)

// --- Tabs for Decision Central ---
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
const transferJournal = ref('')
const transferReason = ref('')

// Setup platform store to get transfer journals
const platformStore = usePlatformStore()
onMounted(() => {
  if (platformStore.journals.length === 0) {
    platformStore.fetchJournals()
  }
})

const transferJournals = computed(() => {
  const currentJournalId = 'lancet' // Mock current
  return platformStore.journals
    .filter(j => j.id !== currentJournalId)
    .map(j => ({ id: j.id, name: j.name }))
})

// Structured Decision Rationale
const decisionRationale = ref({
  scientificRigor: '',
  novelty: '',
  methodology: '',
  dataIntegrity: '',
  ethicalCompliance: ''
})

// Consensus Meeting Data
const meetingAgenda = ref({
  date: new Date().toISOString().slice(0, 16),
  attendees: ['Editor-in-Chief', 'Senior Editor', 'Statistician'],
  notes: ''
})

const openDecisionModal = (journal) => {
  // Permission check: only editor or admin can handle pending final decision manuscripts
  if (journal.status === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION && !['editor', 'admin'].includes(user.value?.role)) {
    toastStore.add({ message: t('editor.audit.decisionMaking.alerts.onlyEditors'), type: 'error' })
    return
  }
  
  currentJournal.value = journal
  decisionType.value = 'Minor Revision' // default
  decisionComments.value = ''
  // Reset Rationale
  decisionRationale.value = {
    scientificRigor: t('editor.audit.decisionMaking.modals.decision.placeholders.rigor'),
    novelty: t('editor.audit.decisionMaking.modals.decision.placeholders.novelty'),
    methodology: t('editor.audit.decisionMaking.modals.decision.placeholders.methodology'),
    dataIntegrity: t('editor.audit.decisionMaking.modals.decision.placeholders.dataIntegrity'),
    ethicalCompliance: 'IRB approval confirmed.'
  }
  showModal.value = true
}

// --- Auto-Consolidation (System Feature) ---
const autoConsolidateReviews = (journal) => {
  // Simulate AI/System extraction of key points
  const reviews = journal.reviewHistory || journal.reviews || []
  const summary = reviews.map(r => `[${r.reviewer || t('editor.audit.decisionMaking.consolidation.reviewerLabel')}]: ${r.comment ? r.comment.substring(0, 50) + '...' : t('common.noData')}`).join('\n')
  return summary
}

const submitDecision = () => {
  // Validate comments unless it's a transfer or consensus meeting
  if (!decisionComments.value && decisionType.value !== 'Transfer' && decisionType.value !== 'Consensus Meeting') {
    toastStore.add({ message: t('editor.audit.decisionMaking.alerts.enterComments'), type: 'warning' })
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
      journal.reviewStage = 'Pending Final Decision'
    } else if (journal.status === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION || journal.status === MANUSCRIPT_STATUS.UNDER_FINAL_DECISION) {
      // If already in final decision stage, move to production process
      newStatus = MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION
      journal.reviewStage = 'In Production'
    } else {
      // Default case: move to production process
      newStatus = MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION
      journal.reviewStage = 'In Production'
    }
  } else if (decisionType.value === 'Reject') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  } else if (decisionType.value === 'Minor Revision' || decisionType.value === 'Major Revision') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REVISION
  } else if (decisionType.value === 'Return to Reviewer') {
    // New Option: Return to Reviewer (Directly restart review process)
    newStatus = MANUSCRIPT_STATUS.UNDER_PEER_REVIEW // or 'under_peer_review'
  } else if (decisionType.value === 'Transfer') {
    if (!transferJournal.value || !transferReason.value) {
      toastStore.add({ message: 'Please select a target journal and provide a reason for transfer.', type: 'warning' })
      return
    }
    newStatus = MANUSCRIPT_STATUS.TRANSFER_SUGGESTED || 'transfer_suggested'
    
    // Add transfer metadata
    const targetJournalObj = platformStore.journals.find(j => j.name === transferJournal.value)
    journal.transferTo = targetJournalObj ? targetJournalObj.id : 'unknown'
    journal.transferReason = transferReason.value
    
    // Notify author
    if (!userStore.notifications) userStore.notifications = []
    const newNotification = {
      id: Date.now(),
      type: 'transfer_suggested',
      title: 'Transfer Suggestion after Review',
      message: `The editor has reviewed your manuscript "${journal.title}" and suggested transferring it to ${transferJournal.value}. Please review it in your dashboard.`,
      date: new Date().toISOString().split('T')[0],
      read: false,
      manuscriptId: journal.id,
      targetUser: journal.author
    }
    userStore.notifications.unshift(newNotification)
    localStorage.setItem('notifications', JSON.stringify(userStore.notifications))
  } else if (decisionType.value === 'Consensus Meeting') {
    // Move to Meeting Queue
    journal.decisionStage = 'consensus_meeting'
    userStore.updateJournal(journal)
    showModal.value = false
    toastStore.add({ message: t('editor.audit.decisionMaking.alerts.movedToConsensus'), type: 'success' })
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
    author: journal.author,
    rationale: decisionRationale.value // Save structured rationale
  }
  userStore.saveDecisionDraft(draft)
  
  showModal.value = false
  
  // Show different messages based on status transition
  if (newStatus === MANUSCRIPT_STATUS.PENDING_FINAL_DECISION) {
    toastStore.add({ 
      message: t('editor.audit.decisionMaking.alerts.decisionRecorded', { type: decisionType.value }) + '\n' + t('editor.audit.decisionMaking.alerts.sentToEIC'), 
      type: 'success' 
    })
  } else {
    toastStore.add({ 
      message: t('editor.audit.decisionMaking.alerts.decisionRecorded', { type: decisionType.value }) + '\n' + t('editor.audit.decisionMaking.alerts.letterGenerated'), 
      type: 'success' 
    })
  }
}

// --- Meeting Functions ---
const scheduleMeeting = (journal) => {
  toastStore.add({ message: t('editor.audit.decisionMaking.alerts.meetingScheduled', { title: journal.title }), type: 'info' })
}

const finalizeMeetingDecision = (journal) => {
  openDecisionModal(journal) // Open decision modal to finalize
}

// --- Appeal Functions ---
const assignIndependentReviewer = (journal) => {
  toastStore.add({ message: t('editor.audit.decisionMaking.alerts.independentAssigned', { title: journal.title }), type: 'success' })
  // Logic to change status or assign reviewer
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-decision-making" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>{{ t('editor.audit.decisionMaking.title') }}</h1>
        <p class="subtitle">{{ t('editor.audit.decisionMaking.subtitle') }}</p>
      </div>

      <!-- Tab Navigation -->
      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'consolidation' }]" 
          @click="activeTab = 'consolidation'"
        >
          {{ t('editor.audit.decisionMaking.tabs.consolidation') }} ({{ decisionJournals.length }})
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'consensus' }]" 
          @click="activeTab = 'consensus'"
        >
          {{ t('editor.audit.decisionMaking.tabs.consensus') }} ({{ consensusJournals.length }})
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'appeals' }]" 
          @click="activeTab = 'appeals'"
        >
          {{ t('editor.audit.decisionMaking.tabs.appeals') }} ({{ appealJournals.length }})
        </button>
      </div>

      <!-- Tab 1: Review Consolidation -->
      <div v-if="activeTab === 'consolidation'" class="tab-pane">
        <div v-if="allDecisionJournals.length === 0" class="no-data">
          {{ t('editor.audit.decisionMaking.consolidation.noManuscripts') }}
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
              <h4>{{ t('editor.audit.decisionMaking.consolidation.reviewerOpinions') }}</h4>
              <div v-if="journal.reviewHistory && journal.reviewHistory.length > 0">
                 <div v-for="(review, idx) in journal.reviewHistory" :key="'h-'+idx" class="review-card">
                   <div class="review-meta">
                     <strong>{{ t('editor.audit.decisionMaking.consolidation.reviewerLabel') }} {{ idx + 1 }}</strong>
                     <span :class="['decision-tag', review.decision?.toLowerCase()]">{{ review.decision || 'N/A' }}</span>
                   </div>
                   <p class="review-text">{{ review.comment }}</p>
                   <div class="review-score" v-if="review.score">{{ t('editor.audit.decisionMaking.consolidation.score') }}: {{ review.score }}/10</div>
                 </div>
              </div>
              <div v-else class="no-reviews">{{ t('editor.audit.decisionMaking.consolidation.noReviews') }}</div>
            </div>

            <!-- Right: Editor Consolidation -->
            <div class="editor-column">
              <h4>{{ t('editor.audit.decisionMaking.consolidation.assessment') }}</h4>
              <div class="assessment-box">
                <div class="auto-summary">
                  <span class="ai-badge">{{ t('editor.audit.decisionMaking.consolidation.systemAnalysis') }}</span>
                  <p><strong>{{ t('editor.audit.decisionMaking.consolidation.consensusLevel') }}:</strong> {{ (journal.reviews && journal.reviews.length > 1) ? t('editor.audit.decisionMaking.consolidation.mixed') : t('editor.audit.decisionMaking.consolidation.high') }}</p>
                  <p><strong>{{ t('editor.audit.decisionMaking.consolidation.keyIssues') }}:</strong> Methodology, Sample Size ({{ t('editor.audit.decisionMaking.consolidation.detected') }})</p>
                </div>
                <button class="btn btn-outline" @click="openDecisionModal(journal)">{{ t('editor.audit.decisionMaking.consolidation.actions.draftDecision') }}</button>
                <button class="btn btn-text" @click="decisionType.value = 'Consensus Meeting'; submitDecision()">{{ t('editor.audit.decisionMaking.consolidation.actions.requestConsensus') }}</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Tab 2: Consensus Meetings -->
      <div v-if="activeTab === 'consensus'" class="tab-pane">
        <div class="meeting-toolbar">
           <button class="btn btn-primary">{{ t('editor.audit.decisionMaking.consensus.scheduleNew') }}</button>
           <span class="meeting-info">{{ t('editor.audit.decisionMaking.consensus.nextMeeting') }}: Tomorrow, 10:00 AM (EST)</span>
        </div>
        
        <div v-if="consensusJournals.length === 0" class="no-data">
          {{ t('editor.audit.decisionMaking.consensus.noManuscripts') }}
        </div>
        
        <div v-for="journal in consensusJournals" :key="journal.id" class="journal-item meeting-item">
           <div class="meeting-card">
             <div class="meeting-header">
               <h3>{{ journal.title }}</h3>
               <span class="priority-tag">High Priority</span>
             </div>
             <p class="reason"><strong>{{ t('editor.audit.decisionMaking.consensus.reasonLabel') }}:</strong> Conflicting reviewer recommendations (Accept vs Reject).</p>
             
             <div class="meeting-actions">
               <button class="btn btn-success" @click="finalizeMeetingDecision(journal)">{{ t('editor.audit.decisionMaking.consensus.actions.finalize') }}</button>
               <button class="btn btn-secondary">{{ t('editor.audit.decisionMaking.consensus.actions.viewMinutes') }}</button>
             </div>
           </div>
        </div>
      </div>

      <!-- Tab 3: Appeals -->
      <div v-if="activeTab === 'appeals'" class="tab-pane">
        <div v-if="appealJournals.length === 0" class="no-data">
          {{ t('editor.audit.decisionMaking.appeals.noAppeals') }}
        </div>
        <div v-for="journal in appealJournals" :key="journal.id" class="journal-item">
          <h3>{{ journal.title }}</h3>
          <p><strong>{{ t('editor.audit.decisionMaking.appeals.reasonLabel') }}:</strong> Author claims reviewer 2 misunderstood the statistical model.</p>
          <button class="btn btn-primary" @click="assignIndependentReviewer(journal)">{{ t('editor.audit.decisionMaking.appeals.actions.assignIndependent') }}</button>
        </div>
      </div>

    </main>

    <!-- Detailed Decision Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content large-modal">
        <div class="modal-header">
          <h2>{{ t('editor.audit.decisionMaking.modals.decision.title') }}: {{ currentJournal.title }}</h2>
          <button class="close-btn" @click="showModal = false">&times;</button>
        </div>
        
        <div class="modal-body">
          <div class="decision-form">
            <!-- Section 1: Decision Type -->
            <div class="form-section">
              <h3>{{ t('editor.audit.decisionMaking.modals.decision.sections.decision') }}</h3>
              <select v-model="decisionType" class="form-control decision-select">
                <option value="Accept">{{ t('editor.audit.decisionMaking.modals.decision.types.accept') }}</option>
                <option value="Minor Revision">{{ t('editor.audit.decisionMaking.modals.decision.types.minor') }}</option>
                <option value="Major Revision">{{ t('editor.audit.decisionMaking.modals.decision.types.major') }}</option>
                <option value="Return to Reviewer">{{ t('editor.audit.decisionMaking.modals.decision.types.return') }}</option>
                <option value="Reject">{{ t('editor.audit.decisionMaking.modals.decision.types.reject') }}</option>
                <option value="Transfer">{{ t('editor.audit.decisionMaking.modals.decision.types.transfer') }}</option>
                <option value="Consensus Meeting">{{ t('editor.audit.decisionMaking.modals.decision.types.consensus') }}</option>
              </select>
              <div v-if="decisionType === 'Return to Reviewer'" class="alert-box warning">
                <small><strong>Note:</strong> {{ t('editor.audit.decisionMaking.modals.decision.returnWarning') }}</small>
              </div>
              <div v-if="decisionType === 'Transfer'" class="transfer-section" style="margin-top: 1rem;">
                <div class="form-group" style="margin-bottom: 1rem;">
                  <label class="input-label required" style="display: block; font-weight: 600; color: #555; margin-bottom: 0.5rem; font-size: 0.9rem;">Select Target Journal</label>
                  <select v-model="transferJournal" class="form-control">
                    <option value="" disabled>Select a sister journal...</option>
                    <option v-for="j in transferJournals" :key="j.id" :value="j.name">{{ j.name }}</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="input-label required" style="display: block; font-weight: 600; color: #555; margin-bottom: 0.5rem; font-size: 0.9rem;">Transfer Reason</label>
                  <textarea v-model="transferReason" class="form-control" rows="3" placeholder="Explain why this journal is a better fit..."></textarea>
                </div>
              </div>
            </div>

            <!-- Section 2: Structured Rationale -->
            <div class="form-section">
              <h3>{{ t('editor.audit.decisionMaking.modals.decision.sections.rationale') }}</h3>
              <div class="rationale-grid">
                <div class="rationale-item">
                  <label>{{ t('editor.audit.decisionMaking.modals.decision.rationaleLabels.rigor') }}</label>
                  <textarea v-model="decisionRationale.scientificRigor" :placeholder="t('editor.audit.decisionMaking.modals.decision.placeholders.rigor')"></textarea>
                </div>
                <div class="rationale-item">
                  <label>{{ t('editor.audit.decisionMaking.modals.decision.rationaleLabels.novelty') }}</label>
                  <textarea v-model="decisionRationale.novelty" :placeholder="t('editor.audit.decisionMaking.modals.decision.placeholders.novelty')"></textarea>
                </div>
                <div class="rationale-item">
                  <label>{{ t('editor.audit.decisionMaking.modals.decision.rationaleLabels.methodology') }}</label>
                  <textarea v-model="decisionRationale.methodology" :placeholder="t('editor.audit.decisionMaking.modals.decision.placeholders.methodology')"></textarea>
                </div>
                <div class="rationale-item">
                  <label>{{ t('editor.audit.decisionMaking.modals.decision.rationaleLabels.dataIntegrity') }}</label>
                  <textarea v-model="decisionRationale.dataIntegrity" :placeholder="t('editor.audit.decisionMaking.modals.decision.placeholders.dataIntegrity')"></textarea>
                </div>
              </div>
            </div>

            <!-- Section 3: Decision Letter -->
            <div class="form-section">
              <h3>{{ t('editor.audit.decisionMaking.modals.decision.sections.letter') }}</h3>
              <RichTextEditor 
                v-model="decisionComments" 
                :placeholder="t('editor.audit.decisionMaking.modals.decision.placeholders.letter')"
              />
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="submitDecision">{{ t('common.confirm') }}</button>
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
