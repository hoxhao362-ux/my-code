<template>
  <div class="templates-container">
    <Navigation 
      :user="user" 
      :current-page="'resources-writer-templates'"
      :logout="userStore.logout"
    />
    <div class="filter-bar">
      <div class="filter-group">
        <label>Subject:</label>
        <select v-model="selectedSubject">
          <option value="all">All Subjects</option>
          <option value="medicine">Medicine</option>
          <option value="biology">Biology</option>
          <option value="public_health">Public Health</option>
        </select>
      </div>
      <div class="filter-group checkbox-group">
        <label>Type:</label>
        <label class="checkbox-label">
          <input type="checkbox" value="original" v-model="selectedTypes"> Original Research
        </label>
        <label class="checkbox-label">
          <input type="checkbox" value="review" v-model="selectedTypes"> Review
        </label>
        <label class="checkbox-label">
          <input type="checkbox" value="case_report" v-model="selectedTypes"> Case Report
        </label>
      </div>
    </div>

    <div class="templates-grid">
      <div v-for="template in filteredTemplates" :key="template.id" class="template-card">
        <div class="card-preview">
          <div class="preview-overlay">
            <span>Preview</span>
          </div>
        </div>
        <div class="card-body">
          <h3>{{ template.name }}</h3>
          <p class="format-info">{{ template.format }}</p>
          <a href="#" class="download-link" @click.prevent="downloadTemplate(template)">Download</a>
        </div>
      </div>
    </div>

    <div v-if="showToast" class="toast">
      Template saved to local drive.
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useUserStore } from '../../../stores/user'
import Navigation from '../../../components/Navigation.vue'

const userStore = useUserStore()
const user = computed(() => userStore.user)

const selectedSubject = ref('all')
const selectedTypes = ref(['original', 'review', 'case_report'])
const showToast = ref(false)

const templates = [
  { id: 1, name: 'Original Research Template', type: 'original', subject: 'medicine', format: 'Word .docx | 55KB' },
  { id: 2, name: 'Systematic Review Template', type: 'review', subject: 'medicine', format: 'Word .docx | 48KB' },
  { id: 3, name: 'Case Report Template', type: 'case_report', subject: 'medicine', format: 'Word .docx | 42KB' },
  { id: 4, name: 'Biology Research Template', type: 'original', subject: 'biology', format: 'LaTeX .tex | 120KB' },
  { id: 5, name: 'Public Health Survey', type: 'original', subject: 'public_health', format: 'Word .docx | 60KB' },
  { id: 6, name: 'Clinical Trial Protocol', type: 'original', subject: 'medicine', format: 'Word .docx | 75KB' }
]

const filteredTemplates = computed(() => {
  return templates.filter(t => {
    const subjectMatch = selectedSubject.value === 'all' || t.subject === selectedSubject.value
    const typeMatch = selectedTypes.value.includes(t.type)
    return subjectMatch && typeMatch
  })
})

const downloadTemplate = (template) => {
  showToast.value = true
  setTimeout(() => {
    showToast.value = false
  }, 3000)
}
</script>

<style scoped>
.templates-container {
  max-width: 1200px;
  margin: 80px auto 0;
  padding: 40px 24px 40px; /* Top padding for navbar */
}

.filter-bar {
  display: flex;
  gap: 32px;
  margin-bottom: 40px;
  padding-bottom: 20px;
  border-bottom: 1px solid #E5E5E5;
  align-items: center;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-group label {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}

select {
  padding: 8px 12px;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  font-size: 14px;
  color: #333;
  outline: none;
}

select:focus {
  border-color: #C93737;
}

.checkbox-group {
  display: flex;
  gap: 20px;
}

.checkbox-label {
  font-weight: normal !important;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.template-card {
  background: white;
  border: 1px solid #E5E5E5;
  border-radius: 4px;
  overflow: hidden;
  transition: border-color 0.3s;
}

.template-card:hover {
  border-color: #C93737;
}

.card-preview {
  height: 160px;
  background-color: #F5F5F5;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.card-preview::before {
  content: "DOC";
  font-size: 48px;
  color: #E0E0E0;
  font-weight: bold;
}

.preview-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(201, 55, 55, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.template-card:hover .preview-overlay {
  opacity: 1;
}

.card-body {
  padding: 20px;
  text-align: center;
}

h3 {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.format-info {
  font-size: 12px;
  color: #999;
  margin-bottom: 16px;
}

.download-link {
  color: #C93737;
  text-decoration: none;
  font-size: 14px;
  font-weight: bold;
}

.download-link:hover {
  text-decoration: underline;
}

.toast {
  position: fixed;
  bottom: 24px;
  right: 24px;
  background-color: #333;
  color: white;
  padding: 12px 24px;
  border-radius: 4px;
  z-index: 1000;
  animation: fadeIn 0.3s;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
