<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'

const props = defineProps({
  visible: Boolean,
  manuscript: Object,
  currentUser: Object
})

const emit = defineEmits(['close', 'submit', 'save-draft'])

// State
const isLoading = ref(true)
const showAttachments = ref(false)
const formRef = ref(null)

// Form Data
const form = reactive({
  // Compliance Check
  formatCompliance: '',
  specificFormatIssues: '',
  ethicsApproval: '',
  missingEthicsDocuments: '',
  coiStatement: '',
  reasonForMissingCoi: '',
  scopeCompliance: '',
  mismatchedResearchField: '',
  
  // Academic Preliminary Judgment
  originality: '',
  scientificValue: '',
  methodology: '',
  academicRemarks: '',
  
  // Initial Review Outcome
  finalOutcome: '',
  detailedReason: '',
  attachments: []
})

// Validation State
const errors = reactive({})

// Mock Similarity Result
const similarityResult = "12% - Passed"

// Options
const complianceOptions = ['Yes', 'No']
const ethicsOptions = ['Yes', 'No', 'Not Applicable']
const evaluationOptions = ['Excellent', 'Good', 'Fair', 'Insufficient']
const outcomeOptions = ['Reject Directly', 'Forward to Peer Review', 'Suggest Transfer to Sister Journal']

// Computed
const isAnyEvaluationInsufficient = computed(() => {
  return [form.originality, form.scientificValue, form.methodology].includes('Insufficient')
})

const isFormValid = computed(() => {
  // Basic Compliance
  if (!form.formatCompliance) return false
  if (form.formatCompliance === 'No' && !form.specificFormatIssues) return false
  
  if (!form.ethicsApproval) return false
  if (form.ethicsApproval === 'No' && !form.missingEthicsDocuments) return false
  
  if (!form.coiStatement) return false
  if (form.coiStatement === 'No' && !form.reasonForMissingCoi) return false
  
  if (!form.scopeCompliance) return false
  if (form.scopeCompliance === 'No' && !form.mismatchedResearchField) return false
  
  // Academic
  if (!form.originality || !form.scientificValue || !form.methodology) return false
  if (isAnyEvaluationInsufficient.value && !form.academicRemarks) return false
  
  // Outcome
  if (!form.finalOutcome) return false
  if (!form.detailedReason) return false
  
  return true
})

// Methods
const initForm = () => {
  isLoading.value = true
  // Simulate API fetch
  setTimeout(() => {
    // Load draft if exists (mock)
    const savedDraft = localStorage.getItem(`initial_review_draft_${props.manuscript?.id}`)
    if (savedDraft) {
      Object.assign(form, JSON.parse(savedDraft))
    }
    isLoading.value = false
  }, 1000)
}

const toggleAttachments = () => {
  showAttachments.value = !showAttachments.value
}

const handleSaveDraft = () => {
  localStorage.setItem(`initial_review_draft_${props.manuscript?.id}`, JSON.stringify(form))
  // Also emit event for parent to handle backend save if needed
  emit('save-draft', { ...form })
  alert('Initial review content saved as draft, continue editing')
}

const validateForm = () => {
  // Reset errors
  Object.keys(errors).forEach(key => delete errors[key])
  let firstErrorField = null
  
  // Helper to set error
  const setError = (field, msg) => {
    errors[field] = msg
    if (!firstErrorField) firstErrorField = field
  }
  
  // Compliance
  if (!form.formatCompliance) setError('formatCompliance', 'Please select Format Compliance')
  else if (form.formatCompliance === 'No' && !form.specificFormatIssues) setError('specificFormatIssues', 'Please specify format issues')
  
  if (!form.ethicsApproval) setError('ethicsApproval', 'Please select Ethics Approval')
  else if (form.ethicsApproval === 'No' && !form.missingEthicsDocuments) setError('missingEthicsDocuments', 'Please specify missing documents')
  
  if (!form.coiStatement) setError('coiStatement', 'Please select COI Statement')
  else if (form.coiStatement === 'No' && !form.reasonForMissingCoi) setError('reasonForMissingCoi', 'Please provide reason')
  
  if (!form.scopeCompliance) setError('scopeCompliance', 'Please select Scope Compliance')
  else if (form.scopeCompliance === 'No' && !form.mismatchedResearchField) setError('mismatchedResearchField', 'Please specify mismatched field')
  
  // Academic
  if (!form.originality) setError('originality', 'Please evaluate Originality')
  if (!form.scientificValue) setError('scientificValue', 'Please evaluate Scientific Value')
  if (!form.methodology) setError('methodology', 'Please evaluate Methodology')
  if (isAnyEvaluationInsufficient.value && !form.academicRemarks) setError('academicRemarks', 'Please provide Academic Remarks')
  
  // Outcome
  if (!form.finalOutcome) setError('finalOutcome', 'Please select Final Outcome')
  if (!form.detailedReason) setError('detailedReason', 'Please provide Detailed Reason')
  
  return firstErrorField
}

const isSubmitting = ref(false)
const isSuccess = ref(false)

const handleSubmit = async () => {
  const firstError = validateForm()
  if (firstError) {
    // Scroll to error
    const element = document.getElementById(firstError)
    if (element) element.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }
  
  if (confirm('Confirm submission? Cannot modify after submission')) {
    isSubmitting.value = true
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    isSubmitting.value = false
    isSuccess.value = true
    
    // Emit data to parent to update store
    emit('submit', { ...form })
    
    // Close after 3 seconds
    setTimeout(() => {
      emit('close')
      isSuccess.value = false // Reset for next time
    }, 3000)
  }
}

const handleFileUpload = (event) => {
  const files = Array.from(event.target.files)
  form.attachments.push(...files.map(f => ({ name: f.name, size: f.size })))
}

const removeAttachment = (index) => {
  form.attachments.splice(index, 1)
}

const viewFullManuscript = () => {
  window.open(`/manuscript/${props.manuscript.id}/view`, '_blank')
}

// Watchers
watch(() => props.visible, (newVal) => {
  if (newVal) {
    initForm()
  }
})

// Helper for Authors
const displayAuthors = computed(() => {
  if (!props.manuscript?.author) return ''
  // Assuming author is a string, split by comma if needed, or just use as is if simple string
  // The prompt says "Authors (first 3 + et al)"
  // If author is just a name string like "John Doe", we can't really split. 
  // But usually it's "A, B, C". Let's try to split by comma.
  const authors = props.manuscript.author.split(',').map(s => s.trim())
  if (authors.length > 3) {
    return `${authors.slice(0, 3).join(', ')} et al`
  }
  return props.manuscript.author
})

</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-container">
      <!-- Skeleton Screen -->
      <div v-if="isLoading" class="skeleton-screen">
        <div class="skeleton-header"></div>
        <div class="skeleton-body">
          <div class="skeleton-line"></div>
          <div class="skeleton-line"></div>
          <div class="skeleton-block"></div>
        </div>
      </div>
      
      <template v-else>
        <!-- Success Overlay -->
        <div v-if="isSuccess" class="success-overlay">
          <div class="success-content">
            <div class="success-icon">✓</div>
            <h3>Initial review submitted successfully</h3>
          </div>
        </div>

        <!-- Top: Basic Info (Fixed) -->
        <header class="modal-header">
          <div class="header-top">
            <h2>Initial Review - [{{ manuscript.id }}] Manuscript Initial Review</h2>
            <button class="close-btn" @click="$emit('close')" :disabled="isSuccess || isSubmitting">Close</button>
          </div>
          
          <div class="basic-info-grid">
            <div class="info-item">
              <span class="label">Manuscript ID:</span>
              <span class="value">{{ manuscript.id }}</span>
            </div>
            <div class="info-item">
              <span class="label">Title:</span>
              <span class="value">{{ manuscript.title }}</span>
            </div>
            <div class="info-item">
              <span class="label">Authors:</span>
              <span class="value">{{ displayAuthors }}</span>
            </div>
            <div class="info-item">
              <span class="label">Submission Date:</span>
              <span class="value">{{ manuscript.date }}</span>
            </div>
            <div class="info-item">
              <span class="label">Type:</span>
              <span class="value">{{ manuscript.type || 'Original Research' }}</span>
            </div>
             <div class="info-item">
              <span class="label">Field:</span>
              <span class="value">{{ manuscript.module || 'General' }}</span>
            </div>
          </div>
          
          <div class="header-actions">
            <button class="btn-outline" @click="viewFullManuscript">View Full Manuscript</button>
            <button class="btn-outline" @click="toggleAttachments">
              {{ showAttachments ? 'Hide Attachments' : 'View Attachments' }}
            </button>
          </div>
          
          <div v-if="showAttachments" class="attachments-list">
             <div class="attachment-item">
               <span>Ethics Approval</span>
               <button class="btn-link">Download</button>
             </div>
             <div class="attachment-item">
               <span>COI Statement</span>
               <button class="btn-link">Download</button>
             </div>
          </div>
        </header>
        
        <!-- Middle: Form (Scrollable) -->
        <div class="modal-body" ref="formRef">
          
          <!-- Compliance Check -->
          <section class="form-section">
            <h3>Compliance Check</h3>
            
            <div class="form-group" id="formatCompliance">
              <label class="required">Format Compliance</label>
              <div class="radio-group">
                <label v-for="opt in complianceOptions" :key="opt">
                  <input type="radio" v-model="form.formatCompliance" :value="opt"> {{ opt }}
                </label>
              </div>
              <div v-if="form.formatCompliance === 'No'" class="sub-field" id="specificFormatIssues">
                <input v-model="form.specificFormatIssues" placeholder="Specific Format Issues" class="text-input">
                <span class="error-msg" v-if="errors.specificFormatIssues">{{ errors.specificFormatIssues }}</span>
              </div>
              <span class="error-msg" v-if="errors.formatCompliance">{{ errors.formatCompliance }}</span>
            </div>
            
            <div class="form-group" id="ethicsApproval">
              <label class="required">Ethics Approval Validity</label>
              <div class="radio-group">
                <label v-for="opt in ethicsOptions" :key="opt">
                  <input type="radio" v-model="form.ethicsApproval" :value="opt"> {{ opt }}
                </label>
              </div>
              <div v-if="form.ethicsApproval === 'No'" class="sub-field" id="missingEthicsDocuments">
                <input v-model="form.missingEthicsDocuments" placeholder="Missing Ethics Documents" class="text-input">
                <span class="error-msg" v-if="errors.missingEthicsDocuments">{{ errors.missingEthicsDocuments }}</span>
              </div>
              <span class="error-msg" v-if="errors.ethicsApproval">{{ errors.ethicsApproval }}</span>
            </div>

            <div class="form-group" id="coiStatement">
              <label class="required">COI Statement Submission</label>
              <div class="radio-group">
                <label v-for="opt in complianceOptions" :key="opt">
                  <input type="radio" v-model="form.coiStatement" :value="opt"> {{ opt }}
                </label>
              </div>
              <div v-if="form.coiStatement === 'No'" class="sub-field" id="reasonForMissingCoi">
                <input v-model="form.reasonForMissingCoi" placeholder="Reason for Missing COI" class="text-input">
                <span class="error-msg" v-if="errors.reasonForMissingCoi">{{ errors.reasonForMissingCoi }}</span>
              </div>
              <span class="error-msg" v-if="errors.coiStatement">{{ errors.coiStatement }}</span>
            </div>

            <div class="form-group">
              <label>Similarity Check Result</label>
              <div class="readonly-field">{{ similarityResult }}</div>
            </div>

            <div class="form-group" id="scopeCompliance">
              <label class="required">Scope Compliance</label>
              <div class="radio-group">
                <label v-for="opt in complianceOptions" :key="opt">
                  <input type="radio" v-model="form.scopeCompliance" :value="opt"> {{ opt }}
                </label>
              </div>
              <div v-if="form.scopeCompliance === 'No'" class="sub-field" id="mismatchedResearchField">
                <input v-model="form.mismatchedResearchField" placeholder="Mismatched Research Field" class="text-input">
                <span class="error-msg" v-if="errors.mismatchedResearchField">{{ errors.mismatchedResearchField }}</span>
              </div>
               <span class="error-msg" v-if="errors.scopeCompliance">{{ errors.scopeCompliance }}</span>
            </div>
          </section>

          <!-- Academic Preliminary Judgment -->
          <section class="form-section">
            <h3>Academic Preliminary Judgment</h3>
            
            <div class="form-group" id="originality">
              <label class="required">Originality Evaluation</label>
              <select v-model="form.originality" class="select-input">
                <option value="" disabled>Select</option>
                <option v-for="opt in evaluationOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <span class="error-msg" v-if="errors.originality">{{ errors.originality }}</span>
            </div>

            <div class="form-group" id="scientificValue">
              <label class="required">Scientific Value Evaluation</label>
              <select v-model="form.scientificValue" class="select-input">
                <option value="" disabled>Select</option>
                <option v-for="opt in evaluationOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
               <span class="error-msg" v-if="errors.scientificValue">{{ errors.scientificValue }}</span>
            </div>

            <div class="form-group" id="methodology">
              <label class="required">Methodology Rigor</label>
              <select v-model="form.methodology" class="select-input">
                <option value="" disabled>Select</option>
                <option v-for="opt in evaluationOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
               <span class="error-msg" v-if="errors.methodology">{{ errors.methodology }}</span>
            </div>

            <div class="form-group" id="academicRemarks">
              <label :class="{ required: isAnyEvaluationInsufficient }">Academic Remarks</label>
              <textarea 
                v-model="form.academicRemarks" 
                rows="3" 
                class="textarea-input"
                :placeholder="isAnyEvaluationInsufficient ? 'Sample size is insufficient/Experimental design has obvious flaws' : ''"
              ></textarea>
               <span class="error-msg" v-if="errors.academicRemarks">{{ errors.academicRemarks }}</span>
            </div>
          </section>

          <!-- Initial Review Outcome -->
          <section class="form-section">
            <h3>Initial Review Outcome</h3>
            
            <div class="form-group" id="finalOutcome">
              <label class="required">Final Initial Review Outcome</label>
              <select v-model="form.finalOutcome" class="select-input">
                <option value="" disabled>Select</option>
                <option v-for="opt in outcomeOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
               <span class="error-msg" v-if="errors.finalOutcome">{{ errors.finalOutcome }}</span>
            </div>

            <div class="form-group" id="detailedReason">
              <label class="required">Detailed Reason for Outcome</label>
              <textarea 
                v-model="form.detailedReason" 
                rows="4" 
                class="textarea-input"
                placeholder="Format issues + Insufficient academic value"
              ></textarea>
               <span class="error-msg" v-if="errors.detailedReason">{{ errors.detailedReason }}</span>
            </div>

            <div class="form-group">
              <label>Attachment Upload</label>
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
        
        <!-- Bottom: Action Buttons (Fixed) -->
        <footer class="modal-footer">
          <button class="btn btn-secondary" @click="handleSaveDraft">Save Draft</button>
          <button 
            class="btn btn-primary" 
            :disabled="!isFormValid" 
            :title="!isFormValid ? 'Please complete all required fields' : ''"
            @click="handleSubmit"
          >
            Submit Initial Review
          </button>
        </footer>
      </template>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000; /* Highest priority */
}

.modal-container {
  background: white;
  width: 800px;
  max-width: 95vw;
  height: 90vh;
  display: flex;
  flex-direction: column;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
  overflow: hidden;
}

/* Header */
.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  background: #fff;
  flex-shrink: 0;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.header-top h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #2c3e50;
}

.basic-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.info-item {
  display: flex;
}

.info-item .label {
  font-weight: 600;
  color: #7f8c8d;
  width: 120px;
}

.header-actions {
  display: flex;
  gap: 1rem;
}

.attachments-list {
  margin-top: 1rem;
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
}

.attachment-item {
  display: flex;
  justify-content: space-between;
  padding: 0.25rem 0;
  font-size: 0.9rem;
}

/* Body */
.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
  background: #f9f9f9;
}

.form-section {
  background: white;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.form-section h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
  display: inline-block;
}

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

.required::after {
  content: " *";
  color: #e74c3c;
}

.sub-field {
  margin-top: 0.5rem;
  margin-left: 1.5rem;
}

/* Inputs */
.text-input, .select-input, .textarea-input {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.textarea-input {
  resize: vertical;
}

.radio-group {
  display: flex;
  gap: 1.5rem;
}

.readonly-field {
  padding: 0.6rem;
  background: #f0f2f5;
  border-radius: 4px;
  color: #555;
}

.error-msg {
  color: #e74c3c;
  font-size: 0.8rem;
  margin-top: 0.25rem;
  display: block;
}

/* Footer */
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #eee;
  background: #fff;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  flex-shrink: 0;
}

/* Buttons */
.btn {
  padding: 0.6rem 1.5rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #3498db;
  color: white;
}

.btn-primary:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.btn-secondary {
  background: #fff;
  border: 1px solid #ddd;
  color: #333;
}

.btn-outline {
  padding: 0.4rem 0.8rem;
  background: transparent;
  border: 1px solid #3498db;
  color: #3498db;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-link {
  background: none;
  border: none;
  color: #3498db;
  text-decoration: underline;
  cursor: pointer;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #7f8c8d;
}

.close-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.btn-delete {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.2rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  margin-left: 0.5rem;
  cursor: pointer;
}

/* Success Overlay */
.success-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 10;
}

.success-content {
  text-align: center;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: #27ae60;
  color: white;
  border-radius: 50%;
  font-size: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
}

.success-content h3 {
  color: #2c3e50;
  font-size: 1.2rem;
}

/* Skeleton */
.skeleton-screen {
  padding: 2rem;
  animation: pulse 1.5s infinite;
}

.skeleton-header {
  height: 100px;
  background: #f0f2f5;
  margin-bottom: 2rem;
  border-radius: 4px;
}

.skeleton-line {
  height: 20px;
  background: #f0f2f5;
  margin-bottom: 1rem;
  width: 60%;
  border-radius: 4px;
}

.skeleton-block {
  height: 200px;
  background: #f0f2f5;
  margin-top: 2rem;
  border-radius: 4px;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
