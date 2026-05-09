<script setup>
import { onMounted } from 'vue'
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

// 匹配后端的 Subject 列表
const subjects = [
  'Anaesthesia & Critical Care',
  'Cardiology',
  'Dermatology',
  'Endocrinology',
  'Gastroenterology',
  'Infectious Diseases',
  'Neurology',
  'Oncology',
  'Pediatrics',
  'Psychiatry',
  'Surgery',
  'Others'
]
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('generalInformation.title') }}</h2>

    <div class="form-group">
      <label class="form-label">{{ t('generalInformation.subjectLabel') }} <span class="required">*</span></label>
      <select v-model="store.formData.subject" class="form-select">
        <option value="" disabled>{{ t('generalInformation.subjectPlaceholder') }}</option>
        <option v-for="s in subjects" :key="s" :value="s">{{ s }}</option>
      </select>
      <div v-if="store.steps[2].status === 'error' && !store.formData.subject" class="error-text">
        {{ t('generalInformation.errors.subjectRequired') }}
      </div>
    </div>

    <div class="form-group">
      <label class="form-label">{{ t('generalInformation.keywordsLabel') }} <span class="required">*</span></label>
      <p class="helper-text">{{ t('generalInformation.keywordsHelper') }}</p>
      <input
        type="text"
        v-model="store.formData.keywords"
        class="form-input"
        :placeholder="t('generalInformation.keywordsPlaceholder')"
      >
      <div v-if="store.steps[2].status === 'error' && !store.formData.keywords" class="error-text">
        {{ t('generalInformation.errors.keywordsRequired') }}
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
.helper-text { font-size: 0.85rem; color: #666; margin-bottom: 0.5rem; }
.required { color: #e74c3c; }
.form-select, .form-input { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 16px; }
.form-select:focus, .form-input:focus { border-color: #3498db; outline: none; }
.error-text { color: #e74c3c; font-size: 14px; margin-top: 5px; }
</style>
