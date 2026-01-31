<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import StepNavigation from './StepNavigation.vue'
import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'
import html2pdf from 'html2pdf.js'
import { useErrorScroll } from '../../composables/useErrorScroll'

const store = useSubmissionStore()
const { t } = useI18n()
const submitting = ref(false)
const showPublishingModal = ref(false)
const { scrollToError } = useErrorScroll()

onMounted(() => {
  if (store.steps[5].status === 'error') {
    scrollToError()
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
    store.formData.authors.forEach((a, i) => a.isCorresponding = i === index)
  } else if (role === 'first') {
    store.formData.authors.forEach((a, i) => a.isFirst = i === index)
  }
}

// Drag Sort Authors
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
        ${store.formData.authors.map(a => `<li>${a.name} (${a.institution})</li>`).join('')}
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
  if (store.validateCurrentStep()) {
    showPublishingModal.value = true
  } else {
    window.scrollTo(0, 0)
  }
}

const confirmSubmit = async () => {
  if (!store.formData.publishingOption) {
    alert('Please select a publishing option')
    return
  }
  
  submitting.value = true
  showPublishingModal.value = false
  
  try {
    await store.submitManuscript()
    alert(t('manuscriptData.successMessage'))
    window.location.href = '/' 
  } catch (e) {
    alert('Submission failed')
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
      
      <div class="form-group">
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

    <!-- Authors -->
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
              <input v-model="author.institution" :placeholder="t('manuscriptData.authors.institution')" class="form-input">
            </div>
            <div class="form-row">
              <input v-model="author.email" :placeholder="t('manuscriptData.authors.email')" class="form-input full">
            </div>
            <div class="roles">
              <label>
                <input 
                  type="radio" 
                  name="corresponding" 
                  :checked="author.isCorresponding"
                  @change="updateAuthorRole(index, 'corresponding')"
                > 
                {{ t('manuscriptData.authors.corresponding') }}
              </label>
              <label>
                <input 
                  type="radio" 
                  name="first" 
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
        <div v-if="!store.formData.authors.some(a => a.isCorresponding)">{{ t('manuscriptData.errors.noCorresponding') }}</div>
        <div v-if="!store.formData.authors.some(a => a.isFirst)">{{ t('manuscriptData.errors.noFirst') }}</div>
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
  </div>
</template>

<style scoped>
.step-container {
  max-width: 900px;
  margin: 0 auto;
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
  border-left: 4px solid #3498db;
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

.required { color: #e74c3c; }

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
  background: #3498db;
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
  border-color: #e74c3c;
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
</style>
