import { defineStore } from 'pinia'
import { userApi, journalApi, reviewApi, adminApi, editorApi } from '../utils/api'
import * as mockUserData from '../mocks/userData'
import * as mockEditorAccounts from '../mocks/editorAccounts'
import * as mockReviewerAccounts from '../mocks/reviewerAccounts'
import * as mockJournalData from '../mocks/journalData'

export const useUserStore = defineStore('user', {
  state: () => ({
    // User Info - Loaded from sessionStorage (Read-Only)
    user: JSON.parse(sessionStorage.getItem('readonly_user')) || null,
    // Submission System User Info - Loaded from localStorage (Submit System)
    submissionUser: JSON.parse(localStorage.getItem('submit_user')) || null,

    // Reviewer Application State
    reviewerApplication: {
      status: localStorage.getItem('reviewer_application_status') || 'pending_apply', // pending_apply, pending_review, approved, rejected, withdrawn
      data: JSON.parse(localStorage.getItem('reviewer_application_data')) || null,
      draft: JSON.parse(localStorage.getItem('reviewer_application_draft')) || null
    },
    
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
    
    // Recommended Reviewers (Mock Data)
    recommendedReviewers: JSON.parse(localStorage.getItem('recommendedReviewers')) || [
      {
        id: 1,
        manuscriptId: 101,
        manuscriptTitle: '基于深度学习的医学图像分析',
        writerId: 1,
        writerName: '张三',
        reviewerName: '李四',
        reviewerEmail: 'lisi@example.com',
        reviewerAffiliation: '北京大学医学部',
        reviewerExpertise: ['医学影像', '深度学习'],
        recommendationReason: '该专家在医学影像领域有丰富经验，发表过多篇相关高质量论文',
        status: 'pending',
        recommendedAt: '2026-02-10T10:00:00Z',
        reviewedAt: null,
        reviewedBy: null,
        submissionCount: 1,
        avgScore: 4.8,
        riskLevel: 'low',
        evalStatus: 'pending'
      },
      {
        id: 2,
        manuscriptId: 102,
        manuscriptTitle: '新型药物研发进展',
        writerId: 2,
        writerName: '王五',
        reviewerName: '赵六',
        reviewerEmail: 'zhaoliu@example.com',
        reviewerAffiliation: '中国科学院药物研究所',
        reviewerExpertise: ['药物化学', '药理学'],
        recommendationReason: '该专家在新型药物研发领域有深入研究，熟悉相关技术路线',
        status: 'accepted',
        recommendedAt: '2026-02-08T14:30:00Z',
        reviewedAt: '2026-02-12T09:15:00Z',
        reviewedBy: 'admin',
        submissionCount: 3,
        avgScore: 3.5,
        riskLevel: 'medium',
        evalStatus: 'pending'
      },
      {
        id: 3,
        manuscriptId: 103,
        manuscriptTitle: '临床研究方法学探讨',
        writerId: 3,
        writerName: '孙七',
        reviewerName: '周八',
        reviewerEmail: 'zhouba@example.com',
        reviewerAffiliation: '北京协和医院',
        reviewerExpertise: ['临床医学', '临床研究方法学'],
        recommendationReason: '该专家在临床研究方法学领域有丰富经验，担任过多项临床试验的PI',
        status: 'rejected',
        recommendedAt: '2026-02-05T16:45:00Z',
        reviewedAt: '2026-02-09T11:20:00Z',
        reviewedBy: 'admin',
        submissionCount: 5,
        avgScore: 2.1,
        riskLevel: 'high',
        evalStatus: 'pending'
      },
      {
        id: 5,
        manuscriptId: 105,
        manuscriptTitle: '生物信息学在医学研究中的应用',
        writerId: 5,
        writerName: '陈一',
        reviewerName: '林二',
        reviewerEmail: 'liner@example.com',
        reviewerAffiliation: '清华大学医学院',
        reviewerExpertise: ['生物信息学', '基因组学'],
        recommendationReason: '该专家在生物信息学领域有突出贡献，开发了多个 widely used 的生物信息学工具',
        status: 'completed', 
        recommendedAt: '2026-01-28T13:15:00Z',
        reviewedAt: '2026-01-30T10:20:00Z',
        reviewedBy: 'admin',
        submissionCount: 1,
        avgScore: 4.9,
        riskLevel: 'low',
        evalStatus: 'unevaluated' 
      }
    ],

    // Opposed Reviewers (Mock Data)
    opposedReviewers: JSON.parse(localStorage.getItem('opposedReviewers')) || [
      {
        id: 1,
        manuscriptId: 101,
        manuscriptTitle: '基于深度学习的医学图像分析',
        writerId: 1,
        writerName: '张三',
        opposedReviewerName: '王某某',
        opposedReviewerAffiliation: '某大学附属医院',
        opposedReason: '学术观点存在严重分歧，且该专家曾公开批评过本课题组的研究方向，可能存在偏见。',
        status: 'pending',
        requestedAt: '2026-02-10T10:00:00Z',
        handledAt: null,
        handledBy: null
      },
      {
        id: 2,
        manuscriptId: 102,
        manuscriptTitle: '新型药物研发进展',
        writerId: 2,
        writerName: '李四',
        opposedReviewerName: '陈某某',
        opposedReviewerAffiliation: '竞争对手实验室',
        opposedReason: '目前正在进行类似药物的研发，存在直接的利益冲突。',
        status: 'accepted',
        requestedAt: '2026-02-08T14:30:00Z',
        handledAt: '2026-02-09T09:15:00Z',
        handledBy: 'admin'
      },
      {
        id: 3,
        manuscriptId: 104,
        manuscriptTitle: '公共卫生政策分析',
        writerId: 4,
        writerName: '赵六',
        opposedReviewerName: '刘某某',
        opposedReviewerAffiliation: '未知机构',
        opposedReason: '理由不充分，仅表示不希望该专家评审。',
        status: 'rejected',
        requestedAt: '2026-02-03T09:30:00Z',
        handledAt: '2026-02-04T14:45:00Z',
        handledBy: 'admin'
      }
    ],

    // Feedback Messages
    feedbackMessages: [],
    
    // User List (for Admin) - Always include all mock data to ensure reviewers are available
    users: [...mockUserData.users, ...mockEditorAccounts.editorAccounts, ...mockReviewerAccounts.reviewerAccounts],

    // System Logs
    systemLogs: JSON.parse(localStorage.getItem('systemLogs')) || [
      // Latest Operations (Mock)
      { id: 13, type: 'operation', user: 'admin', action: 'Login', target: '/admin', time: '2026-01-11 09:30:25', ip: '127.0.0.1', status: 'success' },
      { id: 14, type: 'operation', user: 'admin', action: 'View User List', target: '/admin/users', time: '2026-01-11 09:32:18', ip: '127.0.0.1', status: 'success' },
      { id: 17, type: 'operation', user: 'reviewer1', action: 'Review Manuscript', target: 'Manuscript ID:20260111001', time: '2026-01-11 09:45:30', ip: '192.168.1.106', status: 'success' },
      { id: 18, type: 'operation', user: 'writer1', action: 'Submit Manuscript', target: 'Manuscript ID:20260111002', time: '2026-01-11 09:50:22', ip: '192.168.1.107', status: 'success' },
      { id: 5, type: 'login', user: 'admin', action: 'Login Success', target: '', time: '2026-01-08 17:00:00', ip: '127.0.0.1', status: 'success' },
      { id: 9, type: 'error', user: 'user2', action: 'Access Denied', target: '/admin/dashboard', time: '2026-01-08 16:40:00', ip: '192.168.1.103', status: 'error' }
    ],

    // Decision Drafts
    decisionDrafts: JSON.parse(localStorage.getItem('decisionDrafts')) || [],

    // Notifications
    notifications: JSON.parse(localStorage.getItem('notifications')) || []
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
    currentRole: (state) => state.user?.role || 'user',
    userJournals: (state) => {
      if (!state.user) return []
      return state.journals.filter(journal => journal.writer === state.user.username)
    },
    pendingJournals: (state) => {
      // Localization Update: Support Journal Platform Standard Statuses
      return state.journals.filter(journal => 
        journal.status === 'Pending' || 
        journal.status === 'Under Review' ||
        journal.status === 'pending_initial_review' ||
        journal.status === 'initial_review_passed' ||
        journal.status === 'under_peer_review' ||
        journal.status === 'review_completed' ||
        journal.status === 'final_decision_pending' ||
        // Legacy support
        journal.status === 'Pending Screening' ||
        journal.status === 'Pending Initial Review' ||
        journal.status === 'Pending Re-review' ||
        journal.status === 'Pending Final Decision'
      )
    },
    
    // Reviewer Application Status Getter
    reviewerApplicationStatus: (state) => {
      // If user is already a reviewer (role-based), they are automatically approved
      if (state.user?.role === 'reviewer') {
        return 'approved'
      }
      return state.reviewerApplication.status
    },

    // Role Priority: admin > associate_editor > editor > editorial_assistant > advisory_editor > reviewer > writer > user
    hasRolePermission: (state) => (requiredRole) => {
      const rolePriority = {
        admin: 7,
        associate_editor: 6,
        editor: 5,
        editorial_assistant: 4,
        ea_ae: 4, // Legacy compatibility
        advisory_editor: 3,
        reviewer: 2,
        writer: 1,
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
        const { username, password } = credentials
        const now = Date.now()
        
        // 1. Check Lock Status
        const lockKey = `login_lock_${username}`
        const lockTime = localStorage.getItem(lockKey)
        if (lockTime && now < parseInt(lockTime)) {
          const remainingMinutes = Math.ceil((parseInt(lockTime) - now) / 60000)
          throw new Error(`Account locked. Please try again in ${remainingMinutes} minutes.`)
        }

        // 2. Password Verification
        // Preset passwords mapping based on role
        const PASSWORDS = {
          'admin': 'admin123',
          'editor': 'editor123',
          'associate_editor': 'associate_editor123',
          'editorial_assistant': 'editorial_assistant123',
          'ea_ae': 'editorial_assistant123',
          'advisory_editor': 'advisory_editor123',
          'reviewer': 'reviewer123',
          'writer': 'writer123'
        }
        
        // Get user role first
        let userRole = credentials.role || 'user'
        
        // Find user in users array to get actual role
        const user = this.users.find(u => u.username === username)
        if (user) {
          userRole = user.role
        }
        
        // Determine expected password based on role
        const expectedPassword = PASSWORDS[userRole] || 'user123'
        
        if (password !== expectedPassword) {
          // Increment failed attempts
          const attemptsKey = `login_attempts_${username}`
          let attempts = parseInt(localStorage.getItem(attemptsKey) || '0') + 1
          localStorage.setItem(attemptsKey, attempts.toString())
          
          if (attempts >= 5) {
            // Lock for 30 minutes
            localStorage.setItem(lockKey, (now + 30 * 60 * 1000).toString())
            localStorage.removeItem(attemptsKey) // Reset attempts after locking
            throw new Error('Too many failed attempts. Account locked for 30 minutes.')
          }
          
          throw new Error(`Invalid password. (${attempts}/5 attempts)`)
        }

        // 3. Login Success - Clear attempts
        localStorage.removeItem(`login_attempts_${username}`)
        localStorage.removeItem(lockKey)

        // Log the successful login
        this.addSystemLog({
          type: 'login',
          user: username,
          action: 'Login Submission Success',
          target: 'Submission System',
          status: 'success'
        })

        // Mock Login Logic
        // Align with login() method logic for role determination
        const fullUserInfo = this.users.find(u => u.username === credentials.username)
        let role = credentials.role || fullUserInfo?.role || 
                  (credentials.username === 'admin' ? 'admin' : 
                   credentials.username === 'editor' ? 'editor' : 
                   credentials.username === 'associate_editor' ? 'associate_editor' : 
                   credentials.username === 'editorial_assistant' ? 'editorial_assistant' : 
                   credentials.username === 'ea_ae' ? 'ea_ae' : 
                   credentials.username === 'advisory_editor' ? 'advisory_editor' :
                   credentials.username === 'reviewer' || credentials.username.startsWith('reviewer') ? 'reviewer' : 
                   credentials.username === 'writer' || credentials.username.startsWith('writer') ? 'writer' : 
                   'user')
        
        const userData = {
          username: credentials.username,
          role: role,
          status: fullUserInfo?.status || 'active',
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
        const { username, password } = credentials
        const now = Date.now()
        
        // 1. Check Lock Status (Shared with Submission for simplicity, or use separate keys if needed)
        // Requirement says "Temporary lockout... 30 minutes". Assuming shared lockout policy.
        const lockKey = `login_lock_${username}`
        const lockTime = localStorage.getItem(lockKey)
        if (lockTime && now < parseInt(lockTime)) {
          const remainingMinutes = Math.ceil((parseInt(lockTime) - now) / 60000)
          throw new Error(`Account locked. Please try again in ${remainingMinutes} minutes.`)
        }

        // 2. Password Verification
        const PASSWORDS = {
          'admin': 'admin123',
          'editor': 'editor123',
          'associate_editor': 'associate_editor123',
          'editorial_assistant': 'editorial_assistant123',
          'ea_ae': 'editorial_assistant123',
          'advisory_editor': 'advisory_editor123',
          'reviewer': 'reviewer123',
          'writer': 'writer123'
        }
        
        // Get user role first
        let userRole = credentials.role || 'user'
        
        // Find user in users array to get actual role
        const user = this.users.find(u => u.username === username)
        if (user) {
          userRole = user.role
        }
        
        // Determine expected password based on role
        const expectedPassword = PASSWORDS[userRole] || 'user123'
        
        // Only verify if password is provided (some flows might be token based, but here we assume password login)
        if (password && password !== expectedPassword) {
           const attemptsKey = `login_attempts_${username}`
           let attempts = parseInt(localStorage.getItem(attemptsKey) || '0') + 1
           localStorage.setItem(attemptsKey, attempts.toString())
           
           if (attempts >= 5) {
             localStorage.setItem(lockKey, (now + 30 * 60 * 1000).toString())
             localStorage.removeItem(attemptsKey)
             throw new Error('Too many failed attempts. Account locked for 30 minutes.')
           }
           throw new Error(`Invalid password. (${attempts}/5 attempts)`)
        }
        
        // Clear attempts on success (will happen if we proceed)
        if (password === expectedPassword) {
            localStorage.removeItem(`login_attempts_${username}`)
            localStorage.removeItem(lockKey)
        }

        const response = await userApi.login(credentials)
        let userData = null
        
        if (!response) {
          // Mock Login Fallback
          // First check if user exists in users array to get proper role
          const fullUserInfo = this.users.find(u => u.username === credentials.username)
          let role = credentials.role || fullUserInfo?.role || 
                    (credentials.username === 'admin' ? 'admin' : 
                     credentials.username === 'editor' ? 'editor' : 
                     credentials.username === 'associate_editor' ? 'associate_editor' : 
                     credentials.username === 'editorial_assistant' ? 'editorial_assistant' : 
                     credentials.username === 'ea_ae' ? 'ea_ae' : 
                     credentials.username === 'advisory_editor' ? 'advisory_editor' :
                     credentials.username === 'reviewer' || credentials.username.startsWith('reviewer') ? 'reviewer' : 
                     credentials.username === 'writer' || credentials.username.startsWith('writer') ? 'writer' : 
                     'user')
          
          userData = {
            username: credentials.username,
            role: role,
            status: fullUserInfo?.status || 'active',
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
        // Always use mock data to ensure consistency
        this.journals = mockJournalData.journals
        localStorage.setItem('journals_v2', JSON.stringify(this.journals))
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
      // Use loose equality to handle string/number ID mismatch
      const journalIndex = this.journals.findIndex(journal => String(journal.id) === String(updatedJournal.id))
      if (journalIndex !== -1) {
        // Use splice to ensure reactivity
        this.journals.splice(journalIndex, 1, updatedJournal)
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
    },

    // Update Recommended Reviewer
    updateRecommendedReviewer(updatedReviewer) {
      const index = this.recommendedReviewers.findIndex(r => r.id === updatedReviewer.id)
      if (index !== -1) {
        this.recommendedReviewers[index] = updatedReviewer
        localStorage.setItem('recommendedReviewers', JSON.stringify(this.recommendedReviewers))
        return true
      }
      return false
    },

    // Update Opposed Reviewer
    updateOpposedReviewer(updatedOpposed) {
      const index = this.opposedReviewers.findIndex(o => o.id === updatedOpposed.id)
      if (index !== -1) {
        this.opposedReviewers[index] = updatedOpposed
        localStorage.setItem('opposedReviewers', JSON.stringify(this.opposedReviewers))
        return true
      }
      return false
    },

    // Add System Log
    addSystemLog(logData) {
      const newLog = {
        id: Date.now(),
        time: new Date().toLocaleString(),
        ip: logData.ip || '127.0.0.1', // Mock IP
        status: 'success',
        ...logData
      }
      this.systemLogs.unshift(newLog)
      // Keep only last 1000 logs
      if (this.systemLogs.length > 1000) {
        this.systemLogs = this.systemLogs.slice(0, 1000)
      }
      localStorage.setItem('systemLogs', JSON.stringify(this.systemLogs))
      return newLog
    },

    // Save Decision Draft
    saveDecisionDraft(draft) {
      const index = this.decisionDrafts.findIndex(d => d.manuscriptId === draft.manuscriptId)
      if (index !== -1) {
        this.decisionDrafts[index] = { ...this.decisionDrafts[index], ...draft, lastUpdated: new Date().toISOString() }
      } else {
        this.decisionDrafts.push({ ...draft, lastUpdated: new Date().toISOString() })
      }
      localStorage.setItem('decisionDrafts', JSON.stringify(this.decisionDrafts))
    },

    // Get Decision Draft
    getDecisionDraft(manuscriptId) {
      return this.decisionDrafts.find(d => d.manuscriptId === manuscriptId)
    },

    // --- Reviewer Application Actions ---

    // Save Draft
    saveReviewerApplicationDraft(data) {
      this.reviewerApplication.draft = data
      localStorage.setItem('reviewer_application_draft', JSON.stringify(data))
    },

    // Submit Application
    async submitReviewerApplication(data) {
      // Mock API call
      return new Promise((resolve) => {
        setTimeout(() => {
          this.reviewerApplication.status = 'pending_review'
          this.reviewerApplication.data = data
          this.reviewerApplication.draft = null // Clear draft after submit
          
          localStorage.setItem('reviewer_application_status', 'pending_review')
          localStorage.setItem('reviewer_application_data', JSON.stringify(data))
          localStorage.removeItem('reviewer_application_draft')
          
          resolve(true)
        }, 1000)
      })
    },

    // Withdraw Application
    withdrawReviewerApplication() {
      this.reviewerApplication.status = 'withdrawn'
      localStorage.setItem('reviewer_application_status', 'withdrawn')
    },

    // Reapply (Reset to Draft)
    reapplyReviewer() {
      // Move data back to draft if needed, or just allow editing
      if (this.reviewerApplication.data) {
        this.reviewerApplication.draft = this.reviewerApplication.data
        localStorage.setItem('reviewer_application_draft', JSON.stringify(this.reviewerApplication.data))
      }
      this.reviewerApplication.status = 'pending_apply' // Reset status
      localStorage.setItem('reviewer_application_status', 'pending_apply')
    },

    // --- Editor Actions ---
    // Fetch Editors List
    async fetchEditorsList() {
      try {
        await editorApi.getEditorsList() // Call API (Mocked)
        
        let editors = this.users.filter(u => u.role === 'editor' || u.role === 'associate_editor')

        // Fallback: If local storage data is corrupted or missing editors, use mocks
        if (editors.length === 0) {
           console.warn('No editors found in user store, using mock data fallback.')
           const mockEditors = [
             ...mockEditorAccounts.editorAccounts,
             ...mockUserData.users.filter(u => u.role === 'editor' || u.role === 'associate_editor')
           ]
           // Deduplicate based on ID
           const uniqueEditors = Array.from(new Map(mockEditors.map(item => [item.id, item])).values())
           editors = uniqueEditors
        }

        return editors.map(u => ({ 
            id: u.id, 
            name: u.fullName || u.username, 
            email: u.email 
          }))
      } catch (error) {
        console.error('Fetch editors failed:', error)
        throw error
      }
    },

    // Assign Editor
    async assignEditorToManuscript(manuscriptId, editorId) {
      try {
        await editorApi.assignEditor({ manuscript_id: manuscriptId, editor_id: editorId }) // Call API
        // Update local state
        const journalIndex = this.journals.findIndex(j => j.id === manuscriptId)
        if (journalIndex !== -1) {
          const journal = { ...this.journals[journalIndex] } // Create copy
          journal.assigned_editor_id = editorId
          journal.status = 'assigned_to_editor'
          
          // Find editor name for display consistency
          // Ensure users are loaded or use a fallback if needed
          let editor = this.users.find(u => u.id === editorId)
          if (!editor) {
             // Try to find in mock accounts if not in main list
             const allMocks = [...mockEditorAccounts.editorAccounts, ...mockUserData.users]
             editor = allMocks.find(u => u.id === editorId)
          }

          if (editor) {
             journal.assignedEditor = editor.username 
          } else {
             console.warn(`Editor with ID ${editorId} not found for assignment.`)
             journal.assignedEditor = 'Unknown Editor'
          }
          
          this.updateJournal(journal)
        }
        return true
      } catch (error) {
         console.error('Assign editor failed:', error)
         throw error
      }
    },

    // Assign Task
    async assignTaskToEditor(editorId, taskData) {
       try {
         await editorApi.assignTask({ editor_id: editorId, ...taskData })
         // Logic to update tasks would go here if we had a tasks store
         return true
       } catch (error) {
         console.error('Assign task failed:', error)
         throw error
       }
    },

    // Add Notification
    addNotification(notification) {
      const newNotification = {
        id: Date.now(),
        createdAt: new Date().toISOString(),
        isRead: false,
        ...notification
      }
      this.notifications.unshift(newNotification)
      // Keep only last 100 notifications
      if (this.notifications.length > 100) {
        this.notifications = this.notifications.slice(0, 100)
      }
      localStorage.setItem('notifications', JSON.stringify(this.notifications))
      return newNotification
    },

    // Mark Notification as Read
    markNotificationAsRead(id) {
        const index = this.notifications.findIndex(n => n.id === id)
        if (index !== -1) {
            this.notifications[index].isRead = true
            localStorage.setItem('notifications', JSON.stringify(this.notifications))
        }
    },

    // 临时模拟方法 - 待后端提供 /api/revision/update-status 后替换
    // 更新稿件状态
    updateManuscriptStatus(manuscriptId, newStatus) {
      const journalIndex = this.journals.findIndex(journal => String(journal.id) === String(manuscriptId))
      if (journalIndex !== -1) {
        const updatedJournal = { ...this.journals[journalIndex] }
        updatedJournal.status = newStatus
        updatedJournal.lastUpdated = new Date().toISOString()
        this.journals.splice(journalIndex, 1, updatedJournal)
        localStorage.setItem('journals_v2', JSON.stringify(this.journals))
        return true
      }
      return false
    },

    // 临时模拟方法 - 待后端提供 /api/revision/sync-status 后替换
    // 同步更新稿件状态
    syncStatus() {
      // 模拟同步操作，实际实现中可能需要从后端拉取最新状态
      // 这里只是简单返回当前状态
      return this.journals
    },

    // Return to Reviewer (Mock)
    returnToReviewer(manuscriptId) {
      const journalIndex = this.journals.findIndex(journal => String(journal.id) === String(manuscriptId))
      if (journalIndex !== -1) {
        const updatedJournal = { ...this.journals[journalIndex] }
        updatedJournal.status = 'under_peer_review'
        updatedJournal.lastUpdated = new Date().toISOString()
        this.journals.splice(journalIndex, 1, updatedJournal)
        localStorage.setItem('journals_v2', JSON.stringify(this.journals))
        return true
      }
      return false
    }
  }
})
