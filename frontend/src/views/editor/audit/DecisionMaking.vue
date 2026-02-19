<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Filter for manuscripts ready for decision
// Updated to match actual system status 'review_completed' and ensure assignment correctness
const decisionJournals = computed(() => {
  if (!user.value) return []
  
  return userStore.journals.filter(journal => {
    // 1. Status Check: Must be 'review_completed' (or legacy 'Reviews Completed')
    const isStatusReady = journal.status === 'review_completed' || journal.status === 'Reviews Completed'
    
    // 2. Assignment Check: Must be assigned to current editor
    // If assignedEditor is present, it must match current user
    const isAssignedToMe = journal.assignedEditor === user.value.username
    
    // 3. Data Check: Should have reviews (from reviewHistory preferably)
    const hasReviews = (journal.reviewHistory && journal.reviewHistory.length > 0) || 
                       (journal.reviews && journal.reviews.length > 0)
    
    // Log for debugging if needed (console.log)
    if (isStatusReady && !isAssignedToMe && journal.assignedEditor) {
      console.warn(`Journal ${journal.id} is ready but assigned to ${journal.assignedEditor}, not current user ${user.value.username}`)
    }

    // Return true if status is ready AND assigned to me (or not assigned specifically)
    // We enforce assignment check if the field exists
    return isStatusReady && (!journal.assignedEditor || isAssignedToMe)
  })
})

const showModal = ref(false)
const currentJournal = ref(null)
const decisionType = ref('')
const decisionComments = ref('')

const openDecisionModal = (journal) => {
  currentJournal.value = journal
  decisionType.value = 'Minor Revision' // default
  decisionComments.value = ''
  showModal.value = true
}

const submitDecision = () => {
  if (!decisionComments.value) {
    alert('Please enter decision comments.')
    return
  }
  
  const journal = { ...currentJournal.value }
  let newStatus = ''
  
  // Update status based on decision type using standard constants
  if (decisionType.value === 'Accept') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED
  } else if (decisionType.value === 'Reject') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED
  } else if (decisionType.value === 'Minor Revision' || decisionType.value === 'Major Revision') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REVISION
  } else if (decisionType.value === 'Transfer') {
    newStatus = MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED // Transfer is treated as reject in workflow
  } else {
    newStatus = 'final_decision_made'
  }
  
  journal.status = newStatus
  
  journal.decision = {
    type: decisionType.value,
    comments: decisionComments.value,
    date: new Date().toISOString()
  }
  
  // Save to Journal Store
  userStore.updateJournal(journal)
  
  // Save Draft for Decisions Module (Critical for workflow continuity)
  const draft = {
    manuscriptId: journal.id,
    manuscriptTitle: journal.title,
    content: decisionComments.value,
    templateType: decisionType.value,
    status: 'Draft',
    author: journal.writer || journal.author
  }
  userStore.saveDecisionDraft(draft)
  
  showModal.value = false
  // Updated alert to guide user to next step
  alert(`Decision recorded: ${decisionType.value}. \nDraft letter generated in 'Decisions & Letters' module. Please review and send.`)
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-decision-making" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>Decision Making</h1>
        <p class="subtitle">Consolidate Opinions & Finalize Decisions</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in decisionJournals" :key="journal.id" class="journal-item">
          <div class="journal-header">
             <h3 class="journal-title">{{ journal.title }}</h3>
             <span class="status-badge">{{ journal.status }}</span>
          </div>
          
          <div class="reviews-summary">
            <h4>Reviews Received ({{ (journal.reviewHistory && journal.reviewHistory.length) || (journal.reviews && journal.reviews.length) || 0 }})</h4>
            
            <!-- Priority: Review History (New System) -->
            <div v-if="journal.reviewHistory && journal.reviewHistory.length > 0" class="reviews-list">
               <div v-for="(review, idx) in journal.reviewHistory" :key="'h-'+idx" class="review-item">
                 <div class="review-header">
                   <strong>Reviewer {{ idx + 1 }} ({{ review.reviewer }})</strong>
                   <!-- Display Decision as Recommendation -->
                   <span class="rating" :class="{'accept': review.decision === 'Accept', 'reject': review.decision === 'Reject'}">
                     {{ review.decision }}
                   </span>
                 </div>
                 <p class="review-content">{{ review.comment }}</p>
                 <div v-if="review.confidentialComments" class="confidential-note">
                   <small>Confidential: {{ review.confidentialComments }}</small>
                 </div>
               </div>
            </div>
            
            <!-- Fallback: Old Reviews -->
            <div v-else-if="journal.reviews && journal.reviews.length > 0" class="reviews-list">
               <div v-for="(review, idx) in journal.reviews" :key="'r-'+idx" class="review-item">
                 <div class="review-header">
                   <strong>Reviewer {{ idx + 1 }} ({{ review.reviewer }})</strong>
                   <span class="rating">Rating: {{ review.rating }}/5</span>
                 </div>
                 <p class="review-content">{{ review.comment }}</p>
               </div>
            </div>
            
            <div v-else class="no-reviews">No reviews submitted yet.</div>
          </div>
          
          <div class="actions">
             <button class="btn btn-primary" @click="openDecisionModal(journal)">Make Decision</button>
          </div>
        </div>
        
        <div v-if="decisionJournals.length === 0" class="no-data">
          No manuscripts ready for decision.
        </div>
      </div>
    </main>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2>Make Decision: {{ currentJournal.title }}</h2>
        
        <div class="form-group">
          <label>Decision Type</label>
          <select v-model="decisionType" class="form-control">
            <option value="Accept">Accept</option>
            <option value="Minor Revision">Minor Revision</option>
            <option value="Major Revision">Major Revision</option>
            <option value="Reject">Reject</option>
            <option value="Transfer">Transfer</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Decision Letter (sent to Writer)</label>
          <textarea v-model="decisionComments" rows="6" class="form-control" placeholder="Enter your decision letter here..."></textarea>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
          <button class="btn btn-primary" @click="submitDecision">Send Decision</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-container { min-height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.content { flex: 1; max-width: 1200px; margin: 80px auto 0; padding: 2rem; width: 100%; }
.header { margin-bottom: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem; }
.header h1 { font-size: 1.8rem; color: #2c3e50; margin: 0; }
.subtitle { color: #7f8c8d; margin-top: 0.5rem; }

.journal-item { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.journal-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.journal-title { margin: 0; color: #2c3e50; }
.status-badge { background: #e3f2fd; color: #1976d2; padding: 4px 8px; border-radius: 4px; font-size: 0.8rem; }

.reviews-summary { background: #f9f9f9; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
.reviews-summary h4 { margin: 0 0 1rem 0; color: #555; }
.review-item { background: white; padding: 1rem; border: 1px solid #eee; margin-bottom: 0.5rem; border-radius: 4px; }
.review-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; font-size: 0.9rem; }
.review-content { margin: 0; color: #666; font-size: 0.9rem; }

.rating { font-weight: bold; color: #f1c40f; }
.rating.accept { color: #27ae60; }
.rating.reject { color: #c0392b; }
.confidential-note { background: #fff3cd; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; color: #856404; }

.actions { display: flex; justify-content: flex-end; }
.btn { padding: 0.6rem 1.2rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; color: white; transition: 0.2s; }
.btn-primary { background: #3498db; }
.btn-primary:hover { background: #2980b9; }
.btn-secondary { background: #95a5a6; }

.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; width: 600px; padding: 2rem; border-radius: 8px; }
.form-group { margin-bottom: 1.5rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: bold; color: #555; }
.form-control { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; }
.modal-footer { display: flex; justify-content: flex-end; gap: 1rem; }

.no-data { text-align: center; padding: 3rem; background: white; border-radius: 8px; color: #999; }
</style>
