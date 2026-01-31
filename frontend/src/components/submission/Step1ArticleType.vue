<script setup>
import { computed, onMounted } from 'vue'
import { useSubmissionStore } from '../../stores/submission'
import { useI18n } from '../../composables/useI18n'
import StepNavigation from './StepNavigation.vue'
import { useErrorScroll } from '../../composables/useErrorScroll'

const store = useSubmissionStore()
const { t } = useI18n()
const { scrollToError } = useErrorScroll()

onMounted(() => {
  if (store.steps[0].status === 'error') {
    scrollToError()
  }
})

// Dynamic types
const types = computed(() => {
  return [
    'invited', 'correspondence', 'comments', 'clinical', 'original', 'review'
  ].map(key => ({
    value: key,
    label: t(`articleTypeSelection.types.${key}`)
  }))
})

const selectedTypeLabel = computed(() => {
  const type = types.value.find(t => t.value === store.formData.articleType)
  return type ? type.label : ''
})

// Submission guidelines mapping
const guidelines = computed(() => {
  if (!store.formData.articleType) return null
  return {
    text: t('articleTypeSelection.guidelines.general'), // In real app, this should be dynamic per type
    wordCount: '3000 - 5000 words',
    references: 'Max 50 references'
  }
})
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('articleTypeSelection.title') }}</h2>
    
    <div class="form-group">
      <label class="form-label">{{ t('articleTypeSelection.label') }} <span class="required">*</span></label>
      <select v-model="store.formData.articleType" class="form-select">
        <option value="" disabled>{{ t('articleTypeSelection.placeholder') }}</option>
        <option v-for="type in types" :key="type.value" :value="type.value">
          {{ type.label }}
        </option>
      </select>
    </div>

    <div v-if="store.formData.articleType" class="guidelines-panel animate-fade-in">
      <h3 class="guidelines-title">{{ t('articleTypeSelection.guidelinesTitle') }}</h3>
      <div class="guideline-item">
        <strong>{{ t('articleTypeSelection.guidelines.general') }}:</strong>
        <p class="guideline-text">{{ guidelines.text }}</p>
      </div>
      <div class="guideline-row">
        <div class="guideline-item">
          <strong>{{ t('articleTypeSelection.guidelines.wordCount') }}:</strong>
          <span>{{ guidelines.wordCount }}</span>
        </div>
        <div class="guideline-item">
          <strong>{{ t('articleTypeSelection.guidelines.references') }}:</strong>
          <span>{{ guidelines.references }}</span>
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
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.form-select:focus {
  border-color: #3498db;
  outline: none;
}

.guidelines-panel {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  padding: 1.5rem;
  margin-top: 2rem;
}

.guidelines-title {
  font-size: 1.1rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  border-bottom: 2px solid #3498db;
  display: inline-block;
  padding-bottom: 5px;
}

.guideline-item {
  margin-bottom: 1rem;
}

.guideline-text {
  white-space: pre-wrap;
  color: #666;
  margin-top: 5px;
  line-height: 1.6;
}

.guideline-row {
  display: flex;
  gap: 2rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
