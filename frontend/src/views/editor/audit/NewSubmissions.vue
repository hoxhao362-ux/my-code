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

// Screening Modal Logic
const showScreeningModal = ref(false)
const currentJournal = ref(null)
const screeningChecklist = ref({
  ethics: false,
  coi: false,
  format: false,
  blind: false
})
const scanning = ref(false)
const scanResult = ref(null)

const openScreeningModal = (journal) => {
  currentJournal.value = journal
  screeningChecklist.value = { ethics: false, coi: false, format: false, blind: false }
  scanResult.value = null
  showScreeningModal.value = true
}

const runAutoScan = () => {
  scanning.value = true
  setTimeout(() => {
    scanning.value = false
    // Mock Result: 90% chance success
    const success = Math.random() > 0.1
    scanResult.value = success ? 
      { status: 'pass', message: '✅ No author identifiers found in manuscript metadata. References appear neutral.' } : 
      { status: 'fail', message: '⚠️ Detected potential author name "Zhang San" in PDF properties.' }
    
    if (success) {
      screeningChecklist.value.blind = true
    }
  }, 1500)
}

const confirmScreening = () => {
  if (!Object.values(screeningChecklist.value).every(v => v)) {
    alert('Please complete all screening checks before proceeding.')
    return
  }

  // Move to "Assign Reviewers" stage
  const updatedJournal = { ...currentJournal.value }
  updatedJournal.status = 'Pending Assignment' 
  userStore.updateJournal(updatedJournal)
  
  // Log
  userStore.addSystemLog({
    type: 'operation',
    user: user.value?.username || 'editor',
    action: 'Screening Passed',
    target: `Manuscript ID: ${updatedJournal.id}`,
    ip: '127.0.0.1'
  })

  showScreeningModal.value = false
  alert('Screening passed. Moved to Assign Reviewers list.')
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
            <button class="btn btn-primary" @click="openScreeningModal(journal)">Screen & Send</button>
            <button class="btn btn-warning" @click="handleTransfer(journal)">Suggest Transfer</button>
            <button class="btn btn-danger" @click="handleReject(journal)">Reject</button>
          </div>
        </div>
        <div v-if="pendingJournals.length === 0" class="no-data">
          No new submissions pending screening.
        </div>
      </div>
    </main>

    <!-- Screening Modal -->
    <div v-if="showScreeningModal" class="modal-overlay">
      <div class="modal-content">
        <h2>Initial Screening Checklist</h2>
        <p class="modal-subtitle">Manuscript: {{ currentJournal?.title }}</p>

        <div class="checklist">
          <label class="check-item">
            <input type="checkbox" v-model="screeningChecklist.ethics">
            <span><strong>Ethics Compliance:</strong> Ethics statement and approval number present.</span>
          </label>
          <label class="check-item">
            <input type="checkbox" v-model="screeningChecklist.coi">
            <span><strong>COI Declaration:</strong> Conflict of Interest form is complete.</span>
          </label>
          <label class="check-item">
            <input type="checkbox" v-model="screeningChecklist.format">
            <span><strong>Format Check:</strong> Meets submission guidelines (Word count, Figure quality).</span>
          </label>
          
          <div class="blind-check-section">
            <div class="check-header">
              <label class="check-item">
                <input type="checkbox" v-model="screeningChecklist.blind">
                <span><strong>Double-Blind Compliance:</strong> Manuscript is anonymized.</span>
              </label>
              <button class="btn-scan" @click="runAutoScan" :disabled="scanning">
                {{ scanning ? 'Scanning...' : 'Run Auto-Scan' }}
              </button>
            </div>
            
            <div v-if="scanning" class="scan-progress">
              <div class="spinner-mini"></div> Analyzing PDF metadata and text patterns...
            </div>
            
            <div v-if="scanResult" class="scan-result" :class="scanResult.status">
              {{ scanResult.message }}
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showScreeningModal = false">Cancel</button>
          <button class="btn btn-primary" @click="confirmScreening">Pass Screening & Assign</button>
        </div>
      </div>
    </div>
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
.btn-secondary { background: #95a5a6; }
.no-data {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border-radius: 8px;
}

/* Modal */
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  width: 600px;
  padding: 2rem;
  border-radius: 8px;
}
.modal-subtitle {
  color: #666;
  margin-bottom: 1.5rem;
}
.checklist {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 2rem;
}
.check-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 4px;
}
.check-item:hover {
  background: #f0f0f0;
}
.blind-check-section {
  border: 1px solid #e1e4e8;
  padding: 10px;
  border-radius: 4px;
  background: #fcfcfc;
}
.check-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.btn-scan {
  background: #6c757d;
  color: white;
  border: none;
  padding: 4px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-scan:hover { background: #5a6268; }
.scan-progress {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #666;
  font-size: 0.9rem;
  margin-top: 10px;
}
.spinner-mini {
  width: 16px;
  height: 16px;
  border: 2px solid #ddd;
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 1s infinite linear;
}
.scan-result {
  margin-top: 10px;
  padding: 8px;
  border-radius: 4px;
  font-size: 0.9rem;
}
.scan-result.pass {
  background: #d4edda;
  color: #155724;
}
.scan-result.fail {
  background: #f8d7da;
  color: #721c24;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
