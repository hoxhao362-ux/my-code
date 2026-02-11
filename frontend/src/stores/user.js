import { defineStore } from 'pinia'
import { userApi, journalApi, reviewApi, adminApi } from '../utils/api'
import * as mockUserData from '../mocks/userData'
import * as mockJournalData from '../mocks/journalData'

export const useUserStore = defineStore('user', {
  state: () => ({
    // User Info - Loaded from sessionStorage (Read-Only)
    user: JSON.parse(sessionStorage.getItem('readonly_user')) || null,
    // Submission System User Info - Loaded from localStorage (Submit System)
    submissionUser: JSON.parse(localStorage.getItem('submit_user')) || null,
    
    // Announcements
    announcements: JSON.parse(localStorage.getItem('announcements')) || mockJournalData.announcements,
    
    // Basic Config
    basicConfig: JSON.parse(localStorage.getItem('basicConfig')) || mockJournalData.basicConfig,
    
    // Review Stages
    reviewStages: mockJournalData.reviewStages,
    
    // Module List
    modules: JSON.parse(localStorage.getItem('modules')) || mockJournalData.modules,
    
    // Invitation Codes
    invitationCodes: JSON.parse(localStorage.getItem('invitationCodes')) || mockUserData.invitationCodes,
    
    // Journal List (for Home Display)
    journals: mockJournalData.journals,
    
    // Invitations (Mock Data for Reviewer System)
    invitations: JSON.parse(localStorage.getItem('invitations_v2')) || mockJournalData.invitations,
    
    // Feedback Messages
    feedbackMessages: [],
    
    // User List (for Admin)
    users: JSON.parse(localStorage.getItem('users')) || mockUserData.users
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentRole: (state) => state.user?.role || 'user',
    userJournals: (state) => {
      if (!state.user) return []
      return state.journals.filter(journal => journal.author === state.user.username)
    },
    pendingJournals: (state) => {
      // Localization Update: '待审核' -> 'Pending', '审稿中' -> 'Under Review'
      return state.journals.filter(journal => 
        journal.status === 'Pending' || 
        journal.status === 'Under Review' ||
        journal.status === 'Pending Initial Review' ||
        journal.status === 'Pending Re-review' ||
        journal.status === 'Pending Final Decision'
      )
    },
    // Role Priority: admin > associate_editor > editor > editorial_assistant > advisory_editor > reviewer > author > user
    hasRolePermission: (state) => (requiredRole) => {
      const rolePriority = {
        admin: 7,
        associate_editor: 6,
        editor: 5,
        editorial_assistant: 4,
        ea_ae: 4, // Legacy compatibility
        advisory_editor: 3,
        reviewer: 2,
        author: 1,
        user: 0
      }
      const userRole = state.user?.role || 'user'
      return (rolePriority[userRole] || 0) >= (rolePriority[requiredRole] || 0)
    }
  },

  actions: {
    // Switch User Context (Router Guard Helper)
    syncUserContext(context) {
      if (context === 'submission') {
        this.user = this.submissionUser
      } else {
        // Reload main user from storage in case it changed
        this.user = JSON.parse(sessionStorage.getItem('readonly_user')) || null
      }
    },

    // Login for Submission System
    async loginSubmission(credentials) {
      try {
        // Mock Login Logic
        let role = credentials.role || 
                  (credentials.username === 'admin' ? 'admin' : 
                   credentials.username === 'reviewer' ? 'reviewer' : 
                   credentials.username === 'author' ? 'author' : 
                   'user')
        
        const fullUserInfo = this.users.find(u => u.username === credentials.username)
        
        const userData = {
          username: credentials.username,
          role: role,
          email: fullUserInfo?.email || `${credentials.username}@example.com`,
          phone: fullUserInfo?.phone || '13800138000'
        }
        
        this.submissionUser = userData
        localStorage.setItem('submit_user', JSON.stringify(userData))
        localStorage.setItem('submit_isLogin', 'true')
        localStorage.setItem('submit_userRole', role)
        
        // Context switch only happens explicitly in router guards or specific pages
        // But for immediate feedback if needed:
        // this.user = userData 
        return userData
      } catch (error) {
        console.error('Submission login failed:', error)
        throw error
      }
    },

    // Logout for Submission System
    async logoutSubmission() {
       this.submissionUser = null
       // Only clear submit_ keys
       Object.keys(localStorage).forEach(key => {
         if (key.startsWith('submit_')) {
           localStorage.removeItem(key)
         }
       })
       // Do not touch user (readonly) state here directly, strictly separated
    },

    // Main Login
    async login(credentials) {
      try {
        const response = await userApi.login(credentials)
        let userData = null
        
        if (!response) {
          // Mock Login Fallback
          let role = credentials.role || 
                    (credentials.username === 'admin' ? 'admin' : 
                     credentials.username === 'editor' ? 'editor' : 
                     credentials.username === 'associate_editor' ? 'associate_editor' : 
                     credentials.username === 'editorial_assistant' ? 'editorial_assistant' : 
                     credentials.username === 'ea_ae' ? 'ea_ae' : 
                     credentials.username === 'advisory_editor' ? 'advisory_editor' :
                     credentials.username === 'reviewer' ? 'reviewer' : 
                     credentials.username === 'author' ? 'author' : 
                     'user')
          
          const fullUserInfo = this.users.find(u => u.username === credentials.username)
          
          userData = {
            username: credentials.username,
            role: role,
            email: fullUserInfo?.email || `${credentials.username}@example.com`,
            phone: fullUserInfo?.phone || '13800138000'
          }
        } else {
          userData = {
            ...response,
            username: credentials.username,
            role: response.role || 'user'
          }
        }
        
        this.user = userData
        sessionStorage.setItem('readonly_user', JSON.stringify(userData))
        sessionStorage.setItem('readonly_isLogin', 'true')
        this.refreshJournals()
        return userData
      } catch (error) {
        console.error('Login failed:', error)
        throw error
      }
    },
    
    // Refresh Journals from LocalStorage
    refreshJournals() {
      try {
        const journalsFromStorage = localStorage.getItem('journals_v2')
        if (journalsFromStorage) {
          this.journals = JSON.parse(journalsFromStorage)
        } else {
          localStorage.setItem('journals_v2', JSON.stringify(this.journals))
        }
      } catch (error) {
        console.error('Failed to refresh journals:', error)
      }
    },
    
    // Add Module
    addModule(moduleName) {
      if (!this.modules.includes(moduleName)) {
        this.modules.push(moduleName)
        localStorage.setItem('modules', JSON.stringify(this.modules))
      }
    },
    
    // Remove Module
    removeModule(moduleName) {
      if (moduleName === 'Others') return // Protect default module
      this.modules = this.modules.filter(module => module !== moduleName)
      localStorage.setItem('modules', JSON.stringify(this.modules))
    },
    
    // Update Invitation Code
    updateInvitationCode(type, code) {
      this.invitationCodes[type] = code
      localStorage.setItem('invitationCodes', JSON.stringify(this.invitationCodes))
    },
    
    // Update All Invitation Codes
    updateAllInvitationCodes(codes) {
      this.invitationCodes = { ...this.invitationCodes, ...codes }
      localStorage.setItem('invitationCodes', JSON.stringify(this.invitationCodes))
    },

    // Logout
    async logout() {
      try {
        if (this.user) {
          await userApi.logout()
        }
      } catch (error) {
        console.error('Logout API failed:', error)
      } finally {
        this.user = null
        // Clear only readonly keys from sessionStorage
        Object.keys(sessionStorage).forEach(key => {
          if (key.startsWith('readonly_')) {
            sessionStorage.removeItem(key)
          }
        })
      }
    },

    // Update User
    async updateUser(userData) {
      try {
        const updatedUser = { ...this.user, ...userData }
        this.user = updatedUser
        sessionStorage.setItem('readonly_user', JSON.stringify(updatedUser))
        return updatedUser
      } catch (error) {
        console.error('Update user failed:', error)
        throw error
      }
    },

    // Fetch Current User
    async fetchCurrentUser() {
      try {
        const userData = await userApi.getCurrentUser()
        this.user = userData
        sessionStorage.setItem('readonly_user', JSON.stringify(userData))
        return userData
      } catch (error) {
        console.error('Fetch user failed:', error)
        throw error
      }
    },

    // Upload Journal
    async uploadJournal(formData) {
      try {
        const response = await journalApi.upload(formData)
        return response
      } catch (error) {
        console.error('Upload failed:', error)
        throw error
      }
    },

    // Fetch My Journals
    async fetchMyJournals(params = {}) {
      try {
        const response = await journalApi.getMyJournals(params)
        return response
      } catch (error) {
        console.error('Fetch my journals failed:', error)
        throw error
      }
    },

    // Fetch Journal Detail
    async fetchJournalDetail(jid) {
      try {
        const response = await journalApi.getJournalDetail(jid)
        return response
      } catch (error) {
        console.error('Fetch journal detail failed:', error)
        throw error
      }
    },

    // Delete Journal
    async deleteJournal(jid) {
      try {
        const response = await journalApi.deleteJournal(jid)
        return response
      } catch (error) {
        console.error('Delete journal failed:', error)
        throw error
      }
    },

    // Fetch Pending Journals
    async fetchPendingJournals(params = {}) {
      try {
        const response = await reviewApi.getPendingJournals(params)
        return response
      } catch (error) {
        console.error('Fetch pending journals failed:', error)
        throw error
      }
    },

    // Review Journal
    async reviewJournal(jid, reviewData) {
      try {
        const response = await reviewApi.reviewJournal(jid, reviewData)
        return response
      } catch (error) {
        console.error('Review journal failed:', error)
        throw error
      }
    },

    // Fetch Review History
    async fetchReviewHistory(params = {}) {
      try {
        const response = await reviewApi.getReviewHistory(params)
        return response
      } catch (error) {
        console.error('Fetch review history failed:', error)
        throw error
      }
    },

    // Fetch Review Statistics
    async fetchReviewStatistics() {
      try {
        const response = await reviewApi.getReviewStatistics()
        return response
      } catch (error) {
        console.error('Fetch review stats failed:', error)
        throw error
      }
    },

    // Fetch Rejected Journals
    async fetchRejectedJournals(params = {}) {
      try {
        const response = await reviewApi.getRejectedJournals(params)
        return response
      } catch (error) {
        console.error('Fetch rejected journals failed:', error)
        throw error
      }
    },

    // Fetch Users (Admin)
    async fetchUsers(params = {}) {
      try {
        const response = await adminApi.getUsers(params)
        return response
      } catch (error) {
        console.error('Fetch users failed:', error)
        throw error
      }
    },

    // Update User Role (Admin)
    async updateUserRoleApi(uid, role) {
      try {
        const response = await adminApi.updateUserRole(uid, role)
        return response
      } catch (error) {
        console.error('Update user role failed:', error)
        throw error
      }
    },

    // Delete User (Admin)
    async deleteUserApi(uid) {
      try {
        const response = await adminApi.deleteUser(uid)
        return response
      } catch (error) {
        console.error('Delete user failed:', error)
        throw error
      }
    },

    // Fetch All Journals (Admin)
    async fetchAllJournals(params = {}) {
      try {
        const response = await adminApi.getAllJournals(params)
        return response
      } catch (error) {
        console.error('Fetch all journals failed:', error)
        throw error
      }
    },

    // Admin Delete Journal
    async adminDeleteJournal(jid) {
      try {
        const response = await adminApi.deleteJournal(jid)
        return response
      } catch (error) {
        console.error('Admin delete journal failed:', error)
        throw error
      }
    },

    // Fetch All Review Records (Admin)
    async fetchAllReviewRecords(params = {}) {
      try {
        const response = await adminApi.getAllReviewRecords(params)
        return response
      } catch (error) {
        console.error('Fetch all review records failed:', error)
        throw error
      }
    },

    // Fetch System Statistics (Admin)
    async fetchSystemStatistics() {
      try {
        const response = await adminApi.getSystemStatistics()
        return response
      } catch (error) {
        console.error('Fetch system stats failed:', error)
        throw error
      }
    },

    // Fetch Deleted Journals (Admin)
    async fetchDeletedJournals(params = {}) {
      try {
        const response = await adminApi.getDeletedJournals(params)
        return response
      } catch (error) {
        console.error('Fetch deleted journals failed:', error)
        throw error
      }
    },

    // Permanently Delete Journal (Admin)
  async permanentlyDeleteJournal(jid) {
    try {
      const response = await adminApi.permanentlyDeleteJournal(jid)
      return response
    } catch (error) {
      console.error('Permanently delete journal failed:', error)
      throw error
    }
  },
  
  // Load Feedback Messages
  loadFeedbackMessages() {
    try {
      const storedFeedbacks = localStorage.getItem('feedbacks')
      if (storedFeedbacks) {
        const parsedFeedbacks = JSON.parse(storedFeedbacks)
        this.feedbackMessages = parsedFeedbacks.map(feedback => ({
          ...feedback,
          status: feedback.status || 'Unprocessed'
        }))
      }
    } catch (error) {
      console.error('Load feedback failed:', error)
      localStorage.removeItem('feedbacks')
      this.feedbackMessages = []
    }
  },
  
  // Set Announcements
  setAnnouncements(announcements) {
    this.announcements = announcements
    localStorage.setItem('announcements', JSON.stringify(this.announcements))
  },
  
  // Set Basic Config
  setBasicConfig(config) {
    this.basicConfig = config
    localStorage.setItem('basicConfig', JSON.stringify(this.basicConfig))
  },
  
  // Add Feedback Message
  addFeedbackMessage(feedbackData) {
    const newFeedback = {
      ...feedbackData,
      status: 'Unprocessed',
      createdAt: new Date().toISOString()
    }
    
    this.feedbackMessages.push(newFeedback)
    localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
    return newFeedback
  },
  
  // Update Feedback Status
  updateFeedbackMessageStatus(messageId, status) {
    const messageIndex = this.feedbackMessages.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      this.feedbackMessages[messageIndex].status = status
      localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
      return true
    }
    return false
  },
  
  // Delete Feedback
  deleteFeedbackMessage(messageId) {
    const messageIndex = this.feedbackMessages.findIndex(msg => msg.id === messageId)
    if (messageIndex !== -1) {
      this.feedbackMessages.splice(messageIndex, 1)
      localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
      return true
    }
    return false
  },
  
  // Bulk Delete Feedback
  deleteMultipleFeedbackMessages(messageIds) {
    this.feedbackMessages = this.feedbackMessages.filter(msg => !messageIds.includes(msg.id))
    localStorage.setItem('feedbacks', JSON.stringify(this.feedbackMessages))
    return true
  },
  
  // Update User Role
  updateUserRole(userId, newRole) {
    const userIndex = this.users.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      this.users[userIndex].role = newRole
      localStorage.setItem('users', JSON.stringify(this.users))
      return true
    }
    return false
  },
  
  // Update User Status
  updateUserStatus(userId, newStatus) {
    const userIndex = this.users.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      this.users[userIndex].status = newStatus
      localStorage.setItem('users', JSON.stringify(this.users))
      return true
    }
    return false
  },
  
  // Update User Info
  updateUserInfo(userId, userInfo) {
    const userIndex = this.users.findIndex(user => user.id === userId)
    if (userIndex !== -1) {
      this.users[userIndex] = {
        ...this.users[userIndex],
        ...userInfo
      }
      localStorage.setItem('users', JSON.stringify(this.users))
      return true
    }
    return false
  },
  
  // Add User
  addUser(userData) {
    const id = Math.max(...this.users.map(u => u.id), 0) + 1
    const newUser = {
      id,
      status: 'active',
      ...userData
    }
    this.users.push(newUser)
    localStorage.setItem('users', JSON.stringify(this.users))
    return newUser
  },
  
  // Delete User
  deleteUser(userId) {
    this.users = this.users.filter(user => user.id !== userId)
    localStorage.setItem('users', JSON.stringify(this.users))
    return true
  },
  
  // Add Journal
  addJournal(journalData) {
    this.journals.push(journalData)
    localStorage.setItem('journals_v2', JSON.stringify(this.journals))
    return journalData
  },
  
  // Update Journal
  updateJournal(updatedJournal) {
    const journalIndex = this.journals.findIndex(journal => journal.id === updatedJournal.id)
    if (journalIndex !== -1) {
      this.journals[journalIndex] = updatedJournal
      localStorage.setItem('journals_v2', JSON.stringify(this.journals))
      return true
    }
    return false
  },

  // Update Invitation
  updateInvitation(updatedInvitation) {
    const index = this.invitations.findIndex(i => i.id === updatedInvitation.id)
    if (index !== -1) {
      this.invitations[index] = updatedInvitation
      localStorage.setItem('invitations_v2', JSON.stringify(this.invitations))
      return true
    }
    return false
  }
}
})
