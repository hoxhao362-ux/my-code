<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import { useI18n } from '../../../composables/useI18n'
import Navigation from '../../../components/Navigation.vue'
import IntelligentReviewerRecommendation from '../../../components/audit/IntelligentReviewerRecommendation.vue'

const { t } = useI18n()
const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Filter for manuscripts waiting for assignment
const assignmentJournals = computed(() => {
  return userStore.journals.filter(journal => 
    // Public Pool
    journal.status === 'reviewer_assignment_pending' || 
    journal.status === 'initial_review_passed' || 
    // Assigned specifically to current user (or Admin sees all)
    (journal.status === 'assigned_to_editor' && (journal.assignedEditor === user.value?.username || user.value?.role === 'admin')) ||
    // Legacy support
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
const activeTab = ref('recommended') // 'manual', 'smart', 'recommended'

const writerRecommendedReviewers = computed(() => {
  if (!currentJournal.value) return []
  // Get all recommendations for this manuscript (Removed 'accepted' filter per requirements)
  return userStore.recommendedReviewers.filter(r => 
    String(r.manuscriptId) === String(currentJournal.value.id)
  )
})

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
  
  // Check if there are writer recommendations
  const hasRecommendations = userStore.recommendedReviewers.some(r => 
    String(r.manuscriptId) === String(journal.id) && 
    r.status === 'accepted'
  )
  
  activeTab.value = hasRecommendations ? 'recommended' : 'smart'
  showModal.value = true
}

const handleSmartSelect = (reviewer) => {
  if (!selectedReviewerIds.value.includes(reviewer.id)) {
    selectedReviewerIds.value.push(reviewer.id)
    // Switch to manual tab to show selection
    activeTab.value = 'manual'
  }
}

const handleSelectRecommended = (reviewer) => {
  // Logic to handle recommended reviewer selection
  // Note: These might be 'temporary' reviewers not in the main user table yet.
  // We track them by their recommendation ID or we need to mock a user ID.
  
  if (selectedReviewerIds.value.includes(reviewer.id)) {
    selectedReviewerIds.value = selectedReviewerIds.value.filter(id => id !== reviewer.id)
  } else {
    selectedReviewerIds.value.push(reviewer.id)
  }
}

const confirmAssignment = () => {
  if (selectedReviewerIds.value.length < 1) {
    alert(t('editor.audit.assignReviewers.alerts.selectAtLeastOne'))
    return
  }
  
  const journal = { ...currentJournal.value }
  journal.status = 'under_peer_review'
  
  // Mix of Real Users (Manual/Smart) and Recommended Reviewers
  const newReviewers = selectedReviewerIds.value.map(id => {
    // Check if it's a real user first
    const realUser = availableReviewers.value.find(u => u.id === id)
    if (realUser) {
      return {
        id: realUser.id,
        name: realUser.username,
        status: 'Pending', // Journal Platform Standard
        invitedAt: new Date().toISOString()
      }
    }
    
    // Check if it's a recommended reviewer
    const recReviewer = userStore.recommendedReviewers.find(r => r.id === id)
    if (recReviewer) {
       return {
         id: 'rec-' + recReviewer.id, // Temporary ID
         name: recReviewer.reviewerName,
         email: recReviewer.reviewerEmail,
         status: 'Pending', // Journal Platform Standard
         invitedAt: new Date().toISOString(),
         isExternal: true
       }
    }
    return null
  }).filter(Boolean)
  
  journal.reviewers = [...(journal.reviewers || []), ...newReviewers]
  
  userStore.updateJournal(journal)
  showModal.value = false
  alert(t('editor.audit.assignReviewers.alerts.assignedSuccess', { count: newReviewers.length }))
}

const handleReinvite = (journal) => {
  alert(t('editor.audit.assignReviewers.alerts.reinviteHint'))
}

</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-assign-reviewers" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>{{ t('editor.audit.assignReviewers.title') }}</h1>
        <p class="subtitle">{{ t('editor.audit.assignReviewers.subtitle') }}</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in assignmentJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title">{{ journal.title }}</h3>
            <div class="journal-meta">
              <span><strong>{{ t('editor.audit.assignReviewers.meta.writer') }}:</strong> {{ journal.writer }}</span>
              <span><strong>{{ t('editor.audit.assignReviewers.meta.module') }}:</strong> {{ journal.module }}</span>
            </div>
            <div class="tags">
               <span class="tag">AI</span> <span class="tag">Imaging</span> <!-- Mock tags -->
            </div>
          </div>
          <div class="journal-actions">
            <button class="btn btn-primary" @click="openAssignModal(journal)">{{ t('editor.audit.assignReviewers.actions.assign') }}</button>
            <button class="btn btn-secondary" @click="handleReinvite(journal)">{{ t('editor.audit.assignReviewers.actions.reinvite') }}</button>
          </div>
        </div>
        <div v-if="assignmentJournals.length === 0" class="no-data">
          {{ t('editor.audit.assignReviewers.noManuscripts') }}
        </div>
      </div>
    </main>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay">
      <div class="modal-content">
        <h2>{{ t('editor.audit.assignReviewers.modalTitle') }}</h2>
        
        <!-- Tabs -->
        <div class="modal-tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'recommended' }"
            @click="activeTab = 'recommended'"
          >
            👤 {{ t('editor.audit.assignReviewers.tabs.writerRecommended') }}
            <span v-if="writerRecommendedReviewers.length" class="badge-count">{{ writerRecommendedReviewers.length }}</span>
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'smart' }"
            @click="activeTab = 'smart'"
          >
            🤖 {{ t('editor.audit.assignReviewers.tabs.smartRecommendation') }}
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'manual' }"
            @click="activeTab = 'manual'"
          >
            🔍 {{ t('editor.audit.assignReviewers.tabs.manualSearch') }}
          </button>
        </div>

        <!-- Writer Recommended Tab -->
        <div v-if="activeTab === 'recommended'" class="tab-content">
          <div v-if="writerRecommendedReviewers.length === 0" class="no-data-tab">
            {{ t('editor.audit.assignReviewers.noWriterRecommendations') }}
            <p class="hint">{{ t('editor.audit.assignReviewers.writerRecommendationHint') }}</p>
          </div>
          <div v-else class="reviewer-list">
             <div v-for="reviewer in writerRecommendedReviewers" :key="reviewer.id" class="reviewer-item recommended-item">
               <label>
                 <div class="reviewer-info">
                   <span class="r-name">{{ reviewer.reviewerName }}</span>
                   <span class="r-email">{{ reviewer.reviewerEmail }}</span>
                   <span class="r-aff">{{ reviewer.reviewerAffiliation }}</span>
                   <div class="r-reason">{{ t('editor.audit.assignReviewers.reason') }}: {{ reviewer.recommendationReason }}</div>
                 </div>
               </label>
            </div>
          </div>
        </div>

        <!-- Smart Tab -->
        <div v-if="activeTab === 'smart'" class="tab-content">
          <IntelligentReviewerRecommendation 
            :manuscript="currentJournal" 
            @select="handleSmartSelect" 
          />
        </div>

        <!-- Manual Tab -->
        <div v-if="activeTab === 'manual'" class="tab-content manual-content">
          <div class="modal-search">
             <input v-model="searchQuery" :placeholder="t('editor.audit.assignReviewers.searchPlaceholder')" class="search-input" />
             <div class="filters">
               <label><input type="radio" v-model="filterMethod" value="all"> {{ t('editor.audit.assignReviewers.filters.all') }}</label>
               <label><input type="radio" v-model="filterMethod" value="field"> {{ t('editor.audit.assignReviewers.filters.matchField') }}</label>
             </div>
          </div>
          <div class="reviewer-list">
            <div v-for="reviewer in filteredReviewers" :key="reviewer.id" class="reviewer-item">
               <label>
                 <input type="checkbox" :value="reviewer.id" v-model="selectedReviewerIds">
                 <span class="r-name">{{ reviewer.fullName }}</span>
                 <span class="r-email">{{ reviewer.email }}</span>
               </label>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <div class="selection-count">{{ t('editor.audit.assignReviewers.selectionCount', { count: selectedReviewerIds.length }) }}</div>
          <div class="buttons">
            <button class="btn btn-secondary" @click="showModal = false">{{ t('common.cancel') }}</button>
            <button class="btn btn-primary" @click="confirmAssignment">{{ t('editor.audit.assignReviewers.actions.confirm') }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.audit-container { min-height: 100vh; background: #f5f7fa; display: flex; flex-direction: column; }
.content {
  flex: 1;
  max-width: 1200px;
  margin: 60px auto 0;
  padding: 2rem;
  width: 100%;
}
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

.no-data-tab { text-align: center; padding: 2rem; color: #999; }
.hint { font-size: 0.9rem; color: #3498db; margin-top: 0.5rem; }
.badge-count { background: #3498db; color: white; padding: 2px 6px; border-radius: 10px; font-size: 0.8rem; margin-left: 5px; }
.reviewer-info { flex: 1; display: flex; flex-direction: column; gap: 4px; padding: 10px; border-radius: 6px; background-color: #f9f9f9; }
.r-aff { font-size: 0.85rem; color: #666; }
.r-email { font-size: 0.85rem; color: #888; }
.r-reason { font-size: 0.85rem; color: #27ae60; font-style: italic; background: #f0fdf4; padding: 6px; border-radius: 4px; word-wrap: break-word; white-space: normal; }
.reviewer-item.recommended-item { padding: 8px 0; border-bottom: 1px solid #f9f9f9; }
.reviewer-item.recommended-item label { display: flex; align-items: flex-start; }
.reviewer-item.recommended-item .reviewer-info { flex: 1; min-width: 0; }

/* Modal */
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 1000; }
.modal-content { background: white; width: 700px; padding: 2rem; border-radius: 8px; max-height: 85vh; display: flex; flex-direction: column; }

/* Tabs */
.modal-tabs { display: flex; border-bottom: 1px solid #eee; margin-bottom: 1rem; }
.tab-btn { padding: 10px 20px; background: none; border: none; border-bottom: 2px solid transparent; cursor: pointer; font-size: 1rem; color: #666; }
.tab-btn.active { color: #3498db; border-bottom-color: #3498db; font-weight: bold; }
.tab-btn:hover { color: #3498db; }

.tab-content { flex: 1; overflow-y: auto; }
.manual-content { display: flex; flex-direction: column; min-height: 300px; }

.modal-search { display: flex; justify-content: space-between; margin-bottom: 1rem; }
.search-input { padding: 0.5rem; border: 1px solid #ddd; border-radius: 4px; width: 60%; }
.filters { display: flex; gap: 1rem; align-items: center; }
.reviewer-list { flex: 1; overflow-y: auto; border: 1px solid #eee; padding: 1rem; margin-bottom: 1rem; }
.reviewer-item { padding: 0.5rem 0; border-bottom: 1px solid #f9f9f9; }
.reviewer-item label { display: flex; align-items: center; gap: 0.8rem; cursor: pointer; }
.r-name { font-weight: bold; }
.r-email { color: #888; font-size: 0.9rem; }
.modal-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee; }
.modal-footer .buttons { display: flex; gap: 1rem; }
</style>
