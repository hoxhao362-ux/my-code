<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import { useToastStore } from '../../stores/toast'
import StepNavigation from './StepNavigation.vue'
import { useErrorScroll } from '../../composables/useErrorScroll'

const store = useSubmissionStore()
const { t } = useI18n()
const toastStore = useToastStore()
const { scrollToError } = useErrorScroll()

const uploadError = ref('')
const uploadProgress = ref(0)
const isUploading = ref(false)

const showDeleteConfirm = ref(false)
const fileToDelete = ref(null)

const requiredFileTypes = ['manuscript', 'contribution', 'conflict']

const requiredFilesStatus = computed(() => {
  const status = {}
  requiredFileTypes.forEach(type => {
    status[type] = store.formData.files.some(f => f.type === type && f.uploadStatus !== 'error')
  })
  return status
})

const allRequiredFilesUploaded = computed(() => {
  return requiredFileTypes.every(type => requiredFilesStatus.value[type])
})

const missingRequiredFiles = computed(() => {
  return requiredFileTypes.filter(type => !requiredFilesStatus.value[type])
})

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
const maxFileSize = 20 * 1024 * 1024 // 统一为 20MB 与后端/前文保持一致

const validateFile = (file) => {
  const ext = file.name.split('.').pop().toLowerCase()
  if (!allowedExtensions.includes(ext)) {
    return 'Invalid file format. Only PDF, DOC, DOCX are supported.'
  }
  if (file.size > maxFileSize) {
    return 'File size exceeds 20MB limit.'
  }
  return null
}

// 移除 MD5 计算，仅模拟本地加载动画，真实哈希由后端 /manuscripts 接口生成
const simulateUpload = async (fileObj) => {
  isUploading.value = true
  uploadProgress.value = 0
  
  const totalSteps = 10
  for(let i = 1; i <= totalSteps; i++) {
    await new Promise(r => setTimeout(r, 100)) // 缩短本地模拟延迟
    uploadProgress.value = i * 10
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
      toastStore.add({ message: `File uploaded: ${newFile.name}`, type: 'success' })
    } catch (e) {
      newFile.uploadStatus = 'error'
      uploadError.value = e.message
      // Remove failed file or keep it with error state?
      // For now, let's keep it but mark as error
      toastStore.add({ message: `Upload failed: ${e.message}`, type: 'error' })
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
  // Show custom confirmation dialog
  fileToDelete.value = id
  showDeleteConfirm.value = true
}

const confirmDelete = () => {
  // Only delete if user confirmed
  if (fileToDelete.value) {
    const fileIndex = store.formData.files.findIndex(file => file.id === fileToDelete.value)
    if (fileIndex !== -1) {
      store.formData.files.splice(fileIndex, 1)
    }
    // Close dialog
    showDeleteConfirm.value = false
    fileToDelete.value = null
  }
}

const cancelDelete = () => {
  // Close dialog without deleting
  showDeleteConfirm.value = false
  fileToDelete.value = null
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

const showSelfCitationModal = ref(false)
const selfCitationResults = ref({
  total: 0,
  detected: 0,
  items: []
})

const checkSelfCitations = () => {
  // Simulate scan
  // Mock Data
  const mockTotal = 45
  const mockItems = [
    {
      id: 'ref-1',
      text: 'Smith, A. B., et al. (2023). Study on X. Journal of Y, 10(1), 1–10.',
      highlight: 'Smith, A. B.',
      reason: 'Contains author name(s) from your manuscript',
      status: 'pending' // pending, anonymized
    },
    {
      id: 'ref-2',
      text: 'Research Group of Z University. (2022). Annual Report.',
      highlight: 'Z University',
      reason: 'Includes institutional affiliation from your manuscript',
      status: 'pending'
    }
  ]
  
  selfCitationResults.value = {
    total: mockTotal,
    detected: mockItems.length,
    items: mockItems
  }
  
  hasCheckedCitations.value = true
  showSelfCitationModal.value = true
}

const markAsAnonymized = (id) => {
  const item = selfCitationResults.value.items.find(i => i.id === id)
  if (item) {
    item.status = 'anonymized'
    // Update text to show it's anonymized (Mock)
    item.text = item.text.replace(item.highlight, '[Anonymous]')
  }
}

const downloadTemplate = () => {
  toastStore.add({ message: 'Downloading Anonymization Template...', type: 'info' })
}

const allAnonymized = computed(() => {
  return selfCitationResults.value.items.every(i => i.status === 'anonymized')
})

const closeSelfCitationModal = () => {
  showSelfCitationModal.value = false
  // If all anonymized, auto-check confirmation? No, let user do it.
  // But we can show a success message or update the warning.
}

const handleAnonFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    // Validate PDF/Word
    const ext = file.name.split('.').pop().toLowerCase()
    if (!['pdf', 'doc', 'docx'].includes(ext)) {
      toastStore.add({ message: 'Invalid file format. Only PDF, DOC, DOCX are supported.', type: 'error' })
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

    <!-- Required Files Status Section -->
    <div class="required-files-section">
      <h3 class="section-title">{{ t('attachFiles.requiredFiles.title') }}</h3>
      <p class="section-desc">{{ t('attachFiles.requiredFiles.description') }}</p>
      
      <div class="required-files-grid">
        <div 
          v-for="type in requiredFileTypes" 
          :key="type" 
          class="required-file-item"
          :class="{ 'uploaded': requiredFilesStatus[type] }"
        >
          <div class="file-status-icon">
            <span v-if="requiredFilesStatus[type]" class="status-check">✓</span>
            <span v-else class="status-pending">○</span>
          </div>
          <div class="file-info">
            <div class="file-name">{{ t(`attachFiles.types.${type}`) }}</div>
            <div class="file-desc">{{ t(`attachFiles.requiredFiles.descriptions.${type}`) }}</div>
          </div>
          <div class="file-required-badge">
            <span class="required-star">*</span>
            {{ t('common.required') }}
          </div>
        </div>
      </div>
      
      <div v-if="!allRequiredFilesUploaded && store.formData.files.length > 0" class="missing-files-warning">
        <span class="warning-icon">⚠️</span>
        {{ t('attachFiles.requiredFiles.missingWarning') }}
        <strong>{{ missingRequiredFiles.map(f => t(`attachFiles.types.${f}`)).join(', ') }}</strong>
      </div>
      
      <div v-if="allRequiredFilesUploaded" class="all-files-uploaded">
        <span class="success-icon">✅</span>
        {{ t('attachFiles.requiredFiles.allUploaded') }}
      </div>
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
        <p class="upload-hint">Supported Formats: PDF, DOC, DOCX only (Max 20MB)</p>
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
      <template v-if="!allRequiredFilesUploaded && store.formData.files.length > 0">
        {{ t('attachFiles.requiredFiles.missingError') }}
      </template>
      <template v-else>
        {{ t('attachFiles.errors.noFile') }}
      </template>
    </div>

    <!-- Reference Anonymization Section -->
    <div class="anonymization-section">
      <h3 class="section-title">Reference Anonymization for Blind Review</h3>
      
      <div class="check-action">
        <button class="btn-check" @click="checkSelfCitations">Check Self-Citations</button>
        <span v-if="hasCheckedCitations && !allAnonymized" class="check-result warning">
          ⚠️ Potential self-citations detected: {{ selfCitationResults.detected }} references need anonymization.
        </span>
        <span v-if="hasCheckedCitations && allAnonymized" class="check-result success">
          ✅ All self-citations marked as anonymized.
        </span>
      </div>

      <!-- Self Citation Modal -->
      <div v-if="showSelfCitationModal" class="modal-overlay" @click.self="closeSelfCitationModal">
        <div class="modal-content large-modal">
          <div class="modal-header">
            <h3>Self-Citation Check Results</h3>
            <button class="btn-close" @click="closeSelfCitationModal">×</button>
          </div>
          
          <div class="modal-body">
            <!-- Overview -->
            <div class="sc-section overview">
              <h4>Overview</h4>
              <p>We have completed a self-citation check of your reference list.</p>
              <div class="sc-stats">
                <div class="stat-item">Total references checked: <strong>{{ selfCitationResults.total }}</strong></div>
                <div class="stat-item">Potential self-citations detected: <strong>{{ selfCitationResults.detected }}</strong></div>
              </div>
              <div v-if="!allAnonymized" class="sc-alert">
                ⚠️ If any self-citations are detected, they must be anonymized before you can confirm completion and proceed with submission.
              </div>
            </div>

            <!-- Detected List -->
            <div class="sc-section detected-list">
              <h4>Detected Self-Citations</h4>
              <p class="sc-subtitle">Each potential self-citation is listed below with details:</p>
              
              <div v-for="item in selfCitationResults.items" :key="item.id" class="sc-item" :class="{ 'is-anonymized': item.status === 'anonymized' }">
                <div class="sc-item-header">
                  <span class="sc-id">Reference ID: {{ item.id }}</span>
                  <span class="sc-status" :class="item.status">{{ item.status === 'anonymized' ? 'Anonymized' : 'Requires Anonymization' }}</span>
                </div>
                <div class="sc-row">
                  <span class="sc-label">Citation text:</span>
                  <div class="sc-text" v-html="item.text.replace(item.highlight, `<span class='highlight'>${item.highlight}</span>`)"></div>
                </div>
                <div class="sc-row">
                  <span class="sc-label">Reason flagged:</span>
                  <div class="sc-reason">{{ item.reason }}</div>
                </div>
                <div class="sc-actions" v-if="item.status !== 'anonymized'">
                  <button class="btn-sm btn-primary" @click="markAsAnonymized(item.id)">Mark as Anonymized</button>
                </div>
              </div>
            </div>

            <!-- Guidelines -->
            <div class="sc-section guidelines">
              <h4>Anonymization Guidelines</h4>
              <p>To ensure blind review, please anonymize all self-citations using one of the following formats:</p>
              
              <div class="example-box">
                <div class="example-title">Example 1:</div>
                <div class="example-row">
                  <span class="ex-label">Before (non-anonymized):</span>
                  <span class="ex-text">Smith, A. B., et al. (2023). Study on X. Journal of Y, 10(1), 1–10.</span>
                </div>
                <div class="example-row">
                  <span class="ex-label">After (anonymized):</span>
                  <span class="ex-text"><strong>[Anonymous]</strong>, et al. (2023). Study on X. Journal of Y, 10(1), 1–10.</span>
                </div>
              </div>

              <div class="example-box">
                <div class="example-title">Example 2:</div>
                <div class="example-row">
                  <span class="ex-label">Before (non-anonymized):</span>
                  <span class="ex-text">Smith, A. B., & Jones, C. D. (2022). Research on Z. Journal of W, 8(3), 201–215.</span>
                </div>
                <div class="example-row">
                  <span class="ex-label">After (anonymized):</span>
                  <span class="ex-text"><strong>A study on Z</strong> (2022). Journal of W, 8(3), 201–215.</span>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-footer space-between">
            <div class="footer-left">
               <button class="btn btn-outline" @click="downloadTemplate">Download Anonymization Template</button>
            </div>
            <div class="footer-right">
               <button class="btn btn-secondary" @click="closeSelfCitationModal">Close</button>
            </div>
          </div>
          
          <div class="modal-bottom-alert" v-if="!allAnonymized">
             Important Note: All self-citations must be anonymized before you can confirm completion and proceed with submission.
          </div>
        </div>
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

    <!-- Custom Delete Confirmation Dialog -->
    <div v-if="showDeleteConfirm" class="modal-overlay" @click.self="cancelDelete">
      <div class="modal-content small-modal">
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button class="btn-close" @click="cancelDelete">×</button>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete this file? This action cannot be undone.</p>
        </div>

        <div class="modal-footer">
          <div class="footer-actions">
            <button class="btn btn-secondary" @click="cancelDelete">Cancel</button>
            <button class="btn btn-danger" @click="confirmDelete">Delete</button>
          </div>
        </div>
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

.required-files-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.required-files-section .section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.section-desc {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 1rem;
}

.required-files-grid {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.required-file-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 6px;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
}

.required-file-item.uploaded {
  background: #f0fff4;
  border-color: #28a745;
}

.file-status-icon {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 1rem;
  font-size: 1.2rem;
}

.status-check {
  color: #28a745;
  font-weight: bold;
}

.status-pending {
  color: #adb5bd;
}

.file-info {
  flex: 1;
}

.file-info .file-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.file-info .file-desc {
  font-size: 0.85rem;
  color: #6c757d;
  line-height: 1.4;
}

.file-required-badge {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85rem;
  color: #dc3545;
  font-weight: 500;
}

.required-star {
  color: #dc3545;
}

.missing-files-warning {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 4px;
  color: #856404;
  font-size: 0.9rem;
}

.warning-icon {
  margin-right: 0.5rem;
}

.all-files-uploaded {
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  background: #d4edda;
  border: 1px solid #28a745;
  border-radius: 4px;
  color: #155724;
  font-size: 0.9rem;
  font-weight: 500;
}

.success-icon {
  margin-right: 0.5rem;
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

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content.large-modal {
  width: 800px;
  max-width: 95vw;
  height: 85vh;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.modal-content.small-modal {
  width: 400px;
  max-width: 95vw;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 4px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.btn-danger {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 10px 20px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-danger:hover {
  background: #c0392b;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  width: 100%;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-secondary {
  background: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background: #7f8c8d;
}

.modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #ddd;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.sc-section {
  margin-bottom: 2rem;
}

.sc-section h4 {
  font-size: 1rem;
  color: #2c3e50;
  border-bottom: 2px solid #3498db;
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
  display: inline-block;
}

.sc-stats {
  display: flex;
  gap: 2rem;
  margin: 1rem 0;
  background: #f0f7ff;
  padding: 1rem;
  border-radius: 4px;
}

.sc-alert {
  background: #fff3cd;
  color: #856404;
  padding: 0.8rem;
  border: 1px solid #ffeeba;
  border-radius: 4px;
  margin-top: 1rem;
}

.sc-item {
  border: 1px solid #eee;
  padding: 1rem;
  margin-bottom: 1rem;
  border-radius: 4px;
  background: #fff;
}

.sc-item.is-anonymized {
  background: #f9fff9;
  border-color: #d4edda;
}

.sc-item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.8rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.sc-id { font-weight: bold; color: #555; }
.sc-status { padding: 2px 8px; border-radius: 12px; font-size: 0.8rem; font-weight: bold; }
.sc-status.pending { background: #ffeeba; color: #856404; }
.sc-status.anonymized { background: #d4edda; color: #155724; }

.sc-row { margin-bottom: 0.5rem; }
.sc-label { font-weight: 600; color: #666; display: block; font-size: 0.9rem; }
.sc-text { background: #f9f9f9; padding: 0.5rem; border-radius: 4px; font-family: monospace; font-size: 0.9rem; }
.sc-reason { color: #e74c3c; font-size: 0.9rem; }

:deep(.highlight) { background-color: #ffeeba; padding: 0 2px; }

.sc-actions { margin-top: 1rem; text-align: right; }

.example-box {
  background: #f8f9fa;
  padding: 1rem;
  margin-bottom: 1rem;
  border-left: 3px solid #3498db;
}

.example-title { font-weight: bold; margin-bottom: 0.5rem; color: #3498db; }
.example-row { display: flex; margin-bottom: 0.3rem; font-size: 0.9rem; }
.ex-label { width: 180px; color: #666; flex-shrink: 0; }
.ex-text { font-family: monospace; }

.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #ddd;
  background: #f8f9fa;
}

.modal-footer.space-between {
  display: flex;
  justify-content: space-between;
}

.modal-bottom-alert {
  background: #C93737;
  color: white;
  padding: 0.5rem;
  text-align: center;
  font-weight: 500;
  font-size: 0.9rem;
}

.check-result.success {
  color: #2ecc71;
  font-weight: 500;
  font-size: 0.9rem;
}

.btn-sm { padding: 4px 12px; font-size: 0.85rem; }
.btn-primary { background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-secondary { background: #95a5a6; color: white; border: none; border-radius: 4px; cursor: pointer; }
.btn-outline { background: white; border: 1px solid #ccc; color: #333; border-radius: 4px; cursor: pointer; }</style>
