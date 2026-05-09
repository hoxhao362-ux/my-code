import { defineStore } from 'pinia'
import { useUserStore } from './user'

// Mock Data for Initial State
const MOCK_MESSAGES = [
  {
    id: 'msg_001',
    threadId: 'thread_001',
    type: 'system_notice',
    senderId: 'system',
    senderName: 'System Notification',
    senderRole: 'admin',
    recipientId: 'user_001',
    recipientName: 'User',
    recipientRole: 'author',
    subject: 'Welcome to the Communication System',
    content: 'Welcome to the new internal communication system. You can receive notifications and communicate with editors here.',
    createdAt: '2023-10-01T10:00:00Z',
    readAt: null,
    status: 'delivered',
    attachments: []
  },
  {
    id: 'msg_002',
    threadId: 'thread_002',
    type: 'editor_to_author',
    senderId: 'editor_001',
    senderName: 'Chief Editor',
    senderRole: 'editor',
    recipientId: 'user_001',
    recipientName: 'User',
    recipientRole: 'author',
    subject: 'Regarding your submission #2023001',
    content: '<p>Dear Author,</p><p>We have received your submission. The review process will start shortly.</p>',
    createdAt: '2023-10-05T14:30:00Z',
    readAt: '2023-10-05T15:00:00Z',
    status: 'read',
    manuscriptId: '2023001',
    manuscriptTitle: 'Analysis of AI in Healthcare',
    attachments: []
  }
]

export const useMessageStore = defineStore('messages', {
  state: () => ({
    messages: JSON.parse(localStorage.getItem('messages')) || MOCK_MESSAGES,
    threads: [], // Computed from messages usually, but can be cached
    loading: false,
    error: null,
    activeThreadId: null
  }),

  getters: {
    // Get all messages for the current user
    myMessages: (state) => {
      const userStore = useUserStore()
      const currentUser = userStore.user
      if (!currentUser) return []
      
      return state.messages.filter(msg => 
        msg.recipientId === currentUser.id || 
        msg.senderId === currentUser.id ||
        msg.recipientName === currentUser.username || // Fallback for mock data matching
        msg.senderName === currentUser.username
      ).sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
    },

    // Group messages by thread
    myThreads: (state) => {
      const userStore = useUserStore()
      const currentUser = userStore.user
      if (!currentUser) return []

      const threadMap = new Map()
      
      // Filter relevant messages
      const relevantMessages = state.messages.filter(msg => 
        msg.recipientId === currentUser.id || 
        msg.senderId === currentUser.id ||
        msg.recipientName === currentUser.username || 
        msg.senderName === currentUser.username
      )

      relevantMessages.forEach(msg => {
        if (!threadMap.has(msg.threadId)) {
          // Identify the "other" participant
          const isSender = msg.senderName === currentUser.username || msg.senderId === currentUser.id
          const otherName = isSender ? msg.recipientName : msg.senderName
          const otherRole = isSender ? msg.recipientRole : msg.senderRole
          
          threadMap.set(msg.threadId, {
            id: msg.threadId,
            subject: msg.subject,
            manuscriptId: msg.manuscriptId,
            manuscriptTitle: msg.manuscriptTitle,
            lastMessage: msg,
            participants: [otherName],
            participantRole: otherRole,
            unreadCount: 0,
            updatedAt: msg.createdAt
          })
        }
        
        const thread = threadMap.get(msg.threadId)
        
        // Update last message if this one is newer
        if (new Date(msg.createdAt) > new Date(thread.updatedAt)) {
          thread.lastMessage = msg
          thread.updatedAt = msg.createdAt
        }
        
        // Count unread
        const isRecipient = msg.recipientName === currentUser.username || msg.recipientId === currentUser.id
        if (isRecipient && !msg.readAt) {
          thread.unreadCount++
        }
      })

      return Array.from(threadMap.values()).sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt))
    },

    // Get total unread count
    unreadCount: (state) => {
      const userStore = useUserStore()
      const currentUser = userStore.user
      if (!currentUser) return 0
      
      return state.messages.filter(msg => 
        (msg.recipientName === currentUser.username || msg.recipientId === currentUser.id) && 
        !msg.readAt
      ).length
    },

    // Get messages for active thread
    activeThreadMessages: (state) => {
      if (!state.activeThreadId) return []
      return state.messages
        .filter(msg => msg.threadId === state.activeThreadId)
        .sort((a, b) => new Date(a.createdAt) - new Date(b.createdAt))
    }
  },

  actions: {
    // Send a new message
    async sendMessage(payload) {
      this.loading = true
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 600))
      
      const userStore = useUserStore()
      const currentUser = userStore.user
      
      const newMessage = {
        id: `msg_${Date.now()}`,
        threadId: payload.threadId || `thread_${Date.now()}`,
        type: payload.type || 'general',
        senderId: currentUser.id,
        senderName: currentUser.username,
        senderRole: currentUser.role,
        recipientId: payload.recipientId,
        recipientName: payload.recipientName,
        recipientRole: payload.recipientRole,
        subject: payload.subject,
        content: payload.content,
        manuscriptId: payload.manuscriptId,
        manuscriptTitle: payload.manuscriptTitle,
        createdAt: new Date().toISOString(),
        readAt: null,
        status: 'sent',
        attachments: payload.attachments || []
      }
      
      this.messages.push(newMessage)
      this.persistMessages()
      this.loading = false
      return newMessage
    },

    // Mark a message as read
    async markAsRead(messageId) {
      const msg = this.messages.find(m => m.id === messageId)
      if (msg && !msg.readAt) {
        msg.readAt = new Date().toISOString()
        msg.status = 'read'
        this.persistMessages()
      }
    },

    // Mark all messages in a thread as read
    async markThreadAsRead(threadId) {
      const userStore = useUserStore()
      const currentUser = userStore.user
      
      let updated = false
      this.messages.forEach(msg => {
        if (msg.threadId === threadId && 
            (msg.recipientName === currentUser.username || msg.recipientId === currentUser.id) && 
            !msg.readAt) {
          msg.readAt = new Date().toISOString()
          msg.status = 'read'
          updated = true
        }
      })
      
      if (updated) this.persistMessages()
    },

    // Create a new conversation thread
    startNewThread(recipient, subject, content, manuscript = null) {
      return this.sendMessage({
        recipientId: recipient.id,
        recipientName: recipient.username || recipient.name,
        recipientRole: recipient.role,
        subject: subject,
        content: content,
        manuscriptId: manuscript?.id,
        manuscriptTitle: manuscript?.title
      })
    },

    // Delete a message (Mock)
    deleteMessage(messageId) {
      const index = this.messages.findIndex(m => m.id === messageId)
      if (index !== -1) {
        this.messages.splice(index, 1)
        this.persistMessages()
      }
    },

    setActiveThread(threadId) {
      this.activeThreadId = threadId
      // Auto mark as read when opening thread
      if (threadId) {
        this.markThreadAsRead(threadId)
      }
    },

    persistMessages() {
      localStorage.setItem('messages', JSON.stringify(this.messages))
    },

    // Load messages (if fetching from API in future)
    async fetchMessages() {
      // Current implementation loads from localStorage in state init
      // This is a placeholder for real API integration
      this.loading = true
      await new Promise(resolve => setTimeout(resolve, 500))
      this.loading = false
    }
  }
})
