<script setup>
import { ref, computed, onMounted } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import StepNavigation from './StepNavigation.vue'
import { useErrorScroll } from '../../composables/useErrorScroll'

const store = useSubmissionStore()
const { t } = useI18n()
const { scrollToError } = useErrorScroll()

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

const triggerUpload = () => {
  fileInput.value.click()
}

const processFiles = (fileList) => {
  Array.from(fileList).forEach(file => {
    // Generate a simple ID
    const id = Date.now() + Math.random().toString(36).substr(2, 9)
    store.formData.files.push({
      id,
      name: file.name,
      type: '', // Default empty, user must select
      description: '',
      size: file.size,
      fileObj: file, // Keep raw file for upload
      url: URL.createObjectURL(file) // For preview/download
    })
  })
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
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('attachFiles.title') }}</h2>

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
        <button class="btn-browse">{{ t('attachFiles.browse') }}</button>
      </div>
      <input 
        type="file" 
        ref="fileInput" 
        multiple 
        style="display: none" 
        @change="handleFileChange"
      >
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
</style>
