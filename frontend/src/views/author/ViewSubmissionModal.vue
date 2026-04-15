<script setup>
import { defineProps, defineEmits, ref } from 'vue'
import AttachmentsModal from './AttachmentsModal.vue'
import PdfPreviewModal from '../../components/PdfPreviewModal.vue'

const props = defineProps({
  visible: Boolean,
  manuscript: Object
})

const emit = defineEmits(['close'])

const isGeneratingPdf = ref(false)
const showSuccessMessage = ref(false)
const showAttachmentsModal = ref(false)
const showPdfPreview = ref(false)
const pdfUrl = ref('')

const generatePdfBlob = () => {
  const content = `
      Manuscript ID: ${props.manuscript.id}
      Title: ${props.manuscript.title}
      Author: ${props.manuscript.author}
      Submission Date: ${props.manuscript.submittedDate}
      
      Abstract:
      ${props.manuscript.abstract || 'No abstract'}
      
      [Main Content Placeholder]
      This is a generated PDF simulation for the manuscript.
      
      (In a real application, this would be a real PDF file fetched from the server)
    `
  return new Blob([content], { type: 'text/plain' })
}

const handlePreview = () => {
  if (!props.manuscript) return
  isGeneratingPdf.value = true
  
  setTimeout(() => {
    const blob = generatePdfBlob()
    pdfUrl.value = window.URL.createObjectURL(blob)
    showPdfPreview.value = true
    isGeneratingPdf.value = false
  }, 1000)
}

const handleDownload = () => {
  if (!props.manuscript) return
  
  isGeneratingPdf.value = true
  
  // Simulate PDF generation delay (1.5s)
  setTimeout(() => {
    const blob = generatePdfBlob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    // Naming rule: Manuscript_[ManuscriptID]_[SubmissionDate].pdf
    const dateStr = new Date().toISOString().split('T')[0].replace(/-/g, '')
    link.download = `Manuscript_${props.manuscript.id}_${dateStr}.txt` // Changed to txt for simulation accuracy
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    isGeneratingPdf.value = false
    
    // Show success message
    showSuccessMessage.value = true
    setTimeout(() => {
      showSuccessMessage.value = false
    }, 3000)
    
  }, 1500)
}

const handleViewAttachments = () => {
  showAttachmentsModal.value = true
}

// Mock Ethics Statement
const ethicsStatement = "This study was conducted in accordance with the Declaration of Helsinki. Informed consent was obtained from all participants."
</script>

<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <h3>Manuscript Details: {{ manuscript?.title }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-content">
        <!-- Metadata -->
        <div class="section metadata">
          <div class="meta-item">
            <span class="label">ID:</span>
            <span class="value">#{{ manuscript?.id }}</span>
          </div>
          <div class="meta-item">
            <span class="label">Author:</span>
            <span class="value">{{ manuscript?.author }}</span>
          </div>
          <div class="meta-item">
            <span class="label">Submitted:</span>
            <span class="value">{{ manuscript?.submittedDate }}</span>
          </div>
          <div class="meta-item">
            <span class="label">Status:</span>
            <span class="value status-badge">{{ manuscript?.status }}</span>
          </div>
        </div>

        <!-- Content -->
        <div class="section content-area">
          <h4>Abstract</h4>
          <p class="abstract-text">
            {{ manuscript?.abstract || 'No abstract available for this manuscript.' }}
          </p>

          <h4>Main Content Preview</h4>
          <div class="content-preview">
            <p>[Mock Content] The main body of the manuscript would be displayed here...</p>
          </div>

          <h4>Attachments Summary</h4>
          <ul class="attachment-list">
            <li>
              <span class="file-icon">📄</span>
              <span class="file-name">Main_Manuscript.pdf</span>
              <span class="file-size">(2.4 MB)</span>
            </li>
            <li>
              <span class="file-icon">📊</span>
              <span class="file-name">Supplementary_Data.xlsx</span>
              <span class="file-size">(1.1 MB)</span>
            </li>
          </ul>

          <h4>Ethics Statement</h4>
          <div class="ethics-box">
            {{ ethicsStatement }}
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <div v-if="showSuccessMessage" class="success-msg">
           ✓ PDF downloaded successfully
        </div>
        <button 
          class="btn btn-primary" 
          @click="handleDownload"
          :disabled="isGeneratingPdf"
        >
          <span v-if="isGeneratingPdf" class="spinner">⏳</span>
          {{ isGeneratingPdf ? 'Generating...' : 'Download PDF' }}
        </button>
        <button class="btn btn-info" @click="handlePreview">Preview PDF</button>
        <button class="btn btn-secondary" @click="handleViewAttachments">View Attachments</button>
        <button class="btn btn-outline" @click="$emit('close')">Close</button>
      </div>
    </div>
    
    <!-- Nested Modal -->
    <AttachmentsModal 
      :visible="showAttachmentsModal"
      :manuscript="manuscript"
      @close="showAttachmentsModal = false"
    />

    <!-- PDF Preview Modal -->
    <PdfPreviewModal
      v-if="showPdfPreview"
      :visible="showPdfPreview"
      :file-url="pdfUrl"
      :file-name="`Manuscript_${manuscript?.id}.pdf`"
      @close="showPdfPreview = false"
    />
  </div>
</template>

<style scoped>
.btn-info {
  background: #17a2b8;
  color: white;
}
.btn-info:hover {
  background: #138496;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-box {
  background: white;
  width: 700px;
  max-width: 90%;
  max-height: 90vh;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.section {
  margin-bottom: 1.5rem;
}

.metadata {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  background: #f9f9f9;
  padding: 1rem;
  border-radius: 4px;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.label {
  font-size: 0.85rem;
  color: #666;
  margin-bottom: 0.25rem;
}

.value {
  font-weight: bold;
  color: #333;
}

.status-badge {
  color: #C93737;
}

h4 {
  font-size: 1rem;
  color: #333;
  margin: 1.5rem 0 0.5rem 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.5rem;
}

.abstract-text {
  font-size: 0.95rem;
  line-height: 1.6;
  color: #555;
}

.content-preview {
  background: #f5f5f5;
  padding: 1rem;
  border-radius: 4px;
  color: #777;
  font-style: italic;
}

.attachment-list {
  list-style: none;
  padding: 0;
}

.attachment-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f0f0f0;
}

.file-icon {
  font-size: 1.2rem;
}

.ethics-box {
  background: #e8f5e9;
  padding: 1rem;
  border-radius: 4px;
  color: #2e7d32;
  font-size: 0.9rem;
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: #b02a2a;
}

.btn-primary:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.success-msg {
  color: #28a745;
  font-weight: bold;
  font-size: 0.9rem;
  margin-right: auto;
  align-self: center;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.spinner {
  display: inline-block;
  animation: spin 1s linear infinite;
  margin-right: 5px;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}
</style>
