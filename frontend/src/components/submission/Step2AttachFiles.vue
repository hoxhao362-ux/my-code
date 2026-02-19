<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import StepNavigation from './StepNavigation.vue'
import { useErrorScroll } from '../../composables/useErrorScroll'
// Import SparkMD5 for integrity check (Assuming it is available or we use a simple mock)
// import SparkMD5 from 'spark-md5' 

const store = useSubmissionStore()
const { t } = useI18n()
const { scrollToError } = useErrorScroll()

const uploadError = ref('')
const uploadProgress = ref(0)
const isUploading = ref(false)

onMounted(() => {
  if (store.steps[1].status === 'error') {
    scrollToError()
  }
})

const fileTypes = computed(() => {
  return [
    'manuscript', 'contribution', 'conflict', 'figure', 'table', 'supplementary'
  ].map(key => ({
    value: key,
    label: t(`attachFiles.types.${key}`)
  }))
})

const bulkType = ref('')
const fileInput = ref(null)
const dragOver = ref(false)

// Valid Extensions
const allowedExtensions = ['pdf', 'doc', 'docx']
const maxFileSize = 100 * 1024 * 1024 // 100MB

const validateFile = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!allowedExtensions.includes(ext)) {
    return 'Invalid file format. Only PDF, DOC, DOCX are supported.'
  }
  if (file.size > maxFileSize) {
    return 'File size exceeds 100MB limit.'
  }
  return null
}

const calculateMD5 = (file) => {
  return new Promise((resolve) => {
    // Mock MD5 calculation for frontend-only requirement
    // In real app, use SparkMD5 to read file chunks
    setTimeout(() => {
      resolve(`mock-md5-${file.name}-${file.size}`)
    }, 500)
  })
}

const simulateUpload = async (fileObj) => {
  isUploading.value = true
  uploadProgress.value = 0
  
  const totalSteps = 10
  for(let i = 1; i <= totalSteps; i++) {
    await new Promise(r => setTimeout(r, 200)) // Simulate network delay
    uploadProgress.value = i * 10
  }
  
  // Integrity Check
  const clientMD5 = await calculateMD5(fileObj.fileObj)
  // Mock Server MD5 (should match)
  const serverMD5 = `mock-md5-${fileObj.name}-${fileObj.size}`
  
  if (clientMD5 !== serverMD5) {
    throw new Error('File upload incomplete. Please re-upload the manuscript.')
  }
  
  isUploading.value = false
  uploadProgress.value = 0
  return true
}

const triggerUpload = () => {
  fileInput.value.click()
}

const processFiles = async (fileList) => {
  uploadError.value = ''
  
  for (const file of Array.from(fileList)) {
    // 1. Format & Size Validation
    const error = validateFile(file)
    if (error) {
      uploadError.value = error
      return
    }

    // 2. Prepare File Object
    const id = Date.now() + Math.random().toString(36).substr(2, 9)
    const newFile = {
      id,
      name: file.name,
      type: '', 
      description: '',
      size: file.size,
      fileObj: file,
      url: URL.createObjectURL(file),
      uploadStatus: 'pending' // pending, uploading, success, error
    }
    
    // 3. Add to store immediately (optimistic)
    store.formData.files.push(newFile)
    
    // 4. Simulate Upload & Integrity Check
    try {
      newFile.uploadStatus = 'uploading'
      await simulateUpload(newFile)
      newFile.uploadStatus = 'success'
      // alert('Manuscript uploaded successfully') // Optional: too many alerts if multiple files
    } catch (e) {
      newFile.uploadStatus = 'error'
      uploadError.value = e.message
      // Remove failed file or keep it with error state?
      // For now, let's keep it but mark as error
      alert(`Upload failed: ${e.message}`)
    }
  }
}

const handleFileChange = (e) => {
  if (e.target.files.length) {
    processFiles(e.target.files)
    e.target.value = '' // Reset
  }
}

const onDrop = (e) => {
  dragOver.value = false
  if (e.dataTransfer.files.length) {
    processFiles(e.dataTransfer.files)
  }
}

const handleBulkUpdate = () => {
  if (bulkType.value) {
    store.formData.files.forEach(f => {
      f.type = bulkType.value
    })
  }
}

const removeFile = (id) => {
  if (confirm(t('attachFiles.confirmDelete'))) {
    const idx = store.formData.files.findIndex(f => f.id === id)
    if (idx !== -1) store.formData.files.splice(idx, 1)
  }
}

const downloadFile = (file) => {
  const link = document.createElement('a')
  link.href = file.url
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// Simple drag sort implementation
const dragStartIdx = ref(null)

const onDragStart = (idx) => {
  dragStartIdx.value = idx
}

const onDragOverItem = (e) => {
  e.preventDefault() // Allow drop
}

const onDropItem = (dropIdx) => {
  if (dragStartIdx.value !== null && dragStartIdx.value !== dropIdx) {
    const item = store.formData.files.splice(dragStartIdx.value, 1)[0]
    store.formData.files.splice(dropIdx, 0, item)
  }
  dragStartIdx.value = null
}

// Reference Anonymization Logic
const hasCheckedCitations = ref(false)

const checkSelfCitations = () => {
  // Simulate scan
  hasCheckedCitations.value = true
  alert("Potential self-citations detected: 3 references need anonymization.")
}

const handleAnonFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    // Validate PDF/Word
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['pdf', 'doc', 'docx'].includes(ext)) {
      alert('Invalid file format. Only PDF, DOC, DOCX are supported.')
      e.target.value = ''
      return
    }
    
    store.formData.referenceAnonymization.file = {
      name: file.name,
      url: URL.createObjectURL(file),
      size: file.size
    }
  }
}
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('attachFiles.title') }}</h2>
    
    <!-- Upload Error Message -->
    <div v-if="uploadError" class="error-msg" style="margin-bottom: 1rem;">
      {{ uploadError }}
    </div>

    <!-- Upload Area -->
    <div 
      class="upload-area" 
      :class="{ 'drag-over': dragOver }"
      @dragover.prevent="dragOver = true"
      @dragleave.prevent="dragOver = false"
      @drop.prevent="onDrop"
      @click="triggerUpload"
    >
      <div class="upload-content">
        <div class="upload-icon">☁️</div>
        <p>{{ t('attachFiles.dragDrop') }}</p>
        <p class="upload-hint">Supported Formats: PDF, DOC, DOCX only (Max 100MB)</p>
        <button class="btn-browse">{{ t('attachFiles.browse') }}</button>
      </div>
      <input 
        type="file" 
        ref="fileInput" 
        multiple 
        style="display: none" 
        accept=".pdf,.doc,.docx"
        @change="handleFileChange"
      >
    </div>
    
    <!-- Global Progress (Optional visualization) -->
    <div v-if="isUploading" class="upload-progress-bar">
       <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
       <span class="progress-text">Uploading: {{ uploadProgress }}%</span>
    </div>

    <!-- File List -->
    <div v-if="store.formData.files.length > 0" class="file-list-section">
      <div class="bulk-actions">
        <label>{{ t('attachFiles.bulkUpdate') }}:</label>
        <select v-model="bulkType" @change="handleBulkUpdate" class="form-select bulk-select">
          <option value="">{{ t('attachFiles.placeholders.selectType') }}</option>
          <option v-for="type in fileTypes" :key="type.value" :value="type.value">
            {{ type.label }}
          </option>
        </select>
      </div>

      <div class="file-table-header">
        <div class="col-name">{{ t('attachFiles.fileName') }}</div>
        <div class="col-type">{{ t('attachFiles.fileType') }} <span class="required">*</span></div>
        <div class="col-desc">{{ t('attachFiles.description') }}</div>
        <div class="col-actions">{{ t('attachFiles.actions') }}</div>
      </div>

      <transition-group name="list" tag="div" class="file-list">
        <div 
          v-for="(file, index) in store.formData.files" 
          :key="file.id" 
          class="file-item"
          draggable="true"
          @dragstart="onDragStart(index)"
          @dragover="onDragOverItem"
          @drop="onDropItem(index)"
        >
          <div class="col-name" :title="file.name">
            <span class="drag-handle">☰</span>
            {{ file.name }}
            <span v-if="file.uploadStatus === 'uploading'" class="status-uploading"> (Uploading...)</span>
            <span v-if="file.uploadStatus === 'success'" class="status-success"> ✅</span>
            <span v-if="file.uploadStatus === 'error'" class="status-error"> ❌ Error</span>
          </div>
          <div class="col-type">
            <select v-model="file.type" class="form-select sm">
              <option value="">{{ t('attachFiles.placeholders.selectType') }}</option>
              <option v-for="type in fileTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
          </div>
          <div class="col-desc">
            <input 
              type="text" 
              v-model="file.description" 
              :placeholder="t('attachFiles.placeholders.description')"
              class="form-input sm"
            >
          </div>
          <div class="col-actions">
            <button @click="downloadFile(file)" class="btn-icon" :title="t('attachFiles.download')">⬇️</button>
            <button @click="removeFile(file.id)" class="btn-icon danger" :title="t('attachFiles.delete')">🗑️</button>
          </div>
        </div>
      </transition-group>
    </div>

    <div v-if="store.steps[1].status === 'error'" class="error-msg">
      {{ t('attachFiles.errors.noFile') }}
    </div>

    <!-- Reference Anonymization Section -->
    <div class="anonymization-section">
      <h3 class="section-title">Reference Anonymization for Blind Review</h3>
      
      <div class="check-action">
        <button class="btn-check" @click="checkSelfCitations">Check Self-Citations</button>
        <span v-if="hasCheckedCitations" class="check-result warning">
          ⚠️ Potential self-citations detected: 3 references need anonymization.
        </span>
      </div>

      <div class="upload-anon-file" v-if="hasCheckedCitations">
        <label class="field-label">Upload Anonymized References (PDF/Word)</label>
        <div class="file-input-wrapper">
          <input type="file" accept=".pdf,.doc,.docx" @change="handleAnonFileChange">
          <span v-if="store.formData.referenceAnonymization.file" class="file-name">
            {{ store.formData.referenceAnonymization.file.name }}
          </span>
        </div>
      </div>

      <div class="confirm-checkbox">
        <label class="checkbox-label">
          <input type="checkbox" v-model="store.formData.referenceAnonymization.confirmed">
          <span class="checkbox-text">I confirm all self-citations have been anonymized</span>
        </label>
      </div>
      
      <div v-if="store.steps[1].status === 'error' && !store.formData.referenceAnonymization.confirmed" class="error-text">
        Please confirm reference anonymization.
      </div>
    </div>

    <StepNavigation />
  </div>
</template>

<style scoped>
.step-container {
  max-width: 1000px;
  margin: 0 auto;
}

.step-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.upload-area {
  border: 2px dashed #ccc;
  border-radius: 8px;
  padding: 3rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fdfdfd;
}

.upload-area:hover, .upload-area.drag-over {
  border-color: #3498db;
  background: #f0f8ff;
}

.upload-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
  color: #3498db;
}

.btn-browse {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.upload-hint {
  font-size: 0.9rem;
  color: #666;
  margin-top: 5px;
}

.upload-progress-bar {
  margin-top: 1rem;
  height: 20px;
  background-color: #f3f3f3;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.progress-fill {
  height: 100%;
  background-color: #3498db;
  transition: width 0.3s ease;
}

.progress-text {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.8rem;
  color: #333;
  line-height: 20px;
}

.status-uploading { color: #3498db; font-size: 0.8rem; font-style: italic; }
.status-success { color: #2ecc71; font-size: 0.8rem; }
.status-error { color: #e74c3c; font-size: 0.8rem; }

.file-list-section {
  margin-top: 2rem;
}

.bulk-actions {
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
}

.file-table-header {
  display: flex;
  padding: 0.8rem;
  background: #eee;
  font-weight: 600;
  border-radius: 4px 4px 0 0;
}

.file-item {
  display: flex;
  padding: 0.8rem;
  border-bottom: 1px solid #eee;
  align-items: center;
  background: white;
  transition: background 0.2s;
}

.file-item:hover {
  background: #f9f9f9;
}

.col-name { flex: 2; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; display: flex; align-items: center; gap: 8px; }
.col-type { flex: 1.5; padding: 0 10px; }
.col-desc { flex: 2; padding: 0 10px; }
.col-actions { flex: 0.5; display: flex; gap: 5px; justify-content: center; }

.drag-handle { cursor: move; color: #999; }

.form-select, .form-input {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 4px;
  border-radius: 4px;
}
.btn-icon:hover { background: #eee; }
.btn-icon.danger:hover { background: #fee; color: red; }

.error-msg {
  color: #e74c3c;
  margin-top: 1rem;
  font-weight: 500;
}

/* List transition */
.list-move {
  transition: transform 0.5s;
}

/* Anonymization Section */
.anonymization-section {
  margin-top: 3rem;
  padding: 1.5rem;
  background: #fdfdfd;
  border: 1px solid #eee;
  border-radius: 8px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 1rem;
}

.check-action {
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-check {
  padding: 8px 16px;
  background: white;
  border: 1px solid #C93737;
  color: #C93737;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-check:hover {
  background: #fff5f5;
}

.check-result.warning {
  color: #e67e22;
  font-weight: 500;
  font-size: 0.9rem;
}

.upload-anon-file {
  margin-bottom: 1.5rem;
}

.field-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #555;
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.file-name {
  color: #2ecc71;
  font-size: 0.9rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-text {
  font-weight: 500;
  color: #333;
}
</style>
