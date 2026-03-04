<template>
  <div v-if="visible" class="pdf-modal-overlay" @click.self="$emit('close')">
    <div class="pdf-modal-box">
      <div class="pdf-modal-header">
        <h3>{{ fileName || 'PDF Preview' }}</h3>
        <div class="header-actions">
           <div class="pdf-controls" v-if="pageCount > 0">
             <button class="btn-icon" @click="zoomOut" title="Zoom Out">-</button>
             <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
             <button class="btn-icon" @click="zoomIn" title="Zoom In">+</button>
             <span class="separator">|</span>
             <button class="btn-icon" @click="prevPage" :disabled="pageNum <= 1">‹</button>
             <span class="page-info">{{ pageNum }} / {{ pageCount }}</span>
             <button class="btn-icon" @click="nextPage" :disabled="pageNum >= pageCount">›</button>
           </div>
           <button class="btn-download" @click="downloadFile">Download</button>
           <button class="close-btn" @click="$emit('close')">&times;</button>
        </div>
      </div>
      <div class="pdf-modal-content">
        <div v-if="isLoading" class="loading-state">
          Loading Preview...
        </div>
        <div v-else-if="errorMsg" class="error-state">
          {{ errorMsg }}
        </div>
        <div v-else class="canvas-wrapper">
          <canvas ref="canvasRef"></canvas>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, ref, onMounted, watch } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'

// Set worker source
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`

const props = defineProps({
  visible: Boolean,
  fileUrl: String,
  fileName: String
})

const emit = defineEmits(['close'])

const pdfDoc = ref(null)
const pageNum = ref(1)
const pageCount = ref(0)
const scale = ref(1.0)
const canvasRef = ref(null)
const isLoading = ref(false)
const errorMsg = ref('')

const renderPage = async (num) => {
  if (!pdfDoc.value) return
  isLoading.value = true
  
  try {
    const page = await pdfDoc.value.getPage(num)
    const viewport = page.getViewport({ scale: scale.value })
    const canvas = canvasRef.value
    if (!canvas) return

    const context = canvas.getContext('2d')
    canvas.height = viewport.height
    canvas.width = viewport.width

    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }
    
    await page.render(renderContext).promise
  } catch (err) {
    console.error('Render error:', err)
    errorMsg.value = 'Failed to render page'
  } finally {
    isLoading.value = false
  }
}

const loadPdf = async (url) => {
  if (!url) return
  isLoading.value = true
  errorMsg.value = ''
  
  try {
    const loadingTask = pdfjsLib.getDocument(url)
    pdfDoc.value = await loadingTask.promise
    pageCount.value = pdfDoc.value.numPages
    pageNum.value = 1
    renderPage(1)
  } catch (err) {
    console.error('Error loading PDF:', err)
    errorMsg.value = 'Failed to load PDF document'
  } finally {
    isLoading.value = false
  }
}

watch(() => props.visible, (newVal) => {
  if (newVal && props.fileUrl) {
    // Reset state
    pdfDoc.value = null
    pageNum.value = 1
    scale.value = 1.0
    loadPdf(props.fileUrl)
  }
})

watch(() => props.fileUrl, (newUrl) => {
  if (props.visible && newUrl) {
    loadPdf(newUrl)
  }
})

const prevPage = () => {
  if (pageNum.value <= 1) return
  pageNum.value--
  renderPage(pageNum.value)
}

const nextPage = () => {
  if (pageNum.value >= pageCount.value) return
  pageNum.value++
  renderPage(pageNum.value)
}

const zoomIn = () => {
  scale.value += 0.2
  renderPage(pageNum.value)
}

const zoomOut = () => {
  if (scale.value > 0.4) {
    scale.value -= 0.2
    renderPage(pageNum.value)
  }
}

const downloadFile = () => {
  if (!props.fileUrl) return
  const link = document.createElement('a')
  link.href = props.fileUrl
  link.download = props.fileName || 'document.pdf'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<style scoped>
.pdf-modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.75);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.pdf-modal-box {
  width: 90%;
  height: 90%;
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
}

.pdf-modal-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
  border-radius: 8px 8px 0 0;
}

.pdf-modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.pdf-modal-content {
  flex: 1;
  background: #525659; /* Standard PDF viewer background color */
  position: relative;
  overflow: auto;
  display: flex;
  justify-content: center;
  padding: 20px;
}

.canvas-wrapper {
  box-shadow: 0 0 10px rgba(0,0,0,0.5);
}

.pdf-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #eee;
  padding: 4px 12px;
  border-radius: 20px;
  margin-right: 15px;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  color: #333;
}

.btn-icon:hover {
  background: #ddd;
}

.btn-icon:disabled {
  color: #ccc;
  cursor: not-allowed;
}

.page-info, .zoom-level {
  font-size: 0.9rem;
  font-weight: 500;
  min-width: 40px;
  text-align: center;
}

.separator {
  color: #ccc;
  margin: 0 4px;
}

.error-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #ff6b6b;
  font-size: 1.1rem;
}

.loading-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: white;
  font-size: 1.2rem;
}

.btn-download {
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-download:hover {
  background: #2980b9;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.8rem;
  line-height: 1;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}
</style>
