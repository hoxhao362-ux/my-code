<script setup>
import { ref, computed } from 'vue'
import SubmissionNavigation from './components/SubmissionNavigation.vue'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { useI18n } from '../../composables/useI18n'

import Step1ArticleType from '../../components/submission/Step1ArticleType.vue'
import Step2AttachFiles from '../../components/submission/Step2AttachFiles.vue'
import Step3GeneralInfo from '../../components/submission/Step3GeneralInfo.vue'
import Step4AdditionalInfo from '../../components/submission/Step4AdditionalInfo.vue'
import Step5Comments from '../../components/submission/Step5Comments.vue'
import Step6ManuscriptData from '../../components/submission/Step6ManuscriptData.vue'
import ProgressBar from '../../components/submission/ProgressBar.vue'
import { useSubmissionStore } from '../../stores/submission'

const submissionStore = useSubmissionStore()
const toastStore = useToastStore()
const { t } = useI18n()

// Steps configuration
const steps = computed(() => [
  { id: 1, label: t('progress.step1') }, // Article Type Selection
  { id: 2, label: t('progress.step2') }, // Attach Files
  { id: 3, label: t('progress.step3') }, // General Information
  { id: 4, label: t('progress.step4') }, // Additional Information
  { id: 5, label: t('progress.step5') }, // Comments
  { id: 6, label: t('progress.step6') }  // Manuscript Data
])

const currentStep = computed(() => submissionStore.currentStep)

// Navigation handlers
const nextStep = () => submissionStore.nextStep()
const prevStep = () => submissionStore.prevStep()
const goToStep = (step) => submissionStore.goToStep(step)

const saveForLater = () => {
  toastStore.add({ message: 'Progress saved!', type: 'success' })
}

const statusText = computed(() => {
  const steps1to5 = submissionStore.steps.slice(0, 5)
  const ready = steps1to5.every(s => s.status === 'completed') && submissionStore.currentStep === 6
  return ready ? 'Ready for Submission' : 'Draft (Incomplete)'
})

const statusClass = computed(() => {
  return statusText.value === 'Ready for Submission' ? 'status-ready' : 'status-draft'
})
</script>

<template>
  <div class="submission-process-page">
    <SubmissionNavigation />
    
    <main class="process-container">
      <!-- Status Label -->
      <div class="status-header">
        <span class="status-badge" :class="statusClass">{{ statusText }}</span>
      </div>

      <!-- Progress Bar -->
      <ProgressBar 
        :steps="steps" 
        :current-step="currentStep"
        @step-click="goToStep"
      />
      
      <!-- Step Content -->
      <div class="step-content">
        <Step1ArticleType v-if="currentStep === 1" @next="nextStep" @save="saveForLater" />
        <Step2AttachFiles v-if="currentStep === 2" @next="nextStep" @prev="prevStep" @save="saveForLater" />
        <Step3GeneralInfo v-if="currentStep === 3" @next="nextStep" @prev="prevStep" @save="saveForLater" />
        <Step4AdditionalInfo v-if="currentStep === 4" @next="nextStep" @prev="prevStep" @save="saveForLater" />
        <Step5Comments v-if="currentStep === 5" @next="nextStep" @prev="prevStep" @save="saveForLater" />
        <Step6ManuscriptData v-if="currentStep === 6" @prev="prevStep" @save="saveForLater" />
      </div>
    </main>
  </div>
</template>

<style scoped>
.submission-process-page {
  min-height: 100vh;
  background-color: #fff;
  font-family: Arial, sans-serif;
}

.process-container {
  max-width: 1000px;
  margin: 0 auto 2rem; /* Remove top margin */
  padding: 2rem 1rem 0; /* Add top padding to match Dashboard gap */
}

.step-content {
  margin-top: 2rem;
  background: #fff;
  /* padding: 2rem; */ /* MainSubmit components have their own padding usually */
}

.status-header {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 14px;
  color: white;
}

.status-draft {
  background-color: #999; /* Grey */
}

.status-ready {
  background-color: #28A745; /* Green */
}
</style>