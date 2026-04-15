<script setup>
import { computed } from 'vue'
import { useI18n } from '../../composables/useI18n'
import { useUserStore } from '../../stores/user'
import { useToastStore } from '../../stores/toast'
import { usePlatformStore } from '../../stores/platform'
import { MANUSCRIPT_STATUS } from '../../constants/manuscriptStatus'

const props = defineProps({
  visible: Boolean,
  manuscript: Object
})

const emit = defineEmits(['close', 'transferred', 'declined'])

const { t } = useI18n()
const userStore = useUserStore()
const toastStore = useToastStore()
const platformStore = usePlatformStore()

const targetJournalName = computed(() => {
  if (!props.manuscript?.transferTo) return 'Unknown Journal'
  const journal = platformStore.journals.find(j => j.id === props.manuscript.transferTo)
  return journal ? journal.name : props.manuscript.transferTo
})

const handleAccept = () => {
  if (!confirm(t('transferDetails.acceptConfirm'))) return
  
  const updatedJournal = { ...props.manuscript }
  updatedJournal.status = MANUSCRIPT_STATUS.TRANSFERRED
  userStore.updateJournal(updatedJournal)
  
  // Clone manuscript for the target journal
  const newManuscript = {
    ...props.manuscript,
    id: `MS${new Date().getFullYear()}-${Math.floor(Math.random() * 10000)}-T`,
    status: MANUSCRIPT_STATUS.PENDING_INITIAL_REVIEW,
    transferredFrom: props.manuscript.currentJournalId || 'lancet', // Should come from current journal context
    transferTo: null,
    transferReason: null,
    submissionDate: new Date().toISOString().split('T')[0],
    date: new Date().toISOString().split('T')[0],
    history: [
      {
        date: new Date().toISOString().split('T')[0],
        action: `Transferred from previous journal`
      }
    ]
  }
  userStore.addJournal(newManuscript)
  
  toastStore.add({ message: t('transferDetails.successAccept'), type: 'success' })
  emit('transferred', updatedJournal)
  emit('close')
}

const handleDecline = () => {
  if (!confirm(t('transferDetails.declineConfirm'))) return
  
  const updatedJournal = { ...props.manuscript }
  updatedJournal.status = MANUSCRIPT_STATUS.WITHDRAWN
  userStore.updateJournal(updatedJournal)
  
  toastStore.add({ message: t('transferDetails.successDecline'), type: 'success' })
  emit('declined', updatedJournal)
  emit('close')
}
</script>

<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-content">
      <div class="modal-header">
        <h2>{{ t('transferDetails.title') }}</h2>
        <button class="close-btn" @click="$emit('close')">&times;</button>
      </div>
      
      <div class="modal-body" v-if="manuscript">
        <div class="info-section">
          <h3>{{ manuscript.title }}</h3>
          <p><strong>{{ t('transferDetails.suggestedJournal') }}:</strong> <span class="highlight">{{ targetJournalName }}</span></p>
        </div>
        
        <div class="reason-section">
          <h4>{{ t('transferDetails.reason') }}</h4>
          <div class="reason-box">
            {{ manuscript.transferReason || 'The editor has suggested transferring your manuscript to the recommended journal for a better fit.' }}
          </div>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="handleDecline">{{ t('transferDetails.declineBtn') }}</button>
        <button class="btn btn-primary" @click="handleAccept">{{ t('transferDetails.acceptBtn') }}</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #666;
}

.info-section {
  margin-bottom: 2rem;
}

.info-section h3 {
  margin-top: 0;
  color: #0056b3;
}

.highlight {
  font-weight: bold;
  color: #28a745;
}

.reason-section h4 {
  margin-bottom: 0.5rem;
  color: #555;
}

.reason-box {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid #0056b3;
  line-height: 1.5;
  color: #333;
}

.modal-footer {
  margin-top: 2rem;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  cursor: pointer;
  font-weight: bold;
}

.btn-primary {
  background: #0056b3;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}
</style>
