<script setup>
import { computed, ref, onMounted } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import StepNavigation from './StepNavigation.vue'
import { useErrorScroll } from '../../composables/useErrorScroll'

const store = useSubmissionStore()
const { t } = useI18n()
const { scrollToError } = useErrorScroll()

onMounted(() => {
  if (store.steps[2].status === 'error') {
    scrollToError()
  }
})

// Mock Regions
const regions = [
  'China', 'United States', 'United Kingdom', 'Japan', 'Germany', 'France', 'Canada', 'Australia', 'Other'
]

// Mock Classifications
const allClassifications = [
  'Anaesthesia, Critical & Intensive Care',
  'Cardiology',
  'Dermatology',
  'Emergency Medicine',
  'Endocrinology',
  'Gastroenterology',
  'General Practice',
  'Geriatrics',
  'Hematology',
  'Infectious Diseases',
  'Neurology',
  'Neurosurgery',
  'Obstetrics & Gynecology',
  'Oncology',
  'Ophthalmology',
  'Orthopedics',
  'Pediatrics',
  'Psychiatry',
  'Radiology',
  'Respiratory Medicine',
  'Rheumatology',
  'Surgery',
  'Urology'
]

const showModal = ref(false)
const searchQuery = ref('')
const tempSelected = ref([]) // Temporary selection in modal

const filteredClassifications = computed(() => {
  if (!searchQuery.value) return allClassifications
  return allClassifications.filter(c => 
    c.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const openModal = () => {
  tempSelected.value = [...store.formData.classifications]
  showModal.value = true
}

const toggleSelection = (item) => {
  const idx = tempSelected.value.indexOf(item)
  if (idx === -1) {
    tempSelected.value.push(item)
  } else {
    tempSelected.value.splice(idx, 1)
  }
}

const confirmSelection = () => {
  store.formData.classifications = [...tempSelected.value]
  showModal.value = false
}

const removeClassification = (item) => {
  const idx = store.formData.classifications.indexOf(item)
  if (idx !== -1) store.formData.classifications.splice(idx, 1)
}
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('generalInformation.title') }}</h2>

    <!-- Region -->
    <div class="form-group">
      <label class="form-label">{{ t('generalInformation.regionLabel') }} <span class="required">*</span></label>
      <select v-model="store.formData.region" class="form-select">
        <option value="" disabled>{{ t('generalInformation.regionPlaceholder') }}</option>
        <option v-for="r in regions" :key="r" :value="r">{{ r }}</option>
      </select>
      <div v-if="store.steps[2].status === 'error' && !store.formData.region" class="error-text">
        {{ t('generalInformation.errors.regionRequired') }}
      </div>
    </div>

    <!-- Classifications -->
    <div class="form-group">
      <label class="form-label">{{ t('generalInformation.classificationsLabel') }} <span class="required">*</span></label>
      
      <div class="selected-list" v-if="store.formData.classifications.length > 0">
        <div class="tag" v-for="item in store.formData.classifications" :key="item">
          {{ item }}
          <span class="remove-tag" @click="removeClassification(item)">×</span>
        </div>
      </div>
      
      <button class="btn-add" @click="openModal">+ {{ t('generalInformation.addClassification') }}</button>
      
      <div v-if="store.steps[2].status === 'error' && store.formData.classifications.length === 0" class="error-text">
        {{ t('generalInformation.errors.classificationRequired') }}
      </div>
    </div>

    <!-- Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ t('generalInformation.popupTitle') }}</h3>
          <button class="btn-close" @click="showModal = false">×</button>
        </div>
        
        <div class="modal-body">
          <input 
            type="text" 
            v-model="searchQuery" 
            :placeholder="t('generalInformation.searchPlaceholder')" 
            class="search-input"
          >
          
          <div class="class-list">
            <div 
              v-for="item in filteredClassifications" 
              :key="item"
              class="class-item"
            >
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  :checked="tempSelected.includes(item)"
                  @change="toggleSelection(item)"
                >
                <span :class="{ 'highlight': searchQuery && item.toLowerCase().includes(searchQuery.toLowerCase()) }">
                  {{ item }}
                </span>
              </label>
            </div>
            <div v-if="filteredClassifications.length === 0" class="no-results">
              {{ t('generalInformation.noResults') }}
            </div>
          </div>
        </div>
        
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showModal = false">{{ t('common.cancel') }}</button>
          <button class="btn btn-primary" @click="confirmSelection">{{ t('common.add') }}</button>
        </div>
      </div>
    </div>

    <StepNavigation />
  </div>
</template>

<style scoped>
.step-container {
  max-width: 800px;
  margin: 0 auto;
}

.step-title {
  font-size: 1.5rem;
  color: #2c3e50;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #eee;
}

.form-group {
  margin-bottom: 2rem;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.required {
  color: #e74c3c;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.btn-add {
  padding: 8px 16px;
  background: #fff;
  border: 1px dashed #3498db;
  color: #3498db;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add:hover {
  background: #f0f8ff;
}

.selected-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 1rem;
}

.tag {
  background: #e1f5fe;
  color: #0277bd;
  padding: 5px 10px;
  border-radius: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.remove-tag {
  cursor: pointer;
  font-weight: bold;
}

.remove-tag:hover {
  color: #01579b;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 600px;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  max-height: 80vh;
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.search-input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 15px;
}

.class-list {
  border: 1px solid #eee;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
}

.class-item {
  padding: 10px;
  border-bottom: 1px solid #f9f9f9;
}

.class-item:hover {
  background: #f5f5f5;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  width: 100%;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
}

.btn-secondary { background: #eee; }
.btn-primary { background: #3498db; color: white; }

.error-text {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

.highlight {
  background-color: yellow;
}
</style>
