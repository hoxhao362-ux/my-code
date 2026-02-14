<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'
import { stripHtmlTags, truncateText } from '../../../utils/helpers.js'

const userStore = useUserStore()
const router = useRouter()
const user = computed(() => userStore.user)

// Filter for New Submissions (Submitted, Pending Screening)
const pendingJournals = computed(() => {
  return userStore.journals.filter(journal => 
    journal.status === '待审核' || journal.status === 'Submitted' || journal.status === 'Pending Screening'
  )
})

const handleReject = (journal) => {
  if (confirm('Are you sure you want to reject this submission?')) {
    const updatedJournal = { ...journal }
    updatedJournal.status = 'Rejected' // English status
    userStore.updateJournal(updatedJournal)
    alert('Submission rejected.')
  }
}

const handleSendToReview = (journal) => {
  // Move to "Assign Reviewers" stage
  const updatedJournal = { ...journal }
  updatedJournal.status = 'Pending Assignment' 
  userStore.updateJournal(updatedJournal)
  alert('Moved to Assign Reviewers list.')
}

const handleTransfer = (journal) => {
  if (confirm('Suggest transfer to another journal? (Requires EIC confirmation)')) {
    const updatedJournal = { ...journal }
    updatedJournal.status = 'Transfer Suggested'
    userStore.updateJournal(updatedJournal)
    alert('Transfer suggestion recorded.')
  }
}

const viewDetail = (id) => {
  router.push(`/admin/journal/${id}`)
}
</script>

<template>
  <div class="audit-container">
    <Navigation :user="user" current-page="audit-new-submissions" :toggle-directory="()=>{}" :logout="userStore.logout" />
    
    <main class="content">
      <div class="header">
        <h1>New Submissions</h1>
        <p class="subtitle">Screening & Initial Check</p>
      </div>

      <div class="journals-list">
        <div v-for="journal in pendingJournals" :key="journal.id" class="journal-item">
          <div class="journal-info">
            <h3 class="journal-title" @click="viewDetail(journal.id)">{{ journal.title }}</h3>
            <div class="journal-meta">
              <span><strong>Writer:</strong> {{ journal.author }}</span>
              <span><strong>Date:</strong> {{ journal.date }}</span>
              <span><strong>Module:</strong> {{ journal.module }}</span>
            </div>
            <p class="journal-abstract">{{ truncateText(stripHtmlTags(journal.abstract), 200) }}</p>
            <div class="materials-links">
              <a href="#" @click.prevent class="link">View Manuscript</a>
              <a href="#" @click.prevent class="link">View Attachments</a>
              <a href="#" @click.prevent class="link">Ethics Statement</a>
            </div>
          </div>
          <div class="journal-actions">
            <button class="btn btn-primary" @click="handleSendToReview(journal)">Send to Review</button>
            <button class="btn btn-warning" @click="handleTransfer(journal)">Suggest Transfer</button>
            <button class="btn btn-danger" @click="handleReject(journal)">Reject</button>
          </div>
        </div>
        <div v-if="pendingJournals.length === 0" class="no-data">
          No new submissions pending screening.
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.audit-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
}
.content {
  flex: 1;
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 2rem;
  width: 100%;
}
.header {
  margin-bottom: 2rem;
  border-bottom: 1px solid #ddd;
  padding-bottom: 1rem;
}
.header h1 {
  font-size: 1.8rem;
  color: #2c3e50;
  margin: 0;
}
.subtitle {
  color: #7f8c8d;
  margin-top: 0.5rem;
}
.journal-item {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 1.5rem;
  display: flex;
  gap: 2rem;
}
.journal-info {
  flex: 1;
}
.journal-title {
  color: #2c3e50;
  font-size: 1.2rem;
  cursor: pointer;
  margin-bottom: 0.5rem;
}
.journal-title:hover {
  color: #3498db;
}
.journal-meta {
  display: flex;
  gap: 1.5rem;
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1rem;
}
.journal-abstract {
  color: #555;
  line-height: 1.6;
  margin-bottom: 1rem;
}
.materials-links {
  display: flex;
  gap: 1rem;
}
.link {
  color: #3498db;
  text-decoration: none;
  font-size: 0.9rem;
}
.link:hover {
  text-decoration: underline;
}
.journal-actions {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  min-width: 150px;
}
.btn {
  padding: 0.6rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  color: white;
}
.btn-primary { background: #3498db; }
.btn-primary:hover { background: #2980b9; }
.btn-warning { background: #f39c12; }
.btn-warning:hover { background: #e67e22; }
.btn-danger { background: #e74c3c; }
.btn-danger:hover { background: #c0392b; }
.no-data {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border-radius: 8px;
}
</style>
