<template>
  <div class="message-center-container">
    <!-- Sidebar / Thread List -->
    <div class="thread-list-panel" :class="{ 'hidden-mobile': activeThreadId && isMobile }">
      <div class="panel-header">
        <h2>Messages</h2>
        <button class="btn-compose" @click="openComposeModal">
          <span class="icon">+</span> New Message
        </button>
      </div>
      
      <div class="search-bar">
        <input type="text" v-model="searchQuery" placeholder="Search messages..." />
      </div>

      <div class="threads-scroll-area">
        <div v-if="filteredThreads.length === 0" class="no-threads">
          No messages found.
        </div>
        <div 
          v-for="thread in filteredThreads" 
          :key="thread.id" 
          class="thread-item"
          :class="{ 'active': activeThreadId === thread.id, 'unread': thread.unreadCount > 0 }"
          @click="selectThread(thread.id)"
        >
          <div class="thread-avatar">
            {{ getInitials(thread.participants[0]) }}
          </div>
          <div class="thread-content">
            <div class="thread-header">
              <span class="participant-name">{{ thread.participants[0] }}</span>
              <span class="thread-date">{{ formatDate(thread.updatedAt) }}</span>
            </div>
            <div class="thread-subject">{{ thread.subject }}</div>
            <div class="thread-preview">{{ getPreview(thread.lastMessage) }}</div>
          </div>
          <div v-if="thread.unreadCount > 0" class="unread-badge">{{ thread.unreadCount }}</div>
        </div>
      </div>
    </div>

    <!-- Main Content / Message Detail -->
    <div class="message-detail-panel" :class="{ 'active-mobile': activeThreadId && isMobile }">
      <div v-if="!activeThreadId" class="empty-state">
        <div class="empty-icon">✉️</div>
        <h3>Select a conversation</h3>
        <p>Choose a thread from the list to view details or start a new one.</p>
      </div>
      
      <MessageDetail 
        v-else 
        :thread-id="activeThreadId" 
        @back="activeThreadId = null"
      />
    </div>

    <!-- Compose Modal -->
    <ComposeMessage 
      v-if="showCompose" 
      @close="showCompose = false"
      @sent="handleMessageSent"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useMessageStore } from '../../stores/messages'
import MessageDetail from './MessageDetail.vue'
import ComposeMessage from './ComposeMessage.vue'
import { useRoute } from 'vue-router'

const messageStore = useMessageStore()
const route = useRoute()

const searchQuery = ref('')
const activeThreadId = ref(null)
const showCompose = ref(false)
const isMobile = ref(window.innerWidth < 768)

// Load threads
const threads = computed(() => {
  // Logic to group messages into threads is in the store
  // We need to implement a getter in the store for this
  // Assuming store.myThreads returns formatted threads
  return messageStore.myThreads
}) // This might need the store update to work perfectly if I didn't implement it fully yet

// Filter threads
const filteredThreads = computed(() => {
  if (!searchQuery.value) return threads.value
  const query = searchQuery.value.toLowerCase()
  return threads.value.filter(t => 
    t.subject.toLowerCase().includes(query) || 
    t.participants[0].toLowerCase().includes(query)
  )
})

const selectThread = (id) => {
  activeThreadId.value = id
  messageStore.setActiveThread(id)
}

const openComposeModal = () => {
  showCompose.value = true
}

const handleMessageSent = () => {
  showCompose.value = false
  // Refresh list or auto-select new thread if possible
}

const getInitials = (name) => {
  return name ? name.charAt(0).toUpperCase() : '?'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString()
}

const getPreview = (msg) => {
  if (!msg) return ''
  // Strip HTML tags for preview
  const tmp = document.createElement('DIV')
  tmp.innerHTML = msg.content
  const text = tmp.textContent || tmp.innerText || ''
  return text.substring(0, 50) + (text.length > 50 ? '...' : '')
}

// Responsive handling
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', checkMobile)
  if (route.query.threadId) {
    selectThread(route.query.threadId)
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>

<style scoped>
.message-center-container {
  display: flex;
  height: calc(100vh - 60px); /* Adjust based on navbar height */
  background: #f5f7fa;
  margin-top: 60px; /* Navbar offset */
  overflow: hidden;
}

/* Sidebar */
.thread-list-panel {
  width: 350px;
  background: white;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: transform 0.3s ease;
}

.panel-header {
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f0f0f0;
}

.panel-header h2 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

.btn-compose {
  background: #C93737;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 8px 16px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background 0.2s;
}

.btn-compose:hover {
  background: #b02e2e;
}

.search-bar {
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
}

.search-bar input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background: #f9f9f9;
}

.threads-scroll-area {
  flex: 1;
  overflow-y: auto;
}

.thread-item {
  display: flex;
  padding: 15px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
  position: relative;
}

.thread-item:hover {
  background: #f9f9f9;
}

.thread-item.active {
  background: #eef2f7;
  border-left: 3px solid #C93737;
}

.thread-item.unread {
  background: #fff8f8;
}

.thread-item.unread .participant-name,
.thread-item.unread .thread-subject {
  font-weight: 700;
  color: #000;
}

.thread-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e0e0e0;
  color: #666;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-right: 15px;
  flex-shrink: 0;
}

.thread-content {
  flex: 1;
  min-width: 0; /* Text truncation fix */
}

.thread-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 4px;
}

.participant-name {
  font-weight: 600;
  color: #333;
  font-size: 0.95rem;
}

.thread-date {
  font-size: 0.8rem;
  color: #999;
}

.thread-subject {
  font-size: 0.9rem;
  color: #555;
  margin-bottom: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.thread-preview {
  font-size: 0.85rem;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.unread-badge {
  background: #C93737;
  color: white;
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 10px;
  position: absolute;
  right: 15px;
  top: 40px;
}

/* Main Panel */
.message-detail-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: white;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #999;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  opacity: 0.5;
}

/* Mobile Styles */
@media (max-width: 768px) {
  .thread-list-panel {
    width: 100%;
  }
  
  .thread-list-panel.hidden-mobile {
    display: none;
  }
  
  .message-detail-panel {
    display: none;
  }
  
  .message-detail-panel.active-mobile {
    display: flex;
    width: 100%;
  }
}
</style>
