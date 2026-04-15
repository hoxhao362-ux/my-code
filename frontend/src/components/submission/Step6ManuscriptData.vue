<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import { useToastStore } from '../../stores/toast'
import StepNavigation from './StepNavigation.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import html2pdf from 'html2pdf.js'
import { useErrorScroll } from '../../composables/useErrorScroll'
import { validateORCID, validateDOI, searchInstitutions } from '../../utils/validators'

const store = useSubmissionStore()
const router = useRouter()
const { t } = useI18n()
const toastStore = useToastStore()
const submitting = ref(false)
const showPublishingModal = ref(false)
const showSuccessToast = ref(false) // Journal Platform Standard Toast State
const { scrollToError } = useErrorScroll()

// Helper: Institution Search
const showInstSuggestions = ref(null)
const instSuggestions = ref([])
const activeInstSearch = ref(null)

const handleInstSearch = async (query, index) => {
  if (query.length < 2) {
    instSuggestions.value = []
    showInstSuggestions.value = null
    return
  }
  activeInstSearch.value = index
  instSuggestions.value = await searchInstitutions(query)
  if (instSuggestions.value.length > 0) {
    showInstSuggestions.value = index
  }
}

const selectInstitution = (index, inst) => {
  store.formData.authors[index].institution = inst
  showInstSuggestions.value = null
}

// Helper: ORCID Validation
const validatingORCID = ref({})
const orcidStatus = ref({}) // { index: { valid: bool, msg: string } }

const checkORCID = async (index, orcid) => {
  if (!orcid) return
  validatingORCID.value[index] = true
  const result = await validateORCID(orcid)
  orcidStatus.value[index] = result
  validatingORCID.value[index] = false
}

// Helper: DOI Validation
const repWorkDOI = ref('')
const doiStatus = ref(null)
const validatingDOI = ref(false)

const checkDOI = async () => {
  if (!repWorkDOI.value) return
  validatingDOI.value = true
  const result = await validateDOI(repWorkDOI.value)
  doiStatus.value = result
  validatingDOI.value = false
  
  if (result.valid) {
     // Store it in form data (mock field)
     if (!store.formData.repWorkDOI) store.formData.repWorkDOI = repWorkDOI.value
  }
}

onMounted(() => {
  if (store.steps[5].status === 'error') {
    scrollToError()
  }
  if (store.formData.repWorkDOI) {
      repWorkDOI.value = store.formData.repWorkDOI
  }
})

// Quill Options
const quillOptions = {
  modules: {
    toolbar: [
      ['bold', 'italic', 'underline', 'strike'],
      [{ 'header': [1, 2, 3, false] }],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
      ['clean']
    ]
  },
  theme: 'snow'
}

// Author Management
const addAuthor = () => {
  store.formData.authors.push({
    id: Date.now(),
    name: '',
    institution: '',
    email: '',
    isCorresponding: false,
    isFirst: false
  })
}

const removeAuthor = (index) => {
  store.formData.authors.splice(index, 1)
}

const updateAuthorRole = (index, role) => {
  if (role === 'corresponding') {
    const willBeChecked = !store.formData.authors[index].isCorresponding
    
    if (willBeChecked) {
      store.formData.authors.forEach((w, i) => w.isCorresponding = i === index)
    } else {
      store.formData.authors[index].isCorresponding = false
    }
  } else if (role === 'first') {
    const willBeChecked = !store.formData.authors[index].isFirst
    
    if (willBeChecked) {
      store.formData.authors.forEach((w, i) => w.isFirst = i === index)
    } else {
      store.formData.authors[index].isFirst = false
    }
  }
}

const dragStartIdx = ref(null)
const onDragStart = (idx) => { dragStartIdx.value = idx }
const onDropItem = (dropIdx) => {
  if (dragStartIdx.value !== null && dragStartIdx.value !== dropIdx) {
    const item = store.formData.authors.splice(dragStartIdx.value, 1)[0]
    store.formData.authors.splice(dropIdx, 0, item)
  }
  dragStartIdx.value = null
}

// Funding
const addFunding = () => {
  store.formData.funding.push({ id: Date.now(), body: '', number: '' })
}
const removeFunding = (index) => {
  store.formData.funding.splice(index, 1)
}

// PDF Generation
const generatePDF = () => {
  const content = `
    <div style="font-family: Arial; padding: 20px;">
      <h1>${store.formData.title.replace(/<[^>]*>/g, '')}</h1>
      <h3>${t('manuscriptData.pdf.abstract')}</h3>
      <div>${store.formData.abstract}</div>
      <h3>${t('manuscriptData.pdf.authors')}</h3>
      <ul>
        ${store.formData.authors.map(w => `<li>${w.name} (${w.institution})</li>`).join('')}
      </ul>
      <h3>${t('manuscriptData.pdf.funding')}</h3>
      ${store.formData.noFunding ? t('manuscriptData.pdf.none') : `<ul>${store.formData.funding.map(f => `<li>${f.body} - ${f.number}</li>`).join('')}</ul>`}
    </div>
  `
  const opt = {
    margin: 1,
    filename: 'manuscript_preview.pdf',
    image: { type: 'jpeg', quality: 0.98 },
    html2canvas: { scale: 2 },
    jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
  }
  
  html2pdf().from(content).toPdf().get('pdf').then((pdf) => {
    window.open(pdf.output('bloburl'), '_blank')
  })
}

// Submit Flow
const handlePreSubmit = () => {
  // Trigger full process validation
  if (store.validateAllSteps()) {
    showPublishingModal.value = true
  } else {
    // Find first error step
    const failedStep = store.steps.find(s => s.status === 'error')
    if (failedStep) {
      store.goToStep(failedStep.id)
      
      // Journal Platform Standard Validation Messages
      let msg = 'Please complete all required sections (Article Title, Corresponding Author Info, Copyright Agreement) before submission.'
      
      if (failedStep.id === 4) {
         const info = store.formData.additionalInfo
         
         // Check Reviewers
         let hasReviewerIssue = false
         if (info.recommendedReviewers && info.recommendedReviewers.length > 0) {
             const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
             hasReviewerIssue = info.recommendedReviewers.some(r => !r.name || !r.email || !emailRegex.test(r.email) || !r.coiDeclared)
         }
         
         // Check Blind Review
         const hasBlindIssue = !info.blindReview.confirmed
         
         if (hasReviewerIssue) {
             msg = 'Please complete all required fields for Suggested Reviewers (Full Name, Email, Conflict of Interest Declaration).'
         } else if (hasBlindIssue) {
             msg = 'Please complete the Manuscript Anonymization Check and confirm no identifiable information is included.'
         }
      }
      
      toastStore.add({ message: msg, type: 'warning' })
    }
  }
}

const confirmSubmit = async () => {
  if (!store.formData.publishingOption) {
    toastStore.add({ message: 'Please select a publishing option', type: 'warning' })
    return
  }
  
  submitting.value = true
  showPublishingModal.value = false
  
  try {
    const manuscriptId = await store.submitManuscript()
    
    // Journal Platform Standard: Pure Frontend Cleanup Feedback
    showSuccessToast.value = true
    // Store ID for display if needed, though toast uses fixed text per requirements "Submission successful..."
    // Wait, user said "Submitted status: show ... 'Submitted (Manuscript ID: ${ID})'". 
    // This probably refers to the status label, not the toast.
    // The toast text requirement: "Submission successful. All draft data has been cleared for your next submission."
    
    setTimeout(() => {
      showSuccessToast.value = false
      router.push({ name: 'admin-author-dashboard' })
    }, 3000)
    
  } catch (e) {
    console.error(e)
    toastStore.add({ message: 'Submission failed. Please try again.', type: 'error' })
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('manuscriptData.title') }}</h2>

    <!-- Basic Info -->
    <div class="section">
      <h3>{{ t('generalInformation.title') }}</h3>
      <div class="form-group">
        <label class="form-label">{{ t('manuscriptData.manuscriptTitle') }} <span class="required">*</span></label>
        <QuillEditor 
          v-model:content="store.formData.title" 
          contentType="html" 
          :options="quillOptions"
          class="editor-title"
        />
      </div>
      
      <div class="form-group" v-if="store.formData.articleType === 'original'">
        <label class="form-label">Structured Abstract <span class="required">*</span></label>
        <div class="structured-abstract">
          <div class="abstract-section">
            <label>Background</label>
            <textarea v-model="store.formData.structuredAbstract.background" 
              placeholder="Describe the context and purpose of the study..."
              maxlength="100" class="form-input"></textarea>
            <span class="char-count">{{ store.formData.structuredAbstract.background?.length || 0 }}/100</span>
          </div>
          <div class="abstract-section">
            <label>Methods</label>
            <textarea v-model="store.formData.structuredAbstract.methods" 
              placeholder="Describe the study design, participants, and analytical methods..."
              maxlength="150" class="form-input"></textarea>
            <span class="char-count">{{ store.formData.structuredAbstract.methods?.length || 0 }}/150</span>
          </div>
          <div class="abstract-section">
            <label>Findings</label>
            <textarea v-model="store.formData.structuredAbstract.findings" 
              placeholder="Present the main findings with statistical significance..."
              maxlength="200" class="form-input"></textarea>
            <span class="char-count">{{ store.formData.structuredAbstract.findings?.length || 0 }}/200</span>
          </div>
          <div class="abstract-section">
            <label>Interpretation</label>
            <textarea v-model="store.formData.structuredAbstract.interpretation" 
              placeholder="Explain the meaning and implications of the findings..."
              maxlength="100" class="form-input"></textarea>
            <span class="char-count">{{ store.formData.structuredAbstract.interpretation?.length || 0 }}/100</span>
          </div>
        </div>
      </div>
      
      <div class="form-group" v-else>
        <label class="form-label">{{ t('manuscriptData.abstract') }} <span class="required">*</span></label>
        <QuillEditor 
          v-model:content="store.formData.abstract" 
          contentType="html" 
          :options="quillOptions"
          class="editor-abstract"
        />
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('manuscriptData.keywords') }} <span class="required">*</span></label>
        <input 
          type="text" 
          v-model="store.formData.keywords" 
          :placeholder="t('manuscriptData.keywordsPlaceholder')"
          class="form-input"
        >
      </div>
    </div>

    <div class="section author-section">
      <div class="section-header">
        <h3>{{ t('manuscriptData.authors.title') }}</h3>
        <button class="btn-add" @click="addAuthor">+ {{ t('manuscriptData.authors.add') }}</button>
      </div>
      
      <div class="author-list">
        <div 
          v-for="(author, index) in store.formData.authors" 
          :key="author.id"
          class="author-card"
          :class="{ 'error-border': store.steps[5].status === 'error' && (!author.name || !author.institution || !author.email) }"
          draggable="true"
          @dragstart="onDragStart(index)"
          @dragover.prevent
          @drop="onDropItem(index)"
        >
          <div class="card-header">
            <span class="drag-handle">☰ {{ t('manuscriptData.authors.title') }} {{ index + 1 }}</span>
            <button class="btn-delete" @click="removeAuthor(index)">×</button>
          </div>
          
          <div class="card-body">
            <div class="form-row">
              <input v-model="author.name" :placeholder="t('manuscriptData.authors.name')" class="form-input">
              
              <div class="inst-search-wrapper" style="position: relative; width: 100%;">
                <input 
                  v-model="author.institution" 
                  @input="e => handleInstSearch(e.target.value, index)"
                  :placeholder="t('manuscriptData.authors.institution')" 
                  class="form-input"
                >
                <ul v-if="showInstSuggestions === index && instSuggestions.length > 0" class="inst-suggestions">
                   <li v-for="inst in instSuggestions" :key="inst" @click="selectInstitution(index, inst)">{{ inst }}</li>
                </ul>
              </div>
            </div>
            <div class="form-row">
              <input v-model="author.email" :placeholder="t('manuscriptData.authors.email')" class="form-input">
              <div class="orcid-wrapper" style="width: 100%;">
                <input 
                   v-model="author.orcid" 
                   @blur="checkORCID(index, author.orcid)"
                   placeholder="ORCID (e.g. 0000-0000-0000-0000)" 
                   class="form-input"
                   :class="{'valid': orcidStatus[index]?.valid, 'invalid': orcidStatus[index]?.valid === false}"
                >
                <span v-if="validatingORCID[index]" class="status-icon">⌛</span>
                <span v-else-if="orcidStatus[index]?.valid" class="status-icon success" title="Verified">✓</span>
                <span v-else-if="orcidStatus[index]?.valid === false" class="status-icon error" :title="orcidStatus[index].message">✕</span>
              </div>
            </div>
            <div class="roles">
              <label class="radio-label">
                <input 
                  type="checkbox" 
                  class="role-checkbox"
                  :checked="author.isCorresponding"
                  @change="updateAuthorRole(index, 'corresponding')"
                > 
                {{ t('manuscriptData.authors.corresponding') }}
              </label>
              <label class="radio-label">
                <input 
                  type="checkbox" 
                  class="role-checkbox"
                  :checked="author.isFirst"
                  @change="updateAuthorRole(index, 'first')"
                > 
                {{ t('manuscriptData.authors.first') }}
              </label>
            </div>
          </div>
        </div>
      </div>
      <div v-if="store.steps[5].status === 'error'" class="error-msg">
        <div v-if="store.formData.authors.length === 0">{{ t('manuscriptData.errors.noAuthor') }}</div>
        <div v-if="!store.formData.authors.some(w => w.isCorresponding)">{{ t('manuscriptData.errors.noCorresponding') }}</div>
        <div v-if="!store.formData.authors.some(w => w.isFirst)">{{ t('manuscriptData.errors.noFirst') }}</div>
      </div>
    </div>

    <!-- Funding -->
    <div class="section">
      <div class="section-header">
        <h3>{{ t('manuscriptData.funding.title') }}</h3>
        <button class="btn-add" @click="addFunding" :disabled="store.formData.noFunding">+ {{ t('manuscriptData.funding.add') }}</button>
      </div>
      
      <div class="form-group checkbox-group">
        <label>
          <input type="checkbox" v-model="store.formData.noFunding">
          {{ t('manuscriptData.funding.noFunding') }}
        </label>
      </div>

      <div class="funding-list" :class="{ 'disabled': store.formData.noFunding }">
        <div v-for="(item, index) in store.formData.funding" :key="item.id" class="funding-row">
          <select v-model="item.body" class="form-select" :disabled="store.formData.noFunding">
            <option value="">Select Funding Body</option>
            <option value="NSFC">NSFC</option>
            <option value="NIH">NIH</option>
            <option value="Other">Other</option>
          </select>
          <input 
            v-model="item.number" 
            :placeholder="t('manuscriptData.funding.number')" 
            class="form-input"
            :disabled="store.formData.noFunding"
          >
          <button class="btn-delete-row" @click="removeFunding(index)" :disabled="store.formData.noFunding">🗑️</button>
        </div>
      </div>
      <div v-if="store.steps[5].status === 'error' && !store.formData.noFunding && store.formData.funding.length === 0" class="error-msg">
        {{ t('manuscriptData.errors.noFunding') }}
      </div>
    </div>

    <!-- Representative Work DOI Validation (Requirement #6) -->
    <div class="section">
      <div class="section-header">
        <h3>Representative Work DOI (Author Validation)</h3>
      </div>
      <div class="form-group">
        <label class="form-label">Representative Work DOI (Optional)</label>
        <div class="doi-wrapper" style="display: flex; gap: 10px; align-items: center;">
          <input 
            v-model="repWorkDOI" 
            placeholder="e.g. 10.1038/s41586-020-2012-7" 
            class="form-input"
            style="flex: 1;"
            :class="{'valid': doiStatus?.valid, 'invalid': doiStatus?.valid === false}"
          >
          <button class="btn btn-secondary" @click="checkDOI" :disabled="validatingDOI">
             {{ validatingDOI ? 'Verifying...' : 'Verify DOI' }}
          </button>
        </div>
        <div v-if="doiStatus" :class="doiStatus.valid ? 'success-msg' : 'error-msg'" style="margin-top: 5px; font-size: 13px;">
           {{ doiStatus.message }}
        </div>
        <p class="hint" style="font-size: 12px; color: #666; margin-top: 5px;">
          The system will verify the validity of the DOI link.
        </p>
      </div>
    </div>

    <!-- Actions -->
    <div class="final-actions">
      <button class="btn btn-secondary build-pdf" @click="generatePDF">
        📄 {{ t('manuscriptData.buildPDF') }}
      </button>
    </div>

    <!-- Step Nav (Custom for final step) -->
    <StepNavigation :is-final="true" :loading="submitting" @submit="handlePreSubmit" />

    <!-- Publishing Option Modal -->
    <div v-if="showPublishingModal" class="modal-overlay">
      <div class="modal-content">
        <h3>{{ t('manuscriptData.publishingOption.title') }}</h3>
        <div class="options">
          <label class="option-card">
            <input type="radio" v-model="store.formData.publishingOption" value="Subscription">
            <div class="option-info">
              <strong>{{ t('manuscriptData.publishingOption.subscription') }}</strong>
              <p>{{ t('manuscriptData.publishingOption.subscriptionDesc') }}</p>
            </div>
          </label>
          <label class="option-card">
            <input type="radio" v-model="store.formData.publishingOption" value="Open Access">
            <div class="option-info">
              <strong>{{ t('manuscriptData.publishingOption.openAccess') }}</strong>
              <p>{{ t('manuscriptData.publishingOption.openAccessDesc') }}</p>
            </div>
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn btn-secondary" @click="showPublishingModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="confirmSubmit">{{ t('common.submit') }}</button>
        </div>
      </div>
    </div>
    <!-- Journal Platform Standard Success Toast -->
    <div v-if="showSuccessToast" class="jp-toast-overlay">
      <div class="jp-toast">
        <div class="toast-icon">✓</div>
        <div class="toast-content">
          <h4>Submission successful</h4>
          <p>All draft data has been cleared for your next submission.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.jp-toast-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center; /* Center screen or top? Journal Platform usually center or top. Let's do top-center like a toast */
  align-items: flex-start;
  padding-top: 50px;
  pointer-events: none; /* Let clicks pass through if needed, but usually blocks interaction */
}

.jp-toast {
  background: #333;
  color: white;
  padding: 16px 24px;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex;
  gap: 12px;
  align-items: center;
  min-width: 300px;
  animation: slideDown 0.3s ease-out;
}

.toast-icon {
  background: #27ae60;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.toast-content h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.toast-content p {
  margin: 4px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.step-container {
  max-width: 900px;
  margin: 0 auto;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.step-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.section {
  margin-bottom: 3rem;
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.section h3 {
  margin-bottom: 1.5rem;
  color: #2c3e50;
  font-size: 1.2rem;
  border-left: 4px solid #0056B3;
  padding-left: 10px;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.required { color: #dc3545; }

.form-input, .form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

/* Author Cards */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.btn-add {
  background: #0056B3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.author-list {
  display: grid;
  gap: 1rem;
}

.author-card {
  border: 1px solid #eee;
  border-radius: 6px;
  padding: 1rem;
  background: #f9f9f9;
  cursor: move;
}

.author-card.error-border {
  border-color: #dc3545;
  background: #fff5f5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  color: #666;
  font-size: 14px;
}

.btn-delete {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 18px;
  cursor: pointer;
}

.form-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.roles {
  display: flex;
  gap: 20px;
  margin-top: 10px;
  font-size: 14px;
}

/* Funding */
.funding-list.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.funding-row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.btn-delete-row {
  background: none;
  border: none;
  cursor: pointer;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin: 20px 0;
}

.option-card {
  display: flex;
  gap: 15px;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 6px;
  cursor: pointer;
}

.option-card:hover {
  background: #f0f8ff;
  border-color: #3498db;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}
.btn-primary { background: #3498db; color: white; }
.btn-secondary { background: #eee; }

.error-msg {
  color: #e74c3c;
  margin-top: 10px;
}

.success-msg {
  color: #27ae60;
  margin-top: 10px;
}

.inst-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 100;
  max-height: 200px;
  overflow-y: auto;
  list-style: none;
  padding: 0;
  margin: 0;
}

.inst-suggestions li {
  padding: 8px 12px;
  cursor: pointer;
}.inst-suggestions li:hover {
  background: #f0f8ff;
}

.valid {
  border-color: #27ae60 !important;
  background-image: linear-gradient(to right, transparent, #e8f5e9);
}

.invalid {
  border-color: #e74c3c !important;
  background-image: linear-gradient(to right, transparent, #fdeea9);
}

.status-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
}

.orcid-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

/* Structured Abstract */
.structured-abstract {
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #eee;
}

.abstract-section {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.abstract-section label {
  font-weight: 600;
  font-size: 14px;
  color: #2c3e50;
}

.abstract-section textarea {
  min-height: 80px;
  resize: vertical;
}

.char-count {
  font-size: 12px;
  color: #7f8c8d;
  text-align: right;
}

/* Checkbox style to look like radio */.role-checkbox {
  appearance: none;
  background-color: #fff;
  margin: 0;
  font: inherit;
  color: currentColor;
  width: 1.15em;
  height: 1.15em;
  border: 0.15em solid currentColor;
  border-radius: 50%;
  display: grid;
  place-content: center;
  margin-right: 0.5em;
  cursor: pointer;
}

.role-checkbox::before {
  content: "";
  width: 0.65em;
  height: 0.65em;
  border-radius: 50%;
  transform: scale(0);
  transition: 120ms transform ease-in-out;
  box-shadow: inset 1em 1em #dc3545;
}

.role-checkbox:checked {
  border-color: #dc3545;
}

.role-checkbox:checked::before {
  transform: scale(1);
}

.radio-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 14px;
}

</style>
