<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '../../../stores/user'
import { useToastStore } from '../../../stores/toast'
import { useRoute, useRouter } from 'vue-router'
import { MANUSCRIPT_STATUS, STATUS_LABELS, STATUS_COLORS } from '../../../constants/manuscriptStatus'
import Navigation from '../../../components/Navigation.vue'

const props = defineProps({
  embedded: {
    type: Boolean,
    default: false
  }
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const toastStore = useToastStore()

// State
const manuscript = ref(null)
const currentUser = computed(() => userStore.submissionUser || userStore.user)
const currentStage = ref('acceptance') // acceptance, copyright, proof, publication
const isLoading = ref(false)
const errorMessage = ref('')

// Form Data
const forms = ref({
  acceptance: {
    confirmationSent: false,
    confirmationDate: '',
    acceptanceLetter: '',
    authorResponse: 'accepted', // accepted, declined
    responseDate: ''
  },
  copyright: {
    agreementSent: false,
    agreementSentDate: '',
    agreementSigned: false,
    signedDate: '',
    notes: ''
  },
  proof: {
    proofSent: false,
    proofSentDate: '',
    proofConfirmed: false,
    confirmedDate: '',
    corrections: ''
  },
  publication: {
    publicationDate: '',
    volume: '',
    issue: '',
    pageRange: '',
    doi: '',
    isPublished: false
  }
})

// Computed
const stageProgress = computed(() => {
  const stages = [
    { key: 'acceptance', label: 'Acceptance Confirmation', status: 'pending' },
    { key: 'copyright', label: 'Copyright Agreement', status: 'pending' },
    { key: 'proof', label: 'Proof Correction', status: 'pending' },
    { key: 'publication', label: 'Final Publication', status: 'pending' }
  ]
  
  const currentIndex = stages.findIndex(s => s.key === currentStage.value)
  stages.forEach((stage, index) => {
    if (index < currentIndex) stage.status = 'completed'
    else if (index === currentIndex) stage.status = 'current'
  })
  
  return stages
})

const canProceed = computed(() => {
  switch (currentStage.value) {
    case 'acceptance':
      return forms.value.acceptance.confirmationSent && forms.value.acceptance.authorResponse === 'accepted'
    case 'copyright':
      return forms.value.copyright.agreementSent && forms.value.copyright.agreementSigned
    case 'proof':
      return forms.value.proof.proofSent && forms.value.proof.proofConfirmed
    case 'publication':
      return forms.value.publication.publicationDate && forms.value.publication.volume && forms.value.publication.issue
    default:
      return false
  }
})

const canGoBack = computed(() => {
  return currentStage.value !== 'acceptance'
})

// Methods
const loadManuscript = () => {
  const id = route.params.id
  if (!id) {
    errorMessage.value = 'No manuscript ID provided'
    return
  }
  
  const found = userStore.journals.find(j => String(j.id) === String(id))
  if (found) {
    manuscript.value = found
    // Load existing publication data if any
    if (found.publicationData) {
      forms.value = { ...forms.value, ...found.publicationData }
    } else {
      // Pre-fill with templates
      forms.value.acceptance.acceptanceLetter = `Dear ${found.author || found.writer || 'Author'},

Re: Manuscript ID ${found.id}
Title: ${found.title}

We are pleased to confirm that your manuscript has been accepted for publication in Peerex Peer.

The next steps in the publication process are as follows:
1. Copyright Agreement: You will receive a copyright transfer agreement which must be signed by the corresponding author.
2. Proofs: Our production team will prepare the proofs of your article. You will receive a PDF for review.
3. Publication: Once proofs are approved, your article will be scheduled for publication.

Thank you for choosing Peerex Peer for your work.

Sincerely,

The Editors
Peerex Peer`

      forms.value.copyright.notes = `Please review the attached Copyright Transfer Agreement. 
By signing this agreement, you transfer the copyright of the accepted manuscript to Peerex Peer.
For Open Access (OA) publishing, please contact the editorial office for separate arrangements.`
    }
    
    // Set initial stage based on status
    switch (found.status) {
      case MANUSCRIPT_STATUS.FINAL_DECISION_ACCEPTED:
      case MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION:
        currentStage.value = 'acceptance'
        break
      case MANUSCRIPT_STATUS.PENDING_COPYRIGHT:
        currentStage.value = 'copyright'
        break
      case MANUSCRIPT_STATUS.PENDING_PROOF:
        currentStage.value = 'proof'
        break
      case MANUSCRIPT_STATUS.PENDING_PUBLICATION:
        currentStage.value = 'publication'
        break
      case MANUSCRIPT_STATUS.PUBLISHED:
        currentStage.value = 'publication'
        forms.value.publication.isPublished = true
        break
    }
  } else {
    errorMessage.value = 'Manuscript not found. Please select a manuscript from the list first.'
  }
}

const handleNextStage = () => {
  if (!canProceed.value) return
  
  switch (currentStage.value) {
    case 'acceptance':
      currentStage.value = 'copyright'
      updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_COPYRIGHT)
      break
    case 'copyright':
      currentStage.value = 'proof'
      updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_PROOF)
      break
    case 'proof':
      currentStage.value = 'publication'
      updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_PUBLICATION)
      break
    case 'publication':
      handlePublish()
      break
  }
}

const handlePreviousStage = () => {
  switch (currentStage.value) {
    case 'copyright':
      currentStage.value = 'acceptance'
      updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION)
      break
    case 'proof':
      currentStage.value = 'copyright'
      updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_COPYRIGHT)
      break
    case 'publication':
      currentStage.value = 'proof'
      updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_PROOF)
      break
  }
}

const handlePublish = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    // Simulate publication process
    await new Promise(resolve => setTimeout(resolve, 1500))
    
    forms.value.publication.isPublished = true
    updateManuscriptStatus(MANUSCRIPT_STATUS.PUBLISHED)
    
    // Add system log
    userStore.addSystemLog({
      type: 'operation',
      user: currentUser.value.username,
      action: 'Publish Manuscript',
      target: `Manuscript ID: ${manuscript.value.id}`,
      status: 'success'
    })
    
    toastStore.add({ message: 'Manuscript published successfully!', type: 'success' })
    router.push({ name: 'editor-manuscripts' })
  } catch (error) {
    errorMessage.value = 'Failed to publish manuscript'
    console.error('Publication error:', error)
  } finally {
    isLoading.value = false
  }
}

const updateManuscriptStatus = (newStatus) => {
  if (!manuscript.value) return
  
  const updatedManuscript = {
    ...manuscript.value,
    status: newStatus,
    publicationData: forms.value, // Persist publication data
    lastUpdated: new Date().toISOString()
  }
  
  userStore.updateJournal(updatedManuscript)
  manuscript.value = updatedManuscript
}

const handleSaveDraft = () => {
  if (!manuscript.value) return
  
  const updatedManuscript = {
    ...manuscript.value,
    publicationData: forms.value,
    lastUpdated: new Date().toISOString()
  }
  userStore.updateJournal(updatedManuscript)
  toastStore.add({ message: 'Draft saved successfully', type: 'success' })
}

const handleAcceptanceConfirmation = () => {
  forms.value.acceptance.confirmationSent = true
  forms.value.acceptance.confirmationDate = new Date().toISOString()
  // Mock author response for now, in real flow author would do this
  // But here editor is managing it manually or waiting
  // The requirement says "Editor sends notice" -> "Author confirms"
  // Here we are in Editor view. Editor sends notice.
  // We should wait for author.
  // But for now let's just mark sent.
  updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_ACCEPTANCE_CONFIRMATION)
}

const handleCopyrightAgreement = () => {
  forms.value.copyright.agreementSent = true
  forms.value.copyright.agreementSentDate = new Date().toISOString()
  updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_COPYRIGHT)
}

const handleProofSent = () => {
  forms.value.proof.proofSent = true
  forms.value.proof.proofSentDate = new Date().toISOString()
  updateManuscriptStatus(MANUSCRIPT_STATUS.PENDING_PROOF)
}

const goBack = () => {
  router.back()
}

// Initialize
onMounted(() => {
  loadManuscript()
})
</script>

<template>
  <div class="publication-page-wrapper">
    <Navigation 
      v-if="!embedded"
      :user="userStore.user"
      :current-page="'editor-publication-process'"
      :logout="userStore.logout"
    />
    <div class="publication-process-container" :class="{ 'embedded-mode': embedded }" v-if="manuscript">
    <header class="page-header">
      <div class="header-content">
        <button class="btn-back" @click="goBack">← Back</button>
        <h2>Publication Process</h2>
      </div>
      <div class="meta">
        <span>ID: {{ manuscript.id }}</span>
        <span>Title: {{ manuscript.title }}</span>
        <span>Current Status: <span :style="{ color: STATUS_COLORS[manuscript.status] }">{{ STATUS_LABELS[manuscript.status] }}</span></span>
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
    
    <!-- Error Message -->
    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>
    
    <!-- Acceptance Confirmation Stage -->
    <div v-if="currentStage === 'acceptance'" class="stage-content">
      <h3>1. Acceptance Confirmation</h3>
      <div class="form-section">
        <div class="form-group">
          <label class="label">Acceptance Letter</label>
          <textarea 
            v-model="forms.acceptance.acceptanceLetter"
            placeholder="Enter acceptance letter content..."
            rows="6"
          ></textarea>
        </div>
        
        <div class="form-group">
          <label class="label">Actions</label>
          <button 
            class="btn btn-primary"
            @click="handleAcceptanceConfirmation"
            :disabled="forms.acceptance.confirmationSent"
          >
            {{ forms.acceptance.confirmationSent ? 'Confirmation Sent' : 'Send Acceptance Confirmation' }}
          </button>
        </div>
        
        <div class="form-group" v-if="forms.acceptance.confirmationSent">
          <label class="label">Author Response</label>
          <div class="radio-group">
            <label>
              <input type="radio" v-model="forms.acceptance.authorResponse" value="accepted"> Accepted
            </label>
            <label>
              <input type="radio" v-model="forms.acceptance.authorResponse" value="declined"> Declined
            </label>
          </div>
        </div>
        
        <div class="form-group" v-if="forms.acceptance.confirmationSent">
          <label class="label">Response Date</label>
          <input 
            type="date" 
            v-model="forms.acceptance.responseDate"
          >
        </div>
      </div>
    </div>
    
    <!-- Copyright Agreement Stage -->
    <div v-if="currentStage === 'copyright'" class="stage-content">
      <h3>2. Copyright Agreement</h3>
      <div class="form-section">
        <div class="form-group">
          <label class="label">Copyright Agreement</label>
          <p class="info-text">
            <strong>Note:</strong> 版权与开放获取（OA）相关功能暂不实现，包括版权转让协议、OA 模式、DOI 号自动分配。
          </p>
        </div>
        
        <div class="form-group">
          <label class="label">Actions</label>
          <button 
            class="btn btn-primary"
            @click="handleCopyrightAgreement"
            :disabled="forms.copyright.agreementSent"
          >
            {{ forms.copyright.agreementSent ? 'Agreement Sent' : 'Send Copyright Agreement' }}
          </button>
        </div>
        
        <div class="form-group" v-if="forms.copyright.agreementSent">
          <label class="label">Agreement Status</label>
          <div class="radio-group">
            <label>
              <input type="radio" v-model="forms.copyright.agreementSigned" :value="true"> Signed
            </label>
            <label>
              <input type="radio" v-model="forms.copyright.agreementSigned" :value="false"> Not Signed
            </label>
          </div>
        </div>
        
        <div class="form-group" v-if="forms.copyright.agreementSent && forms.copyright.agreementSigned">
          <label class="label">Signed Date</label>
          <input 
            type="date" 
            v-model="forms.copyright.signedDate"
          >
        </div>
        
        <div class="form-group">
          <label class="label">Notes</label>
          <textarea 
            v-model="forms.copyright.notes"
            placeholder="Enter any notes about copyright..."
            rows="3"
          ></textarea>
        </div>
      </div>
    </div>
    
    <!-- Proof Correction Stage -->
    <div v-if="currentStage === 'proof'" class="stage-content">
      <h3>3. Proof Correction</h3>
      <div class="form-section">
        <div class="form-group">
          <label class="label">Proof Files</label>
          <p class="info-text">
            Upload proof files for author review
          </p>
          <div class="upload-area">
            <input type="file" class="file-input">
            <button class="btn btn-gray-outline">Upload Proof Files</button>
          </div>
        </div>
        
        <div class="form-group">
          <label class="label">Actions</label>
          <button 
            class="btn btn-primary"
            @click="handleProofSent"
            :disabled="forms.proof.proofSent"
          >
            {{ forms.proof.proofSent ? 'Proof Sent' : 'Send Proof to Authors' }}
          </button>
        </div>
        
        <div class="form-group" v-if="forms.proof.proofSent">
          <label class="label">Proof Status</label>
          <div class="radio-group">
            <label>
              <input type="radio" v-model="forms.proof.proofConfirmed" :value="true"> Confirmed
            </label>
            <label>
              <input type="radio" v-model="forms.proof.proofConfirmed" :value="false"> Revisions Needed
            </label>
          </div>
        </div>
        
        <div class="form-group" v-if="forms.proof.proofSent && forms.proof.proofConfirmed">
          <label class="label">Confirmation Date</label>
          <input 
            type="date" 
            v-model="forms.proof.confirmedDate"
          >
        </div>
        
        <div class="form-group">
          <label class="label">Corrections</label>
          <textarea 
            v-model="forms.proof.corrections"
            placeholder="Enter any corrections received..."
            rows="4"
          ></textarea>
        </div>
      </div>
    </div>
    
    <!-- Publication Stage -->
    <div v-if="currentStage === 'publication'" class="stage-content">
      <h3>4. Final Publication</h3>
      <div class="form-section">
        <div class="form-group">
          <label class="label">Publication Date</label>
          <input 
            type="date" 
            v-model="forms.publication.publicationDate"
          >
        </div>
        
        <div class="form-row">
          <div class="form-group half">
            <label class="label">Volume</label>
            <input 
              type="text" 
              v-model="forms.publication.volume"
              placeholder="e.g., 12"
            >
          </div>
          
          <div class="form-group half">
            <label class="label">Issue</label>
            <input 
              type="text" 
              v-model="forms.publication.issue"
              placeholder="e.g., 3"
            >
          </div>
        </div>
        
        <div class="form-group">
          <label class="label">Page Range</label>
          <input 
            type="text" 
            v-model="forms.publication.pageRange"
            placeholder="e.g., 123-145"
          >
        </div>
        
        <div class="form-group">
          <label class="label">DOI</label>
          <input 
            type="text" 
            v-model="forms.publication.doi"
            placeholder="e.g., 10.1016/j.journal.2026.01.001"
          >
          <p class="info-text">
            <strong>Note:</strong> DOI 号自动分配功能暂不实现。
          </p>
        </div>
        
        <div class="form-group" v-if="forms.publication.isPublished">
          <div class="success-message">
            <h4>🎉 Manuscript Published Successfully!</h4>
            <p>Publication Date: {{ forms.publication.publicationDate }}</p>
            <p>Volume: {{ forms.publication.volume }}, Issue: {{ forms.publication.issue }}</p>
            <p>Page Range: {{ forms.publication.pageRange }}</p>
            <p v-if="forms.publication.doi">DOI: {{ forms.publication.doi }}</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Navigation Buttons -->
    <div class="bottom-bar">
      <button 
        class="btn btn-gray"
        @click="handleSaveDraft"
      >
        Save Draft
      </button>
      
      <button 
        class="btn btn-gray"
        @click="handlePreviousStage"
        :disabled="!canGoBack"
      >
        Previous Stage
      </button>
      
      <button 
        class="btn btn-primary"
        :disabled="!canProceed || isLoading"
        @click="currentStage === 'publication' ? handlePublish() : handleNextStage()"
      >
        <span v-if="isLoading">Processing...</span>
        <span v-else-if="currentStage === 'publication' && !forms.publication.isPublished">Publish Manuscript</span>
        <span v-else-if="currentStage === 'publication' && forms.publication.isPublished">Published</span>
        <span v-else>Next Stage</span>
      </button>
    </div>
    </div>
    <div v-else class="error-container">
      <Navigation 
        v-if="!embedded"
        :user="userStore.user"
        :current-page="'editor-manuscripts'"
        :logout="userStore.logout"
      />
      <div class="error-content">
        <p v-if="errorMessage">{{ errorMessage }}</p>
        <p v-else>Loading manuscript...</p>
        <button class="btn btn-gray" @click="goBack">Go Back</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.publication-page-wrapper {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.publication-process-container {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background: white;
  padding: 20px;
  min-height: calc(100vh - 80px);
  color: #333;
}

.publication-process-container.embedded-mode {
  min-height: 100%;
  margin-top: 0;
}

.publication-process-container:not(.embedded-mode) {
  margin-top: 120px;
  padding: 40px;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.error-container {
  min-height: 100vh;
  background-color: #f5f7fa;
}

.error-content {
  margin-top: 120px;
  padding: 40px;
  text-align: center;
  color: #666;
}

.error-content p {
  font-size: 18px;
  margin-bottom: 20px;
}

/* Header */
.page-header {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #333;
}

.page-header h2 {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #666;
}

/* Progress Bar */
.progress-bar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
  padding: 0 20px;
  position: relative;
}

.progress-bar::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 20px;
  right: 20px;
  height: 2px;
  background: #ddd;
  z-index: 0;
}

.progress-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  position: relative;
  z-index: 1;
}

.progress-item::before {
  display: none;
}

.progress-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #ddd;
  z-index: 1;
  margin-bottom: 8px;
}

.progress-label {
  font-size: 12px;
  text-align: center;
  z-index: 1;
}

.progress-item.current .progress-dot {
  background: #0056B3;
  border: 2px solid #0056B3;
}

.progress-item.completed .progress-dot {
  background: #28A745;
  border: 2px solid #28A745;
}

.progress-item.completed::before {
  background: #28A745;
}

/* Error Message */
.error-message {
  background: #ffebee;
  color: #dc3545;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

/* Stage Content */
.stage-content {
  margin-bottom: 30px;
}

.stage-content h3 {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  border-bottom: 1px solid #ddd;
  padding-bottom: 10px;
}

/* Form Section */
.form-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 4px;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group.half {
  flex: 1;
}

.label {
  display: block;
  font-weight: bold;
  margin-bottom: 8px;
  font-size: 14px;
}

textarea, input[type="text"], input[type="date"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

textarea {
  resize: vertical;
  min-height: 100px;
}

.radio-group {
  display: flex;
  gap: 20px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 5px;
}

.upload-area {
  border: 1px dashed #ddd;
  padding: 20px;
  text-align: center;
  margin-bottom: 15px;
}

.file-input {
  display: none;
}

.info-text {
  font-size: 12px;
  color: #666;
  margin-top: 5px;
  font-style: italic;
}

/* Success Message */
.success-message {
  background: #e8f5e8;
  color: #28A745;
  padding: 20px;
  border-radius: 4px;
  border: 1px solid #c8e6c9;
}

.success-message h4 {
  margin-top: 0;
  font-size: 16px;
}

/* Bottom Bar */
.bottom-bar {
  margin-top: 30px;
  display: flex;
  justify-content: center;
  gap: 15px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
}

.btn-primary {
  background: #0056B3;
  color: white;
}

.btn-primary:hover {
  background: #004494;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.btn-gray {
  background: #eee;
  color: #333;
}

.btn-gray:hover {
  background: #ddd;
}

.btn-gray-outline {
  border: 1px solid #ddd;
  background: white;
  color: #333;
  padding: 10px 20px;
}
</style>