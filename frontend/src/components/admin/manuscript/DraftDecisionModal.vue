<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { useToastStore } from '../../../stores/toast'

const toastStore = useToastStore()

const props = defineProps({
  visible: Boolean,
  manuscript: Object,
  currentUser: Object
})

const emit = defineEmits(['close', 'submit', 'save-draft'])

// State
const isLoading = ref(true)
const showReviewComments = ref(false)
const showAESuggestions = ref(false)
const isSubmitting = ref(false)
const isSuccess = ref(false)
const successMessage = ref('')
const formRef = ref(null)

// Form Data
const form = reactive({
  decision: '',
  rationale: '',
  deadline: '4 Weeks',
  transferJournal: '',
  attachments: []
})

// Validation State
const errors = reactive({})

// Mock Data
const reviewComments = ref([
  { id: 1, reviewer: 'Reviewer 1', rating: 'Accept', comment: 'Excellent work, very original.' },
  { id: 2, reviewer: 'Reviewer 2', rating: 'Minor Revision', comment: 'Good study, but needs some clarifications in methodology.' }
])
const aeSuggestions = ref("I recommend acceptance after minor revisions regarding the statistical analysis.")
const sisterJournals = ['Peerex Peer Global Health', 'Peerex Peer Oncology', 'Peerex Peer Public Health']

// Options
const decisionOptions = ['Accept', 'Minor Revision', 'Major Revision', 'Reject', 'Transfer to Sister Journal']
const deadlineOptions = ['2 Weeks', '4 Weeks', '6 Weeks', '8 Weeks']

// Computed
const isEICReviewRequired = computed(() => {
  // Associate Editor: Accept/Major Revision requires EIC review
  if (props.currentUser?.role === 'associate_editor') {
    return ['Accept', 'Major Revision'].includes(form.decision)
  }
  return false
})

const submitButtonText = computed(() => {
  if (isEICReviewRequired.value) {
    return 'Submit for Review'
  }
  return 'Submit Decision'
})

const isFormValid = computed(() => {
  if (!form.decision) return false
  if (!form.rationale) return false
  
  if (form.decision === 'Reject' && form.rationale.length < 10) return false
  if (['Minor Revision', 'Major Revision'].includes(form.decision) && !form.deadline) return false
  if (form.decision === 'Transfer to Sister Journal' && !form.transferJournal) return false
  
  return true
})

// Methods
const initData = () => {
  isLoading.value = true
  setTimeout(() => {
    // Load Draft
    const draft = localStorage.getItem(`decision_draft_${props.manuscript?.id}`)
    if (draft) {
      Object.assign(form, JSON.parse(draft))
    } else {
      // Default Template
      form.rationale = "Based on the reviewers' comments and my own assessment, I have decided to..."
    }
    isLoading.value = false
  }, 1000)
}

const handleSaveDraft = () => {
  localStorage.setItem(`decision_draft_${props.manuscript?.id}`, JSON.stringify(form))
  emit('save-draft', { ...form })
  toastStore.add({ message: 'Decision content saved as draft, continue editing', type: 'success' })
}

const validateForm = () => {
  Object.keys(errors).forEach(key => delete errors[key])
  let firstErrorField = null
  
  const setError = (field, msg) => {
    errors[field] = msg
    if (!firstErrorField) firstErrorField = field
  }

  if (!form.decision) setError('decision', 'Please select a decision outcome')
  
  if (!form.rationale) {
    setError('rationale', 'Please fill in the decision rationale')
  } else if (form.decision === 'Reject' && form.rationale.length < 20) {
    setError('rationale', 'Please provide a detailed reason for rejection')
  }

  if (['Minor Revision', 'Major Revision'].includes(form.decision) && !form.deadline) {
    setError('deadline', 'Please select a deadline')
  }

  if (form.decision === 'Transfer to Sister Journal' && !form.transferJournal) {
    setError('transferJournal', 'Please select a journal to transfer to')
  }

  return firstErrorField
}

const handleSubmit = async () => {
  const firstError = validateForm()
  if (firstError) {
    const element = document.getElementById(firstError)
    if (element) element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

  isSubmitting.value = true
  
  // Simulate API
  await new Promise(resolve => setTimeout(resolve, 1500))
  
  isSubmitting.value = false
  isSuccess.value = true
  
  if (isEICReviewRequired.value) {
    successMessage.value = 'Submitted to Editor-in-Chief for review, please wait for confirmation'
  } else {
    successMessage.value = 'Decision submitted successfully'
  }
  
  emit('submit', { 
    ...form, 
    isEICReviewRequired: isEICReviewRequired.value 
  })
  
  setTimeout(() => {
    emit('close')
    isSuccess.value = false
  }, 3000)
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  form.attachments.push(...files.map(f => ({ name: f.name, size: f.size })))
}

const removeAttachment = (index) => {
  form.attachments.splice(index, 1)
}

const insertComment = (text) => {
  form.rationale += `\n\n> ${text}\n`
}

// Watchers
watch(() => props.visible, (val) => {
  if (val) initData()
})
</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-container">
      <!-- Skeleton -->
      <div v-if="isLoading" class="skeleton-screen">
         <div class="sk-header"></div>
         <div class="sk-body"></div>
      </div>

      <template v-else>
        <!-- Success Overlay -->
        <div v-if="isSuccess" class="success-overlay">
           <div class="success-content">
             <div class="success-icon">✓</div>
             <h3>{{ successMessage }}</h3>
           </div>
        </div>

        <!-- 1. Manuscript Info Overview (Top, Fixed) -->
        <header class="modal-header">
          <div class="header-top">
            <h2>Draft Decision - [{{ manuscript.id }}] Draft Decision Opinion</h2>
            <button class="close-btn" @click="$emit('close')" :disabled="isSuccess">Close</button>
          </div>
          <div class="info-grid">
             <div class="info-item"><span>Title:</span> {{ manuscript.title }}</div>
             <div class="info-item"><span>Field:</span> {{ manuscript.field }}</div>
             <div class="info-item"><span>Status:</span> <span class="status-badge">{{ manuscript.status }}</span></div>
             <div class="info-item"><span>Submitted:</span> {{ manuscript.submittedDate || manuscript.date }}</div>
          </div>
          <div class="header-actions">
             <button class="btn-link" @click="showReviewComments = !showReviewComments">
               {{ showReviewComments ? 'Hide' : 'View' }} Full Review Comments
             </button>
             <button class="btn-link" @click="showAESuggestions = !showAESuggestions">
               {{ showAESuggestions ? 'Hide' : 'View' }} Associate Editor Suggestions
             </button>
          </div>
          
          <!-- Collapsible Info Areas -->
          <div v-if="showReviewComments" class="info-panel">
            <div v-for="rc in reviewComments" :key="rc.id" class="comment-item">
              <strong>{{ rc.reviewer }} ({{ rc.rating }}):</strong> {{ rc.comment }}
              <button class="btn-insert" @click="insertComment(rc.comment)">Insert Quote</button>
            </div>
          </div>
          <div v-if="showAESuggestions" class="info-panel">
             <div class="comment-item">
               <strong>AE Suggestion:</strong> {{ aeSuggestions }}
               <button class="btn-insert" @click="insertComment(aeSuggestions)">Insert Quote</button>
             </div>
          </div>
        </header>

        <!-- 2. Decision Opinion Editing (Scrollable) -->
        <div class="modal-body" ref="formRef">
          
          <!-- Decision Outcome -->
          <section class="form-section">
            <h3>Decision Outcome</h3>
            <div class="form-group" id="decision">
              <label class="required">Decision</label>
              <select v-model="form.decision" class="select-input">
                <option value="" disabled>Select Outcome</option>
                <option v-for="opt in decisionOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <span class="error-msg" v-if="errors.decision">{{ errors.decision }}</span>
              
              <div v-if="isEICReviewRequired" class="info-msg">
                ℹ️ Requires Editor-in-Chief Final Review
              </div>
            </div>
          </section>

          <!-- Rationale Description -->
          <section class="form-section">
            <h3>Rationale Description</h3>
            <div class="form-group" id="rationale">
              <label class="required">Rationale</label>
              <textarea 
                v-model="form.rationale" 
                rows="10" 
                class="textarea-input"
                placeholder="Detailed explanation for the decision..."
              ></textarea>
              <span class="error-msg" v-if="errors.rationale">{{ errors.rationale }}</span>
            </div>
          </section>

          <!-- Follow-up Requirements -->
          <section class="form-section">
            <h3>Follow-up Requirements</h3>
            
            <div v-if="['Minor Revision', 'Major Revision'].includes(form.decision)" class="form-group" id="deadline">
              <label class="required">Revision Deadline</label>
              <select v-model="form.deadline" class="select-input">
                <option v-for="d in deadlineOptions" :key="d" :value="d">{{ d }}</option>
              </select>
              <span class="error-msg" v-if="errors.deadline">{{ errors.deadline }}</span>
            </div>

            <div v-if="form.decision === 'Transfer to Sister Journal'" class="form-group" id="transferJournal">
               <label class="required">Recommended Journal</label>
               <select v-model="form.transferJournal" class="select-input">
                 <option value="" disabled>Select Journal</option>
                 <option v-for="j in sisterJournals" :key="j" :value="j">{{ j }}</option>
               </select>
               <span class="error-msg" v-if="errors.transferJournal">{{ errors.transferJournal }}</span>
            </div>

            <div class="form-group">
              <label>Attachments</label>
              <input type="file" @change="handleFileUpload" multiple class="file-input">
              <div v-if="form.attachments.length" class="file-list">
                <div v-for="(file, index) in form.attachments" :key="index" class="file-item">
                  <span>{{ file.name }}</span>
                  <button @click="removeAttachment(index)" class="btn-delete">Delete</button>
                </div>
              </div>
            </div>
          </section>

        </div>

        <!-- 3. Action Buttons (Bottom, Fixed) -->
        <footer class="modal-footer">
          <button class="btn btn-secondary" @click="handleSaveDraft">Save Draft</button>
          <button class="btn btn-cancel" @click="$emit('close')">Cancel</button>
          <button 
            class="btn btn-primary" 
            :disabled="!isFormValid"
            :title="!isFormValid ? 'Please complete all required fields' : ''"
            @click="handleSubmit"
          >
            {{ submitButtonText }}
          </button>
        </footer>
      </template>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex; justify-content: center; align-items: center;
  z-index: 2000;
}
.modal-container {
  background: white; width: 900px; height: 90vh;
  display: flex; flex-direction: column;
  border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  position: relative;
}

/* Header */
.modal-header {
  padding: 1.5rem; border-bottom: 1px solid #eee; background: white; flex-shrink: 0;
}
.header-top { display: flex; justify-content: space-between; margin-bottom: 1rem; }
.info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.5rem; font-size: 0.9rem; margin-bottom: 1rem; }
.info-item span { font-weight: 600; color: #7f8c8d; width: 80px; display: inline-block; }
.status-badge { background: #e3f2fd; color: #1976d2; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem; }

.header-actions { display: flex; gap: 1rem; }
.btn-link { background: none; border: none; color: #3498db; cursor: pointer; text-decoration: underline; }

.info-panel {
  background: #f8f9fa; padding: 0.8rem; margin-top: 0.8rem; border-radius: 4px; border: 1px solid #eee; font-size: 0.9rem;
}
.comment-item { margin-bottom: 0.5rem; border-bottom: 1px dashed #ddd; padding-bottom: 0.5rem; }
.btn-insert { font-size: 0.75rem; background: #eee; border: 1px solid #ccc; padding: 2px 6px; cursor: pointer; margin-left: 0.5rem; }

/* Body */
.modal-body { flex: 1; overflow-y: auto; padding: 1.5rem; background: #f9f9f9; }
.form-section { background: white; padding: 1.5rem; margin-bottom: 1.5rem; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
.form-section h3 { margin-top: 0; margin-bottom: 1.5rem; font-size: 1.1rem; border-bottom: 2px solid #3498db; padding-bottom: 0.5rem; display: inline-block; }

.form-group { margin-bottom: 1.2rem; }
.form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; }
.required::after { content: " *"; color: #e74c3c; }

.select-input, .textarea-input { width: 100%; padding: 0.6rem; border: 1px solid #ddd; border-radius: 4px; font-size: 0.9rem; }
.error-msg { color: #e74c3c; font-size: 0.8rem; margin-top: 0.25rem; display: block; }
.info-msg { color: #e67e22; font-size: 0.85rem; margin-top: 0.5rem; font-style: italic; }

.file-list { margin-top: 0.5rem; }
.file-item { display: flex; align-items: center; font-size: 0.9rem; margin-bottom: 0.3rem; }
.btn-delete { background: #e74c3c; color: white; border: none; padding: 0.2rem 0.5rem; border-radius: 3px; font-size: 0.7rem; margin-left: 0.5rem; cursor: pointer; }

/* Footer */
.modal-footer { padding: 1rem 1.5rem; border-top: 1px solid #eee; display: flex; justify-content: flex-end; gap: 1rem; background: white; flex-shrink: 0; }
.btn { padding: 0.6rem 1.5rem; border-radius: 4px; border: none; cursor: pointer; }
.btn-primary { background: #3498db; color: white; }
.btn-primary:disabled { background: #bdc3c7; cursor: not-allowed; }
.btn-secondary { background: white; border: 1px solid #ddd; }
.btn-cancel { background: #e74c3c; color: white; }
.close-btn { background: none; border: none; font-size: 1rem; cursor: pointer; color: #7f8c8d; }
.close-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Success Overlay */
.success-overlay {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.95); display: flex; justify-content: center; align-items: center; z-index: 2200;
}
.success-content { text-align: center; }
.success-icon { font-size: 2rem; color: #27ae60; margin-bottom: 1rem; }

/* Skeleton */
.skeleton-screen { padding: 2rem; }
.sk-header { height: 150px; background: #eee; margin-bottom: 2rem; }
.sk-body { height: 400px; background: #eee; }
</style>
