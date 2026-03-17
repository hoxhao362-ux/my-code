<template>
  <div class="message-detail-container">
    <div class="detail-header">
      <button class="back-btn" @click="$emit('back')">← Back</button>
      <div class="header-content">
        <h3>{{ thread?.subject }}</h3>
        <span class="participants">
          {{ thread?.participants.join(', ') }} ({{ thread?.participantRole }})
        </span>
      </div>
    </div>

    <div class="messages-scroll" ref="scrollContainer">
      <div 
        v-for="msg in messages" 
        :key="msg.id" 
        class="message-row"
        :class="{ 'mine': isMyMessage(msg) }"
      >
        <div class="message-bubble">
          <div class="msg-meta">
            <span class="sender-name">{{ msg.senderName }}</span>
            <span class="msg-time">{{ formatTime(msg.createdAt) }}</span>
          </div>
          <div class="msg-content" v-html="msg.content"></div>
          
          <div v-if="msg.attachments && msg.attachments.length" class="attachments">
            <div v-for="file in msg.attachments" :key="file.name" class="attachment-item">
              📎 {{ file.name }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="reply-area">
      <textarea 
        v-model="replyContent" 
        placeholder="Type your reply here..."
        @keydown.ctrl.enter="sendReply"
      ></textarea>
      <div class="reply-actions">
        <button class="btn-attach" title="Attach File (Mock)">📎</button>
        <button class="btn-send" @click="sendReply" :disabled="!replyContent.trim() || sending">
          {{ sending ? 'Sending...' : 'Send Reply' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useMessageStore } from '../../stores/messages'
import { useUserStore } from '../../stores/user'

const props = defineProps({
  threadId: String
})

const emit = defineEmits(['back'])

const messageStore = useMessageStore()
const userStore = useUserStore()
const scrollContainer = ref(null)

const replyContent = ref('')
const sending = ref(false)

const messages = computed(() => {
  return messageStore.activeThreadMessages
})

const thread = computed(() => {
  return messageStore.myThreads.find(t => t.id === props.threadId)
})

const isMyMessage = (msg) => {
  return msg.senderId === userStore.user?.id || msg.senderName === userStore.user?.username
}

const formatTime = (isoString) => {
  return new Date(isoString).toLocaleString()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (scrollContainer.value) {
      scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
    }
  })
}

const sendReply = async () => {
  if (!replyContent.value.trim()) return
  
  sending.value = true
  try {
    await messageStore.sendMessage({
      threadId: props.threadId,
      recipientId: messages.value[0]?.senderId === userStore.user?.id ? messages.value[0]?.recipientId : messages.value[0]?.senderId,
      recipientName: thread.value.participants[0], // Simplified
      subject: `Re: ${thread.value.subject}`,
      content: replyContent.value,
      // Pass other necessary fields
    })
    replyContent.value = ''
    scrollToBottom()
  } finally {
    sending.value = false
  }
}

watch(() => props.threadId, () => {
  scrollToBottom()
  if (props.threadId) {
    messageStore.markThreadAsRead(props.threadId)
  }
}, { immediate: true })

onMounted(() => {
  scrollToBottom()
})
</script>

<style scoped>
.message-detail-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.detail-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  gap: 15px;
  background: white;
}

.back-btn {
  display: none; /* Hidden on desktop */
  background: none;
  border: none;
  font-size: 1rem;
  color: #666;
  cursor: pointer;
}

.header-content h3 {
  margin: 0 0 5px 0;
  font-size: 1.1rem;
  color: #333;
}

.participants {
  font-size: 0.9rem;
  color: #888;
}

.messages-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: #f9f9f9;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message-row {
  display: flex;
  justify-content: flex-start;
}

.message-row.mine {
  justify-content: flex-end;
}

.message-bubble {
  max-width: 70%;
  background: white;
  padding: 15px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  position: relative;
}

.message-row.mine .message-bubble {
  background: #e3f2fd; /* Light Blue for me */
  border-top-right-radius: 2px;
}

.message-row:not(.mine) .message-bubble {
  border-top-left-radius: 2px;
}

.msg-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 0.8rem;
  color: #888;
  gap: 10px;
}

.sender-name {
  font-weight: 600;
  color: #555;
}

.msg-content {
  line-height: 1.5;
  color: #333;
  white-space: pre-wrap;
}

.attachments {
  margin-top: 10px;
  border-top: 1px dashed #ddd;
  padding-top: 10px;
}

.attachment-item {
  font-size: 0.9rem;
  color: #2c3e50;
  background: #f0f0f0;
  padding: 4px 8px;
  border-radius: 4px;
  display: inline-block;
  margin-right: 5px;
}

.reply-area {
  padding: 20px;
  background: white;
  border-top: 1px solid #eee;
}

.reply-area textarea {
  width: 100%;
  height: 80px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  resize: none;
  font-family: inherit;
  margin-bottom: 10px;
}

.reply-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.btn-attach {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
}

.btn-send {
  background: #C93737;
  color: white;
  border: none;
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.btn-send:disabled {
  background: #e0e0e0;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .back-btn {
    display: block;
  }
}
</style>
