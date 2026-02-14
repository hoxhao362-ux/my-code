<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Filter for manuscripts waiting for assignment
const assignmentJournals = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === 'Pending Assignment'
  )
})

const availableReviewers = computed(() => userStore.users.filter(u => u.role === 'reviewer'))

// Selection Logic
const showModal = ref(false)
const currentJournal = ref(null)
const selectedReviewerIds = ref([])
const filterMethod = ref('all') // 'field', 'method'
const searchQuery = ref('')

const filteredReviewers = computed(() => {
  let list = availableReviewers.value
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(r => r.username.toLowerCase().includes(q) || r.email.toLowerCase().includes(q))
  }
  return list
})

const openAssignModal = (journal) => {
  currentJournal.value = journal
  selectedReviewerIds.value = []
  showModal.value = true
}

const confirmAssignment = () => {
  if (selectedReviewerIds.value.length < 1) {
    alert('Please select at least one reviewer.')
    return
  }
  
  const journal = { ...currentJournal.value }
  journal.status = 'Under Review' // English status
  // Mock adding reviewers
  journal.reviewers = selectedReviewerIds.value.map(id => {
    const r = availableReviewers.value.find(u => u.id === id)
    return {
      id: r.id,
      name: r.username,
      status: 'Invited',
      invitedAt: new Date().toISOString()
    }
  })
  
  userStore.updateJournal(journal)
  showModal.value = false
  alert('Reviewers assigned. Manuscript moved to "Under Review".')
}

const handleReinvite = (journal) => {
  alert('Re-invitation feature would go here.')
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-assign-reviewers" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>Assign Reviewers</h1>
        <p class="subtitle">Select and Invite Peer Reviewers</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in assignmentJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title">{{ journal.title }}</h3>
            <div class="journal-meta">
              <span><strong>Writer:</strong> {{ journal.author }}</span>
              <span><strong>Module:</strong> {{ journal.module }}</span>
            </div>
            <div class="tags">
               <span class="tag">AI</span> <span class="tag">Imaging</span> <!-- Mock tags -->
            </div>
          </div>
          <div class="journal-actions">
            <button class="btn btn-primary" @click="openAssignModal(journal)">Assign Reviewers</button>
            <button class="btn btn-secondary" @click="handleReinvite(journal)">Re-invite</button>
          </div>
        </div>
        <div v-if="assignmentJournals.length === 0" class="no-data">
          No manuscripts waiting for reviewer assignment.
        </div>
      </div>
    </main>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2>Select Reviewers</h2>
        <div class="modal-search">
           <input v-model="searchQuery" placeholder="Search reviewers..." class="search-input" />
           <div class="filters">
             <label><input type="radio" v-model="filterMethod" value="all"> All</label>
             <label><input type="radio" v-model="filterMethod" value="field"> Match Field</label>
           </div>
        </div>
        <div class="reviewer-list">
          <div v-for="reviewer in filteredReviewers" :key="reviewer.id" class="reviewer-item">
             <label>
               <input type="checkbox" :value="reviewer.id" v-model="selectedReviewerIds">
               <span class="r-name">{{ reviewer.username }}</span>
               <span class="r-email">{{ reviewer.email }}</span>
             </label>
          </div>
        </div>
        <div class="modal-footer">
          <div class="selection-count">Selected: {{ selectedReviewerIds.length }}</div>
          <div class="buttons">
            <button class="btn btn-secondary" @click="showModal = false">Cancel</button>
            <button class="btn btn-primary" @click="confirmAssignment">Confirm Assignment</button>
          </div>
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

.journal-item { background: white; padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
.journal-title { margin: 0 0 0.5rem 0; color: #2c3e50; }
.journal-meta { color: #666; font-size: 0.9rem; margin-bottom: 0.5rem; display: flex; gap: 1rem; }
.tags { display: flex; gap: 0.5rem; }
.tag { background: #e0f7fa; color: #006064; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }

.btn { padding: 0.5rem 1rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; color: white; transition: 0.2s; }
.btn-primary { background: #3498db; }
.btn-primary:hover { background: #2980b9; }
.btn-secondary { background: #95a5a6; }
.btn-secondary:hover { background: #7f8c8d; }
.journal-actions { display: flex; gap: 1rem; }

.no-data { text-align: center; padding: 3rem; background: white; border-radius: 8px; color: #999; }

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; width: 600px; padding: 2rem; border-radius: 8px; max-height: 80vh; display: flex; flex-direction: column; }
.modal-search { display: flex; justify-content: space-between; margin-bottom: 1rem; }
.search-input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 60%; }
.filters { display: flex; gap: 1rem; align-items: center; }
.reviewer-list { flex: 1; overflow-y: auto; border: 1px solid #eee; padding: 1rem; margin-bottom: 1rem; }
.reviewer-item { padding: 0.5rem 0; border-bottom: 1px solid #f9f9f9; }
.reviewer-item label { display: flex; align-items: center; gap: 0.8rem; cursor: pointer; }
.r-name { font-weight: bold; }
.r-email { color: #888; font-size: 0.9rem; }
.modal-footer { display: flex; justify-content: space-between; align-items: center; }
.modal-footer .buttons { display: flex; gap: 1rem; }
</style>
