<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import Navigation from '../../components/Navigation.vue'

const router = useRouter()
const userStore = useUserStore()
const user = computed(() => userStore.submissionUser || userStore.user)

const activeTab = ref('invitations') // invitations | decision | all

// Mock Data / Logic for Reviewer Letters
const letters = computed(() => {
  if (!user.value) return []
  
  const allLetters = []
  
  // 1. Invitations (Mock from Assignments)
  // Assuming assignments are in userStore or we filter journals where I am a reviewer
  // For now, let's look at `recommendedReviewers` in store if it exists, or just journals I'm reviewing
  
  // A. Review Invitations
  // In a real app, this would be a separate "notifications" or "invitations" table.
  // Here we simulate it based on journals assigned to me.
  const myReviews = userStore.journals.filter(j => 
    j.assignedReviewers && j.assignedReviewers.some(r => r.id === user.value.id || r.username === user.value.username)
  )
  
  myReviews.forEach(journal => {
    // Find my review status
    const myReview = journal.assignedReviewers.find(r => r.username === user.value.username)
    
    // Invitation Letter
    allLetters.push({
      id: `inv-${journal.id}`,
      type: 'invitation',
      title: `Review Invitation: ${journal.title}`,
      manuscriptId: journal.id,
      manuscriptTitle: journal.title,
      date: myReview?.invitedDate || journal.submittedDate || new Date().toISOString(), // Mock date
      content: `Dear ${user.value.username},

You have been invited to review the manuscript "${journal.title}" for Peerex Peer.

Abstract:
${journal.abstract || 'No abstract available.'}

Please log in to your reviewer dashboard to accept or decline this invitation.

Sincerely,
The Editors`,
      status: myReview?.status === 'pending' ? 'pending_action' : 'responded',
      actionLink: `/reviewer/manuscript/${journal.id}`
    })
    
    // Decision Notification (if decision made)
    if (journal.decision) {
      allLetters.push({
        id: `dec-notify-${journal.id}`,
        type: 'decision_notification',
        title: `Decision Notification: ${journal.title}`,
        manuscriptId: journal.id,
        manuscriptTitle: journal.title,
        date: journal.decision.date || new Date().toISOString(),
        content: `Dear Reviewer,

Thank you for your review of the manuscript "${journal.title}".

The editor has reached a decision: ${journal.decision.type}.
We appreciate your contribution to the peer review process.

Sincerely,
The Editors`,
        status: 'read'
      })
    } else if (journal.status === 'accepted' || journal.status === 'rejected' || journal.status === 'revision_required') {
        // Fallback for missing decision object but known status
        allLetters.push({
            id: `dec-notify-fallback-${journal.id}`,
            type: 'decision_notification',
            title: `Decision Notification: ${journal.title}`,
            manuscriptId: journal.id,
            manuscriptTitle: journal.title,
            date: journal.lastUpdated || new Date().toISOString(),
            content: `Dear Reviewer,

Thank you for your review of the manuscript "${journal.title}".

The editor has reached a decision: ${journal.status.toUpperCase().replace('_', ' ')}.
We appreciate your contribution to the peer review process.

Sincerely,
The Editors`,
            status: 'read'
        })
    }
  })

  return allLetters.sort((a, b) => new Date(b.date) - new Date(a.date))
})

const filteredLetters = computed(() => {
  if (activeTab.value === 'all') return letters.value
  if (activeTab.value === 'invitations') return letters.value.filter(l => l.type === 'invitation')
  if (activeTab.value === 'decision') return letters.value.filter(l => l.type === 'decision_notification')
  return []
})

// Actions
const viewLetter = (letter) => {
  selectedLetter.value = letter
  showModal.value = true
}

const handleAction = (letter) => {
  if (letter.actionLink) {
    router.push(letter.actionLink)
  }
}

// Modal State
const showModal = ref(false)
const selectedLetter = ref(null)

</script>

<template>
  <div class="letters-container">
    <Navigation :user="user" current-page="reviewer-letters" />

    <main class="content">
      <header class="page-header">
        <h2>Letters & Invitations</h2>
        <p class="subtitle">Reviewer Communication Center</p>
      </header>

      <div class="tabs">
        <button 
          :class="['tab-btn', { active: activeTab === 'invitations' }]" 
          @click="activeTab = 'invitations'"
        >
          Review Invitations
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'decision' }]" 
          @click="activeTab = 'decision'"
        >
          Decision Notifications
        </button>
        <button 
          :class="['tab-btn', { active: activeTab === 'all' }]" 
          @click="activeTab = 'all'"
        >
          All Communications
        </button>
      </div>

      <div class="letters-list">
        <div v-if="filteredLetters.length === 0" class="empty-state">
          No communications found.
        </div>
        
        <div v-for="letter in filteredLetters" :key="letter.id" class="letter-card" :class="{ 'unread': letter.status === 'pending_action' }">
          <div class="letter-icon">
            <span v-if="letter.type === 'invitation'">📨</span>
            <span v-else>📢</span>
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
                v-if="letter.type === 'invitation' && letter.status === 'pending_action'" 
                class="btn btn-primary"
                @click="handleAction(letter)"
              >
                Respond to Invitation
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
              <p><strong>Manuscript:</strong> {{ selectedLetter.manuscriptTitle }}</p>
            </div>
            <div class="letter-body">
              <pre>{{ selectedLetter.content }}</pre>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showModal = false">Close</button>
            <button 
               v-if="selectedLetter.type === 'invitation' && selectedLetter.status === 'pending_action'" 
               class="btn btn-primary"
               @click="handleAction(selectedLetter)"
            >
              Respond
            </button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.letters-container {
  min-height: 100vh;
  background-color: #f5f7fa;
  display: flex;
  flex-direction: column;
}

.content {
  max-width: 1000px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
  background: white;
  flex: 1;
}

.page-header {
  margin-bottom: 30px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.page-header h2 {
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
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
  color: #3498db;
  border-bottom-color: #3498db;
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
  border-left: 4px solid #3498db;
  background: #f0f7fb;
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
  background: #3498db;
  color: white;
}

.btn-primary:hover {
  background: #2980b9;
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

/* Responsive */
@media (max-width: 768px) {
  .content {
    padding: 1.5rem;
    margin-top: 70px;
  }
  
  .letter-card {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .letter-icon {
    font-size: 1.5rem;
  }
  
  .letter-actions {
    flex-wrap: wrap;
  }
}
</style>
