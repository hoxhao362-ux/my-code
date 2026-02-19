<script setup>
import { ref, computed } from 'vue'
import SubmissionNavigation from './components/SubmissionNavigation.vue'
import { useUserStore } from '../../stores/user'
import { useI18n } from '../../composables/useI18n'

// Import all steps from components/submission directory
import Step1ArticleType from '../../components/submission/Step1ArticleType.vue'
import Step2AttachFiles from '../../components/submission/Step2AttachFiles.vue'
import Step3GeneralInfo from '../../components/submission/Step3GeneralInfo.vue'
import Step4AdditionalInfo from '../../components/submission/Step4AdditionalInfo.vue'
import Step5Comments from '../../components/submission/Step5Comments.vue'
import Step6ManuscriptData from '../../components/submission/Step6ManuscriptData.vue'
import ProgressBar from '../../components/submission/ProgressBar.vue'
import { useSubmissionStore } from '../../stores/submission'

const submissionStore = useSubmissionStore()
const { t } = useI18n()

// Steps configuration
const steps = computed(() => [
  { id: 1, label: t('submission.steps.step1') }, // Article Type Selection
  { id: 2, label: t('submission.steps.step2') }, // Attach Files
  { id: 3, label: t('submission.steps.step3') }, // General Information
  { id: 4, label: t('submission.steps.step4') }, // Additional Information
  { id: 5, label: t('submission.steps.step5') }, // Comments
  { id: 6, label: t('submission.steps.step6') }  // Manuscript Data
])

const currentStep = computed(() => submissionStore.currentStep)

// Navigation handlers
const nextStep = () => submissionStore.nextStep()
const prevStep = () => submissionStore.prevStep()
const goToStep = (step) => submissionStore.goToStep(step)

// Mock save for later
const saveForLater = () => {
  alert('Progress saved!')
}
</script>

<template>
  <div class="submission-process-page">
    <SubmissionNavigation />
    
    <main class="process-container">
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
  margin: 2rem auto;
  padding: 0 1rem;
}

.step-content {
  margin-top: 2rem;
  background: #fff;
  /* padding: 2rem; */ /* MainSubmit components have their own padding usually */
}
</style>