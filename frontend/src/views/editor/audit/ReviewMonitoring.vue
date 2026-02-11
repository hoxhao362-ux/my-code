<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

const monitoringJournals = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === 'Under Review' || journal.status === '审稿中' // Handle both En and legacy Zh status
  )
})

const getReviewerStatus = (reviewer) => {
  // Mock status if not present
  return reviewer.status || 'Invited'
}

const handleRemind = (journal, reviewer) => {
  alert(`Reminder sent to ${reviewer.name}.`)
}

const handleReplace = (journal, reviewer) => {
  if (confirm(`Replace reviewer ${reviewer.name}?`)) {
    alert('Redirecting to replacement selection (mock)...')
    // In real app, this would open a selection modal similar to AssignReviewers
  }
}

const handleExtend = (journal) => {
  alert('Extension granted for 7 days.')
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-review-monitoring" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>Review Monitoring</h1>
        <p class="subtitle">Track Progress & Manage Delays</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in monitoringJournals" :key="journal.id" class="journal-item">
          <div class="journal-main">
            <h3 class="journal-title">{{ journal.title }}</h3>
            <div class="journal-meta">
               <span><strong>Writer:</strong> {{ journal.author }}</span>
               <span><strong>Sent to Review:</strong> {{ journal.date }}</span> <!-- Mock date -->
            </div>
          </div>
          
          <div class="reviewers-section">
            <h4>Reviewers Status</h4>
            <div v-if="journal.reviewers && journal.reviewers.length > 0" class="reviewers-grid">
               <div v-for="reviewer in journal.reviewers" :key="reviewer.id" class="reviewer-card">
                 <div class="r-info">
                   <span class="r-name">{{ reviewer.name }}</span>
                   <span class="r-status" :class="getReviewerStatus(reviewer).toLowerCase()">{{ getReviewerStatus(reviewer) }}</span>
                 </div>
                 <div class="r-actions">
                   <button class="btn-xs" @click="handleRemind(journal, reviewer)">Remind</button>
                   <button class="btn-xs" @click="handleReplace(journal, reviewer)">Replace</button>
                 </div>
               </div>
            </div>
            <div v-else class="no-reviewers">
              No reviewers assigned yet (Data inconsistency).
            </div>
          </div>
          
          <div class="item-footer">
             <button class="btn btn-secondary" @click="handleExtend(journal)">Process Extension Request</button>
          </div>
        </div>
        
        <div v-if="monitoringJournals.length === 0" class="no-data">
          No manuscripts currently under review.
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
.journal-meta { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }

.reviewers-section { background: #f9f9f9; padding: 1rem; border-radius: 6px; margin-bottom: 1rem; }
.reviewers-section h4 { margin: 0 0 1rem 0; font-size: 1rem; color: #555; }
.reviewers-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.reviewer-card { background: white; padding: 0.8rem; border: 1px solid #eee; border-radius: 4px; }
.r-info { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
.r-name { font-weight: bold; font-size: 0.9rem; }
.r-status { font-size: 0.8rem; padding: 2px 6px; border-radius: 4px; }
.r-status.invited { background: #e3f2fd; color: #1565c0; }
.r-status.accepted { background: #e8f5e9; color: #2e7d32; }
.r-status.declined { background: #ffebee; color: #c62828; }
.r-status.overdue { background: #fff3e0; color: #ef6c00; }

.r-actions { display: flex; gap: 0.5rem; }
.btn-xs { padding: 2px 8px; font-size: 0.75rem; border: 1px solid #ddd; background: white; border-radius: 3px; cursor: pointer; }
.btn-xs:hover { background: #f0f0f0; }

.item-footer { display: flex; justify-content: flex-end; }
.btn-secondary { background: #95a5a6; color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer; }

.no-data { text-align: center; padding: 3rem; background: white; border-radius: 8px; color: #999; }
</style>
