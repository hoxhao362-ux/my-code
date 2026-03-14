<template>
  <div class="modal-overlay" @click="$emit('close')">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h3>New Message</h3>
        <button class="close-btn" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <div class="form-group">
          <label>To:</label>
          <select v-model="recipientId" class="form-control">
            <option value="" disabled>Select Recipient</option>
            <!-- Mock Recipients based on User Role -->
            <option v-for="user in availableRecipients" :key="user.id" :value="user.id">
              {{ user.name }} ({{ user.role }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>Subject:</label>
          <input type="text" v-model="subject" class="form-control" placeholder="Enter subject..." />
        </div>

        <div class="form-group">
          <label>Message:</label>
          <textarea v-model="content" class="form-control message-body" placeholder="Type your message..."></textarea>
        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="$emit('close')">Cancel</button>
        <button class="btn-send" @click="sendMessage" :disabled="!isValid || sending">
          {{ sending ? 'Sending...' : 'Send Message' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useMessageStore } from '../../stores/messages'
import { useUserStore } from '../../stores/user'

const emit = defineEmits(['close', 'sent'])
const messageStore = useMessageStore()
const userStore = useUserStore()

const recipientId = ref('')
const subject = ref('')
const content = ref('')
const sending = ref(false)

// Mock Recipients Logic
const availableRecipients = computed(() => {
  const currentUser = userStore.user
  if (!currentUser) return []

  // Simplistic mock list
  // In reality, this should come from an API based on context (e.g. Editors for Author)
  if (currentUser.role === 'author') {
    return [
      { id: 'editor_001', name: 'Chief Editor', role: 'Editor' },
      { id: 'admin', name: 'System Admin', role: 'Admin' }
    ]
  } else if (currentUser.role === 'reviewer') {
    return [
      { id: 'editor_001', name: 'Chief Editor', role: 'Editor' }
    ]
  } else {
    // Editor can send to anyone (Mock)
    return [
      { id: 'user_001', name: 'Author User', role: 'Author' },
      { id: 'reviewer_001', name: 'Reviewer One', role: 'Reviewer' }
    ]
  }
})

const isValid = computed(() => {
  return recipientId.value && subject.value.trim() && content.value.trim()
})

const sendMessage = async () => {
  if (!isValid.value) return
  
  sending.value = true
  const recipient = availableRecipients.value.find(r => r.id === recipientId.value)
  
  try {
    await messageStore.sendMessage({
      recipientId: recipient.id,
      recipientName: recipient.name,
      recipientRole: recipient.role,
      subject: subject.value,
      content: content.value
    })
    emit('sent')
  } finally {
    sending.value = false
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-content {
  background: white;
  width: 500px;
  max-width: 90%;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 5px 15px rgba(0,0,0,0.3);
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #999;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #555;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.message-body {
  height: 150px;
  resize: vertical;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn-cancel {
  background: #f1f1f1;
  border: 1px solid #ddd;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  color: #333;
}

.btn-send {
  background: #C93737;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-send:disabled {
  background: #e0e0e0;
  cursor: not-allowed;
}
</style>
