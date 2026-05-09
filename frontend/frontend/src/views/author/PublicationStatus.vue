<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { MANUSCRIPT_STATUS, STATUS_LABELS, STATUS_COLORS } from '../../constants/manuscriptStatus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const toastStore = useToastStore()

// State
const manuscript = ref(null)
const currentUser = computed(() => userStore.submissionUser || userStore.user)
const isLoading = ref(false)
const errorMessage = ref('')

// Computed
const currentStageKey = computed(() => {
  if (!manuscript.value) return 'acceptance'
  
  switch (manuscript.value.status) {
    case MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION:
      return 'acceptance'
    case MANUSCRIPT_STATUS.PENDING_COPYRIGHT:
      return 'copyright'
    case MANUSCRIPT_STATUS.PENDING_PROOF:
      return 'proof'
    case MANUSCRIPT_STATUS.PENDING_PUBLICATION:
      return 'publication'
    case MANUSCRIPT_STATUS.PUBLISHED:
      return 'published'
    default:
      return 'acceptance'
  }
})

const stageProgress = computed(() => {
  const stages = [
    { key: 'acceptance', label: 'Acceptance Confirmation', status: 'pending' },
    { key: 'copyright', label: 'Copyright Agreement', status: 'pending' },
    { key: 'proof', label: 'Proof Correction', status: 'pending' },
    { key: 'publication', label: 'Final Publication', status: 'pending' }
  ]
  
  const stageKeys = ['acceptance', 'copyright', 'proof', 'publication', 'published']
  const currentIndex = stageKeys.indexOf(currentStageKey.value)
  
  stages.forEach((stage, index) => {
    if (index < currentIndex) stage.status = 'completed'
    else if (index === currentIndex && currentStageKey.value !== 'published') stage.status = 'current'
    else if (currentStageKey.value === 'published') stage.status = 'completed'
  })
  
  return stages
})

// Methods
const loadManuscript = () => {
  const id = route.params.id
  if (!id) return
  
  const found = userStore.journals.find(j => String(j.id) === String(id))
  if (found) {
    // Security check: Ensure author is the owner
    if (found.author !== currentUser.value.username && currentUser.value.role !== 'admin') {
       errorMessage.value = 'Access Denied: You are not the author of this manuscript.'
       return
    }
    manuscript.value = found
  } else {
    errorMessage.value = 'Manuscript not found'
  }
}

const updateStatus = (newStatus, data = {}) => {
  if (!manuscript.value) return
  
  const updatedManuscript = {
    ...manuscript.value,
    status: newStatus,
    publicationData: {
      ...manuscript.value.publicationData,
      ...data
    },
    lastUpdated: new Date().toISOString()
  }
  
  userStore.updateJournal(updatedManuscript)
  manuscript.value = updatedManuscript
  
  userStore.addSystemLog({
    type: 'operation',
    user: currentUser.value.username,
    action: `Author Action: ${newStatus}`,
    target: `Manuscript ID: ${manuscript.value.id}`,
    status: 'success'
  })
}

// Actions
const confirmAcceptance = () => {
  if (!confirm('Confirm that you accept the publication offer?')) return
  
  updateStatus(MANUSCRIPT_STATUS.PENDING_COPYRIGHT, {
    authorResponse: 'accepted',
    authorAcceptedAt: new Date().toISOString()
  })
  toastStore.add({ message: 'Acceptance Confirmed. Proceeding to Copyright Agreement.', type: 'success' })
}

const signCopyright = () => {
  if (!confirm('Confirm that you have read and signed the copyright agreement?')) return
  
  updateStatus(MANUSCRIPT_STATUS.PENDING_PROOF, {
    agreementSigned: true,
    copyrightSignedAt: new Date().toISOString()
  })
  toastStore.add({ message: 'Copyright Agreement Signed. Waiting for Proofs.', type: 'success' })
}

const confirmProof = () => {
  if (!confirm('Confirm that the proofs are correct and ready for publication?')) return
  
  updateStatus(MANUSCRIPT_STATUS.PENDING_PUBLICATION, {
    proofConfirmed: true,
    proofConfirmedAt: new Date().toISOString()
  })
  toastStore.add({ message: 'Proofs Confirmed. Waiting for Final Publication.', type: 'success' })
}

const requestCorrections = () => {
  toastStore.add({ message: 'Please contact the editor via email for corrections.', type: 'info' })
}

const goBack = () => {
  router.push({ name: 'admin-author-dashboard' })
}

onMounted(() => {
  loadManuscript()
})
</script>

<template>
  <div class="author-publication-page" v-if="manuscript">
    <header class="page-header">
      <button class="btn-back" @click="goBack">← Back to Dashboard</button>
      <h2>Publication Status</h2>
      <div class="meta">
        <span>ID: {{ manuscript.id }}</span>
        <span>Title: {{ manuscript.title }}</span>
      </div>
    </header>
    
    <!-- Progress Bar -->
    <div class="progress-bar">
      <div 
        v-for="stage in stageProgress" 
        :key="stage.key"
        class="progress-item"
        :class="stage.status"
      >
        <div class="progress-dot"></div>
        <div class="progress-label">{{ stage.label }}</div>
      </div>
    </div>
    
    <!-- Content Area -->
    <div class="content-card">
      
      <!-- Stage 1: Acceptance -->
      <div v-if="currentStageKey === 'acceptance'" class="stage-section">
        <h3>🎉 Congratulations! Your manuscript has been accepted.</h3>
        
        <div class="letter-box" v-if="manuscript.publicationData?.acceptance?.acceptanceLetter">
          <h4>Acceptance Letter</h4>
          <pre>{{ manuscript.publicationData.acceptance.acceptanceLetter }}</pre>
        </div>
        
        <p>Please confirm your intent to publish.</p>
        
        <div class="action-box">
          <div class="info-row">
            <span class="label">Status:</span>
            <span class="value">Waiting for Author Confirmation</span>
          </div>
          <button class="btn btn-primary" @click="confirmAcceptance">Confirm Acceptance</button>
        </div>
      </div>
      
      <!-- Stage 2: Copyright -->
      <div v-else-if="currentStageKey === 'copyright'" class="stage-section">
        <h3>Copyright Agreement</h3>
        <p>Please sign the copyright agreement to proceed.</p>
        
        <div class="letter-box" v-if="manuscript.publicationData?.copyright?.notes">
          <h4>Editor's Notes</h4>
          <pre>{{ manuscript.publicationData.copyright.notes }}</pre>
        </div>
        
        <div class="action-box">
          <div class="info-row">
            <span class="label">Agreement Status:</span>
            <span class="value">Sent to Author</span>
          </div>
          <p class="note">Note: This is a simplified confirmation. By clicking below, you acknowledge the copyright terms.</p>
          <button class="btn btn-primary" @click="signCopyright">Sign Copyright Agreement</button>
        </div>
      </div>
      
      <!-- Stage 3: Proof -->
      <div v-else-if="currentStageKey === 'proof'" class="stage-section">
        <h3>Proof Correction</h3>
        <p>The editorial team has prepared the proofs. Please review them carefully.</p>
        
        <div class="action-box">
          <div class="info-row">
             <span class="label">Proof Files:</span>
             <a href="#" class="link">Download Proof PDF</a>
          </div>
          <button class="btn btn-primary" @click="confirmProof">Confirm Proofs</button>
          <button class="btn btn-outline" @click="requestCorrections">Request Corrections</button>
        </div>
      </div>
      
      <!-- Stage 4: Publication Pending -->
      <div v-else-if="currentStageKey === 'publication'" class="stage-section">
        <h3>Waiting for Publication</h3>
        <p>You have completed all author steps. The editorial team is finalizing the publication details.</p>
        <div class="status-box pending">
           In Production Queue
        </div>
      </div>
      
      <!-- Stage 5: Published -->
      <div v-else-if="currentStageKey === 'published'" class="stage-section">
        <h3>✨ Published</h3>
        <p>Your manuscript has been officially published.</p>
        
        <div class="publication-details">
           <div class="detail-item">
             <label>Date</label>
             <span>{{ manuscript.publicationData?.publicationDate || 'N/A' }}</span>
           </div>
           <div class="detail-item">
             <label>Volume</label>
             <span>{{ manuscript.publicationData?.volume || 'N/A' }}</span>
           </div>
           <div class="detail-item">
             <label>Issue</label>
             <span>{{ manuscript.publicationData?.issue || 'N/A' }}</span>
           </div>
           <div class="detail-item">
             <label>Pages</label>
             <span>{{ manuscript.publicationData?.pageRange || 'N/A' }}</span>
           </div>
           <div class="detail-item">
             <label>DOI</label>
             <span>{{ manuscript.publicationData?.doi || 'N/A' }}</span>
           </div>
        </div>
      </div>
      
    </div>
  </div>
  <div v-else-if="errorMessage" class="error-page">
    {{ errorMessage }}
    <button @click="goBack">Back</button>
  </div>
</template>

<style scoped>
.author-publication-page {
  max-width: 900px;
  margin: 40px auto;
  padding: 20px;
  font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
}

.page-header {
  margin-bottom: 40px;
  border-bottom: 1px solid #eee;
  padding-bottom: 20px;
}

.btn-back {
  background: none;
  border: none;
  color: #666;
  cursor: pointer;
  margin-bottom: 10px;
  padding: 0;
  font-size: 14px;
}

.btn-back:hover {
  text-decoration: underline;
}

.meta {
  color: #888;
  font-size: 14px;
  margin-top: 5px;
}

.meta span {
  margin-right: 20px;
}

/* Progress Bar */
.progress-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 40px;
  padding: 0 20px;
}

.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
}

.progress-item::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #eee;
  z-index: 0;
}

.progress-item:last-child::before {
  display: none;
}

.progress-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #eee;
  z-index: 1;
  margin-bottom: 10px;
  border: 2px solid white;
}

.progress-label {
  font-size: 12px;
  color: #999;
  text-align: center;
}

.progress-item.completed .progress-dot {
  background: #4caf50;
}

.progress-item.completed::before {
  background: #4caf50;
}

.progress-item.completed .progress-label {
  color: #4caf50;
}

.progress-item.current .progress-dot {
  background: #2196f3;
  box-shadow: 0 0 0 4px rgba(33, 150, 243, 0.2);
}

.progress-item.current .progress-label {
  color: #2196f3;
  font-weight: bold;
}

/* Content Card */
.content-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 40px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.stage-section h3 {
  margin-top: 0;
  color: #333;
}

.action-box {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 6px;
  margin-top: 20px;
  border: 1px solid #eee;
}

.info-row {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.label {
  font-weight: bold;
  color: #555;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-outline {
  background: white;
  border: 1px solid #ddd;
  color: #666;
  margin-left: 10px;
}

.note {
  font-size: 12px;
  color: #888;
  margin-bottom: 15px;
  font-style: italic;
}

.publication-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 20px;
  margin-top: 20px;
  background: #f5f5f5;
  padding: 20px;
  border-radius: 6px;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item label {
  font-size: 12px;
  color: #888;
  margin-bottom: 5px;
}

.detail-item span {
  font-weight: bold;
  color: #333;
}

.status-box.pending {
  background: #e3f2fd;
  color: #1565c0;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
  font-weight: bold;
}

.error-page {
  padding: 40px;
  text-align: center;
  color: #d32f2f;
}

.letter-box {
  background: #f8f9fa;
  border: 1px solid #eee;
  padding: 20px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.letter-box h4 {
  margin-top: 0;
  color: #555;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
  margin-bottom: 10px;
}

pre {
  white-space: pre-wrap;
  font-family: inherit;
  color: #333;
  margin: 0;
  line-height: 1.6;
}
</style>