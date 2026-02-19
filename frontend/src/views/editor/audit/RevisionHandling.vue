<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

import { MANUSCRIPT_STATUS } from '../../../constants/manuscriptStatus'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

const revisionJournals = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === 'Revision Submitted' || 
    journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_REVISION ||
    journal.status === MANUSCRIPT_STATUS.INITIAL_REVIEW_REVISION
  )
})

const handleMinorDecision = (journal, decision) => {
  const updated = { ...journal }
  updated.status = decision === 'Accept' ? 'Accepted' : 'Rejected'
  updated.decision = { type: decision, date: new Date().toISOString() }
  userStore.updateJournal(updated)
  alert(`Minor revision decision: ${decision}.`)
}

const handleMajorReReview = (journal) => {
  const updated = { ...journal }
  updated.status = 'Under Review' // Back to review
  // Ideally, notify reviewers
  userStore.updateJournal(updated)
  alert('Sent back to original reviewers for re-evaluation.')
}

const viewComparison = (journal) => {
  // Mock comparison view
  window.open('', '_blank').document.write('<h1>Manuscript Comparison View</h1><p>Showing changes between v1 and v2...</p>')
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-revision-handling" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>Revision Handling</h1>
        <p class="subtitle">Review Writer Revisions</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in revisionJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title">{{ journal.title }}</h3>
            <div class="journal-meta">
              <span><strong>Writer:</strong> {{ journal.writer }}</span>
              <span><strong>Revision Date:</strong> {{ journal.date }}</span>
            </div>
            <div class="revision-note" v-if="journal.revisionNote">
              <strong>Writer Response:</strong> {{ journal.revisionNote }}
            </div>
          </div>
          
          <div class="actions-group">
             <button class="btn btn-info" @click="viewComparison(journal)">View Changes</button>
             <div class="decision-buttons">
                <span class="label">Decision:</span>
                <button class="btn btn-success" @click="handleMinorDecision(journal, 'Accept')">Accept (Minor)</button>
                <button class="btn btn-warning" @click="handleMajorReReview(journal)">Re-Review (Major)</button>
                <button class="btn btn-danger" @click="handleMinorDecision(journal, 'Reject')">Reject</button>
             </div>
          </div>
        </div>
        
        <div v-if="revisionJournals.length === 0" class="no-data">
          No revisions pending assessment.
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.audit-container { min-height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.content { flex: 1; max-width: 1200px; margin: 80px auto 0; padding: 2rem; width: 100%; }
.header { margin-bottom: 2rem; border-bottom: 1px solid #ddd; padding-bottom: 1rem; }
.header h1 { font-size: 1.8rem; color: #2c3e50; margin: 0; }
.subtitle { color: #7f8c8d; margin-top: 0.5rem; }

.journal-item { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.journal-title { color: #2c3e50; margin-bottom: 0.5rem; }
.journal-meta { color: #666; font-size: 0.9rem; margin-bottom: 1rem; display: flex; gap: 1rem; }
.revision-note { background: #f9f9f9; padding: 0.8rem; border-left: 3px solid #3498db; margin-bottom: 1rem; font-size: 0.9rem; }

.actions-group { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 1rem; }
.decision-buttons { display: flex; gap: 0.5rem; align-items: center; }
.label { font-weight: bold; margin-right: 0.5rem; color: #555; }

.btn { padding: 0.6rem 1rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; color: white; transition: 0.2s; }
.btn-info { background: #17a2b8; }
.btn-success { background: #28a745; }
.btn-warning { background: #ffc107; color: #333; }
.btn-danger { background: #dc3545; }
.btn:hover { opacity: 0.9; }

.no-data { text-align: center; padding: 3rem; background: white; border-radius: 8px; color: #999; }
</style>
