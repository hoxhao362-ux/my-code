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

const types = computed(() => {
  return [
    { value: 'Original Research', label: 'Original Research' },
    { value: 'Review Article', label: 'Review Article' },
    { value: 'Case Report', label: 'Case Report' },
    { value: 'Correspondence', label: 'Correspondence' }
  ]
})

const sections = [
  'Infectious Diseases', 'Oncology', 'Neurology', 'Global Health', 'Others'
]

const typeWordLimits = {
  'Original Research': { minWords: 3000, maxWords: 3500, minRefs: 25 },
  'Review Article': { minWords: 4000, maxWords: 5000, minRefs: 50 },
  'Case Report': { minWords: 1000, maxWords: 1500, minRefs: 15 },
  'Correspondence': { maxWords: 500, maxRefs: 10 }
}

const guidelines = computed(() => {
  if (!store.formData.article_type) return null
  
  const limits = typeWordLimits[store.formData.article_type]
  let wordCountText = 'Not specified'
  let referencesText = 'Not specified'
  
  if (limits) {
    if (limits.minWords && limits.maxWords) wordCountText = `${limits.minWords} - ${limits.maxWords} words`
    else if (limits.maxWords) wordCountText = `Max ${limits.maxWords} words`
    
    if (limits.minRefs && limits.maxRefs) referencesText = `${limits.minRefs} - ${limits.maxRefs} references`
    else if (limits.minRefs) referencesText = `Min ${limits.minRefs} references`
    else if (limits.maxRefs) referencesText = `Max ${limits.maxRefs} references`
  }
  
  return {
    text: t('articleTypeSelection.guidelines.general') || 'Please adhere strictly to the journal formatting guidelines.',
    wordCount: wordCountText,
    references: referencesText
  }
})
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('articleTypeSelection.title') || 'Article Type & Section' }}</h2>
    
    <div class="form-group">
      <label class="form-label">Article Type <span class="required">*</span></label>
      <select v-model="store.formData.article_type" class="form-select">
        <option value="" disabled>Select the type of your manuscript</option>
        <option v-for="type in types" :key="type.value" :value="type.value">
          {{ type.label }}
        </option>
      </select>
    </div>

    <div class="form-group">
      <label class="form-label">Section Category <span class="required">*</span></label>
      <select v-model="store.formData.section_category" class="form-select">
        <option value="" disabled>Select the relevant section</option>
        <option v-for="sec in sections" :key="sec" :value="sec">{{ sec }}</option>
      </select>
    </div>

    <div v-if="store.formData.article_type" class="guidelines-panel animate-fade-in">
      <h3 class="guidelines-title">Submission Guidelines</h3>
      <div class="guideline-item">
        <strong>General Rules:</strong>
        <p class="guideline-text">{{ guidelines.text }}</p>
      </div>
      <div class="guideline-row">
        <div class="guideline-item">
          <strong>Word Count:</strong>
          <span>{{ guidelines.wordCount }}</span>
        </div>
        <div class="guideline-item">
          <strong>References:</strong>
          <span>{{ guidelines.references }}</span>
        </div>
      </div>
    </div>

    <StepNavigation />
  </div>
</template>

<style scoped>
.step-container { max-width: 800px; margin: 0 auto; }
.step-title { font-size: 1.5rem; color: #2c3e50; margin-bottom: 2rem; padding-bottom: 1rem; border-bottom: 1px solid #eee; }
.form-group { margin-bottom: 2rem; }
.form-label { display: block; margin-bottom: 0.5rem; font-weight: 600; color: #333; }
.required { color: #e74c3c; }
.form-select { width: 100%; padding: 10px; font-size: 16px; border: 1px solid #ddd; border-radius: 4px; background: white; }
.form-select:focus { border-color: #3498db; outline: none; }
.guidelines-panel { background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 6px; padding: 1.5rem; margin-top: 2rem; }
.guidelines-title { font-size: 1.1rem; color: #2c3e50; margin-bottom: 1rem; border-bottom: 2px solid #3498db; display: inline-block; padding-bottom: 5px; }
.guideline-item { margin-bottom: 1rem; }
.guideline-text { white-space: pre-wrap; color: #666; margin-top: 5px; line-height: 1.6; }
.guideline-row { display: flex; gap: 2rem; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #eee; }
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
</style>
