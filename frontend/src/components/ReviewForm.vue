<script setup>
import { ref, reactive, computed, watch, nextTick } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useUserStore } from '../stores/user'

const props = defineProps({
  journal: Object,
  readonly: {
    type: Boolean,
    default: false
  },
  initialData: {
    type: Object,
    default: null
  },
  isRevision: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])
const { t } = useI18n()
const userStore = useUserStore()
const user = computed(() => userStore.user)

// Manuscript Info
const manuscriptId = computed(() => props.journal?.id || 'N/A')
const manuscriptTitle = computed(() => props.journal?.title || 'Untitled Manuscript')
const reviewerFullName = computed(() => user.value?.fullName || user.value?.username || 'Unknown Reviewer')
const reviewerAffiliation = computed(() => user.value?.institution || user.value?.affiliation || 'Unknown Affiliation')

// Evaluation Dimensions
const dimensions = computed(() => {
  if (props.isRevision) {
    return ['Addressing of Previous Concerns', 'Quality of Revisions', 'New Issues Identified']
  }
  return ['Originality', 'Methodology', 'Ethical Compliance', 'Readability', 'Importance']
})

const levels = ['Excellent', 'Good', 'Fair', 'Poor']

// Form State
const ratings = reactive({})

// Initialize ratings based on dimensions
watch(dimensions, (newDims) => {
  // Clear old keys not in newDims
  Object.keys(ratings).forEach(key => {
    if (!newDims.includes(key)) delete ratings[key]
  })
  // Add new keys
  newDims.forEach(dim => {
    if (!ratings[dim]) ratings[dim] = ''
  })
}, { immediate: true })

const comments = ref('')
const confidentialComments = ref('')
const decision = ref('')
const uploadedFile = ref(null)
const lastSaved = ref(null) // For auto-save feedback
const showConfirmModal = ref(false)

// Load Draft or Initial Data
const loadData = () => {
  // 1. Try Initial Data (Read-only or Edit mode if provided)
  if (props.initialData) {
    if (props.initialData.ratings) Object.assign(ratings, props.initialData.ratings)
    if (props.initialData.comment) comments.value = props.initialData.comment
    if (props.initialData.confidentialComments) confidentialComments.value = props.initialData.confidentialComments
    if (props.initialData.decision) decision.value = props.initialData.decision
    if (props.initialData.file) {
      uploadedFile.value = { name: props.initialData.file }
    }
    return
  }

  // 2. Try Local Draft (Only if not readonly)
  if (!props.readonly && props.journal) {
    const draftKey = `review_draft_${props.journal.id}`
    const draft = localStorage.getItem(draftKey)
    if (draft) {
      try {
        const parsed = JSON.parse(draft)
        if (parsed.ratings) Object.assign(ratings, parsed.ratings)
        if (parsed.comments) comments.value = parsed.comments
        if (parsed.confidentialComments) confidentialComments.value = parsed.confidentialComments
        if (parsed.decision) decision.value = parsed.decision
        // Files cannot be restored from localStorage easily in this mock, skipping file draft
        lastSaved.value = new Date(parsed.timestamp).toLocaleTimeString()
      } catch (e) {
        console.error('Failed to load draft', e)
      }
    }
  }
}

loadData()

// Auto-Save Logic
const saveDraft = () => {
  if (props.readonly || !props.journal) return
  
  const draft = {
    ratings: { ...ratings },
    comments: comments.value,
    confidentialComments: confidentialComments.value,
    decision: decision.value,
    timestamp: Date.now()
  }
  
  localStorage.setItem(`review_draft_${props.journal.id}`, JSON.stringify(draft))
  lastSaved.value = new Date().toLocaleTimeString()
}

// Watch changes
let saveTimer = null
watch(
  [ratings, comments, confidentialComments, decision],
  () => {
    // Simple debounce via timeout if lodash not available, but for now direct or simple logic
    // Let's use a timeout
    if (saveTimer) clearTimeout(saveTimer)
    saveTimer = setTimeout(saveDraft, 1000)
  },
  { deep: true }
)


const errors = reactive({
  ratings: false,
  comments: false,
  decision: false
})

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // Mock validation
    if (file.size > 10 * 1024 * 1024) {
      alert('File size exceeds 10MB limit.')
      return
    }
    uploadedFile.value = file
  }
}

const removeFile = () => {
  uploadedFile.value = null
  // Reset input
  const input = document.querySelector('input[type="file"]')
  if (input) input.value = ''
}

// Validation
const validate = () => {
  let isValid = true
  let firstErrorElement = null

  // Check all dimensions rated
  if (Object.values(ratings).some(v => !v)) {
    errors.ratings = true
    isValid = false
    if (!firstErrorElement) firstErrorElement = document.querySelector('.dimensions-grid')
  } else {
    errors.ratings = false
  }

  // Check comments
  if (!comments.value.trim()) {
    errors.comments = true
    isValid = false
    if (!firstErrorElement) firstErrorElement = document.querySelector('.comments-section textarea')
  } else {
    errors.comments = false
  }

  // Check decision
  if (!decision.value) {
    errors.decision = true
    isValid = false
    if (!firstErrorElement) firstErrorElement = document.querySelector('.decision-section select')
  } else {
    errors.decision = false
  }

  if (firstErrorElement) {
    firstErrorElement.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  return isValid
}

const handleSubmit = () => {
  if (validate()) {
    showConfirmModal.value = true
  }
}

const confirmSubmit = () => {
  // Clear draft on submit
  if (props.journal) {
    localStorage.removeItem(`review_draft_${props.journal.id}`)
  }
  
  emit('submit', {
    ratings: { ...ratings },
    comments: comments.value,
    confidentialComments: confidentialComments.value,
    decision: decision.value,
    file: uploadedFile.value
  })
  showConfirmModal.value = false
}
</script>

<template>
  <div class="review-form-container">
    <!-- Manuscript Info Header -->
    <div class="info-card manuscript-info-header">
      <div class="info-row">
        <span class="label">Manuscript ID:</span>
        <span class="value">{{ manuscriptId }}</span>
      </div>
      <div class="info-row">
        <span class="label">Manuscript Title:</span>
        <span class="value title-truncate" :title="manuscriptTitle">{{ manuscriptTitle }}</span>
      </div>
      <div class="info-row">
        <span class="label">Reviewer:</span>
        <span class="value">{{ reviewerFullName }} ({{ reviewerAffiliation }})</span>
      </div>
    </div>

    <!-- Comparison Section -->
    <div class="info-card comparison-card">
      <h3>Review Guidelines</h3>
      <ul>
        <li><strong>Scoring:</strong> Please rate each dimension from Excellent to Poor.</li>
        <li>Efficiency: Please complete your review within the due date.</li>
        <li>Priority: 'Originality' is the most critical dimension.</li>
        <li>Response: Provide constructive feedback for the writers.</li>
      </ul>
    </div>

    <!-- Core Rules Section -->
    <div class="info-card rules-card">
      <h3>{{ isRevision ? 'Re-review Guidelines' : 'Review Process Rules' }}</h3>
      <div class="rules-grid" v-if="!isRevision">
        <div class="rule-item">
          <strong>Priority:</strong> Focus on scientific validity and novelty.
        </div>
        <div class="rule-item">
          <strong>Screening:</strong> Initial check for compliance.
        </div>
        <div class="rule-item">
          <strong>Peer Review:</strong> Detailed assessment of the manuscript.
        </div>
        <div class="rule-item">
          <strong>Rejection:</strong> Clearly state reasons for rejection.
        </div>
        <div class="rule-item">
          <strong>Resubmission:</strong> Major revisions will require re-review.
        </div>
      </div>
      <div class="rules-grid" v-else>
        <div class="rule-item">
          <strong>Focus:</strong> Evaluate if the writer has addressed previous comments.
        </div>
        <div class="rule-item">
          <strong>Changes:</strong> Check the diff view for specific modifications.
        </div>
        <div class="rule-item">
          <strong>New Issues:</strong> Identify any new issues introduced in the revision.
        </div>
      </div>
    </div>

    <!-- Rating Form -->
    <div class="form-section">
      <div class="section-header">
        <h3>{{ t('review.title') }}</h3>
        <span class="required-hint">* Required field</span>
        <span v-if="lastSaved && !readonly" class="save-status">Draft saved at {{ lastSaved }}</span>
      </div>
      
      <!-- Dimensions -->
      <div class="dimensions-grid">
        <div v-for="dim in dimensions" :key="dim" class="dimension-item">
          <label :class="{ 'highlight': dim === 'Originality' || dim === 'Resolution of issues' }">
            <span class="required">*</span> {{ dim }}
            <span v-if="dim === 'Originality' || dim === 'Resolution of issues'" class="badge">Highest Priority</span>
          </label>
          <select v-model="ratings[dim]" :class="{ 'error': errors.ratings && !ratings[dim] }" :disabled="readonly">
            <option value="" disabled>Select Level</option>
            <option v-for="level in levels" :key="level" :value="level">
              {{ level }}
            </option>
          </select>
        </div>
      </div>
      <p v-if="errors.ratings && !readonly" class="error-text">Please select a rating level for all required review criteria.</p>

      <!-- Comments -->
      <div class="comments-section">
        <label><span class="required">*</span> Review Comments (To Author)</label>
        <textarea 
          v-model="comments" 
          rows="6" 
          placeholder="Enter your review comments here..."
          :class="{ 'error': errors.comments }"
          :disabled="readonly"
        ></textarea>
        <p v-if="errors.comments && !readonly" class="error-text">Please provide review comments for the author (Review Comments (To Author)).</p>

        <label>Confidential Comments (To Editor)</label>
        <textarea 
          v-model="confidentialComments" 
          rows="3" 
          placeholder="Enter confidential comments for the editor..."
          :disabled="readonly"
        ></textarea>
      </div>

      <!-- File Upload -->
      <div class="file-section">
        <label>Upload Review Report (Optional)</label>
        <div class="file-upload-container" v-if="!readonly">
          <input type="file" @change="handleFileUpload" ref="fileInput" />
          <p class="help-text">Supported formats: PDF, DOCX. Max size: 10MB.</p>
        </div>
        <div v-if="uploadedFile" class="uploaded-file">
          <span>📄 {{ uploadedFile.name }}</span>
          <button class="remove-btn" @click="removeFile" v-if="!readonly">×</button>
        </div>
      </div>

      <!-- Decision -->
      <div class="decision-section">
        <label><span class="required">*</span> Recommendation</label>
        <select v-model="decision" :class="{ 'error': errors.decision }" :disabled="readonly">
          <option value="" disabled>Select Recommendation</option>
          <option value="Accept">Accept</option>
          <option value="Minor Revision">Minor Revision</option>
          <option value="Major Revision">Major Revision</option>
          <option value="Reject">Reject</option>
        </select>
        <p v-if="errors.decision && !readonly" class="error-text">Please select a final recommendation for the manuscript.</p>
      </div>

      <!-- Actions -->
      <div class="form-actions" v-if="!readonly">
        <button class="btn-cancel" @click="$emit('cancel')">Cancel</button>
        <button class="btn-submit" @click="handleSubmit">Submit Review</button>
      </div>
    </div>
  </div>

  <!-- Confirmation Modal -->
  <div v-if="showConfirmModal" class="modal-overlay">
    <div class="modal-container">
      <h3>Confirm Submission</h3>
      <p>Are you sure you want to submit this review? This action cannot be undone, and the review will be immediately available to the editorial team.</p>
      <div class="modal-actions">
        <button class="btn-cancel" @click="showConfirmModal = false">Cancel</button>
        <button class="btn-submit" @click="confirmSubmit">Confirm Submit</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.review-form-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  max-width: 900px;
  margin: 0 auto;
}

.info-card {
  padding: 1.5rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.manuscript-info-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.manuscript-info-header .info-row {
  display: flex;
  gap: 0.5rem;
  align-items: baseline;
  font-size: 0.9rem;
  color: #6c757d;
}

.manuscript-info-header .label {
  font-weight: 600;
  min-width: 120px;
}

.manuscript-info-header .value {
  color: #495057;
  font-weight: 500;
}

.title-truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 600px;
  display: inline-block;
  vertical-align: bottom;
}

.comparison-card {
  background-color: #f0f4f8;
  border-left: 4px solid #3498db;
}

.rules-card {
  background-color: #fff8e1;
  border-left: 4px solid #f1c40f;
}

.info-card h3 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-size: 1.1rem;
}

.info-card ul {
  margin: 0;
  padding-left: 1.5rem;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.rule-item {
  font-size: 0.9rem;
  line-height: 1.4;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  margin: 0;
}

.save-status {
  font-size: 0.85rem;
  color: #27ae60;
  font-style: italic;
}

.form-section {
  border-top: 1px solid #eee;
  padding-top: 1.5rem;
}

.dimensions-grid {
  display: grid;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.dimension-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.dimension-item label {
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dimension-item label.highlight {
  color: #e67e22;
  font-weight: bold;
}

.badge {
  background: #e67e22;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 4px;
}

select, textarea {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

select {
  min-width: 200px;
}

textarea {
  width: 100%;
  margin-top: 0.5rem;
  margin-bottom: 1rem;
}

.comments-section label, .decision-section label, .file-section label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  margin-top: 1rem;
}

.file-upload-container {
  border: 2px dashed #ddd;
  padding: 1.5rem;
  text-align: center;
  border-radius: 6px;
  background: #f9f9f9;
}

.file-upload-container:hover {
  border-color: #3498db;
  background: #f0f8ff;
}

.help-text {
  color: #999;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.uploaded-file {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #e8f5e9;
  border-radius: 4px;
  color: #2e7d32;
}

.remove-btn {
  background: none;
  border: none;
  color: #c0392b;
  font-weight: bold;
  cursor: pointer;
  font-size: 1.2rem;
}

.error {
  border-color: #e74c3c;
}

.error-text {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: -0.5rem;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-submit, .btn-cancel {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
}

.btn-submit {
  background: #27ae60;
  color: white;
}

.btn-submit:hover {
  background: #219150;
}

.btn-cancel {
  background: #95a5a6;
  color: white;
}

.btn-cancel:hover {
  background: #7f8c8d;
}

.required {
  color: #e74c3c;
  margin-right: 4px;
}

.required-hint {
  color: #e74c3c;
  font-size: 0.85rem;
  font-weight: 500;
  margin-left: 1rem;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.modal-container h3 {
  margin-top: 0;
  color: #2c3e50;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.modal-container p {
  color: #555;
  line-height: 1.5;
  margin-bottom: 2rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}
</style>