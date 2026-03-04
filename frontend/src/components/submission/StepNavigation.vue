<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useSubmissionStore } from '../../stores/submission'
import { useToastStore } from '../../stores/toast'
import { useI18n } from '../../composables/useI18n'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  },
  isFinal: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit'])

const store = useSubmissionStore()
const router = useRouter()
const toastStore = useToastStore()
const { t } = useI18n()

const handleNext = () => {
  if (props.isFinal) {
    emit('submit')
  } else {
    store.nextStep()
  }
}

const handleBack = () => {
  store.prevStep()
}

const handleSave = () => {
  if (store.saveDraft()) {
    toastStore.add({ message: t('common.draftSaved'), type: 'success' })
  }
}

const handleCancel = () => {
  if (confirm(t('common.confirmCancel'))) {
    localStorage.removeItem('submission_draft')
    router.push('/')
  }
}
</script>

<template>
  <div class="step-actions">
    <div class="left-actions">
      <button 
        class="btn btn-secondary" 
        @click="handleBack"
        :disabled="store.currentStep === 1 || loading"
      >
        {{ store.currentStep >= 3 ? 'Save as Draft & Previous Step' : t('common.back') }}
      </button>
    </div>
    
    <div class="right-actions">
      <button class="btn btn-outline" @click="handleCancel" :disabled="loading">
        {{ t('common.cancel') }}
      </button>
      <button class="btn btn-outline" @click="handleSave" :disabled="loading">
        {{ t('common.saveLater') }}
      </button>
      <button 
        class="btn btn-primary" 
        @click="handleNext"
        :disabled="loading"
      >
        <span v-if="loading">{{ t('common.loading') }}</span>
        <span v-else>
          {{ 
            isFinal 
              ? 'Submit Manuscript' 
              : (store.currentStep >= 3 ? 'Save as Draft & Next Step' : (store.currentStep === 1 || store.currentStep === 4 ? t('common.proceed') : t('common.next'))) 
          }}
        </span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.step-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 2rem;
  border-top: 1px solid #eee;
  margin-top: 2rem;
}

.right-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #3498db;
  color: white;
  border: none;
}
.btn-primary:hover:not(:disabled) { background: #2980b9; }

.btn-secondary {
  background: #95a5a6;
  color: white;
  border: none;
}
.btn-secondary:hover:not(:disabled) { background: #7f8c8d; }

.btn-outline {
  background: white;
  border: 1px solid #ccc;
  color: #666;
}
.btn-outline:hover:not(:disabled) { border-color: #999; color: #333; }
</style>
