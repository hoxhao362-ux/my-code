<script setup>
import { defineProps, defineEmits, computed } from 'vue'

const props = defineProps({
  visible: Boolean,
  manuscript: Object
})

const emit = defineEmits(['close'])

const attachments = computed(() => {
  // Mock data based on SRS
  return [
    { 
      id: 1, 
      name: 'Supplementary Material.docx', 
      type: 'Document', 
      size: '1.2 MB', 
      date: '2026-02-18', 
      url: '#' 
    },
    { 
      id: 2, 
      name: 'Ethics Approval.pdf', 
      type: 'PDF', 
      size: '850 KB', 
      date: '2026-02-18', 
      url: '#' 
    },
    { 
      id: 3, 
      name: 'Figure 1.png', 
      type: 'Image', 
      size: '2.4 MB', 
      date: '2026-02-19', 
      url: '#' 
    }
  ]
})

const handlePreview = (file) => {
  if (file.type === 'Image') {
    alert(`Previewing image: ${file.name} (Mock Image Viewer)`)
  } else {
    alert('Preview not supported, please download the file.')
  }
}

const handleDownload = (file) => {
  // Simulate download
  const link = document.createElement('a')
  link.href = 'data:text/plain;charset=utf-8,' + encodeURIComponent(`Mock content for ${file.name}`)
  link.download = file.name
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <div v-if="visible" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">
      <div class="modal-header">
        <h3>Attachments for Manuscript {{ manuscript?.id }}</h3>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-content">
        <div v-if="attachments.length === 0" class="no-data">
          No attachments available for this manuscript.
        </div>
        
        <table v-else class="attachments-table">
          <thead>
            <tr>
              <th>File Name</th>
              <th>Type</th>
              <th>Size</th>
              <th>Upload Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in attachments" :key="file.id">
              <td>
                <div class="file-info">
                  <span class="file-icon">
                    {{ file.type === 'Image' ? '🖼️' : file.type === 'PDF' ? '📄' : '📝' }}
                  </span>
                  {{ file.name }}
                </div>
              </td>
              <td>{{ file.type }}</td>
              <td>{{ file.size }}</td>
              <td>{{ file.date }}</td>
              <td>
                <div class="action-buttons">
                  <button class="btn-action preview" @click="handlePreview(file)">Preview</button>
                  <button class="btn-action download" @click="handleDownload(file)">Download</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.6); /* Slightly darker for nested/secondary modal feel */
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1100; /* Higher than parent modal */
}

.modal-box {
  background: white;
  width: 800px;
  max-width: 95%;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
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
}

.no-data {
  text-align: center;
  color: #999;
  padding: 2rem;
  background: #f9f9f9;
  border-radius: 4px;
}

.attachments-table {
  width: 100%;
  border-collapse: collapse;
  border: 1px solid #eee; /* Journal Platform style grey border */
}

.attachments-table th, .attachments-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.attachments-table th {
  background: #f9f9f9;
  color: #666;
  font-weight: 600;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  color: #333;
}

.file-icon {
  font-size: 1.1rem;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  padding: 0.3rem 0.8rem;
  border-radius: 3px;
  font-size: 0.85rem;
  cursor: pointer;
  border: none;
  color: white;
  transition: opacity 0.2s, box-shadow 0.2s;
}

.btn-action:hover {
  opacity: 0.9;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-action.preview {
  background-color: #0056b3; /* Blue */
}

.btn-action.download {
  background-color: #0056B3; /* Blue */
}

.modal-footer {
  padding: 1.5rem;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  border: none;
  padding: 0.5rem 1.5rem;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #5a6268;
}
</style>
