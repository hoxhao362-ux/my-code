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
  if (store.steps[4].status === 'error') {
    scrollToError()
  }
})
</script>

<template>
  <div class="step-container">
    <h2 class="step-title">{{ t('comments.title') }}</h2>

    <div class="form-group">
      <label class="form-label">{{ t('comments.coverLetter') }} <span class="required">*</span></label>
      <textarea 
        v-model="store.formData.coverLetter" 
        class="form-textarea large"
        :placeholder="t('comments.placeholder')"
      ></textarea>
      
      <div v-if="store.steps[4].status === 'error' && !store.formData.coverLetter" class="error-text">
        {{ t('comments.errors.required') }}
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
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  font-size: 16px;
  min-height: 400px;
}

.form-textarea:focus {
  outline: none;
  border-color: #3498db;
}

.error-text {
  color: #e74c3c;
  margin-top: 10px;
}
</style>
