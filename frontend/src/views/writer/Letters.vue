<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'
import SubmissionNavigation from '../submission/components/SubmissionNavigation.vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.submissionUser || userStore.user)

const activeTab = ref('decision') // decision | acceptance | all

// Mock Data / Logic to extract letters from journals
const letters = computed(() => {
  if (!user.value) return []
  
  const allLetters = []
  
  // Filter journals where current user is writer
  const myJournals = userStore.journals.filter(j => 
    j.writer === user.value.username || 
    (j.author && j.author === user.value.username)
  )
  
  myJournals.forEach(journal => {
    // 1. Decision Letters (from Editor Decision)
    if (journal.decision) {
      allLetters.push({
        id: `dec-${journal.id}`,
        type: 'decision',
        title: `Decision on Manuscript ${journal.id}`,
        manuscriptId: journal.id,
        manuscriptTitle: journal.title,
        date: journal.decision.date || journal.lastUpdated,
        content: journal.decision.comments || 'No content available.',
        status: 'received',
        decisionType: journal.decision.type
      })
    } else {
        // Fallback: Check if we have a draft that might be relevant (Data Recovery)
        const draft = userStore.getDecisionDraft(journal.id)
        if (draft && (journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED || 
                      journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_REJECTED || 
                      journal.status === MANUSCRIPT_STATUS.FINAL_DECISION_REVISION)) {
             allLetters.push({
                id: `dec-recovered-${journal.id}`,
                type: 'decision',
                title: `Decision on Manuscript ${journal.id} (Recovered)`,
                manuscriptId: journal.id,
                manuscriptTitle: journal.title,
                date: draft.lastUpdated || new Date().toISOString(),
                content: draft.content || 'Content recovered from draft system.',
                status: 'recovered',
                decisionType: draft.templateType || 'Unknown'
             })
        }
    }
    
    // 2. Acceptance Letters (from Publication Module)
    if (journal.publicationData && journal.publicationData.acceptance && journal.publicationData.acceptance.confirmationSent) {
      allLetters.push({
        id: `acc-${journal.id}`,
        type: 'acceptance',
        title: `Acceptance Confirmation: ${journal.id}`,
        manuscriptId: journal.id,
        manuscriptTitle: journal.title,
        date: journal.publicationData.acceptance.confirmationDate || new Date().toISOString(),
        content: journal.publicationData.acceptance.acceptanceLetter || 'We are pleased to accept your manuscript.',
        status: journal.publicationData.acceptance.authorResponse === 'accepted' ? 'accepted' : 'pending_action',
        isActionRequired: journal.publicationData.acceptance.authorResponse !== 'accepted'
      })
    }

    // 3. Mock "Submission Acknowledgment" for all submitted manuscripts
    if (journal.submitDate) {
        allLetters.push({
            id: `sub-${journal.id}`,
            type: 'acknowledgment',
            title: `Submission Acknowledgment: ${journal.id}`,
            manuscriptId: journal.id,
            manuscriptTitle: journal.title,
            date: journal.submitDate,
            content: `Dear Author,\n\nThank you for submitting your manuscript "${journal.title}" to Journal Platform. Your submission ID is ${journal.id}.\n\nSincerely,\nThe Editorial Office`,
            status: 'read'
        })
    }
  })
  
  return allLetters.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const filteredLetters = computed(() => {
  if (activeTab.value === 'all') return letters.value
  if (activeTab.value === 'decision') return letters.value.filter(l => l.type === 'decision')
  if (activeTab.value === 'acceptance') return letters.value.filter(l => l.type === 'acceptance')
  return []
})

// Actions
const viewLetter = (letter) => {
  selectedLetter.value = letter
  showModal.value = true
}

const handleAccept = (letter) => {
  // Navigate to Publication Status page to perform action
  router.push({ name: 'writer-publication-status', params: { id: letter.manuscriptId } })
}

// Modal State
const showModal = ref(false)
const selectedLetter = ref(null)

</script>

<template>
  <div class="writer-letters-page">
    <SubmissionNavigation />
    <div class="letters-container">
      <header class="page-header">
      <h2>My Letters</h2>
      <p class="subtitle">Manage all your correspondence with the editorial office</p>
    </header>

    <div class="tabs">
      <button 
        :class="['tab-btn', { active: activeTab === 'decision' }]" 
        @click="activeTab = 'decision'"
      >
        Decision Letters
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'acceptance' }]" 
        @click="activeTab = 'acceptance'"
      >
        Acceptance Letters
      </button>
      <button 
        :class="['tab-btn', { active: activeTab === 'all' }]" 
        @click="activeTab = 'all'"
      >
        All Letters
      </button>
    </div>

    <div class="letters-list">
      <div v-if="filteredLetters.length === 0" class="empty-state">
        No letters found in this category.
      </div>
      
      <div v-for="letter in filteredLetters" :key="letter.id" class="letter-card" :class="{ 'unread': letter.status === 'pending_action' }">
        <div class="letter-icon">
          <span v-if="letter.type === 'acceptance'">🎉</span>
          <span v-else-if="letter.type === 'decision'">⚖️</span>
          <span v-else>✉️</span>
        </div>
        <div class="letter-content">
          <div class="letter-header">
            <h3 class="letter-title">{{ letter.title }}</h3>
            <span class="letter-date">{{ new Date(letter.date).toLocaleDateString() }}</span>
          </div>
          <p class="manuscript-ref">Ref: {{ letter.manuscriptTitle }}</p>
          <p class="preview-text">{{ letter.content.substring(0, 100) }}...</p>
          
          <div class="letter-actions">
            <button class="btn btn-outline" @click="viewLetter(letter)">Read Full Letter</button>
            <button 
              v-if="letter.isActionRequired" 
              class="btn btn-primary"
              @click="handleAccept(letter)"
            >
              Respond Now
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Letter Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ selectedLetter.title }}</h3>
          <button class="close-btn" @click="showModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="meta-info">
            <p><strong>Date:</strong> {{ new Date(selectedLetter.date).toLocaleString() }}</p>
            <p><strong>Manuscript:</strong> {{ selectedLetter.manuscriptTitle }} ({{ selectedLetter.manuscriptId }})</p>
          </div>
          <div class="letter-body">
            <pre>{{ selectedLetter.content }}</pre>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">Close</button>
          <button 
            v-if="selectedLetter.isActionRequired" 
            class="btn btn-primary"
            @click="handleAccept(selectedLetter)"
          >
            Proceed to Action
          </button>
        </div>
      </div>
    </div>
    </div>
  </div>
</template>

<style scoped>
.writer-letters-page {
  min-height: 100vh;
  background-color: #fff;
  font-family: Arial, sans-serif;
}

.letters-container {
  max-width: 1000px;
  margin: 0 auto 40px; /* Remove top margin to rely on padding for consistency */
  padding: 2rem 20px 20px; /* Add top padding to match Dashboard gap (Nav margin 20px + Padding 32px = ~52px) */
  background: white;
  min-height: 80vh;
}

.page-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.page-header h2 {
  font-family: 'Georgia', serif;
  color: #2c3e50;
  margin-bottom: 5px;
}

.subtitle {
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.tab-btn {
  padding: 10px 20px;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
}

.tab-btn.active {
  color: #C93737;
  border-bottom-color: #C93737;
  font-weight: bold;
}

/* List */
.letters-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.letter-card {
  display: flex;
  gap: 20px;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s;
}

.letter-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  transform: translateY(-2px);
}

.letter-card.unread {
  border-left: 4px solid #C93737;
  background: #fff9f9;
}

.letter-icon {
  font-size: 2rem;
  padding-top: 5px;
}

.letter-content {
  flex: 1;
}

.letter-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.letter-title {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.letter-date {
  color: #999;
  font-size: 0.9rem;
}

.manuscript-ref {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 10px;
  font-style: italic;
}

.preview-text {
  color: #555;
  margin-bottom: 15px;
  line-height: 1.5;
}

.letter-actions {
  display: flex;
  gap: 10px;
}

/* Buttons */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  transition: 0.2s;
}

.btn-primary {
  background: #C93737;
  color: white;
}

.btn-primary:hover {
  background: #a02626;
}

.btn-outline {
  background: white;
  border: 1px solid #ddd;
  color: #333;
}

.btn-outline:hover {
  border-color: #aaa;
  background: #f5f5f5;
}

.btn-secondary {
  background: #eee;
  color: #333;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 600px;
  max-width: 90%;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: 85vh;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.meta-info {
  background: #f9f9f9;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  font-size: 0.9rem;
}

.meta-info p {
  margin: 5px 0;
}

.letter-body pre {
  white-space: pre-wrap;
  font-family: inherit;
  color: #333;
  line-height: 1.6;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
  background: #f9f9f9;
  border-radius: 8px;
}
</style>
