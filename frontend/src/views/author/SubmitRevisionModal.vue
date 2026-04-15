<script setup>
import { defineProps, defineEmits, ref, computed, reactive } from 'vue'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'

const props = defineProps({
  visible: Boolean,
  manuscript: Object
})

const emit = defineEmits(['close', 'submitted'])
const userStore = useUserStore()
const toastStore = useToastStore()

// State
const response = ref('')
const files = reactive({
  revisedManuscript: null,
  responseDoc: null,
  coverLetter: null,
  supplementary: null,
  highlights: null
})
const declarations = reactive({
  addressedComments: false,
  trackChanges: false,
  coAuthorsApproved: false,
  ethicalApproval: false,
  dataSharing: false
})

const showPreview = ref(false)
const showConfirm = ref(false)
const showSuccess = ref(false)
const submitting = ref(false)
const error = ref('')

// Computed
const revisionType = computed(() => props.manuscript?.revisionType || 'Minor Revision')
const deadline = computed(() => props.manuscript?.deadline || '2026-03-01')

const isDeadlineNear = computed(() => {
  const deadlineDate = new Date(deadline.value)
  const now = new Date()
  const diffTime = deadlineDate - now
  const diffHours = Math.ceil(diffTime / (1000 * 60 * 60))
  return diffHours < 48 && diffHours > 0
})

const metadata = computed(() => ({
  id: props.manuscript?.id || '20262477',
  author: props.manuscript?.author || 'Dr. Jane Smith (University of Oxford)',
  type: props.manuscript?.module || 'Randomized Controlled Trial'
}))

const isFormValid = computed(() => {
  return response.value && 
         response.value.length <= 10000 &&
         files.revisedManuscript && 
         files.responseDoc && 
         files.coverLetter &&
         declarations.addressedComments &&
         declarations.trackChanges &&
         declarations.coAuthorsApproved &&
         declarations.ethicalApproval &&
         declarations.dataSharing
})

// Methods
const handleFileUpload = (type, event) => {
  const file = event.target.files[0]
  if (!file) return

  let maxSize = 0
  let allowedTypes = []

  switch (type) {
    case 'revisedManuscript':
      maxSize = 50 * 1024 * 1024
      allowedTypes = ['.doc', '.docx', '.pdf']
      break
    case 'responseDoc':
      maxSize = 20 * 1024 * 1024
      allowedTypes = ['.doc', '.docx', '.pdf']
      break
    case 'coverLetter':
      maxSize = 10 * 1024 * 1024
      allowedTypes = ['.doc', '.docx', '.pdf']
      break
    case 'supplementary':
      maxSize = 100 * 1024 * 1024
      allowedTypes = ['.zip', '.doc', '.docx', '.pdf']
      break
    case 'highlights':
      maxSize = 5 * 1024 * 1024
      allowedTypes = ['.docx']
      break
  }

  if (file.size > maxSize) {
    toastStore.add({ message: `File size exceeds limit for ${type}.`, type: 'warning' })
    event.target.value = ''
    return
  }

  // Validate Type (Simple extension check)
  const extension = '.' + file.name.split('.').pop().toLowerCase()
  if (!allowedTypes.includes(extension) && !allowedTypes.includes('.docx')) { // Loose check for demo
     // Note: In real app, check MIME type. Here just checking extension logic briefly or rely on accept attr
  }

  files[type] = file
}

const validateAndPreview = () => {
  if (!isFormValid.value) {
    // Trigger validation msg
    if (response.value.length > 10000) {
      error.value = 'Response exceeds 10,000 character limit.'
    } else {
      error.value = 'Please complete all required fields and declarations.'
    }
    return
  }
  error.value = ''
  showPreview.value = true
}

const initiateSubmit = () => {
  if (!isFormValid.value) return
  showConfirm.value = true
}

const submitRevision = async () => {
  showConfirm.value = false
  submitting.value = true
  
  try {
    await new Promise(resolve => setTimeout(resolve, 1500)) // Simulate upload

    // Update Status
    const updatedJournal = { ...props.manuscript }
    updatedJournal.status = MANUSCRIPT_STATUS.REVISION_SUBMITTED
    updatedJournal.revisionNote = response.value
    updatedJournal.lastUpdated = new Date().toISOString()
    // In real app, we would upload files and get URLs.
    
    userStore.updateJournal(updatedJournal)

    showSuccess.value = true
  } catch (e) {
    error.value = 'Submission failed. Please try again.'
  } finally {
    submitting.value = false
  }
}

const close = () => {
  showSuccess.value = false
  emit('close')
  // Reset state if needed, but component destruction handles it usually
}

const downloadReceipt = () => {
  toastStore.add({ message: 'Downloading submission receipt...', type: 'info' })
}

</script>

<template>
  <!-- Main Modal -->
  <div v-if="visible && !showSuccess" class="modal-overlay" @click.self="close">
    <div class="modal-box main-modal">
      <div class="modal-header">
        <h3>Submit Revision for MS ID: {{ metadata.id }}</h3>
        <button class="close-btn" @click="close">&times;</button>
      </div>
      
      <div class="modal-content scrollable">
        <!-- Top Info Area -->
        <div class="info-area">
          <div class="status-row">
            <span class="revision-type">Revision Type: {{ revisionType }}</span>
            <span class="deadline" :class="{ 'text-danger': isDeadlineNear }">Deadline: {{ deadline }}</span>
          </div>
          <div v-if="isDeadlineNear" class="warning-banner">
            Warning: Your revision deadline is in less than 48 hours. Late submissions may be rejected.
          </div>
          <div class="metadata-box">
            <h4>Manuscript Metadata (Confirmed):</h4>
            <div class="meta-grid">
              <div><strong>ID:</strong> {{ metadata.id }}</div>
              <div><strong>Corresponding Author:</strong> {{ metadata.author }}</div>
              <div><strong>Article Type:</strong> {{ metadata.type }}</div>
            </div>
          </div>
        </div>

        <!-- Form Area -->
        <form @submit.prevent>
          <!-- Point-by-Point Response -->
          <div class="form-section">
            <label>Point-by-Point Response to Reviewers <span class="required">*</span></label>
            <div class="field-tip">Please address each reviewer comment individually, clearly stating how you have revised the manuscript in response. Maximum 10,000 characters.</div>
            <textarea 
              v-model="response" 
              rows="8" 
              :class="{ 'error-border': response.length > 10000 }"
            ></textarea>
            <div class="char-count" :class="{ 'text-danger': response.length > 10000 }">
              {{ response.length }} / 10,000 characters
            </div>
          </div>

          <!-- Upload Required Documents -->
          <div class="form-section">
            <h4>Upload Required Documents</h4>
            <div class="field-tip">File naming convention: [MS ID]_[Document Type].docx/pdf (e.g., {{ metadata.id }}_RevisedManuscript.docx)</div>
            
            <!-- 1. Revised Manuscript -->
            <div class="file-input-group">
              <label>Upload Revised Manuscript (Track Changes) <span class="required">*</span></label>
              <input type="file" accept=".doc,.docx,.pdf" @change="handleFileUpload('revisedManuscript', $event)">
              <div class="file-status" v-if="files.revisedManuscript">Selected: {{ files.revisedManuscript.name }}</div>
            </div>

            <!-- 2. Point-by-Point Response Document -->
            <div class="file-input-group">
              <label>Upload Point-by-Point Response Document <span class="required">*</span></label>
              <input type="file" accept=".doc,.docx,.pdf" @change="handleFileUpload('responseDoc', $event)">
              <div class="file-status" v-if="files.responseDoc">Selected: {{ files.responseDoc.name }}</div>
            </div>

            <!-- 3. Cover Letter -->
            <div class="file-input-group">
              <label>Upload Cover Letter (Revision Summary) <span class="required">*</span></label>
              <input type="file" accept=".doc,.docx,.pdf" @change="handleFileUpload('coverLetter', $event)">
              <div class="file-status" v-if="files.coverLetter">Selected: {{ files.coverLetter.name }}</div>
            </div>
          </div>

          <!-- Upload Optional Materials -->
          <div class="form-section">
            <h4>Upload Optional Materials</h4>
            
            <div class="file-input-group">
              <label>Upload Supplementary Materials (if applicable)</label>
              <input type="file" accept=".zip,.doc,.docx,.pdf" @change="handleFileUpload('supplementary', $event)">
              <div class="file-status" v-if="files.supplementary">Selected: {{ files.supplementary.name }}</div>
            </div>

            <div class="file-input-group">
              <label>Upload Highlights (if applicable)</label>
              <input type="file" accept=".docx" @change="handleFileUpload('highlights', $event)">
              <div class="file-status" v-if="files.highlights">Selected: {{ files.highlights.name }}</div>
            </div>
          </div>

          <!-- Revision Declaration -->
          <div class="form-section declaration-section">
            <label>Revision Declaration <span class="required">*</span></label>
            <div class="checkbox-group" title="Please confirm all revision declarations before submission.">
              <div class="checkbox-item">
                <input type="checkbox" id="dec1" v-model="declarations.addressedComments">
                <label for="dec1">I confirm that all reviewer comments have been addressed point-by-point.</label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="dec2" v-model="declarations.trackChanges">
                <label for="dec2">The revised manuscript includes track changes to clearly highlight all modifications.</label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="dec3" v-model="declarations.coAuthorsApproved">
                <label for="dec3">All co-authors have reviewed and approved the revised version of the manuscript.</label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="dec4" v-model="declarations.ethicalApproval">
                <label for="dec4">No new data, findings, or conclusions have been added without appropriate ethical approval (where applicable).</label>
              </div>
              <div class="checkbox-item">
                <input type="checkbox" id="dec5" v-model="declarations.dataSharing">
                <label for="dec5">The manuscript complies with the Peerex Peer's data sharing policy.</label>
              </div>
            </div>
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>
        </form>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close">Cancel</button>
        <button class="btn btn-secondary" @click="validateAndPreview">Preview Submission</button>
        <button class="btn btn-primary" @click="initiateSubmit" :disabled="!isFormValid || submitting">
          {{ submitting ? 'Submitting...' : 'Submit Revision' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Preview Modal -->
  <div v-if="showPreview" class="modal-overlay" style="z-index: 1002;">
    <div class="modal-box preview-modal">
      <div class="modal-header">
        <h3>Preview Submission</h3>
        <button class="close-btn" @click="showPreview = false">&times;</button>
      </div>
      <div class="modal-content scrollable">
        <h4>Response Content</h4>
        <pre class="preview-text">{{ response }}</pre>
        <h4>Files to Submit</h4>
        <ul>
          <li v-for="(file, key) in files" :key="key" v-show="file">
            {{ key }}: {{ file?.name }}
          </li>
        </ul>
        <h4>Declarations</h4>
        <p>All declarations confirmed.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showPreview = false">Close Preview</button>
      </div>
    </div>
  </div>

  <!-- Confirmation Modal -->
  <div v-if="showConfirm" class="modal-overlay" style="z-index: 1003;">
    <div class="modal-box confirm-box">
      <div class="modal-header">
        <h3>Confirm Submission</h3>
      </div>
      <div class="modal-content">
        <p>Are you sure you want to submit this revision? This action cannot be undone.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showConfirm = false">Cancel</button>
        <button class="btn btn-primary" @click="submitRevision">Confirm Submit</button>
      </div>
    </div>
  </div>

  <!-- Success Modal -->
  <div v-if="showSuccess" class="modal-overlay" style="z-index: 1004;">
    <div class="modal-box success-box">
      <div class="modal-header">
        <h3 class="text-success">Submission Successful</h3>
      </div>
      <div class="modal-content">
        <p>Your revision has been submitted to The Peerex Peer editorial team.</p>
        <p><strong>Manuscript ID:</strong> {{ metadata.id }}</p>
        <p>A confirmation email has been sent to the corresponding author ({{ metadata.author }}).</p>
        <p>Your manuscript is now in the Revision Handling queue for editorial review.</p>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="downloadReceipt">Download Receipt</button>
        <button class="btn btn-primary" @click="close">Close</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 1000;
}

.modal-box {
  background: white; border-radius: 4px; display: flex; flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.main-modal { width: 800px; max-width: 95%; height: 90vh; }
.preview-modal { width: 700px; max-width: 90%; max-height: 80vh; }
.confirm-box { width: 400px; }
.success-box { width: 500px; }

.modal-header {
  padding: 1.5rem; border-bottom: 1px solid #eee;
  display: flex; justify-content: space-between; align-items: center;
}
.modal-header h3 { margin: 0; font-size: 1.3rem; color: #333; font-family: 'Times New Roman', serif; }
.text-success { color: #28a745; }

.close-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #999; }

.modal-content { padding: 1.5rem; overflow-y: auto; }
.scrollable { flex: 1; }

.info-area { margin-bottom: 2rem; background: #f8f9fa; padding: 1rem; border-radius: 4px; }
.status-row { display: flex; justify-content: space-between; font-size: 1.1rem; font-weight: bold; margin-bottom: 1rem; }
.text-danger { color: #dc3545; }
.warning-banner { background: #ffe6e6; color: #721c24; padding: 0.8rem; margin-bottom: 1rem; border: 1px solid #f5c6cb; border-radius: 4px; }
.metadata-box { border-top: 1px solid #ddd; padding-top: 1rem; }
.meta-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; margin-top: 0.5rem; color: #555; }

.form-section { margin-bottom: 2rem; }
.form-section h4 { border-bottom: 1px solid #eee; padding-bottom: 0.5rem; margin-bottom: 1rem; color: #0056b3; }
.field-tip { font-size: 0.9rem; color: #666; margin-bottom: 0.5rem; font-style: italic; }

.file-input-group { margin-bottom: 1rem; padding: 1rem; border: 1px dashed #ddd; background: #fff; }
.file-input-group label { display: block; font-weight: 500; margin-bottom: 0.5rem; }
.file-status { margin-top: 0.5rem; color: #28a745; font-size: 0.9rem; }

.checkbox-group { display: flex; flex-direction: column; gap: 0.8rem; }
.checkbox-item { display: flex; align-items: flex-start; gap: 0.8rem; }
.checkbox-item input { margin-top: 0.3rem; }
.checkbox-item label { font-size: 0.95rem; line-height: 1.4; color: #333; cursor: pointer; }

textarea { width: 100%; padding: 0.8rem; border: 1px solid #ddd; border-radius: 4px; resize: vertical; font-family: inherit; }
textarea.error-border { border-color: #dc3545; }
.char-count { text-align: right; font-size: 0.85rem; color: #666; margin-top: 0.3rem; }

.error-msg { color: #dc3545; background: #ffe6e6; padding: 0.8rem; border-radius: 4px; margin-bottom: 1rem; }

.modal-footer { padding: 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; background: #fff; }

.btn { padding: 0.6rem 1.5rem; border-radius: 4px; border: none; cursor: pointer; font-weight: 500; font-size: 1rem; }
.btn-primary { background: #0056b3; color: white; }
.btn-primary:disabled { background: #aab7c4; cursor: not-allowed; }
.btn-secondary { background: #6c757d; color: white; }
.btn-secondary:hover { background: #5a6268; }

.preview-text { background: #f8f9fa; padding: 1rem; white-space: pre-wrap; border: 1px solid #eee; max-height: 300px; overflow-y: auto; }
</style>
