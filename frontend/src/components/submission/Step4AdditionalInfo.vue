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
  if (store.steps[3].status === 'error') {
    scrollToError()
  }
})

const questions = computed(() => [
  { key: 'q1', label: t('additionalInformation.questions.q1'), limit: 500 },
  { key: 'q2', label: t('additionalInformation.questions.q2'), limit: 500 },
  { key: 'q3', label: t('additionalInformation.questions.q3'), limit: 500 },
  { key: 'q4', label: t('additionalInformation.questions.q4'), limit: 500 },
  { key: 'q5', label: t('additionalInformation.questions.q5'), limit: 500 },
  { key: 'q6', label: t('additionalInformation.questions.q6'), limit: 500 },
])

const getCharCount = (text) => text ? text.length : 0
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('additionalInformation.title') }}</h2>

    <!-- Mandatory Questions -->
    <div class="questions-section">
      <div v-for="(q, index) in questions" :key="q.key" class="form-group">
        <label class="form-label">
          {{ index + 1 }}. {{ q.label }} <span class="required">*</span>
        </label>
        <textarea 
          v-model="store.formData.additionalInfo[q.key]" 
          class="form-textarea"
          rows="3"
        ></textarea>
        <div class="char-count" :class="{ 'error': getCharCount(store.formData.additionalInfo[q.key]) > q.limit }">
          {{ getCharCount(store.formData.additionalInfo[q.key]) }} / {{ q.limit }}
        </div>
        <div v-if="getCharCount(store.formData.additionalInfo[q.key]) > q.limit" class="error-text">
          {{ t('additionalInformation.errors.limitExceeded') }}
        </div>
      </div>
    </div>
    
    <div v-if="store.steps[3].status === 'error'" class="error-msg main-error">
      {{ t('additionalInformation.errors.incomplete') }}
    </div>

    <hr class="divider">

    <!-- Optional Fields -->
    <div class="optional-section">
      <div class="form-group checkbox-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="store.formData.additionalInfo.ssrn">
          {{ t('additionalInformation.ssrn') }}
        </label>
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('additionalInformation.socialMedia') }} ({{ t('common.optional') }})</label>
        <input 
          type="text" 
          v-model="store.formData.additionalInfo.socialMedia" 
          class="form-input"
        >
      </div>

      <div class="form-group">
        <label class="form-label">{{ t('additionalInformation.conference') }} ({{ t('common.optional') }})</label>
        <select v-model="store.formData.additionalInfo.conference" class="form-select">
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
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

.form-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
}

.form-input, .form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.char-count {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.char-count.error {
  color: #e74c3c;
  font-weight: bold;
}

.error-text, .error-msg {
  color: #e74c3c;
  font-size: 14px;
  margin-top: 5px;
}

.main-error {
  margin-bottom: 20px;
  font-weight: bold;
  text-align: center;
}

.divider {
  border: 0;
  border-top: 1px solid #eee;
  margin: 2rem 0;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}
</style>
